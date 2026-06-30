# Exoplanet Null-Baseline Canonical Identity Decision

Task: `TASK-0904`
Campaign: `exoplanet-mass-radius`
Current blocker: `docs/reviews/exoplanet-negative-control-gate-a-blocker.md`
Verdict: `RECOMMEND_MINIMAL_NEGATIVE_CONTROL_IDENTITY_LATER_MAINTAINER_GATED`

## Scope

This decision packet reviews whether the existing exoplanet null-baseline
negative/control memory should receive a canonical experiment/hypothesis
identity in a later task. It does not fetch live catalog rows, modify EXO-0001
or EXO-0002, rerun residual metrics, create a RESULT, refit a baseline, lower
the EXO-0003 trigger, or edit CLAIM/KNOW/PRED artifacts.

## Evidence Reviewed

| Evidence | Path | Decision relevance |
| --- | --- | --- |
| Gate A blocker | `docs/reviews/exoplanet-negative-control-gate-a-blocker.md` | Finding is replayable, but canonical RESULT packaging is blocked by missing experiment and hypothesis identities. |
| Replay note | `docs/reviews/exoplanet-null-baseline-negative-memory-replay.md` | The null-baseline memory replays with maximum numeric drift below `1e-12`. |
| Family audit | `docs/reviews/exoplanet-null-baseline-family-audit.md` | Nearest-radius nulls match or beat the CK17-style baseline in the highlighted true-mass slices. |
| Proposal-stage identities | `hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0049-frozen-baseline-benchmark.yaml`; `experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0015-frozen-baseline-benchmark.yaml` | Existing proposals cover the broader frozen-baseline benchmark, but not a narrow canonical negative/control identity. |
| Campaign page | `docs/campaigns/exoplanet-mass-radius.md` | Current campaign posture is monitor-only; next useful work is identity decision and source-version monitoring, not residual rescoring. |

## Decision Options

### Option A: Create a minimal negative/control identity in a later task

Recommended, but maintainer-gated. This option creates only the missing
canonical experiment and hypothesis identities needed to package the already
replayed negative/control memory later. It must not create a new residual lane.

Use this option if the maintainer wants the null-baseline memory to become a
schema-valid negative/control RESULT package in a separate follow-up task.

### Option B: Keep review-note-only memory

Safe default if public/canonical result packaging is not worth the identity
surface yet. The existing notes already preserve the negative/control finding,
its replayability, and the monitor-only boundary.

Use this option if the maintainer wants to avoid adding canonical Exoplanet
identities until a future source-version trigger materially changes the data
surface.

### Option C: Wait for a future source-version trigger

Scientifically conservative, but it leaves the already replayable negative
memory permanently outside the RESULT schema. It is appropriate if canonical
identity is reserved only for new source snapshots, not for packaging existing
control-memory findings.

Use this option if the maintainer wants EXO-0003 source-version notification to
come before any canonical Exoplanet experiment/hypothesis identity.

## Recommendation

Recommend Option A as a later maintainer-approved task:

`CREATE_MINIMAL_NEGATIVE_CONTROL_IDENTITY_LATER`

Reason: the null-baseline memory is deterministic, scientifically useful, and
already replayed; the Gate A blocker is not metric drift or weak limitations,
but absent canonical identity. A narrowly scoped identity can make the
package-or-stop boundary durable while preserving the current monitor-only
posture.

The recommendation is not permission to create identities in this PR and not
permission to package a RESULT. It only states that the next packaging unblock,
if the maintainer wants one, should be a minimal identity task rather than a
new residual-scoring task.

## Future Task Shape

A safe future identity task should have this shape:

- Add one canonical experiment identity for the existing EXO-0001 null-baseline
  negative/control family audit only.
- Add one paired canonical hypothesis identity whose statement is about
  control sensitivity, not a positive mass-radius law.
- Bind the identities to committed evidence only:
  - `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
  - `docs/reviews/exoplanet-null-baseline-family-audit.md`
  - `docs/reviews/exoplanet-null-baseline-negative-memory-replay.md`
  - `docs/reviews/exoplanet-negative-control-gate-a-blocker.md`
- State that the identities authorize packaging of the existing negative/control
  memory only, not scoring any new snapshot or rerunning CK-style residuals.
- Preserve true-mass/minimum-mass separation and nearest-radius null controls.
- Keep EXO-0003 source-version trigger thresholds unchanged.
- Produce no RESULT in the identity task unless a separate task explicitly
  combines identity creation and result packaging after maintainer approval.

Suggested identity wording boundary:

```text
Experiment: Exoplanet null-baseline control-sensitivity audit on the committed
EXO-0001 PSCompPars snapshot.

Hypothesis: In the highlighted true-mass transit-radius slices of EXO-0001,
deterministic nearest-radius null controls match or beat the frozen CK17-style
baseline, so the apparent residual stress is control-sensitive and should not
reopen a positive residual-scoring lane on this snapshot.
```

## No-Reopen Boundary

A later canonical identity must not authorize any of the following:

- live NASA Exoplanet Archive fetch;
- EXO-0003 rows or value-bearing metadata scout;
- lowered source-version or coverage trigger;
- CK17 refit or Chen-Kipping-style rerun on unchanged snapshots;
- candidate formula search;
- composition, habitability, atmosphere, target-priority, discovery,
  prediction, or universal mass-radius wording;
- CLAIM, KNOW, or PRED mutation.

## Consequences For Gate A

If the maintainer accepts the future identity task, Gate A can be revisited for
a negative/control RESULT package without changing metrics. The expected result
would still need a deterministic result-producing command, input hashes,
limitations, and strict validation in its own publication task.

If the maintainer declines identity creation, Gate A remains blocked and the
memory stays as review-note-only negative/control evidence until a future source
trigger or policy change.

## Output Routing

- Task verdict: `RECOMMEND_MINIMAL_NEGATIVE_CONTROL_IDENTITY_LATER_MAINTAINER_GATED`.
- Canonical destination: `docs/reviews/` decision packet only.
- Review tier: none.
- Gate A status: still blocked until canonical experiment/hypothesis identities
  are created in a later maintainer-approved task.
- Gate B status: not attempted for a RESULT; existing memory replay passed with
  sub-`1e-12` drift.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Result impact: none; no RESULT artifact created or modified.
- Exoplanet campaign impact: monitor-only posture preserved; future identity
  task recommended only for negative/control memory packaging.
- Remaining blocker: maintainer decision on whether to create the minimal
  canonical identity pair before any RESULT packaging task.