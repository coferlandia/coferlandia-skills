#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"

print_help() {
  cat <<'EOF'
Usage: pm-detect-conflicts.sh --config <path> [--json]
Description: Identify repo-level coverage gaps that require review (read-only).

Phase 4 detects two conflict classes:
  - repo_path_missing: a child dir of repos_root is not a git repository.
  - missing_archivist_artifact: a git repo lacks one or more expected files.

Richer PM-vs-repo conflict detection is future work.

Options:
  --config <path>   Required path to the PM config.json.
  --json            Emit machine-readable JSON instead of human-readable text.
  -h, --help        Show this help and exit.
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

format_flag="text"
[[ "${json_output}" == true ]] && format_flag="json"

python_cmd="$(pm_python_cmd)"
exec "${python_cmd}" "${script_dir}/lib/archivist.py" conflicts \
  --repos-root "${repos_root}" \
  --format "${format_flag}"
