# Dimensional Validator Gate A Replay Decision

**Task:** `TASK-0744`
**Surface:** Dimensional Analysis Validator live challenge set
**Decision:** `GATE_A_REPLAY_PASS_RESULT_PUBLICATION_DEFERRED`

## Scope

This task reruns the narrow Dimensional Validator publication-gate replay after
the `TASK-0712` boundary fix. It decides whether the live 74-item challenge set
is mechanically ready for a future Gate A result artifact, while preserving the
campaign boundary that dimensional agreement is a formula-quality preflight and
not a physics-discovery claim.

No canonical `RESULT-*`, claim, prediction, or knowledge artifact is created in
this PR. `TASK-0744` allows a result candidate only if Gate A passes and
maintainer approval allows the packaging. This review records the replay
decision and defers result packaging to maintainer-approved follow-up.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `TASK-0712` | Boundary-fix prerequisite; status is `DONE`. |
| `docs/reviews/dimensional-validator-boundary-disagreement-fix.md` | Documents the targeted fixes for `DA-310`, `DA-311`, and `DA-406`. |
| `docs/reviews/dimensional-validator-gate-a-result-readiness.md` | Prior Gate A review that blocked publication at 71/74 agreement. |
| `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml` | Live 74-item challenge-set replay target. |
| `physics_lab/engines/dimensions.py` | Deterministic validator implementation. |
| `tests/test_dimensions.py` | Targeted regression and live replay tests. |
| `results/EXP-0006/RUN-0006/result.yaml` | Frozen `RESULT-0007` MVP benchmark, preserved unchanged. |
| `docs/result-promotion-protocol.md` | Gate A / Gate B routing policy. |

## Replay Performed

The live challenge set was replayed with the committed deterministic validator:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; import yaml; from collections import Counter; from physics_lab.engines.dimensions import validate_challenge_set; path=Path('knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml'); data=yaml.safe_load(path.read_text(encoding='utf-8')); results, summary=validate_challenge_set(data); print('total', summary.total); print('agree', summary.agree); print('agreement_fraction', f'{summary.agreement_fraction:.6f}'); print('computed', {'VALID': summary.valid_count, 'INVALID': summary.invalid_count, 'SUSPICIOUS': summary.suspicious_count, 'INCONCLUSIVE': summary.inconclusive_count}); print('expected', dict(Counter(str(i.get('expected_verdict')) for i in data.get('items', [])))); failures=[(r.item_id, r.expected_verdict, r.computed_verdict, r.detail) for r in results if not r.agrees]; print('failures', failures)"
```

Replay output:

```text
total 74
agree 74
agreement_fraction 1.000000
computed {'VALID': 37, 'INVALID': 35, 'SUSPICIOUS': 2, 'INCONCLUSIVE': 0}
expected {'VALID': 29, 'INVALID': 33, 'SUSPICIOUS': 4, 'KNOWN_LIMIT_FAIL': 8}
failures []
```

Targeted validator tests were also run with a Windows-safe temp directory:

```powershell
.\.venv\Scripts\python.exe -m pytest -n0 tests\test_dimensions.py --basetemp C:\tmp\apl-pytest-task0744
```

Result:

```text
31 passed
```

Additional local validation:

- `ruff check .`: pass.
- `validate-repo . --strict --fail-on-warnings`: pass with informational
  repository-background notes only.
- CI-fast-equivalent targeted suite plus `tests/test_dimensions.py`: `84 passed`.
- Full local `pytest` on this Windows checkout was attempted but not used as the
  decisive gate: the xdist run hit worker crashes after most tests had passed,
  and the serial full-suite rerun exceeded the local timeout. The PR therefore
  relies on targeted deterministic replay, targeted dimensional tests, strict
  repository validation, and GitHub CI for broad regression coverage.

## Comparison To Prior Gate

| Metric | Prior Gate A review (`TASK-0689`) | After boundary fix (`TASK-0744`) |
| --- | ---: | ---: |
| Live challenge items | `74` | `74` |
| Agreement | `71/74` | `74/74` |
| Agreement fraction | `0.959459` | `1.000000` |
| Computed `INCONCLUSIVE` | `0` | `0` |
| Remaining disagreements | `3` | `0` |

The three prior blockers are resolved:

| Item | Prior state | Replay state |
| --- | --- | --- |
| `DA-310` | expected `SUSPICIOUS`, computed `VALID` | agrees |
| `DA-311` | expected `SUSPICIOUS`, computed `VALID` | agrees |
| `DA-406` | expected `KNOWN_LIMIT_FAIL`, computed `SUSPICIOUS` | agrees under dimension-only known-limit handling |

## Gate A Decision

The live 74-item Dimensional Validator challenge set is mechanically ready for a
future scoped Gate A result candidate:

- deterministic replay is complete;
- agreement is `74/74`;
- there are no remaining disagreements;
- there are no inconclusive items;
- targeted regression tests pass;
- the decision preserves the frozen `RESULT-0007` MVP benchmark unchanged.

However, this PR does **not** publish a new `RESULT-*` artifact. The publication
step should be a maintainer-approved result-packaging task that snapshots the
live challenge-set input, assigns a new run/result identity, records hashes, and
passes the repository Gate A checker for the concrete artifact.

## Publication Recommendation

Recommended next step:

```text
Package a new scoped AGENT_PUBLISHED Dimensional Validator live-surface result
candidate from the 74-item replay, preserving the limitation that dimensional
agreement is formula-quality evidence only.
```

Suggested artifact posture for that follow-up:

| Field | Recommended value |
| --- | --- |
| Result scope | live 74-item dimensional challenge-set rebaseline |
| Verdict | `VALID` for deterministic agreement with curated labels |
| Review tier | `AGENT_PUBLISHED` only if Gate A checker passes |
| Gate A | candidate ready, not yet applied to a committed artifact |
| Gate B | not attempted |
| Claim impact | no automatic claim promotion |
| Knowledge impact | no automatic knowledge entry |

## Limitations

- Dimensional consistency remains a formula-quality preflight, not a proof of
  physical truth, numerical validity, or empirical correctness.
- Known-limit rows that agree under the dimensional check still record that the
  validator does not decide the numerical or regime-limit question.
- The live 74-item challenge set should not silently rewrite frozen
  `RESULT-0007`; any result publication needs a new result identity and input
  snapshot.
- Natural-unit and Gaussian-unit formulas remain outside the SI-focused
  benchmark scope unless a future task explicitly expands the unit system.
- Gate B independent replay is not attempted because no new result artifact is
  published here.

## Output Routing

- **Task verdict:** `VALID` as a replay/publication decision.
- **Canonical destination:** this review note,
  `docs/reviews/dimensional-validator-gate-a-replay-decision.md`.
- **Review tier:** `none`; no `RESULT-*` artifact is created.
- **Gate A status:** replay passes mechanically; artifact publication deferred.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** maintainer-approved result packaging is still needed
  before a new `AGENT_PUBLISHED` artifact exists.
