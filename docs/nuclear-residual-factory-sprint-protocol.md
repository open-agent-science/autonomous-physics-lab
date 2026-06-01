# Nuclear Residual-Law Factory Sprint Protocol (TASK-0504)

The Nuclear-first instance of the [Research Factory Protocol](research-factory-protocol.md).
Nuclear Mass Surface is the flagship campaign and the first factory testbed: the
first sprint (TASK-0507) runs a high-throughput **residual-law** test instead of
more single-lane audits. This is the adapter contract for that sprint; it does
not implement the runner (TASK-0506) or run the sprint.

Nuclear residual work is leakage-sensitive. This contract is layered on the
existing guards and does not relax them:

- [nuclear-residual-feature-no-leakage-contract.md](nuclear-residual-feature-no-leakage-contract.md)
- [nuclear-local-curvature-no-leakage-freeze-protocol.md](nuclear-local-curvature-no-leakage-freeze-protocol.md)

## Required inputs

- pinned AME-based mass dataset with source id, retrieval policy, and checksum;
- the frozen Nuclear baseline residual surface (no refit unless a task authorizes it);
- train / holdout / stress splits, with post-AME2020 time-split treated as a
  retrospective holdout, not a prospective prediction;
- no-leakage guards from the contracts above applied to every residual feature;
- a candidate cap of **50–100 bounded candidates** for the first sprint
  (TASK-0507); declared before metrics, no post-hoc expansion.

## Allowed factory families

| family | allowed scope | required guard |
| --- | --- | --- |
| `shell_distance` | distance to magic numbers / shell closures | no-leakage feature contract; shuffled-shell control |
| `odd_even_pairing` | odd-even staggering and pairing terms | parity-matched control |
| `asymmetry` | isospin / (N−Z) asymmetry terms | matched-(N,Z) control |
| `residual_free_local_topology` | local residual-cluster topology | no-leakage freeze protocol; null-neighbor control |
| `separation_energy_derived` | features derived from separation energies | leakage check that the target is not encoded |
| `local_curvature` | local curvature of the mass surface | **only** under the no-leakage freeze protocol; adversarial controls mandatory |

Forbidden families: any universal mass-law search, discovery framing, or a
feature that encodes the prediction target (leakage).

## Required controls

Per [research-factory-protocol.md](research-factory-protocol.md) plus
Nuclear-specific guards:

- null-baseline comparison against the frozen residual surface;
- shuffled-label / destroyed-structure negative control per family;
- matched controls (matched `(N,Z)`, matched shell region) for slice candidates;
- no-leakage verification for every residual feature (contracts above);
- holdout and post-AME2020 time-split separation in all reported metrics;
- complexity penalty for every added feature, split, or parameter;
- no baseline refit and no live fetch.

A candidate missing any required control routes to `DATA_QUALITY_BLOCKED`; a
candidate matched/beaten by a control routes to `NEGATIVE_RESULT` or
`REJECTED_BY_CONTROL` and is preserved as negative memory.

## Stop rules

A Nuclear factory sprint must stop before execution when:

- the no-leakage contracts are not satisfied for a residual feature;
- the candidate pool exceeds the declared cap or expands after seeing metrics;
- a feature encodes the target (leakage);
- a candidate would create a `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` without
  a separate maintainer-approved promotion task, or would trigger reveal scoring;
- baseline refit or live fetch is requested.

## Recommended follow-up shape

This contract does not create the sprint as `READY`. The sprint is TASK-0507
(first Nuclear residual-law factory sprint over 50–100 bounded candidates), which
runs only after the shared runner (TASK-0506) and `factory_summary` schema
(TASK-0505) land. Negative and inconclusive families are first-class memory;
a shortlisted candidate needs a separate replay/prediction-freeze task before any
promotion.
