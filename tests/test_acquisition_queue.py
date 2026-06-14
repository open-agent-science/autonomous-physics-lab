from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from physics_lab.registry.acquisition_queue import (
    acquisition_queue_errors,
    load_acquisition_queue,
    render_acquisition_queue_report,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = REPO_ROOT / "data" / "acquisition_queue.yaml"


def test_committed_acquisition_queue_is_valid_metadata_only() -> None:
    payload = load_acquisition_queue(QUEUE_PATH)

    assert acquisition_queue_errors(payload) == ()
    assert payload["policy"]["mode"] == "report_only_no_fetch"
    for field in (
        "live_fetch_allowed",
        "secrets_read_allowed",
        "local_artifacts_read_allowed",
        "benchmark_input_allowed",
        "value_bearing_rows_allowed",
        "artifact_bytes_allowed",
    ):
        assert payload["policy"][field] is False
    assert {entry["access_class"] for entry in payload["entries"]} >= {
        "key_gated",
        "manual_artifact",
    }


def test_acquisition_queue_report_groups_actions_without_fetching() -> None:
    payload = load_acquisition_queue(QUEUE_PATH)

    report = render_acquisition_queue_report(payload, queue_path=Path("data/acquisition_queue.yaml"))

    assert "Acquisition queue dry-run report" in report
    assert "Ready for maintainer action:" in report
    assert "Blocked or waiting:" in report
    assert "vossmeyer-1994-jpc-cds-absorption" in report
    assert "materials-project-md0002-narrowed" in report
    assert "it did not fetch sources" in report


def test_acquisition_queue_rejects_secret_values_and_machine_local_paths() -> None:
    payload = {
        "policy": {
            "mode": "report_only_no_fetch",
            "live_fetch_allowed": False,
            "secrets_read_allowed": False,
            "local_artifacts_read_allowed": False,
            "benchmark_input_allowed": False,
            "value_bearing_rows_allowed": False,
            "artifact_bytes_allowed": False,
        },
        "entries": [
            {
                "entry_id": "BAD-001",
                "source_id": "bad-source",
                "title": "Bad source",
                "campaign_id": "bad-campaign",
                "domain": "bad_domain",
                "status": "ready_for_maintainer_action",
                "access_class": "manual_artifact",
                "blocker_type": "T1_access",
                "source_locator": "https://example.invalid/source",
                "license_readiness": "unknown",
                "checksum_policy": "none",
                "downstream_task": "TASK-9999",
                "maintainer_action": "Do not use.",
                "local_artifact_expectation": "/Users/example/private.pdf",
                "agent_local_work_allowed": "none",
                "forbidden_actions": [],
                "evidence": [],
                "secret_value": "do-not-store",
            }
        ],
    }

    errors = acquisition_queue_errors(payload)

    assert any("secret_value" in error for error in errors)
    assert any("machine-local path" in error for error in errors)


def test_acquisition_queue_cli_report_is_read_only() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_acquisition_queue.py", "report"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Fetches: disabled" in result.stdout
    assert "Secrets: names may be listed; values are never read" in result.stdout
    assert result.stderr == ""


def test_acquisition_queue_cli_validate_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_acquisition_queue.py", "validate"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "Acquisition queue validation: PASS"
    assert result.stderr == ""
