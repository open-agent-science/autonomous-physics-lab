# Nuclear Shell-Axis Isotope-Chain Transfer Audit

**Task:** `TASK-0323`
**Agent run:** `agent_runs/AGENT-RUN-0023/`
**Script:** `scripts/run_nuclear_shell_axis_chain_transfer_audit.py`
**Metrics:** `agent_runs/AGENT-RUN-0023/metrics.json`
**Evidence class:** sandbox-only retrospective isotope-chain transfer audit

## Scope

This review asks whether the shell-axis signal transfers across isotope chains
or hides chain-local regressions. It uses only committed repository inputs:

- `agent_runs/AGENT-RUN-0018/metrics.json`
- `agent_runs/AGENT-RUN-0020/metrics.json`
- `agent_runs/AGENT-RUN-0021/metrics.json`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`

No live data were fetched. No prediction registry entries, reveal scores,
canonical results, claims, or knowledge artifacts were created or updated.

## Method

The audit groups committed full-known rows by isotope chain using fixed
proton number `Z`. Chains with fewer than three committed rows are flagged as
diagnostics, not support surfaces.

For each chain, the audit reports:

- row count and `A` range;
- frozen baseline MAE;
- per-candidate shell-axis delta MAE;
- best non-shell control delta MAE from committed TASK-0317 control families;
- whether the best shell-axis candidate beats the best non-shell control.

## Results

The chain-transfer verdict is `MIXED_CHAIN_LOCAL`.

| Metric | Value |
| --- | ---: |
| Total chains | 74 |
| Interpretable chains | 48 |
| Too-sparse diagnostic chains | 26 |
| Chains improved by best shell candidate | 21 |
| Chains regressed by best shell candidate | 20 |

Candidate-level transfer is also mixed:

| Candidate | Improved chains | Regressed chains | Improvement rate |
| --- | ---: | ---: | ---: |
| `FULLKNOWN-SHELL-001` | 19 | 24 | 0.396 |
| `FULLKNOWN-SHELL-002` | 18 | 26 | 0.375 |
| `FULLKNOWN-SHELL-003` | 18 | 26 | 0.375 |

Negative deltas mean lower retrospective MAE than the frozen baseline.
Positive deltas are regressions.

## Interpretation

The shell-axis lane is not uniformly chain-transferable. Some chains improve,
but many interpretable chains regress and several non-shell controls beat the
best shell-axis candidate chain-by-chain. This weakens any broad aggregate
support framing and keeps the lane in sandbox diagnostics.

## Verdict

`MIXED_CHAIN_LOCAL`

The shell-axis signal should be treated as chain-local and mixed until a
future reviewed task can explain or constrain the regressing chains. This is
sandbox-only evidence, not a promoted claim.

## Limitations

- Chains with fewer than three committed rows are diagnostic only.
- Best non-shell controls reuse TASK-0317 definitions; no new formula family
  is fit.
- Shell-axis and control coefficients are fit on the 11-row NMD-0002 residual
  slice.
- The audit is retrospective over committed repository data, not a future-data
  reveal.
- No prediction registry entry, canonical result, claim, or knowledge artifact
  is promoted.
