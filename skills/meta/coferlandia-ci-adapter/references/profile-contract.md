# Profile Contract

Canonical path: `.coferlandia/ci/profile.json`; schema owner: `_protocol/delivery/ci-profile.schema.json`.

The profile describes static facts required by Qualification: repository identity, canonical docs, local qualification entrypoints/services/environment-variable names, GitHub submission/gates, merge-group authority, identity sensitivity and externally authorized exceptional lanes. It contains no current run/result state, environment values, or credentials.

The `fingerprint` is SHA-256 over canonical JSON excluding the fingerprint field itself. Any material profile change therefore creates a new qualification identity.

## GitHub submission activation

`github.submission.mode = existing-pr-events` may optionally declare `activation.kind = ready-for-review`. The activation is static repository policy and participates in the profile fingerprint. It tells the GitHub-native `ci` controller that the repository authorizes exactly one Draft -> Ready mutation only after the exact current `READY_FOR_CI` has been validated. It is not Development evidence, merge authority, or a retry mechanism.

Profiles that omit `activation` keep their existing passive/event semantics. `workflow-dispatch` and `none` submissions reject `ready-for-review` activation.
