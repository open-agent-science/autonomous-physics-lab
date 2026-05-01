# Review Metadata Contract

## Purpose

Each workflow run produces human-readable patch-style artifacts — `claim_update.patch.md`,
`knowledge_update.patch.md`, and `review_summary.md` — that a maintainer reads before
deciding whether to promote a claim or update the knowledge graph.

The `review_metadata.yaml` file is a machine-readable companion to these markdown artifacts.
It captures the same structured information in a format that tools, automated checks, and
future agent workflows can parse directly without interpreting markdown prose.

## File Location

```
results/<EXP-id>/<RUN-id>/review_metadata.yaml
```

One file per run.  The path is registered in the corresponding `result.yaml` under the
`artifacts.review_metadata` key.

## Schema

The file is validated against `physics_lab/schemas/review_metadata.schema.json`
(JSON Schema 2020-12).

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `schema_version` | string, `"1"` | Schema version tag |
| `artifact_type` | string, `"review_metadata"` | Fixed discriminator |
| `result_id` | string (`RESULT-XXXX`) | Corresponding result identifier |
| `run_id` | string (`RUN-XXXX`) | Run identifier |
| `experiment_id` | string (`EXP-XXXX`) | Experiment identifier |
| `claim_id` | string (`CLAIM-XXXX`) | Target claim for suggested update |
| `knowledge_id` | string (`KNOW-XXXX`) | Target knowledge note |
| `generated_at` | ISO-8601 datetime | When the workflow run generated this file |
| `proposed_claim_status` | enum | One of `DRAFT`, `PARTIALLY_SUPPORTED`, `SUPPORTED`, `DISPUTED`, `RETRACTED` |
| `required_human_review` | boolean | Always `true`; no automated promotion is performed |
| `evidence_basis` | array of strings | Result IDs and other artefact references supporting the proposal |
| `claim_target_file` | string | Repository-relative path to the claim file |
| `knowledge_target_file` | string | Repository-relative path to the knowledge note |
| `patch_artifacts.claim_patch` | string | Path to `claim_update.patch.md` |
| `patch_artifacts.knowledge_patch` | string | Path to `knowledge_update.patch.md` |
| `patch_artifacts.review_summary` | string | Path to `review_summary.md` |

## Invariants

- `required_human_review` is always `true`.  No workflow sets it to `false`.
- `proposed_claim_status` reflects the workflow's best suggestion, not a recorded promotion.
- A maintainer must read the markdown patch artifacts before acting on this file.
- The file does not replace the human-readable patch artifacts; it supplements them.

## Usage

A tool or future agent can use this file to:

- enumerate pending review proposals without parsing markdown;
- filter runs by proposed claim status;
- cross-reference runs against claims without loading full result payloads;
- verify that patch artifacts exist at the declared paths.

## Validation

`review_metadata.yaml` is validated as part of repository strict validation
(`python3 -m physics_lab.cli validate-repo . --strict`).

The strict run also checks that the file exists as a required run artifact alongside
`result.yaml`, `metrics.json`, `report.md`, and the markdown patch files.
