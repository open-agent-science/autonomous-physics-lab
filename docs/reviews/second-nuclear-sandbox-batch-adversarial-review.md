# Adversarial Review Of Second Nuclear Sandbox Batch Outputs

**Task:** `TASK-0204`  
**Scope:** adversarial review of `TASK-0200`, `TASK-0201`, and `TASK-0202` sandbox outputs  
**Status:** sandbox-only audit; no claim, canonical result, or accepted knowledge promotion  
**Claim boundary:** advisory only; this review does not authorize a third batch in any reviewed lane

## Inputs

- `docs/nuclear-mass-robustness-gate.md`
- `docs/reviews/post-ame2020-timesplit-failure-analysis.md`
- `docs/reviews/autonomous-nuclear-shell-batch-01.md`
- `docs/reviews/autonomous-nuclear-neutron-rich-batch-01.md`
- `docs/reviews/autonomous-nuclear-pairing-batch-01.md`
- `agent_runs/AGENT-RUN-0009/`
- `agent_runs/AGENT-RUN-0010/`
- `agent_runs/AGENT-RUN-0011/`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0028` through `HYP-PROPOSAL-0042`
- `scripts/run_nuclear_shell_batch.py`
- `scripts/run_nuclear_neutron_rich_batch.py`
- `scripts/run_nuclear_pairing_batch.py`

## Method

1. Re-read the robustness gate and the post-AME2020 failure-mode audit to fix the review criteria before examining the second-batch outputs.
2. Compare each lane's committed review doc, `agent_run.yaml`, and `metrics.json` summary against the same structured-holdout and retrospective time-split rules.
3. Inspect proposal families for duplicate motivation, leakage, row memorization, hidden subset regressions, dormant-feature risk, and overclaim wording.
4. Record negative evidence that should remain visible and recommend maintainer actions per lane without promoting any candidate.

## Findings

### 1. No reviewed lane clears the robustness gate for bounded follow-up, let alone promotion

All six executed candidates remain below the gate's minimum stability bar.

| Lane | Executed candidates | Primary post-AME2020 reading | Structured reading | Adversarial conclusion |
| --- | --- | --- | --- | --- |
| Shell-aware (`TASK-0200`) | `HYP-0028`, `HYP-0029` | one mild regression, one marginal win with proton-rich regression | both `OVERFITTED` | keep as sandbox-only negative/partial evidence |
| Neutron-rich (`TASK-0202`) | `HYP-0033`, `HYP-0034` | one strong regression, one numerically null result | both `OVERFITTED` | keep as sandbox-only negative evidence |
| Pairing (`TASK-0201`) | `HYP-0038`, `HYP-0041` | one numerically near-null result, one explicit overfit regression | both `OVERFITTED` | keep as sandbox-only negative evidence |

No candidate improves the structured surface enough to support `ALLOW_BOUNDED_SANDBOX_FOLLOWUP`. The strongest-looking aggregate number in the batch is `HYP-PROPOSAL-0029` at roughly `-0.062 MeV` primary delta MAE, but that stays inside the earlier split-sensitivity envelope and still carries proton-rich regression plus structured-holdout failure.

### 2. The batch does preserve useful negative evidence, and that is its real scientific value

The second batch is productive as falsification and audit evidence:

- `HYP-PROPOSAL-0029` shows that fixing the dormant-feature problem from `AGENT-RUN-0008` is not enough; once the shell feature fires everywhere, instability and subset trade remain.
- `HYP-PROPOSAL-0033` shows that the earlier `HYP-PROPOSAL-0022` aggregate win is not a stable higher-order asymmetry family. The quartic extension flips sign and worsens the same hard surface.
- `HYP-PROPOSAL-0034` shows that an asymmetric-by-design neutron-rich feature can be effectively orthogonal to the 11-row training slice and collapse to a null correction.
- `HYP-PROPOSAL-0038` shows that the frozen baseline pairing term already absorbs almost all visible signal available to a simple `1/A` refinement on this surface.
- `HYP-PROPOSAL-0041` is a successful in-batch overfit diagnostic: it reproduces a clear one-row memorization failure without any temptation to treat the result as physics.

These are worth preserving precisely because they narrow what *not* to do next.

### 3. Leakage control looks effective in this batch; the rejected proposals are appropriately rejected

Independent inspection of `HYP-PROPOSAL-0031`, `0035`, `0037`, `0040`, and `0042` supports the committed rejection logic:

- `HYP-PROPOSAL-0031` and `0040` are explicit N=82-targeted reactions to a known worst-case cluster.
- `HYP-PROPOSAL-0035` turns the known In/Sb failure region into a chain-specific feature.
- `HYP-PROPOSAL-0037` and `0042` move further toward shell- or row-level memorization.

Those rejections are not overly conservative; they are exactly the boundary the robustness gate was created to enforce.

### 4. There is one reporting inconsistency in the committed pairing artifacts, but it does not change the scientific reading

`AGENT-RUN-0011/agent_run.yaml` described both executed candidates as landing in `OVERFITTED` under the structured protocol while listing `HYP-PROPOSAL-0041` with worst regression `+0.648 MeV`. The raw metrics confirm the verdict is still correct, but for a different reason:

- `HYP-PROPOSAL-0041` is `OVERFITTED` because it regresses `3` of `4` structured holdouts.
- It is **not** an example of the `worst_regression >= 1.0 MeV` path.

This is a documentation-precision issue, not a metric or classification bug. The artifact should say that the candidate crosses the verdict rule through repeated regressions rather than through the `1.0 MeV` threshold.

## Lane Decisions

### `TASK-0200` / `AGENT-RUN-0009`

- Decision: keep as sandbox-only negative/partial evidence.
- Maintainer action: do not open a third shell-aware batch from this run alone.
- Reason: the lane fixes the dormant-feature failure mode but still fails the structured surface and retains one-way subset trade.

### `TASK-0202` / `AGENT-RUN-0010`

- Decision: keep as sandbox-only negative evidence.
- Maintainer action: do not promote `HYP-0033` or `HYP-0034`; do not treat this lane as support for `HYP-0022`.
- Reason: quartic asymmetry reverses the prior sign, and the asymmetric neutron-rich feature is effectively null.

### `TASK-0201` / `AGENT-RUN-0011`

- Decision: keep as sandbox-only negative evidence.
- Maintainer action: preserve `HYP-0041` as an explicit overfit reference and treat `HYP-0038` as a null-result diagnostic, not as a near-miss success.
- Reason: the lane adds useful protocol evidence but no promotable correction family.

## Recommended Maintainer Actions

1. Keep all three reviewed runs as sandbox-only evidence under `ALLOW_ONLY_AS_NEGATIVE_CONTROL`.
2. Do not create a canonical promotion task for any second-batch candidate from this evidence alone.
3. Preserve the following negative results in future reviews and follow-up tasks:
   - continuous shell activation without stability (`HYP-0029`);
   - quartic asymmetry sign reversal (`HYP-0033`);
   - null asymmetric neutron-rich feature (`HYP-0034`);
   - null pairing A-inverse refinement (`HYP-0038`);
   - one-row odd-odd memorization (`HYP-0041`).
4. If a future maintainer wants another nuclear follow-up lane, require a broader pinned training surface or an explicitly pre-registered alternative evidence surface before opening it.
5. Keep the time-split wording conservative: retrospective validation only, not blind prediction.

## Limitations

- This review audits committed outputs; it does not introduce a new dataset or a stronger external validation surface.
- The adversarial read can test consistency, leakage boundaries, and review wording, but it cannot rescue the fundamental `NMD-0002` small-sample limit.
- The review confirms negative evidence and reporting quality. It does not replace maintainer judgment on whether the campaign should pause or move to a broader-data task.

## Verdict

`TASK-0204` adversarial conclusion: **keep the entire second nuclear sandbox batch as sandbox-only negative/partial evidence; no candidate is ready for promotion, and no lane independently justifies a third batch.**
