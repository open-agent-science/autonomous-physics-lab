# CLAIM-0009 Anharmonic Gate C Ratification Packet

Task: `TASK-0818`

Claim: `CLAIM-0009` (`DRAFT`)

Verdict: `CLAIM0009_GATEC_PACKET_READY_MAINTAINER_DECISION_REQUIRED`

## Scope

This packet prepares a narrow maintainer Gate C decision for
`CLAIM-0009`. It does not edit the claim file, change claim status, change
result metrics, create knowledge artifacts, or assert external replication.

The safe ceiling considered here is `PARTIALLY_SUPPORTED`, not `SUPPORTED`.
The evidence is range-limited to the configured conservative 1D quartic
oscillator benchmark and its weak/nonlinear slices.

## Evidence Chain

| Artifact | Path | Tier / status | Verdict | Role |
| --- | --- | --- | --- | --- |
| `CLAIM-0009` | `claims/CLAIM-0009-anharmonic-oscillator-period.md` | `DRAFT` | not applicable | Claim under maintainer review. |
| `RESULT-0014` | `results/EXP-0011/RUN-0001/result.yaml` | legacy canonical result | `VALID_IN_RANGE` | Original result currently cited by the claim. |
| `RESULT-0016` | `results/EXP-0011/RUN-0002/result.yaml` | `AGENT_VALIDATED` | `VALID_IN_RANGE` | Gate-B-validated successor evidence. |
| Gate B review | `docs/reviews/first-agent-validated-replay.md` | review note | `PASS` | Replayed `RESULT-0016`; 36 metrics, max absolute drift `0.0`, tolerance `1.0e-09`. |
| Evidence handoff | `docs/reviews/claim-0009-anharmonic-evidence-handoff.md` | review note | `not_applicable` | Prior evidence-to-wording mapping. |

## Benchmark Boundary

The evidence covers only:

- conservative 1D oscillator;
- potential `V(x) = 1/2 k x^2 + lambda x^4`;
- non-negative quartic coefficient `lambda`;
- train anharmonicity ratio `0.0008` to `0.0490`;
- predeclared holdout anharmonicity ratio `0.0512` to `0.1000`;
- stress boundary beginning at `0.1014`.

The evidence excludes softening/double-well potentials, damping, driving,
chaotic regimes, strong-anharmonic regimes, broad symbolic exactness, and any
universal anharmonic formula claim.

## Evidence Summary

`RESULT-0016` reports a deterministic period-integral benchmark with all
verification checks passing. The train-fitted empirical quadratic correction is
the best configured model on the holdout slice:

| Model | Train MRE | Holdout MRE | Holdout max RE | Verdict |
| --- | ---: | ---: | ---: | --- |
| Empirical quadratic | `2.34e-5` | `1.10e-3` | `3.20e-3` | `VALID` |
| Leading perturbative | `1.96e-3` | `1.85e-2` | `3.19e-2` | `PARTIALLY_VALID` |
| Harmonic baseline | `2.81e-2` | `1.04e-1` | `1.39e-1` | `OVERFITTED` |

The stress slice degrades as expected (`stress_mean_relative_error = 6.19e-2`,
`stress_max_relative_error = 1.13e-1`), so the claim must remain explicitly
weak-regime and configured-benchmark scoped.

## Recommended Maintainer Decision

Recommended ceiling: revise wording and move to `PARTIALLY_SUPPORTED`.

Reason: `RESULT-0016` is reproducible, Gate-B replayed, and in-scope
`VALID_IN_RANGE`; the claim can be phrased with the claim-promotion policy's
range-limited wording patterns. `SUPPORTED` is too strong because the evidence
is configured-slice and weak-regime only, with known out-of-range degradation.

Keep-DRAFT is still defensible if the maintainer wants a cross-tool replay,
external replication, or a claim-file evidence update reviewed separately.

## Narrow `PARTIALLY_SUPPORTED` Wording

Suggested maintainer-reviewed statement:

> On the configured conservative 1D quartic oscillator benchmark
> `V(x) = 1/2 k x^2 + lambda x^4` with `lambda >= 0`, the anharmonic period
> surface is partially supported on the configured benchmark: the leading
> perturbative correction is valid only within the tested weak range, and the
> fitted quadratic correction improves the predeclared holdout slice. This does
> not claim exactness, broad-range validity, or a universal anharmonic formula.

Suggested evidence update:

- keep `RESULT-0014`;
- add `RESULT-0016`;
- keep the scope tied to `EXP-0011` and `HYP-0011`.

## Keep-DRAFT Alternative

Suggested safe wording if no status transition is made:

> `CLAIM-0009` remains `DRAFT` pending maintainer Gate C review. `RESULT-0016`
> is `AGENT_VALIDATED` and supports a narrow configured-benchmark reading, but
> the claim file still needs maintainer wording review and an explicit
> `RESULT-0016` evidence link before any status transition.

## Patch-Style Appendix For Future Maintainer-Only Claim Update

This appendix is advisory. It is not applied by this task.

```diff
 status: DRAFT
+status: PARTIALLY_SUPPORTED
 evidence:
   experiments:
     - EXP-0011
   results:
     - RESULT-0014
+    - RESULT-0016
-scope: Benchmark-scoped support for weak-regime anharmonic oscillator period approximations under the configured quartic potential and holdout slices.
+scope: Partially supported on the configured conservative 1D quartic oscillator benchmark; valid only within the tested weak/nonlinear range and predeclared holdout/stress boundaries.
```

Suggested statement replacement:

```text
On the configured conservative 1D quartic oscillator benchmark
V(x) = 1/2 k x^2 + lambda x^4 with lambda >= 0, the anharmonic period surface
is partially supported on the configured benchmark: the leading perturbative
correction is valid only within the tested weak range, and the fitted
quadratic correction improves the predeclared holdout slice. This does not
claim exactness, broad-range validity, or a universal anharmonic formula.
```

## Blockers And Limitations

- Gate C is maintainer-only.
- `CLAIM-0009` currently cites `RESULT-0014`, not the Gate-B-validated
  `RESULT-0016`.
- Gate B replay is agent validation, not maintainer review or external
  replication.
- The original-publisher metadata warning from the Gate B helper remains part
  of the evidence record.
- Stress-slice degradation blocks any `SUPPORTED`, exactness, or broad-range
  wording.

## Output Routing

- Task verdict: `not_applicable` for benchmark validity; ratification-packet
  verdict `CLAIM0009_GATEC_PACKET_READY_MAINTAINER_DECISION_REQUIRED`.
- Canonical destination: `docs/reviews/claim-0009-anharmonic-gatec-ratification-packet.md`.
- Review tier: `none`; this packet references existing `AGENT_VALIDATED`
  `RESULT-0016`.
- Gate A: satisfied for `RESULT-0016` by prior task, not rerun here.
- Gate B: `PASS` for `RESULT-0016`, not rerun here.
- Claim impact: no mutation; maintainer-only `PARTIALLY_SUPPORTED` decision
  prepared.
- Knowledge impact: none.
- Result artifact impact: none.
