# FRB (CHIME) Catalog 2 Access Re-Verification And Readiness Completion

Task: `TASK-0839`
Domain: Radio transients astrophysics (FRB repeater selection-effect audit)
Mode: bounded access re-verification + no-leakage split / exposure-model / reveal-channel readiness completion
Verdict: `SOURCE_LIMITED`
Web-verification date: `2026-06-26`

## Scope And Non-Goals

The FRB source-readiness scout (`TASK-0835`,
[frb-chime-source-readiness-temporal-split-scout.md](frb-chime-source-readiness-temporal-split-scout.md))
returned `SOURCE_LIMITED`: it pinned CHIME/FRB Catalog 2 with a verified
data-product DOI (CANFAR/CADC `10.11570/25.0066`: catalog table, dynamic spectra,
full-sky exposure maps) but the CANFAR landing page returned a server error at
scout time, so access, redistribution clearance, field machine-readability, the
version-locked no-leakage split, and exposure-model tractability could not all be
confirmed.

This task **re-verifies** whether the pinned product now resolves and is
retrievable, re-checks license/reuse/redistribution terms, and **completes** the
readiness finding with one verdict. It is a readiness gate only.

It does **not**: fetch or commit the CHIME/FRB catalog bytes, compute a SHA-256,
fit or run any model, compute any baseline/metric, freeze any `PRED`, build the
FRB-001..00x pilot, scaffold the campaign, or activate the full FRB campaign. It
produces no claim, no result artifact, and no dataset rows. It creates no
`agent_runs/` or `results/` RUN artifact.

It honors the no-leakage / no-peek gates in
[../published-source-dataset-standard.md](../published-source-dataset-standard.md),
[../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md),
[../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md),
and the standing-reveal design in `TASK-0825`. It does not weaken any of them.

Inputs reviewed (repo):

- [frb-chime-source-readiness-temporal-split-scout.md](frb-chime-source-readiness-temporal-split-scout.md)
  (the prior `TASK-0835` scout this task completes)
- [../published-source-dataset-standard.md](../published-source-dataset-standard.md)
- [../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md)
- [../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md)

External pages web-verified on `2026-06-26` are listed under **Sources**.

## 1. Access Re-Verification — The Blocking Question

**Verdict on access: the DOI resolves at the registry layer, but the data
landing/retrieval page does NOT resolve cleanly. Retrievability of the actual
data products cannot be confirmed from public pages on `2026-06-26`.**

This is the specific block `TASK-0835` left open, and it is **not** cleared.

| Probe (web-verified `2026-06-26`) | Result | Reading |
| --- | --- | --- |
| `https://doi.org/10.11570/25.0066` (HTTP) | `302` redirect to `https://www.canfar.net/citation/landing?doi=25.0066` | DOI registration is live and points at the CANFAR citation landing page. |
| DataCite record `https://api.datacite.org/dois/10.11570/25.0066` | `state = findable`; title "The Second CHIME/FRB Catalog of Fast Radio Bursts"; publisher `CADC`; `publicationYear 2025`; `resourceType Dataset` | Metadata record exists and is correct. |
| CANFAR landing `https://www.canfar.net/citation/landing?doi=25.0066` (no redirect follow) | `404 Not Found` | The landing page the DOI points to is missing. |
| CANFAR landing (redirects followed) | `500 Internal Server Error` | The citation-landing service is erroring, not serving the dataset page. |
| `https://www.canfar.net/citation/` (service root) | `404` | The CANFAR citation-landing service path itself is not serving. |
| `https://www.canfar.net/` (host root) | `200` | The CANFAR host is up; the failure is specific to the citation-landing service, not the whole site. |
| CADC alternate host `https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/` | `200` | CADC host is up. |
| CADC `…/citation/landing?doi=25.0066` (alternate host) | `404` | The citation-landing path is also missing on the CADC host. |
| Portal `https://www.chime-frb.ca/catalog2` | `503 Service Unavailable` | The Catalog 2 portal is down. |
| Portal host `https://www.chime-frb.ca/` (root) | `503` | The **entire** CHIME/FRB public web host is down at re-verify time, not just `/catalog2`. |

**Net access finding.** The DataCite/DOI registration layer is healthy
(`findable`, correct metadata, correct redirect target), but **both** public
retrieval surfaces are unavailable:

- the **CANFAR/CADC citation-landing page** the DOI resolves to returns
  `404`/`500` on both the `canfar.net` and the CADC host, and the
  `…/citation/` service root itself is `404`; and
- the **CHIME/FRB Catalog 2 portal** (and its parent host `chime-frb.ca`) is
  fully `503`.

Because neither public surface served the dataset page, the "actually RESOLVES
and is retrievable" requirement is **not satisfied**: I could not reach a page
listing or linking the catalog table, the dynamic spectra, or the exposure-map
files, and therefore could not confirm a license-clear retrieval route from
public pages. Two independent failure surfaces (citation-landing service and the
CHIME portal) reduce the chance this is a single momentary blip, but a transient
multi-service outage cannot be ruled out and is itself the limitation: the
linchpin retrieval path is not demonstrably available right now.

This is honestly `SOURCE_LIMITED`, not `READY`. Per the task's own honesty
clause, if Catalog 2 access (or redistribution) cannot be confirmed from public
pages, the verdict is `SOURCE_LIMITED`.

### License / reuse / redistribution terms (3-question source-rights framework)

License terms were re-checked from the surfaces that **did** resolve (DataCite,
the open-data site, the GitHub software repo). The finding is unchanged from
`TASK-0835` and remains the second, independent limiter:

- **DataCite `rightsList` is empty** — `"rightsList": []`. No Creative Commons,
  CC0, public-domain, or other license is attached to the dataset metadata
  (re-verified `2026-06-26`).
- The **CHIME/FRB Open Data** site states only: *"You may use the data presented
  in this website for publications; however, we ask that you cite the relevant
  CHIME/FRB Collaboration papers."* This is a **cite-the-paper courtesy request**,
  not an explicit redistribution grant, and the page does not mention Catalog 2.
- The **CHIME/FRB Open Data GitHub** repository carries an **MIT license** whose
  header reads `Copyright (c) 2019 CHIME FRB Open Data` — it licenses the
  `cfod` **software utilities only**, not the underlying catalog **data**. Do not
  conflate the two.
- The **Catalog 2 paper** (arXiv `2601.09399`) data-availability statement
  archives the products at CANFAR `10.11570/25.0066` but states **no** data-reuse
  or redistribution license.

Applying the repo's 3-question source-rights framework
([../published-source-dataset-standard.md](../published-source-dataset-standard.md)):

| Question | Determination (`2026-06-26`) |
| --- | --- |
| **Local analysis** allowed? | **Yes** by default — the data is publicly released for analysis and the open-data site explicitly permits use for publications (cite the papers). Allowed once a license-clear copy is in hand. |
| **Source-bytes redistribution** allowed? | **No** (default). No redistribution license is recorded anywhere (empty `rightsList`; cite-the-paper courtesy only; MIT covers software, not data). Do **not** vendor the catalog table, dynamic spectra, or exposure-map files. |
| **Derived-rows publication**? | **`unknown`** — source-specific and unconfirmed. With no explicit open license on the rows, APL may treat individual factual numeric values (a DM, a width, an exposure) as extractable facts with attribution, but a redistributable derived-row dataset is **not** cleared without maintainer license clearance or recorded permission. This is `limited_factual_extract` at best, `unknown` for bulk derived publication. |

Repo standard mapping: `blocker_type = T1_access` — the source is identified, but
the needed retrievable/redistributable copy is **both** access-unavailable (the
landing page does not serve) **and** license-unclear (empty `rightsList`).
Routing: maintainer acquisition lane, to either (a) obtain a confirmed
license / recorded reuse permission, or (b) keep the lane metadata-only with a
fetch+verify manifest that **never** vendors rows.

### Default handling (locator + SHA-256 + fetch/verify, not vendoring)

Committable now (metadata-only): source locator(s) (paper DOI
`10.3847/1538-4365/ae3828`, arXiv `2601.09399`, CANFAR DOI `10.11570/25.0066`,
portal URL), the access date, the catalog version (Catalog 2), an **expected
SHA-256 to be computed at the first license-cleared fetch**, a fetch/verify
command, per-source attribution/citation text, and APL's own extraction
ledger/schema. **No SHA-256 is fabricated here** — it must be computed at the
first license-cleared, access-restored fetch and pinned in a source manifest.

Not cleared to commit: a vendored copy of the catalog table, the dynamic spectra,
or the exposure-map files as redistributed repository bytes.

Fetch/verify command **pattern** (illustrative; do NOT run in this scout; both
**access restoration and license clearance must precede any fetch**; the digest
is a placeholder):

```text
# pattern only — landing-page access AND license clearance MUST precede any fetch;
# digest is a placeholder, computed at first license-cleared fetch, never fabricated
curl -L -o chimefrb_catalog2.csv "<official Catalog 2 CSV/MRT URL once the CANFAR landing or chime-frb.ca/catalog2 portal is restored>"
python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" chimefrb_catalog2.csv
# expected_sha256: <TO BE PINNED AT FIRST LICENSE-CLEARED FETCH — not fabricated here>
```

## 2. Field Availability (Machine-Readable) — Confirmed

Field machine-readability is **not** the blocker and is re-confirmed. The Catalog
2 machine-readable table (verified from the paper's column descriptions,
arXiv `2601.09399`, `2026-06-26`) contains all field families the task asked to
confirm:

- **Per-source exposure / sensitivity:** `exp_up`, `exp_up_err`, `exp_low`,
  `exp_low_err` (upper/lower-transit exposure), plus 68% and 95% completeness
  fluence thresholds `low_ft_68`, `up_ft_68`, `low_ft_95`, `up_ft_95`; and
  downloadable full-sky exposure maps + localization contours as associated
  products at DOI `10.11570/25.0066`.
- **Morphology:** `bc_width` (boxcar width), `width_fitb`/`width_fitb_err`
  (fitted intrinsic width), `scat_time`/`scat_time_err` (scattering time),
  `sp_idx`/`sp_run` (spectral index / running, the bandwidth proxy),
  `dm_fitb`/`dm_fitb_err` and `bonsai_dm` (dispersion measure),
  `flux`/`fluence` with errors.
- **First-detection timestamps:** `mjd_400`/`mjd_400_err`, `mjd_inf`/`mjd_inf_err`
  (arrival MJD at 400 MHz / at infinite frequency). A per-source first-detection
  time is derivable as the minimum arrival MJD over that source's bursts.
- **Repeater flags:** `repeater_name` (non-empty for bursts associated with a
  known repeating source).
- **Dynamic spectra:** total-intensity dynamic spectra released as associated
  products at DOI `10.11570/25.0066`.

Catalog statistics re-confirmed against the paper: **4539 bursts**, **3641
distinct sources** (83 repeating), **981 repeater bursts from 83 repeaters**,
observing window **2018-07-25 to 2023-09-15**.

**Fallback (recorded, NOT promoted to primary):** CHIME/FRB Catalog 1 (the First
CHIME/FRB Catalog, arXiv `2106.04352`), distributed via the CHIME/FRB Open Data
release (`https://chime-frb-open-data.github.io/`, GitHub Pages re-verified `200`
on `2026-06-26`), CSV/FITS + `cfod`. Catalog 1 remains the better-documented
*open-data* product and is the fallback **only if Catalog 2 remains
inaccessible**; it is materially smaller and its first-detection/repeater
statistics are superseded by Catalog 2's uniform reprocessing. Note that the
field availability above is moot for an APL benchmark until a license-clear,
retrievable copy of **either** catalog is in hand — field readability does not
move the access/redistribution gate.

## 3. Version-Locked, No-Leakage Temporal Split — Feasible Only As A Version-Locked Artifact

Question: can a retrospective temporal split (train on the pre-T view; evaluate
which apparent one-offs are later seen to repeat) be built without leaking future
information into the pre-T view? This is assessed from the catalog structure (the
paper), independent of the current access outage.

- **A per-source first-detection time exists** (minimum arrival MJD `mjd_400` /
  `mjd_inf` over a source's bursts), so a date cut T is mechanically
  constructible.
- **Later repeater status is determinable from a strictly later view:** a source
  flagged `repeater_name` only by bursts arriving after T is a legitimate
  later-revealed repeater relative to T.
- **Catalog reprocessing drift is real and it leaks.** Catalog 2 reprocesses
  Catalog 1 events with a uniform, improved framework, changing DM, morphology,
  exposure/sensitivity, source associations, and repeater/non-repeater
  classification relative to Catalog 1. A "pre-T" feature vector read from the
  *Catalog 2* table embeds post-T reprocessing, post-T exposure accumulation, and
  post-T association decisions — reading pre-T features from a single late catalog
  version is a leakage path.

**Verdict on the split: date-locking ALONE is insufficient; VERSION-locking is
required.** A defensible split must (1) fix a catalog **version** as the pre-T
knowledge state (Catalog 1 vintage, or a Catalog 2 sub-product reconstructed to
the information available at T), separate from the later **version** used to read
the repeat/no-repeat outcome label; (2) truncate exposure and sensitivity in the
pre-T view at T (only exposure accumulated up to T, not full-window
`exp_up`/`exp_low`); and (3) treat source-association and repeater-classification
changes between versions as **outcomes**, never as pre-T inputs. A naive
"Catalog 1 as pre-T, Catalog 2 as post-T" split also risks a **framework-shift
confound** (changes that are pipeline artifacts, not physics). The split is
*feasible in principle* but only as an explicitly version-locked artifact with
truncated-exposure pre-T features — **not** as a one-table date filter. This is a
design constraint to carry into a future pilot, not a fresh blocker by itself.

## 4. Exposure-Model Tractability — Promising But Unproven Until Access Is Restored

The campaign's central confounder: a source can look non-repeating only because
CHIME has not pointed at it long/deep enough. If the exposure model is wrong,
"morphology predicts repetition" can collapse to **sky-coverage / declination
bias** dressed up as physics.

- Catalog 2 **does** publish the raw materials for an exposure model: per-source
  upper/lower-transit exposure (`exp_up`, `exp_low`), 68%/95% completeness
  fluence thresholds, full-sky exposure maps, and localization contours. CHIME is
  a transit instrument with a daily cadence and a declination-dependent exposure
  pattern, so exposure is strongly position-dependent and must be modeled
  **per source**, not assumed uniform.
- This supports an **exposure-only baseline** as the PRIMARY control: predict
  "later repeats" from exposure/sensitivity alone (plus trivially-available
  position/DM), with **no morphology**. Any morphology model must beat that
  exposure-only baseline **out-of-sample**, on the version-locked split, before
  "morphology forecasts repetition" can be entertained. The exposure model is a
  **first-class, separately-validated, FROZEN artifact** with its own validation
  and limitations — not a nuisance term inside the morphology model.

**Why this stays `SOURCE_LIMITED` here too:** the released exposure is per-source
**summary** exposure. Reconstructing exposure **truncated at an arbitrary split
time T** (needed for the no-leakage pre-T view in §3) requires the time-resolved
exposure maps, and whether the public products support T-truncated exposure at
single-source granularity is **still unconfirmed** — it requires fetching and
inspecting the exposure-map files, which is (a) out of scope for this scout and
(b) currently impossible because the CANFAR landing page and the portal do not
serve. Tractability is **promising but unproven** until exposure-map granularity
**and** the catalog access/license are resolved.

## 5. Reveal Channel — Admissible Behind A Fixed-UTC Freeze

Question: how does CHIME publish new repeater detections / catalog updates, on
what cadence, and is that an admissible external, immutable, post-freeze reveal
source under the reveal / blind-holdout protocols? (Assessed from the literature;
the reveal papers below resolve independently of the data-portal outage.)

- **Periodic repeater-discovery papers** are the cleanest reveal product. CHIME
  published 25 new repeaters in 2023 (arXiv `2301.08762`) and **30 new repeaters
  / 80 total** in a 2026 paper (arXiv `2605.08410`, submitted 2026-05-08), drawn
  from the same Catalog 2 burst window. These are dated, versioned, externally
  hosted, and immutable once posted. The arXiv abstract pages for `2601.09399`
  and `2605.08410` and the ApJS article (`10.3847/1538-4365/ae3828`) were
  re-verified reachable (`200`) on `2026-06-26`.
- **Astronomer's Telegrams (ATels) and TNS** announce individual new repeaters in
  near-real time, each with a fixed publication timestamp and IVORN/ATel number.

**Admissibility: YES** as an external, immutable, post-freeze reveal source —
with one structural caveat. The reveal/blind-holdout protocols assume a clean
before/after boundary frozen before any target is inspected; ATels and rolling
detections are a **continuous stream**, not a single sealed release. So a future
prospective lane must (1) freeze the pre-reveal package (model, exposure-only
baseline, threshold, target source list) at a **fixed UTC cutoff** and record it
per [../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md);
(2) treat only repeater confirmations with a **publication timestamp strictly
after** that cutoff as the reveal, mirroring the `SOURCE_PREDATES_REGISTRATION`
no-peek logic in
[../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md);
and (3) pin each revealed confirmation by its immutable reference (ATel number /
arXiv id / TNS entry). This matches the standing prospective-reveal design intent
in `TASK-0825`. The channel is admissible; it just needs an explicit fixed-cutoff
freeze rather than treating "any future ATel" as a sealed holdout.

## 6. Verdict

**`SOURCE_LIMITED`.**

One-line summaries:

- **Access result:** DOI `10.11570/25.0066` resolves at the DataCite/registry
  layer (`findable`, correct metadata, `302` → CANFAR landing), but the CANFAR
  citation-landing page returns `404`/`500` (and the `…/citation/` service root
  is `404` on both `canfar.net` and the CADC host) **and** the
  `chime-frb.ca/catalog2` portal — indeed the whole `chime-frb.ca` host — returns
  `503`, so the data products are **not confirmed retrievable** from public pages
  on `2026-06-26`.
- **Field availability:** all required fields (per-source exposure/sensitivity,
  morphology, first-detection timestamps, repeater flags, dynamic spectra) are
  machine-readable and confirmed present in the Catalog 2 table; field
  availability is **not** the limiter.
- **Version-lock / no-leakage feasibility:** feasible **only** as an explicitly
  version-locked artifact (one version for pre-T features, a strictly later
  version for the outcome label) with **T-truncated** per-source exposure;
  date-locking alone leaks via reprocessing drift.
- **Exposure-model finding:** an exposure-only frozen baseline is the right
  primary control and the raw materials exist, but **T-truncated per-source
  exposure** reconstruction is unproven and currently unverifiable while access
  is down — promising but unproven.
- **Reveal-channel finding:** CHIME periodic repeater-discovery papers + ATels +
  TNS are an admissible external, immutable, post-freeze reveal source **only**
  behind a fixed-UTC pre-reveal freeze; rolling detections are not a sealed
  holdout by themselves.

No bounded `FRB-00x` pilot shape is emitted, because the task reserves that for a
`READY` verdict and access/redistribution are not cleared.

### What would move this to READY

1. **Access restored and confirmed:** the CANFAR/CADC landing page for
   `10.11570/25.0066` (or the `chime-frb.ca/catalog2` portal) actually serves the
   dataset and links a retrievable catalog table / dynamic spectra / exposure
   maps; **and**
2. **Redistribution/reuse clearance:** a maintainer-confirmed explicit license,
   recorded reuse permission, or an explicit decision to stay metadata-only with
   a fetch+verify manifest that never vendors rows (resolving the empty
   `rightsList`); **and**
3. **T-truncated exposure confirmed:** by inspecting the released exposure-map /
   time-resolved products under that clearance, confirmation that per-source
   exposure can be reconstructed **truncated at an arbitrary split time T** for
   the no-leakage pre-T view; **and**
4. **A version-locked split design** that uses one catalog version (or a
   reconstructed-to-T view) for pre-T features and a strictly later version for
   the repeat/no-repeat label, with the exposure-only baseline frozen first.

## Output-Routing Summary

- **Destination:** this review note, acting as the **FRB source-readiness +
  reveal-contract gate** for a future *FRB Repeater Selection-Effect Audit*
  campaign. No campaign scaffold, pilot, or task scaffolding is created here.
- **Task verdict:** `SOURCE_LIMITED` (access re-verification + readiness scout;
  not `VALID`/`FALSIFIED` — no benchmark was run).
- **Model / benchmark / PRED / claim / result impact:** none. No model fitted, no
  baseline/metric computed, no `PRED` frozen, no claim or knowledge change, no
  `results/` or `agent_runs/` artifact. No catalog bytes fetched or committed.
- **Review tier:** `none`. **Gate A:** not attempted. **Gate B:** not attempted
  (no dataset, metric, prediction, or result produced).
- **Data redistribution boundary:** catalog rows are **not** cleared for
  repository commit (no explicit license — empty DataCite `rightsList`;
  cite-the-paper courtesy only; the MIT `cfod` license covers software, not
  data; `blocker_type = T1_access`). Only locator + access date + version +
  expected-SHA-256 (computed at first license-cleared fetch, **not** fabricated
  here) + fetch/verify command + attribution are committable. Bulk derived-row
  publication is `unknown`; individual factual values are
  `limited_factual_extract` with attribution.
- **No-leakage boundary:** date-locking alone is insufficient; a version-locked
  split with T-truncated per-source exposure is required, and reprocessing drift /
  classification changes between catalog versions must be treated as outcomes,
  never as pre-T inputs.
- **Reveal-channel boundary:** CHIME periodic repeater-discovery papers + ATels +
  TNS are an admissible external, immutable, post-freeze reveal source **only**
  behind a fixed-UTC pre-reveal freeze; rolling detections are not a sealed
  holdout by themselves.
- **Limitations / blockers:** (1) **primary** — the CANFAR/CADC citation-landing
  page (`404`/`500`) and the `chime-frb.ca` portal/host (`503`) did not serve on
  `2026-06-26`, so retrievability of the data products could not be confirmed from
  public pages; a transient multi-service outage cannot be excluded, and that
  uncertainty is itself the block; (2) catalog redistribution license unconfirmed
  (empty `rightsList`; `T1_access`); (3) T-truncated per-source exposure
  reconstruction unproven and currently unverifiable while access is down;
  (4) prior-art / novelty review against the FRB classification and selection
  literature is deferred to pilot scoping; (5) **no SHA-256, license text, field
  list, or burst count was fabricated** — counts and fields are web-verified
  against the Catalog 2 paper, the empty `rightsList` is read from the live
  DataCite record, and the expected SHA-256 is explicitly deferred to the first
  license-cleared, access-restored fetch.

## Sources

External pages consulted on `2026-06-26`:

- DataCite record for DOI 10.11570/25.0066 (`state: findable`, empty `rightsList`): `https://api.datacite.org/dois/10.11570/25.0066`
- CANFAR/CADC dataset DOI resolution: `https://doi.org/10.11570/25.0066` (302 to the CANFAR citation landing)
- CANFAR citation landing page: `https://www.canfar.net/citation/landing?doi=25.0066` (404 / 500 at re-verify time)
- CANFAR citation service root: `https://www.canfar.net/citation/` (404 at re-verify time)
- CANFAR host root: `https://www.canfar.net/` (200)
- CADC host root: `https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/` (200; `/citation/landing` path 404)
- CHIME/FRB Catalog 2 portal: `https://www.chime-frb.ca/catalog2` (503 at re-verify time)
- CHIME/FRB public host root: `https://www.chime-frb.ca/` (503 at re-verify time)
- The Second CHIME/FRB Catalog of Fast Radio Bursts (arXiv HTML, column descriptions + data-availability statement): `https://arxiv.org/html/2601.09399v1`
- The Second CHIME/FRB Catalog of Fast Radio Bursts (arXiv abstract): `https://arxiv.org/abs/2601.09399`
- The Second CHIME/FRB Catalog of Fast Radio Bursts (IOPscience, ApJS, DOI 10.3847/1538-4365/ae3828): `https://iopscience.iop.org/article/10.3847/1538-4365/ae3828`
- CHIME/FRB Open Data (cite-the-paper courtesy text; no Catalog 2 mention): `https://chime-frb-open-data.github.io/`
- CHIME/FRB Open Data software repository LICENSE (MIT, `Copyright (c) 2019 CHIME FRB Open Data`; software only): `https://raw.githubusercontent.com/chime-frb-open-data/chime-frb-open-data/master/LICENSE`
- The First CHIME/FRB Catalog (fallback product): `https://arxiv.org/abs/2106.04352`
- Discovery of 30 Repeating FRB Sources / 80 total (reveal channel, submitted 2026-05-08): `https://arxiv.org/abs/2605.08410`
- CHIME/FRB Discovery of 25 Repeating Fast Radio Burst Sources (reveal channel): `https://arxiv.org/abs/2301.08762`
