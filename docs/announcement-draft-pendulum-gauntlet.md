# Announcement Draft — Pendulum Gauntlet 100

Use the versions below as starting points for future public communication.
They are intentionally conservative and should stay tied to the canonical
artifacts.

## Version A — Technical

Autonomous Physics Lab now has a reproducible pendulum benchmark package built
from `EXP-0001/RUN-0003`.

APL evaluated 100 deterministic candidate formulas for the ideal pendulum
period ratio against the exact elliptic-integral reference. The top leaderboard
candidate, `model_t4_x1`, validated in the configured test range with about
`3.1e-4` mean relative residual and `9.5e-4` max relative residual. A separate
precision audit showed that this reported error is dominated by model residual,
not elliptic-reference numerical noise or six-decimal coefficient rounding.

This is a verification-first benchmark result, not an exact-discovery claim.
The package includes a full leaderboard, failure-mode summary, verification
checks, and explicit limitations. Near-separatrix diagnostics still fail, so no
global validity claim is made.

Canonical references:

- `results/EXP-0001/RUN-0003/result.yaml`
- `results/EXP-0001/RUN-0003/leaderboard.md`
- `results/EXP-0001/RUN-0003/metrics.json`
- `results/EXP-0001/RUN-0003/precision_audit.md`

## Version B — Science-Friendly

APL has completed a systematic pendulum approximation benchmark that is strong
enough to show externally without overstating what it means.

The project tested 100 deterministic candidate formulas for the ideal pendulum
period ratio and compared them to the exact elliptic-integral reference. The
top leaderboard formula passed the configured in-range checks with about
`3.1e-4` mean relative residual on the test split. An independent audit then
checked whether that error might be coming from numerical reference noise, and
found that it is better interpreted as model residual instead.

That gives APL a clean scientific story: candidate generation, deterministic
evaluation, leaderboard ranking, failure-mode reporting, numerical audit, and
clear limitations. The result is range-aware, reproducible, and honest about
what still fails near the separatrix. No symbolic exactness claim and no global
validity claim are made.

## Version C — Short Social Post

APL tested 100 deterministic formulas for the ideal pendulum period ratio.

Top leaderboard candidate: validated in the configured range at about `3.1e-4`
mean relative residual on the test split.

A dedicated audit says that error is model residual, not numerical reference
noise.

Full leaderboard, failure modes, and limitations are included.

No symbolic exactness claim. No global validity claim.
