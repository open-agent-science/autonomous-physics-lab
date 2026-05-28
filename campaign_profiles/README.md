# Campaign Autonomy Profiles

Campaign profiles are machine-readable contracts for bounded autonomous
research lanes.

Each profile defines:

- campaign id and source documentation;
- autonomy status;
- allowed hypothesis and experiment families;
- required inputs and references;
- required quality gates;
- forbidden claims;
- validation commands;
- PR handoff requirements.

Profiles do not authorize claim promotion. They may authorize canonical
`RESULT-*` or `PRED-*` creation only when the selected task explicitly allows
that artifact class and the result-promotion gates in
`docs/result-promotion-protocol.md` pass. Otherwise, they authorize bounded
proposal, source-readiness, replay, audit, and sandbox work under the task
contract.

## Current Profiles

| Profile | Status | Summary |
| --- | --- | --- |
| `pendulum-formula-falsification.yaml` | `WHITELISTED_PILOT` | First pilot for range-aware candidate formula falsification |
| `dimensional-analysis-validator.yaml` | `WHITELISTED_LIMITED` | Limited classification and challenge-entry proposal work |
| `nuclear-mass-surface.yaml` | `WHITELISTED_LIMITED` | Bounded residual diagnostics, replay, and result-promotion preflights against frozen baselines and structured holdout/reveal protocols |
| `exoplanet-mass-radius.yaml` | `WHITELISTED_LIMITED` | Pinned-snapshot residual maps, matched controls, and source/baseline discipline for the active secondary campaign |
| `quantum-size-effects.yaml` | `SOURCE_READINESS` | Direct-row/source-artifact readiness before baseline or hypothesis batches |
| `particle-mass-relations.yaml` | `GUARDRAIL_ONLY` | Falsification-first and provenance-focused proposal work |
| `textbook-formula-audit.yaml` | `SCAFFOLD` | Per-formula sandbox audits of textbook formulas against pinned public datasets; first slice queued is the Stellar Mass-Luminosity OOD audit |

## Review Rule

If a profile is missing or says `EXCLUDED`, autonomous agents must stop and ask
for a canonical task or proposal path.
