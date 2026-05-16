"""Deterministic review helper for nuclear prediction variant slates.

Reads a factory slate summary (as produced by generate_nuclear_prediction_variants.py
--summary-out) and emits a structured ranking report. The report surfaces diversity
and risk signals for human/agent selection. It does not assign scientific success
scores and does not compare candidates against future measurements.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

EXTREME_SENSITIVITY_THRESHOLD_MEV = 5.0
NEAR_DUPLICATE_THRESHOLD_MEV = 1e-4
REDUNDANT_BATCH_MIN_CANDIDATES = 3

_FLAG_EXTREME_SENSITIVITY = "EXTREME_SENSITIVITY"
_FLAG_ALL_ZERO_DELTA = "ALL_ZERO_DELTA"
_FLAG_REDUNDANT_TARGET_BATCH = "REDUNDANT_TARGET_BATCH"
_FLAG_MISSING_REVIEW_NOTES = "MISSING_REVIEW_NOTES"
_FLAG_DUPLICATE_PREDICTION_ID = "DUPLICATE_PREDICTION_ID"
_FLAG_NEAR_DUPLICATE_VECTOR = "NEAR_DUPLICATE_VECTOR"


@dataclass(frozen=True)
class RankingFlag:
    code: str
    variant_id: str
    message: str


@dataclass
class SlateRankingReport:
    factory_id: str
    task_id: str
    candidate_count: int
    target_batches_covered: list[str]
    model_family_prefixes: list[str]
    candidates_per_batch: dict[str, int]
    duplicate_prediction_ids: list[str]
    near_duplicate_pairs: list[tuple[str, str]]
    delta_table: list[dict[str, Any]]
    flags: list[RankingFlag] = field(default_factory=list)
    generated_at_utc: str = ""

    def to_markdown(self) -> str:
        lines: list[str] = []
        lines.append("# Nuclear Prediction Variant Slate Ranking Report")
        lines.append("")
        lines.append(f"**Factory:** `{self.factory_id}`  ")
        lines.append(f"**Task:** `{self.task_id}`  ")
        lines.append(f"**Candidates:** {self.candidate_count}  ")
        lines.append(f"**Generated at:** {self.generated_at_utc}")
        lines.append("")
        lines.append(
            "> This report is a deterministic review aid. It does not assign "
            "scientific success scores and does not compare candidates against "
            "future or holdout measurements."
        )
        lines.append("")

        lines.append("## Coverage Summary")
        lines.append("")
        lines.append(f"**Target batches ({len(self.target_batches_covered)}):** "
                     + ", ".join(f"`{b}`" for b in sorted(self.target_batches_covered)))
        lines.append("")
        lines.append("**Candidates per target batch:**")
        lines.append("")
        for batch, count in sorted(self.candidates_per_batch.items()):
            lines.append(f"- `{batch}`: {count}")
        lines.append("")
        lines.append(f"**Model family prefixes ({len(self.model_family_prefixes)}):** "
                     + ", ".join(f"`{p}`" for p in sorted(self.model_family_prefixes)))
        lines.append("")

        lines.append("## Duplicate Analysis")
        lines.append("")
        if self.duplicate_prediction_ids:
            lines.append(
                f"**Duplicate prediction IDs ({len(self.duplicate_prediction_ids)}):** "
                + ", ".join(f"`{pid}`" for pid in self.duplicate_prediction_ids)
            )
        else:
            lines.append("No duplicate prediction IDs detected.")
        lines.append("")
        if self.near_duplicate_pairs:
            lines.append(
                f"**Near-duplicate value vector pairs "
                f"(threshold {NEAR_DUPLICATE_THRESHOLD_MEV} MeV) "
                f"({len(self.near_duplicate_pairs)}):**"
            )
            for a, b in self.near_duplicate_pairs:
                lines.append(f"- `{a}` ≈ `{b}`")
        else:
            lines.append(
                f"No near-duplicate value vectors detected "
                f"(threshold {NEAR_DUPLICATE_THRESHOLD_MEV} MeV)."
            )
        lines.append("")

        lines.append("## Delta Sensitivity Table")
        lines.append("")
        lines.append(
            "Candidates sorted by largest absolute delta from baseline (MeV). "
            "Large deltas are not evidence of predictive value; they indicate "
            "coefficient sensitivity and should be reviewed for plausibility."
        )
        lines.append("")
        lines.append("| variant_id | target_batch | max_abs_delta_mev | mean_abs_delta_mev | nuclide_count |")
        lines.append("|-----------|-------------|------------------|--------------------|--------------|")
        for row in self.delta_table:
            lines.append(
                f"| `{row['variant_id']}` "
                f"| `{row['target_batch']}` "
                f"| {row['max_abs_delta_mev']:.6f} "
                f"| {row['mean_abs_delta_mev']:.6f} "
                f"| {row['nuclide_count']} |"
            )
        lines.append("")

        lines.append("## Heuristic Flags")
        lines.append("")
        if not self.flags:
            lines.append("No heuristic flags raised.")
        else:
            lines.append(f"**Total flags: {len(self.flags)}**")
            lines.append("")
            for flag in self.flags:
                lines.append(f"- `[{flag.code}]` `{flag.variant_id}`: {flag.message}")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(
            "*This report was generated by `scripts/rank_nuclear_prediction_variant_slate.py`. "
            "No scientific claim is made or implied by this ranking output.*"
        )
        lines.append("")

        return "\n".join(lines)


def rank_slate(summary: dict[str, Any]) -> SlateRankingReport:
    """Build a SlateRankingReport from a factory summary dict."""
    factory_id = str(summary.get("factory_id", "unknown"))
    task_id = str(summary.get("task_id", "unknown"))
    candidates: list[dict[str, Any]] = list(summary.get("candidates", []))

    duplicate_prediction_ids = _find_duplicate_prediction_ids(candidates)
    near_duplicate_pairs = _find_near_duplicate_pairs(candidates)

    batches_seen: dict[str, int] = {}
    model_prefixes: set[str] = set()
    delta_table: list[dict[str, Any]] = []

    for cand in candidates:
        batch = str(cand.get("target_batch", ""))
        batches_seen[batch] = batches_seen.get(batch, 0) + 1
        model_prefixes.add(_model_family_prefix(str(cand.get("model_id", ""))))
        delta_table.append(_delta_row(cand))

    delta_table.sort(key=lambda r: r["max_abs_delta_mev"], reverse=True)

    flags: list[RankingFlag] = []
    for cand in candidates:
        variant_id = str(cand.get("variant_id", ""))
        flags.extend(_check_extreme_sensitivity(cand, variant_id))
        flags.extend(_check_all_zero_delta(cand, variant_id))
        flags.extend(_check_missing_review_notes(cand, variant_id))

    for batch, count in batches_seen.items():
        if count >= REDUNDANT_BATCH_MIN_CANDIDATES:
            flags.append(
                RankingFlag(
                    code=_FLAG_REDUNDANT_TARGET_BATCH,
                    variant_id=f"<batch:{batch}>",
                    message=(
                        f"Target batch '{batch}' is used by {count} candidates. "
                        "Consider whether target diversity is sufficient."
                    ),
                )
            )

    for pid in duplicate_prediction_ids:
        flags.append(
            RankingFlag(
                code=_FLAG_DUPLICATE_PREDICTION_ID,
                variant_id=f"<prediction_id:{pid}>",
                message=f"Duplicate prediction_id '{pid}' detected in slate.",
            )
        )

    for a, b in near_duplicate_pairs:
        flags.append(
            RankingFlag(
                code=_FLAG_NEAR_DUPLICATE_VECTOR,
                variant_id=f"{a}/{b}",
                message=(
                    f"Variants '{a}' and '{b}' produce near-identical value vectors "
                    f"(all deltas < {NEAR_DUPLICATE_THRESHOLD_MEV} MeV). "
                    "Consider removing one to reduce slate redundancy."
                ),
            )
        )

    return SlateRankingReport(
        factory_id=factory_id,
        task_id=task_id,
        candidate_count=len(candidates),
        target_batches_covered=list(batches_seen.keys()),
        model_family_prefixes=sorted(model_prefixes),
        candidates_per_batch=dict(batches_seen),
        duplicate_prediction_ids=duplicate_prediction_ids,
        near_duplicate_pairs=near_duplicate_pairs,
        delta_table=delta_table,
        flags=flags,
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def rank_slate_from_file(path: str | Path) -> SlateRankingReport:
    """Load a factory summary YAML file and return a SlateRankingReport."""
    summary_path = Path(path)
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = yaml.safe_load(handle)
    if not isinstance(summary, dict):
        raise ValueError(f"Expected mapping in slate summary: {summary_path}")
    return rank_slate(summary)


def _find_duplicate_prediction_ids(candidates: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for cand in candidates:
        pid = cand.get("prediction_id")
        if pid is None:
            continue
        pid_str = str(pid)
        if pid_str in seen and pid_str not in duplicates:
            duplicates.append(pid_str)
        seen.add(pid_str)
    return duplicates


def _find_near_duplicate_pairs(
    candidates: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    """Return pairs of variant_ids whose predicted value vectors are near-identical."""
    indexed = [
        (str(c.get("variant_id", "")), _value_vector(c))
        for c in candidates
    ]
    pairs: list[tuple[str, str]] = []
    for i in range(len(indexed)):
        for j in range(i + 1, len(indexed)):
            vid_a, vec_a = indexed[i]
            vid_b, vec_b = indexed[j]
            if _vectors_near_duplicate(vec_a, vec_b):
                pairs.append((vid_a, vid_b))
    return pairs


def _value_vector(candidate: dict[str, Any]) -> list[float]:
    return [
        float(row.get("predicted_value_mev", math.nan))
        for row in candidate.get("target_nuclides", [])
    ]


def _vectors_near_duplicate(vec_a: list[float], vec_b: list[float]) -> bool:
    if len(vec_a) != len(vec_b) or not vec_a:
        return False
    return all(
        abs(a - b) < NEAR_DUPLICATE_THRESHOLD_MEV
        for a, b in zip(vec_a, vec_b)
        if not (math.isnan(a) or math.isnan(b))
    )


def _delta_row(candidate: dict[str, Any]) -> dict[str, Any]:
    deltas = [
        abs(float(row.get("delta_from_baseline_mev", 0.0)))
        for row in candidate.get("target_nuclides", [])
    ]
    max_delta = max(deltas) if deltas else 0.0
    mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
    return {
        "variant_id": str(candidate.get("variant_id", "")),
        "target_batch": str(candidate.get("target_batch", "")),
        "max_abs_delta_mev": round(max_delta, 6),
        "mean_abs_delta_mev": round(mean_delta, 6),
        "nuclide_count": len(deltas),
    }


def _model_family_prefix(model_id: str) -> str:
    parts = model_id.split("::")
    return parts[0] if parts else model_id


def _check_extreme_sensitivity(
    candidate: dict[str, Any],
    variant_id: str,
) -> list[RankingFlag]:
    nuclides = candidate.get("target_nuclides", [])
    extreme = [
        row
        for row in nuclides
        if abs(float(row.get("delta_from_baseline_mev", 0.0))) > EXTREME_SENSITIVITY_THRESHOLD_MEV
    ]
    if not extreme:
        return []
    max_val = max(abs(float(r["delta_from_baseline_mev"])) for r in extreme)
    return [
        RankingFlag(
            code=_FLAG_EXTREME_SENSITIVITY,
            variant_id=variant_id,
            message=(
                f"{len(extreme)} target(s) exceed ±{EXTREME_SENSITIVITY_THRESHOLD_MEV} MeV delta "
                f"(max observed: {max_val:.3f} MeV). Review coefficient transform plausibility."
            ),
        )
    ]


def _check_all_zero_delta(
    candidate: dict[str, Any],
    variant_id: str,
) -> list[RankingFlag]:
    nuclides = candidate.get("target_nuclides", [])
    if not nuclides:
        return []
    if all(float(row.get("delta_from_baseline_mev", 0.0)) == 0.0 for row in nuclides):
        return [
            RankingFlag(
                code=_FLAG_ALL_ZERO_DELTA,
                variant_id=variant_id,
                message=(
                    "All delta_from_baseline_mev values are 0.0. "
                    "The coefficient transform may have had no effect on this target batch "
                    "(e.g., pairing-only transform on odd-A targets only)."
                ),
            )
        ]
    return []


def _check_missing_review_notes(
    candidate: dict[str, Any],
    variant_id: str,
) -> list[RankingFlag]:
    notes = candidate.get("review_notes", [])
    if not notes:
        return [
            RankingFlag(
                code=_FLAG_MISSING_REVIEW_NOTES,
                variant_id=variant_id,
                message="No review_notes present. Add at least one note describing the scientific intent.",
            )
        ]
    return []
