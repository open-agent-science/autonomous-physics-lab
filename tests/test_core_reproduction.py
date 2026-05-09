from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_core_reproduction_module():
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "scripts" / "reproduce_core_results.py"
    spec = importlib.util.spec_from_file_location("reproduce_core_results", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_default_core_reproduction_scope_excludes_guarded_g2_stress_test() -> None:
    module = _load_core_reproduction_module()

    config_paths = {replay.config_path for replay in module.CORE_REPLAYS}
    result_ids = {replay.result_id for replay in module.CORE_REPLAYS}

    assert "examples/g2_formula_search.yaml" not in config_paths
    assert "RESULT-0012" not in result_ids
    assert {
        "RESULT-0004",
        "RESULT-0005",
        "RESULT-0006",
        "RESULT-0007",
        "RESULT-0009",
        "RESULT-0010",
        "RESULT-0011",
    } == result_ids


def test_core_reproduction_list_mode_reports_scope_without_running() -> None:
    module = _load_core_reproduction_module()

    exit_code = module.main(["--list", "--only", "koide-charged-lepton"])

    assert exit_code == 0


def test_core_reproduction_summary_names_skipped_stress_test(tmp_path) -> None:
    module = _load_core_reproduction_module()
    replay = module.CORE_REPLAYS[0]
    report = module.ReplayReport(
        replay=replay,
        command=("python3", "-m", "physics_lab.cli", "run", replay.config_path),
        result_path=tmp_path / replay.experiment_id / replay.run_id / "result.yaml",
        status="PASS",
        verdict=replay.expected_verdicts[0],
        message="ok",
    )

    summary = module.render_summary([report], tmp_path)

    assert "APL Core Reproduction Summary" in summary
    assert "Muon g-2 formula search is intentionally excluded" in summary
    assert "guarded empirical formula-search stress test" in summary


def test_core_reproduction_accepts_flat_and_nested_artifact_layouts(tmp_path) -> None:
    module = _load_core_reproduction_module()
    replay = module.CORE_REPLAYS[0]
    flat_dir = tmp_path / "flat"
    nested_dir = tmp_path / "nested"
    flat_dir.mkdir()
    nested_path = nested_dir / replay.experiment_id / replay.run_id / "result.yaml"
    nested_path.parent.mkdir(parents=True)
    flat_path = flat_dir / "result.yaml"
    flat_path.write_text("result_id: RESULT-0004\nbest_verdict: VALID_IN_RANGE\n", encoding="utf-8")
    nested_path.write_text("result_id: RESULT-0004\nbest_verdict: VALID_IN_RANGE\n", encoding="utf-8")

    assert module.resolve_result_path(replay, flat_dir) == flat_path
    assert module.resolve_result_path(replay, nested_dir) == nested_path
