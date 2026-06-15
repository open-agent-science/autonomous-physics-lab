# RESULT-0021 Report

`RESULT-0021` records the first frozen MD-0002 formation-energy benchmark.
All values are committed Materials Project computed-DFT values from the
accepted 362-row stable ternary-oxide slice.

The best global null was the train median, with holdout MAE `0.506092`
eV/atom. The train-only exact cation-pair mean reached `0.200606` eV/atom,
improving MAE by `0.305486` eV/atom (`60.3618%`). It beat every declared
label-shuffle and cation-label-shuffle control.

Across seeded 70/30 splits, the cation-pair baseline won `5/5` seeds with mean
MAE `0.192881` eV/atom. Its `0.350085` eV/atom mean margin over the runner-up
exceeded the `0.015359` eV/atom across-seed noise comparator.

Verdict: `VALID_IN_RANGE` on this frozen computed-DFT slice. This result does
not support a universal relation, measured-property claim, material ranking,
synthesis recommendation, device claim, or biomedical claim.
