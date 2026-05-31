"""Campaign output scorecard (TASK-0498).

Reports durable scientific-memory throughput per campaign — committed RESULT and
PRED artifacts by verdict/registry-status and review tier, plus sandbox
agent-run counts — so strategy agents and the Scientific Campaign Director can
steer by output rather than raw task or PR activity.

Design boundaries:
- descriptive only: it counts committed canonical artifacts; it never promotes
  claims, edits review tiers, or ranks scientific truth;
- it reuses the existing campaign catalog and campaign-profile portfolio
  pointers as the artifact->campaign signal instead of inventing a new mapping;
- artifacts with no determinable campaign are reported under coverage, not
  silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


# Prediction-registry subdirectories map to campaigns by directory name.
PREDICTION_DOMAIN_TO_CAMPAIGN = {
    "nuclear_masses": "nuclear-mass-surface",
}
REVIEW_TIERS = ("AGENT_PUBLISHED", "AGENT_VALIDATED", "MAINTAINER_REVIEWED", "EXTERNAL_REPLICATED")


@dataclass(frozen=True)
class CampaignScore:
    """Durable + sandbox output counts for one campaign."""

    campaign_id: str
    status: str
    result_count: int
    result_verdicts: dict[str, int]
    result_tiers: dict[str, int]
    prediction_count: int
    prediction_statuses: dict[str, int]
    prediction_tiers: dict[str, int]
    sandbox_agent_runs: int


@dataclass(frozen=True)
class ScorecardReport:
    """Full campaign output scorecard."""

    campaigns: tuple[CampaignScore, ...]
    repo_claims: dict[str, int]
    repo_knowledge: int
    unmapped_results: tuple[str, ...]
    repo_result_count: int = 0
    repo_result_verdicts: dict[str, int] = None  # type: ignore[assignment]
    repo_result_tiers: dict[str, int] = None  # type: ignore[assignment]

    def totals(self) -> dict[str, int]:
        return {
            "results_total": self.repo_result_count,
            "results_mapped_to_campaign": sum(c.result_count for c in self.campaigns),
            "predictions": sum(c.prediction_count for c in self.campaigns),
            "sandbox_agent_runs": sum(c.sandbox_agent_runs for c in self.campaigns),
            "claims": sum(self.repo_claims.values()),
            "knowledge": self.repo_knowledge,
        }


def _safe_load(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def _catalog_campaigns(root: Path) -> list[tuple[str, str]]:
    data = _safe_load(root / "campaigns" / "catalog.yaml")
    out: list[tuple[str, str]] = []
    for campaign in data.get("campaigns", []) or []:
        if isinstance(campaign, dict) and campaign.get("id"):
            out.append((str(campaign["id"]), str(campaign.get("status", ""))))
    return out


def _result_paths_for_campaign(root: Path, campaign_id: str) -> list[Path]:
    profile = _safe_load(root / "campaign_profiles" / f"{campaign_id}.yaml")
    current = profile.get("portfolio", {}).get("current_results", []) or []
    paths: list[Path] = []
    for ref in current:
        ref_str = str(ref)
        if ref_str.startswith("results/") and ref_str.endswith("result.yaml"):
            paths.append(root / ref_str)
    return paths


def _count_results(paths: list[Path]) -> tuple[int, dict[str, int], dict[str, int]]:
    verdicts: dict[str, int] = {}
    tiers: dict[str, int] = {}
    count = 0
    for path in paths:
        if not path.exists():
            continue
        payload = _safe_load(path)
        if not payload:
            continue
        count += 1
        verdict = str(payload.get("best_verdict", "UNVERDICTED"))
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        tier = str(payload.get("review_tier", "LEGACY_UNTIERED"))
        tiers[tier] = tiers.get(tier, 0) + 1
    return count, verdicts, tiers


def _count_predictions(root: Path, campaign_id: str) -> tuple[int, dict[str, int], dict[str, int]]:
    statuses: dict[str, int] = {}
    tiers: dict[str, int] = {}
    count = 0
    for domain, mapped in PREDICTION_DOMAIN_TO_CAMPAIGN.items():
        if mapped != campaign_id:
            continue
        domain_dir = root / "prediction_registry" / domain
        if not domain_dir.is_dir():
            continue
        for path in sorted(domain_dir.glob("PRED-*.yaml")):
            payload = _safe_load(path)
            if not payload:
                continue
            count += 1
            status = str(payload.get("registry_status", "UNKNOWN"))
            statuses[status] = statuses.get(status, 0) + 1
            tier = str(payload.get("review_tier", "LEGACY_UNTIERED"))
            tiers[tier] = tiers.get(tier, 0) + 1
    return count, statuses, tiers


def _sandbox_agent_runs(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    runs_dir = root / "agent_runs"
    if not runs_dir.is_dir():
        return counts
    for path in sorted(runs_dir.glob("AGENT-RUN-*/agent_run.yaml")):
        payload = _safe_load(path)
        campaign = str(payload.get("campaign_profile_id", "")).strip()
        if campaign:
            counts[campaign] = counts.get(campaign, 0) + 1
    return counts


def _repo_claim_statuses(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    claims_dir = root / "claims"
    if not claims_dir.is_dir():
        return counts
    for path in sorted(claims_dir.glob("CLAIM-*.md")):
        status = "UNKNOWN"
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip().lower()
            if stripped.startswith("status:") or stripped.startswith("- status:"):
                status = line.split(":", 1)[1].strip().strip("`*") or "UNKNOWN"
                break
        counts[status] = counts.get(status, 0) + 1
    return counts


def _all_profile_result_paths(root: Path, campaign_ids: list[str]) -> set[str]:
    mapped: set[str] = set()
    for cid in campaign_ids:
        for path in _result_paths_for_campaign(root, cid):
            mapped.add(path.resolve().as_posix())
    return mapped


def build_scorecard(root: str | Path) -> ScorecardReport:
    """Build the campaign output scorecard from committed artifacts."""
    root_path = Path(root)
    campaigns_meta = _catalog_campaigns(root_path)
    campaign_ids = [cid for cid, _ in campaigns_meta]
    sandbox = _sandbox_agent_runs(root_path)

    scores: list[CampaignScore] = []
    for cid, status in campaigns_meta:
        result_paths = _result_paths_for_campaign(root_path, cid)
        r_count, r_verdicts, r_tiers = _count_results(result_paths)
        p_count, p_statuses, p_tiers = _count_predictions(root_path, cid)
        scores.append(
            CampaignScore(
                campaign_id=cid,
                status=status,
                result_count=r_count,
                result_verdicts=r_verdicts,
                result_tiers=r_tiers,
                prediction_count=p_count,
                prediction_statuses=p_statuses,
                prediction_tiers=p_tiers,
                sandbox_agent_runs=sandbox.get(cid, 0),
            )
        )

    # Coverage + repo-wide result totals across every committed result, since
    # per-campaign attribution only covers profile-curated current_results.
    mapped = _all_profile_result_paths(root_path, campaign_ids)
    unmapped: list[str] = []
    repo_result_count = 0
    repo_verdicts: dict[str, int] = {}
    repo_tiers: dict[str, int] = {}
    results_dir = root_path / "results"
    if results_dir.is_dir():
        for path in sorted(results_dir.glob("**/result.yaml")):
            payload = _safe_load(path)
            if not payload:
                continue
            repo_result_count += 1
            verdict = str(payload.get("best_verdict", "UNVERDICTED"))
            repo_verdicts[verdict] = repo_verdicts.get(verdict, 0) + 1
            tier = str(payload.get("review_tier", "LEGACY_UNTIERED"))
            repo_tiers[tier] = repo_tiers.get(tier, 0) + 1
            if path.resolve().as_posix() not in mapped:
                unmapped.append(path.relative_to(root_path).as_posix())

    knowledge_dir = root_path / "knowledge"
    knowledge = len(list(knowledge_dir.glob("KNOW-*.md"))) if knowledge_dir.is_dir() else 0

    return ScorecardReport(
        campaigns=tuple(scores),
        repo_claims=_repo_claim_statuses(root_path),
        repo_knowledge=knowledge,
        unmapped_results=tuple(unmapped),
        repo_result_count=repo_result_count,
        repo_result_verdicts=repo_verdicts,
        repo_result_tiers=repo_tiers,
    )
