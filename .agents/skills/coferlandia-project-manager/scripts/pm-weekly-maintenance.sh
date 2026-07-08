#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"

print_help() {
  cat <<'EOF'
Usage: pm-weekly-maintenance.sh --config <path> [--json] [--dry-run] [--apply]
Description: Run host-invoked maintenance checks across the portfolio.

Weekly maintenance does not run in the background. It must be invoked by a
user, host process, scheduler, supervising agent, or explicit PM command.

Options:
  --config <path>   Required path to the PM config.json.
  --json            Emit machine-readable JSON instead of human-readable text.
  --dry-run         Explicit dry-run (default; accepted for clarity).
  --apply           Persist maintenance checkpoints and report artifacts.
  -h, --help        Show this help and exit.
EOF
}

config_path=""
json_output=false
apply=false

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
    --dry-run)
      ;;
    --apply)
      apply=true
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
args=(
  "${script_dir}/lib/archivist.py"
  maintenance
  --repos-root "${repos_root}"
  --config "${config_path}"
  --format "${format_flag}"
)
if [[ "${apply}" == true ]]; then
  args+=(--apply)
fi

exec "${python_cmd}" "${args[@]}"
