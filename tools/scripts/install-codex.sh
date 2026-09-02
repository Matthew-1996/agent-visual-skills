#!/usr/bin/env bash
set -euo pipefail

skills=(
  visual-communication
  excalidraw-diagram
  diagram-rendering
  architecture-diagram
  infographic
  web-visual
)

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -- "${script_dir}/../.." && pwd -P)"
source_skills="${repo_root}/codex/skills"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
destination_dir="${codex_home}/skills"

for skill in "${skills[@]}"; do
  source_path="${source_skills}/${skill}"
  if [[ ! -d "${source_path}" || ! -f "${source_path}/SKILL.md" ]]; then
    printf 'error: invalid skill source: %s\n' "${source_path}" >&2
    exit 1
  fi
done

mkdir -p -- "${destination_dir}"

# Validate all destinations before creating a link, so a conflict leaves the
# skills directory exactly as it was.
for skill in "${skills[@]}"; do
  source_path="${source_skills}/${skill}"
  destination_path="${destination_dir}/${skill}"

  if [[ -L "${destination_path}" ]]; then
    if [[ "$(cd -- "${destination_path}" && pwd -P)" == "${source_path}" ]]; then
      continue
    fi
    printf 'error: refusing to replace existing symlink: %s\n' "${destination_path}" >&2
    exit 1
  fi

  if [[ -e "${destination_path}" ]]; then
    printf 'error: refusing to replace existing path: %s\n' "${destination_path}" >&2
    exit 1
  fi
done

for skill in "${skills[@]}"; do
  source_path="${source_skills}/${skill}"
  destination_path="${destination_dir}/${skill}"
  if [[ -L "${destination_path}" ]]; then
    continue
  fi
  ln -s -- "${source_path}" "${destination_path}"
done

printf 'Installed Codex skill links in %s\n' "${destination_dir}"
