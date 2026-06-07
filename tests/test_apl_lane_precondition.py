"""Tests for scripts/apl_lane_precondition.py (TASK-0461)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_lane_precondition.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "apl_lane_precondition_under_test",
        SCRIPT_PATH,
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _index(tasks: list[dict[str, object]], conflicts: list[dict[str, object]] | None = None):
    return {"tasks": tasks, "path_conflicts": conflicts or []}


def test_infer_task_id_from_task_id_and_branch() -> None:
    module = _load_module()
    assert module.infer_task_id("TASK-0461") == "TASK-0461"
    assert module.infer_task_id("agent/roman/codex/task-0461-lane") == "TASK-0461"
    assert module.infer_task_id("feature/no-task") is None


def test_duplicate_task_owner_warns() -> None:
    module = _load_module()
    findings = module.analyze_lane(
        index=_index(
            [
                {
                    "task_id": "TASK-0461",
                    "status": "READY",
                    "lane": "support",
                    "artifact_surface": ["scripts/"],
                    "mapping_basis": "support",
                }
            ]
        ),
        task_id="TASK-0461",
        local_owners=(
            module.LocalOwner("branch", "agent/roman/codex/task-0461-old", "TASK-0461"),
        ),
        current_owner_name="agent/akutenyov/codex/task-0461-lane-collision-preflight",
    )
    assert any("also appears to own TASK-0461" in finding.message for finding in findings)


def test_same_lane_surface_warns() -> None:
    module = _load_module()
    findings = module.analyze_lane(
        index=_index(
            [
                {
                    "task_id": "TASK-0461",
                    "status": "READY",
                    "lane": "support",
                    "artifact_surface": ["scripts/"],
                    "mapping_basis": "support",
                },
                {
                    "task_id": "TASK-0462",
                    "status": "IN_PROGRESS",
                    "lane": "support",
                    "artifact_surface": ["scripts/"],
                    "mapping_basis": "support",
                },
            ]
        ),
        task_id="TASK-0461",
    )
    assert any("shares lane" in finding.message and "scripts/" in finding.message for finding in findings)


def test_blocked_lane_warns() -> None:
    module = _load_module()
    findings = module.analyze_lane(
        index=_index(
            [
                {
                    "task_id": "TASK-0461",
                    "status": "READY",
                    "lane": "support",
                    "artifact_surface": ["scripts/"],
                    "mapping_basis": "support",
                },
                {
                    "task_id": "TASK-0463",
                    "status": "BLOCKED",
                    "lane": "support",
                    "artifact_surface": ["docs/"],
                    "mapping_basis": "support",
                },
            ]
        ),
        task_id="TASK-0461",
    )
    assert any("blocked task TASK-0463" in finding.message for finding in findings)


def test_clean_lane_reports_ok() -> None:
    module = _load_module()
    findings = module.analyze_lane(
        index=_index(
            [
                {
                    "task_id": "TASK-0461",
                    "status": "READY",
                    "lane": "support",
                    "artifact_surface": ["scripts/"],
                    "mapping_basis": "support",
                },
                {
                    "task_id": "TASK-0644",
                    "status": "READY",
                    "lane": "materials-property-residuals",
                    "artifact_surface": ["data/"],
                    "mapping_basis": "domain",
                },
            ]
        ),
        task_id="TASK-0461",
    )
    assert findings == (module.LaneFinding("ok", "No likely lane collision found for TASK-0461."),)
