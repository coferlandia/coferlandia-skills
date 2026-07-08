#!/usr/bin/env bash
set -euo pipefail

print_help() {
  cat <<'EOF'
Usage: pm-sync-to-obsidian.sh --config <path> [--json] [--dry-run] [--apply]
Description: Create or update Obsidian PM project and task notes from the PM registry.
EOF
}

reject_placeholder_invocation() {
  printf '%s\n' "Phase 3 entry point placeholder: sync execution is not implemented yet." >&2
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
    --json|--dry-run|--apply)
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
