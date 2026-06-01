# Exoplanet control-aware go/no-go synthesis

- Task: `TASK-0515`
- Campaign: `exoplanet_mass_radius`
- Decision: `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`
- Task verdict: `INCONCLUSIVE`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`

## Scope

This synthesis decides whether another compact-radius residual follow-up is
warranted on the current pinned PSCompPars snapshot. It compares existing
reviewed sandbox evidence only. It does not fetch live data, run metrics, fit a
correction model, create a factory sprint, or create `RESULT-*`, `PRED-*`,
`CLAIM-*`, or `KNOW-*` artifacts.

## Evidence comparison

| Evidence | Observation | Decision impact |
| --- | --- | --- |
| `TASK-0483` null-baseline family audit | Deterministic nearest-radius null baselines match or beat the frozen CK17-style baseline in the highlighted compact-radius, sub-Neptune, Jovian-radius, and hot-Jupiter true-mass slices. Minimum-mass slices remain underpowered. | The apparent residual stress is control-sensitive. Another CK17-style compact-radius residual pilot on the same snapshot is not warranted. |
| `TASK-0481` host-context preflight | Compact-radius host fields often have usable raw coverage, but no host-context axis has enough interpretable bins to be benchmark-usable under the current coarse-bin floor. | A compact-radius host-context audit would be conditional and underpowered before it starts. It should not be opened as the next residual lane. |
| `TASK-0480` mass-quartile scout | The 92-row compact slice is underpowered at quartile resolution. The upper-mass-half direction is a coarse diagnostic only. | Do not turn the mass-half hint into a follow-up hypothesis on the same snapshot. |
| `TASK-0404` promotion scorecard | The campaign is `BENCHMARK_SUMMARY_ONLY`, with claim-candidate eligibility blocked. | Preserve scientist-readable benchmark wording without strengthening interpretation. |

The earlier compact-radius evidence card and cross-tool replay remain useful
reproducibility memory. They should now be read together with the stronger
null-baseline audit and host-context preflight.

## Decision

`NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`

No additional compact-radius residual or host-context pilot should run on the
current pinned snapshot. The current value of the campaign is the negative
control result: the highlighted CK17-style residual slices are
control-sensitive, and the compact-radius host-context partitions are
underpowered at the declared interpretation floor.

This is not a universal statement about exoplanet mass-radius relations. It is
a bounded go/no-go decision for the current snapshot, baseline family, and
declared compact-radius follow-up surface.

## Lanes not to repeat

Future agents should not repeat these lanes on the current snapshot:

- another positive-framed CK17-style compact-radius residual pilot;
- compact-radius host-context coarse-bin audits using the existing coverage
  floor;
- compact-radius mass-quartile localization with the same 92 eligible rows;
- positive interpretation of the coarse upper-mass-half diagnostic;
- an Exoplanet Research Factory candidate sprint that treats nearest-radius
  nulls as decorative controls;
- any pooled headline metric that mixes true-mass and minimum-mass rows.

## Factory adapter posture

The Exoplanet Research Factory adapter remains `CONTRACT_ONLY`. It should not
advance to a smoke-run task merely because the shared factory protocol and
schema land. A future maintainer-approved task may revisit a dry-run only after
a materially changed input surface, such as a reviewed later pinned snapshot or
an explicitly revised coverage gate. Any future adapter must preserve
null-baseline competition, host-context coverage gates, true-mass/minimum-mass
separation, and stop-on-control-match routing.

## Allowed future work

The no-go decision does not close the campaign. Appropriate later work is:

- replay and external-review use of the existing replication capsule;
- source-maintenance or a maintainer-approved later pinned snapshot under the
  second-snapshot no-live-fetch protocol;
- a fresh go/no-go review only if row coverage, snapshot scope, or the declared
  baseline question materially changes.

No follow-up task proposal is created by this synthesis.

## Public wording boundary

Safe wording:

> On the current pinned PSCompPars snapshot, simple nearest-radius null
> baselines match or beat the frozen CK17-style baseline in the highlighted
> true-mass slices. Compact-radius host-context partitions are underpowered at
> the declared coarse-bin floor, so APL preserves this as benchmark
> negative/control memory rather than opening another residual pilot.

Do not infer composition, habitability, atmosphere, biosignatures, target
priority, anomalous physics, discovery, or a universal mass-radius law.

## Output routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination:
  `docs/reviews/exoplanet-control-aware-go-no-go-synthesis.md`.
- Review tier: `none`.
- Gate A: not attempted; no canonical result or prediction artifact.
- Gate B: not attempted; no canonical artifact replay upgrade.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: current snapshot remains control-sensitive and
  host-context partitions remain underpowered.
