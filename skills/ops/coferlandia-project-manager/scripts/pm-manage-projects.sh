#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/config.sh
source "${script_dir}/lib/config.sh"
# shellcheck source=./lib/git.sh
source "${script_dir}/lib/git.sh"

print_help() {
  cat <<'EOF'
Usage: pm-manage-projects.sh <command> [options]
Description: Manage the explicit list of projects in projects.json.

Commands:
  add <path> [--slug <slug>]   Register a project (path must be a git repo).
  remove <slug|path>           Archive a project (status -> archived; not deleted).
  list [--json]                Print active projects.

Options:
  --config <path>        Config path (derives the projects.json location).
  --projects-file <path> Explicit projects.json path (overrides --config).
  --json                 JSON output (for list, and for add/remove status).
  --help, -h             Show this help.
EOF
}

config_path=""
projects_file_arg=""
json_output=false
slug_arg=""

# Parse global options first, then a subcommand and its args.
subcommand=""
target=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      shift
      [[ $# -gt 0 ]] || die "Missing value for --config"
      config_path="$1"
      ;;
    --projects-file)
      shift
      [[ $# -gt 0 ]] || die "Missing value for --projects-file"
      projects_file_arg="$1"
      ;;
    --json)
      json_output=true
      ;;
    --slug)
      shift
      [[ $# -gt 0 ]] || die "Missing value for --slug"
      slug_arg="$1"
      ;;
    --help|-h)
      print_help
      exit 0
      ;;
    add|remove|list)
      subcommand="$1"
      shift
      break
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
  shift
done

[[ -n "${subcommand}" ]] || { print_help; exit 1; }

# Remaining args belong to the subcommand.
if [[ "${subcommand}" == "add" || "${subcommand}" == "remove" ]]; then
  [[ $# -gt 0 ]] || die "${subcommand} requires a <path> (add) or <slug|path> (remove) argument"
  target="$1"
fi

config_path="$(pm_resolve_config_path "${config_path}")"
projects_file="$(pm_resolve_projects_path "${projects_file_arg}" "${config_path}")"
python_cmd="$(pm_python_cmd)"

# Ensure projects.json exists (seed from template if missing).
ensure_projects_file() {
  if [[ ! -f "${projects_file}" ]]; then
    mkdir -p "$(dirname -- "${projects_file}")"
    cp "$(pm_projects_template_path)" "${projects_file}"
  fi
}

case "${subcommand}" in
  add)
    target_path="$(cd -- "${target}" 2>/dev/null && pwd)" || die "Path does not exist: ${target}"
    pm_git_is_repo "${target_path}" || die "Not a git repository: ${target_path}"

    slug="${slug_arg:-$(basename -- "${target_path}")}"
    ensure_projects_file

    "${python_cmd}" - "${projects_file}" "${target_path}" "${slug}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

projects_file = Path(sys.argv[1])
target_path = sys.argv[2]
slug = sys.argv[3]

payload = json.loads(projects_file.read_text(encoding="utf-8"))
projects = payload.get("projects", [])

resolved = str(Path(target_path).resolve())
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# First, reject duplicates among ACTIVE entries (by path or slug).
for entry in projects:
    if entry.get("status", "active") != "active":
        continue
    if entry.get("path") and str(Path(entry["path"]).resolve()) == resolved:
        raise SystemExit(f"Active project already registered at path: {resolved}")
    if entry.get("slug") == slug:
        raise SystemExit(f"Active project already uses slug: {slug}")

# Otherwise, either reactivate an archived entry with the same slug/path,
# or append a brand-new entry.
for entry in projects:
    same_path = bool(entry.get("path")) and str(Path(entry["path"]).resolve()) == resolved
    if entry.get("slug") == slug or same_path:
        entry["path"] = resolved
        entry["slug"] = slug
        entry["status"] = "active"
        entry["added_at"] = now_iso
        break
else:
    projects.append({
        "slug": slug,
        "path": resolved,
        "added_at": now_iso,
        "status": "active",
    })

payload["projects"] = projects
projects_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "ok",
    "action": "add",
    "slug": slug,
    "path": resolved,
    "projects_file": str(projects_file),
    "active_count": sum(1 for e in projects if e.get("status", "active") == "active"),
}, indent=2))
PY
    ;;
  remove)
    ensure_projects_file
    "${python_cmd}" - "${projects_file}" "${target}" <<'PY'
import json
import sys
from pathlib import Path

projects_file = Path(sys.argv[1])
target = sys.argv[2]

payload = json.loads(projects_file.read_text(encoding="utf-8"))
projects = payload.get("projects", [])

# Match by slug (exact) or by path (resolved equality).
resolved_target = None
try:
    resolved_target = str(Path(target).resolve())
except Exception:
    resolved_target = None

matched = None
for entry in projects:
    if entry.get("status", "active") != "active":
        continue
    if entry.get("slug") == target:
        matched = entry
        break
    if resolved_target is not None and entry.get("path"):
        try:
            if str(Path(entry["path"]).resolve()) == resolved_target:
                matched = entry
                break
        except Exception:
            pass

if matched is None:
    raise SystemExit(f"No active project matched: {target}")

matched["status"] = "archived"
payload["projects"] = projects
projects_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "ok",
    "action": "remove",
    "slug": matched.get("slug"),
    "path": matched.get("path"),
    "projects_file": str(projects_file),
    "active_count": sum(1 for e in projects if e.get("status", "active") == "active"),
}, indent=2))
PY
    ;;
  list)
    ensure_projects_file
    "${python_cmd}" - "${projects_file}" "${json_output}" <<'PY'
import json
import sys
from pathlib import Path

projects_file = Path(sys.argv[1])
json_output = sys.argv[2].lower() == "true"

payload = json.loads(projects_file.read_text(encoding="utf-8"))
active = [e for e in payload.get("projects", []) if e.get("status", "active") == "active"]

if json_output:
    print(json.dumps({
        "status": "ok",
        "projects_file": str(projects_file),
        "projects_detected": len(active),
        "projects": active,
    }, indent=2))
else:
    print("status: ok")
    print(f"projects_file: {projects_file}")
    print(f"projects_detected: {len(active)}")
    for entry in active:
        print(f"{entry.get('slug', '')}\t{entry.get('path', '')}")
PY
    ;;
esac
