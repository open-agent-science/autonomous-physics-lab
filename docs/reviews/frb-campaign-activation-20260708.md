# FRB Flagship Campaign Activation — 2026-07-08

- Decision: the maintainer activated the FRB campaign chain toward the D12
  target (**PRED registration by end of July 2026**), recorded as the
  Class 2 packet `decisions/DEC-20260708-frb-campaign-activation.yaml`;
  the maintainer's merge of the activation PR is the recorded decision.
- Precondition satisfied: TASK-0947 checksum/schema gate returned
  `GATE_PASS` with all five leakage-safety conditions fixed
  (`docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md`);
  its stop condition 7 (explicit maintainer campaign-activation decision)
  is discharged by this record.
- Non-claims: activation seeds work; no model, prediction, or claim exists
  yet, and registration itself remains a separate maintainer-approved
  prediction freeze.

## Activated chain

| Step | Task | Output | Time budget |
| --- | --- | --- | --- |
| 1 | TASK-0963 | T-truncated pre-T exposure fixture (derived features only, no raw NPZ) | ~3-5 days |
| 2 | TASK-0964 | Predeclared contract + frozen model surface, scored by the gate's frozen rule verbatim | ~7-10 days |
| 3 | TASK-0965 | Sealed-prediction registration pack + Class 2 freeze decision stub; **maintainer-ready by 2026-07-28** | ~2-3 days + maintainer approval |

All three tasks inherit the gate's stop conditions verbatim; any violation
stops the task rather than renegotiating the gate. Execution is open to any
capable contributor lane (no identity constraints - these are construction
stages, not validations).

## Discipline carried from precedents

- Freeze/registration mirrors the nuclear TASK-0929 -> TASK-0933 pattern
  (contract first, execution under approval, honest routing on failure).
- External anchoring at registration time follows the PRED-0069..0072
  anchor precedent, so the FRB seal is third-party verifiable from day one
  rather than retrofitted.
- If the chain slips past 2026-07-28 maintainer-ready, the escalation is an
  honest deadline decision, never a compression of the reveal discipline.
