# Changelog

All notable changes to the SuperClaude Config Installer will be documented in this file.

## [1.2.0] - 2026-02

### Added
- `--with-agents` flag for optional TDD agent installation (tdd-coach, test-architect, convention-guard)
- `--no-agents` flag to skip agent installation without prompting
- Interactive prompt for agent installation when no flag given (local mode only)
- Agent tracking via `.superclaude-agents-installed` version file
- `get_agent_files()`, `get_agents_installed()`, `save_agents_installed()`, `remove_agents_installed_flag()` utility functions
- Agent source file validation tests (frontmatter, existence, non-empty)
- E2E tests for install.sh shell wrapper (subprocess-based, fake HOME)
- 58 new tests (168 total) covering agent flows, frontmatter validation, and shell E2E

### Changed
- TDD agent paths (`agents/tdd-coach.md`, etc.) now protected conditionally — only when not installed by this tool
- `--list-files` output now includes optional TDD agents section
- Non-interactive (piped) mode defaults to skipping agent installation

## [1.1.0] - 2026-02

### Added
- `unmerge_settings()` method to reverse settings.json merge on uninstall
- Backup creation before uninstall (`superclaude_uninstall_` prefix)
- `--preserve-agents` flag support during uninstall
- Runtime directory cleanup on uninstall (empty `queue/` removed)
- `--clean-all` flag for complete removal including backups directory

### Changed
- Uninstall now uses settings unmerge instead of deleting settings.json
- `backups/` directory preserved by default during uninstall
- VERSION_MIGRATIONS functions refactored to accumulate across versions

## [1.0.0] - 2026-02

### Added
- Initial release with 106 SuperClaude framework files
- Root config files (24): CLAUDE.md, FLAGS.md, modes, MCP configs, settings.json
- Agent definitions (17): backend-architect, developer, python-expert, etc.
- SC commands (33): analyze, build, design, implement, research, etc.
- Queue commands (5): queue, cancel, list, move, next
- Skills (13): planning (8), drawio2drawio (4), task-queue (1)
- Documentation (1): ANALYZE_COMMAND.md
- Scripts (6): queue_manager, parallel_executor, session_context, etc.
- Hooks (3): queue-auto-execute, queue-session-start, queue-user-prompt
- Library files (2): formatters.py, version.py
- Bin (1): cq
- Test (1): test_scope_analysis.py
- settings.json deep merge preserving user permissions
- Backup before overwrite
- --preserve-agents flag to skip agent file installation
- --dry-run flag for change preview
- --uninstall with TDD project file preservation
- Executable permission setting for hooks and bin files
- Runtime directory creation (queue/, backups/)
