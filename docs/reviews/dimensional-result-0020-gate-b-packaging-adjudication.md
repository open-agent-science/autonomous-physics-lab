# Dimensional RESULT-0020 Gate B Packaging Adjudication

- Task: `TASK-0782`
- Result: `RESULT-0020`
- Input evidence: `TASK-0766` contested replay and `TASK-0807` adjudication brief
- Verdict: `GATE_B_CORE_PASS_WITH_GATE_A_PACKAGING_SCOPE`

## Scope

This adjudication resolves the RESULT-0020 Gate B packaging contest without
changing dimensional validator metrics, challenge-set rows, `best_verdict`,
`CLAIM-0005`, or any knowledge artifact.

The contested replay already established the scientific core: the frozen
74-item dimensional validator replay reproduced the committed metrics with zero
numeric drift. The remaining issue was provenance packaging: three published
`verification.checks` entries were hand-authored Gate A publication checks, not
checks emitted by RESULT-0020's recorded replay command.

## Decision

This task implements the TASK-0807 Option A path: Gate B compares the
replay-emitted core checks and metrics, while explicitly labelled Gate A
packaging annotations are excluded from numeric replay comparison.

The following RESULT-0020 checks are now labelled with
`gate_b_scope: gate_a_packaging` and
`gate_b_treatment: publication_packaging_annotation_not_replay_metric`:

| Check | Reason |
| --- | --- |
| `zero_disagreement_ledger` | The underlying `disagreement_count: 0` is reproduced in metrics, but this named publication wrapper is not emitted by the recorded command. |
| `frozen_input_checksum` | The checksum statement is a Gate A publication assertion; the recorded dimensional workflow does not emit this named check. |
| `protected_result_not_rewritten` | This is protected-artifact packaging metadata, not a dimensional workflow metric. |

`physics_lab/registry/agent_replay_validation.py` now skips numeric comparison
for `verification.checks[*]` entries only when the published artifact explicitly
marks that check with `gate_b_scope: gate_a_packaging`. Unlabelled missing or
drifting metrics remain contested.

## Gate B Replay Outcome

Command:

`python scripts/apl_validate_agent_published_result.py results/EXP-0006/RUN-0007/result.yaml --root . --output-dir <disposable-output> --validator-contributor-id svitidaniuk-pixel --validator-github-username svitidaniuk-pixel --validator-agent-tool Codex --validator-model GPT-5 --json`

Outcome:

| Field | Value |
| --- | --- |
| Helper status | `PASS` |
| Compared numeric metrics | `16` |
| Max absolute drift | `0.0` |
| Stable verdict | `VALID` |
| Replay warning | `same-agent-tool` because both publisher and validator used Codex, with different contributors |
| Contested report | none |

The replay compared the four code-emitted verification checks plus the core
comparison and uncertainty metrics. The previously contested packaging-only
check metrics were intentionally out of Gate B numeric scope after explicit
metadata labelling.

## Result Metadata Impact

This PR does not change `review_tier: AGENT_PUBLISHED` to `AGENT_VALIDATED`.
The reason is procedural, not numeric: this PR both changes the Gate B
comparison policy and relabels RESULT-0020 packaging metadata. Per the
result-promotion protocol, a pure `AGENT_VALIDATED` upgrade should only add
Gate B validation metadata and bump review tier, without changing material
result payload fields. A maintainer or follow-up validation-only PR can apply
that tier update after accepting this packaging-scope policy.

## Limitations Preserved

- RESULT-0020 remains dimensional-consistency evidence over the frozen 74-item
  fixture, not proof of numerical correctness, empirical validity, physical
  truth, or general formula quality.
- `CLAIM-0005` is unchanged and remains conservative.
- The three packaging checks remain useful Gate A publication annotations, but
  are not replay-emitted dimensional workflow metrics.
- Cross-tool validation would still be stronger than the same-agent-tool replay
  warning recorded here.

## Output Routing

- Canonical destination: this review note plus the explicit packaging-scope
  labels in `results/EXP-0006/RUN-0007/result.yaml`.
- Review tier: unchanged; `RESULT-0020` remains `AGENT_PUBLISHED` in this PR.
- Gate A status: previously passed; three checks are now explicitly labelled as
  Gate A packaging annotations.
- Gate B status: `PASS` for the reproducible core after packaging-scope
  relabel; max numeric drift `0.0` across 16 compared metrics.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Result metric impact: none.
- Publication blocker: maintainer acceptance is needed before any follow-up
  validation-only `AGENT_VALIDATED` metadata bump or stronger public wording.

## Final Verdict

`RESULT-0020` is no longer contested on core Gate B replay after explicitly
separating Gate A packaging annotations from replay-emitted dimensional metrics.
The result remains `AGENT_PUBLISHED` pending maintainer acceptance of the
packaging-scope policy and any later validation-only tier update.