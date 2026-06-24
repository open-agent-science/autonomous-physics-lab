# Nuclear Post-Freeze Reveal Source Route Scout

- Task: `TASK-0821`
- Date: `2026-06-24`
- Mode: value-blind source-route scout
- Decision: `REVEAL_SOURCE_ROUTE_BLOCKED`
- Stop code: `NUCLEAR_REVEAL_SOURCE_ROUTE_BLOCKED`
- Selected route: future official AME/NUBASE-style electronic release through
  AMDC/IAEA or equivalent official Atomic Mass Data collaboration channel

## Scope

This scout chooses exactly one candidate post-freeze nuclear mass source route.
It does not fetch or inspect measured values for prediction targets, score any
`PRED-*` entry, open a residual factory, revise frozen registry entries, or
create a `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact.

The selected route is an **official future AME/NUBASE-style electronic
release** with immutable source metadata, measured/non-measured row semantics,
and checksumable artifacts. This is the strongest route class for a later
prospective reveal because it aligns with the repository's existing AME/NUBASE
source model and can support source authority, release timing, row identity,
and no-peek review.

## Inputs Reviewed

- `prediction_registry/nuclear_masses/`
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `docs/reviews/nuclear-reveal-source-manifest-preflight.md`
- `docs/reviews/nuclear-result0018-diagnostic-negative-memory-and-next-lane.md`
- AMDC metadata page: `https://www-nds.iaea.org/amdc/`
- Argonne Atomic Mass Data Resources page:
  `https://www.anl.gov/phy/atomic-mass-data-resources`

The web check was metadata-only. I inspected source landing-page metadata and
did not download value-bearing mass tables, parse AME/NUBASE files, inspect
registry target values, or compare predictions with measurements.

## Selected Route

Route: **future official AME/NUBASE-style release through AMDC/IAEA or an
equivalent Atomic Mass Data collaboration distribution channel**.

Reason for selecting this route:

- it is the highest-authority source class already recognized by the Nuclear
  reveal protocol;
- the AMDC page exposes electronic AME/NUBASE distributions and publication
  references, so a future release can plausibly provide stable source metadata;
- the route can require measured/evaluated/extrapolated row-class separation
  before any target scoring;
- the route can be pinned with an archive/checksum policy before a reveal
  executor sees row-level values.

Current blocker:

- the metadata available in this scout still points to AME2020 and
  NUBASE2020 as the current electronic evaluation surfaces;
- those sources predate the 2026 registry freeze used by the current
  prospective prediction entries;
- no accepted post-freeze official release, checksum policy, measured-row
  flag policy, or maintainer-approved manifest exists.

Therefore this route is the right source class to wait for or reopen, but it is
not ready for a manifest task today.

## Value-Blind Admissibility Table

| Requirement | Assessment |
| --- | --- |
| Publication/release date | Blocked. The currently visible AMDC source surface is AME2020/NUBASE2020, published before the current registry freeze. A future release must clearly postdate the included registry entries. |
| Source authority | Strong route class. Official AME/NUBASE-style distribution from AMDC/IAEA or equivalent collaboration channel is the preferred authority. |
| Value-blind accessibility | Not ready. A future task must pin metadata, checksums, and row-class rules before any executor opens target-bearing tables. |
| Target overlap class | Not assessed with values. A future manifest may record only target-id coverage classes after a no-peek plan is approved; this scout does not inspect target rows. |
| Checksum/archive feasibility | Plausible but unproven for a future release. AMDC exposes electronic files for existing releases, but a future source must be pinned by exact artifact, checksum, size, and retrieval instructions. |
| License/reuse posture | Needs maintainer/source decision. Existing AMDC pages instruct users to cite the papers rather than electronic files; future reuse/redistribution terms must be reviewed before committing raw data. |
| No-peek compatibility | Blocked until a source is post-freeze, immutable, and accepted before value inspection. Current AME2020/NUBASE2020 surfaces cannot support a prospective reveal for 2026 registry entries. |
| Measurement semantics | Blocked. A future route must expose or document measured/evaluated/extrapolated row flags before scoring. |

## Required Future Manifest Fields

A later manifest task should not proceed unless it can fill these fields before
row-level value inspection:

- `manifest_id`
- `task_id`
- source title, release version, issuing body, and release date
- exact source locator and access timestamp
- reuse/license note and archive policy
- raw artifact checksum and file size, or accepted reason no raw copy is
  committed
- normalized artifact checksum if parsing is needed
- parser/normalizer command and code reference
- quantity, units, uncertainty fields, and uncertainty semantics
- value semantics and measured/non-measured flag field
- deterministic target-id fields and target matching rules
- exclusion policy for ambiguous, non-measured, duplicate, and missing rows
- registry snapshot commit and included `PRED-*` ids
- no-peek audit plan and maintainer approval record

If any field remains ambiguous, the future task should stop at source
readiness rather than score predictions.

## Preserved No-Peek Boundary

This scout preserves the no-peek boundary by design:

- no source mass table was downloaded;
- no target nuclides were looked up in an external source;
- no prediction values or target rows were scored;
- no registry values, targets, source-state metadata, or reveal conditions were
  edited;
- no live service result was treated as an immutable source manifest.

## Future Task Recommendation

Do not open a reveal scoring task yet. Open a future manifest task only after a
specific post-freeze official source exists and the maintainer accepts its
source class.

Recommended future task shape:

`Prepare official AME/NUBASE post-freeze reveal-source manifest for Nuclear registry entries`.

Minimum contract:

- metadata-first and value-blind;
- source must postdate the included registry entries;
- source manifest and checksums must be reviewed before target values are
  inspected;
- no `PRED-*` scoring in the manifest PR;
- no claim, knowledge, or broad model-performance wording.

## Output Routing Summary

- Task verdict: `REVEAL_SOURCE_ROUTE_BLOCKED`
- Canonical destination:
  `docs/reviews/nuclear-post-freeze-reveal-source-route-scout.md`
- Review tier: none; value-blind source scout only.
- Gate A status: not applicable; no `RESULT-*` or `PRED-*` artifact was
  created.
- Gate B status: not applicable; no independent replay target was created.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no `results/` artifact created or modified.
- Prediction impact: frozen nuclear prediction registry values, targets,
  source-state metadata, and reveal conditions are unchanged.
- Publication blocker: no accepted post-freeze measured-source manifest is
  pinned; future reveal scoring remains blocked.
