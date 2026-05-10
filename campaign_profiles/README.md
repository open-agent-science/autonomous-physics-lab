# Campaign Autonomy Profiles

Campaign profiles are machine-readable contracts for autonomous sandbox
research.

Each profile defines:

- campaign id and source documentation;
- autonomy status;
- allowed hypothesis and experiment families;
- required inputs and references;
- required quality gates;
- forbidden claims;
- validation commands;
- PR handoff requirements.

Profiles do not authorize claim promotion or canonical result creation. They
only authorize bounded proposal and sandbox work under
`docs/autonomous-research-loop.md`.

## Current Profiles

| Profile | Status | Summary |
| --- | --- | --- |
| `pendulum-formula-falsification.yaml` | `WHITELISTED_PILOT` | First pilot for range-aware candidate formula falsification |
| `dimensional-analysis-validator.yaml` | `WHITELISTED_LIMITED` | Limited classification and challenge-entry proposal work |
| `nuclear-mass-surface.yaml` | `EXCLUDED` | Flagship campaign scaffold exists, but autonomy is blocked until dataset, baseline, and holdout tasks land |
| `particle-mass-relations.yaml` | `GUARDRAIL_ONLY` | Falsification-first and provenance-focused proposal work |

## Review Rule

If a profile is missing or says `EXCLUDED`, autonomous agents must stop and ask
for a canonical task or proposal path.
