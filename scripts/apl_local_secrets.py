#!/usr/bin/env python3
"""Load local maintainer secrets for key-gated source-acquisition commands.

The helper is intentionally small and cross-platform:

- ``status`` reports only whether required variables are SET / not set.
- ``run`` starts a child process with values loaded from a local env file.

It never prints secret values by itself. The child command is still responsible
for not logging environment contents.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SECRETS_FILENAME = ".apl-local-secrets.env"
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class LocalSecretsError(ValueError):
    """Raised when the local secrets file is malformed."""


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file(path: Path) -> dict[str, str]:
    """Parse a simple dotenv-style file without shell expansion."""
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            raise LocalSecretsError(f"{path}:{line_number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        if not _ENV_NAME.fullmatch(key):
            raise LocalSecretsError(f"{path}:{line_number}: invalid env var name {key!r}")
        values[key] = _strip_quotes(value)
    return values


def resolve_secrets_path(path: Path | None = None) -> Path:
    """Resolve the local secrets path for normal checkouts and worktrees."""
    if path is not None:
        return path

    env_path = os.environ.get("APL_LOCAL_SECRETS_FILE")
    if env_path:
        return Path(env_path)

    local_path = REPO_ROOT / DEFAULT_SECRETS_FILENAME
    if local_path.exists():
        return local_path

    # Agents often run from `.worktrees/<task>` while the maintainer keeps the
    # local secrets file at the main checkout root. Search ancestors so the
    # helper works across those worktrees without copying secrets.
    for parent in REPO_ROOT.parents:
        candidate = parent / DEFAULT_SECRETS_FILENAME
        if candidate.exists():
            return candidate
    return local_path


def merged_env(path: Path | None = None) -> dict[str, str]:
    """Return ``os.environ`` with local secrets added but not overriding shell env."""
    path = resolve_secrets_path(path)
    env = dict(os.environ)
    for key, value in load_env_file(path).items():
        env.setdefault(key, value)
    return env


def status_payload(required: list[str], path: Path | None = None) -> dict[str, str]:
    env = merged_env(path)
    return {name: "SET" if env.get(name) else "not set" for name in required}


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--secrets-file",
        type=Path,
        default=None,
        help=(
            "Local dotenv-style secrets file. Defaults to APL_LOCAL_SECRETS_FILE, "
            "then .apl-local-secrets.env in this checkout or an ancestor checkout."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser(
        "status",
        help="Report whether required variables are SET / not set.",
    )
    _add_common_args(status)
    status.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="ENV_VAR",
        help="Required environment variable to check. May be repeated.",
    )
    status.add_argument("--json", action="store_true")

    run = subparsers.add_parser(
        "run",
        help="Run a child command with local secrets loaded into its environment.",
    )
    _add_common_args(run)
    run.add_argument(
        "child_command",
        nargs=argparse.REMAINDER,
        help="Command to run after `--`.",
    )
    return parser


def cmd_status(args: argparse.Namespace) -> int:
    required = list(args.require)
    if not required:
        print("No --require variables supplied.")
        return 0
    payload = status_payload(required, args.secrets_file)
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for name in required:
            print(f"{name} {payload[name]}")
    return 0 if all(value == "SET" for value in payload.values()) else 2


def _normalise_child_command(command: list[str]) -> list[str]:
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise LocalSecretsError("run requires a child command after `--`")
    return command


def cmd_run(args: argparse.Namespace) -> int:
    command = _normalise_child_command(list(args.child_command))
    completed = subprocess.run(command, env=merged_env(args.secrets_file), check=False)
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            return cmd_status(args)
        if args.command == "run":
            return cmd_run(args)
    except LocalSecretsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
