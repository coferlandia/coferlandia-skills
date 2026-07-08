#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"
# shellcheck source=./lib/reporting.sh
source "${script_dir}/lib/reporting.sh"

print_help() {
  cat <<'EOF'
Usage: pm-portfolio-report.sh --config <path> [--json] [--output-dir <dir>]
Description: Generate a portfolio-wide report answering all reporting questions.

Options:
  --config <path>   Required path to the PM config.json.
  --json            Emit machine-readable JSON instead of Markdown.
  --output-dir <dir> Write report to this directory (default: .coferlandia/project-manager/reports/).
                     Ignored when --json is used (prints to stdout).
  -h, --help        Show this help and exit.

Output location:
  Default: .coferlandia/project-manager/reports/
EOF
}

config_path=""
json_output=false
output_dir=""

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
    --output-dir)
      shift
      [[ $# -gt 0 ]] || die "Missing value for --output-dir"
      output_dir="$1"
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

default_branch="$(pm_config_default_branch "${config_path}")"
[[ -n "${default_branch}" ]] || default_branch="main"

format_flag="json"
[[ "${json_output}" == false ]] && format_flag="markdown"

python_cmd="$(pm_python_cmd)"
report_output="$("${python_cmd}" "${script_dir}/lib/reporting.py" portfolio-report \
  --repos-root "${repos_root}" \
  --format "${format_flag}" \
  --default-branch "${default_branch}" \
)"

if [[ "${json_output}" == true ]]; then
  printf '%s\n' "${report_output}"
else
  printf '%s\n' "${report_output}"

  if [[ -n "${output_dir}" ]]; then
    resolved_dir="$(pm_report_output_dir "${output_dir}")"
    written_path="$(printf '%s\n' "${report_output}" | pm_write_report "${resolved_dir}" "portfolio-report" "md")"
    log_info "Report written to: ${written_path}"
  fi
fi
