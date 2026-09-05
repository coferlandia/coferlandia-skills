from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

from .git_service import GitService
from .github_service import GitHubService
from .model import ReleaseArtifact, ReleaseError, ReleasePlan, fingerprint, write_json
from .policy import validate_policy
from .semver import SemVer, validate_requested_version

def classify_consistency(tag_info: dict[str, Any] | None, release_info: dict[str, Any] | None, target_sha: str) -> str:
    if tag_info is None and release_info is None:
        return "NEW"
    if tag_info is None or tag_info.get("kind") != "annotated" or tag_info.get("commit") != target_sha:
        return "INCONSISTENT"
    if release_info is None:
        return "TAG_ONLY_CORRECT"
    if tag_info.get("tag") is not None and release_info.get("tag") != tag_info.get("tag"):
        return "INCONSISTENT"
    return "DRAFT_CORRECT" if release_info.get("draft") else "PUBLISHED_CONSISTENT"

def _version_from_tag(tag: str, prefix: str) -> str | None:
    if not tag.startswith(prefix):
        return None
    value = tag[len(prefix):]
    try:
        SemVer.parse(value)
    except ValueError:
        return None
    return value

def _release_snapshot(releases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"id": item.get("id"), "tag": item.get("tag"), "draft": item.get("draft"), "prerelease": item.get("prerelease"), "published_at": item.get("published_at")} for item in releases if not item.get("draft")]

def _allowed_refs(policy: dict[str, Any], default_branch: str) -> list[str]:
    refs = policy.get("release_refs") or [f"refs/heads/{default_branch}"]
    return [item if item.startswith("refs/") else f"refs/heads/{item}" for item in refs]

def _local_ref_candidates(ref: str) -> list[str]:
    if ref.startswith("refs/heads/"):
        name = ref.removeprefix("refs/heads/")
        return [ref, f"refs/remotes/origin/{name}"]
    return [ref]

def discover_previous_release(git: GitService, releases: list[dict[str, Any]], target: str, prefix: str, explicit_tag: str | None = None) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for release in releases:
        if release.get("draft"):
            continue
        tag = release.get("tag")
        if not isinstance(tag, str):
            continue
        version = _version_from_tag(tag, prefix)
        if version is None:
            continue
        if explicit_tag is not None and tag != explicit_tag:
            continue
        tag_info = git.remote_tag_info(tag) or git.tag_info(tag)
        if not tag_info or tag_info.get("kind") != "annotated":
            continue
        commit = tag_info.get("commit")
        if not isinstance(commit, str) or not git.is_ancestor(commit, target):
            continue
        candidates.append({"version": version, "tag": tag, "commit": commit, "published_at": release.get("published_at"), "prerelease": bool(release.get("prerelease")), "distance": git.distance(commit, target)})
    if explicit_tag is not None:
        if not candidates:
            raise ReleaseError(f"explicit previous release {explicit_tag} is not a valid ancestor of target")
        return candidates[0]
    if not candidates:
        return None
    minimum = min(item["distance"] for item in candidates)
    nearest = [item for item in candidates if item["distance"] == minimum]
    if len({item["commit"] for item in nearest}) > 1:
        raise ReleaseError("previous release is ambiguous across the target lineage")
    nearest.sort(key=lambda item: SemVer.parse(item["version"]), reverse=True)
    return nearest[0]

def _evaluate_required_checks(required: list[str], observed: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    evidence: list[dict[str, Any]] = []
    errors: list[str] = []
    by_name: dict[str, list[dict[str, Any]]] = {}
    for item in observed:
        by_name.setdefault(str(item.get("name")), []).append(item)
    for name in required:
        matches = by_name.get(name, [])
        if not matches:
            errors.append(f"required GitHub check is missing: {name}")
            evidence.append({"name": name, "status": "missing", "conclusion": None, "url": None})
            continue
        item = matches[-1]
        evidence.append({"name": name, "status": item.get("status"), "conclusion": item.get("conclusion"), "url": item.get("url")})
        if item.get("status") != "completed" or item.get("conclusion") != "success":
            errors.append(f"required GitHub check is not successful: {name}")
    return evidence, errors

def inspect_release(root: Path, repository: str, target_revision: str, policy: dict[str, Any], *, previous_tag: str | None = None, refresh: bool = True, git: GitService | None = None, github: GitHubService | None = None) -> dict[str, Any]:
    validate_policy(policy)
    git = git or GitService(root)
    github = github or GitHubService()
    if refresh:
        git.refresh_tags()
    repo_info = github.repository_info(repository)
    default_branch = repo_info.get("default_branch")
    if not default_branch:
        raise ReleaseError("GitHub repository has no default branch")
    target = git.resolve_commit(target_revision)
    refs = _allowed_refs(policy, default_branch)
    reachable = any(any(git.is_reachable_from(target, candidate) for candidate in _local_ref_candidates(ref)) for ref in refs)
    releases = github.list_releases(repository)
    prefix = policy["versioning"]["tag_prefix"]
    non_semver = [item["tag"] for item in releases if not item.get("draft") and isinstance(item.get("tag"), str) and _version_from_tag(item["tag"], prefix) is None]
    previous = discover_previous_release(git, releases, target, prefix, explicit_tag=previous_tag)
    previous_commit = previous["commit"] if previous else None
    observed_checks = github.checks_for_commit(repository, target) if policy["validation"]["required_github_checks"] else []
    validation, check_errors = _evaluate_required_checks(policy["validation"]["required_github_checks"], observed_checks)
    immutability = None
    mode = policy["github_release"]["immutability"]
    if mode in {"observe", "required"}:
        try:
            immutability = github.immutable_releases_status(repository)
        except ReleaseError as exc:
            immutability = {"enabled": None, "enforced_by_owner": None, "observable": False, "error": str(exc)}
            if mode == "required":
                check_errors.append("immutable releases are required by policy but their repository setting could not be verified")
        if mode == "required" and immutability.get("enabled") is not True:
            check_errors.append("immutable releases are required by policy but are not enabled")
    errors = list(check_errors)
    if not reachable:
        errors.append("target commit is not reachable from an allowed release ref")
    snapshot = {"target": target, "allowed_refs": refs, "published_releases": _release_snapshot(releases), "previous_release": previous, "required_checks": validation, "immutability": immutability}
    return {"schema_version": 1, "repository": repository, "default_branch": default_branch, "target_revision": target_revision, "target_commit": target, "allowed_release_refs": refs, "eligible": not errors, "previous_release": previous, "commits": git.commits_between(previous_commit, target), "changed_paths": git.changed_paths(previous_commit, target), "target_tags": git.tags_for_commit(target), "validation": validation, "immutability": immutability, "non_semver_release_tags": non_semver, "errors": errors, "inspection_fingerprint": fingerprint(snapshot)}

def build_plan(root: Path, repository: str, inspection: dict[str, Any], policy: dict[str, Any], *, impact: str, version: str, title: str, release_notes: str, prerelease: bool = False, artifact_paths: list[Path] | None = None, provenance: str | None = None, git: GitService | None = None, github: GitHubService | None = None) -> ReleasePlan:
    validate_policy(policy)
    if not inspection.get("eligible"):
        raise ReleaseError("release target is not eligible: " + "; ".join(inspection.get("errors", [])))
    if inspection.get("non_semver_release_tags"):
        raise ReleaseError("existing release history uses non-SemVer tags; a stronger local publication policy is required")
    previous = inspection.get("previous_release")
    validate_requested_version(previous.get("version") if previous else None, version, impact)
    parsed = SemVer.parse(version)
    if bool(parsed.prerelease) != bool(prerelease):
        raise ReleaseError("prerelease flag must match semantic version prerelease identifier")
    tag = f"{policy['versioning']['tag_prefix']}{version}"
    git = git or GitService(root)
    github = github or GitHubService()
    state = classify_consistency(git.remote_tag_info(tag) or git.tag_info(tag), github.release_by_tag(repository, tag), inspection["target_commit"])
    if state == "INCONSISTENT":
        raise ReleaseError(f"release identity {tag} is inconsistent")
    artifacts = [ReleaseArtifact.from_path(path).__dict__.copy() for path in (artifact_paths or [])]
    provenance_mode = provenance or policy["provenance"]["manifest"]
    if provenance_mode not in {"optional", "required", "disabled"}:
        raise ReleaseError(f"unsupported provenance mode: {provenance_mode}")
    operations = []
    if state == "NEW":
        operations.extend([f"create annotated tag {tag} at {inspection['target_commit']}", f"push tag {tag} without force"])
    if state in {"NEW", "TAG_ONLY_CORRECT"}:
        operations.append(f"create draft GitHub Release {tag} referencing the existing tag")
    if artifacts:
        operations.append("upload and verify declared release artifacts")
    if provenance_mode in {"optional", "required"}:
        operations.append("generate/upload release-manifest.json provenance asset")
    if state != "PUBLISHED_CONSISTENT":
        operations.append("publish verified draft GitHub Release")
    operations.append("verify tag/release/SHA consistency")
    return ReleasePlan(schema_version=1, repository=repository, target_commit=inspection["target_commit"], previous_release=previous, impact=impact, version=version, tag=tag, title=title, release_notes=release_notes, prerelease=prerelease, artifacts=artifacts, provenance=provenance_mode, policy=policy, policy_fingerprint=fingerprint(policy), inspection_fingerprint=inspection["inspection_fingerprint"], observed_state=state, validation=inspection.get("validation", []), operations=operations)

def _asset_digest(asset: dict[str, Any]) -> str | None:
    digest = asset.get("sha256")
    return digest if isinstance(digest, str) and len(digest) == 64 else None

def _verify_or_upload_artifacts(github: GitHubService, repository: str, release: dict[str, Any], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    current = {item["name"]: item for item in release.get("assets", [])}
    for artifact in artifacts:
        path = Path(artifact["path"])
        fresh = ReleaseArtifact.from_path(path)
        if fresh.sha256 != artifact["sha256"]:
            raise ReleaseError(f"artifact changed since dry-run: {artifact['name']}")
        existing = current.get(artifact["name"])
        if existing:
            if _asset_digest(existing) != artifact["sha256"]:
                raise ReleaseError(f"release asset conflicts with planned digest: {artifact['name']}")
            continue
        github.upload_asset(repository, int(release["id"]), path, artifact["name"])
        release = github.release_by_id(repository, int(release["id"]))
        current = {item["name"]: item for item in release.get("assets", [])}
    return release

def _manifest_payload(plan: ReleasePlan, release: dict[str, Any]) -> dict[str, Any]:
    previous = plan.previous_release or {}
    return {"schema_version": 1, "repository": plan.repository, "version": plan.version, "tag": plan.tag, "commit": plan.target_commit, "previous_version": previous.get("version"), "previous_tag": previous.get("tag"), "impact": plan.impact, "created_at": release.get("created_at"), "policy_schema_version": plan.policy.get("schema_version"), "plan_sha256": fingerprint(plan.to_dict()), "artifacts": [{"name": item["name"], "sha256": item["sha256"]} for item in plan.artifacts]}

def _ensure_manifest(root: Path, github: GitHubService, plan: ReleasePlan, release: dict[str, Any]) -> dict[str, Any]:
    if plan.provenance == "disabled":
        return release
    path = root / ".agent/release-publisher/release-manifest.json"
    write_json(path, _manifest_payload(plan, release))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    existing = next((item for item in release.get("assets", []) if item.get("name") == "release-manifest.json"), None)
    if existing:
        if _asset_digest(existing) != digest:
            raise ReleaseError("existing release-manifest.json conflicts with planned provenance")
        return release
    github.upload_asset(plan.repository, int(release["id"]), path, "release-manifest.json")
    return github.release_by_id(plan.repository, int(release["id"]))

def _read_manifest(github: GitHubService, repository: str, release: dict[str, Any]) -> dict[str, Any] | None:
    asset = next((item for item in release.get("assets", []) if item.get("name") == "release-manifest.json"), None)
    if not asset or not asset.get("id"):
        return None
    try:
        value = json.loads(github.download_text_asset(repository, int(asset["id"])))
    except (json.JSONDecodeError, ReleaseError) as exc:
        raise ReleaseError("release-manifest.json could not be read as JSON") from exc
    return value if isinstance(value, dict) else None

def verify_release(root: Path, repository: str, tag: str, policy: dict[str, Any], *, git: GitService | None = None, github: GitHubService | None = None) -> dict[str, Any]:
    validate_policy(policy)
    git = git or GitService(root)
    github = github or GitHubService()
    git.refresh_tags()
    tag_info = git.remote_tag_info(tag) or git.tag_info(tag)
    release = github.release_by_tag(repository, tag)
    errors: list[str] = []
    target = tag_info.get("commit") if tag_info else ""
    state = classify_consistency(tag_info, release, target)
    if state != "PUBLISHED_CONSISTENT":
        errors.append(f"release consistency state is {state}")
    manifest = _read_manifest(github, repository, release) if release else None
    if manifest and (manifest.get("tag") != tag or manifest.get("commit") != target or manifest.get("repository") != repository):
        errors.append("release manifest disagrees with tag/release identity")
    prefix = policy["versioning"]["tag_prefix"]
    version = _version_from_tag(tag, prefix)
    previous = discover_previous_release(git, [item for item in github.list_releases(repository) if item.get("tag") != tag], target, prefix) if target and version else None
    immutability = None
    mode = policy["github_release"]["immutability"]
    if mode in {"observe", "required"}:
        try:
            immutability = github.immutable_releases_status(repository)
        except ReleaseError as exc:
            immutability = {"enabled": None, "enforced_by_owner": None, "observable": False, "error": str(exc)}
            if mode == "required":
                errors.append("immutable releases required by policy could not be verified")
        if mode == "required" and immutability.get("enabled") is not True:
            errors.append("immutable releases required by policy are not enabled")
    return {"schema_version": 1, "repository": repository, "tag": tag, "version": version, "commit": target or None, "release": release, "previous_release": previous, "provenance": manifest, "immutability": immutability, "consistency": "pass" if not errors else "fail", "errors": errors}

def resolve_release(root: Path, repository: str, tag: str, policy: dict[str, Any], *, git: GitService | None = None, github: GitHubService | None = None) -> dict[str, Any]:
    verified = verify_release(root, repository, tag, policy, git=git, github=github)
    if verified["consistency"] != "pass":
        raise ReleaseError("cannot resolve inconsistent release: " + "; ".join(verified["errors"]))
    release = verified["release"]
    previous = verified["previous_release"] or {}
    assets = [item for item in release.get("assets", []) if item.get("name") != "release-manifest.json"]
    return {"schema_version": 1, "repository": repository, "version": verified["version"], "tag": tag, "commit": verified["commit"], "created_at": release.get("created_at"), "published_at": release.get("published_at"), "title": release.get("title"), "release_notes": release.get("body"), "prerelease": release.get("prerelease"), "immutable": release.get("immutable"), "previous_version": previous.get("version"), "previous_tag": previous.get("tag"), "artifacts": assets, "provenance": verified["provenance"], "consistency": "pass"}

def publish_release(root: Path, plan: ReleasePlan, *, git: GitService | None = None, github: GitHubService | None = None) -> dict[str, Any]:
    policy = validate_policy(plan.policy)
    if fingerprint(policy) != plan.policy_fingerprint:
        raise ReleaseError("release plan policy fingerprint does not match embedded policy")
    git = git or GitService(root)
    github = github or GitHubService()
    git.refresh_tags()
    state = classify_consistency(git.remote_tag_info(plan.tag) or git.tag_info(plan.tag), github.release_by_tag(plan.repository, plan.tag), plan.target_commit)
    if state == "INCONSISTENT":
        raise ReleaseError("existing tag/release state is inconsistent")
    if state == "PUBLISHED_CONSISTENT":
        return {"status": "already_consistent", "release": resolve_release(root, plan.repository, plan.tag, policy, git=git, github=github)}
    reinspection = inspect_release(root, plan.repository, plan.target_commit, policy, previous_tag=(plan.previous_release or {}).get("tag"), refresh=False, git=git, github=github)
    if reinspection["inspection_fingerprint"] != plan.inspection_fingerprint:
        raise ReleaseError("release plan is stale; authoritative release state changed after dry-run")
    if not reinspection["eligible"]:
        raise ReleaseError("release is no longer eligible: " + "; ".join(reinspection["errors"]))
    if state == "NEW":
        git.create_annotated_tag(plan.tag, plan.target_commit, f"Release {plan.tag}", sign=policy["tag"]["signing"] == "required")
        try:
            git.push_tag(plan.tag)
        except ReleaseError:
            remote = git.remote_tag_info(plan.tag)
            if not remote or remote.get("kind") != "annotated" or remote.get("commit") != plan.target_commit:
                raise
        remote = git.remote_tag_info(plan.tag)
        if not remote or remote.get("kind") != "annotated" or remote.get("commit") != plan.target_commit:
            raise ReleaseError("remote tag verification failed after publication")
        state = "TAG_ONLY_CORRECT"
    if state == "TAG_ONLY_CORRECT":
        release = github.create_draft_release(plan.repository, plan.tag, plan.title, plan.release_notes, plan.prerelease)
        if not release.get("draft") or release.get("tag") != plan.tag:
            raise ReleaseError("GitHub did not create the expected draft release")
        state = "DRAFT_CORRECT"
    if state == "DRAFT_CORRECT":
        release = github.release_by_tag(plan.repository, plan.tag)
        if not release:
            raise ReleaseError("draft release disappeared during publication")
        release = _verify_or_upload_artifacts(github, plan.repository, release, plan.artifacts)
        release = _ensure_manifest(root, github, plan, release)
        github.publish_release(plan.repository, int(release["id"]))
    verified = verify_release(root, plan.repository, plan.tag, policy, git=git, github=github)
    if verified["consistency"] != "pass":
        raise ReleaseError("published release failed final verification: " + "; ".join(verified["errors"]))
    return {"status": "published", "release": resolve_release(root, plan.repository, plan.tag, policy, git=git, github=github)}
