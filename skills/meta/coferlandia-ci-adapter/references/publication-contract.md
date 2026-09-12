# GitHub-native release publication contract

Use this reference only when repository adaptation explicitly includes complete Coferlandia GITHUB_NATIVE release delivery.

## Boundary

Qualification, Integration and Publication are separate authorities:

- `.coferlandia/ci/profile.json` describes Qualification only.
- repository release policy describes Integration/Publication topology and local decisions.
- `chat-release` orchestrates the GITHUB_NATIVE release lifecycle.
- `coferlandia-release-publisher` exclusively owns exact Commit -> annotated tag -> GitHub Release mechanics.
- the repository publication workflow is only a GitHub-native transport for the publisher.

Never add publication fields to `.coferlandia/ci/profile.json`.

## Policy extension

The adapter owns only the optional `publication.github` transport block. Other `publication` members belong to repository policy or another controller and MUST be preserved.

Supported forms:

```json
{
  "publication": {
    "github": {
      "mode": "none"
    }
  }
}
```

or:

```json
{
  "publication": {
    "github": {
      "mode": "workflow-dispatch",
      "workflow": ".github/workflows/coferlandia-release-publish.yml"
    }
  }
}
```

`workflow` must be a repository-relative YAML path below `.github/workflows/`.

Absence of `publication.github` is backward-compatible and means the generic GitHub-native release controller has no declared publication transport. It must stop with `RELEASE_PUBLICATION_BLOCKED`; it must not infer LOCAL fallback or perform ad-hoc tag/release mutation.

## Canonical workflow inputs

A generated workflow-dispatch publication surface requires exactly the release identity facts that must already be resolved before publication:

- `target_sha` — exact 40-character integrated commit SHA.
- `version` — explicit SemVer without repository tag prefix.
- `impact` — approved semantic impact: `patch`, `minor`, or `major`.
- `title` — explicit GitHub Release title.
- `notes` — final release notes.

These are transport values, not decisions delegated to GitHub Actions. The workflow MUST NOT infer a target, version, impact, title, notes, deployment, or environment promotion.

## Generated workflow invariants

The standard generated workflow must:

1. run only through `workflow_dispatch`;
2. request `contents: write` and no broader repository permission;
3. serialize publication attempts by version without cancelling an in-progress publication;
4. validate immutable dispatch inputs before checkout;
5. checkout exactly `target_sha` with full history/tags and push credentials available;
6. configure a non-interactive Git identity for annotated tag creation;
7. revalidate `HEAD == target_sha` before publisher invocation;
8. materialize notes without shell-evaluating their content;
9. build a deterministic publisher plan from exact inputs;
10. execute `coferlandia-release-publisher publish` from that plan;
11. never deploy or invoke repository deployment workflows.

The target repository supplies the repository-relative publisher entrypoint during adaptation. The adapter rejects absolute paths and parent traversal.

## Controller behavior

`chat-release` must re-read repository policy after integration. For `workflow-dispatch`, it verifies the workflow contract, revalidates the integrated SHA, dispatches with canonical inputs, binds to the new authoritative run, waits for a successful terminal conclusion, then independently verifies the resulting annotated tag and GitHub Release resolve to the exact integrated commit.

A missing workflow, unsupported mode, dispatch capability gap, ambiguous run binding, RED workflow, stale SHA, or release/tag mismatch is a publication blocker. None authorizes direct shell mutation or a LOCAL fallback.

## Adaptation review checklist

Before materializing publication support, verify:

- repository policy file and ownership are current;
- existing sibling `publication` fields will be preserved;
- the publisher skill is vendored/available at the proposed repository-relative path;
- the workflow path does not conflict with repository conventions;
- GitHub Actions is allowed to create tags/releases with `GITHUB_TOKEN` and `contents: write` under repository rules;
- no environment/deployment side effect is attached to the publication workflow;
- the publication workflow itself is covered by repository review/CI policy before use.

After materialization, validate both policy and generated workflow and confirm the CI profile fingerprint did not change unless Qualification facts also changed.
