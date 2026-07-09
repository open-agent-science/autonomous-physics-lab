from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_review_queue.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("apl_review_queue", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _check(name: str, *, status: str = "COMPLETED", conclusion: str = "SUCCESS") -> dict:
    return {"name": name, "status": status, "conclusion": conclusion}


def test_review_queue_ignores_superseded_cancelled_check_rows() -> None:
    module = _load_module()
    checks = [
        {
            "name": "Python fast tests",
            "status": "COMPLETED",
            "conclusion": "CANCELLED",
            "startedAt": "2026-07-09T17:04:51Z",
            "completedAt": "2026-07-09T17:09:03Z",
        },
        {
            "name": "Python fast tests",
            "status": "COMPLETED",
            "conclusion": "SUCCESS",
            "startedAt": "2026-07-09T17:09:12Z",
            "completedAt": "2026-07-09T17:16:23Z",
        },
    ]

    summary = module.summarize_checks(checks)

    assert summary.status == "pass"
    assert summary.failing == ()


def test_review_queue_classifies_actionable_prs_without_waiting() -> None:
    module = _load_module()
    prs = [
        {
            "number": 10,
            "title": "TASK-0100: ready",
            "isDraft": False,
            "mergeStateStatus": "CLEAN",
            "reviewDecision": "",
            "statusCheckRollup": [_check("Python fast tests"), _check("Classify")],
            "url": "https://example.test/10",
        },
        {
            "number": 11,
            "title": "TASK-0101: behind",
            "isDraft": False,
            "mergeStateStatus": "BEHIND",
            "reviewDecision": "",
            "statusCheckRollup": [_check("Python fast tests"), _check("Classify")],
            "url": "https://example.test/11",
        },
        {
            "number": 12,
            "title": "TASK-0102: waiting",
            "isDraft": False,
            "mergeStateStatus": "BLOCKED",
            "reviewDecision": "",
            "statusCheckRollup": [_check("Python fast tests", status="IN_PROGRESS", conclusion="")],
            "url": "https://example.test/12",
        },
        {
            "number": 13,
            "title": "chore(deps): bump package",
            "isDraft": False,
            "mergeStateStatus": "CLEAN",
            "reviewDecision": "",
            "statusCheckRollup": [_check("Python fast tests")],
            "url": "https://example.test/13",
        },
        {
            "number": 14,
            "title": "TASK-0104: draft",
            "isDraft": True,
            "mergeStateStatus": "BLOCKED",
            "reviewDecision": "",
            "statusCheckRollup": [_check("Python fast tests")],
            "url": "https://example.test/14",
        },
    ]

    entries = module.classify_queue(prs, merge_ok_prs={10, 11})
    by_number = {entry.number: entry for entry in entries}

    assert by_number[10].decision == "MERGE_NOW"
    assert by_number[11].decision == "READY_AFTER_UPDATE"
    assert by_number[12].decision == "WAIT_CI"
    assert "do not foreground-watch" in by_number[12].action
    assert by_number[13].decision == "RISKY_DEPENDABOT"
    assert by_number[14].decision == "DRAFT"
    assert [entry.number for entry in entries][:2] == [10, 11]


def test_review_queue_requires_review_marker_before_merge_now() -> None:
    module = _load_module()
    pr = {
        "number": 20,
        "title": "TASK-0200: green but not reviewed",
        "isDraft": False,
        "mergeStateStatus": "CLEAN",
        "reviewDecision": "",
        "statusCheckRollup": [_check("Python fast tests")],
        "url": "https://example.test/20",
    }

    entry = module.classify_pr(pr)

    assert entry.decision == "NEEDS_REVIEW"
    assert "MERGE_OK" in entry.reason
    assert "--merge-ok-pr" in entry.action


def test_review_queue_cli_reads_saved_json(tmp_path: Path) -> None:
    payload = [
        {
            "number": 30,
            "title": "TASK-0300: ready",
            "isDraft": False,
            "mergeStateStatus": "CLEAN",
            "reviewDecision": "",
            "statusCheckRollup": [_check("Python fast tests")],
            "url": "https://example.test/30",
        }
    ]
    input_path = tmp_path / "prs.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_review_queue.py",
            "--input-json",
            str(input_path),
            "--merge-ok-pr",
            "30",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "APL Review Queue Snapshot" in result.stdout
    assert "`MERGE_NOW`" in result.stdout
