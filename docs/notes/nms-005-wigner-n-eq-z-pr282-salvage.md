# NMS-005: Wigner N=Z Pairing-Term Salvage From Superseded PR 282

## Context

PR #282 independently reran `TASK-0201` after the canonical pairing/odd-even
batch had already landed. The PR cannot be merged as submitted because it
reuses canonical artifact identifiers already present on `main`, including
`AGENT-RUN-0011`, `EXP-PROPOSAL-0008`, and `HYP-PROPOSAL-0038..0042`, but with
different scientific content.

This note preserves the only distinct scientific idea from that PR: a Wigner
`N=Z` correction term for nuclear residual testing. It is not a canonical
result, not a replacement for the accepted `AGENT-RUN-0011`, and not evidence
for claim promotion.

## Salvaged Candidate

Candidate family:

```text
r_corr = w * I[N = Z] / A
```

Rationale:

- `N=Z` nuclei can receive additional proton-neutron pairing or Wigner-energy
  contributions in semi-empirical mass formulas.
- The feature is compact and physically motivated.
- It is safe to preserve as a possible negative-control or narrow future
  diagnostic because it does not target the known In/Sb or N=82 failure region.

## Reported PR-282 Metrics

The superseded PR reported these values for its Wigner candidate:

| Check | Reported value |
| --- | ---: |
| Structured holdout verdict | `INCONCLUSIVE` |
| Random-stratified delta MAE | `+0.5388 MeV` |
| Oxygen-chain delta MAE | `-0.0674 MeV` |
| Magic-heavy-region delta MAE | `0.0000 MeV` |
| Neutron-rich-edge delta MAE | `0.0000 MeV` |
| Post-AME2020 primary delta MAE | `+0.0011 MeV` |
| Post-AME2020 activation | `3 / 295` rows |

These metrics should be treated as PR-local evidence only. They are useful for
triage but should not be imported into canonical result memory without a new
proposal id, new experiment proposal id, and a maintainer-reviewed rerun.

## Scientific Reading

The candidate is physically interpretable but nearly dormant on the current
post-AME2020 primary surface. A feature that activates on only `3 / 295`
holdout rows cannot materially evaluate the broader neutron-rich time-split
surface, even if it has a plausible nuclear-structure motivation.

The most useful reading is negative or boundary-setting:

- Wigner-like `N=Z` corrections may be relevant for self-conjugate nuclei.
- The current post-AME2020 holdout is dominated by non-`N=Z` nuclides.
- Therefore this family is a poor third-batch direction for the current
  Nuclear Mass Surface campaign unless a future task explicitly defines an
  `N=Z` or near-`N=Z` benchmark surface.

## Recommended Handling

- Do not merge PR #282 as a replacement for the accepted pairing batch.
- Do not reuse its artifact ids.
- If this idea is revisited, create fresh proposal ids and make the evaluation
  target explicit: either an `N=Z` focused diagnostic surface or a documented
  negative control showing dormancy on neutron-rich holdouts.
- Keep the current campaign interpretation unchanged: the second nuclear
  sandbox wave produced useful negative evidence, not a promotable correction
  family.

## Verdict

`REVIEW_NEEDED` as salvaged scientific memory.

The Wigner `N=Z` idea is worth preserving as a scoped future diagnostic or
negative-control family, but PR #282 should be closed as superseded rather than
merged.
