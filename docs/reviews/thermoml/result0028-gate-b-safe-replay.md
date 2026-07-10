# ThermoML RESULT-0028 Gate-B-Safe Replay

- Task: `TASK-0985`
- Result artifact: `results/EXP-0020/RUN-0002/result.yaml`
- Existing tier: `AGENT_PUBLISHED`
- Verdict: `GATE_B_BLOCKED`

## Summary

The committed RESULT-0028 metrics reproduce byte-for-byte through the recorded
packaging command path, but the formal Gate B helper blocks the replay because
the RESULT records a bespoke packaging-script command rather than an allowed
`physics_lab.cli run` workflow command.

No RESULT-0028 metric, verdict, review tier, claim, knowledge, or fixture file is
changed by this task. The blocker is replay-command shape, not metric drift.

## Formal Gate B Helper

Command:

```bash
python scripts/apl_validate_agent_published_result.py \
  results/EXP-0020/RUN-0002/result.yaml \
  --output-dir /private/tmp/apl-task-0985-gateb-replay \
  --validator-contributor-id gladunrv \
  --validator-github-username gladunrv \
  --validator-agent-tool "Codex Desktop" \
  --validator-model "GPT-5" \
  --expect-status BLOCKED \
  --json
```

Helper status: `BLOCKED`.

Helper issues:

| Code | Severity | Meaning |
| --- | --- | --- |
| `same-contributor` | warning | Replay uses the same contributor id with a different agent tool path; acceptable for maintainer-run reproducibility but not independent-human validation. |
| `unsupported-command` | error | Gate B only supports safe `physics_lab.cli run` commands, not arbitrary shell or packaging-script commands. |

Because the helper stops at command-shape validation, it does not create a
`validation_record` and RESULT-0028 must remain `AGENT_PUBLISHED`.

## Recorded Command Path Check

The recorded RESULT-0028 packager was replayed into a disposable directory with
the original pinned commit:

```bash
python scripts/package_thermoml_esters_lactones_negative_result.py \
  --write \
  --git-commit 269aa0276bc2997e5d41709e76501acbd83bb76d \
  --output-dir /private/tmp/apl-task-0985-result0028-recorded-path-replay
```

The replayed `metrics.json` matched the committed
`results/EXP-0020/RUN-0002/metrics.json` exactly.

| Metric | Committed | Replayed | Delta |
| --- | ---: | ---: | ---: |
| `family_margin_vs_best_non_oracle_k` | `-5.549755` | `-5.549755` | `0.0` |
| `required_family_survival_margin_k` | `5.0` | `5.0` | `0.0` |
| `family_margin_shortfall_k` | `10.549755` | `10.549755` | `0.0` |
| `family_row_count` | `5` | `5` | `0.0` |
| `family_scores.joback.mae_k` | `26.134` | `26.134` | `0.0` |
| `family_scores.molecular_weight_only.mae_k` | `20.584245` | `20.584245` | `0.0` |
| `family_scores.global_median.mae_k` | `96.716` | `96.716` | `0.0` |
| `family_scores.within_family_constant.mae_k` | `81.6544` | `81.6544` | `0.0` |
| `family_scores.nearest_homolog.mae_k` | `78.028` | `78.028` | `0.0` |
| `family_scores.shuffled_group_counts.mae_k` | `146.142` | `146.142` | `0.0` |

Full machine comparison result: `metrics_equal True`.

## Interpretation Boundary

This replay confirms that the negative/control RESULT-0028 package is
deterministic from committed bytes under its recorded packager. It does not
clear Gate B because the recorded command is not on the safe replay allowlist.
The esters/lactones failed-family memory remains scoped to the five rows inside
the committed 40-row ThermoML `Tb` fixture.

No broad property-estimation, chemical-design, process-design, safety,
synthesis, universal Joback, claim, or knowledge statement is made.

## Output Routing

- Canonical destination: review note only, this file.
- Review tier: RESULT-0028 remains `AGENT_PUBLISHED`.
- Gate A status: already passed by the existing RESULT-0028 package.
- Gate B status: `BLOCKED` on formal helper command shape; recorded-path metrics
  drift is `0.0`.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: a Gate-B-safe workflow bridge is required before
  RESULT-0028 can be upgraded to `AGENT_VALIDATED`.
