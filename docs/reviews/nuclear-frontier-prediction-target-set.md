# Nuclear Frontier Prediction-Target Set (No-Peek)

**Task:** `TASK-0826`
**Status:** review-ready prediction-target definition
**Verdict:** `not_applicable` (target definition only; no scoring, no claim)

## Scope

This note records a no-peek prediction-target definition for the neutron-rich /
near-drip / r-process frontier, where current nuclear mass models diverge most
and committed data is sparse. The target set is defined by nuclide identity
(`Z`, `N`) only so a future maintainer-approved standing reveal pipeline
(`TASK-0825`) has a physically-meaningful, leakage-safe list of targets to
freeze model predictions over.

No measured mass values, model predictions, or metrics are produced. No sources
are fetched or pinned, no predictions are registered, and no claims are
promoted.

## Inputs

- `TASK-0826` (this task)
- `TASK-0825` (consuming standing reveal pipeline)
- [`docs/nuclear-prediction-reveal-protocol.md`](../nuclear-prediction-reveal-protocol.md)
- [`docs/blind-holdout-benchmark-protocol.md`](../blind-holdout-benchmark-protocol.md)
- [`data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`](../../data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml)
- [`data/nuclear_masses/post_ame2020_holdout.yaml`](../../data/nuclear_masses/post_ame2020_holdout.yaml)

## Manifest artifact

- Added: [`data/nuclear_masses/frontier_prediction_targets.yaml`](../../data/nuclear_masses/frontier_prediction_targets.yaml)
- Artifact type: value-free target-definition manifest (nuclide IDs + region
  rationale, no measured values, no metrics)
- Selected target count: 37 across four regions
- Schema posture: mirrors the existing value-free target-batch manifests
  ([`data/nuclear_masses/factory_target_batches.yaml`](../../data/nuclear_masses/factory_target_batches.yaml)
  and
  [`data/nuclear_masses/shell_axis_target_batch_proposal.yaml`](../../data/nuclear_masses/shell_axis_target_batch_proposal.yaml));
  it uses `schema_version` + `regions`/`targets`, not the value-bearing
  `dataset_id` + `entries` nuclear-mass dataset shape.

## Regions and rationale

| Region | Targets | Why models diverge here |
| --- | --- | --- |
| `n50_below_ni78` | V-73, Cr-74, Mn-75, Fe-76, Co-77, Fe-78, Co-79, Ni-80, Ni-82 | N=50 shell closure for very neutron-rich Z<28 isotones; smooth liquid-drop extrapolation, shell-quenching, and neutron-excess terms split between models; r-process relevant. |
| `n82_neutron_rich_cd_sn` | Ru-126, Rh-127, Pd-128, Ag-129, Rh-129, Pd-130, Ag-131, Cd-133 | N=82 closed shell below the Sn-Cd line; a classic r-process waiting-point neighborhood where shell-quenching and pairing assumptions diverge by several MeV. |
| `n126_rprocess_waiting_point` | Er-194, Yb-196, Hf-198, W-200, Os-202, Pt-204, Yb-198, Hf-200, W-202, Os-204 | N=126 closed shell for neutron-rich Z<82 nuclei; the third r-process waiting-point region and the most extrapolation-dominated, with almost no measured masses below the stable line. |
| `light_neutron_rich_drip_o_ne_mg` | O-28, O-30, F-31, Ne-32, Ne-34, Na-35, Na-37, Mg-38, Mg-40, Mg-42 | Light neutron-rich O-to-Mg chains crossing N=20 and the "island of inversion", where N=20 magicity and single-particle ordering are model-dependent and even predicted drip-line positions diverge. |

Region rationales describe where mass models diverge. They are not
astrophysical-significance or discovery statements.

## Leakage boundary

**Rule.** A candidate target is admissible only if its (`Z`, `N`) identity does
**not** already have a committed measured value in-repo. Targets must not
overlap the NMD-0003 training rows or the post-AME2020 row-level holdout rows.

**Screened files.**

- [`data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`](../../data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml) — 2309 committed measured (`Z`, `N`) identities
- [`data/nuclear_masses/post_ame2020_holdout.yaml`](../../data/nuclear_masses/post_ame2020_holdout.yaml) — 296 committed row-level holdout (`Z`, `N`) identities

**Method.** Each candidate (`Z`, `N`) was checked against the union of the two
files' identities (2604 combined). Candidates present in either set were
excluded as leakage. All 37 selected targets passed the screen with **zero**
committed-value hits at design time.

**Excluded neighbors (boundary evidence).** Representative neutron-rich
neighbors in the same shell regions that were excluded because they already
carry a committed measured value:

- In NMD-0003 training: Ni-78, Cd-130, Sn-132, Sn-134, Hg-206, O-24, Ne-30,
  Mg-36.
- In post-AME2020 holdout: In-131.

Ni-78 (`Z=28`, `N=50`) is itself committed in NMD-0003 and is therefore
excluded as a target; it is retained in the manifest only as the structural
anchor that bounds the N=50 region. The N=50 targets are the neutron-rich
isotones around and below that doubly-magic crossing.

**Caveats.**

- `no_exact_row_hit_found` means there is no committed measured value for that
  (`Z`, `N`) in the two screened files at design time. It is not a positive
  claim that the nuclide is unmeasured in the wider literature.
- Whether a target is genuinely unmeasured at registration time is a
  source-state question that the future reveal task must re-verify under the
  reveal protocol; it is not asserted here.
- Identity screening is by (`Z`, `N`); isomeric states are out of scope for this
  identity-only manifest.

## Plug-in to the reveal pipeline without weakening no-peek gates

The [nuclear prediction reveal protocol](../nuclear-prediction-reveal-protocol.md)
forbids fetching live measurements, pinning sources, scoring, and claim
promotion in target-definition work, and the
[blind holdout benchmark protocol](../blind-holdout-benchmark-protocol.md) requires
naming a holdout target without exposing its answer. This manifest stays inside
both boundaries: it names targets by identity only, with no values. A future
reveal task under `TASK-0825` must still supply its own source manifest,
checksum record, frozen registry snapshot, and no-peek audit before any
comparison, exactly as those protocols require. Defining the target set ahead of
time strengthens the before/after boundary rather than weakening it, because the
target list is frozen and auditable before any source is revealed.

## Limitations

- Target identifiers are design candidates by (`Z`, `N`) identity, not
  source-state claims.
- No measured mass values, model predictions, or metrics are stored.
- The `no_exact_row_hit_found` screen covers two committed in-repo files only and
  is current as of design time; the reveal task must re-verify source state.
- No live measurements were fetched, no sources pinned, no predictions
  registered, and no claims promoted.

## Output-routing summary

- **Task verdict:** `not_applicable` (target definition only; no benchmark, no
  scoring).
- **Canonical destination:** prediction-target definition for prediction-reveal
  readiness, consumed by `TASK-0825`. No `PRED-*`, no `RESULT-*`, no `CLAIM-*`,
  no `KNOW-*` artifact is created.
- **Measured values:** none committed; the manifest is value-free.
- **Leakage boundary:** stated and enforced — targets are screened against
  NMD-0003 training and the post-AME2020 holdout; 37 selected targets, 0
  committed-value hits.
- **Review tier:** `none`.
- **Gate status:** Gate A not attempted; Gate B not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations / blockers:** source-state verification for each target is
  deferred to the future maintainer-reviewed reveal task; this task neither
  fetches sources nor registers predictions.
