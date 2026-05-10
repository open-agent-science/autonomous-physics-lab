from __future__ import annotations

import copy
import shutil
from pathlib import Path

import yaml

from physics_lab.registry.golden_results import (
    material_result_hash,
)
from physics_lab.registry.repository import _strict_golden_result_issues
from physics_lab.registry.results import load_result


def _copy_flagship_result(root: Path, tmp_path: Path) -> Path:
    source = root / "results" / "EXP-0001" / "RUN-0003" / "result.yaml"
    target = tmp_path / "results" / "EXP-0001" / "RUN-0003" / "result.yaml"
    target.parent.mkdir(parents=True)
    shutil.copyfile(source, target)
    return target


def _write_manifest(root: Path, *, material_hash: str) -> None:
    manifest = root / "results" / "golden-results.yaml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        yaml.safe_dump(
            {
                "golden_results": [
                    {
                        "result_path": "results/EXP-0001/RUN-0003/result.yaml",
                        "result_id": "RESULT-0004",
                        "policy": "material_fields_v1",
                        "material_hash_sha256": material_hash,
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_material_result_hash_ignores_metadata_only_fields() -> None:
    root = Path(__file__).resolve().parent.parent
    payload = load_result(root / "results" / "EXP-0001" / "RUN-0003" / "result.yaml")
    changed = copy.deepcopy(payload)
    changed["generated_at"] = "2099-01-01T00:00:00+00:00"
    changed["git_commit"] = "metadata-only"
    changed["command"] = "python3 -m physics_lab.cli run replayed"
    changed["artifacts"]["report"] = "/tmp/replay/report.md"
    changed["input_file_hashes"]["config"]["path"] = "/tmp/replay/inputs/config.yaml"

    assert material_result_hash(changed) == material_result_hash(payload)


def test_material_result_hash_detects_scientific_result_drift() -> None:
    root = Path(__file__).resolve().parent.parent
    payload = load_result(root / "results" / "EXP-0001" / "RUN-0003" / "result.yaml")
    changed = copy.deepcopy(payload)
    changed["best_model_id"] = "model_drift"

    assert material_result_hash(changed) != material_result_hash(payload)


def test_strict_golden_result_policy_reports_material_drift(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parent.parent
    result_path = _copy_flagship_result(root, tmp_path)
    payload = load_result(result_path)
    _write_manifest(tmp_path, material_hash=material_result_hash(payload))

    assert _strict_golden_result_issues(tmp_path) == []

    payload["best_verdict"] = "INVALID"
    result_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    issues = _strict_golden_result_issues(tmp_path)

    assert len(issues) == 1
    assert issues[0].code == "golden_result_material_drift"
