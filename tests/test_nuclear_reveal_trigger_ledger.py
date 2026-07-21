"""Regression contract for the TASK-1072 Nuclear trigger ledger."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "docs/reviews/nuclear/nuclear-post-registration-reveal-trigger-ledger.md"
PROTOCOL = REPO_ROOT / "docs/nuclear-prediction-reveal-protocol.md"
PROFILE = REPO_ROOT / "campaign_profiles/nuclear-mass-surface.yaml"


def test_nuclear_trigger_ledger_preserves_event_only_no_peek_contract():
    ledger = LEDGER.read_text(encoding="utf-8")

    for invariant in (
        "MONITOR_LEDGER_RATIFIED",
        "MONITOR_ONLY_NO_SCOUT",
        "2026-05-20",
        "SOURCE_PREDATES_REGISTRATION",
        "STOP_VALUE_EXPOSURE",
        "SOURCE_MANIFEST_DECISION_PENDING",
        "target-matching/no-peek task",
    ):
        assert invariant in ledger, f"ledger missing invariant: {invariant!r}"


def test_nuclear_protocol_and_profile_reject_recurring_source_scouts():
    protocol = PROTOCOL.read_text(encoding="utf-8")
    profile = PROFILE.read_text(encoding="utf-8")

    assert "nuclear-post-registration-reveal-trigger-ledger.md" in protocol
    assert "MONITOR_ONLY_NO_SCOUT" in protocol
    assert "Cadence: none. Monitoring is event-trigger-only." in protocol
    assert "Default cadence: monthly" not in protocol
    assert "monthly availability check" not in protocol

    assert "lifecycle_stage: monitor_only" in profile
    assert "activity_status: active_monitor" in profile
    assert "recommended_parallel_agents: 0" in profile
    assert "nuclear-post-registration-reveal-trigger-ledger.md" in profile
