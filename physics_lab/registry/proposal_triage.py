"""Mechanical triage for the task-proposal pool (TASK-0471).

This is the Stage 0/1 layer of the proposal-pool processing architecture
(`docs/proposal-pool-triage.md`): it reconciles each proposal's *declared*
status against an *effective state* derived from canonical signals, flags
drift, routes genuinely-pending proposals to the responsible role, and reports
possible-duplicate clusters as advisory only.

Design boundaries (kept deliberately mechanical):
- the declared ``status`` field stays authoritative; this module never rewrites
  it implicitly — it only reports ``effective_state`` and any mismatch;
- duplicate detection is advisory; it never decides REJECTED/SUPERSEDED;
- no new proposal statuses are introduced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml

from physics_lab.registry.task_discovery import iter_canonical_task_files
from physics_lab.registry.tasks import load_task


PROPOSAL_DIR = "tasks/proposals"

# Routing inputs ------------------------------------------------------------
SCIENCE_RELATED_DOMAINS = frozenset(
    {
        "nuclear_mass_surface",
        "atomic_clock_residuals",
        "exoplanet_mass_radius",
        "quantum_size_effects",
        "textbook_formula_audit",
        "particle_physics",
        "particle_mass_relations",
        "dimensional_analysis",
        "thought_experiment_consistency",
        "anomaly_registry",
        "fresh_physics_data_axes",
    }
)
# Proposal ``type`` and ``related_domain`` are free-form, so routing uses
# keyword signals over both fields. A proposal routes to the Scientific
# Director only when it carries a science signal and no infrastructure signal;
# anything ambiguous or infra-flavoured routes to the Architect.
SCIENCE_KEYWORDS = frozenset(
    {
        "physics",
        "science",
        "scientific",
        "experiment",
        "relativity",
        "empirical",
        "methodology",
        "hypothesis",
        "benchmark",
        "quantum",
        "nuclear",
        "particle",
        "residual",
        "anomaly",
        "dataset",
        "formalization",
        "eft",
        "symmetry",
        "measurement",
        "koide",
        "lattice",
    }
)
INFRA_KEYWORDS = frozenset(
    {
        "workflow",
        "tooling",
        "test",
        "testing",
        "pytest",
        "refactor",
        "validation",
        "documentation",
        "docs",
        "infrastructure",
        "maintainer",
        "contributor",
        "repository",
        "board",
        "closeout",
        "permission",
        "developer",
        "optimization",
        "sync",
        "cli",
        "windows",
        "ci",
    }
)

ROLE_SCIENTIFIC_DIRECTOR = "scientific-director"
ROLE_ARCHITECT = "architect"
ROLE_REVIEW_AGENT = "review-agent"
# Ambiguous proposals get no confident routing. They are shown to every role so
# an agent can read them and self-select whether the proposal is in its
# competence, rather than the script forcing a guess.
ROLE_UNROUTED = "unrouted"
ROLE_NONE = "none"

# Words too generic to signal a duplicate on their own.
_DUPLICATE_STOPWORDS = frozenset(
    {"task", "agent", "proposal", "scaffold", "registry", "format", "protocol", "test", "tests"}
)


@dataclass(frozen=True)
class ProposalState:
    """Reconciled view of a single proposal."""

    path: str
    proposal_id: str
    title: str
    declared_status: str
    declared_decision: str | None
    canonical_task_id: str | None
    referencing_tasks: tuple[str, ...]
    linked_task_id: str | None
    linked_task_status: str | None
    is_science: bool
    effective_state: str
    drift: tuple[str, ...]
    routing_target: str

    @property
    def has_drift(self) -> bool:
        return bool(self.drift)


@dataclass(frozen=True)
class DuplicateCandidate:
    """Low-confidence possible-duplicate pair (never an automatic decision)."""

    left: str
    right: str
    shared: tuple[str, ...]


@dataclass(frozen=True)
class TriageReport:
    """Full triage of the proposal pool."""

    states: tuple[ProposalState, ...]
    duplicates: tuple[DuplicateCandidate, ...]

    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for state in self.states:
            counts[state.effective_state] = counts.get(state.effective_state, 0) + 1
        return counts

    def drifting(self) -> tuple[ProposalState, ...]:
        return tuple(state for state in self.states if state.has_drift)

    def routed_to(self, role: str) -> tuple[ProposalState, ...]:
        return tuple(state for state in self.states if state.routing_target == role)

    def suggested_closeouts(self) -> tuple[ProposalState, ...]:
        """Proposals whose canonical task is DONE but are not yet closed out."""
        return tuple(
            state
            for state in self.states
            if state.effective_state == "resolved"
            and state.declared_status not in {"ACCEPTED", "SUPERSEDED", "REJECTED"}
        )


def _is_proposal_file(path: Path) -> bool:
    name = path.name
    return (
        name.endswith(".yaml")
        and "TEMPLATE" not in name
        and not name.startswith(".")
    )


def load_proposal_payloads(root: Path) -> list[tuple[str, dict[str, Any]]]:
    """Return (repo-relative path, payload) for every proposal file."""
    proposals_dir = root / PROPOSAL_DIR
    payloads: list[tuple[str, dict[str, Any]]] = []
    if not proposals_dir.is_dir():
        return payloads
    for path in sorted(proposals_dir.glob("*.yaml")):
        if not _is_proposal_file(path):
            continue
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if isinstance(data, dict):
            payloads.append((f"{PROPOSAL_DIR}/{path.name}", data))
    return payloads


def task_status_index(root: Path) -> dict[str, str]:
    """Map canonical task id -> status for every TASK-XXXX file."""
    index: dict[str, str] = {}
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return index
    for path in iter_canonical_task_files(root):
        payload = load_task(path)
        index[str(payload["id"])] = str(payload["status"])
    return index


def proposal_reference_index(root: Path) -> dict[str, list[str]]:
    """Map proposal filename -> task ids that reference it in related_objects."""
    index: dict[str, list[str]] = {}
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return index
    for path in iter_canonical_task_files(root):
        payload = load_task(path)
        task_id = str(payload["id"])
        related = payload.get("input", {}).get("related_objects", []) or []
        for ref in related:
            ref_str = str(ref).replace("\\", "/")
            if "/proposals/" not in ref_str:
                continue
            filename = Path(ref_str).name
            index.setdefault(filename, []).append(task_id)
    return index


def _tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(token for token in re.split(r"[^a-z0-9]+", value.lower()) if token)
    return tokens


def _domain_class(payload: dict[str, Any]) -> str:
    """Classify a proposal as 'science', 'infra', or 'ambiguous'.

    Ambiguous means the type/domain signals point both ways or neither way; the
    caller surfaces those for agent self-selection instead of forcing a guess.
    """
    related_domain = str(payload.get("input", {}).get("related_domain") or "").lower()
    proposal_type = str(payload.get("type") or "")
    if related_domain in SCIENCE_RELATED_DOMAINS:
        return "science"
    tokens = _tokens(proposal_type, related_domain)
    has_science = bool(tokens & SCIENCE_KEYWORDS)
    has_infra = bool(tokens & INFRA_KEYWORDS)
    if has_science and not has_infra:
        return "science"
    if has_infra and not has_science:
        return "infra"
    return "ambiguous"


def _is_science(payload: dict[str, Any]) -> bool:
    return _domain_class(payload) == "science"


def _route(effective_state: str, domain_class: str, has_drift: bool) -> str:
    if has_drift:
        return ROLE_REVIEW_AGENT
    if effective_state == "pending":
        if domain_class == "science":
            return ROLE_SCIENTIFIC_DIRECTOR
        if domain_class == "infra":
            return ROLE_ARCHITECT
        return ROLE_UNROUTED
    return ROLE_NONE


def compute_proposal_state(
    rel_path: str,
    payload: dict[str, Any],
    statuses: dict[str, str],
    references: dict[str, list[str]],
) -> ProposalState:
    """Reconcile one proposal's declared status against its effective state."""
    filename = Path(rel_path).name
    declared_status = str(payload.get("status") or "")
    promotion = payload.get("promotion") or {}
    declared_decision = promotion.get("decision")
    canonical_task_id = promotion.get("canonical_task_id")
    referencing_tasks = tuple(references.get(filename, ()))

    linked_task_id = canonical_task_id or (referencing_tasks[0] if referencing_tasks else None)
    linked_task_status = statuses.get(linked_task_id) if linked_task_id else None

    if linked_task_id and linked_task_status is not None:
        effective_state = "resolved" if linked_task_status == "DONE" else "accepted"
    elif declared_status == "REJECTED":
        effective_state = "rejected"
    elif declared_status == "SUPERSEDED":
        effective_state = "superseded"
    elif declared_status == "ACCEPTED":
        effective_state = "accepted"
    else:
        effective_state = "pending"

    drift: list[str] = []
    if effective_state in {"accepted", "resolved"} and declared_status == "PROPOSED":
        drift.append(
            f"declared PROPOSED but canonical task {linked_task_id} exists "
            f"(status {linked_task_status})"
        )
    if declared_status == "ACCEPTED" and linked_task_id is None:
        drift.append("declared ACCEPTED but has no canonical_task_id and no referencing task")
    if canonical_task_id and canonical_task_id not in statuses:
        drift.append(f"promotion.canonical_task_id {canonical_task_id} does not exist")
    if declared_decision == "accepted" and declared_status == "PROPOSED":
        drift.append("promotion.decision is accepted but status is still PROPOSED")

    domain_class = _domain_class(payload)
    is_science = domain_class == "science"
    routing_target = _route(effective_state, domain_class, bool(drift))

    return ProposalState(
        path=rel_path,
        proposal_id=str(payload.get("proposal_id") or filename),
        title=str(payload.get("title") or ""),
        declared_status=declared_status,
        declared_decision=declared_decision,
        canonical_task_id=canonical_task_id,
        referencing_tasks=referencing_tasks,
        linked_task_id=linked_task_id,
        linked_task_status=linked_task_status,
        is_science=is_science,
        effective_state=effective_state,
        drift=tuple(drift),
        routing_target=routing_target,
    )


def _slug_tokens(proposal_id: str) -> set[str]:
    parts = proposal_id.split("-")
    # Drop a leading YYYYMMDD date token and the following contributor token.
    if parts and parts[0].isdigit() and len(parts[0]) == 8:
        parts = parts[2:]
    return {token for token in parts if len(token) >= 4 and token not in _DUPLICATE_STOPWORDS}


def duplicate_candidates(states: tuple[ProposalState, ...]) -> tuple[DuplicateCandidate, ...]:
    """Return advisory possible-duplicate pairs among pending proposals."""
    pending = [state for state in states if state.effective_state == "pending"]
    candidates: list[DuplicateCandidate] = []
    for i, left in enumerate(pending):
        left_tokens = _slug_tokens(left.proposal_id)
        for right in pending[i + 1 :]:
            shared = left_tokens & _slug_tokens(right.proposal_id)
            if len(shared) >= 2:
                candidates.append(
                    DuplicateCandidate(
                        left=left.path,
                        right=right.path,
                        shared=tuple(sorted(shared)),
                    )
                )
    return tuple(candidates)


def triage_pool(root: str | Path) -> TriageReport:
    """Run the full mechanical triage of the proposal pool."""
    root_path = Path(root)
    statuses = task_status_index(root_path)
    references = proposal_reference_index(root_path)
    states = tuple(
        compute_proposal_state(rel_path, payload, statuses, references)
        for rel_path, payload in load_proposal_payloads(root_path)
    )
    return TriageReport(states=states, duplicates=duplicate_candidates(states))


def proposal_drift_paths(root: str | Path) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return (path, drift reasons) for every drifting proposal.

    Used by the advisory validate-repo drift check.
    """
    report = triage_pool(root)
    return tuple((state.path, state.drift) for state in report.drifting())
