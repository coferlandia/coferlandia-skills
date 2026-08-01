# Change Classification

## Skill impact

Classify from semantics, not paths alone.

- **No version bump:** formatting, spelling, or wording with no changed instruction, trigger,
  authority, output, validation, CLI contract, or expected behavior.
- **Patch/minor-compatible skill increment:** behavior correction or compatible clarification that
  changes what an agent must do.
- **Larger compatible increment:** substantial new compatible capability.
- **Breaking increment:** activation, authority, contract, required output, or workflow change that
  invalidates existing consumers or requires migration.

Preserve the repository's existing per-skill version style. Do not mass-normalize historical
versions as part of an unrelated release.

## Repository/plugin impact

- **Patch:** compatible correction to a shipped skill, docs, manifest, packaging, or protocol.
- **Minor:** new skill or substantial compatible capability.
- **Major:** removal, incompatible contract, or migration requiring consumer adaptation.

## Evidence checklist

Before classifying, inspect:

- complete diff against integration base;
- changed activation/description/frontmatter;
- changed normative verbs and authority boundaries;
- references loaded conditionally by the skill;
- CLI commands, schemas, outputs, exit codes, package contents;
- installation/discovery surfaces;
- tests that encode new behavior;
- compatibility and migration consequences.
