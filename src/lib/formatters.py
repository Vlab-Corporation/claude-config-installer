#!/usr/bin/env python3
"""
Output formatters for cq CLI
Supports: JSON (for API/web), Pretty (for terminal), Minimal (for shell prompts)
"""
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any

# Import version
try:
    from version import __version__
except ImportError:
    __version__ = "1.0.0"


class BaseFormatter(ABC):
    """Abstract base class for output formatters"""

    @abstractmethod
    def format_status(self, data: Dict[str, Any]) -> str:
        """Format queue status output"""
        pass

    @abstractmethod
    def format_list(self, data: Dict[str, Any]) -> str:
        """Format task list output"""
        pass

    @abstractmethod
    def format_task(self, data: Dict[str, Any]) -> str:
        """Format single task output"""
        pass

    @abstractmethod
    def format_message(self, message: str, level: str = "info") -> str:
        """Format a message (info, success, warning, error)"""
        pass


class JSONFormatter(BaseFormatter):
    """JSON output formatter for API/web integration"""

    def _add_meta(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata to output"""
        return {
            **data,
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
        }

    def format_status(self, data: Dict[str, Any]) -> str:
        """Format queue status as JSON"""
        output = self._add_meta(data)
        return json.dumps(output, indent=2, ensure_ascii=False)

    def format_list(self, data: Dict[str, Any]) -> str:
        """Format task list as JSON"""
        output = {
            "tasks": data.get("tasks", []),
            "meta": {
                "total": data.get("total", 0),
                "queued": data.get("queued", 0),
                "execution_order": data.get("execution_order", []),
            },
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
        }
        return json.dumps(output, indent=2, ensure_ascii=False)

    def format_task(self, data: Dict[str, Any]) -> str:
        """Format single task as JSON"""
        output = self._add_meta({"task": data})
        return json.dumps(output, indent=2, ensure_ascii=False)

    def format_message(self, message: str, level: str = "info") -> str:
        """Format message as JSON"""
        output = {
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
        }
        return json.dumps(output, indent=2, ensure_ascii=False)


class PrettyFormatter(BaseFormatter):
    """Pretty terminal output formatter with colors and formatting"""

    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }

    # Status icons
    ICONS = {
        "queued": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫",
        "blocked": "🔒",
    }

    PRIORITY_COLORS = {
        "critical": "red",
        "high": "yellow",
        "normal": "white",
        "low": "dim",
    }

    def _color(self, text: str, color: str) -> str:
        """Apply color to text"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _icon(self, status: str) -> str:
        """Get icon for status"""
        return self.ICONS.get(status, "❓")

    def format_status(self, data: Dict[str, Any]) -> str:
        """Format queue status with pretty formatting"""
        queued = data.get("queued", 0)
        running = data.get("running", 0)
        completed = data.get("completed_today", 0)
        failed = data.get("failed_today", 0)

        lines = [
            "",
            self._color("╭" + "─" * 58 + "╮", "cyan"),
            self._color("│", "cyan") + f"  🚀 {self._color('Claude Queue Status', 'bold')}" + " " * 33 + self._color("│", "cyan"),
            self._color("├" + "─" * 58 + "┤", "cyan"),
            self._color("│", "cyan") + f"  Queued: {self._color(str(queued), 'yellow')}  │  Running: {self._color(str(running), 'green')}  │  Today: ✅ {completed}  ❌ {failed}" + " " * (16 - len(str(completed)) - len(str(failed))) + self._color("│", "cyan"),
            self._color("╰" + "─" * 58 + "╯", "cyan"),
            "",
        ]
        return "\n".join(lines)

    def format_list(self, data: Dict[str, Any]) -> str:
        """Format task list as pretty table"""
        tasks = data.get("tasks", [])

        if not tasks:
            return "\n" + self._color("  📭 Queue is empty", "dim") + "\n"

        lines = [
            "",
            self._color("  #   ID           Command                              Priority   Status", "bold"),
            self._color(" " + "─" * 75, "dim"),
        ]

        for i, task in enumerate(tasks, 1):
            task_id = task.get("id", "")[:12]
            command = task.get("command", "")[:35]
            if len(task.get("command", "")) > 35:
                command += "..."
            priority = task.get("priority", "normal")
            status = task.get("status", "queued")

            priority_color = self.PRIORITY_COLORS.get(priority, "white")
            icon = self._icon(status)

            priority_str = self._color(f"{priority:<10}", priority_color)
            line = f"  {i:<3} {task_id:<12} {command:<38} {priority_str} {icon} {status}"
            lines.append(line)

        lines.append("")
        return "\n".join(lines)

    def format_task(self, data: Dict[str, Any]) -> str:
        """Format single task details"""
        task_id = data.get("id", "unknown")
        command = data.get("command", "")
        priority = data.get("priority", "normal")
        status = data.get("status", "unknown")
        created = data.get("created_at", "")
        started = data.get("started_at", "")

        lines = [
            "",
            self._color(f"  Task: {task_id}", "bold"),
            f"  Command:  {command}",
            f"  Priority: {self._color(priority, self.PRIORITY_COLORS.get(priority, 'white'))}",
            f"  Status:   {self._icon(status)} {status}",
            f"  Created:  {created}",
        ]
        if started:
            lines.append(f"  Started:  {started}")
        lines.append("")

        return "\n".join(lines)

    def format_message(self, message: str, level: str = "info") -> str:
        """Format message with appropriate styling"""
        icons = {
            "info": self._color("[i]", "blue"),
            "success": self._color("[✓]", "green"),
            "warning": self._color("[!]", "yellow"),
            "error": self._color("[✗]", "red"),
        }
        return f"{icons.get(level, '[?]')} {message}"


class MinimalFormatter(BaseFormatter):
    """Minimal output formatter for shell prompts and scripts"""

    def format_status(self, data: Dict[str, Any]) -> str:
        """Format queue status minimally"""
        queued = data.get("queued", 0)
        running = data.get("running", 0)

        if queued == 0 and running == 0:
            return ""

        parts = []
        if running > 0:
            parts.append(f"R:{running}")
        if queued > 0:
            parts.append(f"Q:{queued}")

        return " ".join(parts)

    def format_list(self, data: Dict[str, Any]) -> str:
        """Format task list minimally"""
        tasks = data.get("tasks", [])
        if not tasks:
            return ""

        lines = []
        for task in tasks[:5]:  # Show max 5 tasks
            task_id = task.get("id", "")[-8:]  # Last 8 chars
            status = task.get("status", "?")[0].upper()  # First letter
            lines.append(f"{status}:{task_id}")

        return " ".join(lines)

    def format_task(self, data: Dict[str, Any]) -> str:
        """Format single task minimally"""
        task_id = data.get("id", "")[-8:]
        status = data.get("status", "?")[0].upper()
        return f"{status}:{task_id}"

    def format_message(self, message: str, level: str = "info") -> str:
        """Format message minimally"""
        prefix = {"info": "i", "success": "+", "warning": "!", "error": "x"}
        return f"[{prefix.get(level, '?')}] {message}"


def get_formatter(format_type: str) -> BaseFormatter:
    """Get formatter instance by type"""
    formatters = {
        "json": JSONFormatter,
        "pretty": PrettyFormatter,
        "minimal": MinimalFormatter,
    }
    formatter_class = formatters.get(format_type, PrettyFormatter)
    return formatter_class()
