# Exoplanet Compact-Radius Independent Replay

**Task:** `TASK-0445`  
**Replayed artifact:** `AGENT-RUN-0042`  
**Original task:** `TASK-0427`  
**Original runner:** `scripts/run_exoplanet_compact_subneptune_matched_control_audit.py`  
**Snapshot:** `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`  
**Replay agent/tool:** `roman` / `codex`  
**Original agent/tool:** `roman` / `claude-code`  
**Verdict:** `SANDBOX_PASS` replay matched

## Scope

This review records an independent replay of the compact/sub-Neptune
matched-control audit from `AGENT-RUN-0042`.

The replay uses only committed inputs and the existing runner. It does not
perform a live fetch, refit the Chen-Kipping baseline, create a canonical
`RESULT-*`, edit `CLAIM-*`, `KNOW-*`, or `PRED-*` artifacts, or introduce any
composition, habitability, target-priority, discovery, or new mass-radius-law
wording.

## Replay Command

The runner was executed into a temporary output directory so the prior
`AGENT-RUN-0042` sandbox artifact was not rewritten:

```bash
python3 scripts/run_exoplanet_compact_subneptune_matched_control_audit.py \
  --out /tmp/apl-task-0445-replay/metrics.json \
  --report /tmp/apl-task-0445-replay/report.md \
  --agent-run /tmp/apl-task-0445-replay/agent_run.yaml \
  --limitations /tmp/apl-task-0445-replay/limitations.md \
  --preflight /tmp/apl-task-0445-replay/preflight.md \
  --review-summary /tmp/apl-task-0445-replay/review_summary.md \
  --review /tmp/apl-task-0445-replay/review.md
```

The temporary `agent_run.yaml` still carries the original runner's hardcoded
`AGENT-RUN-0042`/`TASK-0427` identity. For that reason this PR records the
independent replay as a review note rather than creating a misleading
`AGENT-RUN-0043` directory.

## Comparison Method

`/tmp/apl-task-0445-replay/metrics.json` was compared against the committed
`agent_runs/AGENT-RUN-0042/metrics.json` recursively.

Tolerance policy:

- numeric fields: absolute tolerance `1.0e-12`
- list lengths and object keys: exact match
- strings, booleans, and nulls: exact match

Comparison outcome:

- differing fields: `0`
- maximum absolute numeric drift: `0.0`
- replay verdict: `SANDBOX_PASS`
- pilot reproduction status: `match`

## Reproduced Metrics

| Quantity | Replayed value |
| --- | ---: |
| Eligible true-mass/transit-radius count | `1207` |
| Eligible true-mass log10 RMSE | `0.15817019267448623` |

| Slice | Label | Count | Target log10 RMSE | Verdict | Outcome | Adverse control | Delta vs adverse |
| --- | --- | ---: | ---: | --- | --- | --- | ---: |
| `CSN-001` | `compact_radius_lt1p5Re` | `92` | `0.2633500276766559` | `SANDBOX_PASS` | `residual_stress_above_eligible_and_controls` | `per_class_median` | `0.025679576629077605` |
| `CSN-002` | `sub_neptune_radius_1p5_4Re` | `340` | `0.20417461029825096` | `INCONCLUSIVE` | `control_sensitive_residual_stress` | `nearest_radius_outside_slice` | `0.007627108182247239` |
| `CSN-003` | `compact_or_sub_neptune_radius_lt4Re` | `432` | `0.21812633379546395` | `INCONCLUSIVE` | `control_sensitive_residual_stress` | `per_class_median` | `0.018475622966713262` |

## Interpretation

The replay confirms that the committed runner reproduces the `AGENT-RUN-0042`
metrics exactly in this Codex session. This strengthens the benchmark
reproducibility of the compact-radius matched-control audit, especially because
the original artifact was produced with `claude-code` and this replay was run
with `codex`.

The scientific interpretation remains bounded:

- the compact-radius slice remains sandbox benchmark evidence only;
- `CSN-001` is a matched-control survivor within the current diagnostic panel;
- `CSN-002` and `CSN-003` remain control-sensitive/inconclusive;
- no causal, composition, habitability, target-priority, discovery, or new
  mass-radius-law interpretation is supported.

## Output Routing

- Task verdict: `SANDBOX_PASS` replay matched
- Canonical destination: `docs/reviews/exoplanet-compact-radius-independent-replay.md`
- Review tier: `none`
- Gate A status: not attempted
- Gate B status: Gate-B-style replay matched for sandbox evidence, but no
  canonical `RESULT-*` artifact was upgraded
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Result artifact impact: no canonical result artifact created or edited
- Publication blocker: this remains sandbox benchmark evidence; external
  comparability is improved but not promoted to a claim, prediction, or
  knowledge artifact

## Final Verdict

Independent replay matched `AGENT-RUN-0042` exactly. The appropriate follow-up
is to cite this as cross-tool sandbox replay evidence for the exoplanet
benchmark package, while keeping all public wording benchmark-only and
non-claim-facing.
