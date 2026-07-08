from __future__ import annotations

import csv
import hashlib
import importlib.util
import math
from pathlib import Path

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_frb_catalog1_pre_t_exposure_surface.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("frb_task0963", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path) -> None:
    fieldnames = [
        "tns_name",
        "repeater_name",
        "ra",
        "dec",
        "mjd_inf",
        "mjd_400",
        "excluded_flag",
        "catalog1_flag",
        "exp_up",
        "exp_low",
    ]
    rows = [
        {
            "tns_name": "FRB20190101A",
            "repeater_name": "LATE_LABEL_SHOULD_NOT_APPEAR",
            "ra": "0.0",
            "dec": "0.0",
            "mjd_inf": "58484.0",
            "mjd_400": "",
            "excluded_flag": "0",
            "catalog1_flag": "1",
            "exp_up": "999999",
            "exp_low": "999999",
        },
        {
            "tns_name": "FRB20200101A",
            "repeater_name": "",
            "ra": "0.0",
            "dec": "0.0",
            "mjd_inf": "58849.0",
            "mjd_400": "",
            "excluded_flag": "0",
            "catalog1_flag": "1",
            "exp_up": "1",
            "exp_low": "1",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_fixture_filters_pre_t_sources_and_avoids_labels(tmp_path, monkeypatch) -> None:
    module = _load_module()
    csv_path = tmp_path / "catalog.csv"
    upper_npz = tmp_path / "upper.npz"
    lower_npz = tmp_path / "lower.npz"
    output = tmp_path / "fixture.yaml"
    _write_csv(csv_path)

    upper = np.zeros(12, dtype=np.float64)
    lower = np.zeros(12, dtype=np.float64)
    pixel = int(module.healpix_ring_ang2pix(1, np.array([0.0]), np.array([0.0]))[0])
    assert pixel == 4
    upper[pixel] = 9.0
    lower[pixel] = 18.0
    np.savez_compressed(upper_npz, exposure=upper)
    np.savez_compressed(lower_npz, exposure=lower)

    monkeypatch.setattr(module, "NSIDE", 1)
    monkeypatch.setattr(module, "CATALOG_EXPECTED_BYTES", csv_path.stat().st_size)
    monkeypatch.setattr(module, "CATALOG_EXPECTED_SHA256", _sha256(csv_path))
    monkeypatch.setattr(module, "UPPER_EXPECTED_BYTES", upper_npz.stat().st_size)
    monkeypatch.setattr(module, "UPPER_EXPECTED_SHA256", _sha256(upper_npz))
    monkeypatch.setattr(module, "LOWER_EXPECTED_BYTES", lower_npz.stat().st_size)
    monkeypatch.setattr(module, "LOWER_EXPECTED_SHA256", _sha256(lower_npz))

    fixture = module.build_fixture(
        csv_path=csv_path,
        upper_npz=upper_npz,
        lower_npz=lower_npz,
        generated_at_utc="2026-07-08T00:00:00Z",
        output_path=output,
    )

    assert fixture["feature_contract"]["label_contact"] is False
    assert fixture["aggregate_counts"]["pre_t_feature_rows"] == 1
    assert fixture["aggregate_counts"]["nonzero_total_exposure_rows"] == 1
    assert "LATE_LABEL_SHOULD_NOT_APPEAR" not in yaml.safe_dump(fixture)
    feature = fixture["features"][0]
    assert feature["source_id"] == "FRB20190101A"
    assert feature["E_upper_hours"] == 0.01
    assert feature["E_lower_hours"] == 0.02
    assert feature["score_pre_t"] == round(math.log1p(0.03), 12)
