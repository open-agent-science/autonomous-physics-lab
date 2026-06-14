# Quantum: Open-Licensed-First Source-Selection Application (TASK-0751)

**Task:** `TASK-0751`
**Campaign:** `quantum-size-effects`
**Scope:** apply the [open-licensed-first preference order](../fresh-data-intake-protocol.md#source-selection-preference-order-open-licensed-first)
to the Quantum candidate set. Workflow/policy only: no rows curated, no live
fetch, no digitizer run, no metrics, no claim.

## Why Quantum Is the Worked Example

Quantum stalled through a long sequence of closed figure-PDF scouts that each
preserved a blocker without landing a single direct row. The lesson: the campaign
optimized for "find any source" instead of "find an open, table-derived source
first." This review re-classifies the candidates by the new tier order so future
effort goes to the highest-leverage tier.

## Tier Classification of Current Quantum Candidates

| Candidate | License | Data exposure | Tier | Status |
| --- | --- | --- | --- | --- |
| Yu 2003 (qd-0001) | closed | calibration curve | n/a | committed but calibration-derived (not a direct row) |
| Moreels 2009 (qd-0002) | closed | calibration curve | n/a | committed but calibration-derived (not a direct row) |
| Norris-Bawendi 1996 (PRB) | closed | figure-derived | **Tier 4** | blocker preserved (no legal copy / tool run) |
| Kang-Wise 1997 | closed | model-parameter tables / figures | **Tier 4** | rejected as inadmissible |
| Vossmeyer 1994 (JPC) | closed | probable table, access-gated | **Tier 4** | access blocker (TASK-0687); fallback only |
| Almeida 2023 (Nano Lett) | **CC BY 4.0** | figure-only size axis | **Tier 3** | license cleared + source checksummed (TASK-0741); size axis needs digitization |

Observation: the campaign's best current source (Almeida) is only **Tier 3** —
open license, but figure-only for the size axis. Every other ranked source is
**Tier 4** (closed). No **Tier 1/2** (open tabulated) source has been
systematically scouted.

## Mandated Next Action

Per the preference order, the next Quantum source step is a **Tier 1/2 open
tabular scout**, performed *before* committing effort to Almeida's figure
digitization (which remains a valid Tier-3 fallback, now license-clear):

1. **Tier 1 search** — open-data repositories (Zenodo, Figshare, OSF) and
   open materials/nanocrystal databases for published per-sample
   (size, first-exciton-energy) tables for any well-characterized QD material
   (InP, CdSe, PbS, CuInS2, etc.).
2. **Tier 2 search** — recent open-access (CC BY) optical-property papers whose
   primary or supplementary tables list per-sample size and E1s/peak values
   (not just a sizing equation).

Per-candidate verification checklist (all three required to qualify as Tier 1/2):

- open license (CC BY / CC0) on the exact version that holds the data;
- per-sample tabulated (size, energy) values — a fitted sizing equation alone
  does **not** qualify (it is calibration-derived);
- extractable size and property semantics (units, size axis, peak kind).

A bounded scout for this review found that open candidates plausibly exist
(e.g. open-access nanocrystal optical-property papers and arXiv preprints), but
none was verified in this pass as simultaneously open-licensed **and**
per-sample tabulated, so the qualified Tier 1/2 scout is the recommended
follow-up rather than an assertion of a specific ready source.

## Consistency With TASK-0741

This does not retract the Almeida work. TASK-0741 cleared Almeida's license and
checksum-pinned the source, which is useful regardless. The preference order only
redirects the **next** effort: scout Tier 1/2 first; fall back to Almeida's
Tier-3 figure digitization if no Tier 1/2 source qualifies.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (workflow/policy task; no scientific metric).
- **Canonical destination:** the new preference-order section in
  `docs/fresh-data-intake-protocol.md` plus this application review; a one-line
  pointer is added to the Quantum campaign page.
- **Review tier:** `none`.
- **Gate A status:** not attempted. **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** workflow memory only; no knowledge entry.
- **Result artifact impact:** no `results/` artifact or `qd-*.yaml` row created.
- **Limitations / blockers:** the preference order is guidance, not an automated
  gate; a qualified Tier 1/2 source for Quantum still has to be found by a
  follow-up scout.
