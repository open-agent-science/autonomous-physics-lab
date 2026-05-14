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
    resolved_gh_path = gh_path if gh_path is not None else (
        find_gh_path(candidate_paths=candidate_paths) if discover_gh else None
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
) -> str | None:
    """Find GitHub CLI even when Codex PATH omits Homebrew directories."""
    discovered = shutil.which("gh")
    if discovered is not None:
        return discovered
    for candidate in candidate_paths:
        path = Path(candidate)
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    return None
