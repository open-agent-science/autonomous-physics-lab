# Stellar M-L DEBCat Row-Readiness Gate

**Task:** `TASK-0658`
**Campaign:** `textbook-formula-audit` (Stellar mass-luminosity surface)
**Mode:** planning only
**Gate verdict:** `SOURCE_PINNED_ROWS_BLOCKED`

## Scope

This gate decides whether the DEBCat detached-eclipsing-binary source — pinned
metadata-only by `TASK-0628` and governed by the holdout/no-leakage protocol
from `TASK-0657` — now supplies enough admissible **mass**, **luminosity**,
**uncertainty**, and **system-identifier** evidence to start a first
mass-luminosity row package. If any of those axes is missing, model-derived
only, or licence-blocked, the gate preserves the blocker explicitly instead of
authorising row curation.

It runs only on committed repository evidence. It does **not** fetch DEBCat
rows, parse `debs.dat`, transcribe or normalise values, compute luminosities,
fit the `L/L_sun = (M/M_sun)^alpha` exponent, run residual or benchmark
metrics, create result/prediction artifacts, or promote any Stellar M-L claim.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/textbook-stellar-ml-debcat-source-artifact-package.md` | `TASK-0628` source-artifact package; `DEBCAT_METADATA_PINNED_ROWS_BLOCKED`. |
| `docs/reviews/stellar-ml-debcat-holdout-leakage-protocol.md` | `TASK-0657` system-level holdout/no-leakage protocol. |
| `docs/reviews/textbook-stellar-ml-source-candidate-admissibility.md` | `TASK-0610` DEBCat source selection and deferred-luminosity decision. |
| `data/textbook_formula_audit/stellar_ml/source_manifest.yaml` | Campaign source manifest; DEBCat candidate entry, blockers, frozen baseline convention. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/README.md` | Package summary and guardrails. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/license_review.md` | Reuse posture; no explicit redistribution licence found. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/provenance.yaml` | Locator, checksum, retrieval metadata, `blocker_reasons`. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/extraction_notes.md` | Fields to preserve in a later row task; extraction not started. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/blocker_notes.md` | What is unblocked vs. what remains blocked; three maintainer routes. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/raw_derived_policy.md` | Raw/derived artifact policy; row curation not authorised. |

## Method

The gate re-evaluates the four row-readiness axes named in `TASK-0658`
(mass, luminosity, uncertainty, system identifiers) plus the cross-cutting
licence/storage axis, using the committed `TASK-0628` package and the
`TASK-0657` protocol as the authoritative evidence. Each axis is classified as
`PASS`, conditional, or `BLOCKER`. A first row package is authorised only if no
axis required for the benchmark is a `BLOCKER`. The benchmark target is the
textbook relation `L/L_sun = (M/M_sun)^alpha` with the manifest's frozen
audit range `0.5 <= M/M_sun <= 2.0`, so an admissible **luminosity** column is
not optional: it is the dependent variable.

## Gate Findings

### 1. System and component identifiers — `PASS`

DEBCat is a catalogue of physical binary systems with primary/secondary
component structure. The package records `binary_system_identifier`,
`component_role`, and `source_reference_notes` as fields to preserve, and the
holdout protocol's primary no-leakage key (`physical_binary_system`) is
expressible against them. Identity evidence is sufficient to support
system-level lane assignment once rows exist. This axis is not the blocker.

### 2. Mass admissibility — `CONDITIONAL_PASS_PENDING_LICENCE_AND_SCHEMA`

DEBCat supplies **direct dynamical component masses** from detached eclipsing
binaries — the exact independent-mass property the campaign requires, and a
deliberate alternative to Gaia/isochrone model-derived masses (which remain
forbidden as benchmark truth). The mass axis is admissible *in principle*, but
it is not yet row-ready because:

- the value-bearing `debs.dat` table is not committed and no normalised
  component-row schema has been reviewed (`row_schema_kind:
  stellar_ml_component_rows_pending`);
- `extraction_method: not_extracted`; no row count after inclusion/exclusion
  filters exists;
- admissibility is gated by the licence/storage decision in finding 5.

Mass alone, even once licensed and schema-reviewed, is **not** sufficient for a
benchmark row package, because the relation also needs luminosity (finding 3).

### 3. Luminosity admissibility — `BLOCKER`

This is the load-bearing blocker. Luminosity is the dependent variable of the
audited relation, and committed evidence does not make any DEBCat luminosity
input admissible:

- the `TASK-0657` protocol lists luminosity inputs as **inadmissible** until a
  later row-readiness task defines source, conversion, and uncertainty
  semantics, and explicitly bars "DEBCat value-bearing table rows while the
  current package remains metadata-only";
- `provenance.yaml` records `LUMINOSITY_PROVENANCE_NOT_DEFINED` as a blocker and
  the manifest marks `derived_luminosity` as "Blocked until luminosity
  provenance and conversion policy are defined";
- the source-selection review (`TASK-0610`) already deferred luminosity:
  "Luminosity is not benchmark-ready by default."

Provenance is not merely missing paperwork. Whether DEBCat exposes a directly
reported luminosity or one that must be reconstructed from the directly
measured radius and effective temperature (a Stefan–Boltzmann
`log L/L_sun = 2 log(R/R_sun) + 4 log(Teff/Teff_sun)` derivation, with an
adopted solar `Teff` / bolometric zero point and propagated `R`/`Teff`
uncertainties) is itself unresolved in committed evidence and must not be
assumed. A reconstructed luminosity would be a `derived_luminosity` row class,
not a direct observation; it is methodologically acceptable for an M-L fit only
if it does not import model-derived *mass*, but its derivation and uncertainty
path must be pinned before any row is admitted. The gate must not fetch the
table to settle this, so the axis stays a `BLOCKER`.

### 4. Uncertainty semantics — `PARTIAL` (mass yes, luminosity no)

The package commits to preserving component **mass uncertainty** semantics
separately from radius, temperature, and luminosity, and the manifest's
`uncertainty_semantics` note requires keeping primary/secondary pairing and
uncertainty intact. That is adequate planning for the mass axis. **Luminosity
uncertainty** semantics are undefined and inherit finding 3's blocker: with no
admitted derivation path there is no uncertainty model for the dependent
variable. Uncertainty readiness is therefore partial and cannot clear the gate
on its own.

### 5. Licence, redistribution, and storage — `BLOCKER`

`TASK-0628` found no explicit redistribution licence on the consulted DEBCat
page beyond a citation request, so the package is metadata-only
checksum-pinned (`raw_artifact_commit_allowed: false`,
`derived_artifact_commit_allowed: false`). The source identity is well pinned
(stable locator, `sha256
326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`, HTTP
`Last-Modified`/`ETag`, 374-system catalogue log), but a first row package
cannot commit value-bearing rows until a maintainer selects one of the three
routes recorded in `blocker_notes.md`:

1. explicit permission/licence basis for committing DEBCat-derived rows;
2. a metadata-only checksum route with a reviewed extraction ledger and no raw
   table committed;
3. a replacement source with clearer redistribution terms.

### 6. Holdout / no-leakage readiness — `PASS_AT_POLICY_LEVEL`

`TASK-0657` provides a complete system-level split/no-leakage protocol
(`train`/`validation`/`holdout`/`excluded` lanes keyed on physical binary
system, frozen-before-residuals, model-derived masses barred, luminosity gated
separately). The policy is sufficient; it cannot be exercised yet because no
rows exist to assign. This axis does not block the gate, but it also cannot
substitute for the missing rows.

## Decision

**Row curation does not proceed.** DEBCat is a correctly pinned, well-identified
direct-mass source, but a first Stellar M-L row package is blocked on two
independent axes:

- **Luminosity provenance** (finding 3) — the benchmark's dependent variable
  has no admissible source/derivation/uncertainty policy, and is explicitly
  barred by the merged holdout protocol;
- **Licence/storage** (finding 5) — value-bearing rows cannot be committed
  until a maintainer chooses a redistribution route.

Mass, identifiers, and the holdout policy are ready or conditionally ready, but
none of them lets the benchmark run while luminosity and licence remain blocked.
This matches the `TASK-0658` instruction to preserve a blocker review when
luminosity evidence is missing or model-derived only.

## What Would Reopen Row Curation

Both of the following must land before a DEBCat row-curation/row-readiness task
should run:

1. **Maintainer licence/storage routing decision** for DEBCat — pick route 1,
   2, or 3 from `blocker_notes.md` so the storage shape of any committed rows is
   settled.
2. **Luminosity-provenance policy task** — determine whether DEBCat luminosity
   is directly reported or must be reconstructed from radius and effective
   temperature; pin the conversion and uncertainty semantics; confirm the
   derivation does not import model-derived mass truth; and decide whether
   luminosity is admitted as a `direct_observation` or `derived_luminosity` row
   class.

After both land, a row-curation task may build the system-to-lane manifest
under `TASK-0657`, freeze it before any residual inspection, and only then hand
off to a benchmark task. A licence decision **alone** would at most permit a
mass-and-identifier scaffold; that scaffold still cannot run the M-L benchmark
because luminosity stays inadmissible, so it is a partial step, not row
readiness for the benchmark.

## Recommended Next Tasks

- A **luminosity-provenance gate** for the Stellar M-L surface (the binding
  scientific blocker; should run first or in parallel with the licence
  decision).
- A **maintainer licence/storage routing decision** for the DEBCat artifact.
- Defer any **row-curation / exponent-audit** task until both above are merged.

## Limitations

- Uses committed repository evidence only; no live fetch of `debs.dat`, the
  catalogue page, the DEBCat paper, or any supplement was performed.
- Does not inspect actual DEBCat column contents, so it cannot state whether a
  directly reported luminosity column exists; that determination is delegated to
  the recommended luminosity-provenance task.
- Does not assign row-level holdout lanes, transcribe rows, or compute any
  value, by design.
- Does not make a licence determination; that decision is reserved for the
  maintainer.

## Output-Routing Summary

- **Task verdict:** `not_applicable` for a scientific claim; row-readiness gate
  classification is `SOURCE_PINNED_ROWS_BLOCKED`.
- **Canonical destination:** this review note,
  `docs/reviews/stellar-ml-debcat-row-readiness-gate.md`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact is proposed.
- **Gate A status:** not attempted (no dataset rows or metrics produced).
- **Gate B status:** not attempted.
- **Claim impact:** no claim change; no Stellar M-L exponent, residual, or law
  is asserted.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** Stellar M-L row curation remains blocked by
  undefined luminosity provenance and an unresolved DEBCat licence/storage
  route; direct dynamical masses and system identifiers are ready or
  conditionally ready, but cannot support the benchmark alone.
