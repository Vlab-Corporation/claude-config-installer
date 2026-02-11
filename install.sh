#!/bin/bash
# SuperClaude Config Installer - Shell wrapper
# Usage: ./install.sh [options]

cd "$(dirname "$0")" || exit 1
python3 install.py "$@"
