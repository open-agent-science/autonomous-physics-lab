# Codex Task: Continue the v0.2 Verification Stack

Read `AGENTS.md` first and follow it.

## Goal

Strengthen the pendulum benchmark as verification-backed scientific evidence.

The current vertical slice already exists:

`Hypothesis -> Experiment -> Result -> Claim -> Knowledge -> Next Task`

The next work should deepen verification quality, keep artifacts reproducible,
and avoid overclaiming scientific validity.

## Priority Areas

Work in or around:

```text
physics_lab/engines/verification.py
physics_lab/engines/symbolic.py
physics_lab/workflows/runner.py
results/EXP-0001/RUN-0001/
tests/test_pendulum.py
docs/status.md
docs/next-steps.md
```

## Current Canonical Outputs

The canonical artifacts live here:

```text
results/EXP-0001/RUN-0001/result.yaml
results/EXP-0001/RUN-0001/metrics.json
results/EXP-0001/RUN-0001/report.md
results/EXP-0001/RUN-0001/claim_update.md
results/EXP-0001/RUN-0001/knowledge_update.md
```

## What To Improve Next

Examples:

1. deepen known-limit checks;
2. improve behavior diagnostics near `theta -> pi`;
3. keep result semantics range-aware;
4. tighten contributor and snapshot tooling;
5. preserve reproducibility and schema validity.

## Constraints

- Do not add dashboard.
- Do not add web API.
- Do not add LLM calls.
- Do not add ScienceClaw, OpenClaw, or LabClaw integration yet.
- Keep it deterministic and testable.
- Keep tests fast.
- Do not weaken verification-first wording.
- Do not promote claims directly from code execution.

## Before Finishing

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml
python3 -m physics_lab.cli validate-repo .
```
