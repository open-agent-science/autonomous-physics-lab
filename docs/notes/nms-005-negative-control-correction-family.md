# NMS-005: Negative-Control Correction Family for Nuclear Residual Testing

## Proposed Family

δ(N, Z) = c₁ · sin(π·N/2) · sin(π·Z/2)

## Why It Looks Attractive

This family produces a correction that alternates sign for odd/even N and Z —
mimicking the nuclear pairing effect, where even-even nuclei are more bound
than odd-A or odd-odd nuclei. It is algebraically simple and has a physical
motivation.

## Why It Should Fail Under Holdout

### Structural failure on even-N even-Z nuclei

For even N: sin(πN/2) = sin(kπ) = 0 for integer k.
For even Z: sin(πZ/2) = 0 similarly.

The most common measured nuclei in the AME dataset are even-even (they have the
highest stability). For all even-even nuclei, δ(N,Z) = 0 — the correction
vanishes exactly. The family cannot learn from the most common training cases.

### Overfitting on sparse odd-N coverage

If the training set is sparse in odd-N nuclei (as it will be for very
neutron-rich species), the oscillation frequency is not well constrained by
data. The single parameter c₁ absorbs a mixture of genuine pairing effects and
unrelated residual noise.

### Expected holdout spike

On a holdout set that includes odd-N nuclei (e.g., an isotope-chain holdout for
a mixed-parity chain), the correction will mismatch badly unless c₁ happens to
be calibrated for that specific chain.

## Diagnostic Axis It Should Fail

Shell-closure residual map: near magic numbers (N=8, 20, 28, 50, 82, 126), the
pairing structure is qualitatively different from a simple sinusoidal model.
The negative control should show large residuals near these closures.

## Limitation Statement

No numerical test has been run. This family is proposed as a methodological
negative control, not as a correction candidate. Failure under holdout is
expected by design.
