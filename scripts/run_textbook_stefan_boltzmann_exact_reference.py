"""Run the sandbox-only Stefan-Boltzmann exact-reference software audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physics_lab.engines.stefan_boltzmann import audit_exact_reference_fixture  # noqa: E402

DEFAULT_CONFIG = (
    ROOT
    / "data"
    / "textbook_formula_audit"
    / "textbook_stefan_boltzmann_exact_reference.yaml"
)


def _load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping at top of {path}")
    return payload


def _render_report(metrics: dict[str, Any]) -> str:
    lines = [
        "# Textbook Stefan-Boltzmann exact-reference fixture",
        "",
        f"- Task: `{metrics['task_id']}`",
        f"- Fixture: `{metrics['fixture_id']}`",
        f"- Verdict: `{metrics['verdict']}`",
        "- Boundary: synthetic software/gate fixture only; no empirical audit.",
        "",
        "## Gates",
        "",
        "| gate | status |",
        "| --- | --- |",
    ]
    for name, gate in metrics["gates"].items():
        lines.append(f"| `{name}` | `{gate['status']}` |")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in metrics["limitations"]],
            "",
            "## Output Routing",
            "",
            "- Canonical destination: sandbox output directory and review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)

    metrics = audit_exact_reference_fixture(_load_config(args.config))
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (args.output_dir / "report.md").write_text(
            _render_report(metrics),
            encoding="utf-8",
        )
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0 if metrics["verdict"] == "VALID_IN_RANGE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
