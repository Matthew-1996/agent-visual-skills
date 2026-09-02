#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"
source "$script_dir/resolve-browser.sh"

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'bootstrap-macos: %s is required but was not found on PATH.\n' "$command_name" >&2
    exit 127
  fi
}

require_command brew
require_command npm
require_command uv

if ! chrome="$(resolve_local_browser)"; then
  printf 'bootstrap-macos: a local Chrome/Chromium executable is required.\n' >&2
  exit 127
fi

if ! command -v dot >/dev/null 2>&1; then
  brew install graphviz
fi

if ! command -v d2 >/dev/null 2>&1; then
  brew install d2
fi

# Mermaid uses the installed Chrome. playwright-core never downloads browsers.
PUPPETEER_SKIP_DOWNLOAD=true PUPPETEER_EXECUTABLE_PATH="$chrome" npm install --prefix "$repo_root/tools/node" --registry=https://registry.npmjs.org/
uv sync --project "$repo_root/tools/python"

printf 'bootstrap-macos: local rendering dependencies are ready.\n'
