#!/usr/bin/env python3
"""
Claude Code Task Queue Manager
Manages task queuing with conflict detection, dependency resolution, and auto-execution.
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

# Import parallel execution system
try:
    from parallel_executor import (
        ParallelScheduler, EnhancedConflictAnalyzer, ConflictLevel,
        ContextMerger, ExecutionPlan
    )
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

# Paths
QUEUE_DIR = Path.home() / ".claude" / "queue"
TASKS_FILE = QUEUE_DIR / "tasks.json"
HISTORY_FILE = QUEUE_DIR / "history.json"

class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

class TaskStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

@dataclass
class ScopeInfo:
    """Tracks modification scope for conflict detection"""
    files: list = field(default_factory=list)
    directories: list = field(default_factory=list)
    modules: list = field(default_factory=list)
    patterns: list = field(default_factory=list)  # e.g., "*.test.ts"
    estimated_scope: str = "unknown"  # file, module, project, system

@dataclass
class Task:
    id: str
    command: str
    priority: str
    status: str
    scope: dict
    depends_on: list
    on_success: Optional[str]
    on_fail: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    note: str
    error_message: Optional[str]

    @classmethod
    def create(cls, command: str, priority: str = "normal",
               depends_on: list = None, on_success: str = None,
               on_fail: str = None, note: str = "", scope: dict = None):
        return cls(
            id=f"task-{uuid.uuid4().hex[:8]}",
            command=command,
            priority=priority,
            status=TaskStatus.QUEUED.value,
            scope=scope or {},
            depends_on=depends_on or [],
            on_success=on_success,
            on_fail=on_fail,
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            note=note,
            error_message=None
        )

class ConflictAnalyzer:
    """Analyzes potential conflicts between tasks based on scope"""

    # Korean action words mapping to English equivalents
    KOREAN_ACTIONS = {
        # Migration/Update
        "마이그레이션": "migrate",
        "마이그레이트": "migrate",
        "이관": "migrate",
        "업데이트": "update",
        "수정": "update",
        "변경": "update",
        "갱신": "update",
        # Create/Add
        "추가": "add",
        "생성": "create",
        "만들기": "create",
        "신규": "create",
        # Fix
        "버그수정": "fix",
        "고치기": "fix",
        "수리": "fix",
        "패치": "fix",
        # Implement
        "구현": "implement",
        "개발": "implement",
        "작성": "implement",
        # Delete/Remove
        "삭제": "delete",
        "제거": "remove",
        # Test
        "테스트": "test",
        "검증": "test",
        # Analyze
        "분석": "analyze",
        "검토": "analyze",
        # Build
        "빌드": "build",
        "컴파일": "build",
        # Other
        "리팩터링": "refactor",
        "리팩토링": "refactor",
        "최적화": "optimize",
        "개선": "improve",
        "강화": "improve",
        "활성화": "enable",
        "비활성화": "disable",
    }

    # Command patterns for scope extraction
    PATTERNS = {
        "file_ops": [
            r'(?:edit|modify|update|fix|refactor)\s+([^\s]+\.[a-z]+)',
            r'(?:in|at|file)\s+([^\s]+\.[a-z]+)',
            r'@([^\s]+\.[a-z]+)',  # @file.ts pattern
            r'(?:the|a)\s+([^\s]+\.[a-z]+)\s+file',  # "the config.json file"
        ],
        "module_ops": [
            r'(?:migrate|update|refactor|fix|add|create|implement|delete|remove|test|analyze|build|improve|enable|disable)\s+(\w+)',
            r'(?:module|component|service|feature)\s+(\w+)',
            r'(\w+)\s+(?:module|component|service|feature)',  # "auth module"
            r'(\w+)\s+(?:모듈|컴포넌트|서비스|기능)',  # Korean: "auth 모듈"
        ],
        "directory_ops": [
            r'(?:in|under|directory)\s+([^\s/]+/[^\s]*)',
            r'(?:in|under)\s+(src/[^\s]*)',
        ],
        "test_ops": [
            r'test\s+(\w+)',
            r'(?:tests?)\s+(?:for|in)\s+(\w+)',
        ],
        "auto_dev": [
            # English actions
            r'/sc:auto-dev\s+(?:migrate|update|fix|add|create|implement|delete|remove|test|analyze|build|improve|enable|disable)\s+(\w+)',
            # Korean actions (captured after Korean word)
            r'/sc:auto-dev\s+(?:마이그레이션|마이그레이트|이관|업데이트|수정|변경|갱신|추가|생성|만들기|신규|버그수정|고치기|수리|패치|구현|개발|작성|삭제|제거|테스트|검증|분석|검토|빌드|컴파일|리팩터링|리팩토링|최적화|개선|강화|활성화|비활성화)\s+(\w+)',
            # Module before Korean action
            r'/sc:auto-dev\s+(\w+)\s+(?:모듈|컴포넌트|서비스|기능)?\s*(?:마이그레이션|수정|추가|삭제|구현|테스트)',
        ],
        "slash_commands": [
            # /sc:implement, /sc:test, /sc:build, /sc:analyze, /sc:improve
            r'/sc:(?:implement|test|build|analyze|improve|design|cleanup|troubleshoot)\s+(\w+)',
            # /queue with nested command
            r'/queue\s+["\']?/sc:\w+\s+(?:\w+\s+)?(\w+)',
        ],
        "natural_language": [
            # English natural language
            r'(?:the|a)\s+(\w+)\s+(?:bug|issue|error|problem|module|component|feature)',
            r'(?:authentication|authorization|login|logout|signup|profile|user|admin|payment|cart|checkout|order|product|notification|email|api|database|cache|session)\b',
            # Korean natural language
            r'(\w+)\s+(?:의|에서|에|를|을)\s+(?:버그|이슈|에러|문제|모듈)',
        ],
    }

    @classmethod
    def extract_scope(cls, command: str) -> ScopeInfo:
        """Extract modification scope from command string"""
        scope = ScopeInfo()
        # Keep original for Korean pattern matching, use lower for English
        command_lower = command.lower()

        # Extract files
        for pattern in cls.PATTERNS["file_ops"]:
            matches = re.findall(pattern, command_lower, re.IGNORECASE)
            scope.files.extend(matches)

        # Extract modules from multiple pattern categories
        pattern_categories = [
            cls.PATTERNS["module_ops"],
            cls.PATTERNS["auto_dev"],
            cls.PATTERNS["slash_commands"],
            cls.PATTERNS["natural_language"],
        ]

        for patterns in pattern_categories:
            for pattern in patterns:
                # Use original command for Korean patterns (case-sensitive for Korean)
                if any(korean in pattern for korean in ["마이그레이션", "모듈", "의|에서"]):
                    matches = re.findall(pattern, command)
                else:
                    matches = re.findall(pattern, command_lower, re.IGNORECASE)

                # Filter out common non-module words
                filtered = [m for m in matches if m.lower() not in [
                    'the', 'a', 'an', 'in', 'at', 'on', 'for', 'to', 'of',
                    'tests', 'test', 'file', 'files', 'all', 'this', 'that',
                    'please', 'help', 'need', 'want', 'should', 'must',
                    'middleware', 'integration', 'unit', 'e2e',
                ]]
                scope.modules.extend(filtered)

        # Extract directories
        for pattern in cls.PATTERNS["directory_ops"]:
            matches = re.findall(pattern, command_lower)
            scope.directories.extend(matches)

        # Special handling for Korean compound words (e.g., 사용자인증)
        korean_compound = re.findall(r'[\uac00-\ud7af]{2,}', command)
        if korean_compound and not scope.modules:
            # Add Korean compound as potential module
            scope.modules.extend(korean_compound[:1])  # Only first one

        # Determine estimated scope
        if scope.files:
            scope.estimated_scope = "file"
        elif scope.directories:
            scope.estimated_scope = "directory"
        elif scope.modules:
            scope.estimated_scope = "module"
        elif any(word in command_lower for word in ['all', 'project', 'everything']):
            scope.estimated_scope = "project"
        else:
            scope.estimated_scope = "unknown"

        # Deduplicate and clean
        scope.files = list(set(f for f in scope.files if f))
        scope.modules = list(set(m for m in scope.modules if m and len(m) > 1))
        scope.directories = list(set(d for d in scope.directories if d))

        return scope

    @classmethod
    def detect_conflicts(cls, new_task: Task, existing_tasks: list) -> list:
        """Detect potential conflicts between new task and existing queued tasks"""
        conflicts = []
        new_scope = ScopeInfo(**new_task.scope) if new_task.scope else cls.extract_scope(new_task.command)

        for existing in existing_tasks:
            if existing.status not in [TaskStatus.QUEUED.value, TaskStatus.RUNNING.value]:
                continue

            existing_scope = ScopeInfo(**existing.scope) if existing.scope else cls.extract_scope(existing.command)

            conflict_reasons = []

            # Check file conflicts
            file_overlap = set(new_scope.files) & set(existing_scope.files)
            if file_overlap:
                conflict_reasons.append(f"files: {', '.join(file_overlap)}")

            # Check module conflicts
            module_overlap = set(new_scope.modules) & set(existing_scope.modules)
            if module_overlap:
                conflict_reasons.append(f"modules: {', '.join(module_overlap)}")

            # Check directory conflicts
            for new_dir in new_scope.directories:
                for exist_dir in existing_scope.directories:
                    if new_dir.startswith(exist_dir) or exist_dir.startswith(new_dir):
                        conflict_reasons.append(f"directories: {new_dir} ↔ {exist_dir}")

            if conflict_reasons:
                conflicts.append({
                    "task_id": existing.id,
                    "task_command": existing.command,
                    "reasons": conflict_reasons
                })

        return conflicts

class DependencyResolver:
    """Resolves task dependencies and determines execution order"""

    @classmethod
    def topological_sort(cls, tasks: list) -> list:
        """Sort tasks based on dependencies (Kahn's algorithm)"""
        if not tasks:
            return []

        # Build adjacency list and in-degree count
        graph = {t.id: [] for t in tasks}
        in_degree = {t.id: 0 for t in tasks}
        task_map = {t.id: t for t in tasks}

        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id in graph:
                    graph[dep_id].append(task.id)
                    in_degree[task.id] += 1

        # Start with tasks that have no dependencies
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            # Sort by priority within same dependency level
            queue.sort(key=lambda tid: (
                Priority[task_map[tid].priority.upper()].value,
                task_map[tid].created_at
            ))

            current = queue.pop(0)
            result.append(task_map[current])

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(tasks):
            raise ValueError("Circular dependency detected in task queue")

        return result

    @classmethod
    def get_next_executable(cls, tasks: list) -> Optional[Task]:
        """Get the next task that can be executed (all dependencies satisfied)"""
        completed_ids = {t.id for t in tasks if t.status == TaskStatus.COMPLETED.value}

        for task in cls.topological_sort([t for t in tasks if t.status == TaskStatus.QUEUED.value]):
            deps_satisfied = all(dep_id in completed_ids for dep_id in task.depends_on)
            if deps_satisfied:
                return task

        return None

    @classmethod
    def get_independent_tasks(cls, tasks: list, failed_task_id: str) -> list:
        """Get tasks that don't depend on the failed task (can continue execution)"""
        # Find all tasks that depend on failed task (directly or transitively)
        blocked = {failed_task_id}
        changed = True

        while changed:
            changed = False
            for task in tasks:
                if task.id not in blocked:
                    if any(dep in blocked for dep in task.depends_on):
                        blocked.add(task.id)
                        changed = True

        # Return tasks that are not blocked
        return [t for t in tasks if t.id not in blocked and t.status == TaskStatus.QUEUED.value]

class QueueManager:
    """Main queue manager coordinating all operations"""

    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        """Ensure queue files exist"""
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        if not TASKS_FILE.exists():
            self._save_tasks([])
        if not HISTORY_FILE.exists():
            self._save_history({"completed": [], "cancelled": [], "failed": []})

    def _load_tasks(self) -> list:
        """Load tasks from file"""
        with open(TASKS_FILE) as f:
            data = json.load(f)
        return [Task(**t) for t in data.get("tasks", [])]

    def _save_tasks(self, tasks: list):
        """Save tasks to file"""
        data = {
            "version": 1,
            "tasks": [asdict(t) for t in tasks],
            "last_updated": datetime.now().isoformat()
        }
        with open(TASKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_history(self) -> dict:
        """Load history from file"""
        with open(HISTORY_FILE) as f:
            return json.load(f)

    def _save_history(self, history: dict):
        """Save history to file"""
        history["version"] = 1
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    def add(self, command: str, priority: str = "normal",
            depends_on: list = None, on_success: str = None,
            on_fail: str = None, note: str = "") -> dict:
        """Add a new task to the queue with conflict analysis"""

        # Extract scope from command
        scope = ConflictAnalyzer.extract_scope(command)

        # Create task
        task = Task.create(
            command=command,
            priority=priority,
            depends_on=depends_on or [],
            on_success=on_success,
            on_fail=on_fail,
            note=note,
            scope=asdict(scope)
        )

        # Load existing tasks
        tasks = self._load_tasks()

        # Detect conflicts
        conflicts = ConflictAnalyzer.detect_conflicts(task, tasks)

        result = {
            "task": asdict(task),
            "conflicts": conflicts,
            "scope_analysis": asdict(scope),
            "action_required": len(conflicts) > 0
        }

        if conflicts:
            result["message"] = "CONFLICT_DETECTED"
            result["options"] = [
                "parallel - Run in parallel (ignore conflicts)",
                "depend - Add dependency (run after conflicting tasks)",
                "cancel - Cancel this task"
            ]
        else:
            # No conflicts, add to queue
            tasks.append(task)
            self._save_tasks(tasks)
            result["message"] = "TASK_ADDED"
            result["position"] = len([t for t in tasks if t.status == TaskStatus.QUEUED.value])

        return result

    def add_with_resolution(self, command: str, resolution: str,
                           conflict_task_ids: list = None, **kwargs) -> dict:
        """Add task with conflict resolution already decided"""

        scope = ConflictAnalyzer.extract_scope(command)

        if resolution == "depend" and conflict_task_ids:
            kwargs["depends_on"] = list(set(kwargs.get("depends_on", []) + conflict_task_ids))

        task = Task.create(
            command=command,
            scope=asdict(scope),
            **kwargs
        )

        tasks = self._load_tasks()
        tasks.append(task)
        self._save_tasks(tasks)

        return {
            "task": asdict(task),
            "message": "TASK_ADDED",
            "resolution_applied": resolution
        }

    def list(self, status: str = None, verbose: bool = False) -> dict:
        """List tasks in the queue"""
        tasks = self._load_tasks()

        if status:
            tasks = [t for t in tasks if t.status == status]

        # Sort by execution order
        queued = [t for t in tasks if t.status == TaskStatus.QUEUED.value]
        try:
            sorted_queued = DependencyResolver.topological_sort(queued)
        except ValueError as e:
            sorted_queued = queued

        other = [t for t in tasks if t.status != TaskStatus.QUEUED.value]

        return {
            "total": len(tasks),
            "queued": len(queued),
            "tasks": [asdict(t) for t in sorted_queued + other],
            "execution_order": [t.id for t in sorted_queued]
        }

    def cancel(self, task_id: str = None, cancel_all: bool = False) -> dict:
        """Cancel task(s) from the queue"""
        tasks = self._load_tasks()
        history = self._load_history()
        cancelled = []

        if cancel_all:
            for task in tasks:
                if task.status == TaskStatus.QUEUED.value:
                    task.status = TaskStatus.CANCELLED.value
                    task.completed_at = datetime.now().isoformat()
                    history["cancelled"].append(asdict(task))
                    cancelled.append(task.id)
        elif task_id:
            for task in tasks:
                if task.id == task_id and task.status == TaskStatus.QUEUED.value:
                    task.status = TaskStatus.CANCELLED.value
                    task.completed_at = datetime.now().isoformat()
                    history["cancelled"].append(asdict(task))
                    cancelled.append(task.id)
                    break

        # Remove cancelled tasks from queue
        tasks = [t for t in tasks if t.status != TaskStatus.CANCELLED.value]

        self._save_tasks(tasks)
        self._save_history(history)

        return {
            "cancelled": cancelled,
            "remaining": len([t for t in tasks if t.status == TaskStatus.QUEUED.value])
        }

    def get_next(self) -> dict:
        """Get the next task to execute"""
        tasks = self._load_tasks()
        next_task = DependencyResolver.get_next_executable(tasks)

        if next_task:
            return {
                "has_next": True,
                "task": asdict(next_task),
                "remaining": len([t for t in tasks if t.status == TaskStatus.QUEUED.value]) - 1
            }

        return {
            "has_next": False,
            "message": "No executable tasks (dependencies not met or queue empty)"
        }

    def start(self, task_id: str) -> dict:
        """Mark a task as started"""
        tasks = self._load_tasks()

        for task in tasks:
            if task.id == task_id:
                task.status = TaskStatus.RUNNING.value
                task.started_at = datetime.now().isoformat()
                self._save_tasks(tasks)
                return {"started": task_id}

        return {"error": f"Task {task_id} not found"}

    def complete(self, task_id: str, success: bool = True, error_message: str = None) -> dict:
        """Mark a task as completed or failed"""
        tasks = self._load_tasks()
        history = self._load_history()
        next_task = None
        chain_task = None

        for task in tasks:
            if task.id == task_id:
                task.completed_at = datetime.now().isoformat()

                if success:
                    task.status = TaskStatus.COMPLETED.value
                    history["completed"].append(asdict(task))

                    # Check for success chain
                    if task.on_success:
                        chain_task = task.on_success
                else:
                    task.status = TaskStatus.FAILED.value
                    task.error_message = error_message
                    history["failed"].append(asdict(task))

                    # Check for fail chain
                    if task.on_fail:
                        chain_task = task.on_fail

                break

        # Remove completed/failed task from active queue
        active_tasks = [t for t in tasks if t.status not in [
            TaskStatus.COMPLETED.value,
            TaskStatus.FAILED.value,
            TaskStatus.CANCELLED.value
        ]]

        self._save_tasks(active_tasks)
        self._save_history(history)

        # Get next task
        if not success:
            # On failure, get independent tasks only
            independent = DependencyResolver.get_independent_tasks(active_tasks, task_id)
            if independent:
                next_task = independent[0]
        else:
            next_task = DependencyResolver.get_next_executable(active_tasks)

        result = {
            "task_id": task_id,
            "status": "completed" if success else "failed",
            "chain_task": chain_task
        }

        if next_task:
            result["next_task"] = asdict(next_task)
            result["auto_execute"] = True
        else:
            result["queue_empty"] = len(active_tasks) == 0
            result["blocked_count"] = len([t for t in active_tasks if t.status == TaskStatus.QUEUED.value])

        return result

    def move(self, task_id: str, position: str) -> dict:
        """Move task to different priority position"""
        tasks = self._load_tasks()

        for task in tasks:
            if task.id == task_id:
                if position == "first":
                    task.priority = "critical"
                elif position == "last":
                    task.priority = "low"
                elif position in ["critical", "high", "normal", "low"]:
                    task.priority = position

                self._save_tasks(tasks)
                return {"moved": task_id, "new_priority": task.priority}

        return {"error": f"Task {task_id} not found"}

    def clear(self) -> dict:
        """Clear the entire queue"""
        return self.cancel(cancel_all=True)

    def status(self) -> dict:
        """Get overall queue status"""
        tasks = self._load_tasks()
        history = self._load_history()

        return {
            "queued": len([t for t in tasks if t.status == TaskStatus.QUEUED.value]),
            "running": len([t for t in tasks if t.status == TaskStatus.RUNNING.value]),
            "completed_today": len([
                t for t in history.get("completed", [])
                if t.get("completed_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))
            ]),
            "failed_today": len([
                t for t in history.get("failed", [])
                if t.get("completed_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))
            ])
        }

    # ===========================================
    # Parallel Execution Support
    # ===========================================

    def get_parallel_plan(self) -> dict:
        """Generate parallel execution plan for queued tasks"""
        if not PARALLEL_AVAILABLE:
            return {"error": "Parallel execution module not available"}

        tasks = self._load_tasks()
        queued = [t for t in tasks if t.status == TaskStatus.QUEUED.value]

        if not queued:
            return {"error": "No queued tasks"}

        scheduler = ParallelScheduler()
        plan = scheduler.generate_execution_plan(queued)

        groups_info = []
        for i, group in enumerate(plan.groups):
            group_info = {
                "group_id": i + 1,
                "task_count": len(group.tasks),
                "task_ids": [t.id for t in group.tasks],
                "task_commands": [t.command[:50] + "..." if len(t.command) > 50 else t.command for t in group.tasks],
                "can_parallel": group.can_parallel,
                "has_soft_conflicts": group.has_soft_conflicts
            }
            if group.soft_conflict_pairs:
                group_info["soft_conflict_pairs"] = group.soft_conflict_pairs
            groups_info.append(group_info)

        return {
            "parallel_plan": {
                "total_tasks": len(queued),
                "total_groups": plan.total_groups,
                "max_parallelism": plan.estimated_parallelism,
                "sequential_time_units": plan.sequential_time,
                "parallel_time_units": plan.parallel_time,
                "time_savings_percent": round(plan.time_savings_percent, 1),
                "sessions_needed": scheduler.sessions_needed(plan.groups)
            },
            "groups": groups_info
        }

    def get_parallel_group(self, group_num: int = 1) -> dict:
        """Get tasks for a specific parallel group"""
        if not PARALLEL_AVAILABLE:
            return {"error": "Parallel execution module not available"}

        tasks = self._load_tasks()
        queued = [t for t in tasks if t.status == TaskStatus.QUEUED.value]

        if not queued:
            return {"error": "No queued tasks"}

        scheduler = ParallelScheduler()
        groups = scheduler.create_parallel_groups(queued)

        if group_num < 1 or group_num > len(groups):
            return {"error": f"Invalid group number. Available: 1-{len(groups)}"}

        group = groups[group_num - 1]
        return {
            "group": group_num,
            "total_groups": len(groups),
            "tasks": [asdict(t) for t in group.tasks],
            "can_parallel": group.can_parallel,
            "has_soft_conflicts": group.has_soft_conflicts,
            "soft_conflict_pairs": group.soft_conflict_pairs
        }

    def analyze_conflict(self, task_id_a: str, task_id_b: str) -> dict:
        """Analyze conflict level between two tasks"""
        if not PARALLEL_AVAILABLE:
            return {"error": "Parallel execution module not available"}

        tasks = self._load_tasks()
        task_a = next((t for t in tasks if t.id == task_id_a), None)
        task_b = next((t for t in tasks if t.id == task_id_b), None)

        if not task_a:
            return {"error": f"Task {task_id_a} not found"}
        if not task_b:
            return {"error": f"Task {task_id_b} not found"}

        analyzer = EnhancedConflictAnalyzer()
        level = analyzer.analyze_conflict_level(task_a, task_b)

        level_info = {
            ConflictLevel.NONE: "NONE - Can run in parallel",
            ConflictLevel.SOFT: "SOFT - Can parallel with warning",
            ConflictLevel.HARD: "HARD - Must run sequentially"
        }

        return {
            "task_a": task_id_a,
            "task_b": task_id_b,
            "conflict_level": level.name,
            "conflict_value": level.value,
            "description": level_info[level],
            "can_parallel": level != ConflictLevel.HARD
        }

def main():
    """CLI interface for queue manager"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        return

    qm = QueueManager()
    cmd = sys.argv[1]

    try:
        if cmd == "add":
            command = sys.argv[2] if len(sys.argv) > 2 else ""
            priority = sys.argv[3] if len(sys.argv) > 3 else "normal"
            result = qm.add(command, priority)

        elif cmd == "add-resolved":
            command = sys.argv[2]
            resolution = sys.argv[3]
            conflict_ids = sys.argv[4].split(",") if len(sys.argv) > 4 else []
            result = qm.add_with_resolution(command, resolution, conflict_ids)

        elif cmd == "list":
            status = sys.argv[2] if len(sys.argv) > 2 else None
            result = qm.list(status)

        elif cmd == "cancel":
            if len(sys.argv) > 2:
                if sys.argv[2] == "--all":
                    result = qm.cancel(cancel_all=True)
                else:
                    result = qm.cancel(task_id=sys.argv[2])
            else:
                result = {"error": "Task ID or --all required"}

        elif cmd == "next":
            result = qm.get_next()

        elif cmd == "start":
            task_id = sys.argv[2] if len(sys.argv) > 2 else ""
            result = qm.start(task_id)

        elif cmd == "complete":
            task_id = sys.argv[2] if len(sys.argv) > 2 else ""
            success = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
            error_msg = sys.argv[4] if len(sys.argv) > 4 else None
            result = qm.complete(task_id, success, error_msg)

        elif cmd == "move":
            task_id = sys.argv[2] if len(sys.argv) > 2 else ""
            position = sys.argv[3] if len(sys.argv) > 3 else "first"
            result = qm.move(task_id, position)

        elif cmd == "clear":
            result = qm.clear()

        elif cmd == "status":
            result = qm.status()

        # Parallel execution commands
        elif cmd == "parallel-plan":
            result = qm.get_parallel_plan()

        elif cmd == "parallel-group":
            group_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            result = qm.get_parallel_group(group_num)

        elif cmd == "analyze-conflict":
            if len(sys.argv) < 4:
                result = {"error": "Usage: analyze-conflict <task_id_a> <task_id_b>"}
            else:
                result = qm.analyze_conflict(sys.argv[2], sys.argv[3])

        else:
            result = {"error": f"Unknown command: {cmd}"}

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
