# Dimensional Validator Gate A Result Readiness

**Task:** `TASK-0689`  
**Surface:** Dimensional Analysis Validator live challenge set  
**Decision:** `GATE_A_BLOCKED_REMAINING_BOUNDARY_DISAGREEMENTS`  
**Review date:** 2026-06-10

## Scope

This review re-assesses whether the expanded live dimensional-analysis
challenge set clears **Gate A** for a new `AGENT_PUBLISHED` quality-gate
`RESULT-*` candidate after `TASK-0681` landed the boundary expansion from
`TASK-0661`.

It does not create a `RESULT-*`, modify `results/EXP-0006/RUN-0006`, add
claims, expand the challenge set further, or run new engine experiments beyond
replaying committed challenge-set verdicts.

Reviewed inputs:

- `docs/reviews/dimensional-validator-boundary-result-preflight.md` (`TASK-0661`)
- `docs/reviews/dimensional-validator-boundary-expansion.md` (`TASK-0681`)
- `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`
- `knowledge/challenge_sets/dimensional_analysis_challenge_set_mvp_50.yaml`
- `physics_lab/engines/dimensions.py`
- `tests/test_dimensions.py`
- `docs/result-promotion-protocol.md`
- `docs/campaigns/dimensional-analysis-validator.md`
- `docs/results/dimensional-analysis-validator-summary.md`

## Replay Performed

The committed live challenge set was replayed with the deterministic validator:

```bash
python3 -c 'from pathlib import Path; import yaml; from collections import Counter; from physics_lab.engines.dimensions import validate_challenge_set; path=Path("knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml"); data=yaml.safe_load(path.read_text(encoding="utf-8")); results, summary=validate_challenge_set(data); print("total", summary.total); print("agree", summary.agree); print("agreement_fraction", f"{summary.agreement_fraction:.6f}"); print("computed", {"VALID": summary.valid_count, "INVALID": summary.invalid_count, "SUSPICIOUS": summary.suspicious_count, "INCONCLUSIVE": summary.inconclusive_count}); print("expected", dict(Counter(str(i.get("expected_verdict")) for i in data.get("items", [])))); failures=[(r.item_id, r.expected_verdict, r.computed_verdict, r.detail) for r in results if not r.agrees]; print("failures"); [print(f) for f in failures]'
```

Replay environment:

- Python: `3.12.13` from `.venv/bin/python3`
- Challenge set: `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`
- Runner: `physics_lab.engines.dimensions.validate_challenge_set`

## Post-Expansion Metrics

| Metric | Pre-expansion (`TASK-0661`) | Post-expansion (this review) |
| --- | ---: | ---: |
| Live challenge items | `70` | `74` |
| Agreement | `65/70` | `71/74` |
| Agreement fraction | `0.928571` | `0.959459` |
| Computed `INCONCLUSIVE` | `1` | `0` |
| Remaining disagreements | `5` | `3` |

The expansion removed two preflight blockers and added four curated boundary
items without introducing new inconclusive results:

| Item | Pre-expansion | Post-expansion | Status |
| --- | --- | --- | --- |
| `DA-011` Snell's law textbook identity | `VALID` vs `SUSPICIOUS` | `VALID` vs `VALID` | **resolved** via `dimensionless_relation_policy: accepted_textbook_identity` |
| `DA-407` large-angle pendulum with `pi` | `KNOWN_LIMIT_FAIL` vs `INCONCLUSIVE` | `KNOWN_LIMIT_FAIL` vs `VALID` | **resolved** via built-in `pi` constant |
| `DA-022` circle circumference with `pi` | n/a | agrees | **added and passing** |
| `DA-023` small-angle pendulum with `pi` | n/a | agrees | **added and passing** |
| `DA-312` Snell normalized ratio | n/a | agrees | **added and passing** |
| `DA-408` Lorentz `beta > 1` | n/a | agrees via relaxed known-limit rule | **added and passing** |
| `DA-310` incompatible ratio product | `SUSPICIOUS` vs `VALID` | unchanged | **still blocked** |
| `DA-311` undamped spring missing `2pi` | `SUSPICIOUS` vs `VALID` | unchanged | **still blocked** |
| `DA-406` refractive index below unity | `KNOWN_LIMIT_FAIL` vs `SUSPICIOUS` | unchanged | **still blocked** |

## Gate A Assessment

Gate A in `docs/result-promotion-protocol.md` is the mechanical publication
gate for new `AGENT_PUBLISHED` `RESULT-*` artifacts. This task asks whether
the **expanded live curation surface** is now ready to support such a
quality-gate result, not whether the frozen MVP can be replayed again.

### What improved

- Live agreement rose from `92.9%` to `95.9%`.
- The `pi` parsing blocker and all-dimensionless textbook over-flagging that
  `TASK-0661` singled out are now handled on committed items.
- Repository tests still pass the live-set thresholds in
  `tests/test_dimensions.py` (`≥90%` agreement, `≤1` inconclusive).

### Why Gate A remains blocked

1. **Three curated boundary disagreements remain** on the exact semantic and
   known-limit classes the preflight said must be handled before promoting the
   live surface as a reusable public quality gate.
2. **`DA-406` exposes a known-limit/dimensionless interaction gap.** Other
   known-limit items can agree when the dimensional pass returns `VALID`, but
   all-dimensionless known-limit formulas still fall into the suspicious
   heuristic unless separately curated.
3. **`DA-310` and `DA-311` remain documented MVP-limit cases.** The frozen
   `RESULT-0007` summary already records the semantically-empty dimensionless
   ratio class as outside MVP scope; the live surface still fails to classify
   those curated `SUSPICIOUS` labels.
4. **Campaign policy still separates live curation from canonical results.**
   `docs/campaigns/dimensional-analysis-validator.md` states that follow-on
   challenge entries are curation work until a future benchmark task
   intentionally rebaselines them. Gate A publication of a new live-surface
   `RESULT-*` would therefore need both mechanical readiness and an explicit
   rebaseline decision; the boundary disagreements block the readiness half.

### Conservative interpretation

A dimensional-consistency gate is a formula-quality preflight, not numerical
or empirical validation of physics. Publishing a new live-surface quality-gate
result at `95.9%` while three boundary-curated items still disagree would
overstate reusable coverage relative to the committed challenge labels.

## Decision

`GATE_A_BLOCKED_REMAINING_BOUNDARY_DISAGREEMENTS`

Do **not** create a new `AGENT_PUBLISHED` quality-gate `RESULT-*` from the
current live 74-item surface in this pass.

Preserve `RESULT-0007` / `EXP-0006/RUN-0006` as the frozen 50-item MVP
canonical benchmark. Continue using the live challenge set as a deterministic
local preflight surface only.

## If Gate A Were Ready Later

A future approved rebaseline task could publish a successor result with this
shape:

| Field | Proposed value |
| --- | --- |
| Experiment / run | new run under `EXP-0006` or successor experiment id |
| Input snapshot | checksum-pinned copy of `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml` at publish commit |
| Command | deterministic `validate_challenge_set` replay via committed CLI/workflow entrypoint |
| Metrics artifact | agreement fraction, per-verdict counts, explicit disagreement table |
| `best_verdict` | `VALID_IN_RANGE` or `PARTIALLY_VALID`, not a physics-truth claim |
| `review_tier` | `AGENT_PUBLISHED` at Gate A; `AGENT_VALIDATED` only after independent Gate B replay |
| Limitations | must list any remaining semantic-suspicion or known-limit classes outside engine scope |

This task does **not** authorize creating that artifact now.

## Smallest Unblock Path

Recommended single follow-up task:

**Targeted semantic-suspicion and known-limit dimensionless handling for
`DA-310`, `DA-311`, and `DA-406`.**

Minimum scope:

1. Add an explicit curated metadata path for semantically suspicious but
   dimensionally balanced formulas (`failure_mode: physically_meaningless`,
   missing dimensionless factor such as `2pi`) so the engine can emit
   `SUSPICIOUS` instead of `VALID` on `DA-310` and `DA-311`.
2. Teach the validator to honor `check_type: known_limit` on
   all-dimensionless formulas such as `DA-406` without auto-downgrading them
   to generic suspicious heuristics when the curated label is
   `KNOWN_LIMIT_FAIL`.
3. Re-run the live challenge-set replay and only then reopen Gate A readiness
   for a rebaselined benchmark result task.

Do not solve this by silently loosening `_agrees()` without engine support;
that would preserve metrics while hiding the boundary behavior the challenge
set is trying to curate.

## Limitations

- Deterministic dimensional replay only; no empirical data or natural-unit
  support beyond committed constants.
- No semantic row-class validation for Nuclear, Materials, Exoplanet, Quantum,
  Atomic, or Textbook campaign surfaces.
- No maintainer endorsement of a reusable public quality gate in this review.
- Gate B independent replay was not attempted because no new `RESULT-*` was
  published.

## Output Routing

- Task verdict: `GATE_A_BLOCKED_REMAINING_BOUNDARY_DISAGREEMENTS`.
- Canonical destination:
  `docs/reviews/dimensional-validator-gate-a-result-readiness.md`.
- Review tier: `none`.
- Gate A status: **blocked** for a new live-surface quality-gate `RESULT-*`.
- Gate B status: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result impact: no `results/` artifact created or modified.
- Publication blocker: three curated boundary disagreements remain
  (`DA-310`, `DA-311`, `DA-406`); intentional MVP/live rebaseline decision
  still required before Gate A publication.
