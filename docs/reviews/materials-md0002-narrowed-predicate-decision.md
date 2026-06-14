# Materials MD-0002 Narrowed Predicate Decision

**Task:** `TASK-0737`
**Campaign:** Materials Property Residuals
**Mode:** planning only; no live fetch, no row values, no metrics
**Decision:** `NARROWED_PREDICATE_SELECTED_NO_FETCH`

## Scope

`TASK-0699` executed the maintainer-gated MD-0002 count check and stopped on the
predeclared row cap. The original stable-ternary-oxide contract produced 2738
included rows per axis after conservative non-oxygen-anion exclusion, exceeding
the 1500-row cap. This review chooses one narrower pre-acquisition predicate and
one fallback predicate for a later maintainer-gated acquisition.

This task does not run the Materials Project API, inspect material identifiers,
inspect formation-energy or band-gap values, compute metrics, tune baselines,
populate the holdout manifest, create `RESULT-*` / `PRED-*` / `CLAIM-*`
artifacts, or change the 1500-row cap.

## Inputs Reviewed

- `TASK-0699` and `docs/reviews/materials-md0002-acquisition-runbook-result.md`
- `docs/reviews/materials-md0002-acquisition-preflight-package.md`
- `docs/reviews/materials-md0002-acquisition-go-no-go.md`
- `docs/reviews/materials-md0002-wider-replication-slice-plan.md`
- `data/materials/md0002_holdout_manifest.yaml`
- `data/materials/fixtures/md0002_schema_fixture.yaml`
- `data/materials/schema.md`

## Cap-Exceeded Evidence

The maintainer-gated count check reported:

| Field | Value |
| --- | ---: |
| Raw candidate rows | 3473 |
| Included rows after stable ternary oxide and common non-O anion exclusion | 2738 |
| Cap per axis | 1500 |
| Cap status | EXCEEDED |

The runbook also recorded common non-O anion occurrence counts in the raw
candidate set (`S`, `Te`, `Se`, `I`, `F`, `H`, `N`, `Cl`, `Br`). Removing those
anion-like chemistries was not enough to reach the cap, so the next narrowing
must restrict the cation-pair family before any value-bearing rows are committed.

## Selected Predicate

Use a strict cation-family subset of the existing stable ternary oxide contract:

```yaml
predicate_id: md0002_alkali_alkaline_earth_3d_transition_oxide
base_query:
  elements_contains: O
  nelements: 3
  is_stable: true
  required_fields:
    - material_id
    - formula_pretty
    - composition
    - nelements
    - elements
    - energy_above_hull
    - is_stable
    - formation_energy_per_atom
    - band_gap
    - symmetry
    - theoretical
    - builder_meta
    - origins
post_query_inclusion:
  - "Exactly three distinct elements."
  - "Exactly one element is O."
  - "Exactly one non-O element is in alkali_or_alkaline_earth_cations."
  - "Exactly one non-O element is in first_row_transition_metal_cations."
  - "is_stable is true and energy_above_hull is 0.0 under the pinned Materials Project convention."
  - "formation_energy_per_atom and band_gap are both present."
  - "material_id, normalized composition, DFT functional, units, and database_version are present."
element_sets:
  alkali_or_alkaline_earth_cations:
    - Li
    - Na
    - K
    - Rb
    - Cs
    - Be
    - Mg
    - Ca
    - Sr
    - Ba
  first_row_transition_metal_cations:
    - Sc
    - Ti
    - V
    - Cr
    - Mn
    - Fe
    - Co
    - Ni
    - Cu
    - Zn
excluded_by_construction:
  - "binary oxides"
  - "quaternary-or-higher oxides"
  - "non-oxide rows"
  - "oxide rows with a non-O anion"
  - "p-block-only cation pairs"
  - "rare-earth-only cation pairs"
  - "transition-transition cation pairs"
  - "metastable rows"
  - "rows missing either planned axis"
```

This predicate keeps the original MD-0002 scientific question narrow: a stable
computed-DFT ternary-oxide retest of the MD-0001 formation-energy signal, with
band gap retained as a separate diagnostic axis. It uses cation-pair families
already named by the MD-0002 holdout scaffold (`alkali_transition_pair` and
`alkaline_earth_transition_pair`) and freezes a concrete transition-metal
subfamily before acquisition.

## Expected Row-Count Rationale

The selected predicate starts from the 2738-row cation-oxide count and removes
large cation-pair families that are not needed for the first widening retest:
rare-earth-transition, p-block-transition, transition-transition, rare-earth
main-group, p-block-only, and mixed/ambiguous families. It keeps two chemically
common families - alkali-transition and alkaline-earth-transition - across the
first-row transition metals, which should preserve enough row power for the
planned 70/15/15 split while materially reducing the count.

Expected outcome: the maintainer count check should land within the predeclared
600-1500 included rows per axis target. This is a pre-score estimate only; if the
count is outside the target, the acquisition task must report the count and
apply the stop behavior below rather than silently widening, truncating, or
subsampling.

## Fallback Predicate

If the selected predicate still exceeds the 1500-row cap in a count-only check,
use this single narrower fallback predicate:

```yaml
fallback_predicate_id: md0002_alkali_3d_transition_oxide
inherits:
  - md0002_alkali_alkaline_earth_3d_transition_oxide
change:
  alkali_or_alkaline_earth_cations:
    - Li
    - Na
    - K
    - Rb
    - Cs
```

This fallback removes the alkaline-earth cation branch (`Be`, `Mg`, `Ca`, `Sr`,
`Ba`) while keeping the same first-row transition-metal list, source, stability,
axis, checksum, attribution, and no-peek requirements. It is intended only as a
predeclared cap fallback, not as a residual-tuned choice.

If the primary predicate returns fewer than 600 included rows per axis, do not
auto-broaden in the same run. Report the count and let the maintainer decide
whether the lower row power is acceptable or whether a new planning task should
define a different predicate.

## Acquisition Handoff

The next maintainer-gated acquisition task should:

1. Run the selected predicate count check with `MP_API_KEY` outside the
   repository.
2. If the included count is 600-1500 per axis, proceed with the pinned snapshot,
   normalized formation-energy and band-gap files, checksum recording,
   attribution, and holdout/no-peek manifest population.
3. If the count exceeds 1500, stop and report the selected-predicate count. The
   fallback predicate may then be used only as the reviewed fallback path, with
   its own count recorded.
4. If the fallback also exceeds 1500 or misses required source/version/field
   metadata, stop and preserve a blocker note.
5. Do not compute baselines, residuals, rankings, material recommendations,
   synthesis/device/biomedical guidance, predictions, or claims.

## Holdout And Split Implications

No update to `data/materials/md0002_holdout_manifest.yaml` is required in this
task. The selected predicate still uses the existing pre-score split axes:

- material-id modulo 70/15/15;
- seeded random robustness splits;
- cation-pair family;
- spacegroup/prototype;
- property-range bins declared before residual inspection;
- source version.

The cation-pair split should record the selected acquisition family as a
pre-score dataset-scope label, not as a post-score filter.

## Rejected Options

| Option | Reason rejected |
| --- | --- |
| Raise the cap above 1500 | Violates the frozen contract and weakens cap discipline. |
| Randomly sample or truncate 2738 rows | Violates no-peek/source integrity and would make row inclusion arbitrary. |
| Filter by formation energy or band gap value | Uses value-bearing property axes before acquisition and risks residual tuning. |
| Filter by material desirability, synthesis relevance, or application class | Outside campaign scope and risks material-design claims. |
| Use p-block or rare-earth families as the first fallback | Scientifically possible later, but less directly tied to the MD-0001 cation-group retest path than alkali/alkaline-earth plus 3d transition-metal oxides. |

## Limitations

- This is a planning decision only; no Materials Project rows were fetched.
- Row-count expectations are chemistry-based estimates from the cap-exceeded
  runbook, not inspected source rows.
- The selected predicate may still exceed the cap or fall below the lower target.
- MD-0002 remains computed DFT only and cannot support measured-property,
  materials-design, synthesis, device, biomedical, or discovery claims.

## Output Routing Summary

- **Task verdict:** `NARROWED_PREDICATE_SELECTED_NO_FETCH`.
- **Canonical destination:** this review note,
  `docs/reviews/materials-md0002-narrowed-predicate-decision.md`.
- **Review tier:** source/dataset planning review; no `RESULT-*` or `PRED-*`
  artifact.
- **Gate A status:** not attempted.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** campaign routing only.
- **Publication blocker:** MD-0002 remains unpublished until a maintainer-gated
  acquisition executes the selected predicate, pins source version/checksums,
  and freezes the holdout manifest before any scoring.
