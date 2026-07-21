"""Bounded read-only GitHub metadata access for APL agent tools."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener, urlopen

from physics_lab.registry.pr_capability import (
    env_with_discovered_tool_paths,
    find_gh_path,
    suspicious_proxy_env_names,
)
from physics_lab.registry.task_occupancy import is_task_claim_issue


CANONICAL_GITHUB_REPOSITORY = "open-agent-science/autonomous-physics-lab"
PUBLIC_GITHUB_API_ROOT = "https://api.github.com"
PUBLIC_GITHUB_API_VERSION = "2026-03-10"
PUBLIC_GITHUB_RESPONSE_LIMIT_BYTES = 4_000_000
PUBLIC_GITHUB_MAX_CHANGED_FILES = 100
PUBLIC_GITHUB_LOW_RATE_LIMIT = 5
DEFAULT_GITHUB_READ_TIMEOUT_SECONDS = 15
PR_METADATA_GH_ATTEMPTS = 2
PR_METADATA_RETRY_SECONDS = 0.5


@dataclass(frozen=True)
class GitHubReadResult:
    """One bounded GitHub read and its provenance."""

    payload: Any | None
    source: str
    diagnostics: tuple[str, ...] = ()
    complete: bool = True

    @property
    def available(self) -> bool:
        return self.payload is not None


class GitHubReadError(RuntimeError):
    """Raised when a bounded public GitHub read cannot be trusted."""


def _diagnostic_excerpt(value: str) -> str:
    """Return a bounded single-line diagnostic without echoing command input."""
    return " ".join(value.strip().split())[:240]


def _gh_failure_is_retryable(*, stdout: str, stderr: str, timed_out: bool) -> bool:
    if timed_out:
        return True
    combined = f"{stdout}\n{stderr}".lower()
    permanent_markers = (
        "401",
        "authentication",
        "auth login",
        "not logged into",
    )
    return not any(marker in combined for marker in permanent_markers)


def _proxy_mapping(env: Mapping[str, str]) -> dict[str, str]:
    """Return urllib proxy settings from an already-sanitized environment."""
    proxies: dict[str, str] = {}
    for scheme in ("http", "https"):
        value = env.get(f"{scheme}_proxy") or env.get(f"{scheme.upper()}_PROXY")
        if value:
            proxies[scheme] = value
    all_proxy = env.get("all_proxy") or env.get("ALL_PROXY")
    if all_proxy:
        proxies.setdefault("http", all_proxy)
        proxies.setdefault("https", all_proxy)
    return proxies


def _task_claim_records(items: list[Any]) -> list[dict[str, Any]]:
    """Normalize and semantically filter a bounded open-issue window."""
    records: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict) or "pull_request" in item:
            continue
        record = {
            "number": item.get("number"),
            "title": item.get("title") or "",
            "body": item.get("body") or "",
            "labels": item.get("labels") or [],
            "url": item.get("html_url") or item.get("url") or "",
        }
        if is_task_claim_issue(record):
            records.append(record)
    return records


class GitHubReadOnlyClient:
    """Use authenticated ``gh`` first, then bounded public REST reads.

    The public cache lives only for this client instance. Agent tools therefore
    share data inside one run without creating a committed or cross-run metadata
    surface that can become stale.
    """

    def __init__(
        self,
        root: Path,
        *,
        env: Mapping[str, str] | None = None,
        gh_path: str | None = None,
        clear_suspicious_proxy: bool = False,
        timeout: int = DEFAULT_GITHUB_READ_TIMEOUT_SECONDS,
    ) -> None:
        self.root = root
        self.timeout = timeout
        source_env = dict(os.environ if env is None else env)
        self._proxy_names = suspicious_proxy_env_names(source_env)
        self._network_blocked = bool(
            self._proxy_names and not clear_suspicious_proxy
        )
        self.env = env_with_discovered_tool_paths(
            source_env,
            clear_suspicious_proxy=clear_suspicious_proxy,
        )
        self.gh_path = gh_path or find_gh_path(env=self.env)
        self._gh_permanent_diagnostics: tuple[str, ...] = ()
        self._public_cache: dict[str, Any] = {}
        self._public_warnings: list[str] = []
        self._explicit_proxy_handler = bool(
            clear_suspicious_proxy and self._proxy_names
        )

    @property
    def public_cache_size(self) -> int:
        """Expose cache size for diagnostics and deterministic tests."""
        return len(self._public_cache)

    @property
    def blocker_diagnostics(self) -> tuple[str, ...]:
        if not self._network_blocked:
            return ()
        return (
            "Live GitHub metadata was not checked because known local blocker "
            "proxy variables are set: "
            + ", ".join(self._proxy_names)
            + ". Retry with --ignore-suspicious-proxy when network access is allowed.",
        )

    def _run_gh_json(
        self,
        arguments: list[str],
        *,
        expected_type: type,
        label: str,
        attempts: int = 1,
        timeout: int | None = None,
    ) -> GitHubReadResult:
        if self._network_blocked:
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=self.blocker_diagnostics,
            )
        if self._gh_permanent_diagnostics:
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=self._gh_permanent_diagnostics,
            )
        if self.gh_path is None:
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=("GitHub CLI `gh` is not installed or discoverable.",),
            )

        diagnostics: list[str] = []
        for attempt in range(1, attempts + 1):
            timed_out = False
            try:
                completed = subprocess.run(
                    [self.gh_path, *arguments],
                    cwd=self.root,
                    check=False,
                    capture_output=True,
                    text=True,
                    shell=False,
                    timeout=timeout or self.timeout,
                    env=dict(self.env),
                )
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                stdout = str(exc.stdout or "")
                stderr = str(exc.stderr or "")
                returncode = -1
                detail = f"timed out after {timeout or self.timeout}s"
            except OSError as exc:
                stdout = ""
                stderr = str(exc)
                returncode = -1
                detail = f"{type(exc).__name__}: {exc}"
            else:
                stdout = completed.stdout
                stderr = completed.stderr
                returncode = completed.returncode
                detail = _diagnostic_excerpt(stderr or stdout)

            if returncode == 0:
                try:
                    payload = json.loads(stdout)
                except json.JSONDecodeError as exc:
                    diagnostics.append(
                        f"{label} attempt {attempt} returned invalid JSON: {exc}"
                    )
                else:
                    if isinstance(payload, expected_type):
                        return GitHubReadResult(
                            payload=payload,
                            source="gh",
                            diagnostics=tuple(diagnostics),
                        )
                    diagnostics.append(
                        f"{label} attempt {attempt} returned an unexpected JSON shape."
                    )
            else:
                diagnostics.append(
                    f"{label} attempt {attempt} failed"
                    + (f": {detail}" if detail else ".")
                )

            if not _gh_failure_is_retryable(
                stdout=stdout,
                stderr=stderr,
                timed_out=timed_out,
            ):
                self._gh_permanent_diagnostics = tuple(diagnostics)
                break
            if attempt < attempts:
                time.sleep(PR_METADATA_RETRY_SECONDS)

        return GitHubReadResult(
            payload=None,
            source="unavailable",
            diagnostics=tuple(diagnostics),
        )

    def public_json(self, path: str) -> Any:
        """Return one trusted public REST payload, cached for this run only."""
        trusted_prefix = f"/repos/{CANONICAL_GITHUB_REPOSITORY}/"
        if not path.startswith(trusted_prefix) or ".." in path:
            raise ValueError(
                "Public GitHub fallback path is outside the canonical repository."
            )
        if self._network_blocked:
            raise GitHubReadError(self.blocker_diagnostics[0])
        if path in self._public_cache:
            return self._public_cache[path]

        request = Request(
            f"{PUBLIC_GITHUB_API_ROOT}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": PUBLIC_GITHUB_API_VERSION,
                "User-Agent": "autonomous-physics-lab-agent-tools",
            },
        )
        try:
            if self._explicit_proxy_handler:
                opener = build_opener(ProxyHandler(_proxy_mapping(self.env)))
                response_context = opener.open(request, timeout=self.timeout)
            else:
                response_context = urlopen(  # noqa: S310 - fixed trusted host
                    request,
                    timeout=self.timeout,
                )
            with response_context as response:
                payload_bytes = response.read(PUBLIC_GITHUB_RESPONSE_LIMIT_BYTES + 1)
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset", "unknown")
        except HTTPError as exc:
            remaining = exc.headers.get("X-RateLimit-Remaining", "unknown")
            reset = exc.headers.get("X-RateLimit-Reset", "unknown")
            raise GitHubReadError(
                f"public GitHub REST returned HTTP {exc.code} "
                f"(rate remaining={remaining}, reset={reset})"
            ) from exc
        except (OSError, TimeoutError, URLError) as exc:
            raise GitHubReadError(
                f"public GitHub REST request failed: {exc}"
            ) from exc

        if len(payload_bytes) > PUBLIC_GITHUB_RESPONSE_LIMIT_BYTES:
            raise GitHubReadError(
                "public GitHub REST response exceeded the bounded size limit"
            )
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubReadError("public GitHub REST returned invalid JSON") from exc

        if remaining is not None:
            try:
                remaining_count = int(remaining)
            except (TypeError, ValueError):
                remaining_count = PUBLIC_GITHUB_LOW_RATE_LIMIT + 1
            if remaining_count <= PUBLIC_GITHUB_LOW_RATE_LIMIT:
                self._public_warnings.append(
                    "Public GitHub REST rate limit is low "
                    f"(remaining={remaining_count}, reset={reset}); later reads may "
                    "degrade to local registry-only metadata."
                )

        self._public_cache[path] = payload
        return payload

    def _public_result(self, path: str) -> GitHubReadResult:
        try:
            payload = self.public_json(path)
        except (GitHubReadError, TypeError, ValueError) as exc:
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=(f"Public GitHub REST fallback failed: {exc}",),
            )
        return GitHubReadResult(
            payload=payload,
            source="public_rest",
            diagnostics=tuple(dict.fromkeys(self._public_warnings)),
        )

    def list_pull_requests(self, *, limit: int = 100) -> GitHubReadResult:
        """List the bounded PR window used for task occupancy."""
        if not 1 <= limit <= 100:
            raise ValueError("GitHub PR list limit must be between 1 and 100.")
        gh_result = self._run_gh_json(
            [
                "pr",
                "list",
                "--state",
                "all",
                "--limit",
                str(limit),
                "--json",
                "number,title,body,state,mergedAt,headRefName,url,isDraft",
            ],
            expected_type=list,
            label="gh pr list",
            timeout=max(self.timeout, 20),
        )
        if gh_result.available:
            return GitHubReadResult(
                payload=[item for item in gh_result.payload if isinstance(item, dict)],
                source="gh",
                diagnostics=gh_result.diagnostics,
            )

        public_result = self._public_result(
            f"/repos/{CANONICAL_GITHUB_REPOSITORY}/pulls"
            f"?state=all&sort=updated&direction=desc&per_page={limit}"
        )
        diagnostics = tuple(
            dict.fromkeys((*gh_result.diagnostics, *public_result.diagnostics))
        )
        if not isinstance(public_result.payload, list):
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=diagnostics
                + (("Public GitHub pull-request list was not a JSON list.",) if public_result.available else ()),
            )

        records: list[dict[str, Any]] = []
        for item in public_result.payload:
            if not isinstance(item, dict):
                continue
            head = item.get("head") or {}
            merged_at = item.get("merged_at")
            records.append(
                {
                    "number": item.get("number"),
                    "title": item.get("title") or "",
                    "body": item.get("body") or "",
                    "state": "MERGED" if merged_at else str(item.get("state") or "").upper(),
                    "mergedAt": merged_at,
                    "headRefName": head.get("ref") if isinstance(head, dict) else "",
                    "url": item.get("html_url") or "",
                    "isDraft": bool(item.get("draft")),
                }
            )
        return GitHubReadResult(
            payload=records,
            source="public_rest",
            diagnostics=diagnostics,
        )

    def list_task_claims(self, *, limit: int = 100) -> GitHubReadResult:
        """List semantically identified open task claims through the shared path."""
        if not 1 <= limit <= 100:
            raise ValueError("GitHub issue list limit must be between 1 and 100.")
        # Labels are advisory. Query one bounded open-issue window and apply the
        # same title/body semantics used by claim closeout instead of hiding an
        # otherwise valid claim when the issue-template labels were not applied.
        gh_result = self._run_gh_json(
            [
                "issue",
                "list",
                "--state",
                "open",
                "--limit",
                str(limit),
                "--json",
                "number,title,body,labels,url",
            ],
            expected_type=list,
            label="gh issue list",
            timeout=max(self.timeout, 20),
        )
        if gh_result.available:
            return GitHubReadResult(
                payload=_task_claim_records(gh_result.payload),
                source="gh",
                diagnostics=gh_result.diagnostics,
            )

        public_result = self._public_result(
            f"/repos/{CANONICAL_GITHUB_REPOSITORY}/issues"
            f"?state=open&sort=updated&direction=desc&per_page={limit}"
        )
        diagnostics = tuple(
            dict.fromkeys((*gh_result.diagnostics, *public_result.diagnostics))
        )
        if not isinstance(public_result.payload, list):
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=diagnostics
                + (("Public GitHub task-claim list was not a JSON list.",) if public_result.available else ()),
            )
        return GitHubReadResult(
            payload=_task_claim_records(public_result.payload),
            source="public_rest",
            diagnostics=diagnostics,
        )

    def load_pull_request(
        self,
        number: int,
        *,
        max_changed_files: int = PUBLIC_GITHUB_MAX_CHANGED_FILES,
    ) -> GitHubReadResult:
        """Load complete PR metadata, preserving an explicit partial fallback."""
        if number <= 0:
            raise ValueError("Pull-request number must be positive.")
        gh_result = self._run_gh_json(
            [
                "pr",
                "view",
                str(number),
                "--json",
                "number,title,body,headRefName,headRefOid,baseRefName,state,mergedAt,statusCheckRollup,files",
            ],
            expected_type=dict,
            label="gh pr view",
            attempts=PR_METADATA_GH_ATTEMPTS,
            timeout=max(self.timeout, 30),
        )
        if gh_result.available:
            return GitHubReadResult(
                payload=gh_result.payload,
                source="gh_view",
                diagnostics=gh_result.diagnostics,
            )

        public_result = self._load_public_pull_request(
            number,
            max_changed_files=max_changed_files,
        )
        diagnostics = tuple(
            dict.fromkeys((*gh_result.diagnostics, *public_result.diagnostics))
        )
        if public_result.available:
            return GitHubReadResult(
                payload=public_result.payload,
                source="public_rest",
                diagnostics=diagnostics,
            )

        partial_result = self._run_gh_json(
            [
                "pr",
                "list",
                "--state",
                "all",
                "--limit",
                "200",
                "--json",
                "number,title,headRefName,headRefOid,baseRefName,state,mergedAt,statusCheckRollup",
            ],
            expected_type=list,
            label="gh pr list",
            timeout=max(self.timeout, 60),
        )
        diagnostics = tuple(
            dict.fromkeys((*diagnostics, *partial_result.diagnostics))
        )
        if partial_result.available:
            for row in partial_result.payload:
                if isinstance(row, dict) and int(row.get("number") or -1) == number:
                    return GitHubReadResult(
                        payload=row,
                        source="gh_list",
                        diagnostics=diagnostics
                        + (
                            "Only partial gh pr list metadata was available; PR body "
                            "and files were not verified.",
                        ),
                        complete=False,
                    )
        return GitHubReadResult(
            payload=None,
            source="unavailable",
            diagnostics=diagnostics,
        )

    def _load_public_pull_request(
        self,
        number: int,
        *,
        max_changed_files: int,
    ) -> GitHubReadResult:
        pull_path = f"/repos/{CANONICAL_GITHUB_REPOSITORY}/pulls/{number}"
        try:
            pull_payload = self.public_json(pull_path)
            if not isinstance(pull_payload, dict):
                raise GitHubReadError("public pull-request response was not an object")
            returned_number = int(pull_payload.get("number") or -1)
            if returned_number != number:
                raise GitHubReadError(
                    f"public pull-request number mismatch: expected {number}, "
                    f"got {returned_number}"
                )
            head = pull_payload.get("head") or {}
            base = pull_payload.get("base") or {}
            if not isinstance(head, dict) or not isinstance(base, dict):
                raise GitHubReadError(
                    "public pull-request response omitted head/base metadata"
                )
            head_sha = str(head.get("sha") or "").strip()
            if len(head_sha) not in range(40, 65) or any(
                character not in "0123456789abcdefABCDEF" for character in head_sha
            ):
                raise GitHubReadError(
                    "public pull-request response omitted a valid head SHA"
                )
            changed_file_count = int(pull_payload.get("changed_files") or 0)
            if changed_file_count > max_changed_files:
                raise GitHubReadError(
                    "public fallback refuses PRs with more than "
                    f"{max_changed_files} changed files"
                )

            files_payload = self.public_json(
                f"{pull_path}/files?per_page={max_changed_files}"
            )
            if not isinstance(files_payload, list):
                raise GitHubReadError("public changed-files response was not a list")
            if len(files_payload) != changed_file_count:
                raise GitHubReadError(
                    "public changed-files response was incomplete: "
                    f"expected {changed_file_count}, got {len(files_payload)}"
                )

            checks_payload = self.public_json(
                f"/repos/{CANONICAL_GITHUB_REPOSITORY}/commits/{head_sha}/check-runs"
                "?filter=latest&per_page=100"
            )
            if not isinstance(checks_payload, dict):
                raise GitHubReadError("public check-runs response was not an object")
            check_runs = checks_payload.get("check_runs") or []
            if not isinstance(check_runs, list):
                raise GitHubReadError(
                    "public check-runs response omitted the check_runs list"
                )
            check_run_count = int(checks_payload.get("total_count") or 0)
            if check_run_count != len(check_runs):
                raise GitHubReadError(
                    "public check-runs response was incomplete: "
                    f"expected {check_run_count}, got {len(check_runs)}"
                )
        except (GitHubReadError, TypeError, ValueError) as exc:
            return GitHubReadResult(
                payload=None,
                source="unavailable",
                diagnostics=(f"Public GitHub REST fallback failed: {exc}",),
            )

        normalized_payload = {
            "number": returned_number,
            "title": pull_payload.get("title") or "",
            "body": pull_payload.get("body") or "",
            "headRefName": head.get("ref") or "",
            "headRefOid": head_sha,
            "baseRefName": base.get("ref") or "main",
            "state": str(pull_payload.get("state") or "").upper(),
            "mergedAt": pull_payload.get("merged_at"),
            "files": [
                {"path": item.get("filename") or ""}
                for item in files_payload
                if isinstance(item, dict)
            ],
            "statusCheckRollup": [
                {
                    "name": item.get("name") or "",
                    "status": item.get("status") or "",
                    "conclusion": item.get("conclusion") or "",
                    "startedAt": item.get("started_at") or "",
                    "completedAt": item.get("completed_at") or "",
                }
                for item in check_runs
                if isinstance(item, dict)
            ],
        }
        return GitHubReadResult(
            payload=normalized_payload,
            source="public_rest",
            diagnostics=tuple(dict.fromkeys(self._public_warnings)),
        )
