#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"

print_help() {
  cat <<'EOF'
Usage: pm-check-superpowers-skills.sh [--config <path>] [--json]
Description: Compatibility wrapper that checks Superpowers skills through the generic external-skill resolver.
EOF
}

json_output=false
config_path="$(pm_config_template_path)"

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

pm_require_file "${config_path}"
python_cmd="$(pm_python_cmd)"
provider_json="$("${python_cmd}" "${script_dir}/pm-external-skills.py" --config "${config_path}" --provider superpowers --json)"

"${python_cmd}" - "${provider_json}" "${json_output}" <<'PY'
import json
import sys

provider = json.loads(sys.argv[1])
json_output = sys.argv[2].lower() == "true"
skills = provider["skills"]
payload = {
    "status": "ok" if not skills["required_missing"] else "partial",
    "required_available": skills["required_available"],
    "required_missing": skills["required_missing"],
    "optional_available": skills["optional_available"],
    "optional_missing": skills["optional_missing"],
    "repository_url": provider.get("repository_url"),
}

if json_output:
    print(json.dumps(payload, indent=2))
else:
    print(f"status: {payload['status']}")
    print(f"repository: {payload['repository_url']}")
    print(f"required_available: {', '.join(payload['required_available']) if payload['required_available'] else 'none'}")
    print(f"required_missing: {', '.join(payload['required_missing']) if payload['required_missing'] else 'none'}")
    print(f"optional_available: {', '.join(payload['optional_available']) if payload['optional_available'] else 'none'}")
    print(f"optional_missing: {', '.join(payload['optional_missing']) if payload['optional_missing'] else 'none'}")
PY
