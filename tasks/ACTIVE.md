# Active Task Board

## CURRENT STRATEGY

APL is verification-first scientific infrastructure.

Current phase: `v0.1-private-alpha — scientific campaign and contributor workflow validation`

Current goal:

- active scientific campaigns with conservative result wording
- private contributor pilot and maintainer review workflow validation
- public release only after explicit gates are satisfied

The repository remains private until
[../docs/public-release-gates.md](../docs/public-release-gates.md) are
satisfied.

Use [../docs/strategy.md](../docs/strategy.md) as the strategic compass and
[../docs/agent-task-protocol.md](../docs/agent-task-protocol.md) as the
canonical execution protocol. Use
[../docs/agent-operating-model.md](../docs/agent-operating-model.md) for
supporting workflow context and handoff norms.

Repository-level orientation now starts with
[../docs/mission-control.md](../docs/mission-control.md) and
[../docs/campaigns/README.md](../docs/campaigns/README.md) before drilling
into task-level work.

For new task ideas without a maintainer-assigned canonical `TASK-XXXX` id, use
the proposal-first flow in [../docs/task-proposal-protocol.md](../docs/task-proposal-protocol.md).

For spare token or time budget scientific work, use
[../tasks/microtasks/README.md](../tasks/microtasks/README.md) together with
[../docs/agent-scientific-work-mode.md](../docs/agent-scientific-work-mode.md).
Prefer one small batch from one campaign queue rather than mixing campaigns in
one PR.

<!-- BEGIN AUTO TASK STATUS BOARD -->

> This task-status snapshot is generated from canonical task YAML files.
> Edit `tasks/TASK-*.yaml` for routine status transitions, then run
> `python3 -m physics_lab.cli sync-active-board .` on the maintainer branch.

## READY

- `TASK-0066` — Review v0.2 public readiness gates (`release_review`, priority `medium`, difficulty `low`)
- `TASK-0112` — Implement microtask run registry and expanded repeatable queues (`agent_workflow`, priority `high`, difficulty `medium`)
- `TASK-0114` — Add microtask queue consistency validator (`agent_workflow`, priority `medium`, difficulty `low`)
- `TASK-0115` — Add docs-link integrity check for campaign and result pages (`maintainer_workflow`, priority `medium`, difficulty `low`)
- `TASK-0116` — Add microtask queue summary table generator (`agent_workflow`, priority `low`, difficulty `low`)
- `TASK-0117` — Add maintainer review and closeout Mermaid flow (`documentation`, priority `medium`, difficulty `low`)
- `TASK-0135` — Audit and freeze pendulum gauntlet reproducibility (`scientific_audit`, priority `high`, difficulty `medium`)
- `TASK-0136` — Split repository validation and scientific-memory integrity checks (`code_quality_refactor`, priority `medium`, difficulty `medium`)
- `TASK-0137` — Split maintainer review helper into clearer policy layers (`code_quality_refactor`, priority `medium`, difficulty `medium`)
- `TASK-0138` — Add canonical replay and golden-result hardening layer (`repository_validation`, priority `medium`, difficulty `medium`)
- `TASK-0146` — Add one-command core result reproduction script (`reproducibility`, priority `high`, difficulty `medium`)
- `TASK-0148` — Add scientific result quality rubric (`scientific_governance`, priority `high`, difficulty `medium`)
- `TASK-0149` — Define blind holdout benchmark protocol (`benchmark_protocol`, priority `high`, difficulty `medium`)
- `TASK-0150` — Create external reviewer replication guide (`documentation`, priority `medium`, difficulty `low`)
- `TASK-0159` — Implement anharmonic oscillator period benchmark with perturbative baseline and holdout evaluation (`scientific_benchmark`, priority `high`, difficulty `high`)

## IN_PROGRESS

None.

## REVIEW_READY

- `TASK-0133` — Repair duplicate result-id collision and prevent duplicate canonical results (`maintainer_workflow`, priority `high`, difficulty `medium`)
- `TASK-0154` — Add agent-run PR packaging and maintainer review checklist (`review_workflow`, priority `medium`, difficulty `medium`)
- `TASK-0157` — Close merged review-ready tasks after public-hardening and autonomy curation wave (`maintainer_workflow`, priority `high`, difficulty `low`)
- `TASK-0158` — Curate autonomy and scientific-value upgrade queue before public article prep (`maintainer_workflow`, priority `high`, difficulty `low`)
- `TASK-0161` — Close autonomy foundation tasks and unblock autonomous PR packaging (`maintainer_workflow`, priority `high`, difficulty `low`)

## DONE RECENTLY

- `TASK-0156` — Curate Phase B autonomous research follow-up queue (merged)
- `TASK-0153` — Run first pendulum autonomous research pilot with sandbox-only outputs (merged)
- `TASK-0152` — Implement research proposal preflight gate and sandbox agent-run layout (merged)
- `TASK-0151` — Define autonomous research loop contract and campaign autonomy profiles (merged)
- `TASK-0147` — Harden muon g-2 benchmark wording and guardrails (merged)
- `TASK-0145` — Add reproducibility capsules for major canonical results (merged)
- `TASK-0144` — Sync public-facing docs with canonical experiment state (merged)
- `TASK-0143` — Close stale merged workflow tasks and unblock release-review queue (merged)
- `TASK-0142` — Curate public-alpha hardening and credibility follow-up queue (merged)
- `TASK-0141` — Add context-bundle regeneration check to closeout helper (merged)
- `TASK-0139` — Curate scientific audit and architectural hardening follow-up queue (merged)
- `TASK-0134` — Salvage dimensional-validator replay and freeze benchmark scope (merged)
- `TASK-0128` — Add agent catalog and documentation entrypoint links (merged)
- `TASK-0127` — Implement muon g-2 empirical formula search benchmark (merged)
- `TASK-0126` — Curate canonical implementation task for muon g-2 formula-search salvage (merged)
- `TASK-0125` — Curate microtask PR flow improvement queue (merged)
- `TASK-0124` — Add microtask PR scaffold and preflight helper (merged)
- `TASK-0123` — Clarify batch microtask branch and title protocol (merged)
- `TASK-0122` — Add microtask PR template and metadata guidance (merged)
- `TASK-0121` — Curate newcomer contributor task batch for upcoming onboarding (merged)
- `TASK-0120` — Add use-your-agent quickstart diagram pack (merged)
- `TASK-0119` — Add thought-experiment campaign orientation note (merged)
- `TASK-0118` — Add particle-mass campaign map diagram (merged)
- `TASK-0113` — Align maintainer review helper protected-artifact checks with scientific task contracts (merged)
- `TASK-0111` — Plan microtask scale readiness for daily multi-agent scientific work (merged)
- `TASK-0110` — Verify high-precision asymptotic refined pendulum model (merged)
- `TASK-0109` — Define protocol support for microtask batch PRs (merged)
- `TASK-0108` — Add microtask PR support to maintainer review helper (merged)
- `TASK-0107` — Reframe TASK-0104 as a repository-native opening pack (merged)
- `TASK-0106` — Close stale completed tasks and align closeout validation (merged)
- `TASK-0105` — Curate v0.2 packaging follow-up queue and close completed task admin items (merged)
- `TASK-0104` — Prepare v0.2 repository opening pack (merged)
- `TASK-0103` — Run final public overclaim audit for v0.2 materials (merged)
- `TASK-0102` — Package Koide falsification campaign results (merged)
- `TASK-0100` — Update status and v0.2 roadmap after Koide and validator campaign results (merged)
- `TASK-0099` — Refresh repository snapshot logic to prefer current source-of-truth state (merged)
- `TASK-0097` — Create negative result registry for APL falsifications (merged)
- `TASK-0096` — Write Koide neutrino falsification public result package (merged)
- `TASK-0095` — Add visual orientation diagrams for humans and agents (merged)
- `TASK-0094` — Fix maintainer review helper false-positive stale diff detection (merged)
- `TASK-0093` — Test Koide relation for neutrino masses (merged)
- `TASK-0092` — Fix duplicate canonical task ids and enforce uniqueness (merged)
- `TASK-0088` — Test Brannen quark-mass Koide cascade for up and down sectors (merged)
- `TASK-0087` — Stabilize strict input-hash validation across Windows line endings (merged)
- `TASK-0086` — Run physics-constrained pendulum gauntlet with fixed log coefficient (merged)
- `TASK-0085` — Define PR title format for microtask PRs without a canonical TASK-XXXX (merged)
- `TASK-0084` — Add explicit no-direct-main-push guardrail to agent instructions (merged)
- `TASK-0083` — Add agent-ready scientific work loop follow-up tasks (merged)
- `TASK-0082` — Add Koide baseline planning for guarded next-step evaluation (merged)
- `TASK-0081` — Run first hypothesis register pilot through an APL next-step flow (merged)
- `TASK-0080` — Run first dimensional-analysis scientific microtask batch (merged)
- `TASK-0078` — Add Agent Work Menu for spare-token scientific work (merged)
- `TASK-0077` — Add proposal PR format and salvage guardrails (merged)
- `TASK-0076` — Add fast and deep maintainer review lanes (merged)
- `TASK-0075` — Add scientific microtask queues for agent work (merged)
- `TASK-0074` — Harden closeout protocol binding checks for automation (merged)
- `TASK-0073` — Define maintainer automation agent architecture and routine instructions (merged)
- `TASK-0071` — Support closeout batch PRs in review helper (merged)
- `TASK-0067` — Add v0.2 release-focused campaign tasks (merged)
- `TASK-0064` — Implement dimensional analysis validator MVP (merged)
- `TASK-0063` — Generate v0.2 static visual result pack (merged)
- `TASK-0062` — Update project status and roadmap for scientific campaign phase (merged)
- `TASK-0061` — Create Mission Control and campaign map (merged)
- `TASK-0060` — Add open pull request list to repository snapshot (merged)
- `TASK-0058` — Standardize scoped verdict wording for tau holdout (merged)
- `TASK-0057` — Reduce snapshot noise from worktrees and include proposal backlog (merged)
- `TASK-0056` — Accept selected science-track proposals into canonical tasks (merged)
- `TASK-0055` — Add experiment flow diagram to architecture docs (merged)
- `TASK-0054` — Fix maintainer review helper temp claim path handling in git worktrees (merged)
- `TASK-0051` — Define hypothesis register schema and launch entry micro-task track (merged)
- `TASK-0050` — Define and launch approximation-breakdown probes micro-task track (merged)
- `TASK-0049` — Define and launch physical constants verification micro-task track (merged)
- `TASK-0048` — Add schema support for dataset-based particle-mass reproduction benchmarks (merged)
- `TASK-0047` — Reduce closeout PR conflicts around active board sync (merged)
- `TASK-0044` — Sync active task board from task files to reduce merge conflicts (merged)
- `TASK-0043` — Add task proposal protocol and id allocation rules (merged)
- `TASK-0042` — Add numerology guardrails for particle mass relation work (merged)
- `TASK-0041` — Design complexity penalty for mass-relation formulas (merged)
- `TASK-0040` — Build particle mass relation falsifier MVP (merged)
- `TASK-0039` — Design Koide-like triplet search with baselines (merged)
- `TASK-0038` — Reproduce historical tau-mass holdout prediction (merged)
- `TASK-0037` — Reproduce Koide charged-lepton relation (merged)
- `TASK-0036` — Create particle mass dataset scaffold (merged)
- `TASK-0035` — Refactor maintainer review checks into smaller modules (merged)
- `TASK-0034` — Add maintainer review agent mode (merged)
- `TASK-0033` — Standardize contributor-agent identity format (merged)
- `TASK-0032` — Build public scientific result package for Pendulum Gauntlet 100 (merged)
- `TASK-0031` — Add beginner-friendly contributor task set (merged)
- `TASK-0030` — Record first friend contributor dry run (merged)
- `TASK-0029` — Audit project language for overclaim risk (merged)
- `TASK-0028` — Plan light-clock thought experiment consistency check (merged)
- `TASK-0027` — Create units and physical constants reference (merged)
- `TASK-0026` — Add 10 more dimensional-analysis challenge items (merged)
- `TASK-0025` — Create result artifacts index (merged)
- `TASK-0024` — Create task index table (merged)
- `TASK-0023` — Create first contributor runbook (merged)
- `TASK-0022` — Add PR review bundle snapshot script (merged)
- `TASK-0021` — Add AI agent attribution policy (merged)
- `TASK-0020` — Add pytest-timeout and validation safeguards against hanging tests (merged)
- `TASK-0019` — Standardize agent branch, commit, and pull request protocol (merged)
- `TASK-0018` — Support planning-only and workflow tasks without fake hypothesis references (merged)
- `TASK-0017` — Create a dimensional analysis challenge set (merged)
- `TASK-0015` — Plan the diffusion scaling benchmark (merged)
- `TASK-0014` — Plan a thought-experiment consistency suite (merged)
- `TASK-0013` — Plan a particle mass relation falsifier inspired by Koide-style formulas (merged)
- `TASK-0012` — Run a private multi-agent contributor dry run (merged)
- `TASK-0011` — Audit numerical precision versus model residual for the pendulum gauntlet run (merged)
- `TASK-0010` — Run pendulum hypothesis gauntlet with 100 candidate formulas (merged)
- `TASK-0008` — Add machine-readable review metadata for patch-style evidence artifacts (merged)
- `TASK-0007` — Add fail-on-warnings support for strict repository validation (merged)
- `TASK-0006` — Establish shared agent task board and operating model (merged)
- `TASK-0005` — Add artifact hash drift validation (merged)
- `TASK-0004` — Strengthen claim promotion policy (merged)
- `TASK-0003` — Add theory-aware pendulum approximation near the separatrix (merged)
- `TASK-0002` — Verify damped oscillator regimes against exact solutions (merged)
- `TASK-0001` — Find better pendulum correction formula (merged)

## PROPOSED

- `TASK-0016` — Plan an electromagnetic invariance mini-benchmark (`benchmark_planning`, priority `medium`, difficulty `medium`)
- `TASK-0089` — Search for empirical formula for muon g-2 anomaly using fundamental constants (`benchmark_planning`, priority `medium`, difficulty `high`)
- `TASK-0090` — Design empirical formula search for Hubble tension reconciliation (`benchmark_planning`, priority `low`, difficulty `high`)
- `TASK-0091` — Find analytic correction to Bethe-Weizsäcker formula for nuclear magic numbers (`scientific_experiment`, priority `medium`, difficulty `medium`)

## BLOCKED

- `TASK-0155` — Run second autonomous research pilot on dimensional-analysis validator (`autonomous_research_pilot`, priority `medium`, difficulty `high`)
- `TASK-0160` — Run autonomous research pilot on anharmonic oscillator benchmark (`autonomous_research_pilot`, priority `high`, difficulty `high`)

## REJECTED

- `TASK-0009` — Plan EXP-0003 as a diffusion scaling benchmark (`benchmark_planning`, priority `high`, difficulty `medium`)
- `TASK-0059` — Prepare Koide tau holdout public summary package (`documentation`, priority `medium`, difficulty `low`)
- `TASK-0065` — Finalize Koide tau holdout public result package (`release_preparation`, priority `medium`, difficulty `medium`)

<!-- END AUTO TASK STATUS BOARD -->

## Recommended first tasks for new contributors

Prefer independent `READY` tasks with:

- documentation-only scope;
- no canonical result-artifact churn;
- no shared branch or board-maintenance coupling;
- validation that does not require regenerating benchmark outputs.

If a contributor first needs scientific context rather than a task, start with
[../docs/campaigns/README.md](../docs/campaigns/README.md) and then return to
the `READY` section.

If multiple `READY` tasks fit, pick the smallest one that does not touch the
same artifact surface as another open PR.

## DO NOT START YET

- dashboard
- web API
- arXiv or OpenAlex ingestion
- multi-agent runtime
- database backend
- public launch
- discovery-level physics claims

## PROPOSED NOTE

`PROPOSED` items are backlog ideas, not active execution tasks. Agents should
start from `READY` tasks unless a maintainer explicitly redirects them.
