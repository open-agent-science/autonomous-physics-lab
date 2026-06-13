# Materials MD-0002 Acquisition Runbook Result

**Task:** `TASK-0699`
**Campaign:** Materials Property Residuals
**Status:** blocked before live fetch
**Verdict:** `BLOCKED_KEY_GATED_NO_FETCH`

## Scope

`TASK-0699` is the maintainer-gated Materials Project acquisition task for
`MD-0002`. Its accepted output would be value-bearing MD-0002 source/data
artifacts:

- `data/materials/snapshots/materials_project_stable_ternary_oxides_<database_version>.json`
- `data/materials/md-0002-materials-project-formation-energy.yaml`
- `data/materials/md-0002-materials-project-band-gap.yaml`
- a populated `data/materials/md0002_holdout_manifest.yaml`

This run did not create those artifacts because the required secret-gated source
access was not available.

## Blocker

The task contract requires `MP_API_KEY` to be provided outside the repository and
forbids committing secrets. The execution environment did not expose
`MP_API_KEY`, so no Materials Project API request was made.

This is a correct stop condition. The acquisition must not be simulated with fake
rows, copied from the fixture, silently skipped while marking the task complete,
or replaced with benchmark/scoring work.

## Maintainer-Run Next Step

From a local maintainer shell with a personal Materials Project API key:

```bash
python3 -m pip install mp-api
export MP_API_KEY="<your key>"
```

Then execute the frozen `TASK-0631` / `TASK-0670` contract:

- query Materials Project summary for stable ternary oxides:
  `elements` contains `O`, `nelements == 3`, `is_stable == true`;
- request `material_id`, `formula_pretty`, `composition`, `nelements`,
  `elements`, `energy_above_hull`, `is_stable`,
  `formation_energy_per_atom`, `band_gap`, `symmetry.symbol`, DFT functional
  indicator, and `database_version`;
- stop and report if included rows exceed 1500 per axis;
- pin `database_version`, retrieval UTC, exact filter dictionary, raw snapshot
  checksum, and normalized dataset checksums;
- commit formation-energy and band-gap dataset files as separate computed-DFT
  axes with CC BY 4.0 attribution;
- populate `data/materials/md0002_holdout_manifest.yaml` before any residual or
  benchmark inspection.

## Guardrails Preserved

- No `MP_API_KEY` was committed, printed, or written into an artifact.
- No live Materials Project fetch was attempted from this agent environment.
- No fake fixture rows were promoted into MD-0002 data files.
- No benchmark metrics, residuals, material recommendations, `RESULT-*`,
  `PRED-*`, `CLAIM-*`, or knowledge promotion were created.
- Formation energy and band gap remain separate planned axes.

## Output Routing Summary

- Task verdict: `BLOCKED_KEY_GATED_NO_FETCH`.
- Canonical destination: this review note plus the `TASK-0699` blocker state.
- Review tier: `none`.
- Gate A status: `not_attempted`; source access was unavailable.
- Gate B status: `not_applicable`; no replay or benchmark metric was attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: MD-0002 value-bearing acquisition remains blocked until a
  maintainer reruns the task with `MP_API_KEY`, pins version/checksums/row
  counts, and freezes holdout assignments.
