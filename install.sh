#!/bin/bash
# SuperClaude Config Installer - Shell wrapper
#
# Usage:
#   Local:    ./install.sh [options]
#   One-liner: curl -sL https://raw.githubusercontent.com/Vlab-Corporation/claude-config-installer/main/install.sh | bash
#   With args: curl -sL https://raw.githubusercontent.com/Vlab-Corporation/claude-config-installer/main/install.sh | bash -s -- --verbose
#
# Options are passed directly to install.py:
#   --verbose, -v        Show detailed output
#   --dry-run            Preview changes without modifying files
#   --preserve-agents    Skip agents/ directory
#   --uninstall          Remove SuperClaude files
#   --clean-all          Remove everything including backups (with --uninstall)
#   --list-files         Show all managed files
#   --check-update       Check for newer version
#   --version, -V        Show version

set -e

REPO_URL="https://github.com/Vlab-Corporation/claude-config-installer.git"
CLAUDE_DIR="$HOME/.claude"

# --- Helper functions ---

log_info()  { echo -e "\033[94m[i]\033[0m $1"; }
log_ok()    { echo -e "\033[92m[+]\033[0m $1"; }
log_warn()  { echo -e "\033[93m[!]\033[0m $1"; }
log_error() { echo -e "\033[91m[x]\033[0m $1"; }

check_python3() {
    if ! command -v python3 &>/dev/null; then
        log_error "Python 3 is required but not installed."
        echo "  Install Python 3.6+ from https://www.python.org/downloads/"
        exit 1
    fi

    local py_version
    py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    local py_major py_minor
    py_major=$(echo "$py_version" | cut -d. -f1)
    py_minor=$(echo "$py_version" | cut -d. -f2)

    if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 6 ]; }; then
        log_error "Python 3.6+ required (found $py_version)"
        exit 1
    fi
}

check_claude_dir() {
    if [ ! -d "$CLAUDE_DIR" ]; then
        log_warn "Claude Code directory not found: $CLAUDE_DIR"
        log_info "Creating $CLAUDE_DIR ..."
        mkdir -p "$CLAUDE_DIR"
    fi
}

show_version() {
    local script_dir="$1"
    local version
    version=$(python3 -c "import sys; sys.path.insert(0, '$script_dir'); from src.version import __version__; print(__version__)" 2>/dev/null || echo "unknown")
    echo ""
    echo "=========================================="
    echo "  SuperClaude Config Installer v$version"
    echo "=========================================="
    echo ""
}

# --- Detect execution mode ---

is_local() {
    # Local mode if BASH_SOURCE[0] points to an actual file on disk
    [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]
}

# --- Main ---

if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ] 2>/dev/null; then
    # Sourced — do nothing (allow function reuse)
    :
elif is_local; then
    # ---- Local mode (./install.sh) ----
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    check_python3
    check_claude_dir
    show_version "$SCRIPT_DIR"

    python3 "$SCRIPT_DIR/install.py" "$@"
else
    # ---- Piped mode (curl | bash) ----
    log_info "Detected piped installation mode"

    check_python3
    check_claude_dir

    # Clone to temp directory
    TMPDIR=$(mktemp -d)
    trap 'rm -rf "$TMPDIR"' EXIT

    if ! command -v git &>/dev/null; then
        log_error "git is required for remote installation."
        echo "  Install git or use: git clone $REPO_URL && cd claude-config-installer && ./install.sh"
        exit 1
    fi

    log_info "Cloning repository..."
    git clone --depth 1 --quiet "$REPO_URL" "$TMPDIR/claude-config-installer"

    SCRIPT_DIR="$TMPDIR/claude-config-installer"
    show_version "$SCRIPT_DIR"

    log_info "Running installer..."
    python3 "$SCRIPT_DIR/install.py" "$@"

    log_ok "Temporary files cleaned up automatically"
fi
