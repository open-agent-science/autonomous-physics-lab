# Exoplanet Source-Version Monitor Contract

**Task:** `TASK-0650`
**Campaign:** Exoplanet Mass-Radius Benchmark
**Mode:** maintainer workflow contract (docs/runbook only; no automation shipped)
**Verdict:** `MONITOR_CONTRACT_DEFINED_NO_AUTOMATION`

## Purpose

Replace ad hoc `EXO-0003` metadata scouts with a conservative, repeatable
contract for checking whether NASA Exoplanet Archive source metadata has
**materially changed** enough to warrant maintainer attention. The monitor
notifies maintainers only when a scientific gate may have moved; it does not
authorize snapshot acquisition, row commits, residual metrics, or claim changes.

This contract follows `TASK-0629` (`WAIT`) and implements the trigger discipline
from `TASK-0599` (`WAIT_FOR_MATERIAL_TRIGGER`).

## Execution Posture

| Item | Policy |
| --- | --- |
| Default delivery | **Manual maintainer run** using this runbook (quarterly or after NASA release-note updates). |
| Automation | **Not created by this task.** A separate task proposal may add a scheduled GitHub Action or maintainer script only if maintainers explicitly request it. |
| Agent tasks | Ordinary agent tasks may **not** run this monitor on a live-fetch loop. Each check is a bounded maintainer or maintainer-approved metadata scout. |
| Value-bearing fetch | **Forbidden** by this contract. Aggregate `COUNT(*)` metadata queries only. |

## Pinned Reference State

Record these baselines at each run. Do not notify if all comparators match.

| Signal | Pinned reference | Source |
| --- | --- | --- |
| Last committed snapshot | `EXO-0002` (`data/exoplanets/exo-0002-pscomppars-snapshot.yaml`) | `6298` raw rows under committed query family |
| Query contract | `data/exoplanets/snapshot_plans/pscomppars_query.adql` | byte-identical; `FROM ps WHERE default_flag = 1` |
| Query SHA-256 | `28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8` | second-snapshot runbook |
| Last metadata scout | `TASK-0629` on `2026-06-06` | verdict `WAIT` |
| Reopen coverage gate | `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml` | per-slice floor `150`, growth `50%` vs EXO-0001 |
| Release-notes surface | PS/PSCompPars release notes URL (below) | last consulted May 27, 2026 doc update; PS table version Oct 16, 2025 |

Update the pinned reference row in this runbook only after a maintainer merges
a new snapshot or accepted metadata scout that changes the baseline.

## Allowed Checks (Metadata Only)

The monitor **may** inspect only the following signal classes:

### 1. Release-note and source-version markers

- PS/PSCompPars release-notes page last-updated timestamp or equivalent archive
  changelog marker.
- Declared PS / PSCompPars table version date in NASA release notes.
- Archive documentation revision date when it explicitly references PS or
  PSCompPars schema or service changes.

**URLs (maintainer reference):**

- Release notes: `https://exoplanetarchive.ipac.caltech.edu/docs/ps-pscp_release_notes.html`
- PS column definitions: `https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html`
- PSCompPars calculation notes: `https://exoplanetarchive.ipac.caltech.edu/docs/pscp_calc.html`

### 2. Query availability

- TAP sync endpoint accepts the committed aggregate queries (HTTP success,
  parseable aggregate response).
- Required committed query fields remain queryable at metadata level (column
  existence / aggregate acceptance, not row values).

**Endpoint:** `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`

### 3. Aggregate `COUNT(*)` thresholds

Permissive upper-bound aggregates only — same family as `TASK-0629`:

| Aggregate id | Query shape (metadata only) |
| --- | --- |
| `raw_default_flag` | `COUNT(*)` from `ps` where `default_flag = 1` |
| `published_confirmed` | above + `soltype = 'Published Confirmed'` |
| `true_mass_transit_radius` | permissive true-mass + transit-radius filter (see TASK-0629) |
| `minimum_mass_transit_radius` | permissive minimum-mass + transit-radius filter |
| `compact_true_mass` | true-mass slice `pl_rade < 1.5` |
| `sub_neptune_true_mass` | true-mass slice `1.5 <= pl_rade < 4` |
| `jovian_true_mass` | true-mass slice `8 <= pl_rade < 16` |
| `hot_jupiter_true_mass` | true-mass slice `pl_orbper < 10` and `8 <= pl_rade < 16` |

Compare counts against:

- **EXO-0002 raw baseline** (`6298` for `raw_default_flag`) — any increase
  is a *necessary but not sufficient* material-change signal;
- **TASK-0599 practical trigger targets** — slice must plausibly reach floor
  before acquisition is worth discussing:
  - compact: `150`
  - sub-Neptune: `510`
  - jovian: `851`
  - hot-Jupiter: `668`
  - minimum-mass lane: `150` with growth

Also evaluate against `second_snapshot_reopen_coverage_gate.yaml` gate_2
(`150` eligible rows per axis slice) and gate_3 (`50%` growth vs EXO-0001
eligible count for the same slice).

## Forbidden Checks

The monitor **must not**:

- fetch, store, log, or inspect individual planet **row values**;
- compute residuals, baseline metrics, CK17-style comparisons, or factory scores;
- read or infer **habitability**, biosignature, or target-priority labels;
- read or infer **composition** or atmospheric labels;
- rank targets or planets by scientific interest;
- commit normalized snapshot rows or update checksums without a separate
  maintainer-approved acquisition task;
- relax reopen gates inside a monitor run;
- treat elapsed time alone as a trigger.

## No-Notify-If-Unchanged Rule

**Default outcome: `NO_NOTIFY`.**

Do not notify maintainers when **all** of the following hold:

1. Release-notes / table-version markers are unchanged since the last recorded
   monitor run (or since the last accepted metadata scout baseline).
2. `raw_default_flag` aggregate count equals the pinned EXO-0002 baseline
   (`6298`) within zero tolerance (exact match required for this signal).
3. No slice aggregate count has crossed a TASK-0599 floor that previously failed.
4. TAP aggregate queries remain available with the committed query contract.
5. No new archive notice indicates PS/PSCompPars schema breakage for committed
   fields.

When unchanged, record a one-line monitor log entry with date and `NO_NOTIFY`
only. Do not open tasks, PRs, or acquisition work.

## Notify Conditions

Notify maintainers only when at least one **notify class** fires:

| Notify class | Condition | Recommended maintainer action |
| --- | --- | --- |
| `NOTIFY_QUERY_BREAKAGE` | TAP endpoint failure or committed field no longer aggregate-queryable | Maintainer infrastructure review; **not** acquisition |
| `NOTIFY_SOURCE_VERSION_CHANGE` | Release notes or table-version marker changed | Run bounded metadata scout (`TASK-0629` pattern); still **no acquisition** |
| `NOTIFY_RAW_ROW_GROWTH` | `raw_default_flag` count exceeds EXO-0002 baseline (`6298`) | Run metadata scout; compare slice aggregates to TASK-0599 floors |
| `NOTIFY_SLICE_THRESHOLD_PLAUSIBLE` | At least one declared slice aggregate meets its TASK-0599 floor **and** gate_3 growth vs EXO-0001 is plausible under permissive counting | Open `EXO-0003` **metadata preflight** task; acquisition still blocked until preflight passes |
| `NOTIFY_QUERY_AMENDMENT_CANDIDATE` | Archive changes suggest switching from committed `ps` query to literal `PSCompPars` | Separate `QUERY_AMENDMENT_REVIEW`; never fold into monitor acquisition |

**Notification is advisory.** It does not authorize live value-bearing acquisition,
baseline replay, gate revision, or claim promotion.

## Monitor Run Output (Required Fields)

Each run must produce a short maintainer record (issue comment, review note, or
log file — maintainer choice):

```text
monitor_run_utc: <ISO-8601>
pinned_snapshot_id: EXO-0002
query_contract_sha256: 28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8
release_notes_marker: <observed version or last-updated string>
raw_default_flag_count: <integer>
slice_aggregates: {compact: N, sub_neptune: N, jovian: N, hot_jupiter: N, min_mass: N}
tap_available: true|false
notify_class: NO_NOTIFY | NOTIFY_*
recommended_action: <one line>
value_bearing_fetch_performed: false
```

## Relationship To Other Exoplanet Gates

| Document | Role |
| --- | --- |
| `docs/reviews/exoplanet-third-snapshot-trigger-plan.md` | Defines when EXO-0003 acquisition may be considered |
| `docs/reviews/exoplanet-exo0003-metadata-trigger-scout.md` | Example scout implementing this contract manually |
| `docs/reviews/exoplanet-control-aware-go-no-go-synthesis.md` | Preserves negative/control memory; monitor does not override |
| `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md` | Acquisition shape **after** preflight clears |
| `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml` | Frozen scientific floors |

Lowering reopen thresholds requires a separate **gate-revision review**, not
a monitor notification.

## Future Automation (Optional, Not In Scope)

If maintainers later request automation, a task proposal should specify:

- scheduled cadence (e.g. monthly);
- GitHub Action or maintainer script with `live_external_fetch_allowed: false`
  except aggregate TAP metadata queries;
- secret-less public TAP access only;
- auto-open issue on `NOTIFY_*` classes;
- hard stop on any row-value response parsing.

This task does **not** create that automation.

## Guardrails

- Preserve Exoplanet negative/control memory until a materially changed snapshot
  or accepted gate revision exists.
- True-mass and minimum-mass axes stay separate in all aggregate reporting.
- Time alone is never sufficient to notify or acquire.
- Monitor output must never include planet names, row previews, or target lists.

## Limitations

- Aggregate counts are permissive upper bounds, not committed loader post-filter
  counts; a passing monitor signal still requires a full metadata scout before
  preflight.
- This contract does not inspect row-level drift, class relabeling, or
  residual-relevant changes hidden within unchanged counts.
- NASA archive availability and field semantics can change without notice;
  `NOTIFY_QUERY_BREAKAGE` is operational, not scientific.

## Output-Routing Summary

- **Task verdict:** `MONITOR_CONTRACT_DEFINED_NO_AUTOMATION`
- **Canonical destination:** this runbook,
  `docs/runbooks/exoplanet-source-version-monitor-contract.md`
- **Review tier:** `none`
- **Gate A / Gate B:** not applicable
- **Claim impact:** none
- **Knowledge impact:** workflow only — replaces repeated manual scout planning
- **Publication blocker:** EXO-0003 acquisition remains blocked until material
  trigger evidence clears via scout + preflight, unchanged from TASK-0629
