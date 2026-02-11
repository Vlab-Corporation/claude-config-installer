"""
Tests for src/version.py — version constants, migrations, and utility functions.
"""

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from src.version import (
    __version__,
    __version_info__,
    __title__,
    __description__,
    VERSION_FILE,
    VERSION_MIGRATIONS,
    get_version,
    get_version_info,
    get_full_version_string,
    get_current_install_files,
    get_all_historical_files,
    get_files_to_uninstall,
    get_executable_files,
    get_runtime_dirs,
    get_legacy_files_to_remove,
    get_installed_version,
    save_installed_version,
)


# =============================================================================
# Version Constants
# =============================================================================

class TestVersionConstants:
    """Verify version string format and metadata values."""

    def test_version_format_is_semver(self):
        assert re.match(r"^\d+\.\d+\.\d+$", __version__)

    def test_version_info_is_tuple_of_ints(self):
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) == 3
        assert all(isinstance(x, int) for x in __version_info__)

    def test_version_info_matches_version_string(self):
        expected = tuple(int(x) for x in __version__.split("."))
        assert __version_info__ == expected

    def test_title_is_superclaude_config(self):
        assert __title__ == "SuperClaude Config"

    def test_description_is_set(self):
        assert __description__
        assert "SuperClaude" in __description__

    def test_version_file_points_to_claude_dir(self):
        assert ".claude" in str(VERSION_FILE)
        assert ".superclaude-installer-version" in str(VERSION_FILE)

    def test_current_version_exists_in_migrations(self):
        assert __version__ in VERSION_MIGRATIONS


# =============================================================================
# Version Migrations — File Mapping Integrity
# =============================================================================

class TestVersionMigrations:
    """Verify the 106-file mapping is complete and valid."""

    def test_install_files_count_is_106(self):
        install_files = get_current_install_files()
        assert len(install_files) == 106, (
            f"Expected 106 install files, got {len(install_files)}"
        )

    def test_all_source_paths_start_with_src(self):
        for src in get_current_install_files().keys():
            assert src.startswith("src/"), f"Source path should start with 'src/': {src}"

    def test_no_dest_paths_start_with_src(self):
        for dest in get_current_install_files().values():
            assert not dest.startswith("src/"), (
                f"Destination should not start with 'src/': {dest}"
            )

    def test_no_duplicate_destinations(self):
        dests = list(get_current_install_files().values())
        assert len(dests) == len(set(dests)), "Duplicate destination paths found"

    def test_no_duplicate_sources(self):
        srcs = list(get_current_install_files().keys())
        assert len(srcs) == len(set(srcs)), "Duplicate source paths found"


# =============================================================================
# Category Counts
# =============================================================================

class TestInstallFileCategories:
    """Verify file counts per category."""

    def _count_by_prefix(self, dest_prefix):
        return sum(
            1
            for dest in get_current_install_files().values()
            if dest.startswith(dest_prefix)
        )

    def _count_root_files(self):
        """Root files are those without '/' in the dest path."""
        return sum(
            1
            for dest in get_current_install_files().values()
            if "/" not in dest
        )

    def test_root_config_count_is_24(self):
        assert self._count_root_files() == 24

    def test_agents_count_is_17(self):
        assert self._count_by_prefix("agents/") == 17

    def test_commands_queue_count_is_5(self):
        count = sum(
            1
            for dest in get_current_install_files().values()
            if dest.startswith("commands/queue")
        )
        assert count == 5

    def test_commands_sc_count_is_33(self):
        assert self._count_by_prefix("commands/sc/") == 33

    def test_skills_planning_count_is_8(self):
        assert self._count_by_prefix("skills/planning/") == 8

    def test_skills_drawio_count_is_4(self):
        assert self._count_by_prefix("skills/drawio2drawio/") == 4

    def test_skills_task_queue_count_is_1(self):
        assert self._count_by_prefix("skills/task-queue/") == 1

    def test_docs_count_is_1(self):
        assert self._count_by_prefix("docs/") == 1

    def test_scripts_count_is_6(self):
        assert self._count_by_prefix("scripts/") == 6

    def test_hooks_count_is_3(self):
        assert self._count_by_prefix("hooks/") == 3

    def test_lib_count_is_2(self):
        assert self._count_by_prefix("lib/") == 2

    def test_bin_count_is_1(self):
        assert self._count_by_prefix("bin/") == 1

    def test_tests_count_is_1(self):
        assert self._count_by_prefix("tests/") == 1


# =============================================================================
# Executable Files
# =============================================================================

class TestExecutableFiles:
    """Verify executable file list."""

    def test_executable_files_count_is_4(self):
        assert len(get_executable_files()) == 4

    def test_all_hooks_are_executable(self):
        executables = get_executable_files()
        hook_files = [f for f in executables if f.startswith("hooks/")]
        assert len(hook_files) == 3

    def test_bin_cq_is_executable(self):
        assert "bin/cq" in get_executable_files()

    def test_all_shell_hooks_have_sh_extension(self):
        for f in get_executable_files():
            if f.startswith("hooks/"):
                assert f.endswith(".sh"), f"Hook should have .sh extension: {f}"


# =============================================================================
# Runtime Dirs
# =============================================================================

class TestRuntimeDirs:
    """Verify runtime directory list."""

    def test_runtime_dirs_include_queue(self):
        assert "queue" in get_runtime_dirs()

    def test_runtime_dirs_include_backups(self):
        assert "backups" in get_runtime_dirs()


# =============================================================================
# Version Tracking
# =============================================================================

class TestVersionTracking:
    """Test installed version read/write/delete."""

    def test_get_installed_version_returns_none_when_no_file(self, tmp_path):
        fake_file = tmp_path / ".superclaude-installer-version"
        with patch("src.version.VERSION_FILE", fake_file):
            assert get_installed_version() is None

    def test_save_and_get_installed_version(self, tmp_path):
        fake_file = tmp_path / ".superclaude-installer-version"
        with patch("src.version.VERSION_FILE", fake_file):
            assert save_installed_version() is True
            assert get_installed_version() == __version__

    def test_get_installed_version_returns_none_for_invalid_format(self, tmp_path):
        fake_file = tmp_path / ".superclaude-installer-version"
        fake_file.write_text("invalid")
        with patch("src.version.VERSION_FILE", fake_file):
            assert get_installed_version() is None

    def test_get_installed_version_returns_none_for_partial_version(self, tmp_path):
        fake_file = tmp_path / ".superclaude-installer-version"
        fake_file.write_text("1.0")
        with patch("src.version.VERSION_FILE", fake_file):
            assert get_installed_version() is None


# =============================================================================
# TDD Exclusion Verification
# =============================================================================

class TestTddExclusion:
    """Verify TDD project files are NOT in our install mapping."""

    TDD_FILES = [
        "commands/sc/tdd.md",
        "commands/sc/tdd-backend.md",
        "commands/sc/tdd-uiux.md",
        "skills/sc-tdd/SKILL.md",
        "skills/sc-tdd-backend/SKILL.md",
        "skills/sc-tdd-uiux/SKILL.md",
        "docs/MODE_TDD.md",
        "docs/MODE_TDD_BACKEND.md",
        "docs/MODE_TDD_UIUX.md",
        "docs/TDD_DOMAIN_CLASSIFICATION.md",
        "docs/TDD_FRAMEWORK_PATTERNS.md",
        "docs/TDD_API_MOCKING.md",
        "docs/TDD_E2E_INFRASTRUCTURE.md",
        "docs/TDD_INTEGRATION_TESTS.md",
        "docs/TDD_EXISTING_TESTS.md",
        "docs/TDD_ERROR_RECOVERY.md",
        "docs/TDD_MCP_FALLBACK.md",
        "docs/conventions/CONVENTIONS.md",
        "agents/tdd-coach.md",
        "agents/test-architect.md",
        "agents/convention-guard.md",
        ".tdd-version",
        ".tdd-agents-installed",
    ]

    def test_no_tdd_files_in_install_mapping(self):
        install_dests = set(get_current_install_files().values())
        for tdd_file in self.TDD_FILES:
            assert tdd_file not in install_dests, (
                f"TDD file should NOT be in install mapping: {tdd_file}"
            )

    def test_no_tdd_files_in_uninstall_list(self):
        uninstall_files = set(get_files_to_uninstall())
        for tdd_file in self.TDD_FILES:
            assert tdd_file not in uninstall_files, (
                f"TDD file should NOT be in uninstall list: {tdd_file}"
            )


# =============================================================================
# Utility Functions
# =============================================================================

class TestUtilityFunctions:
    """Test version utility functions."""

    def test_get_version_returns_string(self):
        assert isinstance(get_version(), str)
        assert get_version() == __version__

    def test_get_version_info_returns_tuple(self):
        assert isinstance(get_version_info(), tuple)

    def test_get_full_version_string_format(self):
        result = get_full_version_string()
        assert "SuperClaude Config" in result
        assert __version__ in result

    def test_get_all_historical_files_returns_sorted_list(self):
        files = get_all_historical_files()
        assert files == sorted(files)

    def test_get_files_to_uninstall_matches_historical(self):
        assert get_files_to_uninstall() == get_all_historical_files()

    def test_get_legacy_files_to_remove_empty_for_fresh_install(self):
        with patch("src.version.get_installed_version", return_value=None):
            assert get_legacy_files_to_remove() == []
