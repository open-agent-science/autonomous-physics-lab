# CLAIM-0007 Particle-Mass Falsifier Evidence Handoff

- Task: `TASK-0784`
- Claim: `CLAIM-0007`
- Claim artifact: `claims/CLAIM-0007-particle-mass-falsifier-mvp.md`
- Primary evidence: `RESULT-0011`
- Campaign summary: `docs/results/koide-campaign-summary.md`
- Decision lane: maintainer Gate C review
- Handoff verdict: `MAINTAINER_DECISION_NEEDED`

## Scope

This handoff maps the existing particle-mass falsifier evidence to the wording
of `CLAIM-0007`. It does not change the claim, result, knowledge, or golden
result registries; rerun the falsifier; introduce a new formula family; or
authorize a broad particle-mass search.

`CLAIM-0007` is currently `DRAFT`. The evidence supports a narrow statement
about the fixed standard Koide target under the exact encoded charged-fermion
family survey. It does not support a scheme-independent quark conclusion, a
general statement about all Koide-like relations, or an explanation of
particle-mass generation.

## Evidence Map

| Evidence surface | Stored outcome | What it supports | Boundary |
| --- | --- | --- | --- |
| `RESULT-0011`, charged leptons | `Q = 0.6666644634145`; gap `0.43 sigma`; family verdict `VALID` | The stored charged-lepton pole-mass triplet remains compatible with the fixed `2/3` target under first-order propagated uncertainty. | Reproduction in one explicit dataset, not explanation or cross-family generalization. |
| `RESULT-0011`, up-type quarks | `Q = 0.8489807776610612`; gap `159.16 sigma`; family verdict `INVALID` | The encoded up-quark triplet does not meet the fixed target under the stored inputs. | Inputs mix `MS-bar` running masses at different scales with a direct top-mass measurement. |
| `RESULT-0011`, down-type quarks | `Q = 0.7314967575627492`; gap `8.84 sigma`; family verdict `INVALID` | The encoded down-quark triplet does not meet the fixed target under the stored inputs. | The `d`, `s`, and `b` running masses are not all evaluated at one common scale. |
| `RESULT-0011`, global verification | Verification passed; global verdict `INVALID` | At least one of the predeclared within-family charged-fermion triplets fails the same fixed target outside propagated uncertainty; both quark families fail. | The global verdict is benchmark-scoped and inherits every source, scheme, scale, and model limitation below. |
| `RESULT-0005` and `RESULT-0006` | Charged-lepton reproduction and historical tau holdout reproduce in scope. | The charged-lepton success is a real repository benchmark surface that should remain visible in the claim interpretation. | Neither result establishes a mechanism or predicts survival in another particle family. |
| `RESULT-0009` and `RESULT-0010` | Direct neutrino and tested quark extensions are `INVALID` in scope. | The broader campaign consistently rejects simple unmodified extension of the charged-lepton target under the tested assumptions. | These runs test different datasets and bounded relation families; they do not close all modified Koide-like constructions. |

## CLAIM-0007 Wording Map

### Supported As Written

The following parts of the current statement are supported by `RESULT-0011`:

- the target is fixed to the standard `Q = 2/3`;
- the survey is limited to the encoded charged-lepton, up-quark, and
  down-quark within-family triplets;
- the charged-lepton triplet is within propagated uncertainty;
- the encoded up-type and down-type quark triplets miss the target outside
  propagated uncertainty;
- the conclusion is explicitly tied to the stored falsifier MVP.

### Supported Only With Narrow Interpretation

The title phrase "fails cross-family survival" is acceptable only when read as
"the same fixed target does not survive across all three encoded within-family
surfaces." The experiment does not evaluate arbitrary cross-family triplets,
all fermion sectors, or every mass convention.

The phrase "charged-fermion family survey" must remain tied to the three stored
triplets. It must not be shortened to "particle families" without the encoded
scope and quark-input limitations.

### Unsupported

The evidence does not support wording that:

- declares the standard Koide relation globally false;
- rules out every phase extension, alternate target, exponent, common-scale
  quark reformulation, or other modified relation;
- says only charged leptons can satisfy any Koide-like relation;
- treats the mixed-scale quark result as invariant under renormalization scheme
  or scale;
- claims that APL explained, derived, or accounted for particle-mass
  generation;
- treats numerical closeness or falsification alone as evidence of a physical
  mechanism;
- generalizes from three encoded triplets to all particles or all eligible
  triplet selections.

### Too Broad Or Ambiguous

Avoid unqualified phrases such as:

- "Koide fails for quarks";
- "Koide works only for charged leptons";
- "the particle-mass relation is falsified";
- "cross-family universality is disproved";
- "particle-mass numerology is settled."

A maintainer revision should prefer:

> In `RESULT-0011`, the fixed standard Koide target does not survive all three
> encoded within-family charged-fermion triplets: the charged-lepton triplet is
> within propagated uncertainty, while the stored mixed-scheme/scale up- and
> down-quark triplets are outside it.

That wording preserves the observed result and exposes the main quark-data
limitation in the claim statement itself.

## Limitation Ledger

### Source

- Charged leptons use stored PDG 2025 update pole masses.
- Quarks use stored PDG 2024 values.
- The canonical run records hashes for its frozen input files, including the
  dataset snapshot.
- The result is therefore reproducible against the repository snapshot, but
  the campaign combines editions and should not be described as one uniform
  external measurement campaign.

### Mass Definition, Scheme, And Scale

- Charged-lepton inputs are pole masses with no running scale.
- The up and charm masses are `MS-bar` running masses at `2 GeV` and `mc(mc)`;
  the top input is a direct collider measurement.
- The down and strange masses are `MS-bar` at `2 GeV`; the bottom mass is
  `MS-bar` at `mb(mb)`.
- No renormalization-group evolution places the quark inputs at a common scale.
- This is the principal blocker to scheme-independent or universal quark
  wording. It does not erase the stored benchmark result.

### Uncertainty

- The run applies first-order uncertainty propagation to `Q`.
- Asymmetric source uncertainties are collapsed to the larger side before
  propagation, which is conservative but not a full distributional treatment.
- The `159.16 sigma` and `8.84 sigma` gaps are large relative to the propagated
  input uncertainties in the encoded snapshot.
- Those sigma values do not quantify uncertainty from choosing a mass scheme,
  renormalization scale, dataset edition, or model family.

### Random Baseline

- Each family is compared with `10,000` deterministic log-uniform random
  triplets using fixed seeds.
- For charged leptons, none of the sampled triplets landed within the observed
  target gap.
- For up and down quarks, `57.62%` and `17.32%` of random triplets,
  respectively, landed within their much larger observed gaps.
- This baseline calibrates accidental numerical closeness only. It is not a
  physical prior, a particle-generation model, or evidence for the target.

### Complexity Penalty

- The fixed standard relation receives total complexity penalty `1.0`, with
  structural flexibility as the only non-zero ledger component.
- No fitted parameters, tuned exponents, arbitrary constants, cross-family
  mixing, or post hoc prediction are charged in this predeclared MVP.
- This low penalty supports treating the failure as a clean falsifier of the
  fixed target in scope. It does not compare a wider family of modified
  formulas or authorize a new search.

## Maintainer-Only Decision Options

1. **Keep `CLAIM-0007` as `DRAFT`.**

   This is the conservative choice while the numerology-adjacent campaign and
   mixed-scheme/scale quark inputs remain unresolved.

2. **Tighten the wording and keep `DRAFT`.**

   Replace ambiguous "cross-family" language with the explicit three-triplet
   survey wording above and put the mixed-scheme/scale quark limitation in the
   statement, without changing status.

3. **Request independent replay or a common-scale quark follow-up.**

   A Gate B replay can establish deterministic reproducibility under the same
   inputs. A separate common-scale source/benchmark task would address the
   stronger physics limitation. Neither step should reopen broad formula
   search.

4. **Move to `PARTIALLY_SUPPORTED` after maintainer Gate C review.**

   This is defensible only for a tightly scoped negative claim about the stored
   benchmark. The maintainer should first confirm that the wording cannot be
   read as scheme-independent or as a global Koide falsification.

`SUPPORTED` is not recommended because the evidence is benchmark-limited and
the quark comparison is scheme/scale-sensitive. `REFUTED` is not applicable:
the referenced result supports, rather than contradicts, the negative claim.

## Recommended Maintainer Path

Tighten the wording and keep `CLAIM-0007` as `DRAFT` until either an independent
replay is recorded or the maintainer explicitly accepts the current
mixed-scheme/scale benchmark as sufficient for a narrow
`PARTIALLY_SUPPORTED` status. Do not require a broad formula search; it would
increase numerology risk without resolving the present claim boundary.

## Output Routing

- Task verdict: `not_applicable` for new science; this task is an evidence
  handoff with decision verdict `MAINTAINER_DECISION_NEEDED`.
- Canonical destination:
  `docs/reviews/claim-0007-particle-mass-falsifier-evidence-handoff.md`.
- Referenced artifact tier: `RESULT-0011` is `LEGACY_UNTIERED`; it predates the
  explicit multi-tier result-promotion fields.
- Gate A: not retrospectively recorded under the current protocol. The stored
  result has deterministic inputs, hashes, verification pass, limitations,
  and a canonical `INVALID` verdict, but no `agent_proposal_evaluation` block.
- Gate B: not attempted for `RESULT-0011`.
- Gate C: maintainer decision required for any `CLAIM-0007` wording or status
  change.
- Claim impact: none; `CLAIM-0007` remains unchanged and `DRAFT`.
- Knowledge impact: none.
- Result and golden-result impact: none.
- Publication blockers: maintainer Gate C review, numerology-adjacent domain
  risk, mixed quark mass definitions/scales, and no independent Gate B replay.
