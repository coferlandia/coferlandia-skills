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
  pm-onboard.sh --dry-run
  pm-onboard.sh --json
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

config_path="$(pm_resolve_config_path "${config_path}")"
config_exists=false
config_preexisting=false
config_generated=false
readiness_json=""
[[ -f "${config_path}" ]] && config_exists=true
config_preexisting="${config_exists}"

if [[ "${config_exists}" == false && "${mode}" == "apply" ]]; then
  "${script_dir}/pm-generate-config.sh" --config "${config_path}" --apply --json >/dev/null
  config_exists=true
  config_generated=true
fi

if [[ "${config_exists}" == true ]]; then
  readiness_json="$("${script_dir}/pm-doctor.sh" --config "${config_path}" --json)"
fi

if [[ "${json_output}" == true ]]; then
  python_cmd="$(pm_python_cmd)"
  "${python_cmd}" - "${mode}" "${config_path}" "${config_exists}" "${config_preexisting}" "${config_generated}" "${readiness_json}" <<'PY'
import json
import sys

mode = sys.argv[1]
config_path = sys.argv[2]
config_exists = sys.argv[3].lower() == "true"
config_preexisting = sys.argv[4].lower() == "true"
config_generated = sys.argv[5].lower() == "true"
readiness = json.loads(sys.argv[6]) if sys.argv[6] else None
payload = {
    "status": "ok",
    "mode": mode,
    "config_path": config_path,
    "config_exists": config_exists,
    "config_preexisting": config_preexisting,
}
if readiness is not None:
    payload["readiness"] = readiness
if config_generated:
    payload["config_generation"] = {"status": "applied"}
if not config_exists and mode != "apply":
    payload["readiness"] = {"status": "missing"}
    payload["next_approved_action"] = "generate_config"
print(json.dumps(payload, indent=2))
PY
else
  printf 'status: ok\n'
  printf 'mode: %s\n' "${mode}"
  printf 'config_path: %s\n' "${config_path}"
  printf 'config_preexisting: %s\n' "${config_preexisting}"
  if [[ "${config_exists}" == true ]]; then
    if [[ "${config_generated}" == true ]]; then
      printf 'config_generation_status: applied\n'
    fi
    "${script_dir}/pm-doctor.sh" --config "${config_path}"
  else
    printf 'config_status: missing\n'
    printf 'next_approved_action: generate_config\n'
  fi
fi
