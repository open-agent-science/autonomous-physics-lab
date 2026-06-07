# Dimensional Validator Boundary Result Preflight

- Task: `TASK-0661`
- Surface: Dimensional Validator quality gate
- Verdict: `QUALITY_GATE_PRELIMINARY_NOT_PROMOTABLE`
- Decision: keep the validator as a useful deterministic preflight gate, but do
  not promote the live 70-item curation surface to an `AGENT_VALIDATED`
  reusable quality-gate result yet.

## Scope

This preflight replays the current live dimensional-analysis challenge surface
and identifies whether it is strong enough to support a public-safe reusable
quality gate for Nuclear, Materials, Exoplanet, Quantum, Atomic, and Textbook
formula-audit work.

Reviewed inputs:

- `docs/campaigns/dimensional-analysis-validator.md`
- `docs/results/dimensional-analysis-validator-summary.md`
- `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`
- `knowledge/challenge_sets/dimensional_analysis_challenge_set_mvp_50.yaml`
- `physics_lab/engines/dimensions.py`
- `tests/test_dimensions.py`
- `tests/test_dimensional_validator_pilot.py`
- `docs/result-promotion-protocol.md`

No challenge entries, canonical `RESULT-*` artifacts, `CLAIM-*` files,
`KNOW-*` files, prediction entries, or campaign metrics were created or
modified.

## Replay Performed

The live curation surface was replayed with the deterministic validator:

```bash
.venv/bin/python -c 'from pathlib import Path; import yaml; from collections import Counter; from physics_lab.engines.dimensions import validate_challenge_set; path=Path("knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml"); data=yaml.safe_load(path.read_text(encoding="utf-8")); results, summary=validate_challenge_set(data); print("python", __import__("sys").version.split()[0]); print("total", summary.total); print("agree", summary.agree); print("agreement_fraction", f"{summary.agreement_fraction:.6f}"); print("computed", {"VALID": summary.valid_count, "INVALID": summary.invalid_count, "SUSPICIOUS": summary.suspicious_count, "INCONCLUSIVE": summary.inconclusive_count}); print("expected", dict(Counter(str(i.get("expected_verdict")) for i in data.get("items", [])))); failures=[(r.item_id, r.expected_verdict, r.computed_verdict, r.detail) for r in results if not r.agrees]; print("failures"); [print(f) for f in failures]'
```

Replay environment:

- Python: `3.12.13` from `.venv/bin/python`
- Challenge set: `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`
- Runner: `physics_lab.engines.dimensions.validate_challenge_set`

## Replay Metrics

| Metric | Value |
| --- | ---: |
| Live challenge items | `70` |
| Agreement | `65/70` |
| Agreement fraction | `0.928571` |
| Computed `VALID` | `32` |
| Computed `INVALID` | `35` |
| Computed `SUSPICIOUS` | `2` |
| Computed `INCONCLUSIVE` | `1` |

The current live surface still clears the existing test threshold of at least
90% agreement and at most one inconclusive result. That is enough to keep the
validator useful as a local deterministic sanity check. It is not enough to
promote the live surface as a reusable campaign-wide result because the misses
are concentrated exactly at the semantic and known-limit boundary this preflight
is meant to assess.

## Boundary Disagreements

| Item | Expected | Computed | Boundary exposed |
| --- | --- | --- | --- |
| `DA-310` incompatible ratio product | `SUSPICIOUS` | `VALID` | Dimensionally balanced but semantically empty ratio. |
| `DA-311` undamped spring period missing `2pi` | `SUSPICIOUS` | `VALID` | Missing dimensionless constant; numerical failure is invisible to dimensional analysis. |
| `DA-011` Snell's law | `VALID` | `SUSPICIOUS` | Legitimate all-dimensionless textbook relation is over-flagged. |
| `DA-406` refractive-index limit | `KNOWN_LIMIT_FAIL` | `SUSPICIOUS` | Known-limit condition is not encoded; all-dimensionless heuristic fires instead. |
| `DA-407` large-angle pendulum limit | `KNOWN_LIMIT_FAIL` | `INCONCLUSIVE` | Formula uses `pi`, which the expression grammar does not currently treat as a dimensionless constant. |

These are acceptable limitations for the frozen MVP result, which is pinned to
the 50-item benchmark scope. They are blockers for claiming that the expanded
live curation surface is already a public-safe reusable quality gate.

## Cross-Campaign Boundary Coverage

The replay supports the following low-risk use:

- reject formulas with direct SI unit mismatches;
- catch missing dimensional constants in ordinary SI expressions;
- guard formula-generation tasks from obvious length/time/mass/current/unit
  mistakes before any scientific interpretation;
- preserve the frozen `RESULT-0007` replay boundary, because current CLI replay
  remains pinned to the 50-item MVP input.

The replay does not yet cover several campaign-relevant boundary classes:

| Campaign surface | Missing or weak boundary class |
| --- | --- |
| Nuclear Mass Surface | MeV, mass excess, binding-energy-per-nucleon, and dimensionless isotope labels need explicit row-field semantics; dimensional validity alone cannot distinguish source/reveal readiness or no-peek status. |
| Materials Property Residuals | eV-per-atom, band-gap eV, formation-energy sign conventions, composition stoichiometry, and prototype/group labels need schema-aware checks beyond SI dimensions. |
| Exoplanet Mass-Radius | Radius, mass, density, gravity, true mass vs minimum mass, and model-derived rows need row-class flags; dimensional agreement cannot detect class mixing or habitability-like interpretation drift. |
| Quantum Size Effects | eV/nm formulas, effective mass conventions, and natural-unit shortcuts remain outside the SI-focused MVP unless constants and unit-system assumptions are explicit. |
| Atomic Clock Residuals | Fractional frequency shifts and covariance/source-artifact semantics are mostly dimensionless; the validator cannot assess covariance reconstruction or source consistency. |
| Textbook Formula Audit | Exact-reference constants, approximation-domain failures, and missing dimensionless factors such as `2pi` require convention or numerical reference checks. |

## Promotion Decision

Recommended decision:

- keep using the validator as a deterministic first-pass quality gate for
  formula drafts;
- do not publish a new `RESULT-*` or upgrade any existing dimensional-validator
  artifact from this preflight;
- do not claim that dimensional consistency proves physical correctness;
- preserve `RESULT-0007` as the frozen 50-item MVP result;
- require targeted boundary expansion before the live 70-item curation surface
  becomes a reusable `AGENT_PUBLISHED` or `AGENT_VALIDATED` quality-gate result.

The highest-value follow-up is a small challenge-set expansion or engine-scope
task that handles dimensionless constants and all-dimensionless textbook
relations explicitly, then separately decides whether known-limit checks belong
in the dimensional validator or in a distinct semantic/numerical gate.

## Output Routing

- Task verdict: `QUALITY_GATE_PRELIMINARY_NOT_PROMOTABLE`.
- Canonical destination:
  `docs/reviews/dimensional-validator-boundary-result-preflight.md`.
- Review tier: `none`; this is a routing/preflight review, not a canonical
  result artifact.
- Gate A status: blocked for the live 70-item surface because semantic
  dimensionless and known-limit boundary cases still need targeted handling.
- Gate B status: not applicable; no `AGENT_PUBLISHED` result was replayed for
  tier upgrade.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no `results/` artifact created or modified.
- Limitations: deterministic dimensional replay only; no empirical data, no
  natural-unit support, no semantic row-class validation, no approximation-domain
  scoring, and no maintainer endorsement of a reusable public quality gate.
