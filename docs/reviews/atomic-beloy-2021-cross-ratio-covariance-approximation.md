# Atomic Beloy 2021 Cross-Ratio Covariance Approximation

**Task:** `TASK-0402`
**Predecessor:** `TASK-0371` (first-batch row curation), `TASK-0401` (row readiness re-check), `TASK-0344` (covariance/uncertainty contract)
**Campaign:** Atomic-Clock Residuals
**Source under test:** Beloy, K., et al. (BACON), arXiv:2005.14694 / Nature 591, 564 (2021)
**Verdict:** `SOURCE_DERIVED_APPROXIMATION_PSD` (sandbox-only; lower-bound shared-clock only; no benchmark; no claim)

## Scope

The committed Beloy 2021 first-batch direct-ratio rows
(`ACR-0001-ROW-001..003`) share clocks across pairs (Al⁺, Yb, Sr each
appear in two of the three ratios). The source paper publishes per-row
Bayesian-model 1-σ totals (Table 1, last row) and per-clock systematic
contributions (Table 1, per-clock columns), but it does **not** publish
a 3×3 cross-ratio covariance matrix. The `TASK-0401` re-check explicitly
flagged this as Blocker 1 before any benchmark consumer may combine two
or more rows.

This document attempts a deterministic source-derived approximation of
the 3×3 cross-ratio covariance matrix using only committed source
artifacts and documented uncertainty components. Where the source does
not support deterministic sign assignment, the contribution is omitted
and labelled as an excluded lab-wide component.

The output is sandbox-only: no benchmark is authorised, no drift is fit,
no constants-variation constraint is derived, no prediction-registry
entry is added, and no claim is promoted.

## Inputs Used

| Input | Role |
| --- | --- |
| `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` | Per-row Bayesian totals and per-clock systematic components. |
| `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf` | Source artifact (Table 1, Sec. 4.5). |
| `docs/reviews/atomic-clock-beloy-2021-direct-ratio-row-curation.md` | TASK-0371 first-batch curation (extraction-shape lock to per-ratio totals). |
| `docs/reviews/atomic-clock-covariance-uncertainty-semantics.md` | TASK-0344 required-fields and stop conditions. |
| `docs/reviews/atomic-beloy-2021-row-readiness-recheck.md` | TASK-0401 PINNED_DATASET classification and Blocker 1 statement. |

## Methodology

Each ratio `v_X / v_Y` has fractional uncertainty contributions from
clock X (sign `+1`) and clock Y (sign `−1`). A physical systematic shift
of a single clock therefore appears with the same magnitude but
ratio-orientation-dependent sign in every ratio that contains that
clock.

For an unordered pair of rows `(i, j)` and a shared clock `c`:

```
Cov_c(i, j) = sign_c(i) * sign_c(j) * sigma_{c, i} * sigma_{c, j}
Cov(i, j)   = sum over shared clocks c of Cov_c(i, j)
```

with `sign_c(row) = +1` if clock `c` is the numerator of that row's
ratio and `−1` if it is the denominator.

The diagonal entries are the Bayesian-model 1-σ totals squared, taken
directly from the dataset (`uncertainty.total` per row).

### Sign table

| Row | Ratio | Numerator | Denominator | Signs |
| --- | --- | --- | --- | --- |
| ACR-0001-ROW-001 | Al⁺/Yb | BACON-CLOCK-AL27PLUS | BACON-CLOCK-YB171 | Al⁺ = +1, Yb = −1 |
| ACR-0001-ROW-002 | Al⁺/Sr | BACON-CLOCK-AL27PLUS | BACON-CLOCK-SR87 | Al⁺ = +1, Sr = −1 |
| ACR-0001-ROW-003 | Yb/Sr  | BACON-CLOCK-YB171   | BACON-CLOCK-SR87 | Yb  = +1, Sr = −1 |

## Per-Pair Decomposition

All values in units of 1e-36 (i.e. fractional² × 10⁻³⁶ ≡ (1e-18)²).

| Pair | Shared clock | σ_{c,i} (1e-18) | σ_{c,j} (1e-18) | sign_i × sign_j | Cov_c | ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| (ROW-001, ROW-002) | Al⁺ | 1.7 | 1.5 | +1 | +2.55 | +0.0540 |
| (ROW-001, ROW-003) | Yb  | 1.4 | 1.4 | −1 | −1.96 | −0.0489 |
| (ROW-002, ROW-003) | Sr  | 4.8 | 5.0 | +1 | +24.00 | +0.4412 |

No pair has more than one shared clock, so `Cov(i, j) = Cov_c(i, j)` for
each pair above.

## Reconstructed 3×3 Covariance Matrix

Row/column order: `[ACR-0001-ROW-001, ACR-0001-ROW-002, ACR-0001-ROW-003]`.

Covariance (units 1e-36):

| | ROW-001 | ROW-002 | ROW-003 |
| --- | ---: | ---: | ---: |
| **ROW-001** | 34.81 |  +2.55 | −1.96 |
| **ROW-002** |  +2.55 | 64.00 | +24.00 |
| **ROW-003** | −1.96 | +24.00 | 46.24 |

Correlation (dimensionless):

| | ROW-001 | ROW-002 | ROW-003 |
| --- | ---: | ---: | ---: |
| **ROW-001** | +1.0000 | +0.0540 | −0.0489 |
| **ROW-002** | +0.0540 | +1.0000 | +0.4412 |
| **ROW-003** | −0.0489 | +0.4412 | +1.0000 |

### Positive-semidefiniteness check

- Top-left 2×2 minor determinant: `2221.338` (1e-72 units) — positive.
- Full 3×3 determinant: `82178.32` (1e-108 units) — positive.
- Eigenvalues (1e-36 units): `[28.1211, 36.1981, 80.7308]` — all
  strictly positive.

Verdict: **PSD pass**. The reconstructed matrix is a valid covariance
matrix.

## Independent-Row Treatment Decision

Per the `TASK-0402` requirement ("check whether downstream benchmark
code would need to treat rows as correlated, partially correlated, or
independent-with-warning"):

| Pair | Correlation magnitude | Classification | Required benchmark treatment |
| --- | ---: | --- | --- |
| (ROW-002, ROW-003) | 0.4412 | `load_bearing_correlation` | **Correlated.** A benchmark that combines these two rows must use this approximation (or a stricter one) or document explicit independence as a known-underestimate limitation. |
| (ROW-001, ROW-002) | 0.0540 | `small_positive_correlation` | Partially correlated. Independence is an acceptable first-pass approximation if noted; using this matrix is strictly safer. |
| (ROW-001, ROW-003) | 0.0489 | `small_negative_correlation` | Partially correlated. Same guidance as above. |

The Sr-shared coupling between ROW-002 and ROW-003 is the load-bearing
item: Sr is the dominant systematic in both rows (4.8 and 5.0 in 1e-18
units), so treating these two as independent in a joint benchmark would
materially understate joint uncertainty.

## Excluded Contributions (Documented Lower Bound)

The off-diagonals capture only the shared-**clock** systematic coupling
that can be signed deterministically from the dataset. The following
physically-shared components are present in Table 1 of the source but
are intentionally excluded from the reconstructed off-diagonals because
their cross-row signs are not unambiguously recoverable from the
per-row decomposition:

| Component | Per-row magnitudes (1e-18) | Why excluded | Upper-bound off-diagonal contribution (1e-36) |
| --- | --- | --- | --- |
| Network link noise (σ_N) | 0.3 / 0.5 / 0.5 | Shared lab-wide effect; per-ratio sign convention not published. | (1,2) ≤ 0.15; (1,3) ≤ 0.15; (2,3) ≤ 0.25 |
| Geopotential redshift (σ_G) | 0.2 / 0.4 / 0.4 | Per-clock height components not published per-row; cannot sign cross-row. | (1,2) ≤ 0.08; (1,3) ≤ 0.08; (2,3) ≤ 0.16 |
| Statistical | per-row only | Daily measurements treated as independent campaigns in source. | 0 by construction. |

Adding the upper-bound network + geopotential contributions to each
off-diagonal would shift the correlations to approximately
`ρ(1,2) ≤ +0.060`, `ρ(1,3) ≤ −0.040` (still small in magnitude), and
`ρ(2,3) ≤ +0.449`. The load-bearing (2,3) entry is therefore robust to
the exclusion; the small (1,2) and (1,3) entries remain small.

**Consequence:** the off-diagonal magnitudes in the reconstructed matrix
are **lower bounds** on the true cross-row systematic coupling. A
benchmark consumer that wants a conservative upper bound on joint
uncertainty should add the network and geopotential contributions
(with their sign ambiguity flagged) as a sensitivity check.

## Hybrid-Diagonal Caveat

The diagonal entries are the Bayesian-model 1-σ totals squared (Table 1
last row), which already absorb within-row full-correlation across days
per Sec. 4.5 of the source. The off-diagonals, by contrast, are derived
from per-systematic shared-clock components only. The matrix therefore
mixes a Bayesian-total variance on the diagonal with a per-systematic
covariance on the off-diagonal — this is the documented construction
for the approximation, not a bug, but a future benchmark consumer who
wants a strictly Bayesian-consistent matrix must rebuild the diagonals
from per-systematic quadrature plus statistical (`sys² ⊕ stat²`) using
the dataset's `systematic_components_e_minus_18` and `statistical`
fields. The matrix in this approximation favours preserving published
per-row 1-σ values on the diagonal at the cost of internal mixed
construction; that trade-off is documented and reviewable.

## How To Reproduce

The matrix is fully deterministic from committed artifacts. The
reproduction recipe is recorded inside
`data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml`
under `how_to_reproduce`:

1. Open the Beloy direct-ratio dataset YAML.
2. For each unordered pair `(i, j)` and each clock `c` shared between
   them, look up `sigma_{c, i}`, `sigma_{c, j}` from
   `uncertainty.systematic_components_e_minus_18` and
   `sign_c(row)` from the ratio orientation.
3. Accumulate `Cov(i, j) += sign_c(i) * sign_c(j) * sigma_{c, i} * sigma_{c, j}`.
4. Place each row's `uncertainty.total**2` on the diagonal.
5. Verify positive-semidefiniteness via eigenvalue or leading-minor
   check.

A pure-Python recomputation following these steps reproduces the matrix
to the precision shown in this review.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for scientific claim;
  `SOURCE_DERIVED_APPROXIMATION_PSD` for the covariance-reconstruction
  workflow output (sandbox-only).
- **Canonical destination:**
  `docs/reviews/atomic-beloy-2021-cross-ratio-covariance-approximation.md`
  (this file) and
  `data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml`
  (machine-readable approximation; explicitly labelled source-derived,
  not a paper result).
- **Review tier:** `none` (no `RESULT/PRED` tier applies; data file is
  a covariance approximation, not a measurement value or a fit
  outcome).
- **Gate A status:** `not_attempted` (no `RESULT/PRED` artifact
  proposed).
- **Gate B status:** `not_attempted` (the approximation is single-source
  by construction; cross-source independent replay is the role of
  `TASK-0403` and any future replication task, not of this matrix).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations and blockers:** see the lower-bound and hybrid-diagonal
  caveats. The matrix unblocks Blocker 1 of `TASK-0401` only in the
  sense that a benchmark consumer now has a reviewable, PSD covariance
  approximation. Blocker 1's full resolution still depends on whether a
  future benchmark task accepts the lower-bound construction or
  requires a stricter Bayesian-consistent rebuild.

## Limitations

- **Lower-bound off-diagonals.** Only shared-clock systematic coupling
  with deterministic signs is included. Network and geopotential
  contributions are physically shared but cannot be deterministically
  signed from the published per-row decomposition; the upper-bound
  magnitudes are listed for sensitivity-check use.
- **Hybrid construction.** Diagonals use Bayesian-model totals;
  off-diagonals use per-systematic shared-clock products. A strictly
  consistent Bayesian rebuild would change the diagonals.
- **No statistical cross-row term.** Daily measurements are treated as
  independent campaigns per the source; a future analysis revisiting
  the measurement schedule may add a small statistical block.
- **No 3×3 paper-published matrix.** This is a source-derived
  approximation, not a published result; downstream wording must not
  present the matrix as a paper-validated covariance.
- **Sandbox-only.** Do not benchmark, fit drifts, derive constants
  constraints, or promote claims from this approximation without
  explicit maintainer-approved follow-up.

## Verdict

`SOURCE_DERIVED_APPROXIMATION_PSD` (sandbox-only). A reviewable 3×3
cross-ratio covariance approximation has been constructed from the
committed Beloy 2021 dataset under a documented shared-clock-only
methodology. The matrix is positive-semidefinite, and the load-bearing
(ROW-002, ROW-003) Sr-shared correlation (ρ ≈ +0.44) is now visible to
any future benchmark consumer. The off-diagonals are explicitly lower
bounds; lab-wide network and geopotential contributions are listed for
sensitivity-check use but intentionally excluded from the matrix
itself. No claim, prediction, result, or knowledge entry is created or
modified, and the dataset's sandbox-only promotion boundary is
preserved.
