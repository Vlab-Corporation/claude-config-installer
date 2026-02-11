"""
Integration tests for the full install/uninstall cycle.
"""

import json
import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from src.version import get_current_install_files, get_executable_files


@pytest.mark.integration
class TestFullInstallUninstallCycle:
    """Test complete install -> verify -> uninstall -> verify cycle."""

    def test_full_cycle(self, patched_paths, mock_source_files):
        from install import Installer

        claude_dir = patched_paths["claude_dir"]

        # Install
        installer = Installer(verbose=True)
        assert installer.install() is True

        # Verify all files exist
        for dest in get_current_install_files().values():
            assert (claude_dir / dest).exists(), f"Missing after install: {dest}"

        # Verify version file
        version_file = patched_paths["version_file"]
        assert version_file.exists()

        # Uninstall
        installer2 = Installer(verbose=True)
        assert installer2.uninstall() is True

        # Verify files removed
        for dest in get_current_install_files().values():
            assert not (claude_dir / dest).exists(), f"Should be removed: {dest}"


@pytest.mark.integration
class TestInstallOnEmptyClaudeDir:
    """Test installation on a clean ~/.claude/ directory."""

    def test_installs_all_files_from_scratch(self, patched_paths):
        from install import Installer

        claude_dir = patched_paths["claude_dir"]

        installer = Installer(verbose=True)
        assert installer.install() is True

        installed_count = sum(
            1
            for dest in get_current_install_files().values()
            if (claude_dir / dest).exists()
        )
        assert installed_count == len(get_current_install_files())


@pytest.mark.integration
class TestInstallPreservesTddFiles:
    """Test that installation does not touch TDD project files."""

    def test_tdd_files_preserved_after_install(
        self, patched_paths, tdd_populated_claude_dir
    ):
        from install import Installer

        claude_dir = patched_paths["claude_dir"]

        installer = Installer(verbose=True)
        installer.install()

        # TDD files should still exist
        assert (claude_dir / "commands" / "sc" / "tdd.md").exists()
        assert (claude_dir / "commands" / "sc" / "tdd-backend.md").exists()
        assert (claude_dir / "commands" / "sc" / "tdd-uiux.md").exists()
        assert (claude_dir / "skills" / "sc-tdd" / "SKILL.md").exists()
        assert (claude_dir / "docs" / "MODE_TDD.md").exists()
        assert (claude_dir / ".tdd-version").exists()

    def test_tdd_files_preserved_after_uninstall(
        self, patched_paths, tdd_populated_claude_dir
    ):
        from install import Installer

        claude_dir = patched_paths["claude_dir"]

        installer = Installer(verbose=True)
        installer.install()
        installer.uninstall()

        assert (claude_dir / "commands" / "sc" / "tdd.md").exists()
        assert (claude_dir / "skills" / "sc-tdd" / "SKILL.md").exists()
        assert (claude_dir / "docs" / "MODE_TDD.md").exists()
        assert (claude_dir / ".tdd-version").exists()


@pytest.mark.integration
class TestSettingsMergePreservesPermissions:
    """Test that settings merge preserves user permissions."""

    def test_permissions_preserved(self, patched_paths, mock_settings_file):
        from install import Installer

        installer = Installer(verbose=True)
        installer.merge_settings()

        settings_path = patched_paths["claude_dir"] / "settings.json"
        data = json.loads(settings_path.read_text())
        assert "permissions" in data
        assert data["permissions"]["allow"] == ["/usr/local/bin/npm"]
        assert data["permissions"]["deny"] == ["/usr/sbin/rm"]


@pytest.mark.integration
class TestHooksHaveExecutablePermissions:
    """Test that hooks have correct permissions after install."""

    def test_all_hooks_executable(self, patched_paths):
        from install import Installer

        installer = Installer(verbose=True)
        installer.install()

        claude_dir = patched_paths["claude_dir"]
        for rel_path in get_executable_files():
            path = claude_dir / rel_path
            assert path.exists(), f"Executable file should exist: {rel_path}"
            mode = path.stat().st_mode
            assert mode & stat.S_IXUSR, f"Should have user execute: {rel_path}"


@pytest.mark.integration
class TestPreserveAgentsFlag:
    """Test --preserve-agents flag in full install cycle."""

    def test_agents_not_installed_with_flag(self, patched_paths):
        from install import Installer

        claude_dir = patched_paths["claude_dir"]

        installer = Installer(verbose=True, preserve_agents=True)
        installer.install()

        # Agent files should NOT be installed
        assert not (claude_dir / "agents" / "developer.md").exists()
        assert not (claude_dir / "agents" / "backend-architect.md").exists()

        # Other files should be installed
        assert (claude_dir / "CLAUDE.md").exists()
        assert (claude_dir / "FLAGS.md").exists()
        assert (claude_dir / "commands" / "sc" / "agent.md").exists()

    def test_existing_agents_preserved(self, patched_paths):
        from install import Installer

        claude_dir = patched_paths["claude_dir"]

        # Create a pre-existing custom agent
        (claude_dir / "agents").mkdir(parents=True, exist_ok=True)
        (claude_dir / "agents" / "my-custom-agent.md").write_text("# Custom agent")

        installer = Installer(verbose=True, preserve_agents=True)
        installer.install()

        # Custom agent should still exist
        assert (claude_dir / "agents" / "my-custom-agent.md").exists()
