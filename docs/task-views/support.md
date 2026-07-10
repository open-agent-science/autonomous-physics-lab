# Support Tasks

> This file is generated from canonical `tasks/TASK-*.yaml` files.
> Generated support-lane view for docs, workflow, coverage, repository, and contributor-experience work that should not displace research mode by default.
> Refresh with `python3 -m physics_lab.cli sync-active-board .`.

## READY

- `TASK-0959` - Repackage RESULT-0027 onto a Gate-B-safe workflow and surface the fair-null comparison honestly (`scientific_replay_validation`, priority `high`, difficulty `medium`, domain `astrophysics`)
- `TASK-0960` - Enforce Gate-B-replayable commands at Gate A packaging time (`maintainer_tooling`, priority `high`, difficulty `medium`, domain `cross_campaign_quality`)
- `TASK-0985` - Replay ThermoML RESULT-0028 through a Gate-B-safe workflow (`scientific_replay_validation`, priority `high`, difficulty `medium`, domain `thermophysical_property_estimation`)

## IN_PROGRESS

None.

## REVIEW_READY

- `TASK-0969` - Harden CI: least-privilege GITHUB_TOKEN on ci.yml and SHA-pin all GitHub Actions (`repository_hardening`, priority `high`, difficulty `low`, domain `repository_hardening`)
- `TASK-0970` - Add Dependabot config for GitHub Actions and pip supply-chain updates (`repository_hardening`, priority `medium`, difficulty `low`, domain `repository_hardening`)
- `TASK-0971` - Doctor: detect a stale physics_lab editable install that breaks the validation gate (`tooling_fix`, priority `high`, difficulty `low`, domain `repository_hardening`)
- `TASK-0972` - Replace the workflow runner if-chain with a data-driven dispatch table (`code_quality_refactor`, priority `medium`, difficulty `low`, domain `repository_architecture`)
- `TASK-0973` - Split registry god-package (slice 1): extract PR helpers into physics_lab/ops/pr_helpers (`code_quality_refactor`, priority `medium`, difficulty `medium`, domain `repository_architecture`)
- `TASK-0981` - Closeout policy guard for task-queue seeded tasks (`maintainer_workflow`, priority `high`, difficulty `low`, domain `maintainer_workflow`)
- `TASK-0984` - Audit the FRB sealed-registration pack before maintainer prediction freeze (`scientific_validation`, priority `high`, difficulty `medium`, domain `radio_transients_astrophysics`)
- `TASK-1000` - Add maintainer review queue anti-stall guardrails (`maintainer_tooling`, priority `high`, difficulty `low`, domain `maintainer_review`)
- `TASK-1003` - Split registry god-package (slice 2): move agent_run_pr into ops and drop its registry re-export (`code_quality_refactor`, priority `medium`, difficulty `low`, domain `repository_architecture`)
