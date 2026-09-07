# Profile Contract

Canonical path: `.coferlandia/ci/profile.json`; schema owner: `_protocol/delivery/ci-profile.schema.json`.

The profile describes static facts required by Qualification: repository identity, canonical docs, local qualification entrypoints/services/environment, GitHub submission/gates, merge-group authority, identity sensitivity and externally authorized exceptional lanes. It contains no current run/result state or credentials.

The `fingerprint` is SHA-256 over canonical JSON excluding the fingerprint field itself. Any material profile change therefore creates a new qualification identity.
