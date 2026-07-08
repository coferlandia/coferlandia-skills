#!/usr/bin/env bash

config_lib_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./logging.sh
source "${config_lib_dir}/logging.sh"

pm_config_default_path() {
  printf '%s\n' ".agents/skills/coferlandia-project-manager/templates/config.template.json"
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
