"""
E2E tests for install.sh — the shell wrapper for the SuperClaude Config Installer.

These tests run install.sh as a subprocess with a fake HOME directory,
verifying argument forwarding, banner display, exit codes, and file operations.
"""

import os
import subprocess
from pathlib import Path

import pytest

from src.version import (
    __version__,
    get_current_install_files,
    get_executable_files,
    get_agent_files,
)


PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
INSTALL_SH = PROJECT_ROOT / "install.sh"


def run_install_sh(*args, home_dir=None, env_extra=None, timeout=60):
    """Run install.sh with given args and return CompletedProcess."""
    env = os.environ.copy()
    if home_dir:
        env["HOME"] = str(home_dir)
    if env_extra:
        env.update(env_extra)

    result = subprocess.run(
        ["bash", str(INSTALL_SH)] + list(args),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(PROJECT_ROOT),
        timeout=timeout,
    )
    return result


@pytest.fixture
def fake_home(tmp_path):
    """Create a fake HOME directory with .claude/ pre-created."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".claude").mkdir()
    return home


# =============================================================================
# --version flag
# =============================================================================


@pytest.mark.e2e
class TestInstallShVersionFlag:
    """Test install.sh --version flag."""

    def test_shows_version_string(self, fake_home):
        result = run_install_sh("--version", home_dir=fake_home)
        assert result.returncode == 0
        assert __version__ in result.stdout

    def test_shows_install_path(self, fake_home):
        result = run_install_sh("--version", home_dir=fake_home)
        assert ".claude" in result.stdout


# =============================================================================
# --list-files flag
# =============================================================================


@pytest.mark.e2e
class TestInstallShListFilesFlag:
    """Test install.sh --list-files flag."""

    def test_lists_files_and_exits_zero(self, fake_home):
        result = run_install_sh("--list-files", home_dir=fake_home)
        assert result.returncode == 0
        assert "CLAUDE.md" in result.stdout

    def test_shows_file_count(self, fake_home):
        result = run_install_sh("--list-files", home_dir=fake_home)
        expected_count = len(get_current_install_files())
        assert str(expected_count) in result.stdout

    def test_shows_optional_agents_section(self, fake_home):
        result = run_install_sh("--list-files", home_dir=fake_home)
        assert "Optional TDD agents" in result.stdout
        assert "tdd-coach.md" in result.stdout

    def test_shows_executable_files_section(self, fake_home):
        result = run_install_sh("--list-files", home_dir=fake_home)
        assert "Executable files" in result.stdout

    def test_shows_runtime_dirs_section(self, fake_home):
        result = run_install_sh("--list-files", home_dir=fake_home)
        assert "Runtime directories" in result.stdout


# =============================================================================
# Version banner (from install.sh show_version)
# =============================================================================


@pytest.mark.e2e
class TestInstallShVersionBanner:
    """Test that install.sh displays the version banner before install.py runs."""

    def test_shows_shell_banner(self, fake_home):
        result = run_install_sh("--dry-run", "--no-agents", home_dir=fake_home)
        # install.sh show_version outputs "SuperClaude Config Installer v<version>"
        assert "SuperClaude Config Installer" in result.stdout
        assert __version__ in result.stdout

    def test_shows_separator_lines(self, fake_home):
        result = run_install_sh("--dry-run", "--no-agents", home_dir=fake_home)
        assert "==========" in result.stdout


# =============================================================================
# --dry-run mode
# =============================================================================


@pytest.mark.e2e
class TestInstallShDryRun:
    """Test install.sh --dry-run mode (no files should be modified)."""

    def test_dry_run_exits_zero(self, fake_home):
        result = run_install_sh("--dry-run", "--no-agents", home_dir=fake_home)
        assert result.returncode == 0

    def test_dry_run_no_files_created(self, fake_home):
        run_install_sh("--dry-run", "--no-agents", home_dir=fake_home)
        claude_dir = fake_home / ".claude"
        assert not (claude_dir / "CLAUDE.md").exists()
        assert not (claude_dir / "FLAGS.md").exists()

    def test_dry_run_output_indicates_preview(self, fake_home):
        result = run_install_sh("--dry-run", "--no-agents", home_dir=fake_home)
        assert "DRY RUN" in result.stdout

    def test_dry_run_with_verbose(self, fake_home):
        result = run_install_sh(
            "--dry-run", "--verbose", "--no-agents", home_dir=fake_home
        )
        assert result.returncode == 0
        assert "Would" in result.stdout


# =============================================================================
# Actual install
# =============================================================================


@pytest.mark.e2e
class TestInstallShActualInstall:
    """Test install.sh actual installation on a fake HOME."""

    def test_installs_all_files(self, fake_home):
        result = run_install_sh("--no-agents", home_dir=fake_home)
        assert result.returncode == 0

        claude_dir = fake_home / ".claude"
        for dest in get_current_install_files().values():
            assert (claude_dir / dest).exists(), f"Missing: {dest}"

    def test_sets_executable_permissions(self, fake_home):
        run_install_sh("--no-agents", home_dir=fake_home)

        claude_dir = fake_home / ".claude"
        for rel_path in get_executable_files():
            path = claude_dir / rel_path
            assert path.exists(), f"Executable should exist: {rel_path}"
            assert os.access(path, os.X_OK), f"Should be executable: {rel_path}"

    def test_creates_version_file(self, fake_home):
        run_install_sh("--no-agents", home_dir=fake_home)

        version_file = fake_home / ".claude" / ".superclaude-installer-version"
        assert version_file.exists()
        assert __version__ in version_file.read_text()

    def test_creates_runtime_dirs(self, fake_home):
        run_install_sh("--no-agents", home_dir=fake_home)

        claude_dir = fake_home / ".claude"
        assert (claude_dir / "queue").exists()
        assert (claude_dir / "backups").exists()

    def test_success_message_displayed(self, fake_home):
        result = run_install_sh("--no-agents", home_dir=fake_home)
        assert "Installation completed successfully" in result.stdout


# =============================================================================
# Uninstall
# =============================================================================


@pytest.mark.e2e
class TestInstallShUninstall:
    """Test install.sh --uninstall on fake HOME."""

    def test_uninstall_removes_files(self, fake_home):
        # Install first
        run_install_sh("--no-agents", home_dir=fake_home)
        claude_dir = fake_home / ".claude"
        assert (claude_dir / "CLAUDE.md").exists()

        # Then uninstall
        result = run_install_sh("--uninstall", home_dir=fake_home)
        assert result.returncode == 0
        assert not (claude_dir / "CLAUDE.md").exists()

    def test_uninstall_creates_backup(self, fake_home):
        run_install_sh("--no-agents", home_dir=fake_home)
        run_install_sh("--uninstall", home_dir=fake_home)

        backups_dir = fake_home / ".claude" / "backups"
        assert backups_dir.exists()
        backup_dirs = [
            d
            for d in backups_dir.iterdir()
            if d.name.startswith("superclaude_uninstall_")
        ]
        assert len(backup_dirs) >= 1

    def test_uninstall_removes_version_file(self, fake_home):
        run_install_sh("--no-agents", home_dir=fake_home)

        version_file = fake_home / ".claude" / ".superclaude-installer-version"
        assert version_file.exists()

        run_install_sh("--uninstall", home_dir=fake_home)
        assert not version_file.exists()


# =============================================================================
# --with-agents / --no-agents flag forwarding
# =============================================================================


@pytest.mark.e2e
class TestInstallShWithAgents:
    """Test --with-agents and --no-agents flag forwarding."""

    def test_with_agents_installs_tdd_agents(self, fake_home):
        result = run_install_sh("--with-agents", home_dir=fake_home)
        assert result.returncode == 0

        claude_dir = fake_home / ".claude"
        for dest in get_agent_files().values():
            assert (claude_dir / dest).exists(), f"Agent missing: {dest}"

    def test_no_agents_skips_tdd_agents(self, fake_home):
        result = run_install_sh("--no-agents", home_dir=fake_home)
        assert result.returncode == 0

        claude_dir = fake_home / ".claude"
        for dest in get_agent_files().values():
            assert not (claude_dir / dest).exists(), f"Should not exist: {dest}"

    def test_with_agents_creates_tracking_file(self, fake_home):
        run_install_sh("--with-agents", home_dir=fake_home)

        tracking_file = fake_home / ".claude" / ".superclaude-agents-installed"
        assert tracking_file.exists()

    def test_uninstall_after_with_agents_removes_agents(self, fake_home):
        run_install_sh("--with-agents", home_dir=fake_home)

        claude_dir = fake_home / ".claude"
        for dest in get_agent_files().values():
            assert (claude_dir / dest).exists()

        run_install_sh("--uninstall", home_dir=fake_home)
        for dest in get_agent_files().values():
            assert not (claude_dir / dest).exists(), f"Agent should be removed: {dest}"


# =============================================================================
# --preserve-agents flag forwarding
# =============================================================================


@pytest.mark.e2e
class TestInstallShPreserveAgents:
    """Test --preserve-agents flag forwarding."""

    def test_preserve_agents_skips_standard_agents(self, fake_home):
        result = run_install_sh(
            "--preserve-agents", "--no-agents", home_dir=fake_home
        )
        assert result.returncode == 0

        claude_dir = fake_home / ".claude"
        # Standard agents should NOT be installed
        assert not (claude_dir / "agents" / "developer.md").exists()
        assert not (claude_dir / "agents" / "backend-architect.md").exists()

        # Other files should be installed
        assert (claude_dir / "CLAUDE.md").exists()
        assert (claude_dir / "FLAGS.md").exists()


# =============================================================================
# Claude directory creation
# =============================================================================


@pytest.mark.e2e
class TestInstallShClaudeDirCreation:
    """Test that install.sh creates ~/.claude/ if missing."""

    def test_creates_claude_dir_when_missing(self, tmp_path):
        home = tmp_path / "home_no_claude"
        home.mkdir()
        # Deliberately NOT creating .claude/

        result = run_install_sh("--dry-run", "--no-agents", home_dir=home)
        assert result.returncode == 0
        # install.sh check_claude_dir should have created it
        assert (home / ".claude").exists()


# =============================================================================
# Exit code propagation
# =============================================================================


@pytest.mark.e2e
class TestInstallShExitCode:
    """Test exit code propagation from install.py through install.sh."""

    def test_successful_install_returns_zero(self, fake_home):
        result = run_install_sh("--no-agents", home_dir=fake_home)
        assert result.returncode == 0

    def test_successful_uninstall_returns_zero(self, fake_home):
        run_install_sh("--no-agents", home_dir=fake_home)
        result = run_install_sh("--uninstall", home_dir=fake_home)
        assert result.returncode == 0

    def test_version_flag_returns_zero(self, fake_home):
        result = run_install_sh("--version", home_dir=fake_home)
        assert result.returncode == 0

    def test_list_files_flag_returns_zero(self, fake_home):
        result = run_install_sh("--list-files", home_dir=fake_home)
        assert result.returncode == 0
