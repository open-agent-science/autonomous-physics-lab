#!/usr/bin/env python3
"""Deterministic figure digitization of the Almeida 2023 InP sizing curves.

Extracts the per-sample ``(edge length, E1s)`` and ``(volume, E1s)`` data points
for the *This work* filled-triangle markers in Figure 2b of:

    Almeida, G.; van der Poll, L.; Evers, W. H.; Szoboszlai, E.; Vonk, S. J. W.;
    Rabouw, F. T.; Houtepen, A. J. "Size-Dependent Optical Properties of InP
    Colloidal Quantum Dots," Nano Letters 2023, 23 (18), 8697-8703.
    DOI 10.1021/acs.nanolett.3c02630. Licensed CC-BY 4.0 (version-of-record,
    PMC10540257, zero embargo).

This is a WebPlotDigitizer-class extraction implemented as deterministic image
processing. It does NOT use LLM-estimated coordinates and does NOT substitute
the published sizing formula for measured points: every value is the centroid
of a detected filled marker mapped through auto-derived axis calibration. An
independent agent can replay byte-identical output from the same checksum-pinned
figure asset (Gate B style).

The figure asset itself is not vendored in the repository (publisher asset). It
is referenced by SHA-256 and locator; supply it locally to replay:

    python3 scripts/extract_almeida_sizing.py \\
        --image images_large_nl3c02630_0001.jpeg \\
        --outdir data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical

Source asset SHA-256:
    3b7a37c9c5b0377f0101288f91ea4a4ae27294ab3670c6b9489224969e68e2ce
Locator:
    https://pubs.acs.org/cms/10.1021/acs.nanolett.3c02630/asset/images/large/nl3c02630_0001.jpeg
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

EXPECTED_SHA = "3b7a37c9c5b0377f0101288f91ea4a4ae27294ab3670c6b9489224969e68e2ce"

# Independently known band-edge energies E1s = 1239.84 / lambda1s for the six
# size-series samples (lambda1s read from the published figure-panel labels).
# E1s is the *known* axis used to locate each marker row; the extracted size is
# the unknown quantity, so this is a cross-check, not a circular fit.
LAMBDA_NM = {2.695: 460, 2.583: 480, 2.431: 510, 2.254: 550, 2.138: 580, 2.000: 620}
ANCHORS_E1S = [2.695, 2.583, 2.431, 2.254, 2.138, 2.000]

# Plot geometry auto-detected from the SHA-pinned asset (black-line projection
# for frames, perpendicular tick bands for calibration). Pinned here because the
# SHA check guarantees the same pixels; axis_calibration.csv records the anchors.
PANELS = {
    "edge_length_nm": {
        "frame": (106, 516, 607, 908),
        "xt": (106.5, 1.0, 516.0, 6.0),
        "yt": (607.5, 2.8, 908.0, 1.8),
        "size_unit": "nm",
        "excl": [(230, 516, 607, 658), (350, 516, 658, 702), (110, 292, 826, 908)],
    },
    "volume_nm3": {
        "frame": (550, 958, 607, 908),
        "xt": (550.0, 0.0, 958.0, 20.0),
        "yt": (607.5, 2.8, 908.0, 1.8),
        "size_unit": "nm^3",
        "excl": [(680, 958, 607, 658), (760, 958, 658, 706)],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _black_not_red(path: Path):
    """Return (black-and-not-red mask, RGB array). Heavy deps imported lazily."""
    import numpy as np
    from PIL import Image

    arr = np.asarray(Image.open(path).convert("RGB")).astype(int)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    black = (r < 110) & (g < 110) & (b < 110)
    red = (r > 110) & ((r - g) > 45) & ((r - b) > 45)
    return black & ~red, arr


def _lin(p, p0, v0, p1, v1):
    return v0 + (p - p0) * (v1 - v0) / (p1 - p0)


def _expected_py(e1s, yt):
    return yt[0] + (yt[1] - e1s) * (yt[2] - yt[0]) / (yt[1] - yt[3])


def _error_half_width(blk, cx, cy, cfg):
    """Half-width of the horizontal error bar through (cx, cy), gap-tolerant."""
    x0, x1 = cfg["frame"][0], cfg["frame"][1]
    import numpy as np

    cyr = int(round(cy))
    rows = blk[max(cyr - 1, 0):cyr + 2, x0 + 2:x1 - 2].any(axis=0)
    xs = np.where(rows)[0] + x0 + 2
    if xs.size == 0:
        return 0.0

    def walk(seq):
        cur = cx
        for x in seq:
            if abs(x - cur) <= 3:
                cur = x
            else:
                break
        return cur

    xmin = walk(sorted([x for x in xs if x <= cx])[::-1])
    xmax = walk(sorted([x for x in xs if x >= cx]))
    mid = _lin(cx, *cfg["xt"])
    lo, hi = _lin(xmin, *cfg["xt"]), _lin(xmax, *cfg["xt"])
    return round(max(abs(mid - lo), abs(hi - mid)), 3)


def _extract_marker(blk, cfg, e1s):
    """Pick the most-solid filled triangle in the E1s band; return its centroid."""
    import numpy as np
    from scipy import ndimage

    x0, x1, _, _ = cfg["frame"]
    py = _expected_py(e1s, cfg["yt"])
    ya, yb = int(py - 9), int(py + 10)
    band = np.zeros_like(blk)
    band[ya:yb, x0 + 5:x1 - 4] = blk[ya:yb, x0 + 5:x1 - 4]
    for ex0, ex1, ey0, ey1 in cfg["excl"]:
        band[max(ya, ey0):min(yb, ey1), ex0:ex1] = False
    labels, count = ndimage.label(band)
    best = None
    for i in range(1, count + 1):
        core = ndimage.binary_erosion(labels == i, structure=np.ones((3, 3)))
        inter = int(core.sum())
        if inter == 0:
            continue
        cyc, cxc = ndimage.center_of_mass(core)
        if best is None or inter > best[0]:
            best = (inter, float(cxc), float(cyc))
    if best is None:
        return None
    inter, cx, cy = best
    return {
        "size": round(_lin(cx, *cfg["xt"]), 3),
        "e1s_meas": round(_lin(cy, *cfg["yt"]), 3),
        "px": round(cx, 1),
        "py": round(cy, 1),
        "core_px": inter,
        "unc": _error_half_width(blk, cx, cy, cfg),
    }


def _fit_e1s(panel, size):
    """Published fit (cross-check only, never substituted for measured size)."""
    if panel == "edge_length_nm":
        return round(1.33 + 9.128 * (size * 10.0) ** -0.684, 3)
    return round(1.33 + 1.219 * size ** -0.251, 3)


def extract(image: Path):
    blk, _ = _black_not_red(image)
    rows = []
    for panel, cfg in PANELS.items():
        for e1s in ANCHORS_E1S:
            marker = _extract_marker(blk, cfg, e1s)
            if marker is None:
                continue
            rows.append({"panel": panel, "e1s_known": e1s, **marker,
                         "fit_e1s": _fit_e1s(panel, marker["size"]),
                         "size_unit": cfg["size_unit"],
                         "lambda1s_nm": LAMBDA_NM[e1s]})
    return rows


def write_calibration(outdir: Path):
    path = outdir / "axis_calibration.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["panel", "axis", "anchor_id", "pixel_x", "pixel_y",
                         "axis_value", "axis_unit"])
        for panel, cfg in PANELS.items():
            x0, x1, ytop, ybot = cfg["frame"]
            px0, vx0, px1, vx1 = cfg["xt"]
            py0, vy0, py1, vy1 = cfg["yt"]
            su = cfg["size_unit"]
            writer.writerow([panel, "x", "x_lo", px0, ybot, vx0, su])
            writer.writerow([panel, "x", "x_hi", px1, ybot, vx1, su])
            writer.writerow([panel, "y", "y_hi", x0, py0, vy0, "eV"])
            writer.writerow([panel, "y", "y_lo", x0, py1, vy1, "eV"])
    return path


def write_points(outdir: Path, rows):
    path = outdir / "extracted_points.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["panel", "sample_lambda1s_nm", "e1s_ev_known",
                         "e1s_ev_measured", "size_value", "size_unit",
                         "size_uncertainty", "raw_pixel_x", "raw_pixel_y",
                         "marker_core_px", "inclusion_status", "fit_e1s_crosscheck",
                         "notes"])
        for r in rows:
            low_solidity = r["core_px"] < 8
            status = "included_flag_review" if low_solidity else "included"
            note = "marker overlaps Xu open triangle; low solidity" if low_solidity \
                else "filled This-work marker"
            writer.writerow([r["panel"], r["lambda1s_nm"], r["e1s_known"],
                             r["e1s_meas"], r["size"], r["size_unit"], r["unc"],
                             r["px"], r["py"], r["core_px"], status,
                             r["fit_e1s"], note])
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", required=True, type=Path,
                        help="Local CC-BY figure asset (not vendored).")
    parser.add_argument("--outdir", required=True, type=Path,
                        help="Directory to write axis_calibration.csv / extracted_points.csv.")
    parser.add_argument("--expect-sha", default=EXPECTED_SHA)
    parser.add_argument("--no-sha-check", action="store_true")
    args = parser.parse_args(argv)

    if not args.image.is_file():
        raise SystemExit(f"image not found: {args.image}")
    digest = sha256(args.image)
    if not args.no_sha_check and digest != args.expect_sha:
        raise SystemExit(
            f"SHA-256 mismatch: got {digest}, expected {args.expect_sha}. "
            "Pass --no-sha-check to override (geometry may not apply).")

    args.outdir.mkdir(parents=True, exist_ok=True)
    rows = extract(args.image)
    cal = write_calibration(args.outdir)
    pts = write_points(args.outdir, rows)

    print(f"asset_sha256={digest}")
    print(f"wrote {cal}")
    print(f"wrote {pts}")
    print("\npanel            lambda  E1s_known  E1s_meas   size    +/-    core  fit_E1s")
    for r in rows:
        print(f"{r['panel']:<15} {r['lambda1s_nm']:>4}    {r['e1s_known']:.3f}     "
              f"{r['e1s_meas']:.3f}   {r['size']:6.3f}  {r['unc']:.2f}   "
              f"{r['core_px']:>3}   {r['fit_e1s']:.3f}")


if __name__ == "__main__":
    main()
