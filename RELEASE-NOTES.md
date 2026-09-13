# Coferlandia Skills Release Notes

## Unreleased

## v2.10.3 (2026-09-12)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-ci-adapter | 1.2.1 | 1.2.2 | Separates the publication control-plane checkout from the immutable release target so current publisher fixes can recover an older partial release without changing release identity. |

### Plugin and packaging

- Bumps the repository/plugin from v2.10.2 to v2.10.3 for the compatible publication recovery transport fix.

### Migration or compatibility

- Compatible patch: existing release policy and publication request schema are unchanged.

## v2.10.2 (2026-09-12)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-release-publisher | 1.1.2 | 1.1.3 | Fixes draft release discovery so publication can safely resume from an existing annotated tag plus matching draft when GitHub omits drafts from the release-by-tag endpoint. |

### Plugin and packaging

- Bumps the repository/plugin from v2.10.1 to v2.10.2 for the compatible release-publisher recovery fix.
- Corrects the publisher compatibility contract to require GitHub token authorization rather than a preinstalled GitHub CLI.

### Migration or compatibility

- Compatible patch: existing release policies, tags and matching draft Releases remain valid; partial `TAG + DRAFT` state resumes without recreating or moving release identity.

## v2.10.1 (2026-09-12)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-ci-adapter | 1.2.0 | 1.2.1 | Removes the generated GitHub-native publication workflow dependency on a preinstalled GitHub CLI by using Python standard-library GitHub REST calls while preserving runner, authority and exact-SHA controls. |
| coferlandia-release-publisher | 1.1.1 | 1.1.2 | Replaces GitHub CLI subprocess calls with a Python standard-library GitHub REST transport using GITHUB_TOKEN or GH_TOKEN without changing fail-closed release semantics. |

### Plugin and packaging

- Publication no longer requires GitHub CLI on the selected runner; Python 3.11+ and GitHub token authorization are sufficient.

### Migration or compatibility

- Compatible patch: existing repository publication policies and runner declarations remain valid.

## v2.10.0 (2026-09-12)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-ci-adapter | 1.1.1 | 1.2.0 | Adds deterministic repository-owned remote Development validation adaptation while preserving separate Qualification and publication contracts. |

### Chat prompts

- `chat-coder` 1.3.0 -> 1.4.0 can complete required Development validation through a repository-owned remote execution surface when the active client cannot run the checks locally. It prefers direct execution, validates exact-candidate remote evidence, may delegate bounded bootstrap to `coferlandia-ci-adapter`, and still stops at `READY_FOR_CI`.

### Repository and protocol

- Adds `DEVELOPMENT_VALIDATION v1` and a JSON schema for a separate `.coferlandia/development/validation.json` contract that owns Development commands, working directory, required services/environment names, runner labels, shell, exact pull-request-head binding, and one success-only Development gate.
- Generated Development workflows run only for Draft pull requests, explicitly checkout and verify the exact PR head SHA, execute repository-declared commands with `contents: read`, record the Development contract fingerprint, and never emit Qualification or merge authority.
- Extends `READY_FOR_CI v1` so repository-owned remote Development evidence is valid only when candidate SHA, current Development fingerprint, declared gate, and allowed terminal conclusion all match.
- Keeps `.coferlandia/ci/profile.json` strictly scoped to Qualification; remote Development GREEN never satisfies `READY_FOR_MERGE` or an effective/synthetic merge candidate.

### Plugin and packaging

- Bumps the repository/plugin from v2.9.1 to v2.10.0 for the additive compatible remote Development execution and adapter-bootstrap capability.
- Ships `chat-coder` 1.4.0, `coferlandia-ci-adapter` 1.2.0, the shared Development validation protocol/schema, and regression coverage.

### Migration or compatibility

- Existing repositories remain compatible and may continue using direct/local Development validation. Remote Development adaptation is additive and repository-owned.
- Repositories adopting the remote surface must explicitly declare their own safe GitHub Actions runner labels, shell and Development commands; no SecretarIA-specific stack, branch, runner or command is embedded in Coferlandia Skills.
- Self-hosted runner isolation, installed tooling and ambient environment remain repository/operator responsibilities; the generated workflow does not inject secret values.

## v2.9.1 (2026-09-12)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-ci-adapter | 1.1.0 | 1.1.1 | Makes the GitHub-native publication runner repository-configurable while preserving ubuntu-latest as the compatible default and keeping publication separate from Qualification. |
| coferlandia-release-publisher | 1.1 | 1.1.1 | Accepts and validates repository publication runner metadata without changing exact Commit-to-Release semantics. |

### Repository and protocol

- Adds optional publication.github.runs_on so repositories can explicitly select GitHub-hosted or self-hosted publication runners without coupling runner choice to .coferlandia/ci/profile.json.
- Adds deterministic self-hosted multi-label runner rendering and regression coverage after the SecretarIA publication transport exposed the hardcoded ubuntu-latest assumption.

### Plugin and packaging

- Bumps the plugin from v2.9.0 to v2.9.1 for the compatible publication-runner hotfix.

### Migration or compatibility

- Existing publication policies without runs_on remain compatible and continue to default to ubuntu-latest; repositories requiring self-hosted publication must declare their exact runner labels during adaptation.

## v2.9.0 (2026-09-12)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-ci-adapter | 1.0.0 | 1.1.0 | Adds opt-in adaptation of repository-declared GitHub-native release publication policy/workflows while keeping `.coferlandia/ci/profile.json` scoped strictly to Qualification. |
| coferlandia-release-publisher | 1.0 | 1.1 | Adds validation and explicit non-interactive support for policy-declared GitHub publication transports without changing exact annotated-tag/GitHub-Release publication semantics. |

### Chat prompts

- `chat-release` 1.0.0 -> 1.1.0 completes the GITHUB_NATIVE publication path after release integration. It resolves `publication.github` independently from the CI profile, transports only explicit release identity, observes one authoritative publication run, and independently verifies the resulting annotated tag and GitHub Release against the exact integrated commit.
- Adds the standard Chat-compatible `issue-comment` transport: a versioned control comment on the merged release PR carries `schema`, `target_sha`, `version`, `impact`, `title`, and `notes`; a repository workflow validates authority and invokes `coferlandia-release-publisher`.
- Keeps `workflow-dispatch` as an optional publication transport only for GitHub-native clients that actually expose an Actions dispatch primitive. Missing/unsupported publication surfaces fail closed as `RELEASE_PUBLICATION_BLOCKED`; no LOCAL fallback or direct tag/Release mutation is introduced.

### Repository and protocol

- Defines `publication.github` as a release-policy transport contract separate from `.coferlandia/ci/profile.json`, preserving the boundary between Qualification, Integration, and Publication authority.
- Standardizes the Chat publication request marker `<!-- coferlandia-release-publication-request:v1 -->` and exact JSON identity envelope.
- Generated issue-comment publication workflows require repository `admin` or `maintain` authority, require the release PR to already be merged, parse the comment payload as data, checkout the exact target SHA, grant minimal read permissions plus `contents: write`, and never deploy.
- `coferlandia-ci-adapter` can now validate and materialize the optional release publication policy/workflow while preserving existing repository-owned publication fields and CI-only behavior.

### Plugin and packaging

- Bumps the repository/plugin from v2.8.0 to v2.9.0 for the substantial compatible GitHub-native release-publication capability.
- Ships updated `chat-release`, `coferlandia-ci-adapter`, `coferlandia-release-publisher`, their tests, and publication-contract documentation.

### Migration or compatibility

- Existing repositories using only the CI profile contract remain compatible; publication adaptation is explicit and opt-in.
- Existing release policies remain compatible when `publication.github` is absent; GITHUB_NATIVE publication simply remains blocked until the repository explicitly declares a supported transport.
- Repositories adopting the standard Chat-compatible path need a durable release PR/work surface, a vendored/available `coferlandia-release-publisher`, and GitHub Actions permission to create tags/releases with `contents: write`.
- Publication remains separate from deployment, and neither `chat-release` nor the generated workflow may infer a version, target SHA, deployment target, or other unresolved semantic decision.

## v2.8.0 (2026-09-11)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| local-release | new | 1.0.0 | Adds the LOCAL aggregate release surface: candidate/work-surface initialization, manifest currentization, aggregate review, exact-candidate qualification, `READY_FOR_RELEASE`, repository-approved integration, publisher composition, explicit repair/requalification states, and no GitHub-native Qualification fallback or deployment ownership. |

### Chat prompts

- `chat-coder` 1.2.1 -> 1.3.0 adds explicit delegated delivery context without changing the ordinary default: exceptional contexts must come from an explicitly invoked controlling surface plus durable repository policy/evidence, may select a different approved base/target, never weaken Development/TDD/review/`READY_FOR_CI`, and fail closed instead of silently falling back to ordinary development.
- Adds `chat-release` 1.0.0 as the explicit GITHUB_NATIVE aggregate release controller. It initializes/reuses the repository-approved release work surface, builds/currentizes the release manifest, performs aggregate release review, qualifies one exact release candidate, emits `READY_FOR_RELEASE`, integrates through repository policy, and delegates Commit-to-Release publication to `coferlandia-release-publisher`.
- Adds `hotfix` 1.0.0 as an explicitly invoked emergency-remediation controller supporting either an existing Issue (`hotfix #123`) or a free-form bug report. It creates/reuses the primary Issue, uses `UNRESOLVED` while diagnosis is incomplete, classifies an executable strategy as `PERMANENT` or `TEMPORARY_MITIGATION`, fails closed with `HOTFIX_BLOCKED` when no bounded remedy is safe, and delegates Development/Qualification/Integration/publication to repository-approved owners.
- For `TEMPORARY_MITIGATION`, `hotfix` requires a distinct permanent-fix Issue before the candidate can become `HOTFIX_READY`, preserving known/probable root cause, temporary mitigation, deferral rationale, final behavior, temporary surfaces to remove, removal criteria, and regression/prevention expectations. Production may be stabilized while permanent resolution intentionally remains open.
- `merge` 1.0.0 -> 1.1.0 resolves and verifies the pull request's authoritative target ref instead of generically assuming the repository default branch, enabling consumers with an intermediate integration branch without hardcoding that topology in Coferlandia.

### Repository and protocol

- Adds `READY_FOR_RELEASE v1`, binding release qualification to exact source/target/base/profile/effective-candidate/manifest/review identity for both LOCAL and GITHUB_NATIVE strategies.
- Adds `HOTFIX v1`, a durable exact-candidate emergency record with `UNRESOLVED | PERMANENT | TEMPORARY_MITIGATION`, mandatory follow-up debt for temporary mitigations, exact `READY_FOR_CI` binding before `HOTFIX_READY`, and fail-closed `HOTFIX_BLOCKED` semantics.
- Extends the prompt registry, validator, bootstrap, shared delivery protocol, agent guidance, and requalification rules with first-class Release and Hotfix lifecycles while preserving ordinary left-to-right development composition and no cross-strategy fallback.
- Keeps repository-specific branch topology, CI workflows, tests, runners, version policy, deployment and reconciliation outside generic controllers.

### Plugin and packaging

- Adds the public `local-release` Agent Skill and ships the expanded public Chat prompt/protocol catalog.
- Bumps the repository/plugin from v2.7.3 to v2.8.0 for additive compatible release and emergency-remediation capabilities.

### Migration or compatibility

- Existing standard repositories remain compatible: `chat-coder -> ci/local-ci -> merge` still works when the pull request targets the default branch, with ordinary Development remaining the default delivery context.
- Consumer repositories may define non-default ordinary integration targets and explicit exceptional delivery contexts through their own policy; generic controllers resolve those targets/contexts instead of assuming branch names.
- Release and hotfix topology, workflows, tests, runners, deployment and reconciliation remain repository-owned; no consumer repository is migrated automatically.
- LOCAL and GITHUB_NATIVE remain explicit alternatives. `local-release` never falls back to `chat-release`, and GitHub-native release qualification never falls back to LOCAL. Both surfaces own equivalent candidate initialization, aggregate review, exact-candidate release authority, integration and publisher composition; only Qualification evidence differs.
- A temporary hotfix mitigation is not equivalent to permanent resolution: the permanent-fix Issue remains open after production stabilization until the structural correction is completed through normal work.

## v2.7.3 (2026-09-11)

### Chat prompts

- `chat-coder` 1.2.0 -> 1.2.1 makes affected pre-existing tests part of every behavior/contract change: Development must review them before adding coverage, preserve still-valid behavior, update intentionally changed expectations, and remove tests only when their behavior was intentionally removed or superseded.
- Requires consolidation/removal of materially duplicate or overlapping tests that add no independent coverage or diagnostic value, prefers updating/extending/parameterizing existing coverage when appropriate, and cleans test-only fixtures/helpers/mocks/snapshots/data made obsolete by the change.
- Explicitly states that test-count growth is not a goal: the final suite should be the smallest clear set that adequately protects current intended behavior, while tests/assertions may never be weakened or removed merely to make validation pass.
- Adds regression coverage protecting the test-suite reconciliation and hygiene contract.

### Plugin and packaging

- Bumps the shipped repository/plugin from v2.7.2 to v2.7.3 as a compatible Chat Coder correction.
- No public Agent Skill versions change in this release.

### Migration or compatibility

- Existing consumers remain compatible. Repositories vendoring the public prompt family should update `chat-coder.md` so behavior changes reconcile existing coverage instead of only accumulating new tests.
- Qualification strategy, `READY_FOR_CI`, `READY_FOR_MERGE`, and merge semantics are unchanged.

## v2.7.2 (2026-09-10)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| local-ci | 1.0.0 | 1.1.0 | Makes the Agent Skill invocation surface itself select LOCAL Qualification, keeps `READY_FOR_CI` from implicitly starting Qualification, and preserves fail-closed local blocking with no GitHub-native fallback. |

### Chat prompts

- `ci` 1.1.0 -> 1.2.0 explicitly binds the controller to `ci` / `gh ci` / `github ci` Chat invocation and makes `GITHUB_NATIVE` a property of that surface rather than a strategy inferred by another router.
- Reaching `READY_FOR_CI` or discovering Agent Skills does not load the Chat `ci` controller; standalone `chat-coder` still terminates at `READY_FOR_CI`.
- GitHub-native Qualification now explicitly forbids inventing `workflow_dispatch` when the repository profile declares existing PR-event submission.

### Repository and protocol

- Clarifies that Qualification strategy is selected by the invoked controller surface: `local-ci` means `LOCAL`, explicit Chat `ci` means `GITHUB_NATIVE`; a separate strategy router is unnecessary.
- Extends contract tests and activation pressure cases to protect surface separation, no implicit stage insertion, and no cross-strategy fallback.

### Plugin and packaging

- Bumps the shipped repository/plugin from v2.7.1 to v2.7.2 as a compatible correction to the v2.6/v2.7 delivery-controller model.

### Migration or compatibility

- Existing consumers remain compatible. Consumers with repository-local strategy routers may simplify them and route Agent Skill Qualification directly to `local-ci` while keeping explicit Chat `ci` as the GitHub-native surface.
- Repository CI profiles continue to own local commands/services and GitHub submission/gate facts; they do not select the Qualification strategy.
- LOCAL failures remain local and GITHUB_NATIVE failures remain remote; neither strategy becomes a fallback for the other.

## v2.7.1 (2026-09-10)

### Chat prompts

- `ci` 1.0.0 -> 1.1.0 completes the environment/configuration contract introduced across Development and `READY_FOR_CI` in v2.7.0 by re-evaluating the exact candidate against the authoritative base before GitHub-native Qualification.
- Qualification now fails closed when `Environment change: YES | NO` is missing, ambiguous, or contradicted by the candidate, and requires candidate-bound non-secret operational evidence when environment/configuration impact is declared.
- Adds regression coverage for the CI environment/configuration qualification barrier.

### Plugin and packaging

- Bumps the shipped repository/plugin from v2.7.0 to v2.7.1 as a compatible correction completing the v2.7.0 public delivery-controller contract.
- No public Agent Skill versions change in this release.

### Migration or compatibility

- Consumers that vendor the public prompt family should update `ci.md` together with the v2.7.x `chat-coder` and `READY_FOR_CI` contract.
- Qualification strategy, required GitHub gates, and `READY_FOR_MERGE` semantics are unchanged.

## v2.7.0 (2026-09-10)

### Chat prompts

- `chat-coder` 1.0.3 -> 1.2.0 incorporates the generic environment/configuration impact contract already proven in a consumer: Development must explicitly classify `Environment change: YES | NO`, record non-secret evidence and deployment actions when the runtime/configuration contract changes, synchronize repository-owned environment examples/runbooks when applicable, and execute deterministic configuration checks before `READY_FOR_CI`.
- Clarifies derived-artifact readiness so synchronization applies only to outputs that repository-owned policy, instructions, or tooling explicitly declare to be versioned contracts.
- Explicitly excludes reproducible diagnostic/report outputs from Git synchronization and snapshot-freshness requirements unless the repository itself declares those outputs to be versioned contracts; test inventories and generated test manifests are therefore not special-cased by the generic controller.

### Repository and protocol

- Extends `READY_FOR_CI v1` with candidate-bound environment classification/evidence and the same fail-closed rules for stale or contradictory operational configuration documentation.
- Distinguishes authoritative versioned derived contracts from reproducible reports, preserving deterministic freshness requirements for the former while preventing the latter from becoming artificial merge hotspots.
- Adds regression coverage for both sides of the derived-artifact distinction and for the environment/configuration handoff contract.

### Plugin and packaging

- Bumps the shipped repository/plugin from v2.6.4 to v2.7.0 for the substantial compatible Chat Coder and shared delivery-protocol capability.
- No public Agent Skill versions change in this release.

### Migration or compatibility

- Consumers should update vendored/installed `chat-coder` and `_protocol/delivery/READY_FOR_CI.md` together.
- Repository-declared versioned contracts such as generated OpenAPI/schema clients, schemas, code-generation outputs, or intentionally versioned snapshots remain mandatory synchronization targets when their authoritative inputs change.
- Fully reproducible diagnostics/reports do not need to be committed merely to satisfy Chat Coder; repositories that intentionally want one versioned must declare that contract through repository-owned policy/tooling.
- Qualification strategy and `READY_FOR_MERGE` semantics are unchanged.

## v2.6.4 (2026-09-09)

### Chat prompts

- `chat-coder` 1.0.2 -> 1.0.3 requires Development to identify and synchronize repository-owned versioned derived artifacts whenever their authoritative inputs change, using the repository's own generation or synchronization mechanism rather than hand-editing generated output.
- The generic rule covers generated API/schema clients, schemas, snapshots, inventories/manifests, and equivalent code-generation outputs without hardcoding any consumer repository or technology.
- When a repository defines a deterministic freshness, idempotence, or diff check for generated artifacts, that check must pass without unexpected diff before `READY_FOR_CI`; missing, stale, or manually approximated required artifacts block the handoff.

### Repository and protocol

- Tightens `READY_FOR_CI v1` so affected versioned derived artifacts must be synchronized on the exact source candidate through repository-owned tooling, alongside the existing complete cheap-development validation contract.
- Adds regression coverage that preserves this requirement while keeping Qualification of the effective/synthetic merge candidate separate.

### Plugin and packaging

- Bumps the installable plugin from v2.6.3 to v2.6.4 because the shipped Chat Coder and shared delivery protocol changed.

### Migration or compatibility

- Existing consumers remain compatible but should update vendored/installed Chat Coder and `READY_FOR_CI` copies together. Repository-specific generators and artifact paths remain repository-owned configuration, not generic prompt policy.
- Qualification strategy and `READY_FOR_MERGE` semantics are unchanged.

## v2.6.3 (2026-09-09)

### Chat prompts

- `chat-coder` 1.0.1 -> 1.0.2 makes `READY_FOR_CI` contingent on fresh evidence from every applicable cheap deterministic development check for the exact source candidate, instead of allowing focused iteration tests and a clean review to stand in for the repository's broader development contract.
- Frontend changes must run the repository's canonical complete frontend unit-test suite plus repository-defined lint/typecheck checks when applicable; backend and other changed surfaces follow the equivalent repository-owned development validation.
- When Development resumes after Qualification fails, Chat Coder must identify the exact failing command/assertion and validation candidate before correcting code or a demonstrably stale contract, and must never weaken an assertion merely to obtain green CI.

### Repository and protocol

- Tightens `READY_FOR_CI v1` validity so required checks cannot be failing, skipped, unknown, stale, or bound to an older candidate SHA.
- Keeps Development readiness explicitly separate from Qualification of the effective or synthetic merge candidate.
- Adds regression coverage for the strengthened Chat Coder and READY_FOR_CI contracts.

### Plugin and packaging

- Bumps the installable plugin from v2.6.2 to v2.6.3 because `prompts/**` and the shared delivery protocol are shipped public artifacts.

### Migration or compatibility

- Existing prompt consumers remain compatible but should update vendored/installed Chat Coder and delivery protocol copies together. Candidates previously declared `READY_FOR_CI` from only focused checks may now correctly remain blocked until the repository's cheap development validation is complete.
- Qualification strategy and `READY_FOR_MERGE` semantics are unchanged.

## v2.6.2 (2026-09-09)

### Chat prompts

- `chat-coder` 1.0.0 -> 1.0.1 restores explicit issue ownership at Development entry: an unassigned Issue must be assigned to the authenticated GitHub user as the first state-changing action, the assignment must be re-read and verified, and work stops rather than taking over an Issue owned by somebody else.
- Restores `Assignee = <authenticated GitHub user>` in the terminal development report and adds regression coverage for the ownership contract.

### Plugin and packaging

- Bumps the installable plugin from v2.6.1 to v2.6.2 because `prompts/**` is a shipped public artifact family.
- Keeps the prompt registry and composition semantics unchanged; this patch only corrects Chat Coder Development ownership behavior.

### Migration or compatibility

- Existing consumers remain compatible. Vendored or installed prompt catalogs should update to receive the corrected Chat Coder ownership semantics.
- No Agent Skill behavior changes in this release.

## v2.6.1 (2026-09-07)

### Repository and protocol

- Promotes `prompts/**` from repository-only discovery material to a shipped public artifact family alongside `skills/**`.
- Defines full Coferlandia vendoring as preserving both public families: Agent Skills and Chat delivery prompts remain distinct execution surfaces but are distributed together.

### Plugin and packaging

- Fixes the installable plugin package so it includes `prompts/INDEX.md`, `prompts/registry.json`, `prompts/BOOTSTRAP.md`, `prompts/chat-coder.md`, `prompts/ci.md`, and `prompts/merge.md`.
- Classifies changes under `prompts/**` as shipped plugin changes so future prompt changes participate in repository release/version checks.
- Adds regression coverage that fails if the public prompt catalog is omitted from the generated package.

### Migration or compatibility

- Consumers that vendor the complete Coferlandia runtime should install/update both the public skills catalog and the public prompt catalog. Existing Agent Skill behavior is unchanged.
- This patch corrects the packaging/distribution decision recorded in v2.6.0; the prompt and skill execution surfaces remain intentionally separate.

## v2.6.0 (2026-09-07)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| local-ci | new | 1.0.0 | Adds generic LOCAL Qualification from durable READY_FOR_CI to candidate/profile-bound READY_FOR_MERGE without GitHub-native fallback or merge coupling. |
| coferlandia-ci-adapter | new | 1.0.0 | Adds repository CI discovery plus deterministic validation, fingerprinting, drift checking, and rendering of one `.coferlandia/ci/profile.json` shared by Chat and local Qualification. |

### Repository and protocol

- Adds `prompts/` as a first-class repository-addressable Chat controller family with generic `chat-coder`, `ci`, and `merge` prompts, a small bootstrap/registry, deterministic alias resolution, and exact left-to-right composition.
- Separates Development, Qualification, and Integration through versioned `READY_FOR_CI`, `READY_FOR_MERGE`, and requalification contracts bound to exact candidate/base/profile identity.
- Defines `LOCAL` and `GITHUB_NATIVE` as equal Qualification strategies: neither is a fallback for the other, both emit the same READY_FOR_MERGE identity envelope, and `merge` never executes CI implicitly.
- Adds a shared repository CI profile schema so repo-specific commands, workflows, services, gates, Merge Queue semantics, and exceptional-lane references remain outside generic controllers.
- Adds pressure coverage proving SecretarIA's existing CI facts are representable in a repository profile without hardcoding them in the generic prompts or Local CI skill.
- Extends Linux/Windows CI to validate prompt registry/contracts, delivery identity/requalification, Local CI, and CI Adapter behavior on Python 3.11 and 3.13.

### Plugin and packaging

- Bumps the installable Agent Skills plugin from v2.5.0 to v2.6.0 for the additive `local-ci` and `coferlandia-ci-adapter` public skills plus shared delivery protocol.
- Refreshes plugin discovery metadata and the human guide for local qualification and repository CI adaptation.
- Keeps the Chat `prompts/` family repository-addressable and intentionally outside the Agent Skills `.plugin` payload in V1; the package continues to ship public Agent Skills and `_protocol/` only.

### Migration or compatibility

- Existing Agent Skills consumers may update normally; this is an additive compatible release.
- A consumer repository must be studied/adapted to produce `.coferlandia/ci/profile.json` before generic Chat CI or Local CI can qualify it; the adapter does not invent missing commands or workflows.
- No consumer repository is migrated automatically by this release. SecretarIA is a conformance fixture and remains a separate repository-local migration step after generic parity is accepted.
- Qualification strategy stays explicit: a failed/unavailable local run does not switch to GitHub-native CI, and a failed/unavailable GitHub-native run does not switch to Local CI.

## v2.5.0 (2026-09-05)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-release-publisher | new | 1.0 | Adds a generic Commit-to-Release standard with SemVer planning, exact annotated-tag identity, GitHub Release publication, idempotent recovery, and machine-readable verification/resolution independent of deployment. |

### Repository and protocol

- Adds a reusable product-release boundary after development/integration: an exact existing commit becomes a formal release without requiring a synthetic declaration commit.
- Separates semantic release decisions from deterministic Git/GitHub mechanics, including historical targets, release-line ancestry, prereleases, explicit policy checks, and fail-closed inconsistency handling.
- Preserves repository-local precedence only when a stronger local contract explicitly owns final Commit-to-published-Release; preparation-only release/versioning gates may compose before the generic publisher.
- Adds Linux/Windows CI coverage for activation, SemVer/policy contracts, real temporary Git histories, GitHub adapter behavior, release planning, and consistency states.

### Plugin and packaging

- Bumps the installable plugin from v2.4.0 to v2.5.0 for the additive `coferlandia-release-publisher` public skill.
- Refreshes plugin discovery metadata and the human skill guide to include deterministic release publication and machine-readable release resolution.
- Keeps transient release plans/provenance under `.agent/` and therefore excluded from plugin packaging; optional provenance becomes a GitHub Release asset rather than a required file in the target commit.

### Migration or compatibility

- Existing consumers may update normally; this is an additive compatible release.
- The generic publisher does not auto-migrate repositories whose published GitHub Release history uses another version scheme; those repositories require an explicit stronger local publication contract or policy decision.
- Deployment, production rollback, host selection, Docker/service operations, and deployed-version state remain outside the release publisher contract.

## v2.4.0 (2026-09-03)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| project-orchestrator | 2.3 | 2.4 | Adds fail-closed exact-candidate GitHub CI gates, durable integration-check states, remote base validation, merge-group awareness, double revalidation, and head-conditional squash merge protection. |

### Repository and protocol

- Adds deterministic exact-candidate integration-gate policy and regression coverage for project-orchestrator.

### Plugin and packaging

- Bumps the installable plugin for the additive project-orchestrator integration-safety behavior.

### Migration or compatibility

- Existing repositories remain compatible when integration.github is absent or required_gates is empty. Repositories that need controller-enforced CI may configure workflow or check-run gates explicitly.

## v2.3.0 (2026-08-03)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-config-toolsmith | new | 1.0.0 | Adds an explicit agentic-plus-deterministic process that discovers a project's existing configuration, builds a static contract and standardized native-or-fallback CLI, records ambiguous candidates, generates agent documentation, and preserves the project's native stores as the only runtime source of truth. |
| coferlandia-config-devops | new | 1.0.0 | Adds Config Operator Execute Mode and control-tower Guide Mode for converting natural-language configuration intent into exact prepare/apply/activate/rollback operations through the Toolsmith-generated interface. |

### Repository and protocol

- Added configuration operations as a first-class skill family while preserving the boundary between repository preparation and day-to-day operation.
- Added permanent Linux/Windows CI coverage for both new skill suites, contract validation, candidate lifecycle behavior, generated Python facades, Guide Mode, and activation boundaries.
- Updated the canonical skill index and human guide with the ownership, composition, and explicit-invocation rules for the new skills.
- Kept deterministic retrieval non-authoritative: agents must consult the complete generated handbook before concluding that a requested configuration outcome is unsupported.

### Plugin and packaging

- Bumped the installable plugin from v2.2.0 to v2.3.0 for the two additive public skills.
- Refreshed plugin and marketplace descriptions and keywords to include agent-operable configuration and DevOps workflows.
- Updated the README managed release block and verified that packaging excludes repository-local and transient artifacts.

### Migration or compatibility

- Existing consumers may update normally; this is an additive compatible release.
- `coferlandia-config-toolsmith` never migrates or replaces a project's configuration architecture implicitly. Generated contracts contain capabilities and bindings, not current or effective values.
- Projects must run Config Toolsmith explicitly before Config DevOps can operate them; Config DevOps consumes the generated contract and CLI and does not invent missing adapters or fields.

## v2.2.0 (2026-08-01)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| project-evangelist | new | 1.0 | Adds progressive, evidence-based developer documentation with verified technology and architecture summaries, reading paths, repository maps, and contributor guidance. |
| the-architect | new | 1.0.0 | Adds cross-project architecture memory, Architecture Gates, evidence-based assessments, reusable-component governance, and a deterministic Markdown/Obsidian CLI. |
| coferlandia-project-manager | 0.6.0 | 0.8.0 | Adds Epic Planner execution strategies and Architecture Gate selection before material development work. |
| software-development | 4.4 | 4.6 | Adds the broad-context Analyst role, executable low-context task contracts, and Architecture Gate enforcement before decomposition or implementation. |
| project-orchestrator | 1.1 | 2.3 | Adds Epic/task execution, one-time contract materialization, immutable review lifecycles, final integration traceability, and durable concurrent work-item claims. |
| project-documentation-archivist | 3.0.0 | 3.1.0 | Clarifies in-project durable-knowledge ownership while the Architect owns cross-project architecture and component evidence. |
| skill-repository-versioning | 1.1.0 | 1.2.0 | Defers to stronger repository-local release-maintenance workflows instead of running a competing generic protocol. |

### Repository and protocol

- Added the repository-local `coferlandia-release-maintainer` final-delivery gate under `.agents/skills/` without shipping it as a public plugin skill.
- Added one canonical release-maintenance policy and per-skill `CHANGELOG.md` ownership for every public skill.
- Updated skill authoring templates, quality standards, and validation so new and modified public skills keep `metadata.version`, changelog history, release notes, and repository release metadata coherent.
- Added deterministic release inspection, preparation, validation, README rendering, and package verification through one Python CLI.
- Preserved `skills/INDEX.md` as the inventory source of truth rather than duplicating release history there.

### Plugin and packaging

- Bumped the installable plugin from v2.1.0 to v2.2.0 for the accumulated shipped skill and protocol changes.
- Corrected plugin repository/homepage metadata to `coferlandia/coferlandia-skills` and refreshed marketplace descriptions.
- Replaced pull-before-package behavior with deterministic packaging of the already-reviewed branch state.
- The package now includes `RELEASE-NOTES.md` and `SKILLS-GUIDE.md`, excludes repository-local `.agents/**` and `.agent/**`, reopens the archive for verification, and reports a SHA-256 digest.
- CI now enforces changelog/version consistency, the release-ready gate, README projection freshness, and verified plugin packaging on Linux and Windows.

### Migration or compatibility

- Existing consumers should reinstall or update the plugin to receive the accumulated v2.2.0 skill set.
- Repository contributors must run the local release-maintenance gate before final commit, pull-request readiness, or integration when a shipped surface changed; intermediate implementation commits remain allowed under the defined boundary.
- The public `skill-repository-versioning` skill remains reusable in other repositories and delegates when a repository provides a stronger local release workflow.

## v2.0.0 (2026-07-27)

### Breaking project protocol change

- **project-documentation-archivist** — v3.0.0. GitHub Issues and GitHub Projects become the operational source of truth. `TODO.md`, `HISTORY.md`, and legacy `OPEN_QUESTIONS.md` are migration inputs only; Archivist now owns durable knowledge (`README.md`, `AGENTS.md`, `DECISIONS.md`, `RUNBOOK.md`) plus traceability metadata and ships a guarded, idempotent per-project migration workflow.
- **coferlandia-project-manager** — v0.6.0. PM becomes a GitHub-backed architecture and portfolio manager. It keeps design-oriented Superpowers, reads operational state from GitHub, and treats Obsidian as a generated projection rather than a task database.
- **software-development** — v4.4. Debugging and implementation traceability use GitHub Issues/PRs/commits in GitHub-native Coferlandia repositories instead of depending on local TODO/HISTORY files.
- **project-skill-miner** — v1.1.0. Current GitHub development evidence joins durable documentation as an authoritative mining source; legacy TODO/HISTORY files are migration evidence only.

### Migration

- Existing projects migrate repository-by-repository with Archivist preflight, inventory, reviewed decisions, idempotent GitHub Issue creation/mapping, knowledge distillation, cutover validation, and only then removal of legacy tracking files.
- This is a breaking protocol migration; mixed portfolios remain observable through an explicit legacy-migration compatibility mode until each project cuts over.

### Repository

- Bumped the repo-wide plugin version to 2.0.0 because the shared project-management/documentation protocol changes incompatibly.
- Updated `skills/INDEX.md` descriptions for the GitHub-native ownership model.

## v1.9.0 (2026-07-15)

### Skills

- **project-orchestrator** (`ops`) — v1.1. Adds real Codex/OpenCode execution,
  JSONL/session handling, provider fallbacks, schema-complete result validation,
  persisted recovery, candidate/review/fix/merge lifecycle controls, reports,
  doctor diagnostics, and fake-provider integration coverage.

### Repository

- `coferlandia-skills` — bumped the repo-wide release version for the new
  orchestration skill and its onboarding/configuration surface.

## v1.8.0 (2026-07-14)

### Skills

- **coferlandia-project-manager** (`ops`) — v0.5.1. Preserves explicit
  `projects.json` slugs across portfolio, health, archivist, and board outputs;
  reports `projects_count`; and rejects runtime commands when the managed-project
  manifest is absent instead of treating it as an empty portfolio.

### Repository

- `coferlandia-skills` — ships the `skills/ops` category in the plugin manifest,
  including `coferlandia-project-manager` at its canonical location.

## v1.7.0 (2026-07-13)

### Skills

- **coferlandia-skill-toolsmith** (`meta`) — v1.0.0. Explicit-invocation-only
  meta skill that analyzes a target skill, classifies its deterministic
  vs. semantic behavior, and consolidates the deterministic parts behind one
  unified Python CLI (`scripts/<skill-name>-cli.py`) following a stable output
  envelope, documented exit codes, and mandatory `--help` / `version` /
  `self-check` / `capabilities` commands. It then rewires the target `SKILL.md`
  to call that single public interface, preserving all semantic rules and
  decision criteria. Activation is gated to explicit requests only and enforced
  with an anti-rationalization table and red-flags list; it never self-activates
  on similarity, token inefficiency, or refactor opportunities. Ships with
  fixture-backed activation tests (`tests/test_activation.py`) and a walk-through
  target (`tests/fixtures/sample-target-skill/`).

### Repository

- `coferlandia-skills` — bumped the repo-wide release version to include the new
  meta skill and its test/fixture surface.

## v1.6.0 (2026-07-12)

### Skills

- **coferlandia-software-dev** (`engineering`) — v3.3.0. Adds distinct
  `coding-agent` and `code-reviewer` roles, repository-local isolated-worktree
  controls, reviewer reconciliation and local-integration gates, traceability
  handoffs, and fixture-backed REQUIRED TDD/systematic-debugging disciplines with
  explicit fallbacks.

### Repository

- `coferlandia-skills` — bumped the repo-wide release version for the updated
  development-control surface.

## v1.5.0 (2026-07-08)

### Skills

- **coferlandia-project-manager** (`meta`) - v1.0.0. Added a new project-local
  skill for operating a repo-scoped project manager home, with repo-local
  defaults for runtime artifacts, Obsidian vault output, onboarding, and
  readiness checks.

### Repository

- `coferlandia-skills` - bumped the repo-wide release version to include the new
  skill and its packaging surface.

## v1.4.0 (2026-07-07)

### Protocol

- `HOW_TO_CREATE_SKILLS.md` — added an explicit reference to
  `superpowers:writing-skills` in the prerequisites for skill authoring, so
  approved skill drafts follow the dedicated writing workflow when that skill is
  available.

## v1.3.0 (2026-07-07)

### Skills

- **coferlandia-project-skill-miner** (`meta`) — v1.0.0. Mines a project's
  documentation for current operational recipes, classifies candidate project-local
  skills by confidence and staleness, requires explicit approval before generation,
  and writes approved downstream skills only under the target repository's
  `.agents/skills/<skill-name>/` path. Integrates with
  `superpowers:writing-skills` when available before authoring each approved
  generated skill.

### Repository

- `skills/INDEX.md` — added the new `coferlandia-project-skill-miner` entry and
  updated the inventory date.
- Added a fixture-backed activation test set for the new skill, including current,
  dangerous, ambiguous, and stale documented procedures to verify proposal-vs-approval
  behavior.

## v1.2.0 (2026-07-06)

### Convention

- **Artifact output convention** — all skills now declare an `## Output Location`
  section. Generated artifacts default to `.coferlandia/` at the target project's
  root; standard repo artifacts (README.md, AGENTS.md, LICENSE, RUNBOOK.md) stay at
  the project root unless the skill explicitly overrides them. The single source of
  truth lives in `_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md`.

### Skills

- **project-documentation-archivist** (`content`) — v2.1.0. Catalog files now go to
  `.coferlandia/catalog/` and archived sources to `.coferlandia/archive/YYYY/` instead
  of `docs/catalog/` and `docs/archive/`. Standard repo artifacts (README.md, AGENTS.md,
  RUNBOOK.md) remain at the project root. HISTORY.md, TODO.md, and DECISIONS.md go to
  `.coferlandia/`.
- **coferlandia-software-dev** (`engineering`) — v2.3.0. Documentation artifacts default
  to `.coferlandia/` when no archivist structure exists in the target repo.
- **skill-repository-versioning** (`meta`) — v1.1.0. Explicit output location added
  (in-place repo management, no `.coferlandia/` needed).
- **using-coferlandia-skills** (`meta`) — v1.1.0. Explicit output location added (no
  file artifacts generated).
- **sagan-scientific-debunker** (`content`) — v1.2.0. Explicit output location added
  (conversation-only, no files).

### Protocol

- `ARTIFACT_OUTPUT_CONVENTIONS.md` — new single source of truth for output paths.
- `HOW_TO_CREATE_SKILLS.md` — references the new convention in prerequisites and Step 4.
- `SKILL_TEMPLATE.md` — includes `## Output Location` / `### Output Exceptions` sections.

## v1.1.0 (2026-07-05)

### Skills

- **coferlandia-software-dev** (`engineering`) — v2.2.0. Adds optional supervisory-agent role to Step 2, with explicit mode selection at task start, mandatory execution context package, structured checkpoint contract, role & authority boundary, and audit trail. No changes to Steps 1, 3, 4, or 5.
- **coferlandia-software-dev** (`engineering`) — v2.1.0. Adds commit proposal + explicit approval as Step 5.5, test-results-report requirement before proposing a commit, push never automatic, and optional integration with `project-documentation-archivist` for documentation updates (HISTORY.md, TODO.md, DECISIONS.md, RUNBOOK.md, AGENTS.md).
- **coferlandia-software-dev** (`engineering`) — v2.0.0. Complete redesign into a multi-role engineering workflow with Developer, Debugger, Code Reviewer, and Commit Prep modes. Adds strict mode detection, control-authority abstraction, code review protocol, and commit preparation gates. Replaces v1.x workflow entirely.
- **coferlandia-software-dev** (`engineering`) — v1.0.0. Initial development process skill: mandatory study → plan → implement → review → test/docs/commit workflow.
- **using-coferlandia-skills** (`meta`) — v1.0.0. First meta-skill: checks `skills/INDEX.md` and invokes matching skills before responding to any task.
- **skill-repository-versioning** (`meta`) — v1.0.0. Pre-commit checklist: update index, classify change, bump per-skill vs. repo-wide release versions correctly.
- **project-documentation-archivist** (`content`) — v2.0.0. Evidence-first project knowledge base with managed blocks, deterministic source indexing, open questions, module manifests, and incremental processing.
- **sagan-scientific-debunker** (`content`) — v1.1.0. Adds systematic structured claim analysis and stronger source hierarchy.

### Protocol

- `HOW_TO_CREATE_SKILLS.md` — added a decision tree for per-skill vs. repo-wide version bumps; linked `superpowers:writing-skills` in Step 3; added "adding a skill" checklist.
- `VERSIONING.md` — added per-skill vs. repo-wide versioning examples, dirty-worktree note, release commit checklist.
- `CHANGELOG.md` — added historical entry guidance, documented the initial repo-wide release history as v1.0.0, added same-change-line multiple skill version bump guidance.
- `SKILL_TEMPLATE.md` — added `{category}` and `{status}` placeholders to metadata; added error-handling and gotchas guidance; clarified external tools in references section.

### Repository

- GitHub Actions CI validates all skills and checks version drift on push/PR (including Windows and Linux runners).
- The repository tracks its version through `.version-bump.json`.
- Added `RELEASE-NOTES.md` to keep detailed release history out of `README.md`.

## v1.0.0 (2026-07-04)

- Established the reusable Coferlandia skill repository protocol.
- Added Apache-2.0 licensing and repository-level author/license/version policy.
- Added `_protocol/` templates and `validate_skill.py` tooling.
- Added first four canonical skills under `skills/`.
