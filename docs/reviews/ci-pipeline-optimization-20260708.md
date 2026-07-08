# CI Pipeline Optimization — 2026-07-08 (TASK-0966)

- Basis: three-stream audit — workflow-config review, 150-run history
  (2026-07-06..08, 763 runner-min), and a `--durations=50` suite profile.
- Non-claims: CI tooling only; no scientific artifact, board, or policy
  change.

## Measured problem

| Metric (per typical merged PR) | Before |
| --- | --- |
| Full test suite executions | 3x (PR + 2 merge-matrix legs) |
| `validate-repo --strict` executions | ~5x as CI steps + ~5x inside suite smokes |
| Workflow runs triggered | 5-6 (incl. CI on the board-sync bot commit) |
| Bot machinery share of run count | 31% (competing for 2 self-hosted slots) |
| p90 self-hosted job queue | 386 s (worst run: 64% of wall time queued) |
| Weekly pace | ~2,400 runner-min |

Slowest tests: the tier-1 freeze full recompute (105 s, already
`full_repo`-marked and load-bearing) and repo-wide validate smokes
(20-40 s each). The 2026-07-08 nightly failure was one of those smokes
exceeding the global 60 s pytest timeout on a hosted runner - a repo-growth
drift, not flakiness.

## Changes and coverage preservation

| Change | Savings | Where the coverage lives now |
| --- | --- | --- |
| main-matrix -> single 3.11 leg, no ruff, no second full_repo pass | ~900 min/wk | 3.12 full suite: PR fast lane (identical squash tree) + NEW nightly whole-suite step; ruff: PR lane; full_repo: single merge leg + risk-gated PR lane + nightly |
| PR `full_repo` smoke gated to non-draft pushes | ~380 min/wk | every ready-for-review push + merge leg + nightly |
| Board-sync commit: `[skip ci]` + pre-push validation inside the sync job (strict validate + the same 8 targeted docs/task test files) | ~210 min/wk + 31% fewer queue entries | identical checks, moved before the push instead of after |
| `test_status_cli_reports_project_snapshot_fields` -> `full_repo` (census now 9) | ~18 s per PR push | full_repo lanes |
| `timeout(240)` on the two repo-wide smokes | fixes the real nightly failure | n/a (reliability fix) |
| Stale config removed: `master` trigger, dead `CONTEXT.md` glob, "~7 tests" comment | hygiene | n/a |

Expected pace: ~2,400 -> ~900-1,000 runner-min/wk, with burst depth on the
two self-hosted slots reduced by roughly a third of run count - queue
latency improves without adding a runner (measured utilization was only
~11%; queueing, not capacity, was the bottleneck).

## Deliberately NOT changed

- Job names backing required branch-protection checks.
- The 105 s tier-1 freeze recompute: expensive and load-bearing (protects
  the sealed PRED registry); it stays in the full_repo set.
- Replay-determinism tests (9-18 s each): they are the product.
- `fail-fast: false` semantics and PR cancel-in-progress (already correct).
- No test was deleted or weakened; only markers/timeouts added.

## Verification

- All three workflow files parse (yaml.safe_load).
- Marker census: 9 `full_repo` tests collect; 1,970 fast-lane tests
  collect; ruff clean.
- The three touched tests pass locally (25.6 s, incl. both timeout-bumped
  smokes).
## Refinements from an independent cross-check audit

A second agent audit cross-checked this change and contributed three fixes
applied in the follow-up commit:

1. `pull_request` trigger gains `types: [opened, synchronize, reopened,
   ready_for_review]` - without `ready_for_review` (absent from the default
   set) the draft-gated smoke would never fire on a draft -> ready flip
   that has no new push. This was a real gap in the first commit.
2. Path-based pytest invocations ignore markers: the targeted docs/task
   list includes `tests/test_validate_repo_auto_sync.py`, whose live
   full_repo smoke was silently running in the docs lane and in the
   board-sync pre-push step. Both invocations now carry
   `-m "not full_repo"` (verified: 8/9 collected, live smoke deselected).
3. Dedicated full_repo invocations (nightly + PR risk step) now run
   `-n0 --timeout=300`: parallel repo-wide scans contend with the GP freeze
   recompute (measured 55 s solo vs 124 s under xdist); serial is ~3 min
   and stable.

The cross-check also independently confirmed the stale findings, the
nightly root cause, and the caution against `fetch-depth: 2` (kept out).

- Follow-up candidates (not in this PR): uv-based env builds (~6 installs
  per PR), `fetch-depth: 2` in classify, a `ci-full` label to force the
  smoke on a draft.
