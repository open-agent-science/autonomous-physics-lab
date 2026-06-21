# Textbook Wien/FIRAS Source Pinning

Task: `TASK-0801`

Verdict: `SOURCE_ARTIFACT_PINNED_ROWS_CURATED_NO_METRICS`

## Result

The exact NASA LAMBDA COBE/FIRAS CMB monopole v1 ASCII product is committed at
`data/textbook_formula_audit/wien_firas/source_artifacts/cobe-firas-monopole/`.
Two independent downloads produced the same SHA-256:

`df793c3dca09ebfa7dbc5aa0ec1951daa8884431bc30eff28a710d7516cf50fa`

The artifact contains 43 rows over `2.27` to `21.33 cm^-1`. Its header and the
LAMBDA product description establish that the audited candidate ordinate is
an absolute monopole intensity: a 2.725 K blackbody plus the published
residual. The residual column remains diagnostic only.

## Curated Surface

`data/textbook_formula_audit/wien_firas/firas_monopole_rows.yaml` preserves all
five source columns and records a provenance class for each value:

- native axis: `source_reported_direct`;
- absolute monopole intensity: `source_derived_absolute`;
- residual: `source_reported_residual`;
- uncertainty: `source_reported_1sigma`;
- Galactic-pole component: `source_modeled`.

The normalized file is generated deterministically by
`scripts/normalize_firas_monopole_source.py`, which refuses a source checksum
or row-count mismatch.

## License And Provenance

The product is hosted by NASA LAMBDA and was developed by NASA GSFC. It is
committed under the U.S.-Government-work/public-domain posture with NASA
attribution and without endorsement. The package records its exact URL,
retrieval date, v1 revision, upstream HTTP metadata, byte count, citations,
checksum, and redistribution decision.

## Boundaries

No blackbody spectrum was fitted. No `B_nu` to `B_lambda` conversion, peak
location, Wien residual, RESULT, PRED, CLAIM, or KNOW artifact was produced.
The temperature source remains intentionally separate.

TASK-0802 may run only after it pins the chosen reference-temperature source
and predeclares the wavelength-domain Jacobian and controls.

## Output Routing

- Task verdict: `not_applicable` for scientific formula validity; source gate
  verdict `SOURCE_ARTIFACT_PINNED_ROWS_CURATED_NO_METRICS`.
- Canonical destination: committed source artifact and normalized source rows.
- Review tier: `none`.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: none.
- Knowledge impact: none.
- Remaining blocker: separate temperature provenance and TASK-0802 metric
  authorization.
