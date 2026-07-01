# SKILL_LIFECYCLE.md

> A skill's states and how to transition between them.

---

## States

```
draft ──→ active ──→ deprecated
  ↑           │
  └───────────┘ (iteration)
```

| State | Description | When to use |
|--------|-------------|------------|
| `draft` | In development. May have incomplete instructions | When creating a new skill |
| `active` | Tested, complete, production-ready | After passing the QUALITY_STANDARDS.md checklist |
| `deprecated` | Replaced or outdated | When a skill is superseded by a better one |

The state goes in `SKILL.md`'s frontmatter:
```yaml
metadata:
  status: active
```

---

## Typical Lifecycle

### 1. Creation (`draft`)

- An agent or human identifies the need for a skill
- Follow the protocol in `HOW_TO_CREATE_SKILLS.md`
- The skill is created with `status: draft`
- Commit message: `skill(category/name): create skill as draft`

### 2. Activation (`active`)

- Test the skill with at least one real case
- Verify the full checklist in `QUALITY_STANDARDS.md`
- Update `status: active` in the frontmatter
- Update `skills/INDEX.md`
- Commit: `skill(category/name): activate skill after verification`

### 3. Iteration

- On finding an error → add a Gotcha and commit
- On improving instructions → bump `version` in metadata
- On adding scripts → document them in `SKILL.md`
- Commit: `skill(category/name): fix {what}`

### 4. Deprecation (`deprecated`)

- The skill is no longer relevant, or was superseded by another
- Update `status: deprecated`
- Add to the top of `SKILL.md`'s body:
  ```
  > ⚠️ **DEPRECATED** - Use `skills/{category}/{new-skill}/` instead.
  ```
- Commit: `skill(category/name): deprecate, replaced by {new-skill}`
- Keep the file (don't delete it) for historical reference

---

## Agent Responsibility During Iteration

When an agent uses a skill and finds an error or unexpected behavior:

1. **Fix** the problem on the spot
2. **Document** the error as a Gotcha in `SKILL.md`
3. **Bump** the minor version (e.g., `1.0` → `1.1`)
4. **Commit** with the format: `skill(category/name): add gotcha about {what}`

This is part of the "by agents" cycle — every agent that uses a skill helps improve it.
