# Textbook Formula Audit — Candidate List

This note records the ordered candidate slate for the Textbook Formula Audit
campaign (`docs/campaigns/textbook-formula-audit.md`,
`campaign_profiles/textbook-formula-audit.yaml`). Each candidate is one
formula audit slice with a named primary source, a public dataset target,
and a declared verification gate slate.

This is a **triage note**, not a roadmap commitment. Candidates here are
ordered by combined criteria of: dataset openness, verification-gate fit,
falsifiability clarity, audit isolation (no overlap with other campaigns'
write surfaces), and parallel-agent friendliness.

No candidate listed here may be audited until a per-candidate
source/baseline planning task is opened, accepted, and proceeds through the
standard agent task protocol.

## Ranking Criteria

For each candidate the table below records:

- **Source openness**: O = fully open public dataset, R = available via
  registration, P = paywalled (excluded).
- **Verification-gate fit**: number of APL gauntlet-style gates that
  meaningfully apply (dimensional consistency, limiting behaviour,
  asymptotic alignment, monotonicity, evenness, separatrix).
- **Falsifiability clarity**: clear pass/fail per slice with a published
  primary source declaring validity range.
- **Audit isolation**: the audit's dataset and review surface do not
  collide with any current APL campaign's write surface.
- **Parallel-agent friendliness**: multiple agents can run independent
  per-slice audits without coordination.

## Ordered Candidate Slate

### 1. Stellar Mass-Luminosity (M-L) Out-of-Distribution Audit — **first recommended slice**

- **Primary source**: Russell (1914); Eddington (1924); modern parameterised
  forms summarised in Salaris & Cassisi (2005), `L ∝ M^α` with α ≈ 3.5 on the
  main sequence and known piecewise α by mass range.
- **Dataset target**: Gaia DR3 (full public release) main-sequence stars
  with derived stellar masses and luminosities, restricted to a curated
  quality-flag subset.
- **Why first**: largest open astrophysics dataset, century-old formula
  with well-documented breakdowns by mass range / metallicity / evolutionary
  stage, multiple verification gates apply directly (monotonicity in mass,
  limiting behaviour at low and high mass, dimensional consistency,
  asymptotic alignment at the convective-radiative boundary).
- **Expected outcome shape**: per-mass-range verdicts; clean failure map
  across the convective/radiative boundary and the upper-MS turnoff;
  expected `PARTIALLY_VALID` for low-mass single-power-law and
  `VALID_IN_RANGE` for the standard 1-10 M_sun window.
- **Audit isolation**: no current APL campaign touches Gaia DR3 data; no
  write-surface conflict.
- **Parallel-agent friendliness**: yes — per-mass-bin slices can be audited
  independently.
- **First follow-up task proposal**:
  `tasks/proposals/20260528-roman-stellar-mass-luminosity-ood-source-baseline-planning.yaml`.

### 2. Kleiber's Allometric Scaling Law (3/4 Power)

- **Primary source**: Kleiber (1932); West-Brown-Enquist (1997) derivation.
- **Dataset target**: open mammalian metabolic compendia (e.g. Hayssen &
  Lacy 1985 derivatives, AnAge open subset, open ZIMS-derived datasets if
  redistribution permits).
- **Why prioritised**: famous, controversial, has a long literature of
  documented breakdowns, dimensional analysis applies, several published
  null-baseline alternatives (2/3 power, body-mass-range-dependent
  exponents).
- **Expected outcome shape**: per-taxonomic-class verdicts; expected
  `PARTIALLY_VALID` for full-mammal aggregate, with explicit class-specific
  slope drift visible in the residual map.
- **Audit isolation**: cross-domain (biology) — no APL campaign collision.
- **Parallel-agent friendliness**: yes — per-class audits run independently.
- **Audit caveat**: requires explicit source-licence review for any
  biological compendium before snapshotting; some compendia restrict
  redistribution.

### 3. Wien Displacement Law

- **Primary source**: Wien (1893); standard form in Mihalas (1978).
- **Dataset target**: NIST or open spectroscopic compendia with measured
  peak emission wavelengths for objects of known temperature; calibrator
  set should include known blackbody-like astrophysical sources from public
  catalogues.
- **Why prioritised**: dimensional consistency and limiting-behaviour gates
  both apply directly; small dataset is sufficient; failure modes are
  cleanly diagnostic.
- **Expected outcome shape**: `VALID_IN_RANGE` for blackbody-approximation
  regime; `PARTIALLY_VALID` or `INCONCLUSIVE` for non-blackbody emitters
  outside the assumption window.
- **Audit isolation**: no campaign collision.
- **Parallel-agent friendliness**: yes.
- **TASK-0783 status**: selected as the next source-curation-only slice after
  Stellar M-L replay/cleanup. The selected route is NASA LAMBDA COBE/FIRAS
  source-artifact pinning for a wavelength-domain peak audit; no Wien metrics
  are ready until checksums, license posture, temperature semantics, and
  spectral-axis/domain semantics are frozen.

### 4. Stefan-Boltzmann Law

- **Primary source**: Stefan (1879); Boltzmann (1884).
- **Dataset target**: open stellar-luminosity / effective-temperature
  catalogues (Gaia DR3 derived parameters, or a Hipparcos calibrator
  subset).
- **Why prioritised**: same scaffolding as Wien, complementary slice;
  pairs well with the M-L audit as a stellar-physics duo.
- **Expected outcome shape**: `VALID_IN_RANGE` for non-evolved stars at
  Solar metallicity; failure surfaces around stellar evolution stages
  outside the calibration window.
- **Audit isolation**: shares Gaia DR3 with the M-L audit; will reuse the
  M-L snapshot once that snapshot is pinned. Coordinate so two audits
  share one snapshot.
- **Parallel-agent friendliness**: yes — once snapshot is shared.

### 5. Tully-Fisher Relation

- **Primary source**: Tully & Fisher (1977).
- **Dataset target**: SPARC galaxy rotation-curve database (open).
- **Why prioritised**: open dataset, dimensional consistency applies,
  well-documented breakdowns by galaxy type and HI-rich-vs-poor regimes;
  a strong falsification target.
- **Expected outcome shape**: `PARTIALLY_VALID` for spiral subset;
  `OVERFITTED` for early-type galaxies; piecewise-by-Hubble-type residual
  map.
- **Audit isolation**: no collision.
- **Parallel-agent friendliness**: per-type slices.

### 6. Faber-Jackson Relation

- **Primary source**: Faber & Jackson (1976).
- **Dataset target**: open elliptical galaxy velocity-dispersion catalogues
  (e.g. ATLAS3D where redistribution permits, or HyperLeda subset).
- **Why prioritised**: companion to Tully-Fisher for elliptical galaxies;
  same audit machinery, different dataset surface.
- **Audit isolation**: no collision.
- **Parallel-agent friendliness**: yes.

### 7. Gell-Mann–Okubo Mass Formula

- **Primary source**: Gell-Mann (1961); Okubo (1962).
- **Dataset target**: PDG (open) baryon and meson octet/decuplet mass
  tables.
- **Why prioritised**: APL already has Koide / particle-mass infrastructure
  (`data/particle_masses/`, `physics_lab/workflows/koide_*.py`); this audit
  extends that infrastructure to the SU(3) quark-model mass-formula
  surface without overlap.
- **Expected outcome shape**: per-multiplet verdicts; `PARTIALLY_VALID`
  for ground-state octets, `INCONCLUSIVE` or `OVERFITTED` for excited
  states.
- **Audit isolation**: extends existing particle-mass campaign rather than
  competing with it; coordinate write surfaces carefully.
- **Parallel-agent friendliness**: per-multiplet audits.

### 8. Bode-Titius Pattern Audit (Falsification target)

- **Primary source**: Titius (1766); Bode (1772).
- **Dataset target**: NASA Exoplanet Archive (already pinned for the
  exoplanet campaign) plus Solar System bodies.
- **Why prioritised**: high-virality falsification target; standard view is
  that the pattern is not predictive for exoplanetary systems, but a
  disciplined audit on a pinned snapshot makes that judgement reproducible.
- **Expected outcome shape**: `FALSIFIED` for exoplanetary systems on the
  pinned snapshot; per-system audits.
- **Audit isolation**: shares the exoplanet PSCompPars snapshot — must
  coordinate snapshot reuse rather than reingesting.
- **Parallel-agent friendliness**: per-system audits.

### 9. Hubble Law (Local Universe Window)

- **Primary source**: Hubble (1929).
- **Dataset target**: NED open subset for low-redshift recession velocities
  vs distances.
- **Why prioritised**: dimensional consistency and limiting-behaviour gates
  apply; high name-recognition; bounded to **local-universe window only**
  to stay out of the Hubble tension landscape.
- **Audit caveat**: must be **explicitly bounded** to low-redshift sample
  (e.g. z < 0.05) to avoid drifting into a Hubble-tension audit, which is a
  separate political-and-technical risk surface.
- **Audit isolation**: no current APL collision.
- **Parallel-agent friendliness**: yes.

### 10. Sutherland Viscosity Formula

- **Primary source**: Sutherland (1893).
- **Dataset target**: NIST WebBook gas viscosity data (open).
- **Why prioritised**: small dataset, clear validity window, demonstrates
  the audit machinery on a non-astrophysical, non-biological slice.
- **Audit isolation**: no collision.
- **Parallel-agent friendliness**: per-gas audits.

## Excluded Or Deferred Candidates

The following candidates were considered but excluded from the initial
slate:

- **Climate-sensitivity formulas** — excluded on political/policy risk
  grounds; the campaign's discipline does not change the fact that climate
  sensitivity audits are reputationally hazardous before a stable APL
  external review process exists.
- **Pioneer / flyby anomaly audits** — excluded because the dataset
  pinning is non-trivial and the topic is closer to single-paper reanalysis
  than to textbook formula auditing.
- **Famous-paper-reproducibility sweep in physics** — excluded as a
  separate campaign concept (not a textbook-formula audit); should live
  under its own campaign if pursued.
- **Cosmological-constant landscape audits** — excluded for the same
  political and technical-difficulty reasons as climate sensitivity.
- **Drug dose-response formula audits** — excluded as biology-heavy and
  cross-domain; should live under a future "biomedical formula audit"
  campaign rather than diluting the textbook-physics-formula campaign.

## Slate Maintenance

Order in this note is **advisory**, not authoritative. The maintainer or a
campaign curator may reorder, add, or remove candidates. Any new candidate
must declare: a primary published source, an open dataset target, an audit
isolation note, and a verification-gate slate.

Each candidate becomes a real audit only when a per-candidate source/baseline
planning task is opened, accepted, and proceeds through the standard agent
task protocol.

## Cross-References

- `docs/campaigns/textbook-formula-audit.md` — campaign charter and
  guardrails.
- `campaign_profiles/textbook-formula-audit.yaml` — machine-readable
  campaign profile.
- `docs/result-promotion-protocol.md` — multi-tier review-tier promotion
  policy that applies to any RESULT artifact produced under this campaign.
- `tasks/proposals/20260528-roman-stellar-mass-luminosity-ood-source-baseline-planning.yaml`
  — first follow-up task proposal for the Stellar Mass-Luminosity OOD audit
  source and baseline planning step.
