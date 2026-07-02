# NMD-0003 GP Uncertainty-Calibration Failure — Negative/Blocker Result Preflight

- Task: `TASK-0912`
- Domain: nuclear mass residuals (NMD-0003 GP predictive uncertainty)
- Publication class checked: scoped negative/blocker `RESULT`
- Source finding: `TASK-0899` no-peek calibration audit
  (`NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED`)
- Outcome: `KEEP_REVIEW_NOTE_ONLY` (no `RESULT-*` artifact created)

## Purpose

This is a package-or-stop preflight. It decides whether the `TASK-0899` no-peek
calibration audit — in which no predeclared route family met the frozen success
conditions and `TASK-0827` stayed blocked — should become a canonical
`AGENT_PUBLISHED` negative/blocker `RESULT-*`, stay review-note-only memory, or
wait for a dedicated calibration-method task.

It does not tune or rerun any calibration family, does not create a `RESULT-*`,
`PRED-*`, `CLAIM-*`, or `KNOW-*` artifact, does not modify `RESULT-0025`, does
not create an `agent_runs/AGENT-RUN-*` entry, and does not unblock `TASK-0827`.
The failed success conditions, the heavy-tail ledger, and the prediction-freeze
impact are preserved exactly as recorded in the source evidence.

## Source material

- [NMD-0003 GP no-peek uncertainty calibration audit](nmd0003-gp-uncertainty-calibration-audit.md)
- `agent_runs/AGENT-RUN-0089/metrics.json`
- `agent_runs/AGENT-RUN-0089/report.md`
- [Result promotion protocol](../result-promotion-protocol.md)
- [Nuclear prediction reveal protocol](../nuclear-prediction-reveal-protocol.md)
- [RESULT-0025 (NMD-0003 GP extrapolation replay)](../../results/EXP-0018/RUN-0001/result.yaml)
- [AGENT_PUBLISHED result template](../../results/RESULT-TEMPLATE.agent-published.yaml)

## The finding is deterministic and replayable

The underlying negative finding is deterministic and Gate-B-replayable from
committed inputs. Re-running `python3 scripts/run_nmd0003_gp_calibration_audit.py`
against the committed inputs reproduces the recorded audit exactly (no random
seed; closed-form GP fit and LOO identities). Recorded provenance:

- code reference `physics_lab/engines/nmd0003_gp_calibration_audit.py`;
  engine version `0.1.0`; physics_lab `0.1.0`.
- git commit `ef12778c67ba349759d97b31611602308503c78e`.
- input SHA-256 hashes: dataset
  `f36ca012704ad8d5ffd039f2b8f01b5553690685d447aee3bab0f9983edf9d52`; frozen
  gate `2988c2eb28e0e1bee783bd4824a9680313b5ef81f1e9ae96698893e4525b8cd2`;
  post-AME2020 holdout
  `47bfe520df8ca4a95c1614192c5da165782b2308ba58110e6832afb1b8151e49`.

Replayability of the *finding* is necessary but not sufficient for Gate A. Gate
A also requires a schema-valid `results/.../result.yaml` bound to registered
experiment and hypothesis identities. That packaging layer is where the blockers
sit.

### Failed success conditions preserved exactly

Predeclared success conditions (frozen before scoring): central calibration
`|1-sigma coverage - 0.682689| <= 0.05 AND |2-sigma coverage - 0.9545| <= 0.03`;
tail control `0.85 <= RMS standardized residual <= 1.2`; sharpness
`median width inflation <= 3.0 AND p90 width inflation <= 4.0`; coverage surface
(no target silently dropped); scope (audit only, `TASK-0827` stays blocked
unless every condition passes). Holdout scoring after freeze:

| family | 1-sigma cov | 2-sigma cov | RMS z | median width infl | p90 width infl | all pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `global_robust_tail` | `0.623729` | `0.959322` | `4.333163` | `0.652357` | `0.652357` | `False` |
| `region_quantile_min_count` | `0.654237` | `0.949153` | `4.003043` | `0.701762` | `1.333223` | `False` |
| `conformal_global` | `0.623729` | `0.959322` | `4.333163` | `0.652357` | `0.652357` | `False` |

Any family passes: `False`. Passing families: `none`. Tripped stop conditions:
`none`. Every family fails tail control (RMS z far above `1.2`); the tail is not
fixable by the frozen multipliers without over-shrinking central coverage.

### Heavy-tail ledger preserved exactly

The dominant driver is a single heavy-tail holdout outlier; `Ga-84` at
`z = 46.302384` (corrected residual `26.33775` MeV, raw sigma `0.568821` MeV,
`medium_60_le_A_lt_140`, `high_eta_ge_0_25`, `not_near_magic`). The next four
are `Si-23` (`4.043471`), `P-26` (`3.791288`), `Si-24` (`3.436624`), and
`Sc-51` (`-3.105043`). This ledger is not re-derived here; it is cited from the
source audit unchanged.

### Prediction-freeze impact preserved exactly

Prediction-freeze impact: `unchanged_task_0827_remains_blocked`. No frozen route
family met the predeclared success conditions, so `TASK-0827` stays blocked.
This preflight does not change that.

## Gate A checklist (met / not-met per condition)

The nine mechanical Gate A conditions from `docs/result-promotion-protocol.md`
for a `RESULT-*`, evaluated against the `TASK-0899` audit as-is:

| # | Gate A condition | Status | Evidence / gap |
| --- | --- | --- | --- |
| 1 | Deterministic run (`command` + `code_reference`, replay reproduces values) | `MET` | Pinned command, engine, `git_commit`, and no-seed closed-form determinism are recorded and replayable. |
| 2 | Verification block populated (>=1 explicit check, non-empty `best_verdict`) | `NOT MET` | Checks are describable, but the native verdict `NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED` is not in the `result.schema.json` enum. A schema-valid negative result would have to be re-expressed as `best_verdict: INVALID` (or `INCONCLUSIVE`), which no committed artifact currently emits. |
| 3 | Input hashes recorded | `PARTIAL` | Three SHA-256 input hashes exist, but `result.schema.json` requires `input_file_hashes` keyed exactly `config` / `experiment` / `hypothesis` / `task` (optional `fixture`). The audit's keys are `dataset` / `frozen_gate` / `post_ame2020_holdout`; no committed `config`/`experiment`/`hypothesis`/`task` input snapshots exist for a calibration-audit result. |
| 4 | Limitations not empty | `MET` | Five limitations recorded (audit-only, retrospective time-split, single model class, three-family no-peek scope, LOO-vs-holdout characterization). |
| 5 | Engine version + git commit pinned | `MET` | `engine_version: 0.1.0`, `git_commit: ef12778...`. |
| 6 | Schema validation passes (`validate-repo --strict --fail-on-warnings`, 0 errors/0 warnings) | `NOT MET` | A calibration-audit result cannot currently be made schema-valid: it lacks `run_id`, a registered `experiment_id` + `hypothesis_id` for a *calibration-audit* result, the full eight-file `artifacts` block (`report`, `metrics`, `claim_update`, `claim_update_patch`, `knowledge_update`, `knowledge_update_patch`, `review_summary`, `review_metadata`), and one of the two `oneOf` payload shapes (here the `comparison_summary` + `uncertainty_summary` shape). |
| 7 | No protected-artifact rewrite | `MET` (conditional) | Holds only if `RESULT-0025` and `results/golden-results.yaml` stay untouched. This preflight touches neither. |
| 8 | No forbidden overclaim wording | `MET` | Negative/blocker framing only; no breakthrough, proof-style, unlimited-scope, discovery, future-prediction, or nuclear-law wording. |
| 9 | Dataset provenance valid | `MET` | Committed NMD-0003 training, frozen gate, and post-AME2020 holdout inputs with stable SHA-256 and no live fetch. |

**Headline:** Gate A is `BLOCKED`. Conditions 1, 4, 5, 8, 9 are met and 7 holds
conditionally, but conditions 2, 3, and 6 are not met, and they cannot be
satisfied without new packaging code plus a canonical experiment/hypothesis
identity for a calibration-audit result — work that exceeds this preflight's
no-tune, no-rerun, no-new-`AGENT-RUN` scope.

## Decisive blockers

1. **No schema-valid result-emitter for a calibration audit.** The committed
   command writes a sandbox audit (`agent_runs/AGENT-RUN-0089/metrics.json` and
   `report.md`), not a `results/.../result.yaml`. There is no committed path
   that emits a schema-valid negative `RESULT-*` for the calibration audit, and
   adding one is engine/tooling work.

2. **Verdict-vocabulary mismatch.** The audit's native verdict is not a
   `result.schema.json` `best_verdict`. A schema-valid negative result would be
   `INVALID` (per the `result-promotion-protocol.md` TASK-0432 caveat that the
   schema uses `INVALID`, not `FALSIFIED`); no artifact currently carries that.

3. **Experiment/hypothesis identity is scoped to the accuracy replay, not a
   calibration audit.** `EXP-0018` (`nmd0003-gp-extrapolation-replay`) and
   `HYP-0018` exist, but they back the extrapolation-*accuracy* replay
   (`RESULT-0025`), not a calibration-audit result. A calibration-audit
   `RESULT-*` would either need its own canonical experiment/hypothesis identity
   (does not exist) or would reuse `EXP-0018`/`HYP-0018` out of their scoped
   meaning.

4. **The calibration finding is already durable memory, and reusing
   `EXP-0018`/`HYP-0018` would largely duplicate `RESULT-0025`.** `RESULT-0025`
   already records the miscalibration as an `AGENT_PUBLISHED` PASS check
   (`uncertainty_miscalibration_recorded`) with the same holdout coverage
   (`0.823729` / `0.966102`) and RMS standardized residual (`2.826769`), and
   already lists heavy-tailed/miscalibrated uncertainty as a limitation. A new
   negative RESULT bound to the same identities would add little distinct
   scientific memory over `RESULT-0025` plus the source audit note, while
   consuming a new result identity.

## Recommendation

**`KEEP_REVIEW_NOTE_ONLY`.**

The negative/blocker finding is already preserved durably and honestly across
three surfaces: `agent_runs/AGENT-RUN-0089/` (the deterministic audit),
`docs/reviews/nmd0003-gp-uncertainty-calibration-audit.md` (the human-readable
audit note), and the `uncertainty_miscalibration_recorded` PASS check plus
limitation text inside `RESULT-0025`. `TASK-0827` stays blocked by that recorded
evidence regardless of whether a separate negative `RESULT-*` exists.

Packaging a *new* canonical negative `RESULT-*` today is blocked by Gate A
conditions 2, 3, and 6 and by the missing calibration-audit experiment/hypothesis
identity. Clearing those blockers is `NEEDS_ENGINE_WORK`-shaped, not something a
preflight (or an ad-hoc packaging step in this task) should force. Because the
finding is not being lost, the conservative and correct decision is to keep it as
review-note-plus-sandbox memory rather than create a thin, largely duplicative
RESULT under mismatched identities.

## Stop conditions

This preflight stops — creates no `RESULT-*` — because any of the following would
be required to proceed and each is out of scope here:

- writing new engine/packaging code to emit a schema-valid calibration-audit
  `result.yaml` (the audit only emits a sandbox `metrics.json` / `report.md`);
- re-expressing the native audit verdict as `best_verdict: INVALID` inside a new
  result artifact;
- registering a new canonical experiment + hypothesis identity for a
  calibration-audit result, or reusing `EXP-0018`/`HYP-0018` outside their
  extrapolation-accuracy scope;
- synthesizing the eight-file `artifacts` block and a `comparison_summary` +
  `uncertainty_summary` payload for a calibration audit;
- any tuning, rerun, or family re-selection of the frozen calibration config;
- any edit to `RESULT-0025`, `results/golden-results.yaml`, or the
  `TASK-0827` blocker.

If a source-version trigger (a new AME release, a different frozen baseline, or a
different GP model class) materially changes the residual surface and LOO
diagnostics, a fresh maintainer-approved task may revisit packaging.

## Future result-packaging task shape (advisory only)

Recorded for the maintainer as a possible follow-up; **not** proposed or created
by this task. It becomes actionable only if the maintainer decides the negative
calibration memory should exist as its own canonical `RESULT-*` rather than as
review-note-plus-`RESULT-0025` memory. Gate A prerequisites are only partially
clear (identity + emitter design are open), so this stays advisory:

- type: `scientific_result_publication` (negative/blocker), `NEEDS_ENGINE_WORK`.
- goal: emit a schema-valid `AGENT_PUBLISHED` negative `RESULT-*` for the
  NMD-0003 GP no-peek calibration failure with `best_verdict: INVALID`,
  preserving the failed conditions, heavy-tail ledger, and
  `unchanged_task_0827_remains_blocked` impact exactly.
- prerequisites: (a) a canonical experiment + hypothesis identity for a
  calibration-audit result, distinct from the `EXP-0018`/`HYP-0018` accuracy
  replay, or an explicit maintainer decision to reuse them; (b) a deterministic
  result-emitter that writes `results/.../result.yaml` plus the eight-file
  `artifacts` block from the frozen config and committed inputs; (c) a
  `comparison_summary` + `uncertainty_summary` payload mapping (e.g. observed vs
  nominal coverage and RMS standardized residual vs the calibrated target of
  `1.0`).
- guardrails: no calibration tuning or family re-selection; no `PRED`/`CLAIM`/
  `KNOW` creation; no `RESULT-0025` or golden-result edit; `TASK-0827` stays
  blocked; no breakthrough, proof-style, unlimited-scope, discovery,
  future-prediction, or nuclear-law wording.
- explicit non-duplication check: confirm the new RESULT adds distinct memory
  over `RESULT-0025`'s `uncertainty_miscalibration_recorded` check before
  creating it; if it would only restate `RESULT-0025`, keep the review-note-only
  decision.

## Output-routing summary

- Negative/blocker result preflight only; no RESULT/PRED/CLAIM/KNOW mutation.
- Task verdict: `KEEP_REVIEW_NOTE_ONLY` (treated as `not_applicable` for
  canonical promotion in this task).
- Canonical destination:
  `docs/reviews/nmd0003-calibration-failure-negative-result-preflight.md`.
- Review tier: `none`.
- Gate A: `BLOCKED` (conditions 2, 3, 6 not met; no schema-valid
  calibration-audit result-emitter and no calibration-audit experiment/hypothesis
  identity). Gate B: not attempted; the underlying finding is deterministic and
  replayable from committed inputs.
- Claim impact: no claim change. Knowledge impact: no knowledge change.
- Result impact: no `RESULT-*` created; `RESULT-0025` and
  `results/golden-results.yaml` untouched.
- Prediction-freeze impact: `unchanged_task_0827_remains_blocked`; `TASK-0827`
  stays blocked.
- Limitations / blockers: packaging requires new engine/tooling and a
  calibration-audit experiment/hypothesis identity; deferred to a future
  maintainer-approved task. No `agent_runs/AGENT-RUN-*` entry is created by this
  preflight.
