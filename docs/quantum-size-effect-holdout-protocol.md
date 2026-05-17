# Quantum Size Effect Holdout Protocol

## Purpose

This protocol defines how the Quantum Size Effects campaign splits curated
measurement data for holdout evaluation before any candidate model or
correction term is scored.

The goal is to distinguish:

- interpolation within a known size regime and material;
- generalization across materials and composition families;
- source or publication transfer across independent measurement labs;
- size-range extrapolation beyond the training distribution.

This protocol is upstream of `TASK-0225` (baseline residual benchmark). No
holdout target should be inspected before the benchmark is defined and its
pre-reveal package is committed.

## Scope

The protocol applies to future quantum-dot size-effect benchmarks,
correction-hypothesis experiments, and sandbox autonomous pilots under
`campaign_profiles/quantum-size-effects.yaml` (when that profile exists).

It is intended for:

- conservative effective-mass baseline comparisons;
- compact size-scaling corrections with explicit material applicability flags;
- residual structure exploration across materials, size regimes, and sources;
- negative-control candidates that should fail under structured holdout.

It is not a license to claim a universal quantum-dot design law, to support
synthesis or fabrication guidance, or to make biomedical or device-performance
claims.

## Property Kind Separation Policy

Absorption peak, emission peak, and bandgap values are **never combined on a
single residual axis**. This is a hard rule for this campaign, not an
optimisation choice.

Before any split or benchmark task is designed:

- choose one `property_kind` as the primary residual target for that task;
- report the other two kinds separately if included in the dataset;
- record the chosen `property_kind` in the pre-reveal package;
- do not change the choice after any target is inspected.

Leakage risk: if absorption and emission values are both fit to a single
energy axis, a model can exploit the Stokes shift to absorb its own variance.
This leakage is not visible in aggregate residual metrics.

## Required Baseline Freeze

Before any candidate is judged under this protocol, freeze these surfaces:

- pinned dataset file or files and their source manifest versions;
- `property_kind` used as the residual target;
- size axis convention (`diameter_nm` or `radius_nm`) and unit;
- baseline model family, parameter source, and any per-material flags;
- residual target definition in eV;
- holdout slice definition from the families below;
- complexity penalty rule if model selection is involved;
- model-selection rule;
- pass/fail threshold or evaluation criterion;
- expected limitations and negative-control predictions.

The frozen surfaces must be committed before any holdout target is inspected.
See `docs/blind-holdout-benchmark-protocol.md` for the artifact structure.

## Holdout Families

Every serious candidate should be evaluated on at least one of the structured
holdout families below. A single random split is not sufficient for a campaign
claim.

### 1. Material Holdout (Required for First Baseline)

Drop all entries from one material family at training time. Evaluate the
candidate on those withheld entries only.

Natural choices for the first baseline:

- withhold CdSe while training on InP, PbS, CdS, ZnSe (or the available
  materials);
- withhold InP while training on CdSe and others;
- repeat the withheld-material sweep to check for material-specific
  sensitivity.

Leakage risk: if the candidate uses a material-specific parameter from the
held-out material's literature, it is not a genuine out-of-material evaluation.
Record all parameter sources explicitly.

### 2. Size-Range Holdout (Required for First Baseline)

Drop entries from the largest or smallest size bin at training time.
Evaluate on that bin only.

Define bins by the size distribution of the dataset, not by theoretical
confinement regimes. Suggested partition for a first baseline:

- small: diameter below 3 nm or radius below 1.5 nm;
- mid: diameter 3–6 nm or radius 1.5–3 nm;
- large: diameter above 6 nm or radius above 3 nm.

Adjust bin boundaries to reflect the actual dataset distribution when the
source manifest is populated. Document the chosen boundaries in the
pre-reveal package.

Leakage risk: published size-bandgap curves are often fit to mid-range data.
A model that interpolates the curve will underperform at size extremes if the
curve was not designed for them. This is a desirable failure mode to capture.

### 3. Source or Publication Holdout (Optional for First Baseline)

Drop all entries from one publication source at training time. Evaluate on
entries from that source only.

This tests whether systematic measurement offsets between labs or instruments
are absorbed into the model.

Leakage risk: if a publication reports a size-bandgap fit and the dataset
contains values derived from that fit, the holdout tests the fit's
extrapolation rather than independent measurement. Record whether each entry
is a directly measured value or a curve-read value in `measurement_type`
and `notes`.

This holdout is optional until at least two independent publication sources
are registered in `source_manifest.yaml` for the same material and property.

### 4. Composition-Family Holdout (Optional for First Baseline)

Drop entries with `composition_note` indicating alloy, doping, or shell
structure at training time. Evaluate on those entries only.

This tests whether a baseline model trained on pure-core particles applies to
composite particles without refitting.

This holdout is optional until the dataset contains a sufficient number of
alloyed or core-shell entries as indicated by `composition_note`.

## Negative Controls

Every benchmark task using this protocol must include at least one explicit
negative control.

Suggested negative controls for a first baseline:

- **Wrong-material parameters**: apply Brus effective-mass coefficients
  for material A when evaluating material B. The residual should increase
  significantly compared to the matched-material baseline.
- **Constant-energy predictor**: predict the bulk bandgap of each material
  independent of size. The residual should be larger than the size-aware
  baseline in small-particle regimes.
- **Shuffled-size predictor**: assign sizes randomly from the training
  distribution. The residual should equal or exceed the constant predictor
  for a well-fit baseline.

Record the negative-control result in the result package alongside the
primary holdout result. If a negative control does not fail as expected,
treat that as a flag requiring review before the result is promoted.

## Split Rules for Absorption, Emission, and Bandgap

When a dataset file contains multiple property kinds:

- define one primary residual target for the task (e.g. `absorption_peak_eV`);
- split the primary-target entries using the chosen holdout family;
- do not use emission or bandgap entries to inform the split definition or
  to supplement training data for the primary residual;
- report emission and bandgap residuals separately if evaluated, using their
  own entries only;
- never average residuals across property kinds.

If a future task requires joint evaluation of multiple property kinds, each
kind must have its own residual surface and its own holdout slice. They must
not be merged into a single metric.

## Complexity Notes for Future Correction Hypotheses

When a correction hypothesis is proposed after the baseline:

- state the hypothesis in terms of the residual structure visible in the
  baseline result;
- declare how many free parameters the correction adds per material;
- require the correction to reduce residuals on the held-out slice, not only
  on training data;
- flag any parameter that is specific to the held-out material or size range
  as a leakage risk;
- never promote a correction that was tuned after holdout inspection.

A correction that reduces training residuals but fails the material holdout
is a negative result. Record it as such using the negative-results registry.

## Protocol Application Steps

For each benchmark task that uses this protocol:

1. Choose the primary `property_kind` and record it in the task file.
2. Choose the holdout family or families from the four above.
3. Define the exact split rule and bin boundaries before opening any target
   data.
4. Commit the pre-reveal package (see `docs/blind-holdout-benchmark-protocol.md`).
5. Run training-only checks on the non-holdout slice.
6. Stop. Request maintainer review of the pre-reveal package.
7. After maintainer approval, perform the reveal.
8. Record the reveal outcome in the reveal record.
9. Do not alter the pre-reveal package after the reveal.
10. Submit the result package for maintainer review before promoting to a
    canonical result.

## First Baseline Minimum

The first baseline benchmark under `TASK-0225` must use at minimum:

- one property kind as the primary residual target;
- material holdout on at least one material;
- size-range holdout on at least one size bin;
- one negative control.

The first baseline does **not** need to cover all four holdout families, all
materials in the dataset, or all property kinds simultaneously. Expand
coverage iteratively after the first result is reviewed.

## Relationship to the Campaign Plan

This protocol formalises the holdout outlook described in
`docs/notes/quantum-size-effects-campaign-plan.md`. The campaign plan records
the full task queue and diagnostic surfaces. This document defines the split
rules and leakage-risk catalogue that govern how those surfaces are evaluated.

`TASK-0225` (baseline residual benchmark) must reference this document when
defining its pre-reveal package.
