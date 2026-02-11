"""
SuperClaude Config Installer - Version information.

This module provides version information for the SuperClaude Config Installer.
The version follows semantic versioning (MAJOR.MINOR.PATCH).

Usage:
    from src.version import __version__, get_version

    print(f"SuperClaude Config v{__version__}")
    print(get_version())
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


__version__ = "1.1.0"
__version_info__ = tuple(int(x) for x in __version__.split("."))

# Metadata
__title__ = "SuperClaude Config"
__description__ = "Installs SuperClaude framework configuration to ~/.claude/"
__author__ = "TerryJoo"
__email__ = "jooyungik@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/Vlab-Corporation/claude-config-installer"


# =============================================================================
# Version File for Installed Version Tracking
# =============================================================================

VERSION_FILE = Path.home() / ".claude" / ".superclaude-installer-version"


# =============================================================================
# Version Migration Registry
# =============================================================================
#
# Each version entry contains:
#   - description: Human-readable description of the version
#   - install_files: Dict of source -> destination paths installed by this version
#   - executable_files: List of files that need chmod +x
#   - runtime_dirs: List of directories to create at install time
#   - legacy_files: List of files/dirs to remove when upgrading TO this version
#   - changes: List of changes in this version
#
# IMPORTANT: This is the Single Source of Truth (SSOT) for all file mappings.
# install.py reads from here - do NOT duplicate file lists elsewhere.
# =============================================================================

VERSION_MIGRATIONS: Dict[str, Dict[str, Any]] = {
    "1.0.0": {
        "description": "Initial SuperClaude framework installation",
        "install_files": {
            # === Root Config (24) ===
            "src/root/CLAUDE.md": "CLAUDE.md",
            "src/root/BUSINESS_PANEL_EXAMPLES.md": "BUSINESS_PANEL_EXAMPLES.md",
            "src/root/BUSINESS_SYMBOLS.md": "BUSINESS_SYMBOLS.md",
            "src/root/FLAGS.md": "FLAGS.md",
            "src/root/PRINCIPLES.md": "PRINCIPLES.md",
            "src/root/RESEARCH_CONFIG.md": "RESEARCH_CONFIG.md",
            "src/root/RULES.md": "RULES.md",
            "src/root/MODE_Brainstorming.md": "MODE_Brainstorming.md",
            "src/root/MODE_Business_Panel.md": "MODE_Business_Panel.md",
            "src/root/MODE_DeepResearch.md": "MODE_DeepResearch.md",
            "src/root/MODE_Introspection.md": "MODE_Introspection.md",
            "src/root/MODE_Orchestration.md": "MODE_Orchestration.md",
            "src/root/MODE_Task_Management.md": "MODE_Task_Management.md",
            "src/root/MODE_Task_Queue.md": "MODE_Task_Queue.md",
            "src/root/MODE_Token_Efficiency.md": "MODE_Token_Efficiency.md",
            "src/root/MCP_Context7.md": "MCP_Context7.md",
            "src/root/MCP_Magic.md": "MCP_Magic.md",
            "src/root/MCP_Morphllm.md": "MCP_Morphllm.md",
            "src/root/MCP_Playwright.md": "MCP_Playwright.md",
            "src/root/MCP_Sequential.md": "MCP_Sequential.md",
            "src/root/MCP_Serena.md": "MCP_Serena.md",
            "src/root/MCP_Tavily.md": "MCP_Tavily.md",
            "src/root/settings.json": "settings.json",
            "src/root/.superclaude-metadata.json": ".superclaude-metadata.json",
            # === Agents (17) ===
            "src/agents/backend-architect.md": "agents/backend-architect.md",
            "src/agents/business-panel-experts.md": "agents/business-panel-experts.md",
            "src/agents/deep-research-agent.md": "agents/deep-research-agent.md",
            "src/agents/developer.md": "agents/developer.md",
            "src/agents/devops-architect.md": "agents/devops-architect.md",
            "src/agents/frontend-architect.md": "agents/frontend-architect.md",
            "src/agents/learning-guide.md": "agents/learning-guide.md",
            "src/agents/performance-engineer.md": "agents/performance-engineer.md",
            "src/agents/python-expert.md": "agents/python-expert.md",
            "src/agents/quality-engineer.md": "agents/quality-engineer.md",
            "src/agents/refactoring-expert.md": "agents/refactoring-expert.md",
            "src/agents/requirements-analyst.md": "agents/requirements-analyst.md",
            "src/agents/root-cause-analyst.md": "agents/root-cause-analyst.md",
            "src/agents/security-engineer.md": "agents/security-engineer.md",
            "src/agents/socratic-mentor.md": "agents/socratic-mentor.md",
            "src/agents/system-architect.md": "agents/system-architect.md",
            "src/agents/technical-writer.md": "agents/technical-writer.md",
            # === Commands/Queue (5) ===
            "src/commands/queue.md": "commands/queue.md",
            "src/commands/queue/cancel.md": "commands/queue/cancel.md",
            "src/commands/queue/list.md": "commands/queue/list.md",
            "src/commands/queue/move.md": "commands/queue/move.md",
            "src/commands/queue/next.md": "commands/queue/next.md",
            # === Commands/SC (33) ===
            "src/commands/sc/README.md": "commands/sc/README.md",
            "src/commands/sc/agent.md": "commands/sc/agent.md",
            "src/commands/sc/analyze.md": "commands/sc/analyze.md",
            "src/commands/sc/brainstorm.md": "commands/sc/brainstorm.md",
            "src/commands/sc/build.md": "commands/sc/build.md",
            "src/commands/sc/business-panel.md": "commands/sc/business-panel.md",
            "src/commands/sc/cleanup.md": "commands/sc/cleanup.md",
            "src/commands/sc/design.md": "commands/sc/design.md",
            "src/commands/sc/document.md": "commands/sc/document.md",
            "src/commands/sc/drawio2drawio.md": "commands/sc/drawio2drawio.md",
            "src/commands/sc/estimate.md": "commands/sc/estimate.md",
            "src/commands/sc/explain.md": "commands/sc/explain.md",
            "src/commands/sc/git.md": "commands/sc/git.md",
            "src/commands/sc/help.md": "commands/sc/help.md",
            "src/commands/sc/implement.md": "commands/sc/implement.md",
            "src/commands/sc/improve.md": "commands/sc/improve.md",
            "src/commands/sc/index.md": "commands/sc/index.md",
            "src/commands/sc/index-repo.md": "commands/sc/index-repo.md",
            "src/commands/sc/load.md": "commands/sc/load.md",
            "src/commands/sc/planning.md": "commands/sc/planning.md",
            "src/commands/sc/pm.md": "commands/sc/pm.md",
            "src/commands/sc/recommend.md": "commands/sc/recommend.md",
            "src/commands/sc/reflect.md": "commands/sc/reflect.md",
            "src/commands/sc/research.md": "commands/sc/research.md",
            "src/commands/sc/save.md": "commands/sc/save.md",
            "src/commands/sc/sc.md": "commands/sc/sc.md",
            "src/commands/sc/select-tool.md": "commands/sc/select-tool.md",
            "src/commands/sc/spawn.md": "commands/sc/spawn.md",
            "src/commands/sc/spec-panel.md": "commands/sc/spec-panel.md",
            "src/commands/sc/task.md": "commands/sc/task.md",
            "src/commands/sc/test.md": "commands/sc/test.md",
            "src/commands/sc/troubleshoot.md": "commands/sc/troubleshoot.md",
            "src/commands/sc/workflow.md": "commands/sc/workflow.md",
            # === Skills/Planning (8) ===
            "src/skills/planning/SKILL.md": "skills/planning/SKILL.md",
            "src/skills/planning/CONVENTION_TRACKER.md": "skills/planning/CONVENTION_TRACKER.md",
            "src/skills/planning/DOMAIN_EXPERTS.md": "skills/planning/DOMAIN_EXPERTS.md",
            "src/skills/planning/ERROR_HANDLING.md": "skills/planning/ERROR_HANDLING.md",
            "src/skills/planning/EXAMPLES.md": "skills/planning/EXAMPLES.md",
            "src/skills/planning/REVIEW_CRITERIA.md": "skills/planning/REVIEW_CRITERIA.md",
            "src/skills/planning/REVIEW_FORMAT.md": "skills/planning/REVIEW_FORMAT.md",
            "src/skills/planning/TEST_SCENARIOS.md": "skills/planning/TEST_SCENARIOS.md",
            # === Skills/Drawio2drawio (4) ===
            "src/skills/drawio2drawio/SKILL.md": "skills/drawio2drawio/SKILL.md",
            "src/skills/drawio2drawio/ANALYSIS_SCHEMA.md": "skills/drawio2drawio/ANALYSIS_SCHEMA.md",
            "src/skills/drawio2drawio/PIPELINE.md": "skills/drawio2drawio/PIPELINE.md",
            "src/skills/drawio2drawio/SHAPE_STANDARDS.md": "skills/drawio2drawio/SHAPE_STANDARDS.md",
            # === Skills/Task-Queue (1) ===
            "src/skills/task-queue/SKILL.md": "skills/task-queue/SKILL.md",
            # === Docs (1) ===
            "src/docs/ANALYZE_COMMAND.md": "docs/ANALYZE_COMMAND.md",
            # === Scripts (6) ===
            "src/scripts/auto_continue.py": "scripts/auto_continue.py",
            "src/scripts/auto_queue_hook.py": "scripts/auto_queue_hook.py",
            "src/scripts/parallel_executor.py": "scripts/parallel_executor.py",
            "src/scripts/queue_manager.py": "scripts/queue_manager.py",
            "src/scripts/session_context.py": "scripts/session_context.py",
            "src/scripts/task_analyzer.py": "scripts/task_analyzer.py",
            # === Hooks (3) ===
            "src/hooks/queue-auto-execute.sh": "hooks/queue-auto-execute.sh",
            "src/hooks/queue-session-start.sh": "hooks/queue-session-start.sh",
            "src/hooks/queue-user-prompt.sh": "hooks/queue-user-prompt.sh",
            # === Lib (2) ===
            "src/lib/formatters.py": "lib/formatters.py",
            "src/lib/version.py": "lib/version.py",
            # === Bin (1) ===
            "src/bin/cq": "bin/cq",
            # === Tests (1) ===
            "src/tests/test_scope_analysis.py": "tests/test_scope_analysis.py",
        },
        "executable_files": [
            "hooks/queue-auto-execute.sh",
            "hooks/queue-session-start.sh",
            "hooks/queue-user-prompt.sh",
            "bin/cq",
        ],
        "runtime_dirs": [
            "queue",
            "backups",
        ],
        "legacy_files": [],
        "changes": [
            "Initial release with 106 SuperClaude framework files",
        ],
    },
    "1.1.0": {
        "description": "Improved uninstall with settings unmerge, backup, and cleanup",
        "install_files": {},
        "executable_files": [],
        "runtime_dirs": [],
        "legacy_files": [],
        "changes": [
            "Add unmerge_settings() to reverse settings.json merge on uninstall",
            "Create backup before uninstall with superclaude_uninstall_ prefix",
            "Honor --preserve-agents flag during uninstall",
            "Add runtime directory cleanup on uninstall",
            "Add --clean-all flag for complete removal including backups",
        ],
    },
}


# =============================================================================
# Version Utility Functions
# =============================================================================

def get_version() -> str:
    """Return the current version string."""
    return __version__


def get_version_info() -> tuple:
    """Return the version as a tuple of integers (major, minor, patch)."""
    return __version_info__


def get_full_version_string() -> str:
    """Return a full version string with title."""
    return f"{__title__} v{__version__}"


# =============================================================================
# Install File Functions
# =============================================================================

def get_current_install_files() -> Dict[str, str]:
    """
    Get the install file mapping for the current version.

    Accumulates install_files from all versions up to and including the current
    version. Later versions can override earlier entries for the same source path.

    This is the Single Source of Truth (SSOT) for what files should be installed.

    Returns:
        Dict mapping source paths to destination paths
    """
    all_files: Dict[str, str] = {}
    for version in sorted(VERSION_MIGRATIONS.keys(), key=lambda v: tuple(int(x) for x in v.split("."))):
        v_tuple = tuple(int(x) for x in version.split("."))
        if v_tuple <= __version_info__:
            all_files.update(VERSION_MIGRATIONS[version].get("install_files", {}))
    return all_files


def get_all_historical_files() -> List[str]:
    """
    Get all destination files that have ever been installed by any version.

    Returns:
        List of unique destination paths (relative to CLAUDE_DIR) from all versions
    """
    all_files = set()

    for migration in VERSION_MIGRATIONS.values():
        install_files = migration.get("install_files", {})
        for dest in install_files.values():
            all_files.add(dest)

        for legacy in migration.get("legacy_files", []):
            all_files.add(legacy)

    return sorted(list(all_files))


def get_files_to_uninstall() -> List[str]:
    """
    Get comprehensive list of files to remove during uninstall.

    Returns:
        List of unique file/directory paths to remove
    """
    return get_all_historical_files()


def get_executable_files() -> List[str]:
    """
    Get list of files that need executable permissions.

    Accumulates executable_files from all versions up to current.

    Returns:
        List of destination paths that need chmod +x
    """
    result: List[str] = []
    for version in sorted(VERSION_MIGRATIONS.keys(), key=lambda v: tuple(int(x) for x in v.split("."))):
        v_tuple = tuple(int(x) for x in version.split("."))
        if v_tuple <= __version_info__:
            for f in VERSION_MIGRATIONS[version].get("executable_files", []):
                if f not in result:
                    result.append(f)
    return result


def get_runtime_dirs() -> List[str]:
    """
    Get list of runtime directories to create during installation.

    Accumulates runtime_dirs from all versions up to current.

    Returns:
        List of directory paths relative to CLAUDE_DIR
    """
    result: List[str] = []
    for version in sorted(VERSION_MIGRATIONS.keys(), key=lambda v: tuple(int(x) for x in v.split("."))):
        v_tuple = tuple(int(x) for x in version.split("."))
        if v_tuple <= __version_info__:
            for d in VERSION_MIGRATIONS[version].get("runtime_dirs", []):
                if d not in result:
                    result.append(d)
    return result


# =============================================================================
# Legacy File Functions
# =============================================================================

def get_legacy_files_to_remove(from_version: Optional[str] = None) -> List[str]:
    """
    Get list of legacy files to remove when upgrading.

    Args:
        from_version: The version to upgrade from, or None for fresh install

    Returns:
        List of relative paths to legacy files/directories to remove
    """
    if from_version is None:
        from_version = get_installed_version()

    if from_version is None:
        return []

    try:
        from_tuple = tuple(int(x) for x in from_version.split("."))
    except (ValueError, AttributeError):
        return []

    legacy_files = []
    for version, migration in VERSION_MIGRATIONS.items():
        version_tuple = tuple(int(x) for x in version.split("."))
        if version_tuple > from_tuple:
            for legacy_file in migration.get("legacy_files", []):
                if legacy_file not in legacy_files:
                    legacy_files.append(legacy_file)

    return legacy_files


# =============================================================================
# Installed Version Tracking
# =============================================================================

def get_installed_version() -> Optional[str]:
    """
    Get the currently installed version from the version file.

    Returns:
        Version string if file exists and is valid, None otherwise
    """
    try:
        if not VERSION_FILE.exists():
            return None

        content = VERSION_FILE.read_text().strip()

        parts = content.split(".")
        if len(parts) != 3:
            return None

        for part in parts:
            if not part.isdigit():
                return None

        return content
    except Exception:
        return None


def save_installed_version() -> bool:
    """
    Save the current version to the version file.

    Returns:
        True if successful, False otherwise
    """
    try:
        VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        VERSION_FILE.write_text(__version__)
        return True
    except Exception:
        return False
