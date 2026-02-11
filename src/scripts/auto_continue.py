#!/usr/bin/env python3
"""
Auto-Continuation System for Claude Code Task Queue

This module solves the following root causes:
1. Hook cannot trigger Claude actions → Uses flag file + system reminder
2. Stop event timing is too late → Persists continuation state to flag file
3. No Claude-side auto-continuation → Outputs <system-reminder> for Claude

Flow:
1. Task completes → QueueManager returns auto_execute=true
2. Stop hook → Sets continuation flag file
3. User submits new prompt → UserPromptSubmit hook reads flag
4. Hook outputs <system-reminder> → Claude sees and executes /queue:next
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Default paths
DEFAULT_QUEUE_DIR = Path.home() / ".claude" / "queue"
DEFAULT_FLAG_FILE = DEFAULT_QUEUE_DIR / ".auto_continue"
DEFAULT_TASKS_FILE = DEFAULT_QUEUE_DIR / "tasks.json"


class AutoContinuationManager:
    """Manages the continuation flag file for auto-execution flow"""

    def __init__(self, flag_file: Path = None, ttl_seconds: int = 300):
        """
        Initialize the continuation manager.

        Args:
            flag_file: Path to the continuation flag file
            ttl_seconds: Time-to-live for the flag in seconds (default 5 minutes)
        """
        self.flag_file = flag_file or DEFAULT_FLAG_FILE
        self.ttl_seconds = ttl_seconds

    def set_continuation(self, task_info: Dict[str, Any]) -> None:
        """
        Set the continuation flag with next task information.

        Args:
            task_info: Dictionary containing task_id, command, priority, etc.
        """
        # Ensure directory exists
        self.flag_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "task_id": task_info.get("task_id") or task_info.get("id"),
            "command": task_info.get("command", ""),
            "priority": task_info.get("priority", "normal"),
            "remaining": task_info.get("remaining", 0),
            "created_at": datetime.now().isoformat()
        }

        with open(self.flag_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_continuation(self) -> Optional[Dict[str, Any]]:
        """
        Get the continuation flag if it exists and is not expired.

        Returns:
            Task info dictionary or None if no valid flag exists
        """
        if not self.flag_file.exists():
            return None

        try:
            with open(self.flag_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Corrupted file, remove it
            self.clear_continuation()
            return None

        # Check TTL
        created_at = data.get("created_at")
        if created_at:
            try:
                created_time = datetime.fromisoformat(created_at)
                age_seconds = (datetime.now() - created_time).total_seconds()
                if age_seconds > self.ttl_seconds:
                    # Expired
                    self.clear_continuation()
                    return None
            except (ValueError, TypeError):
                pass

        return data

    def clear_continuation(self) -> None:
        """Remove the continuation flag file"""
        try:
            if self.flag_file.exists():
                self.flag_file.unlink()
        except IOError:
            pass


def format_system_reminder(task_info: Optional[Dict[str, Any]]) -> str:
    """
    Format a system reminder for Claude to continue queue execution.

    Args:
        task_info: Task information dictionary

    Returns:
        Formatted system reminder string or empty string
    """
    if not task_info:
        return ""

    task_id = task_info.get("task_id", "unknown")
    command = task_info.get("command", "next task")
    remaining = task_info.get("remaining", 0)
    priority = task_info.get("priority", "normal")

    reminder = f"""<system-reminder>
QUEUE AUTO-CONTINUATION: A queued task is ready for execution.

Next Task:
  ID: {task_id}
  Command: {command}
  Priority: {priority}
  Remaining: {remaining} more task(s) in queue

ACTION REQUIRED: Execute /queue:next immediately to continue the queue.
This is an automated continuation from a previous task completion.
</system-reminder>"""

    return reminder


def handle_stop_event(
    completion_result: Dict[str, Any],
    flag_file: Path = None
) -> None:
    """
    Handle the Stop event by setting continuation flag if needed.

    Called by the Stop hook when a task completes.

    Args:
        completion_result: Result from QueueManager.complete()
        flag_file: Path to the continuation flag file
    """
    manager = AutoContinuationManager(flag_file)

    # Check if auto-execution should continue
    auto_execute = completion_result.get("auto_execute", False)
    next_task = completion_result.get("next_task")
    queue_empty = completion_result.get("queue_empty", False)

    if auto_execute and next_task and not queue_empty:
        # Set continuation flag for next prompt
        task_info = {
            "task_id": next_task.get("id"),
            "command": next_task.get("command"),
            "priority": next_task.get("priority", "normal"),
            "remaining": completion_result.get("blocked_count", 0) + 1
        }
        manager.set_continuation(task_info)


def handle_user_prompt_event(
    flag_file: Path = None,
    clear_after: bool = True
) -> str:
    """
    Handle the UserPromptSubmit event by outputting system reminder if needed.

    Called by the UserPromptSubmit hook.

    Args:
        flag_file: Path to the continuation flag file
        clear_after: Whether to clear the flag after outputting

    Returns:
        System reminder string or empty string
    """
    manager = AutoContinuationManager(flag_file)
    task_info = manager.get_continuation()

    if not task_info:
        return ""

    output = format_system_reminder(task_info)

    if clear_after:
        manager.clear_continuation()

    return output


def stop_hook_main(flag_file: Path = None, tasks_file: Path = None) -> None:
    """
    Main entry point for Stop hook script.

    Checks queue status and sets continuation flag if there are pending tasks.
    """
    flag_file = flag_file or DEFAULT_FLAG_FILE
    tasks_file = tasks_file or DEFAULT_TASKS_FILE

    if not tasks_file.exists():
        return

    try:
        with open(tasks_file) as f:
            data = json.load(f)

        tasks = data.get("tasks", [])
        queued_tasks = [t for t in tasks if t.get("status") == "queued"]

        if queued_tasks:
            # Get next executable task (first queued task for simplicity)
            next_task = queued_tasks[0]

            manager = AutoContinuationManager(flag_file)
            manager.set_continuation({
                "task_id": next_task.get("id"),
                "command": next_task.get("command"),
                "priority": next_task.get("priority", "normal"),
                "remaining": len(queued_tasks)
            })

    except (json.JSONDecodeError, IOError):
        pass


def user_prompt_hook_main(flag_file: Path = None) -> None:
    """
    Main entry point for UserPromptSubmit hook script.

    Outputs system reminder if continuation flag exists.
    """
    flag_file = flag_file or DEFAULT_FLAG_FILE

    output = handle_user_prompt_event(flag_file, clear_after=True)
    if output:
        print(output)


if __name__ == "__main__":
    # CLI interface for hook scripts
    if len(sys.argv) < 2:
        print("Usage: auto_continue.py [stop|user-prompt]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stop":
        stop_hook_main()
    elif command == "user-prompt":
        user_prompt_hook_main()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
