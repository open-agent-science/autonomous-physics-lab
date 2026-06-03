# Constants Verification

Lifecycle: **archived legacy worked example**.

This directory preserves `CV-0001`, an early verification-format example for
the fine-structure constant. It used to live at repository root as
`constants_verification/`; it is now archived here because it is useful
historical memory, not a current default campaign lane.

Do not add new constants-verification entries here by default. Future constants
or formula checks should normally route through one of these paths:

- Textbook Formula Audit when the work is a bounded formula/domain audit;
- source/dataset artifacts when external published values or rows matter;
- `results/` when a reproducible reviewed result is being published;
- `knowledge/` only after the relevant result or claim review gate.

Do not recreate `constants_verification/` at repository root without a new
maintainer-approved architecture task.
