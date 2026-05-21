# Nuclear Shell-Axis Magic-Axis Asymmetry Audit

**Task:** `TASK-0321`  
**Agent run:** `agent_runs/AGENT-RUN-0021/`  
**Script:** `scripts/run_nuclear_shell_axis_magic_asymmetry_audit.py`  
**Metrics:** `agent_runs/AGENT-RUN-0021/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Evidence class:** sandbox-only retrospective magic-axis asymmetry audit

## Scope

This review checks whether the bounded shell-axis support from `TASK-0310` and
`TASK-0315` is magic-N dominant, magic-Z dominant, symmetric, tied, or too
sparse to interpret.

The audit reuses only committed repository data:

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `agent_runs/AGENT-RUN-0018/metrics.json`
- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`

It does not fetch live data, score `PRED-0063` through `PRED-0068`, create or
edit prediction registry entries, modify canonical results, promote claims, or
write knowledge artifacts.

## Subset Design

The audit reports the primary holdout, magic-N, magic-Z, near-magic,
double-magic, and deterministic non-magic A-matched control subsets.

| Subset | Rows | Sparse warning |
| --- | ---: | --- |
| `primary_holdout` | 295 | no |
| `magic_n` | 17 | no |
| `magic_z` | 13 | no |
| `near_magic` | 126 | no |
| `double_magic` | 5 | yes |
| `non_magic_matched_magic_n` | 17 | no |
| `non_magic_matched_magic_z` | 13 | no |
| `non_magic_matched_near_magic` | 126 | no |
| `non_magic_matched_double_magic` | 5 | yes |

The non-magic controls are deterministic nearest-`A` matches without
replacement. They are diagnostic matched subsets, not causal controls.

## Results

Negative delta means lower retrospective MAE than the frozen baseline.
Positive delta means regression.

| Candidate | Magic-N ΔMAE MeV | Magic-Z ΔMAE MeV | Near-magic ΔMAE MeV | Double-magic ΔMAE MeV | Matched-N ΔMAE MeV | Matched-Z ΔMAE MeV | Direction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `FULLKNOWN-SHELL-001` | -0.326992 | -0.158489 | -0.224264 | -0.412072 | -0.197071 | +0.057011 | `NEUTRON_DOMINANT` |
| `FULLKNOWN-SHELL-002` | -0.376547 | -0.001094 | -0.169194 | -0.293656 | -0.190732 | +0.025462 | `NEUTRON_DOMINANT` |
| `FULLKNOWN-SHELL-003` | -0.512894 | -0.022180 | -0.156882 | -0.323638 | -0.395316 | +0.052776 | `NEUTRON_DOMINANT` |
| `FULLKNOWN-SHELL-004` | +0.453871 | +0.459333 | +0.322204 | +0.697641 | +0.197071 | +0.079456 | `NO_MAGIC_AXIS_SUPPORT` |
| `FULLKNOWN-SHELL-005` | -0.000197 | -0.000021 | -0.000216 | -0.000151 | -0.000120 | +0.000011 | `SYMMETRIC_OR_TIED` |
| `FULLKNOWN-SHELL-006` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `NO_MAGIC_AXIS_SUPPORT` |

## Interpretation

`NEUTRON_DOMINANT_BUT_SPARSE`

All three primary shell-axis candidates improve magic-N more than magic-Z
under the predeclared `0.05 MeV` directional margin. The neutron-axis-only
candidate has the strongest magic-N improvement, but even the proton-axis
feature improves magic-N more than magic-Z on this committed retrospective
surface.

The sign-inverted control regresses both magic axes, and the shuffled-feature
control remains near the noise floor. The baseline reference stays exactly at
zero deltas.

This is not a broad claim about shell structure. Magic-N has 17 rows,
magic-Z has 13 rows, and double-magic has only 5 rows. The correct use is as a
bounded sandbox diagnostic for follow-up review, not as a registry expansion,
future-measurement reveal, or claim promotion.

## Limitations

- Magic-N, magic-Z, and double-magic subsets are sparse.
- The double-magic and matched double-magic panels have fewer than 10 rows and
  are explicit sparse diagnostics.
- Matched controls are deterministic nearest-`A` non-magic subsets, not causal
  controls.
- Candidate coefficients are fit on only the 11-row NMD-0002 residual slice.
- No prediction registry, canonical result, claim, or knowledge artifact is
  updated.

## Verdict

`NEUTRON_DOMINANT_BUT_SPARSE`

The shell-axis support is directionally stronger on magic-N than magic-Z for
all three primary candidates, while controls remain conservative. The result
must stay sandbox-only because the relevant magic subsets are sparse and the
coefficient-stability warning from `TASK-0316` still applies.
