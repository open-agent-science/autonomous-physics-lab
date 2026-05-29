# Nuclear Neutron-Rich Boundary Transfer Hypothesis Lane

**Task:** `TASK-0450`
**Agent run:** `AGENT-RUN-0044`
**Campaign:** `nuclear-mass-surface`
**Verdict:** `NEGATIVE_RESULT`
**Sandbox only:** true

## Candidate

- Feature: `boundary_distance = max(0, (N - Z)/A - 0.18)` (closed-form, residual-free).
- Fit: `r_corr = beta * boundary_distance` via least squares on the 11-row NMD-0002 training slice. `beta = -7.9335 MeV` (per unit boundary distance).

## Aggregate MAE (MeV)

| Surface | baseline | candidate | matched_high_error | sign_inverted |
| --- | ---: | ---: | ---: | ---: |
| `training_lstsq` | 2.8245 | 2.8134 | 2.8245 | 2.8356 |
| `primary_holdout` | 4.5526 | 4.7014 | 4.7168 | 4.4067 |
| `full_known` | 4.4904 | 4.6335 | 4.6488 | 4.3502 |

## Verdict Rationale

- full_known candidate vs baseline: -0.1431 MeV
- Candidate fails the 0.25 MeV survival margin on full_known vs baseline.

## Isotope-Chain Transfer

- Transfer rate (fraction of eligible chains with candidate improvement > 0): 0.082
- Eligible chains (>= 2 rows on full_known): 61

| Chain | count | baseline MAE | candidate MAE | delta |
| --- | ---: | ---: | ---: | ---: |
| `Z=8` | 2 | 0.8738 | 0.8738 | 0.0000 |
| `Z=10` | 3 | 1.4246 | 1.6117 | -0.1871 |
| `Z=14` | 2 | 2.2667 | 2.2667 | 0.0000 |
| `Z=15` | 2 | 1.1894 | 1.1894 | 0.0000 |
| `Z=16` | 3 | 2.0113 | 2.0113 | 0.0000 |
| `Z=18` | 2 | 1.4790 | 1.4790 | 0.0000 |
| `Z=20` | 4 | 3.2760 | 3.4332 | -0.1572 |
| `Z=21` | 6 | 3.1854 | 3.3684 | -0.1831 |
| `Z=22` | 5 | 1.6856 | 1.7635 | -0.0779 |
| `Z=23` | 6 | 0.7139 | 0.7857 | -0.0717 |
| `Z=24` | 10 | 2.5138 | 2.7376 | -0.2238 |
| `Z=25` | 4 | 1.8314 | 1.8314 | 0.0000 |
| `Z=26` | 12 | 2.3189 | 2.4839 | -0.1649 |
| `Z=27` | 2 | 3.2546 | 3.5956 | -0.3410 |
| `Z=28` | 3 | 5.6226 | 5.9838 | -0.3612 |
| `Z=29` | 4 | 7.8946 | 8.2912 | -0.3967 |
| `Z=30` | 2 | 4.5663 | 4.8063 | -0.2400 |
| `Z=31` | 6 | 8.5640 | 8.7689 | -0.2048 |
| `Z=32` | 7 | 5.8342 | 6.1622 | -0.3280 |
| `Z=33` | 13 | 5.2382 | 5.4702 | -0.2320 |
| `Z=34` | 14 | 4.4070 | 4.5988 | -0.1919 |
| `Z=35` | 8 | 4.1858 | 4.3758 | -0.1901 |
| `Z=36` | 6 | 3.7299 | 3.8320 | -0.1021 |
| `Z=37` | 7 | 4.7802 | 5.2819 | -0.5018 |
| `Z=38` | 9 | 4.7783 | 5.2387 | -0.4604 |
| `Z=39` | 2 | 5.4955 | 5.7731 | -0.2777 |
| `Z=40` | 5 | 4.3068 | 4.4103 | -0.1036 |
| `Z=41` | 2 | 2.1702 | 2.5639 | -0.3937 |
| `Z=42` | 4 | 3.5007 | 3.7650 | -0.2643 |
| `Z=44` | 6 | 1.2227 | 1.3252 | -0.1025 |
| `Z=45` | 4 | 0.6051 | 0.6010 | 0.0041 |
| `Z=46` | 6 | 3.0322 | 3.1553 | -0.1231 |
| `Z=47` | 5 | 3.1120 | 3.1120 | 0.0000 |
| `Z=48` | 3 | 3.1639 | 3.3195 | -0.1556 |
| `Z=49` | 18 | 7.9821 | 8.2434 | -0.2613 |
| `Z=50` | 2 | 1.8683 | 1.8683 | 0.0000 |
| `Z=51` | 4 | 9.7825 | 10.0834 | -0.3008 |
| `Z=52` | 2 | 5.7263 | 5.8772 | -0.1509 |
| `Z=53` | 8 | 8.2880 | 8.6459 | -0.3579 |
| `Z=58` | 4 | 3.4596 | 3.9301 | -0.4705 |
| `Z=59` | 5 | 3.5033 | 3.9447 | -0.4414 |
| `Z=60` | 3 | 1.3612 | 1.5222 | -0.1610 |
| `Z=61` | 4 | 1.8486 | 1.8688 | -0.0202 |
| `Z=63` | 2 | 2.7342 | 3.1442 | -0.4100 |
| `Z=65` | 2 | 4.4935 | 4.4935 | 0.0000 |
| `Z=69` | 3 | 6.1922 | 6.1922 | 0.0000 |
| `Z=70` | 8 | 5.1125 | 5.1125 | 0.0000 |
| `Z=71` | 4 | 4.2874 | 4.2874 | 0.0000 |
| `Z=72` | 3 | 5.5608 | 5.5608 | 0.0000 |
| `Z=73` | 3 | 5.1524 | 5.1524 | 0.0000 |
| `Z=74` | 3 | 6.1059 | 6.1059 | 0.0000 |
| `Z=75` | 3 | 5.6341 | 5.6341 | 0.0000 |
| `Z=76` | 3 | 6.5351 | 6.5351 | 0.0000 |
| `Z=77` | 3 | 6.0540 | 6.0540 | 0.0000 |
| `Z=78` | 3 | 6.9761 | 6.9761 | 0.0000 |
| `Z=79` | 2 | 6.7957 | 6.7957 | 0.0000 |
| `Z=80` | 3 | 7.3890 | 7.3890 | 0.0000 |
| `Z=91` | 3 | 5.7670 | 5.3799 | 0.3872 |
| `Z=92` | 8 | 5.9621 | 5.5778 | 0.3843 |
| `Z=93` | 4 | 5.9451 | 5.5754 | 0.3697 |
| `Z=94` | 4 | 6.6145 | 6.3108 | 0.3037 |

## Per-Subset Behavior (full_known)

| Subset | count | baseline MAE | candidate MAE | delta |
| --- | ---: | ---: | ---: | ---: |
| `light_a_lt_50` | 24 | 1.8723 | 1.8956 | -0.0234 |
| `neutron_rich` | 162 | 5.3198 | 5.5900 | -0.2702 |
| `not_neutron_rich` | 144 | 3.5574 | 3.5574 | 0.0000 |
| `post_ame2020_measured` | 295 | 4.5526 | 4.7014 | -0.1488 |

## Leakage Audit

- Feature uses only `Z`, `N`, `A`. No baseline residual, error rank, candidate-fit residual, source-status flag, or future comparison row enters feature construction. ✅
- Beta is fit by closed-form least squares on the training slice only; no candidate-fit residual feeds the controls. ✅
- Matched-high-error control uses the baseline residual rank, NOT the candidate residual; it intentionally restricts to non-neutron-rich rows to test specificity. ✅
- Sign-inverted control reuses the same beta with opposite sign; same fit logic. ✅

## Promotion Boundary

- `sandbox_only: true`
- `writes_canonical_result: false`
- `claim_promotion_allowed: false`
- `prediction_registry_allowed: false`
- Required next step: maintainer review before any follow-up. No `PRED-XXXX`, `RESULT-XXXX`, `CLAIM-XXXX`, or `KNOW-XXXX` artifact is created by this run.

