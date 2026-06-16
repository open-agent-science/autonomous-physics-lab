# Publish Full DEBCat Stellar M-L Dataset Under Granted CC BY 4.0

**Task:** `TASK-0763`
**Campaign:** `textbook-formula-audit` (Stellar mass-luminosity)
**Verdict:** `PERMISSION_GRANTED_FULL_DATASET_PUBLISHED_CC_BY_4_0` — the
long-standing DEBCat redistribution blocker is cleared by an explicit maintainer
permission; the full normalized rows and frozen holdout manifest are now
committed under CC BY 4.0. No benchmark result, prediction, or claim is promoted
by this task.

## Permission Grant (the gate that was missing)

The Stellar M-L source policy committed only the deterministic extractor plus
non-substitutive `*.sample.yaml` artifacts, because TASK-0628 / TASK-0731 found
no explicit DEBCat redistribution licence. `data/DATA_LICENSES.yaml` recorded the
exact unblock condition: *"Full rows may be committed only under explicit DEBCat
redistribution permission."*

That permission has now been granted by the DEBCat maintainer:

- **Requested by:** Roman Hladun (`gladunrv@gmail.com`), email to John Southworth, 2026-06-13.
- **Granted by:** Dr John Southworth (DEBCat maintainer, Astrophysics Group, Keele University; reply from `taylorsouthworth@gmail.com`), 2026-06-16.
- **Verbatim grant:** "All the information in DEBCat is publicly available from
  other sources as well as DEBCat. I am happy for you to include what you wish
  from DEBCat in your repository, if you apply a CC BY 4.0 license."
- **Condition applied:** CC BY 4.0 with attribution to Southworth, J. (2015),
  ASP Conf. Ser. 496, 164, and a link to DEBCat.

The request offered redistribution under CC BY 4.0 with full attribution, or, if
declined, an extractor-only fallback. The grant accepted CC BY 4.0, so the
forward-compatible "extractor + sample" posture flips to "full dataset committed".

## What This Task Committed

- `data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml` — full
  normalized component rows (748 component rows across 373 systems; 742 admitted,
  6 excluded; luminosity provenance: 597 direct, 145 derived).
- `data/textbook_formula_audit/stellar_ml/debcat_holdout_manifest.yaml` — the
  frozen, value-blind system-level split (train 191 / validation 81 /
  holdout 100 / excluded 1 systems).
- `debcat_component_rows.yaml.license.yaml` and
  `debcat_holdout_manifest.yaml.license.yaml` — sibling redistribution markers
  (`redistribution_status: cc_by_4_0` + `permission_evidence`) that the
  `tests/test_stellar_ml_debcat_rows.py` guard requires before any full file may
  be committed.
- `.gitignore` — removed the DEBCat full-file ignore block.
- `source_artifacts/debcat/provenance.yaml` — flipped `full_dataset_committed`
  to `true`, recorded the CC BY 4.0 status and `publication_task: TASK-0763`.
- `data/DATA_LICENSES.yaml` — `debcat-stellar-ml-sample` entry updated to
  `license: CC BY 4.0`, permission evidence recorded, full paths declared.

The rows were produced deterministically by `scripts/extract_debcat_stellar_ml_rows.py`
from the pinned `debs.dat` snapshot (SHA-256 `326902...b464da`, 95297 bytes,
remote `Last-Modified` 2026-05-16), fetched locally with
`scripts/fetch_source_artifact.py` and checksum-verified. This is the same
extractor and snapshot the committed samples were derived from, so the committed
full files match the documented local-regeneration path.

## Scope and Limitations

- **Raw artifact still not committed.** The raw `debs.dat` ASCII table is *not*
  vendored. Route 2 (metadata-only checksum pinning) is retained because the raw
  table is regenerable from the pinned locator and checksum; the grant would also
  permit committing it, but there is no need.
- **No benchmark result or claim.** This task only publishes the dataset under a
  now-explicit licence. It does not fit a mass-luminosity exponent, compute
  residuals, run a benchmark, or promote a `RESULT-*`/`PRED-*`/`CLAIM-*`. The
  holdout lanes remain frozen and value-blind.
- **No leakage change.** The committed manifest is the same deterministic,
  system-level, value-blind split the extractor produces; component pairs from a
  single physical binary stay in one lane.
- **Future DEBCat release.** Southworth noted (2026-06-16) that an improved
  DEBCat database is planned but at least a year out. This dataset is pinned to
  the checksummed 2026-05-16 snapshot and remains valid; ingesting any future
  DEBCat release is a separate task.

## Validation

- `python3 -m pytest tests/test_stellar_ml_debcat_rows.py tests/test_data_redistribution_declarations.py tests/test_docs_links.py`
- `python3 -m ruff check .`
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`

## Not A Claim

DEBCat component masses and luminosities are curated catalogue observations.
Publishing them under CC BY 4.0 makes the benchmark reproducible; it is not a
stellar-structure result, a mass-luminosity law, or any physical claim.
