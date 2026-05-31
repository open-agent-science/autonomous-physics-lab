# Exoplanet Research Factory Adapter Contract

## Purpose

This contract defines how a future Exoplanet Mass-Radius adapter may plug into
the shared Research Factory layer after the Nuclear-first factory protocol
lands. It is a planning and protocol artifact only. It does not run exoplanet
metrics, generate candidate corrections, fit a new mass-radius relation, write a
canonical result, create a prediction, promote a claim, or update knowledge.

The adapter is intentionally blocked from a full sprint until the shared
factory protocol/schema work and the Exoplanet campaign gates are reviewed. The
current exoplanet evidence is control-sensitive:

- `TASK-0483` found that deterministic nearest-radius null baselines match or
  beat the frozen CK17-style baseline in the highlighted true-mass slices.
- `TASK-0481` found no compact-radius host-context axis that is
  benchmark-usable under the current coarse-bin floor.

Any future adapter must therefore treat failed, null-matched, and underpowered
families as useful negative memory rather than as evidence for planet physics.

## Adapter Identity

- Campaign profile: `campaign_profiles/exoplanet-mass-radius.yaml`
- Adapter id: `exoplanet_mass_radius_residual_factory`
- Adapter contract version: `0.1`
- Current status: `CONTRACT_ONLY`
- First implementation gate: shared Research Factory protocol and
  `factory_summary` artifact schema are accepted.
- Campaign gate: a maintainer accepts whether the post-`TASK-0481` state allows
  a narrow conditional follow-up or only negative/control memory.

## Required Inputs

The adapter must receive these inputs before any candidate is generated:

| input | required value |
| --- | --- |
| dataset | `data/exoplanets/exo-0001-pscomppars-snapshot.yaml` or a later maintainer-approved pinned snapshot |
| source policy | no live fetch; source version, retrieval date, and checksum remain explicit |
| loader | committed exoplanet loader and inclusion/exclusion filters |
| axis labels | `true_mass_with_transit_radius` and `minimum_mass_with_transit_radius` stay separate |
| baseline | frozen CK17-style baseline or explicitly declared null baseline |
| row fields | `mass_class`, `radius_class`, mass/radius values, uncertainties, detection method, host fields, equilibrium-temperature proxies, provenance |
| evidence gates | `TASK-0483` null-baseline family audit and `TASK-0481` host-context preflight |
| candidate cap | declared before generation; no post-hoc expansion after seeing metrics |
| output routing | shared Research Factory route verdict plus Exoplanet-specific blockers |

Rows with true mass and rows with minimum mass or `M sin i` must never be pooled
into one headline metric. Minimum-mass slices that remain underpowered should
route to `DATA_QUALITY_BLOCKED` or `INCONCLUSIVE`, not to a positive shortlist.

## Allowed Factory Families

Allowed families are diagnostic candidate families, not claims about planet
composition or habitability.

| family | allowed scope | required guard |
| --- | --- | --- |
| `radius_regime` | compact, sub-Neptune, Jovian-radius, hot-Jupiter, and declared transition slices | compare against nearest-radius and shuffled/null controls |
| `mass_provenance` | true-mass and minimum-mass axes, reported separately | no pooling across provenance classes |
| `detection_method` | transit, radial-velocity-adjacent labels, timing labels when count-supported | sample-size and mass/radius matched controls |
| `host_context` | host Teff, stellar radius, metallicity fields | coverage gate first; compact-radius host context is conditional/underpowered after `TASK-0481` |
| `irradiation_proxy` | equilibrium temperature and irradiation flux fields when present | missingness report and no habitability wording |
| `measurement_quality` | mass/radius uncertainty bands and missing-uncertainty flags | uncertainty-matched controls and explicit missingness route |
| `null_baseline_family` | per-class medians, nearest-radius/null neighbors, shuffled labels | null must be treated as a competitor, not a decorative control |

Forbidden families include biosignature, habitability, target-priority,
composition labels, atmosphere labels, discovery labels, and a new universal
mass-radius-law search.

## Required Controls

Every executed candidate must record the following controls or route to
`DATA_QUALITY_BLOCKED`:

- null-baseline comparison against at least one deterministic null family;
- matched controls appropriate to the candidate family, including nearest
  radius or nearest log-mass when applicable;
- shuffled or label-destruction negative control for slice-label candidates;
- true-mass/minimum-mass separation in all reported metrics;
- host-context coverage gate before any host family is executed;
- minimum row-count floor declared before metrics;
- complexity penalty for every added split, feature, or free parameter;
- no baseline refit unless a future task explicitly authorizes it;
- no live external fetch.

The adapter must preserve adverse control results. A candidate beaten or matched
by a null family should normally route to `NEGATIVE_RESULT` or
`REJECTED_BY_CONTROL`.

## Route Verdict Mapping

| route verdict | Exoplanet meaning |
| --- | --- |
| `NEGATIVE_RESULT` | candidate is matched/beaten by nulls or matched controls; preserve as negative memory |
| `INCONCLUSIVE` | effect is visible but underpowered, coverage-limited, or control-sensitive |
| `SHORTLIST_CANDIDATE` | candidate survives declared controls in a sandbox run, but remains non-claim evidence |
| `READY_FOR_REPLAY` | shortlisted candidate has a deterministic replay target and no unresolved source/provenance blocker |
| `READY_FOR_PRED_FREEZE` | blocked by default; requires a future no-peek prediction-freeze task and maintainer approval |
| `REJECTED_BY_CONTROL` | null, shuffled, matched, or uncertainty control removes the apparent advantage |
| `LOCAL_ONLY` | useful for local diagnosis but not suitable for reviewable campaign memory |
| `DATA_QUALITY_BLOCKED` | missingness, row count, source provenance, or mass-provenance limits block interpretation |

No route verdict may create `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*`
artifacts by itself.

## Campaign-Specific Factory Summary Fields

A future `factory_summary` artifact should include these Exoplanet-specific
fields in addition to the shared fields:

- `snapshot_path`
- `snapshot_source_id`
- `snapshot_checksum_policy`
- `axis`
- `mass_class_policy`
- `radius_class_policy`
- `baseline_id`
- `null_baseline_ids`
- `candidate_family`
- `candidate_slice_definition`
- `host_context_fields_used`
- `coverage_gate_status`
- `minimum_row_count`
- `control_outcomes`
- `complexity_penalty`
- `forbidden_claim_check`
- `route_verdict`

## Stop Rules

A future Exoplanet factory sprint must stop before execution when any of these
conditions is true:

- the shared Research Factory protocol or factory-summary schema is missing;
- the task does not name a pinned dataset and source policy;
- the task attempts a live NASA Exoplanet Archive fetch;
- the candidate family uses habitability, biosignature, atmosphere,
  target-priority, discovery, or composition framing;
- the candidate pools true-mass and minimum-mass rows in one headline metric;
- host-context coverage is below the declared gate;
- compact-radius host context is treated as benchmark-usable without a new
  task that explicitly revises the `TASK-0481` blocker;
- a null baseline matches or beats the candidate and the route is still marked
  positive;
- a prediction, claim, result, or knowledge artifact would be created without a
  maintainer-approved promotion task.

## Recommended Follow-Up Shape

Do not create the next sprint as `READY` from this contract. A later maintainer
may choose one of these shapes:

1. `TASK-PROPOSAL`: Implement Exoplanet Research Factory adapter smoke run.
   Scope: load the pinned snapshot, enumerate allowed families, reject blocked
   families before metrics, and emit a dry-run factory summary with no
   candidate correction metrics.
2. `TASK-PROPOSAL`: Run Exoplanet control-aware go/no-go synthesis.
   Scope: combine `TASK-0483` and `TASK-0481` to decide whether any residual
   family remains worth a factory sprint.
3. `TASK-PROPOSAL`: Define conditional host-context missingness audit.
   Scope: only if the maintainer wants a narrow host-context analysis despite
   the compact-radius benchmark-axis blocker.

Until one of these is accepted, the Exoplanet Research Factory adapter remains
contract-only and non-executable.
