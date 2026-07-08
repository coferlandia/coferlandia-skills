#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"

print_help() {
  cat <<'EOF'
Usage: pm-onboard.sh --config <path> [--json] [--dry-run] [--apply]
Description: Build or validate the project manager onboarding state.
Examples:
  pm-onboard.sh --config config.json --dry-run
  pm-onboard.sh --config config.json --json
EOF
}

config_path=""
json_output=false
mode="dry-run"

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
      mode="dry-run"
      ;;
    --apply)
      mode="apply"
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
readiness_json="$("${script_dir}/pm-doctor.sh" --config "${config_path}" --json)"

if [[ "${json_output}" == true ]]; then
  python_cmd="$(pm_python_cmd)"
  "${python_cmd}" - "${mode}" "${readiness_json}" <<'PY'
import json
import sys

mode = sys.argv[1]
readiness = json.loads(sys.argv[2])
payload = {
    "status": "ok",
    "mode": mode,
    "readiness": readiness,
}
print(json.dumps(payload, indent=2))
PY
else
  printf 'status: ok\n'
  printf 'mode: %s\n' "${mode}"
  "${script_dir}/pm-doctor.sh" --config "${config_path}"
fi
