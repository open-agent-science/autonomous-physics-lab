# Nuclear Shell-Axis Isotope-Chain Transfer Audit

**Agent run:** `AGENT-RUN-0023`
**Task:** `TASK-0323`
**Evidence class:** retrospective full-known isotope-chain transfer audit
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`
**Script:** `scripts/run_nuclear_shell_axis_chain_transfer_audit.py`
**Metrics:** `agent_runs/AGENT-RUN-0023/metrics.json`

## Scope

This sandbox audit groups committed full-known rows by isotope chain using fixed `Z` and asks whether shell-axis improvements transfer across chains or remain chain-local. It does not score future measurements or promote claims.

## Transfer Verdict

`MIXED_CHAIN_LOCAL`

Shell-axis behavior transfers unevenly by isotope chain; chain-level regressions remain visible and block broad support wording.

## Candidate Transfer Summary

| Candidate | Interpretable chains | Improved | Regressed | Improvement rate | Worst regression chain |
| --- | ---: | ---: | ---: | ---: | --- |
| `FULLKNOWN-SHELL-001` | 48 | 19 | 24 | 0.396 | `Z_080` +0.705235 MeV |
| `FULLKNOWN-SHELL-002` | 48 | 18 | 26 | 0.375 | `Z_020` +0.368349 MeV |
| `FULLKNOWN-SHELL-003` | 48 | 18 | 26 | 0.375 | `Z_071` +1.128924 MeV |

## Per-Chain Outcomes

| Chain | Rows | A range | Baseline MAE | Best shell delta | Best shell | Best non-shell delta | Best non-shell | Class |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| `Z_002` | 1 | 4-4 | 2.685975 | -1.754815 | `FULLKNOWN-SHELL-002` | -0.807914 | `SPECIFICITY-CONTROL-003` | too_sparse |
| `Z_007` | 1 | 14-14 | 4.171542 | -1.416326 | `FULLKNOWN-SHELL-003` | -0.918738 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_008` | 2 | 16-17 | 0.873841 | +0.678302 | `FULLKNOWN-SHELL-001` | -0.001905 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_010` | 3 | 24-26 | 1.424578 | -0.235078 | `FULLKNOWN-SHELL-001` | -0.233550 | `SPECIFICITY-CONTROL-003` | interpretable |
| `Z_014` | 2 | 23-24 | 2.266735 | -0.221450 | `FULLKNOWN-SHELL-003` | -0.001905 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_015` | 2 | 26-27 | 1.189406 | -0.151918 | `FULLKNOWN-SHELL-003` | -0.001905 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_016` | 3 | 27-36 | 2.011335 | +0.052453 | `FULLKNOWN-SHELL-001` | -0.366823 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_017` | 1 | 36-36 | 1.204897 | +0.377485 | `FULLKNOWN-SHELL-001` | +0.027052 | `SPECIFICITY-CONTROL-002` | too_sparse |
| `Z_018` | 2 | 31-36 | 1.479020 | +0.000000 | `FULLKNOWN-SHELL-001` | -0.009524 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_019` | 1 | 36-36 | 0.292845 | +0.502763 | `FULLKNOWN-SHELL-002` | -0.027052 | `SPECIFICITY-CONTROL-002` | too_sparse |
| `Z_020` | 4 | 36-54 | 3.276028 | +0.017811 | `FULLKNOWN-SHELL-001` | -0.065377 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_021` | 6 | 50-55 | 3.185377 | -0.960685 | `FULLKNOWN-SHELL-001` | -0.275491 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_022` | 5 | 43-56 | 1.685616 | +0.141047 | `FULLKNOWN-SHELL-001` | -0.018381 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_023` | 6 | 54-59 | 0.713923 | +0.033664 | `FULLKNOWN-SHELL-001` | -0.008200 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_024` | 10 | 46-65 | 2.513808 | +0.000000 | `FULLKNOWN-SHELL-001` | -0.027874 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_025` | 4 | 48-59 | 1.831447 | +0.073354 | `FULLKNOWN-SHELL-002` | +0.045239 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_026` | 12 | 50-70 | 2.318916 | +0.122182 | `FULLKNOWN-SHELL-002` | -0.263276 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_027` | 2 | 69-70 | 3.254580 | -1.026111 | `FULLKNOWN-SHELL-001` | -0.500044 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_028` | 3 | 54-75 | 5.622629 | -0.387579 | `FULLKNOWN-SHELL-001` | -0.086613 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_029` | 4 | 56-78 | 7.894563 | -1.081778 | `FULLKNOWN-SHELL-003` | -0.183815 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_030` | 2 | 58-79 | 4.566333 | -0.340687 | `FULLKNOWN-SHELL-001` | -0.196196 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_031` | 6 | 60-84 | 8.564017 | -0.333186 | `FULLKNOWN-SHELL-003` | -0.047621 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_032` | 7 | 62-86 | 5.834184 | -0.462633 | `FULLKNOWN-SHELL-003` | -0.086086 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_033` | 13 | 64-89 | 5.238222 | -0.422672 | `FULLKNOWN-SHELL-003` | -0.058871 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_034` | 14 | 66-91 | 4.406959 | -0.258870 | `FULLKNOWN-SHELL-003` | -0.055588 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_035` | 8 | 71-92 | 4.185764 | -0.416218 | `FULLKNOWN-SHELL-003` | -0.073829 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_036` | 6 | 70-92 | 3.729920 | -0.098007 | `FULLKNOWN-SHELL-003` | -0.050305 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_037` | 7 | 90-103 | 4.780163 | -0.105463 | `FULLKNOWN-SHELL-003` | -0.118293 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_038` | 9 | 75-105 | 4.778256 | -0.000002 | `FULLKNOWN-SHELL-001` | -0.617878 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_039` | 2 | 81-104 | 5.495469 | +0.000000 | `FULLKNOWN-SHELL-001` | -0.744291 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_040` | 5 | 80-106 | 4.306754 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.016790 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_041` | 2 | 104-109 | 2.170241 | -0.000047 | `FULLKNOWN-SHELL-001` | -0.392756 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_042` | 4 | 87-112 | 3.500713 | +0.000000 | `FULLKNOWN-SHELL-001` | -0.741634 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_043` | 1 | 115-115 | 4.438326 | -0.002543 | `FULLKNOWN-SHELL-001` | -0.923929 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_044` | 6 | 91-113 | 1.222701 | +0.000000 | `FULLKNOWN-SHELL-001` | -0.000198 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_045` | 4 | 93-113 | 0.605142 | +0.011691 | `FULLKNOWN-SHELL-002` | +0.000000 | `SPECIFICITY-CONTROL-003` | interpretable |
| `Z_046` | 6 | 95-123 | 3.032201 | -0.189816 | `FULLKNOWN-SHELL-003` | -0.485346 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_047` | 5 | 95-113 | 3.111969 | -0.798932 | `FULLKNOWN-SHELL-003` | -0.441551 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_048` | 3 | 118-125 | 3.163894 | -0.211018 | `FULLKNOWN-SHELL-001` | -0.231898 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_049` | 18 | 99-134 | 7.982110 | -0.633505 | `FULLKNOWN-SHELL-001` | -0.062338 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_050` | 2 | 103-120 | 1.868297 | -0.284853 | `FULLKNOWN-SHELL-002` | -0.088189 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_051` | 4 | 104-137 | 9.782538 | -1.026111 | `FULLKNOWN-SHELL-001` | -0.143742 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_052` | 2 | 107-133 | 5.726274 | -0.672905 | `FULLKNOWN-SHELL-003` | -0.046261 | `SPECIFICITY-CONTROL-002` | too_sparse |
| `Z_053` | 8 | 108-142 | 8.287981 | -0.524159 | `FULLKNOWN-SHELL-003` | -0.099789 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_054` | 1 | 111-111 | 2.882991 | +0.000520 | `FULLKNOWN-SHELL-002` | +0.000000 | `SPECIFICITY-CONTROL-003` | too_sparse |
| `Z_055` | 1 | 112-112 | 2.205738 | +0.000169 | `FULLKNOWN-SHELL-002` | -0.031637 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_057` | 1 | 151-151 | 4.101536 | -0.002543 | `FULLKNOWN-SHELL-001` | -0.119317 | `SPECIFICITY-CONTROL-002` | too_sparse |
| `Z_058` | 4 | 151-154 | 3.459645 | -0.000390 | `FULLKNOWN-SHELL-001` | -0.116527 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_059` | 5 | 152-157 | 3.503306 | -0.000047 | `FULLKNOWN-SHELL-001` | -0.114744 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_060` | 3 | 151-157 | 1.361157 | -0.000001 | `FULLKNOWN-SHELL-001` | -0.039101 | `SPECIFICITY-CONTROL-002` | interpretable |
| `Z_061` | 4 | 151-161 | 1.848581 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.052383 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_062` | 1 | 153-153 | 2.392364 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.791790 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_063` | 2 | 163-165 | 2.734222 | -0.000000 | `FULLKNOWN-SHELL-001` | -1.065779 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_065` | 2 | 148-155 | 4.493475 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.120004 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_067` | 1 | 152-152 | 5.556879 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.411114 | `SPECIFICITY-CONTROL-004` | too_sparse |
| `Z_068` | 1 | 151-151 | 4.425256 | +0.000000 | `FULLKNOWN-SHELL-001` | -0.118099 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_069` | 3 | 152-157 | 6.192227 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.381055 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_070` | 8 | 150-157 | 5.112497 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.127623 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_071` | 4 | 151-156 | 4.287402 | +0.000000 | `FULLKNOWN-SHELL-001` | -1.027109 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_072` | 3 | 156-159 | 5.560789 | +0.000002 | `FULLKNOWN-SHELL-002` | -0.142227 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_073` | 3 | 157-160 | 5.152431 | +0.000023 | `FULLKNOWN-SHELL-002` | -0.146036 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_074` | 3 | 160-163 | 6.105865 | +0.000036 | `FULLKNOWN-SHELL-002` | -0.449076 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_075` | 3 | 161-164 | 5.634144 | +0.000232 | `FULLKNOWN-SHELL-002` | -0.265462 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_076` | 3 | 164-167 | 6.535086 | +0.000087 | `FULLKNOWN-SHELL-002` | -1.112355 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_077` | 3 | 165-168 | 6.053973 | +0.000343 | `FULLKNOWN-SHELL-002` | -0.176513 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_078` | 3 | 168-171 | 6.976107 | +0.000030 | `FULLKNOWN-SHELL-002` | -0.190737 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_079` | 2 | 170-172 | 6.795734 | +0.000011 | `FULLKNOWN-SHELL-002` | -0.194292 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_080` | 3 | 172-175 | 7.389006 | +0.000001 | `FULLKNOWN-SHELL-002` | -0.203181 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_081` | 1 | 176-176 | 6.548527 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.213340 | `SPECIFICITY-CONTROL-001` | too_sparse |
| `Z_082` | 1 | 208-208 | 8.453688 | -1.754815 | `FULLKNOWN-SHELL-002` | -0.103007 | `SPECIFICITY-CONTROL-002` | too_sparse |
| `Z_091` | 3 | 235-237 | 5.767046 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.732510 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_092` | 8 | 235-242 | 5.962141 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.451442 | `SPECIFICITY-CONTROL-001` | interpretable |
| `Z_093` | 4 | 239-242 | 5.945074 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.595514 | `SPECIFICITY-CONTROL-004` | interpretable |
| `Z_094` | 4 | 239-242 | 6.614522 | +0.000000 | `FULLKNOWN-SHELL-002` | -0.459062 | `SPECIFICITY-CONTROL-001` | interpretable |

Negative deltas mean lower retrospective MAE than the frozen baseline. Positive deltas are regressions.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- Chains with fewer than three committed rows are diagnostic only.
- Best non-shell controls reuse TASK-0317 definitions; no new formula family is fit.
- Shell-axis and control coefficients are fit on the 11-row NMD-0002 residual slice.
- The full-known surface is committed repository data; this is not a future-measurement reveal.

## Promotion Boundary

- Prediction registry files are not edited.
- Canonical `RESULT-*` files are not edited.
- Claims and knowledge files are not edited.
- No future measurement reveal is scored.
