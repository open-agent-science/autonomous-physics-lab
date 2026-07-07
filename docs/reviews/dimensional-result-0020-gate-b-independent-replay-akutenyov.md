# RESULT-0020 Independent Gate B Replay By Akutenyov

- Task: `TASK-0948`
- Result: `RESULT-0020`
- Artifact: `results/EXP-0006/RUN-0007/result.yaml`
- Replay date: 2026-07-07
- Gate: Gate B independent replay
- Replay status: `PASS`

## Replayer Identity

The identity was recorded before the replay command was run.

| Field | Value |
| --- | --- |
| contributor_id | `akutenyov` |
| github_username | `akutenyov` |
| agent_tool | `Codex` |
| model | `GPT-5` |
| validation_independence | `independent` |

The replayer is a different human from both the original RESULT-0020
publisher (`romanhladun24-dot`) and the TASK-0782 packaging-fix /
TASK-0916 blocker author (`gladunrv`). The replay tool is non-Claude, as
required by TASK-0948.

## Scope Guard

This task replays only the committed RESULT-0020 command from its pinned input
hashes. It must not change metrics, challenge-set rows, verification values,
`best_verdict`, CLAIM-0005, or any knowledge artifact. Dimensional agreement
is formula-quality evidence only; it is not evidence of numerical accuracy,
empirical validity, or physical correctness.

## Replay Command

```powershell
python scripts/apl_validate_agent_published_result.py `
  results/EXP-0006/RUN-0007/result.yaml `
  --root . `
  --output-dir .gate-b-replay-task0948 `
  --tolerance 1e-9 `
  --validator-contributor-id akutenyov `
  --validator-github-username akutenyov `
  --validator-agent-tool Codex `
  --validator-model GPT-5 `
  --expect-status PASS `
  --json
```

The helper replayed the result's committed command:

```text
python -m physics_lab.cli run examples/dimensional_analysis_live_74.yaml --output-dir results/EXP-0006/RUN-0007
```

## Replay Outcome

- Status: `PASS`; `ok: true`; exit code `0`.
- Compared metrics: `17`.
- Metrics within tolerance: `17/17`.
- Maximum absolute drift: `0.0`.
- Tolerance: `1.0e-9`.
- Contested report: none.
- Verdict: `VALID`, unchanged.
- Frozen scope: 74 items; 74 agreements, 0 disagreements, 0 inconclusive.

The helper emitted one non-blocking `same-agent-tool` warning because Codex
was also used by the original publisher. Under the R1 policy, independence is
classified at the human level: `akutenyov` is different from both the
publisher and the packaging-fix author, so the validation record correctly
uses `validation_independence: independent`.

All compared metric deltas were exactly zero. The paths covered the comparison
summary, uncertainty summary, item counts, agreement fraction and threshold,
and zero-disagreement count.

## Artifact Update

The clean `PASS` applies the permitted metadata-only transition:

- `review_tier: AGENT_PUBLISHED` -> `AGENT_VALIDATED`;
- Gate B gates recorded under `agent_proposal_evaluation`;
- `validation_record` records identity, human-level independence, timestamp,
  command, tolerance, metric count, and zero drift.

No metric, challenge-set row, verification value, command, input hash,
`best_verdict`, CLAIM-0005 content, or knowledge artifact changed.

## Output Routing

- Task verdict: `not_applicable`; this is validation metadata, not a new
  scientific result.
- Canonical destinations: this replay note and the metadata block of
  `results/EXP-0006/RUN-0007/result.yaml`.
- Review tier: `AGENT_VALIDATED`.
- Gate A: previously passed; unchanged.
- Gate B: `PASS`, 17 metrics, maximum drift `0.0`, tolerance `1.0e-9`.
- Validation independence: `independent`.
- Claim impact: none; CLAIM-0005 is unchanged.
- Knowledge impact: none.
- Scientific-content impact: none.
- Limitation: the replay confirms deterministic dimensional-label agreement
  only. Dimensional validity does not establish physical correctness.
