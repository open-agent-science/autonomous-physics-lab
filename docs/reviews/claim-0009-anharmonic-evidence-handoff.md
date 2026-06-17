# CLAIM-0009 Anharmonic Evidence Handoff

- Task: `TASK-0758`
- Campaign: `anharmonic_oscillator`
- Claim: [`CLAIM-0009`](../../claims/CLAIM-0009-anharmonic-oscillator-period.md) (`status: DRAFT`)
- Hypothesis: `HYP-0011`; Experiment: `EXP-0011`
- Mode: maintainer-facing evidence handoff — **no claim-status change**
- Verdict: `not_applicable` (evidence assembly only)

## Scope

This note assembles the reviewable evidence for `CLAIM-0009` and maps it to the
current claim wording so a maintainer can make a claim-status decision. It does
**not** edit `CLAIM-0009` status, change benchmark metrics, create knowledge
artifacts, assert external replication, or promote the claim. Per
[`claim-promotion-policy.md`](../claim-promotion-policy.md), all `CLAIM-*`
status transitions remain maintainer-only in Phase 1.

## Evidence Chain

| Object | Run | Tier | Verdict | Role |
| --- | --- | --- | --- | ---: |
| `RESULT-0014` | `EXP-0011/RUN-0001` (`TASK-0159`) | canonical Gate A benchmark | `VALID_IN_RANGE` | original benchmark run currently cited by the claim |
| `RESULT-0016` | [`EXP-0011/RUN-0002`](../../results/EXP-0011/RUN-0002/result.yaml) (`TASK-0412`) | `AGENT_VALIDATED` | `VALID_IN_RANGE` | Gate-B-validated successor benchmark |

- **Gate A:** satisfied for `RESULT-0016` by `TASK-0412` packaging.
- **Gate B:** `PASS` — first AGENT_VALIDATED replay (`TASK-0415`,
  [`first-agent-validated-replay.md`](first-agent-validated-replay.md)): 36
  numeric metrics compared, maximum absolute drift `0.0`, tolerance `1.0e-09`,
  verdict unchanged `VALID_IN_RANGE`.
- **Replay command:**
  `python3 scripts/apl_validate_agent_published_result.py results/EXP-0011/RUN-0002/result.yaml --output-dir <tmp> --json`
  (recorded run command: `physics-lab run examples/anharmonic_agent_published_result.yaml`).
- **Gate B caveat preserved:** the helper emitted `original-publisher-unknown`
  (no original-publisher metadata stored on `RESULT-0016`), so the replay
  identity is recorded but original vs validating agents cannot be mechanically
  compared. This is single-contributor agent validation, not external
  replication.

## Benchmark Metrics (RESULT-0016)

Scope: conservative 1D quartic oscillator `V(x) = ½ k x² + λ x⁴`, `λ ≥ 0`.
Anharmonicity parameter `ε = λ A² / k`. Train range `ε ∈ [0.0008, 0.049]`;
predeclared holdout `ε ∈ [0.0512, 0.1]`.

| Model | Formula | Train MRE | Holdout MRE | Holdout max RE | Complexity | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `model_empirical_quadratic` (best) | `T = T0(1 + a·ε + b·ε²)` | `2.34e-5` | `1.10e-3` | `3.20e-3` | 2 | `VALID` |
| `model_perturbative_leading` | `T = T0(1 − 3/2·ε)` | `1.96e-3` | `1.85e-2` | `3.19e-2` | 1 | `PARTIALLY_VALID` |
| `model_harmonic` (baseline) | `T = 2π√(m/k)` | `2.81e-2` | `1.04e-1` | `1.39e-1` | 1 | `OVERFITTED` |

Out-of-range stress slice degrades as expected (stress MRE `6.19e-2`, max
`1.13e-1`), confirming the weak-regime boundary.

## Evidence-to-Wording Mapping

Current claim statement: *"The conservative quartic anharmonic oscillator admits
a useful benchmark surface where a leading-order perturbative period correction
is accurate in a weak regime and where higher-order empirical corrections can be
compared on a predeclared holdout slice."*

| Claim wording | Status vs evidence |
| --- | --- |
| benchmark surface for `V = ½kx² + λx⁴`, `λ ≥ 0`, configured slices | **Supportable** — matches `RESULT-0016` scope and limitations exactly. |
| leading-order perturbative correction "accurate in a weak regime" | **Supportable but needs an explicit range qualifier.** `model_perturbative_leading` is `PARTIALLY_VALID`: train MRE `1.96e-3` but holdout MRE rises to `1.85e-2`. The bare word "accurate" should read "accurate only within the tested weak range." |
| higher-order empirical corrections "compared on a predeclared holdout slice" | **Supportable** — `model_empirical_quadratic` is `VALID` on the predeclared holdout (MRE `1.10e-3`). |
| (implicit) anything beyond weak regime / driven / damped / chaotic / strong-anharmonic / universal law | **Too broad — not supported.** The claim already cautions against this; the stress slice confirms out-of-range degradation. |

**Evidence-linkage gap (for maintainer action):** `CLAIM-0009` currently lists
`RESULT-0014` only, but the Gate-B-validated evidence object is `RESULT-0016`.
The claim-promotion policy requires `CLAIM-*` to reference concrete `RESULT-*`
ids and to remain limited by the weakest relevant scope. A maintainer may want
to add `RESULT-0016` to the claim evidence list. This handoff does **not** edit
the claim.

## Maintainer Decision Options

Per [`claim-promotion-policy.md`](../claim-promotion-policy.md) (maintainer-only):

1. **Leave `DRAFT`.** Lowest-risk; appropriate if the wording review is not yet
   done or if single-contributor Gate B validation is considered insufficient.
2. **Revise wording, then `PARTIALLY_SUPPORTED`.** Best-evidence-matched option:
   add the explicit range qualifier to "accurate", link `RESULT-0016`, and use
   required patterns ("valid only within the tested range", "supported on the
   configured benchmark"). The evidence (reproducible `RESULT-0016`, in-scope
   Gate B pass, range-limited with known out-of-scope failures) fits the
   `PARTIALLY_SUPPORTED` criteria.
3. **Request more evidence before promotion.** E.g. independent cross-tool or
   external replication beyond the single-contributor Gate B, or a finer holdout.
4. **`SUPPORTED`** is **not** justified now: the support is range-limited with
   known out-of-scope failures, validation is single-contributor
   (`original-publisher-unknown`), and the wording has not had maintainer review.

Recommendation framing (advisory, non-binding): option 2 is the best
evidence-matched path, but the policy's "prefer under-claiming" rule means
staying at `DRAFT` (option 1) is fully defensible until wording review and the
`RESULT-0016` evidence link are settled.

## Output Routing Summary

- Task verdict: `not_applicable` (evidence handoff; no metric or status change).
- Canonical destination: `docs/reviews/claim-0009-anharmonic-evidence-handoff.md`.
- Review tier: `none` (references existing `AGENT_VALIDATED` `RESULT-0016`).
- Gate A status: satisfied for `RESULT-0016` (`TASK-0412`).
- Gate B status: `PASS` (`TASK-0415`, single-contributor; not external replication).
- Claim impact: none; `CLAIM-0009` stays `DRAFT`. A maintainer-only decision is
  requested, with `PARTIALLY_SUPPORTED` as the best evidence-matched ceiling.
- Knowledge impact: none.
- Result artifact impact: none; no `results/` artifact changed.
- Limitations / blockers: maintainer review required for any status change;
  evidence-linkage gap (`RESULT-0014` cited vs `RESULT-0016` validated); Gate B
  is single-contributor with `original-publisher-unknown`; support is
  weak-regime range-limited only.
