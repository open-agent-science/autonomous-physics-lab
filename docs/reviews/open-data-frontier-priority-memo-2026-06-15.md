# Portfolio Open-Data Lane Map (TASK-0752)

**Task:** `TASK-0752`
**Scope:** portfolio-level curator recommendation. Ranks active campaigns by
open-data availability and result-proximity, and assigns every active campaign a
bounded, parallel-safe lane. This is a recommendation; any `missions/current.yaml`
change needs maintainer sign-off.

## Strategic Read

The project already produces durable outputs — but all 10 `CLAIM-*` artifacts
come from the **mature** classical/particle campaigns. The **source-readiness
frontier has promoted no RESULT yet**, because its binding constraint is
source-to-row acquisition, not idea generation.

Correction to an earlier single-thread "concentrate on Materials" read: with
many agents available, the goal is **parallel progress without collisions**, not
concentration. Two frontier campaigns are now near a first promotable RESULT on
**open data** and can be driven **in parallel** on disjoint surfaces:

- **Materials** — MD-0001 formation-energy is robust, replayed, null-controlled,
  and split-robust; the MD-0002 widening chain is queued. Source: Materials
  Project (CC BY 4.0) — no source bottleneck.
- **Stellar M-L** — Route 2 DEBCat local-extractor benchmark reached
  `SANDBOX_PASS` (holdout MAE 0.347 dex beats the 0.445 dex null). Source: DEBCat
  (open astronomical catalog) — no source bottleneck.

Open-data availability therefore sets **priority and agent-strength allocation**,
not which campaigns to keep alive. Every active campaign keeps a live lane.

## Priority Ranking (open-data x result-proximity)

| Rank | Campaign | Open-data tier | Result-proximity | Why |
| ---: | --- | --- | --- | --- |
| 1 | **Materials** (lead) | Tier 1 (MP CC BY 4.0) | near first RESULT | robust replayed signal; only the maintainer-gated MD-0002 fetch stands between it and a retest |
| 2 | **Stellar M-L** (lead) | Tier 1 (open DEBCat) | near first RESULT | Route 2 benchmark already `SANDBOX_PASS`; needs promotion-readiness review |
| 3 | **Atomic** | Tier 2/3 (arXiv) | first benchmark exists (source-limited) | de-limit lane + Pizzocaro lane, both parallel-safe |
| 4 | **Quantum** | Tier 3/4 (figures/closed) | no rows yet | source-starved; open-tabular scout before figure digitization |
| 5 | **Nuclear** | reveal-gated | diagnostic only | bounded non-F2 lane + reveal monitor |
| 5 | **Exoplanet** | reveal-gated | negative-control memory | monitor for a materially-changed snapshot |
| 6 | mature (anharmonic, dimensional, particle-mass, pendulum) | n/a | claims exist | verifier-quality-floor support |

Lower confidence on the Stellar / textbook-formula-audit ranking: it is a
sub-lane of `textbook-formula-audit` rather than its own profile; maintainer to
confirm scope.

## Parallel-Safe Lane Map (no campaign abandoned)

Each lane has a disjoint write surface so independent agents can run concurrently
without collision.

| Campaign | Next parallel-safe lane | Write surface |
| --- | --- | --- |
| **Materials** | Close `TASK-0737` (narrowed predicate) → run `TASK-0738` (maintainer-gated MD-0002 fetch with `MP_API_KEY`) → `TASK-0702` freeze → `TASK-0703` formation-energy retest → promotion-readiness | `data/materials/`, `docs/reviews/materials-*` |
| **Stellar M-L** | Promotion-readiness / Gate-A scorecard for the Route 2 `SANDBOX_PASS` benchmark (does it clear controls + holdout for a first RESULT candidate?) | `docs/reviews/stellar-ml-*`, stellar agent runs |
| **Atomic** | (a) `TASK-0742` Pizzocaro ledger gate [READY]; (b) scout a 3rd high-precision Yb/Sr direct-ratio source (open/arXiv-first) to de-limit the benchmark | `data/atomic_clocks/`, `docs/reviews/atomic-*` |
| **Quantum** | Tier-1/2 open-tabular scout for a QD size↔energy source (`TASK-0751` policy); Almeida Tier-3 digitization only as fallback | `data/quantum_dots/`, `docs/reviews/quantum-*` |
| **Nuclear** | Preserve diagnostic/negative memory; open exactly one non-F2 no-leakage hypothesis lane; monitor for reveal data | nuclear hypotheses/reviews |
| **Exoplanet** | Preserve negative-control memory; monitor for a reviewed later pinned snapshot; do not re-run compact-radius pilots | exoplanet reviews |
| **Mature x4** | Verifier-quality-floor support: regression, replay, hardening; available for parallel agents at low new-science priority | respective campaign dirs |

## Coordination Rules For Parallel Agents

- One agent per lane per branch/worktree; lanes above are disjoint by design.
- Apply the [open-licensed-first preference order](../fresh-data-intake-protocol.md#source-selection-preference-order-open-licensed-first)
  when any lane needs a new source.
- Do not re-open a closed-source figure-digitization lane (Quantum Tier 4) while
  a Tier 1/2 open candidate is untried.
- Reveal-gated lanes (Nuclear, Exoplanet) stay monitor/diagnostic; do not force
  scoring without reveal data.

## Proposed Mission Recommendation (maintainer sign-off required)

Recommend `missions/current.yaml` foreground the **two open-data parallel leads**
(Materials, Stellar M-L) as the nearest first-frontier-RESULT paths, keep Atomic
/ Quantum / Nuclear / Exoplanet on the bounded lanes above, and keep the mature
campaigns in support. This file is not edited by this task.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (portfolio prioritization / workflow recommendation).
- **Canonical destination:** this lane map + a one-line pointer in `docs/current-missions.md`; `TASK-0752` → `REVIEW_READY`.
- **Review tier:** `none`.
- **Gate A status:** not attempted. **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** portfolio routing only; no knowledge entry.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** advisory only; `missions/current.yaml` change needs maintainer sign-off; the Stellar/textbook-formula-audit scope and the two reveal-gated lanes are lower-confidence and should be confirmed by the maintainer.
