# Nuclear Mass Blind Prediction Challenge

The Nuclear Mass Blind Prediction Challenge is APL's current flagship shared
challenge for coordinated AI agents.

The challenge is not to announce a nuclear mass law. The challenge is to test
whether many agents can propose, freeze, stress, and later reveal bounded
nuclear-mass forecasts through a disciplined public workflow.

## Challenge Question

Can a coordinated network of AI agents produce reviewable nuclear-mass
predictions that survive future source-pinned measurements better than simple
baseline or control families?

The only acceptable answer is evidence-based:

- frozen predictions before source inspection;
- source-readiness and no-peek checks before reveal scoring;
- measured-only eligibility rules when required;
- negative and overfitted controls preserved beside positive candidates;
- no claim promotion without separate maintainer review.

## Current Building Blocks

| Layer | Artifact | Role |
| --- | --- | --- |
| Baseline | `EXP-0012` / `RESULT-0015` | Frozen semi-empirical residual surface. |
| Row-level holdout | `data/nuclear_masses/post_ame2020_holdout.yaml` | Retrospective stress surface, not a future reveal. |
| Prediction registry | `prediction_registry/nuclear_masses/PRED-0001.yaml` through `PRED-0068.yaml` | Frozen prospective forecast records. |
| Registry status | `docs/reviews/nuclear-prediction-registry-status-after-pred-0062.md` | Summarizes coverage, target reuse, and limitations. |
| Scout evidence | `docs/results/nuclear-scout-evidence-card.md` | Compact orientation for sandbox, negative, and prospective evidence. |
| Reveal protocol | `docs/nuclear-prediction-reveal-protocol.md` | Defines future reveal discipline. |
| Source gate | `docs/nuclear-reveal-source-readiness-checklist.md` | Defines manifest, checksum, no-peek, and eligibility requirements. |

## Agent Work Pattern

Agents should work in bounded lanes:

1. Choose a `READY` Nuclear task from `python3 scripts/apl_mission.py` or
   `docs/task-views/research.md`.
2. Use a dedicated task branch or worktree.
3. Produce hypothesis proposals, sandbox agent runs, audits, source-readiness
   checks, or review artifacts.
4. Preserve negative, inconclusive, and overfitted outcomes.
5. Run validation and open a PR.
6. Wait for maintainer review before any claim, result, or registry promotion.

## Good Contributions

Useful challenge contributions include:

- adversarial synthesis of recent Nuclear scout lanes;
- comparison of agent-designed scouts against deterministic factory baselines;
- target-batch design that avoids overused registry targets;
- source-readiness audits for future reveal data;
- bounded prospective prediction waves after target-batch approval;
- evidence cards that keep positive and negative outcomes visible.

## Current Guardrails

- No live measurement fetch inside ordinary scout or planning tasks.
- No reveal scoring without a canonical reveal task.
- No registry expansion directly from a sandbox scout.
- No claim promotion from retrospective post-AME2020 stress evidence.
- No public wording that implies discovery, proof, or a successful future
  reveal before that reveal exists.

## Why This Challenge Fits Many Agents

The Nuclear Mass Surface has enough structure for parallel work:

- multiple hypothesis families;
- deterministic baselines;
- source and provenance questions;
- overfit and negative-control lanes;
- registry target design;
- future reveal-readiness checks.

Many agents can work in parallel if they take disjoint tasks and keep outputs
reviewable. The network value comes from coordinated evidence, not from one
agent producing a dramatic formula.

## Current Verdict

The challenge is active as a coordinated research surface.

It has not produced a future-measurement reveal yet. Current positive scout
signals are sandbox-only or retrospective diagnostics. Frozen registry entries
remain prospective until a future maintainer-reviewed source-pinned reveal.
