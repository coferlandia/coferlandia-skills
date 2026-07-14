#!/usr/bin/env bash

discovery_lib_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./config.sh
source "${discovery_lib_dir}/config.sh"
# shellcheck source=./git.sh
source "${discovery_lib_dir}/git.sh"

pm_project_slug_from_path() {
  basename -- "$1"
}

pm_discover_project_paths() {
  local repos_root="$1"
  [[ -n "${repos_root}" ]] || return 0
  [[ -d "${repos_root}" ]] || return 0

  find "${repos_root}" -mindepth 1 -maxdepth 1 -type d | sort | while IFS= read -r project_path; do
    [[ -n "${project_path}" ]] || continue
    pm_git_is_repo "${project_path}" && printf '%s\n' "${project_path}"
  done
}

