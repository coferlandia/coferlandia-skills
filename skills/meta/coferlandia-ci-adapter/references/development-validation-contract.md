# Remote Development Validation Contract

Use this reference when adapting a repository so Chat Coder can finish Development validation without requiring its active client to execute the repository locally.

The shared semantic authority is `_protocol/delivery/DEVELOPMENT_VALIDATION.md`. This reference describes how `coferlandia-ci-adapter` materializes that contract.

## Repository-owned inputs

Discover, do not invent:

- `repository`: `owner/name`;
- `documentation`: current authoritative development/testing docs;
- `working_directory`: where Development commands run;
- `commands`: ordered cheap deterministic checks required before `READY_FOR_CI`;
- `required_services`: services the selected runner must make available;
- `environment`: variable names only, never values;
- `github.runner_labels`: the exact approved runner selector;
- `github.shell`: `bash` or `pwsh`.

Use the standard gate name `Development Validation / Gate` unless repository policy already owns another Development gate identity. The only supported allowed conclusion in v1 is `success`.

The workflow path must live under `.github/workflows/` and the candidate binding is always `pull-request-head`.

## Example semantic input

```json
{
  "schema_version": 1,
  "repository": "example/repo",
  "documentation": ["AGENTS.md", "docs/development.md"],
  "working_directory": ".",
  "commands": [
    {
      "id": "unit",
      "command": "python -m unittest",
      "purpose": "Run canonical Development tests"
    }
  ],
  "required_services": [],
  "environment": [],
  "github": {
    "submission": {
      "mode": "existing-pr-events",
      "workflow": ".github/workflows/coferlandia-development-validation.yml"
    },
    "candidate_binding": "pull-request-head",
    "runner_labels": ["ubuntu-latest"],
    "shell": "bash",
    "gate": {
      "name": "Development Validation / Gate",
      "allowed_conclusions": ["success"]
    }
  }
}
```

`development render` adds the deterministic `fingerprint` and writes both the contract and workflow.

## Safety

The generated workflow uses `pull_request` Draft lifecycle events, not `pull_request_target`. Candidate code receives only `contents: read` GitHub permission from the workflow. The adapter does not inject repository secrets or credential values.

Do not choose a self-hosted runner unless repository policy explicitly allows candidate code to execute there. Runner hardening and ambient host environment remain operator responsibilities.

## Idempotence and drift

The fingerprint excludes only the stored `fingerprint` field itself. Reordering JSON object keys does not change it. Any semantic change to commands, runner labels, shell, paths, services, environment names or gate identity changes the fingerprint.

Re-rendering the same input produces the same stored contract and workflow. Chat Coder must reject remote evidence bound to an older fingerprint or candidate SHA.

## Stage boundary

This surface is Development-only. Do not encode Qualification gates, merge-group behavior, release publication, deployment or exceptional-lane authority here. Those remain owned by their existing contracts.
