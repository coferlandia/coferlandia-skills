# Coferlandia Vendor Integrity

Coferlandia can be vendored into repositories that keep local copies of public Chat prompts,
Agent Skills, and shared delivery protocol files. Exact vendoring must be mechanically
verifiable: source version metadata alone is not enough.

## Public families

The vendor manifest generator maps public artifacts into stable consumer paths:

- `prompts`: `prompts/**` -> `.agents/prompts/**`
- `delivery`: `_protocol/delivery/**` -> `_protocol/delivery/**`
- `skill:<name>`: `skills/<category>/<name>/**` -> `.agents/skills/<name>/**`

Repository-local files outside selected upstream families are not errors. Modifying an
upstream-owned path in an exact selected family is drift.

## Generate a manifest

From an exact Coferlandia source checkout:

```bash
python _protocol/distribution/vendor_manifest.py generate \
  --root . \
  --release-version <release-version> \
  --source-revision <40-char-source-sha> \
  --output /path/to/vendor-manifest.json
```

The manifest contains exact SHA-256 values for every public artifact and a deterministic
`manifest_fingerprint`.

The recorded source revision identifies the source checkout whose public bytes were
manifested. Finalize the public artifact contents first, then generate the manifest. The
manifest/checker files themselves are intentionally outside the distributed families, so
there is no self-hash cycle.

## Consumer provenance

Consumers keep a small JSON file beside their vendored source metadata:

```json
{
  "schema_version": 1,
  "source_repository": "coferlandia/coferlandia-skills",
  "source_release_version": "<release-version>",
  "source_revision": "<40-char-source-sha>",
  "manifest_fingerprint": "<sha256>",
  "families": [
    "prompts",
    "delivery",
    "skill:coferlandia-ci-adapter"
  ],
  "artifacts": [
    ".agents/prompts/chat-coder.md",
    ".agents/prompts/ci.md",
    "_protocol/delivery/READY_FOR_CI.md"
  ],
  "overlays": [
    {
      "consumer_path": ".agents/prompts/registry.json",
      "reason": "repository-local aliases extend the upstream registry"
    }
  ]
}
```

Families bound the upstream namespace. When `artifacts` is omitted, every manifest entry in the listed families is exact. When `artifacts` is present, only those explicit consumer paths are exact; every selected path must exist in the source manifest. `overlays` documents intentional non-exact upstream paths with a non-empty reason. An exact artifact and overlay may not overlap, and unknown artifact/overlay paths fail closed. Local-only skills/prompts remain allowed outside upstream-owned paths.

## Offline verification

```bash
python _protocol/distribution/vendor_manifest.py check \
  --root . \
  --manifest .agents/vendor/coferlandia-vendor-manifest.json \
  --provenance .agents/vendor/coferlandia-vendor-provenance.json
```

The command fails closed on:

- missing expected artifact;
- one-byte content drift;
- mismatched source repository/release/revision;
- invalid manifest fingerprint;
- provenance manifest fingerprint mismatch;
- unknown selected family;
- unknown exact artifact path;
- unknown/invalid overlay declaration;
- overlap between an exact artifact and declared overlay.

It does not use GitHub or any network service.

## Source verification

A source repository may prove that a previously generated manifest still matches the current
public bytes:

```bash
python _protocol/distribution/vendor_manifest.py check-source \
  --root . \
  --manifest /path/to/vendor-manifest.json
```

## Local adaptations

Do not silently modify an exact upstream-owned path while preserving the upstream version.
A consumer that needs a true adaptation should either:

1. upstream the generic behavior and re-vendor the released artifact; or
2. declare the specific upstream path as a provenance `overlay` with an explicit reason when the consumer intentionally maintains that path locally.

Prefer exact artifact selection for runtime subsets rather than copying upstream tests that the consumer does not install. The source manifest remains complete; consumer provenance decides which installed paths are exact and which are explicit overlays. The checker intentionally treats same-version/different-bytes as drift for every exact artifact.
