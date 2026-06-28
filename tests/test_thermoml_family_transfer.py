"""TASK-0851 bounded ThermoML family-transfer tests."""

from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.thermoml_family_transfer import load_audit_fixture, run_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/thermophysical/thermoml_tb_audit_fixture.yaml"


def test_fixture_is_balanced_bounded_and_source_pinned() -> None:
    rows, payload = load_audit_fixture(FIXTURE)
    assert len(rows) == 40
    assert len({row["family"] for row in rows}) == 8
    assert payload["source"]["archive_sha256"] == (
        "231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2"
    )
    assert payload["source"]["archive_bytes_committed"] is False
    assert payload["rights"]["substantial_corpus_committed"] is False


def test_family_transfer_executes_all_declared_controls() -> None:
    transfer = run_fixture(FIXTURE)["transfer"]
    assert set(transfer["aggregate"]) == {
        "joback",
        "global_median",
        "molecular_weight_only",
        "nearest_homolog",
        "shuffled_group_counts",
        "within_family_constant",
    }
    assert len(transfer["per_family"]) == 8


def test_family_transfer_is_deterministic() -> None:
    assert json.dumps(run_fixture(FIXTURE), sort_keys=True) == json.dumps(
        run_fixture(FIXTURE), sort_keys=True
    )

