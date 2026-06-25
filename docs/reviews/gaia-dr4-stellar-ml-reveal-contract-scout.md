# Gaia DR4 Stellar M-L Reveal-Contract Scout

- Task: `TASK-0834`
- Date: `2026-06-25`
- Mode: prospective reveal-CONTRACT readiness scout (planning-only)
- Verdict: **`NEEDS_FIELDS`**
- Anchor result: `RESULT-0022` (`results/EXP-0015/RUN-0001/result.yaml`)

## Scope And Non-Goals

This note scouts whether a future prospective freeze-then-reveal can use the
already-validated stellar mass-luminosity result `RESULT-0022` as a frozen
blind prediction against a future authoritative Gaia DR4 release. It establishes
the reveal CONTRACT and returns a single verdict. It is contract readiness only.

This scout does NOT, and a future executor of this contract must separately
gate before doing any of, the following:

- freeze any prediction or register/score a `PRED-*` entry;
- fetch, download, or ingest any Gaia DR4 data or any DR4 value (DR4 is
  unreleased);
- create or promote any `RESULT-*`, `CLAIM-*`, or knowledge artifact;
- edit `RESULT-0022`, the frozen DEBCat slice, or any other task.

No live web value was copied into the repository. Only public ESA/Gaia source
metadata and the committed `RESULT-0022` artifacts were inspected. The Gaia DR4
release date below is recorded from the official ESA page with its verification
status; it is NOT hardcoded as immutable.

## Anchor: What RESULT-0022 Actually Is

`RESULT-0022` is a controlled stellar mass-luminosity baseline benchmark on a
frozen DEBCat detached-eclipsing-binary slice. Its domain, variables, and units
constrain what a compatible DR4 reveal must look like.

| Property | RESULT-0022 value |
| --- | --- |
| Domain | Main-sequence-compatible detached eclipsing binary components |
| Mass range | `0.5-2.0 M_sun`, 223 admitted components |
| Mass quantity | Direct dynamical mass (DEBCat), `mass_provenance_class: direct_observation` |
| Luminosity quantity | `log_luminosity_solar` (log L in `L_sun`) |
| Luminosity provenance | Mixed row-level: DEBCat catalogue-reported `log L` and Stefan-Boltzmann-derived `log L` from `log R`, `log T` |
| Relation form | `log L = alpha * log M` (fixed intercept `L0=1`) |
| Scoring metric | Holdout MAE in `dex` of `log L`; null = per-mass-band train-median |
| Split unit | `system_id` (system-level, no binary-component leakage) |
| Source | DEBCat (Southworth), committed Route 2 rows, CC BY 4.0 (TASK-0763) |
| Review tier | `AGENT_VALIDATED` (Gate B replay, TASK-0776); not maintainer-reviewed |
| Headline scope | `alpha=3.5` inadequate as the SOLE frozen baseline on this slice; NOT a universal-law claim |

Two facts dominate the contract design:

1. RESULT-0022 already trained on DEBCat. DEBCat therefore cannot be used as a
   fresh, independent control without explicit leakage handling (see Control
   Set and Leakage).
2. RESULT-0022's target is luminosity in `L_sun` (log L, dex), derived per-row
   from catalogue values or Stefan-Boltzmann. Any DR4 luminosity used as the
   reveal target must be reconciled to that quantity and provenance, or the
   reveal must convert and document the difference.

## Official Gaia DR4 Release Source And Date

| Field | Value |
| --- | --- |
| Release | Gaia Data Release 4 (Gaia DR4) |
| Stated date | 2 December 2026 |
| Official source pages | ESA Cosmos Gaia "Data Release Scenario"; ESA Cosmos Gaia DR4 landing page; ESA Cosmos Gaia DR4 content page |
| Date checked | 2026-06-25 |
| Verification status | **Verified-on-official-page, but explicitly a TARGET scenario, not immutable** |

What the official ESA pages actually say (paraphrased, with the load-bearing
wording quoted):

- The ESA Cosmos "Gaia Data Release Scenario" page lists 2 December 2026 as the
  planned DR4 date (DR4 based on 66 months of data), and presents it as part of
  the "target _release scenario_" that is "based on the current status of
  processing," adding that "final, detailed release contents will be decided on
  only after completion of the validation work."
- The ESA Cosmos Gaia DR4 landing page shows "Coming up: 2 December 2026" and
  states a contents overview is available now, with an update expected "End of
  June 2026 ... specifying number of sources for data products."
- A December 2025 ESA Cosmos Image-of-the-Week describes "Gaia Data Release 4
  (Gaia DR4) in December 2026" as "the first true release for the Gaia mission,
  where all data types are released for the full nominal mission period."

Conclusion on the date: the "2 December 2026" date from the earlier strategy
report IS now corroborated on the official ESA page, so the date itself is not a
blocker. But ESA explicitly frames it as a target tied to validation progress,
and explicitly defers final product contents and per-product source counts.
This is exactly why the verdict is `NEEDS_FIELDS` and not
`REVEAL_CONTRACT_READY`: the date is good enough to arm a contract, but the
field-level schema is not yet final.

## DR4 Product / Field Mapping (Assessed, Not Assumed)

The ESA Cosmos Gaia DR4 content page publishes a first overview of planned DR4
tables. The DR4-relevant products for a mass-luminosity reveal, and their
DR3 analogues (used only to read the intended semantics; DR3 column names and
counts are NOT guaranteed to carry into DR4), are:

| DR4 product (planned) | What it carries | Relevance to RESULT-0022 |
| --- | --- | --- |
| `nss_two_body_orbit` | NSS orbital solution parameters for astrometric, spectroscopic, and eclipsing binaries and combinations | Source of dynamical orbital constraints; eclipsing+SB2 combinations constrain both component masses |
| `nss_masses` | "Masses derived from the non-single stars (NSS) solutions with orbital parameters" | Primary candidate for the mass axis (true dynamical masses) |
| `nss_resolved_pair`, `nss_multiple_orbits`, `nss_non_linear_spectro`, `rvs_two_body_orbit` | Other NSS / RVS multiplicity solutions | Secondary / population-expansion sources; not the primary mass axis |
| `ap_rvs`, `ap_xp` | Astrophysical parameters via GSP-Spec / GSP-Phot / FLAME (incl. luminosity, radius, Teff, absolute magnitude) | Primary candidate for the luminosity axis (FLAME `L`) |

### Mass axis: assessed COMPATIBLE in semantics, unconfirmed in schema

- DR3's `binary_masses`/`nss_masses` carried `m1`, `m2` (with 16th/84th
  percentile bounds) in solar masses, "derived from the NSS solutions with
  orbital parameters" — i.e. true dynamical masses from astrometric +
  spectroscopic (SB1/SB2) + eclipsing combinations. This is the same KIND of
  quantity RESULT-0022 uses (direct dynamical mass, `M_sun`).
- Compatibility caveat: only certain solution types (notably Orbital+SB2 and
  Eclipsing+SB2 / double-lined) yield BOTH component masses; SB1/astrometric-only
  solutions yield mass functions or primary-only constraints. RESULT-0022 needs
  per-component `M` in `0.5-2.0 M_sun`, so only the two-component-mass solution
  subset is eligible. DR3 had on the order of 5,376 SB2 orbital solutions, of
  which a few hundred were flagged eclipsing — a useful but modest two-mass
  population. DR4's 66-month, full-epoch data is expected to enlarge this, but
  the DR4 two-component-mass count and the exact DR4 column names/units are not
  yet published.

### Luminosity axis: assessed PARTIALLY compatible; provenance mismatch must be reconciled

- DR4 plans FLAME-derived astrophysical parameters (`ap_rvs`, `ap_xp`). In DR3,
  `lum_flame` is luminosity in `L_sun`, computed from parallax, G magnitude,
  extinction, and a bolometric correction. The Gaia DR3 documentation states
  FLAME "observed" parameters (luminosity `L`, absolute magnitude `MG`, radius
  `R`) are "relatively model-independent," in contrast to FLAME mass/age which
  "strongly depend on evolution models." DR3 `lum_flame` agreed with the
  literature to a 2-3% median offset and 5-6% dispersion.
- This is genuinely a luminosity in `L_sun`, so it CAN map onto RESULT-0022's
  `log_luminosity_solar` target — but its provenance (parallax + bolometric
  correction via GSP-Phot) differs from RESULT-0022's DEBCat
  catalogue-reported / Stefan-Boltzmann luminosities. The reveal must either (a)
  use the same luminosity provenance family as RESULT-0022 (preferred for a
  clean comparison), or (b) explicitly declare and bound the
  provenance-difference as a systematic. A luminosity-vs-absolute-magnitude
  distinction also exists: `MG` is not bolometric `L`; only `lum_flame`
  (bolometric `L`) is admissible as the target, not `MG`.
- Critically, the dynamical-mass table and the FLAME luminosity table are
  DIFFERENT products; a row must be joined across `nss_masses` and `ap_*` on
  `source_id`. Both must exist for the same star for it to be a reveal target.

### What is uncertain until the DR4 data model is published

- Exact DR4 column names, units, and uncertainty fields for `nss_masses` and
  for FLAME luminosity (not guaranteed identical to DR3).
- The DR4 count of two-component-mass (SB2 / eclipsing+SB2) solutions in the
  `0.5-2.0 M_sun` main-sequence-compatible regime.
- Whether DR4 supplies a per-source luminosity provenance compatible with, or
  convertible to, RESULT-0022's luminosity definition.
- Whether DR4 NSS eclipsing solutions overlap RESULT-0022's DEBCat training
  systems (leakage), and to what extent.

Per ESA, per-product source counts update only at end of June 2026 and final
contents only after validation. None of these four items is confirmable now.

## Reveal Contract Specification

This is the contract a future maintainer-approved reveal task would execute. It
reuses the Blind Holdout Benchmark Protocol
([`docs/blind-holdout-benchmark-protocol.md`](../blind-holdout-benchmark-protocol.md))
and the reveal/no-peek structure of the Nuclear Prediction Reveal Protocol
([`docs/nuclear-prediction-reveal-protocol.md`](../nuclear-prediction-reveal-protocol.md)),
and the standing prospective-reveal pipeline design pattern of
[`tasks/TASK-0825-design-standing-prospective-reveal-pipeline.yaml`](../../tasks/TASK-0825-design-standing-prospective-reveal-pipeline.yaml).
It does NOT weaken the no-peek or admissibility gates of those documents.

### Trigger (admissibility gate)

The reveal task is admissible to RUN only when ALL hold:

1. Gaia DR4 is officially released (date confirmed on the ESA Gaia release page,
   not a target), and the DR4 data model for `nss_masses` and FLAME luminosity
   is published.
2. The required fields exist with confirmed units: per-component dynamical mass
   in `M_sun` and bolometric luminosity in `L_sun` (or deterministically
   convertible).
3. The frozen prediction package below was committed BEFORE the DR4 release
   timestamp (pre-reveal boundary auditable in git/PR history).
4. A leakage audit (below) is completed and the eligible target set is the
   DEBCat-disjoint subset, or the leakage-bearing subset is reported separately
   as a weaker, non-blind diagnostic.

### Frozen-prediction shape

Freeze, before reveal, exactly:

- Predictor: `RESULT-0022`'s frozen `log L = alpha * log M` family, evaluated as
  the FIXED textbook baselines (`alpha=3.5`, `alpha=4.0`) AND the
  train-fitted exponent (`alpha_hat = 4.526004`, fixed intercept `log L0 = 0`)
  exactly as recorded in `results/EXP-0015/RUN-0001/result.yaml`. No refit, no
  new model family, no coefficient re-tuning after reveal.
- Prediction target: predicted `log L` (in `L_sun`) for each eligible DR4 star
  given its DR4 dynamical `log M`.
- Eligibility regime, predeclared: per-component dynamical mass in
  `0.5-2.0 M_sun`, main-sequence-compatible, two-component-mass solution types
  only (e.g. Orbital+SB2, Eclipsing+SB2), DEBCat-disjoint (see leakage).
- Predeclared decision rule and metric below; predeclared limitations and
  failure modes (small-N, provenance systematic, residual leakage).

### Crossmatch key

- Primary key: Gaia `source_id`, joining DR4 `nss_masses` (mass axis) to DR4
  `ap_*` FLAME (luminosity axis) for the same source.
- RESULT-0022 / DEBCat-to-Gaia crossmatch (for the leakage audit only): match
  DEBCat systems to Gaia `source_id` via coordinates / existing DEBCat-Gaia
  cross-identifications, with a fixed match radius predeclared before reveal.

### Control set and leakage (independence)

RESULT-0022 already used DEBCat. Therefore:

- DEBCat is NOT an independent control here; it is the training source. Using
  DEBCat systems as DR4 reveal targets would be in-sample, not blind. The
  primary reveal target set MUST be DR4-NSS systems with NO DEBCat counterpart
  (DEBCat-disjoint), so the reveal tests extrapolation onto genuinely
  independent dynamical masses.
- Independent control: the DEBCat-disjoint DR4 two-component-mass subset is the
  control/holdout. DEBCat detached eclipsing binaries are bright, well-studied
  systems and a meaningful fraction will plausibly receive DR4 NSS eclipsing/SB2
  solutions; these overlap rows are the leakage risk and must be EXCLUDED from
  the blind score (or scored only as a separate, labelled, non-blind
  diagnostic). The leakage audit (crossmatch DR4 NSS targets against the frozen
  DEBCat row set) is a hard pre-scoring gate.
- Split discipline: keep any per-system aggregation system-level (no
  binary-component leakage), consistent with RESULT-0022.

### No-peek / no-leakage policy

- Freeze the prediction package and commit it before the DR4 release timestamp;
  the pre-reveal boundary must be visible in git/PR history.
- No DR4 value may inform candidate selection, exponent choice, regime cuts,
  thresholds, or wording. No refit after reveal.
- No live, informal, or pre-release DR4 values; only the official released DR4
  data model and tables, pinned with a source manifest and checksums per the
  reveal protocol.
- If the no-peek audit fails or DEBCat-overlap leakage cannot be excluded, the
  comparison may stand only as a retrospective diagnostic, never as prospective
  blind evidence.

### Scoring metric

- Primary: holdout MAE in `dex` of `log L` on the DEBCat-disjoint eligible DR4
  set, exactly the RESULT-0022 metric, comparing fixed `alpha=3.5`, fixed
  `alpha=4.0`, and the frozen train-fitted exponent against the per-mass-band
  median null carried from RESULT-0022.
- Predeclared decision rule: the reveal CONFIRMS the RESULT-0022 reading only if
  the frozen exponents beat the null by more than the recorded split-noise
  reference (`0.04 dex`) on the independent DR4 set; otherwise it is a recorded
  out-of-sample falsification or `INCONCLUSIVE` (prefer `INCONCLUSIVE` for small
  reveal-N), per the reveal protocol's conservative-verdict rule.
- Both outcomes are useful: a confirmed extrapolation onto independent DR4
  dynamical masses is non-gameable evidence; a documented failure is an
  out-of-sample falsification. Neither auto-promotes to a claim; promotion
  requires a separate maintainer-reviewed result/claim task.

### Fallback (if required DR4 fields are absent or incompatible)

In priority order, if DR4 does not deliver the needed fields:

1. If DR4 lacks a compatible bolometric luminosity but provides Teff + radius,
   derive `log L` via Stefan-Boltzmann (the SAME provenance class RESULT-0022
   already uses for part of its rows), predeclaring this as the luminosity route
   before reveal.
2. If DR4 two-component-mass coverage in `0.5-2.0 M_sun` is too small (e.g. < a
   predeclared minimum-N), restrict to the available regime and report
   `INCONCLUSIVE` for sparse reveal coverage rather than over-interpreting.
3. If DR4 NSS masses are not true dynamical (e.g. only model-derived FLAME
   masses are available for the overlap population) or units/semantics are
   incompatible, do NOT freeze/score against DR4. Hold the contract armed and
   fall back to the already-scoped independent transfer route
   ([`docs/reviews/stellar-ml-independent-transfer-dataset-scout.md`](./stellar-ml-independent-transfer-dataset-scout.md),
   high-mass DEBCat regime) or a later DR-data-model revision, with no claim.
4. If the DR4 date slips (it is a target scenario), keep the contract armed and
   waiting; a slipped date is "not yet revealed," not a falsification.

## Overlap-Population Estimate (estimates, with basis)

These are ESTIMATES from DR3 analogues and the DEBCat size, not DR4 facts.

| Quantity | Estimate | Basis |
| --- | --- | --- |
| DEBCat systems (RESULT-0022 source universe) | ~199-244 systems; RESULT-0022 admitted 223 components in `0.5-2.0 M_sun` | DEBCat (Southworth) catalogue metadata; `RESULT-0022` |
| DR3 two-component-mass (SB2) orbital solutions | ~5,376 SB2 systems; ~533 flagged eclipsing | Gaia DR3 NSS documentation / literature |
| DR4 two-component-mass population | Expected materially larger than DR3 (66 months, full epoch astrometry + RVS), but unquantified until the end-June-2026 / release source-count update | ESA Cosmos DR4 pages; not yet published |
| Eligible DEBCat-disjoint MS targets in `0.5-2.0 M_sun` | Plausibly order tens-to-low-hundreds, but UNKNOWN; depends on DR4 two-mass count, the MS-compatible fraction in `0.5-2.0 M_sun`, and the DEBCat-overlap removed | Derived estimate; not confirmable pre-release |
| DEBCat-DR4 overlap (leakage) | Non-zero and meaningful: DEBCat systems are bright, many likely receive DR4 NSS eclipsing/SB2 solutions; must be excluded from the blind score | Qualitative, from DEBCat's bright/well-studied nature |

The eligible blind-target count is the load-bearing unknown. It could be large
enough for a strong reveal or small enough to force `INCONCLUSIVE`; this cannot
be decided until the DR4 schema and counts publish.

## Verdict

**`NEEDS_FIELDS`** — compatible fields are plausibly present but not yet
confirmable.

Reasoning (one paragraph): The official ESA Gaia release date (2 December 2026)
is now verified on the official ESA Cosmos pages, so the contract is not
`BLOCKED` on a missing date or missing product class — DR4 plans the exact
product families a mass-luminosity reveal needs (`nss_masses` /
`nss_two_body_orbit` for true dynamical masses; `ap_rvs` / `ap_xp` FLAME for
bolometric luminosity in `L_sun`), and dynamical mass in `M_sun` is
semantically compatible with RESULT-0022's domain and units. But ESA explicitly
frames the date as a target tied to validation, defers per-product source counts
to (earliest) end of June 2026, and finalizes contents only after validation;
and three field-level questions cannot be answered until the DR4 data model
publishes: (1) the exact DR4 column names/units for `nss_masses` and FLAME
luminosity, (2) the DR4 count of two-component-mass solutions in the
`0.5-2.0 M_sun` main-sequence regime, and (3) whether DR4 luminosity provenance
can be reconciled to RESULT-0022's luminosity, plus the DEBCat-overlap leakage
must be quantified at reveal. With compatible fields probable but unconfirmable,
the disciplined verdict is `NEEDS_FIELDS`, not an overclaimed
`REVEAL_CONTRACT_READY`. The contract above is fully specified and armed; a
future task may freeze and reveal once the trigger gate is satisfied.

## Output-Routing Summary

- Verdict: `NEEDS_FIELDS`.
- Canonical destination: prospective-reveal CONTRACT readiness for a future
  Gaia DR4 stellar mass-luminosity freeze
  (`docs/reviews/gaia-dr4-stellar-ml-reveal-contract-scout.md`).
- Review tier: none; planning / contract-readiness scout only.
- Gate A: not attempted (no `RESULT-*` artifact created).
- Gate B: not attempted (no independent replay target created).
- PRED: none frozen, registered, or scored.
- DR4 data: not fetched, not ingested; date recorded with verification status,
  not hardcoded.
- Claim/Knowledge/Result impact: none; `RESULT-0022` and the frozen DEBCat slice
  are unchanged.
- Trigger / admissibility gates: official DR4 release + published data model;
  confirmed dynamical mass (`M_sun`) and bolometric luminosity (`L_sun`) fields;
  pre-reveal freeze committed before the DR4 release timestamp; DEBCat-overlap
  leakage audit passed (DEBCat-disjoint target set); no-peek audit passed.
- Limitations / blockers: DR4 schema and per-product counts not final
  (ESA: counts update earliest end of June 2026, contents after validation);
  DR4 two-component-mass coverage in `0.5-2.0 M_sun` unknown; DR4 luminosity
  provenance must be reconciled to RESULT-0022's luminosity; DEBCat-DR4 overlap
  (leakage) is non-zero and must be excluded from any blind score; the
  RESULT-0022 headline remains scoped to its frozen `0.5-2.0 M_sun` slice and is
  `AGENT_VALIDATED`, not maintainer-reviewed.

## Sources

Public source metadata consulted (no values ingested):

- ESA Cosmos Gaia, Data Release Scenario: https://www.cosmos.esa.int/web/gaia/release
- ESA Cosmos Gaia, DR4 landing page: https://www.cosmos.esa.int/web/gaia/data-release-4
- ESA Cosmos Gaia, DR4 content overview: https://www.cosmos.esa.int/web/gaia/dr4
- ESA Cosmos Gaia, Image of the Week 2025-12-16: https://www.cosmos.esa.int/web/gaia/iow_20251216
- Gaia DR3 `binary_masses` table metadata (Gaia@AIP): https://gaia.aip.de/metadata/gaiadr3/binary_masses/
- Gaia DR3 documentation, FLAME (Final Luminosity Age Mass Estimator): https://gea.esac.esa.int/archive/documentation/GDR3/Data_analysis/chap_cu8par/sec_cu8par_apsis/ssec_cu8par_apsis_flame.html
- Gaia DR3 documentation, `nss_two_body_orbit` data model: https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_non--single_stars_tables/ssec_dm_nss_two_body_orbit.html
- DEBCat detached eclipsing binary catalogue (Southworth): https://www.astro.keele.ac.uk/jkt/debcat/ and https://arxiv.org/abs/1411.1219

## Repository Inputs Reviewed

- `results/EXP-0015/RUN-0001/result.yaml` (`RESULT-0022`)
- `docs/reviews/stellar-ml-result0022-gate-b-replay.md`
- `docs/reviews/stellar-ml-independent-transfer-dataset-scout.md`
- `docs/blind-holdout-benchmark-protocol.md`
- `docs/nuclear-prediction-reveal-protocol.md`
- `tasks/TASK-0825-design-standing-prospective-reveal-pipeline.yaml`
- `tasks/TASK-0834-gaia-dr4-stellar-ml-reveal-contract-scout.yaml`
