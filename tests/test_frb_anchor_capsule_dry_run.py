"""Guards for the TASK-0994 FRB anchor-capsule dry-run helper."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.package_frb_prediction_anchor_dry_run import (
    PACKAGE_FILES,
    STAGED_PRED_MEMBER_PATH,
    build_capsule,
)

ROOT = Path(__file__).resolve().parents[1]


def test_frb_anchor_dry_run_is_historical_after_go_register(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="TASK-0994 dry-run capsule is retired"):
        build_capsule(ROOT, tmp_path / "capsule")


def test_frb_anchor_dry_run_allowlist_remains_the_preapproval_eleven_member_contract() -> None:
    historical_member_count = len(PACKAGE_FILES) + 1  # plus generated staged PRED draft.

    assert historical_member_count == 11
    assert STAGED_PRED_MEMBER_PATH == (
        "staged_payloads/prediction_registry/radio_transients/PRED-0001.draft.yaml"
    )
    assert PACKAGE_FILES[0].path == "decisions/DEC-20260709-frb-prediction-freeze-stub.yaml"
    assert PACKAGE_FILES[0].bytes == 2_181
    assert PACKAGE_FILES[0].sha256 == (
        "2554cc15eda2e12ec08dcc5ba44e240d135fd915c8f8ebbdb67c7c2c6ea725b5"
    )


def test_frb_anchor_dry_run_note_records_historical_status() -> None:
    note = (ROOT / "docs/reviews/frb-prediction-freeze-anchor-dry-run.md").read_text(
        encoding="utf-8"
    )

    assert "Dry-run archive bytes: `612208`" in note
    assert "6657398e88e080862d9195d4a18f891a904716df2901654310b3dfc27d3a8165" in note
    assert "Post-approval note, 2026-07-10" in note
    assert "use the `TASK-0996` registration note" in note
