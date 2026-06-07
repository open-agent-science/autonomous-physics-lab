# Stellar M-L DEBCat Holdout and Leakage Protocol

Task: `TASK-0657`
Domain: Textbook Formula Audit / Stellar mass-luminosity
Mode: planning only
Verdict: `PROTOCOL_DEFINED_NO_ROWS_NO_METRICS`

## Purpose

This protocol defines the split and no-leakage rules for a future DEBCat-based
stellar mass-luminosity benchmark. It does not fetch DEBCat rows, parse table
values, compute luminosities, fit exponents, create results, create claims, or
promote Stellar M-L to a standalone campaign.

The core rule is system-level splitting: both components of the same physical
binary system must always be assigned to the same train, validation, holdout, or
excluded lane.

## Evidence Reviewed

- `docs/reviews/textbook-stellar-ml-source-candidate-admissibility.md`
- `docs/notes/textbook-formula-audit-candidate-list.md`
- `docs/notes/stellar-ml-campaign-promotion-gate.md`
- `TASK-0628`
- `data/textbook_formula_audit/stellar_ml/source_manifest.yaml`
- `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/README.md`
- `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/license_review.md`
- `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/extraction_notes.md`
- `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/blocker_notes.md`

## Split Lanes

Future row-curation tasks should assign each physical binary system to exactly
one lane:

- `train`: allowed for baseline calibration only after the baseline family is
  predeclared.
- `validation`: allowed for predeclared quality checks, not final result claims.
- `holdout`: no-peek lane for final benchmark scoring.
- `excluded`: ambiguous, inadmissible, duplicate, model-derived, or
  insufficiently licensed/provenanced rows.

Component rows may be the eventual row granularity, but lane assignment is at
the physical-system level. If the physical system identifier is ambiguous, all
components from that candidate system belong in `excluded` until the ambiguity
is resolved by a later row-readiness task.

## Required No-Leakage Constraints

1. Keep both components of a detached eclipsing binary in the same split.
2. Keep duplicate aliases or renamed references for the same binary in the same
   split.
3. Freeze the system-to-lane manifest before inspecting residuals or fitting any
   exponent.
4. Do not tune mass-band thresholds, evolutionary filters, uncertainty filters,
   or exclusion rules after seeing holdout residuals.
5. Do not use model-derived masses as benchmark truth.
6. Do not compute or import luminosities until luminosity provenance and
   uncertainty policy are approved.
7. Treat any accidental component split across lanes as a stop condition: the
   benchmark manifest must be rebuilt before metrics are valid.

## Candidate Split Axes

These axes should be recorded before row values are used for metrics.

| Axis | Rule |
| --- | --- |
| System id | Primary no-leakage key. All components from one physical binary system share one lane. |
| Mass band | Predeclare mass ranges before residual inspection. Thresholds may be adjusted only before any holdout metric exists. |
| Evolutionary-stage flag | Separate main-sequence-compatible systems from evolved, pre-main-sequence, ambiguous, or unknown systems under documented source semantics. |
| Reference/source family | Track original catalogue/reference family so one source family cannot silently dominate both train and holdout interpretation. |
| Uncertainty class | Bin mass and future luminosity uncertainty under frozen thresholds; unknown or incompatible uncertainty semantics go to `excluded` or a diagnostic lane. |

Mass-band and uncertainty-class thresholds are protocol parameters, not
discoveries. They must be chosen for audit coverage and leakage control, not for
better textbook-formula residuals.

## Luminosity Inputs Still Inadmissible

The following inputs remain inadmissible until a later row-readiness task
defines source, conversion, and uncertainty semantics:

- luminosities derived without a documented provenance path
- luminosities requiring unreviewed bolometric corrections, extinction
  corrections, parallax transforms, or effective-temperature/radius conversions
- any value whose derivation imports model-derived mass truth
- literature luminosity fields without redistribution and citation review
- DEBCat value-bearing table rows while the current package remains
  metadata-only

Direct dynamical component masses may be considered later only after licensing,
storage, schema, and uncertainty review. Derived luminosity is a separate gate
and must not be assumed admissible just because the mass source is selected.

## Row-Readiness Checklist

A future row-curation task must provide, before metrics:

- system identifier and component identifier
- system-to-lane assignment manifest
- source artifact checksum and citation path
- mass value, mass uncertainty, and direct-observation semantics
- luminosity value, luminosity uncertainty, and admissible derivation path, if
  luminosity is approved at all
- exclusion reason for every non-admitted candidate row
- confirmation that no fit, exponent, threshold, or residual metric was chosen
  after holdout inspection

## Output Routing Summary

- New DEBCat rows: none
- New luminosities: none
- New fitted exponents: none
- New result artifact: none
- New claim artifact: none
- Current routing: protocol note only; Stellar M-L remains inside Textbook
  Formula Audit until promotion gates are met
