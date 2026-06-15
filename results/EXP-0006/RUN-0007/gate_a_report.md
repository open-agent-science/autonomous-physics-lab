# RESULT-0020 Gate A Report

**Task:** `TASK-0750`
**Artifact:** `results/EXP-0006/RUN-0007/result.yaml`
**Decision:** `PASS`

## Deterministic Replay

Published command:

```text
python -m physics_lab.cli run examples/dimensional_analysis_live_74.yaml --output-dir results/EXP-0006/RUN-0007
```

The same config was replayed to a separate temporary output directory. The
canonical and replayed `metrics.json` files were byte-identical:

```text
canonical sha256: b66a82ec687c144956baba763e5ee7b64ea9d44ed468793ac5679937da26b4f3
replay sha256:    b66a82ec687c144956baba763e5ee7b64ea9d44ed468793ac5679937da26b4f3
match: true
```

## Published Metrics

| Metric | Value |
| --- | ---: |
| Frozen challenge items | 74 |
| Agreement | 74/74 |
| Agreement fraction | 1.0 |
| Computed VALID | 37 |
| Computed INVALID | 35 |
| Computed SUSPICIOUS | 2 |
| Computed INCONCLUSIVE | 0 |
| Remaining disagreements | 0 |

Frozen fixture SHA-256:
`2717de440c8718e24d341be0037bbeda043abca0fe3381a5e2b5842f701d3b42`.
It matches the live challenge-set source at the pinned publication code commit
`f47c86ca4df8b059a5b9482c758bc432a82feed0`.

## Gate A Checker

Command:

```text
python scripts/apl_check_result_publication.py results/EXP-0006/RUN-0007/result.yaml
```

Output:

```text
PASS results/EXP-0006/RUN-0007/result.yaml (result)
```

The artifact records a deterministic command, verification checks, input
hashes, limitations, engine version, code commit, protected-result check, and
the required `agent_proposal_evaluation` block.

## Routing

- Review tier: `AGENT_PUBLISHED`.
- Gate A: pass.
- Gate B: not attempted.
- Hypothesis impact: evidence reference only; `HYP-0006` status and verdict are
  unchanged.
- Claim impact: none; `CLAIM-0005` remains unchanged and `DRAFT`.
- Knowledge impact: none.
- Protected artifact impact: `RESULT-0007`, `EXP-0006/RUN-0006`, and
  `results/golden-results.yaml` are unchanged.
- Trust qualifier: agent-published, not yet independently validated or
  maintainer-reviewed.
