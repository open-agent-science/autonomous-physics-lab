"""Operational automation for Autonomous Physics Lab.

PR preparation, review, mission, and closeout tooling live here, separated from
the scientific-memory ``physics_lab.registry`` package (artifact load / validate
/ index). This split follows the 2026-07-09 architecture audit, which found the
registry package had accreted ~70% ops automation. The ``ops`` layer depends
downward on ``registry`` (artifact loaders); ``registry`` must not import
``ops``.
"""
