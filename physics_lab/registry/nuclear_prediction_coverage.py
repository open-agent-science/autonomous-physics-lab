"""Coverage audit helpers for the nuclear prediction registry."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction


TARGET_DOMAINS = (
    "frontier",
    "shell_magic",
    "neutron_rich",
    "isotope_chain",
    "odd_even",
    "mid_mass",
)


def build_nuclear_prediction_registry_coverage(root: Path) -> dict[str, Any]:
    """Build a deterministic coverage summary for committed nuclear predictions."""
    root = root.resolve()
    entries = _load_entries(root)
    prediction_ids = [entry["prediction_id"] for entry in entries]
    target_rows = [
        (entry, target)
        for entry in entries
        for target in entry["target_set"]["target_nuclides"]
    ]
    target_frequency: Counter[str] = Counter(
        str(target["nuclide_id"]) for _, target in target_rows
    )
    target_batches: Counter[str] = Counter(
        str(entry["target_set"]["label"]) for entry in entries
    )
    task_counts: Counter[str] = Counter(str(entry["task_id"]) for entry in entries)
    quantity_counts: Counter[str] = Counter(
        str(entry["target_set"]["quantity"]) for entry in entries
    )
    transform_counts: Counter[str] = Counter(
        _transform_class(entry) for entry in entries
    )
    domain_entry_ids: dict[str, list[str]] = {domain: [] for domain in TARGET_DOMAINS}
    flagged_entries: list[dict[str, Any]] = []

    for entry in entries:
        entry_domains = _entry_domains(entry)
        for domain in entry_domains:
            domain_entry_ids[domain].append(str(entry["prediction_id"]))
        flags = _reveal_care_flags(entry, target_frequency, target_batches)
        if flags:
            flagged_entries.append(
                {
                    "prediction_id": entry["prediction_id"],
                    "task_id": entry["task_id"],
                    "target_batch": entry["target_set"]["label"],
                    "model_id": entry["source_state"]["model_reference"]["model_id"],
                    "flags": flags,
                }
            )

    repeated_targets = [
        {
            "nuclide_id": nuclide_id,
            "entry_count": count,
            "prediction_ids": [
                str(entry["prediction_id"])
                for entry, target in target_rows
                if str(target["nuclide_id"]) == nuclide_id
            ],
            "target_batches": sorted(
                {
                    str(entry["target_set"]["label"])
                    for entry, target in target_rows
                    if str(target["nuclide_id"]) == nuclide_id
                }
            ),
        }
        for nuclide_id, count in sorted(
            target_frequency.items(),
            key=lambda item: (-item[1], item[0]),
        )
        if count > 1
    ]

    return {
        "task_id": "TASK-0272",
        "audit_scope": {
            "registry_path": "prediction_registry/nuclear_masses/",
            "entry_count": len(entries),
            "target_row_count": len(target_rows),
            "lowest_prediction_id": prediction_ids[0] if prediction_ids else None,
            "highest_prediction_id": prediction_ids[-1] if prediction_ids else None,
            "id_gaps": _id_gaps(prediction_ids),
            "live_external_fetch_allowed_values": sorted(
                {
                    bool(entry["source_state"]["live_external_fetch_allowed"])
                    for entry in entries
                }
            ),
        },
        "source_task_counts": _counter_items(task_counts),
        "quantity_counts": _counter_items(quantity_counts),
        "transform_class_counts": _counter_items(transform_counts),
        "target_batch_counts": _counter_items(target_batches),
        "domain_coverage": [
            {
                "domain": domain,
                "entry_count": len(ids),
                "prediction_ids": sorted(ids),
            }
            for domain, ids in domain_entry_ids.items()
        ],
        "repeated_target_nuclides": repeated_targets,
        "reveal_readiness_flags": flagged_entries,
        "coverage_gaps": _coverage_gaps(domain_entry_ids, target_batches),
        "limitations": [
            "Coverage is inferred from committed registry metadata and target labels only.",
            "Repeated target nuclides are review signals, not automatic leakage or quality errors.",
            "No live external measurements are fetched or compared by this audit.",
            "Reveal eligibility still requires a future source manifest and no-peek audit.",
        ],
    }


def write_coverage_summary(root: Path, output_path: Path) -> dict[str, Any]:
    """Write the registry coverage summary to YAML and return the payload."""
    coverage = build_nuclear_prediction_registry_coverage(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(coverage, sort_keys=False, allow_unicode=False, width=96),
        encoding="utf-8",
    )
    return coverage


def _load_entries(root: Path) -> list[dict[str, Any]]:
    registry_dir = root / "prediction_registry" / "nuclear_masses"
    return [
        load_nuclear_mass_prediction(path)
        for path in sorted(registry_dir.glob("PRED-[0-9][0-9][0-9][0-9].yaml"))
    ]


def _counter_items(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"label": label, "count": count}
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _id_gaps(prediction_ids: list[str]) -> list[str]:
    if not prediction_ids:
        return []
    observed = {int(prediction_id.split("-")[1]) for prediction_id in prediction_ids}
    highest = max(observed)
    return [
        f"PRED-{idx:04d}"
        for idx in range(1, highest + 1)
        if idx not in observed
    ]


def _transform_class(entry: dict[str, Any]) -> str:
    task_id = str(entry["task_id"])
    model_id = str(entry["source_state"]["model_reference"]["model_id"]).lower()
    frozen_note = str(
        entry["source_state"]["model_reference"]["frozen_parameters_note"]
    ).lower()
    if "feature terms frozen" in frozen_note or task_id == "TASK-0265":
        return "feature_term_selected_registry"
    if task_id == "TASK-0251":
        return "factory_coefficient_transform_selected_registry"
    if "pairing" in model_id:
        return "manual_pairing_or_odd_even_control"
    if "shell" in model_id:
        return "manual_shell_or_magic_control"
    if "neutron-excess" in model_id or "asymmetry" in model_id:
        return "manual_neutron_excess_or_asymmetry_control"
    if "blend" in model_id or "reference" in model_id or "volume" in model_id:
        return "smooth_or_reference_control"
    return "baseline_or_unspecified_control"


def _entry_domains(entry: dict[str, Any]) -> list[str]:
    label = str(entry["target_set"]["label"]).lower()
    model_id = str(entry["source_state"]["model_reference"]["model_id"]).lower()
    text = f"{label} {model_id}"
    domains: list[str] = []
    if "frontier" in text or "heavy-extension" in text:
        domains.append("frontier")
    if any(token in text for token in ("shell", "magic", "n50", "n82")):
        domains.append("shell_magic")
    if any(token in text for token in ("neutron-rich", "neutron-excess", "asymmetry", "frontier")):
        domains.append("neutron_rich")
    if "chain" in text or "isotope" in text:
        domains.append("isotope_chain")
    if any(token in text for token in ("odd-even", "pairing")):
        domains.append("odd_even")
    if "mid-mass" in text:
        domains.append("mid_mass")
    return sorted(set(domains))


def _reveal_care_flags(
    entry: dict[str, Any],
    target_frequency: Counter[str],
    target_batches: Counter[str],
) -> list[str]:
    task_id = str(entry["task_id"])
    model_id = str(entry["source_state"]["model_reference"]["model_id"]).lower()
    target_batch = str(entry["target_set"]["label"])
    flags: list[str] = []
    if task_id not in {"TASK-0251", "TASK-0265"}:
        flags.append("manual_lane_source_review")
    if "near-null" in model_id or "null" in target_batch.lower() or "zero" in model_id:
        flags.append("near_null_or_ablation_control")
    if target_batches[target_batch] >= 10:
        flags.append("high_reuse_target_batch")
    if any(
        target_frequency[str(target["nuclide_id"])] >= 10
        for target in entry["target_set"]["target_nuclides"]
    ):
        flags.append("high_reuse_target_nuclide")
    if task_id == "TASK-0265":
        flags.append("feature_term_selected_wave")
    return flags


def _coverage_gaps(
    domain_entry_ids: dict[str, list[str]],
    target_batches: Counter[str],
) -> list[dict[str, str | int]]:
    gaps: list[dict[str, str | int]] = []
    for domain in TARGET_DOMAINS:
        count = len(domain_entry_ids[domain])
        if count == 0:
            status = "missing"
        elif count < 4:
            status = "thin"
        else:
            status = "covered"
        gaps.append({"domain": domain, "status": status, "entry_count": count})
    if target_batches.get("frontier-next-row", 0) >= 10:
        gaps.append(
            {
                "domain": "frontier",
                "status": "overrepresented_target_batch",
                "entry_count": target_batches["frontier-next-row"],
            }
        )
    if target_batches.get("mid-mass-region-probe", 0) == 0:
        gaps.append(
            {
                "domain": "mid_mass",
                "status": "missing_factory_feature_term_registry_batch",
                "entry_count": 0,
            }
        )
    return gaps
