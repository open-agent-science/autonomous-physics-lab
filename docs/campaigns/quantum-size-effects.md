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

This campaign now has six direct Almeida 2023 InP measurement rows and a
source-scoped sandbox baseline. It is **baseline-review-ready**, but not yet
authorized for autonomous correction search or cross-material claims.

## Public Monitoring Snapshot

**Current question:** is the first six-row InP baseline, including its
one-point size holdout and controls, strong enough to authorize a narrowly
bounded autonomous pilot?

**Shareable result:** `TASK-0293` admitted six deterministic figure-derived
Almeida InP rows as direct measurement evidence. `TASK-0225` then froze a
five-row train / one-row largest-size holdout benchmark. The fixed published
Almeida relation produced holdout error `0.048395 eV`, versus `0.420200 eV`
for the constant train-mean null and `0.375676 eV` for a deterministic
shuffled-size control.

**Not a claim:** this is sandbox, source-scoped consistency evidence. The
published relation and rows share the same InP source series, the holdout has
one row, and there is no cross-material validation, new material law, device,
synthesis, biomedical, or design claim.

**Active next work:** `TASK-0277` must review provenance, residuals, controls,
outliers, and leakage risks before `TASK-0226` can be considered. No correction
search is authorized by the baseline alone.

## Historical Source-Readiness Trail

The chronology below records how the direct-row blocker was resolved. Status
labels in this section describe their state at the time and are not the current
execution recommendation.

**Earlier source work:** `TASK-0589` turned the Norris-Bawendi 1996 blocker into a
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
artifact. `TASK-0710` (Vossmeyer source-copy handoff) and `TASK-0711` (Almeida
source-copy checksum/reuse decision) are both DONE and each preserved the same
blocker: no redistributable source copy exists yet, so neither route can land
direct rows.

**Current decision point (resolved):** the maintainer selected option (a) and
`TASK-0741` (DONE) executed it. The Almeida 2023 InP CC-BY 4.0 source was
chosen over Vossmeyer and over the calibration-consistency waiver; the article
and SI were supplied locally, the CC-BY 4.0 license is confirmed on the
version-of-record, and the source bytes are checksum-pinned (see
[`docs/reviews/quantum-almeida-2023-deterministic-source-artifact-package.md`](../reviews/quantum-almeida-2023-deterministic-source-artifact-package.md)).
The deterministic optical-energy axis (six labeled lambda_1s samples,
460-620 nm) was recorded before the size-axis digitization was available.
`TASK-0755` first preserved the missing-raster blocker rather than fabricating
rows. After the maintainer supplied the needed Almeida figure surfaces, the
row-curation and readiness path landed six direct InP rows, `TASK-0293` passed,
and `TASK-0225` produced the first source-scoped sandbox baseline.

**Expected next result (resolved -> review gate):** `TASK-0277` should review
the `TASK-0225` baseline provenance, one-point holdout, controls, residuals,
and leakage risks before any correction-hypothesis pilot is authorized. The
calibration-consistency waiver (option b) and pause (option c) are no longer
the active path.

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
- `TASK-0225` — baseline residual benchmark (DONE; source-scoped sandbox
  baseline on six direct Almeida InP rows, with one largest-size holdout and
  null/shuffled controls);
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
- `TASK-0293` — re-run readiness gate after a direct seed (DONE; six
  deterministic Almeida InP rows admitted as direct measurement evidence);
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
- `TASK-0755` — Almeida 2023 InP size-axis digitization and readiness gate
  (DONE; preserved the first missing-raster blocker and fed the later direct
  Almeida row-curation path).

Safe next contributions are:

- `TASK-0277` review of the first source-scoped baseline before any autonomous
  pilot;
- conservative residual visualization or tabular summaries only after the
  baseline closeout is reflected in task state;
- independent-source scouting for future material-transfer holdouts, without
  treating the six-row Almeida baseline as cross-material evidence.

### What not to implement yet

- do not fetch live datasets, scrape publication tables, or store raw vendor
  spec sheets in the repository without source-manifest review;
- do not treat `data/quantum_dots/source_manifest.yaml` as benchmark data;
- do not run autonomous-pilot work before `TASK-0277` reviews and narrows the
  baseline follow-up scope;
- do not run autonomous formula search across quantum-dot size data merely
  because `TASK-0225` produced a source-scoped baseline;
- do not start a public-facing campaign result, claim, or article task before
  maintainer review approves the baseline interpretation.

Future source-artifact, digitisation, and row-curation work should use the
[Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md) so
calibration-derived rows, direct measurements, and figure-derived points stay
separate before any baseline task runs. Per the protocol's
[open-licensed-first source-selection preference order](../fresh-data-intake-protocol.md#source-selection-preference-order-open-licensed-first),
scout open tabulated sources (Tier 1/2) before opening a figure-digitisation
lane on a closed source; see
[the Quantum application note](../reviews/quantum-open-licensed-first-source-selection-application.md).

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

Current evidence is source-scoped and sandbox-only:

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
- `TASK-0668` and `TASK-0687` kept the two then-promising routes honest:
  Almeida later advanced through the direct-row path, while Vossmeyer remains
  gated on a committable legal source artifact.
- `TASK-0293` admitted six deterministic Almeida InP figure-derived rows as
  direct measurement evidence.
- `TASK-0225` produced the first source-scoped sandbox baseline: the fixed
  published Almeida relation held out the largest-size row with absolute error
  `0.048395 eV`, versus `0.420200 eV` for the train-mean null and
  `0.375676 eV` for the shuffled-size control.

Historical context:

- `tasks/proposals/20260507-roman-quantum-dots-size-effects-campaign.yaml` is
  the accepted proposal that promoted this direction into the canonical
  `TASK-0222`..`TASK-0226` queue.

## Open Questions

- Is the six-row, one-holdout Almeida InP baseline sufficient for any bounded
  autonomous follow-up, or should it remain review-only until an independent
  material/source holdout exists?
- Which independent source could provide the next direct row-level material or
  publication-source holdout?
- Which visualization or tabular summary would help reviewers inspect the
  baseline without implying a design law?
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
- `TASK-0283` originally kept `TASK-0225` blocked because the committed rows
  were not direct measurement rows;
- `TASK-0291` has a deterministic digitisation/table-value protocol, but
  remains blocked until a compliant artifact, primary-source table values,
  maintainer-provided rows, or waiver exists for absorption rows;
- `TASK-0292` has a promising Jasieniak 2011 table path, but remains a
  review-only blocker record until the ACS Supporting Information table or a
  deterministic digitisation artifact is available to the curator;
- `TASK-0306` defined the digitisation protocol and artifact shape that can
  unblock future figure-derived absorption rows once a compliant artifact or
  equivalent table evidence is committed;
- `TASK-0293` re-ran the readiness gate and admitted six direct Almeida InP
  rows;
- `TASK-0298` triaged the direct-measurement source candidates (see
  `docs/reviews/quantum-direct-measurement-source-triage.md`) so row-level
  agents have an explicit first-attempt recommendation per direct-seed task;
- `TASK-0225` produced the first source-scoped baseline; review it before
  opening correction search;
- use `TASK-0326` to decide whether a weaker calibration-consistency benchmark
  is worth explicitly authorizing; TASK-0325 has preserved a Jasieniak 2011
  evidence blocker rather than producing measurement-grade rows;
- `TASK-0326` recommended that any calibration-consistency benchmark be a
  separate follow-up task with labels such as `calibration_curve_consistency`
  and `calibration_derived`; it did not replace the direct-row readiness path;
- use the TASK-0334 source-artifact package as the next handoff for
  Jasieniak 2011: it records the official ACS Supporting Information locator
  and checksum/extraction plan, but row curation remains blocked until the
  SI/table extraction or deterministic digitisation artifact is reviewed;
- use `TASK-0335` as the weak `calibration_curve_consistency` scope contract;
  do not run metrics or pretend to unblock the measurement benchmark;
- use `TASK-0491` as historical context for the calibration-consistency
  alternative: that weaker sandbox-only path still requires explicit
  maintainer approval, declared labels, and frozen negative controls;
- keep `TASK-0336` blocked until `TASK-0334` lands a deterministic artifact or
  the maintainer supplies equivalent table/digitisation evidence;
- run `TASK-0364` against the ranked `TASK-0347` candidates before returning
  to calibration-polynomial sources;
- after `TASK-0225`, use `TASK-0277` to review readiness before the autonomous
  pilot and `TASK-0276` for conservative residual visuals if the review needs
  them;
- run `TASK-0226` only after `TASK-0277` explicitly accepts or narrows the
  pilot scope.

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
- Do not open public-facing scientific claims before maintainer review accepts
  the sandbox baseline interpretation and any future result-promotion path.

## Visualization Ideas

- size-versus-bandgap scatter overlays per material family once an independent
  row-level source exists;
- per-material residual heatmaps over diameter or radius bins;
- absorption-versus-emission diagnostic panels showing why the two should not
  be merged;
- holdout-versus-train residual comparison strips for the current Almeida
  source-scoped baseline and any future independent-source holdout;
- campaign flow diagram from pinned dataset to baseline to holdout to
  sandbox pilot to maintainer review.
