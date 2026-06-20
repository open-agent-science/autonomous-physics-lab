#!/usr/bin/env python3
"""
Deterministic figure digitizer for SI Figure S2b of:
  Almeida et al., "Size-Dependent Optical Properties of InP Colloidal Quantum
  Dots," Nano Letters 2023, doi:10.1021/acs.nanolett.3c02630, CC-BY 4.0.

Goal: extract the per-sample mean EDGE LENGTH (Angstrom and nm) for the six
InP samples from the panel-b TEM edge-length-distribution histograms
(lambda1s = 460, 480, 510, 550, 580, 620 nm).

Method (robust, validated against independently-extracted Fig-2b values):
  GRAY-HISTOGRAM weighted centroid. For each x-column inside a panel box the
  bar height equals the number of medium-gray pixels in that column (the bars
  are solid gray fills). The edge-length center is the column-height-weighted
  centroid sum(L_i * h_i)/sum(h_i). The thin black "Edge length distribution"
  and red "Volume distribution" curves overlay the bars but remove only a few
  pixels per column (negligible vs bar heights of ~100-250 px), so the gray
  centroid is insensitive to them. The x=0 y-axis column is masked out.

Calibration: the x-axis is 0..60 Angstrom. Major tick marks (printed below the
baseline, aligned with the "0 10 20 30 40 50 60" labels) are detected and a
line is fit, giving px-per-Angstrom and the x-pixel of 0 A. Tick spacing is
validated to be even (~78 px / 10 A) before the calibration is trusted.

Panel geometry is found from first principles (no magic y-values trusted
blindly): the y-axis (x=0) column and the per-panel box borders are detected as
long black runs, and the six boxes are read off as (top, baseline) pairs.

Determinism: pure function of the 300-DPI PNG render of page 9. No randomness.
Inputs that are environment-specific (the PDF path) only affect an optional
re-render guarded behind --render.

Usage:
  python3 extract_s2b.py            # uses /tmp/s2b_out/si_s2-09.png (or the
                                    # pre-existing /tmp/almeida_si_s2-09.png)
Outputs (in the script's directory):
  s2b_centers.csv, s2b_overlay.png
"""
import os
import sys
import csv
import numpy as np
from PIL import Image, ImageDraw

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
OUTDIR = os.path.dirname(os.path.abspath(__file__))
RENDER_CANDIDATES = [
    os.path.join(OUTDIR, "si_s2-09.png"),
    "/tmp/s2b_out/si_s2-09.png",
    "/tmp/almeida_si_s2-09.png",
]
# Maintainer-supplied SHA-pinned SI PDF (not vendored); place locally or pass
# its path. Only used with --render.
PDF_PATH = os.environ.get("ALMEIDA_SI_PDF", "nl3c02630_si_001.pdf")
PDF_SHA256 = "2d0080214d9f7116561cbd80659d40463f868b57ca211179f5d854d12ad265ee"

# E1s (eV) per sample, supplied with the task (1S exciton energy).
E1S = {460: 2.695, 480: 2.583, 510: 2.431, 550: 2.254, 580: 2.138, 620: 2.000}

# Independently-extracted Fig-2b edge lengths (Angstrom) used ONLY as a
# cross-check of method+calibration (not used in the extraction itself).
FIG2B_TARGET_A = {460: 15.0, 480: 19.9, 510: 25.4, 550: 27.6, 580: 31.3}

# Gray-bar color mask. Bars are medium gray: all channels close together,
# brightness ~105..215. Curves/axis are darker (black) or red (R>>G,B).
GRAY_SPREAD_MAX = 28     # max(R,G,B) - min(R,G,B)
GRAY_BRIGHT_MIN = 105
GRAY_BRIGHT_MAX = 215
# Dark (axis / borders / ticks / curve) mask.
DARK_MAX = 95
YAXIS_MASK_PX = 16       # ignore columns within this many px of the x=0 axis
PLOT_X_LO, PLOT_X_HI = 852, 1313  # inside the box, away from the side borders

EXPECT_PX_PER_10A = 77.8   # nominal, used only to validate detected tick spacing
LAMBDAS = [460, 480, 510, 550, 580, 620]


# ----------------------------------------------------------------------------
# Image / mask helpers
# ----------------------------------------------------------------------------
def load_image():
    for p in RENDER_CANDIDATES:
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            return p, np.asarray(im).astype(int)
    raise FileNotFoundError(
        "No render found. Run with --render or create one with:\n"
        f'  pdftoppm -f 9 -l 9 -r 300 -png "{PDF_PATH}" {OUTDIR}/si_s2'
    )


def masks(im):
    mx = im.max(2)
    mn = im.min(2)
    spread = mx - mn
    R, G, B = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    is_gray = (spread < GRAY_SPREAD_MAX) & (mx >= GRAY_BRIGHT_MIN) & (mx <= GRAY_BRIGHT_MAX)
    is_dark = (mx < DARK_MAX) & (mn < DARK_MAX)
    is_red = (R > 140) & (R - np.maximum(G, B) > 30)
    return is_gray, is_dark, is_red


# ----------------------------------------------------------------------------
# Geometry detection (panel boxes + y-axis), from first principles
# ----------------------------------------------------------------------------
def detect_yaxis_x(is_dark):
    """The x=0 vertical axis: the column (in 840..860) with the most dark px."""
    band = is_dark[200:2710, 840:860]
    colsum = band.sum(0)
    x = 840 + int(np.argmax(colsum))
    return x


def detect_boxes(is_dark, yaxis_x):
    """Return six (top, baseline) y-pairs.

    The left edge of every panel box is the x=0 axis, drawn as a tall dark run.
    Splitting that column into contiguous vertical segments yields one segment
    per box. The vertical segment's TOP is accurate, but its BOTTOM can overshoot
    the baseline by a few px, so the bottom is SNAPPED to the nearest strong
    horizontal line (the true baseline) detected across the plot width."""
    # strong horizontal lines (box baselines) across the plot width
    rowsum = is_dark[:, PLOT_X_LO:PLOT_X_HI].sum(1)
    hlines = np.array([y for y in range(200, 2760) if rowsum[y] > 300])

    def snap(y, win=15):
        cand = hlines[np.abs(hlines - y) <= win]
        return int(cand[np.argmin(np.abs(cand - y))]) if len(cand) else int(y)

    col = (is_dark[:, yaxis_x - 1] | is_dark[:, yaxis_x] | is_dark[:, yaxis_x + 1])
    ys = np.where(col)[0]
    ys = ys[(ys > 200) & (ys < 2760)]
    segs = []
    start = prev = ys[0]
    for y in ys[1:]:
        if y - prev > 8:           # gap between two boxes
            if prev - start > 200:  # a real box is ~356 px tall
                segs.append((int(start), snap(prev)))
            start = y
        prev = y
    if prev - start > 200:
        segs.append((int(start), snap(prev)))
    if len(segs) != 6:
        raise RuntimeError(f"Expected 6 panel boxes, found {len(segs)}: {segs}")
    return segs  # top-to-bottom == 460,480,510,550,580,620


# ----------------------------------------------------------------------------
# X calibration from tick marks
# ----------------------------------------------------------------------------
def detect_ticks(is_dark, baseline_y, yaxis_x):
    """Major-tick x-positions for 0..60, from the short marks just below the
    baseline that align with the axis number labels. Returns sorted x list."""
    band = is_dark[baseline_y + 1:baseline_y + 9, 800:1360]
    cs = band.sum(0)
    xs = np.where(cs >= 4)[0] + 800
    if len(xs) == 0:
        return []
    groups, members, prev = [], [xs[0]], xs[0]
    for x in xs[1:]:
        if x - prev > 10:
            groups.append(int(round(np.mean(members))))
            members = []
        members.append(x)
        prev = x
    groups.append(int(round(np.mean(members))))
    return groups


def calibrate_x(is_dark, baselines, yaxis_x):
    """Fit x_px = slope * L_Angstrom + x0 using major ticks pooled across all
    panels. Tick spacing is validated to be ~even before being trusted."""
    anchor_x = {}  # Angstrom value -> list of detected pixel positions
    for by in baselines:
        ticks = detect_ticks(is_dark, by, yaxis_x)
        # keep ticks that fall on the 0..60 grid (multiples of ~78 px from yaxis)
        for t in ticks:
            val = round((t - yaxis_x) / EXPECT_PX_PER_10A) * 10
            if 0 <= val <= 60 and abs((t - yaxis_x) - val / 10.0 * EXPECT_PX_PER_10A) < 12:
                anchor_x.setdefault(val, []).append(t)
    vals = sorted(anchor_x)
    xs = np.array([np.mean(anchor_x[v]) for v in vals], float)
    vals = np.array(vals, float)
    # validate even spacing of the recovered anchors
    if len(vals) >= 3:
        dx_per_A = np.diff(xs) / np.diff(vals)
        if dx_per_A.std() > 0.5:
            raise RuntimeError(f"Tick spacing not even: {dx_per_A}")
    A = np.vstack([vals, np.ones_like(vals)]).T
    (slope, x0), *_ = np.linalg.lstsq(A, xs, rcond=None)
    resid = xs - (slope * vals + x0)
    return float(slope), float(x0), vals.astype(int).tolist(), xs.tolist(), float(np.abs(resid).max())


# ----------------------------------------------------------------------------
# Per-panel extraction
# ----------------------------------------------------------------------------
def panel_profile(is_gray, top, baseline, yaxis_x):
    """Column gray-pixel counts (= bar heights) across the plot, y-axis masked."""
    xs = np.arange(PLOT_X_LO, PLOT_X_HI)
    gc = is_gray[top + 3:baseline - 1, PLOT_X_LO:PLOT_X_HI].sum(0).astype(float)
    gc = gc * (np.abs(xs - yaxis_x) > YAXIS_MASK_PX)
    gc[gc < 5] = 0.0          # drop isolated speckle
    return xs, gc


def extract_panel(is_gray, top, baseline, yaxis_x, slope, x0):
    xs, gc = panel_profile(is_gray, top, baseline, yaxis_x)
    def to_A(x):
        return (np.asarray(x) - x0) / slope
    w = gc / gc.sum()
    A = to_A(xs)
    mean_A = float((A * w).sum())
    std_A = float(np.sqrt(((A - mean_A) ** 2 * w).sum()))
    mode_A = float(to_A(xs[int(np.argmax(gc))]))
    # FWHM from the half-max crossings of the column-height profile
    hm = gc.max() / 2.0
    above = np.where(gc >= hm)[0]
    fwhm_A = float(to_A(xs[above.max()]) - to_A(xs[above.min()])) if len(above) > 1 else float("nan")
    return dict(mean_A=mean_A, std_A=std_A, mode_A=mode_A, fwhm_A=fwhm_A,
                centroid_x=float((xs * w).sum()))


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def maybe_render():
    import subprocess
    import hashlib
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(PDF_PATH)
    h = hashlib.sha256(open(PDF_PATH, "rb").read()).hexdigest()
    if h != PDF_SHA256:
        raise RuntimeError(f"PDF SHA mismatch: {h} != {PDF_SHA256}")
    subprocess.run(["pdftoppm", "-f", "9", "-l", "9", "-r", "300", "-png",
                    PDF_PATH, os.path.join(OUTDIR, "si_s2")], check=True)


def main():
    if "--render" in sys.argv:
        maybe_render()

    src, im = load_image()
    is_gray, is_dark, is_red = masks(im)

    yaxis_x = detect_yaxis_x(is_dark)
    boxes = detect_boxes(is_dark, yaxis_x)           # 6 x (top, baseline)
    baselines = [b for (_, b) in boxes]
    slope, x0, cal_vals, cal_xs, cal_resid = calibrate_x(is_dark, baselines, yaxis_x)

    px_per_A = slope
    print(f"# render            : {src}")
    print(f"# image size        : {im.shape[1]}x{im.shape[0]}")
    print(f"# y-axis (x=0) at px: {yaxis_x}")
    print(f"# panel boxes (top,baseline): {boxes}")
    print(f"# calibration       : {px_per_A:.5f} px/A, x0={x0:.2f} px "
          f"(0->{x0:.1f}px ... 60->{x0 + 60 * slope:.1f}px), "
          f"max tick residual {cal_resid:.2f}px")
    print(f"# calib anchors (A) : {cal_vals}")
    print()

    rows = []
    print(f"{'lam':>4} {'E1s':>6} {'edge_A':>7} {'edge_nm':>8} {'unc_nm':>7} "
          f"{'Fig2b_A':>8} {'delta':>6} xcheck")
    for lam, (top, base) in zip(LAMBDAS, boxes):
        r = extract_panel(is_gray, top, base, yaxis_x, slope, x0)
        edge_A = r["mean_A"]
        edge_nm = edge_A / 10.0
        unc_nm = r["std_A"] / 10.0
        tgt = FIG2B_TARGET_A.get(lam)
        if tgt is not None:
            delta = edge_A - tgt
            ok = "OK" if abs(delta) <= 3.0 else "FAIL"
            tgt_s, d_s = f"{tgt:8.1f}", f"{delta:+6.2f}"
        else:
            delta, ok, tgt_s, d_s = None, "extract", f"{'--':>8}", f"{'--':>6}"
        print(f"{lam:>4} {E1S[lam]:>6.3f} {edge_A:>7.2f} {edge_nm:>8.3f} "
              f"{unc_nm:>7.3f} {tgt_s} {d_s} {ok}")
        rows.append(dict(
            lambda1s_nm=lam, e1s_ev=E1S[lam],
            edge_length_A=round(edge_A, 2), edge_length_nm=round(edge_nm, 3),
            size_unc_nm=round(unc_nm, 3),
            method="gray_histogram_weighted_centroid",
            calib_px_per_A=round(px_per_A, 5), x0_px=round(x0, 2),
            mode_A=round(r["mode_A"], 2), fwhm_A=round(r["fwhm_A"], 2),
            fig2b_target_A=("" if tgt is None else tgt),
            delta_A=("" if delta is None else round(delta, 2)),
        ))

    # ---- CSV ----
    csv_path = os.path.join(OUTDIR, "s2b_centers.csv")
    cols = ["lambda1s_nm", "e1s_ev", "edge_length_A", "edge_length_nm",
            "size_unc_nm", "method", "calib_px_per_A", "x0_px",
            "mode_A", "fwhm_A", "fig2b_target_A", "delta_A"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\n# wrote {csv_path}")

    # ---- overlay PNG ----
    overlay = Image.fromarray(im.astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(overlay)
    for (top, base), row in zip(boxes, rows):
        cx = int(round(row["x0_px"] + row["edge_length_A"] * px_per_A))
        d.line([(cx, top), (cx, base)], fill=(0, 110, 255), width=3)          # centroid (blue)
        # +-1 std band (green)
        s_px = int(round(row["size_unc_nm"] * 10 * px_per_A))
        d.line([(cx - s_px, (top + base) // 2), (cx + s_px, (top + base) // 2)],
               fill=(0, 180, 0), width=2)
        # Fig-2b target (magenta), where available
        if row["fig2b_target_A"] != "":
            tx = int(round(x0 + float(row["fig2b_target_A"]) * px_per_A))
            d.line([(tx, top), (tx, base)], fill=(230, 0, 230), width=2)
    crop = overlay.crop((700, 250, 1340, 2720))
    out_png = os.path.join(OUTDIR, "s2b_overlay.png")
    crop.save(out_png)
    print(f"# wrote {out_png}  (blue=extracted centroid, green=+-1std, magenta=Fig2b target)")


if __name__ == "__main__":
    main()
