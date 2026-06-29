# Exoplanet null-baseline negative/control Gate A blocker

- Task: `TASK-0888`
- Domain: `exoplanet_mass_radius`
- Publication class checked: scoped negative/control `RESULT`
- Outcome: `BLOCKED_BY_GATE_A` (no `RESULT-*` artifact created)

This note records a strict package-or-stop decision. `TASK-0888` may package the
existing Exoplanet null-baseline negative/control memory as a canonical
`AGENT_PUBLISHED` negative `RESULT-*` only if **every** Gate A element can be made
deterministic and conservative from committed `EXO-0001`/`EXO-0002` evidence and
the existing null-baseline runner. It must otherwise stop and preserve this
blocker without creating any `RESULT-*` artifact.

The assessment below was performed with no live NASA Exoplanet Archive fetch, no
`EXO-0003` value-bearing rows, no candidate formula, no CK-style baseline refit,
no residual-scoring restart, and no lowering of the `EXO-0003` trigger gate. The
Exoplanet residual lane stays monitor-only.

## Source material

- [Exoplanet negative/control result-publication preflight](exoplanet-negative-control-result-publication-preflight.md)
- [Exoplanet null-baseline negative-control memory replay](exoplanet-null-baseline-negative-memory-replay.md)
- [Exoplanet null-baseline family audit](exoplanet-null-baseline-family-audit.md)
- [Result promotion protocol](../result-promotion-protocol.md)
- [AGENT_PUBLISHED result template](../../results/RESULT-TEMPLATE.agent-published.yaml)

## Finding is replayable; packaging is not

The underlying negative/control finding is deterministic. Re-running
`scripts/run_exoplanet_null_baseline_family_audit.py` against the committed
`data/exoplanets/exo-0001-pscomppars-snapshot.yaml` reproduces the documented
memory exactly:

| axis | slice | rows | CK17 RMSE | best null | classification |
| --- | --- | ---: | ---: | --- | --- |
| `true_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 92 | 0.263350 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `true_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 340 | 0.204175 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `true_mass_with_transit_radius` | `jovian_radius_8_16Re` | 567 | 0.083354 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `true_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 445 | 0.069788 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |

Verdict `INCONCLUSIVE`, audit class `BENCHMARK_CONTROL_PANEL`, matching
`docs/reviews/exoplanet-null-baseline-family-audit.md` and the sub-`1e-12`
replay drift already captured in
`docs/reviews/exoplanet-null-baseline-negative-memory-replay.md`.

Replayability of the *finding* is necessary but not sufficient for Gate A.
Packaging a canonical `RESULT-*` also requires a canonical **experiment identity**
and **hypothesis identity** that the result references, because
`physics_lab/registry/repository.py` rejects any `results/.../result.yaml` whose
`experiment_id` is not present in the experiments registry and whose
`hypothesis_id` is not present in the hypothesis registry. Those identities do
not exist for this lane and cannot be created here without reopening the
residual lane that this task forbids.

## Gate A readiness

| Gate A check | status | finding |
| --- | --- | --- |
| deterministic result-producing run exists | `PARTIAL` | The runner reproduces the negative/control metrics deterministically, but it writes a sandbox audit (`metrics.json` / `report.md` / `agent_run.yaml`), not a schema-valid `results/.../result.yaml`. No result-producing command is available without adding new packaging code, which exceeds this task's scope. |
| canonical experiment identity exists for the result path | `BLOCKED` | No canonical Exoplanet experiment file exists. `experiments/` contains no exoplanet entry, and `EXP-0014` is now `materials-md0002-formation-energy-benchmark`. Only non-canonical `experiment_proposals/exoplanet-mass/EXP-PROPOSAL-00{15..19}.yaml` exist. `repository.py` raises `references missing experiment_id` for any result without a registered experiment. |
| canonical hypothesis identity exists for the result path | `BLOCKED` | No canonical Exoplanet hypothesis file exists (`hypotheses/` has no exoplanet entry; only `hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-00{49..53}.yaml`). `repository.py` raises `references missing hypothesis_id` for any result without a registered hypothesis. |
| verification block can be populated from committed evidence | `PARTIAL` | A control-panel verification block could be described from the replay, but it cannot be bound to a schema-valid result without the missing experiment/hypothesis identities and a result-producing command. |
| input file hashes can be recorded without new execution | `PARTIAL` | The committed snapshot has source provenance and a stable SHA-256, so a hash row is feasible, but `input_file_hashes` only becomes meaningful inside a result artifact, which is blocked. |
| limitations are explicit | `PASS` | The source reviews already constrain the finding to control-sensitive negative memory and forbid composition, habitability, atmosphere, target-priority, discovery, prediction, and universal mass-radius wording. |
| engine version and git commit pinnable | `PASS` | Engine version `0.1.0` and the current `git_commit` are available, but they only pin a result artifact, which is blocked. |
| schema validation can run on a RESULT artifact | `NOT_APPLICABLE` | No `RESULT-*` is created because the experiment/hypothesis identities are missing. |
| protected artifacts remain untouched | `PASS` | This note does not modify any `results/` artifact or `results/golden-results.yaml`. |
| forbidden overclaim wording absent | `PASS` | This note preserves the negative/control framing and promotes no claim, prediction, or knowledge. |

## Exact missing Gate A element

The decisive blocker is the **missing canonical experiment identity (and its
paired hypothesis identity)** for the Exoplanet mass-radius null-baseline lane.
A schema-valid, `validate-repo --strict --fail-on-warnings`-passing negative
`RESULT-*` must set `experiment_id` and `hypothesis_id` to entries that exist in
`experiments/` and `hypotheses/`. The lane has only proposal-stage artifacts
(`EXP-PROPOSAL-*`, `HYP-PROPOSAL-*`), never promoted to canonical files.

Creating those canonical identities to satisfy Gate A would promote the
Exoplanet residual lane from monitor-only into a registered experiment +
hypothesis surface — i.e. it would reopen residual scoring — which
`TASK-0888` explicitly forbids. There is therefore no conservative, in-scope way
to complete Gate A in this task. A separate maintainer-approved decision to
establish a canonical Exoplanet experiment/hypothesis identity would be required
first, and that decision is out of scope here.

## Decision

Gate A is blocked. Per the task's package-or-stop requirement, this task creates
this blocker note only and leaves `results/`, `experiments/`, `hypotheses/`, and
`results/golden-results.yaml` untouched.

The strongest current public-safe statement remains unchanged:

> On the committed `EXO-0001` PSCompPars snapshot, nearest-radius null baselines
> match or beat the frozen CK17-style baseline in the highlighted true-mass
> slices. The apparent residual structure is control-sensitive, so APL keeps the
> Exoplanet mass-radius residual lane monitor-only and does not reopen a positive
> residual-scoring lane on this snapshot. The nearest-radius neighbor is a
> diagnostic control that uses observed radius; it is not a deployable predictor.

This memory stays monitor-only unless a future source-version trigger materially
changes the snapshot rows and control surface, at which point a fresh
maintainer-approved task may revisit packaging.

## Output Routing

- Task verdict: `BLOCKED_BY_GATE_A` (treated as `not_applicable` for canonical promotion).
- Canonical destination: `docs/reviews/exoplanet-negative-control-gate-a-blocker.md`.
- Review tier: `none`.
- Gate A: blocked (missing canonical experiment + hypothesis identity for the Exoplanet mass-radius null-baseline lane).
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result impact: no `RESULT-*` artifact created; no protected artifact modified.
- Exoplanet status: stays monitor-only.
- Limitations / blockers: a canonical Exoplanet experiment/hypothesis identity does not exist and cannot be created in this task without reopening residual scoring; packaging is deferred to a future maintainer-approved task.
