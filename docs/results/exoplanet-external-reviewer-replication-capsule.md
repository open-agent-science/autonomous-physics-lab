# Exoplanet External-Reviewer Replication Capsule

**Task:** `TASK-0484`  
**Campaign:** `exoplanet_mass_radius`  
**Capsule status:** external-reviewer replication guide  
**Result boundary:** `BENCHMARK_SUMMARY_ONLY`  
**Claim promotion:** not allowed

## Purpose

This capsule gives an external reviewer the shortest committed path for
inspecting and replaying the current exoplanet compact-radius benchmark surface.
It packages existing evidence only. It does not change metrics, promote claims,
create a `RESULT-*` artifact, or authorize stronger scientific wording.

The reviewer question is:

> Can the committed APL repository reproduce the compact-radius benchmark
> diagnostic from pinned exoplanet inputs, and are the public limitation lines
> explicit enough to prevent overclaiming?

## What This Capsule Covers

- A pinned NASA Exoplanet Archive PSCompPars snapshot.
- A frozen Chen-Kipping-style mass-radius baseline benchmark surface.
- The compact-radius slice (`R < 1.5 R_earth`) as the strongest current
  matched-control survivor.
- Independent replay evidence showing exact reproduction of the committed
  sandbox metrics.
- Scorecard wording boundaries that keep the output benchmark-only.

## Canonical Evidence Paths

| Purpose | Path |
| --- | --- |
| Public benchmark evidence card | `docs/results/exoplanet-compact-radius-benchmark-card.md` |
| Result-promotion scorecard | `docs/reviews/exoplanet-failure-map-result-promotion-scorecard.md` |
| Scorecard machine-readable review | `docs/reviews/exoplanet-failure-map-result-promotion-scorecard.review.yaml` |
| Compact/sub-Neptune matched-control audit | `docs/reviews/exoplanet-compact-subneptune-matched-control-audit.md` |
| Independent compact-radius replay | `docs/reviews/exoplanet-compact-radius-independent-replay.md` |
| Replayed metrics artifact | `agent_runs/AGENT-RUN-0042/metrics.json` |
| Pinned normalized snapshot | `data/exoplanets/exo-0001-pscomppars-snapshot.yaml` |
| Source manifest | `data/exoplanets/source_manifest.yaml` |
| Replay runner | `scripts/run_exoplanet_compact_subneptune_matched_control_audit.py` |
| Campaign page | `docs/campaigns/exoplanet-mass-radius.md` |
| Public dashboard | `docs/campaigns/public-science-dashboard.md` |

## Pinned Source And Checksum Context

The source manifest records the committed PSCompPars source contract:

- source family: NASA Exoplanet Archive Planetary Systems Composite Parameters;
- live fetch allowed: `false`;
- retrieval date: `2026-05-23T17:15:49Z`;
- raw snapshot path:
  `data/exoplanets/raw/exo-pscomppars-20260523T171549Z.csv`;
- raw SHA-256:
  `a86aefd7d0fd7c2e93aaad87f97adb4c96f1246d8fc00abae7d7c43082ba4e54`;
- normalized snapshot path:
  `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`;
- normalized SHA-256:
  `d86dc539c5175cafae44fadcb55194c00ac91d21b8f0ace1754fae3412dc1a6c`;
- row count: `6291`;
- included post-filter count: `4301`;
- excluded count: `1990`.

Reviewers should treat these hashes as provenance guards for committed inputs,
not as scientific-validity proofs.

## Local Verification Commands

Run these commands from the repository root after installing the project test
requirements.

### Repository hygiene

```bash
python3 -m ruff check .
python3 -m pytest tests/test_docs_links.py
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

### Re-run the compact/sub-Neptune audit into a temporary directory

Use a disposable output directory so committed sandbox artifacts are not
rewritten:

```bash
mkdir -p /tmp/apl-exoplanet-reviewer-replay
python3 scripts/run_exoplanet_compact_subneptune_matched_control_audit.py \
  --out /tmp/apl-exoplanet-reviewer-replay/metrics.json \
  --report /tmp/apl-exoplanet-reviewer-replay/report.md \
  --agent-run /tmp/apl-exoplanet-reviewer-replay/agent_run.yaml \
  --limitations /tmp/apl-exoplanet-reviewer-replay/limitations.md \
  --preflight /tmp/apl-exoplanet-reviewer-replay/preflight.md \
  --review-summary /tmp/apl-exoplanet-reviewer-replay/review_summary.md \
  --review /tmp/apl-exoplanet-reviewer-replay/review.md
```

Expected replay target:

- compare `/tmp/apl-exoplanet-reviewer-replay/metrics.json` with
  `agent_runs/AGENT-RUN-0042/metrics.json`;
- numeric tolerance: absolute tolerance `1.0e-12`;
- object keys, list lengths, strings, booleans, and nulls: exact match.

The committed independent replay recorded:

- differing fields: `0`;
- maximum absolute numeric drift: `0.0`;
- replay verdict: `SANDBOX_PASS`;
- pilot reproduction status: `match`.

## Current Benchmark Values To Inspect

| Quantity | Current value |
| --- | ---: |
| Snapshot rows | `6291` |
| Eligible true-mass/transit-radius rows | `1207` |
| Eligible true-mass log10 RMSE | `0.15817019267448623` |
| Compact-radius slice | `R < 1.5 R_earth` |
| Compact-radius count | `92` |
| Compact-radius log10 RMSE | `0.2633500276766559` |
| Adverse control | `per_class_median` |
| Delta vs adverse control | `0.025679576629077605` |
| Control margin | `0.022` |
| Scorecard verdict | `BENCHMARK_SUMMARY_ONLY` |
| Claim-candidate eligibility | `BLOCK` |

The compact-radius slice is the only currently highlighted slice that survives
this matched-control and deterministic negative-control panel within the
scorecard-approved wording boundary. Sub-Neptune and combined compact/sub-Neptune
slices remain control-sensitive or inconclusive.

## Safe External-Reviewer Wording

External reviewers may describe the artifact as follows:

> APL maintains a benchmark-only compact-radius residual diagnostic on a pinned
> NASA Exoplanet Archive PSCompPars snapshot. Under a frozen
> Chen-Kipping-style baseline, the compact-radius slice (`R < 1.5 R_earth`) is
> the strongest current matched-control survivor, and an independent replay
> reproduced the committed sandbox metrics exactly. The scorecard verdict is
> `BENCHMARK_SUMMARY_ONLY`, not a claim candidate.

## Forbidden Wording

Do not say or imply that this capsule:

- identifies a new exoplanet mass-radius law;
- predicts habitability, biosignatures, composition, atmospheric properties, or
  target priority;
- globally falsifies Chen-Kipping or any broad mass-radius relation;
- proves anomalous physics in compact planets;
- promotes a `CLAIM-*`, `KNOW-*`, `PRED-*`, or canonical `RESULT-*` artifact;
- upgrades sandbox benchmark memory into external replication by itself.

## Limitations

- This capsule is a replication guide and communication boundary, not a new
  scientific result.
- The evidence remains benchmark-only and claim-blocked under the scorecard.
- The benchmark uses one committed PSCompPars snapshot; cross-snapshot or
  reveal-style claims require a future second-snapshot protocol.
- Matched controls are diagnostic slices, not causal adjustments.
- Minimum-mass/transit-radius rows remain structurally underpowered and are not
  part of the headline metric.
- The reviewer should inspect committed paths and rerun commands rather than
  relying on prose summaries.

## External Review Checklist

- [ ] Confirm repository hygiene commands pass.
- [ ] Confirm the pinned source manifest paths and checksums are present.
- [ ] Re-run the compact/sub-Neptune audit into a temporary output directory.
- [ ] Compare replay metrics against `agent_runs/AGENT-RUN-0042/metrics.json`.
- [ ] Confirm the benchmark values match the evidence card and independent replay.
- [ ] Confirm scorecard verdict remains `BENCHMARK_SUMMARY_ONLY`.
- [ ] Confirm forbidden wording is absent from any public summary using this
      capsule.

## Output Routing

- Task verdict: `BENCHMARK_SUMMARY_ONLY`
- Canonical destination:
  `docs/results/exoplanet-external-reviewer-replication-capsule.md`
- Review tier: `none`
- Gate A status: not attempted
- Gate B status: not attempted by this task; existing independent sandbox replay
  is cited from `docs/reviews/exoplanet-compact-radius-independent-replay.md`
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Result artifact impact: no canonical `RESULT-*` created or edited
