#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"
report_dir="$repo_root/test-results"
report_path="$report_dir/environment.json"
renderer_python="$repo_root/tools/python/.venv/bin/python"
source "$script_dir/resolve-browser.sh"

json_escape() {
  sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

tool_path=""
tool_version=""
tool_available=false

record_command() {
  local name="$1"
  shift
  tool_path="$(command -v "$name" 2>/dev/null || true)"
  tool_available=false
  tool_version=""
  if [[ -n "$tool_path" ]]; then
    tool_available=true
    tool_version="$("$tool_path" "$@" 2>&1 | head -n 1 || true)"
  fi
}

record_chrome() {
  tool_path=""
  tool_available=false
  tool_version=""
  local resolved=""
  if resolved="$(resolve_local_browser 2>/dev/null)"; then
    tool_path="$resolved"
    tool_available=true
    tool_version="$("$resolved" --version 2>&1 | head -n 1 || true)"
  fi
}

record_explicit() {
  local path="$1"
  shift
  tool_path="$path"
  tool_available=false
  tool_version=""
  if [[ -x "$path" ]]; then
    tool_available=true
    tool_version="$("$path" "$@" 2>&1 | head -n 1 || true)"
  fi
}

record_python_package() {
  local distribution="$1"
  tool_path="$renderer_python"
  tool_available=false
  tool_version=""
  if [[ -x "$renderer_python" ]]; then
    tool_version="$("$renderer_python" -c 'import importlib.metadata,sys; print(importlib.metadata.version(sys.argv[1]))' "$distribution" 2>/dev/null || true)"
    if [[ -n "$tool_version" ]]; then
      tool_available=true
    fi
  fi
}

record_mmdc() {
  tool_path="$repo_root/tools/node/node_modules/.bin/mmdc"
  tool_available=false
  tool_version=""
  if [[ -x "$tool_path" ]]; then
    tool_available=true
    tool_version="$("$tool_path" --version 2>&1 | head -n 1 || true)"
  fi
}

json_entry() {
  printf '{"available":%s,"path":"%s","version":"%s"}' \
    "$tool_available" \
    "$(printf '%s' "$tool_path" | json_escape)" \
    "$(printf '%s' "$tool_version" | json_escape)"
}

mkdir -p "$report_dir"
system_name="$(sw_vers -productName 2>/dev/null || uname -s)"
system_version="$(sw_vers -productVersion 2>/dev/null || uname -r)"
system_arch="$(uname -m)"
record_command python3 --version; python3_entry="$(json_entry)"
record_explicit "$renderer_python" --version; renderer_python_entry="$(json_entry)"
record_command uv --version; uv_entry="$(json_entry)"
record_command node --version; node_entry="$(json_entry)"
record_command npm --version; npm_entry="$(json_entry)"
record_chrome; chrome_entry="$(json_entry)"
chrome_available="$tool_available"; chrome_path="$tool_path"; chrome_version="$tool_version"
record_command codex --version; codex_entry="$(json_entry)"
record_command git --version; git_entry="$(json_entry)"
record_command dot -V; dot_entry="$(json_entry)"
record_command d2 --version; d2_entry="$(json_entry)"
record_mmdc; mmdc_entry="$(json_entry)"
record_python_package playwright; playwright_entry="$(json_entry)"; playwright_available="$tool_available"
record_python_package Pillow; pillow_entry="$(json_entry)"
record_python_package matplotlib; matplotlib_entry="$(json_entry)"
tool_path="$chrome_path"
tool_available=false
tool_version=""
if [[ "$chrome_available" == true && "$playwright_available" == true ]]; then
  tool_available=true
  tool_version="offline file preview via Playwright and $chrome_version"
fi
local_preview_entry="$(json_entry)"

printf '{\n  "system": {"name":"%s","version":"%s","arch":"%s"},\n  "python3": %s,\n  "renderer_python": %s,\n  "uv": %s,\n  "node": %s,\n  "npm": %s,\n  "chrome": %s,\n  "codex": %s,\n  "git": %s,\n  "dot": %s,\n  "d2": %s,\n  "mmdc": %s,\n  "playwright": %s,\n  "pillow": %s,\n  "matplotlib": %s,\n  "local_preview": %s\n}\n' \
  "$(printf '%s' "$system_name" | json_escape)" \
  "$(printf '%s' "$system_version" | json_escape)" \
  "$(printf '%s' "$system_arch" | json_escape)" \
  "$python3_entry" "$renderer_python_entry" "$uv_entry" "$node_entry" "$npm_entry" \
  "$chrome_entry" "$codex_entry" "$git_entry" "$dot_entry" "$d2_entry" "$mmdc_entry" \
  "$playwright_entry" "$pillow_entry" "$matplotlib_entry" "$local_preview_entry" > "$report_path"

printf 'Wrote %s\n' "$report_path"
