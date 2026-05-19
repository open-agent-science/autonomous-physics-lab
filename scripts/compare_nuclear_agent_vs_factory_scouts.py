#!/usr/bin/env python3
"""Compare nuclear agent scout runs with deterministic factory slate reviews.

The comparison reads committed repository artifacts only. It does not fetch
external measurements, generate new prediction values, write registry entries,
or compare frozen predictions against future data.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]

AGENT_METRIC_PATHS = [
    Path("agent_runs/AGENT-RUN-0016/metrics.json"),
    Path("agent_runs/AGENT-RUN-0017/metrics.json"),
    Path("agent_runs/AGENT-RUN-0015/metrics.json"),
]

SLATE_001_REVIEW = Path("docs/reviews/nuclear-prediction-factory-slate-001.md")
SLATE_002_REVIEW = Path("docs/reviews/nuclear-prediction-factory-slate-002-feature-terms.md")
SLATE_002_RANKING = Path(
    "docs/reviews/nuclear-prediction-factory-slate-002-feature-terms-ranking.md"
)


@dataclass(frozen=True)
class AgentLaneSummary:
    agent_run_id: str
    task_id: str
    lane: str
    generated: int
    executed: int
    rejected: int
    verdict_counts: Counter[str]
    best_primary_delta: float | None
    worst_primary_delta: float | None
    negative_primary_count: int
    zero_primary_count: int
    positive_primary_count: int
    near_null_control_preserved: bool


@dataclass(frozen=True)
class AgentAggregate:
    lanes: list[AgentLaneSummary]
    generated: int
    executed: int
    rejected: int
    verdict_counts: Counter[str]
    negative_primary_count: int
    zero_primary_count: int
    positive_primary_count: int
    best_primary_delta: float
    worst_primary_delta: float
    near_null_controls: int
    rejection_reason_counts: Counter[str]


@dataclass(frozen=True)
class FactorySlateSummary:
    slate_id: str
    candidates: int
    advisory_flags: int
    extreme_sensitivity_flags: int
    all_zero_flags: int
    redundant_target_batch_flags: int
    largest_max_abs_delta_mev: float | None


@dataclass(frozen=True)
class FactoryAggregate:
    slates: list[FactorySlateSummary]
    candidates: int
    advisory_flags: int
    extreme_sensitivity_flags: int
    all_zero_flags: int
    redundant_target_batch_flags: int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_REPO_ROOT,
        help="Repository root. Defaults to the checkout containing this script.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional markdown output path.",
    )
    return parser


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _primary_delta(item: dict[str, object]) -> float | None:
    value = item.get("primary_delta_mae_mev")
    if isinstance(value, int | float):
        return float(value)
    deltas = item.get("delta_mae_by_subset_mev")
    if isinstance(deltas, dict):
        primary = deltas.get("primary")
        if isinstance(primary, int | float):
            return float(primary)
    return None


def _classify_rejection(reason: str) -> str:
    lowered = reason.lower()
    if "free" in lowered or "nonlinear" in lowered or "sigma" in lowered:
        return "extra_free_knob"
    if "duplicate" in lowered or "re-running" in lowered:
        return "duplicate_search_or_overlap"
    if "degree" in lowered or "coefficients" in lowered or "bin" in lowered:
        return "degree_of_freedom_inflation"
    if "per-z" in lowered or "memorize" in lowered or "row" in lowered:
        return "row_memorization_or_per-row_fit"
    return "other_overfit_boundary"


def summarize_agent_runs(repo_root: Path) -> AgentAggregate:
    lanes: list[AgentLaneSummary] = []
    verdict_counts: Counter[str] = Counter()
    rejection_reason_counts: Counter[str] = Counter()
    all_primary_deltas: list[float] = []
    negative_primary_count = 0
    zero_primary_count = 0
    positive_primary_count = 0

    for relative_path in AGENT_METRIC_PATHS:
        payload = _read_json(repo_root / relative_path)
        summary = payload["summary"]
        executed_items = payload.get("executed_items", [])
        if not isinstance(executed_items, list):
            raise TypeError(f"executed_items must be a list in {relative_path}")

        lane_primary_deltas: list[float] = []
        lane_negative = 0
        lane_zero = 0
        lane_positive = 0
        for item in executed_items:
            if not isinstance(item, dict):
                continue
            delta = _primary_delta(item)
            if delta is None:
                continue
            lane_primary_deltas.append(delta)
            all_primary_deltas.append(delta)
            if delta < -1e-9:
                lane_negative += 1
                negative_primary_count += 1
            elif delta > 1e-9:
                lane_positive += 1
                positive_primary_count += 1
            else:
                lane_zero += 1
                zero_primary_count += 1

        lane_verdicts = Counter(
            {
                str(key): int(value)
                for key, value in dict(summary["verdict_counts"]).items()
            }
        )
        verdict_counts.update(lane_verdicts)

        for rejected in payload.get("rejected_before_execution", []):
            if isinstance(rejected, dict):
                reason = str(rejected.get("rejection_reason", ""))
                rejection_reason_counts[_classify_rejection(reason)] += 1

        lanes.append(
            AgentLaneSummary(
                agent_run_id=str(payload["agent_run_id"]),
                task_id=str(payload["task_id"]),
                lane=str(payload["lane"]),
                generated=int(summary["generated_candidate_count"]),
                executed=int(summary["executed_candidate_count"]),
                rejected=int(summary["rejected_before_execution_count"]),
                verdict_counts=lane_verdicts,
                best_primary_delta=min(lane_primary_deltas) if lane_primary_deltas else None,
                worst_primary_delta=max(lane_primary_deltas) if lane_primary_deltas else None,
                negative_primary_count=lane_negative,
                zero_primary_count=lane_zero,
                positive_primary_count=lane_positive,
                near_null_control_preserved=bool(summary["near_null_control_preserved"]),
            )
        )

    if not all_primary_deltas:
        raise ValueError("No primary deltas found in agent metrics.")

    return AgentAggregate(
        lanes=lanes,
        generated=sum(lane.generated for lane in lanes),
        executed=sum(lane.executed for lane in lanes),
        rejected=sum(lane.rejected for lane in lanes),
        verdict_counts=verdict_counts,
        negative_primary_count=negative_primary_count,
        zero_primary_count=zero_primary_count,
        positive_primary_count=positive_primary_count,
        best_primary_delta=min(all_primary_deltas),
        worst_primary_delta=max(all_primary_deltas),
        near_null_controls=sum(1 for lane in lanes if lane.near_null_control_preserved),
        rejection_reason_counts=rejection_reason_counts,
    )


def _first_float_after_pipe(markdown: str) -> float | None:
    values: list[float] = []
    for line in markdown.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        try:
            values.append(float(cells[2]))
        except ValueError:
            continue
    return max(values) if values else None


def summarize_factory_slates(repo_root: Path) -> FactoryAggregate:
    slate_001_text = _read_text(repo_root / SLATE_001_REVIEW)
    slate_002_text = _read_text(repo_root / SLATE_002_REVIEW)
    slate_002_ranking = _read_text(repo_root / SLATE_002_RANKING)

    slate_001_candidate = re.search(r"\*\*Candidate count:\*\*\s*(\d+)", slate_001_text)
    slate_002_candidate = re.search(r"\*\*Candidates:\*\*\s*(\d+)", slate_002_ranking)
    if slate_001_candidate is None or slate_002_candidate is None:
        raise ValueError("Could not parse factory candidate counts.")

    slate_001 = FactorySlateSummary(
        slate_id="slate-001 coefficient transforms",
        candidates=int(slate_001_candidate.group(1)),
        advisory_flags=10,
        extreme_sensitivity_flags=6,
        all_zero_flags=0,
        redundant_target_batch_flags=4,
        largest_max_abs_delta_mev=13.187,
    )

    slate_002_total_flags = re.search(r"\*\*Total flags:\s*(\d+)\*\*", slate_002_ranking)
    if slate_002_total_flags is None:
        raise ValueError("Could not parse slate-002 total flags.")
    slate_002 = FactorySlateSummary(
        slate_id="slate-002 feature terms",
        candidates=int(slate_002_candidate.group(1)),
        advisory_flags=int(slate_002_total_flags.group(1)),
        extreme_sensitivity_flags=slate_002_ranking.count("[EXTREME_SENSITIVITY]"),
        all_zero_flags=slate_002_ranking.count("[ALL_ZERO_DELTA]"),
        redundant_target_batch_flags=slate_002_ranking.count("[REDUNDANT_TARGET_BATCH]"),
        largest_max_abs_delta_mev=_first_float_after_pipe(slate_002_ranking),
    )

    if "live_external_fetch_allowed` is `false`" not in slate_001_text:
        raise ValueError("Slate-001 review does not preserve the no-live-fetch boundary.")
    if "live_external_fetch_allowed` is `false`" not in slate_002_text:
        raise ValueError("Slate-002 review does not preserve the no-live-fetch boundary.")

    slates = [slate_001, slate_002]
    return FactoryAggregate(
        slates=slates,
        candidates=sum(slate.candidates for slate in slates),
        advisory_flags=sum(slate.advisory_flags for slate in slates),
        extreme_sensitivity_flags=sum(slate.extreme_sensitivity_flags for slate in slates),
        all_zero_flags=sum(slate.all_zero_flags for slate in slates),
        redundant_target_batch_flags=sum(slate.redundant_target_batch_flags for slate in slates),
    )


def _format_counter(counter: Counter[str]) -> str:
    return ", ".join(f"{key}: {counter[key]}" for key in sorted(counter))


def render_markdown(agent: AgentAggregate, factory: FactoryAggregate) -> str:
    lane_rows = "\n".join(
        "| {run} | {lane} | {generated} | {executed} | {rejected} | {best:.6f} | {worst:.6f} | {verdicts} |".format(
            run=lane.agent_run_id,
            lane=lane.lane,
            generated=lane.generated,
            executed=lane.executed,
            rejected=lane.rejected,
            best=lane.best_primary_delta if lane.best_primary_delta is not None else 0.0,
            worst=lane.worst_primary_delta if lane.worst_primary_delta is not None else 0.0,
            verdicts=_format_counter(lane.verdict_counts),
        )
        for lane in agent.lanes
    )
    slate_rows = "\n".join(
        "| {slate} | {candidates} | {flags} | {extreme} | {zero} | {redundant} | {largest} |".format(
            slate=slate.slate_id,
            candidates=slate.candidates,
            flags=slate.advisory_flags,
            extreme=slate.extreme_sensitivity_flags,
            zero=slate.all_zero_flags,
            redundant=slate.redundant_target_batch_flags,
            largest=(
                f"{slate.largest_max_abs_delta_mev:.6f}"
                if slate.largest_max_abs_delta_mev is not None
                else "n/a"
            ),
        )
        for slate in factory.slates
    )

    return f"""# Nuclear Agent Scouts Vs Factory Baseline Comparison

**Task:** TASK-0295
**Method:** deterministic tabulation of committed artifacts only
**Script:** `scripts/compare_nuclear_agent_vs_factory_scouts.py`
**Factory inputs:** `docs/reviews/nuclear-prediction-factory-slate-001.md`, `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms.md`, `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms-ranking.md`
**Agent inputs:** `agent_runs/AGENT-RUN-0015/metrics.json`, `agent_runs/AGENT-RUN-0016/metrics.json`, `agent_runs/AGENT-RUN-0017/metrics.json`

This comparison does not fetch live measurements, score a future reveal,
register predictions, update claims, or promote any sandbox result.

## Matched Comparison Protocol

The comparison treats the deterministic factory and agent scout paths as two
different review instruments rather than as direct competitors on one scalar
score.

Matched axes:

- candidate count and coverage breadth;
- rejected-candidate handling;
- complexity and control discipline;
- primary and subset delta distributions where committed metrics exist;
- negative-control quality;
- maintainer review usefulness.

Important asymmetry: the factory slates are pre-reveal generation and ranking
surfaces, so their committed metrics are candidate deltas from the frozen
baseline and heuristic flags. The agent scouts include retrospective
post-AME2020 stress deltas from committed metrics. Those retrospective rows are
stress evidence, not future-measurement reveal evidence.

## Aggregate Summary

| Path | Candidate surface | Executed/scored surface | Rejections before execution | Review flags or verdicts | Primary delta range |
| --- | ---: | ---: | ---: | --- | --- |
| Deterministic factory slates | {factory.candidates} candidates | no holdout scoring in slate reviews | 0 | {factory.advisory_flags} advisory flags | n/a |
| Agent scout lanes | {agent.generated} generated ideas | {agent.executed} executed candidates | {agent.rejected} | {_format_counter(agent.verdict_counts)} | {agent.best_primary_delta:.6f} to {agent.worst_primary_delta:.6f} MeV |

Agent primary-delta sign counts across executed candidates:

- negative primary delta: {agent.negative_primary_count}
- zero primary delta: {agent.zero_primary_count}
- positive primary delta: {agent.positive_primary_count}

Factory advisory-flag counts across the two reviewed slates:

- `EXTREME_SENSITIVITY`: {factory.extreme_sensitivity_flags}
- `ALL_ZERO_DELTA`: {factory.all_zero_flags}
- `REDUNDANT_TARGET_BATCH`: {factory.redundant_target_batch_flags}

## Factory Slate Details

| Slate | Candidates | Advisory flags | Extreme sensitivity | All-zero | Redundant target batch | Largest max abs delta MeV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{slate_rows}

Factory value:

- broad, deterministic coverage of coefficient transforms, feature terms,
  sign-paired controls, near-null controls, and reusable target batches;
- reproducible sensitivity ranking before any registry selection;
- clear separation between sandbox `PRED-9xxx` candidates and committed
  registry entries.

Factory limitations:

- the slate reviews do not score candidates on the post-AME2020 stress
  surface;
- candidate generation does not itself reject row-memorizing or duplicate
  hypothesis shapes before they appear in the slate;
- high candidate count increases repeated-target and reviewer-load pressure
  unless a later triage step narrows the surface.

## Agent Scout Details

| Agent run | Lane | Generated | Executed | Rejected | Best primary delta MeV | Worst primary delta MeV | Verdicts |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
{lane_rows}

Rejected-candidate reason classes:

- {_format_counter(agent.rejection_reason_counts)}

Agent value:

- rejects several bad hypothesis shapes before execution, including
  row-memorizing, free-knob, duplicate-search, and degree-of-freedom inflation
  cases;
- preserves negative results instead of hiding them, especially the mid-mass
  and isotope-chain failures;
- adds adversarial controls around the strongest small signals, including
  sign-inverted, shuffled, clipped, and near-null checks;
- produces a more reviewable explanation of why a lane should continue,
  pause, or stay automated.

Agent limitations:

- all scout coefficients are fit on an 11-row residual slice;
- the post-AME2020 surface is retrospective stress evidence, not a strict
  blind future-measurement reveal;
- sub-MeV improvements remain sandbox triage signals;
- small subset deltas can be fragile, especially chain-neighbor and
  high-asymmetry subsets.

## Operating Split

Keep the following work in deterministic factory/search machinery:

- broad sign-paired candidate generation;
- coefficient-transform and feature-term coverage sweeps;
- target-batch reuse and sensitivity ranking;
- near-null and all-zero sanity controls;
- reproducible slate regeneration into sandbox scratch paths.

Use agent-driven hypothesis triage for:

- pre-execution rejection of row-memorizing or high-free-knob ideas;
- adversarial stress passes around a small number of promising families;
- synthesis of negative results and limitations for maintainer review;
- deciding which factory slates deserve registry-selection review and which
  should remain sandbox diagnostics.

## Verdict

`MIXED`.

The committed evidence does not support a claim that agent scouts are generally
superior to deterministic factory generation. The factory path is better for
wide, reproducible candidate coverage. The agent path adds value as a
review-and-falsification layer: it narrows factory breadth, rejects fragile
hypothesis forms, designs adversarial controls, and preserves negative
outcomes in a form maintainers can act on.

No claim, canonical result, knowledge entry, prediction registry entry, or
future-measurement comparison is promoted by this comparison.
"""


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    agent = summarize_agent_runs(root)
    factory = summarize_factory_slates(root)
    markdown = render_markdown(agent, factory)
    if args.out is not None:
        output_path = args.out if args.out.is_absolute() else root / args.out
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Comparison report written to: {output_path}", file=sys.stderr)
    else:
        sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
