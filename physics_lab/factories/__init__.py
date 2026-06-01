"""Reusable bounded Research Factory layer (TASK-0506).

A shared, campaign-agnostic core plus campaign adapters. Adapters generate
bounded candidates under locked controls; the core orchestrates the run and
emits a schema-valid ``factory_summary`` without promoting any claim. See
docs/research-factory-protocol.md.
"""

from physics_lab.factories.core import (
    Candidate,
    CampaignAdapter,
    FactoryRun,
    FactorySpec,
    get_adapter,
    register_adapter,
    run_factory,
    write_factory_summary,
)

# Register the first-party adapters on import.
from physics_lab.factories import nuclear as _nuclear  # noqa: F401  (registration side effect)

__all__ = [
    "Candidate",
    "CampaignAdapter",
    "FactoryRun",
    "FactorySpec",
    "get_adapter",
    "register_adapter",
    "run_factory",
    "write_factory_summary",
]
