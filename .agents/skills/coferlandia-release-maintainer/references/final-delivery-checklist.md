# Final Delivery Checklist

- [ ] Complete diff inspected against the intended integration base.
- [ ] Every affected public skill classified explicitly.
- [ ] Skill versions changed where shipped behavior changed.
- [ ] Every public skill has `CHANGELOG.md`; latest entry matches `metadata.version`.
- [ ] Latest `RELEASE-NOTES.md` section matches plugin version and contains affected skill rows.
- [ ] `Unreleased` is absent or empty in release-ready state.
- [ ] README generated latest-release block is current and human text outside markers is preserved.
- [ ] `skills/INDEX.md` changed only when inventory/discovery changed.
- [ ] Plugin/marketplace URLs and descriptions are current.
- [ ] `validate_skill.py --all skills` passes.
- [ ] `bump_version.py --check` and `--audit` pass.
- [ ] Release-maintainer `check --release-ready` passes.
- [ ] Full affected and repository-wide tests pass.
- [ ] Plugin archive rebuilt from the reviewed branch without pulling.
- [ ] Archive reopened; required entries present; local/private paths absent.
- [ ] Package SHA-256 recorded.
- [ ] Independent review findings resolved.
- [ ] Final commit/PR/integration authority receives exact evidence and suggested message.
