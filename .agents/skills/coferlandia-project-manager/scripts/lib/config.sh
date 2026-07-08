#!/usr/bin/env bash

config_lib_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./logging.sh
source "${config_lib_dir}/logging.sh"

pm_config_default_path() {
  printf '%s\n' ".agents/skills/coferlandia-project-manager/templates/config.template.json"
}

pm_normalize_path_for_bash() {
  local path="$1"
  local normalized="$path"

  if [[ "$normalized" =~ ^([A-Za-z]):[\\/](.*)$ ]]; then
    local drive_letter
    local remainder
    drive_letter="${BASH_REMATCH[1],,}"
    remainder="${BASH_REMATCH[2]//\\//}"
    normalized="/mnt/${drive_letter}/${remainder}"
  fi

  printf '%s\n' "$normalized"
}

pm_config_json_value() {
  local config_path="$1"
  local key_path="$2"
  local python_cmd
  python_cmd="$(pm_python_cmd)"

"${python_cmd}" - "${config_path}" "${key_path}" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
key_path = sys.argv[2].split(".")
try:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid JSON in {config_path}: {exc}") from exc

value = payload
try:
    for key in key_path:
        value = value[key]
except (KeyError, TypeError) as exc:
    raise SystemExit(f"Missing config key: {'.'.join(key_path)}") from exc

if value is None:
    print("")
elif isinstance(value, (dict, list)):
    print(json.dumps(value))
else:
    print(value)
PY
}

pm_config_repos_root() {
  local config_path="$1"
  local repos_root
  repos_root="$(pm_config_json_value "$config_path" "repos_root")"
  pm_normalize_path_for_bash "$repos_root"
}

pm_config_default_branch() {
  local config_path="$1"
  pm_config_json_value "$config_path" "git.default_branch"
}

pm_require_file() {
  local path="$1"
  [[ -f "$path" ]] || die "Expected file not found: $path"
}

pm_python_cmd() {
  if command -v python >/dev/null 2>&1; then
    printf '%s\n' "python"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    printf '%s\n' "python3"
    return 0
  fi

  die "Python interpreter not found. Expected 'python' or 'python3' in PATH."
}
