# Nuclear F2 Diagnostic Result Publication Preflight

Task: `TASK-0633`
Domain: Nuclear Mass Surface
Mode: result-publication preflight
Verdict: `GATE_A_PASS_DIAGNOSTIC_RESULT_PUBLISHED`

## Scope

This review starts from the committed TASK-0625 artifacts only:

- `agent_runs/AGENT-RUN-0068/metrics.json`
- `agent_runs/AGENT-RUN-0068/report.md`
- `docs/reviews/nuclear-f2-survival-margin-component-ablation.md`
- `scripts/run_nuclear_f2_component_ablation.py`

No F2 search, feature-family tuning, reveal scoring, prediction entry, claim
file, or knowledge file is created.

## Gate A Check

Gate A is satisfied for a scoped diagnostic RESULT artifact.

| Gate A requirement | Status | Evidence |
| --- | --- | --- |
| Deterministic run | PASS | `scripts/run_nuclear_f2_component_ablation.py` replayed to `D:\Python\APLab\tmp\TASK-0633-replay`. |
| Verification block populated | PASS | `results/EXP-0012/RUN-0002/result.yaml` contains deterministic replay, survival-margin, and protected-result checks. |
| Input hashes recorded | PASS | `results/EXP-0012/RUN-0002/inputs/config.yaml` records dataset, gate, manifest, control, replay, decision, and script hashes. |
| Limitations listed | PASS | Result limitations preserve diagnostic-only and no-reveal/no-claim boundaries. |
| Engine version and git commit pinned | PASS | `engine_version: 0.1.0`; `git_commit: 8587687b69b8847c6257478e126ae0ca86b2903d`. |
| Schema validation passes | PASS | `validate-repo --strict --fail-on-warnings` passed after adding the result and hypothesis evidence reference. |
| No protected artifact rewrite | PASS | `RESULT-0018` is new and not listed in `results/golden-results.yaml`. |
| No forbidden overclaim wording | PASS | Result wording stays diagnostic-only. |
| Dataset provenance valid | PASS | NMD-0003 dataset, split gate, F2 manifest, and control/replay metrics are hash-pinned. |

The replayed metric/report byte hashes differ from committed AGENT-RUN-0068
because the committed files use CRLF line endings and replay output used LF.
`diff --strip-trailing-cr` found no content differences for `metrics.json` or
`report.md`.

## Published Result

Prepared artifact:

```text
results/EXP-0012/RUN-0002/result.yaml
```

Result ID: `RESULT-0018`

Review tier: `AGENT_PUBLISHED`

Best verdict: `INCONCLUSIVE`

Reason: the full F2 reference remains replayable, but no component-ablation
variant clears the predeclared controls-first survival margin. This is
diagnostic publication memory, not claim support.

## Metrics Preserved

- Full F2 reference full-known MAE improvement: `0.200411` MeV.
- Best control full-known MAE improvement: `0.001151` MeV.
- Full F2 minus best control: `0.199260` MeV.
- Predeclared survival margin: `0.250000` MeV.
- Best single-component variant: `only_magic_n_near`.
- Best single-component full-known MAE improvement: `0.074761` MeV.
- Clearing component variants: none.

## Output Routing

Task verdict: `GATE_A_PASS_DIAGNOSTIC_RESULT_PUBLISHED`.

Canonical destination: `results/EXP-0012/RUN-0002/result.yaml`.

Review tier: `AGENT_PUBLISHED`.

Gate A status: pass.

Gate B status: not attempted.

Claim impact: none.

Knowledge impact: none.

Hypothesis evidence routing: `RESULT-0018` is referenced from `HYP-0012` so the
result is not an orphan registry artifact; hypothesis status and wording are
unchanged.

Limitations: no post-AME2020 reveal scoring; no prediction; no claim or
knowledge promotion; no F2 feature search or tuning; not independently
validated.
