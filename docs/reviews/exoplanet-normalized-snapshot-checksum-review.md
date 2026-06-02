# Exoplanet normalized snapshot checksum review

**Task:** `TASK-0528`
**Verdict:** `VALID` as a metadata reproducibility improvement; no benchmark run.

## Scope

This review closes the normalized-snapshot checksum gap for the committed
`EXO-0001` PSCompPars YAML artifact. It does not fetch live archive data, alter
rows, change filters, reopen residual hypotheses, compute metrics, or strengthen
mass-radius interpretation.

## Input References

- `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- `data/exoplanets/source_manifest.yaml`
- `docs/reviews/exoplanet-pscomppars-snapshot-ingestion.md`
- `docs/reviews/exoplanet-failure-map-result-promotion-scorecard.md`

## Method

The snapshot now carries an embedded canonical-payload SHA-256. The
canonicalizer parses the committed YAML payload, replaces
`snapshot_provenance.normalized_checksum_sha256` with `null`, serializes the
full payload as sorted compact JSON, and hashes the UTF-8 bytes. Normalizing the
embedded field avoids a self-reference while preserving sensitivity to row and
metadata drift.

The source manifest separately records the byte-level SHA-256 of the committed
YAML file exactly as stored in git. This remains useful for exact archive-file
replay.

## Code Reference

- `physics_lab/datasets/exoplanets.py`
- `scripts/check_exoplanet_normalized_snapshot_checksum.py`
- `scripts/ingest_exoplanet_pscomppars_snapshot.py`
- `tests/test_exoplanet_mass_radius_dataset_schema.py`

## Metrics

- Embedded canonical-payload SHA-256:
  `dc4d8df2d0860f87d6384a1a1bebbe8e3e51a400175593f2b48e6c64a33ae5ee`
- Committed normalized-file SHA-256:
  `bd7c919e4ba1de5acb01e45c78f64aa2b5af859edd62f0e88eaa62a44fb54c2d`
- Snapshot rows changed: `0`
- Live archive fetches performed: `0`
- RESULT, PRED, CLAIM, or KNOW artifacts created: `0`

## Replay

```bash
python3 scripts/check_exoplanet_normalized_snapshot_checksum.py
```

The command exits non-zero when the embedded canonical-payload checksum does
not match the replayed value.

## Limitations

- The embedded checksum verifies deterministic normalized-payload identity; it
  does not validate scientific correctness.
- The source remains a composite-catalog snapshot, not a per-publication
  primary-table extraction.
- This task does not improve holdout quality, external comparability, or
  minimum-mass-axis power.

## Output Routing

- Task verdict: `VALID`
- Canonical destination: source artifact metadata and review note
- Review tier: `none`
- Gate A: not applicable; no RESULT or PRED artifact was created
- Gate B: not applicable
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Publication blocker: none for the metadata checksum gap; existing campaign
  interpretation limits remain in force
