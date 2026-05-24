# Strategy Curator Response - 2026-05-24

Status: maintainer-facing task-queue synthesis; no scientific claim promotion.

## Verdict

The strategic curator report is useful, but part of its repository-state
snapshot is already stale after the latest task-queue merge. The READY pool is
no longer four tasks, and `main` is clean after the post-merge board sync.

The important recommendation still stands: APL should now optimize for a
steady conveyor of reviewable science outputs, blocker reviews, and campaign
decisions rather than broad new infrastructure.

## Accepted

- Keep Nuclear as the flagship validation challenge, but avoid another
  unbounded audit loop.
- Treat Exoplanet Mass-Radius as the fastest visible benchmark/result surface.
- Keep Quantum Size Effects and Atomic Clock Residuals source-gated until
  direct rows and uncertainty semantics are reviewable.
- Add gates that make result promotion, prediction-registry reveal readiness,
  and campaign maturity explicit.
- Keep a minimum READY science task pool so parallel agents have independent
  work without inventing ad hoc tasks.

## Already Covered

- Fresh-data source artifacts, manifests, extraction ledgers, stop conditions,
  and readiness matrix work are covered by `TASK-0373` through `TASK-0379`.
- Nuclear no-leakage and stability follow-up work is covered by `TASK-0367`
  and `TASK-0368`.
- Exoplanet residual mapping and bounded residual scouts are covered by
  `TASK-0362`, `TASK-0369`, and `TASK-0370`.
- Atomic direct-row and source-version stop-condition work is covered by
  `TASK-0371` and `TASK-0372`.

## Rejected Or Deferred

- No new "clean generated board state" task is needed while `main` is clean and
  generated task views are handled by the post-merge board-sync action.
- No duplicate campaign-curator generator task is needed yet because the repo
  already has `scripts/apl_campaign_curator.py` and
  `physics_lab.registry.campaign_curator`.
- No public-alpha push should be tied to Nuclear sandbox evidence alone.

## New Task Decisions

- Update `TASK-0378` so the fresh-data readiness matrix also defines campaign
  maturity states.
- Add `TASK-0380` for a result-promotion scorecard.
- Add `TASK-0381` for a machine-readable Nuclear prediction registry count and
  reveal-readiness report.
- Add `TASK-0382` for a science-output conveyor health report.
- Add `TASK-0383` for a READY science task pool health policy.

These tasks are deliberately bounded: they improve the gates that decide when
science outputs are real enough to show, without promoting any current sandbox
result into a claim.
