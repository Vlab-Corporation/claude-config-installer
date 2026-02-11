#!/usr/bin/env python3
"""
Conflict-Based Parallel Execution System
Enables parallel task execution with intelligent conflict detection and context merging.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from collections import defaultdict
import json


class ConflictLevel(Enum):
    """3-Level Conflict Detection System"""
    NONE = 0   # Different files/modules - parallel OK
    SOFT = 1   # Same directory or import relationship - parallel with warning
    HARD = 2   # Same file or direct dependency - sequential required


@dataclass
class ScopeInfo:
    """Task scope information for conflict analysis"""
    files: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


@dataclass
class ConflictInfo:
    """Information about a detected conflict"""
    file: str
    task_a_id: str
    task_b_id: str
    conflict_type: str  # "same_file", "import_relationship", "same_directory"


@dataclass
class MergedContext:
    """Result of merging multiple execution contexts"""
    files_changed: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    conflicts: List[ConflictInfo] = field(default_factory=list)
    has_conflicts: bool = False
    merged_changes: Dict[str, str] = field(default_factory=dict)


@dataclass
class ParallelGroup:
    """A group of tasks that can execute in parallel"""
    tasks: List[Any] = field(default_factory=list)
    can_parallel: bool = True
    has_soft_conflicts: bool = False
    soft_conflict_pairs: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Execution plan for parallel groups"""
    groups: List[ParallelGroup] = field(default_factory=list)
    total_groups: int = 0
    estimated_parallelism: int = 0
    sequential_time: float = 0.0
    parallel_time: float = 0.0
    time_savings_percent: float = 0.0


class DependencyGraph:
    """Directed graph for task dependencies and conflicts"""

    def __init__(self):
        self.edges: Dict[str, Dict[str, str]] = defaultdict(dict)  # from -> {to: edge_type}
        self.nodes: Set[str] = set()

    def add_node(self, node_id: str):
        """Add a node to the graph"""
        self.nodes.add(node_id)

    def add_edge(self, from_id: str, to_id: str, edge_type: str = "dependency"):
        """Add directed edge with type (dependency, hard, soft)"""
        self.nodes.add(from_id)
        self.nodes.add(to_id)
        self.edges[from_id][to_id] = edge_type

    def has_edge(self, from_id: str, to_id: str) -> bool:
        """Check if edge exists"""
        return to_id in self.edges.get(from_id, {})

    def get_edge_type(self, from_id: str, to_id: str) -> Optional[str]:
        """Get edge type if exists"""
        return self.edges.get(from_id, {}).get(to_id)

    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get all nodes that this node depends on (incoming edges)"""
        deps = set()
        for from_id, edges in self.edges.items():
            if node_id in edges:
                deps.add(from_id)
        return deps

    def get_dependents(self, node_id: str) -> Set[str]:
        """Get all nodes that depend on this node (outgoing edges)"""
        return set(self.edges.get(node_id, {}).keys())

    def topological_sort(self) -> List[str]:
        """Return nodes in topological order (dependencies first)"""
        in_degree = defaultdict(int)
        for node in self.nodes:
            in_degree[node] = 0

        for from_id, targets in self.edges.items():
            for to_id in targets:
                in_degree[to_id] += 1

        # Start with nodes that have no dependencies
        queue = [n for n in self.nodes if in_degree[n] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for dependent in self.edges.get(node, {}):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result


class EnhancedConflictAnalyzer:
    """Enhanced 3-level conflict analyzer for parallel execution"""

    def analyze_conflict_level(self, task_a: Any, task_b: Any) -> ConflictLevel:
        """
        Analyze conflict level between two tasks.

        Returns:
            ConflictLevel.NONE: Different files/modules - parallel OK
            ConflictLevel.SOFT: Same directory or import relationship - parallel with warning
            ConflictLevel.HARD: Same file or direct dependency - sequential required
        """
        # Check for explicit dependency
        if hasattr(task_b, 'depends_on') and task_b.depends_on:
            if task_a.id in task_b.depends_on:
                return ConflictLevel.HARD

        if hasattr(task_a, 'depends_on') and task_a.depends_on:
            if task_b.id in task_a.depends_on:
                return ConflictLevel.HARD

        # Extract scope info
        scope_a = self._extract_scope(task_a)
        scope_b = self._extract_scope(task_b)

        # Level 2: HARD conflict - same file
        if self._has_file_overlap(scope_a, scope_b):
            return ConflictLevel.HARD

        # Level 1: SOFT conflict - same directory or import relationship
        if self._has_directory_overlap(scope_a, scope_b):
            return ConflictLevel.SOFT

        if self._has_import_relationship(scope_a, scope_b):
            return ConflictLevel.SOFT

        # Level 0: No conflict
        return ConflictLevel.NONE

    def _extract_scope(self, task: Any) -> ScopeInfo:
        """Extract scope info from task"""
        if hasattr(task, 'scope') and task.scope:
            scope_dict = task.scope if isinstance(task.scope, dict) else {}
            return ScopeInfo(
                files=scope_dict.get('files', []),
                directories=scope_dict.get('directories', []),
                modules=scope_dict.get('modules', []),
                imports=scope_dict.get('imports', []),
                exports=scope_dict.get('exports', [])
            )
        return ScopeInfo()

    def _has_file_overlap(self, scope_a: ScopeInfo, scope_b: ScopeInfo) -> bool:
        """Check if tasks target same files"""
        files_a = set(scope_a.files)
        files_b = set(scope_b.files)
        return bool(files_a & files_b)

    def _has_directory_overlap(self, scope_a: ScopeInfo, scope_b: ScopeInfo) -> bool:
        """Check if tasks target same directories"""
        dirs_a = set(scope_a.directories)
        dirs_b = set(scope_b.directories)
        return bool(dirs_a & dirs_b)

    def _has_import_relationship(self, scope_a: ScopeInfo, scope_b: ScopeInfo) -> bool:
        """Check if one task exports what another imports"""
        exports_a = set(scope_a.exports)
        imports_b = set(scope_b.imports)

        exports_b = set(scope_b.exports)
        imports_a = set(scope_a.imports)

        return bool(exports_a & imports_b) or bool(exports_b & imports_a)


class ParallelScheduler:
    """Scheduler for creating parallel execution groups"""

    def __init__(self):
        self.analyzer = EnhancedConflictAnalyzer()

    def build_dependency_graph(self, tasks: List[Any]) -> DependencyGraph:
        """Build dependency graph from tasks based on conflicts"""
        graph = DependencyGraph()

        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.id)

        # Add explicit dependencies
        for task in tasks:
            if hasattr(task, 'depends_on') and task.depends_on:
                for dep_id in task.depends_on:
                    graph.add_edge(dep_id, task.id, "dependency")

        # Add implicit dependencies based on conflicts
        for i, task_a in enumerate(tasks):
            for task_b in tasks[i+1:]:
                level = self.analyzer.analyze_conflict_level(task_a, task_b)

                if level == ConflictLevel.HARD:
                    # Add edge from earlier to later task (ordering by position)
                    graph.add_edge(task_a.id, task_b.id, "hard")
                elif level == ConflictLevel.SOFT:
                    # Soft conflicts don't create hard dependencies
                    # but we track them for warnings
                    pass

        return graph

    def create_parallel_groups(self, tasks: List[Any]) -> List[ParallelGroup]:
        """
        Create parallel execution groups from tasks.
        Uses greedy algorithm to maximize parallelism while respecting hard conflicts.
        """
        if not tasks:
            return []

        graph = self.build_dependency_graph(tasks)
        task_map = {t.id: t for t in tasks}

        # Track which tasks are scheduled
        scheduled: Set[str] = set()
        groups: List[ParallelGroup] = []

        # Get topological order
        topo_order = graph.topological_sort()

        while len(scheduled) < len(tasks):
            # Find all tasks that can run in this group
            # (all dependencies satisfied)
            available = []

            for task_id in topo_order:
                if task_id in scheduled:
                    continue

                # Check if all hard dependencies are satisfied
                deps = graph.get_dependencies(task_id)
                hard_deps = {d for d in deps if graph.get_edge_type(d, task_id) in ("hard", "dependency")}

                if hard_deps <= scheduled:
                    available.append(task_id)

            if not available:
                break

            # Create group from available tasks
            group = ParallelGroup()
            group_task_ids: Set[str] = set()

            for task_id in available:
                # Check for hard conflicts with tasks already in this group
                can_add = True
                for existing_id in group_task_ids:
                    level = self.analyzer.analyze_conflict_level(
                        task_map[existing_id],
                        task_map[task_id]
                    )
                    if level == ConflictLevel.HARD:
                        can_add = False
                        break
                    elif level == ConflictLevel.SOFT:
                        group.has_soft_conflicts = True
                        group.soft_conflict_pairs.append((existing_id, task_id))

                if can_add:
                    group.tasks.append(task_map[task_id])
                    group_task_ids.add(task_id)
                    scheduled.add(task_id)

            if group.tasks:
                group.can_parallel = len(group.tasks) > 1
                groups.append(group)

        return groups

    def generate_execution_plan(self, tasks: List[Any]) -> ExecutionPlan:
        """Generate full execution plan with time estimates"""
        groups = self.create_parallel_groups(tasks)

        # Estimate times (assuming 1 unit per task for simplicity)
        sequential_time = float(len(tasks))
        parallel_time = float(len(groups))  # Each group runs in parallel

        max_parallelism = max((len(g.tasks) for g in groups), default=0)

        time_savings = ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0

        return ExecutionPlan(
            groups=groups,
            total_groups=len(groups),
            estimated_parallelism=max_parallelism,
            sequential_time=sequential_time,
            parallel_time=parallel_time,
            time_savings_percent=time_savings
        )

    def sessions_needed(self, groups: List[ParallelGroup]) -> int:
        """Calculate maximum sessions needed for parallel execution"""
        if not groups:
            return 0
        return max(len(g.tasks) for g in groups)


class ContextMerger:
    """Merges contexts from parallel task executions"""

    def merge(self, contexts: List[Dict[str, Any]]) -> MergedContext:
        """
        Merge multiple execution contexts into one.
        Detects file conflicts and deduplicates patterns.
        """
        merged = MergedContext()

        # Track which files were changed by which tasks
        file_changes: Dict[str, List[str]] = defaultdict(list)  # file -> [task_ids]

        for ctx in contexts:
            task_id = ctx.get('task_id', 'unknown')

            # Merge files_changed
            for f in ctx.get('files_changed', []):
                if f not in merged.files_changed:
                    merged.files_changed.append(f)
                file_changes[f].append(task_id)

            # Merge patterns (deduplicated)
            for p in ctx.get('patterns', []):
                if p not in merged.patterns:
                    merged.patterns.append(p)

            # Merge changes
            for f, change in ctx.get('changes', {}).items():
                if f in merged.merged_changes:
                    # Conflict detected!
                    merged.has_conflicts = True
                    merged.conflicts.append(ConflictInfo(
                        file=f,
                        task_a_id=merged.merged_changes.get(f'{f}_task_id', 'unknown'),
                        task_b_id=task_id,
                        conflict_type="same_file"
                    ))
                else:
                    merged.merged_changes[f] = change
                    merged.merged_changes[f'{f}_task_id'] = task_id

        # Detect conflicts from multiple tasks changing same file
        for f, task_ids in file_changes.items():
            if len(task_ids) > 1 and not any(c.file == f for c in merged.conflicts):
                merged.has_conflicts = True
                merged.conflicts.append(ConflictInfo(
                    file=f,
                    task_a_id=task_ids[0],
                    task_b_id=task_ids[1],
                    conflict_type="same_file"
                ))

        return merged


# CLI Entry Point
if __name__ == "__main__":
    import sys

    print("Conflict-Based Parallel Execution System")
    print("=" * 50)
    print("\nUsage:")
    print("  Import this module to use EnhancedConflictAnalyzer,")
    print("  ParallelScheduler, and ContextMerger classes.")
    print("\nClasses:")
    print("  - ConflictLevel: NONE, SOFT, HARD")
    print("  - EnhancedConflictAnalyzer: 3-level conflict detection")
    print("  - ParallelScheduler: Parallel group scheduling")
    print("  - DependencyGraph: Task dependency management")
    print("  - ContextMerger: Post-parallel context merging")
