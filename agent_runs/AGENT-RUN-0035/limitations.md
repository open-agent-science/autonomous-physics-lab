# Limitations

- Regime predicates use only committed catalog fields and CK17; no per-regime CK17 refit is performed.
- Per-class median, shuffled-regime, and sample-size-matched controls share rows with the candidate where they overlap; control bias from the shared eligible set is expected and reported by-design.
- Minimum slice count is 30 rows; smaller regimes are flagged `under_minimum_slice` and excluded from the verdict.
- Shuffled-regime control is single-draw with a deterministic seed; no Monte-Carlo distribution is computed.
- Equilibrium temperature and orbital period are present for only a subset of rows; regimes that depend on them are smaller by construction.
- No habitability, biosignature, composition, target-priority, prediction registry, claim, or knowledge promotion is authorised.
