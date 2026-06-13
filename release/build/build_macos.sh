#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller is not installed. Please install dependencies first." >&2
  exit 1
fi

pyinstaller --noconfirm --clean icon_bundler.spec
