# Runbook: Materials Project Pinned-Snapshot Acquisition

**Task:** `TASK-0547`
**Source:** Materials Project (CC BY 4.0)
**Lane:** `T4_snapshot_approval` — maintainer-run (Materials Project requires a personal API key)
**Operates under:** [Source Acquisition, Pinning, and Extraction Lane](../source-acquisition-lane.md)
and the [Published-Source and Reusable-Dataset Standard](../published-source-dataset-standard.md)

## Why this is maintainer-run

The Materials Project API requires a personal API key (`MP_API_KEY`). Per the
acquisition lane's no-secret rule, key-gated fetches are **maintainer-run**: the
key stays in your environment and is never committed, logged, or placed in a PR.
This runbook makes the fetch a single reproducible command; an agent prepared it
but did not run it.

## Prerequisites

```bash
python3 -m pip install mp-api          # provides mp_api.client.MPRester
export MP_API_KEY="<your key>"          # never commit this; do not paste into a PR
```

Get a key from your Materials Project account (Dashboard → API). The key is
personal; do not share or commit it.

## Frozen query (pin before fetch)

Bounded, reproducible first snapshot. The scope is fixed here so the snapshot is
deterministic; do not widen it after seeing rows (no-peek).

- Endpoint: `https://api.materialsproject.org` (via `mp-api`)
- Property axes (separate, never pooled): `formation_energy_per_atom` (eV/atom),
  `band_gap` (eV)
- Scope filter (first snapshot): `num_elements <= 3` AND `is_stable = true`
  (a bounded, stable subset; revise only via a pre-fetch amendment)
- Fields: `material_id`, `formula_pretty`, `composition`, `nsites`,
  `symmetry`, `formation_energy_per_atom`, `band_gap`, `energy_above_hull`,
  `is_stable`, `elements`

## Fetch script (maintainer runs locally)

```python
# materials_acquire.py  (run locally; do NOT commit outputs containing the key)
import csv, hashlib, json, datetime
from mp_api.client import MPRester

API_KEY = __import__("os").environ["MP_API_KEY"]   # from env, never hard-coded
FIELDS = ["material_id","formula_pretty","composition","nsites","symmetry",
          "formation_energy_per_atom","band_gap","energy_above_hull",
          "is_stable","elements"]

with MPRester(API_KEY) as mpr:
    docs = mpr.materials.summary.search(
        num_elements=(1, 3), is_stable=True, fields=FIELDS,
    )
    db_version = mpr.get_database_version()

rows = [{k: getattr(d, k, None) for k in FIELDS} for d in docs]
raw = json.dumps({"database_version": db_version, "query": "num_elements<=3,is_stable=true",
                  "fields": FIELDS, "rows": rows}, sort_keys=True, default=str).encode()
open("materials_snapshot_raw.json","wb").write(raw)
print("rows:", len(rows))
print("database_version:", db_version)
print("sha256:", hashlib.sha256(raw).hexdigest())
print("retrieved_at_utc:", datetime.datetime.utcnow().isoformat()+"Z")
```

## After the fetch — fill the manifest and commit (no key, no raw dump if large)

1. Record into `data/materials/materials_snapshot_manifest.yaml`:
   `database_version`, `retrieved_at_utc`, `row_count`, `selected_fields`,
   `checksum_sha256`, `query`, `license_status: open`, the CC BY attribution text,
   and `no_peek_attestation: true`.
2. Normalize rows into the `data/materials/schema.md` shape as
   `data/materials/md-0001-materials-project-<axis>.yaml` (one property axis per
   file; keep `computed_dft` provenance and the DFT functional explicit).
3. Commit the normalized snapshot + manifest. Do **not** commit `MP_API_KEY`,
   `materials_acquire.py` with a hard-coded key, or any `.env`. If the raw JSON is
   large, keep it out of git and record only its checksum + how to regenerate.
4. Hand off to a separate row-curation / baseline task; this runbook does not add
   benchmark metrics or claims.

## Guardrails

- CC BY 4.0: redistribution of curated rows is allowed **with attribution** — keep
  the attribution + citation in every committed dataset file.
- One property axis per file; never pool `formation_energy_per_atom` and
  `band_gap`, and never mix computed and (future) measured rows.
- No live fetch inside any benchmark runner; no claim, no model training.
- Never commit secrets.
