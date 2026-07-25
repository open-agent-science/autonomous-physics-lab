# RESULT-0032 — Frozen Within-OQMD Baseline

- Contract verdict: `FAIL`
- RESULT verdict: `INVALID`
- Exact cation-pair holdout MAE: `0.308533591392` eV/atom
- IUPAC group-pair null holdout MAE: `0.154250620789` eV/atom
- Exact-pair unseen holdout rows: `5` of `26`
- Sensitivity seeds passing all comparators: `0/5`

The exact cation-pair baseline beats the global-median and every frozen shuffle control, but it is worse than the predeclared IUPAC group-pair null. The fail-closed contract therefore returns FAIL. No refit, row exclusion, threshold change, or cross-database pooling was performed.

## Frozen integrity and partition ledger

All six paths and SHA-256 values in the execution config matched before target loading. TASK-1053 reported `SPLIT_READY_FOR_BENCHMARK_PREFLIGHT`, TASK-1054 reported `CONTRACT_READY_FOR_FROZEN_SPLIT`, and TASK-1063 reported `INDEPENDENT_SOURCE_REPLAY_PASS`.

| Partition | Rows | Reduced-composition groups |
| --- | ---: | ---: |
| train | 120 | 120 |
| validation | 26 | 26 |
| holdout | 26 | 26 |

Missing/non-finite target exclusions: `0`. Cross-partition composition leakage: `0`. Row-order MAE drift: `0.000000000000`.

## Primary and secondary metrics

| Model | Train MAE | Validation MAE | Holdout MAE | Holdout RMSE | Unseen holdout groups |
| --- | ---: | ---: | ---: | ---: | ---: |
| `candidate` | 0.083174437568 | 0.230519423791 | 0.308533591392 | 0.454728159583 | 5 |
| `global_median_null` | 0.505340695865 | 0.540324691709 | 0.459529604455 | 0.558668204286 | 0 |
| `iupac_group_pair_null` | 0.167464512790 | 0.166005044968 | 0.154250620789 | 0.214827864827 | 0 |

## Required shuffle controls

| Control | Holdout MAE | Candidate clears frozen margin |
| --- | ---: | --- |
| `label_shuffle_seed_1054` | 0.592778498900 | True |
| `cation_pair_label_shuffle_seed_1054` | 0.567374651217 | True |
| `label_shuffle_seed_2054` | 0.641259628909 | True |
| `cation_pair_label_shuffle_seed_2054` | 0.518404658434 | True |
| `label_shuffle_seed_3054` | 0.536164839354 | True |
| `cation_pair_label_shuffle_seed_3054` | 0.692746908612 | True |
| `label_shuffle_seed_4054` | 0.632195896001 | True |
| `cation_pair_label_shuffle_seed_4054` | 0.486719464120 | True |
| `label_shuffle_seed_5054` | 0.577985116928 | True |
| `cation_pair_label_shuffle_seed_5054` | 0.658612687618 | True |

## Identity-group-preserving sensitivity

| Seed | Candidate holdout MAE | IUPAC null holdout MAE | All comparators pass |
| ---: | ---: | ---: | --- |
| 1054 | 0.302772400357 | 0.238696058431 | False |
| 2054 | 0.194973586591 | 0.174905540705 | False |
| 3054 | 0.218257495267 | 0.175800179163 | False |
| 4054 | 0.236706351393 | 0.239656925150 | False |
| 5054 | 0.297987242437 | 0.250224073379 | False |

## Complete frozen-holdout failure ledger

Every holdout row is retained; rows using the train-global-mean fallback are marked explicitly.

| Entry | Name | Cation pair | Target | Prediction | Residual | Absolute residual | Fallback |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2757 | Sr2Ti6O13 | Sr-Ti | -3.274071590435 | -2.032794482534 | -1.241277107901 | 1.241277107901 | True |
| 36003 | Ba2Fe6O11 | Ba-Fe | -1.977758489087 | -2.379664907375 | 0.401906418288 | 0.401906418288 | False |
| 648541 | SrV4O10 | Sr-V | -2.580349568995 | -2.827317594158 | 0.246968025163 | 0.246968025163 | False |
| 1338415 | Li3FeO4 | Fe-Li | -1.795538382116 | -2.032794482534 | 0.237256100418 | 0.237256100418 | True |
| 1345476 | SrTi2O5 | Sr-Ti | -3.316081875246 | -2.032794482534 | -1.283287392712 | 1.283287392712 | True |
| 1347212 | Cs4TiO4 | Cs-Ti | -2.161224561922 | -2.835226570774 | 0.674002008852 | 0.674002008852 | False |
| 1347984 | Sr2Mn3O8 | Mn-Sr | -2.289863538744 | -2.636780265963 | 0.346916727220 | 0.346916727220 | False |
| 1348506 | SrMnO2 | Mn-Sr | -2.494046644117 | -2.636780265963 | 0.142733621846 | 0.142733621846 | False |
| 1348842 | K2Mn3O7 | K-Mn | -1.857021006066 | -1.811115744819 | -0.045905261247 | 0.045905261247 | False |
| 1369277 | CsMnO2 | Cs-Mn | -1.864383985992 | -1.681372828216 | -0.183011157776 | 0.183011157776 | False |
| 1752950 | Li2FeO2 | Fe-Li | -1.873389962034 | -2.032794482534 | 0.159404520500 | 0.159404520500 | True |
| 1880486 | BaV2O4 | Ba-V | -2.721527847726 | -2.575605058820 | -0.145922788906 | 0.145922788906 | False |
| 1880956 | K3CoO3 | Co-K | -1.488244230653 | -1.419076889631 | -0.069167341022 | 0.069167341022 | False |
| 2061686 | Cs3Mn2O4 | Cs-Mn | -1.705593443104 | -1.681372828216 | -0.024220614888 | 0.024220614888 | False |
| 2151770 | Rb4Cu3O6 | Cu-Rb | -1.217700486949 | -2.032794482534 | 0.815093995585 | 0.815093995585 | True |
| 2156236 | Rb6Cr2O9 | Cr-Rb | -1.855503766555 | -2.187864961314 | 0.332361194759 | 0.332361194759 | False |
| 2172655 | K4Co3O6 | Co-K | -1.457839077006 | -1.419076889631 | -0.038762187375 | 0.038762187375 | False |
| 2172994 | Cs5Cu2O4 | Cs-Cu | -1.170701887444 | -1.175130751742 | 0.004428864298 | 0.004428864298 | False |
| 2173280 | Ba6Mn5O15 | Ba-Mn | -2.451340840740 | -2.425313743326 | -0.026027097414 | 0.026027097414 | False |
| 2173445 | SrMn2O4 | Mn-Sr | -2.363905655063 | -2.636780265963 | 0.272874610901 | 0.272874610901 | False |
| 2173536 | SrCo2O4 | Co-Sr | -1.829814694984 | -2.109826601750 | 0.280011906766 | 0.280011906766 | False |
| 2173628 | Rb6Cr2O7 | Cr-Rb | -1.851338200645 | -2.187864961314 | 0.336526760669 | 0.336526760669 | False |
| 2173880 | Na2Mn3O6 | Mn-Na | -1.988503735783 | -1.715799539801 | -0.272704195982 | 0.272704195982 | False |
| 2173928 | K8Fe2O7 | Fe-K | -1.561962970175 | -1.500706897367 | -0.061256072809 | 0.061256072809 | False |
| 2174149 | Na7Ti10O20 | Na-Ti | -2.854843316254 | -2.794754197472 | -0.060089118782 | 0.060089118782 | False |
| 2174292 | K7MnO6 | K-Mn | -1.491357460713 | -1.811115744819 | 0.319758284105 | 0.319758284105 | False |

## Boundary

This is bounded negative/control evidence on one computed-DFT OQMD slice, not experimental replication, a materials law, or a material recommendation.
