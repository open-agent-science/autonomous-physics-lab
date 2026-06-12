#!/usr/bin/env python3
"""Generate the lightweight campaign catalog from campaign profile files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "campaign_profiles" / "_catalog.yaml"
PROFILE_ROOT = REPO_ROOT / "campaign_profiles"

CURATOR_REVIEW_INTERVALS = frozenset(
    {
        "quarterly_active",
        "quarterly_blocked",
        "quarterly_planning",
        "semiannual_quality_floor",
    }
)
CURATOR_REVIEW_REASONS = frozenset(
    {
        "flagship_validation",
        "benchmark_monitoring",
        "source_readiness",
        "planning_scaffold",
        "quality_floor_hygiene",
    }
)
CURATOR_POOLS = frozenset(
    {
        "frontier_planning",
        "prediction_reveal",
        "result_promotion",
        "source_data_benchmark",
        "verifier_quality_floor",
    }
)
SURFACE_TYPES = frozenset(
    {
        "formula_audit",
        "fresh_data_benchmark",
        "guardrail_falsification",
        "prediction_reveal",
        "quality_floor",
        "source_pinned_benchmark",
    }
)
LIFECYCLE_STAGES = frozenset(
    {
        "active_benchmark",
        "mature",
        "monitor_only",
        "pinned_dataset",
        "reveal_blocked",
        "scaffold",
        "source_readiness",
    }
)
ACTIVITY_STATUSES = frozenset(
    {
        "active",
        "active_limited",
        "active_monitor",
        "active_support",
        "planning",
        "watchlist",
    }
)
CURATOR_REVIEW_CADENCES = frozenset(
    {
        "as_needed",
        "biweekly",
        "monthly",
        "quarterly",
        "weekly",
    }
)
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def _validate_curator_review(path: Path, campaign_id: str, review: dict[str, Any]) -> None:
    for field in (
        "status",
        "last_reviewed",
        "review_interval",
        "next_review_due",
        "review_reason",
        "source",
        "notes",
    ):
        if field not in review:
            raise ValueError(f"{path}: campaign {campaign_id} curator_review missing {field}")

    interval = str(review["review_interval"])
    if interval not in CURATOR_REVIEW_INTERVALS:
        allowed = ", ".join(sorted(CURATOR_REVIEW_INTERVALS))
        raise ValueError(
            f"{path}: campaign {campaign_id} has invalid review_interval {interval!r}; "
            f"expected one of: {allowed}"
        )

    reason = str(review["review_reason"])
    if reason not in CURATOR_REVIEW_REASONS:
        allowed = ", ".join(sorted(CURATOR_REVIEW_REASONS))
        raise ValueError(
            f"{path}: campaign {campaign_id} has invalid review_reason {reason!r}; "
            f"expected one of: {allowed}"
        )

    for date_field in ("last_reviewed", "next_review_due"):
        value = str(review[date_field])
        if not ISO_DATE_PATTERN.match(value):
            raise ValueError(
                f"{path}: campaign {campaign_id} curator_review.{date_field} "
                f"must be YYYY-MM-DD, got {value!r}"
            )


def _validate_enum(
    path: Path,
    campaign_id: str,
    field: str,
    value: object,
    allowed_values: frozenset[str],
) -> None:
    rendered = str(value)
    if rendered not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise ValueError(
            f"{path}: campaign {campaign_id} has invalid {field} {rendered!r}; "
            f"expected one of: {allowed}"
        )


def _validate_curator_metadata(path: Path, campaign_id: str, portfolio: dict[str, Any]) -> None:
    for field, allowed in (
        ("surface_type", SURFACE_TYPES),
        ("lifecycle_stage", LIFECYCLE_STAGES),
        ("activity_status", ACTIVITY_STATUSES),
    ):
        if field not in portfolio:
            raise ValueError(f"{path}: campaign {campaign_id} portfolio missing {field}")
        _validate_enum(path, campaign_id, field, portfolio[field], allowed)

    curator = portfolio.get("curator")
    if not isinstance(curator, dict):
        raise ValueError(f"{path}: campaign {campaign_id} portfolio.curator must be a mapping")

    for field in (
        "primary_pool",
        "secondary_pools",
        "review_cadence",
        "transfer_requires",
    ):
        if field not in curator:
            raise ValueError(f"{path}: campaign {campaign_id} curator missing {field}")

    _validate_enum(path, campaign_id, "curator.primary_pool", curator["primary_pool"], CURATOR_POOLS)
    _validate_enum(
        path,
        campaign_id,
        "curator.review_cadence",
        curator["review_cadence"],
        CURATOR_REVIEW_CADENCES,
    )

    secondary_pools = curator["secondary_pools"]
    if not isinstance(secondary_pools, list):
        raise ValueError(f"{path}: campaign {campaign_id} curator.secondary_pools must be a list")
    for pool in secondary_pools:
        _validate_enum(path, campaign_id, "curator.secondary_pools", pool, CURATOR_POOLS)
    if str(curator["primary_pool"]) in {str(pool) for pool in secondary_pools}:
        raise ValueError(
            f"{path}: campaign {campaign_id} curator.secondary_pools must not repeat primary_pool"
        )

    transfer_requires = curator["transfer_requires"]
    if not isinstance(transfer_requires, list) or not transfer_requires:
        raise ValueError(
            f"{path}: campaign {campaign_id} curator.transfer_requires must be a non-empty list"
        )
    for requirement in transfer_requires:
        if not isinstance(requirement, str) or not requirement:
            raise ValueError(
                f"{path}: campaign {campaign_id} curator.transfer_requires entries must be strings"
            )


def _portfolio_profiles(profile_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    profiles: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(profile_root.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        data = _load_yaml(path)
        if "portfolio" in data:
            profiles.append((path, data))
    return profiles


def build_catalog(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Build the catalog payload from campaign_profiles/*.yaml."""
    campaigns: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path, profile in _portfolio_profiles(root / "campaign_profiles"):
        campaign_id = str(profile["id"])
        if campaign_id in seen:
            raise ValueError(f"Duplicate campaign id in campaign profiles: {campaign_id}")
        seen.add(campaign_id)

        portfolio = profile["portfolio"]
        _validate_curator_metadata(path, campaign_id, portfolio)
        _validate_curator_review(path, campaign_id, portfolio["curator_review"])
        allowed_work = []
        allowed_work.extend(profile.get("allowed_hypothesis_families", []))
        allowed_work.extend(profile.get("allowed_experiment_families", []))
        if not allowed_work:
            allowed_work = portfolio["allowed_work"]

        forbidden_work = profile.get("forbidden_claims", []) or portfolio["forbidden_work"]

        campaigns.append(
            {
                "id": campaign_id,
                "title": profile["title"],
                "status": portfolio["status"],
                "domain": portfolio["domain"],
                "surface_type": portfolio["surface_type"],
                "lifecycle_stage": portfolio["lifecycle_stage"],
                "activity_status": portfolio["activity_status"],
                "curator": portfolio["curator"],
                "current_stage": portfolio["current_stage"],
                "agent_capacity": {
                    "recommended_parallel_agents": portfolio[
                        "recommended_parallel_agents"
                    ],
                    "coordination_notes": portfolio["coordination_notes"],
                },
                "best_next_actions": portfolio["best_next_actions"],
                "required_gates": portfolio["required_gates"],
                "allowed_work": allowed_work,
                "forbidden_work": forbidden_work,
                "current_results": portfolio["current_results"],
                "open_questions": portfolio["open_questions"],
                "curator_review": portfolio["curator_review"],
                "source_docs": profile.get("source_docs", []),
            }
        )

    campaigns.sort(key=lambda item: item["id"])
    return {
        "registry_version": 1,
        "updated": "2026-06-12",
        "generated_by": "scripts/generate_campaign_catalog.py",
        "source_roots": [
            "campaign_profiles/",
            "docs/campaigns/",
            "missions/current.yaml",
        ],
        "purpose": (
            "Lightweight machine-readable campaign portfolio registry for "
            "parallel agent research lanes. Generated from campaign profile "
            "metadata so the catalog does not become a separate hand-maintained "
            "source of truth."
        ),
        "relationship_to_missions": (
            "`missions/current.yaml` remains the recommendation and "
            "prioritization source for live agent onboarding. This generated "
            "catalog is a stable portfolio map for mission control, snapshots, "
            "and curators."
        ),
        "campaigns": campaigns,
    }


def render_catalog(catalog: dict[str, Any]) -> str:
    """Render catalog YAML with a generated-file banner."""
    body = yaml.safe_dump(catalog, sort_keys=False, allow_unicode=False, width=88)
    return (
        "# Generated campaign portfolio index; do not edit by hand.\n"
        "# Generated by scripts/generate_campaign_catalog.py.\n"
        "# Edit campaign_profiles/*.yaml portfolio blocks instead.\n"
        f"{body}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if catalog is stale")
    parser.add_argument(
        "--write",
        action="store_true",
        help="write campaign_profiles/_catalog.yaml",
    )
    args = parser.parse_args()
    if not args.check and not args.write:
        args.check = True

    rendered = render_catalog(build_catalog(REPO_ROOT))
    if args.check:
        if not CATALOG_PATH.exists():
            raise SystemExit(f"Missing generated catalog: {CATALOG_PATH}")
        current = CATALOG_PATH.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit(
                "campaign_profiles/_catalog.yaml is stale; run "
                "python3 scripts/generate_campaign_catalog.py --write"
            )
    if args.write:
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
