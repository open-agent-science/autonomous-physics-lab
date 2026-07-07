"""Invariants for the decision-autonomy policy matrix (TASK-0952, v0 dry-run)."""

import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy" / "decision-autonomy.yaml"
TEMPLATE_PATH = REPO_ROOT / "decisions" / "DECISION-TEMPLATE.yaml"

REQUIRED_NON_REDUCIBLE = {
    "claim_support_status_change",
    "knowledge_endorsement",
    "external_publication",
    "data_rights_decision",
    "external_communication",
    "prediction_freeze",
    "repo_settings_change",
    "git_history_rewrite",
    "autonomy_policy_change",
}

# Fixed calibration set: Decision Day #2 (2026-07-06) replayed against the
# matrix. See docs/reviews/decision-autonomy-dry-run-plan.md.
RETRO_DECISIONS = [
    ("D2-1-frb-conditional-go", "source_readiness_go", "class_1_lazy_consensus"),
    ("D2-2-thermoml-rights", "data_rights_decision", "class_2_maintainer_only"),
    ("D2-3-atomic-hold-ratify", "campaign_hold_monitor", "class_1_lazy_consensus"),
    ("D2-4-muon-park", "claim_role_classification", "class_1_lazy_consensus"),
    ("D2-5-task0305-manifest-go", "source_readiness_go", "class_1_lazy_consensus"),
    ("D2-6-board-hygiene", "board_hygiene", "class_0_auto"),
    ("D2-7-proposal-adjudication", "proposal_adjudication", "class_0_auto"),
    ("D2-8-next-external-artifact", "external_publication", "class_2_maintainer_only"),
]


def load_policy():
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def classify(policy, decision_type):
    """Classify a decision type; unknown types are default-deny (class 2)."""
    entry = policy["decision_types"].get(decision_type)
    if entry is None:
        return policy["unknown_decision_type_default"]
    return entry["class"]


def test_policy_file_exists_and_parses():
    policy = load_policy()
    assert policy["policy_id"] == "decision-autonomy-v0"
    assert policy["status"] == "dry_run"
    assert policy["self_modification"] == "maintainer_only"


def test_v0_nothing_can_auto_apply():
    policy = load_policy()
    for name, cls in policy["autonomy_classes"].items():
        assert cls["can_apply_now"] is False, f"{name} must not auto-apply in v0"


def test_three_classes_present():
    policy = load_policy()
    assert set(policy["autonomy_classes"]) == {
        "class_0_auto",
        "class_1_lazy_consensus",
        "class_2_maintainer_only",
    }


def test_non_reducible_list_complete():
    policy = load_policy()
    non_reducible = set(policy["autonomy_classes"]["class_2_maintainer_only"]["non_reducible"])
    missing = REQUIRED_NON_REDUCIBLE - non_reducible
    assert not missing, f"non_reducible list is missing: {sorted(missing)}"


def test_non_reducible_types_map_to_class_2():
    policy = load_policy()
    for decision_type in REQUIRED_NON_REDUCIBLE:
        assert classify(policy, decision_type) == "class_2_maintainer_only", decision_type


def test_every_decision_type_maps_to_known_class():
    policy = load_policy()
    known = set(policy["autonomy_classes"])
    for decision_type, entry in policy["decision_types"].items():
        assert entry["class"] in known, decision_type


def test_unknown_decision_type_is_default_deny():
    policy = load_policy()
    assert classify(policy, "brand-new-unmapped-type") == "class_2_maintainer_only"


def test_class_1_quorum_shape():
    policy = load_policy()
    quorum = policy["autonomy_classes"]["class_1_lazy_consensus"]["quorum"]
    assert quorum["min_votes"] >= 2
    assert quorum["separate_sessions_required"] is True
    assert quorum["devils_advocate_required"] is True
    assert quorum["advocate_blocker_forces_escalation"] is True


def test_retro_calibration_decision_day_2():
    policy = load_policy()
    for slug, decision_type, expected_class in RETRO_DECISIONS:
        assert classify(policy, decision_type) == expected_class, slug


def test_template_has_required_fields():
    template = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
    for field in (
        "decision_id",
        "decision_type",
        "autonomy_class",
        "reversibility",
        "external_exposure",
        "artifact_impact",
        "agent_quorum",
        "devils_advocate",
        "veto",
        "decision_record",
    ):
        assert field in template, field
    assert template["decision_record"]["status"] == "dry_run_only"
    for flag in template["artifact_impact"].values():
        assert flag is False


# --- CLI validator (scripts/apl_decision.py) ---

_spec = importlib.util.spec_from_file_location(
    "apl_decision", REPO_ROOT / "scripts" / "apl_decision.py"
)
apl_decision = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(apl_decision)


def _valid_class1_packet():
    return {
        "decision_id": "DEC-20260706-test",
        "decision_type": "campaign_hold_monitor",
        "autonomy_class": "class_1_lazy_consensus",
        "reversibility": "reversible",
        "external_exposure": "none",
        "artifact_impact": {
            "result_status_change": False,
            "claim_status_change": False,
            "prediction_change": False,
            "knowledge_change": False,
            "external_publication": False,
        },
        "recommended_action": "hold_campaign",
        "basis": ["docs/reviews/example.md"],
        "agent_quorum": {
            "director_agent": {
                "vote": "approve", "agent_id": "claude", "vendor": "anthropic",
                "agent_tool": "Claude Code", "model_version": "Fable 5",
                "session_id": "sess-a",
            },
            "critic_agent": {
                "vote": "approve", "agent_id": "codex", "vendor": "openai",
                "agent_tool": "Codex", "model_version": "GPT-5.5-pro",
                "session_id": "sess-b",
            },
            "cross_vendor": True,
        },
        "devils_advocate": {
            "alternative_considered": "continue scouting",
            "strongest_objection": "a new source may appear",
            "why_rejected": "scouting exhausted; contract triggers cover reactivation",
            "escalation_required": False,
        },
        "veto": {"window_hours": 48, "deadline_utc": None, "maintainer_vetoed": False},
        "decision_record": {"decided_by": "agent_quorum", "applied_by": "pending",
                            "status": "dry_run_only", "revert_of": None},
    }


def test_cli_valid_class1_packet_passes():
    policy = load_policy()
    assert apl_decision.validate_packet(_valid_class1_packet(), policy) == []


def test_cli_unknown_type_fails_default_deny():
    policy = load_policy()
    packet = _valid_class1_packet()
    packet["decision_type"] = "brand-new-unmapped-type"
    errors = apl_decision.validate_packet(packet, policy)
    assert any("not in the approved matrix" in e for e in errors)


def test_cli_artifact_impact_forces_class2():
    policy = load_policy()
    packet = _valid_class1_packet()
    packet["artifact_impact"]["claim_status_change"] = True
    errors = apl_decision.validate_packet(packet, policy)
    assert any("class_2_maintainer_only" in e for e in errors)


def test_cli_advocate_blocker_forces_escalation():
    policy = load_policy()
    packet = _valid_class1_packet()
    packet["devils_advocate"]["escalation_required"] = True
    errors = apl_decision.validate_packet(packet, policy)
    assert any("escalation to maintainer is mandatory" in e for e in errors)


def test_cli_same_session_quorum_rejected():
    policy = load_policy()
    packet = _valid_class1_packet()
    packet["agent_quorum"]["critic_agent"]["session_id"] = "sess-a"
    errors = apl_decision.validate_packet(packet, policy)
    assert any("separate sessions" in e for e in errors)


def test_cli_dry_run_forbids_agent_apply():
    policy = load_policy()
    packet = _valid_class1_packet()
    packet["decision_record"]["applied_by"] = "agent"
    errors = apl_decision.validate_packet(packet, policy)
    assert any("applied_by: agent is forbidden" in e for e in errors)


def test_cli_class2_requires_maintainer_decider():
    policy = load_policy()
    packet = _valid_class1_packet()
    packet["decision_type"] = "external_publication"
    packet["autonomy_class"] = "class_2_maintainer_only"
    errors = apl_decision.validate_packet(packet, policy)
    assert any("decided_by: maintainer" in e for e in errors)
