#!/usr/bin/env python3
"""Run the deterministic FIRAS Wien-peak consistency metric slice (TASK-0802).

Consumes ONLY the committed, checksum-pinned FIRAS monopole rows and the frozen
textbook Wien-displacement reference at the TASK-0815 reference temperature. It
computes one wavelength-domain Wien-peak consistency metric with explicit
wavelength-vs-frequency domain-conversion handling, emits exactly one admissible
verdict from the TASK-0793 note, and writes a schema-valid sandbox agent-run
package.

No live fetch, no source re-pin, no blackbody fit, no fitted free parameters.

Example::

    python3 scripts/run_textbook_wien_firas_peak_consistency.py \\
        --out-dir agent_runs/AGENT-RUN-0078
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.textbook_wien_firas_peak import (
    CONTROL_MIN_RELATIVE_MISS,
    INTERPOLATED_RELATIVE_TOLERANCE,
    RAW_BIN_RELATIVE_TOLERANCE,
    REFERENCE_TEMPERATURE_CITATION,
    REFERENCE_TEMPERATURE_SIGMA_K,
    SPEED_OF_LIGHT_M_S,
    WIEN_WAVELENGTH_DISPLACEMENT_M_K,
    evaluate_wien_firas_peak,
    load_firas_rows,
)
from physics_lab.workflows.artifacts import git_commit


REPO_ROOT = Path(__file__).resolve().parents[1]
FIRAS_ROWS_REL = "data/textbook_formula_audit/wien_firas/firas_monopole_rows.yaml"
WIEN_REFERENCE_REL = (
    "data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml"
)
SCRIPT_REL = "scripts/run_textbook_wien_firas_peak_consistency.py"
ENGINE_REL = "physics_lab/engines/textbook_wien_firas_peak.py"

TASK_ID = "TASK-0802"
CAMPAIGN_PROFILE_ID = "textbook-formula-audit"
HYP_PROPOSAL_REL = (
    "hypothesis_proposals/textbook-formula-audit/"
    "HYP-PROPOSAL-0062-firas-wien-peak-consistency.yaml"
)
EXP_PROPOSAL_REL = (
    "experiment_proposals/textbook-formula-audit/"
    "EXP-PROPOSAL-0028-firas-wien-peak-consistency.yaml"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_reference_constant() -> None:
    """Confirm the engine constant matches the committed exact-reference fixture."""
    fixture = yaml.safe_load((REPO_ROOT / WIEN_REFERENCE_REL).read_text("utf-8"))
    fixture_constant = float(fixture["source_convention"]["value_m_k"])
    if fixture_constant != WIEN_WAVELENGTH_DISPLACEMENT_M_K:
        raise SystemExit(
            "Wien constant mismatch between engine and committed fixture: "
            f"{WIEN_WAVELENGTH_DISPLACEMENT_M_K} != {fixture_constant}"
        )


def _build_metrics(metric: Any, input_hashes: dict[str, str], command: str) -> dict[str, Any]:
    lam_ref_mm = metric.reference_wavelength_peak_m * 1000.0
    return {
        "agent_run_id": None,  # filled in by caller
        "benchmark_id": "textbook-firas-wien-peak-consistency-slice",
        "task_id": TASK_ID,
        "dataset_id": "TFA-WIEN-FIRAS-MONOPOLE-V1",
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "command": command,
        "code_reference": ENGINE_REL,
        "input_hashes": input_hashes,
        "verdict": metric.verdict,
        "admissible_verdicts": [
            "CONSISTENT_IN_SCOPE",
            "DOMAIN_CONVERSION_MISMATCH",
            "INCONCLUSIVE_PRODUCT_SEMANTICS",
            "INCONCLUSIVE_SAMPLING_RESOLUTION",
        ],
        "constants": {
            "speed_of_light_m_s": SPEED_OF_LIGHT_M_S,
            "wien_wavelength_displacement_constant_m_k": (
                WIEN_WAVELENGTH_DISPLACEMENT_M_K
            ),
            "wien_constant_provenance": "CODATA 2022 / NIST",
        },
        "reference_temperature": {
            "value_k": metric.reference_temperature_k,
            "sigma_k": REFERENCE_TEMPERATURE_SIGMA_K,
            "citation": REFERENCE_TEMPERATURE_CITATION,
            "provenance_role": (
                "separately pinned reference temperature (TASK-0815 contract); "
                "not a fitted parameter chosen from the FIRAS rows"
            ),
        },
        "domain_conversion": {
            "native_axis": "wavenumber cm^-1 (FIRAS B_nu)",
            "target_domain": "wavelength-domain Wien peak lambda_peak = b / T",
            "jacobian": "B_lambda = B_nu * nu^2 / c (nu = c * k_m, lambda = 1 / k_m)",
            "unit_conversion": "k[cm^-1] -> k[m^-1] (x100) -> nu[Hz] (xc) -> lambda[m] (1/k_m)",
            "note": (
                "Frequency-domain and wavelength-domain peaks differ by the Planck "
                "Jacobian (Wien non-invariance); they are reported separately."
            ),
        },
        "primary_metric": {
            "reference_wavelength_peak_m": metric.reference_wavelength_peak_m,
            "reference_wavelength_peak_mm": lam_ref_mm,
            "reference_wavenumber_cm_inverse": metric.reference_wavenumber_cm_inverse,
            "wavelength_domain_peak_raw_bin_m": metric.wavelength_domain_peak_raw_bin_m,
            "wavelength_domain_peak_raw_bin_mm": (
                metric.wavelength_domain_peak_raw_bin_m * 1000.0
            ),
            "wavelength_domain_peak_raw_bin_wavenumber_cm_inverse": (
                metric.wavelength_domain_peak_raw_bin_wavenumber_cm_inverse
            ),
            "wavelength_domain_peak_interpolated_m": (
                metric.wavelength_domain_peak_interpolated_m
            ),
            "wavelength_domain_peak_interpolated_mm": (
                metric.wavelength_domain_peak_interpolated_m * 1000.0
            ),
            "raw_bin_relative_difference": metric.raw_bin_relative_difference,
            "interpolated_relative_difference": (
                metric.interpolated_relative_difference
            ),
            "raw_bin_relative_tolerance": RAW_BIN_RELATIVE_TOLERANCE,
            "interpolated_relative_tolerance": INTERPOLATED_RELATIVE_TOLERANCE,
            "interpolation_method": (
                "fixed parabolic-vertex refinement of the located raw-bin peak; "
                "deterministic sampling-resolution diagnostic, not a model fit"
            ),
        },
        "domain_conversion_handling": {
            "frequency_domain_peak_wavenumber_cm_inverse": (
                metric.frequency_domain_peak_wavenumber_cm_inverse
            ),
            "frequency_domain_peak_frequency_hz": (
                metric.frequency_domain_peak_frequency_hz
            ),
            "frequency_domain_peak_frequency_ghz": (
                metric.frequency_domain_peak_frequency_hz / 1e9
            ),
            "no_jacobian_relabel_wavelength_m": (
                metric.no_jacobian_relabel_wavelength_m
            ),
            "no_jacobian_relabel_wavelength_mm": (
                metric.no_jacobian_relabel_wavelength_m * 1000.0
            ),
            "no_jacobian_relabel_relative_difference": (
                metric.no_jacobian_relabel_relative_difference
            ),
        },
        "controls": {
            "definitions": {
                "absolute_product_gate": (
                    "fail if the committed product is residual-only/model-normalized"
                ),
                "no_jacobian_relabel_rejected": (
                    "relabelling wavenumber as wavelength without the Jacobian must "
                    "miss the reference by at least the control threshold"
                ),
                "frequency_domain_peak_distinct": (
                    "the native frequency-domain peak must differ from the "
                    "wavelength-domain peak by more than one bin"
                ),
                "wrong_temperature_rejected": (
                    "an intentionally offset reference temperature (+10%) must miss"
                ),
            },
            "control_min_relative_miss": CONTROL_MIN_RELATIVE_MISS,
            "wrong_temperature_k": metric.wrong_temperature_k,
            "wrong_temperature_relative_difference": (
                metric.wrong_temperature_relative_difference
            ),
            "outcomes": metric.controls,
            "all_passed": all(metric.controls.values()),
        },
        "sampling_resolution": {
            "bin_spacing_below_cm_inverse": metric.bin_spacing_below_cm_inverse,
            "bin_spacing_above_cm_inverse": metric.bin_spacing_above_cm_inverse,
            "note": (
                "FIRAS bin spacing limits the raw-bin peak precision; the parabolic "
                "refinement reports the sampling sensitivity."
            ),
        },
        "circularity_caveat": (
            "The Fixsen 2009 reference temperature is itself derived by fitting a "
            "Planck spectrum to FIRAS, so this is a blackbody self-consistency check "
            "in scope, not independent empirical validation of Wien displacement."
        ),
        "promotion_boundary": {
            "creates_claim": False,
            "creates_knowledge": False,
            "creates_prediction": False,
            "creates_result": False,
            "consistency_in_scope_only": True,
        },
    }


def _render_report(metrics: dict[str, Any]) -> str:
    pm = metrics["primary_metric"]
    dc = metrics["domain_conversion_handling"]
    ctl = metrics["controls"]
    return "\n".join(
        [
            "# FIRAS Wien-Peak Consistency Slice",
            "",
            f"- Task: `{TASK_ID}`",
            f"- Benchmark: `{metrics['benchmark_id']}`",
            f"- Verdict: `{metrics['verdict']}`",
            f"- Engine: `{ENGINE_REL}` (version `{metrics['engine_version']}`)",
            "- Scope: bounded spectral-domain consistency audit only; not a "
            "universal validation of Wien displacement, blackbody physics, or CMB physics.",
            "",
            "## Reference",
            "",
            f"- Reference temperature `T_ref = {metrics['reference_temperature']['value_k']} K`"
            f" (`{metrics['reference_temperature']['citation']}`).",
            f"- Textbook wavelength-domain peak `lambda_peak = b / T = "
            f"{pm['reference_wavelength_peak_mm']:.4f} mm` "
            f"(= {pm['reference_wavenumber_cm_inverse']:.3f} cm^-1).",
            "",
            "## Primary metric (wavelength-domain, Jacobian applied)",
            "",
            "| quantity | value |",
            "| --- | --- |",
            f"| raw-bin peak | {pm['wavelength_domain_peak_raw_bin_mm']:.4f} mm "
            f"({pm['wavelength_domain_peak_raw_bin_wavenumber_cm_inverse']:.2f} cm^-1) |",
            f"| interpolated peak | {pm['wavelength_domain_peak_interpolated_mm']:.4f} mm |",
            f"| raw-bin relative difference | {pm['raw_bin_relative_difference']:.5f} "
            f"(tol {pm['raw_bin_relative_tolerance']}) |",
            f"| interpolated relative difference | "
            f"{pm['interpolated_relative_difference']:.5f} "
            f"(tol {pm['interpolated_relative_tolerance']}) |",
            "",
            "## Domain-conversion handling (reported separately)",
            "",
            f"- Jacobian: `{metrics['domain_conversion']['jacobian']}`.",
            f"- Frequency-domain peak: "
            f"{dc['frequency_domain_peak_wavenumber_cm_inverse']:.2f} cm^-1 "
            f"({dc['frequency_domain_peak_frequency_ghz']:.1f} GHz) — distinct from "
            "the wavelength-domain peak by the Planck Jacobian.",
            f"- No-Jacobian relabel control: {dc['no_jacobian_relabel_wavelength_mm']:.4f} mm "
            f"(relative difference {dc['no_jacobian_relabel_relative_difference']:.4f}) — "
            "correctly wrong.",
            "",
            "## Controls",
            "",
            "| control | passed |",
            "| --- | --- |",
            *[f"| `{name}` | `{passed}` |" for name, passed in ctl["outcomes"].items()],
            "",
            "## Limitations",
            "",
            "- Single pinned FIRAS monopole product; one reference temperature.",
            "- The reference temperature is FIRAS-derived, so this is a blackbody "
            "self-consistency check in scope, not independent validation.",
            "- Sandbox evidence only; no canonical RESULT/CLAIM/KNOW/PRED is created.",
            "",
            "## Output Routing",
            "",
            "- Canonical destination: sandbox agent-run package plus "
            "`docs/reviews/` consistency note.",
            "- Review tier: none (sandbox-only).",
            "- Gate A: not attempted (sandbox-by-default).",
            "- Gate B: not attempted.",
            "- Claim impact: none. Knowledge impact: none.",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    pm = metrics["primary_metric"]
    return "\n".join(
        [
            "# FIRAS Wien-Peak Consistency Review Summary",
            "",
            f"- Task: `{TASK_ID}`",
            f"- Verdict: `{metrics['verdict']}`",
            f"- Wavelength-domain peak (interpolated): "
            f"{pm['wavelength_domain_peak_interpolated_mm']:.4f} mm vs reference "
            f"{pm['reference_wavelength_peak_mm']:.4f} mm "
            f"(relative difference {pm['interpolated_relative_difference']:.5f}).",
            "- Domain conversion handled with the explicit "
            "`B_lambda = B_nu * nu^2 / c` Jacobian; frequency-domain peak and "
            "no-Jacobian relabel reported separately as controls.",
            f"- All predeclared controls passed: "
            f"`{metrics['controls']['all_passed']}`.",
            "- Boundary: consistency-in-scope only; sandbox evidence; no canonical "
            "promotion and no universal Wien/blackbody claim.",
            "",
        ]
    )


def _render_limitations() -> str:
    return "\n".join(
        [
            "# Limitations",
            "",
            "- Single pinned COBE/FIRAS absolute monopole product (43 rows, one "
            "spectral axis).",
            "- One separately pinned reference temperature "
            f"(`{REFERENCE_TEMPERATURE_CITATION}`); the FIRAS-recalibrated value is "
            "reserved for sensitivity only.",
            "- The reference temperature is FIRAS-derived, so the audit is a "
            "blackbody self-consistency check, not independent empirical validation "
            "of Wien displacement.",
            "- Raw-bin peak precision is limited by FIRAS bin spacing; the "
            "interpolation is a fixed sampling-resolution diagnostic, not a fit.",
            "- Sandbox-only: no canonical RESULT/CLAIM/KNOW/PRED artifact is created.",
            "- Not a blackbody-universality, textbook-falsification, proof, or "
            "discovery statement.",
            "",
        ]
    )


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Task: `{TASK_ID}`",
            "- `committed_inputs_only`: consumed the checksum-pinned FIRAS rows and "
            "the frozen Wien exact-reference fixture; no live fetch, no source re-pin.",
            "- `temperature_pinned_upstream`: used the TASK-0815 reference "
            f"temperature `{metrics['reference_temperature']['value_k']} K`; not "
            "chosen after seeing output.",
            "- `domain_conversion_declared`: applied the "
            "`B_lambda = B_nu * nu^2 / c` Jacobian before locating the wavelength "
            "peak; no-Jacobian relabel kept as a negative control.",
            "- `no_fitted_free_parameters`: no blackbody fit; the parabolic "
            "refinement is a fixed deterministic interpolation.",
            "- `single_evaluation`: one consistency metric; no added bins or spectra.",
            "",
        ]
    )


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _build_agent_run_manifest(run_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
    run_dir_rel = f"agent_runs/{run_id}"
    # Map the scoped Wien verdict onto the agent-run schema enum: a clean
    # in-scope consistency result with all controls passing is a SANDBOX_PASS;
    # an inconclusive scoped verdict maps to INCONCLUSIVE.
    scoped = metrics["verdict"]
    if scoped == "CONSISTENT_IN_SCOPE" and metrics["controls"]["all_passed"]:
        manifest_verdict = "SANDBOX_PASS"
    elif scoped in {
        "INCONCLUSIVE_PRODUCT_SEMANTICS",
        "INCONCLUSIVE_SAMPLING_RESOLUTION",
    }:
        manifest_verdict = "INCONCLUSIVE"
    else:
        manifest_verdict = "REVIEW_NEEDED"
    return {
        "id": run_id,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "REVIEW_READY",
        "sandbox_only": True,
        "created_by": {"contributor_id": "gladunrv", "agent_id": "claude"},
        "proposal_paths": {
            "hypothesis": HYP_PROPOSAL_REL,
            "experiment": EXP_PROPOSAL_REL,
        },
        "artifacts": {
            "metrics": f"{run_dir_rel}/metrics.json",
            "report": f"{run_dir_rel}/report.md",
            "limitations": f"{run_dir_rel}/limitations.md",
            "preflight": f"{run_dir_rel}/preflight.md",
            "review_summary": f"{run_dir_rel}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "committed_inputs_only",
                    "status": "PASS",
                    "notes": (
                        "Consumed the checksum-pinned FIRAS rows and the frozen "
                        "Wien exact-reference fixture; no live fetch or re-pin."
                    ),
                },
                {
                    "name": "temperature_pinned_upstream",
                    "status": "PASS",
                    "notes": (
                        "Used the TASK-0815 reference temperature "
                        f"{metrics['reference_temperature']['value_k']} K; not "
                        "chosen after seeing metric output."
                    ),
                },
                {
                    "name": "domain_conversion_declared",
                    "status": "PASS",
                    "notes": (
                        "Applied B_lambda = B_nu * nu^2 / c before locating the "
                        "wavelength peak; no-Jacobian relabel kept as a control."
                    ),
                },
                {
                    "name": "no_fitted_free_parameters",
                    "status": "PASS",
                    "notes": (
                        "No blackbody fit; the parabolic refinement is a fixed "
                        "deterministic interpolation diagnostic."
                    ),
                },
            ],
        },
        "limitations": [
            "Single pinned COBE/FIRAS absolute monopole product and one reference "
            "temperature.",
            "The reference temperature is FIRAS-derived, so this is a blackbody "
            "self-consistency check, not independent validation.",
            "Raw-bin peak precision is limited by FIRAS bin spacing.",
            "Sandbox-only; no canonical RESULT/CLAIM/KNOW/PRED artifact is created.",
            "Not a blackbody-universality, textbook-falsification, or discovery "
            "statement.",
        ],
        "verdict": manifest_verdict,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review of the sandbox consistency slice; a separate "
                "Gate A result-packaging task would be required before any "
                "RESULT-* candidate."
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default="agent_runs/AGENT-RUN-0078",
        help="Sandbox agent-run output directory (repository-relative).",
    )
    args = parser.parse_args(argv)

    out_dir = (REPO_ROOT / args.out_dir).resolve()
    run_id = out_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)

    _verify_reference_constant()

    rows_path = REPO_ROOT / FIRAS_ROWS_REL
    dataset = load_firas_rows(rows_path)
    metric = evaluate_wien_firas_peak(dataset)

    input_hashes = {
        "firas_rows_sha256": _sha256(rows_path),
        "wien_reference_fixture_sha256": _sha256(REPO_ROOT / WIEN_REFERENCE_REL),
        "engine_sha256": _sha256(REPO_ROOT / ENGINE_REL),
        "script_sha256": _sha256(REPO_ROOT / SCRIPT_REL),
    }
    command = f"python3 {SCRIPT_REL} --out-dir {args.out_dir}"

    metrics = _build_metrics(metric, input_hashes, command)
    metrics["agent_run_id"] = run_id

    _write(
        out_dir / "metrics.json",
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
    )
    _write(out_dir / "report.md", _render_report(metrics))
    _write(out_dir / "review_summary.md", _render_review_summary(metrics))
    _write(out_dir / "limitations.md", _render_limitations())
    _write(out_dir / "preflight.md", _render_preflight(metrics))

    manifest = _build_agent_run_manifest(run_id, metrics)
    _write(
        out_dir / "agent_run.yaml",
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
    )

    print(f"verdict={metric.verdict}")
    print(
        "wavelength_peak_interpolated_mm="
        f"{metric.wavelength_domain_peak_interpolated_m * 1000.0:.4f}"
    )
    print(
        "interpolated_relative_difference="
        f"{metric.interpolated_relative_difference:.5f}"
    )
    print(f"controls_all_passed={all(metric.controls.values())}")
    print(f"wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
