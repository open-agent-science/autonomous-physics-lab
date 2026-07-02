# RESULT-0020 Dimensional Validator Gate B Validation-Independence Blocker

- Task: `TASK-0916`
- Result: `RESULT-0020`
- Artifact: `results/EXP-0006/RUN-0007/result.yaml`
- Helper: `scripts/apl_validate_agent_published_result.py`
- Gate B engine: `physics_lab/registry/agent_replay_validation.py`
- Original publisher: `romanhladun24-dot` (agent tool Codex, GPT-5), task `TASK-0750`
- Gate B replay re-run verdict: **`PASS` (clean replay, zero numeric drift)**
- Tier decision this task: **no promotion.** RESULT-0020 stays at
  `AGENT_PUBLISHED`. The metadata-only `AGENT_VALIDATED` bump is deferred to an
  independent replayer (see the blocker below).

## Scope

This task decides whether the `AGENT_PUBLISHED` Dimensional Analysis Validator
live 74-item replay result should be promoted to `AGENT_VALIDATED` by a
metadata-only tier update, after the merged `TASK-0782` packaging adjudication
made Gate B replay cleanly.

It does **not** re-run a new dimensional challenge search, change RESULT-0020
metrics, change the `VALID` software/convention verdict, change any challenge-set
(fixture) row, change any verification value, promote `CLAIM-0005`, create
`KNOW-*` knowledge artifacts, create predictions, broaden the benchmark, or create
any sandbox `agent_runs/AGENT-RUN-*`. RESULT-0020's committed artifact is
byte-unchanged by this task.

## Gate B Re-Run (Clean Disposable Directory)

The canonical Gate B helper was re-run against the unmodified committed artifact
from a clean, disposable temporary output directory:

```bash
python3 scripts/apl_validate_agent_published_result.py \
  results/EXP-0006/RUN-0007/result.yaml \
  --root . \
  --output-dir <clean-gate-b-tmp-dir> \
  --validator-contributor-id gladunrv \
  --validator-github-username gladunrv \
  --validator-agent-tool "Claude Code" \
  --validator-model "Claude Opus 4.8" \
  --json
```

The helper replayed the RESULT's recorded safe command:

```bash
python -m physics_lab.cli run examples/dimensional_analysis_live_74.yaml
```

Outcome:

- Status: **`PASS`**, `ok: true`, exit code `0`.
- **17** numeric metrics compared; **maximum absolute drift `0.0`** at tolerance
  `1.0e-9`. Every compared metric matched exactly.
- Zero issues (no errors, no warnings). The engine's replay-identity independence
  check reported no overlap, because the replay identity (`gladunrv` / Claude
  Code) differs from the recorded original publisher (`romanhladun24-dot` /
  Codex) on both the contributor and the agent-tool axis.
- The replayed `verification`, `comparison_summary`, `uncertainty_summary`, and
  `best_verdict` blocks are deep-equal to the committed artifact; all stable
  string identities (`result_id`, `experiment_id`, `hypothesis_id`, `task_id`,
  `run_id`) match.
- The helper emitted an `AGENT_VALIDATED` validation-record draft (not applied by
  this task; see the blocker).

## Metric-Drift Table

Re-run from a clean directory versus the committed RESULT-0020 payload. All
compared numeric metrics have zero drift; there are **no contested fields**.

| Metric path | Expected | Observed | Abs drift | Within tol (1e-9) |
| --- | --- | --- | --- | --- |
| `comparison_summary[0].reference_value` | 0.9 | 0.9 | 0.0 | yes |
| `comparison_summary[0].observed_value` | 1.0 | 1.0 | 0.0 | yes |
| `comparison_summary[0].absolute_difference` | 0.1 | 0.1 | 0.0 | yes |
| `comparison_summary[0].relative_difference` | 0.111111 | 0.111111 | 0.0 | yes |
| `uncertainty_summary.observed_uncertainty` | 0.0 | 0.0 | 0.0 | yes |
| `uncertainty_summary.reference_uncertainty` | 0.0 | 0.0 | 0.0 | yes |
| `uncertainty_summary.combined_uncertainty` | 0.0 | 0.0 | 0.0 | yes |
| `verification.checks[0].metrics.item_count` | 74 | 74 | 0.0 | yes |
| `verification.checks[1].metrics.declared_total_items` | 74 | 74 | 0.0 | yes |
| `verification.checks[1].metrics.parsed_item_count` | 74 | 74 | 0.0 | yes |
| `verification.checks[2].metrics.inconclusive_count` | 0 | 0 | 0.0 | yes |
| `verification.checks[2].metrics.inconclusive_limit` | 1 | 1 | 0.0 | yes |
| `verification.checks[3].metrics.agree` | 74 | 74 | 0.0 | yes |
| `verification.checks[3].metrics.total` | 74 | 74 | 0.0 | yes |
| `verification.checks[3].metrics.agreement_fraction` | 1.0 | 1.0 | 0.0 | yes |
| `verification.checks[3].metrics.threshold` | 0.9 | 0.9 | 0.0 | yes |
| `verification.checks[4].metrics.disagreement_count` | 0 | 0 | 0.0 | yes |

- Contested fields: **none**.
- Maximum absolute drift across all 17 compared metrics: **`0.0`**.
- `best_verdict` unchanged: `VALID`.

`verification.checks[4].metrics.disagreement_count` is the metric that was
missing before the merged `TASK-0782` packaging fix (it was previously the sole
`metric-missing` Gate B error). It now reproduces exactly.

## Independence Assessment (Honest)

Gate B mechanical replay is clean, so the *mechanical* precondition for an
`AGENT_VALIDATED` bump is met. But the promotion decision is not purely
mechanical: the result-promotion protocol and the standing Gate-B-independence
principle require that the validation be genuinely independent of what is being
validated. Two independence axes are relevant here, and they diverge.

| Independence axis | Original party | This task | Independent? |
| --- | --- | --- | --- |
| RESULT-0020 publisher (`TASK-0750`) | `romanhladun24-dot` / Codex / GPT-5 | `gladunrv` / Claude Code / Opus 4.8 | Yes (different contributor and different agent tool) |
| Gate B packaging fix (`TASK-0782`) that made the checks deterministically emit so Gate B replays clean | `gladunrv` / Claude | `gladunrv` / Claude | No (identical contributor and identical agent identity) |

Publisher independence is satisfied and the engine's replay-identity check passes
with no overlap. However, the clean Gate B `PASS` is a direct downstream product
of `TASK-0782`: before that merged packaging fix, this exact result was
`CONTESTED_RESULT` (a `metric-missing` error on
`verification.checks[4].metrics.disagreement_count`). The three formerly
hand-authored publication-gate checks now reproduce only because `TASK-0782`
modified `physics_lab/workflows/dimensional_validator.py` to emit them
deterministically — and that fix was authored by this same
`gladunrv` / `claude` identity.

Promoting `AGENT_PUBLISHED` → `AGENT_VALIDATED` on the strength of this replay
would therefore have the same identity that engineered the pass certify the pass.
That is a review-independence conflict: it is not the publisher self-validating,
but it is the author of the mechanism-under-which-Gate-B-now-passes validating
that Gate B passes. Under the conservative reading of the promotion protocol, an
`AGENT_VALIDATED` certification should be independent of the packaging change
that made the replay clean, not just independent of the original publisher.

## Decision: Preserve Blocker, Leave RESULT-0020 at `AGENT_PUBLISHED`

No tier change is performed by this task. RESULT-0020 remains at
`AGENT_PUBLISHED`. The metadata-only `review_tier` / `validation_record` update to
`AGENT_VALIDATED` is deferred to an independent replayer.

To clear this blocker, an identity that is independent of **both** the original
publisher (`romanhladun24-dot` / Codex) **and** the `TASK-0782` packaging fix
(`gladunrv` / Claude) should re-run the same canonical Gate B helper from a clean
directory and, if it also observes a clean `PASS` with zero drift, apply the
metadata-only tier bump. A different agent tool (for example Codex) or the
maintainer satisfies this. The mechanical replay is already reproducible and
zero-drift, so the remaining step is purely an independence one.

## No-Claim Language

RESULT-0020 remains evidence that the committed validator agrees with the frozen
curated dimensional benchmark labels on the 74-item `frozen_live_74` scope. A
clean Gate B replay confirms only that the recorded command reproduces the
published metrics; it does not prove numerical correctness, empirical validity,
physical truth, symbolic understanding, or general formula quality outside the
curated fixture. Dimensional validity is not physical correctness.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (validation-routing decision; no new
  scientific verdict produced).
- **Canonical destination:** this review note,
  `docs/reviews/dimensional-result-0020-gate-b-validation-independence-blocker.md`.
- **Review tier:** RESULT-0020 stays at its input tier `AGENT_PUBLISHED`; no
  tiered artifact is created or promoted.
- **Gate A status:** previously passed; unchanged.
- **Gate B status:** **clean replay (`PASS`)**, 17 metrics compared, maximum
  absolute drift `0.0`, zero contested fields. The tier promotion is
  **blocked on review-independence**, not on replay reproducibility.
- **Claim impact:** none. `CLAIM-0005` is unchanged and stays conservative.
- **Knowledge impact:** none. No `KNOW-*` entry created or edited.
- **Result artifact impact:** none. `results/EXP-0006/RUN-0007/result.yaml` is
  byte-unchanged (metrics, verdict, challenge-set rows, verification values
  untouched).
- **Publication blocker:** the `AGENT_VALIDATED` metadata-only tier bump requires
  a replayer independent of the `TASK-0782` packaging fix (and of the original
  publisher). This same-agent-as-Gate-B-fix concern is preserved here rather than
  resolved by self-validation.

## Verdict

`RESULT0020_GATEB_CLEAN_BUT_PROMOTION_BLOCKED_ON_VALIDATION_INDEPENDENCE`: Gate B
replays RESULT-0020 cleanly (`PASS`, 17 metrics, zero drift, zero contested
fields), but the metadata-only `AGENT_VALIDATED` promotion is intentionally not
taken because the clean replay depends on the `TASK-0782` packaging fix authored
by this same `gladunrv` / `claude` identity. RESULT-0020 stays at
`AGENT_PUBLISHED`; no metric, verdict, challenge-set, verification value, or
`CLAIM-0005` change was made.
