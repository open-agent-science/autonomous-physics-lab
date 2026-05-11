# NMS-002: Measured vs Extrapolated Nuclear Mass Data — Policy Note

## The Ambiguity

The AME (Atomic Mass Evaluation) dataset contains both directly measured nuclear
masses and extrapolated (model-estimated) entries. The AME convention marks
extrapolated values with a `#` flag in the data files.

## Why Silent Mixing is Disallowed

Silently combining measured and extrapolated entries in a residual fit creates
two problems:

1. **Circular reasoning risk:** extrapolated AME entries are themselves derived
   from nuclear mass models. If the Bethe-Weizsäcker (BW) baseline is one of
   the models used in the AME extrapolation, then residuals for extrapolated
   entries may be artificially small — the correction formula is fitting
   model-on-model noise.

2. **Overfitting near shell closures:** extrapolated entries cluster near
   neutron or proton drip lines, where experimental data is sparse and shell-
   closure effects are largest. Including them in training without flagging
   inflates apparent coverage of the difficult nuclear structure regime.

## Required Policy

- Every dataset entry must carry a boolean flag: `measured: true` (AME
  experimental value) or `measured: false` (AME extrapolated value).
- Training sets should document the fraction of extrapolated entries used.
- Holdout sets should prefer measured entries; extrapolated-only holdout
  results must be reported separately.
- Any residual map or correction-term analysis that includes extrapolated
  entries must state so explicitly.

## Limitation Statement

Policy note only. No code change to the dataset loader is implemented here.
Maintainer review required before adopting this policy in canonical pipelines.
