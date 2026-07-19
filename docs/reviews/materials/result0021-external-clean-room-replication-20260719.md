# RESULT-0021 external clean-room replication

## Pre-run contract

- Task: `TASK-1065`
- Campaign: `materials-property-residuals`
- Executor identity: `akutenyov`, a human-controlled contributor distinct from repository owners `gladunrv` and `romanhladun24-dot`.
- Contract sealed UTC: `2026-07-19T11:28:50.9828409Z`.
- Public inputs only: Zenodo record `21207072`, asset `md0002-v0.1.0.zip`, public repository tag `dataset-md0002-v0.1.0`, and release-facing documentation.
- Archive byte-size expectation: `795018` bytes.
- Archive SHA-256 expectation: `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22`.
- Benchmark axis: `formation_energy_per_atom` only; `band_gap` is not pooled or scored.
- Independent method: parse the released YAML directly; for each holdout material, predict the mean training formation energy for its unordered non-oxygen cation pair, with the global training median only when that pair is absent. Controls are the training global median and null prediction `0.0`.
- Frozen split: release-provided material-level labels; no identifiers, values, prototypes, or pair definitions may be tuned after scoring.
- Metric: holdout MAE in `eV_per_atom` over 54 material-level formation-energy rows.
- Predeclared comparison tolerance: absolute difference no greater than `1e-12` for metrics and `0` for counts, identifiers, checksums, and split membership.
- Independence boundary: the replay script does not import `physics_lab.workflows.materials_md0002_formation_energy` or reproduce repository implementation. Canonical RESULT-0021 metrics were not read until the independent output and hash were sealed.

## Public-input and archive checks

- Zenodo DOI: `10.5281/zenodo.21207072`.
- Archive accessed and downloaded on `2026-07-19 UTC` into a worktree-local clean-room directory.
- Archive file: `md0002-v0.1.0.zip`; observed `795018` bytes; SHA-256 `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22`; both match the published expectations.
- Public tag: `dataset-md0002-v0.1.0` resolves to commit `8be7469616fb8957d4f967124720ee30db20f6e9`.
- Archive and tag normalized-dataset SHA-256: `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1`.
- Archive raw-snapshot SHA-256: `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567`.
- Normalized rows: `724`; unique material identifiers: `362`; property axes: `formation_energy_per_atom` and `band_gap`.
- The two axes have identical material-to-split assignments. Formation-energy split counts are `253` train, `55` validation, and `54` holdout; frozen split digest is `0c1b06cddefe06d0dc6ee0c3341bba2966e0cb337d607afb6d7d797debfc46ef`.

## Independent execution

Code reference: [`scripts/md0002_external_clean_room_replay.py`](../../../scripts/md0002_external_clean_room_replay.py). It uses `PyYAML` and Python standard-library operations only; it has no import from `physics_lab`.

```text
python scripts/md0002_external_clean_room_replay.py \
  --archive-dir .external-clean-room/archive \
  --zip .external-clean-room/md0002-v0.1.0.zip \
  --output docs/reviews/materials/result0021-external-clean-room-replay-20260719.json
```

Environment: Windows 11, CPython `3.12.13`, PyYAML `6.0.3`. The sealed output was written at `2026-07-19T11:30:10.577886+00:00` and has SHA-256 `1fa936ac50a0a2096aa80a590e1be7f451bfcfdd50f08788829cefc72ab8f55e`.

The sealed replay reports:

| Measure | External value |
| --- | ---: |
| Cation-pair baseline MAE | `0.20060612204925257 eV_per_atom` |
| Global-training-median control MAE | `0.5060915176365851 eV_per_atom` |
| Zero null control MAE | `2.0356192354480647 eV_per_atom` |
| Train cation pairs | `79` |

## Canonical comparison after sealing

The canonical public result serializes the compared MAEs to six decimal places. The `1e-12` tolerance is applied to those serialized values: `round(external, 6)` is compared directly with the stored canonical number. This proves equality at the published precision, not equality of unrecorded additional canonical digits.

| Required field | Canonical RESULT-0021 | External replay | Status |
| --- | --- | --- | --- |
| Best model | `model_cation_pair_mean` | cation-pair train mean | match |
| Best verdict | `VALID_IN_RANGE` | cation-pair baseline below median control | match |
| Formation-energy rows | `362` | `362` | match |
| Train / validation / holdout | `253 / 55 / 54` | `253 / 55 / 54` | match |
| Cation-pair holdout MAE | `0.200606` | `0.200606` | delta `0.0` |
| Global-median control MAE | `0.506092` | `0.506092` | delta `0.0` |
| Control ordering | cation-pair lower than global-median control | `0.200606 < 0.506092` | match |
| Frozen split identity | material-level | material-level; digest recorded above | match |

The canonical workflow describes a global train-mean fallback, while the predeclared clean-room script uses the global training median when a cation pair is absent. Eight holdout rows use that fallback. The two public fallback choices yield the same frozen-holdout MAE (`0.20060612204925257`) for this dataset; the distinction is retained as a limitation rather than silently normalized away. The zero control is an external-only diagnostic; canonical RESULT-0021 records the global-median control.

## Verdict and maintainer request

**Verdict: `EXTERNAL_CLEAN_ROOM_PASS`.**

This is a public-artifact clean-room reproduction of one computed-DFT benchmark slice. It is eligible for maintainer review of the `EXTERNAL_REPLICATED` tier only. It does not itself mutate the review tier, RESULT-0021, its metrics, the Zenodo record, any dataset, CLAIM, or KNOW artifact.

## Output routing

| Route | Outcome |
| --- | --- |
| External identity | Attested human-controlled `akutenyov`, distinct from the two named maintainer identities; maintainer must verify before tier promotion. |
| Public-only provenance | Zenodo archive, public tag, and public documentation only. |
| Gate and review status | Clean-room checks and comparison passed; maintainer review remains required. |
| Tier request | Request review for `EXTERNAL_REPLICATED`; no automatic tier mutation. |
| Result and claim impact | No RESULT, CLAIM, metric, or public-wording mutation. |
| Knowledge impact | No KNOW promotion or knowledge-memory mutation. |
| Blockers | None for the scoped public artifact replay; fallback-semantic limitation remains documented above. |

## Scope limitations

- The source values are Materials Project computed DFT values, not experimental measurements.
- This validates reproducibility of the frozen MD-0002 formation-energy benchmark slice only; it is not a materials-discovery, synthesis, device, experimental-agreement, or universal-law claim.
- Band-gap rows were deliberately not pooled or scored.
- The externally visible canonical MAEs are stored to six decimal places, so the comparison cannot prove equality beyond that published precision.