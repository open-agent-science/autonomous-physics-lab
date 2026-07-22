# ThermoML Tb Feasible Expansion Contract Adjudication

Task: `TASK-1084`
Contract: `data/thermophysical/thermoml_tb_feasible_expansion_contract.yaml`

## Verdict

`REVISED_CONTRACT_READY_NO_SCORE`

The availability-capped, family-equal-weighted option clears a predeclared
count-only incremental-information floor. It is ready as a non-executable
contract for a later extraction task. No archive, selected identity, fixture
row, scientific value, or result artifact was opened, and no Joback score was
computed for this adjudication. A broad repository text search used to locate
control definitions surfaced snippets from prior performance documents. Those
snippets were excluded from the option comparison, information floor, and
selection; every decision quantity below is reproduced from aggregate counts.

## Frozen Inputs

The decision uses only committed aggregate identity counts and existing
contract metadata:

| Family | Admissible non-conflict identities | Existing rows | Revised cap | Maximum additions |
| --- | ---: | ---: | ---: | ---: |
| acids | 6 | 5 | 6 | 1 |
| esters/lactones | 48 | 5 | 10 | 5 |
| ketones | 8 | 5 | 8 | 3 |
| alcohols/phenols | 29 | 5 | 10 | 5 |
| ethers | 12 | 5 | 10 | 5 |
| halocarbons | 15 | 5 | 10 | 5 |
| aromatic hydrocarbons | 20 | 5 | 10 | 5 |
| alkanes/cycloalkanes | 11 | 5 | 10 | 5 |

The counts come from the checksum-pinned ThermoML v1.2.6 aggregate preflight.
They contain no identities or `Tb` values.

## Incremental-Information Rule

The following floor was fixed before selecting among the three options:

- retain all eight families with exactly `1/8` aggregate weight each;
- retain at least six identities in every family;
- reach at least 64 total rows and at least 24 identities beyond the existing
  40-row fixture;
- keep effective family count at 8;
- reach an equal-family-weighted effective row count of at least 64, using
  `64 / sum_f(1 / n_f)`.

The 64-row threshold is the balanced equivalent of eight identities per
family. It requires a 60% increase over the existing fixture while refusing to
treat raw rows from dense families as additional family-level groups.

## Option Comparison

| Option | Row ceiling | Maximum additions | Effective families | Equal-family weighted effective rows | Information floor | Decision |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Balanced six per family | 48 | 8 | 8 | 48.000000 | fail | Reject: one added identity per family is low incremental value. |
| Availability-capped, family-equal weighting | 74 | 34 | 8 | 71.775701 | pass before article-cap verification | Select with hard extraction stop conditions. |
| STOP | 40 | 0 | 8 | 40.000000 | fail | Fallback if later extraction cannot clear the frozen gates. |

The selected option does not claim more than eight effective family groups.
Its incremental value is narrower: more independent compound identities
within the same predeclared families, with dense families prevented from
dominating the primary aggregate.

## Frozen Future Contract

A later extraction task may retain the existing 40 rows and add distinct
eligible identities up to family-specific caps of 6, 10, 8, 10, 10, 10, 10,
and 10 in the existing family order. It must:

1. use only the exact checksum-matching local archive and perform no live
   fetch;
2. preserve the frozen pure-component, identity, uncertainty, conflict,
   family, and Joback-coverage filters;
3. choose additions through deterministic molecular-weight quantile positions
   with InChIKey tie-breaking, never through a value, error, residual, or prior
   family outcome;
4. apply the five-row source-article cap across existing and added rows;
5. freeze selected identities and counts before any benchmark task exists;
6. stop without a partial fixture if the article cap or any other filter drops
   the surface below the information floor.

The future benchmark remains a separate task. Its primary aggregate gives each
family weight `1/8` and each row within a family weight `1/n_family`. It keeps
the eight leave-one-family-out folds, fixed Joback estimator, existing five
controls, shuffle seed, 5 K margin, and six-of-eight family survival rule.

PASS requires Joback to beat the best eligible non-oracle control by the fixed
margin both in the equal-family aggregate and in at least six families. FAIL
requires the symmetric control-dominated outcome. Every mixed or unstable
outcome is INCONCLUSIVE. Threshold, control, family, or route changes after
scores become visible are forbidden.

## Rights Boundary

The merged maintainer decision
`decisions/DEC-20260708-thermoml-option-a.yaml` supplies an approved maximum
scope of 80 attributed factual rows. This narrower 74-row ceiling stays inside
that scope. The future fixture must retain
`limited_factual_extract_with_attribution` and
`covered_by_repo_license: false`.

The approval does not permit archive bytes, extracted XML/JSON, a normalized
corpus, copied source layout, a dataset DOI, Zenodo, or any external release.
The exact five-row source-article cap and per-row attribution remain mandatory.
The decision record has not been applied by this planning task; extraction and
rights metadata validation belong to the later fixture PR.

## Limitations

- Aggregate counts do not prove that the five-row source-article cap can fill
  every family cap. That is a hard future stop, not a reason to inspect
  identities now.
- The incidental repository-search snippets are a procedural contamination
  caveat. They were not used in the decision, and the contract records no
  prior metric, residual, or family outcome; independent review should verify
  the count-only arithmetic before merge.
- The revision increases within-family identity coverage but adds no ninth
  family and does not increase effective family count beyond eight.
- Contract readiness is not evidence that Joback transfers, fails globally,
  or supports production property prediction.
- No chemical-design, process, synthesis, or safety conclusion is made.

## Output Routing

- Canonical destination: the value-blind contract and this review note.
- Source readiness: ready for a separate gated extraction task.
- Benchmark readiness: contract ready; expanded fixture does not yet exist.
- Future task routing: advisory only. This PR does not create or imply an
  executable task; any extraction requires a separately maintainer-assigned
  canonical task and fresh claim.
- Gate A: not attempted.
- Gate B: not applicable.
- Existing `RESULT-0026` and `RESULT-0028`: unchanged, not opened, and not used
  for option selection.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: future extraction must satisfy archive identity,
  article-cap, attribution, deterministic selection, incremental-information,
  and rights-metadata gates before committing any rows; scoring remains a
  separate task.
