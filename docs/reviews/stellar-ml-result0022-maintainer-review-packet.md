# Stellar M-L RESULT-0022 Maintainer Review Packet

- Task: `TASK-0812`
- Result: `RESULT-0022`
- Experiment: `EXP-0015`
- Current review tier: `AGENT_VALIDATED`
- Decision authority: maintainer
- Packet verdict: `MAINTAINER_REVIEW_READY`

## Purpose And Boundary

This packet assembles the existing Stellar mass-luminosity evidence for a
maintainer decision. It does not change `RESULT-0022`, rerun a model
comparison, create or promote a claim or knowledge artifact, or broaden the
audited population.

The supported conclusion is narrow:

> The textbook single exponent `alpha=3.5` is inadequate as the sole baseline
> on the frozen DEBCat main-sequence-compatible `0.5-2.0 M_sun` slice under
> the committed system-level split and completed controls.

This is not a universal falsification of `alpha=3.5`, a universal
mass-luminosity law, a stellar-evolution result, Gaia-derived truth, or a
discovery claim.

## Evidence Chain

| Stage | Evidence | Outcome |
| --- | --- | --- |
| Source and dataset publication | `docs/reviews/stellar-ml-debcat-full-dataset-publication.md` | Full normalized DEBCat rows and frozen holdout manifest committed under CC BY 4.0 after an explicit grant; raw `debs.dat` remains uncommitted. |
| Scope reconciliation | `docs/reviews/stellar-ml-debcat-scope-flag-reconciliation.md` | Dataset metadata permits the frozen benchmark and alpha fit, while claim promotion, prediction use, and live fetch remain disallowed. |
| Gate A publication | `results/EXP-0015/RUN-0001/gate_a_report.md` | `PASS`, 9/9 checks; published as a scoped `AGENT_PUBLISHED` result. |
| Canonical result | `results/EXP-0015/RUN-0001/result.yaml` | `RESULT-0022`, verdict `VALID_IN_RANGE`, best model the train-fitted single exponent. |
| Gate B replay | `docs/reviews/stellar-ml-result0022-gate-b-replay.md` | `PASS`; 68 numeric fields matched at tolerance `1e-9`, maximum absolute drift `0.0`, verdict unchanged. |
| Alternate-split control | `docs/reviews/stellar-ml-alternate-split-stability-audit.md` | `CONCLUSION_STABLE` across three additional value-blind system-level splits, with a modest fitted-vs-3.5 margin. |
| Complexity control | `docs/reviews/stellar-ml-piecewise-complexity-audit.md` | `PIECEWISE_NOT_JUSTIFIED`; a two-segment fit gains only `0.004188 dex`, below the predeclared `0.04 dex` penalty threshold. |

The chain supports reproducibility and bounded robustness. It does not provide
independent external-dataset replication.

## Gate Status And Commands

### Gate A

Gate A is `PASS`. The publication report records all 9 checks as true:
deterministic execution, populated verification, pinned input hashes, explicit
limitations, pinned engine/commit, schema validation, no protected-artifact
rewrite, no forbidden overclaim wording, and valid dataset provenance.

Canonical run command recorded by the result:

```bash
physics-lab run examples/stellar_ml_debcat_baseline_benchmark.yaml
```

Equivalent repository CLI form documented on the public campaign surface:

```bash
python3 -m physics_lab.cli run examples/stellar_ml_debcat_baseline_benchmark.yaml
```

Gate A check:

```bash
python3 scripts/apl_check_result_publication.py results/EXP-0015/RUN-0001/result.yaml
```

### Gate B

Gate B is `PASS`. The independent replay used:

```bash
python3 scripts/apl_validate_agent_published_result.py results/EXP-0015/RUN-0001/result.yaml --output-dir .pytest-basetemp/task0776-gateb-replay --validator-contributor-id romanhladun24-dot --validator-github-username romanhladun24-dot --validator-agent-tool Codex --validator-model GPT-5 --json
```

The replay compared 68 numeric fields with tolerance `1e-9`, found maximum
absolute drift `0.0`, preserved `VALID_IN_RANGE`, and upgraded the result from
`AGENT_PUBLISHED` to `AGENT_VALIDATED`. Gate B establishes deterministic
reproduction of the committed benchmark; it is not maintainer endorsement or
external scientific replication.

## Core Result Metrics

The frozen admitted lane contains 223 main-sequence-compatible components:
102 train, 56 validation, and 65 holdout. Physical binary systems stay within
one lane.

| Baseline | Fit parameters | Frozen holdout MAE (dex) | Interpretation |
| --- | ---: | ---: | --- |
| Train-fitted single exponent, `alpha=4.526004` | 1 | `0.119925` | Best simple baseline in the canonical result. |
| Fixed textbook mid-mass exponent, `alpha=4.0` | 0 | `0.137608` | Better than the single `alpha=3.5` baseline. |
| Fixed textbook single exponent, `alpha=3.5` | 0 | `0.184954` | Beats the null, but is inadequate as the sole baseline in scope. |
| Per-mass-band train-median null | descriptive control | `0.331817` | Worse than all three formula baselines. |

The `alpha=3.5` gap is `0.065029 dex` versus the fitted single exponent and
`0.047346 dex` versus the fixed `alpha=4.0` baseline. Both exceed the
predeclared `0.04 dex` split-noise reference. The null-minus-formula margin is
positive in 5/5 canonical seeded splits (`0.102269-0.180271 dex`), and the real
margin (`0.146863 dex`) exceeds every luminosity-shuffle control; the largest
shuffled margin is `-0.092278 dex`.

Stage diagnostics explain the main-sequence restriction rather than extending
the result: holdout MAE is `0.184954 dex` for the main-sequence lane,
`0.30805` for subgiants, `1.708908` for evolved stars, and `0.237776` for
unknown stage. Non-main-sequence rows are diagnostic only.

## Alternate-Split Stability

The follow-up audit used three predeclared value-blind 70/30 system-level
splits under seeds 101, 202, and 303. No new model family or live data was
introduced.

| Seed | `alpha=3.5` MAE | Fitted alpha | Fitted MAE | Null MAE | Fitted gain over 3.5 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 101 | `0.1684` | `4.584` | `0.1186` | `0.3022` | `0.0498` |
| 202 | `0.1393` | `4.636` | `0.0974` | `0.3128` | `0.0419` |
| 303 | `0.1446` | `4.545` | `0.0875` | `0.2966` | `0.0571` |

In all three splits, `alpha=3.5` beats the null and the fitted exponent beats
`alpha=3.5` by more than `0.04 dex`. The direction is stable, but the margin is
modest: seed 202 clears the reference by only `0.0019 dex`. The fitted exponent
stays near `4.5-4.6`; this is a bounded stability observation, not a promoted
universal exponent.

## Piecewise Complexity Audit

The complexity audit is distinct from the fixed `alpha=4.0` baseline in the
canonical result. It tested a two-segment train-fitted model with a
predeclared physical breakpoint at `M=1 M_sun`:

- single fitted exponent: `alpha=4.526`, one fitted parameter,
  holdout MAE `0.119925 dex`;
- two-segment fit: `alpha_low=4.83`, `alpha_high=4.43`, two fitted parameters,
  holdout MAE `0.115737 dex`;
- improvement: `0.004188 dex`.

The two-segment gain is far below the predeclared `0.04 dex` complexity
threshold. The audit verdict is therefore `PIECEWISE_NOT_JUSTIFIED`: retain
the single fitted exponent as the parsimonious descriptive baseline. This
negative control prevents the result from being reframed as evidence for a
piecewise stellar-evolution model.

## DEBCat Scope And Limitations

- Source: DEBCat detached eclipsing binaries, Southworth (2015), with direct
  dynamical component masses.
- License: normalized rows and holdout manifest are committed under CC BY 4.0
  after the explicit TASK-0763 permission grant.
- Snapshot boundary: the benchmark is tied to the checksum-pinned 2026-05-16
  source snapshot. It does not use live data.
- Storage boundary: raw `debs.dat` is not committed; the normalized committed
  rows and extraction/provenance records are the reproducible benchmark input.
- Population boundary: only admitted main-sequence-compatible components in
  `0.5-2.0 M_sun` support the result. Evolved, subgiant, unknown-stage, and
  out-of-range rows are diagnostic or excluded.
- Luminosity boundary: values mix catalogue-reported luminosities and
  Stefan-Boltzmann-derived luminosities from radius and effective temperature,
  with per-row provenance. Residuals inherit this heterogeneity.
- Dependence boundary: binary components are grouped by physical system to
  prevent train/holdout leakage, but the catalogue remains one curated source.
- Generalization boundary: there is no independent second stellar catalogue,
  broader mass range, metallicity-stratified replication, or external
  replication in this evidence chain.

These limitations allow a scoped benchmark statement. They block any broader
claim about a universal mass-luminosity law or stellar evolution.

## Maintainer Decision Options

### Option 1: Keep `AGENT_VALIDATED` Benchmark Memory

Leave `RESULT-0022` and public wording at the current trust tier.

- Result impact: none.
- Claim and knowledge impact: none.
- Benefit: preserves a reproducible benchmark without semantic endorsement.
- Cost: the public surface continues to identify the result as independently
  replayed but not maintainer-reviewed.

### Option 2: Add Maintainer-Reviewed Public Wording

Approve a tightly scoped public capsule using the wording below. Any review
tier mutation remains a separate maintainer-controlled action.

- Result impact: optional maintainer review-tier action, not performed here.
- Claim and knowledge impact: none.
- Required boundary: wording must retain the frozen dataset, mass range,
  baseline comparison, modest-margin, and no-universal-law qualifiers.

### Option 3: Request External Source Scouting

Keep the current result unchanged and commission a planning/source task for a
second independently curated stellar dataset with direct or independently
defensible masses and luminosities.

- Purpose: test transfer beyond the single DEBCat snapshot and population.
- Required preconditions: pin license, checksum, row schema, uncertainty and
  luminosity provenance, system-level leakage policy, mass/stage scope, and
  holdout policy before metrics.
- This is required before broader generalization, but not before publishing
  the scoped DEBCat wording.

### Option 4: Keep Waiting

Take no public or source-scout action until a naturally updated DEBCat release
or a clearly admissible external dataset appears.

- Benefit: no additional coordination cost.
- Cost: does not reduce the current single-source generalization blocker.
- It does not justify another split audit, Gate B replay, or model search on
  the unchanged snapshot.

## Recommendation

Recommend **Option 2** for the existing public campaign surface, while treating
**Option 3** as the next step only if the maintainer wants evidence that can
generalize beyond the frozen DEBCat slice.

The completed Gate A, zero-drift Gate B replay, alternate-split stability, and
negative piecewise-complexity result are sufficient for conservative
maintainer-reviewed wording about this benchmark. They are not sufficient for
a `CLAIM-*`, `KNOW-*`, universal exponent, or stellar-evolution statement.

## Recommended Public Wording

> On a frozen, CC BY 4.0 DEBCat slice of 223 main-sequence-compatible binary
> components spanning `0.5-2.0 M_sun`, the fixed `L proportional to M^3.5`
> baseline beats a per-mass-band median null but has higher holdout error
> (`0.184954 dex`) than a train-fitted single exponent near `4.53`
> (`0.119925 dex`). The direction is stable across the committed controls and
> three additional value-blind system-level splits, although the alternate-
> split margin is modest. A two-segment fit is not justified after the
> predeclared complexity penalty. This independently replayed result shows
> only that `alpha=3.5` is inadequate as the sole baseline on this frozen
> slice; it does not falsify the textbook relation universally or establish a
> universal mass-luminosity or stellar-evolution law.

## Output Routing

- Task verdict: `MAINTAINER_REVIEW_READY`.
- Canonical destination:
  `docs/reviews/stellar-ml-result0022-maintainer-review-packet.md`.
- Review destination: maintainer decision on public wording and optional
  future external-source scouting.
- Existing result tier: `AGENT_VALIDATED`; unchanged by this task.
- Gate A status: existing `PASS` (9/9).
- Gate B status: existing `PASS` (68 numeric fields, tolerance `1e-9`,
  maximum drift `0.0`, verdict unchanged).
- Claim impact: none; no claim created, edited, or promoted.
- Knowledge impact: none; no knowledge artifact created or edited.
- Result impact: none; no metrics, verdict, review tier, or result file changed.
- Dataset impact: none; no source rows, manifests, or provenance files changed.
- Publication blocker: none for the conservative scoped wording above.
  Independent external-source evidence is a blocker only for broader
  generalization beyond the frozen DEBCat slice.

## Final Verdict

`RESULT-0022` is ready for a maintainer wording decision. The defensible public
statement is that `alpha=3.5` is inadequate as the sole baseline on the frozen
DEBCat main-sequence-compatible slice. The evidence does not support universal
falsification, a promoted physical claim, or knowledge promotion.

## Maintainer Decision (2026-07-02)

Decision: **Option 2 + Option 3** — the scoped public capsule is approved (execution: `TASK-0922`) and an external stellar-dataset scout is commissioned (`TASK-0928`). No universal-law claim.
Recorded in [maintainer-decision-day-2026-07-02.md](./maintainer-decision-day-2026-07-02.md).
