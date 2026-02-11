"""
Tests that all source files referenced in VERSION_MIGRATIONS actually exist in src/.
"""

from pathlib import Path

import pytest

from src.version import get_current_install_files, get_agent_files


PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


class TestSourceFilesExist:
    """Verify every source file in the install mapping exists on disk."""

    def test_all_source_files_exist(self):
        missing = []
        for src in get_current_install_files().keys():
            src_path = PROJECT_ROOT / src
            if not src_path.exists():
                missing.append(src)

        assert not missing, (
            f"Missing {len(missing)} source files:\n"
            + "\n".join(f"  {f}" for f in missing)
        )

    def test_source_files_are_not_empty(self):
        empty = []
        for src in get_current_install_files().keys():
            src_path = PROJECT_ROOT / src
            if src_path.exists() and src_path.stat().st_size == 0:
                empty.append(src)

        assert not empty, (
            f"Found {len(empty)} empty source files:\n"
            + "\n".join(f"  {f}" for f in empty)
        )

    def test_source_file_count_matches_mapping(self):
        install_files = get_current_install_files()
        existing = sum(
            1
            for src in install_files.keys()
            if (PROJECT_ROOT / src).exists()
        )
        assert existing == len(install_files), (
            f"Expected {len(install_files)} source files, found {existing}"
        )


class TestSourceFileFormat:
    """Verify source file formats are valid."""

    def test_json_files_are_valid_json(self):
        import json

        for src in get_current_install_files().keys():
            if src.endswith(".json"):
                src_path = PROJECT_ROOT / src
                if src_path.exists():
                    try:
                        json.loads(src_path.read_text())
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Invalid JSON in {src}: {e}")

    def test_shell_scripts_have_shebang(self):
        for src in get_current_install_files().keys():
            if src.endswith(".sh"):
                src_path = PROJECT_ROOT / src
                if src_path.exists():
                    content = src_path.read_text()
                    assert content.startswith("#!"), (
                        f"Shell script missing shebang: {src}"
                    )


class TestAgentSourceFilesExist:
    """Verify optional TDD agent source files exist on disk."""

    def test_all_agent_source_files_exist(self):
        missing = []
        for src in get_agent_files().keys():
            src_path = PROJECT_ROOT / src
            if not src_path.exists():
                missing.append(src)

        assert not missing, (
            f"Missing {len(missing)} agent source files:\n"
            + "\n".join(f"  {f}" for f in missing)
        )

    def test_agent_source_files_are_not_empty(self):
        empty = []
        for src in get_agent_files().keys():
            src_path = PROJECT_ROOT / src
            if src_path.exists() and src_path.stat().st_size == 0:
                empty.append(src)

        assert not empty, (
            f"Found {len(empty)} empty agent source files:\n"
            + "\n".join(f"  {f}" for f in empty)
        )

    def test_agent_files_have_frontmatter(self):
        """Agent .md files should have YAML frontmatter with name and description."""
        for src in get_agent_files().keys():
            src_path = PROJECT_ROOT / src
            if src_path.exists() and src_path.suffix == ".md":
                content = src_path.read_text()
                assert content.startswith("---"), (
                    f"Agent file should start with YAML frontmatter: {src}"
                )
