# Nuclear Shell-Axis Registry Target Batch Design

**Task:** TASK-0296  
**Scope:** target-batch design only  
**Recommended next gate:** maintainer review before TASK-0297 registration  

This review designs a conservative prospective target batch for a future
shell-axis registry mini-wave. It does not write `PRED-*` entries, fetch live
measurements, score a reveal, update claims, or promote sandbox evidence.

## Inputs Reviewed

- `docs/reviews/nuclear-shell-axis-stress-scout-001.md`
- `docs/reviews/nuclear-adversarial-stress-synthesis-after-0289.md`
- `docs/reviews/nuclear-prediction-registry-coverage-audit.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `data/nuclear_masses/factory_target_batches.yaml`
- `prediction_registry/nuclear_masses/PRED-0051.yaml`

## Design Guardrails

The proposed batch follows these guardrails:

- avoid adding pressure to the overrepresented exact targets `Ni-76`, `Ca-55`,
  `Ga-85`, and `Zn-80`;
- avoid the documented chain-neighbor holdout rows `Ca-54`, `Ga-83`, `Ga-84`,
  `Ni-74`, `Ni-75`, and `Zn-79`;
- avoid exact rows already screened as present in the committed measured or
  post-AME2020 holdout slices during this task (`In-132`, `In-131`, `Sb-133`,
  `I-137`);
- avoid reusing the exact high-visibility shell-magic batch rows `Cu-79`,
  `Kr-86`, `Te-134`, and `Xe-138`;
- include paired negative controls in the future registry mini-wave;
- freeze quantity, units, source boundaries, and reveal conditions before any
  future `PRED-*` entry is written.

The target identifiers below are design candidates for future source-state and
no-peek review. They are not claims that the nuclides are currently
unmeasured, newly measured, or reveal-eligible.

## Proposed Target Batch

Recommended batch id for future registration: `shell-axis-balanced-001`.

Quantity and units for any future registry entries:

- quantity: `mass_excess_mev`
- units: `MeV`
- prediction form: deterministic point estimate
- uncertainty: not claimed unless a later task defines a reviewed calibration

| Nuclide | Z | N | A | Shell-axis role | Rationale | Registry exact count at design time | Committed measured or holdout screen |
| --- | ---: | ---: | ---: | --- | --- | ---: | --- |
| `V-70` | 23 | 47 | 70 | lower N=50 shoulder | tests shell-axis behavior below the N=50 line without reusing `Ca-55` or `Ni-76` pressure | 0 | no committed exact-row hit found |
| `Mn-75` | 25 | 50 | 75 | N=50 line | keeps the lower shell probe near N=50 while staying away from the exact high-repeat targets | 0 | no committed exact-row hit found |
| `Co-77` | 27 | 50 | 77 | N=50 and near Z=28 | probes the proton-axis neighborhood without adding another `Ni-*` target | 0 | no committed exact-row hit found |
| `Cu-81` | 29 | 52 | 81 | upper N=50 shoulder | complements `Co-77` across Z=28 and avoids the repeated `Cu-79` exact row | 0 | no committed exact-row hit found |
| `Ag-129` | 47 | 82 | 129 | lower heavy N=82 line | extends shell-axis testing to the heavy shell line without using `Te-134` or `Xe-138` | 0 | no committed exact-row hit found |
| `Cd-130` | 48 | 82 | 130 | heavy N=82 line | adds a paired heavy-shell point below Z=50 with no current exact registry pressure | 0 | no committed exact-row hit found |
| `Sb-135` | 51 | 84 | 135 | upper heavy-shell shoulder | tests the upper side of the heavy shell region while avoiding `Sb-133` and `I-137` exact-row screens | 0 | no committed exact-row hit found |
| `Cs-139` | 55 | 84 | 139 | upper heavy-shell shoulder | provides a high-Z companion point away from the repeated `Xe-138` exact row | 0 | no committed exact-row hit found |

This eight-target batch is intentionally small. It creates two matched
four-target shell neighborhoods rather than a broad sweep, limiting future
multiple-testing pressure while preserving a meaningful light/heavy split.

## Deferred Or Excluded Targets

The following rows should not be used in the immediate shell-axis mini-wave
unless a maintainer explicitly changes the target-batch contract:

- high-repeat exact targets: `Ni-76`, `Ca-55`, `Ga-85`, `Zn-80`;
- documented chain-neighbor rows: `Ca-54`, `Ga-83`, `Ga-84`, `Ni-74`,
  `Ni-75`, `Zn-79`;
- committed exact-row screens from this task: `In-132`, `In-131`, `Sb-133`,
  `I-137`;
- repeated shell-magic batch rows: `Cu-79`, `Kr-86`, `Te-134`, `Xe-138`;
- source-state-risk rows that can be reconsidered only after explicit source
  manifest review: `Sn-132`, `Xe-136`, `Cs-137`, `Ba-136`, `La-139`,
  `Ce-140`.

## Future Mini-Wave Model And Control Shape

TASK-0297 can use this batch to register a small prospective mini-wave if the
maintainer approves the design. The recommended future wave is six registry
entries, all over the same eight targets:

| Future entry role | Candidate/control family | Origin | Purpose |
| --- | --- | --- | --- |
| primary candidate | proton-axis Gaussian | `STRESS-SHELL-001` / `SHELL-SCOUT-003` | strongest current sandbox signal |
| companion candidate | proton x neutron product | `STRESS-SHELL-002` / `SHELL-SCOUT-005` | tests whether coupled shell distance preserves direction |
| diagnostic candidate | neutron-axis Gaussian | `STRESS-SHELL-003` / `SHELL-SCOUT-002` | checks whether the N-axis subset behavior transfers |
| negative control | sign-inverted proton-axis Gaussian | `STRESS-SHELL-004` | must regress under the same reveal surface |
| negative control | near-null shell-axis correction | `STRESS-SHELL-006` | preserves a no-effect sanity check |
| reference control | frozen baseline reference | `RESULT-0015::model_fitted_semi_empirical` | anchors interpretation against the committed baseline |

The future registry task should freeze model coefficients and target rows
before any reveal source is inspected. It should not tune coefficients after
source availability is known.

## Frozen Source Boundaries

Before registration, the future task should freeze:

- the exact registry snapshot and repository commit used for target rows;
- the baseline reference, currently `RESULT-0015::model_fitted_semi_empirical`;
- the candidate formulas and coefficients from the reviewed shell-axis stress
  lane, without adding new free parameters;
- the source manifest format required by
  `docs/nuclear-reveal-source-readiness-checklist.md`;
- an explicit `live_external_fetch_allowed: false` boundary unless a later
  maintainer-approved reveal task changes that rule.

## Reveal Conditions

A later reveal or scoring task should proceed only if all of these conditions
are true:

- the source manifest names the source, version or access date, archive state,
  value semantics, units, and checksum or archive limitation;
- no-peek review confirms the source was not inspected before the relevant
  future registry entries were frozen;
- target matching is deterministic by `(Z, A)` or an equivalent reviewed key;
- measured, unmeasured, ambiguous, and source-absent rows are separated before
  scoring;
- partial reveal handling is predeclared;
- negative controls are scored and reported next to the candidate entries;
- excluded rows remain excluded unless a maintainer explicitly approves a new
  batch design.

## Limitations

- This task performs target-batch design only.
- No live measurements were fetched.
- No `prediction_registry/nuclear_masses/PRED-*.yaml` files were written.
- No reveal score, claim, knowledge entry, or canonical result was promoted.
- Exact-row absence from committed repository datasets is not equivalent to a
  public source-state claim.
- The shell-axis evidence remains sandbox-grade until a future reviewed
  prospective registry and reveal workflow evaluates it.

## Verdict

`REVIEW_READY` as a conservative target-batch design. The recommended next
step is maintainer review of `shell-axis-balanced-001`. If approved, TASK-0297
can freeze a small prospective mini-wave with paired negative controls.
