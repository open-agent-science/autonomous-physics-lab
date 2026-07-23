from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

from physics_lab.registry.pr_capability import (
    active_sandbox_env_names,
    check_pr_capability,
    env_with_discovered_tool_paths,
    find_git_path,
    fork_publication_commands,
    suspicious_proxy_env_names,
    without_suspicious_proxy_env,
)
from physics_lab.registry.pr_capability import (
    env_with_overrides as pr_capability_env_with_overrides,
)
from physics_lab.registry.review_git import CommandResult
from physics_lab.registry.subprocess_env import env_with_overrides


def _write_gh_stub(bin_dir: Path, *, exit_code: int = 0) -> Path:
    """Create a tiny cross-platform gh stub and return its executable path."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        stub = bin_dir / "gh.cmd"
        stub.write_text(f"@echo off\r\nexit /b {exit_code}\r\n", encoding="utf-8")
        return stub

    stub = bin_dir / "gh"
    stub.write_text(
        dedent(
            f"""\
            #!/bin/sh
            exit {exit_code}
            """
        ),
        encoding="utf-8",
    )
    stub.chmod(0o755)
    return stub


def _write_routing_gh_stub(
    bin_dir: Path,
    *,
    permission: str,
    login: str = "test-contributor",
) -> Path:
    """Create a gh stub that authenticates and reports viewerPermission."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        stub = bin_dir / "gh.cmd"
        stub.write_text(
            dedent(
                f"""\
                @echo off
                if "%1"=="repo" echo {permission}
                if "%1"=="api" echo {login}
                exit /b 0
                """
            ),
            encoding="utf-8",
        )
        return stub

    stub = bin_dir / "gh"
    stub.write_text(
        dedent(
            f"""\
            #!/bin/sh
            if [ "$1" = "repo" ]; then
              printf '%s\\n' '{permission}'
            fi
            if [ "$1" = "api" ]; then
              printf '%s\\n' '{login}'
            fi
            exit 0
            """
        ),
        encoding="utf-8",
    )
    stub.chmod(0o755)
    return stub


def test_pr_capability_is_advisory_without_gh_or_token(tmp_path: Path) -> None:
    report = check_pr_capability(
        tmp_path,
        env={},
        discover_gh=False,
    )

    assert report.ok
    assert report.errors == ()
    assert any("Direct PR creation is not available" in item for item in report.warnings)
    assert any("gh auth login" in item for item in report.warnings)
    assert any("read-only" in item for item in report.warnings)


def test_pr_capability_reports_unverified_token_without_gh(tmp_path: Path) -> None:
    report = check_pr_capability(
        tmp_path,
        env={"GITHUB_TOKEN": "present"},
        discover_gh=False,
    )

    assert report.ok
    assert report.gh_auth_state == "token_env_unverified"
    assert report.token_env_names == ("GITHUB_TOKEN",)
    assert any("environment token is unverified" in item for item in report.warnings)
    assert not any("fallback appears available" in item for item in report.warnings)


def test_pr_capability_discovers_homebrew_style_gh_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_gh = _write_gh_stub(tmp_path)
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda _name, path=None: None,
    )

    report = check_pr_capability(
        tmp_path,
        env={},
        candidate_paths=(str(fake_gh),),
        require_gh_auth=False,
    )

    assert report.ok
    assert report.gh_path == str(fake_gh)


def test_pr_capability_discovers_windows_style_gh_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_gh = _write_gh_stub(tmp_path / "GitHub CLI")
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda _name, path=None: None,
    )

    report = check_pr_capability(
        tmp_path,
        env={},
        candidate_paths=(str(fake_gh),),
        require_gh_auth=False,
    )

    assert report.ok
    assert report.gh_path == str(fake_gh)


def test_pr_capability_reports_authenticated_gh(tmp_path: Path) -> None:
    fake_gh = _write_gh_stub(tmp_path, exit_code=0)

    report = check_pr_capability(
        tmp_path,
        env={"PATH": ""},
        gh_path=str(fake_gh),
        check_repository_permission=False,
    )

    assert report.gh_auth_state == "authenticated"
    assert report.publication_route == "not_checked"
    assert report.sandbox_detected is False
    assert report.sandbox_env_names == ()
    assert report.warnings == ()


def test_pr_capability_routes_read_permission_through_fork(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(command, **_kwargs) -> CommandResult:
        argv = tuple(command)
        calls.append(argv)
        if argv[1:3] == ("auth", "status"):
            return CommandResult(0, "", "")
        if argv[1:3] == ("repo", "view"):
            return CommandResult(0, "READ\n", "")
        if argv[1:3] == ("api", "user"):
            return CommandResult(0, "ablmnzde\n", "")
        raise AssertionError(f"Unexpected command: {argv}")

    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_git_path",
        lambda env=None: "git-tool",
    )
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.run_command",
        fake_run,
    )
    branch = "agent/ablmnzde/codex/task-1094-external-contributor-fork-flow"

    report = check_pr_capability(
        tmp_path,
        env={"PATH": ""},
        gh_path="gh-tool",
        branch=branch,
    )

    assert report.gh_auth_state == "authenticated"
    assert report.repository_permission == "READ"
    assert report.authenticated_login == "ablmnzde"
    assert report.publication_route == "fork"
    assert report.fork_commands == (
        (
            "gh-tool",
            "repo",
            "fork",
            "open-agent-science/autonomous-physics-lab",
            "--clone=false",
            "--remote",
            "--remote-name",
            "fork",
        ),
        ("git-tool", "push", "--set-upstream", "fork", branch),
        (
            "gh-tool",
            "pr",
            "create",
            "--repo",
            "open-agent-science/autonomous-physics-lab",
            "--base",
            "main",
            "--head",
            f"ablmnzde:{branch}",
            "--draft",
            "--title",
            "TASK-1094: external contributor fork flow",
            "--body-file",
            ".apl-pr-body.md",
        ),
    )
    assert any("expected external-contributor state" in item for item in report.warnings)
    assert any(
        "Do not request upstream write permission solely" in item
        for item in report.warnings
    )
    assert ("gh-tool", "repo", "view") == calls[1][:3]


def test_pr_capability_routes_write_permission_directly(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fake_run(command, **_kwargs) -> CommandResult:
        argv = tuple(command)
        if argv[1:3] == ("auth", "status"):
            return CommandResult(0, "", "")
        if argv[1:3] == ("repo", "view"):
            return CommandResult(0, "WRITE\n", "")
        raise AssertionError(f"Unexpected command: {argv}")

    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_git_path",
        lambda env=None: "git-tool",
    )
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.run_command",
        fake_run,
    )

    report = check_pr_capability(
        tmp_path,
        env={"PATH": ""},
        gh_path="gh-tool",
        branch="agent/gladunrv/codex/task-1094-external-contributor-fork-flow",
    )

    assert report.repository_permission == "WRITE"
    assert report.publication_route == "direct"
    assert report.fork_commands == ()
    assert report.warnings == ()


def test_pr_capability_does_not_assume_direct_when_permission_query_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fake_run(command, **_kwargs) -> CommandResult:
        argv = tuple(command)
        if argv[1:3] == ("auth", "status"):
            return CommandResult(0, "", "")
        if argv[1:3] == ("repo", "view"):
            return CommandResult(1, "", "network unavailable")
        raise AssertionError(f"Unexpected command: {argv}")

    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_git_path",
        lambda env=None: "git-tool",
    )
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.run_command",
        fake_run,
    )

    report = check_pr_capability(
        tmp_path,
        env={"PATH": ""},
        gh_path="gh-tool",
        branch="agent/gladunrv/codex/task-1094-external-contributor-fork-flow",
    )

    assert report.repository_permission is None
    assert report.publication_route == "unknown"
    assert report.fork_commands == ()
    assert any("Do not assume" in item for item in report.warnings)


def test_fork_publication_commands_reject_unsafe_identifiers() -> None:
    assert fork_publication_commands(
        repository="open-agent-science/autonomous-physics-lab",
        login="safe-login",
        branch="agent/safe/codex/task-1094-safe;touch-bad",
    ) == ()
    assert fork_publication_commands(
        repository="open-agent-science/autonomous-physics-lab",
        login="unsafe;login",
        branch="agent/safe/codex/task-1094-safe-branch",
    ) == ()


def test_pr_capability_does_not_treat_sandbox_keyring_failure_as_revocation(
    tmp_path: Path,
) -> None:
    fake_gh = _write_gh_stub(tmp_path, exit_code=1)

    report = check_pr_capability(
        tmp_path,
        env={"PATH": "", "CODEX_SANDBOX": "seatbelt"},
        gh_path=str(fake_gh),
    )

    assert report.gh_auth_state == "sandbox_credential_unverified"
    assert report.sandbox_detected is True
    assert report.sandbox_env_names == ("CODEX_SANDBOX",)
    assert any("does not prove" in item for item in report.warnings)
    assert any("protocol-approved sandbox escalation" in item for item in report.warnings)
    assert any("Only if that keychain-aware check" in item for item in report.warnings)
    assert not any("not authenticated" in item for item in report.warnings)


def test_pr_capability_accepts_explicit_sandbox_signal_for_other_agents(
    tmp_path: Path,
) -> None:
    fake_gh = _write_gh_stub(tmp_path, exit_code=1)

    report = check_pr_capability(
        tmp_path,
        env={"PATH": ""},
        gh_path=str(fake_gh),
        agent_sandbox=True,
    )

    assert report.gh_auth_state == "sandbox_credential_unverified"
    assert report.sandbox_detected is True
    assert report.sandbox_env_names == ()
    assert any("explicit --agent-sandbox signal" in item for item in report.warnings)


def test_pr_capability_does_not_claim_failed_env_token_is_available(
    tmp_path: Path,
) -> None:
    fake_gh = _write_gh_stub(tmp_path, exit_code=1)
    secret = "never-print-this-token"

    report = check_pr_capability(
        tmp_path,
        env={"PATH": "", "GH_TOKEN": secret},
        gh_path=str(fake_gh),
    )

    assert report.gh_auth_state == "token_env_unverified"
    assert report.token_env_names == ("GH_TOKEN",)
    rendered = repr(report)
    assert secret not in rendered
    assert any("unverified" in item for item in report.warnings)
    assert not any("fallback appears available" in item for item in report.warnings)


def test_pr_capability_reports_non_sandbox_auth_failure_conservatively(
    tmp_path: Path,
) -> None:
    fake_gh = _write_gh_stub(tmp_path, exit_code=1)

    report = check_pr_capability(tmp_path, env={"PATH": ""}, gh_path=str(fake_gh))

    assert report.gh_auth_state == "unauthenticated_or_invalid"
    assert any("gh auth login" in item for item in report.warnings)
    assert any("does not authorize GitHub writes" in item for item in report.warnings)


def test_active_sandbox_env_names_returns_names_without_values() -> None:
    assert active_sandbox_env_names(
        {"CODEX_SANDBOX": "secret-host-detail", "PATH": "test"}
    ) == ("CODEX_SANDBOX",)


def test_pr_capability_discovers_git_from_candidate_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_git = _write_gh_stub(tmp_path / "Git" / "cmd")
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda _name, path=None: None,
    )

    assert find_git_path(candidate_paths=(str(fake_git),), env={}) == str(fake_git)


def test_proxy_blocker_detection_reports_loopback_port() -> None:
    hits = suspicious_proxy_env_names(
        {
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://proxy.example.test:8080",
        }
    )

    assert hits == ("HTTPS_PROXY",)


def test_proxy_blocker_detection_deduplicates_case_variants() -> None:
    hits = suspicious_proxy_env_names(
        {
            "HTTP_PROXY": "http://127.0.0.1:9",
            "http_proxy": "http://127.0.0.1:9",
        }
    )

    assert hits == ("HTTP_PROXY",)


def test_without_suspicious_proxy_env_removes_only_known_blocker_values() -> None:
    env = without_suspicious_proxy_env(
        {
            "HTTP_PROXY": "http://127.0.0.1:9",
            "http_proxy": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://proxy.example.test:8080",
            "PATH": "test-path",
        }
    )

    assert "HTTP_PROXY" not in env
    assert "http_proxy" not in env
    assert env["HTTPS_PROXY"] == "http://proxy.example.test:8080"
    assert env["PATH"] == "test-path"


def test_env_with_discovered_tool_paths_can_clear_known_blocker_proxy(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_gh_path",
        lambda env=None: None,
    )
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_git_path",
        lambda env=None: None,
    )

    env = env_with_discovered_tool_paths(
        {
            "PATH": "",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://proxy.example.test:8080",
        },
        clear_suspicious_proxy=True,
    )

    assert "HTTPS_PROXY" not in env
    assert env["HTTP_PROXY"] == "http://proxy.example.test:8080"


def test_env_with_overrides_inherits_active_environment(monkeypatch) -> None:
    monkeypatch.setenv("APL_ENV_GUARDRAIL_SENTINEL", "kept")

    env = env_with_overrides(HTTPS_PROXY="http://127.0.0.1:9")

    assert env["APL_ENV_GUARDRAIL_SENTINEL"] == "kept"
    assert env["HTTPS_PROXY"] == "http://127.0.0.1:9"


def test_env_with_overrides_can_remove_explicit_keys() -> None:
    env = env_with_overrides(
        {"PATH": "base-path", "HTTPS_PROXY": "http://127.0.0.1:9"},
        HTTPS_PROXY=None,
        HTTP_PROXY="http://proxy.example.test:8080",
    )

    assert env["PATH"] == "base-path"
    assert "HTTPS_PROXY" not in env
    assert env["HTTP_PROXY"] == "http://proxy.example.test:8080"


def test_pr_capability_keeps_backward_compatible_env_with_overrides_alias() -> None:
    assert pr_capability_env_with_overrides is env_with_overrides


def test_env_with_overrides_preserves_dependency_discovery_in_child_process() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = env_with_overrides(APL_ENV_GUARDRAIL_SENTINEL="kept")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import os, yaml; "
                "print(os.environ['APL_ENV_GUARDRAIL_SENTINEL']); "
                "print(yaml.__name__)"
            ),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert result.stdout.splitlines() == ["kept", "yaml"]


def test_env_with_discovered_tool_paths_prepends_tool_dirs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_gh = _write_gh_stub(tmp_path / "GitHub CLI")
    fake_git = _write_gh_stub(tmp_path / "Git" / "cmd")
    calls = {"gh": fake_gh, "git": fake_git}

    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda name, path=None: str(calls[name]) if path in ("", None) else None,
    )

    env = env_with_discovered_tool_paths({"PATH": ""})
    parts = [Path(part) for part in env["PATH"].split(os.pathsep)]

    assert fake_gh.parent in parts
    assert fake_git.parent in parts


def test_pr_capability_cli_reports_missing_tooling_as_warning_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env["PATH"] = ""
    # Disable the hardcoded gh discovery fallback so the test simulates
    # the "gh not installed" state deterministically. Without this
    # override, developer machines with Homebrew gh would resolve
    # /opt/homebrew/bin/gh from the fallback list and silently flip the
    # warning path off.
    env["APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"] = ""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_pr_capability_check.py",
            "--root",
            ".",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert "PR capability check" in result.stdout
    assert "gh auth state: gh_unavailable" in result.stdout
    assert "git path:" in result.stdout
    assert "suspicious proxy env:" in result.stdout
    assert "Warnings:" in result.stdout
    assert "Direct PR creation" in result.stdout or "not authenticated" in result.stdout


def test_pr_capability_cli_reports_clean_state_when_gh_authenticated(
    tmp_path: Path,
) -> None:
    """Positive-path counterpart to the warning-path CLI test.

    A stub gh binary on a sandboxed PATH returns success for
    `gh auth status`. The script should report no warnings. The env-var
    override pins discovery to the stub so the registry's hardcoded
    fallback path does not silently shadow it.
    """
    repo_root = Path(__file__).resolve().parents[1]

    stub_bin = tmp_path / "stub-bin"
    stub_gh = _write_routing_gh_stub(stub_bin, permission="WRITE")

    env = os.environ.copy()
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env["PATH"] = str(stub_bin)
    env["APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"] = str(stub_gh)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_pr_capability_check.py",
            "--root",
            ".",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "PR capability check" in result.stdout
    assert "gh auth state: authenticated" in result.stdout
    assert "repository permission: WRITE" in result.stdout
    assert "publication route: direct" in result.stdout
    assert os.path.normcase(str(stub_gh)) in os.path.normcase(result.stdout)
    assert "Warnings: none" in result.stdout
    assert "Errors: none" in result.stdout


def test_pr_capability_cli_json_exposes_fork_command_argv(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    stub_bin = tmp_path / "stub-bin"
    stub_gh = _write_routing_gh_stub(
        stub_bin,
        permission="READ",
        login="external-user",
    )
    branch = "agent/external-user/codex/task-1094-fork-route"
    env = os.environ.copy()
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env["PATH"] = str(stub_bin)
    env["APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"] = str(stub_gh)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_pr_capability_check.py",
            "--root",
            ".",
            "--branch",
            branch,
            "--json",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    payload = json.loads(result.stdout)
    assert payload["repository_permission"] == "READ"
    assert payload["publication_route"] == "fork"
    assert payload["authenticated_login"] == "external-user"
    assert payload["fork_commands"][0][1:3] == ["repo", "fork"]
    assert payload["fork_commands"][1] == [
        "git",
        "push",
        "--set-upstream",
        "fork",
        branch,
    ]
    assert payload["fork_commands"][2][1:3] == ["pr", "create"]
    assert f"external-user:{branch}" in payload["fork_commands"][2]
