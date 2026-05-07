"""Generate static result figures for APL v0.2 result pack.

Reads from canonical result artifacts; writes PNGs to docs/figures/.
Run from repository root: python3 scripts/generate_result_figures.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = REPO_ROOT / "docs" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

STYLE = {
    "valid": "#2ecc71",
    "invalid": "#e74c3c",
    "target": "#3498db",
    "neutral": "#95a5a6",
    "text": "#2c3e50",
    "bg": "#fafafa",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": STYLE["bg"],
    "axes.facecolor": STYLE["bg"],
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.facecolor": STYLE["bg"],
})


# ---------------------------------------------------------------------------
# Figure 1: Pendulum Gauntlet Leaderboard
# ---------------------------------------------------------------------------

def fig_pendulum_leaderboard() -> None:
    path = REPO_ROOT / "results" / "EXP-0001" / "RUN-0003" / "metrics.json"
    d = json.loads(path.read_text())
    lb = d["leaderboard_top10"]

    labels = [f"#{e['rank']} {e['formula']}" for e in lb]
    errors = [e["test_mean_relative_error"] * 100 for e in lb]
    verdicts = [e["verdict"] for e in lb]
    colors = [STYLE["valid"] if v == "VALID" else STYLE["invalid"] for v in verdicts]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(range(len(lb)), errors, color=colors, edgecolor="white", height=0.6)
    ax.set_yticks(range(len(lb)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Test mean relative error (%)")
    ax.set_title("Pendulum Gauntlet — Top-10 Candidate Leaderboard (EXP-0001 / RUN-0003)")

    valid_patch = mpatches.Patch(color=STYLE["valid"], label="VALID")
    invalid_patch = mpatches.Patch(color=STYLE["invalid"], label="FAIL")
    ax.legend(handles=[valid_patch, invalid_patch], loc="lower right")

    for bar, err in zip(bars, errors):
        ax.text(bar.get_width() + 0.000005, bar.get_y() + bar.get_height() / 2,
                f"{err:.4f}%", va="center", fontsize=7, color=STYLE["text"])

    ax.text(0.99, 0.02, "Source: results/EXP-0001/RUN-0003/metrics.json",
            transform=ax.transAxes, ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "pendulum-gauntlet-leaderboard.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 2: Pendulum Error Curve (best model vs exact, across amplitude range)
# ---------------------------------------------------------------------------

def fig_pendulum_error_curve() -> None:
    """Plot relative error of small-angle expansions vs exact elliptic integral."""
    from scipy.special import ellipk

    def elliptic_period_ratio(theta: float) -> float:
        k = math.sin(theta / 2)
        return (2 / math.pi) * ellipk(k**2)

    thetas = np.linspace(0.001, math.pi * 0.99, 500)
    exact = np.array([elliptic_period_ratio(float(t)) for t in thetas])

    # Standard small-angle expansion up to θ⁴
    approx_2 = 1 + thetas**2 / 16
    approx_4 = 1 + thetas**2 / 16 + 11 * thetas**4 / 3072
    err_2 = np.abs((approx_2 - exact) / exact) * 100
    err_4 = np.abs((approx_4 - exact) / exact) * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.semilogy(np.degrees(thetas), err_2, color="#e67e22", lw=1.5, label="θ² expansion")
    ax.semilogy(np.degrees(thetas), err_4, color=STYLE["valid"], lw=1.5, label="θ⁴ expansion (small-angle)")
    ax.axvline(90, color=STYLE["neutral"], ls="--", lw=1, label="θ = 90°")
    ax.axhline(0.1, color=STYLE["target"], ls=":", lw=1, label="0.1% threshold")
    ax.set_xlabel("Amplitude θ (degrees)")
    ax.set_ylabel("Relative error vs exact (%)")
    ax.set_title("Pendulum Period Approximation — Error vs Amplitude (EXP-0001)")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 180)
    ax.text(0.99, 0.02, "Source: results/EXP-0001/RUN-0003 | exact = elliptic integral",
            transform=ax.transAxes, ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "pendulum-error-curve.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 3: Pendulum Failure Modes
# ---------------------------------------------------------------------------

def fig_pendulum_failure_modes() -> None:
    path = REPO_ROOT / "results" / "EXP-0001" / "RUN-0003" / "metrics.json"
    d = json.loads(path.read_text())
    fm = d["failure_mode_summary"]

    labels = ["No failure\n(VALID)", "Moderate error", "High error"]
    sizes = [fm.get("none", 0), fm.get("moderate_error", 0), fm.get("high_error", 0)]
    colors = [STYLE["valid"], "#f39c12", STYLE["invalid"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    # Pie chart
    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, textprops={"fontsize": 9}
    )
    ax1.set_title("100 Candidates — Failure Mode Distribution")

    # Bar chart showing totals
    ax2.bar(labels, sizes, color=colors, edgecolor="white")
    ax2.set_ylabel("Number of candidates")
    ax2.set_title("Failure Mode Counts")
    for i, v in enumerate(sizes):
        ax2.text(i, v + 0.5, str(v), ha="center", fontsize=10, fontweight="bold")

    fig.suptitle("Pendulum Gauntlet — Failure Mode Analysis (EXP-0001 / RUN-0003)", fontsize=11)
    fig.text(0.99, 0.01, "Source: results/EXP-0001/RUN-0003/metrics.json",
             ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "pendulum-failure-modes.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 4: Koide Tau Holdout
# ---------------------------------------------------------------------------

def fig_koide_tau_holdout() -> None:
    path = REPO_ROOT / "results" / "EXP-0005" / "RUN-0005" / "metrics.json"
    d = json.loads(path.read_text())

    predicted = d["predicted_tau_mass_mev"]
    measured = d["measured_tau_mass_mev"]
    pred_unc = d["predicted_uncertainty_mev"]
    meas_unc = d["measured_uncertainty_mev"]
    z = d["z_score"]

    fig, ax = plt.subplots(figsize=(7, 4))

    # Measured band
    ax.axhspan(measured - meas_unc, measured + meas_unc, alpha=0.25,
               color=STYLE["valid"], label=f"Measured ± 1σ ({meas_unc:.2f} MeV)")
    ax.axhline(measured, color=STYLE["valid"], lw=2, label=f"Measured: {measured:.2f} MeV")

    # Predicted point + uncertainty
    ax.errorbar([0], [predicted], yerr=pred_unc * 1000,
                fmt="o", color=STYLE["target"], ms=10, capsize=6, lw=2,
                label=f"Predicted: {predicted:.4f} MeV")

    ax.set_xticks([])
    ax.set_ylabel("τ mass (MeV)")
    ax.set_title(f"Koide Tau Holdout Prediction vs Measurement\n"
                 f"Δm = {abs(predicted - measured):.4f} MeV  |  z = {z:.2f}σ  |  VALID")
    ax.legend(fontsize=9, loc="upper right")
    ax.set_ylim(measured - 3 * meas_unc, measured + 3 * meas_unc)
    ax.text(0.99, 0.02, "Source: results/EXP-0005/RUN-0005/metrics.json",
            transform=ax.transAxes, ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "koide-tau-holdout.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 5: Koide Q Deviation — All SM Families
# ---------------------------------------------------------------------------

def fig_koide_q_deviation() -> None:
    TARGET = 2 / 3

    # Data from canonical result metrics
    sectors = [
        ("Charged\nleptons\n(e,μ,τ)", 0.6666644634145, 5.08e-6, "VALID"),
        ("Neutrinos\nNH\n(ν₁,ν₂,ν₃)", 0.5839944574961611, 0.001169, "INVALID"),
        ("Down quarks\n(d,s,b)", 0.7314967575627492, 0.007331, "INVALID"),
        ("Up quarks\n(u,c,t)", 0.8489807776610612, 0.001145, "INVALID"),
    ]

    labels = [s[0] for s in sectors]
    q_vals = [s[1] for s in sectors]
    uncs = [s[2] for s in sectors]
    verdicts = [s[3] for s in sectors]
    colors = [STYLE["valid"] if v == "VALID" else STYLE["invalid"] for v in verdicts]

    fig, ax = plt.subplots(figsize=(9, 5))

    x = np.arange(len(sectors))
    ax.axhline(TARGET, color=STYLE["target"], lw=2, ls="--", zorder=1,
               label=f"Target Q = 2/3 = {TARGET:.4f}")
    ax.axhspan(TARGET - 0.02, TARGET + 0.02, alpha=0.08, color=STYLE["target"])

    bars = ax.bar(x, q_vals, color=colors, edgecolor="white", width=0.5, zorder=2)
    ax.errorbar(x, q_vals, yerr=[3 * u for u in uncs],
                fmt="none", color="black", capsize=5, lw=1.5, zorder=3,
                label="±3σ uncertainty")

    for i, (bar, q, v) in enumerate(zip(bars, q_vals, verdicts)):
        ax.text(i, q + 0.012, f"Q={q:.4f}", ha="center", fontsize=8, color=STYLE["text"])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Koide quantity Q")
    ax.set_ylim(0.45, 1.0)
    ax.set_title("Koide Formula Q vs Target 2/3 — All SM Fermion Families")
    valid_patch = mpatches.Patch(color=STYLE["valid"], label="VALID")
    invalid_patch = mpatches.Patch(color=STYLE["invalid"], label="INVALID")
    ax.legend(handles=[valid_patch, invalid_patch,
                        plt.Line2D([0], [0], color=STYLE["target"], ls="--", lw=2, label="Target Q = 2/3")],
              fontsize=8, loc="upper left")
    ax.text(0.99, 0.02, "Sources: EXP-0004/RUN-0004, EXP-0007/RUN-0001, EXP-0008/RUN-0001",
            transform=ax.transAxes, ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "koide-q-deviation.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 6: Koide Neutrino Falsification
# ---------------------------------------------------------------------------

def fig_koide_neutrino_falsification() -> None:
    path = REPO_ROOT / "results" / "EXP-0007" / "RUN-0001" / "metrics.json"
    d = json.loads(path.read_text())
    TARGET = d["koide_target"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for ax, key, label, color in [
        (axes[0], "NH", "Normal Hierarchy (NH)", "#8e44ad"),
        (axes[1], "IH", "Inverted Hierarchy (IH)", "#c0392b"),
    ]:
        data = d[key]
        q_max = data["q_max"]
        unc = data["q_max_uncertainty_1sigma"]
        gap_sigma = data["gap_in_sigma"]

        ax.axhline(TARGET, color=STYLE["target"], lw=2, ls="--",
                   label=f"Target Q = 2/3 = {TARGET:.4f}")
        ax.axhspan(TARGET - 3 * unc, TARGET + 3 * unc, alpha=0.1, color=STYLE["target"])

        ax.errorbar([0], [q_max], yerr=3 * unc,
                    fmt="o", color=color, ms=10, capsize=6, lw=2,
                    label=f"Q_max = {q_max:.4f}")

        # Gap annotation
        ax.annotate(
            "", xy=(0, TARGET), xytext=(0, q_max),
            arrowprops=dict(arrowstyle="<->", color="black", lw=1.5)
        )
        mid = (TARGET + q_max) / 2
        ax.text(0.15, mid, f"Gap\n{gap_sigma:.0f}σ", fontsize=9,
                color="black", va="center")

        ax.set_xticks([])
        ax.set_ylabel("Q value")
        ax.set_ylim(0.40, 0.80)
        ax.set_title(f"{label}\nQ_max = {q_max:.4f}  |  Gap = {gap_sigma:.0f}σ  |  INVALID")
        ax.legend(fontsize=8, loc="upper right")

    fig.suptitle("Koide Neutrino Falsification — Phase-Scan Q_max vs Target 2/3 (EXP-0007)", fontsize=11)
    fig.text(0.99, 0.01, "Source: results/EXP-0007/RUN-0001/metrics.json",
             ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "koide-neutrino-falsification.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 7: Koide Quark Cascade Gap
# ---------------------------------------------------------------------------

def fig_koide_quark_cascade_gap() -> None:
    path = REPO_ROOT / "results" / "EXP-0008" / "RUN-0001" / "metrics.json"
    d = json.loads(path.read_text())
    TARGET = d["target"]

    up = d["up_sector"]
    dn = d["down_sector"]

    fig, ax = plt.subplots(figsize=(9, 5))

    sectors = [
        ("Up sector\n(u, c, t)", up["q_standard"], up["q_standard_uncertainty"],
         up["q_phase_min"], up["q_phase_max"], up["q_standard_gap_sigma"]),
        ("Down sector\n(d, s, b)", dn["q_standard"], dn["q_standard_uncertainty"],
         dn["q_phase_min"], dn["q_phase_max"], dn["q_standard_gap_sigma"]),
    ]

    ax.axhline(TARGET, color=STYLE["target"], lw=2.5, ls="--",
               label=f"Target Q = 2/3 = {TARGET:.4f}", zorder=3)
    ax.axhspan(TARGET - 0.01, TARGET + 0.01, alpha=0.1, color=STYLE["target"])

    x_pos = [0.3, 0.7]
    for i, (label, q_std, q_unc, q_min, q_max, gap_sigma) in enumerate(sectors):
        x = x_pos[i]
        # Phase scan range
        ax.fill_between([x - 0.08, x + 0.08], q_min, q_max,
                        alpha=0.25, color=STYLE["invalid"],
                        label="Phase scan Q(δ) range" if i == 0 else "")
        # Standard Q point
        ax.errorbar([x], [q_std], yerr=3 * q_unc,
                    fmt="s", color=STYLE["invalid"], ms=10, capsize=6, lw=2,
                    label="Q_std ± 3σ" if i == 0 else "")
        ax.text(x, q_std + 0.025, f"Q={q_std:.4f}\n{gap_sigma}σ above 2/3",
                ha="center", fontsize=9, color=STYLE["text"])
        ax.text(x, q_min - 0.04, label, ha="center", fontsize=10, fontweight="bold")

    ax.set_xlim(0, 1)
    ax.set_ylim(0.5, 1.35)
    ax.set_xticks([])
    ax.set_ylabel("Koide quantity Q")
    ax.set_title("Koide Quark Cascade — Standard Q and Phase Scan Range vs Target 2/3 (EXP-0008)")
    ax.legend(fontsize=9, loc="upper right")
    ax.text(0.99, 0.02, "Source: results/EXP-0008/RUN-0001/metrics.json",
            transform=ax.transAxes, ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "koide-quark-cascade-gap.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Figure 8: Dimensional Validator Summary
# ---------------------------------------------------------------------------

def fig_dimensional_validator_summary() -> None:
    path = REPO_ROOT / "results" / "EXP-0006" / "RUN-0006" / "metrics.json"
    d = json.loads(path.read_text())

    total = d["total_items"]
    agree = d["agree"]
    valid_c = d["valid_count"]
    invalid_c = d["invalid_count"]
    agreement_pct = d["agreement_fraction"] * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Agreement pie
    wedges, texts, autotexts = ax1.pie(
        [agree, total - agree],
        labels=[f"Agree ({agree})", f"Disagree ({total - agree})"],
        colors=[STYLE["valid"], STYLE["invalid"]],
        autopct="%1.0f%%", startangle=90,
        textprops={"fontsize": 10}
    )
    ax1.set_title(f"Validator Agreement: {agreement_pct:.0f}% of {total} items")

    # Classification breakdown
    categories = ["VALID items", "INVALID items"]
    counts = [valid_c, invalid_c]
    bar_colors = [STYLE["valid"], STYLE["invalid"]]
    bars = ax2.bar(categories, counts, color=bar_colors, edgecolor="white", width=0.4)
    for bar, count in zip(bars, counts):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 str(count), ha="center", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Number of items")
    ax2.set_title("Challenge Set Classification (50 items)")
    ax2.set_ylim(0, max(counts) * 1.2)

    fig.suptitle("Dimensional Analysis Validator — Benchmark Summary (EXP-0006 / RUN-0006)", fontsize=11)
    fig.text(0.99, 0.01, "Source: results/EXP-0006/RUN-0006/metrics.json",
             ha="right", fontsize=7, color=STYLE["neutral"])
    fig.tight_layout()
    out = FIGURES_DIR / "dimensional-validator-summary.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating APL v0.2 static result figures...")
    fig_pendulum_leaderboard()
    fig_pendulum_error_curve()
    fig_pendulum_failure_modes()
    fig_koide_tau_holdout()
    fig_koide_q_deviation()
    fig_koide_neutrino_falsification()
    fig_koide_quark_cascade_gap()
    fig_dimensional_validator_summary()
    print(f"Done. All figures written to {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
