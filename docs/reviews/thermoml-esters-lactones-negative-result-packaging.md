# RESULT-0028 Packaging: ThermoML Esters/Lactones Failed-Family Negative Control

- Task: `TASK-0936`
- New artifact: `RESULT-0028` (`results/EXP-0020/RUN-0002/result.yaml`)
- Source evidence: `RESULT-0026` (`results/EXP-0020/RUN-0001/`, byte-unchanged)
- Preflight basis: `TASK-0918`
  ([thermoml-esters-lactones-negative-result-preflight.md](thermoml-esters-lactones-negative-result-preflight.md))
- Packager: `scripts/package_thermoml_esters_lactones_negative_result.py`
- Run date: `2026-07-06`
- Gate A: **`PASS`** (`scripts/apl_check_result_publication.py`)
- Review tier: `AGENT_PUBLISHED`
- Verdict: `INVALID` (bounded family-survival failure; schema-safe negative wording per the preflight)

## What Was Packaged

The `TASK-0918` preflight recommended `PACKAGE_AS_NEGATIVE_RESULT`: preserve
the clean, predeclared, deterministic esters/lactones failure inside
`RESULT-0026` as a first-class bounded negative/control result instead of
leaving it only as review-note memory. RESULT-0028 records exactly that, using
only the committed `RESULT-0026` metrics at a pinned commit:

> On the committed 40-row ThermoML normal-boiling-temperature fixture, the
> frozen Joback estimator cleared the aggregate and seven of eight held-out
> family margins, but esters/lactones did not clear the predeclared +5 K
> family-survival margin: Joback MAE was 26.134 K versus 20.584245 K for the
> molecular-weight-only control across five rows.

| Quantity | Value |
| --- | ---: |
| Family margin vs best non-oracle control | `-5.549755` K |
| Required survival margin | `+5.0` K |
| Margin shortfall | `10.549755` K |
| Joback MAE (5 rows) | `26.134` K |
| Molecular-weight-only control MAE (5 rows) | `20.584245` K |

The aggregate-positive context is preserved verbatim inside the package:
`RESULT-0026` stays aggregate-positive and family-dependent (aggregate margin
`28.502118` K; 7/8 families clear), and its metrics, verdict, review tier, and
golden-result pinning are untouched.

## Determinism And Gate Status

- The packager is deterministic from committed inputs (source metrics read at
  the pinned commit via `git show`; constant `generated_at`): a second run into
  a disposable directory reproduced the committed RUN-0002 package
  **byte-identically** (`diff -r` empty).
- Gate A: `PASS` via `scripts/apl_check_result_publication.py` — all nine
  `gates_checked` items hold, input hashes recorded, limitations listed, no
  claim/knowledge update proposed.
- Gate B: **not attempted** (correctly pending a different identity). Honest
  routing note: the recorded packaging-script command is not on the Gate B
  safe-command allowlist, so the formal helper will report
  `BLOCKED unsupported-command` (the same structural situation as RESULT-0027,
  see [exoplanet-result-0027-gate-b-replay.md](exoplanet-result-0027-gate-b-replay.md)).
  The available validation routes are a byte-identical repackage replay by an
  independent identity, or a later maintainer-approved `physics-lab run`
  workflow bridge mirroring `TASK-0907`.

## Boundaries Preserved

- Negative statement scoped to the five esters/lactones rows inside the
  committed 40-row `Tb` fixture; no claim that Joback fails generally for
  esters, lactones, boiling points, or property estimation.
- The molecular-weight-only control is diagnostic within the fixture, not a
  proposed estimator.
- ThermoML attribution, DOI (`10.18434/mds2-2422`), archive SHA-256, and the
  raw-archive non-vendoring boundary are carried into the package unchanged.
- No chemical-design, safety, synthesis, process-design, universal-Joback, or
  broad property-estimation wording anywhere in the package.
- No claim, knowledge, prediction, fixture-row, or Joback-coefficient change.

## Output-Routing Summary

- **Task verdict:** `INVALID` for the packaged family-survival failure
  (bounded negative/control result; the aggregate `RESULT-0026` verdict is
  unaffected).
- **Canonical destination:** `results/EXP-0020/RUN-0002/` (RESULT-0028) plus
  this review note.
- **Review tier:** `AGENT_PUBLISHED` (Gate A `PASS`; Gate B pending an
  independent identity).
- **Gate A status:** `PASS`. **Gate B status:** not attempted; next step
  documented above.
- **Claim impact:** none (no-op claim stubs committed in the package).
- **Knowledge impact:** none.
- **Result artifact impact:** one new artifact (RESULT-0028); `RESULT-0026`
  byte-unchanged.
- **Publication blocker:** none for the `AGENT_PUBLISHED` tier; tier upgrades
  remain gated on independent validation and maintainer review.
