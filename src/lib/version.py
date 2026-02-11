#!/usr/bin/env python3
"""
Version module - Single source of truth for Claude Queue version

This module reads version from the VERSION file and provides:
- __version__: Version string (e.g., "1.0.0")
- VERSION_INFO: Tuple of (major, minor, patch) integers
"""
from pathlib import Path

# Find VERSION file - check multiple locations
# 1. Project root (during development)
# 2. Installed location (~/.claude/VERSION)
# 3. Relative to this file

_VERSION_LOCATIONS = [
    Path(__file__).parent.parent.parent.parent / "VERSION",  # Project root
    Path(__file__).parent.parent.parent / "VERSION",  # One level up
    Path(__file__).parent.parent / "VERSION",  # Two levels up
    Path.home() / ".claude" / "VERSION",  # Installed location
]


def _read_version() -> str:
    """Read version from VERSION file"""
    for location in _VERSION_LOCATIONS:
        if location.exists():
            return location.read_text().strip()
    # Fallback version if VERSION file not found
    return "1.0.0"


def _parse_version_info(version_string: str) -> tuple:
    """Parse version string into tuple of integers (major, minor, patch)"""
    # Remove any prerelease or build metadata
    base_version = version_string.split('-')[0].split('+')[0]
    parts = base_version.split('.')
    return tuple(int(p) for p in parts[:3])


# Public API
__version__ = _read_version()
VERSION_INFO = _parse_version_info(__version__)

# Convenience accessors
VERSION_MAJOR = VERSION_INFO[0]
VERSION_MINOR = VERSION_INFO[1]
VERSION_PATCH = VERSION_INFO[2]


def get_version() -> str:
    """Get version string"""
    return __version__


def get_version_info() -> tuple:
    """Get version as tuple of integers"""
    return VERSION_INFO


if __name__ == "__main__":
    print(f"Claude Queue v{__version__}")
    print(f"Version Info: {VERSION_INFO}")
