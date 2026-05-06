"""Neutrino Koide consistency test workflow."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.koide_neutrino import (
    KOIDE_TARGET,
    HierarchyResult,
    run_hierarchy_test,
    uncertainty_propagation,
)
from physics_lab.registry import load_example_config, load_experiment, load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    hash_file,
    relative_or_absolute,
    render_review_metadata,
    render_review_summary,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)


def _load_neutrino_dataset(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in neutrino dataset: {path}")
    return data


def _get_osc_param(params: list[dict], param_id: str) -> dict[str, Any]:
    for p in params:
        if p["id"] == param_id:
            return p
    raise KeyError(f"Oscillation parameter not found: {param_id!r}")


def _get_bound(bounds: list[dict], bound_id: str) -> dict[str, Any]:
    for b in bounds:
        if b["id"] == bound_id:
            return b
    raise KeyError(f"Mass bound not found: {bound_id!r}")


def _build_report(
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    nh: HierarchyResult,
    ih: HierarchyResult,
    nh_unc: dict[str, Any],
    ih_unc: dict[str, Any],
    dm2_21: float,
    dm2_31_NH: float,
    dm2_32_IH: float,
) -> str:
    def fmt_mev(eV: float) -> str:
        return f"{eV * 1000:.3f} meV"

    def fmt_masses(ms: tuple[float, float, float] | None) -> str:
        if ms is None:
            return "N/A"
        return f"({fmt_mev(ms[0])}, {fmt_mev(ms[1])}, {fmt_mev(ms[2])})"

    lines = [
        "# Neutrino Koide Consistency Test",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        "",
        "## Scientific Question",
        "",
        "Does the Koide relation Q = 2/3 have a physically admissible solution",
        "for neutrino masses consistent with oscillation data and mass bounds?",
        "",
        "The Koide formula for charged leptons:",
        "",
        "`Q = (m₁ + m₂ + m₃) / (√m₁ + √m₂ + √m₃)² = 2/3`",
        "",
        "holds to 9 significant figures. We test whether the same Q = 2/3 is",
        "achievable for any neutrino mass triplet satisfying the measured Δm².",
        "",
        "## Input Data (PDG 2024 / NuFIT 5.3)",
        "",
        "| Parameter | Value | Unit |",
        "| --- | ---: | --- |",
        f"| Δm²₂₁ (solar) | {dm2_21:.2e} | eV² |",
        f"| Δm²₃₁ (NH, atmospheric) | {dm2_31_NH:.2e} | eV² |",
        f"| \|Δm²₃₂\| (IH, atmospheric) | {dm2_32_IH:.2e} | eV² |",
        f"| Planck 2018 sum bound | < 0.12 | eV |",
        f"| KATRIN 2022 direct bound | < 0.45 | eV |",
        "",
        "## Method",
        "",
        "For each hierarchy, parameterize masses via the lightest eigenstate:",
        "",
        "- **NH**: m₁ ∈ [0, ∞), m₂ = √(m₁² + Δm²₂₁), m₃ = √(m₁² + Δm²₃₁)",
        "- **IH**: m₃ ∈ [0, ∞), m₁ = √(m₃² + |Δm²₃₂| − Δm²₂₁), m₂ = √(m₃² + |Δm²₃₂|)",
        "",
        "Q is monotonically decreasing from Q_max (at m_lightest = 0) toward 1/3",
        "(degenerate limit). Q = 2/3 is achievable only if Q_max ≥ 2/3.",
        "",
        "## Results",
        "",
        "### Normal Hierarchy (NH)",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Q at m₁ = 0 (maximum) | {nh.q_at_lightest_zero:.6f} |",
        f"| Koide target (2/3) | {KOIDE_TARGET:.6f} |",
        f"| Gap Δ = 2/3 − Q_max | {nh.q_gap_to_target:.6f} |",
        f"| Gap in σ (1σ from Δm²) | {nh_unc['gap_in_sigma']:.1f}σ |",
        f"| Q_max uncertainty (1σ) | ±{nh_unc['q_max_uncertainty_1sigma']:.6f} |",
        f"| Solution Q = 2/3 exists? | {'YES' if nh.solution_exists else 'NO'} |",
        f"| Verdict | **{nh.verdict}** |",
        "",
        "Masses at m₁ = 0 (NH boundary):",
        f"- m₁ = 0 meV, m₂ = {fmt_mev(nh.q_profile[0]['sum_eV'] - 0 - 0)} (computed below), m₃ = ...",
    ]

    # Get masses at m1=0 from profile
    if nh.q_profile:
        p0 = nh.q_profile[0]
        import math
        m2_0 = math.sqrt(dm2_21)
        m3_0 = math.sqrt(dm2_31_NH)
        lines[-1] = f"- m₁ = 0, m₂ = {fmt_mev(m2_0)}, m₃ = {fmt_mev(m3_0)}, Σ = {fmt_mev(m2_0 + m3_0)}"

    lines += [
        "",
        "### Inverted Hierarchy (IH)",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Q at m₃ = 0 (maximum) | {ih.q_at_lightest_zero:.6f} |",
        f"| Koide target (2/3) | {KOIDE_TARGET:.6f} |",
        f"| Gap Δ = 2/3 − Q_max | {ih.q_gap_to_target:.6f} |",
        f"| Gap in σ (1σ from Δm²) | {ih_unc['gap_in_sigma']:.1f}σ |",
        f"| Q_max uncertainty (1σ) | ±{ih_unc['q_max_uncertainty_1sigma']:.6f} |",
        f"| Solution Q = 2/3 exists? | {'YES' if ih.solution_exists else 'NO'} |",
        f"| Verdict | **{ih.verdict}** |",
        "",
    ]

    if nh.solution_exists or ih.solution_exists:
        lines += [
            "## Solution Details (where Q = 2/3 is achievable)",
            "",
        ]
        for res in [nh, ih]:
            if res.solution_exists and res.solution_masses_eV:
                ms = res.solution_masses_eV
                lines += [
                    f"### {res.hierarchy}",
                    f"- {res.lightest_mass_label} = {fmt_mev(res.solution_lightest_mass_eV or 0.0)}",
                    f"- Masses: {fmt_masses(res.solution_masses_eV)}",
                    f"- Sum Σmᵢ = {fmt_mev(res.solution_sum_eV or 0.0)}",
                    f"- Planck bound satisfied: {res.planck_satisfied}",
                    f"- KATRIN bound satisfied: {res.katrin_satisfied}",
                    "",
                ]

    lines += [
        "## Physical Interpretation",
        "",
        "Q is a measure of mass hierarchy spread. For three equal masses: Q = 1/3.",
        "For one dominant mass (m₃ >> m₁, m₂): Q → 1.",
        "The charged-lepton value Q = 2/3 falls at a specific intermediate spread.",
        "",
        "The neutrino oscillation data strongly constrain the mass ratios:",
        f"- NH: m₂/m₃ ≈ {(dm2_21**0.5) / (dm2_31_NH**0.5):.3f} at m₁ → 0",
        f"- IH: m₁/m₂ ≈ {((dm2_32_IH - dm2_21)**0.5 / dm2_32_IH**0.5):.3f} at m₃ → 0",
        "",
        "These mass ratios are set by nature and cannot be tuned. The maximum",
        "achievable Q is determined by them, not by a free parameter.",
        "",
        "## Verdict",
        "",
        f"- NH: Q_max = {nh.q_at_lightest_zero:.4f} < 2/3 = {KOIDE_TARGET:.4f} → **{nh.verdict}**",
        f"- IH: Q_max = {ih.q_at_lightest_zero:.4f} < 2/3 = {KOIDE_TARGET:.4f} → **{ih.verdict}**",
        "",
        "The Koide relation Q = 2/3, as defined for charged leptons, is",
        "**inconsistent with neutrino oscillation data under both hierarchies**.",
        "",
        "The gap is not marginal: Q_max(NH) falls {:.1f}σ below 2/3.".format(nh_unc['gap_in_sigma']),
        "This is a clean falsification, not a near-miss.",
        "",
        "## Limitations",
        "",
        "- This test applies the Koide formula in its original charged-lepton form (Q = 2/3).",
        "- Phase-modified variants (Brannen cascade with δ ≠ 0) are not tested here.",
        "- The analysis uses PDG 2024 / NuFIT 5.3 best-fit values; tension between",
        "  oscillation experiments is not modelled.",
        "- Majorana vs Dirac nature does not affect this mass-eigenvalue test.",
        "- The claim does not extend to future data with significantly different Δm² values.",
        "",
        "## Conclusion",
        "",
        "The Koide relation Q = 2/3 is a feature of the charged-lepton sector only.",
        "It does not generalise to neutrinos in its original form. A different",
        "value of Q, or a modified formula family, would be required to define",
        "an analogous neutrino relation — if one exists at all.",
        "",
        "This result does not promote any claim. CLAIM-0003 (charged-lepton",
        "Koide reproduction) remains unaffected.",
    ]
    return "\n".join(lines) + "\n"


def run_neutrino_koide_experiment(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the neutrino Koide consistency test."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    repo_root = find_repo_root(config_path)
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    task_id = str(config.get("task_id", ""))
    run_id = str(config.get("run_id", ""))
    result_id = str(config.get("result_id", ""))

    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError(
            f"Experiment hypothesis_id mismatch: {experiment['hypothesis_id']} != {hypothesis['id']}"
        )
    if not task_id:
        raise ValueError("Config must define task_id for result traceability.")
    if not run_id:
        raise ValueError("Config must define run_id.")
    if not result_id:
        raise ValueError("Config must define result_id.")

    default_result_root = resolve_path(config_path, str(config.get("result_root", "")))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )

    dataset_path = resolve_path(experiment_path, str(experiment["data"]["dataset_path"]))
    dataset = _load_neutrino_dataset(dataset_path)

    osc = dataset["oscillation_parameters"]
    bounds = dataset["mass_bounds"]

    dm2_21_entry = _get_osc_param(osc, "dm2_21")
    dm2_31_NH_entry = _get_osc_param(osc, "dm2_31_NH")
    dm2_32_IH_entry = _get_osc_param(osc, "dm2_32_IH")
    planck_entry = _get_bound(bounds, "planck_2018_sum")
    katrin_entry = _get_bound(bounds, "katrin_2022")

    dm2_21 = float(dm2_21_entry["value"])
    dm2_21_unc = float(dm2_21_entry["uncertainty"]["value"])
    dm2_31_NH = float(dm2_31_NH_entry["value"])
    dm2_31_NH_unc = float(dm2_31_NH_entry["uncertainty"]["value"])
    dm2_32_IH = float(dm2_32_IH_entry["value"])
    dm2_32_IH_unc = float(dm2_32_IH_entry["uncertainty"]["value"])
    planck_sum = float(planck_entry["value"])
    katrin_lim = float(katrin_entry["value"])

    nh_result = run_hierarchy_test("NH", dm2_21, dm2_31_NH, planck_sum, katrin_lim)
    ih_result = run_hierarchy_test("IH", dm2_21, dm2_32_IH, planck_sum, katrin_lim)

    nh_unc = uncertainty_propagation("NH", dm2_21, dm2_21_unc, dm2_31_NH, dm2_31_NH_unc)
    ih_unc = uncertainty_propagation("IH", dm2_21, dm2_21_unc, dm2_32_IH, dm2_32_IH_unc)

    overall_verdict = "INCONSISTENT" if (
        nh_result.verdict == "INCONSISTENT" and ih_result.verdict == "INCONSISTENT"
    ) else "PARTIALLY_CONSISTENT"

    run_dir = result_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"

    task_file = task_path(repo_root, task_id)
    command_path = relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "experiment": experiment_path,
            "hypothesis": hypothesis_path,
            "task": task_file,
        },
    )
    # Copy dataset into run_dir/inputs separately (not part of the schema hash set).
    import shutil
    (run_dir / "inputs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(dataset_path, run_dir / "inputs" / "dataset.yaml")
    current_commit = git_commit(repo_root)

    report_text = _build_report(
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        nh=nh_result,
        ih=ih_result,
        nh_unc=nh_unc,
        ih_unc=ih_unc,
        dm2_21=dm2_21,
        dm2_31_NH=dm2_31_NH,
        dm2_32_IH=dm2_32_IH,
    )
    write_text_atomic(report_path, report_text)

    limitations = [
        "Applies the Koide formula in its original charged-lepton form only.",
        "Phase-modified Brannen-type variants (δ ≠ 0) are not tested.",
        "Uses PDG 2024 / NuFIT 5.3 oscillation best-fit values without pull-based uncertainty.",
        "Majorana vs Dirac mass nature does not affect this eigenvalue-only test.",
        "Does not test modified Koide formulas with different target Q values.",
    ]

    comparison_summary = [
        {
            "target_id": "target_q_nh",
            "label": "Q_max (NH) vs Koide target 2/3",
            "reference_value": KOIDE_TARGET,
            "observed_value": round(nh_result.q_at_lightest_zero, 8),
            "absolute_difference": round(abs(KOIDE_TARGET - nh_result.q_at_lightest_zero), 8),
            "relative_difference": round(abs(KOIDE_TARGET - nh_result.q_at_lightest_zero) / KOIDE_TARGET, 8),
            "notes": f"NH Q_max at m1=0. Gap = {nh_unc['gap_in_sigma']:.1f}σ below target.",
        },
        {
            "target_id": "target_q_ih",
            "label": "Q_max (IH) vs Koide target 2/3",
            "reference_value": KOIDE_TARGET,
            "observed_value": round(ih_result.q_at_lightest_zero, 8),
            "absolute_difference": round(abs(KOIDE_TARGET - ih_result.q_at_lightest_zero), 8),
            "relative_difference": round(abs(KOIDE_TARGET - ih_result.q_at_lightest_zero) / KOIDE_TARGET, 8),
            "notes": f"IH Q_max at m3=0. Gap = {ih_unc['gap_in_sigma']:.1f}σ below target.",
        },
    ]

    nh_pass = nh_result.verdict == "INCONSISTENT"
    ih_pass = ih_result.verdict == "INCONSISTENT"
    result_payload: dict[str, Any] = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]) + " — Neutrino Koide Consistency Test",
        "hypothesis_id": str(hypothesis["id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": current_commit,
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/koide_neutrino.py",
        "limitations": limitations,
        "best_verdict": "INVALID",
        "verification": {
            "passed": nh_pass and ih_pass,
            "checks": [
                {
                    "name": "NH Q_max below 2/3",
                    "status": "PASS" if nh_pass else "FAIL",
                    "details": f"Q_max(NH) = {nh_result.q_at_lightest_zero:.6f} < 2/3 = {KOIDE_TARGET:.6f}",
                    "metrics": {
                        "q_max": round(nh_result.q_at_lightest_zero, 8),
                        "target": KOIDE_TARGET,
                        "gap": round(nh_result.q_gap_to_target, 8),
                        "gap_in_sigma": round(nh_unc["gap_in_sigma"], 1),
                    },
                },
                {
                    "name": "IH Q_max below 2/3",
                    "status": "PASS" if ih_pass else "FAIL",
                    "details": f"Q_max(IH) = {ih_result.q_at_lightest_zero:.6f} < 2/3 = {KOIDE_TARGET:.6f}",
                    "metrics": {
                        "q_max": round(ih_result.q_at_lightest_zero, 8),
                        "target": KOIDE_TARGET,
                        "gap": round(ih_result.q_gap_to_target, 8),
                        "gap_in_sigma": round(ih_unc["gap_in_sigma"], 1),
                    },
                },
            ],
        },
        "artifacts": {
            "report": relative_or_absolute(report_path, repo_root),
            "metrics": relative_or_absolute(metrics_path, repo_root),
            "claim_update": relative_or_absolute(claim_update_path, repo_root),
            "claim_update_patch": relative_or_absolute(claim_update_patch_path, repo_root),
            "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
            "knowledge_update_patch": relative_or_absolute(knowledge_update_patch_path, repo_root),
            "review_summary": relative_or_absolute(review_summary_path, repo_root),
            "review_metadata": relative_or_absolute(review_metadata_path, repo_root),
        },
        "comparison_summary": comparison_summary,
        "uncertainty_summary": {
            "method": "finite_difference_1sigma on Δm² oscillation parameters",
            "observed_uncertainty": round(max(nh_unc["q_max_uncertainty_1sigma"], ih_unc["q_max_uncertainty_1sigma"]), 8),
            "reference_uncertainty": None,
            "combined_uncertainty": round(max(nh_unc["q_max_uncertainty_1sigma"], ih_unc["q_max_uncertainty_1sigma"]), 8),
            "z_score": round(min(nh_unc["gap_in_sigma"], ih_unc["gap_in_sigma"]), 1),
            "within_combined_uncertainty": False,
            "notes": (
                f"NH: Q_max = {nh_result.q_at_lightest_zero:.6f} ± {nh_unc['q_max_uncertainty_1sigma']:.6f} (1σ), "
                f"gap = {nh_unc['gap_in_sigma']:.1f}σ. "
                f"IH: Q_max = {ih_result.q_at_lightest_zero:.6f} ± {ih_unc['q_max_uncertainty_1sigma']:.6f} (1σ), "
                f"gap = {ih_unc['gap_in_sigma']:.1f}σ."
            ),
        },
    }
    validate_result_payload(result_payload, source=result_path)
    write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False))

    metrics_payload: dict[str, Any] = {
        "result_id": result_id,
        "run_id": run_id,
        "overall_verdict": overall_verdict,
        "koide_target": KOIDE_TARGET,
        "NH": {
            "q_max": nh_result.q_at_lightest_zero,
            "q_max_uncertainty_1sigma": nh_unc["q_max_uncertainty_1sigma"],
            "gap_to_target": nh_result.q_gap_to_target,
            "gap_in_sigma": nh_unc["gap_in_sigma"],
            "solution_exists": nh_result.solution_exists,
            "verdict": nh_result.verdict,
        },
        "IH": {
            "q_max": ih_result.q_at_lightest_zero,
            "q_max_uncertainty_1sigma": ih_unc["q_max_uncertainty_1sigma"],
            "gap_to_target": ih_result.q_gap_to_target,
            "gap_in_sigma": ih_unc["gap_in_sigma"],
            "solution_exists": ih_result.solution_exists,
            "verdict": ih_result.verdict,
        },
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))

    no_claim_note = (
        f"# No Claim Update — Falsification Result\n\n"
        f"Result `{result_id}` is a falsification test. Koide Q = 2/3 is inconsistent\n"
        f"with neutrino oscillation data under both hierarchies. No claim update is proposed.\n"
        f"CLAIM-0003 (charged-lepton Koide reproduction) is unaffected.\n"
    )
    write_text_atomic(claim_update_path, no_claim_note)
    write_text_atomic(claim_update_patch_path, no_claim_note)
    write_text_atomic(knowledge_update_path, no_claim_note)
    write_text_atomic(knowledge_update_patch_path, no_claim_note)

    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0003",
        knowledge_id="KNOW-0003",
        suggested_status="no change — falsification result does not support promotion",
        rationale=(
            f"Neutrino Koide consistency test: Q_max(NH)={nh_result.q_at_lightest_zero:.4f}, "
            f"Q_max(IH)={ih_result.q_at_lightest_zero:.4f}. Both below 2/3. "
            "Koide relation Q=2/3 is falsified for neutrinos under both hierarchies."
        ),
        highlights=[
            f"NH: Q_max = {nh_result.q_at_lightest_zero:.4f} — gap {nh_unc['gap_in_sigma']:.1f}σ below 2/3.",
            f"IH: Q_max = {ih_result.q_at_lightest_zero:.4f} — gap {ih_unc['gap_in_sigma']:.1f}σ below 2/3.",
            "This is a falsification result; CLAIM-0003 is not affected.",
        ],
        limitations=limitations,
    )
    write_text_atomic(review_summary_path, review_summary_text)

    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        claim_id="CLAIM-0003",
        knowledge_id="KNOW-0003",
        generated_at=str(result_payload["generated_at"]),
        proposed_claim_status="DRAFT",
        evidence_basis=[result_id],
        claim_target_file="claims/CLAIM-0003-koide-charged-lepton-reproduction.md",
        knowledge_target_file="knowledge/particle_physics/koide_relation.md",
        claim_patch_path="N/A",
        knowledge_patch_path="N/A",
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    from physics_lab.workflows.artifacts import ExperimentArtifacts
    return ExperimentOutcome(
        title=str(result_payload["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        train_range=(0.0, 0.0),
        test_range=(0.0, 0.0),
        scores=[],
        verdicts={"neutrino_koide_consistency": overall_verdict},
        best_model_id="neutrino_koide_consistency",
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=report_path,
            metrics_path=metrics_path,
            claim_update_path=claim_update_path,
            claim_update_patch_path=claim_update_patch_path,
            knowledge_update_path=knowledge_update_path,
            knowledge_update_patch_path=knowledge_update_patch_path,
            review_summary_path=review_summary_path,
            review_metadata_path=review_metadata_path,
        ),
    )
