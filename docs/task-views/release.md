# Release Tasks

> This file is generated from canonical `tasks/TASK-*.yaml` files.
> Generated release/readiness view for public wording, replication, signoff, and launch-gate work that needs a maintainer-facing checklist.
> Refresh with `python3 -m physics_lab.cli sync-active-board .`.

## READY

- `TASK-0869` - Package the ThermoML Tb family-stratified Joback transfer as a bounded Gate A result (`scientific_result_publication`, priority `high`, difficulty `high`, domain `thermophysical_property_estimation`)
- `TASK-0886` - Prepare a maintainer-review packet for Stellar RESULT-0024 high-mass transfer (`scientific_result_publication`, priority `medium`, difficulty `medium`, domain `astrophysics_stellar`)
- `TASK-0887` - Prepare the MD-0002 external dataset release and DOI decision packet (`scientific_source_curation`, priority `medium`, difficulty `medium`, domain `materials_science`)
- `TASK-0888` - Package the Exoplanet null-baseline negative/control memory only if Gate A can be made deterministic (`scientific_result_publication`, priority `medium`, difficulty `medium`, domain `astrophysics`)
- `TASK-0890` - Prepare a public-safe maintainer-review packet for Nuclear RESULT-0025 point-estimator evidence (`scientific_result_publication`, priority `medium`, difficulty `medium`, domain `nuclear_physics`)

## IN_PROGRESS

None.

## REVIEW_READY

- `TASK-0883` - Harden CI: fork-guard the self-hosted PR runner so untrusted fork-PR code runs on GitHub-hosted runners (public-repo RCE guard) (`maintainer_tooling`, priority `high`, difficulty `low`, domain `ci_security`)
- `TASK-0884` - Docs coherence: correct now-false 'still private' wording after the v0.2 public opening (strategy + contributor pilot) (`documentation`, priority `medium`, difficulty `low`, domain `release_readiness`)
