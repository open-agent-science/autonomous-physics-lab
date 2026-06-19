# Textbook Wien Displacement — FIRAS Source-Artifact Curation (TASK-0793)

**Task:** `TASK-0793` · **Campaign:** `textbook-formula-audit` ·
**Mode:** source-curation only (planning).
**Verdict:** `SOURCE_ROUTE_OPEN_PENDING_FETCH_AND_PIN` — the NASA LAMBDA COBE/FIRAS
monopole spectrum is an open, reusable, blackbody-grade route for a future
wavelength-domain Wien-peak audit. It is **not a no-go**, but it is **not yet pinned**:
a future fetch step must commit the exact product file + SHA-256, and the audit must
resolve the frequency-vs-wavelength spectral-axis convention before any metric is run.
No data was fetched, no metric was run, and no `RESULT`/`PRED`/`CLAIM`/`KNOW` artifact is
created here.

Builds on the Wien source/baseline plan (`docs/reviews/textbook-wien-displacement-source-baseline-plan.md`, TASK-0492) and the slice selection (`docs/reviews/textbook-next-formula-source-baseline-slice.md`, TASK-0783). It does not restate the formula convention; it pins the empirical FIRAS route those notes deferred.

## Audit question (scoped, for a future metric task — not run here)

> On the pinned COBE/FIRAS CMB monopole spectrum, does the **wavelength-domain** peak of
> the spectral radiance agree with `lambda_peak = b / T` (CODATA `b`, FIRAS `T`) within a
> pre-registered tolerance, after an explicit and declared spectral-axis conversion?

Not a claim that Wien displacement is universally validated or falsified; not a blackbody-universality, cosmology, or discovery statement.

## Source route

- **Product:** COBE/FIRAS CMB monopole (absolute) spectrum — the calibrated CMB
  brightness vs spectral axis, with per-point uncertainty and residual.
- **Archive:** NASA LAMBDA (Legacy Archive for Microwave Background Data Analysis),
  `lambda.gsfc.nasa.gov` (COBE/FIRAS products). Exact product URL + retrieval timestamp
  to be pinned at fetch time.
- **Primary citations:** Fixsen et al. 1996, ApJ 473, 576 (FIRAS CMB spectrum);
  Fixsen 2009, ApJ 707, 916 (`T = 2.7255 ± 0.0006 K`); Mather et al. 1999. These must be
  attributed in any committed artifact.

## License / reuse status

- COBE/FIRAS data products distributed by NASA LAMBDA are **U.S. Government works, not
  subject to domestic copyright**, and are freely reusable with attribution per NASA's
  data-use guidance. This is materially cleaner than the DEBCat route (which required an
  explicit redistribution grant): the FIRAS table is **Route 1 eligible** — the full
  value-bearing table may be committed with citation, no permission request needed.
- Action for the future fetch task: still record the exact product URL, retrieval
  timestamp, and a `DATA_LICENSES.yaml` entry (`public_domain_us_gov` / NASA attribution)
  before committing rows.

## Checksum policy (no fetch performed here)

- A future fetch task pins the exact FIRAS product file by **SHA-256**, stores it under
  `data/textbook_formula_audit/wien_firas/`, and records the checksum + retrieval
  timestamp in a source manifest. The replay path reads only the committed pinned file —
  **no live fetch at audit time** (same Route-1 discipline as MD-0002).
- This curation task deliberately records the *policy*, not a checksum, because no bytes
  were retrieved.

## Row schema (to confirm against the pinned file)

| field | unit | role |
| --- | --- | --- |
| `spectral_axis` | wavenumber `cm^-1` (FIRAS native) | independent variable |
| `monopole_intensity` | `MJy/sr` (spectral radiance per unit frequency, `B_nu`) | measured |
| `uncertainty` | `kJy/sr` | per-point sigma |
| `residual` | `kJy/sr` | (CMB − model) diagnostic, not promoted |

FIRAS reports the spectrum on a **frequency / wavenumber** axis (`B_nu` vs `cm^-1`), i.e.
the **frequency domain**. The exact column order/units must be confirmed against the
pinned product header at fetch time.

## Baseline contract (the spectral-axis crux)

The Wien plan (TASK-0492) is the **wavelength-domain** peak `lambda_peak = b / T`, and it
explicitly rejects frequency-domain peaks "unless the row includes a wavelength-domain
spectral-radiance peak". FIRAS is frequency-domain, so the audit **must** declare one of:

1. **Convert** `B_nu(nu)` → `B_lambda(lambda)` via the exact Planck Jacobian
   `B_lambda = B_nu * nu^2 / c` (equivalently `c / lambda^2`), then locate the
   wavelength-domain peak. This is deterministic and is the recommended contract.
2. Or switch scope to the **frequency-domain** Wien constant (`nu_peak / T ≈ 5.879e10 Hz/K`),
   which is a *different* relation — out of scope for the wavelength-domain TASK-0492 plan.

The peaks are genuinely different quantities (Wien-peak non-invariance):

- Wavelength-domain peak for `T = 2.7255 K`: `lambda_peak = b/T ≈ 1.063 mm` (≈ `9.4 cm^-1`).
- Frequency-domain peak: `nu_peak ≈ 160 GHz` (≈ `5.3 cm^-1`).

Both fall **inside** the nominal FIRAS coverage window (≈ `2–21 cm^-1`) with margin —
to be confirmed exactly against the pinned file. Constant convention is unchanged:
`b = 2.897771955e-3 m K` (CODATA 2022, NIST), SI internally.

## Required negative/controls (declared now; run only in a future metric task)

1. **Wrong-temperature control:** predict the peak for a deliberately offset `T`
   (e.g. `T ± 10%`); the audit must reject it (peak must track the FIRAS `T`, not an
   arbitrary one).
2. **Domain-consistency control:** the wavelength-domain and frequency-domain peaks must
   differ by the known Planck factor; a spectrum (or a mis-applied Jacobian) that collapses
   them is non-blackbody / mis-converted and must fail.
3. **Circularity caveat (mandatory framing):** FIRAS `T` is itself obtained by fitting a
   Planck spectrum to the same data, so a raw "peak vs `b/T`" comparison is partly a
   **self-consistency** check, not independent validation. A future metric task must either
   use an independently determined `T` or frame the outcome explicitly as a
   blackbody-self-consistency check — never as universal validation of Wien's law.

## Output routing

- Source-readiness impact only. Gate A / Gate B **not attempted**.
- Claim impact: none. Knowledge impact: none. No metrics, fit, or peak-finding run.
- Next step (separate task, needs its own authorization): fetch + SHA-256-pin the FIRAS
  monopole product, add the `DATA_LICENSES.yaml` entry and source manifest, and only then
  a metric task implementing the declared `B_nu→B_lambda` conversion + the three controls.

## Limitations / no-claim

Planning/source-curation note only. No COBE/FIRAS bytes were retrieved, no checksum was
computed, no spectrum was fit, and no Wien verdict is asserted. Not a blackbody-universality,
cosmology, CMB-physics, or discovery claim.
