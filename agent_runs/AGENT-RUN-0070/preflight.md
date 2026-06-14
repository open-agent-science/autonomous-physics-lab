
# AGENT-RUN-0070 Preflight

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | PASS | `textbook-formula-audit` authorizes sandbox formula-audit runs. |
| Source binding | PASS | DEBCat rows were regenerated from checksum-verified local `debs.dat`. |
| Baseline freeze | PASS | Uses fixed `alpha=3.5`; no exponent fit or residual-tuned parameter change. |
| Holdout freeze | PASS | Uses extractor-assigned physical-binary-system lanes. |
| Storage boundary | PASS | Raw/full DEBCat artifacts remain local-only and uncommitted. |
| Promotion boundary | PASS | No canonical result, prediction, claim, or knowledge artifact is created. |
