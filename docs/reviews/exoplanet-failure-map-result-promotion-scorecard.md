# Exoplanet failure-map result-promotion scorecard

**Task:** `TASK-0404`
**Campaign:** `exoplanet-mass-radius`
**Scorecard reference:** `docs/result-promotion-scorecard.md`
**Final verdict:** `BENCHMARK_SUMMARY_ONLY`
**Claim promotion allowed:** `no`

## Boundary

This scorecard applies the result-promotion review process from
`docs/result-promotion-scorecard.md` to the current exoplanet failure-map
artifact set on the committed PSCompPars snapshot.

It does **not** create, modify, or promote any CLAIM-*, KNOW-*, RESULT-*, or
PRED-* artifact. It does **not** authorize habitability, composition,
target-priority, biosignature, atmospheric, inflation-physics, or
new-mass-radius-law wording. It does **not** initiate a Gate A publication,
a Gate B replay, or a claim-status transition.

The output is a decision artifact telling the maintainer what the existing
exoplanet evidence can and cannot say in scientist-facing or public-facing
communications.

## Evidence base

Seven sandbox/audit artifacts and the seven AGENT-RUN metrics files under
review:

| Artifact | Task | Agent run | Verdict | Role |
| --- | --- | --- | --- | --- |
| `exoplanet-mass-radius-residual-failure-map.md` | TASK-0362 | AGENT-RUN-0032 | INCONCLUSIVE | failure map packaging on first CK17 benchmark |
| `exoplanet-true-mass-residual-slice-audit.md` | TASK-0369 | AGENT-RUN-0035 | INCONCLUSIVE | true-mass slice diagnostic |
| `exoplanet-regime-residual-scout.md` | TASK-0370 | AGENT-RUN-0034 | INCONCLUSIVE | bounded regime scout |
| `exoplanet-compact-subneptune-residual-hypothesis-pilot.md` | TASK-0390 | AGENT-RUN-0036 | SANDBOX_PASS | compact/sub-Neptune pilot |
| `exoplanet-neptunian-residual-matched-control-audit.md` | TASK-0391 | AGENT-RUN-0037 | INCONCLUSIVE | neptunian matched-control audit |
| `exoplanet-host-uncertainty-selection-effects.md` | TASK-0392 | AGENT-RUN-0038 | INCONCLUSIVE | host + uncertainty selection-effects |
| `exoplanet-compact-subneptune-matched-control-audit.md` | TASK-0427 | AGENT-RUN-0042 | SANDBOX_PASS | compact/sub-Neptune matched-control audit |

Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml` (PSCompPars,
SHA-256 raw checksum committed, retrieved 2026-05-23T17:15:49Z).

## Per-axis scores

Scoring vocabulary from
`physics_lab/schemas/result_candidate_review.schema.json`:
`PASS`, `PARTIAL`, `FAIL`, `NOT_APPLICABLE`.

| Axis | Score | Justification |
| --- | --- | --- |
| `baseline_strength` | `PASS` | Frozen Chen-Kipping 2017 piecewise median baseline pinned with named primary source; per-class median null floor explicitly compared and reported. CK17 beats null on the true-mass-with-transit-radius axis by +0.084 log10 RMSE; the minimum-mass axis is recorded as blocked (only 2 post-filter rows) rather than glossed over. |
| `source_provenance` | `PASS` | PSCompPars snapshot is pinned with `source_family_id: EXO-SRC-CLASS-001`, retrieval timestamp, snapshot kind, and raw CSV SHA-256 checksum. Source policy in the snapshot YAML disallows live external fetch. |
| `artifact_checksums` | `PARTIAL` | Raw CSV checksum is present (`raw_checksum_sha256`); normalized checksum field is explicitly `null` in the snapshot YAML. All AGENT-RUN-* metrics files are committed and reproducible from runner scripts at pinned git commits, but the normalized-checksum gap should be closed by a future snapshot maintenance task before any external-replication claim. |
| `holdout_or_reveal_quality` | `PARTIAL` | Per-slice audits and matched controls exist, but no formal predict-then-reveal protocol covers the exoplanet residual surface yet. The minimum-mass axis is structurally underpowered (2 post-filter rows). TASK-0393 (define exoplanet second-snapshot no-live-fetch protocol) is the natural next step for an external-comparable reveal contract. |
| `uncertainty_handling` | `PASS` | Mass and radius relative-uncertainty thresholds documented (0.30 and 0.15 respectively); uncertainty bands stratified per slice in TASK-0392; TASK-0427 adds an uncertainty-equalized-subset negative control and a matched uncertainty-band cohort. Across all 7 reviews, mass-class and radius-class semantics are kept separate and uncertainty fields propagated rather than collapsed. |
| `negative_controls` | `PASS` | TASK-0391 carries 4 controls (per-class median, nearest-radius, host-temperature, uncertainty-band); TASK-0392 carries deterministic sample-size matched controls per slice; TASK-0427 carries 9 controls per slice (5 matched cohorts, 1 residual shift, 3 deterministic negative controls). CSN-001 from TASK-0427 is the strongest current matched-control survivor; all other interpreted slices come back as control-sensitive or selection-effect-persists-vs-control rather than promoted. |
| `leakage_risk` | `PASS` | Baseline is frozen at named published source; no in-task refit on the full snapshot in any audit; loader filter chain (TASK-0345/0346/0354) is reviewed; deterministic commands recorded; per-runner seeds recorded in `thresholds.shuffle_seed` and `thresholds.random_outside_seed` for TASK-0427. No agent-run output edits a canonical input. |
| `reproducibility` | `PASS` | TASK-0427 reproduces TASK-0390's pilot baselines (eligible + CSN-001/002/003) bit-for-bit at `max_abs_delta = 5.6e-17` (well under the runner's declared `1.0e-09` tolerance); all metrics files are regenerable from runners at pinned commits; tests cover synthetic-fixture round-trip plus committed pilot-baseline reproduction. |
| `external_comparability` | `PARTIAL` | CK17 baseline is widely cited; PSCompPars is the standard NASA Exoplanet Archive composite; but no external researcher or external Gate B has replicated the audits; cross-tool Gate B (Codex replays Claude or vice versa) on the exoplanet runner family is recommended before any external-comparability upgrade. |
| `public_wording_risk` | `PASS` | All seven reviews use "benchmark", "failure map", "residual stress", "control-sensitive", "selection-effect-persists-vs-control", "sandbox-only", or "INCONCLUSIVE" language. None of them use discovery, habitability, biosignature, target-priority, composition, atmospheric-inference, or new-mass-radius-law framings. Each review carries an explicit forbidden-claims list. |

## Eligibility

| Path | Decision |
| --- | --- |
| `sandbox_followup` | `ALLOW` — bounded follow-ups are appropriate, particularly a deeper compact-slice (R<1.5 R_earth) pilot and a cross-tool Gate B replay of TASK-0427. |
| `public_summary` | `ALLOW` — the artifact set is suitable for a scientist-facing benchmark-and-failure-map summary under strict wording. |
| `claim_candidate` | `BLOCK` — no audited slice clears all the criteria for claim-candidate framing: even CSN-001 (the strongest matched-control survivor) is one slice in one campaign with same-tool runners, no Gate B cross-tool replay, no external replication, and no formal future-reveal protocol. |

## Final verdict

`BENCHMARK_SUMMARY_ONLY`

The exoplanet failure-map artifact set is suitable for a reproducible
benchmark-and-failure-map public summary. It is **not** a claim candidate.
Claim status remains under maintainer-only Gate C per
`docs/result-promotion-protocol.md`.

## TASK-0427 status: prerequisite, not blocker

The TASK-0427 compact/sub-Neptune matched-control audit (`AGENT-RUN-0042`,
merged in PR #609) is a **strengthening prerequisite** for any
compact/sub-Neptune-specific scientist-facing wording. Without TASK-0427's
matched-control survival evidence, the pilot's "compact slice shows elevated
residual stress" finding from TASK-0390 could be misread as a planet-physics
conclusion rather than as a benchmark-diagnostic surface.

TASK-0427 is **not** a blocker for the scorecard: it landed before this
scorecard was written. Its survival of all 9 controls is the reason
`negative_controls` scores `PASS` here.

## Allowed wording

Scientists and public-facing alpha docs may use this set of statements,
referencing the artifacts in this scorecard:

- "APL maintains a frozen Chen-Kipping piecewise median baseline against a
  pinned NASA Exoplanet Archive PSCompPars snapshot and reports per-slice
  residual structure with explicit selection-effect and matched-control
  diagnostics."
- "On the true-mass / transit-radius axis the frozen baseline beats a
  per-class median null floor; on the minimum-mass / transit-radius axis the
  surface is structurally underpowered and is reported as inconclusive."
- "Across seven sandbox audits the compact-radius slice (R < 1.5 R_earth) is
  the only slice that survives all matched and deterministic negative
  controls within the campaign's 0.022 log10 RMSE margin. This is a
  benchmark-diagnostic surface, not a planet-physics conclusion."
- "Sub-Neptune (1.5 ≤ R/R_earth < 4) residual stress is largely explained by
  radius-position matching; combined (R < 4 R_earth) residual stress is
  largely explained by mass-class bias."
- "All audited reductions are deterministic and reproduce bit-for-bit on
  replay at the pinned git commits."

## Forbidden wording

The following framings are out of scope under this scorecard verdict and
must not appear in any scientist-facing or public-facing summary that
references this artifact set:

- "APL identified a new mass-radius law for exoplanets." (any
  discovery-style framing is out of scope under this verdict)
- "APL predicts which exoplanets are habitable, rocky, gaseous, or
  Earth-like."
- "APL identifies high-priority planet candidates for follow-up
  observation."
- "APL falsified Chen-Kipping for sub-Neptunes." — the audits report
  per-slice control-sensitivity, not a universal falsification.
- "APL's compact-slice survival indicates anomalous physics in
  super-Earth-sized planets." — the survival is a benchmark-diagnostic
  signal pending Gate B cross-tool replay and external replication.
- "APL infers atmospheric composition, biosignature, or inflation physics
  from any of these audits."

## Limitations preserved

- Normalized-snapshot checksum is `null`; should be filled before any
  external-replication framing.
- Minimum-mass-with-transit-radius axis has only 2 post-filter rows; the
  axis is structurally underpowered and is documented as blocked.
- All audits are same-tool (Claude Code or Codex); no cross-tool Gate B
  replay of any exoplanet runner has been recorded.
- No formal predict-then-reveal protocol for the exoplanet residual surface
  exists; TASK-0393 is the natural next planning step.
- Three of seven artifacts (the pilot + the two matched-control audits)
  carry per-slice SANDBOX_PASS verdicts; the remaining four are
  INCONCLUSIVE. The scorecard verdict aggregates these without overwriting
  any per-artifact verdict.
- The result_candidate_review.schema.json artifact emitted alongside this
  document (`docs/reviews/exoplanet-failure-map-result-promotion-scorecard.review.yaml`)
  is the machine-readable form of these same scores and the final verdict.

## Recommended next steps (not authorized by this PR)

1. **Open a cross-tool Gate B replay task** on `scripts/run_exoplanet_compact_subneptune_matched_control_audit.py` (Codex replays a Claude-Code-authored runner or vice versa). Same-tool reproducibility is already strong; cross-tool replay strengthens external-comparability from `PARTIAL` toward `PASS`.
2. **Open a deeper compact-slice (R<1.5 R_earth) follow-up pilot** under the exoplanet campaign profile (mass-quartile, host-metallicity, irradiation-flux subsetting). Sandbox-only by default.
3. **Schedule TASK-0393** (define exoplanet second-snapshot no-live-fetch protocol) so a formal future-reveal contract can lift `holdout_or_reveal_quality` from `PARTIAL` toward `PASS`.
4. **Close the normalized-snapshot checksum gap** in `data/exoplanets/exo-0001-pscomppars-snapshot.yaml` before any external-replication public claim.
5. **Do not** promote any CLAIM-* status for the exoplanet campaign on the strength of this artifact set; the final verdict here explicitly blocks claim-candidate eligibility.

## Cross-references

- `docs/result-promotion-scorecard.md` — review-gate authority.
- `docs/result-promotion-protocol.md` — multi-tier review-tier protocol.
- `physics_lab/schemas/result_candidate_review.schema.json` — machine-readable
  schema for the companion YAML artifact.
- `docs/reviews/exoplanet-failure-map-result-promotion-scorecard.review.yaml`
  — machine-readable companion to this scorecard.
- `campaign_profiles/exoplanet-mass-radius.yaml` — campaign autonomy profile
  whose required quality checks the audits satisfied.
