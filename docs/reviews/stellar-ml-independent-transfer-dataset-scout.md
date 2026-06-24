# Stellar M-L Independent Transfer Dataset Scout

- Task: `TASK-0819`
- Date: `2026-06-24`
- Mode: planning-only source/regime scout
- Decision: `STELLAR_TRANSFER_ROUTE_READY_FOR_TASK`
- Selected route: disjoint high-mass DEBCat regime (`mass_solar > 2.0`)

## Scope

This scout chooses exactly one future transfer route for the Stellar M-L
campaign after `RESULT-0022`. It does not fetch live row values, run a
benchmark, change the frozen DEBCat main-sequence slice, edit `RESULT-0022`,
or create/promote a claim or knowledge artifact.

The selected route is a disjoint DEBCat regime transfer, not a new independent
source transfer. It is the lowest-risk next transfer surface because it uses
the already committed Route 2 DEBCat rows and the existing provenance posture,
while testing whether the `RESULT-0022` reading survives outside the
`0.5-2.0 M_sun` main-sequence-compatible slice.

## Inputs Reviewed

- `results/EXP-0015/RUN-0001/result.yaml`
- `docs/reviews/stellar-ml-result0022-gate-b-replay.md`
- `docs/reviews/stellar-ml-alternate-split-stability-audit.md`
- `docs/reviews/stellar-ml-piecewise-complexity-audit.md`
- `docs/reviews/stellar-ml-debcat-result-routing.md`
- `data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`
- `data/DATA_LICENSES.yaml`
- DEBCat catalogue metadata page: `https://www.astro.keele.ac.uk/jkt/debcat/`
- DEBCat publication metadata: Southworth 2014, `https://arxiv.org/abs/1411.1219`

Only repository-committed rows and public source metadata were inspected. No
live DEBCat row table was downloaded, no stellar values were copied from the
web, and no model or metric comparison was run.

## Selected Route

Route: **high-mass DEBCat regime transfer**.

Definition for a future task:

- source family: committed DEBCat Route 2 normalized rows
- candidate filter: admitted rows with `mass_solar > 2.0`
- required split unit: `system_id`, not component row
- required target quantity: `log_luminosity_solar`
- allowed provenance classes: direct dynamical mass rows already present in
  the committed dataset; luminosity provenance must remain row-level
- non-goal: no broad stellar-evolution or universal mass-luminosity statement

Local committed-row feasibility check:

| Surface | Count |
| --- | ---: |
| Admitted components with `mass_solar > 2.0` | 217 |
| Distinct systems in that route | 121 |
| Train lane components | 110 |
| Validation lane components | 51 |
| Holdout lane components | 56 |
| `main_sequence_compatible` flags | 92 |
| `evolved` flags | 73 |
| `unknown` flags | 41 |
| `subgiant` flags | 11 |
| Catalogue-reported luminosity rows | 187 |
| Stefan-Boltzmann-derived luminosity rows | 30 |

This is large enough to justify a future scoped transfer task. It is not large
or homogeneous enough to justify a claim without a later benchmark, stage
controls, and maintainer review.

## Admissibility Table

| Requirement | Assessment |
| --- | --- |
| Source accessibility | Ready for a future task because the required rows are already committed. The live DEBCat page remains useful only as source metadata, not as a value source for this scout. |
| License/reuse posture | Compatible with the existing DEBCat Route 2 posture recorded in the repository. Future work should cite the DEBCat publication/source and preserve the CC BY 4.0 grant/provenance note already used by `RESULT-0022`. |
| Row identity | Compatible. Rows carry `row_id`, `system_id`, and component identifiers; future split discipline must remain system-level to avoid binary-component leakage. |
| Mass provenance | Compatible. The selected high-mass rows preserve `mass_provenance_class: direct_observation`. |
| Luminosity provenance | Mixed but auditable. Most high-mass rows use `debcat_catalogue_reported_logL`; 30 use `stefan_boltzmann_from_debcat_logR_logT`. A future task must stratify or report this mixture. |
| Uncertainty semantics | Partly ready. Mass uncertainty classes are mostly `precise`, while luminosity uncertainty includes `standard`, `coarse`, `precise`, and a small `unknown` tail. A future task must predeclare exclusion or sensitivity handling. |
| Evolutionary-stage labeling | Ready only as a controlled regime stress route. The route intentionally includes stage diversity; a future task must either predeclare high-mass all-stage diagnostics or split `main_sequence_compatible` from evolved/subgiant/unknown rows. |
| Leakage from `RESULT-0022` | Acceptable if the future task filters `mass_solar > 2.0`, keeps system-level splits, and does not tune choices from `RESULT-0022` holdout residuals. |

## Blockers And Guardrails

- This is a **regime transfer**, not an independent public-catalog transfer.
  It can test scope extension inside the same committed DEBCat source posture,
  but it cannot by itself prove external-source validity.
- A future benchmark must not reuse the `RESULT-0022` headline wording beyond
  its frozen `0.5-2.0 M_sun` slice.
- The high-mass route is stage-confounded. Evolved, subgiant, and unknown-stage
  rows must be preserved as explicit strata or exclusions.
- Luminosity provenance is mixed. A future task should include a provenance
  sensitivity table before any result-promotion wording.
- No live DEBCat values should be fetched during the benchmark task unless a
  separate source-refresh task pins a new source artifact and checksum trail.

## Future Task Recommendation

Open a future benchmark task only if it is scoped as:

`Run a high-mass DEBCat regime-transfer benchmark for RESULT-0022 boundaries`.

Minimum contract:

- use only committed rows unless a separate source-refresh task is approved;
- filter `mass_solar > 2.0`;
- split by `system_id`;
- predeclare whether the primary lane is all-stage high-mass or
  high-mass-main-sequence-compatible only;
- compare fixed textbook baselines, train-fitted exponent, and a null baseline
  without adding new model families;
- report stage and luminosity-provenance sensitivity;
- no claim, knowledge, or universal-law wording.

## Output Routing Summary

- Task verdict: `STELLAR_TRANSFER_ROUTE_READY_FOR_TASK`
- Canonical destination:
  `docs/reviews/stellar-ml-independent-transfer-dataset-scout.md`
- Review tier: none; planning/source scout only.
- Gate A status: not applicable; no `RESULT-*` artifact was created.
- Gate B status: not applicable; no independent replay target was created.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: `RESULT-0022` and the frozen DEBCat slice are unchanged.
- Publication blocker: any future high-mass benchmark must handle stage
  confounding and luminosity-provenance mixture before interpretation.
