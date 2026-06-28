# FIRAS/Wien RESULT-0023 Gate B Workflow Packaging

Task: `TASK-0873`
Result: `RESULT-0023`

## Verdict

`RESULT-0023` is now Gate-B-replayable at the packaging level. Its provenance
command has been changed from the standalone script path to:

```bash
physics-lab run examples/textbook_firas_wien_peak_consistency.yaml
```

The new workflow adapter regenerates the same FIRAS/Wien scoped result from the
committed inputs and preserves the exact reference temperature, FIRAS rows,
domain/Jacobian handling, controls, tolerances, and no-claim limitations.

## Replay Check

The repository Gate B helper now accepts the canonical result and can replay it
through the safe `physics-lab run` command. This task ran the helper with a
Codex replay identity and observed no metric drift.

This is still not an AGENT_VALIDATED promotion: the result remains
`AGENT_PUBLISHED` until a maintainer accepts an independent replay record.

## Metric Mutation Check

No numeric scientific metric was changed.

- Reference wavelength peak: unchanged.
- Raw-bin relative difference and tolerance: unchanged.
- Interpolated relative difference and tolerance: unchanged.
- Control outcomes: unchanged.
- Verdict: `CONSISTENT_IN_SCOPE` / `VALID_IN_RANGE`, unchanged.

The only `metrics.json` change is the Gate B status text, replacing the obsolete
"requires engine-workflow repackaging" note with a packaging-complete / promotion
not-yet-applied note.

## Limitations Preserved

- FIRAS spectral-domain self-consistency only.
- Not independent validation or falsification of Wien displacement, blackbody
  physics, CMB physics, or universal textbook truth.
- The reference temperature is FIRAS-derived, so the comparison is partly
  circular and must retain the blackbody self-consistency qualifier.
- No CLAIM, KNOW, PRED, or new RESULT artifact is created.

## Output Routing

- Canonical destination: existing `results/EXP-0016/RUN-0001/` packaging metadata
  and this review note.
- Review tier: remains `AGENT_PUBLISHED`.
- Gate A: already passed by `TASK-0845`.
- Gate B: replayable command available; AGENT_VALIDATED promotion not applied.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: none for workflow packaging; independent replay/maintainer
  review is still required for review-tier promotion.
