#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
artifact_dir="$repo_root/test-results/acceptance-artifacts"
matplotlib_cache="$repo_root/test-results/tmp/matplotlib"

mkdir -p "$artifact_dir" "$matplotlib_cache"
export MPLCONFIGDIR="$matplotlib_cache"

exec "$repo_root/tools/python/.venv/bin/python" "$repo_root/tests/acceptance_runner.py"
