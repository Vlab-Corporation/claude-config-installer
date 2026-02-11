# Changelog

All notable changes to the SuperClaude Config Installer will be documented in this file.

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
