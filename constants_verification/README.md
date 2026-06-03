# Constants Verification

Lifecycle: **legacy worked example**.

This directory currently preserves `CV-0001`, an early verification-format
example for the fine-structure constant. It is useful historical memory, but it
is not a current default campaign lane.

Do not add new constants-verification entries here by default. Future constants
or formula checks should normally route through one of these paths:

- Textbook Formula Audit when the work is a bounded formula/domain audit;
- source/dataset artifacts when external published values or rows matter;
- `results/` when a reproducible reviewed result is being published;
- `knowledge/` only after the relevant result or claim review gate.

Keep this directory until a dedicated migration task updates schemas, docs,
validation inference, and historical links together.
