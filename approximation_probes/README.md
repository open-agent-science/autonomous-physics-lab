# Approximation Probes

Lifecycle: **retained narrow deterministic probe track**.

This directory is intentionally small. It currently contains `AP-0001`, the
small-angle pendulum breakdown probe, backed by deterministic code in
`physics_lab/engines/approximation_probes.py` and tests in
`tests/test_approximation_probes.py`.

Keep this surface for exact-reference approximation breakdown probes only when
they include:

- deterministic code;
- a committed artifact;
- a test or validation command;
- an explicit claim ceiling.

Do not expand this into a broad formula-audit registry. Larger formula-audit
work should route through the Textbook Formula Audit campaign and its task,
dataset, result, or review artifacts.
