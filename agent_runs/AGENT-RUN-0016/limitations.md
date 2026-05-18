# AGENT-RUN-0016 Limitations

- This is a sandbox-only adversarial stress scout. It does not create or update canonical results, claims, knowledge, or prediction registry entries.
- Feature coefficients are fit on the small 11-row NMD-0002 residual slice. Sub-MeV deltas are retrospective diagnostics, not prospective prediction evidence.
- The post-AME2020 row-level holdout is already committed in the repository. Evaluation here is a retrospective stress check, not a live reveal or blind prediction.
- The four overrepresented registry targets (Ni-76, Ca-55, Ga-85, Zn-80) are absent from the post-AME2020 holdout, so the holdout is not directly biased by repeated-target pressure. The `registry_repeat_chain_neighbor` subset contains only six rows (Ni-74, Ni-75, Ca-54, Ga-83, Ga-84, Zn-79), so its delta is fragile and not interpretable in isolation.
- Candidate verdicts are conservative triage labels for maintainer review, not scientific acceptance.
- STRESS-SHELL-001, STRESS-SHELL-002, and STRESS-SHELL-003 reproduce the prior shell-axis signals from AGENT-RUN-0012. They are flagged `PARTIALLY_VALID` only as sandbox-triage labels and remain bounded sub-MeV diagnostic effects on a small training surface.
- STRESS-SHELL-004 sign-inverted control regresses primary, magic, heavy, and chain-neighbor subsets as expected when the underlying signal direction is consistent. Its verdict is `INCONCLUSIVE` because the rule fires only if the inverted form *improves* the surface.
- STRESS-SHELL-005 shuffled control collapses to a near-noise-floor delta (sub-milli-MeV magnitude on every subset). Its `PARTIALLY_VALID` label is a strict triage outcome; the practical interpretation is that the shuffle scheme destroys the row-feature correspondence and leaves only fit-machinery noise, which is the expected behavior of a shell-axis signal under shuffle stress.
- STRESS-SHELL-006 near-null control returns exactly zero deltas, as required by the design.
