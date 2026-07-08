#!/usr/bin/env bash
set -euo pipefail

print_help() {
  cat <<'EOF'
Usage: pm-project-report.sh --config <path> --project <slug> [--json]
Description: Generate a report for one managed project.

Output location:
  Default: .coferlandia/project-manager/reports/
EOF
}

reject_placeholder_invocation() {
  printf '%s\n' "Phase 5 entry point placeholder: project reporting is not implemented yet." >&2
  printf '%s\n' "Use --help to inspect the planned CLI contract." >&2
  exit 1
}

received_non_help_args=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      print_help
      exit 0
      ;;
    --config)
      shift
      [[ $# -gt 0 ]] || {
        printf 'Missing value for --config\n' >&2
        exit 1
      }
      received_non_help_args=true
      ;;
    --project)
      shift
      [[ $# -gt 0 ]] || {
        printf 'Missing value for --project\n' >&2
        exit 1
      }
      received_non_help_args=true
      ;;
    --json)
      received_non_help_args=true
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      exit 1
      ;;
  esac
  shift
done

if [[ "${received_non_help_args}" == "true" ]]; then
  reject_placeholder_invocation
fi

print_help
