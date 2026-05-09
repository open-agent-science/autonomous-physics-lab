#!/usr/bin/env python3
"""Replay the bounded core APL result surface into a temporary output tree."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = Path("/tmp/apl-core-reproduction")


@dataclass(frozen=True)
class CoreReplay:
    key: str
    title: str
    config_path: str
    experiment_id: str
    run_id: str
    result_id: str
    expected_verdicts: tuple[str, ...]
    rationale: str

    @property
    def result_path_parts(self) -> tuple[str, str, str]:
        return (self.experiment_id, self.run_id, "result.yaml")


@dataclass(frozen=True)
class ReplayReport:
    replay: CoreReplay
    command: tuple[str, ...]
    result_path: Path
    status: str
    verdict: str | None
    message: str


CORE_REPLAYS: tuple[CoreReplay, ...] = (
    CoreReplay(
        key="pendulum-gauntlet",
        title="Pendulum Gauntlet 100",
        config_path="examples/pendulum_gauntlet.yaml",
        experiment_id="EXP-0001",
        run_id="RUN-0003",
        result_id="RESULT-0004",
        expected_verdicts=("VALID_IN_RANGE",),
        rationale="strongest classical-mechanics benchmark package",
    ),
    CoreReplay(
        key="dimensional-analysis",
        title="Dimensional Analysis Validator MVP",
        config_path="examples/dimensional_analysis.yaml",
        experiment_id="EXP-0006",
        run_id="RUN-0006",
        result_id="RESULT-0007",
        expected_verdicts=("VALID",),
        rationale="frozen 50-item dimensional-analysis benchmark",
    ),
    CoreReplay(
        key="koide-charged-lepton",
        title="Charged-Lepton Koide Reproduction",
        config_path="examples/koide_charged_lepton.yaml",
        experiment_id="EXP-0004",
        run_id="RUN-0004",
        result_id="RESULT-0005",
        expected_verdicts=("VALID",),
        rationale="scoped charged-lepton reproduction benchmark",
    ),
    CoreReplay(
        key="koide-tau-holdout",
        title="Historical Tau Holdout",
        config_path="examples/koide_tau_holdout.yaml",
        experiment_id="EXP-0005",
        run_id="RUN-0005",
        result_id="RESULT-0006",
        expected_verdicts=("VALID", "VALID_IN_RANGE"),
        rationale="historical holdout-style tau benchmark",
    ),
    CoreReplay(
        key="koide-neutrino-falsification",
        title="Koide Neutrino Falsification",
        config_path="examples/koide_neutrino.yaml",
        experiment_id="EXP-0007",
        run_id="RUN-0001",
        result_id="RESULT-0009",
        expected_verdicts=("INVALID",),
        rationale="first-class negative particle-mass result",
    ),
    CoreReplay(
        key="koide-quark-falsification",
        title="Quark Koide Cascade Falsification",
        config_path="examples/koide_quark.yaml",
        experiment_id="EXP-0008",
        run_id="RUN-0001",
        result_id="RESULT-0010",
        expected_verdicts=("INVALID",),
        rationale="quark-sector negative result under stored assumptions",
    ),
    CoreReplay(
        key="particle-mass-falsifier",
        title="Particle-Mass Relation Falsifier MVP",
        config_path="examples/particle_mass_falsifier.yaml",
        experiment_id="EXP-0009",
        run_id="RUN-0001",
        result_id="RESULT-0011",
        expected_verdicts=("INVALID",),
        rationale="fixed-target falsifier workflow with uncertainty propagation",
    ),
)


SKIPPED_BY_DESIGN: tuple[str, ...] = (
    "EXP-0010 / Muon g-2 formula search is intentionally excluded from the default "
    "core replay. It remains a guarded empirical formula-search stress test, not "
    "a public success story.",
    "Earlier baseline runs and follow-up pendulum variants remain canonical but "
    "are not part of this bounded public-facing core replay.",
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay APL's bounded core result surface into a temporary output tree "
            "without modifying canonical results/ artifacts."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Base output directory for regenerated artifacts. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--only",
        action="append",
        choices=[replay.key for replay in CORE_REPLAYS],
        help="Replay only the named core slice. May be supplied multiple times.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue replaying later slices after a failure and report all failures at the end.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the bounded default replay scope without running experiments.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used for CLI replay subprocesses.",
    )
    return parser.parse_args(argv)


def select_replays(keys: Iterable[str] | None) -> tuple[CoreReplay, ...]:
    if not keys:
        return CORE_REPLAYS
    requested = set(keys)
    return tuple(replay for replay in CORE_REPLAYS if replay.key in requested)


def command_for(replay: CoreReplay, output_dir: Path, python_executable: str) -> tuple[str, ...]:
    return (
        python_executable,
        "-m",
        "physics_lab.cli",
        "run",
        replay.config_path,
        "--output-dir",
        str(output_dir),
    )


def resolve_result_path(replay: CoreReplay, run_output_dir: Path) -> Path:
    nested_path = run_output_dir.joinpath(*replay.result_path_parts)
    if nested_path.exists():
        return nested_path
    flat_path = run_output_dir / "result.yaml"
    if flat_path.exists():
        return flat_path
    return nested_path


def load_result(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


def validate_replay_output(replay: CoreReplay, result_path: Path) -> tuple[str, str]:
    if not result_path.exists():
        return ("FAIL", f"missing result artifact: {result_path}")

    try:
        result = load_result(result_path)
    except Exception as exc:
        return ("FAIL", f"could not read result artifact: {exc}")

    actual_result_id = result.get("result_id")
    actual_verdict = result.get("best_verdict")
    if actual_result_id != replay.result_id:
        return ("FAIL", f"expected result_id {replay.result_id}, observed {actual_result_id}")
    if actual_verdict not in replay.expected_verdicts:
        expected = ", ".join(replay.expected_verdicts)
        return ("FAIL", f"expected verdict in [{expected}], observed {actual_verdict}")
    return ("PASS", f"result_id {actual_result_id}, verdict {actual_verdict}")


def run_replay(
    replay: CoreReplay,
    *,
    output_dir: Path,
    python_executable: str,
) -> ReplayReport:
    run_output_dir = output_dir / replay.key
    run_output_dir.mkdir(parents=True, exist_ok=True)
    command = command_for(replay, run_output_dir, python_executable)
    result_path = run_output_dir.joinpath(*replay.result_path_parts)
    print(f"\n==> {replay.key}: {replay.title}", flush=True)
    print(f"$ {' '.join(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="", flush=True)
    if completed.returncode != 0:
        return ReplayReport(
            replay=replay,
            command=command,
            result_path=resolve_result_path(replay, run_output_dir),
            status="FAIL",
            verdict=None,
            message=f"command exited with code {completed.returncode}",
        )

    result_path = resolve_result_path(replay, run_output_dir)
    status, message = validate_replay_output(replay, result_path)
    verdict = None
    if result_path.exists():
        try:
            verdict = str(load_result(result_path).get("best_verdict"))
        except Exception:
            verdict = None
    return ReplayReport(
        replay=replay,
        command=command,
        result_path=result_path,
        status=status,
        verdict=verdict,
        message=message,
    )


def render_summary(reports: Iterable[ReplayReport], output_dir: Path) -> str:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# APL Core Reproduction Summary",
        "",
        f"Generated at: `{generated_at}`",
        f"Output directory: `{output_dir}`",
        "",
        "This replay covers the bounded current major result surface. It does not "
        "rewrite canonical artifacts under `results/`.",
        "",
        "## Included Replay Slices",
        "",
        "| Status | Key | Result | Verdict | Artifact |",
        "|---|---|---|---|---|",
    ]
    for report in reports:
        result_label = f"{report.replay.experiment_id}/{report.replay.run_id} ({report.replay.result_id})"
        artifact = report.result_path.as_posix()
        verdict = report.verdict or "n/a"
        lines.append(
            f"| {report.status} | `{report.replay.key}` | `{result_label}` | `{verdict}` | `{artifact}` |"
        )

    lines.extend(
        [
            "",
            "## Skipped By Design",
            "",
            *[f"- {item}" for item in SKIPPED_BY_DESIGN],
            "",
            "## Notes",
            "",
            "- Compare scientific metrics and verdicts, not generated timestamps or absolute paths.",
            "- For detailed expected metrics and caveats, see `docs/reproducibility-capsules.md`.",
            "- Any `FAIL` row should be treated as reviewer-visible evidence, not hidden.",
            "",
        ]
    )
    return "\n".join(lines)


def print_scope(replays: Iterable[CoreReplay]) -> None:
    print("Bounded core replay scope:")
    for replay in replays:
        expected = ", ".join(replay.expected_verdicts)
        print(f"- {replay.key}: {replay.result_id}, expected verdict {expected}")
    print("\nSkipped by design:")
    for item in SKIPPED_BY_DESIGN:
        print(f"- {item}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    replays = select_replays(args.only)
    if args.list:
        print_scope(replays)
        return 0

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    reports: list[ReplayReport] = []
    for replay in replays:
        report = run_replay(
            replay,
            output_dir=output_dir,
            python_executable=args.python,
        )
        reports.append(report)
        print(f"{report.status}: {report.message}", flush=True)
        if report.status != "PASS" and not args.continue_on_failure:
            break

    summary_text = render_summary(reports, output_dir)
    summary_path = output_dir / "CORE_REPRODUCTION_SUMMARY.md"
    summary_path.write_text(summary_text, encoding="utf-8")
    print(f"\nSummary: {summary_path}")

    failures = [report for report in reports if report.status != "PASS"]
    if failures:
        print(f"Core reproduction completed with {len(failures)} failure(s).")
        return 1
    print("Core reproduction PASS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
