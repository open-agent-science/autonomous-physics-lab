# Particle AHS Diagnostic Replay Routing

- Task: `TASK-0991`
- Sandbox run: `AGENT-RUN-0091`
- Benchmark config: `examples/benchmarks/particle_ahs_common_scheme_baseline.yaml`
- Verdict: `KEEP_SANDBOX_MEMORY`

## Summary

The AHS common-scheme geometric-midpoint diagnostic replayed byte-identically
from committed bytes. The replay confirms the sandbox diagnostic memory, but it
does not justify a canonical RESULT artifact because the benchmark has only two
charge sectors, no holdout, no predeclared success threshold, and no
covariance-aware significance model.

No particle-mass formula search, Koide test, scheme mixing, mass/Yukawa
conversion, claim promotion, or BSM interpretation is performed by this task.

## Replay Command

```bash
python scripts/run_particle_ahs_common_scheme_baseline.py \
  --output-dir /private/tmp/apl-task-0991-ahs-replay/AGENT-RUN-0091
```

Replay status: `PASS`.

## Drift And Checksum Table

| Artifact or metric | Committed | Replayed | Delta / status |
| --- | ---: | ---: | ---: |
| `metrics_equal` | `true` | `true` | `PASS` |
| source SHA-256 | `b96709627e13542c6c047ca565713028321bba98fcb070d1a016ab774e29b480` | same | `PASS` |
| `mean_absolute_residual_dex` | `0.17454158374947432` | `0.17454158374947432` | `0.0` |
| `root_mean_square_residual_dex` | `0.17897548381070558` | `0.17897548381070558` | `0.0` |
| `maximum_absolute_residual_dex` | `0.21413273613863043` | `0.21413273613863043` | `0.0` |
| up-type signed residual | `0.1349504313603182` | `0.1349504313603182` | `0.0` |
| down-type signed residual | `-0.21413273613863043` | `-0.21413273613863043` | `0.0` |
| `agent_run.yaml` | `c455d26ab67a5b6d0b263753d973e3c580f5112ef8aa148bfc5ec248d0d27456` | same | byte-identical |
| `metrics.json` | `cf8ee51f8bfd47531701c4decf237adb7d86d77ee8a039abc7152d9b006f4f83` | same | byte-identical |
| `report.md` | `cd18c38e831025e9e9b66b966b49a6885e213c6fd4838e963a78f6f2910005c3` | same | byte-identical |
| `limitations.md` | `ae22ff632960c99542fec7ec5cde05f5c57be7928aaf53fd9f62a52460a6fc93` | same | byte-identical |
| `preflight.md` | `422fde645c2fb999aa89e7925592a57edba21d9f4dcbfb9c868afc08b3b421ae` | same | byte-identical |
| `review_summary.md` | `eeb26020fa62cdb38f0dd45c3373cd2ac18ef2a066213286acb5f5d4093739ea` | same | byte-identical |

## Promotion Fit

Result-promotion protocol check:

| Option | Decision | Reason |
| --- | --- | --- |
| Canonical `RESULT-*` | Reject | The run has an `INCONCLUSIVE` diagnostic verdict but no predeclared pass/fail threshold, no holdout, only two sectors, and no uncertainty/covariance significance model. |
| Review note only | Accept | The replay strengthens durable memory that the diagnostic is deterministic and bounded. |
| Keep sandbox memory | Accept | `AGENT-RUN-0091` already encodes the correct artifact tier and no-claim boundary. |

The correct route is therefore to keep `AGENT-RUN-0091` as sandbox diagnostic
memory and use review notes for durable routing context. A future canonical
artifact would need a separately approved benchmark contract with an explicit
quality rule, source/covariance policy, and no-claim wording.

## Interpretation Boundary

The geometric-midpoint baseline is a descriptive zero-parameter reference on
one source-derived common-scheme Yukawa surface. The up-type middle value is
above its geometric midpoint and the down-type middle value is below its
geometric midpoint; that is descriptive memory only.

This task does not support or refute a particle-mass law. It does not reopen
formula search, combine schemes, convert Yukawas into masses, modify
`CLAIM-0006` or `CLAIM-0007`, or create a `RESULT`, `PRED`, `CLAIM`, or `KNOW`
artifact.

## Output Routing

- Canonical destination: review note only, this file, with existing sandbox
  memory retained at `agent_runs/AGENT-RUN-0091/`.
- Review tier: none; no canonical result tier is set.
- Gate A status: not attempted; no RESULT artifact is created.
- Gate B status: not applicable to sandbox-only routing; replay drift is `0.0`.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: canonical RESULT promotion would require a new
  maintainer-approved benchmark contract with threshold and significance policy.
