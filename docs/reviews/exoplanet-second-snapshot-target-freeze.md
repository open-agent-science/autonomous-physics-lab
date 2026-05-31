# Exoplanet Second-Snapshot Target Freeze

**Task:** `TASK-0482`  
**Campaign:** `exoplanet-mass-radius`  
**Protocol class:** pre-reveal target-freeze rule  
**Status:** no live fetch, no future rows inspected, no scoring

## Scope

This review defines the target-freeze rule for a future second NASA Exoplanet
Archive PSCompPars snapshot. It uses only committed repository memory:

- `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`;
- `data/exoplanets/snapshot_plans/pscomppars_query.adql`;
- `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md`;
- `docs/reviews/exoplanet-second-snapshot-protocol-review.md`;
- `docs/reviews/exoplanet-failure-map-result-promotion-scorecard.md`.

It does not fetch archive data, inspect newer catalog rows, create prediction
entries, score a second snapshot, or promote any claim.

## Freeze Artifact

The machine-readable freeze rule is committed at:

- `data/exoplanets/second_snapshot_target_freeze.yaml`

The artifact is intentionally a rule freeze, not a future-value table. It
contains no second-snapshot row values and does not enumerate future targets
from any live source.

## Target Identity Rule

The frozen target surface is defined from the committed `EXO-0001` snapshot
only. A future reveal task must match second-snapshot rows to first-snapshot
targets by exact `pl_name`.

The following fields are audit context for row identity changes, but they do
not authorize target substitution after reveal:

- `hostname`;
- `discoverymethod`;
- `disc_year`.

If a future row cannot be matched by exact `pl_name`, it is a blocker or a
context-only schema-drift note, not a license to select a replacement planet.

## Frozen Axes

The target freeze preserves the campaign's mass-provenance boundary by defining
two separate axes.

### True-mass / transit-radius axis

This axis admits only committed first-snapshot rows whose mass provenance can
be mapped before reveal to true-mass semantics.

Required fields:

- `pl_name`;
- `hostname`;
- `pl_rade`, `pl_radeerr1`, `pl_radeerr2`;
- `pl_bmasse`, `pl_bmasseerr1`, `pl_bmasseerr2`;
- `pl_bmassprov`.

Rows with missing, ambiguous, model-derived, or minimum-mass provenance are
excluded from this axis.

### Minimum-mass / transit-radius axis

This axis admits only committed first-snapshot rows whose mass provenance can
be mapped before reveal to `M sin i` or equivalent minimum-mass semantics.

Required fields are the same as the true-mass axis, but row counts, metrics,
blockers, and wording must be reported separately.

No future reveal may average true-mass and minimum-mass rows into one headline
success metric.

## Fields To Compare

A future second-snapshot reveal may compare only fields selected by the
committed query contract unless a pre-reveal amendment is merged first.

Identity and provenance fields:

- `pl_name`;
- `hostname`;
- `default_flag`;
- `soltype`;
- `pl_refname`;
- `st_refname`;
- `disc_refname`.

Planet observable fields:

- `pl_rade`, `pl_radeerr1`, `pl_radeerr2`;
- `pl_radj`;
- `pl_bmasse`, `pl_bmasseerr1`, `pl_bmasseerr2`;
- `pl_bmassj`;
- `pl_bmassprov`;
- `pl_dens`.

Orbital, discovery, and host-context fields:

- `pl_orbper`, `pl_orbsmax`, `pl_orbeccen`;
- `pl_eqt`, `pl_insol`;
- `discoverymethod`, `disc_year`;
- `st_spectype`, `st_teff`, `st_rad`, `st_mass`, `st_met`, `st_age`,
  `st_logg`, `sy_dist`, and associated uncertainty fields selected by the
  committed query.

The field list is deliberately conservative: habitability, biosignature,
target-priority, atmospheric-composition, and spectroscopy summary fields are
not part of the committed query contract and are out of scope.

## Exclusion Rules

The future reveal must exclude or block rows under these conditions:

1. The row is not present in the committed `EXO-0001` snapshot.
2. The row has no exact future `pl_name` match.
3. The required mass or radius fields for the selected axis are missing.
4. The mass-provenance label cannot be mapped before reveal to true-mass or
   minimum-mass semantics.
5. The mass is model-derived rather than measured, unless a later pre-reveal
   amendment creates a separate model-derived diagnostic axis.
6. The future source schema cannot map required fields without a pre-reveal
   amendment.

New planets appearing in a future second snapshot may be reported as context
only. They are not part of the frozen target set and must not influence the
pre-registered benchmark verdict.

## Reveal Conditions

A future second-snapshot acquisition or scoring task may proceed only after all
conditions below are met:

1. A maintainer approves the exact source URL, query artifact, acquisition
   actor, storage path, and checksum method.
2. The future acquisition uses the committed ADQL query contract or a separately
   merged pre-reveal amendment.
3. Raw and normalized future artifacts receive SHA-256 checksums before
   scoring.
4. The acquisition records retrieval timestamp, row count, field list, and
   no-peek attestation.
5. No target axis, mass-provenance mapping, metric, slice, threshold, success
   rule, null rule, or blocker rule changes after future row inspection.
6. True-mass and minimum-mass axes remain separate in row counts, metrics,
   blockers, and wording.

## Stop Conditions

The reveal is blocked rather than scored when:

- timestamp, checksum, row count, field list, or no-peek attestation is
  missing;
- the query differs without a pre-reveal amendment;
- required fields are renamed, removed, or semantically changed without a
  deterministic pre-reveal mapping;
- a target row changes mass-provenance class in a way that cannot be resolved
  without inspecting future values;
- either target axis falls below a pre-declared sample-size floor in the future
  reveal task;
- any analysis mixes true-mass and minimum-mass rows into one headline metric.

These stop conditions are protocol outcomes, not failed scientific hypotheses.

## Prediction Boundary

This task does not create prediction entries. A future prediction-registry task
would need explicit maintainer approval and a separate no-peek package that
names concrete targets, expected fields, success criteria, and publication
route before acquisition.

## Verdict

`VALID_IN_RANGE`

The exoplanet campaign now has a concrete second-snapshot target-freeze rule:
membership is derived from committed `EXO-0001` rows only, future rows are
matched by exact `pl_name`, comparable fields are limited to the committed
PSCompPars query contract, and true-mass versus minimum-mass axes remain
separate. No future data were fetched or inspected.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: target-freeze review plus
  `data/exoplanets/second_snapshot_target_freeze.yaml`;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- limitations / blockers: this is a rule freeze, not an enumerated
  target-list artifact; exact `pl_bmassprov` label mapping and any sample-size
  floors must be locked before future reveal scoring.
