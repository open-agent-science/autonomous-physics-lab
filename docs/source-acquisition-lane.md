# Source Acquisition, Pinning, and Extraction Lane

**Task:** `TASK-0545`
**Status:** cross-campaign lane protocol
**Sits under:** [Published-Source and Reusable-Dataset Standard](published-source-dataset-standard.md)

## Why This Exists

APL's data bottleneck is not missing standards — it is a missing **executor
lane**. Ordinary agent task PRs are correctly forbidden from live-fetch, so the
one step that actually acquires data (snapshot an open database, retrieve a
version-of-record, run a digitization pass) is usually a maintainer-only manual
action that rarely happens.
Exoplanet has data only because a maintainer ran the snapshot+pin (TASK-0353);
no equivalent ran for the other campaigns.

This lane makes acquisition a **documented, auditable, maintainer-run step**.
A source candidate tagged with a `blocker_type`
(see the [standard](published-source-dataset-standard.md)) routes here and exits
as a pinned, checksummed, provenance-rich source artifact — or a precise
recorded blocker. Rows still require a separate row-curation task; this lane
never adds measurement rows itself.

## Lane Routing By `blocker_type`

| `blocker_type` | Lane | Who runs it | Output |
| --- | --- | --- | --- |
| `T1_access` | Maintainer-provided source artifact | Maintainer (has access/version-of-record) | Committed redistributable artifact + checksum, or metadata-only locator + expected checksum + recorded access/license blocker |
| `T2_extraction_tool` | Deterministic extraction/digitization | Curator with a WebPlotDigitizer-class tool | Extraction ledger + per-point artifact under the campaign's digitization dir |
| `T3_coverage` | Coverage-expansion task | Curation task | A larger curated slice that clears the campaign's coverage gate |
| `T4_snapshot_approval` | Approved snapshot fetch + pin | Maintainer or approved actor; agent may run only public, key-free, network-allowed fetches | Pinned snapshot + manifest + checksum |
| `none` | Direct row-curation task | Row-curation task | Curated rows under the campaign schema |

## Who Runs The Fetch

- **Public, key-free, explicitly acquisition-scoped, and network is approved**
  → an agent may run a bounded acquisition in a single acquisition task: one
  approved source, snapshot only, checksum, source manifest entry, license note.
  No live-fetch inside ordinary agent task PRs or any benchmark runner.
- **Needs an API key, login, cookie, or private artifact** → the **maintainer**
  runs the fetch locally. The agent prepares the runbook, schema, expected
  snapshot manifest, and validator so the maintainer's run is one command.
- **License is readable but not clearly redistributable by this repository**
  → keep DOI/URL/checksum metadata and a local fetch+verify command; do not
  commit the artifact bytes unless a compatible license or explicit permission
  is recorded.
- **Artifact is public and stable upstream** → prefer the same metadata-only
  route unless committing the raw bytes has a documented reproducibility need
  and a maintainer-approved license route. Public access alone is not a reason
  to mirror the file in git.

### No-Secret Rule (hard)

Never commit API keys, tokens, cookies, credentials, `.env` files, or private
artifacts. Key-gated fetches are maintainer-run; the key stays in the
maintainer's environment and never enters the repo, a commit, a log, or a PR.

### Key-Gated Acquisition Handshake

If a source needs a local API key, login, cookie, or private artifact, the agent
should not immediately publish a blocker. It should first tell the maintainer
the exact environment variable needed, point to the relevant runbook, and provide
the local setup pattern from [Local Source Secrets](local-source-secrets.md).

Agents may check only whether the variable is present (`SET` / `not set`),
preferably with the cross-platform `scripts/apl_local_secrets.py` helper. They
must never print, log, commit, or paste the value. A source-access blocker is
recorded only after the maintainer confirms the key/access is unavailable or the
safe local setup path fails.

## Maintainer Acquisition Runbook Contract

Every acquisition (agent-run or maintainer-run) must record:

```text
source_id:
source_url_or_endpoint:
query_or_doi:            # exact ADQL / API query / DOI
license_status:          # open | metadata_only | restricted | unknown
attribution_text:        # required for CC BY etc.
acquisition_actor:       # maintainer | approved-actor | agent (public/key-free only)
retrieval_timestamp_utc:
raw_artifact_path:       # or external reference if not committable
normalized_artifact_path:# if committed
row_count:
selected_fields:
checksum_sha256:         # raw and normalized
redistribution_decision: # file_committed_with_permission | metadata_only
no_peek_attestation:     # no benchmark tuning occurred after row inspection
```

A runbook that cannot fill `checksum_sha256`, `license_status`, or
`retrieval_timestamp_utc` is not complete and must not be used to curate rows.

## What This Lane Does Not Authorize

- autonomous crawler/ingester or live-fetch inside ordinary agent task PRs;
- committing copyrighted PDFs/tables/figures or any secret;
- treating arXiv/non-exclusive preprint licenses as automatic third-party
  redistribution permission;
- mirroring public upstream files just because they are accessible elsewhere;
- adding measurement rows (rows need a separate row-curation task);
- auto-unblocking a benchmark task from an acquisition;
- promoting any claim, knowledge entry, or canonical result.

## Relationship To Other Documents

- [Published-Source and Reusable-Dataset Standard](published-source-dataset-standard.md) — source admissibility, `blocker_type`, dataset-publication rules.
- [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md) — the source-to-row lifecycle stages this lane feeds.
- [Source-Manifest Minimum Schema](source-manifest-minimum-schema.md) — required manifest fields for a pinned source.
- [Local Source Secrets](local-source-secrets.md) — local-only env file pattern and key-gated acquisition handshake.
- `agents/data-acquisition.yaml` — the maintainer-run role profile that operates this lane.

## Output Routing Summary

- Task verdict: `not_applicable` (lane/infrastructure).
- Canonical destination: this lane doc plus the `data-acquisition` role profile.
- Review tier: `none`. Claim/knowledge impact: none.
- Limitations: policy + role, not code; the deterministic extraction-runner tool
  (T2) and the Fresh Source Scout (front of funnel) are deferred follow-ups
  (TASK-0546 / TASK-0544).
