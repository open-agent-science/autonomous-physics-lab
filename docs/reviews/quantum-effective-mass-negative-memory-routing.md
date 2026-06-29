# Quantum Effective-Mass Transfer Negative-Memory Routing

**Task:** `TASK-0871`  
**Source run:** `AGENT-RUN-0085`  
**Source task:** `TASK-0850`  
**Verdict:** `NEGATIVE_MEMORY_ACCEPTED_SANDBOX_ONLY`

## Purpose

This planning-only scorecard routes the committed InP-ZnSe effective-mass
transfer evidence into durable negative memory. It reruns no metric, changes no
effective mass or dataset value, adds no fitted rescue term, and does not modify
`TASK-0226` or any `RESULT`, `PRED`, `CLAIM`, or `KNOW` artifact.

The bounded conclusion is about one fixed bulk reduced-mass prefactor on the
current six-row InP TEM and ten-row ZnSe SAXS surfaces. It is not a conclusion
that effective mass is generally irrelevant to quantum confinement.

## Evidence Reviewed

- [`AGENT-RUN-0085` metrics](../../agent_runs/AGENT-RUN-0085/metrics.json) and
  [report](../../agent_runs/AGENT-RUN-0085/report.md).
- [TASK-0850 transfer review](quantum-effective-mass-scaled-confinement-transfer.md).
- [Frozen effective-mass inputs](../../data/quantum_dots/effective_mass_inputs.yaml).
- The TASK-0842 bulk-gap-only transfer values embedded in the source run.

The frozen rule was

`mu = (1 / me + 1 / mh)^-1`

and

`C_target = C_source * mu_source / mu_target`.

No mass, source coefficient, exponent, threshold, or scaling factor was fitted
on either holdout.

## Primary Evidence

The primary TASK-0850 framing converts the tetrahedral InP edge length to an
equal-volume spherical diameter before transfer.

| Direction | mass-scaled MAE (eV) | bulk-gap-only MAE (eV) | degradation (eV) | best control MAE (eV) | shortfall vs control (eV) |
| --- | ---: | ---: | ---: | ---: | ---: |
| InP -> ZnSe | `0.161570` | `0.099216` | `0.062354` | `0.145800` | `0.015770` |
| ZnSe -> InP | `0.991542` | `0.119375` | `0.872168` | `0.219500` | `0.772042` |

Both primary directions worsen relative to the bulk-gap-only transfer and lose
to the held-out per-material-mean control. Neither clears the predeclared
`0.05 eV` survival margin.

## Framing-Sensitivity Check

The committed characteristic-length sensitivity framing moves in the opposite
direction:

| Direction | mass-scaled MAE (eV) | bulk-gap-only MAE (eV) | margin vs best control (eV) |
| --- | ---: | ---: | ---: |
| InP -> ZnSe | `0.048033` | `0.354724` | `0.097551` |
| ZnSe -> InP | `0.162912` | `0.381642` | `0.056588` |

This sensitivity result does not replace the predeclared primary judge. It
shows that the apparent transfer outcome depends strongly on how unlike TEM
and SAXS size observables are mapped to a common length. Selecting the favorable
framing after seeing both outcomes would be post-hoc route selection.

## Routing Scorecard

| Check | Status | Evidence |
| --- | --- | --- |
| Inputs frozen before scoring | `PASS` | Literature masses and both material datasets are committed; no holdout fit was used. |
| Bidirectional primary improvement | `FAIL` | Primary degradation is `0.062354 eV` forward and `0.872168 eV` reverse. |
| Best-control survival | `FAIL` | Both primary directions lose to the per-material-mean control. |
| Framing stability | `FAIL` | Equivalent-diameter and characteristic-length framings give opposite route decisions. |
| Source breadth | `LIMITED` | Two materials, one source and morphology per material, with 6 and 10 direct-size rows. |
| Effective-mass scope | `LIMITED` | Scalar bulk masses omit nonparabolicity, anisotropy, dielectric confinement, Coulomb terms, and finite barriers. |
| Independent replay | `NOT_ATTEMPTED` | Replay is not required to preserve internal do-not-repeat memory, but is required before stronger public or canonical-result wording. |
| Promotion readiness | `FAIL` | Primary controls and framing stability do not support Gate A packaging. |

## Routing Decision

Keep `AGENT-RUN-0085` as sandbox evidence and use this note as its durable
negative-memory index. Do not create a canonical result or a separate
public-facing card from the current evidence.

Independent replay is not required merely to stop repeated execution of the
same bounded route. It becomes mandatory before any later task proposes a
canonical result or stronger public wording. No replay task is proposed now:
repeating the unchanged computation would not alter the source and framing
limitations.

## Do-Not-Repeat Boundary

Do not rerun or repackage the simple bulk reduced-mass prefactor as a rescue on
the current InP/ZnSe surfaces when all of these remain unchanged:

- the same six InP TEM and ten ZnSe SAXS rows;
- equivalent spherical diameter as the primary cross-material size mapping;
- the same scalar bulk electron and hole masses;
- `C_target = C_source * mu_source / mu_target` with the source exponent fixed;
- the same mean and shuffled-size controls and `0.05 eV` margin.

In particular, do not tune masses, coefficients, exponents, geometry mappings,
or thresholds against either holdout; do not promote the favorable
characteristic-length sensitivity framing after reveal; and do not use the
negative result for material, device, or biomedical recommendations.

`TASK-0226` remains closed/superseded and is not reopened by this routing.

## Reopen Conditions

The lane may be reconsidered only when the scientific surface changes before
scoring. A valid reopen requires at least one of:

1. a materially disjoint, source-admissible direct-size material pair;
2. a predeclared and independently justified cross-morphology size-observable
   harmonization contract;
3. a fixed nanocrystal model that adds physically sourced finite-barrier,
   dielectric, Coulomb, anisotropy, or nonparabolic corrections without fitting
   the target holdout; or
4. independent replay attached to a separately authorized promotion task after
   one of the preceding changes.

Changing only a scalar bulk mass, choosing a favorable size framing after
inspection, or adding a fitted residual term does not reopen the lane.

## Output Routing Summary

- **Task verdict:** `NEGATIVE_MEMORY_ACCEPTED_SANDBOX_ONLY`.
- **Canonical destination:** this review note plus unchanged
  `agent_runs/AGENT-RUN-0085/` evidence.
- **Review tier:** `none`.
- **Gate A status:** not attempted; primary control and framing-stability gates
  fail.
- **Gate B status:** not attempted; no independent replay was run.
- **Result impact:** none; no canonical result created or modified.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** two-material source ceiling, opposite framing
  outcomes, primary control failure, and no independent replay.

