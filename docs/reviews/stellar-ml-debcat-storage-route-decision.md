# Stellar M-L DEBCat Storage Route Decision

**Task:** `TASK-0707`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Mode:** planning only (no fetch, no row transcription, no metrics)
**Decision:** `ROUTE2_ACCEPTED_NORMALIZED_ROWS_WITH_LEDGER_RAW_DEBS_DAT_NOT_COMMITTED`

## Scope

This note records the storage decision for the DEBCat source path after the
luminosity-provenance policy in `TASK-0688`. It decides how later row curation
may use the checksum-pinned DEBCat source artifact. It does not fetch
`debs.dat`, transcribe values, normalize component rows, compute luminosities,
fit mass-luminosity exponents, create `RESULT-*` artifacts, or promote claims.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/stellar-ml-luminosity-provenance-and-license-route.md` | Recommends Route 2 after defining luminosity provenance. |
| `data/textbook_formula_audit/stellar_ml/source_manifest.yaml` | Campaign source manifest and DEBCat row-class policy. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/provenance.yaml` | Locator, retrieval metadata, checksum, citation, and blockers. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/raw_derived_policy.md` | Raw/derived artifact guardrail from the metadata-only package. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/blocker_notes.md` | Lists the previous maintainer-route blocker. |

## Route Decision

Route 2 is accepted:

`metadata-only checksum pinning + reviewed extraction ledger + normalized row commit`

This keeps the raw value-bearing DEBCat ASCII table out of the repository while
allowing a later row-curation task to commit normalized component rows derived
from the checksum-pinned source copy. The row-curation task must include a
reviewed extraction ledger that maps every committed normalized row back to the
source locator/checksum, source column semantics, component identity, luminosity
path, citation, and exclusion/uncertainty policy.

## Route Comparison

| Route | Decision |
| --- | --- |
| Route 1: explicit permission for raw/derived DEBCat redistribution | Not selected. It would be cleaner for raw archival, but it is not required before the first source-gated row package. |
| Route 2: metadata-only checksum + extraction ledger + normalized row commit | **Selected.** It preserves reproducibility without committing raw `debs.dat` under unclear redistribution terms. |
| Route 3: replacement source | Not selected. DEBCat remains the best first source for direct dynamical component masses; replacement remains a contingency if row-curation review fails. |

## Metadata Updates

The DEBCat source manifest and provenance metadata now record:

- storage route decision: `route2_confirmed_by_task_0707`;
- raw artifact commit: still forbidden;
- normalized component-row commit: allowed only in a later row-curation task;
- required ledger fields: source checksum, source locator, source column mapping,
  binary system id, component role, luminosity provenance path, uncertainty
  class, citation, and exclusion reason when applicable;
- source checksum binding:
  `326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`.

## Row-Curation Preconditions

A later DEBCat row-curation task may proceed only if it:

1. uses the checksum-pinned source artifact metadata already recorded;
2. keeps raw `debs.dat` uncommitted;
3. commits normalized component rows only, not the raw source table;
4. includes an extraction ledger with per-row source-column and luminosity-path
   provenance;
5. follows the `TASK-0657` physical-binary-system no-leakage rule;
6. follows the `TASK-0688` luminosity policy:
   catalogue log-luminosity first, Stefan-Boltzmann fallback only when the
   catalogue luminosity path is missing or inadmissible;
7. excludes Gaia, isochrone, or other model-derived masses as benchmark truth;
8. freezes holdout lanes before any exponent fit or residual inspection.

## Still Forbidden

- committing raw `debs.dat`;
- fetching or refreshing the DEBCat source in this task;
- transcribing values in this task;
- fitting or tuning the stellar mass-luminosity exponent;
- creating benchmark metrics, `RESULT-*`, `PRED-*`, `CLAIM`, or `KNOW` artifacts;
- presenting the later empirical audit as a discovery or stellar-evolution claim.

## Limitations

- This decision accepts the storage route, not the row package itself.
- No live licence recheck or external permission request was performed here.
- The later row-curation task must still verify actual column headers, fill
  rates, component pairing, uncertainty semantics, and row exclusions.

## Output Routing Summary

- **Task verdict:** `not_applicable` (planning/storage route gate); decision
  `ROUTE2_ACCEPTED_NORMALIZED_ROWS_WITH_LEDGER_RAW_DEBS_DAT_NOT_COMMITTED`.
- **Canonical destination:** this review note,
  `docs/reviews/stellar-ml-debcat-storage-route-decision.md`, plus source
  manifest/provenance metadata updates.
- **Review tier:** none; no `RESULT-*` / `PRED-*` artifact.
- **Gate A status:** not applicable because no rows or metrics were produced.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none; row-curation routing only.
- **Publication blocker:** empirical Stellar M-L metrics remain blocked until a
  later row-curation task commits normalized rows, an extraction ledger, and a
  frozen no-leakage holdout manifest.
