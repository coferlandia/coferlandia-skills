#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"

print_help() {
  cat <<'EOF'
Usage: pm-detect-superpowers.sh [--config <path>] [--json]
Description: Compatibility wrapper that detects Superpowers through the generic external-skill resolver.
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
instances = provider.get("instances", [])
roots = [item.get("skill_root") for item in instances if item.get("skill_root")]
payload = {
    "status": "ok" if provider.get("present") else "missing",
    "presence": provider.get("presence"),
    "roots": roots,
    "repository_url": provider.get("repository_url"),
    "tested": provider.get("tested", {}),
}

if json_output:
    print(json.dumps(payload, indent=2))
else:
    print(f"status: {payload['status']}")
    print(f"repository: {payload['repository_url']}")
    if roots:
        print("roots:")
        for root in roots:
            print(f"- {root}")
    else:
        print("roots: none")
PY
