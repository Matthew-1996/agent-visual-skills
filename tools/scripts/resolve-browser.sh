#!/usr/bin/env bash

resolve_local_browser() {
  local candidate=""
  if [[ -n "${CHROMIUM_BIN:-}" ]]; then
    if [[ -f "${CHROMIUM_BIN}" && -x "${CHROMIUM_BIN}" ]]; then
      printf '%s\n' "${CHROMIUM_BIN}"
      return 0
    fi
    printf 'browser resolver: CHROMIUM_BIN must name an executable local browser: %s\n' "${CHROMIUM_BIN}" >&2
    return 1
  fi

  for candidate in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
    if [[ -f "${candidate}" && -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  for candidate in chromium chromium-browser google-chrome google-chrome-stable; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      command -v "${candidate}"
      return 0
    fi
  done
  printf 'browser resolver: set CHROMIUM_BIN or install Chrome/Chromium.\n' >&2
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  set -euo pipefail
  resolve_local_browser
fi
