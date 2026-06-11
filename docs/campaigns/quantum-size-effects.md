# Quantum Size Effects

## Goal

Prepare a future APL campaign around size-dependent optical and electronic
properties of semiconductor quantum dots, using theory, computation, dataset
comparison, and visualization only.

The target is not a new quantum-dot design law and not a material-design
framing. The target is a disciplined benchmark surface where compact,
physically constrained size-scaling models can be compared against curated,
source-pinned measurement data with explicit residuals, breakdown maps, and
holdouts.

## Orientation Note for New Contributors

This campaign is currently **scaffold-complete with source-manifest evidence,
but not yet row-level benchmark-ready**.

## Public Monitoring Snapshot

**Current question:** can APL curate direct quantum-dot size/optical-property
measurement rows before running attractive size-effect baselines?

**Shareable result:** the campaign is intentionally blocked from benchmark
metrics because committed rows are calibration-derived rather than direct
measurement rows. That blocker is useful public scientific memory: it shows
APL refusing to score a model against weak provenance.

**Not a claim:** there is no quantum-dot size-effect benchmark result yet, no
new material law, and no device, synthesis, biomedical, or design claim.

**Active next work:** `TASK-0589` turned the Norris-Bawendi 1996 blocker into a
maintainer-ready source-copy checklist, but it still needs a legitimate source
copy, target panel, redistribution decision, WebPlotDigitizer-class tool run,
axis calibration, extracted points, uncertainty, and replay before rows can be
curated. `TASK-0588` rejected the Kang-Wise 1997 fallback as currently
inadmissible: the visible tables are model parameters, not direct size-energy
measurements, and no checksum-pinned source copy or deterministic digitization
package exists. `TASK-0605`, `TASK-0630`, `TASK-0637`, `TASK-0654`, and
`TASK-0655` built the Almeida 2023 non-spherical source route, but it is still
metadata/fixture-only without a source-copy checksum or real digitized points.
`TASK-0687` added a Vossmeyer 1994 source-artifact verification path: promising
for CdS direct-table rows, but still blocked on a committable legal source
artifact. The next task wave is `TASK-0710` (Vossmeyer source-copy handoff) and
`TASK-0711` (Almeida source-copy checksum/reuse decision).

**Expected next result:** a legal source-artifact package or precise blocker
for Vossmeyer or Almeida. The baseline benchmark remains blocked until real
direct measurement rows pass readiness.

The first scaffold, dataset/schema surface, and holdout protocol have landed
under `TASK-0222`, `TASK-0223`, and `TASK-0224`. `TASK-0275` added the first
reviewed source-manifest seed. `TASK-0281` and `TASK-0282` added two
calibration-derived row-level seeds (Yu 2003 cadmium chalcogenides;
Moreels 2009 PbS). `TASK-0283` then ran the row-level readiness gate and
kept `TASK-0225` BLOCKED because every committed row is calibration-derived
rather than directly measured.

Current task posture:

- `TASK-0281` — Yu 2003 multi-material absorption row-level seed (DONE);
- `TASK-0282` — Moreels 2009 PbS absorption row-level extension (DONE);
- `TASK-0283` — row-level readiness gate before baseline (DONE; see
  `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`);
- `TASK-0225` — baseline residual benchmark (BLOCKED; needs either a
  direct-measurement row-level seed or a maintainer waiver to score a
  calibration-curve consistency benchmark instead of a measurement-versus-
  model benchmark);
- `TASK-0291` — direct-measurement absorption seed (DONE; first-attempt
  investigation against Yu 2003 found no tabulated values and figure-only
  scatter points; see
  `docs/reviews/quantum-size-direct-absorption-seed-review.md`. Unblock paths:
  WebPlotDigitizer-class figure digitisation, access to primary source tables
  in Vossmeyer 1994 / Soloviev 2000 / Murray 1993 / Peng 1998,
  maintainer-provided table values, or an explicit maintainer waiver to accept
  relaxed-precision figure reads);
- `TASK-0292` — direct-measurement band-edge seed (DONE; first investigation
  against Jasieniak 2011 found a promising ACS Supporting Information table
  path, but the SI table was not retrieved for row-level review and no
  digitisation artifact exists; see
  `docs/reviews/quantum-size-direct-band-edge-seed-review.md`);
- `TASK-0293` — re-run readiness gate after a direct seed (BLOCKED until
  `TASK-0291` or `TASK-0292` lands, or maintainer waiver is explicit);
- `TASK-0298` — direct-measurement source triage (DONE; see
  `docs/reviews/quantum-direct-measurement-source-triage.md`. Yu 2003 was
  the triaged first-attempt source for `TASK-0291`; Jasieniak 2011 is the
  first-attempt source for `TASK-0292`; Moreels 2009 is a secondary
  `TASK-0291` candidate);
- `TASK-0306` — direct-measurement digitisation protocol (DONE; see
  `docs/quantum-direct-measurement-digitization-protocol.md` for the
  WebPlotDigitizer-class workflow, per-point provenance fields, and the
  list of provenance modes that are never acceptable);
- `TASK-0226` — first autonomous sandbox-only hypothesis pilot (BLOCKED).
- `TASK-0325` — direct-measurement digitisation/table-value package
  (DONE; Jasieniak 2011 band-edge path selected, but no committed SI/table
  extraction or deterministic digitisation artifact exists, so this pass
  produced a blocker package rather than a `qd-*.yaml` seed);
- `TASK-0326` — calibration-curve consistency waiver decision (DONE;
  recommends a separate weaker calibration-curve consistency benchmark only
  after maintainer approval, while keeping `TASK-0225` blocked for the
  original measurement-versus-model benchmark).
- `TASK-0334` — deterministic Jasieniak 2011 source-artifact package
  (DONE; metadata-only source-artifact package records the ACS Supporting
  Information locator and checksum/extraction plan, but no source table or
  deterministic digitisation artifact is committed, so row curation remains
  blocked);
- `TASK-0335` — calibration-curve consistency benchmark scope package
  (DONE; see
  `docs/reviews/quantum-calibration-curve-consistency-benchmark-scope.md`;
  protocol only, no metrics);
- `TASK-0336` — direct band-edge row curation from an approved source artifact
  (BLOCKED until `TASK-0334` or an equivalent maintainer-provided artifact).
- `TASK-0347` — open direct-table source triage (DONE; ranks
  Norris-Bawendi 1996 CdSe and Kang-Wise 1997 PbS as the best first attempts
  because they may expose table-derived direct rows through APS-access paths).
- `TASK-0356` — direct source-artifact intake path (DONE; defines the artifact
  directory layout, required metadata, checksum policy, and row-type evidence
  checklist before any `qd-*.yaml` seed can be curated).
- `TASK-0364` — PMC/arXiv/direct-table source curation attempt (DONE; it
  preserved source blockers and recommended staying with ranked
  `TASK-0347` candidates rather than another calibration-polynomial path).
- `TASK-0490` — synthetic figure-digitization fixture dry run (DONE; validates
  axis calibration, point provenance, uncertainty, and included/excluded point
  states for future WebPlotDigitizer-class artifacts, but adds no real rows).
- `TASK-0491` — calibration-consistency go/no-go scorecard (DONE; records
  `NEEDS_MAINTAINER_DECISION` before any separate sandbox-only implementation,
  preserves the `TASK-0225` and `TASK-0293` blockers, and defines mandatory
  labels, negative controls, stop conditions, and public wording).
- `TASK-0556` — direct-source candidate classification (DONE; recommends
  Norris-Bawendi 1996 as the best current direct-row unblock path, with
  calibration-derived or table-inaccessible candidates kept as blockers);
- `TASK-0563` — deterministic Norris-Bawendi digitization preflight (DONE;
  preserved a precise source-copy/tool-run blocker, with no `qd-*` rows or
  baseline metrics).
- `TASK-0588` — Kang-Wise 1997 fallback source-artifact package (DONE;
  currently not admissible because visible tables are model-parameter tables
  and figure access/digitization remains blocked).
- `TASK-0589` — Norris-Bawendi source-copy handoff (DONE; maintainer-facing
  checklist only, no values or copyrighted source copies).
- `TASK-0605` — scout one additional open direct-table source beyond the
  exhausted Norris/Kang paths (DONE; Almeida 2023 InP optical data was
  selected as promising but digitization/schema-gated).
- `TASK-0630` — Almeida 2023 source-artifact feasibility (DONE;
  `SCHEMA_EXTENSION_NEEDED` because the source uses tetrahedral edge length
  and volume rather than the current diameter/radius-only schema route).
- `TASK-0637` — non-spherical size-axis schema extension (DONE).
- `TASK-0654` — Almeida 2023 license and figure-surface review (DONE;
  metadata-only, no source files or coordinates committed).
- `TASK-0655` — synthetic non-spherical digitization fixture (DONE; validates
  schema/ledger mechanics, no real Almeida points).
- `TASK-0668` — checksum-pinned Almeida source-artifact package (DONE;
  metadata/source-route pass only, no committed source copy, digitization, or
  rows).
- `TASK-0687` — Vossmeyer 1994 source-artifact verification (DONE; promising
  CdS direct-table path, but no committable legal source artifact yet).

Safe next contributions are:

- planning, scope, and limitation notes;
- direct-measurement row-level dataset curation that can re-run the
  `TASK-0283` readiness gate;
- a maintainer-approved waiver package if the first benchmark is intentionally
  scoped as calibration-curve consistency rather than measurement-versus-model;
- deterministic source-artifact packaging for Vossmeyer 1994, Almeida 2023,
  Norris-Bawendi 1996 after a maintainer-provided source copy, or an equivalent
  open direct-table source before any direct band-edge row seed is added;
- visualization sketches that do not require baseline residual artifacts.

### What not to implement yet

- do not fetch live datasets, scrape publication tables, or store raw vendor
  spec sheets in the repository without source-manifest review;
- do not treat `data/quantum_dots/source_manifest.yaml` as benchmark data;
- do not run visualization or autonomous-pilot work before the baseline
  residual artifact exists;
- do not run autonomous formula search across quantum-dot size data before
  `TASK-0225` lands a frozen baseline;
- do not start a public-facing campaign result, claim, or article task before
  the first canonical baseline exists.

Future source-artifact, digitisation, and row-curation work should use the
[Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md) so
calibration-derived rows, direct measurements, and figure-derived points stay
separate before any baseline task runs.

## Why It Matters

This campaign is a candidate next real-data surface for APL because it
combines:

- size-dependent optical and electronic measurements with explicit
  experimental uncertainties;
- compact, interpretable baseline models such as Brus-style effective-mass
  approximations and related size-scaling functions;
- known systematic residual regions across material families, size regimes,
  and absorption-versus-emission semantics;
- holdout-friendly structure across materials, size ranges, sources, and
  composition families;
- easier-to-visualize residuals than nuclear binding-energy surfaces while
  still requiring discipline about provenance.

A clean failure map across material families is already useful scientific
memory, even before any compact correction term survives a holdout.

## Current Results

No benchmark result yet.

Current evidence is infrastructure and source curation only:

- `TASK-0222` created this campaign page;
- `campaign_profiles/quantum-size-effects.yaml` — the campaign profile and
  guardrails;
- `docs/notes/quantum-size-effects-campaign-plan.md` — the sequenced plan;
- `tasks/microtasks/quantum-size-effects.yaml` — a small scoped microtask
  queue for planning-only contributions;
- `TASK-0223` defined the dataset/source-manifest schema surface;
- `TASK-0224` defined the holdout protocol;
- `TASK-0275` added a reviewed source-manifest seed, but no row-level
  measurement dataset.
- `TASK-0281` and `TASK-0282` added calibration-derived absorption row-level
  seeds for Yu 2003 cadmium chalcogenides and Moreels 2009 PbS.
- `TASK-0283` reviewed those seeds and kept the benchmark blocked because they
  are calibration-derived rather than direct measurement rows.
- `TASK-0335` defines the separate
  `quantum_calibration_curve_consistency` scope package for a possible weaker
  calibration-derived benchmark, but records no metrics and does not unblock
  the direct measurement-versus-model benchmark.
- `TASK-0347` gives the campaign a ranked open-source path away from the
  Jasieniak ACS blocker: first try Norris-Bawendi 1996 CdSe, then Kang-Wise
  1997 PbS, then Andreev-Lipovskii 1999 PbS if the first two fail.
- `TASK-0356` gives curators a concrete intake path for maintainer-provided or
  open source files, including required metadata and checksum handling.
- `TASK-0490` validates the shape of a future figure-digitization ledger with
  synthetic data only; it is infrastructure for later row curation, not a
  quantum-dot measurement result.
- `TASK-0491` records `NEEDS_MAINTAINER_DECISION` for any separate
  `quantum_calibration_curve_consistency` sandbox implementation. It defines
  mandatory labels, negative controls, and stop conditions without running
  metrics or unblocking the direct-row benchmark.
- `TASK-0668` and `TASK-0687` keep the two most promising current routes
  honest: Almeida 2023 and Vossmeyer 1994 both remain source-artifact gated
  before any real measurement rows can be committed.

Historical context:

- `tasks/proposals/20260507-roman-quantum-dots-size-effects-campaign.yaml` is
  the accepted proposal that promoted this direction into the canonical
  `TASK-0222`..`TASK-0226` queue.

## Open Questions

- Which property kind should anchor the first benchmark — absorption peak,
  emission peak, or bandgap — and how should the other two be treated when the
  dataset task lands?
- Which baseline family should be the conservative first comparison — a
  Brus-style effective-mass approximation, a generalized size-scaling
  function, or both with explicit per-material applicability flags?
- Which holdout split should be required versus optional — material-level,
  size-range, publication-source, or composition-family?
- How should absorption-versus-emission and bandgap semantics be separated in
  the dataset so they are not mistakenly mixed under one residual metric?
- How should size-related fields be canonicalized — diameter versus radius,
  in nanometers, with what tolerance for reported uncertainty?

## Recommended Tasks

- `TASK-0223` and `TASK-0224` have delivered the dataset/schema and holdout
  foundation;
- `TASK-0275` has delivered the first source-manifest seed;
- `TASK-0281` and `TASK-0282` delivered calibration-derived row-level
  absorption seeds;
- `TASK-0283` keeps `TASK-0225` blocked because the committed rows are not
  direct measurement rows;
- `TASK-0291` has a deterministic digitisation/table-value protocol, but
  remains blocked until a compliant artifact, primary-source table values,
  maintainer-provided rows, or waiver exists for absorption rows;
- `TASK-0292` has a promising Jasieniak 2011 table path, but remains a
  review-only blocker record until the ACS Supporting Information table or a
  deterministic digitisation artifact is available to the curator;
- `TASK-0306` defined the digitisation protocol and artifact shape that can
  unblock future figure-derived absorption rows once a compliant artifact or
  equivalent table evidence is committed;
- `TASK-0293` should re-run the readiness gate after either direct seed lands;
- `TASK-0298` triaged the direct-measurement source candidates (see
  `docs/reviews/quantum-direct-measurement-source-triage.md`) so row-level
  agents have an explicit first-attempt recommendation per direct-seed task;
- next, add at least one direct-measurement row-level `qd-*.yaml` seed and
  re-run the readiness gate, or request a maintainer waiver for a
  calibration-curve consistency benchmark;
- use `TASK-0326` to decide whether a weaker calibration-consistency benchmark
  is worth explicitly authorizing; TASK-0325 has preserved a Jasieniak 2011
  evidence blocker rather than producing measurement-grade rows;
- `TASK-0326` recommends that any calibration-consistency benchmark be a
  separate follow-up task with labels such as `calibration_curve_consistency`
  and `calibration_derived`; it should not unblock `TASK-0225` or replace
  direct-row readiness review by itself;
- use the TASK-0334 source-artifact package as the next handoff for
  Jasieniak 2011: it records the official ACS Supporting Information locator
  and checksum/extraction plan, but row curation remains blocked until the
  SI/table extraction or deterministic digitisation artifact is reviewed;
- use `TASK-0335` as the weak `calibration_curve_consistency` scope contract;
  do not run metrics or pretend to unblock the measurement benchmark;
- use `TASK-0491` as the go/no-go scorecard: a separate sandbox-only
  calibration-consistency task requires explicit maintainer approval, all
  declared labels, frozen negative controls, and the preserved `TASK-0225`
  and `TASK-0293` blockers;
- keep `TASK-0336` blocked until `TASK-0334` lands a deterministic artifact or
  the maintainer supplies equivalent table/digitisation evidence;
- run `TASK-0364` against the ranked `TASK-0347` candidates before returning
  to calibration-polynomial sources;
- after `TASK-0225`, use `TASK-0276` for conservative residual visuals and
  `TASK-0277` to review readiness before the autonomous pilot;
- run `TASK-0226` only after a maintainer-approved baseline exists.

Planning-only microtasks may be picked from
`tasks/microtasks/quantum-size-effects.yaml`. They must not produce canonical
results, claims, datasets, or experiments.

## Recommended Contributor Types

- condensed-matter contributors who like dataset curation and source-manifest
  work;
- benchmark designers comfortable with baselines, breakdown maps, and subset
  metrics;
- visualization contributors who can sketch residual maps without claiming
  unpublished data;
- reviewers focused on overclaim resistance, provenance discipline, and
  scope separation between synthesis and computation.

## What Not To Claim

- Do not say APL has discovered a quantum-dot design law.
- Do not say baseline residuals imply a new condensed-matter theory.
- Do not say the campaign supports material selection, device fabrication, or
  biomedical applications.
- Do not provide synthesis recipes, chemical handling guidance, or device
  fabrication instructions of any kind.
- Do not blur absorption peak, emission peak, and bandgap values under one
  residual metric.
- Do not promote sandbox fit improvements as canonical benchmark results.
- Do not open public-facing scientific claims before the first canonical
  baseline and residual benchmark exist.

## Visualization Ideas

- size-versus-bandgap scatter overlays per material family once the dataset
  task lands;
- per-material residual heatmaps over diameter or radius bins;
- absorption-versus-emission diagnostic panels showing why the two should not
  be merged;
- holdout-versus-train residual comparison strips once the holdout protocol
  exists;
- campaign flow diagram from pinned dataset to baseline to holdout to
  sandbox pilot to maintainer review.
