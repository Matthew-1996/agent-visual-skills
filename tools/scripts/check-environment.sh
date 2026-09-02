#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"
report_dir="$repo_root/test-results"
report_path="$report_dir/environment.json"
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

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
  if [[ -x "$chrome" ]]; then
    tool_path="$chrome"
    tool_available=true
    tool_version="$("$chrome" --version 2>&1 | head -n 1 || true)"
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
record_command python3 --version; python3_entry="$(json_entry)"
record_command uv --version; uv_entry="$(json_entry)"
record_command node --version; node_entry="$(json_entry)"
record_command npm --version; npm_entry="$(json_entry)"
record_chrome; chrome_entry="$(json_entry)"
record_command dot -V; dot_entry="$(json_entry)"
record_command d2 --version; d2_entry="$(json_entry)"
record_mmdc; mmdc_entry="$(json_entry)"

printf '{\n  "python3": %s,\n  "uv": %s,\n  "node": %s,\n  "npm": %s,\n  "chrome": %s,\n  "dot": %s,\n  "d2": %s,\n  "mmdc": %s\n}\n' \
  "$python3_entry" "$uv_entry" "$node_entry" "$npm_entry" "$chrome_entry" "$dot_entry" "$d2_entry" "$mmdc_entry" > "$report_path"

printf 'Wrote %s\n' "$report_path"
