# Independent Audit - HYP-PROPOSAL-0021

**Task:** `TASK-0173`
**Candidate:** `HYP-PROPOSAL-0021`
**Audit type:** replay plus split-sensitivity review
**Status:** REVIEW_READY
**Date:** 2026-05-11

---

## Recommendation

`HYP-PROPOSAL-0021` survives independent replay as **sandbox-only follow-up
evidence**, but not as a promotion-ready nuclear result.

The strongest honest reading is:

- replay confirmed;
- negative evidence preserved;
- selection sensitivity is visible and should stay visible;
- the candidate is suitable for later maintainer-reviewed comparison work, not
  for canonical result promotion.

---

## Inputs Audited

- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0021-shell-dual-heavy-anchor-odd-a.yaml`
- `agent_runs/AGENT-RUN-0005/metrics.json`
- `agent_runs/AGENT-RUN-0005/report.md`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `docs/nuclear-mass-holdout-protocol.md`

Code used for deterministic replay:

- `physics_lab/engines/nuclear_mass_baselines.py`
- `physics_lab/engines/nuclear_masses.py`
- `tests/test_nuclear_mass_hyp_0021_audit.py`

---

## Highest-Value Scientific Action

After inspecting the current missions and active campaigns, the highest-value
scientific action is this audit rather than a fresh search loop.

Why:

1. `TASK-0173` is the highest-priority `READY` science task on the board.
2. The nuclear mass surface is the current flagship real-data campaign.
3. `TASK-0178` explicitly stays blocked until this audit is complete.
4. Auditing the strongest sandbox candidate improves scientific discipline more
   than generating another unreviewed candidate batch.

---

## Replay Result

The stored pilot metrics for `HYP-PROPOSAL-0021` replay exactly from the frozen
`RESULT-0015` residual surface.

Confirmed stored summary:

- improved active holdouts: `4`
- regressed active holdouts: `0`
- mean `delta_mae_mev`: `-0.33501713070505423`
- worst MAE regression: `0.0`
- stored sandbox verdict: `VALID_IN_RANGE`

This confirms that the pilot package is reproducible as written.

---

## Leakage and Selection-Risk Assessment

### What looks clean

- The replay itself is deterministic.
- The baseline surface is frozen and pinned.
- The audit reproduced the stored deltas directly from committed repository
  inputs.

### What does not count as clean isolation

The candidate was still chosen **after seeing performance on the active
holdout package** inside `AGENT-RUN-0005`.

That means:

- the holdout families are useful stress surfaces,
- but they also influenced which candidate was highlighted as the strongest one.

So the audit conclusion is not "no leakage risk." The honest conclusion is:

> the replay is real, but proposal selection was not blind to the revealed
> holdout structure.

This is exactly why the result must remain sandbox evidence only.

---

## Split-Sensitivity Check

To test cherry-picking pressure, the audit enumerated all `48` same-shape
stratified random holdouts using:

- one light nuclide from `{He-4, N-14, O-16, O-17}`
- one medium nuclide from `{Ca-40, Ca-48, Fe-56, Fe-57}`
- one heavy nuclide from `{Sn-120, Pb-208, U-238}`

### Result

For `HYP-PROPOSAL-0021`:

- improves baseline MAE on `28/48` stratified random splits
- regresses baseline MAE on `13/48` splits
- ties baseline MAE on `7/48` splits
- median `delta_mae_mev`: `-0.135265169994792`
- best split `delta_mae_mev`: `-0.7440386250631548`
- worst split `delta_mae_mev`: `0.9480738911860487`

For the specific pilot split `('He-4', 'Fe-57', 'Pb-208')`:

- `delta_mae_mev = -0.2551303671269771`
- rank `18/48` among same-shape stratified random splits

Interpretation:

- the pilot split is not obviously the luckiest available split;
- the candidate is not robust enough to say "random holdout success is stable"
  without qualification.

---

## Why The Odd-A Term Helps

Relative to the simpler `HYP-PROPOSAL-0020` family:

- `HYP-PROPOSAL-0021` is better on `18/48` stratified random splits
- it is worse on `0/48`
- it ties on the remaining `30/48`

Crucially:

- every gain over `HYP-PROPOSAL-0020` happens only when the holdout contains
  `O-17` or `Fe-57`
- on the heavy magic and neutron-rich structured holdouts, `HYP-PROPOSAL-0021`
  behaves exactly like `HYP-PROPOSAL-0020`

So the odd-A extension is doing something real, but narrow:

- it acts as a lightweight empirical correction for the odd-A revealed rows;
- it does not provide new evidence that the heavy shell-sensitive behavior is
  more general than the simpler shell-only family already suggested.

---

## Complexity Review

Compared with `HYP-PROPOSAL-0020`, this candidate adds:

- one extra parameter;
- no new discontinuity;
- no explicit row memorization rule;
- no complex region-switch cascade.

That is a modest complexity increase by the campaign’s stated standards.

So the complexity objection is not "too many parameters." The main objection is
selection sensitivity on a tiny pinned slice.

---

## Negative Result Preservation

The audit does not weaken the negative evidence from `HYP-PROPOSAL-0022`.

That family still matters because it shows that a plausible asymmetry
refinement can:

- look superficially reasonable,
- help one local slice,
- and still fail the heavy magic and neutron-rich checks badly.

This remains important scientific memory and should stay visible beside any
follow-up discussion of `HYP-PROPOSAL-0021`.

---

## Verdict

**Verdict:** `PARTIALLY_VALID` as an audited sandbox follow-up candidate.

Why not stronger:

- replay passed;
- the candidate remains compact;
- but selection used revealed holdout performance, and the odd-A benefit is
  visibly tied to the revealed odd-A rows on this tiny pinned dataset.

This is enough to justify later maintainer-reviewed comparison work.
It is not enough to justify canonical result promotion.

---

## Limitations

- The audit still lives on `NMD-0002`, a very small measured-only slice.
- The candidate was not chosen under a blind selection rule.
- The split-sensitivity check improves honesty, but it is still internal
  stress-testing rather than external validation.
- No broader pinned dataset was introduced here.

---

## Self-Review

Before PR:

- replayed stored metrics independently
- added deterministic audit coverage in tests
- checked for a selection-sensitive explanation rather than a stronger claim
- preserved negative evidence instead of writing only around the successful
  candidate

The PR should be reviewed as an audit package, not as a benchmark promotion.
