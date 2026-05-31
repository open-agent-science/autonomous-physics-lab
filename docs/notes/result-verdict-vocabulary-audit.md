# Result Verdict Vocabulary Audit (TASK-0432)

Audit of the verdict vocabulary accepted by APL schemas versus the wording used
in protocol docs and committed result artifacts. This note is an **audit only**:
per TASK-0432 it does not change any schema and does not rewrite any `RESULT-*`
artifact. It documents the authoritative vocabulary, the legacy mapping, and one
real protocol↔schema inconsistency, and recommends conservative follow-ups.

## 1. Verdict vocabulary by schema (authoritative)

| Schema | Field | Enum |
| --- | --- | --- |
| `result.schema.json` | `best_verdict` | `VALID_IN_RANGE`, `VALID`, `PARTIALLY_VALID`, `INVALID`, `OVERFITTED`, `INCONCLUSIVE` |
| `result.schema.json` | `scores[].verdict` | `VALID`, `PARTIALLY_VALID`, `INVALID`, `OVERFITTED`, `INCONCLUSIVE` |
| `agent_run.schema.json` | `verdict` | `SANDBOX_PASS`, `SANDBOX_FAIL`, `FALSIFIED`, `INCONCLUSIVE`, `OVERFITTED`, `REVIEW_NEEDED` |
| `microtask_run.schema.json` | `verdict` | `VALID`, `PARTIALLY_VALID`, `INVALID`, `FALSIFIED`, `INCONCLUSIVE`, `OVERFITTED`, `REVIEW_NEEDED`, `NOT_RUN` |
| `hypothesis.schema.json` | `status` | `PROPOSED`, `FORMALIZED`, `TESTING`, `VALID_IN_RANGE`, `PARTIALLY_VALID`, `FALSIFIED`, `OVERFITTED`, `INCONCLUSIVE`, `INTEGRATED` |
| `hypothesis_proposal` / `experiment_proposal` | `sandboxVerdict` | `SANDBOX_PASS`, `SANDBOX_FAIL`, `FALSIFIED`, `INCONCLUSIVE`, `OVERFITTED`, `REVIEW_NEEDED` |
| `result.schema.json` | `verificationCheck.status` | `PASS`, `FAIL`, `PLACEHOLDER` (a per-check status, not a verdict) |

Key structural fact: **`FALSIFIED` is first-class in every verdict vocabulary
except the `result` schema.** The `result` schema uses `INVALID` for the
negative/falsification verdict instead.

## 2. What committed result artifacts actually emit

Counts of `verdict:` / `status:` values across `results/` (2026-05-31):

- `verdict: OVERFITTED` (366), `verdict: VALID` (59), `verdict: INVALID` (38),
  `verdict: PARTIALLY_VALID` (16), `verdict: VALID_IN_RANGE` (8),
  `verdict: INCONCLUSIVE` (5) — all inside the `result` schema enum.
- **No committed `RESULT-*` uses `best_verdict: FALSIFIED`.** Negative results
  (e.g. the Koide falsifications RESULT-0009 / RESULT-0010 / RESULT-0011) use
  `INVALID`, which is schema-valid.
- Out-of-enum tokens come from the gauntlet/challenge layer, not from
  `best_verdict` (see §4).

So the *live* result corpus already follows the `result` schema. The drift is in
the docs, not the artifacts.

## 3. Core inconsistency: protocol says `FALSIFIED`, result schema rejects it

`docs/result-promotion-protocol.md` instructs agents to publish a negative
result with `best_verdict: FALSIFIED` (negative/falsification row, the
`best_verdict` value table, and the verdict→artifact mapping). But
`result.schema.json` does **not** include `FALSIFIED` in `best_verdict`, so
`validate-repo --strict` would reject such a file.

Consequence: an agent that follows `result-promotion-protocol.md` literally to
publish a negative `RESULT-*` produces a **schema-invalid** artifact. The
protocol and the schema disagree on the single most important negative-evidence
verdict.

`AGENTS.md` ("Prefer this verdict vocabulary": `VALID`, `PARTIALLY_VALID`,
`INVALID`, `OVERFITTED`, `INCONCLUSIVE`) agrees with the `result` schema and
does **not** list `FALSIFIED`. So `result-promotion-protocol.md` is the outlier.

## 4. Legacy and cross-layer mapping

- **Negative / falsification RESULT artifact** → `best_verdict: INVALID`
  (schema-valid; used by all committed negatives). `FALSIFIED` is the
  falsification-oriented synonym used one layer up, in `agent_run`,
  `hypothesis`, `microtask_run`, and the research-quality-gate / sandbox
  vocabulary. When prose says a lane verdict is `FALSIFIED`, the corresponding
  committed `RESULT-*` records `best_verdict: INVALID`.
- **Gauntlet / challenge expectations**: `STRESS_TEST_HIT`, `KNOWN_LIMIT_FAIL`,
  and `SUSPICIOUS` appear in the `expected_verdict` field of challenge entries
  (9 occurrences) and as a free-text `global_verdict` that is explicitly mapped
  to a schema verdict (e.g. `Global verdict: STRESS_TEST_HIT → schema:
  INCONCLUSIVE` in RESULT-0012). These are an evaluation-expectation vocabulary,
  not `best_verdict` values, and they already carry their own mapping to the
  schema enum.
- **Stray term**: `docs/negative-results-registry.md` step 3 says
  `best_verdict: INVALID` or `INCONSISTENT`; `INCONSISTENT` is not in any schema
  enum and should read `INVALID`.

## 5. Recommendations (conservative; kept separate per TASK-0432)

These are **not** applied in this audit task (schema changes and artifact
rewrites are out of scope here). They are surfaced for a maintainer decision:

1. **Resolve the `FALSIFIED` vs `INVALID` split for RESULT `best_verdict`** as a
   separate follow-up. Two options:
   - **Option A (recommended, lower disruption):** add `FALSIFIED` to the
     `result` schema `best_verdict` (and `scores[].verdict`) enum so the
     `result` layer matches the protocol, AGENTS lifecycle, and every other
     schema, and so negatives can be labelled with the same falsification term
     end-to-end. Existing `INVALID` negatives stay valid; no artifact rewrite
     required. This is a schema change and must be its own PR.
   - **Option B (docs-only):** change `result-promotion-protocol.md` to
     instruct `best_verdict: INVALID` for negative RESULTs and describe
     `FALSIFIED` only as the upstream agent_run/hypothesis term. Lower blast
     radius but spreads the same concept across two words by layer.
2. **Fix the stray `INCONSISTENT`** in `docs/negative-results-registry.md`
   step 3 → `INVALID` (trivial docs fix, can ride with Option A or B).
3. Until (1) is decided, agents publishing a negative `RESULT-*` should use
   `best_verdict: INVALID` (schema-valid), as the committed corpus already does,
   regardless of `result-promotion-protocol.md` saying `FALSIFIED`.

## 6. Validation note

- `FALSIFIED` is accepted in: `agent_run`, `hypothesis`, `microtask_run`,
  `hypothesis_proposal`/`experiment_proposal` schemas.
- `FALSIFIED` is **rejected** in: `result.schema.json` (`best_verdict`,
  `scores[].verdict`).
- `INVALID` is accepted in `result` and `microtask_run`; it is **not** an
  `agent_run` verdict.
- Therefore both `FALSIFIED` and `INVALID` are "live" in the repository, but in
  different layers: `INVALID` for committed `RESULT-*`, `FALSIFIED` for the
  agent-run / hypothesis / sandbox layer that feeds them.
