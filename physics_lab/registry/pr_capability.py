"""Preflight checks for opening GitHub pull requests from agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
from typing import Mapping

from physics_lab.registry.review_git import run_command
from physics_lab.registry.subprocess_env import env_with_overrides as env_with_overrides


TOKEN_ENV_NAMES = ("GH_TOKEN", "GITHUB_TOKEN")
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
    """Result of checking whether this environment can open a PR directly."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    gh_path: str | None
    git_path: str | None
    token_env_names: tuple[str, ...]
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
) -> PrCapabilityReport:
    """Check whether a PR can be opened directly, without blocking local work."""
    env_map = os.environ if env is None else env
    tokens = tuple(name for name in TOKEN_ENV_NAMES if env_map.get(name))
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
                "GitHub CLI `gh` was not found; token-based API fallback appears available."
            )
        else:
            warnings.append(
                "Direct PR creation is not available in this environment: neither `gh` "
                "nor `GH_TOKEN`/`GITHUB_TOKEN` is available. Continue local task work "
                "and provide maintainer-run `git push` and `gh pr create` commands."
            )
        return PrCapabilityReport(
            errors=tuple(errors),
            warnings=tuple(warnings),
            gh_path=None,
            git_path=git_path,
            token_env_names=tokens,
            suspicious_proxy_env_names=suspicious_proxy_names,
        )

    if require_gh_auth:
        result = run_command([resolved_gh_path, "auth", "status"], cwd=root, timeout=20)
        if result.returncode != 0:
            if tokens:
                warnings.append(
                    "`gh auth status` failed, but token-based API fallback appears available."
                )
            else:
                warnings.append(
                    "`gh` is installed but not authenticated, and no "
                    "`GH_TOKEN`/`GITHUB_TOKEN` fallback is available. Continue local "
                    "task work and provide maintainer-run publication commands."
                )

    return PrCapabilityReport(
        errors=tuple(errors),
        warnings=tuple(warnings),
        gh_path=resolved_gh_path,
        git_path=git_path,
        token_env_names=tokens,
        suspicious_proxy_env_names=suspicious_proxy_names,
    )


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
