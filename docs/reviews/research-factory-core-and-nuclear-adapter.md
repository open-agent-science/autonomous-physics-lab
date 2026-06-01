# Research Factory Core + Nuclear Adapter (TASK-0506)

Implementation review for the first executable slice of the v0.3 Research
Factory layer: a reusable campaign-agnostic core plus the first Nuclear
residual-law adapter and a bounded smoke run. It implements
[research-factory-protocol.md](../research-factory-protocol.md) and the
[Nuclear sprint contract](../nuclear-residual-factory-sprint-protocol.md), and
emits a [`factory_summary`](../factory-summary-artifact.md) artifact. It does
**not** run the full 50-100 candidate sprint (TASK-0507) or create any canonical
artifact.

## What landed

- `physics_lab/factories/core.py` — campaign-agnostic core: `FactorySpec`
  (config loader), `Candidate`, `FactoryRun`, the `CampaignAdapter` protocol, an
  adapter registry (`register_adapter` / `get_adapter`), `run_factory`
  (orchestration + cap enforcement + candidate-count assembly + **schema
  validation of the summary before it leaves the core**), and
  `write_factory_summary`.
- `physics_lab/factories/nuclear.py` — `NuclearResidualFactoryAdapter`: loads the
  committed nuclide slice, reads frozen semi-empirical baseline coefficients from
  the committed `RESULT-0015` artifact (reusing
  `physics_lab/engines/nuclear_mass_baselines.py`), builds residual-correction
  candidates from `shell_distance` and `odd_even_pairing`, applies a null-baseline
  and a shuffled-feature control, and routes each candidate.
- `scripts/run_research_factory.py` — deterministic, campaign-agnostic entrypoint
  (`--config`, `--output-dir`); it selects the adapter by `adapter_id` and never
  contains Nuclear-specific code.
- `examples/factories/nuclear_residual_factory_smoke.yaml` — the bounded smoke
  config.
- `tests/test_research_factory_core.py`, `tests/test_nuclear_residual_factory.py`.

## Reuse without copying the Nuclear path

A second campaign joins the runner by:

1. declaring `allowed_factory_families` / `required_factory_controls` /
   `factory_stop_rules` in its `campaign_profiles/<id>.yaml` (Exoplanet already
   has these, TASK-0508);
2. implementing a class with `adapter_id`, `adapter_version`, and
   `build_run(spec) -> FactoryRun`, then calling `register_adapter(...)`;
3. pointing a factory config at the new `adapter_id`.

The runner and `run_factory` are unchanged — no Nuclear code is copied. The
core enforces the candidate cap, the canonical route-verdict / candidate-state
vocabulary, and schema validity for every adapter.

## Controls and leakage guard

- Every executed candidate records a **null-baseline** and a **shuffled-feature**
  control outcome. A candidate whose shuffled control reduces residual as much as
  the real feature routes to `REJECTED_BY_CONTROL`.
- Leakage-sensitive families (`residual_free_local_topology`,
  `separation_energy_derived`, `local_curvature`) are **blocked**
  (`PREFLIGHT_REJECTED` / `DATA_QUALITY_BLOCKED`, `leakage_status: NOT_CHECKED`)
  in this smoke adapter until a dedicated no-leakage implementation is added.
  They do not silently execute just because a config flag is present.

## Deviation from the task's accepted-output path

The task listed `examples/nuclear_residual_factory_smoke.yaml`, but
`validate-repo` validates **every** top-level `examples/*.yaml` against the
`example_config` schema (non-recursive glob). A factory config is a different
shape, so it is placed at `examples/factories/nuclear_residual_factory_smoke.yaml`
(a subdirectory the example-config glob does not pick up). This keeps strict
validation green without weakening it.

## Boundaries / limitations

- Bounded two-family smoke over an 11-nuclide committed slice; the numbers are
  plumbing, not a scientific result.
- The baseline is not refit during the factory run; coefficients are read from
  the committed `results/EXP-0012/RUN-0001/result.yaml` artifact.
- No `prediction_registry`, `results/`, `claims/`, or `knowledge/` writes; the
  `factory_summary` is a per-run sandbox artifact written to the chosen
  `--output-dir`.
- The full Nuclear sprint (50-100 candidates) is TASK-0507.
