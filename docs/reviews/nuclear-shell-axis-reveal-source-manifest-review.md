# Nuclear Shell-Axis Reveal Source-Manifest Review

**Task:** TASK-0307
**Status:** source-manifest review, blocked source outcome
**Target batch:** `shell-axis-balanced-001`
**Registry entries:** `PRED-0063` through `PRED-0068`
**Readiness decision:** `BLOCKED_SOURCE_NOT_PINNED`

## Scope

This review attempted to bridge the TASK-0303 source preflight and the
future TASK-0305 reveal-scoring task by looking for one source-manifest
candidate that could be prepared without exposing row-level target mass
values.

The task did not prepare a concrete source manifest. No acceptable source
candidate was found that satisfied the post-registration timing and
source-pinning requirements without weakening the no-peek boundary.
`TASK-0305` must remain blocked.

## Inputs Reviewed

- `data/nuclear_masses/shell_axis_reveal_source_manifest_template.yaml`
- `docs/reviews/nuclear-shell-axis-mini-wave-source-preflight.md`
- `docs/reviews/nuclear-shell-axis-mini-wave-synthetic-reveal-dry-run.md`
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `prediction_registry/nuclear_masses/PRED-0063.yaml`
- `prediction_registry/nuclear_masses/PRED-0064.yaml`
- `prediction_registry/nuclear_masses/PRED-0065.yaml`
- `prediction_registry/nuclear_masses/PRED-0066.yaml`
- `prediction_registry/nuclear_masses/PRED-0067.yaml`
- `prediction_registry/nuclear_masses/PRED-0068.yaml`

## Source Candidate Decision

No source manifest file was created in `data/nuclear_masses/` because a
manifest with real source fields would imply that a specific source was
pinned for later scoring. That condition is not met.

Metadata-only source screening used broad source-level checks only. It did
not query the eight target nuclides, did not inspect target rows, did not
download nuclear-mass tables, and did not record measured `mass_excess`
values.

Rejected source classes:

| Candidate class | Source-level status | Reason not accepted |
| --- | --- | --- |
| Official evaluation | AME2020 / NUBASE2020 surfaces remain the reviewed official evaluation baseline available from AMDC/IAEA metadata. | Predates `registered_at_utc: 2026-05-20T00:00:00Z`; cannot unlock a prospective reveal. |
| Live AMDC or IAEA service endpoint | Live service surfaces are useful discovery aids but are not an immutable post-registration manifest by themselves. | Live access without a pinned artifact, checksum, release date, and reviewed row semantics is excluded by TASK-0303. |
| Recent literature or compilation papers | Broad literature screens can identify possible future source classes. | The screened post-AME2020 compilation surfaces predate registration or are not a single approved source manifest for this target wave. |

The only protocol-safe output for this task is therefore a blocked review
note, not a source manifest.

## No-Peek Registry Audit

The audit checked repository metadata only and did not inspect external
target values.

| Check | Result |
| --- | --- |
| Registry file creation history | `PRED-0063` through `PRED-0068` were added by `09cb2912c7ae9f68e463f7baa8a5ca10d778db82` (`feat(task-0297): register shell-axis mini-wave`). |
| Post-registration registry edits | `git log` shows no later commits touching the six registry files before this task. |
| Registration timestamp | All six entries record `registered_at_utc: 2026-05-20T00:00:00Z`. |
| Source-state commit | All six entries record `source_state.git_commit: 9e8d7d339a4f0f432e41689862a649eb029b8575`. |
| Target batch label | All six entries use `shell-axis-balanced-001`. |
| Target count | All six entries contain eight target nuclides. |
| Controls present | Candidate entries `PRED-0063` through `PRED-0065` remain paired with sign-inverted `PRED-0066`, near-null `PRED-0067`, and baseline reference `PRED-0068`. |
| External value exposure | No external target-row values were queried, copied, normalized, scored, or committed in this task. |

Registry file hashes at review time:

| Entry | SHA-256 |
| --- | --- |
| `PRED-0063` | `44e4c21469fc06369096aec240007a967be728867655eb7bcf1debc9558d98ed` |
| `PRED-0064` | `bf94e95e8dfd5043d991a51f84163f22f3aabd1f0bf25d873bef390bc9c28833` |
| `PRED-0065` | `6025d879eae5cc67ff19698888e3fb3b4fde6f64963c8d4bd45917436286f47b` |
| `PRED-0066` | `7931224d562a6c244e5f2358ef6136479f94f2aa758435dc24de5bc1a2b25590` |
| `PRED-0067` | `f212906c7fdaf3d054e2d5f54d1e74c4180b06c41052e7eb0f590959bff0360c` |
| `PRED-0068` | `c45fccc82b4eb8eba71388df7295fd602aaa34cfffd07cfde76cc10261510487` |

This is a metadata-only audit. It does not by itself authorize scoring.

## Why TASK-0305 Remains Blocked

TASK-0305 requires all of the following before any reveal scoring:

- `TASK-0303` source-readiness preflight completed and reviewed;
- `TASK-0304` synthetic scoring shape completed and reviewed;
- a concrete `TASK-0307` or equivalent source manifest candidate;
- no-peek review against the concrete source;
- explicit maintainer approval of that source manifest for scoring.

The first two conditions are satisfied. The third is not.

Because no concrete source manifest candidate was prepared, the later
no-peek review and maintainer source approval cannot yet happen. A
future task may retry source-manifest preparation after a qualifying
post-registration official evaluation, peer-reviewed measurement table,
collaboration release, or archive copy is available and pinning can be
done without exposing target rows.

## Stop Conditions Preserved

This review stopped before any target-value exposure. It preserves the
TASK-0303 stop conditions:

- no row-level source values were inspected;
- no measured, extrapolated, or missing labels were assigned to target
  nuclides;
- no checksums were invented for an unpinned source;
- no `PRED-*` entry was edited;
- no reveal metrics were computed;
- no claim, result, or knowledge entry was promoted.

## Maintainer Recommendation

Do not approve `TASK-0305` yet.

The next legitimate reveal step is not scoring. It is either:

- wait for a qualifying post-registration source and rerun a
  source-manifest preparation task; or
- if the maintainer wants a weaker retrospective diagnostic, create a
  separate task that explicitly changes the evidence class and wording
  boundary before any comparison.

## Limitations

- The source screen was intentionally narrow and metadata-only.
- No source file was downloaded or hashed, so this task cannot establish
  reproducibility for a future comparison.
- The lack of an accepted source candidate is a blocking workflow result,
  not evidence for or against the shell-axis mini-wave.
- A future acceptable source may still reveal zero eligible measured target
  rows; that outcome must be preserved rather than backfilled from another
  source.

## Verdict

`BLOCKED_SOURCE_NOT_PINNED`. TASK-0307 produced a reviewable negative
source-manifest outcome and preserved the no-peek boundary. TASK-0305
remains blocked.
