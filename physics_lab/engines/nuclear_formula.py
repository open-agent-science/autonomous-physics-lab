"""Nuclear binding energy formulas: Bethe-Weizsäcker + shell correction fitting."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import yaml
from scipy.optimize import least_squares

MAGIC_NUMBERS: tuple[int, ...] = (2, 8, 20, 28, 50, 82, 126)
MAGIC_N = np.array(list(MAGIC_NUMBERS), dtype=float)
MAGIC_Z = np.array([2, 8, 20, 28, 50, 82], dtype=float)

# Standard BW coefficients (MeV) from liquid-drop model literature
BW_INIT = {
    "a_V": 15.75,
    "a_S": 17.80,
    "a_C": 0.7103,
    "a_A": 23.69,
    "a_p": 11.18,
}


# ---------------------------------------------------------------------------
# Bethe-Weizsäcker formula
# ---------------------------------------------------------------------------


def pairing_delta(Z: int, N: int, A: int, a_p: float) -> float:
    if A % 2 == 1:
        return 0.0
    if Z % 2 == 0 and N % 2 == 0:
        return a_p / math.sqrt(A)
    return -a_p / math.sqrt(A)


def bw_binding_energy(Z: int, N: int, a_V: float, a_S: float, a_C: float, a_A: float, a_p: float) -> float:
    A = Z + N
    if A <= 0:
        return 0.0
    vol = a_V * A
    sur = -a_S * A ** (2 / 3)
    cou = -a_C * Z * (Z - 1) / A ** (1 / 3)
    asy = -a_A * (N - Z) ** 2 / A
    pair = pairing_delta(Z, N, A, a_p)
    return vol + sur + cou + asy + pair


def magic_distance(x: int) -> int:
    return min(abs(x - m) for m in MAGIC_NUMBERS)


# ---------------------------------------------------------------------------
# Shell correction formula families
# All funcs take (N_raw, Z_raw, *params) -> ndarray
# ---------------------------------------------------------------------------

ShellFunc = Callable[..., np.ndarray]


def _dN(N_raw: np.ndarray) -> np.ndarray:
    """Distance to nearest magic neutron number."""
    return np.min(np.abs(N_raw[:, None] - MAGIC_N[None, :]), axis=1)


def _dZ(Z_raw: np.ndarray) -> np.ndarray:
    """Distance to nearest magic proton number."""
    return np.min(np.abs(Z_raw[:, None] - MAGIC_N[None, :]), axis=1)


def _gauss(d: np.ndarray, a: float, sigma: float) -> np.ndarray:
    return a * np.exp(-(d**2) / (sigma**2 + 1e-12))


def _lorentz(d: np.ndarray, a: float, sigma: float) -> np.ndarray:
    return a / (1.0 + (d / (sigma + 1e-6)) ** 2)


def _exp_decay(d: np.ndarray, a: float, tau: float) -> np.ndarray:
    return a * np.exp(-d / (tau + 1e-6))


@dataclass
class FormulaCandidate:
    name: str
    n_params: int
    func: Callable[..., np.ndarray]
    p0: list[float]
    bounds: tuple[list[float], list[float]]


def _make_candidates() -> list[FormulaCandidate]:
    candidates = []

    # 1. Gaussian in d_N only
    candidates.append(FormulaCandidate(
        name="gauss_N",
        n_params=2,
        func=lambda N, Z, a, sigma: _gauss(_dN(N), a, sigma),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 2. Gaussian in d_Z only
    candidates.append(FormulaCandidate(
        name="gauss_Z",
        n_params=2,
        func=lambda N, Z, a, sigma: _gauss(_dZ(Z), a, sigma),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 3. Gaussian sum (N + Z), shared sigma
    candidates.append(FormulaCandidate(
        name="gauss_NZ_sum_shared_sigma",
        n_params=3,
        func=lambda N, Z, a, b, sigma: _gauss(_dN(N), a, sigma) + _gauss(_dZ(Z), b, sigma),
        p0=[2.0, 2.0, 4.0],
        bounds=([0, 0, 0.1], [30, 30, 30]),
    ))

    # 4. Gaussian sum (N + Z), independent sigma
    candidates.append(FormulaCandidate(
        name="gauss_NZ_sum_indep_sigma",
        n_params=4,
        func=lambda N, Z, a, b, sN, sZ: _gauss(_dN(N), a, sN) + _gauss(_dZ(Z), b, sZ),
        p0=[2.0, 2.0, 4.0, 4.0],
        bounds=([0, 0, 0.1, 0.1], [30, 30, 30, 30]),
    ))

    # 5. Gaussian min(d_N, d_Z)
    candidates.append(FormulaCandidate(
        name="gauss_min_NZ",
        n_params=2,
        func=lambda N, Z, a, sigma: _gauss(np.minimum(_dN(N), _dZ(Z)), a, sigma),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 6. Gaussian product (doubly-magic term)
    candidates.append(FormulaCandidate(
        name="gauss_NZ_product",
        n_params=2,
        func=lambda N, Z, a, sigma: a * np.exp(-(_dN(N)**2 + _dZ(Z)**2) / (sigma**2 + 1e-12)),
        p0=[5.0, 4.0],
        bounds=([0, 0.1], [50, 30]),
    ))

    # 7. Lorentzian in d_N only
    candidates.append(FormulaCandidate(
        name="lorentz_N",
        n_params=2,
        func=lambda N, Z, a, sigma: _lorentz(_dN(N), a, sigma),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 8. Lorentzian in d_Z only
    candidates.append(FormulaCandidate(
        name="lorentz_Z",
        n_params=2,
        func=lambda N, Z, a, sigma: _lorentz(_dZ(Z), a, sigma),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 9. Lorentzian sum, shared width
    candidates.append(FormulaCandidate(
        name="lorentz_NZ_sum_shared",
        n_params=3,
        func=lambda N, Z, a, b, sigma: _lorentz(_dN(N), a, sigma) + _lorentz(_dZ(Z), b, sigma),
        p0=[2.0, 2.0, 4.0],
        bounds=([0, 0, 0.1], [30, 30, 30]),
    ))

    # 10. Lorentzian sum, independent widths
    candidates.append(FormulaCandidate(
        name="lorentz_NZ_sum_indep",
        n_params=4,
        func=lambda N, Z, a, b, sN, sZ: _lorentz(_dN(N), a, sN) + _lorentz(_dZ(Z), b, sZ),
        p0=[2.0, 2.0, 4.0, 4.0],
        bounds=([0, 0, 0.1, 0.1], [30, 30, 30, 30]),
    ))

    # 11. Lorentzian min(d_N, d_Z)
    candidates.append(FormulaCandidate(
        name="lorentz_min_NZ",
        n_params=2,
        func=lambda N, Z, a, sigma: _lorentz(np.minimum(_dN(N), _dZ(Z)), a, sigma),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 12. Exponential in d_N only
    candidates.append(FormulaCandidate(
        name="exp_N",
        n_params=2,
        func=lambda N, Z, a, tau: _exp_decay(_dN(N), a, tau),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 13. Exponential in d_Z only
    candidates.append(FormulaCandidate(
        name="exp_Z",
        n_params=2,
        func=lambda N, Z, a, tau: _exp_decay(_dZ(Z), a, tau),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 14. Exponential sum, shared τ
    candidates.append(FormulaCandidate(
        name="exp_NZ_sum_shared",
        n_params=3,
        func=lambda N, Z, a, b, tau: _exp_decay(_dN(N), a, tau) + _exp_decay(_dZ(Z), b, tau),
        p0=[2.0, 2.0, 4.0],
        bounds=([0, 0, 0.1], [30, 30, 30]),
    ))

    # 15. Exponential sum, independent τ
    candidates.append(FormulaCandidate(
        name="exp_NZ_sum_indep",
        n_params=4,
        func=lambda N, Z, a, b, tN, tZ: _exp_decay(_dN(N), a, tN) + _exp_decay(_dZ(Z), b, tZ),
        p0=[2.0, 2.0, 4.0, 4.0],
        bounds=([0, 0, 0.1, 0.1], [30, 30, 30, 30]),
    ))

    # 16. Exponential min(d_N, d_Z)
    candidates.append(FormulaCandidate(
        name="exp_min_NZ",
        n_params=2,
        func=lambda N, Z, a, tau: _exp_decay(np.minimum(_dN(N), _dZ(Z)), a, tau),
        p0=[3.0, 4.0],
        bounds=([0, 0.1], [30, 30]),
    ))

    # 17. Power-law Lorentzian N
    candidates.append(FormulaCandidate(
        name="power_lorentz_N",
        n_params=3,
        func=lambda N, Z, a, sigma, p: a / (1 + (_dN(N) / (sigma + 1e-6)) ** p),
        p0=[3.0, 4.0, 2.0],
        bounds=([0, 0.1, 0.5], [30, 30, 6]),
    ))

    # 18. Power-law Lorentzian Z
    candidates.append(FormulaCandidate(
        name="power_lorentz_Z",
        n_params=3,
        func=lambda N, Z, a, sigma, p: a / (1 + (_dZ(Z) / (sigma + 1e-6)) ** p),
        p0=[3.0, 4.0, 2.0],
        bounds=([0, 0.1, 0.5], [30, 30, 6]),
    ))

    # 19. Power-law Lorentzian sum
    candidates.append(FormulaCandidate(
        name="power_lorentz_NZ_sum",
        n_params=4,
        func=lambda N, Z, a, b, sigma, p: (
            a / (1 + (_dN(N) / (sigma + 1e-6)) ** p) + b / (1 + (_dZ(Z) / (sigma + 1e-6)) ** p)
        ),
        p0=[2.0, 2.0, 4.0, 2.0],
        bounds=([0, 0, 0.1, 0.5], [30, 30, 30, 6]),
    ))

    # 20. Linear ramp (clipped): max(0, a - b*d_N)
    candidates.append(FormulaCandidate(
        name="linear_ramp_N",
        n_params=2,
        func=lambda N, Z, a, b: np.maximum(0.0, a - b * _dN(N)),
        p0=[4.0, 0.5],
        bounds=([0, 0.01], [30, 10]),
    ))

    # 21. Linear ramp sum N + Z
    candidates.append(FormulaCandidate(
        name="linear_ramp_NZ",
        n_params=3,
        func=lambda N, Z, a, b, c: np.maximum(0.0, a - b * _dN(N) - c * _dZ(Z)),
        p0=[4.0, 0.3, 0.3],
        bounds=([0, 0.01, 0.01], [30, 10, 10]),
    ))

    # 22. Gaussian + Lorentzian (N and Z mixed)
    candidates.append(FormulaCandidate(
        name="gauss_N_lorentz_Z",
        n_params=4,
        func=lambda N, Z, a, sG, b, sL: _gauss(_dN(N), a, sG) + _lorentz(_dZ(Z), b, sL),
        p0=[2.0, 4.0, 2.0, 4.0],
        bounds=([0, 0.1, 0, 0.1], [30, 30, 30, 30]),
    ))

    # 23. Gaussian N + exponential Z
    candidates.append(FormulaCandidate(
        name="gauss_N_exp_Z",
        n_params=4,
        func=lambda N, Z, a, sG, b, tZ: _gauss(_dN(N), a, sG) + _exp_decay(_dZ(Z), b, tZ),
        p0=[2.0, 4.0, 2.0, 4.0],
        bounds=([0, 0.1, 0, 0.1], [30, 30, 30, 30]),
    ))

    # 24. Doubly-magic enhancement: Gaussian product + Gaussian sum
    candidates.append(FormulaCandidate(
        name="doubly_magic_plus_sum",
        n_params=5,
        func=lambda N, Z, aD, sD, aN, aZ, sS: (
            aD * np.exp(-(_dN(N)**2 + _dZ(Z)**2) / (sD**2 + 1e-12))
            + _gauss(_dN(N), aN, sS) + _gauss(_dZ(Z), aZ, sS)
        ),
        p0=[3.0, 3.0, 1.5, 1.5, 4.0],
        bounds=([0, 0.1, 0, 0, 0.1], [30, 20, 20, 20, 30]),
    ))

    # 25. Multi-magic Gaussian N: separate amplitude per magic neutron number + shared width
    # Allows each magic-N closure to have its own correction magnitude and sign
    def _multi_gauss_N(N_raw: np.ndarray, Z_raw: np.ndarray,
                       a2: float, a8: float, a20: float, a28: float,
                       a50: float, a82: float, a126: float,
                       sigma: float) -> np.ndarray:
        amps = np.array([a2, a8, a20, a28, a50, a82, a126])
        result = np.zeros(len(N_raw))
        for k, m in enumerate(MAGIC_N):
            result += amps[k] * np.exp(-((N_raw - m) ** 2) / (sigma**2 + 1e-12))
        return result

    candidates.append(FormulaCandidate(
        name="multi_gauss_N_shared_sigma",
        n_params=8,
        func=_multi_gauss_N,
        p0=[1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0],
        bounds=([-20, -20, -20, -20, -20, -20, -20, 0.1], [20, 20, 20, 20, 20, 20, 20, 30]),
    ))

    # 26. Multi-magic Gaussian N+Z: separate amplitudes for each magic number in both N and Z
    def _multi_gauss_NZ(N_raw: np.ndarray, Z_raw: np.ndarray,
                        aN2: float, aN8: float, aN20: float, aN28: float,
                        aN50: float, aN82: float, aN126: float,
                        aZ2: float, aZ8: float, aZ20: float, aZ28: float,
                        aZ50: float, aZ82: float,
                        sigma: float) -> np.ndarray:
        aN = np.array([aN2, aN8, aN20, aN28, aN50, aN82, aN126])
        aZ = np.array([aZ2, aZ8, aZ20, aZ28, aZ50, aZ82])
        result = np.zeros(len(N_raw))
        for k, m in enumerate(MAGIC_N):
            result += aN[k] * np.exp(-((N_raw - m) ** 2) / (sigma**2 + 1e-12))
        for k, m in enumerate(MAGIC_Z):
            result += aZ[k] * np.exp(-((Z_raw - m) ** 2) / (sigma**2 + 1e-12))
        return result

    candidates.append(FormulaCandidate(
        name="multi_gauss_NZ_shared_sigma",
        n_params=14,
        func=_multi_gauss_NZ,
        p0=[1.0] * 13 + [4.0],
        bounds=([-20] * 13 + [0.1], [20] * 13 + [30]),
    ))

    return candidates


ALL_CANDIDATES = _make_candidates()


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------


def load_binding_energy_dataset(path: Any) -> list[dict]:
    data = yaml.safe_load(open(path, encoding="utf-8").read())
    return data["nuclides"]


# ---------------------------------------------------------------------------
# Fitting pipeline
# ---------------------------------------------------------------------------


@dataclass
class FitResult:
    name: str
    params: list[float]
    rms_train: float
    rms_test: float
    rms_bw_train: float
    rms_bw_test: float
    improvement_train: float
    improvement_test: float
    converged: bool
    bw_coeffs: dict[str, float]


@dataclass
class NuclearShellCorrectionResult:
    bw_rms_train: float
    bw_rms_test: float
    candidates: list[FitResult]
    best: FitResult
    bw_coeffs: dict[str, float]
    n_train: int
    n_test: int
    n_total: int
    magic_numbers: list[int] = field(default_factory=lambda: list(MAGIC_NUMBERS))


def _bw_coefficients() -> dict[str, float]:
    """Return standard BW liquid-drop coefficients (not refitted).

    Using literature values keeps the shell correction physically meaningful —
    refitting BW on a magic-number-enriched dataset would absorb part of the
    shell signal into the liquid-drop parameters.
    """
    return dict(BW_INIT)


def _compute_residuals(nuclides: list[dict], bw_coeffs: dict[str, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (residuals, N_raw, Z_raw) arrays for the given nuclide list."""
    N_raw = np.array([int(n["N"]) for n in nuclides], dtype=float)
    Z_raw = np.array([int(n["Z"]) for n in nuclides], dtype=float)
    residuals = np.array([
        float(n["B_exp"]) - bw_binding_energy(
            int(n["Z"]), int(n["N"]),
            bw_coeffs["a_V"], bw_coeffs["a_S"], bw_coeffs["a_C"],
            bw_coeffs["a_A"], bw_coeffs["a_p"],
        )
        for n in nuclides
    ])
    return residuals, N_raw, Z_raw


def _fit_candidate(
    candidate: FormulaCandidate,
    N_train: np.ndarray,
    Z_train: np.ndarray,
    res_train: np.ndarray,
) -> tuple[list[float], bool]:
    """Fit a shell correction candidate to training residuals."""
    def obj(params: np.ndarray) -> np.ndarray:
        pred = candidate.func(N_train, Z_train, *params)
        return res_train - pred

    try:
        result = least_squares(
            obj,
            x0=candidate.p0,
            bounds=candidate.bounds,
            max_nfev=10000,
        )
        return list(result.x), result.cost < 1e8
    except Exception:
        return list(candidate.p0), False


def run_nuclear_shell_correction(dataset_path: Any) -> NuclearShellCorrectionResult:
    """Full pipeline: load data, apply standard BW, fit 26 shell correction candidates."""
    nuclides = load_binding_energy_dataset(dataset_path)

    # 80/20 train/test split by index (every 5th nuclide to test)
    test_indices = set(range(4, len(nuclides), 5))
    train = [n for i, n in enumerate(nuclides) if i not in test_indices]
    test = [n for i, n in enumerate(nuclides) if i in test_indices]

    bw_coeffs = _bw_coefficients()

    res_train, N_train, Z_train = _compute_residuals(train, bw_coeffs)
    res_test, N_test, Z_test = _compute_residuals(test, bw_coeffs)

    rms_bw_train = float(np.sqrt(np.mean(res_train**2)))
    rms_bw_test = float(np.sqrt(np.mean(res_test**2)))

    fit_results: list[FitResult] = []
    for cand in ALL_CANDIDATES:
        params, converged = _fit_candidate(cand, N_train, Z_train, res_train)

        pred_train = cand.func(N_train, Z_train, *params)
        pred_test = cand.func(N_test, Z_test, *params)

        rms_train = float(np.sqrt(np.mean((res_train - pred_train) ** 2)))
        rms_test = float(np.sqrt(np.mean((res_test - pred_test) ** 2)))

        improvement_train = (rms_bw_train - rms_train) / rms_bw_train if rms_bw_train > 0 else 0.0
        improvement_test = (rms_bw_test - rms_test) / rms_bw_test if rms_bw_test > 0 else 0.0

        fit_results.append(FitResult(
            name=cand.name,
            params=params,
            rms_train=rms_train,
            rms_test=rms_test,
            rms_bw_train=rms_bw_train,
            rms_bw_test=rms_bw_test,
            improvement_train=improvement_train,
            improvement_test=improvement_test,
            converged=converged,
            bw_coeffs=bw_coeffs,
        ))

    fit_results.sort(key=lambda r: r.rms_test)
    best = fit_results[0]

    return NuclearShellCorrectionResult(
        bw_rms_train=rms_bw_train,
        bw_rms_test=rms_bw_test,
        candidates=fit_results,
        best=best,
        bw_coeffs=bw_coeffs,
        n_train=len(train),
        n_test=len(test),
        n_total=len(nuclides),
    )
