"""Registry helpers for public scientific memory."""

from physics_lab.registry.active_board import sync_active_board
from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.claims import load_claim
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.agents import load_agent
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.knowledge import load_knowledge
from physics_lab.registry.research_proposals import (
    load_experiment_proposal,
    load_hypothesis_proposal,
)
from physics_lab.registry.results import load_result, validate_result_payload
from physics_lab.registry.review_metadata import load_review_metadata
from physics_lab.registry.tasks import load_task
from physics_lab.registry.task_proposals import load_task_proposal
from physics_lab.registry.validation import infer_kind_from_path, load_schema, validate_document

__all__ = [
    "infer_kind_from_path",
    "load_agent",
    "load_agent_run",
    "sync_active_board",
    "load_claim",
    "load_example_config",
    "load_experiment_proposal",
    "load_experiment",
    "load_hypothesis_proposal",
    "load_hypothesis",
    "load_knowledge",
    "load_result",
    "load_review_metadata",
    "load_schema",
    "load_task",
    "load_task_proposal",
    "validate_document",
    "validate_result_payload",
]
