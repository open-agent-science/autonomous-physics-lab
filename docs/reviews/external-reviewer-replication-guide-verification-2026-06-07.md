# External Reviewer Replication Guide — Post-Transfer Verification (2026-06-07)

This note clears named blocker **B2** from
[v0.2-public-readiness.md](./v0.2-public-readiness.md): the external reviewer
replication guide is verified against the current public evidence surface after
the transfer to the `open-agent-science` organization.

## Method

Audited [external-reviewer-replication-guide.md](../external-reviewer-replication-guide.md)
against the live repository state on `main` (commit `8569d95a` at audit time).
Re-verification is cheap and should be repeated against the exact opening commit
during the B3 release-time signoff.

## Findings — PASS

- **Clone URL** points at `https://github.com/open-agent-science/autonomous-physics-lab.git`
  (post-transfer owner correct; the earlier `gladunrv` reference was synced by
  TASK-0674).
- **Bounded core replay table matches `scripts/reproduce_core_results.py --list`
  exactly** — the same seven surfaces and result ids:
  `pendulum-gauntlet` (RESULT-0004), `dimensional-analysis` (RESULT-0007),
  `koide-charged-lepton` (RESULT-0005), `koide-tau-holdout` (RESULT-0006),
  `koide-neutrino-falsification` (RESULT-0009),
  `koide-quark-falsification` (RESULT-0010),
  `particle-mass-falsifier` (RESULT-0011), with `EXP-0010` / Muon g-2 excluded
  by design.
- **All referenced canonical result directories exist**: `EXP-0001/RUN-0003`,
  `EXP-0006/RUN-0006`, `EXP-0004/RUN-0004`, `EXP-0005/RUN-0005`,
  `EXP-0007/RUN-0001`, `EXP-0008/RUN-0001`, `EXP-0009/RUN-0001`,
  `EXP-0011/RUN-0001`, `EXP-0012/RUN-0001`.
- **All referenced docs exist**: `status.md`, `reproducibility-capsules.md`,
  `result-artifacts-index.md`, `negative-results-registry.md`,
  `result-quality-rubric.md`.
- **Validation commands** in the guide match the canonical `validate-repo` and
  `pytest` commands.

## Verdict

**B2: PASS.** The guide is accurate and current; no corrections are required for
the public-opening decision.

## Optional enhancement (not a blocker)

The repository has grown newer canonical surfaces since the guide's curation
(`EXP-0013` Stefan-Boltzmann exact-reference, Materials `MD-0001`, Exoplanet
mass-radius, and nuclear research-factory sprints). The guide intentionally stays
a bounded core replay surface, so omitting them is curation, not drift. A future
update may add a short pointer to these newer campaign surfaces, but it is not
required to clear B2.
