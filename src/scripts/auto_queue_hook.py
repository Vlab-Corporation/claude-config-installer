#!/usr/bin/env python3
"""
Auto Queue Hook for Claude Code

This module provides:
1. AutoQueueHook - Stop hook that finds queued tasks matching session context
2. update_session_context - PostToolUse hook for tracking session work
3. format_output - Output formatting for hook results

Hook Integration:
- PostToolUse: Tracks files modified during session
- Stop: Checks for matching queued tasks and notifies user
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Any, Optional

from session_context import (
    SessionContext, SessionContextManager, ContextMatcher,
    extract_context_from_tool
)

# Default paths
DEFAULT_CONTEXT_FILE = Path.home() / ".claude" / "queue" / "session_context.json"
DEFAULT_TASKS_FILE = Path.home() / ".claude" / "queue" / "tasks.json"


class AutoQueueHook:
    """
    Claude Code Stop hook for context-aware queue execution.

    At session end, checks if any queued tasks match the session's
    work context and notifies the user if matches are found.
    """

    def __init__(
        self,
        context_file: Path = None,
        tasks_file: Path = None,
        threshold: float = 0.3,
        cleanup: bool = True
    ):
        """
        Initialize the hook.

        Args:
            context_file: Path to session context JSON file
            tasks_file: Path to queue tasks JSON file
            threshold: Minimum match score to consider a task matching
            cleanup: Whether to delete context file after run
        """
        self.context_file = context_file or DEFAULT_CONTEXT_FILE
        self.tasks_file = tasks_file or DEFAULT_TASKS_FILE
        self.threshold = threshold
        self.cleanup = cleanup

        self.manager = SessionContextManager(self.context_file)
        self.matcher = ContextMatcher()

    def run(self) -> Dict[str, Any]:
        """
        Execute the hook logic.

        Returns:
            Dictionary with status and matching task information
        """
        # Step 1: Load session context
        context = self.manager.load()

        if context is None:
            return {
                "status": "no_context",
                "matching_tasks": []
            }

        if not context.has_work():
            self._cleanup_if_enabled()
            return {
                "status": "no_work_tracked",
                "matching_tasks": []
            }

        # Step 2: Load queued tasks
        tasks = self._load_queued_tasks()

        if not tasks:
            self._cleanup_if_enabled()
            return {
                "status": "no_queued_tasks",
                "matching_tasks": []
            }

        # Step 3: Find matching tasks
        matching = self.matcher.find_matching_tasks(
            tasks, context, threshold=self.threshold
        )

        # Step 4: Cleanup
        self._cleanup_if_enabled()

        # Step 5: Return results
        if not matching:
            return {
                "status": "no_matches",
                "matching_tasks": []
            }

        return {
            "status": "matches_found",
            "matching_tasks": [asdict(t) for t in matching],
            "context_summary": {
                "files_count": len(context.files),
                "modules": list(context.modules)[:5],
                "directories": list(context.directories)[:3]
            }
        }

    def _load_queued_tasks(self) -> List:
        """Load queued tasks from tasks file"""
        if not self.tasks_file.exists():
            return []

        try:
            with open(self.tasks_file) as f:
                data = json.load(f)

            # Import Task here to avoid circular imports
            from queue_manager import Task, TaskStatus

            tasks = []
            for t in data.get("tasks", []):
                task = Task(**t)
                # Only include queued tasks
                if task.status == TaskStatus.QUEUED.value:
                    tasks.append(task)

            return tasks

        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    def _cleanup_if_enabled(self):
        """Delete context file if cleanup is enabled"""
        if self.cleanup:
            self.manager.cleanup()


def format_output(result: Dict[str, Any], max_display: int = 3) -> str:
    """
    Format hook result for console output.

    Args:
        result: Hook run result dictionary
        max_display: Maximum number of tasks to display

    Returns:
        Formatted string for console output
    """
    if result["status"] != "matches_found":
        return ""

    matching = result.get("matching_tasks", [])
    if not matching:
        return ""

    lines = [
        "",
        "🔄 Found {} queued task(s) matching your session:".format(len(matching))
    ]

    # Show up to max_display tasks
    for task in matching[:max_display]:
        command = task.get("command", "")
        if len(command) > 50:
            command = command[:47] + "..."
        lines.append(f"   • {command}")

    # Show count of remaining tasks
    remaining = len(matching) - max_display
    if remaining > 0:
        lines.append(f"   ... and {remaining} more")

    lines.append("")
    lines.append("Run `/queue:next` to continue with queued tasks.")
    lines.append("")

    return "\n".join(lines)


def update_session_context(
    tool_name: str,
    tool_input: str,
    context_file: Path = None
) -> None:
    """
    Update session context from a tool use (PostToolUse hook).

    Args:
        tool_name: Name of the tool that was used
        tool_input: JSON string of tool input parameters
        context_file: Path to context file (uses default if not provided)
    """
    ctx_file = context_file or DEFAULT_CONTEXT_FILE
    manager = SessionContextManager(ctx_file)

    # Parse tool input
    try:
        params = json.loads(tool_input) if isinstance(tool_input, str) else tool_input
    except json.JSONDecodeError:
        return  # Invalid input, skip

    # Extract context update from tool
    update = extract_context_from_tool(tool_name, params, track_reads=False)

    if update is None or not update.file:
        return  # No relevant context to track

    # Load existing context or create new
    context = manager.load()
    if context is None:
        context = SessionContext.create()

    # Add the file
    context.add_file(update.file)

    # Save updated context
    manager.save(context)


def main():
    """
    Main entry point for Stop hook script.

    Usage: python auto_queue_hook.py
    """
    hook = AutoQueueHook()
    result = hook.run()
    output = format_output(result)

    if output:
        print(output)


if __name__ == "__main__":
    main()
