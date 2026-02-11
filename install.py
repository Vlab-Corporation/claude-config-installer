#!/usr/bin/env python3
"""
SuperClaude Config Installer

Installs the SuperClaude framework configuration to ~/.claude/.
Safely copies config, command, skill, and agent files with backup support.

Usage:
    python3 install.py                  # Install
    python3 install.py --uninstall      # Remove
    python3 install.py --verbose        # Detailed output
    python3 install.py --dry-run        # Preview changes
    python3 install.py --list-files     # Show managed files
    python3 install.py --preserve-agents  # Skip agents/ directory
    python3 install.py --check-update   # Check for updates
"""

import argparse
import json
import os
import shutil
import ssl
import stat
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from src.version import (
    __version__,
    get_full_version_string,
    get_installed_version,
    save_installed_version,
    get_legacy_files_to_remove,
    get_current_install_files,
    get_files_to_uninstall,
    get_executable_files,
    get_runtime_dirs,
)


# Configuration
CLAUDE_DIR = Path.home() / ".claude"
SCRIPT_DIR = Path(__file__).parent.resolve()
GITHUB_REPO = "Vlab-Corporation/claude-config-installer"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# File mappings from version.py (SSOT)
INSTALL_MAP = get_current_install_files()

# TDD project files that must never be touched
TDD_MANAGED_PATHS = [
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


class Installer:
    def __init__(self, verbose=False, preserve_agents=False, dry_run=False):
        self.verbose = verbose
        self.preserve_agents = preserve_agents
        self.dry_run = dry_run
        self.installed_files = []
        self.backup_dir = None

    def log(self, message, level="info"):
        """Print log message with formatting."""
        icons = {
            "info": "\033[94m[i]\033[0m",
            "success": "\033[92m[+]\033[0m",
            "warning": "\033[93m[!]\033[0m",
            "error": "\033[91m[x]\033[0m",
        }
        print(f"{icons.get(level, '[?]')} {message}")

    def log_verbose(self, message):
        """Print verbose log message."""
        if self.verbose:
            print(f"    {message}")

    def _get_install_map(self):
        """Get install map, optionally filtering out agent files."""
        install_map = INSTALL_MAP.copy()
        if self.preserve_agents:
            install_map = {
                src: dest for src, dest in install_map.items()
                if not dest.startswith("agents/")
            }
        return install_map

    def check_prerequisites(self):
        """Check if prerequisites are met."""
        self.log("Checking prerequisites...")

        if sys.version_info < (3, 6):
            self.log("Python 3.6+ required", "error")
            return False
        self.log_verbose(f"Python {sys.version_info.major}.{sys.version_info.minor} OK")

        if not CLAUDE_DIR.exists():
            self.log(f"Claude Code directory not found: {CLAUDE_DIR}", "error")
            self.log("Please install Claude Code first: https://claude.ai/code", "info")
            return False
        self.log_verbose(f"Claude directory found: {CLAUDE_DIR}")

        install_map = self._get_install_map()
        missing = []
        for src in install_map.keys():
            src_path = SCRIPT_DIR / src
            if not src_path.exists():
                missing.append(src)

        if missing:
            self.log(f"Missing {len(missing)} source files:", "error")
            for f in missing[:5]:
                self.log_verbose(f"  {f}")
            if len(missing) > 5:
                self.log_verbose(f"  ... and {len(missing) - 5} more")
            return False

        self.log_verbose("All source files present")
        self.log("Prerequisites check passed", "success")
        return True

    def create_backup(self):
        """Create backup of existing files that would be overwritten."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = CLAUDE_DIR / "backups" / f"superclaude_{timestamp}"

        install_map = self._get_install_map()
        files_to_backup = []
        for dest in install_map.values():
            dest_path = CLAUDE_DIR / dest
            if dest_path.exists():
                files_to_backup.append(dest_path)

        if not files_to_backup:
            self.log("No existing files to backup (fresh install)", "info")
            return

        if self.dry_run:
            self.log(f"Would backup {len(files_to_backup)} files", "info")
            return

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        for file_path in files_to_backup:
            rel_path = file_path.relative_to(CLAUDE_DIR)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            self.log_verbose(f"Backed up: {rel_path}")
        self.log(f"Backup created: {self.backup_dir}", "success")

    def remove_legacy_files(self):
        """Remove legacy files from previous versions."""
        legacy_files = get_legacy_files_to_remove()
        if not legacy_files:
            return []

        removed = []
        for legacy in legacy_files:
            legacy_path = CLAUDE_DIR / legacy
            try:
                if legacy_path.is_dir():
                    if not self.dry_run:
                        shutil.rmtree(legacy_path)
                    removed.append(legacy)
                    self.log_verbose(f"Removed legacy directory: {legacy}")
                elif legacy_path.exists():
                    if not self.dry_run:
                        legacy_path.unlink()
                    removed.append(legacy)
                    self.log_verbose(f"Removed legacy file: {legacy}")
            except Exception as e:
                self.log(f"Warning: Could not remove legacy file {legacy}: {e}", "warning")

        if removed:
            self.log(f"Removed {len(removed)} legacy items", "info")
        return removed

    def install_files(self):
        """Copy files to Claude directory."""
        self.log("Installing files...")
        install_map = self._get_install_map()

        # settings.json is handled separately by merge_settings
        settings_src = None
        settings_dest = None

        for src, dest in install_map.items():
            if dest == "settings.json":
                settings_src = src
                settings_dest = dest
                continue

            src_path = SCRIPT_DIR / src
            dest_path = CLAUDE_DIR / dest

            if self.dry_run:
                action = "overwrite" if dest_path.exists() else "create"
                self.log_verbose(f"Would {action}: {dest}")
                self.installed_files.append(dest_path)
                continue

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            self.installed_files.append(dest_path)
            self.log_verbose(f"Installed: {dest}")

        count = len(install_map) - (1 if settings_src else 0)
        self.log(f"{'Would install' if self.dry_run else 'Installed'} {count} files", "success")

    def merge_settings(self):
        """Merge settings.json with existing settings, preserving user config."""
        self.log("Processing settings.json...")

        template_path = SCRIPT_DIR / "src" / "root" / "settings.json"
        target_path = CLAUDE_DIR / "settings.json"

        if not template_path.exists():
            self.log("settings.json template not found, skipping", "warning")
            return

        template = json.loads(template_path.read_text())

        if not target_path.exists():
            if self.dry_run:
                self.log("Would create settings.json (fresh install)", "info")
                return
            target_path.write_text(json.dumps(template, indent=2) + "\n")
            self.log("Created settings.json (fresh install)", "success")
            return

        try:
            existing = json.loads(target_path.read_text())
        except (json.JSONDecodeError, Exception) as e:
            self.log(f"Could not parse existing settings.json: {e}", "warning")
            if self.dry_run:
                self.log("Would overwrite corrupted settings.json", "warning")
                return
            target_path.write_text(json.dumps(template, indent=2) + "\n")
            self.log("Replaced corrupted settings.json with template", "warning")
            return

        merged = self._deep_merge_settings(existing, template)

        if self.dry_run:
            self.log("Would merge settings.json", "info")
            return

        target_path.write_text(json.dumps(merged, indent=2) + "\n")
        self.log("Merged settings.json", "success")

    def _deep_merge_settings(self, existing, template):
        """Deep merge settings, preserving user config and merging hooks."""
        merged = existing.copy()

        # Merge hooks (array merge with dedup by command path)
        if "hooks" in template:
            if "hooks" not in merged:
                merged["hooks"] = {}

            for event_name, event_hooks in template["hooks"].items():
                if event_name not in merged["hooks"]:
                    merged["hooks"][event_name] = event_hooks
                else:
                    existing_commands = set()
                    for hook_group in merged["hooks"][event_name]:
                        for hook in hook_group.get("hooks", []):
                            existing_commands.add(hook.get("command", ""))

                    for hook_group in event_hooks:
                        for hook in hook_group.get("hooks", []):
                            if hook.get("command", "") not in existing_commands:
                                merged["hooks"][event_name].append(hook_group)
                                break

        # Apply non-hook, non-permission settings from template
        for key, value in template.items():
            if key == "hooks":
                continue
            if key == "permissions":
                continue
            if key not in merged:
                merged[key] = value

        return merged

    def set_executable_permissions(self):
        """Set executable permissions on hooks and bin files."""
        executable_files = get_executable_files()
        if not executable_files:
            return

        self.log("Setting executable permissions...")
        for rel_path in executable_files:
            path = CLAUDE_DIR / rel_path
            if path.exists():
                if self.dry_run:
                    self.log_verbose(f"Would chmod +x: {rel_path}")
                    continue
                mode = path.stat().st_mode
                os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                self.log_verbose(f"chmod +x: {rel_path}")
            else:
                self.log_verbose(f"Skip chmod (not found): {rel_path}")

        self.log(
            f"{'Would set' if self.dry_run else 'Set'} executable permissions on {len(executable_files)} files",
            "success",
        )

    def create_runtime_dirs(self):
        """Create runtime directories needed by the framework."""
        runtime_dirs = get_runtime_dirs()
        if not runtime_dirs:
            return

        for dir_name in runtime_dirs:
            dir_path = CLAUDE_DIR / dir_name
            if dir_path.exists():
                self.log_verbose(f"Directory exists: {dir_name}")
                continue
            if self.dry_run:
                self.log_verbose(f"Would create directory: {dir_name}")
                continue
            dir_path.mkdir(parents=True, exist_ok=True)
            self.log_verbose(f"Created directory: {dir_name}")

    def verify_installation(self):
        """Verify all files are installed correctly."""
        self.log("Verifying installation...")

        install_map = self._get_install_map()
        missing = []
        for dest in install_map.values():
            dest_path = CLAUDE_DIR / dest
            if not dest_path.exists():
                missing.append(dest)

        if missing:
            self.log(f"{len(missing)} files missing after install:", "error")
            for f in missing[:5]:
                self.log_verbose(f"  {f}")
            return False

        # Check executable permissions
        for rel_path in get_executable_files():
            path = CLAUDE_DIR / rel_path
            if path.exists() and not os.access(path, os.X_OK):
                self.log(f"Missing execute permission: {rel_path}", "warning")

        self.log("Installation verified", "success")
        return True

    def install(self):
        """Run the full installation process."""
        print("\n" + "=" * 50)
        print(f"  {get_full_version_string()} - Installer")
        print("=" * 50 + "\n")

        if self.dry_run:
            self.log("DRY RUN - No changes will be made", "warning")
            print()

        if not self.check_prerequisites():
            return False

        self.remove_legacy_files()
        self.create_backup()
        self.install_files()
        self.merge_settings()
        self.set_executable_permissions()
        self.create_runtime_dirs()

        if self.dry_run:
            print("\n" + "=" * 50)
            self.log("DRY RUN completed - no changes were made", "info")
            print("=" * 50 + "\n")
            return True

        if not self.verify_installation():
            self.log("Installation completed with warnings", "warning")
            return True

        if save_installed_version():
            self.log_verbose(f"Saved version {__version__} to version file")
        else:
            self.log("Could not save version file", "warning")

        print("\n" + "=" * 50)
        self.log("Installation completed successfully!", "success")
        print("=" * 50)
        print("\nSuperClaude framework has been installed to ~/.claude/")
        print("Restart Claude Code to activate the configuration.")
        print()

        return True

    def uninstall(self):
        """Remove SuperClaude files, preserving TDD project files."""
        print("\n" + "=" * 50)
        print(f"  {get_full_version_string()} - Uninstaller")
        print("=" * 50 + "\n")

        if self.dry_run:
            self.log("DRY RUN - No files will be deleted", "warning")

        all_files_to_remove = get_files_to_uninstall()
        self.log(f"Checking {len(all_files_to_remove)} files...")

        removed_count = 0

        for item in all_files_to_remove:
            # Never touch TDD project files
            if item in TDD_MANAGED_PATHS:
                self.log_verbose(f"Preserved (TDD): {item}")
                continue

            item_path = CLAUDE_DIR / item

            try:
                if item_path.is_dir():
                    if self.dry_run:
                        self.log_verbose(f"Would remove directory: {item}")
                    else:
                        shutil.rmtree(item_path)
                        self.log_verbose(f"Removed directory: {item}")
                    removed_count += 1
                elif item_path.exists():
                    if self.dry_run:
                        self.log_verbose(f"Would remove file: {item}")
                    else:
                        item_path.unlink()
                        self.log_verbose(f"Removed file: {item}")
                    removed_count += 1
            except PermissionError:
                self.log(f"Permission denied: {item}", "warning")
            except Exception as e:
                self.log(f"Could not remove {item}: {e}", "warning")

        # Clean up empty parent directories
        if not self.dry_run:
            cleaned_parents = set()
            for item in all_files_to_remove:
                item_path = CLAUDE_DIR / item
                try:
                    parent = item_path.parent
                    while parent != CLAUDE_DIR and parent not in cleaned_parents:
                        cleaned_parents.add(parent)
                        if parent.exists() and not any(parent.iterdir()):
                            parent.rmdir()
                            self.log_verbose(
                                f"Removed empty directory: {parent.relative_to(CLAUDE_DIR)}"
                            )
                        parent = parent.parent
                except Exception:
                    pass

        # Remove version tracking file
        version_file = CLAUDE_DIR / ".superclaude-installer-version"
        if version_file.exists():
            if self.dry_run:
                self.log_verbose("Would remove version file")
            else:
                version_file.unlink()
                self.log_verbose("Removed version file")
            removed_count += 1

        action = "Would remove" if self.dry_run else "Removed"
        self.log(f"{action} {removed_count} items", "success")

        print("\n" + "=" * 50)
        if self.dry_run:
            self.log("DRY RUN completed - no files were deleted", "info")
        else:
            self.log("Uninstallation completed", "success")
        print("=" * 50 + "\n")

        return True

    def check_update(self):
        """Check if a newer version is available on GitHub."""
        self.log("Checking for updates...")

        try:
            req = Request(
                GITHUB_API_URL,
                headers={"User-Agent": "SuperClaude-Config-Installer"},
            )

            try:
                context = ssl.create_default_context()
            except Exception:
                context = ssl._create_unverified_context()

            with urlopen(req, timeout=5, context=context) as response:
                data = json.loads(response.read().decode("utf-8"))
                latest_version = data.get("tag_name", "").lstrip("v")

                if not latest_version:
                    self.log("Could not determine latest version", "warning")
                    return False

                current = tuple(int(x) for x in __version__.split("."))
                latest = tuple(int(x) for x in latest_version.split("."))

                print(f"\nCurrent version: v{__version__}")
                print(f"Latest version:  v{latest_version}")

                if latest > current:
                    self.log(
                        f"Update available: v{__version__} -> v{latest_version}",
                        "warning",
                    )
                    print(f"\nDownload from:")
                    print(f"  https://github.com/{GITHUB_REPO}/releases/latest")
                    return True
                else:
                    self.log("You are using the latest version", "success")
                    return False

        except (HTTPError, URLError, ValueError, Exception) as e:
            self.log(f"Could not check for updates: {e}", "warning")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Install the SuperClaude framework configuration"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove SuperClaude configuration files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--preserve-agents",
        action="store_true",
        help="Skip installing agents/ directory files",
    )
    parser.add_argument(
        "--check-update",
        action="store_true",
        help="Check if a newer version is available",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="store_true",
        help="Show version information",
    )
    parser.add_argument(
        "--list-files",
        action="store_true",
        help="List all managed files",
    )

    args = parser.parse_args()

    if args.version:
        print(get_full_version_string())
        print(f"Installation path: {CLAUDE_DIR}")
        sys.exit(0)

    if args.list_files:
        print(f"\n{get_full_version_string()}")
        print(f"\nFiles to install ({len(INSTALL_MAP)}):")
        for src, dest in sorted(INSTALL_MAP.items()):
            print(f"  {src} -> {dest}")
        print(f"\nExecutable files ({len(get_executable_files())}):")
        for f in get_executable_files():
            print(f"  {f}")
        print(f"\nRuntime directories ({len(get_runtime_dirs())}):")
        for d in get_runtime_dirs():
            print(f"  {d}/")
        sys.exit(0)

    installer = Installer(
        verbose=args.verbose,
        preserve_agents=args.preserve_agents,
        dry_run=args.dry_run,
    )

    if args.check_update:
        installer.check_update()
        sys.exit(0)
    elif args.uninstall:
        success = installer.uninstall()
    else:
        success = installer.install()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
