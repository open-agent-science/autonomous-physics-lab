# RESULT-0027 Gate-B Workflow Repackage

- Task: `TASK-0959`
- Result: `RESULT-0027`
- Artifact: `results/EXP-0021/RUN-0001/result.yaml`
- Prior blocker: formal Gate B helper rejected the direct packaging-script command as `unsupported-command`
- New replay command: `physics-lab run examples/exoplanet_null_baseline_result.yaml`
- Replayer: `gladunrv` / Codex / GPT-5
- Publisher: `akutenyov` / Codex / GPT-5
- Gate B helper status: `PASS`

## Scope

This bridge changes packaging and transparency only. It does not fetch live
NASA Exoplanet Archive data, add EXO-0003 rows, refit or rescore CK17-style
baselines, pool minimum-mass rows, change RESULT-0027 metrics, change the
`INCONCLUSIVE` verdict, or create/promote any `CLAIM-*`, `KNOW-*`, or `PRED-*`
artifact.

## What Changed

RESULT-0027 now records a Gate-B-safe workflow command:

```bash
physics-lab run examples/exoplanet_null_baseline_result.yaml
```

The legacy `scripts/package_exoplanet_null_baseline_result.py --write` entrypoint
is kept as a compatibility wrapper, but the canonical replay route lives in
`physics_lab/workflows/exoplanet_null_baseline_result.py`.

The artifact also surfaces fair-null comparator rows in `comparison_summary` and
`report.md`. The existing nearest-radius control remains explicitly labeled as a
diagnostic control that uses observed radius and is not a prospective or
deployable predictor. The fair-null rows show the relevant context directly in
the artifact: `nearest_mass_neighbor` and `per_class_median` trail the frozen
CK17 baseline in three of four highlighted true-mass slices.

## Formal Gate B Run

Command:

```bash
python scripts/apl_validate_agent_published_result.py \
  results/EXP-0021/RUN-0001/result.yaml \
  --root . \
  --output-dir /private/tmp/apl-task0959-gateb-final \
  --validator-contributor-id gladunrv \
  --validator-github-username gladunrv \
  --validator-agent-tool Codex \
  --validator-model GPT-5 \
  --json
```

Outcome:

- Status: `PASS`
- Numeric metric fields compared: 52
- Max absolute drift: `0.0`
- Tolerance: `1.0e-09`
- Non-blocking warning: same agent tool (`Codex`) as publisher, different contributor

The result now records `review_tier: AGENT_VALIDATED` with
`validation_independence: independent`. The independence classification is at
the contributor/human level: publisher `akutenyov` differs from replayer
`gladunrv`; the same-tool warning remains disclosed in the validation note.

## Output-Routing Summary

- Canonical destination: updated `results/EXP-0021/RUN-0001/result.yaml` and this bridge note.
- Review tier: `AGENT_VALIDATED` by formal Gate B replay; not maintainer-reviewed.
- Gate A status: previously `PASS`; unchanged.
- Gate B status: `PASS`.
- Verdict impact: none; `best_verdict` remains `INCONCLUSIVE`.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: no formal Gate B command-shape blocker remains for RESULT-0027.

## Verdict

`RESULT0027_GATEB_WORKFLOW_REPACKAGE_PASS`: RESULT-0027 is now replayable through
the canonical safe workflow route, formal Gate B passes with zero numeric drift,
and the artifact exposes the fair-null comparison surface without changing the
scientific verdict or making a mass-radius claim.
