#!/usr/bin/env python3
"""
Session Context Tracking for Context-Aware Queue Execution

Tracks what files, modules, and directories a Claude Code session works on,
enabling intelligent matching of queued tasks to session context.
"""

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Set, Dict, Any

# Import Task and ScopeInfo from queue_manager
try:
    from queue_manager import Task, ScopeInfo
except ImportError:
    # For standalone testing
    Task = None
    ScopeInfo = None


@dataclass
class ContextUpdate:
    """Result of extracting context from a tool use"""
    file: Optional[str] = None
    module: Optional[str] = None
    directory: Optional[str] = None


@dataclass
class SessionContext:
    """
    Tracks what a session has worked on for context matching.

    Stores files, modules, and directories that were modified during
    a Claude Code session, enabling matching with queued task scopes.
    """
    session_id: str
    files: Set[str] = field(default_factory=set)
    modules: Set[str] = field(default_factory=set)
    directories: Set[str] = field(default_factory=set)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def create(cls, session_id: str = None) -> 'SessionContext':
        """Factory method to create a new SessionContext"""
        return cls(
            session_id=session_id or f"session-{uuid.uuid4().hex[:8]}",
            files=set(),
            modules=set(),
            directories=set()
        )

    def add_file(self, file_path: str) -> None:
        """
        Add a file to the tracked context.
        Also extracts and adds module name and directory.
        """
        if not file_path:
            return

        # Normalize path
        file_path = str(file_path)
        self.files.add(file_path)

        # Extract module name from file
        path = Path(file_path)
        module_name = path.stem  # filename without extension
        if module_name and len(module_name) > 1:
            self.modules.add(module_name)

        # Extract parent directory from path components
        if path.parent:
            # Add immediate parent directory name as module context
            parent_name = path.parent.name
            if parent_name and len(parent_name) > 1 and parent_name not in ['.', '..']:
                self.modules.add(parent_name)

            # Add directory path
            dir_path = str(path.parent)
            if not dir_path.endswith('/'):
                dir_path += '/'
            self.directories.add(dir_path)

        self._update_timestamp()

    def add_module(self, module_name: str) -> None:
        """Add a module name to the tracked context"""
        if module_name and len(module_name) > 1:
            self.modules.add(module_name)
            self._update_timestamp()

    def add_directory(self, directory: str) -> None:
        """Add a directory to the tracked context"""
        if directory:
            # Normalize to end with /
            if not directory.endswith('/'):
                directory += '/'
            self.directories.add(directory)
            self._update_timestamp()

    def has_work(self) -> bool:
        """Check if any work has been tracked"""
        return bool(self.files or self.modules or self.directories)

    def _update_timestamp(self) -> None:
        """Update the last_updated timestamp"""
        self.last_updated = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage"""
        return {
            "session_id": self.session_id,
            "files": list(self.files),
            "modules": list(self.modules),
            "directories": list(self.directories),
            "started_at": self.started_at,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """Deserialize from dictionary"""
        return cls(
            session_id=data.get("session_id", f"session-{uuid.uuid4().hex[:8]}"),
            files=set(data.get("files", [])),
            modules=set(data.get("modules", [])),
            directories=set(data.get("directories", [])),
            started_at=data.get("started_at", datetime.now().isoformat()),
            last_updated=data.get("last_updated", datetime.now().isoformat())
        )


class SessionContextManager:
    """
    Manages persistence of SessionContext to filesystem.

    Handles saving, loading, and cleanup of session context files.
    """

    def __init__(self, context_file: Path = None):
        """
        Initialize with path to context file.

        Args:
            context_file: Path to JSON file for context storage.
                         Defaults to ~/.claude/queue/session_context.json
        """
        self.context_file = context_file or (
            Path.home() / ".claude" / "queue" / "session_context.json"
        )

    def save(self, context: SessionContext) -> None:
        """Save session context to file"""
        # Ensure directory exists
        self.context_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.context_file, 'w') as f:
            json.dump(context.to_dict(), f, indent=2)

    def load(self) -> Optional[SessionContext]:
        """Load session context from file, returns None if not found"""
        if not self.context_file.exists():
            return None

        try:
            with open(self.context_file) as f:
                data = json.load(f)
            return SessionContext.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def cleanup(self) -> None:
        """Delete the context file"""
        if self.context_file.exists():
            self.context_file.unlink()


class ContextMatcher:
    """
    Matches queued tasks against session context.

    Compares task scopes (files, modules, directories) with session
    work history to find relevant tasks for the current session.
    """

    def match_score(self, task: 'Task', context: SessionContext) -> float:
        """
        Calculate match score between a task and session context.

        Args:
            task: Task with scope to match
            context: SessionContext with tracked work

        Returns:
            Float between 0.0 (no match) and 1.0 (perfect match)
        """
        if not context.has_work():
            return 0.0

        task_scope = self._extract_task_scope(task)
        if not task_scope:
            return 0.0

        # Calculate overlaps
        file_overlap = self._calculate_file_overlap(task_scope, context)
        module_overlap = self._calculate_module_overlap(task_scope, context)
        dir_overlap = self._calculate_directory_overlap(task_scope, context)

        # Weight the overlaps - use max to ensure any significant match counts
        # Files are most specific, modules second, directories third
        weighted_overlap = file_overlap * 0.5 + module_overlap * 0.35 + dir_overlap * 0.15

        # Boost: if any single dimension has strong match, ensure minimum score
        max_single = max(file_overlap, module_overlap, dir_overlap)
        boosted = max(weighted_overlap, max_single * 0.8)

        return min(1.0, boosted)

    def find_matching_tasks(
        self,
        tasks: List['Task'],
        context: SessionContext,
        threshold: float = 0.3
    ) -> List['Task']:
        """
        Find all tasks that match the session context above threshold.

        Args:
            tasks: List of tasks to check
            context: SessionContext to match against
            threshold: Minimum match score (0.0-1.0)

        Returns:
            List of matching tasks sorted by score (highest first)
        """
        matches = []
        for task in tasks:
            score = self.match_score(task, context)
            if score >= threshold:
                matches.append((score, task))

        # Sort by score descending
        matches.sort(key=lambda x: x[0], reverse=True)

        return [task for _, task in matches]

    def _extract_task_scope(self, task: 'Task') -> Optional[Dict]:
        """Extract scope from task object"""
        if not task.scope:
            return None
        return task.scope if isinstance(task.scope, dict) else asdict(task.scope)

    def _calculate_file_overlap(
        self,
        task_scope: Dict,
        context: SessionContext
    ) -> float:
        """Calculate file overlap score"""
        task_files = set(task_scope.get('files', []))
        if not task_files:
            return 0.0

        # Check exact matches
        exact_matches = task_files & context.files
        if exact_matches:
            return len(exact_matches) / len(task_files)

        # Check filename matches (ignoring path)
        task_filenames = {Path(f).name for f in task_files}
        context_filenames = {Path(f).name for f in context.files}
        filename_matches = task_filenames & context_filenames
        if filename_matches:
            return len(filename_matches) / len(task_files) * 0.8

        return 0.0

    def _calculate_module_overlap(
        self,
        task_scope: Dict,
        context: SessionContext
    ) -> float:
        """Calculate module overlap score"""
        task_modules = set(task_scope.get('modules', []))
        if not task_modules:
            return 0.0

        context_modules_lower = {m.lower() for m in context.modules}
        task_modules_lower = {m.lower() for m in task_modules}

        # Exact matches
        exact_matches = task_modules_lower & context_modules_lower
        if exact_matches:
            return len(exact_matches) / len(task_modules)

        # Partial matches (substring)
        partial_score = 0.0
        for tm in task_modules_lower:
            for cm in context_modules_lower:
                if tm in cm or cm in tm:
                    partial_score += 0.5 / len(task_modules)

        return min(1.0, partial_score)

    def _calculate_directory_overlap(
        self,
        task_scope: Dict,
        context: SessionContext
    ) -> float:
        """Calculate directory overlap score"""
        task_dirs = set(task_scope.get('directories', []))
        if not task_dirs:
            return 0.0

        # Normalize directories
        task_dirs_normalized = {
            d if d.endswith('/') else d + '/' for d in task_dirs
        }
        context_dirs = context.directories

        # Check overlap (including parent/child relationships)
        overlap_count = 0
        for td in task_dirs_normalized:
            for cd in context_dirs:
                # Exact match or parent/child relationship
                if td == cd or td.startswith(cd) or cd.startswith(td):
                    overlap_count += 1
                    break

        if overlap_count:
            return overlap_count / len(task_dirs)

        return 0.0


def extract_context_from_tool(
    tool_name: str,
    params: Dict[str, Any],
    track_reads: bool = False
) -> Optional[ContextUpdate]:
    """
    Extract context update from a tool use.

    Args:
        tool_name: Name of the tool (Write, Edit, Read, etc.)
        params: Tool parameters dictionary
        track_reads: Whether to track Read operations (default False)

    Returns:
        ContextUpdate with extracted information, or None
    """
    # Tools that modify files
    if tool_name in ['Write', 'Edit']:
        file_path = params.get('file_path')
        if file_path:
            return ContextUpdate(file=file_path)

    # Read operations (optional tracking)
    if tool_name == 'Read' and track_reads:
        file_path = params.get('file_path')
        if file_path:
            return ContextUpdate(file=file_path)

    # Other tools don't provide useful context
    return None
