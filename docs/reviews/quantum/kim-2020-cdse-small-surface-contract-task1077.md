# Kim-2020 CdSe Small-Surface Contract Decision

Task: `TASK-1077`
Contract: `data/quantum_dots/kim2020_cdse_small_surface_benchmark_contract.yaml`

## Verdict

`HOLD_UNDERPOWERED`

No model or validator was run. The current surface has exactly four
source-matched sample groups on the absorption axis and the same four groups on
the emission axis. That is insufficient for the required deletion-stability
test.

## Metadata Reverification

Both curated datasets preserve the frozen source semantics:

| Field | Absorption | Emission |
| --- | --- | --- |
| Dataset | `qd-0005` | `qd-0006` |
| Property axis | `absorption_peak_eV` | `emission_peak_eV` |
| Included groups | 4 | 4 |
| Provenance | `text_stated_summary` | `text_stated_summary` |
| Printed precision | 0.01 eV | 0.01 eV |
| Rounding floor | 0.005 eV | 0.005 eV |
| Morphology | `unknown_non_spherical` | `unknown_non_spherical` |
| Instrument uncertainty | `not_reported` | `not_reported` |

The axes remain separate. No pooled residual metric or equivalent-sphere
conversion is allowed. The excluded figure-digitization coordinates remain
excluded.

## Structural Information Check

The only frozen physics-motivated family is an affine inverse-square size form,
fit separately on each axis with two parameters. The controls are a train mean
and a same-complexity affine diameter trend. These controls are necessary to
ask whether a future diagnostic adds information beyond a monotonic plot.

The frozen sensitivity procedure first removes one sample group and then
recomputes grouped leave-one-out errors. Starting from four groups:

- outer deletion leaves 3 groups;
- an inner leave-one-out fold trains on 2 groups;
- the candidate has 2 parameters;
- the inner fit therefore has 0 residual degrees of freedom.

Any apparent deletion-stable comparison would be driven by exactly determined
fits, not by enough independent groups to evaluate residual behavior. Missing
instrument uncertainty makes a threshold-adjacent interpretation weaker still.

The contract therefore requires at least eight groups per property axis. After
one outer deletion and one inner holdout, six groups remain for training, which
leaves four residual degrees of freedom for the two-parameter candidate. This
is a structural admission floor, not a post-hoc power claim.

## Frozen Future Routing

If a later source expansion clears the information and uncertainty gates, each
axis must be judged independently. A PASS requires the candidate to beat both
nulls by more than 0.01 eV in the full surface and every deletion surface,
without worse maximum error. A FAIL requires both controls to beat the
candidate by that margin throughout. All mixed, unstable, threshold-adjacent,
or uncertainty-unresolved outcomes route to INCONCLUSIVE.

No score may be computed under this task, and the frozen thresholds cannot be
changed after outcomes become visible.

## Scope And Limitations

This decision concerns one four-sample, text-reported CdSe surface. It does not
test a quantum-confinement law, establish a material-design rule, or change
`RESULT-0029`. The group floor is a conservative contract criterion; it is not
a guarantee that eight future groups will provide adequate statistical power.

## Output Routing

- Canonical destination: the non-executable benchmark contract and this review
  note.
- Benchmark readiness: `HOLD_UNDERPOWERED`; no execution task is implied.
- Gate A: not attempted.
- Gate B: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: at least eight source-matched groups per axis plus
  reported instrument uncertainty or a reviewed, predeclared uncertainty
  envelope.
