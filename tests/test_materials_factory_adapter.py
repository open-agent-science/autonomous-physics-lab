"""Second-adapter proof for the campaign-agnostic Research Factory core (TASK-1060).

The materials formation-energy adapter must (a) plug into the shared core through
the same ``CampaignAdapter`` interface as nuclear, (b) produce a schema-valid
``factory_summary`` for a bounded, reproducible run, (c) reproduce the validated
TASK-0626 smoke-sprint science exactly, and (d) leave the core campaign-agnostic.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from physics_lab.factories import get_adapter, run_factory
from physics_lab.factories.core import FactorySpec
from physics_lab.factories.materials import MaterialsFormationEnergyFactoryAdapter

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = (
    REPO_ROOT / "examples" / "factories" / "materials_md0001_formation_energy_smoke.yaml"
)


def _run() -> dict:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    spec = FactorySpec.from_config(config)
    return run_factory(spec, get_adapter(spec.adapter_id))


def test_materials_adapter_is_registered_on_import() -> None:
    adapter = get_adapter("materials_formation_energy_factory")
    assert isinstance(adapter, MaterialsFormationEnergyFactoryAdapter)
    assert adapter.adapter_version == "0.1"


def test_materials_adapter_produces_schema_valid_bounded_run() -> None:
    # run_factory validates the summary against the factory_summary schema and
    # enforces the candidate cap before returning, so a returned summary is valid.
    summary = _run()
    assert summary["adapter_id"] == "materials_formation_energy_factory"
    assert summary["campaign_id"] == "materials-md0001-formation-energy"
    assert summary["candidate_counts"]["generated"] == 4
    assert summary["candidate_counts"]["generated"] <= summary["candidate_cap"]
    assert {c["name"] for c in summary["controls"]} == {
        "label_shuffle_control",
        "cation_group_shuffle_control",
        "matched_random_formula_family_control",
    }
    assert summary["campaign_specific"]["target_axis"] == "formation_energy_per_atom"
    assert summary["campaign_specific"]["excluded_axis"] == "band_gap"
    assert summary["campaign_specific"]["split_counts"] == {
        "train": 119,
        "validation": 17,
        "holdout": 33,
    }


def test_materials_adapter_run_is_deterministic() -> None:
    # Every candidate lane is a valid core route verdict; the frozen MD-0001 slice
    # gives a stable, diagnostic-only NEGATIVE_RESULT slate.
    summary = _run()
    holdout = {
        c["family"]: c["metrics"]["holdout_mae_improvement"]
        for c in summary["candidates"]
    }
    assert holdout == {
        "cation_group_residual_offsets": 0.0,
        "formula_family_residual_offsets": -0.067957,
        "oxygen_stoichiometry_residual_offsets": -0.002585,
        "formula_family_x_cation_group_offsets": -0.12619,
    }
    assert summary["route_verdict_summary"] == {"NEGATIVE_RESULT": 4}


def test_materials_adapter_matches_smoke_sprint_science() -> None:
    # Faithfulness: the adapter reproduces the validated TASK-0626 smoke sprint
    # per-lane holdout improvements exactly, so routing through the shared core
    # did not change the materials science.
    from scripts.run_materials_md0001_formation_energy_factory_smoke import (
        run_materials_factory_smoke_sprint,
    )

    smoke = run_materials_factory_smoke_sprint()
    smoke_holdout = {
        lid: lane["improvement_vs_baseline_mae"]["holdout"]
        for lid, lane in smoke["candidates"].items()
    }
    summary = _run()
    adapter_holdout = {
        c["family"]: c["metrics"]["holdout_mae_improvement"]
        for c in summary["candidates"]
    }
    assert adapter_holdout == smoke_holdout


def test_core_stays_campaign_agnostic() -> None:
    # The shared core must not import campaign science; adapters own it. Docstring
    # pointers to example adapters are fine, so this checks import statements and
    # campaign-specific science tokens rather than any prose mention.
    core_src = (REPO_ROOT / "physics_lab" / "factories" / "core.py").read_text(
        encoding="utf-8"
    )
    import_lines = [
        line for line in core_src.splitlines() if line.strip().startswith(("import ", "from "))
    ]
    for line in import_lines:
        assert "physics_lab.engines" not in line
        assert "physics_lab.factories.nuclear" not in line
        assert "physics_lab.factories.materials" not in line
    for science_token in ("formation_energy", "cation_group", "shell_distance", "MaterialsRow"):
        assert science_token not in core_src
