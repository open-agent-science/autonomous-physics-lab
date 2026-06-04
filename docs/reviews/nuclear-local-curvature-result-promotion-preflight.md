# Nuclear Local-Curvature Result-Promotion Preflight

**Task:** `TASK-0428`
**Scorecard:** [`docs/result-promotion-scorecard.md`](../result-promotion-scorecard.md)
**Protocol:** [`docs/result-promotion-protocol.md`](../result-promotion-protocol.md)
**Preflight verdict:** `NEGATIVE_MEMORY` (sandbox-only; no `PRED`/`CLAIM`/`KNOW`/`RESULT` artifact authorized)

## Scope

This preflight applies the result-promotion scorecard to the combined
local-curvature artifact set produced by `TASK-0394` (no-leakage
prototype, `AGENT-RUN-0039`) and `TASK-0397` (negative-control
expansion, `AGENT-RUN-0041`). It classifies the lane in the scorecard
vocabulary, lists exact Gate A blockers for any future publication
attempt, and decides whether to propose a narrow follow-up
publication task or close the lane as negative scientific memory.

The preflight is metadata-only. It does **not** fit any candidate,
score any reveal, fetch external data, modify `prediction_registry/`,
`claims/`, `knowledge/`, or `results/` artifacts, and does not
reopen `LOCAL-CURVATURE-001` as a positive candidate.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/result-promotion-protocol.md` | Promotion-protocol authority. |
| `docs/result-promotion-scorecard.md` | Required-scores list and verdict vocabulary. |
| `TASK-0394` | No-leakage prototype task scope. |
| `docs/reviews/nuclear-local-curvature-no-leakage-prototype.md` | TASK-0394 falsification review. |
| `agent_runs/AGENT-RUN-0039/metrics.json` | TASK-0394 prototype metrics + no-leakage contract block. |
| `docs/reviews/nuclear-local-curvature-negative-control-expansion.md` | TASK-0397 expanded-controls review. |
| `agent_runs/AGENT-RUN-0041/metrics.json` | TASK-0397 expanded-controls metrics. |
| `docs/nuclear-residual-feature-no-leakage-contract.md` | Cross-family eligibility map (F1 family). |
| `docs/nuclear-local-curvature-no-leakage-freeze-protocol.md` | Per-family freeze protocol the prototype implements. |

## Headline Evidence (already in the reviewed artifacts)

| Quantity | Value | Source |
| --- | ---: | --- |
| Lane verdict under no-leakage prototype | `FALSIFIED` | `AGENT-RUN-0039` / TASK-0394 review |
| Candidate `LOCAL-CURVATURE-001` full-known ΔMAE | **+0.0196 MeV** (worse than zero correction) | `AGENT-RUN-0039` |
| Strongest no-leakage control vs candidate margin | **−0.0596 MeV** (control beats candidate) | `AGENT-RUN-0039` summary |
| Strongest control id | `LOCAL-NOLEAK-CTRL-002` | `AGENT-RUN-0039` |
| Candidate subset win-rate | **0 of 19 subsets** | `AGENT-RUN-0039` summary |
| Pre-no-leakage lane verdict (TASK-0397) | `PARTIALLY_VALID` | `AGENT-RUN-0041` / TASK-0397 review |
| Pre-no-leakage candidate vs strongest control margin | +0.5443 MeV | `AGENT-RUN-0041` |
| Training rows | 11 (NMD-0002) | `AGENT-RUN-0039.datasets` |
| Holdout rows | 295 (post-AME2020 primary holdout) | `AGENT-RUN-0039.datasets` |
| Full-known unique rows | 306 | `AGENT-RUN-0039.datasets` |
| Frozen baseline | `RESULT-0015` semi-empirical | `AGENT-RUN-0039.frozen_baseline` |
| Live external fetch | `false` | both runs |

**Key narrative.** TASK-0397 left `LOCAL-CURVATURE-001` as the
strongest local-curvature candidate after an expanded but
leakage-permissive control panel (PARTIALLY_VALID, margin
+0.544 MeV). TASK-0394 then closed the leakage path (per-fold
neighbor caches, baseline-only neighbor residuals, target-row
exclusion, holdout-row exclusion from cache) and the candidate
flipped to FALSIFIED: it became slightly worse than the no-correction
baseline and lost to its strongest no-leakage control on every
subset. This is exactly the failure mode the
no-leakage contract was written to expose.

## Scorecard

Applied to the combined `TASK-0394` + `TASK-0397` artifact set.

| Category | Score | Notes |
| --- | --- | --- |
| **Baseline strength** | `PASS` | `RESULT-0015` semi-empirical baseline is frozen and reused; coefficients listed in `AGENT-RUN-0039.frozen_baseline`; the 306-row full-known surface is fully committed. |
| **Source provenance** | `PASS` | NMD-0002 training slice and post-AME2020 primary holdout are both committed datasets; `live_external_fetch_allowed: false` in both runs; no opaque third-party calls. |
| **Artifact checksums** | `PARTIAL` | `agent_run.yaml`, `metrics.json`, and review notes are committed and content-addressable via git, but no scorecard-level snapshot checksum or dataset hash field is recorded in either metrics file. NMD-0002 / post-AME2020 schema tests cover dataset structure; per-snapshot checksum semantics would need a separate hardening pass before public reuse. |
| **Holdout or reveal quality** | `FAIL` | The lane is fully retrospective. The post-AME2020 panel is a time-split-style holdout, not a frozen prospective reveal scored against future-only measurements. No `PRED-XXXX` entry was registered for `LOCAL-CURVATURE-001`. Per the prediction-reveal protocol, this lane never reached reveal scope. |
| **Uncertainty handling** | `PARTIAL` | Per-row baseline residuals are deterministic, but neither run propagates per-row measurement uncertainties through MAE or computes a confidence interval on `candidate ΔMAE` vs the no-correction baseline. The TASK-0344-style uncertainty discipline is recorded in Nuclear-campaign context but not re-applied to the candidate-vs-control margin. |
| **Negative controls** | `PASS` | TASK-0397 added six expanded controls (chain-shuffled, mass-number-only, magic-distance-only, smooth-window, neighbor-availability, near-null neighborhood). TASK-0394 added four no-leakage controls including `LOCAL-NOLEAK-CTRL-002` (the falsifier). The strongest control beats the candidate by 0.060 MeV on full-known and on every one of 19 subsets. This is the load-bearing PASS for the verdict. |
| **Leakage risk** | `PASS` | The no-leakage contract block in `AGENT-RUN-0039` records `target_row_excluded: true`, `per_fold_neighbor_cache: true`, `baseline_only_neighbor_residuals: true`, `holdout_rows_excluded_from_cache: true`, `missing_neighbor_strategy: zero_fill_when_no_left_or_right_neighbor`, `target_family: F1_local_curvature`, and pins the freeze protocol path. F1 promotion path of the no-leakage contract is satisfied. |
| **Reproducibility** | `PASS` | Both runs are deterministic; runners, metrics, datasets, frozen baseline, and review notes are all in-repo and re-executable. `metrics.json` shape allows a re-runner to recompute deltas without external inputs. |
| **External comparability** | `FAIL` | Single-tool execution (Codex, `AGENT-RUN-0039` / `AGENT-RUN-0041`), single frozen baseline (`RESULT-0015`), no cross-source replay, no independent re-implementation. Strict Gate-B style independent replay does not exist for this lane. |
| **Public wording risk** | `PASS_IF_FRAMED_AS_FALSIFICATION` | Existing TASK-0394 review correctly uses "FALSIFIED", "negative/inconclusive campaign memory", "does not authorize claim promotion, public discovery wording, a reveal score, or a PRED-* entry". Any rewording that drops the falsification framing would flip this to `FAIL`. |

**Three-axis classification per the scorecard:**

- **Sandbox follow-up eligibility:** `NOT_RECOMMENDED` — the candidate is falsified under the contract-compliant no-leakage prototype; spawning further variant sandbox runs of `LOCAL-CURVATURE-*` would chase noise.
- **Public benchmark-summary eligibility:** `NOT_APPLICABLE` — the lane is a falsification, not a benchmark surface. The benchmark-summary verdict is reserved for reproducible benchmark / failure-map artifacts (compare the Exoplanet failure-map scorecard).
- **Claim-candidate eligibility:** `BLOCKED` — `FAIL` on holdout-or-reveal-quality and external-comparability; `PARTIAL` on artifact checksums and uncertainty handling. Even a maintainer-approved claim-candidate review would not pass.

## Verdict (scorecard vocabulary)

**`NEGATIVE_MEMORY`** — preserve the `LOCAL-CURVATURE-001`
falsification as Nuclear-campaign negative scientific memory.

Rationale:

- The candidate is `FALSIFIED` under the bounded no-leakage panel by
  `LOCAL-NOLEAK-CTRL-002` with a 0.060 MeV margin and 0 of 19 subset
  wins.
- Pre-no-leakage `PARTIALLY_VALID` evidence is exactly the artifact
  the no-leakage contract was designed to demote, so the lane's
  earlier favorable framing should not be revived.
- Three of four claim-candidate Gate A categories are `FAIL` or
  `PARTIAL`; promoting to any tier higher than `NEGATIVE_MEMORY`
  would force the wording into discovery-adjacent space that the
  scorecard explicitly forbids.
- The lane is more useful preserved as a worked example of "what the
  no-leakage gate looks like in practice" than as a sandbox seed for
  more variants.

## Allowed and Forbidden Wording

**Allowed:**

- "APL falsified `LOCAL-CURVATURE-001` under a bounded no-leakage
  prototype."
- "Negative / inconclusive campaign memory for the
  local-curvature residual lane."
- "Preserved as a worked example of the F1 promotion path."
- "Pre-no-leakage controls showed partial validity; the no-leakage
  prototype removed it."
- "Sandbox-only retrospective evidence."

**Forbidden:**

- "discovery", "new nuclear law", "breakthrough", "first-principles
  result";
- "reveal success" or any wording that implies the candidate scored
  against frozen prospective `PRED-*` rows;
- "broad formula for nuclear masses";
- any phrasing that treats the pre-no-leakage `PARTIALLY_VALID`
  status as the current state.

## Gate A Blockers For Any Future Publication Attempt

A future publication task (per the result-promotion protocol) would
need to clear, at minimum:

1. **Holdout / reveal quality (`FAIL`).** Register a `PRED-XXXX`
   entry for a future `LOCAL-CURVATURE-*` candidate before reveal
   data exists, with no-peek discipline. The current lane has none.
2. **External comparability (`FAIL`).** Independent re-implementation
   of the no-leakage prototype by a different agent tool, against
   the same NMD-0002 + post-AME2020 surfaces, with deterministic
   tolerances on candidate ΔMAE and control margins.
3. **Artifact checksums (`PARTIAL`).** Add scorecard-level
   per-snapshot dataset checksums to the metrics file so the
   exact `AGENT-RUN-0039` inputs can be hashed and re-verified.
4. **Uncertainty handling (`PARTIAL`).** Propagate committed per-row
   measurement uncertainties through the MAE difference between
   candidate, baseline, and strongest control; report a confidence
   interval on the falsification margin.
5. **Wording risk on candidate revival.** Any "we tested it and it
   failed" framing must keep the falsification load-bearing; rewording
   the same evidence to imply revival would flip the score to `FAIL`.

None of these are authorized by this PR.

## Follow-Up Recommendation

The task scope allows proposing one narrow follow-up *only if the
preflight passes*. The preflight does not pass for any
promotion-tier higher than `NEGATIVE_MEMORY`, so the recommendation
is **do not open a new task**. The existing TASK-0394 / TASK-0397
reviews plus this preflight already capture the load-bearing
information:

- the candidate is falsified;
- the no-leakage panel that falsified it is recorded and
  reproducible;
- the F1 contract path is now an operating example, not a path that
  needs more variants.

A future maintainer who wants to package the falsification as a
narrow public artifact (e.g. a one-page "what the no-leakage gate
catches" note for the public dashboard) would need a separate task
under the dashboard / public-summary scope, not under the
LOCAL-CURVATURE-* lane scope. That decision is left to the
maintainer; this PR does not propose it.

## Output Routing (`docs/result-promotion-protocol.md`)

- **Task verdict:** `NEGATIVE_MEMORY` (scorecard vocabulary).
- **Canonical destination:** this review note
  (`docs/reviews/nuclear-local-curvature-result-promotion-preflight.md`).
- **Review tier:** `none` (no `RESULT/PRED` tier applies; preserved
  as Nuclear-campaign negative memory).
- **Gate A status:** `BLOCKED` (`FAIL` on holdout/reveal-quality
  and external-comparability; `PARTIAL` on artifact checksums and
  uncertainty handling).
- **Gate B status:** `not_attempted` (no cross-source / cross-tool
  replay performed; would require its own task).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations and blockers:** see the Scorecard, Gate A Blockers,
  and Limitations sections.

No `result_candidate_review.yaml` is created. The task spec allows it
"only if the schema already supports it" and only when the preflight
passes; the preflight verdict is `NEGATIVE_MEMORY`, so no machine
review record is appropriate.

## Limitations

- The preflight is metadata-only; it does not re-execute the
  runners or recompute metrics. It depends on the committed
  `agent_run.yaml` + `metrics.json` integrity for both `AGENT-RUN-0039`
  and `AGENT-RUN-0041`.
- The scorecard is applied to the combined TASK-0394 + TASK-0397
  artifact set; if either artifact is later rewritten, this preflight
  must be re-run.
- The lane is single-tool (Codex). The "external comparability" FAIL
  reflects that this preflight is also single-tool (Claude Code) and
  is not a Gate-B style independent replay of the runner itself.
- The `NEGATIVE_MEMORY` verdict applies only to the
  `LOCAL-CURVATURE-001` candidate under the present no-leakage
  prototype. Other F1-family candidates (`LOCAL-CURVATURE-002`,
  `-003`) are already falsified by the negative-control expansion;
  they remain sandbox memory and do not get a fresh sandbox lane
  from this preflight.
- The preflight does not authorize, schedule, or sequence any of the
  five Gate A blockers; each would be its own maintainer-approved
  task.

## What This Preflight Does Not Do

- It does not write any `PRED-XXXX.yaml`, `CLAIM-XXXX`, `KNOW-XXXX`,
  or canonical `RESULT-XXXX` artifact.
- It does not reopen `LOCAL-CURVATURE-001` as a positive candidate.
- It does not relax the F1 promotion path, the freeze protocol, the
  no-leakage contract, the prediction-reveal protocol, or the
  controls-first gauntlet.
- It does not run an independent re-implementation; the strict
  Gate-B-style replay remains an unresolved follow-up.
- It does not propose a public-dashboard summary task; the
  maintainer decides whether to open one separately.
