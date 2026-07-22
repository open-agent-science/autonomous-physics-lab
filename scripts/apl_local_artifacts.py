#!/usr/bin/env python3
"""Resolve private source inputs and shared task-local APL work directories.

The helper performs exact lookups only. It does not scan a home directory,
list a private source vault, fetch data, or change publication rights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_SOURCE_ROOT_ENV = "APL_PRIVATE_SOURCE_ROOT"
LOCAL_WORK_ROOT_ENV = "APL_LOCAL_WORK_ROOT"
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_TASK_ID_RE = re.compile(r"^TASK-[0-9]{4,}$")
_RUN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class LocalArtifactError(ValueError):
    """Raised when a local artifact request is unsafe or cannot be resolved."""


def primary_checkout_root(repo_root: Path = REPO_ROOT) -> Path:
    """Return the primary checkout shared by linked git worktrees."""
    commands = (
        [
            "git",
            "-C",
            str(repo_root),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        ["git", "-C", str(repo_root), "rev-parse", "--git-common-dir"],
    )
    completed: subprocess.CompletedProcess[str] | None = None
    for command in commands:
        try:
            candidate = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except OSError:
            break
        if candidate.returncode == 0 and candidate.stdout.strip():
            completed = candidate
            break
    if completed is None:
        return repo_root.resolve()

    common_dir = Path(completed.stdout.strip()).expanduser()
    if not common_dir.is_absolute():
        common_dir = repo_root / common_dir
    common_dir = common_dir.resolve()
    if common_dir.name == ".git":
        return common_dir.parent
    return repo_root.resolve()


def _absolute_root(raw_path: str | Path, *, label: str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        raise LocalArtifactError(f"{label} must be an absolute path: {raw_path}")
    return path.resolve()


def _resolve_root(
    *,
    explicit: str | Path | None,
    env_name: str,
    suffix: str,
    cli_label: str,
    repo_root: Path = REPO_ROOT,
) -> tuple[Path, str]:
    if explicit is not None:
        return _absolute_root(explicit, label=cli_label), "cli"
    env_value = os.environ.get(env_name)
    if env_value:
        return _absolute_root(env_value, label=env_name), "environment"
    primary = primary_checkout_root(repo_root)
    return primary.with_name(f"{primary.name}{suffix}"), "default"


def resolve_private_source_root(
    explicit: str | Path | None = None,
    *,
    repo_root: Path = REPO_ROOT,
) -> tuple[Path, str]:
    return _resolve_root(
        explicit=explicit,
        env_name=PRIVATE_SOURCE_ROOT_ENV,
        suffix="-private-sources",
        cli_label="--private-source-root",
        repo_root=repo_root,
    )


def resolve_local_work_root(
    explicit: str | Path | None = None,
    *,
    repo_root: Path = REPO_ROOT,
) -> tuple[Path, str]:
    return _resolve_root(
        explicit=explicit,
        env_name=LOCAL_WORK_ROOT_ENV,
        suffix="-local-work",
        cli_label="--local-work-root",
        repo_root=repo_root,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_sha256(value: str) -> str:
    if not _SHA256_RE.fullmatch(value):
        raise LocalArtifactError("--sha256 must be a 64-character hexadecimal digest")
    return value.lower()


def _validate_filename(filename: str) -> str:
    if (
        not filename
        or filename in {".", ".."}
        or PurePosixPath(filename).name != filename
        or PureWindowsPath(filename).name != filename
    ):
        raise LocalArtifactError("--filename must be one exact basename, not a path")
    return filename


def _validate_source_id(source_id: str | None) -> str | None:
    if source_id is not None and not _SOURCE_ID_RE.fullmatch(source_id):
        raise LocalArtifactError(
            "--source-id must use lowercase letters, digits, dots, underscores, or hyphens"
        )
    return source_id


def _verify_file(path: Path, expected_sha256: str) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise LocalArtifactError(f"source file not found: {path}")
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise LocalArtifactError(
            f"checksum mismatch for {path.name}: expected {expected_sha256}, got {actual_sha256}"
        )
    return {
        "path": str(path),
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": actual_sha256,
    }


def locate_source(
    *,
    filename: str | None,
    expected_sha256: str,
    source_id: str | None = None,
    explicit_input: str | Path | None = None,
    private_source_root: str | Path | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Locate one exact source file and verify its pinned checksum."""
    expected = _normalise_sha256(expected_sha256)
    source_id = _validate_source_id(source_id)

    if explicit_input is not None:
        path = _absolute_root(explicit_input, label="--input")
        if filename is not None and path.name != _validate_filename(filename):
            raise LocalArtifactError(
                f"explicit input basename {path.name!r} does not match --filename {filename!r}"
            )
        payload = _verify_file(path, expected)
        payload.update({"source_id": source_id, "layout": "explicit", "root_origin": "input"})
        return payload

    if filename is None:
        raise LocalArtifactError("--filename is required when --input is not supplied")
    filename = _validate_filename(filename)
    root, root_origin = resolve_private_source_root(
        private_source_root,
        repo_root=repo_root,
    )
    candidates: list[tuple[Path, str]] = []
    if source_id is not None:
        candidates.append((root / source_id / filename, "source_scoped"))
    candidates.append((root / filename, "legacy_root"))

    resolved_root = root.resolve()
    for candidate, layout in candidates:
        if not candidate.exists() or not candidate.is_file():
            continue
        resolved_candidate = candidate.resolve()
        if not resolved_candidate.is_relative_to(resolved_root):
            raise LocalArtifactError(
                f"source candidate resolves outside the private source root: {candidate}"
            )
        payload = _verify_file(resolved_candidate, expected)
        payload.update(
            {
                "source_id": source_id,
                "layout": layout,
                "root_origin": root_origin,
            }
        )
        return payload

    attempted = ", ".join(str(path) for path, _ in candidates)
    raise LocalArtifactError(f"source file not found; exact paths checked: {attempted}")


def resolve_task_workdir(
    *,
    task_id: str,
    run_id: str = "primary",
    local_work_root: str | Path | None = None,
    create: bool = False,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    if not _TASK_ID_RE.fullmatch(task_id):
        raise LocalArtifactError("--task must match TASK- followed by at least four digits")
    if not _RUN_ID_RE.fullmatch(run_id):
        raise LocalArtifactError(
            "--run must use lowercase letters, digits, dots, underscores, or hyphens"
        )
    root, root_origin = resolve_local_work_root(local_work_root, repo_root=repo_root)
    workdir = root / task_id / run_id
    if create:
        workdir.mkdir(parents=True, exist_ok=True)
    return {
        "path": str(workdir),
        "task_id": task_id,
        "run_id": run_id,
        "created": create,
        "exists": workdir.is_dir(),
        "root_origin": root_origin,
    }


def roots_payload(
    *,
    private_source_root: str | Path | None = None,
    local_work_root: str | Path | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    private_root, private_origin = resolve_private_source_root(
        private_source_root,
        repo_root=repo_root,
    )
    work_root, work_origin = resolve_local_work_root(
        local_work_root,
        repo_root=repo_root,
    )
    return {
        "primary_checkout": str(primary_checkout_root(repo_root)),
        "private_source_root": str(private_root),
        "private_source_root_exists": private_root.is_dir(),
        "private_source_root_origin": private_origin,
        "local_work_root": str(work_root),
        "local_work_root_exists": work_root.is_dir(),
        "local_work_root_origin": work_origin,
    }


def _print_payload(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    roots = subparsers.add_parser("roots", help="Show resolved local roots without creating them.")
    roots.add_argument("--private-source-root")
    roots.add_argument("--local-work-root")
    roots.add_argument("--json", action="store_true")

    locate = subparsers.add_parser(
        "locate",
        help="Locate one exact private source and verify its SHA-256 checksum.",
    )
    locate.add_argument("--input", help="Explicit absolute source path; highest precedence.")
    locate.add_argument("--private-source-root", help="Explicit absolute private-source root.")
    locate.add_argument("--source-id")
    locate.add_argument("--filename")
    locate.add_argument("--sha256", required=True)
    locate.add_argument("--json", action="store_true")

    workdir = subparsers.add_parser("workdir", help="Resolve one task/run local work directory.")
    workdir.add_argument("--task", required=True)
    workdir.add_argument("--run", default="primary")
    workdir.add_argument("--local-work-root")
    workdir.add_argument("--create", action="store_true")
    workdir.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "roots":
            payload = roots_payload(
                private_source_root=args.private_source_root,
                local_work_root=args.local_work_root,
            )
        elif args.command == "locate":
            payload = locate_source(
                filename=args.filename,
                expected_sha256=args.sha256,
                source_id=args.source_id,
                explicit_input=args.input,
                private_source_root=args.private_source_root,
            )
            payload = {"status": "FOUND", **payload}
        elif args.command == "workdir":
            payload = resolve_task_workdir(
                task_id=args.task,
                run_id=args.run,
                local_work_root=args.local_work_root,
                create=args.create,
            )
        else:
            parser.error(f"unknown command: {args.command}")
            return 2
    except LocalArtifactError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _print_payload(payload, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
