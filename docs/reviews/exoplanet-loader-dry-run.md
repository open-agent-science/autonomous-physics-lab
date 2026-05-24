# Exoplanet Mass-Radius Loader Dry-Run

**Task:** TASK-0354
**Status:** dry-run plumbing only (no real catalog row exists; no
baseline scored; no claim promoted)
**Campaign:** Exoplanet Mass-Radius
**Inputs:**

- `physics_lab/datasets/exoplanets.py` — loader module
- `tests/fixtures/exoplanets/synthetic_pscomppars_snapshot.yaml` — synthetic fixture
- `tests/test_exoplanet_mass_radius_loader.py` — test suite
- `docs/reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md` (TASK-0345) — filter chain source of truth
- `docs/exoplanet-mass-radius-baseline-protocol.md` (TASK-0346) — downstream consumer
- `physics_lab/schemas/exoplanet_mass_radius.schema.json` (TASK-0337) — row schema
- `data/exoplanets/source_manifest_template.yaml` — query contract

## Scope

This dry-run delivers a deterministic exoplanet dataset loader that
can be run **before** the first real `PSCompPars` snapshot lands. It
exercises every inclusion/exclusion filter branch the future ingestion
task will need, using **only synthetic fixture rows**. No live NASA
Exoplanet Archive data is fetched, no Chen-Kipping baseline is
evaluated, no metric is computed, no plot is rendered, no prediction
registry entry is registered, and no claim is promoted.

The dry-run lets a future curator:

- validate that the loader handles a realistic PSCompPars-shaped
  snapshot without surprises;
- pre-confirm that the per-class counts and exclusion-reason
  histograms are useful diagnostics for the eventual ingestion review
  note;
- swap the synthetic fixture for a real snapshot under
  `data/exoplanets/exo-NNNN-pscomppars-snapshot.yaml` and re-run the
  loader without changing the loader code.

## What The Loader Does

`physics_lab/datasets/exoplanets.py` exposes three functions plus a
result dataclass:

| Function | Role |
| --- | --- |
| `load_exoplanet_snapshot(path)` | reads YAML + runs invariants beyond the JSON Schema (synthetic safety, non-empty entries, no-live-fetch on committed snapshots) |
| `apply_inclusion_filters(snapshot, *, mass_sigma_threshold, radius_sigma_threshold)` | applies the seven-step filter chain and returns a `FilteredSnapshot` |
| `summarize(filtered)` | JSON-serializable summary for review notes / PR bodies |
| `load_and_filter(path, ...)` | convenience wrapper for the common case |

The seven-step filter chain (mirrors TASK-0345 plan ordering):

1. **Unknown class guard** — reject rows whose `row_class`,
   `mass_class`, or `radius_class` is outside the canonical buckets.
2. **Duplicate planet-name guard** — fail any planet that appears
   twice within the same snapshot.
3. **Snapshot-time exclusion** — preserve any row marked
   `inclusion_status: excluded` with its declared reason (synthetic
   equivalent of `soltype != Published Confirmed`).
4. **Mass-class gate for true-mass axis** — drop
   `mass_class == "model_inferred"` rows (circular-validation guard).
5. **Radius-class gate for transit-radius axis** — drop
   `radius_class == "model_inferred"` rows (non-transit-derived).
6. **Mass relative-uncertainty filter** — drop rows where
   `sigma_M / M > mass_sigma_threshold` (default 0.30).
7. **Radius relative-uncertainty filter** — drop rows where
   `sigma_R / R > radius_sigma_threshold` (default 0.15).

The loader also reports **both** pre-filter and post-filter counts so
the pre/post comparison is itself a diagnostic.

## What The Loader Does Not Do

- It does not fetch from NASA Exoplanet Archive (or any other live
  source). Live external fetch is disallowed on committed snapshots
  and the loader enforces this.
- It does not compute Chen-Kipping baseline residuals, calibration
  metrics, z-scores, or failure maps. Those belong to a future
  baseline-implementation task that the TASK-0346 protocol governs.
- It does not silently rewrite `mass_class`, `radius_class`,
  `inclusion_status`, or `inclusion_reason`. An unknown class raises
  a dedicated exclusion reason rather than being mapped to a default
  bucket.
- It does not produce habitability, biosignature, or
  planet-prioritization output.

## Synthetic Fixture Shape

`tests/fixtures/exoplanets/synthetic_pscomppars_snapshot.yaml` carries
10 fabricated rows that span every filter branch:

| Row | Class | Filter outcome |
| --- | --- | --- |
| SYN-001 Earth-like | direct, true mass, transit radius | included |
| SYN-002 sub-Neptune | direct, true mass, transit radius | included |
| SYN-003 hot Jupiter | direct, true mass, transit radius | included |
| SYN-004 M sin i only | rv_minimum_mass_only | included (minimum-mass axis) |
| SYN-005 model-inferred mass | model_inferred mass | **excluded** (circular validation) |
| SYN-006 model-inferred radius | true mass + non-transit radius | **excluded** (non-transit radius) |
| SYN-007 noisy mass | direct, sigma_M/M = 0.40 | **excluded post-filter** |
| SYN-008 noisy radius | direct, sigma_R/R = 0.25 | **excluded post-filter** |
| SYN-009 microlensing | microlensing_mass | included (alternate axis) |
| SYN-010 snapshot-excluded | already `inclusion_status: excluded` | preserved with its reason |

Pre-filter included: **7** rows. Post-filter included: **5** rows.
Exclusion-reason histogram covers all five canonical reason codes plus
the snapshot-preserved `solution_type_not_confirmed`.

## Tests

`tests/test_exoplanet_mass_radius_loader.py` covers:

- fixture-level invariants (synthetic safety, non-empty entries,
  no-live-fetch on non-synthetic snapshots);
- the seven-step filter chain (per-row outcomes and per-reason
  exclusion counts);
- threshold override behavior (relaxed and strict);
- duplicate-name guard and unknown-class guard;
- schema-versus-loader bucket consistency (catches any drift between
  the schema enums and the loader's `KNOWN_*` constants);
- summary JSON-serializability and threshold reporting;
- input-snapshot immutability across repeated filter calls.

Total: **14 passing tests** in `0.5 s`.

## What Future Work Should Use This Loader For

The loader is intentionally narrow:

1. A future maintainer-approved ingestion task lands the real pinned
   `PSCompPars` snapshot at `data/exoplanets/exo-NNNN-pscomppars-snapshot.yaml`
   under the same schema.
2. A pre-baseline review task runs `load_and_filter` against that
   real snapshot, captures the `summarize()` JSON, and includes it in
   the snapshot's review note so the row counts and exclusion histogram
   are reviewable before any baseline runs.
3. A later baseline-implementation task (TASK-0346 protocol) consumes
   the `included_rows` from `FilteredSnapshot` as its scoring set; it
   reports both pre- and post-filter metrics per the protocol.

Steps 2 and 3 are **separate maintainer-approved tasks**. This dry-run
does not unblock either.

## Limitations

- All counts in this document and in the test suite are tied to the
  synthetic fixture. Updating the fixture requires updating the
  assertions; do not relax tests to accommodate fixture drift without
  explanation.
- The fixture is not a physically realistic exoplanet population; it
  is a stress-test of filter branches.
- The loader's quality-filter thresholds (0.30 for mass, 0.15 for
  radius) match the TASK-0345 plan's recommended defaults. A future
  ingestion task may justify different thresholds as long as both
  pre- and post-filter views are recorded in the snapshot review.
- The loader does not validate the snapshot against the JSON Schema
  itself; that step belongs to the repository's existing
  schema-validation harness and runs separately.

## Verdict

`VALID` as plumbing for the future real-snapshot ingestion path.
`INCONCLUSIVE` as benchmark evidence (no real catalog row exists
yet). The next allowed step is a maintainer-approved ingestion task
that consumes the locked PSCompPars query contract from TASK-0345 and
emits a real snapshot under
`data/exoplanets/exo-NNNN-pscomppars-snapshot.yaml`.
