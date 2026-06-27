from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from scripts.apl_task_occupancy import check_task_occupancy
from physics_lab.registry.subprocess_env import env_with_overrides
from physics_lab.registry.task_occupancy import classify_task_pr_occupancy


def test_task_pr_occupancy_uses_title_and_branch_not_body() -> None:
    # Occupancy is derived only from canonical implementation signals: a
    # `TASK-XXXX:` title or a `.../task-XXXX-<slug>` branch. A body-only mention
    # (PR #10 implements TASK-0001 via its branch but only names TASK-0617 in
    # the body) must not occupy the mentioned task.
    records = [
        {
            "number": 10,
            "state": "OPEN",
            "title": "Implementation",
            "body": "Primary task: TASK-0617",
            "headRefName": "agent/sviti/codex/task-0001-placeholder",
        },
        {
            "number": 11,
            "state": "OPEN",
            "title": "TASK-0618: title match",
            "body": "",
            "headRefName": "agent/sviti/codex/task-0618-title",
        },
        {
            "number": 12,
            "state": "MERGED",
            "title": "Follow-up",
            "body": "",
            "headRefName": "agent/sviti/codex/task-0619-merged",
        },
    ]

    results = classify_task_pr_occupancy(
        ("TASK-0617", "TASK-0618", "TASK-0619", "TASK-0620"),
        records,
    )

    by_id = {item.task_id: item for item in results}
    assert by_id["TASK-0617"].classification == "apparently_free"
    assert by_id["TASK-0618"].classification == "occupied"
    assert by_id["TASK-0618"].reasons == ("open PR #11",)
    assert by_id["TASK-0619"].classification == "merged_pending_closeout"
    assert by_id["TASK-0620"].classification == "apparently_free"


def test_task_pr_occupancy_open_pr_takes_precedence_over_merged() -> None:
    records = [
        {
            "number": 20,
            "state": "MERGED",
            "title": "TASK-0617: merged",
            "body": "",
            "headRefName": "agent/sviti/codex/task-0617-merged",
        },
        {
            "number": 21,
            "state": "OPEN",
            "title": "TASK-0617: open",
            "body": "",
            "headRefName": "agent/sviti/codex/task-0617-open",
        },
    ]

    result = classify_task_pr_occupancy(("TASK-0617",), records)[0]

    assert result.classification == "occupied"
    assert result.reasons == (
        "merged PR #20 pending local closeout",
        "open PR #21",
    )


def test_task_pr_occupancy_normalizes_requested_task_ids() -> None:
    records = [
        {
            "number": 30,
            "state": "OPEN",
            "title": "TASK-0617: lower-case request check",
            "body": "",
            "headRefName": "",
        },
    ]

    result = classify_task_pr_occupancy(("task-0617", ""), records)[0]

    assert result.task_id == "TASK-0617"
    assert result.classification == "occupied"
    assert result.reasons == ("open PR #30",)


def test_task_occupancy_check_is_advisory_on_proxy_blocker(tmp_path: Path) -> None:
    report = check_task_occupancy(
        tmp_path,
        ("TASK-0617",),
        env={"HTTPS_PROXY": "http://127.0.0.1:9"},
    )

    assert report.checked is False
    assert report.source == "local_registry_only"
    assert "--ignore-suspicious-proxy" in report.warnings[0]


def test_task_occupancy_cli_json_runs_with_proxy_advisory() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_task_occupancy.py",
            "--task",
            "TASK-0617",
            "--json",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
        env=env_with_overrides(
            HTTPS_PROXY="http://127.0.0.1:9",
            PATH=os.environ.get("PATH", ""),
        ),
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "ModuleNotFoundError" not in result.stderr
    payload = json.loads(result.stdout)
    assert payload["checked"] is False
    assert payload["source"] == "local_registry_only"
