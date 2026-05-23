from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_ci_runner_status.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("apl_ci_runner_status", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_status_payload_documents_fallback_labels() -> None:
    module = _load_module()
    payload = module.build_runner_status_payload()

    assert payload["repository_variable_values"]["self_hosted"] == json.dumps(
        module.SELF_HOSTED_LABELS
    )
    assert payload["repository_variable_values"]["github_hosted"] == json.dumps(
        module.GITHUB_HOSTED_LABELS
    )
    assert "APL_PR_RUNNER_LABELS" in payload["runner_variables"]
    assert "gh run list --workflow CI --limit 10" in payload["queue_visibility_commands"]
    assert "./svc.sh status" in payload["vps_health_commands"]
    assert "5 minutes" in payload["fallback_decision_rule"]


def test_runner_status_markdown_is_copy_paste_friendly() -> None:
    module = _load_module()
    markdown = module.render_markdown(
        module.build_runner_status_payload(include_ssh=True)
    )

    assert "# APL CI Runner Status" in markdown
    assert "`APL_MAIN_RUNNER_LABELS`" in markdown
    assert "`[\"ubuntu-latest\"]`" in markdown
    assert "`ssh root@<runner-host>`" in markdown
    assert "Fallback Decision Rule" in markdown


def test_runner_status_cli_json() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/apl_ci_runner_status.py", "--json"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["repository_variable_values"]["github_hosted"] == (
        "[\"ubuntu-latest\"]"
    )
    assert "gh pr checks <pr-number>" in payload["queue_visibility_commands"]
