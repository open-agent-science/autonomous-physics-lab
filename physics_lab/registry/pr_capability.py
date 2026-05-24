"""Preflight checks for opening GitHub pull requests from agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
from typing import Mapping

from physics_lab.registry.review_git import run_command


TOKEN_ENV_NAMES = ("GH_TOKEN", "GITHUB_TOKEN")
DEFAULT_GH_CANDIDATE_PATHS = (
    "/opt/homebrew/bin/gh",
    "/usr/local/bin/gh",
)
# Env var that overrides the hardcoded gh discovery fallback. Set to a
# colon-separated list of paths to use those instead of DEFAULT_GH_CANDIDATE_PATHS;
# set to an empty string to disable the fallback entirely. The env var exists
# so tests can deterministically simulate the "gh not installed" case
# regardless of whether the developer's local machine has gh in Homebrew.
GH_CANDIDATE_PATHS_ENV_VAR = "APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"


def _candidate_paths_from_env(
    env: Mapping[str, str] | None,
) -> tuple[str, ...] | None:
    """Return the candidate-paths override from the environment, or None.

    A set-but-empty env var disables the fallback (returns an empty tuple).
    An unset env var returns None so callers can keep their default.
    """
    env_map = os.environ if env is None else env
    raw = env_map.get(GH_CANDIDATE_PATHS_ENV_VAR)
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
    token_env_names: tuple[str, ...]

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
    # Env var override for candidate paths wins when set. An empty value
    # disables the fallback entirely so tests can simulate "gh not installed"
    # even on Macs where Homebrew installs gh under /opt/homebrew/bin/.
    env_candidate_paths = _candidate_paths_from_env(env_map)
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
            token_env_names=tokens,
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
        token_env_names=tokens,
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
    env_candidate_paths = _candidate_paths_from_env(env_map)
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
