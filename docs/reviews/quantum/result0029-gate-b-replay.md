# Quantum RESULT-0029 Gate B Replay

- Task: `TASK-0987`
- Result artifact: `results/EXP-0022/RUN-0001/result.yaml`
- Existing verdict: `INCONCLUSIVE`
- Verdict: `GATE_B_PASS`

## Summary

The recorded RESULT-0029 workflow replayed successfully through the formal Gate
B helper. All compared numeric metrics matched within the `1e-9` tolerance with
maximum absolute drift `0.0`, and the `INCONCLUSIVE` verdict is unchanged.

This replay validates deterministic reproduction of the frozen no-refit
InP-to-ZnSe transfer contract. It does not relax the `0.05 eV` survival margin,
does not refit on ZnSe, and does not promote a quantum-size law or any claim.

## Command

```bash
python scripts/apl_validate_agent_published_result.py \
  results/EXP-0022/RUN-0001/result.yaml \
  --output-dir /private/tmp/apl-task-0987-result0029-gateb-replay \
  --validator-contributor-id gladunrv \
  --validator-github-username gladunrv \
  --validator-agent-tool "Codex Desktop" \
  --validator-model "GPT-5" \
  --json
```

Helper status: `PASS`.

Helper warning:

| Code | Severity | Meaning |
| --- | --- | --- |
| `same-contributor` | warning | Replay uses the same contributor id with a different agent tool path. This records deterministic reproducibility, not independent-human validation. |

## Drift Table

| Metric | Expected | Observed | Delta |
| --- | ---: | ---: | ---: |
| `verification.checks[1].metrics.primary_transfer_mae_ev` | `0.09921632` | `0.09921632` | `0.0` |
| `verification.checks[1].metrics.primary_best_control_mae_ev` | `0.1458` | `0.1458` | `0.0` |
| `verification.checks[1].metrics.primary_margin_ev` | `0.04658368` | `0.04658368` | `0.0` |
| `verification.checks[2].metrics.margin_shortfall_ev` | `0.00341632` | `0.00341632` | `0.0` |
| `verification.checks[3].metrics.secondary_reverse_margin_ev` | `0.100125421` | `0.100125421` | `0.0` |
| `comparison_summary[0].observed_value` | `0.04658368` | `0.04658368` | `0.0` |
| `comparison_summary[1].observed_value` | `0.09921632` | `0.09921632` | `0.0` |
| `comparison_summary[2].observed_value` | `0.100125421` | `0.100125421` | `0.0` |

Full helper comparison count: 22 numeric metrics, maximum absolute drift `0.0`.

## Interpretation Boundary

The primary model still beats the required controls but misses the frozen
survival rule: the margin remains `0.04658368 eV` against the `0.05 eV`
threshold, a shortfall of `0.00341632 eV`. The secondary reverse direction
remains diagnostic only and cannot rescue the primary verdict.

No target-material coefficient, exponent, intercept, bulk gap, geometry map,
threshold, residual correction, or effective-mass rescue is fitted after
observing ZnSe errors. No quantum-dot size law, material recommendation,
device-performance guidance, biomedical wording, claim, knowledge artifact, or
prediction is created.

## Output Routing

- Canonical destination: RESULT-0029 review-tier metadata update plus this
  review note.
- Review tier: RESULT-0029 upgraded from `AGENT_PUBLISHED` to
  `AGENT_VALIDATED`.
- Gate A status: already passed by the existing RESULT-0029 package.
- Gate B status: `PASS`, with `validation_independence:
  same_account_different_tool`.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: maintainer review is still required for any stronger
  interpretation or claim/knowledge promotion.
