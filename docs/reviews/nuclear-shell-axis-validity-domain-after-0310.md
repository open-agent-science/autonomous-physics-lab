# Nuclear Shell-Axis Validity Domain After TASK-0310

**Task:** `TASK-0315`  
**Evidence source:** `agent_runs/AGENT-RUN-0018/metrics.json`  
**Prior review:** `docs/reviews/nuclear-shell-axis-full-known-retrospective-audit.md`  
**Result note:** `docs/results/nuclear-shell-axis-full-known-audit.md`  
**Evidence class:** sandbox-only retrospective domain map

## Scope

This review maps the domain of validity implied by the `TASK-0310`
full-known-data retrospective audit. It reads the committed
`AGENT-RUN-0018` metrics and does not rerun candidate generation, tune
coefficients, edit prediction registry entries, score `PRED-0063` through
`PRED-0068`, modify canonical `RESULT-*` files, or promote claims.

Negative delta means lower MAE than the frozen `RESULT-0015` baseline on the
same subset. Positive delta means a regression.

## Audit Surface

| Subset | Rows | Baseline MAE MeV | Interpretation caution |
| --- | ---: | ---: | --- |
| Full-known unique surface | 306 | 4.490449 | Main retrospective committed-data surface. |
| Primary holdout | 295 | 4.552569 | Primary retrospective holdout behavior. |
| Training slice | 11 | 2.824522 | Coefficient fit surface; too small for broad claims. |
| Magic Z | 13 | 3.584303 | Sparse but directly aligned with proton-axis structure. |
| Magic N | 17 | 4.992014 | Sparse but directly aligned with neutron-axis structure. |
| Near-magic | 126 | 4.546848 | Broadest shell-proximity support surface. |
| Double-magic | 5 | 3.021909 | Very sparse; useful only as a fragility signal. |
| Light A<50 | 24 | 1.872252 | Consistent regression surface for shell-axis candidates. |
| Mid-mass | 198 | 4.519041 | Broad support surface. |
| Heavy A>=100 | 156 | 5.303283 | Mixed for neutron-axis candidate. |
| Neutron-rich high | 31 | 9.451698 | High-error support surface, still subset-limited. |
| Post-AME2020 measured comparison | 240 | 4.461256 | Retrospective measured-comparison subset. |
| Post-AME2020 extrapolated comparison | 55 | 4.951025 | Retrospective extrapolated-comparison subset. |
| Registry-repeat chain neighbor | 6 | 13.477141 | Very sparse, high-error diagnostic tied to repeated registry pressure. |

## Candidate Domain Map

| Candidate | Support zones | Regression zones | Sparse or fragile zones | Domain verdict |
| --- | --- | --- | --- | --- |
| `FULLKNOWN-SHELL-001` proton-axis Gaussian | Full-known -0.086092; holdout -0.091504; near-magic -0.224264; magic Z -0.158489; magic N -0.326992; double-magic -0.412072; mid-mass -0.162852; heavy -0.086113; neutron-rich -0.357017; measured -0.073328; extrapolated -0.170818; repeat-chain neighbor -0.824735. | Training +0.059043; light A<50 +0.104064. | Training n=11, double-magic n=5, repeat-chain neighbor n=6. | Strongest bounded support profile, but not valid for light nuclei and not promotion-ready. |
| `FULLKNOWN-SHELL-002` proton x neutron product | Full-known -0.070030; holdout -0.071641; training -0.026837; magic-any -0.197889; magic N -0.376547; near-magic -0.169194; double-magic -0.293656; mid-mass -0.117419; heavy -0.099203; neutron-rich -0.229458; measured -0.064275; extrapolated -0.103782; repeat-chain neighbor -0.382745. | Light A<50 +0.148840. Magic Z is effectively neutral at -0.001094. | Training n=11, double-magic n=5, repeat-chain neighbor n=6. | Useful secondary support, especially where neutron-axis information matters; weaker proton-axis specificity than `FULLKNOWN-SHELL-001`. |
| `FULLKNOWN-SHELL-003` neutron-axis Gaussian | Full-known -0.060145; holdout -0.061969; training -0.011248; magic-any -0.295574; magic N -0.512894; near-magic -0.156882; double-magic -0.323638; mid-mass -0.206938; neutron-rich -0.276888; measured -0.068076; extrapolated -0.035317; repeat-chain neighbor -0.611142. | Light A<50 +0.259976; heavy A>=100 +0.009103. Magic Z is weak at -0.022180. | Training n=11, double-magic n=5, repeat-chain neighbor n=6. | Diagnostic support for neutron-axis behavior, but the light regression is largest and the heavy subset is not supported. |
| `FULLKNOWN-SHELL-004` sign-inverted control | None. | Full-known +0.127546; holdout +0.127005; training +0.142063; magic Z +0.459333; magic N +0.453871; near-magic +0.322204; double-magic +0.697641; mid-mass +0.212299; heavy +0.111046; neutron-rich +0.357017; measured +0.113674; extrapolated +0.185174; repeat-chain neighbor +0.824735. | Light A<50 is only a small regression at +0.016535, but this does not rescue the control. | Expected negative control behavior; supports sign specificity by failing in the opposite direction. |
| `FULLKNOWN-SHELL-005` shuffled-feature control | No material support; all deltas are near zero. | Light A<50 +0.000256; training +0.000178. | Near-noise-floor magnitudes across every subset. | Row-feature correspondence control collapses, preserving the non-shuffled signal boundary. |
| `FULLKNOWN-SHELL-006` near-null baseline reference | None. | None. | Exact zero deltas by construction. | Baseline-reference control behaves as expected. |

## Support Zones

The strongest support zones are bounded and retrospective:

- `near_magic` supports all three shell-axis candidates, with deltas from
  `-0.156882` to `-0.224264 MeV` across 126 rows.
- `magic_n` is the most consistently improved explicit magic subset, with
  deltas from `-0.326992` to `-0.512894 MeV` across 17 rows.
- `mid_mass` improves for all three candidates, from `-0.117419` to
  `-0.206938 MeV` across 198 rows.
- `neutron_rich_high` improves for all three candidates, from `-0.229458` to
  `-0.357017 MeV` across 31 rows, but starts from a high baseline MAE.
- `post_ame2020_measured_comparison` and
  `post_ame2020_extrapolated_comparison` both improve for all three primary
  candidates, so the retrospective support is not limited to one comparison
  label.
- `registry_repeat_chain_neighbor` improves for all three primary candidates,
  but this subset has only 6 rows and should be treated as a fragile diagnostic
  rather than a standalone result.

`FULLKNOWN-SHELL-001` has the broadest support profile because it improves
every non-training subset except light `A<50`. It is therefore the best
bounded shell-axis reference for the next audit, not a claim candidate.

## Regression Zones

The main regression zone is explicit and should constrain future use:

| Subset | `FULLKNOWN-SHELL-001` | `FULLKNOWN-SHELL-002` | `FULLKNOWN-SHELL-003` | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Light A<50 | +0.104064 | +0.148840 | +0.259976 | All three primary shell-axis candidates regress light nuclei. |
| Training slice | +0.059043 | -0.026837 | -0.011248 | The strongest aggregate candidate regresses the 11-row fit surface. |
| Heavy A>=100 | -0.086113 | -0.099203 | +0.009103 | Neutron-axis-only support does not extend cleanly to the heavy subset. |

The light-nuclei regression is not a rounding artifact: it is the worst subset
regression for all three primary candidates. Any future shell-axis follow-up
should either exclude light `A<50` from the intended domain or treat it as a
mandatory failure/limitation panel.

## Sparse And Fragile Zones

Some zones look favorable but are too small to carry independent conclusions:

- `double_magic` has only 5 rows. It improves for all three primary
  candidates and regresses strongly under the sign-inverted control, but it is
  too sparse to be used as a promotion surface.
- `registry_repeat_chain_neighbor` has only 6 rows. Its large improvement for
  `FULLKNOWN-SHELL-001` and large regression under the sign-inverted control
  are useful stress signals, not evidence of broad chain-neighbor validity.
- `training_slice` has only 11 rows and is also the coefficient-fit surface.
  The fact that `FULLKNOWN-SHELL-001` regresses it while improving the larger
  holdout is a stability question, not a solved result.
- `post_ame2020_extrapolated_comparison` has 55 rows and remains
  retrospective. It can be used for comparison-label diagnostics, not for
  future-measurement reveal wording.

## Control Behavior

The controls preserve the audit boundary:

- The sign-inverted control regresses all substantive support surfaces,
  including full-known `+0.127546`, primary holdout `+0.127005`, magic Z
  `+0.459333`, magic N `+0.453871`, and registry-repeat chain neighbor
  `+0.824735 MeV`.
- The shuffled-feature control collapses to near-zero deltas; its largest
  positive subset delta is light `A<50` at `+0.000256 MeV`.
- The near-null baseline-reference control returns exactly zero deltas.

This means the retrospective signal is not reproduced by the tested null
controls, but it remains bounded by the small fit surface and subset
regressions.

## Recommended Next Step

The next Nuclear step should be coefficient stability audit (`TASK-0316`).

Rationale:

- `TASK-0315` identifies a plausible support domain, but the coefficients are
  still fit on only 11 NMD-0002 rows.
- `FULLKNOWN-SHELL-001` is the broadest support candidate, yet it regresses
  the training slice, so leave-one-out or jackknife stress is the most direct
  next falsification surface.
- Specificity controls (`TASK-0317`) remain valuable, but they are more
  informative after coefficient stability is tested.
- Source wait remains mandatory for real reveal scoring; `TASK-0305` should
  stay blocked until a reviewed source manifest exists.
- No further shell-axis expansion or new prediction registration should happen
  before stability and specificity are reviewed.

## Verdict

`BOUNDED_DOMAIN_MAP`

The shell-axis family has bounded retrospective support concentrated around
near-magic, magic-N, mid-mass, neutron-rich, measured/extrapolated comparison,
and sparse registry-repeat chain-neighbor diagnostics. It has a clear
exclusion or warning zone for light `A<50`, and `FULLKNOWN-SHELL-003` also
does not support the heavy subset. The correct next move is not promotion or
reveal scoring, but a coefficient stability audit followed by specificity
controls if stability does not fail.
