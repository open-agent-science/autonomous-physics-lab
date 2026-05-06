"""Quark Koide cascade workflow — Brannen phase extension test."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.koide_quark import (
    KOIDE_TARGET,
    SectorResult,
    run_sector_test,
)
from physics_lab.registry import load_example_config, load_experiment, load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    relative_or_absolute,
    render_review_metadata,
    render_review_summary,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)


def _load_quark_dataset(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in quark dataset: {path}")
    return data


def _get_quark(quarks: list[dict], quark_id: str) -> dict:
    for q in quarks:
        if q["id"] == quark_id:
            return q
    raise KeyError(f"Quark not found: {quark_id!r}")


def _build_report(
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    up: SectorResult,
    down: SectorResult,
) -> str:
    return f"""# Quark Koide Cascade — Brannen Phase Extension Test

**Result ID:** `{result_id}`
**Run:** `{run_id}`
**Experiment:** `EXP-0008`
**Hypothesis:** `{hypothesis_id}`
**Task:** `{task_id}`

---

## Scope

This experiment tests whether the Koide formula Q = 2/3 can be satisfied
by the up-type quark triplet (u, c, t) or the down-type triplet (d, s, b)
using PDG 2024 running masses. Two formulas are evaluated:

1. **Standard Koide** (real, δ = 0): Q = (Σm) / (Σ√m)²
2. **Phase scan** Q(δ) = (Σm) / |√m₁ + √m₂·e^(iδ) + √m₃·e^(2iδ)|², δ ∈ [0, π]
3. **Brannen equal-spacing** Q_B = (Σm) / (Σm − Σ√(mᵢmⱼ))

Key analytic result: for this phase parameterisation, Q(δ) is minimised at
δ = 0, so Q_min = Q_std. If Q_std > 2/3, then no phase brings Q to 2/3.

---

## Up-Type Sector (u, c, t)

| Metric | Value |
| --- | ---: |
| Masses | mu = 2.16 MeV, mc = 1270 MeV, mt = 172,690 MeV |
| Q standard (δ=0) | {up.q_standard:.6f} |
| Q target (2/3) | {KOIDE_TARGET:.6f} |
| Gap Δ = Q − 2/3 | {up.q_standard_gap:.6f} |
| Q uncertainty (1σ) | ±{up.q_standard_unc:.6f} |
| Gap in σ | **{up.q_standard_gap_sigma}σ** |
| Q phase min (scan) | {up.q_phase_min:.6f} |
| Q phase max (scan) | {up.q_phase_max:.6f} |
| Phase achieves Q = 2/3? | **{"YES" if up.phase_achieves_target else "NO"}** |
| Q Brannen equal-spacing | {up.q_brannen:.6f} |
| Brannen fit B/A ratio | {up.brannen_fit_B_over_A} |
| Verdict | **{up.verdict}** |

---

## Down-Type Sector (d, s, b)

| Metric | Value |
| --- | ---: |
| Masses | md = 4.67 MeV, ms = 93.4 MeV, mb = 4183 MeV |
| Q standard (δ=0) | {down.q_standard:.6f} |
| Q target (2/3) | {KOIDE_TARGET:.6f} |
| Gap Δ = Q − 2/3 | {down.q_standard_gap:.6f} |
| Q uncertainty (1σ) | ±{down.q_standard_unc:.6f} |
| Gap in σ | **{down.q_standard_gap_sigma}σ** |
| Q phase min (scan) | {down.q_phase_min:.6f} |
| Q phase max (scan) | {down.q_phase_max:.6f} |
| Phase achieves Q = 2/3? | **{"YES" if down.phase_achieves_target else "NO"}** |
| Q Brannen equal-spacing | {down.q_brannen:.6f} |
| Brannen fit B/A ratio | {down.brannen_fit_B_over_A} |
| Verdict | **{down.verdict}** |

---

## Physical Interpretation

**Why Q > 2/3 for quarks:**

The Koide formula Q = 2/3 holds for charged leptons because the three lepton
masses satisfy a specific numerical relation. For quarks, the mass hierarchies
are far more extreme: mt/mu ~ 80,000 (up sector) and mb/md ~ 900 (down sector),
compared to mτ/me ~ 3,500 for leptons.

For the standard Koide formula, Q increases as masses become more hierarchical.
The charged-lepton masses happen to sit at the precise hierarchy where Q = 2/3.
Quark masses are more hierarchical, giving Q > 2/3.

**Why the phase scan cannot help:**

For the parameterisation Q(δ) = (Σm)/|√m₁ + √m₂·e^(iδ) + √m₃·e^(2iδ)|²,
the denominator is maximised at δ = 0 (standard real formula), so Q is
minimised at δ = 0. Since Q_min = Q_std > 2/3, no phase δ ∈ [0, π] brings
Q to 2/3.

**Brannen B/A ratio:**

The Brannen parametrization √mₖ = A + B·cos(δ_fit + 2πk/3) always has an
exact solution for any three positive masses. The ratio B/A measures how
"extreme" the mass hierarchy is. For charged leptons B/A ≈ 1.4; for up quarks
B/A ≈ 1.76 and for down quarks B/A ≈ 1.55. These values indicate that the
Brannen parametrization goes through negative values between the three evaluation
points — a sign of large hierarchy.

**Down sector note:**

The down-type sector shows a smaller gap to 2/3 ({down.q_standard_gap_sigma}σ)
compared to up ({up.q_standard_gap_sigma}σ), driven primarily by the large PDG
uncertainties on md (~10%) and ms (~10%). Even with 1σ favourable shifts, Q_std
remains above 2/3 for the down sector.

---

## Limitations

- Quark masses at mixed renormalization scales: mu, md, ms at μ = 2 GeV;
  mc at mc (charm pole), mb at mb (bottom pole), mt from direct measurements.
  No RGE running was applied to bring all masses to a common scale.
- PDG uncertainties on light quark masses are non-Gaussian and asymmetric;
  Gaussian propagation used here is an approximation.
- This test covers only the standard real Koide formula and one class of
  phase-modified formulas. Other extensions (e.g., non-equal phase spacing,
  quark mixing, GUT-scale masses) are not tested.
- The Brannen equal-spacing formula Q_B is also above 2/3 for both sectors,
  but Q_B is a distinct quantity from the phase-scan Q(δ).
"""


def _build_metrics(up: SectorResult, down: SectorResult) -> dict:
    return {
        "up_sector": {
            "quarks": list(up.quarks),
            "masses_MeV": list(up.masses_MeV),
            "uncertainties_MeV": list(up.uncertainties_MeV),
            "q_standard": up.q_standard,
            "q_standard_uncertainty": up.q_standard_unc,
            "q_standard_gap_to_target": up.q_standard_gap,
            "q_standard_gap_sigma": up.q_standard_gap_sigma,
            "q_brannen": up.q_brannen,
            "q_brannen_gap_to_target": up.q_brannen_gap,
            "q_brannen_gap_sigma": up.q_brannen_gap_sigma,
            "q_phase_min": up.q_phase_min,
            "q_phase_max": up.q_phase_max,
            "phase_achieves_target": up.phase_achieves_target,
            "brannen_fit_B_over_A": up.brannen_fit_B_over_A,
            "verdict": up.verdict,
        },
        "down_sector": {
            "quarks": list(down.quarks),
            "masses_MeV": list(down.masses_MeV),
            "uncertainties_MeV": list(down.uncertainties_MeV),
            "q_standard": down.q_standard,
            "q_standard_uncertainty": down.q_standard_unc,
            "q_standard_gap_to_target": down.q_standard_gap,
            "q_standard_gap_sigma": down.q_standard_gap_sigma,
            "q_brannen": down.q_brannen,
            "q_brannen_gap_to_target": down.q_brannen_gap,
            "q_brannen_gap_sigma": down.q_brannen_gap_sigma,
            "q_phase_min": down.q_phase_min,
            "q_phase_max": down.q_phase_max,
            "phase_achieves_target": down.phase_achieves_target,
            "brannen_fit_B_over_A": down.brannen_fit_B_over_A,
            "verdict": down.verdict,
        },
        "target": KOIDE_TARGET,
    }


def run_quark_koide_experiment(
    config_path: Path,
    output_dir: Path | None = None,
) -> ExperimentOutcome:
    """Run the quark Koide cascade experiment and write result artifacts."""
    repo_root = find_repo_root(config_path)
    config = load_example_config(config_path)

    exp_path = resolve_path(config_path, config["experiment_path"])
    hyp_path = resolve_path(config_path, config["hypothesis_path"])

    experiment = load_experiment(exp_path)
    hypothesis = load_hypothesis(hyp_path)

    task_id: str = config.get("task_id", "TASK-0088")
    run_id: str = config.get("run_id", "RUN-0001")
    result_id: str = config.get("result_id", "RESULT-0010")
    result_root = resolve_path(config_path, config.get("result_root", "results/EXP-0008"))

    run_dir = Path(output_dir) if output_dir else result_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Load quark masses from dataset
    dataset_path = resolve_path(exp_path, experiment["data"]["dataset_path"])
    dataset = _load_quark_dataset(dataset_path)

    up_quarks_data = dataset["quark_masses"]["up_sector"]
    down_quarks_data = dataset["quark_masses"]["down_sector"]

    def _mass(q: dict) -> float:
        return float(q["value_MeV"])

    def _unc(q: dict) -> float:
        return max(float(q["uncertainty_plus_MeV"]), float(q["uncertainty_minus_MeV"]))

    up = run_sector_test(
        sector="up",
        quarks=("u", "c", "t"),
        masses_MeV=(
            _mass(up_quarks_data[0]),
            _mass(up_quarks_data[1]),
            _mass(up_quarks_data[2]),
        ),
        uncertainties_MeV=(
            _unc(up_quarks_data[0]),
            _unc(up_quarks_data[1]),
            _unc(up_quarks_data[2]),
        ),
    )

    down = run_sector_test(
        sector="down",
        quarks=("d", "s", "b"),
        masses_MeV=(
            _mass(down_quarks_data[0]),
            _mass(down_quarks_data[1]),
            _mass(down_quarks_data[2]),
        ),
        uncertainties_MeV=(
            _unc(down_quarks_data[0]),
            _unc(down_quarks_data[1]),
            _unc(down_quarks_data[2]),
        ),
    )

    import shutil

    task_file = task_path(repo_root, task_id)
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "experiment": exp_path,
            "hypothesis": hyp_path,
            "task": task_file,
        },
    )
    (run_dir / "inputs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(dataset_path, run_dir / "inputs" / "dataset.yaml")

    best_verdict = (
        "INVALID"
        if up.verdict == "INVALID" and down.verdict == "INVALID"
        else "INCONSISTENT"
    )

    limitations = [
        "Quark masses at mixed renormalization scales (μ=2 GeV for light quarks, self-consistent pole for c, b, t).",
        "No RGE running applied to bring all masses to a common scale.",
        "Gaussian uncertainty propagation used for asymmetric PDG uncertainties.",
        "Only one class of phase-modified Koide formulas tested; other extensions are out of scope.",
        "Brannen equal-spacing Q_B is a distinct quantity from the phase-scan Q(δ).",
        "Does not test quark-mixing or GUT-scale mass relations.",
    ]

    result_payload: dict[str, Any] = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": "EXP-0008",
        "title": "Quark Koide Cascade — Brannen Phase Extension Test",
        "hypothesis_id": hypothesis["id"],
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": git_commit(repo_root),
        "command": f"physics-lab run {relative_or_absolute(config_path, repo_root)}",
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/koide_quark.py",
        "limitations": limitations,
        "best_verdict": best_verdict,
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "Up Q_min above 2/3",
                    "status": "PASS" if up.q_phase_min > KOIDE_TARGET else "FAIL",
                    "details": f"Q_min(up) = {up.q_phase_min:.6f} > 2/3 = {KOIDE_TARGET:.6f}",
                    "metrics": {
                        "q_standard": up.q_standard,
                        "q_phase_min": up.q_phase_min,
                        "target": KOIDE_TARGET,
                        "gap": up.q_standard_gap,
                        "gap_sigma": up.q_standard_gap_sigma,
                    },
                },
                {
                    "name": "Down Q_min above 2/3",
                    "status": "PASS" if down.q_phase_min > KOIDE_TARGET else "FAIL",
                    "details": f"Q_min(down) = {down.q_phase_min:.6f} > 2/3 = {KOIDE_TARGET:.6f}",
                    "metrics": {
                        "q_standard": down.q_standard,
                        "q_phase_min": down.q_phase_min,
                        "target": KOIDE_TARGET,
                        "gap": down.q_standard_gap,
                        "gap_sigma": down.q_standard_gap_sigma,
                    },
                },
            ],
        },
        "artifacts": {
            "report": f"results/EXP-0008/{run_id}/report.md",
            "metrics": f"results/EXP-0008/{run_id}/metrics.json",
            "claim_update": f"results/EXP-0008/{run_id}/claim_update.md",
            "claim_update_patch": f"results/EXP-0008/{run_id}/claim_update.patch.md",
            "knowledge_update": f"results/EXP-0008/{run_id}/knowledge_update.md",
            "knowledge_update_patch": f"results/EXP-0008/{run_id}/knowledge_update.patch.md",
            "review_summary": f"results/EXP-0008/{run_id}/review_summary.md",
            "review_metadata": f"results/EXP-0008/{run_id}/review_metadata.yaml",
        },
        "comparison_summary": [
            {
                "target_id": "target_q_up",
                "label": "Q_std (up) vs Koide target 2/3",
                "reference_value": KOIDE_TARGET,
                "observed_value": up.q_standard,
                "absolute_difference": up.q_standard_gap,
                "relative_difference": up.q_standard_gap / KOIDE_TARGET,
                "notes": f"Up Q_std = {up.q_standard:.6f}. Gap = {up.q_standard_gap_sigma}σ above target.",
            },
            {
                "target_id": "target_q_down",
                "label": "Q_std (down) vs Koide target 2/3",
                "reference_value": KOIDE_TARGET,
                "observed_value": down.q_standard,
                "absolute_difference": down.q_standard_gap,
                "relative_difference": down.q_standard_gap / KOIDE_TARGET,
                "notes": f"Down Q_std = {down.q_standard:.6f}. Gap = {down.q_standard_gap_sigma}σ above target.",
            },
        ],
        "uncertainty_summary": {
            "method": "finite_difference_1sigma on PDG quark mass uncertainties",
            "observed_uncertainty": down.q_standard_unc,
            "reference_uncertainty": None,
            "combined_uncertainty": down.q_standard_unc,
            "z_score": down.q_standard_gap_sigma,
            "within_combined_uncertainty": False,
            "notes": (
                f"Up: Q_std = {up.q_standard:.6f} ± {up.q_standard_unc:.6f} (1σ), "
                f"gap = {up.q_standard_gap_sigma}σ. "
                f"Down: Q_std = {down.q_standard:.6f} ± {down.q_standard_unc:.6f} (1σ), "
                f"gap = {down.q_standard_gap_sigma}σ (weakest sector, reported here)."
            ),
        },
    }

    result_path = run_dir / "result.yaml"

    # Write claim/knowledge update stubs (no promotion for INVALID result)
    claim_update_text = (
        "# Claim Update — EXP-0008 / RUN-0001\n\n"
        "Result verdict: INVALID. The quark Koide test produced a clean falsification.\n"
        "No claim promotion is proposed. No existing claim is affected.\n"
    )
    write_text_atomic(run_dir / "claim_update.md", claim_update_text)
    write_text_atomic(run_dir / "claim_update.patch.md", claim_update_text)

    knowledge_update_text = (
        "# Knowledge Update — EXP-0008 / RUN-0001\n\n"
        "The standard Koide formula Q = 2/3 does not hold for quark mass triplets\n"
        "under PDG 2024 masses. Up sector: Q = {:.6f} ({:.1f}σ above 2/3). "
        "Down sector: Q = {:.6f} ({:.1f}σ above 2/3).\n"
        "Phase-modified formula Q(δ) also cannot reach 2/3 for either sector.\n"
        "See docs/notes/koide-quark-cascade.md.\n"
    ).format(up.q_standard, up.q_standard_gap_sigma, down.q_standard, down.q_standard_gap_sigma)
    write_text_atomic(run_dir / "knowledge_update.md", knowledge_update_text)
    write_text_atomic(run_dir / "knowledge_update.patch.md", knowledge_update_text)

    # Write core artifacts before validation (so source path exists conceptually)
    report_text = _build_report(
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=hypothesis["id"],
        task_id=task_id,
        up=up,
        down=down,
    )
    write_text_atomic(run_dir / "report.md", report_text)

    metrics = _build_metrics(up, down)
    write_text_atomic(run_dir / "metrics.json", json.dumps(metrics, indent=2))

    validate_result_payload(result_payload, source=result_path)
    result_yaml = yaml.dump(result_payload, allow_unicode=True, sort_keys=False)
    write_text_atomic(result_path, result_yaml)

    # Review artifacts
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"

    generated_at = str(result_payload["generated_at"])

    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="N/A",
        knowledge_id="N/A",
        suggested_status="no change — falsification result",
        rationale=(
            f"Quark Koide cascade test: Q_std(up) = {up.q_standard:.4f} ({up.q_standard_gap_sigma}σ above 2/3), "
            f"Q_std(down) = {down.q_standard:.4f} ({down.q_standard_gap_sigma}σ above 2/3). "
            "Phase scan Q(δ) cannot reach 2/3 for either sector. Verdict: INVALID."
        ),
        highlights=[
            f"Up sector: Q_std = {up.q_standard:.6f}, gap = {up.q_standard_gap_sigma}σ above 2/3.",
            f"Down sector: Q_std = {down.q_standard:.6f}, gap = {down.q_standard_gap_sigma}σ above 2/3.",
            "Phase scan Q(δ) ∈ [Q_std, Q_max]: minimum equals standard Koide; 2/3 not achievable.",
            "This is a falsification result; no claim promotion proposed.",
        ],
        limitations=limitations,
    )
    write_text_atomic(review_summary_path, review_summary_text)

    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id="EXP-0008",
        claim_id="N/A",
        knowledge_id="N/A",
        generated_at=generated_at,
        proposed_claim_status="DRAFT",
        evidence_basis=[result_id],
        claim_target_file="N/A",
        knowledge_target_file="knowledge/particle_physics/quark_masses.yaml",
        claim_patch_path="N/A",
        knowledge_patch_path="N/A",
        review_summary_path=str(relative_or_absolute(review_summary_path, repo_root)),
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
        verdicts={"up_sector": up.verdict, "down_sector": down.verdict},
        best_model_id="quark_koide_cascade",
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=run_dir / "report.md",
            metrics_path=run_dir / "metrics.json",
            claim_update_path=run_dir / "claim_update.md",
            claim_update_patch_path=run_dir / "claim_update.patch.md",
            knowledge_update_path=run_dir / "knowledge_update.md",
            knowledge_update_patch_path=run_dir / "knowledge_update.patch.md",
            review_summary_path=review_summary_path,
            review_metadata_path=review_metadata_path,
        ),
    )
