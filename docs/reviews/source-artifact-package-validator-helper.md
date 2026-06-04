# Source Artifact Package Validator Helper Review

**Task:** TASK-0379
**Status:** validator helper review; no source fetches; no rows; no claims
**Code:** `physics_lab/registry/source_artifacts.py`

## Inputs Reviewed

- `TASK-0379`
- `templates/source_artifact_package/`
- `docs/fresh-data-intake-protocol.md`
- `docs/fresh-data-stop-conditions.md`
- `docs/source-manifest-minimum-schema.md`
- `docs/extraction-ledger-template.md`

## Method

This task adds an opt-in deterministic validator for source artifact package
directories. The helper checks:

- required package files;
- provenance metadata;
- stable citation or locator;
- checksum sidecar or explicit archive policy for pinned/value-bearing
  artifacts;
- completed redistribution/license posture when artifacts are pinned;
- row-class and inclusion-status labels;
- blocker reasons for blocker-only packages;
- review status and allowed next step.

The helper does not fetch external sources, inspect remote locators, ingest row
values, run benchmarks, or promote claims.

## Accepted Output Check

- `physics_lab/registry/source_artifacts.py` implements the validation helper.
- `physics_lab/cli.py` exposes `validate-source-artifact-package` with Markdown
  style console output and `--json` automation output.
- `tests/test_source_artifact_package_validation.py` covers valid packages,
  checksum sidecars, missing checksum/archive policy, missing license posture,
  missing row class, blocker-only packages, and missing blocker fields.
- This review note records scope and limitations.

## Limitations

- The helper is opt-in and is not wired into full repository validation yet,
  because some historical source artifact directories are metadata-only notes
  that predate the package template.
- The helper verifies local package structure and metadata, not scientific
  correctness of extracted values.
- JSON output is for automation/reporting only and does not create tasks,
  merge PRs, promote claims, or rewrite source artifacts.

## Verdict

`VALID` as a deterministic source artifact package validation helper. It
supports source-heavy campaign work while keeping value ingestion and claim
promotion out of scope.
