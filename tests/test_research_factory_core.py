"""Tests for the campaign-agnostic Research Factory core (TASK-0506)."""

from __future__ import annotations

import pytest
import yaml

from physics_lab.factories.core import (
    Candidate,
    FactoryRun,
    FactorySpec,
    get_adapter,
    run_factory,
    write_factory_summary,
)
from physics_lab.registry.validation import validate_document


def _spec(cap: int = 10) -> FactorySpec:
    return FactorySpec.from_config(
        {
            "factory_id": "demo-factory",
            "campaign_id": "demo-campaign",
            "adapter_id": "demo_adapter",
            "adapter_version": "0.1",
            "task_id": "TASK-0506",
            "dataset": {
                "snapshot_ref": "data/demo.yaml",
                "retrieval_policy": "no_live_fetch",
                "checksum_policy": "manifest",
            },
            "baseline": {"baseline_id": "demo-baseline", "baseline_type": "frozen"},
            "families": ["demo_family"],
            "controls": ["null_baseline"],
            "candidate_cap": cap,
            "limitations": ["Synthetic core test; no promotion."],
            "reproducibility": {
                "code_reference": "tests/test_research_factory_core.py",
                "command": "pytest",
                "run_date": "2026-06-01",
            },
        }
    )


class _FakeAdapter:
    adapter_id = "demo_adapter"
    adapter_version = "0.1"

    def __init__(self, candidates: tuple[Candidate, ...]) -> None:
        self._candidates = candidates

    def build_run(self, spec: FactorySpec) -> FactoryRun:
        return FactoryRun(
            dataset={
                "snapshot_ref": spec.dataset["snapshot_ref"],
                "retrieval_policy": "no_live_fetch",
                "checksum_policy": "manifest",
            },
            baseline={"baseline_id": "demo-baseline", "baseline_type": "frozen"},
            controls=({"name": "null_baseline", "outcome": "applied"},),
            candidates=self._candidates,
        )


def _candidate(cid: str, state: str, verdict: str) -> Candidate:
    return Candidate(
        candidate_id=cid,
        family="demo_family",
        complexity=1.0,
        leakage_status="CHECKED_CLEAN",
        candidate_state=state,
        route_verdict=verdict,
    )


def test_from_config_requires_core_keys() -> None:
    with pytest.raises(ValueError, match="missing required keys"):
        FactorySpec.from_config({"factory_id": "x"})


def test_run_factory_emits_schema_valid_summary_and_counts() -> None:
    candidates = (
        _candidate("CAND-0001", "SHORTLISTED", "SHORTLIST_CANDIDATE"),
        _candidate("CAND-0002", "REJECTED_BY_CONTROL", "REJECTED_BY_CONTROL"),
        _candidate("CAND-0003", "PREFLIGHT_REJECTED", "DATA_QUALITY_BLOCKED"),
    )
    summary = run_factory(_spec(), _FakeAdapter(candidates))
    counts = summary["candidate_counts"]
    assert counts == {
        "generated": 3,
        "preflight_rejected": 1,
        "executed": 2,
        "shortlisted": 1,
        "rejected_by_control": 1,
    }
    assert summary["route_verdict_summary"]["SHORTLIST_CANDIDATE"] == 1
    # run_factory already validates, but assert independently too.
    assert validate_document(summary, "factory_summary", "x/factory_summary.yaml") is summary


def test_run_factory_enforces_candidate_cap() -> None:
    candidates = tuple(
        _candidate(f"CAND-{i:04d}", "EXECUTED", "NEGATIVE_RESULT") for i in range(1, 4)
    )
    with pytest.raises(ValueError, match="cap exceeded"):
        run_factory(_spec(cap=2), _FakeAdapter(candidates))


def test_run_factory_rejects_unknown_route_verdict() -> None:
    bad = (_candidate("CAND-0001", "EXECUTED", "DISCOVERY"),)
    with pytest.raises(ValueError, match="route verdict"):
        run_factory(_spec(), _FakeAdapter(bad))


def test_run_factory_rejects_adapter_id_mismatch() -> None:
    spec = _spec()
    adapter = _FakeAdapter(())
    adapter.adapter_id = "other_adapter"
    with pytest.raises(ValueError, match="mismatch"):
        run_factory(spec, adapter)


def test_get_adapter_unknown_raises() -> None:
    with pytest.raises(ValueError, match="No research-factory adapter"):
        get_adapter("does_not_exist")


def test_write_factory_summary_roundtrips(tmp_path) -> None:
    summary = run_factory(_spec(), _FakeAdapter((_candidate("CAND-0001", "EXECUTED", "NEGATIVE_RESULT"),)))
    out = write_factory_summary(summary, tmp_path / "run")
    assert out.exists()
    assert yaml.safe_load(out.read_text(encoding="utf-8"))["factory_id"] == "demo-factory"
