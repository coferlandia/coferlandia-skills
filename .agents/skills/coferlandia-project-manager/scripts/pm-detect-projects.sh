#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/discovery.sh
source "${script_dir}/lib/discovery.sh"

print_help() {
  cat <<'EOF'
Usage: pm-detect-projects.sh --config <path> [--json]
Description: Detect direct child repositories under repos_root.
EOF
}

config_path=""
json_output=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      shift
      [[ $# -gt 0 ]] || die "Missing value for --config"
      config_path="$1"
      ;;
    --json)
      json_output=true
      ;;
    --help|-h)
      print_help
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
  shift
done

[[ -n "${config_path}" ]] || die "Missing required --config <path>"
repos_root="$(pm_config_repos_root "${config_path}")"
[[ -n "${repos_root}" ]] || die "repos_root is required in config"
[[ -d "${repos_root}" ]] || die "repos_root does not exist: ${repos_root}"

mapfile -t project_paths < <(pm_discover_project_paths "${repos_root}")

if [[ "${json_output}" == true ]]; then
  python_cmd="$(pm_python_cmd)"
  "${python_cmd}" - "${repos_root}" "${project_paths[@]}" <<'PY'
import json
import sys
from pathlib import Path

repos_root = sys.argv[1]
project_paths = sys.argv[2:]
projects = [
    {
        "project_slug": Path(path).name,
        "repo_path": path,
    }
    for path in project_paths
]
print(json.dumps({
    "status": "ok",
    "repos_root": repos_root,
    "projects_detected": len(projects),
    "projects": projects,
}, indent=2))
PY
else
  printf 'status: ok\n'
  printf 'repos_root: %s\n' "${repos_root}"
  printf 'projects_detected: %s\n' "${#project_paths[@]}"
  for project_path in "${project_paths[@]}"; do
    printf '%s\n' "${project_path}"
  done
fi
