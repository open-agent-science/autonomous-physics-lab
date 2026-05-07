# PMR-010 — Allowed vs Disallowed Triplet Mixing Under Koide Numerology Guardrails

**Microtask:** `PMR-010`
**Campaign:** `particle-mass-relations`
**Type:** `guardrail-note`
**Status:** REVIEW_NEEDED
**Date:** 2026-05-07

---

## Family Mix Being Evaluated

This note addresses triplets that combine particles from different sectors:
- **Cross-family mixing**: {me, mμ, ms} (lepton + quark)
- **Cross-generation mixing within a sector**: {mu, mc, mb} (mixed-generation quarks)
- **Same-family same-generation**: {me, mμ, mτ} (the canonical charged-lepton triplet)

---

## Guardrail Reasoning

### G1 — Physical motivation requirement

The Koide formula was originally proposed for charged leptons as a family
(same gauge quantum numbers, same generation pattern, no mixing allowed by
SM quantum numbers). Applying it to cross-family triplets violates the
original physical motivation:
- Leptons and quarks have different color charge, weak isospin, and
  renormalization-group running behavior.
- A Koide-like relation between a lepton mass and a quark mass would require
  a physical mechanism connecting the two sectors — none is established in SM.
- Cross-family triplets are therefore **numerology candidates by default**:
  any match found should be treated as accidental until an independent
  physical argument for the coupling is provided.

### G2 — Trials inflation risk

The charged-lepton triplet {me, mμ, mτ} is **one specific combination**
with a prior (Koide's publication). The number of possible triplets from
all known particle masses (charged leptons + neutrinos + 6 quarks) is:
C(12, 3) = 220 combinations (ignoring ordering). Note: neutrino masses
are not individually measured (only mass-squared differences are known),
so the effective count is lower if neutrinos are excluded, but the
argument about trials inflation holds regardless.
Of these 220, at most a handful have physical motivation (same-family,
same-generation, known mixing structure). Testing all combinations and
reporting the best match inflates the effective trials count by a large
factor, which is not corrected by the bare z-score of the best match.

Any result from a cross-family or untargeted triplet scan **must** report:
- the total number of triplets tested,
- the number that passed the match criterion,
- the expected number of accidental matches at the same precision threshold.

### G3 — Scale ambiguity is worse in mixed triplets

Quark mass values depend on renormalization scheme and scale (MS-bar at 2 GeV,
pole mass, etc.), while lepton masses are physical pole masses. A mixed
lepton+quark triplet combines quantities defined at different scales — the
numerical value of Q depends on which quark mass definition is used, making
any "closeness" claim scheme-dependent.

---

## Classification of Specific Mixing Patterns

| Triplet | Family Mix | Status under guardrails |
|---|---|---|
| {me, mμ, mτ} | Same-family, same sector | **Allowed** — canonical, physically motivated |
| {mν₁, mν₂, mν₃} | Same-family, same sector | **Allowed** (tested in EXP-0007, result INVALID) |
| {mu, mc, mt} | Same sector, mixed generation | **Requires justification** — quark cascade tested in EXP-0008, result INVALID |
| {md, ms, mb} | Same sector, mixed generation | **Requires justification** — tested in EXP-0008, result INVALID |
| {me, mμ, ms} | Cross-sector lepton+quark | **Disallowed without new physical argument** — numerology by default |
| {mτ, mb, mt} | Cross-sector lepton+quark | **Disallowed without new physical argument** |
| Any triplet found by post-hoc search over all masses | Untargeted | **Requires full trials correction** |

---

## Guardrail Tie-Back

This classification applies the anti-cherry-picking guardrail from
`docs/notes/particle-mass-numerology-guardrails.md` (produced by TASK-0042):
> "no hand-selected particle triplet may be presented as meaningful without
> stating whether other eligible triplets were considered"

Cross-sector triplets lack independent physical motivation predating the
numerical coincidence. The SM does not predict Koide-like structure between
quarks and leptons, and no established BSM model provides such a connection
at the mass-eigenvalue level without introducing many additional parameters.

---

## Claim Ceiling

This note establishes which triplet mixes are safe or unsafe under current
numerology guardrails. It does not prove that disallowed triplets are
physically meaningless — it states that any match found in them requires
independent physical justification before it can be classified above
NUMEROLOGY tier.
