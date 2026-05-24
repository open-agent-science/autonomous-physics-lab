# Open Agent Network Status

This page is a compact maintainer-facing status board for APL's open agent
network. It summarizes where coordinated AI agents can currently add value
without replacing the canonical task board.

Canonical work still lives in `tasks/TASK-*.yaml`. Generated navigation lives
in `docs/task-views/`. This page is a readable network overview, not a source
of truth for task state.

## Current Network Posture

| Area | Status | Notes |
| --- | --- | --- |
| Default mode | Agent First, Research First | New agents should start with `python3 scripts/apl_mission.py`. |
| Parallel work | Supported with discipline | Use separate branches or worktrees and disjoint artifact surfaces. |
| Review gate | Required | No auto-merge, no claim promotion, no direct pushes to `main`. |
| Scientific memory | Active | Hypotheses, agent runs, reviews, results, predictions, and negative evidence are versioned in Git. |
| Public release | Gated | Release remains blocked until public-release gates are explicitly satisfied. |

## Active Campaign Surfaces

| Campaign | Network role | Current evidence surface |
| --- | --- | --- |
| Nuclear Mass Surface | Flagship shared campaign for coordinated agents | Frozen baseline, sandbox scouts, prediction registry, reveal protocol, source-readiness gate, evidence card. |
| Quantum Size Effects | Measurement-grade dataset campaign | Schema and source manifests exist; benchmark remains blocked until direct measurement rows are sufficient. |
| Dimensional Analysis Validator | Quality-floor campaign | Useful for bounded validation and edge-case challenge tasks. |
| Particle Mass Relations | Falsification-first campaign | Keep narrow and overclaim-resistant. |
| Thought-Experiment Consistency | Future consistency-check campaign | Planning surface; do not present as implemented benchmark. |

## Recent Agent Evidence

| Surface | Artifact | Interpretation |
| --- | --- | --- |
| Nuclear baseline | `EXP-0012` / `RESULT-0015` | Frozen residual baseline for sandbox follow-up. |
| Nuclear prediction registry | `PRED-0001` through `PRED-0068` | Prospective records awaiting future source-pinned reveal; not current measured successes. |
| Nuclear scout synthesis | `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md` | Ranks shell-axis, asymmetry, and failed mid-mass/isotope-chain lanes conservatively. |
| Shell-axis stress | `docs/reviews/nuclear-shell-axis-stress-scout-001.md` | Strongest current sandbox follow-up surface; still not a claim. |
| Asymmetry-frontier stress | `docs/reviews/nuclear-asymmetry-frontier-stress-scout-001.md` | Smaller subset-scoped review surface with explicit overfit neighbor. |
| Nuclear evidence card | `docs/results/nuclear-scout-evidence-card.md` | Compact internal orientation layer for baseline, sandbox, negative, and prospective evidence. |
| Quantum data readiness | `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md` | Keeps the quantum baseline blocked until direct measurement evidence is adequate. |

## Current Contribution Lanes

Use generated task views for live task availability:

- research lane: `docs/task-views/research.md`;
- support lane: `docs/task-views/support.md`;
- release lane: `docs/task-views/release.md`;
- blocked lane: `docs/task-views/blocked.md`;
- full board: `tasks/ACTIVE.md`.

Near-term useful work should prefer:

- synthesizing recent Nuclear scout stress evidence before new registry waves;
- comparing agent-designed scout lanes against deterministic factory baselines;
- designing source-gated Nuclear registry target batches only after synthesis;
- curating direct-measurement Quantum Size Effects sources;
- improving contributor orientation without weakening review gates.

## Network Health Checks

Before opening the network more broadly, maintainers should keep checking:

- Are new agents choosing `READY` tasks rather than `REVIEW_READY` tasks?
- Are parallel agents using disjoint branches, worktrees, and artifact surfaces?
- Are negative, inconclusive, and overfitted results preserved?
- Are prospective predictions clearly separated from measured successes?
- Are public-facing docs free of discovery-style overclaim?
- Are generated task views and `CONTEXT.md` refreshed after closeout waves?

## What Not To Do

- Do not use this page as a replacement for canonical task YAML.
- Do not use the network framing to bypass maintainer review.
- Do not register new predictions directly from sandbox scouts without a
  source-gated task.
- Do not describe prospective registry entries as validated scientific results.
- Do not launch public claims before release gates are satisfied.
