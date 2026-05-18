# Nuclear Scout Lane Synthesis After PRED-0062

**Task:** TASK-0285
**Scope:** sandbox-only synthesis of three completed scout lanes
(TASK-0278 shell-neighborhood, TASK-0279 neutron-rich, TASK-0280 pairing /
odd-even) against the post-`PRED-0062` registry status snapshot.

This note does not run new fits, score new reveals, register new `PRED-*`
entries, update claims, or promote sandbox signals as discoveries. It only
ranks committed sandbox evidence so that maintainer-selected follow-ups can
be planned conservatively.

## Inputs Reviewed

- `docs/reviews/nuclear-shell-neighborhood-variant-scout-001.md` (AGENT-RUN-0012)
- `docs/reviews/nuclear-neutron-rich-variant-scout-001.md` (AGENT-RUN-0013)
- `docs/reviews/nuclear-pairing-odd-even-variant-scout-001.md` (AGENT-RUN-0014)
- `docs/reviews/nuclear-prediction-registry-status-after-pred-0062.md`
- `docs/reviews/nuclear-prediction-registry-coverage-audit.md`

All three scouts fit linear corrections on the 11-row NMD-0002 residual
slice and report MAE deltas on the pinned post-AME2020 holdout. Effect sizes
are sub-MeV in every executed candidate and are retrospective diagnostics,
not prospective measurement comparisons.

## Combined Result Table (executed candidates only)

| Candidate | Family | Description | Primary ΔMAE (MeV) | Best subset ΔMAE (MeV) | Local verdict |
|-----------|--------|-------------|--------------------:|------------------------:|---------------|
| SHELL-SCOUT-003 | shell | proton-only Gaussian `β_z·s_z²` | **−0.0915** | magic_z −0.388, magic_n −0.292, heavy −0.088 | `PARTIALLY_VALID` |
| SHELL-SCOUT-005 | shell | proton × neutron product `β_p·s_z²·s_n²` | −0.0716 | magic_n −0.411, heavy −0.090 | `PARTIALLY_VALID` |
| SHELL-SCOUT-002 | shell | neutron-only Gaussian `β_n·s_n²` | −0.0620 | magic_n −0.592, heavy ≈ 0 | `PARTIALLY_VALID` |
| NR-SCOUT-003 | neutron-rich | positive asymmetry fraction | −0.0243 | asymmetry ≥ 0.25 −0.126 | `PARTIALLY_VALID` |
| NR-SCOUT-004 | neutron-rich | frontier excess after N−Z = 20 | −0.0181 | asymmetry ≥ 0.25 −0.143 | `PARTIALLY_VALID` |
| PAIR-SCOUT-003 | pairing | pairing cube-root | −0.0085 | even-even −0.015, odd-odd −0.021 | `PARTIALLY_VALID` |
| SHELL-SCOUT-006 | shell | near-null control | 0 | 0 | `INCONCLUSIVE` |
| PAIR-SCOUT-002 | pairing | baseline-shape pairing (dormant) | 0 | 0 | `INCONCLUSIVE` |
| NR-SCOUT-001 | neutron-rich | quadratic neutron-excess ramp (dormant) | 0 | 0 | `INCONCLUSIVE` |
| NR-SCOUT-006 | neutron-rich | near-null control | 0 | 0 | `INCONCLUSIVE` |
| PAIR-SCOUT-006 | pairing | near-null control | 0 | 0 | `INCONCLUSIVE` |
| PAIR-SCOUT-001 | pairing | pairing inverse-A | +0.007 | even-even +0.014, odd-odd +0.015 | `INCONCLUSIVE` |
| NR-SCOUT-002 | neutron-rich | cubic neutron-excess ramp | +0.025 | asymmetry ≥ 0.25 +0.138 | `INCONCLUSIVE` |
| SHELL-SCOUT-001 | shell | combined `β_z·s_z² + β_n·s_n²` | +0.047 | near_magic +0.113 | `OVERFITTED` |
| SHELL-SCOUT-004 | shell | proton-vs-neutron contrast | +0.072 | near_magic +0.189 | `OVERFITTED` |
| PAIR-SCOUT-004 | pairing | odd-A offset | +0.080 | odd-A +0.151 | `INCONCLUSIVE` |
| PAIR-SCOUT-005 | pairing | per-parity-class offsets | +0.167 | odd-odd +0.333 | `OVERFITTED` |
| NR-SCOUT-005 | neutron-rich | matched quadratic+cubic pair | **+1.369** | asymmetry ≥ 0.25 **+4.812** | `OVERFITTED` |

Negative ΔMAE means the candidate reduces retrospective MAE relative to the
frozen `RESULT-0015::model_fitted_semi_empirical` baseline. Positive ΔMAE
means regression.

## Ranking by Effect Size, Consistency, and Overfit Risk

### Strongest sub-MeV signals (shell axis)

The three shell-axis `PARTIALLY_VALID` candidates dominate the primary
ΔMAE table. Among them:

- **SHELL-SCOUT-003** (proton-only Gaussian) is the most consistent: it has
  the best primary ΔMAE (−0.092 MeV), improves both magic_z and magic_n,
  and is the only candidate that simultaneously improves `heavy_a_ge_100`
  (−0.088 MeV) and the magic subsets with a single free coefficient. Its
  one-parameter form lowers overfit risk relative to combined or product
  forms.
- **SHELL-SCOUT-005** (proton × neutron product) is the second-strongest
  signal and matches SHELL-SCOUT-003 on the heavy subset (−0.090 MeV). It
  is a useful cross-check because its functional form is non-additive, so
  a coherent SHELL-SCOUT-003 + SHELL-SCOUT-005 picture would be a stronger
  shell-axis indication than either alone.
- **SHELL-SCOUT-002** (neutron-only Gaussian) is the strongest single-axis
  effect on a single subset (`magic_n` −0.592 MeV) but leaves
  `heavy_a_ge_100` essentially flat (+0.020 MeV). It is the cleanest
  neutron-axis cross-check to SHELL-SCOUT-003.

### Smaller non-shell signals

- **NR-SCOUT-003** and **NR-SCOUT-004** are smaller primary signals
  (−0.024 and −0.018 MeV) but show concentrated improvement on the
  asymmetry-rich subset (−0.126 and −0.143 MeV at asymmetry ≥ 0.25). They
  are worth recording as candidate review surfaces specifically for the
  high-asymmetry frontier, not as general baseline corrections.
- **PAIR-SCOUT-003** (cube-root pairing) is real but tiny (−0.0085 MeV
  primary; −0.021 MeV on odd-odd, where NMD-0002 has only one row). The
  effect is too small and too coupled to a one-row subset to chase as a
  follow-up family.

### Negative results worth preserving

- **NR-SCOUT-005** is the strongest single negative result in the queue
  (+1.369 MeV primary, +4.812 MeV on asymmetry ≥ 0.25). It is a clean
  example of how a slightly higher-capacity neutron-excess ramp blows up at
  the high-asymmetry frontier and should be preserved as a documented
  negative control for any future reveal package.
- **SHELL-SCOUT-001** (additive combined form) regresses primary by
  +0.047 MeV even though magic_any improves by −0.259 MeV — a textbook
  example of subset-improvement-with-primary-regression overfit pattern.
- **SHELL-SCOUT-004** (proton-vs-neutron contrast) regresses on every
  reported subset. Preserve as a sign-flip negative control rather than a
  candidate.
- **PAIR-SCOUT-005** (per-parity-class offsets) regresses on every reported
  subset; useful as a complexity-budget negative.

### Inconclusive / dormant outcomes

- The near-null controls (`SHELL-SCOUT-006`, `NR-SCOUT-006`,
  `PAIR-SCOUT-006`), the baseline-shape pairing reuse (`PAIR-SCOUT-002`),
  and the dormant `NR-SCOUT-001` confirm that fitting machinery is not
  injecting spurious signal. Keep them as runner regression checks; do not
  treat them as candidate families.

## Repeated-Target Pressure (from coverage audit)

`Ni-76` appears in 18 registry entries; `Ca-55`, `Ga-85`, and `Zn-80` each
appear in 14. The registry's `mid-mass` domain has only one entry. Any
follow-up that produces frozen `PRED-*` entries should:

- avoid further amplifying `Ni-76` or the three 14-repeat targets;
- prefer mid-mass or isotope-chain targets to reduce repeated-target
  pressure;
- record sign-paired controls when registering a new family so future
  reveal interpretation is not biased toward agreement.

These constraints argue against immediately producing more registry waves
from any of the shell-axis candidates above; they should pass adversarial
review and an explicit target-batch design step first. That is the role of
a future maintainer-selected follow-up task, not of this synthesis.

## Recommended Follow-Up Families (≤ 3)

The protocol allows at most 1–3 follow-up families. The synthesis
recommends the following, in priority order, for **future maintainer
review and follow-up task assignment only** — not for immediate registry
expansion:

1. **SHELL-SCOUT-003 (proton-only Gaussian).** Strongest, most consistent,
   single-parameter signal. The natural follow-up is an adversarial review
   pass and a small paired-control registry design (with a sign-inverted
   negative control) targeting under-covered mid-mass or isotope-chain
   nuclides rather than the high-repeat targets (`Ni-76`, `Ca-55`,
   `Ga-85`, `Zn-80`).
2. **SHELL-SCOUT-005 (proton × neutron product).** Promote only as a
   cross-check companion to SHELL-SCOUT-003 in the same follow-up; both
   families should fail or succeed coherently to be treated as real shell
   signal.
3. **NR-SCOUT-003 (positive asymmetry fraction).** Scope the follow-up
   strictly to the high-asymmetry frontier subset where the effect is
   concentrated. Pair with `NR-SCOUT-005` as the documented negative
   control. Lower priority than the shell pair because the primary effect
   is smaller and a quadratic+cubic neighbor (NR-SCOUT-005) overfits
   catastrophically — that asymmetric-axis is fragile.

Not recommended for follow-up:

- **SHELL-SCOUT-002** alone — it carries useful magic_n information but
  largely overlaps with SHELL-SCOUT-003; include it inside the same
  shell-axis follow-up design rather than as a separate family.
- **NR-SCOUT-004** — concentrated on asymmetry ≥ 0.25 like NR-SCOUT-003,
  so the same review can capture it without a separate family.
- **PAIR-SCOUT-003** — effect size too small and overly dependent on a
  one-row odd-odd training subset.
- All `OVERFITTED` and `INCONCLUSIVE` candidates as primary follow-ups.

The cap of 1–3 families is honored: families 1+2 form one shell-axis
review and family 3 is a separate asymmetric-frontier review.

## Boundary Restated

- This synthesis is sandbox-only. No `PRED-*` entry, claim, result, or
  knowledge artifact is created or modified.
- All effect sizes are retrospective diagnostics on the post-AME2020
  surface and on an 11-row training slice. They are not prospective
  predictions and not evidence for a new nuclear mass law.
- Any future `PRED-*` registration from these recommendations must go
  through a separate maintainer-approved task that specifies target batches,
  paired negative controls, and target-overlap discipline.
- Repeated-target pressure on `Ni-76`, `Ca-55`, `Ga-85`, `Zn-80` and the
  thin mid-mass coverage mean the next registry wave should bias toward
  underrepresented nuclides; this aligns with the parallel TASK-0286
  mid-mass / isotope-chain gap scout.

## Verdict

Three completed scout lanes leave a small, consistent, sub-MeV
shell-axis signal (best captured by SHELL-SCOUT-003, with SHELL-SCOUT-005
as a cross-check), a smaller asymmetry-frontier signal (NR-SCOUT-003), and
a useful catalogue of dormant and overfit controls. The recommended
follow-up surface is at most two adversarial-review tasks. No registry
expansion is justified from this synthesis alone.
