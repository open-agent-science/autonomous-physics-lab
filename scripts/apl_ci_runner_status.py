"""Print APL self-hosted CI runner fallback and queue diagnostic commands."""

from __future__ import annotations

import argparse
import json
from typing import Any


SELF_HOSTED_LABELS = ["self-hosted", "linux", "x64"]
GITHUB_HOSTED_LABELS = ["ubuntu-latest"]
RUNNER_VARIABLES = ("APL_PR_RUNNER_LABELS", "APL_MAIN_RUNNER_LABELS")


def build_runner_status_payload(*, include_ssh: bool = False) -> dict[str, Any]:
    """Return a stable maintainer runbook payload for CI runner triage."""

    github_commands = [
        "gh run list --workflow CI --limit 10",
        "gh run view <run-id> --jobs",
        "gh run view <run-id> --log-failed",
        "gh pr checks <pr-number>",
    ]
    repository_variable_values = {
        "self_hosted": json.dumps(SELF_HOSTED_LABELS),
        "github_hosted": json.dumps(GITHUB_HOSTED_LABELS),
    }
    vps_commands = [
        "cd /opt/actions-runner",
        "./svc.sh status",
        "systemctl status 'actions.runner.*'",
        "journalctl -u 'actions.runner.*' -n 120 --no-pager",
        "ss -tlnp | grep ':22'",
        "systemctl status ssh",
    ]
    if include_ssh:
        vps_commands.insert(0, "ssh root@<runner-host>")

    return {
        "runner_variables": list(RUNNER_VARIABLES),
        "repository_variable_values": repository_variable_values,
        "queue_visibility_commands": github_commands,
        "vps_health_commands": vps_commands,
        "fallback_decision_rule": (
            "If a PR Python job waits for a self-hosted runner for more than "
            "5 minutes and the VPS service cannot be confirmed healthy, set "
            "APL_PR_RUNNER_LABELS to [\"ubuntu-latest\"], rerun the failed or "
            "queued job, and restore self-hosted labels after the runner is healthy."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render the runbook payload as copy-paste friendly Markdown."""

    lines = [
        "# APL CI Runner Status",
        "",
        "## Runner Variables",
        "",
    ]
    for variable in payload["runner_variables"]:
        lines.append(f"- `{variable}`")
    lines.extend(
        [
            "",
            "## Label Values",
            "",
            f"- Self-hosted: `{payload['repository_variable_values']['self_hosted']}`",
            f"- GitHub-hosted fallback: `{payload['repository_variable_values']['github_hosted']}`",
            "",
            "## Queue Visibility",
            "",
        ]
    )
    lines.extend(f"- `{command}`" for command in payload["queue_visibility_commands"])
    lines.extend(["", "## VPS Health Checks", ""])
    lines.extend(f"- `{command}`" for command in payload["vps_health_commands"])
    lines.extend(
        [
            "",
            "## Fallback Decision Rule",
            "",
            payload["fallback_decision_rule"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable runner triage guidance.",
    )
    parser.add_argument(
        "--include-ssh",
        action="store_true",
        help="Include an SSH placeholder in the VPS command list.",
    )
    args = parser.parse_args(argv)

    payload = build_runner_status_payload(include_ssh=args.include_ssh)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
