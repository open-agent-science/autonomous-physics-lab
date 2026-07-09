# FRB Pre-T Model Selection Freeze

- Task: `TASK-0964`
- Domain: radio transients astrophysics
- Verdict: `FRB_PRE_T_EXPOSURE_MODEL_SURFACE_FROZEN`
- Frozen surface: `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml`

## Scope

This freezes the exposure-only pre-T repeater-propensity surface that the
registration pack task can consume. It does not read repeat labels, score
repeat outcomes, register a PRED entry, create a RESULT artifact, or promote
a claim.

## Frozen Selection

- Selected model: `gate_total_exposure_log1p`.
- Formula: `log1p(E_upper_hours + E_lower_hours)`.
- Nonzero scored rows: `465` of `479`.
- Unique score values: `457`.
- Per-source score digest: `00404c62efb1edc300f008f53961e691cb1c06208ef5a032ff83b0bf8ddb60d7`.

The selected model beats the constant-null comparator on the predeclared
label-free coverage and rank-resolution checks. No label-performance metric
is computed.

## Leakage Boundary

- Columns read: `source_id`, `E_upper_hours`, `E_lower_hours`, `score_pre_t`.
- Label contact: `false`.
- Forbidden fields remain excluded: repeater labels, Catalog 2 full-window
  exposure, morphology, and post-T source associations.
- Scoring rule is the gate formula verbatim:
  `score_pre_t = log1p(E_upper_hours + E_lower_hours)`.

## Output Routing

- Canonical destination: frozen model surface under `data/radio_transients/`
  plus this review note.
- Review tier: none.
- Gate A / Gate B: not applicable.
- Prediction impact: staged surface only; no PRED registered.
- Claim impact: none.
- Knowledge impact: none.
- Next stage: `TASK-0965` prepares the maintainer-approved sealed prediction
  registration pack after `TASK-0964` is merged.

## Limitations

- This is an exposure-only propensity ordering, not evidence that the model
  predicts repeaters.
- Registration and external anchoring are out of scope for this task.
- Reveal scoring must use the later checksum-pinned label surface and the
  frozen scoring rule without modification.
