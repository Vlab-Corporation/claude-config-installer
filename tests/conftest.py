"""
Shared pytest fixtures for the SuperClaude Config Installer test suite.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict
from unittest.mock import patch

import pytest


# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Mock Claude Environment
# =============================================================================

@pytest.fixture
def mock_claude_dir(tmp_path):
    """Create a mock ~/.claude directory structure."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)

    # Standard Claude Code directories
    (claude_dir / "commands" / "sc").mkdir(parents=True)
    (claude_dir / "commands" / "queue").mkdir(parents=True)
    (claude_dir / "skills" / "planning").mkdir(parents=True)
    (claude_dir / "skills" / "drawio2drawio").mkdir(parents=True)
    (claude_dir / "skills" / "task-queue").mkdir(parents=True)
    (claude_dir / "agents").mkdir()
    (claude_dir / "docs").mkdir()
    (claude_dir / "scripts").mkdir()
    (claude_dir / "hooks").mkdir()
    (claude_dir / "lib").mkdir()
    (claude_dir / "bin").mkdir()
    (claude_dir / "tests").mkdir()
    (claude_dir / "backups").mkdir()

    return claude_dir


@pytest.fixture
def mock_home_dir(tmp_path, mock_claude_dir):
    """Create a mock home directory with .claude subdirectory."""
    return tmp_path


@pytest.fixture
def mock_source_files(tmp_path):
    """
    Create mock source files matching the 106-file install mapping
    plus optional agent files.
    """
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    from src.version import get_current_install_files, get_agent_files

    all_files = {}
    all_files.update(get_current_install_files())
    all_files.update(get_agent_files())

    for src_path in all_files.keys():
        full_path = source_dir / src_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.endswith(".json"):
            if "settings" in src_path:
                content = json.dumps({
                    "hooks": {
                        "SessionStart": [{
                            "matcher": "",
                            "hooks": [{
                                "type": "command",
                                "command": "$HOME/.claude/hooks/queue-session-start.sh",
                                "timeout": 10,
                            }],
                        }],
                        "Stop": [{
                            "matcher": "",
                            "hooks": [{
                                "type": "command",
                                "command": "$HOME/.claude/hooks/queue-auto-execute.sh",
                                "timeout": 10,
                            }],
                        }],
                    },
                    "alwaysThinkingEnabled": True,
                }, indent=2)
            else:
                content = json.dumps({"version": "1.0.0"}, indent=2)
        elif src_path.endswith(".sh"):
            content = "#!/bin/bash\necho 'test hook'"
        elif src_path.endswith(".py"):
            content = "# test python file\n"
        elif "bin/cq" in src_path:
            content = "#!/bin/bash\necho 'test bin'"
        else:
            basename = Path(src_path).stem
            content = f"# {basename}\nTest content for {src_path}."

        full_path.write_text(content)

    return source_dir


@pytest.fixture
def patched_paths(mock_home_dir, mock_source_files):
    """Patch CLAUDE_DIR and SCRIPT_DIR constants in install.py."""
    mock_version_file = mock_home_dir / ".claude" / ".superclaude-installer-version"
    mock_agent_version_file = mock_home_dir / ".claude" / ".superclaude-agents-installed"
    with patch.multiple(
        "install",
        CLAUDE_DIR=mock_home_dir / ".claude",
        SCRIPT_DIR=mock_source_files,
    ):
        with patch("src.version.VERSION_FILE", mock_version_file):
            with patch("src.version.AGENT_VERSION_FILE", mock_agent_version_file):
                yield {
                    "claude_dir": mock_home_dir / ".claude",
                    "script_dir": mock_source_files,
                    "version_file": mock_version_file,
                    "agent_version_file": mock_agent_version_file,
                }


@pytest.fixture
def installer_instance(patched_paths):
    """Create an Installer instance with patched paths."""
    from install import Installer
    return Installer(verbose=True)


@pytest.fixture
def silent_installer(patched_paths):
    """Create an Installer instance with verbose=False."""
    from install import Installer
    return Installer(verbose=False)


@pytest.fixture
def dry_run_installer(patched_paths):
    """Create an Installer instance with dry_run=True."""
    from install import Installer
    return Installer(verbose=True, dry_run=True)


@pytest.fixture
def preserve_agents_installer(patched_paths):
    """Create an Installer instance with preserve_agents=True."""
    from install import Installer
    return Installer(verbose=True, preserve_agents=True)


# =============================================================================
# Settings Fixtures
# =============================================================================

@pytest.fixture
def mock_settings_file(mock_claude_dir):
    """Create a mock existing settings.json with user permissions."""
    settings = {
        "permissions": {
            "allow": ["/usr/local/bin/npm"],
            "deny": ["/usr/sbin/rm"],
        },
        "hooks": {
            "SessionStart": [{
                "matcher": "",
                "hooks": [{
                    "type": "command",
                    "command": "$HOME/.claude/hooks/custom-hook.sh",
                    "timeout": 5,
                }],
            }],
        },
        "customSetting": "user-value",
    }
    settings_path = mock_claude_dir / "settings.json"
    settings_path.write_text(json.dumps(settings, indent=2))
    return settings_path


# =============================================================================
# Populated Directory Fixtures
# =============================================================================

@pytest.fixture
def populated_claude_dir(mock_claude_dir):
    """Create a Claude directory with pre-existing SuperClaude files."""
    (mock_claude_dir / "CLAUDE.md").write_text("# Old CLAUDE.md\nPrevious version.")
    (mock_claude_dir / "FLAGS.md").write_text("# Old FLAGS\nPrevious version.")
    (mock_claude_dir / "agents" / "developer.md").write_text("# Old developer agent")
    return mock_claude_dir


@pytest.fixture
def tdd_populated_claude_dir(mock_claude_dir):
    """Create a Claude directory with TDD project files that must be preserved."""
    # TDD commands
    (mock_claude_dir / "commands" / "sc" / "tdd.md").write_text("# TDD command")
    (mock_claude_dir / "commands" / "sc" / "tdd-backend.md").write_text("# TDD backend")
    (mock_claude_dir / "commands" / "sc" / "tdd-uiux.md").write_text("# TDD uiux")

    # TDD skills
    (mock_claude_dir / "skills" / "sc-tdd").mkdir(parents=True, exist_ok=True)
    (mock_claude_dir / "skills" / "sc-tdd" / "SKILL.md").write_text("# TDD skill")
    (mock_claude_dir / "skills" / "sc-tdd-backend").mkdir(parents=True, exist_ok=True)
    (mock_claude_dir / "skills" / "sc-tdd-backend" / "SKILL.md").write_text("# TDD backend skill")
    (mock_claude_dir / "skills" / "sc-tdd-uiux").mkdir(parents=True, exist_ok=True)
    (mock_claude_dir / "skills" / "sc-tdd-uiux" / "SKILL.md").write_text("# TDD uiux skill")

    # TDD docs
    (mock_claude_dir / "docs" / "MODE_TDD.md").write_text("# TDD mode")
    (mock_claude_dir / "docs" / "MODE_TDD_BACKEND.md").write_text("# TDD backend mode")
    (mock_claude_dir / "docs" / "MODE_TDD_UIUX.md").write_text("# TDD uiux mode")

    # TDD version files
    (mock_claude_dir / ".tdd-version").write_text("2.2.0")
    (mock_claude_dir / ".tdd-agents-installed").write_text("2.2.0")

    return mock_claude_dir


# =============================================================================
# Uninstall-specific Fixtures
# =============================================================================

@pytest.fixture
def clean_all_installer(patched_paths):
    """Create an Installer instance with clean_all=True."""
    from install import Installer
    return Installer(verbose=True, clean_all=True)


@pytest.fixture
def with_agents_installer(patched_paths):
    """Create an Installer instance with install_agents=True."""
    from install import Installer
    return Installer(verbose=True, install_agents=True)


@pytest.fixture
def no_agents_installer(patched_paths):
    """Create an Installer instance with install_agents=False."""
    from install import Installer
    return Installer(verbose=True, install_agents=False)


# =============================================================================
# Test Markers
# =============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (may use file system)")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to execute")
