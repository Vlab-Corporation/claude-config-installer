# SuperClaude Config Installer

Installs the SuperClaude framework configuration to `~/.claude/` for Claude Code.

## Prerequisites

- Python 3.6+
- Claude Code installed (`~/.claude/` directory exists)

## Installation

```bash
git clone https://github.com/Vlab-Corporation/claude-config-installer.git
cd claude-config-installer
python3 install.py
```

## Usage

```bash
python3 install.py                    # Install all files
python3 install.py --verbose          # Install with detailed output
python3 install.py --dry-run          # Preview changes without modifying files
python3 install.py --preserve-agents  # Install without overwriting agents/
python3 install.py --list-files       # Show all managed files
python3 install.py --uninstall        # Remove SuperClaude files (preserves user settings)
python3 install.py --uninstall --preserve-agents  # Uninstall but keep agents/
python3 install.py --uninstall --clean-all  # Remove everything including backups
python3 install.py --uninstall --dry-run  # Preview uninstall
python3 install.py --check-update     # Check for newer version
python3 install.py --version          # Show version
```

## What Gets Installed

| Category | Count | Destination |
|----------|-------|-------------|
| Root Config | 24 | `~/.claude/` |
| Agents | 17 | `~/.claude/agents/` |
| SC Commands | 33 | `~/.claude/commands/sc/` |
| Queue Commands | 5 | `~/.claude/commands/queue/` |
| Skills | 13 | `~/.claude/skills/` |
| Docs | 1 | `~/.claude/docs/` |
| Scripts | 6 | `~/.claude/scripts/` |
| Hooks | 3 | `~/.claude/hooks/` |
| Lib | 2 | `~/.claude/lib/` |
| Bin | 1 | `~/.claude/bin/` |
| Tests | 1 | `~/.claude/tests/` |
| **Total** | **106** | |

## Coexistence with TDD Project

This installer does not touch files managed by the [Claude TDD](https://github.com/Vlab-Corporation/claude_cli_tdd) project. TDD-specific commands, skills, docs, and agents are excluded from both install and uninstall operations.

## Settings Merge

When `~/.claude/settings.json` already exists, the installer performs a deep merge:
- **hooks**: Array merge with dedup by command path
- **permissions**: Always preserved (never overwritten)
- **Other keys**: Existing values preserved, new template keys added

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT
