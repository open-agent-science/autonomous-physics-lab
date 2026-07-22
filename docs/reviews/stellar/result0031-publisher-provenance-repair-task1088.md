# RESULT-0031 Publisher Provenance Repair

Task: `TASK-1088`

## Verdict

`PUBLISHER_PROVENANCE_REPAIRED_NO_REPLAY`

The original publisher identity for `RESULT-0031` was recovered from the
public metadata of merged task PR
[`#1609`](https://github.com/open-agent-science/autonomous-physics-lab/pull/1609).
The repair adds only the schema-permitted `published_by` block. It does not run
Gate B, establish replay independence, or change any scientific content.

## Durable Record Check

The GitHub PR record was inspected on 2026-07-22 and agreed on every required
identity field:

| Field | Durable record |
| --- | --- |
| PR | `#1609` |
| State | merged on `2026-07-19T14:28:00Z` |
| Task | `TASK-1050` |
| Result | `RESULT-0031` |
| Author login | `gladunrv` |
| Contributor ID | `gladunrv` |
| Branch | `agent/gladunrv/codex/task-1050-run-the-frozen-stellar-relation-on-the-source-curated-chara-comp` |
| PR head commit | `598c6cd054c9715d6028020f2210fd537611aab7` |
| Agent tool | `Codex` |
| Model/version | `GPT-5 Codex` |

The PR title, body, linked task, result summary, branch, author, and merged
state were mutually consistent. Had any of those fields disagreed, the task
would have stopped with the canonical result unchanged.

## Applied Repair

The following identity was added under
`agent_proposal_evaluation.published_by`:

```yaml
contributor_id: gladunrv
github_username: gladunrv
agent_tool: Codex
model_version: GPT-5 Codex
```

The pre-repair result blob was
`c7e99408f1c193ca7ed420e0d9694faa0bf537d8`. The diff changes no metric,
input hash, threshold, model identifier, limitation, verdict, or review tier.
`RESULT-0031` remains `AGENT_PUBLISHED` and `INCONCLUSIVE`.

## Remaining Gate

This repair only makes identity-aware replay admissible. A future executor for
`TASK-1089` must pass the repository independence check against
`gladunrv / Codex / GPT-5 Codex` before computing replay metrics. Only an exact
independent Gate B pass may upgrade the result to `AGENT_VALIDATED`.

The Gate B helper was exercised with the recovered publisher identity and now
stops at `self-validation-forbidden`, rather than the former missing-publisher
metadata error. No replay metrics were computed during that check.

No refit, margin relaxation, added CHARA row, claim promotion, or universal
stellar-relation wording is authorized.

## Output Routing

- Canonical destination: publisher metadata on the existing `RESULT-0031`.
- Review tier: unchanged at `AGENT_PUBLISHED`.
- Gate A: unchanged from the original publication.
- Gate B: not attempted.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: independent replay remains required for validation.
