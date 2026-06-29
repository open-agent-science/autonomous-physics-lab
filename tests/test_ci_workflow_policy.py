from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def test_main_push_ci_runs_are_not_cancelled_by_board_sync_pushes() -> None:
    workflow = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))

    concurrency = workflow["concurrency"]
    group = str(concurrency["group"])
    cancel_in_progress = str(concurrency["cancel-in-progress"])

    assert "github.event.pull_request.number || github.sha" in group
    assert "github.ref" not in group
    assert cancel_in_progress == "${{ github.event_name == 'pull_request' }}"
