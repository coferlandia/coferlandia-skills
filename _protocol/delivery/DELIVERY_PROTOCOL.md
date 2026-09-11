# Coferlandia Delivery Protocol

Ordinary development keeps three separate responsibilities:

```text
DEVELOPMENT          QUALIFICATION                  INTEGRATION
chat-coder           ci (GITHUB_NATIVE)             merge
   |                 or local-ci (LOCAL)               |
READY_FOR_CI  ->          READY_FOR_MERGE      ->   COMPLETE
```

Aggregate release is a separate lifecycle over one exact release candidate:

```text
RELEASE QUALIFICATION / PROMOTION
chat-release (GITHUB_NATIVE) | local-release (LOCAL)
                 |
         READY_FOR_RELEASE
                 |
 repository-approved release integration
                 |
 coferlandia-release-publisher when formal publication is required
                 |
              COMPLETE
```

Explicit emergency remediation is an orchestration lifecycle rather than an alternative implementation engine:

```text
hotfix #issue | hotfix: <report>
          |
 create/reuse primary Issue
          |
 PERMANENT | TEMPORARY_MITIGATION
          |
 durable HOTFIX contract
          |
 repository-approved Development / Qualification / Integration
          |
 publication + reconciliation/verification when repository policy requires
          |
 HOTFIX_COMPLETE | HOTFIX_BLOCKED
```

For `TEMPORARY_MITIGATION`, a distinct permanent-fix Issue is mandatory before the emergency candidate becomes `HOTFIX_READY`; the hotfix may complete with production stabilized while that structural follow-up remains open.

Development, Qualification and Integration are separate responsibilities. Qualification strategy is explicitly selected; `LOCAL` and `GITHUB_NATIVE` are equal alternatives, not fallback paths. Release controllers preserve that same strategy distinction. `hotfix` is loaded only by explicit invocation and may orchestrate repository-approved owners without absorbing or weakening their contracts.

Durable state defaults to managed GitHub comments/records with exact candidate identity. Controllers re-read current repository/GitHub state on every invocation. Chat history, old local results and superseded checks are never authority.

Ordinary controller composition is left-to-right and exact. A controller verifies its own precondition and stops if it is not satisfied. No controller inserts a missing stage. The explicitly invoked `hotfix` controller is a declared higher-level orchestration surface and therefore owns only the emergency lifecycle described by `_protocol/delivery/HOTFIX.md`.
