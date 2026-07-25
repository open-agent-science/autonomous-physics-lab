"""Preflight checks for opening GitHub pull requests from agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
from typing import Literal, Mapping

from physics_lab.registry.review_git import run_command
from physics_lab.registry.subprocess_env import env_with_overrides as env_with_overrides


TOKEN_ENV_NAMES = ("GH_TOKEN", "GITHUB_TOKEN")
SANDBOX_ENV_NAMES = ("CODEX_SANDBOX",)
CANONICAL_GITHUB_REPOSITORY = "open-agent-science/autonomous-physics-lab"
DIRECT_WRITE_PERMISSIONS = frozenset({"ADMIN", "MAINTAIN", "WRITE"})
FORK_ROUTE_PERMISSIONS = frozenset({"TRIAGE", "READ"})
GhAuthState = Literal[
    "authenticated",
    "not_checked",
    "gh_unavailable",
    "sandbox_credential_unverified",
    "token_env_unverified",
    "unauthenticated_or_invalid",
]
PublicationRoute = Literal["direct", "fork", "unknown", "not_checked"]
PROXY_ENV_NAMES = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "GIT_HTTP_PROXY",
    "GIT_HTTPS_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)
DEFAULT_GH_CANDIDATE_PATHS = (
    "C:/Program Files/GitHub CLI/gh.exe",
    "C:/Program Files (x86)/GitHub CLI/gh.exe",
    "/opt/homebrew/bin/gh",
    "/usr/local/bin/gh",
)
DEFAULT_GIT_CANDIDATE_PATHS = (
    "C:/Program Files/Git/cmd/git.exe",
    "C:/Program Files/Git/bin/git.exe",
    "C:/Program Files (x86)/Git/cmd/git.exe",
    "C:/Program Files (x86)/Git/bin/git.exe",
)
# Env var that overrides the hardcoded gh discovery fallback. Set to a
# colon-separated list of paths to use those instead of DEFAULT_GH_CANDIDATE_PATHS;
# set to an empty string to disable the fallback entirely. The env var exists
# so tests can deterministically simulate the "gh not installed" case
# regardless of whether the developer's local machine has gh in Homebrew.
GH_CANDIDATE_PATHS_ENV_VAR = "APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"
GIT_CANDIDATE_PATHS_ENV_VAR = "APL_PR_CAPABILITY_GIT_CANDIDATE_PATHS"


def _candidate_paths_from_env(
    env: Mapping[str, str] | None,
    *,
    env_var: str = GH_CANDIDATE_PATHS_ENV_VAR,
) -> tuple[str, ...] | None:
    """Return the candidate-paths override from the environment, or None.

    A set-but-empty env var disables the fallback (returns an empty tuple).
    An unset env var returns None so callers can keep their default.
    """
    env_map = os.environ if env is None else env
    raw = env_map.get(env_var)
    if raw is None:
        return None
    if raw == "":
        return ()
    return tuple(part for part in raw.split(os.pathsep) if part)


@dataclass(frozen=True)
class PrCapabilityReport:
    """Result of checking which PR publication route this environment can use."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    gh_path: str | None
    git_path: str | None
    gh_auth_state: GhAuthState
    repository: str
    repository_permission: str | None
    authenticated_login: str | None
    publication_route: PublicationRoute
    branch: str | None
    fork_commands: tuple[tuple[str, ...], ...]
    token_env_names: tuple[str, ...]
    sandbox_detected: bool
    sandbox_env_names: tuple[str, ...]
    suspicious_proxy_env_names: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def check_pr_capability(
    root: Path,
    *,
    env: Mapping[str, str] | None = None,
    gh_path: str | None = None,
    candidate_paths: tuple[str, ...] = DEFAULT_GH_CANDIDATE_PATHS,
    discover_gh: bool = True,
    require_gh_auth: bool = True,
    check_repository_permission: bool = True,
    agent_sandbox: bool = False,
    repository: str = CANONICAL_GITHUB_REPOSITORY,
    branch: str | None = None,
) -> PrCapabilityReport:
    """Diagnose the direct or fork PR route without blocking local work."""
    env_map = os.environ if env is None else env
    tokens = tuple(name for name in TOKEN_ENV_NAMES if env_map.get(name))
    sandbox_names = active_sandbox_env_names(env_map)
    sandbox_detected = agent_sandbox or bool(sandbox_names)
    git_path = find_git_path(env=env_map)
    suspicious_proxy_names = suspicious_proxy_env_names(env_map)
    # Env var override for candidate paths wins when set. An empty value
    # disables the fallback entirely so tests can simulate "gh not installed"
    # even on Macs where Homebrew installs gh under /opt/homebrew/bin/.
    env_candidate_paths = _candidate_paths_from_env(
        env_map,
        env_var=GH_CANDIDATE_PATHS_ENV_VAR,
    )
    effective_candidate_paths = (
        env_candidate_paths
        if env_candidate_paths is not None
        else candidate_paths
    )
    resolved_gh_path = gh_path if gh_path is not None else (
        find_gh_path(
            candidate_paths=effective_candidate_paths,
            env=env_map,
        )
        if discover_gh
        else None
    )
    errors: list[str] = []
    warnings: list[str] = []
    current_branch = branch or _current_git_branch(
        root,
        git_path=git_path,
        env=env_map,
    )
    repository_permission: str | None = None
    authenticated_login: str | None = None
    publication_route: PublicationRoute = (
        "unknown"
        if require_gh_auth and check_repository_permission
        else "not_checked"
    )
    fork_commands: tuple[tuple[str, ...], ...] = ()

    if suspicious_proxy_names:
        warnings.append(
            "Network proxy environment variables look like a local blocker "
            f"({', '.join(suspicious_proxy_names)}). If GitHub API calls fail "
            "with a 127.0.0.1 connection error, unset these variables for the "
            "single publication command and retry."
        )

    if resolved_gh_path is None:
        if tokens:
            warnings.append(
                "GitHub CLI `gh` was not found while GH_TOKEN/GITHUB_TOKEN is present. "
                "The environment token is unverified; do not describe it as an "
                "available fallback or print its value. Ask the maintainer to "
                "authenticate GitHub CLI through the standard web flow first "
                "(`gh auth login --hostname github.com --git-protocol https --web`) "
                "or verify the environment token through their secure credential "
                "path before GitHub writes."
            )
            gh_auth_state: GhAuthState = "token_env_unverified"
        else:
            warnings.append(
                "Direct PR creation is not available in this environment: neither `gh` "
                "nor `GH_TOKEN`/`GITHUB_TOKEN` is available. Ask the maintainer to "
                "install or expose GitHub CLI and authorize it with "
                "`gh auth login --hostname github.com --git-protocol https --web`, "
                "then verify with `gh auth status --hostname github.com`. Continue "
                "local task work while authorization is pending; the bounded public "
                "REST fallback is read-only and does not authorize GitHub writes."
            )
            gh_auth_state = "gh_unavailable"
        return PrCapabilityReport(
            errors=tuple(errors),
            warnings=tuple(warnings),
            gh_path=None,
            git_path=git_path,
            gh_auth_state=gh_auth_state,
            repository=repository,
            repository_permission=repository_permission,
            authenticated_login=authenticated_login,
            publication_route=publication_route,
            branch=current_branch,
            fork_commands=fork_commands,
            token_env_names=tokens,
            sandbox_detected=sandbox_detected,
            sandbox_env_names=sandbox_names,
            suspicious_proxy_env_names=suspicious_proxy_names,
        )

    gh_auth_state = "not_checked"
    if require_gh_auth:
        result = run_command(
            [resolved_gh_path, "auth", "status", "--hostname", "github.com"],
            cwd=root,
            timeout=20,
            env=env_map,
        )
        if result.returncode == 0:
            gh_auth_state = "authenticated"
            if check_repository_permission:
                # Authentication proves identity, not upstream push access. Keep this
                # separate permission query so external contributors are routed to a
                # fork instead of receiving a predictable 403 from `git push origin`.
                permission_result = run_command(
                    [
                        resolved_gh_path,
                        "repo",
                        "view",
                        repository,
                        "--json",
                        "viewerPermission",
                        "--jq",
                        ".viewerPermission",
                    ],
                    cwd=root,
                    timeout=20,
                    env=env_map,
                )
                permission = permission_result.stdout.strip().upper()
                if permission_result.returncode != 0 or not permission:
                    publication_route = "unknown"
                    warnings.append(
                        "GitHub authentication succeeded, but repository permission "
                        f"for `{repository}` could not be determined. Do not assume "
                        "that `origin` accepts pushes; rerun this check in a network-"
                        "enabled maintainer terminal before publication."
                    )
                elif permission in DIRECT_WRITE_PERMISSIONS:
                    repository_permission = permission
                    publication_route = "direct"
                elif permission in FORK_ROUTE_PERMISSIONS:
                    repository_permission = permission
                    publication_route = "fork"
                    login_result = run_command(
                        [resolved_gh_path, "api", "user", "--jq", ".login"],
                        cwd=root,
                        timeout=20,
                        env=env_map,
                    )
                    login = login_result.stdout.strip()
                    if login_result.returncode == 0 and _is_safe_github_login(login):
                        authenticated_login = login
                        fork_commands = fork_publication_commands(
                            repository=repository,
                            login=login,
                            branch=current_branch,
                            gh_command=resolved_gh_path,
                            git_command=git_path or "git",
                        )
                    warnings.append(
                        f"GitHub authentication is valid, but `{repository}` grants "
                        f"{permission} rather than upstream write access. This is an "
                        "expected external-contributor state: publish through a "
                        "contributor-owned fork and open a cross-repository PR. Do "
                        "not request upstream write permission solely to contribute."
                    )
                    if authenticated_login is None:
                        warnings.append(
                            "The authenticated GitHub login could not be determined, "
                            "so an exact cross-repository PR command was not generated."
                        )
                    elif current_branch is None:
                        warnings.append(
                            "The current Git branch could not be determined, so an "
                            "exact fork publication command pack was not generated."
                        )
                    elif not fork_commands:
                        warnings.append(
                            "The current branch is not a safe canonical task branch, "
                            "so an executable fork command pack was not generated."
                        )
                else:
                    repository_permission = permission
                    publication_route = "unknown"
                    warnings.append(
                        f"GitHub reported unsupported viewerPermission `{permission}` "
                        f"for `{repository}`. Do not assume direct push access."
                    )
        elif tokens:
            gh_auth_state = "token_env_unverified"
            warnings.append(
                "`gh auth status` failed while GH_TOKEN/GITHUB_TOKEN is present. "
                "The environment token is unverified; do not describe it as an "
                "available fallback or print its value. Ask the maintainer to "
                "authenticate GitHub CLI through the standard web flow first "
                f"(`{resolved_gh_path} auth login --hostname github.com "
                "--git-protocol https --web`) or verify the environment token "
                "through their secure credential path before GitHub writes."
            )
        elif sandbox_detected:
            # macOS Keychain and similar host credential stores can be intentionally
            # invisible to an agent sandbox. Treat that as unknown, not as proof that
            # the token expired; writes still require an authenticated rerun.
            gh_auth_state = "sandbox_credential_unverified"
            sandbox_label = (
                ", ".join(sandbox_names)
                if sandbox_names
                else "explicit --agent-sandbox signal"
            )
            warnings.append(
                "`gh auth status` failed inside an agent sandbox "
                f"({sandbox_label}). This does not prove that the host "
                "credential or token is invalid. Do not run `gh auth login`/`logout` "
                "from this result alone. Read-only APL PR metadata may use the bounded "
                "public REST fallback; before any GitHub write, rerun "
                f"`{resolved_gh_path} auth status --hostname github.com` in the "
                "maintainer terminal or with protocol-approved sandbox escalation. "
                "Only if that keychain-aware check also fails should the agent ask "
                "the maintainer to run the standard web login flow."
            )
        else:
            gh_auth_state = "unauthenticated_or_invalid"
            warnings.append(
                "`gh` authentication failed outside a recognized agent sandbox, and "
                "no GH_TOKEN/GITHUB_TOKEN fallback is present. Ask the maintainer to "
                "authorize the discovered CLI with "
                f"`{resolved_gh_path} auth login --hostname github.com "
                "--git-protocol https --web`, then verify with "
                f"`{resolved_gh_path} auth status --hostname github.com`. The bounded "
                "public REST fallback may support read-only review while authorization "
                "is pending, but it does not authorize GitHub writes."
            )

    return PrCapabilityReport(
        errors=tuple(errors),
        warnings=tuple(warnings),
        gh_path=resolved_gh_path,
        git_path=git_path,
        gh_auth_state=gh_auth_state,
        repository=repository,
        repository_permission=repository_permission,
        authenticated_login=authenticated_login,
        publication_route=publication_route,
        branch=current_branch,
        fork_commands=fork_commands,
        token_env_names=tokens,
        sandbox_detected=sandbox_detected,
        sandbox_env_names=sandbox_names,
        suspicious_proxy_env_names=suspicious_proxy_names,
    )


def _current_git_branch(
    root: Path,
    *,
    git_path: str | None,
    env: Mapping[str, str],
) -> str | None:
    if git_path is None:
        return None
    result = run_command(
        [git_path, "branch", "--show-current"],
        cwd=root,
        timeout=20,
        env=env,
    )
    branch = result.stdout.strip()
    return branch or None


def _is_safe_github_login(login: str) -> bool:
    return bool(
        1 <= len(login) <= 39
        and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", login)
        and "--" not in login
    )


def _is_safe_task_branch(branch: str) -> bool:
    return bool(
        re.fullmatch(
            r"agent/[a-z0-9][a-z0-9-]*/[a-z0-9][a-z0-9-]*/"
            r"task-[0-9]{4}-[a-z0-9][a-z0-9-]*",
            branch,
        )
    )


def _task_title_from_branch(branch: str) -> str:
    task_segment = branch.rsplit("/", maxsplit=1)[-1]
    match = re.fullmatch(r"task-([0-9]{4})-(.+)", task_segment)
    if match is None:
        raise ValueError("A canonical task branch is required.")
    return f"TASK-{match.group(1)}: {match.group(2).replace('-', ' ')}"


def fork_publication_commands(
    *,
    repository: str,
    login: str,
    branch: str | None,
    gh_command: str = "gh",
    git_command: str = "git",
    body_file: str = ".apl-pr-body.md",
) -> tuple[tuple[str, ...], ...]:
    """Return shell-free argv commands for an external contributor fork PR."""
    if (
        not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
        or not _is_safe_github_login(login)
        or branch is None
        or not _is_safe_task_branch(branch)
    ):
        return ()
    return (
        (
            gh_command,
            "repo",
            "fork",
            repository,
            "--clone=false",
            "--remote",
            "--remote-name",
            "fork",
        ),
        (git_command, "push", "--set-upstream", "fork", branch),
        (
            gh_command,
            "pr",
            "create",
            "--repo",
            repository,
            "--base",
            "main",
            "--head",
            f"{login}:{branch}",
            "--draft",
            "--title",
            _task_title_from_branch(branch),
            "--body-file",
            body_file,
        ),
    )


def active_sandbox_env_names(
    env: Mapping[str, str] | None = None,
) -> tuple[str, ...]:
    """Return recognized agent-sandbox markers without exposing their values."""
    env_map = os.environ if env is None else env
    return tuple(name for name in SANDBOX_ENV_NAMES if env_map.get(name))


def find_gh_path(
    *,
    candidate_paths: tuple[str, ...] = DEFAULT_GH_CANDIDATE_PATHS,
    env: Mapping[str, str] | None = None,
) -> str | None:
    """Find GitHub CLI even when Codex PATH omits Homebrew directories.

    When the ``APL_PR_CAPABILITY_GH_CANDIDATE_PATHS`` env var is set, its
    value (or an empty value meaning "no fallback") replaces the
    ``candidate_paths`` argument. This lets tests force a deterministic
    "gh not installed" state regardless of the local installation.
    """
    env_map = os.environ if env is None else env
    env_candidate_paths = _candidate_paths_from_env(
        env_map,
        env_var=GH_CANDIDATE_PATHS_ENV_VAR,
    )
    effective_candidate_paths = (
        env_candidate_paths
        if env_candidate_paths is not None
        else candidate_paths
    )

    # PATH-based discovery still runs first so that an explicitly set PATH
    # remains the canonical way to find gh in normal use.
    discovered = shutil.which("gh", path=env_map.get("PATH") or None)
    if discovered is not None:
        return discovered
    for candidate in effective_candidate_paths:
        path = Path(candidate)
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    return None


def find_git_path(
    *,
    candidate_paths: tuple[str, ...] = DEFAULT_GIT_CANDIDATE_PATHS,
    env: Mapping[str, str] | None = None,
) -> str | None:
    """Find Git even when the current shell PATH omits Git for Windows."""
    env_map = os.environ if env is None else env
    env_candidate_paths = _candidate_paths_from_env(
        env_map,
        env_var=GIT_CANDIDATE_PATHS_ENV_VAR,
    )
    effective_candidate_paths = (
        env_candidate_paths
        if env_candidate_paths is not None
        else candidate_paths
    )

    discovered = shutil.which("git", path=env_map.get("PATH") or None)
    if discovered is not None:
        return discovered
    for candidate in effective_candidate_paths:
        path = Path(candidate)
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    return None


def suspicious_proxy_env_names(env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Return proxy env names that point at the known local blocker port.

    Codex sessions may intentionally set proxy variables to ``127.0.0.1:9``
    when network access is unavailable. That is useful sandbox metadata, but it
    makes GitHub CLI failures look like authentication failures. Reporting the
    exact variables keeps the fix local to the publication command.
    """
    env_map = os.environ if env is None else env
    hits: list[str] = []
    seen_keys: set[str] = set()
    for name in PROXY_ENV_NAMES:
        key = name.lower()
        if key in seen_keys:
            continue
        value = (env_map.get(name) or "").strip().lower()
        if not value:
            continue
        if "127.0.0.1:9" in value or "localhost:9" in value:
            hits.append(name)
            seen_keys.add(key)
    return tuple(dict.fromkeys(hits))


def without_suspicious_proxy_env(env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return a copy without known local-blocker proxy variables.

    This helper is deliberately opt-in. It removes only variables whose value
    points at the known loopback blocker port and leaves legitimate proxy
    configuration untouched.
    """
    env_map = dict(os.environ if env is None else env)
    blocked_keys = {name.lower() for name in suspicious_proxy_env_names(env_map)}
    return {
        name: value
        for name, value in env_map.items()
        if name.lower() not in blocked_keys
    }


def env_with_discovered_tool_paths(
    env: Mapping[str, str] | None = None,
    *,
    clear_suspicious_proxy: bool = False,
) -> dict[str, str]:
    """Return a child environment with discovered tool dirs on PATH."""
    env_map = dict(os.environ if env is None else env)
    if clear_suspicious_proxy:
        env_map = without_suspicious_proxy_env(env_map)
    path_parts = [
        part
        for part in (env_map.get("PATH") or "").split(os.pathsep)
        if part
    ]
    existing = {os.path.normcase(part) for part in path_parts}
    for tool_path in (find_gh_path(env=env_map), find_git_path(env=env_map)):
        if tool_path is None:
            continue
        parent = str(Path(tool_path).parent)
        key = os.path.normcase(parent)
        if key not in existing:
            path_parts.insert(0, parent)
            existing.add(key)
    env_map["PATH"] = os.pathsep.join(path_parts)
    return env_map
