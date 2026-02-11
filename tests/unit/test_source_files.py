"""
Tests that all source files referenced in VERSION_MIGRATIONS actually exist in src/.
"""

import re
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


# =============================================================================
# Agent Frontmatter Validation (all agents: standard + TDD)
# =============================================================================

def _parse_frontmatter(content):
    """Extract YAML frontmatter fields from markdown content.

    Returns dict of field -> value, or None if no valid frontmatter.
    """
    if not content.startswith("---"):
        return None

    end = content.find("---", 3)
    if end == -1:
        return None

    raw = content[3:end].strip()
    fields = {}
    for line in raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def _get_all_agent_sources():
    """Collect all agent .md source paths (standard 17 + TDD 3)."""
    agents = []
    for src, dest in get_current_install_files().items():
        if dest.startswith("agents/") and src.endswith(".md"):
            agents.append(src)
    for src in get_agent_files().keys():
        if src.endswith(".md"):
            agents.append(src)
    return agents


class TestAgentFrontmatterValidation:
    """Validate YAML frontmatter for all agent .md files (standard + TDD)."""

    def test_all_agents_have_closing_frontmatter(self):
        """Frontmatter must have both opening and closing --- delimiters."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            if not content.startswith("---"):
                errors.append(f"{src}: missing opening ---")
                continue
            end = content.find("---", 3)
            if end == -1:
                errors.append(f"{src}: missing closing ---")

        assert not errors, "\n".join(errors)

    def test_all_agents_have_name_field(self):
        """Every agent must have a 'name' field in frontmatter."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields is None:
                errors.append(f"{src}: no valid frontmatter")
            elif "name" not in fields:
                errors.append(f"{src}: missing 'name' field")

        assert not errors, "\n".join(errors)

    def test_all_agents_have_description_field(self):
        """Every agent must have a 'description' field in frontmatter."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields and "description" not in fields:
                errors.append(f"{src}: missing 'description' field")

        assert not errors, "\n".join(errors)

    def test_name_follows_lowercase_hyphen_pattern(self):
        """Agent name must be lowercase letters, numbers, and hyphens only."""
        pattern = re.compile(r"^[a-z0-9][a-z0-9-]*$")
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields and "name" in fields:
                name = fields["name"]
                if not pattern.match(name):
                    errors.append(f"{src}: invalid name '{name}' (must be lowercase-hyphen)")

        assert not errors, "\n".join(errors)

    def test_name_does_not_contain_reserved_words(self):
        """Agent name must not contain 'anthropic' or 'claude'."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields and "name" in fields:
                name = fields["name"].lower()
                if "anthropic" in name:
                    errors.append(f"{src}: name contains reserved word 'anthropic'")
                if "claude" in name:
                    errors.append(f"{src}: name contains reserved word 'claude'")

        assert not errors, "\n".join(errors)

    def test_name_max_length(self):
        """Agent name must be 64 characters or fewer."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields and "name" in fields:
                if len(fields["name"]) > 64:
                    errors.append(f"{src}: name too long ({len(fields['name'])} > 64)")

        assert not errors, "\n".join(errors)

    def test_description_not_empty(self):
        """Agent description must not be empty."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields and "description" in fields:
                if not fields["description"]:
                    errors.append(f"{src}: empty description")

        assert not errors, "\n".join(errors)

    def test_name_matches_filename(self):
        """Agent frontmatter name should match the filename (without .md)."""
        errors = []
        for src in _get_all_agent_sources():
            content = (PROJECT_ROOT / src).read_text()
            fields = _parse_frontmatter(content)
            if fields and "name" in fields:
                expected_name = Path(src).stem
                if fields["name"] != expected_name:
                    errors.append(
                        f"{src}: name '{fields['name']}' doesn't match filename '{expected_name}'"
                    )

        assert not errors, "\n".join(errors)
