# FRB (CHIME) Source-Readiness And Temporal-Split Feasibility Scout

Task: `TASK-0835`
Domain: Radio transients astrophysics (FRB repeater selection-effect audit)
Mode: bounded source-readiness + no-leakage split-feasibility + reveal-channel scout
Verdict: `SOURCE_LIMITED`
Web-verification date: `2026-06-25`

## Scope And Non-Goals

This scout checks whether a future *FRB Repeater Selection-Effect Audit* campaign
has a pinnable, redistribution-clear data product, a version-locked no-leakage
temporal split, a tractable exposure model, and an admissible prospective reveal
channel — **before** any model, benchmark, or campaign scaffold exists.

It does **not**: fetch or commit the CHIME/FRB catalog, compute a SHA-256, fit or
run any model, compute any baseline/metric, freeze any `PRED`, build the
FRB-001..008 pilot, or scaffold the campaign. It produces no claim, no result
artifact, and no dataset rows. It is a readiness gate only.

It honors the no-leakage / no-peek gates in
[../published-source-dataset-standard.md](../published-source-dataset-standard.md),
[../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md),
[../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md),
and the standing-reveal design in
`TASK-0825`.
It does not weaken any of them.

Inputs reviewed (repo):

- [../published-source-dataset-standard.md](../published-source-dataset-standard.md)
- [../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md)
- [../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md)
- `TASK-0825` — standing prospective-reveal pipeline design

External sources web-verified on `2026-06-25` are listed under **Sources**.

## 1. Pinned Data Product

**Pinned primary product: CHIME/FRB Catalog 2 (the Second CHIME/FRB Catalog of
Fast Radio Bursts).** It is publicly released and machine-readable, so it is the
primary candidate over the Catalog 1 fallback.

| Field | Value (web-verified `2026-06-25`) | Status |
| --- | --- | --- |
| Catalog | CHIME/FRB Catalog 2 | published |
| Reference paper | The Second CHIME/FRB Catalog of Fast Radio Bursts, ApJS, arXiv:2601.09399, DOI `10.3847/1538-4365/ae3828` | verified |
| Bursts | 4539 | verified (matches strategy note) |
| Distinct sources | 3641 (3558 non-repeating; 83 repeating) | verified |
| Repeater bursts | 981 from 83 repeaters | verified (matches strategy note) |
| Observing window | 2018-07-25 to 2023-09-15 | verified |
| Data-product DOI (CANFAR/CADC) | `10.11570/25.0066` (catalog table, dynamic spectra, full-sky exposure maps) | verified that the DOI exists and resolves to the dataset; landing page was returning a server error at scout time, see below |
| Portal | `https://www.chime-frb.ca/catalog2` | verified to exist; was HTTP 503 at scout time |
| Formats | CSV / FITS download + journal machine-readable table (MRT) + `cfod` python package | verified (CSV/FITS for Catalog 1 portal/`cfod`; Catalog 2 paper states MRT with the article and via the portal/CANFAR) |

Fallback (NOT selected, but recorded): **CHIME/FRB Catalog 1** (the First
CHIME/FRB Catalog, arXiv:2106.04352, ApJ 2021), ~536 bursts from 2018-07-25 to
2019-07-01, 62 bursts from 18 repeaters, distributed via the CHIME/FRB Open Data
release (`https://chime-frb-open-data.github.io/`, CSV/FITS + `cfod`). Catalog 1
is the better-documented *open-data* product, but it is materially smaller and
its first-detection/repeater statistics are superseded by Catalog 2's uniform
reprocessing, so it is a fallback only.

### Per-source / per-burst field availability (machine-readable)

Confirmed present as machine-readable columns in the Catalog 2 table (field
names quoted from the paper's column descriptions):

- **Dispersion measure:** `dm_fitb`, `dm_fitb_err`, plus Galactic-excess DM
  (`dm_exc_ne2001`, `dm_exc_ymw16`).
- **Flux / fluence:** `flux`, `flux_err`, `fluence`, `fluence_err`.
- **Exposure (per source):** `exp_up`, `exp_low` (upper/lower-transit exposure)
  with errors; the paper computes a localization-weighted exposure by
  integrating the exposure map over the 90% confidence region.
- **Sensitivity / completeness (per source):** fluence thresholds
  `low_ft_68`, `up_ft_68`, `low_ft_95`, `up_ft_95` (68% and 95% completeness
  limits); plus downloadable full-sky exposure maps at DOI `10.11570/25.0066`.
- **Morphology:** `bc_width` (boxcar width), `width_fitb` (fitted intrinsic
  width), `scat_time` (scattering time), `sp_idx` (spectral index),
  `sub_num` (number of sub-bursts/components).
- **First-detection timestamp / arrival time:** `mjd_400`, `mjd_inf` (MJD at
  400 MHz / at infinite frequency). A per-source first-detection time is
  therefore derivable as the minimum arrival MJD over that source's bursts.
- **Repeater flag:** `repeater_name` (non-empty for bursts associated with a
  known repeating source).
- **Dynamic spectra:** total-intensity dynamic spectra released as associated
  products at DOI `10.11570/25.0066`.

All five field families the task asked to confirm — per-source
exposure/sensitivity, morphology, first-detection timestamps, repeater flags,
dynamic spectra — are present and machine-readable. **Field availability is not
the blocker; redistribution license is.**

### Redistribution / reuse policy — the readiness gate

This is where the lane is constrained. Per the repo standard, *published ≠
redistributable*: a source being readable and citable does not make its content
committable to this repo.

Findings (web-verified `2026-06-25`):

- The CHIME/FRB Open Data site states only: *"You may use the data presented in
  this website for publications; however, we ask that you cite the relevant
  CHIME/FRB Collaboration papers."* This is a **cite-the-paper** courtesy
  request, **not** an explicit redistribution grant.
- The CANFAR/CADC dataset DOI `10.11570/25.0066` DataCite record has an **empty
  `rightsList`** — no Creative Commons or other license is attached to the
  dataset metadata (resourceType `Dataset`, publisher CADC, 2025).
- The CHIME/FRB Open Data **GitHub** repository (`chime-frb-open-data`) carries
  an **MIT license — for the SOFTWARE utilities only** (the `cfod` package). It
  does **not** license the underlying catalog DATA. Do not conflate the two.

Conclusion: the catalog is **publicly accessible and citably reusable for
analysis**, but there is **no explicit open-data redistribution license**
(no CC BY / CC0 / public-domain dedication) covering the catalog rows. Under the
repo standard this maps to:

- **Committable now (metadata-only):** the source locator(s) (paper DOI, CANFAR
  DOI, portal URL), the access date, the catalog version, an **expected SHA-256
  to be computed at the first license-cleared fetch**, a fetch/verify command,
  per-source attribution/citation text, and APL's own extraction ledger/schema.
  Individual factual numeric values (a DM, a width, an exposure) are facts and
  are extractable with attribution.
- **NOT cleared to commit:** a vendored copy of the catalog table, the dynamic
  spectra, or the exposure-map files as redistributed repository bytes, because
  no redistribution license is recorded. `blocker_type = T1_access` (the
  needed redistributable copy/version is license-unclear), routing to the
  maintainer acquisition lane to either (a) obtain explicit reuse/redistribution
  permission or a confirmed license, or (b) keep the lane metadata-only with a
  fetch+verify manifest and never vendor rows.

A fetch/verify command **pattern** (illustrative; do NOT run in this scout, and
do NOT fabricate the digest — the expected SHA-256 must be computed at the first
license-cleared fetch and pinned in a source manifest):

```text
# pattern only — license clearance MUST precede any fetch; digest is a placeholder
curl -L -o chimefrb_catalog2.csv "<official catalog2 CSV/MRT URL from chime-frb.ca/catalog2 or CANFAR 10.11570/25.0066>"
python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" chimefrb_catalog2.csv
# expected_sha256: <TO BE PINNED AT FIRST LICENSE-CLEARED FETCH — not fabricated here>
```

## 2. Version-Locked, No-Leakage Temporal Split Feasibility

Question: can a retrospective temporal split (train on the pre-T view; evaluate
which apparent one-offs are later seen to repeat) be constructed without leaking
future information into the pre-T view?

Findings:

- **A per-source first-detection time exists.** It is derivable as the minimum
  arrival MJD (`mjd_400` / `mjd_inf`) over a source's bursts. So a date-based
  cut T is mechanically constructible.
- **Later repeater status is determinable from a strictly later view.** A source
  flagged `repeater_name` only because of bursts that all arrive after T is a
  legitimate "later-revealed repeater" relative to T.
- **Catalog reprocessing drift is real and it leaks.** Catalog 2 **reprocessed
  every Catalog 1 event with a uniform, improved analysis framework**, changing
  DM, morphology measurements, exposure/sensitivity, source associations, and —
  critically — **repeater/non-repeater classification** relative to Catalog 1.
  That means a "pre-T" feature vector read from the *Catalog 2* table is **not**
  what was knowable at time T: it embeds post-T reprocessing, post-T exposure
  accumulation, and post-T association decisions. Reading pre-T features from a
  single late catalog version is a leakage path.

**Verdict on the split: date-locking ALONE is NOT sufficient; VERSION-locking is
required.** A defensible split must:

1. fix a catalog **version** as the "knowledge state" for the pre-T view (e.g.
   Catalog 1 vintage, or a Catalog 2 sub-product explicitly reconstructed to the
   information available at T), separate from the later **version** used to read
   the repeat/no-repeat outcome label;
2. ensure exposure and sensitivity in the pre-T view are truncated at T (only
   exposure accumulated up to T), not the full-window `exp_up`/`exp_low`;
3. treat source-association and repeater-classification changes between versions
   as outcomes, never as pre-T inputs.

Because the two CHIME catalog versions use **different analysis frameworks**, a
naive "Catalog 1 as pre-T, Catalog 2 as post-T" split also risks a
**framework-shift confound** (changes that are reprocessing artifacts, not
physics). The split is *feasible in principle* but only as an explicitly
version-locked artifact with truncated-exposure pre-T features; it is **not**
feasible as a one-table date filter. This is a design constraint to carry into
the pilot, not a blocker by itself.

## 3. Exposure-Model Tractability — The Whole Ballgame

The campaign's central confounder: a source can look non-repeating only because
CHIME has not pointed at it long/deep enough. If the exposure model is wrong,
"morphology predicts repetition" can collapse to **sky-coverage / declination
bias** dressed up as physics.

Findings:

- Catalog 2 **does** release the raw materials for an exposure model:
  per-source upper/lower-transit exposure (`exp_up`, `exp_low`), 68%/95%
  completeness fluence thresholds, and downloadable full-sky exposure maps. CHIME
  is a transit instrument with a daily cadence and a declination-dependent
  exposure pattern, so exposure is strongly position-dependent and **must** be
  modeled per source, not assumed uniform.
- This is enough to make an **exposure-only baseline** the PRIMARY control:
  a model that predicts "later repeats" from exposure/sensitivity alone (plus
  trivially-available position/DM), with **no morphology**. Any morphology model
  must beat that exposure-only baseline **out-of-sample**, on the version-locked
  split, before "morphology forecasts repetition" can be entertained.

**Framing (carry into the pilot):** the exposure model is a **first-class,
separately-validated, FROZEN artifact** — built and validated on its own, frozen,
and only then used as the control. It is not a nuisance term tucked inside the
morphology model. If exposure is mis-specified, the audit's headline collapses to
sky-coverage bias, so the exposure model gets its own validation, its own
limitations section, and its own freeze before any morphology comparison runs.

**Caveats that keep this SOURCE_LIMITED rather than READY here too:** the
released exposure is per-source summary exposure; reconstructing exposure
*truncated at an arbitrary split time T* (needed for the no-leakage pre-T view in
§2) requires the time-resolved exposure maps, and whether the public products
support T-truncated exposure at single-source granularity is **not yet
confirmed** without fetching and inspecting the exposure-map files (out of scope
for this scout). Tractability is **promising but unproven** until the
exposure-map granularity and the catalog license are both resolved.

## 4. Reveal Channel For The Prospective Lane

Question: how and on what cadence does CHIME publish new repeater detections /
catalog updates, and is that an admissible external, immutable, post-freeze
reveal source under the reveal / blind-holdout protocols?

Findings (web-verified `2026-06-25`):

- **Periodic repeater-discovery papers** are the cleanest reveal product. CHIME
  published 25 new repeaters in 2023 (arXiv:2301.08762) and **30 new repeaters /
  80 total** in a 2026 paper ("Discovery of 30 Repeating Fast Radio Burst Sources
  and Uniform Population Statistics of 80 Repeating Sources from CHIME/FRB",
  arXiv:2605.08410, **submitted 2026-05-08**), drawn from the same Catalog 2
  burst window. These are dated, versioned, externally hosted, and immutable
  once posted.
- **Astronomer's Telegrams (ATels) and TNS** announce individual new repeaters
  in near-real time (e.g. FRB 20240209A, FRB 20240114A in 2024), each with a
  fixed publication timestamp and IVORN/ATel number.
- CHIME's own VOEvent service documentation asks users to cite VOEvents by IVORN
  with *"This research has made use of the CHIME/FRB VOEvent Service."*

**Admissibility:** YES as an external, immutable, post-freeze reveal source —
**with one structural caveat.** The reveal/blind-holdout protocols assume a clean
before/after boundary frozen before any target is inspected. ATels and rolling
detections are a *continuous stream*, not a single sealed release, so the
prospective lane must:

1. freeze the pre-reveal package (model, exposure-only baseline, threshold,
   target source list) at a **fixed UTC cutoff** and record it per
   [../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md);
2. treat only repeater confirmations with a **publication timestamp strictly
   after** that cutoff (next discovery paper, or post-cutoff ATels/TNS) as the
   reveal, mirroring the `SOURCE_PREDATES_REGISTRATION` no-peek logic in
   [../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md);
3. pin each revealed confirmation by its immutable reference (ATel number /
   arXiv id / TNS entry) in a reveal record.

This matches the standing prospective-reveal design intent in
`TASK-0825`.
The channel is admissible; it just needs an explicit fixed-cutoff freeze rather
than treating "any future ATel" as a sealed holdout.

## 5. Honest Campaign Reframe And Novelty Position

**Primary contribution = an exposure-controlled SELECTION-EFFECT AUDIT, with
both outcomes valuable:**

- if morphology survives **exposure-matched out-of-sample** controls and beats
  the frozen exposure-only baseline ⇒ first-burst morphology carries genuine
  forecasting information about which apparent one-offs later repeat;
- if it does **not** ⇒ that is strong evidence the apparent repeater /
  non-repeater two-population split is partly an **observational selection
  effect** (sky coverage / exposure), not source physics.

The **forecast** (naming specific apparent one-offs likely to repeat, scored
against later CHIME reveals) is the **prospective-reveal overlay** on top of the
audit, not the headline.

**Novelty position (honest):** the field is crowded. FRB repeater/non-repeater
classification, morphology studies, and **semi-supervised hidden-repeater
searches** are active (e.g. machine-learning reclassification of CHIME bursts;
the CHIME 25- and 30-repeater clustering searches themselves). APL must **not**
claim novelty as "classifying FRBs" or "predicting repeaters" per se. The honest
differentiator is **methodological**: a pre-registered, exposure-controlled,
version-locked, **out-of-sample** audit with a **frozen exposure-only baseline as
the gate** and a **frozen prospective-reveal overlay** with public failure
memory — the discipline professional FRB forecasting papers rarely combine.

During this initial scouting I did **not** identify a directly comparable,
pre-registered, exposure-controlled, externally-revealed FRB repeater audit with
public failure memory. (Absence of a hit in a bounded scout is **not** proof of
absence; a proper prior-art review against the FRB classification / selection
literature must be part of pilot scoping before any novelty wording is used.)

## 6. Named Confounders To Control Later

Carry-forward list for the pilot (not addressed here, by design):

- **selection bias** (declination-dependent exposure / sky-coverage masquerading
  as a morphology signal — the headline confounder);
- **incomplete or mis-specified exposure model** (especially T-truncated,
  per-source exposure needed for the no-leakage pre-T view);
- **catalog reprocessing drift** (DM / morphology / exposure / classification
  changing between Catalog 1 and Catalog 2 frameworks — the version-lock leakage
  path);
- **source-association errors** (bursts wrongly grouped/split into sources,
  which directly corrupt repeat/no-repeat labels);
- **follow-up / monitoring bias** (some sources receive extra targeted exposure
  after an interesting first burst, coupling morphology to later exposure);
- **framework-shift confound** (Catalog 1 vs Catalog 2 measurement changes that
  are pipeline artifacts, not physics);
- **data / license semantics** (redistribution rights, attribution, and the
  exact meaning of released exposure/sensitivity fields).

## 7. Verdict

**`SOURCE_LIMITED`.**

One-paragraph reasoning: CHIME/FRB Catalog 2 is genuinely strong on *data
substance* — it is public, machine-readable, and ships exactly the per-source
exposure, sensitivity/completeness, morphology, first-detection timestamps,
repeater flags, and dynamic spectra the campaign needs, with full-sky exposure
maps. Two readiness gates are nonetheless unmet. (a) **Redistribution license is
unconfirmed:** there is no explicit open-data license on the catalog rows
(CANFAR DataCite `rightsList` empty; open-data site only requests citation; the
MIT license covers the `cfod` software, not the data), so APL is cleared for a
metadata-only locator + expected-SHA-256 + fetch/verify manifest but **not** to
vendor catalog rows — pending maintainer license clearance (`T1_access`).
(b) **No-leakage feasibility needs version-locking and T-truncated exposure**
that the public summary products are not yet confirmed to support without
fetching and inspecting the exposure maps. Field availability is excellent;
redistribution clearance and version-locked exposure reconstruction are the
limiters. That is `SOURCE_LIMITED`, not `READY`. No bounded `FRB-00x` pilot shape
is emitted, because the task reserves that for a `READY` verdict.

### What would move this to READY

1. Maintainer-confirmed redistribution/reuse clearance for the catalog rows (an
   explicit license, recorded permission, or a decision to stay metadata-only
   with a fetch+verify manifest and never vendor rows); **and**
2. confirmation — by inspecting the released exposure-map / time-resolved
   products under that clearance — that per-source exposure can be reconstructed
   **truncated at an arbitrary split time T** to build the no-leakage pre-T view;
   **and**
3. a version-locked split design that uses one catalog version (or a
   reconstructed-to-T view) for pre-T features and a strictly later version for
   the repeat/no-repeat label, with the exposure-only baseline frozen first.

## Output-Routing Summary

- **Task verdict:** `SOURCE_LIMITED` (readiness/feasibility scout; not
  `VALID`/`FALSIFIED` — no benchmark was run).
- **Canonical destination:** this review note, acting as the **source-readiness
  + reveal-contract gate** for a future *FRB Repeater Selection-Effect Audit*
  campaign. No campaign scaffold, pilot, or task scaffolding is created here.
- **Review tier:** `none`. **Gate A:** not attempted. **Gate B:** not attempted
  (no dataset, metric, prediction, or result produced).
- **Model / benchmark / PRED / claim / result impact:** none. No model fitted,
  no baseline/metric computed, no `PRED` frozen, no claim or knowledge change, no
  `results/` artifact. No catalog bytes fetched or committed.
- **Data redistribution boundary:** catalog rows are **not** cleared for
  repository commit (no explicit license; `T1_access`); only locator + access
  date + version + expected-SHA-256 (computed at first license-cleared fetch) +
  fetch/verify command + attribution are committable. The MIT `cfod` software
  license does not license the data.
- **No-leakage boundary:** date-locking alone is insufficient; a version-locked
  split with T-truncated per-source exposure is required, and reprocessing drift
  / classification changes between catalog versions must be treated as outcomes,
  never as pre-T inputs.
- **Reveal-channel boundary:** CHIME periodic repeater-discovery papers + ATels
  + TNS are an admissible external, immutable, post-freeze reveal source **only**
  behind a fixed-UTC pre-reveal freeze; rolling detections are not a sealed
  holdout by themselves.
- **Limitations / blockers:** (1) catalog license/redistribution unconfirmed
  (primary blocker); (2) T-truncated per-source exposure reconstruction unproven
  without inspecting exposure-map files (out of scope here); (3) CANFAR landing
  page and `chime-frb.ca/catalog2` portal returned transient server errors (503 /
  444) at scout time, so portal-level data-policy text could not be read directly
  and the redistribution finding rests on the open-data site, DataCite, and the
  GitHub license; (4) prior-art / novelty review against the FRB classification
  and selection literature is deferred to pilot scoping; (5) no SHA-256, license
  text, field availability, or burst count was fabricated — counts and fields are
  web-verified against the Catalog 2 paper, and the expected SHA-256 is
  explicitly deferred to first license-cleared fetch.

## Sources

External pages consulted on `2026-06-25`:

- The Second CHIME/FRB Catalog of Fast Radio Bursts (arXiv HTML): `https://arxiv.org/html/2601.09399v1`
- The Second CHIME/FRB Catalog of Fast Radio Bursts (arXiv abstract): `https://arxiv.org/abs/2601.09399`
- The Second CHIME/FRB Catalog of Fast Radio Bursts (IOPscience, ApJS): `https://iopscience.iop.org/article/10.3847/1538-4365/ae3828`
- CHIME/FRB Catalog 2 portal: `https://www.chime-frb.ca/catalog2` (HTTP 503 at scout time)
- CANFAR/CADC dataset DOI landing: `https://www.canfar.net/citation/landing?doi=25.0066` (server error at scout time)
- DataCite record for DOI 10.11570/25.0066: `https://api.datacite.org/dois/10.11570/25.0066` (empty `rightsList`)
- CHIME/FRB Open Data: `https://chime-frb-open-data.github.io/`
- CHIME/FRB Open Data software repository (MIT license, software only): `https://github.com/chime-frb-open-data/chime-frb-open-data`
- CHIME/FRB Public Database: `https://www.chime-frb.ca/`
- The First CHIME/FRB Catalog (fallback product): `https://arxiv.org/pdf/2106.04352`
- CHIME/FRB Discovery of 25 Repeating Fast Radio Burst Sources (arXiv): `https://arxiv.org/abs/2301.08762`
- Discovery of 30 Repeating FRB Sources / 80 total (arXiv, submitted 2026-05-08): `https://arxiv.org/abs/2605.08410`
- CHIME/FRB ATel example (FRB 20240209A): `https://ui.adsabs.harvard.edu/abs/2024ATel16670....1S/abstract`
- The CHIME/FRB Discovery of FRB 20240114A: `https://arxiv.org/abs/2505.13297`
