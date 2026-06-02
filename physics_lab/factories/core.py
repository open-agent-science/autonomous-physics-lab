"""Campaign-agnostic core for the bounded Research Factory layer (TASK-0506).

The core defines the shared spec, candidate, adapter interface, and the run
orchestration that assembles a schema-valid ``factory_summary``. Campaign-specific
science lives in adapters (see ``physics_lab/factories/nuclear.py``); the core
never hard-codes a campaign. See docs/research-factory-protocol.md.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import yaml

from physics_lab.registry.validation import validate_document

ROUTE_VERDICTS = (
    "NEGATIVE_RESULT",
    "INCONCLUSIVE",
    "SHORTLIST_CANDIDATE",
    "READY_FOR_REPLAY",
    "READY_FOR_PRED_FREEZE",
    "REJECTED_BY_CONTROL",
    "LOCAL_ONLY",
    "DATA_QUALITY_BLOCKED",
)
CANDIDATE_STATES = (
    "GENERATED",
    "PREFLIGHT_REJECTED",
    "EXECUTED",
    "SHORTLISTED",
    "REJECTED_BY_CONTROL",
)
LEAKAGE_STATES = ("CHECKED_CLEAN", "NOT_CHECKED", "LEAKAGE_FOUND")


@dataclass(frozen=True)
class FactorySpec:
    """One factory run configuration, loaded from a factory config file."""

    factory_id: str
    campaign_id: str
    adapter_id: str
    adapter_version: str
    task_id: str
    dataset: dict[str, Any]
    baseline: dict[str, Any]
    families: tuple[str, ...]
    controls: tuple[str, ...]
    candidate_cap: int
    splits: dict[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    reproducibility: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "FactorySpec":
        required = (
            "factory_id",
            "campaign_id",
            "adapter_id",
            "adapter_version",
            "task_id",
            "dataset",
            "baseline",
            "families",
            "controls",
            "candidate_cap",
        )
        missing = [key for key in required if key not in config]
        if missing:
            raise ValueError(f"Factory config missing required keys: {', '.join(missing)}")
        return cls(
            factory_id=str(config["factory_id"]),
            campaign_id=str(config["campaign_id"]),
            adapter_id=str(config["adapter_id"]),
            adapter_version=str(config["adapter_version"]),
            task_id=str(config["task_id"]),
            dataset=dict(config["dataset"]),
            baseline=dict(config["baseline"]),
            families=tuple(str(f) for f in config["families"]),
            controls=tuple(str(c) for c in config["controls"]),
            candidate_cap=int(config["candidate_cap"]),
            splits=dict(config.get("splits", {})),
            limitations=tuple(str(x) for x in config.get("limitations", [])),
            reproducibility=dict(config.get("reproducibility", {})),
            options=dict(config.get("options", {})),
        )


@dataclass(frozen=True)
class Candidate:
    """One bounded candidate, fully evaluated and routed by an adapter."""

    candidate_id: str
    family: str
    complexity: float
    leakage_status: str
    candidate_state: str
    route_verdict: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    control_outcomes: tuple[dict[str, str], ...] = ()

    def to_summary(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "candidate_id": self.candidate_id,
            "family": self.family,
            "complexity": self.complexity,
            "leakage_status": self.leakage_status,
            "candidate_state": self.candidate_state,
            "route_verdict": self.route_verdict,
        }
        if self.parameters:
            payload["parameters"] = dict(self.parameters)
        if self.metrics:
            payload["metrics"] = dict(self.metrics)
        if self.control_outcomes:
            payload["control_outcomes"] = [dict(item) for item in self.control_outcomes]
        return payload


@dataclass(frozen=True)
class FactoryRun:
    """Campaign-specific run output assembled by an adapter."""

    dataset: dict[str, Any]
    baseline: dict[str, Any]
    controls: tuple[dict[str, str], ...]
    candidates: tuple[Candidate, ...]
    campaign_specific: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class CampaignAdapter(Protocol):
    """Interface a campaign implements to plug into the shared runner."""

    adapter_id: str
    adapter_version: str

    def build_run(self, spec: FactorySpec) -> FactoryRun: ...


_REGISTRY: dict[str, CampaignAdapter] = {}


def register_adapter(adapter: CampaignAdapter) -> None:
    """Register a campaign adapter by its ``adapter_id``."""
    _REGISTRY[adapter.adapter_id] = adapter


def get_adapter(adapter_id: str) -> CampaignAdapter:
    """Return the registered adapter for ``adapter_id``."""
    if adapter_id not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY)) or "none"
        raise ValueError(f"No research-factory adapter registered for {adapter_id!r}. Known: {known}")
    return _REGISTRY[adapter_id]


def _candidate_counts(candidates: tuple[Candidate, ...]) -> dict[str, int]:
    states = Counter(c.candidate_state for c in candidates)
    executed = states["EXECUTED"] + states["SHORTLISTED"] + states["REJECTED_BY_CONTROL"]
    return {
        "generated": len(candidates),
        "preflight_rejected": states["PREFLIGHT_REJECTED"],
        "executed": executed,
        "shortlisted": states["SHORTLISTED"],
        "rejected_by_control": states["REJECTED_BY_CONTROL"],
    }


def run_factory(spec: FactorySpec, adapter: CampaignAdapter) -> dict[str, Any]:
    """Run one bounded factory and return a schema-valid ``factory_summary`` dict."""
    if adapter.adapter_id != spec.adapter_id:
        raise ValueError(
            f"Adapter id mismatch: spec wants {spec.adapter_id!r}, adapter is {adapter.adapter_id!r}"
        )
    run = adapter.build_run(spec)
    if len(run.candidates) > spec.candidate_cap:
        raise ValueError(
            f"Candidate cap exceeded: {len(run.candidates)} > {spec.candidate_cap}; "
            "no post-hoc expansion is allowed."
        )
    for candidate in run.candidates:
        if candidate.route_verdict not in ROUTE_VERDICTS:
            raise ValueError(f"Unknown route verdict: {candidate.route_verdict!r}")
        if candidate.candidate_state not in CANDIDATE_STATES:
            raise ValueError(f"Unknown candidate state: {candidate.candidate_state!r}")

    route_summary = Counter(c.route_verdict for c in run.candidates)
    summary: dict[str, Any] = {
        "schema_version": "1",
        "factory_id": spec.factory_id,
        "campaign_id": spec.campaign_id,
        "adapter_id": spec.adapter_id,
        "adapter_version": spec.adapter_version,
        "task_id": spec.task_id,
        "dataset": run.dataset,
        "baseline": run.baseline,
        "candidate_cap": spec.candidate_cap,
        "candidate_counts": _candidate_counts(run.candidates),
        "controls": [dict(item) for item in run.controls],
        "candidates": [c.to_summary() for c in run.candidates],
        "route_verdict_summary": {k: route_summary[k] for k in route_summary},
        "limitations": list(spec.limitations)
        or ["Sandbox factory run; no claim, prediction, or result promotion."],
        "reproducibility": spec.reproducibility,
    }
    if spec.splits:
        summary["splits"] = spec.splits
    if run.campaign_specific:
        summary["campaign_specific"] = run.campaign_specific

    # Guarantee the artifact is schema-valid before it leaves the core.
    validate_document(summary, "factory_summary", f"{spec.factory_id}/factory_summary.yaml")
    return summary


def write_factory_summary(summary: dict[str, Any], output_dir: str | Path) -> Path:
    """Write the ``factory_summary`` YAML into ``output_dir`` (cross-platform)."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "factory_summary.yaml"
    out_path.write_text(yaml.safe_dump(summary, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return out_path
