# Nuclear Mass Split Rationale

## Why One Split Is Not Enough

The nuclear-mass campaign is structurally richer than pendulum or a simple
regression benchmark.

A candidate can look good for the wrong reason:

- it can memorize one shell neighborhood;
- it can exploit one isotope family;
- it can improve average error while making neutron-rich behavior worse;
- it can overfit the tiny benchmark slice by adding expressive but
  non-transferable structure.

That is why `TASK-0169` uses multiple holdout families instead of a single
 train/test cut.

## Split Intent

### Random Nuclide Holdout

Why keep it:

- it gives a coarse sanity check against obvious memorization;
- it is easy to reproduce with a fixed seed;
- it helps compare future tasks that may use different dataset sizes.

Why it is not enough:

- it does not isolate shell-region generalization;
- it can leak local structure too easily;
- it can flatter a candidate that is only slightly more flexible than the
  baseline.

### Isotope-Chain Holdout

Why it matters:

- nuclear residual patterns often cluster along chains;
- if a correction cannot survive unseen members of a chain, it is not a good
  scientific story for later autonomy.

What failure means:

- likely interpolation on neighboring nuclides rather than generalization.

### Magic-Number Region Holdout

Why it matters:

- shell-sensitive interpretation is central to the campaign;
- many attractive correction families will target exactly these regions;
- hiding one shell neighborhood is the cleanest way to test whether a proposed
  shell-aware term travels at all.

What failure means:

- the candidate may only be describing one known bump rather than a reusable
  structure.

### Neutron-Rich Extrapolation Holdout

Why it matters:

- this is where many naive residual terms become unstable;
- it is the most honest internal stress test before any future time-split
  dataset exists.

What failure means:

- the candidate adds flexibility without extrapolation discipline.

## Time-Split Holdout Is Future Work

The campaign should absolutely want a time-split holdout later, but not by
pretending one exists already.

A time-split should activate only after:

- a later curated measurement batch is committed separately;
- source and checksum policy are explicit;
- older and newer surfaces are not blended.

Until then, chain, shell, and neutron-rich splits do the scientific heavy
lifting.

## Why Complexity Penalty Must Stay Visible

Nuclear residual tasks are vulnerable to pretty-but-fragile corrections.

The campaign should prefer:

- compact parameterization;
- limited region switching;
- easy-to-review symbolic structure.

It should penalize:

- many special cases;
- hidden piecewise behavior;
- narrow shell bumps that only win after extra tuning.

## Negative Controls We Expect To Fail

Useful negative controls include:

- one shell term tuned to `Pb-208` style regions only;
- one isotope-chain-specific correction that does not transfer to neighboring
  chains;
- one over-flex asymmetry term that helps train MAE but worsens neutron-rich
  holdout.

These failures are valuable because they tell reviewers what not to trust in
the later autonomous pilot.

## Practical Consequence For TASK-0170

The first autonomous nuclear-mass pilot should not merely report:

- one improved fit;
- one pooled MAE;
- one attractive symbolic term.

It should report:

- which holdout families were active;
- where the candidate improved;
- where it degraded;
- whether it beat the baseline cleanly enough to survive review;
- which negative control failed and why.
