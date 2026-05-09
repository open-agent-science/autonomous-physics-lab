# v0.2 Overclaim Audit

## Scope

`TASK-0103` reviewed the main public-facing `v0.2` surfaces:

- `README.md`
- `docs/status.md`
- `docs/mission-control.md`
- `docs/results/*`
- `docs/campaigns/*`
- `docs/releases/*`
- `docs/announcement*`
- `claims/*`

The goal was not to rewrite the repository narrative from scratch. The goal
was to remove wording that drifted wider than the tested scope or that had
become stale after the newer Koide and validator campaign results.

## Highest-Risk Tightenings

1. Koide quark wording was tightened from a near-global negative framing to a
   scoped benchmark framing.
   Files:
   - `claims/CLAIM-0006-koide-quark-falsification.md`
   - `docs/results/koide-quark-cascade-falsification.md`

2. Neutrino falsification wording was tightened to stay explicitly inside the
   tested setup instead of sounding globally exhaustive.
   File:
   - `docs/results/koide-neutrino-falsification.md`

3. The particle-mass campaign page was refreshed so public readers see the
   current reproduction-plus-falsification package instead of an older
   charged-lepton-only story.
   File:
   - `docs/campaigns/particle-mass-relations.md`

4. The old `v0.1` release draft now carries a historical-note disclaimer so it
   is less likely to be mistaken for the current repository-wide state.
   File:
   - `docs/releases/v0.1-public-alpha.md`

5. `EXP-0010` muon g-2 output is now explicitly fenced off from the public
   success surface and described only as a guarded empirical formula-search
   stress test.
   Files:
   - `README.md`
   - `AGENTS.md`
   - `docs/status.md`
   - `docs/mission-control.md`
   - `docs/roadmap.md`
   - `docs/releases/v0.2-public-alpha.md`

## Current Public Wording Rule

- Reproductions should be described as "in scope" or benchmark-scoped.
- Falsifications should be described as "in scope" or "under the tested setup."
- No public surface should imply that APL has explained particle masses,
  made a discovery-level breakthrough, or globally settled Koide-like
  relations.

## Residual Risk

The main residual risk is not explicit hype language. It is future drift:
older campaign pages, release drafts, or claim files can become stale after
new canonical results land. The safest fix remains the current one: keep
status docs, campaign docs, and public result summaries aligned with canonical
artifacts and rerun wording audits before any public-opening decision.

`EXP-0010` is the clearest current example: once a high-risk formula-search
benchmark lands in canonical memory, it is easy for stale counts or loose
highlights to make it sound more central or more trustworthy than intended.
