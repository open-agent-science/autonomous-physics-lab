# TASK-0986: Revised ThermoML source-access contract

## Scope

This is a planning-only decision packet for the ThermoML 80-row fixture. It
does not fetch an archive, extract rows, modify fixtures, run Joback metrics,
or create a result or claim.

## Current blocker

TASK-0955 established that the requested 80-row route cannot proceed in the
current executor workspace. The exact archive required by the existing source
manifest is:

| Field | Frozen value |
| --- | --- |
| Archive | `ThermoML.v2020-09-30.tgz` |
| Size | `189433115` bytes |
| SHA-256 | `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2` |
| DOI | `10.18434/mds2-2422` |
| Source version | `1.2.6` |

The repository contract has `live_external_fetch_allowed: false`, and the
archive is not vendored. Therefore a live download is not an admissible way to
unblock the task. A future executor must either receive the exact archive at an
untracked local path and verify the identity above, or use a maintainer-approved
revised contract.

## Maintainer options

| Option | What it permits | Main risk or cost |
| --- | --- | --- |
| `PROVIDE_ARCHIVE` | Keep the current contract and provide the exact checksum-matching archive locally. | Requires a controlled local handoff and enough storage; the archive remains outside the repository. |
| `REVISE_CONTRACT` | Approve a bounded, factual extract with the narrower rights and data limits below. | The extract is intentionally incomplete and cannot be treated as a public ThermoML corpus. |
| `KEEP_BLOCKED` | Retain the current blocker and do not attempt the 80-row route. | No additional ThermoML coverage is produced. |
| `SELECT_NEW_SOURCE` | Replace this expansion route with a different public source surface. | Requires a new source-readiness decision and does not alter existing ThermoML results. |

## Recommended contract

**Recommendation: `REVISE_CONTRACT`.** This is a contract decision only; it
does not authorize execution until a maintainer accepts it.

The narrow contract should be:

- at most 80 rows;
- only the `Tb` (normal boiling point) property axis;
- at most 10 rows from each of the eight already named families and at most
  five rows per source article;
- per-row source attribution retained in the review package;
- no raw archive, XML, JSON, or source bytes committed or redistributed;
- no normalized ThermoML corpus and no external dataset DOI asserted for the
  bounded extract;
- `covered_by_repo_license: false`;
- no live external fetch by the executor;
- maintainer-only approval for any increase in row count, family scope,
  property axis, or redistribution rights.

This preserves the bounded-facts route described by the existing maintainer
decision packet while keeping the source-rights boundary explicit.

## Future execution matrix

| Accepted option | Future task may do | Future task may not do |
| --- | --- | --- |
| `PROVIDE_ARCHIVE` | Verify filename, byte count, and SHA-256; perform only the extraction explicitly authorized by the current task. | Fetch live, vendor the archive, or broaden the fixture without a new task. |
| `REVISE_CONTRACT` | Build the bounded Tb-only extract under the row, family, article, attribution, and license limits above. | Add other properties, publish raw/source bytes, create a normalized corpus, or infer a broader ThermoML result. |
| `KEEP_BLOCKED` | Record the blocker and preserve existing artifacts unchanged. | Retry live access or silently lower the identity/rights requirements. |
| `SELECT_NEW_SOURCE` | Scout and validate a new public source under a separate source-readiness task. | Substitute the new source into existing ThermoML results without explicit review. |

## Unblock checklist

1. A maintainer records one exact option as accepted.
2. For `PROVIDE_ARCHIVE`, the archive is supplied outside Git and its identity
   is verified against the frozen manifest.
3. For `REVISE_CONTRACT`, a new executable extraction task references this
   contract and repeats the no-raw-bytes and no-live-fetch limits.
4. The executor records only the bounded facts and source attributions.
5. Validation confirms that no result, prediction, claim, or committed source
   archive changed.

## Output routing

- Gate A: not applicable; no result or prediction is produced.
- Gate B: not applicable; no scientific replay is performed.
- Claim impact: none.
- Knowledge impact: source-access decision packet only.
- Publication blocker: maintainer decision and, if applicable, controlled
  archive handoff remain outstanding.

## Verdict

`REVISE_CONTRACT`

