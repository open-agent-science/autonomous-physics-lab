from __future__ import annotations

import json
from pathlib import Path
import subprocess
from unittest.mock import patch

from physics_lab.registry.github_readonly import (
    CANONICAL_GITHUB_REPOSITORY,
    GitHubReadOnlyClient,
)


class _FakeResponse:
    def __init__(self, payload: object, *, remaining: str = "59") -> None:
        self._payload = json.dumps(payload).encode("utf-8")
        self.headers = {
            "X-RateLimit-Remaining": remaining,
            "X-RateLimit-Reset": "1784100000",
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self, limit: int) -> bytes:
        return self._payload[:limit]


def _client(root: Path) -> GitHubReadOnlyClient:
    return GitHubReadOnlyClient(root, env={"PATH": ""}, gh_path="/custom/gh")


def test_public_json_caches_successful_response_for_one_client_run(
    tmp_path: Path,
) -> None:
    path = f"/repos/{CANONICAL_GITHUB_REPOSITORY}/pulls?state=open"
    response = _FakeResponse([{"number": 1}])

    with patch(
        "physics_lab.registry.github_readonly.urlopen",
        return_value=response,
    ) as request_mock:
        client = _client(tmp_path)
        first = client.public_json(path)
        second = client.public_json(path)

    assert first == second == [{"number": 1}]
    assert client.public_cache_size == 1
    request_mock.assert_called_once()


def test_public_cache_is_isolated_between_agent_process_clients(
    tmp_path: Path,
) -> None:
    path = f"/repos/{CANONICAL_GITHUB_REPOSITORY}/pulls?state=open"
    first_client = _client(tmp_path)
    second_client = _client(tmp_path)

    with patch(
        "physics_lab.registry.github_readonly.urlopen",
        side_effect=[_FakeResponse([]), _FakeResponse([])],
    ) as request_mock:
        assert first_client.public_json(path) == []
        assert first_client.public_json(path) == []
        assert second_client.public_json(path) == []

    assert request_mock.call_count == 2
    assert first_client.public_cache_size == 1
    assert second_client.public_cache_size == 1


def test_gh_command_keeps_windows_path_as_one_argument_and_disables_shell(
    tmp_path: Path,
) -> None:
    gh_path = "C:\\Program Files\\GitHub CLI\\gh.exe"
    client = GitHubReadOnlyClient(
        tmp_path,
        env={"PATH": ""},
        gh_path=gh_path,
    )
    completed = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="[]", stderr=""
    )

    with patch(
        "physics_lab.registry.github_readonly.subprocess.run",
        return_value=completed,
    ) as run_mock:
        result = client.list_pull_requests()

    assert result.source == "gh"
    command = run_mock.call_args.args[0]
    assert command[0] == gh_path
    assert run_mock.call_args.kwargs["shell"] is False


def test_list_pull_requests_uses_public_rest_after_gh_auth_failure(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    public_payload = [
        {
            "number": 1579,
            "title": "TASK-1049: replay",
            "body": "",
            "state": "open",
            "merged_at": None,
            "head": {"ref": "agent/gladunrv/codex/task-1049-replay"},
            "html_url": "https://github.com/example/pull/1579",
            "draft": False,
        }
    ]
    auth_failure = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="HTTP 401: Requires authentication; try gh auth login",
    )

    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ) as run_mock,
        patch.object(client, "public_json", return_value=public_payload),
    ):
        result = client.list_pull_requests()

    assert result.source == "public_rest"
    assert result.payload == [
        {
            "number": 1579,
            "title": "TASK-1049: replay",
            "body": "",
            "state": "OPEN",
            "mergedAt": None,
            "headRefName": "agent/gladunrv/codex/task-1049-replay",
            "url": "https://github.com/example/pull/1579",
            "isDraft": False,
        }
    ]
    assert run_mock.call_count == 1
    assert "401" in result.diagnostics[0]


def test_list_task_claims_filters_pull_requests_from_public_issue_endpoint(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    auth_failure = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="HTTP 401: Requires authentication",
    )
    public_payload = [
        {"number": 10, "title": "Claim TASK-0001", "body": "TASK-0001"},
        {
            "number": 11,
            "title": "PR carrying the same label",
            "body": "",
            "pull_request": {"url": "https://api.github.com/pulls/11"},
        },
    ]

    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ),
        patch.object(client, "public_json", return_value=public_payload),
    ):
        result = client.list_task_claims()

    assert result.source == "public_rest"
    assert result.payload == [
        {"number": 10, "title": "Claim TASK-0001", "body": "TASK-0001"}
    ]


def test_permanent_gh_auth_failure_is_reused_inside_one_agent_run(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    auth_failure = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="HTTP 401: authentication required"
    )

    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ) as run_mock,
        patch.object(client, "public_json", return_value=[]),
    ):
        pulls = client.list_pull_requests()
        claims = client.list_task_claims()

    assert pulls.source == claims.source == "public_rest"
    assert run_mock.call_count == 1
    assert claims.diagnostics == pulls.diagnostics


def test_load_pull_request_retries_one_transient_gh_failure(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    payload = {
        "number": 104,
        "title": "TASK-0104: Fixture",
        "body": "complete body",
        "headRefName": "agent/roman/codex/task-0104-fixture",
        "headRefOid": "a" * 40,
        "baseRefName": "main",
        "state": "OPEN",
        "mergedAt": None,
        "statusCheckRollup": [],
        "files": [],
    }
    responses = [
        subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="HTTP 503"
        ),
        subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        ),
    ]

    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            side_effect=responses,
        ) as run_mock,
        patch("physics_lab.registry.github_readonly.time.sleep") as sleep_mock,
        patch.object(
            client,
            "public_json",
            side_effect=AssertionError("successful retry must not use REST"),
        ),
    ):
        result = client.load_pull_request(104)

    assert result.source == "gh_view"
    assert result.payload == payload
    assert run_mock.call_count == 2
    sleep_mock.assert_called_once()
    assert result.diagnostics == ("gh pr view attempt 1 failed: HTTP 503",)


def test_load_pull_request_normalizes_complete_public_rest_payload(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    head_sha = "a" * 40
    requested_paths: list[str] = []

    def fake_public_json(path: str):
        requested_paths.append(path)
        if path.endswith("/pulls/104"):
            return {
                "number": 104,
                "title": "TASK-0104: Fixture",
                "body": "complete body",
                "state": "open",
                "merged_at": None,
                "changed_files": 1,
                "head": {
                    "ref": "agent/roman/codex/task-0104-fixture",
                    "sha": head_sha,
                },
                "base": {"ref": "main"},
            }
        if "/pulls/104/files?" in path:
            return [{"filename": "tasks/TASK-0104-fixture.yaml"}]
        if f"/commits/{head_sha}/check-runs?" in path:
            return {
                "total_count": 1,
                "check_runs": [
                    {
                        "name": "Python fast tests (3.12)",
                        "status": "completed",
                        "conclusion": "success",
                        "started_at": "2026-07-15T10:00:00Z",
                        "completed_at": "2026-07-15T10:01:00Z",
                    }
                ],
            }
        raise AssertionError(f"unexpected public API path: {path}")

    auth_failure = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="HTTP 401: authentication required"
    )
    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ) as run_mock,
        patch.object(client, "public_json", side_effect=fake_public_json),
    ):
        result = client.load_pull_request(104)

    assert result.source == "public_rest"
    assert result.complete is True
    assert result.payload["headRefOid"] == head_sha
    assert result.payload["files"] == [
        {"path": "tasks/TASK-0104-fixture.yaml"}
    ]
    assert result.payload["statusCheckRollup"][0]["conclusion"] == "success"
    assert len(requested_paths) == 3
    assert run_mock.call_count == 1


def test_load_pull_request_refuses_incomplete_public_check_runs(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    head_sha = "a" * 40

    def fake_public_json(path: str):
        if path.endswith("/pulls/104"):
            return {
                "number": 104,
                "changed_files": 1,
                "head": {
                    "ref": "agent/roman/codex/task-0104-fixture",
                    "sha": head_sha,
                },
                "base": {"ref": "main"},
            }
        if "/pulls/104/files?" in path:
            return [{"filename": "tasks/TASK-0104-fixture.yaml"}]
        if f"/commits/{head_sha}/check-runs?" in path:
            return {"total_count": 101, "check_runs": []}
        raise AssertionError(f"unexpected public API path: {path}")

    auth_failure = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="HTTP 401: authentication required"
    )
    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ),
        patch.object(client, "public_json", side_effect=fake_public_json),
    ):
        result = client.load_pull_request(104)

    assert result.payload is None
    assert any(
        "check-runs response was incomplete" in item
        for item in result.diagnostics
    )


def test_load_pull_request_refuses_large_public_pr_before_extra_requests(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)
    requested_paths: list[str] = []

    def fake_public_json(path: str):
        requested_paths.append(path)
        return {
            "number": 104,
            "changed_files": 101,
            "head": {
                "ref": "agent/roman/codex/task-0104-fixture",
                "sha": "a" * 40,
            },
            "base": {"ref": "main"},
        }

    auth_failure = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="HTTP 401: authentication required"
    )
    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ),
        patch.object(client, "public_json", side_effect=fake_public_json),
    ):
        result = client.load_pull_request(104)

    assert result.payload is None
    assert requested_paths == [
        f"/repos/{CANONICAL_GITHUB_REPOSITORY}/pulls/104"
    ]
    assert any("more than 100 changed files" in item for item in result.diagnostics)


def test_public_rest_surfaces_low_rate_limit_warning(tmp_path: Path) -> None:
    client = _client(tmp_path)
    auth_failure = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="HTTP 401: authentication required"
    )

    with (
        patch(
            "physics_lab.registry.github_readonly.subprocess.run",
            return_value=auth_failure,
        ),
        patch(
            "physics_lab.registry.github_readonly.urlopen",
            return_value=_FakeResponse([], remaining="5"),
        ),
    ):
        result = client.list_pull_requests()

    assert result.source == "public_rest"
    assert any("rate limit is low" in item for item in result.diagnostics)
