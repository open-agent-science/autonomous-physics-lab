# Preflight

- PASS: data_boundary ? only committed snapshot rows are read; no live fetch.
- PASS: baseline_freeze ? frozen baseline helpers are reused without refit.
- PASS: bin_predeclaration ? mass quartiles are rank-balanced bins sorted by mass and row_id before metric interpretation.
- PASS: promotion_boundary ? no RESULT, CLAIM, KNOW, or PRED artifact is written.
