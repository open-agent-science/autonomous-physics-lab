# FIRAS/Wien RESULT-0023 Gate B Replay

Task: `TASK-0885`
Result: `RESULT-0023`
Canonical artifact: `results/EXP-0016/RUN-0001/result.yaml`
Verdict: `GATE_B_PASS_AGENT_VALIDATED`

## Scope

This note records an independent Gate B replay of the workflow-packaged FIRAS/Wien self-consistency result. The replay uses the RESULT's recorded safe command and writes output to a non-canonical replay directory.

This task does not refit the reference temperature, repin FIRAS rows, change wavelength-domain/Jacobian semantics, change controls or tolerances, edit RESULT metrics, create a CLAIM/KNOW/PRED artifact, or claim independent empirical validation of Wien displacement. The result remains a scoped FIRAS spectral-domain self-consistency check with an explicit circularity caveat because the reference temperature is FIRAS-derived.

## Replay Command

```bash
python3 scripts/apl_validate_agent_published_result.py   results/EXP-0016/RUN-0001/result.yaml   --output-dir .pytest-basetemp/task0885-gateb-replay   --validator-contributor-id romanhladun24-dot   --validator-github-username romanhladun24-dot   --validator-agent-tool Codex   --validator-model GPT-5   --json
```

The helper replayed the recorded safe workflow command:

```bash
physics-lab run examples/textbook_firas_wien_peak_consistency.yaml
```

Replay output directory: `.pytest-basetemp/task0885-gateb-replay`

## Gate B Outcome

- Status: `PASS`
- Issues: none
- Contested report: none
- Best verdict unchanged: `VALID_IN_RANGE`
- Review tier update: `AGENT_PUBLISHED` to `AGENT_VALIDATED`
- Tolerance: `1.0e-09`
- Compared numeric fields: `27`
- Maximum absolute numeric drift: `9.275010772434589e-20`
- Original publisher: `gladunrv` / `Claude Code`
- Replayed by: `romanhladun24-dot` / `Codex`

## Metric Drift Table

| Field | Expected | Observed | Absolute drift |
| --- | ---: | ---: | ---: |
| `verification.checks[1].metrics.reference_wavelength_peak_m` | `0.001063215270337702` | `0.001063215270337702` | `0.0` |
| `verification.checks[1].metrics.wavelength_domain_peak_interpolated_m` | `0.0010641903994487105` | `0.0010641903994487105` | `0.0` |
| `verification.checks[1].metrics.raw_bin_relative_difference` | `0.01307103781199158` | `0.01307103781199158` | `0.0` |
| `verification.checks[1].metrics.interpolated_relative_difference` | `0.000917151152935081` | `0.000917151152935081` | `0.0` |
| `verification.checks[2].metrics.controls_all_passed` | `1.0` | `1.0` | `0.0` |
| `comparison_summary[0].absolute_difference` | `9.751291110085e-07` | `9.751291110084073e-07` | `9.275010772434589e-20` |

All compared numeric fields are within the declared absolute tolerance. The largest drift is floating-point serialization noise far below tolerance.

## Boundary Checks

- Input hashes: verified by the replay helper before command execution.
- Code reference: preserved as `physics_lab/engines/textbook_wien_firas_peak.py`.
- Reference temperature: unchanged at `2.72548 K`.
- FIRAS rows: unchanged; no live fetch or source repinning.
- Domain contract: unchanged wavelength-domain peak after the declared `B_nu -> B_lambda` Jacobian.
- Controls: unchanged; all four controls remain passing.
- Limitations: preserved and tightened to say agent-validated by replay, not maintainer-reviewed.

## Output Routing

- Task verdict: `GATE_B_PASS_AGENT_VALIDATED`.
- Canonical destination: `results/EXP-0016/RUN-0001/result.yaml` plus this review note.
- Review tier: `AGENT_VALIDATED`; this is independent replay, not maintainer endorsement.
- Gate A status: existing `PASS` from the original AGENT_PUBLISHED result package.
- Gate B status: `PASS`; replay metadata is recorded under `agent_proposal_evaluation.validation_record`.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Result impact: review-tier and validation-record metadata only; RESULT-0023 metrics and verdict are unchanged.
- Public wording: still FIRAS/Wien spectral-domain self-consistency only, with no universal textbook-law or independent Wien-displacement claim.
- Remaining blocker: maintainer review is required for any `MAINTAINER_REVIEWED` tier, claim status change, or knowledge entry.
