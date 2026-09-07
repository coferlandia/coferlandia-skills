# Coferlandia Delivery Protocol

```text
DEVELOPMENT          QUALIFICATION                  INTEGRATION
chat-coder           ci (GITHUB_NATIVE)             merge
   |                 or local-ci (LOCAL)               |
READY_FOR_CI  ->          READY_FOR_MERGE      ->   COMPLETE
```

Development, Qualification and Integration are separate responsibilities. Qualification strategy is explicitly selected; `LOCAL` and `GITHUB_NATIVE` are equal alternatives, not fallback paths.

Durable state defaults to managed PR comments with exact candidate identity. Controllers re-read current repository/GitHub state on every invocation. Chat history, old local results and superseded checks are never authority.

Composition is left-to-right and exact. A controller verifies its own precondition and stops if it is not satisfied. No controller inserts a missing stage.
