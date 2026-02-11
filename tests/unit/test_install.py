"""
Tests for install.py — Installer class methods.
"""

import json
import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from src.version import get_current_install_files, get_executable_files


# =============================================================================
# Prerequisites
# =============================================================================

class TestPrerequisites:
    """Test check_prerequisites method."""

    def test_passes_with_valid_setup(self, installer_instance):
        assert installer_instance.check_prerequisites() is True

    def test_fails_when_source_file_missing(self, patched_paths):
        from install import Installer

        # Remove one source file
        install_files = get_current_install_files()
        first_src = list(install_files.keys())[0]
        src_path = patched_paths["script_dir"] / first_src
        if src_path.exists():
            src_path.unlink()

        installer = Installer(verbose=False)
        assert installer.check_prerequisites() is False

    def test_fails_when_claude_dir_missing(self, patched_paths):
        from install import Installer
        import shutil

        shutil.rmtree(patched_paths["claude_dir"])

        installer = Installer(verbose=False)
        assert installer.check_prerequisites() is False


# =============================================================================
# Backup
# =============================================================================

class TestBackup:
    """Test create_backup method."""

    def test_creates_backup_of_existing_files(self, installer_instance, patched_paths):
        # Create an existing file that would be overwritten
        claude_dir = patched_paths["claude_dir"]
        (claude_dir / "CLAUDE.md").write_text("# Existing content")

        installer_instance.create_backup()

        assert installer_instance.backup_dir is not None
        assert installer_instance.backup_dir.exists()
        assert (installer_instance.backup_dir / "CLAUDE.md").exists()

    def test_no_backup_on_fresh_install(self, installer_instance, patched_paths):
        # Remove any pre-existing files
        claude_dir = patched_paths["claude_dir"]
        for dest in get_current_install_files().values():
            p = claude_dir / dest
            if p.exists():
                p.unlink()

        installer_instance.create_backup()
        # backup_dir should not be created when no files exist
        assert installer_instance.backup_dir is None or not installer_instance.backup_dir.exists()


# =============================================================================
# Install Files
# =============================================================================

class TestInstallFiles:
    """Test install_files method."""

    def test_installs_all_files(self, installer_instance, patched_paths):
        installer_instance.install_files()

        claude_dir = patched_paths["claude_dir"]
        install_files = get_current_install_files()
        # settings.json is handled by merge_settings, so skip it
        for dest in install_files.values():
            if dest == "settings.json":
                continue
            dest_path = claude_dir / dest
            assert dest_path.exists(), f"File should be installed: {dest}"

    def test_installed_files_tracked(self, installer_instance, patched_paths):
        installer_instance.install_files()
        # 106 total - 1 settings.json = 105
        assert len(installer_instance.installed_files) == 105

    def test_creates_parent_directories(self, installer_instance, patched_paths):
        installer_instance.install_files()

        claude_dir = patched_paths["claude_dir"]
        assert (claude_dir / "commands" / "sc").is_dir()
        assert (claude_dir / "skills" / "planning").is_dir()
        assert (claude_dir / "agents").is_dir()


# =============================================================================
# Executable Permissions
# =============================================================================

class TestExecutablePermissions:
    """Test set_executable_permissions method."""

    def test_sets_executable_on_hooks(self, installer_instance, patched_paths):
        installer_instance.install_files()
        installer_instance.set_executable_permissions()

        claude_dir = patched_paths["claude_dir"]
        for rel_path in get_executable_files():
            path = claude_dir / rel_path
            if path.exists():
                mode = path.stat().st_mode
                assert mode & stat.S_IXUSR, f"Should be executable: {rel_path}"

    def test_sets_executable_on_bin_cq(self, installer_instance, patched_paths):
        installer_instance.install_files()
        installer_instance.set_executable_permissions()

        cq_path = patched_paths["claude_dir"] / "bin" / "cq"
        assert cq_path.exists()
        assert os.access(cq_path, os.X_OK)


# =============================================================================
# Settings Merge
# =============================================================================

class TestSettingsMerge:
    """Test merge_settings method."""

    def test_creates_settings_on_fresh_install(self, installer_instance, patched_paths):
        claude_dir = patched_paths["claude_dir"]
        settings_path = claude_dir / "settings.json"
        if settings_path.exists():
            settings_path.unlink()

        installer_instance.merge_settings()

        assert settings_path.exists()
        data = json.loads(settings_path.read_text())
        assert "hooks" in data
        assert "alwaysThinkingEnabled" in data

    def test_preserves_existing_permissions(
        self, installer_instance, patched_paths, mock_settings_file
    ):
        installer_instance.merge_settings()

        settings_path = patched_paths["claude_dir"] / "settings.json"
        data = json.loads(settings_path.read_text())
        assert "permissions" in data
        assert data["permissions"]["allow"] == ["/usr/local/bin/npm"]

    def test_preserves_existing_custom_settings(
        self, installer_instance, patched_paths, mock_settings_file
    ):
        installer_instance.merge_settings()

        settings_path = patched_paths["claude_dir"] / "settings.json"
        data = json.loads(settings_path.read_text())
        assert data.get("customSetting") == "user-value"

    def test_merges_hooks_without_duplicates(
        self, installer_instance, patched_paths, mock_settings_file
    ):
        installer_instance.merge_settings()

        settings_path = patched_paths["claude_dir"] / "settings.json"
        data = json.loads(settings_path.read_text())
        # Should have both existing custom hook and template hooks
        assert "hooks" in data
        assert "SessionStart" in data["hooks"]

    def test_adds_template_settings_not_in_existing(
        self, installer_instance, patched_paths, mock_settings_file
    ):
        installer_instance.merge_settings()

        settings_path = patched_paths["claude_dir"] / "settings.json"
        data = json.loads(settings_path.read_text())
        assert data.get("alwaysThinkingEnabled") is True


# =============================================================================
# Runtime Dirs
# =============================================================================

class TestRuntimeDirs:
    """Test create_runtime_dirs method."""

    def test_creates_queue_directory(self, installer_instance, patched_paths):
        installer_instance.create_runtime_dirs()
        assert (patched_paths["claude_dir"] / "queue").is_dir()

    def test_creates_backups_directory(self, installer_instance, patched_paths):
        installer_instance.create_runtime_dirs()
        assert (patched_paths["claude_dir"] / "backups").is_dir()

    def test_does_not_fail_if_directory_exists(self, installer_instance, patched_paths):
        (patched_paths["claude_dir"] / "queue").mkdir(exist_ok=True)
        installer_instance.create_runtime_dirs()  # Should not raise


# =============================================================================
# Verification
# =============================================================================

class TestVerification:
    """Test verify_installation method."""

    def test_passes_after_full_install(self, installer_instance, patched_paths):
        installer_instance.install_files()
        installer_instance.merge_settings()
        installer_instance.set_executable_permissions()
        assert installer_instance.verify_installation() is True

    def test_fails_when_file_missing(self, installer_instance, patched_paths):
        installer_instance.install_files()
        installer_instance.merge_settings()
        # Remove a file
        (patched_paths["claude_dir"] / "CLAUDE.md").unlink()
        assert installer_instance.verify_installation() is False


# =============================================================================
# Uninstall
# =============================================================================

class TestUninstall:
    """Test uninstall method."""

    def test_removes_installed_files(self, installer_instance, patched_paths):
        installer_instance.install_files()
        installer_instance.merge_settings()
        installer_instance.uninstall()

        claude_dir = patched_paths["claude_dir"]
        for dest in get_current_install_files().values():
            dest_path = claude_dir / dest
            assert not dest_path.exists(), f"File should be removed: {dest}"

    def test_preserves_tdd_files(self, patched_paths, tdd_populated_claude_dir):
        from install import Installer

        installer = Installer(verbose=False)
        installer.install_files()
        installer.merge_settings()
        installer.uninstall()

        # TDD files should still exist
        claude_dir = patched_paths["claude_dir"]
        assert (claude_dir / "commands" / "sc" / "tdd.md").exists()
        assert (claude_dir / "skills" / "sc-tdd" / "SKILL.md").exists()
        assert (claude_dir / "docs" / "MODE_TDD.md").exists()
        assert (claude_dir / ".tdd-version").exists()


# =============================================================================
# Preserve Agents
# =============================================================================

class TestPreserveAgents:
    """Test --preserve-agents flag behavior."""

    def test_skips_agent_files(self, preserve_agents_installer, patched_paths):
        preserve_agents_installer.install_files()

        claude_dir = patched_paths["claude_dir"]
        # Agent files should NOT be installed
        assert not (claude_dir / "agents" / "developer.md").exists()
        assert not (claude_dir / "agents" / "backend-architect.md").exists()

    def test_installs_non_agent_files(self, preserve_agents_installer, patched_paths):
        preserve_agents_installer.install_files()

        claude_dir = patched_paths["claude_dir"]
        # Non-agent files should still be installed
        assert (claude_dir / "CLAUDE.md").exists()
        assert (claude_dir / "commands" / "sc" / "agent.md").exists()


# =============================================================================
# Dry Run
# =============================================================================

class TestDryRun:
    """Test --dry-run flag behavior."""

    def test_no_files_created(self, dry_run_installer, patched_paths):
        claude_dir = patched_paths["claude_dir"]

        # Remove any pre-existing files to test clean state
        for dest in get_current_install_files().values():
            p = claude_dir / dest
            if p.exists():
                p.unlink()

        dry_run_installer.install_files()

        # No new files should exist (except pre-existing dirs)
        for dest in get_current_install_files().values():
            if dest == "settings.json":
                continue
            dest_path = claude_dir / dest
            assert not dest_path.exists(), f"File should NOT exist in dry run: {dest}"

    def test_no_settings_modified(self, dry_run_installer, patched_paths):
        claude_dir = patched_paths["claude_dir"]
        settings_path = claude_dir / "settings.json"

        original = '{"original": true}'
        settings_path.write_text(original)

        dry_run_installer.merge_settings()

        assert settings_path.read_text() == original

    def test_install_returns_true(self, dry_run_installer):
        assert dry_run_installer.install() is True
