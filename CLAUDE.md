# SuperClaude Config Installer — Project Guidelines

## Project Conventions

### Language & Framework

| Setting | Value |
|---------|-------|
| Language | Python 3.6+ |
| Test Framework | pytest |
| Coverage Target | 80% |

### Code Style

#### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions | snake_case | `get_installed_version()` |
| Classes | PascalCase | `Installer` |
| Constants | UPPER_SNAKE_CASE | `VERSION_MIGRATIONS` |
| Private | _underscore_prefix | `_deep_merge_settings()` |
| Modules | snake_case | `version.py` |

#### Import Organization

```python
# Standard library (alphabetical)
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Third-party (alphabetical) - only in tests
import pytest

# Local imports (alphabetical)
from src.version import __version__, get_current_install_files
```

### Test Conventions

#### File Naming
- Test files: `test_*.py` in `tests/` directory
- Unit tests: `tests/unit/test_<module>.py`
- Integration tests: `tests/integration/test_<feature>.py`

#### Test Function Naming
```python
# Pattern: test_[unit]_[scenario]_[expected_result]
def test_get_installed_version_returns_none_when_file_missing():
    pass
```

#### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange
    installer = Installer()

    # Act
    result = installer.check_prerequisites()

    # Assert
    assert result is True
```

### Git Conventions

#### Commit Message Format
```
<type>(<scope>): <description>
```

#### Commit Types
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

## Project Structure

```
claude-config-installer/
├── CLAUDE.md                     # This file
├── CHANGELOG.md
├── README.md
├── install.py                    # Main installer
├── install.sh                    # Shell wrapper
├── pyproject.toml
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── version.py                # VERSION_MIGRATIONS SSOT
│   ├── root/                     # Root-level ~/.claude/ files (24)
│   ├── agents/                   # Agent definitions (17)
│   ├── commands/                 # Command files (38)
│   │   ├── queue.md
│   │   ├── queue/
│   │   └── sc/
│   ├── docs/                     # Documentation (1)
│   ├── skills/                   # Skill definitions (13)
│   │   ├── planning/
│   │   ├── drawio2drawio/
│   │   └── task-queue/
│   ├── scripts/                  # Python utilities (6)
│   ├── hooks/                    # Shell hooks (3)
│   ├── lib/                      # Python libraries (2)
│   ├── bin/                      # Executables (1)
│   └── tests/                    # Framework tests (1)
└── tests/                        # Installer tests
    ├── conftest.py
    ├── unit/
    │   ├── test_version.py
    │   ├── test_install.py
    │   └── test_source_files.py
    └── integration/
        └── test_installer_integration.py
```

## Key Design Decisions

- **version.py is SSOT**: All file mappings live in `VERSION_MIGRATIONS`. `install.py` reads from there.
- **TDD project coexistence**: TDD files (commands, skills, docs, agents) are excluded from install AND uninstall.
- **settings.json merge**: Deep merge preserves user permissions and existing hooks.
- **No runtime state**: `settings.local.json`, `history.jsonl`, `session-env/`, `todos/` are never touched.
