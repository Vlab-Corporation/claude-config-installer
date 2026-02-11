#!/usr/bin/env python3
"""
Task Analyzer - Ultrathink Analysis System
Analyzes task lists for dependencies, conflicts, and parallel execution grouping.

Features:
- Parse tasks from multiple formats (string, markdown, JSON)
- Detect dependencies between tasks
- Detect conflicts (hard and soft)
- Create parallel execution groups
- Integrate with queue system
"""
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any

# Import from existing modules
try:
    from queue_manager import QueueManager, ConflictAnalyzer
except ImportError:
    QueueManager = None
    ConflictAnalyzer = None


@dataclass
class AnalysisResult:
    """Result of task analysis"""
    tasks: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    explicit_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    conflicts: List[Tuple[str, str, str]] = field(default_factory=list)  # (task_a, task_b, reason)
    soft_conflicts: List[Tuple[str, str, str]] = field(default_factory=list)
    groups: List[List[str]] = field(default_factory=list)
    time_estimate: Dict[str, Any] = field(default_factory=dict)
    has_warnings: bool = False
    has_circular_warning: bool = False
    executed: bool = False
    queued: bool = False
    auto_executed: bool = False

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            "tasks": self.tasks,
            "dependencies": self.dependencies,
            "conflicts": [{"task_a": c[0], "task_b": c[1], "reason": c[2]} for c in self.conflicts],
            "soft_conflicts": [{"task_a": c[0], "task_b": c[1], "reason": c[2]} for c in self.soft_conflicts],
            "groups": self.groups,
            "execution_plan": {
                "total_groups": len(self.groups),
                "max_parallel": max(len(g) for g in self.groups) if self.groups else 0,
            },
            "time_estimate": self.time_estimate,
            "warnings": {
                "has_warnings": self.has_warnings,
                "has_circular": self.has_circular_warning,
            }
        }, indent=2, ensure_ascii=False)

    def to_pretty(self) -> str:
        """Convert to pretty formatted string"""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("  📊 Task Analysis Result")
        lines.append("=" * 60)

        # Tasks
        lines.append(f"\n📝 Tasks ({len(self.tasks)}):")
        for i, task in enumerate(self.tasks, 1):
            lines.append(f"   {i}. {task}")

        # Dependencies
        if any(self.dependencies.values()):
            lines.append("\n🔗 Dependencies:")
            for task, deps in self.dependencies.items():
                if deps:
                    lines.append(f"   {task} ← {', '.join(deps)}")

        # Conflicts
        if self.conflicts:
            lines.append("\n⚠️  Hard Conflicts:")
            for a, b, reason in self.conflicts:
                lines.append(f"   {a} ⚡ {b}: {reason}")

        if self.soft_conflicts:
            lines.append("\n💡 Soft Conflicts (can run parallel with caution):")
            for a, b, reason in self.soft_conflicts:
                lines.append(f"   {a} ~ {b}: {reason}")

        # Parallel Groups
        lines.append("\n🚀 Execution Groups:")
        for i, group in enumerate(self.groups, 1):
            parallel = "✅ Parallel" if len(group) > 1 else "➡️  Sequential"
            lines.append(f"   Group {i} ({parallel}): {', '.join(group)}")

        # Time Estimate
        if self.time_estimate:
            seq = self.time_estimate.get('sequential', 0)
            par = self.time_estimate.get('parallel', 0)
            savings = self.time_estimate.get('savings_percent', 0)
            lines.append(f"\n⏱️  Time Estimate:")
            lines.append(f"   Sequential: ~{seq} units")
            lines.append(f"   Parallel:   ~{par} units")
            lines.append(f"   Savings:    ~{savings}%")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


class TaskAnalyzer:
    """Analyzes tasks for dependencies, conflicts, and parallel grouping"""

    # Dependency patterns (task_type -> depends_on types)
    DEPENDENCY_RULES = {
        'test': ['impl', 'implement', 'build', '구현', '빌드'],
        'deploy': ['build', 'test', '빌드', '테스트'],
        'integration': ['impl', 'unit', '구현', '단위'],
        '테스트': ['구현', '빌드', 'implement', 'build'],
        '배포': ['빌드', '테스트', 'build', 'test'],
        '통합': ['구현', '단위', 'implement', 'unit'],
    }

    # Action keywords for Korean/English
    ACTION_KEYWORDS = {
        '구현': 'implement', '테스트': 'test', '빌드': 'build',
        '배포': 'deploy', '문서화': 'docs', '리팩토링': 'refactor',
        '수정': 'fix', '추가': 'add', '삭제': 'delete',
        'implement': 'implement', 'test': 'test', 'build': 'build',
        'deploy': 'deploy', 'docs': 'docs', 'refactor': 'refactor',
    }

    def __init__(self):
        self.conflict_analyzer = ConflictAnalyzer() if ConflictAnalyzer else None

    # =========================================================================
    # Task Parsing
    # =========================================================================

    def parse_task_string(self, task_string: str) -> List[str]:
        """Parse task string into list of tasks"""
        if not task_string or not task_string.strip():
            return []

        tasks = []

        # Try comma separation first
        if ',' in task_string:
            parts = task_string.split(',')
            tasks = [p.strip() for p in parts if p.strip()]
        # Try newline separation
        elif '\n' in task_string:
            lines = task_string.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove numbering (1. 2. etc)
                line = re.sub(r'^\d+\.\s*', '', line)
                # Remove markdown checkbox
                line = re.sub(r'^-\s*\[.\]\s*', '', line)
                # Remove bullet points
                line = re.sub(r'^[-*]\s*', '', line)
                if line:
                    tasks.append(line)
        else:
            # Single task
            tasks = [task_string.strip()]

        return tasks

    def parse_markdown_tasks(self, content: str) -> List[str]:
        """Parse markdown content for tasks"""
        tasks = []
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Skip headers
            if line.startswith('#'):
                continue
            # Parse checkbox items
            match = re.match(r'^-\s*\[.\]\s*(.+)$', line)
            if match:
                tasks.append(match.group(1).strip())
                continue
            # Parse bullet items
            match = re.match(r'^[-*]\s+(.+)$', line)
            if match:
                tasks.append(match.group(1).strip())

        return tasks

    def parse_json_tasks(self, content: str) -> List[str]:
        """Parse JSON content for tasks"""
        data = json.loads(content)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and 'tasks' in data:
            return data['tasks']
        return []

    def load_from_file(self, filepath: str) -> List[str]:
        """Load tasks from file"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        content = path.read_text(encoding='utf-8')
        suffix = path.suffix.lower()

        if suffix == '.json':
            return self.parse_json_tasks(content)
        elif suffix == '.md':
            return self.parse_markdown_tasks(content)
        else:
            # Plain text - one task per line
            return self.parse_task_string(content)

    # =========================================================================
    # Dependency Analysis
    # =========================================================================

    def _extract_action_and_target(self, task: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract action type and target from task string"""
        task_lower = task.lower()

        # Find action
        action = None
        for keyword, action_type in self.ACTION_KEYWORDS.items():
            if keyword in task_lower:
                action = action_type
                break

        # Find target (module name)
        target = None
        # Look for common patterns
        patterns = [
            r'(\w+)\s*(?:구현|테스트|빌드|배포|모듈|컴포넌트)',
            r'(?:implement|test|build|deploy)\s+(\w+)',
            r'(\w+)\s+(?:implement|test|build|module)',
            r'(\w+)\.py',
            r'(\w+)\.ts',
            r'src/(\w+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                target = match.group(1).lower()
                break

        # Fallback: use first significant word
        if not target:
            words = re.findall(r'\b[a-zA-Z가-힣]+\b', task)
            for word in words:
                if word.lower() not in self.ACTION_KEYWORDS:
                    target = word.lower()
                    break

        return action, target

    def analyze_dependencies(self, tasks: List[str]) -> AnalysisResult:
        """Analyze dependencies between tasks"""
        result = AnalysisResult(tasks=tasks)
        result.dependencies = {task: [] for task in tasks}

        # Build task index by action and target
        task_actions = {}
        for task in tasks:
            action, target = self._extract_action_and_target(task)
            task_actions[task] = (action, target)

        # Check for dependencies
        for task in tasks:
            action, target = task_actions[task]
            if not action:
                continue

            # Find what this action type depends on
            depends_on_actions = self.DEPENDENCY_RULES.get(action, [])

            for other_task in tasks:
                if other_task == task:
                    continue

                other_action, other_target = task_actions[other_task]
                if not other_action:
                    continue

                # Check if other task is a dependency
                # 1. Same target, dependent action type
                if target and other_target and target == other_target:
                    if other_action in depends_on_actions:
                        result.dependencies[task].append(other_task)

        return result

    # =========================================================================
    # Conflict Analysis
    # =========================================================================

    def _extract_scope(self, task: str) -> Dict[str, Set[str]]:
        """Extract scope (files, modules, directories) from task"""
        scope = {'files': set(), 'modules': set(), 'directories': set()}

        # File patterns
        file_patterns = [
            r'(\w+\.(?:py|ts|js|tsx|jsx|md|json|yaml|yml))',
            r'@(\S+)',
        ]
        for pattern in file_patterns:
            matches = re.findall(pattern, task)
            scope['files'].update(matches)

        # Module patterns
        module_patterns = [
            r'(\w+)\s*(?:모듈|컴포넌트|서비스|module|component|service)',
            r'(?:모듈|컴포넌트|서비스|module|component|service)\s*(\w+)',
            r'(\w+)\s*(?:구현|테스트|리팩토링)',
            r'(?:implement|test|refactor)\s+(\w+)',
        ]
        for pattern in module_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            scope['modules'].update(m.lower() for m in matches)

        # Directory patterns
        dir_patterns = [
            r'src/(\w+)',
            r'in\s+(\w+)/',
            r'(\w+)/\s*(?:폴더|디렉토리|directory|folder)',
        ]
        for pattern in dir_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            scope['directories'].update(m.lower() for m in matches)

        return scope

    def analyze_conflicts(self, tasks: List[str]) -> AnalysisResult:
        """Analyze conflicts between tasks"""
        result = AnalysisResult(tasks=tasks)

        # Build scope for each task
        task_scopes = {task: self._extract_scope(task) for task in tasks}

        # Check for conflicts between all pairs
        for i, task_a in enumerate(tasks):
            scope_a = task_scopes[task_a]

            for task_b in tasks[i+1:]:
                scope_b = task_scopes[task_b]

                # File conflict (hard)
                common_files = scope_a['files'] & scope_b['files']
                if common_files:
                    result.conflicts.append((task_a, task_b, f"same file: {', '.join(common_files)}"))
                    continue

                # Module conflict (soft or hard depending on specificity)
                common_modules = scope_a['modules'] & scope_b['modules']
                if common_modules:
                    result.soft_conflicts.append((task_a, task_b, f"same module: {', '.join(common_modules)}"))
                    continue

                # Directory conflict (soft)
                common_dirs = scope_a['directories'] & scope_b['directories']
                if common_dirs:
                    result.soft_conflicts.append((task_a, task_b, f"same directory: {', '.join(common_dirs)}"))

        return result

    # =========================================================================
    # Parallel Grouping
    # =========================================================================

    def create_parallel_groups(self, tasks: List[str]) -> AnalysisResult:
        """Create parallel execution groups"""
        # Get dependencies and conflicts
        dep_result = self.analyze_dependencies(tasks)
        conflict_result = self.analyze_conflicts(tasks)

        result = AnalysisResult(
            tasks=tasks,
            dependencies=dep_result.dependencies,
            conflicts=conflict_result.conflicts,
            soft_conflicts=conflict_result.soft_conflicts,
        )

        # Build dependency graph
        remaining = set(tasks)
        completed = set()
        groups = []

        # Hard conflict pairs (can't be in same group)
        hard_conflict_pairs = set()
        for a, b, _ in result.conflicts:
            hard_conflict_pairs.add((a, b))
            hard_conflict_pairs.add((b, a))

        while remaining:
            # Find tasks with all dependencies satisfied
            ready = []
            for task in remaining:
                deps = result.dependencies.get(task, [])
                if all(d in completed or d not in tasks for d in deps):
                    ready.append(task)

            if not ready:
                # Circular dependency - break by taking first remaining
                result.has_circular_warning = True
                ready = [list(remaining)[0]]

            # Group ready tasks that don't conflict
            group = []
            for task in ready:
                can_add = True
                for existing in group:
                    if (task, existing) in hard_conflict_pairs:
                        can_add = False
                        break
                if can_add:
                    group.append(task)
                    remaining.remove(task)

            # Remaining ready tasks go to next group
            for task in ready:
                if task in remaining:
                    remaining.remove(task)
                    # Add to a new group or append to existing
                    if not groups or task in [t for g in groups for t in g]:
                        pass
                    else:
                        group.append(task)

            if group:
                groups.append(group)
                completed.update(group)

        result.groups = groups
        result.has_warnings = len(result.soft_conflicts) > 0

        # Time estimate
        total_tasks = len(tasks)
        sequential_time = total_tasks
        parallel_time = len(groups)
        savings = round((1 - parallel_time / sequential_time) * 100) if sequential_time > 0 else 0

        result.time_estimate = {
            'sequential': sequential_time,
            'parallel': parallel_time,
            'savings_percent': max(0, savings),
        }

        return result

    # =========================================================================
    # Main Analysis
    # =========================================================================

    def analyze(self, tasks: List[str], execute: bool = False, auto: bool = False) -> AnalysisResult:
        """Full analysis of tasks"""
        # Deduplicate while preserving order
        seen = set()
        unique_tasks = []
        for task in tasks:
            if task not in seen:
                seen.add(task)
                unique_tasks.append(task)

        result = self.create_parallel_groups(unique_tasks)

        if auto:
            result.auto_executed = True
            result.executed = True
            result.queued = True
            self._execute_groups(result)
        elif execute:
            result.executed = True
            result.queued = True
            self._execute_groups(result)

        return result

    def analyze_queue(self) -> AnalysisResult:
        """Analyze current queue tasks"""
        if not QueueManager:
            return AnalysisResult()

        qm = QueueManager()
        tasks_data = qm.list_tasks()

        # Extract commands and track explicit dependencies
        tasks = []
        explicit_deps = {}

        for task_data in tasks_data:
            if task_data.get('status') == 'queued':
                cmd = task_data.get('command', '')
                task_id = task_data.get('id', '')
                tasks.append(cmd)

                if task_data.get('depends_on'):
                    explicit_deps[task_id] = task_data['depends_on']

        result = self.analyze(tasks)
        result.explicit_dependencies = explicit_deps
        return result

    def _execute_groups(self, result: AnalysisResult):
        """Add tasks to queue based on analysis"""
        if not QueueManager:
            return

        qm = QueueManager()

        # Add tasks group by group with proper dependencies
        prev_group_ids = []

        for group in result.groups:
            group_ids = []
            for task in group:
                # Add with dependency on previous group
                depends_on = prev_group_ids if prev_group_ids else None
                task_id = qm.add_task(
                    command=task,
                    priority='normal',
                    depends_on=depends_on[0] if depends_on and len(depends_on) == 1 else None
                )
                if task_id:
                    group_ids.append(task_id)

            prev_group_ids = group_ids
