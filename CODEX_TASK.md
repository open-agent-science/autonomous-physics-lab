# Codex Task: TASK-0003 — Theory-aware Pendulum Approximation Near Separatrix

Read `AGENTS.md`, `docs/status.md`, and
`tasks/TASK-0003-theory-aware-pendulum-near-separatrix.yaml` first.

## Goal

Improve the pendulum benchmark by adding at least one theory-aware candidate
family that behaves better as `theta` approaches `pi`.

The current best low-order polynomial candidate is `VALID_IN_RANGE`, but it
still fails near-separatrix diagnostics.

## Required Work

1. Add candidate families that include known logarithmic behavior near `theta -> pi`.
2. Keep the current low-order polynomial candidates unchanged.
3. Add or extend separatrix-aware verification checks.
4. Produce a new canonical run:
   - `results/EXP-0001/RUN-0002/result.yaml`
   - `metrics.json`
   - `report.md`
   - `claim_update.md`
   - `knowledge_update.md`
5. Compare `RUN-0001` vs `RUN-0002`:
   - in-range accuracy
   - near-separatrix behavior
   - complexity score
   - limitations
6. Do not overwrite `RUN-0001`.

## Candidate Ideas

Consider forms involving:

- `epsilon = pi - theta`
- `log(1 / epsilon)`
- `log(8 / (pi - theta))`
- `sin(theta / 2)^2`
- rational or blended formulas with a complexity penalty

## Scientific Rules

- Do not claim exact discovery.
- Keep verdicts range-aware.
- If the candidate improves separatrix behavior but worsens small-angle accuracy,
  report that tradeoff explicitly.
- The result must clearly state the validity regime.

## Constraints

- Do not add a third benchmark.
- Do not add dashboard.
- Do not add web API.
- Do not add LLM calls.
- Do not add literature ingestion.
- Do not add multi-agent runtime.
- Keep tests fast.

## Before Finishing

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
git diff --exit-code
```
