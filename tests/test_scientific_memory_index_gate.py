"""Publication gate for the scientific-memory review-tier index.

These tests are hermetic: they build tiny artifact trees in tmp_path and
assert renderer/gate behavior there. They intentionally do NOT assert that
the committed docs/scientific-memory-review-tiers.md is byte-identical to a
live render — that byte-sync check runs as
`scripts/apl_scientific_memory_index.py --check` in the nightly watchdog,
after the post-merge board sync has regenerated the index. Running it in the
PR lane would force every scientific PR to regenerate the shared index
in-branch and reintroduce the exact parallel-PR merge-conflict problem the
post-merge sync pattern exists to avoid.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from physics_lab.registry.scientific_memory_index import (
    collect_scientific_memory_artifacts,
    render_scientific_memory_index,
    write_scientific_memory_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "apl_scientific_memory_index",
    REPO_ROOT / "scripts" / "apl_scientific_memory_index.py",
)
index_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(index_cli)


def _write_result(
    root: Path,
    run: str,
    review_tier: str,
    validation_independence: str | None = None,
) -> None:
    payload: dict = {
        "result_id": f"RESULT-{run[-4:]}",
        "title": f"Fixture result {run}",
        "review_tier": review_tier,
        "best_verdict": "VALID_IN_RANGE",
    }
    if validation_independence is not None:
        payload["agent_proposal_evaluation"] = {
            "validation_record": {
                "validation_independence": validation_independence,
            }
        }
    target = root / "results" / "EXP-0001" / run / "result.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(payload), encoding="utf-8")


def _result_row(root: Path, result_id: str) -> str:
    rendered = render_scientific_memory_index(root)
    rows = [line for line in rendered.splitlines() if f"`{result_id}`" in line]
    assert len(rows) == 1, f"expected exactly one row for {result_id}"
    return rows[0]


def test_recorded_independence_is_rendered(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0001", "AGENT_VALIDATED", "independent")
    row = _result_row(tmp_path, "RESULT-0001")
    assert "| `independent` |" in row


def test_replayed_result_without_record_shows_not_recorded(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0002", "AGENT_VALIDATED")
    row = _result_row(tmp_path, "RESULT-0002")
    assert "| `not_recorded` |" in row


def test_maintainer_reviewed_without_record_shows_not_recorded(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0003", "MAINTAINER_REVIEWED")
    row = _result_row(tmp_path, "RESULT-0003")
    assert "| `not_recorded` |" in row


def test_unreplayed_result_shows_na_independence(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0004", "AGENT_PUBLISHED")
    row = _result_row(tmp_path, "RESULT-0004")
    assert "| `n/a` |" in row


def test_collector_exposes_independence_field(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0005", "AGENT_VALIDATED", "same_owner_different_account")
    artifacts = collect_scientific_memory_artifacts(tmp_path)
    assert [a.validation_independence for a in artifacts] == [
        "same_owner_different_account"
    ]


def test_index_header_documents_independence_axis(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0006", "AGENT_VALIDATED", "independent")
    rendered = render_scientific_memory_index(tmp_path)
    assert "| Class | Artifact | Status | Independence | Next action | Path |" in rendered
    assert "`Independence` is a separate axis from the tier" in rendered


def test_check_passes_when_index_in_sync(tmp_path: Path, capsys) -> None:
    _write_result(tmp_path, "RUN-0007", "AGENT_VALIDATED", "independent")
    write_scientific_memory_index(tmp_path)
    assert index_cli.main(["--root", str(tmp_path), "--check"]) == 0
    assert "IN SYNC" in capsys.readouterr().out


def test_check_fails_when_index_is_stale(tmp_path: Path, capsys) -> None:
    _write_result(tmp_path, "RUN-0008", "AGENT_VALIDATED", "independent")
    write_scientific_memory_index(tmp_path)
    # A canonical change after the last regen must flip --check to failing.
    _write_result(tmp_path, "RUN-0009", "AGENT_PUBLISHED")
    assert index_cli.main(["--root", str(tmp_path), "--check"]) == 1
    out = capsys.readouterr().out
    assert "STALE" in out
    assert "--write" in out


def test_check_fails_when_index_is_missing(tmp_path: Path) -> None:
    _write_result(tmp_path, "RUN-0010", "AGENT_VALIDATED", "independent")
    assert index_cli.main(["--root", str(tmp_path), "--check"]) == 1


def test_write_then_check_roundtrip_is_deterministic(tmp_path: Path) -> None:
    for run, tier, independence in (
        ("RUN-0011", "AGENT_VALIDATED", "independent"),
        ("RUN-0012", "AGENT_VALIDATED", "same_account_different_tool"),
        ("RUN-0013", "AGENT_PUBLISHED", None),
    ):
        _write_result(tmp_path, run, tier, independence)
    first = write_scientific_memory_index(tmp_path).read_text(encoding="utf-8")
    second = write_scientific_memory_index(tmp_path).read_text(encoding="utf-8")
    assert first == second
    assert index_cli.main(["--root", str(tmp_path), "--check"]) == 0
