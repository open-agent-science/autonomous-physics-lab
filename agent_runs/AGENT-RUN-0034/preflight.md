# Preflight

| check | status | notes |
| --- | --- | --- |
| data boundary | PASS | Uses committed `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`; no live archive fetch. |
| baseline freeze | PASS | Uses TASK-0361 frozen Chen-Kipping baseline metrics; no refit or tuning. |
| axis separation | PASS | Headline metrics use `true_mass_with_transit_radius`; minimum-mass rows are sparse diagnostics only. |
| promotion boundary | PASS | No `RESULT-*`, prediction registry, claim, knowledge, habitability, biosignature, target-priority, or discovery output. |
| sample-size handling | PASS | Low-count slices are labeled weak or blocked instead of folded into success wording. |
