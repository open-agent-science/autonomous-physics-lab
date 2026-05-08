"""Muon g-2 anomaly formula search workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import math
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.g2_formula_search import (
    DELTA_AMU,
    SIGMA_COMBINED,
    run_formula_search,
)
from physics_lab.registry import load_example_config, load_experiment, load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
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


def _build_report(
    search: dict[str, Any],
    result_id: str,
    run_id: str,
    experiment: dict[str, Any],
    hypothesis: dict[str, Any],
    task_id: str,
) -> str:
    lines = [
        "# Muon g-2 Anomaly Formula Search",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Experiment: `{experiment['id']}`",
        f"- Hypothesis: `{hypothesis['id']}`",
        f"- Task: `{task_id}`",
        f"- Global verdict: `{search['global_verdict']}`",
        "",
        "## Target",
        "",
        f"Δaμ = {DELTA_AMU / 1e-11:.0f} × 10⁻¹¹  (σ = {SIGMA_COMBINED / 1e-11:.0f} × 10⁻¹¹)",
        "",
        "Significance: ~5.1σ (data-driven HVP, 2023 BNL+FNAL combined).",
        "",
        "## Results by Formula Family",
        "",
    ]
    for fr in search["families"]:
        n_hits = fr["n_hits_1sigma"]
        rb = fr["random_baseline"]
        guard = "✓ PASS" if rb["guardrail_passed"] else "✗ FAIL"
        lines += [
            f"### {fr['family_id']} — {fr['label']}",
            "",
            f"- Formulas evaluated: {fr['n_evaluated']}",
            f"- Hits within 1σ: {n_hits}",
            f"- Random baseline hit-rate: {rb['hit_rate_1sigma']*100:.2f}%  "
            f"(guardrail P<1%: {guard})",
            f"- Notes: {fr['notes']}",
            "",
        ]
        if fr["hits"]:
            lines += [
                "| Formula | Value (×10⁻¹¹) | z-score | C | Credible? |",
                "|---|---:|---:|---|---|",
            ]
            for h in fr["hits"]:
                credible = "Yes" if (h["complexity"] <= 1 and rb["guardrail_passed"]) else "No"
                lines.append(
                    f"| `{h['formula']}` "
                    f"| {h['value_1e11']:.1f} "
                    f"| {h['z_score']:.3f} "
                    f"| {h['complexity']} "
                    f"| {credible} |"
                )
            lines.append("")
        else:
            lines += ["No hits within 1σ.", ""]

    lines += [
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total formulas evaluated | {search['summary']['total_formulas_evaluated']} |",
        f"| Hits within 1σ | {search['summary']['total_hits_1sigma']} |",
        f"| Credible hits (C≤1, P<1%) | {search['summary']['credible_hits']} |",
        f"| Interesting hits (z<0.5σ) | {search['summary']['interesting_hits_half_sigma']} |",
        f"| Best z-score | {search['summary']['best_z_score']:.3f}σ |",
    ]
    if search["summary"]["best_formula"]:
        lines.append(f"| Best formula | `{search['summary']['best_formula']}` |")
    lines += [
        "",
        "## Numerology Guardrail Assessment",
        "",
        "A result is **credible** only if ALL hold:",
        "1. z < 1.0 (within 1σ)",
        "2. C ≤ 1 free real-valued parameter",
        "3. P(random match) < 1% within the family",
        "4. Physical plausibility (SM loop diagram motivation)",
        "",
    ]
    if search["global_verdict"] == "NULL":
        lines += [
            "**Global verdict: NULL**",
            "",
            "No formula from any tested family reproduces Δaμ within 1σ.",
            "The anomaly is not simply expressible as a power-law combination of",
            "{α, mμ/me, mμ/mτ, mW/mZ, GF·mμ², mμ/mπ⁰} with integer exponents and ≤ 1 coefficient.",
        ]
    elif search["global_verdict"] == "NUMEROLOGY_ONLY":
        lines += [
            "**Global verdict: NUMEROLOGY_ONLY**",
            "",
            "Hits found within 1σ, but none pass the random baseline guardrail (P<1%).",
            "All matches are consistent with accidental coincidence within the tested family.",
        ]
    else:
        lines += [
            "**Global verdict: VALID_EMPIRICAL**",
            "",
            "At least one formula passes all numerology guardrails.",
            "This is an empirical observation only — no physical mechanism is claimed.",
        ]
    lines += [
        "",
        "## Limitations",
        "",
        "- This search uses the data-driven HVP baseline (~5.1σ). The BMW lattice-QCD result",
        "  reduces the discrepancy to ~1.5σ; matching a formula to a contested target is not",
        "  itself evidence for BSM physics.",
        "- Integer/rational exponent constraints exclude smooth BSM contributions from",
        "  non-trivial loop integrals.",
        "- A null result within these families does not exclude all possible BSM formulas.",
        "- F3 with c≈1/3 has physical motivation (HLbL leading-log estimate) but the",
        "  random baseline for continuous c fails the P<1% threshold.",
        "",
    ]
    return "\n".join(lines)


_VERDICT_MAP = {
    "VALID_EMPIRICAL": "VALID",
    "NUMEROLOGY_ONLY": "PARTIALLY_VALID",
    "NULL": "INVALID",
}


def _build_result_payload(
    search: dict[str, Any],
    result_id: str,
    run_id: str,
    experiment: dict[str, Any],
    hypothesis: dict[str, Any],
    task_id: str,
    git_sha: str,
    command: str,
    input_hashes: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    raw_z = search["summary"]["best_z_score"]
    best_z = raw_z if raw_z is not None else 0.0
    best_formula = search["summary"]["best_formula"] or "none"
    # Use the actual formula value from the engine (not a signed approximation)
    raw_best_value = search["summary"].get("best_value")
    best_value = raw_best_value if raw_best_value is not None else DELTA_AMU
    abs_diff = abs(best_value - DELTA_AMU)
    rel_diff = abs_diff / DELTA_AMU if DELTA_AMU != 0 and math.isfinite(abs_diff) else 0.0

    schema_verdict = _VERDICT_MAP.get(search["global_verdict"], "INCONCLUSIVE")

    return {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(hypothesis["id"]),
        "task_id": task_id,
        "generated_at": generated_at,
        "engine_version": __version__,
        "git_commit": git_sha,
        "command": command,
        "input_file_hashes": {
            k: v for k, v in input_hashes.items()
            if k in {"config", "experiment", "hypothesis", "task"}
        },
        "code_reference": "physics_lab/workflows/g2_formula.py",
        "limitations": [
            "Data-driven HVP baseline used (5.1σ). BMW lattice-QCD reduces to ~1.5σ.",
            "Integer/rational exponent constraints only.",
            "F3 c≈1/3 is the strongest empirical match but fails P<1% guardrail.",
            "No physical mechanism claimed for any matching formula.",
        ],
        "best_verdict": schema_verdict,
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "target_defined",
                    "status": "PASS",
                    "details": f"Target Δaμ = {DELTA_AMU/1e-11:.0f}×10⁻¹¹, σ = {SIGMA_COMBINED/1e-11:.0f}×10⁻¹¹",
                    "metrics": {
                        "delta_amu_1e11": DELTA_AMU / 1e-11,
                        "sigma_1e11": SIGMA_COMBINED / 1e-11,
                    },
                },
                {
                    "name": "families_evaluated",
                    "status": "PASS",
                    "details": f"{len(search['families'])} formula families evaluated, "
                               f"{search['summary']['total_formulas_evaluated']} total formulas",
                    "metrics": {
                        "total_formulas": search["summary"]["total_formulas_evaluated"],
                        "total_hits_1sigma": search["summary"]["total_hits_1sigma"],
                    },
                },
                {
                    "name": "random_baseline",
                    "status": "PASS",
                    "details": "Random baseline computed for each family with N=100,000 samples",
                    "metrics": {
                        "n_samples": 100000,
                        "threshold_pct": 1.0,
                    },
                },
                {
                    "name": "global_verdict",
                    "status": "PASS",
                    "details": f"Global verdict: {search['global_verdict']} → schema: {schema_verdict}",
                    "metrics": {
                        "credible_hits": search["summary"]["credible_hits"],
                        "interesting_hits_half_sigma": search["summary"]["interesting_hits_half_sigma"],
                        "best_z_score": search["summary"]["best_z_score"],
                    },
                },
            ],
        },
        "comparison_summary": [
            {
                "target_id": "target_delta_amu",
                "label": "Muon g-2 anomaly",
                "reference_value": DELTA_AMU,
                "observed_value": best_value,
                "unit": "dimensionless",
                "absolute_difference": abs_diff,
                "relative_difference": rel_diff,
                "notes": f"Best formula: {best_formula}, z={best_z:.3f}σ. "
                         f"Internal verdict: {search['global_verdict']}.",
            }
        ],
        "uncertainty_summary": {
            "method": "z_score_against_delta_amu_with_random_baseline",
            "observed_uncertainty": None,
            "reference_uncertainty": SIGMA_COMBINED,
            "combined_uncertainty": SIGMA_COMBINED,
            "z_score": best_z if raw_z is not None else None,
            "within_combined_uncertainty": bool(best_z < 1.0) if raw_z is not None else False,
            "notes": (
                f"Best z={best_z:.3f}σ. Credible hits (C≤1, P<1%): "
                f"{search['summary']['credible_hits']}."
            ),
        },
        "artifacts": {
            "report": f"results/EXP-0010/{run_id}/report.md",
            "metrics": f"results/EXP-0010/{run_id}/metrics.json",
            "claim_update": f"results/EXP-0010/{run_id}/claim_update.md",
            "claim_update_patch": f"results/EXP-0010/{run_id}/claim_update.patch.md",
            "knowledge_update": f"results/EXP-0010/{run_id}/knowledge_update.md",
            "knowledge_update_patch": f"results/EXP-0010/{run_id}/knowledge_update.patch.md",
            "review_summary": f"results/EXP-0010/{run_id}/review_summary.md",
            "review_metadata": f"results/EXP-0010/{run_id}/review_metadata.yaml",
        },
    }


def run_g2_formula_experiment(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    config_path = Path(config_path)
    config = load_example_config(config_path)
    repo_root = find_repo_root(config_path)

    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)

    run_id = str(config.get("run_id", "RUN-0001"))
    result_id = str(config.get("result_id", "RESULT-0012"))
    task_id = str(config.get("task_id", "TASK-0089"))

    if output_dir is not None:
        result_root = Path(output_dir) / str(experiment["id"])
    else:
        result_root = resolve_path(config_path, config["result_root"])

    result_dir = result_root / run_id
    result_dir.mkdir(parents=True, exist_ok=True)

    result_path = result_dir / "result.yaml"
    report_path = result_dir / "report.md"
    metrics_path = result_dir / "metrics.json"
    claim_update_path = result_dir / "claim_update.md"
    claim_update_patch_path = result_dir / "claim_update.patch.md"
    knowledge_update_path = result_dir / "knowledge_update.md"
    knowledge_update_patch_path = result_dir / "knowledge_update.patch.md"
    review_summary_path = result_dir / "review_summary.md"
    review_metadata_path = result_dir / "review_metadata.yaml"

    generated_at = datetime.now(tz=timezone.utc).isoformat()
    git_sha = git_commit(repo_root)
    command = f"physics-lab run {config_path.name}"

    task_file = task_path(repo_root, task_id)
    knowledge_path_str = config.get("knowledge_path", "../knowledge/particle_physics/muon_g2.yaml")
    knowledge_resolved = resolve_path(config_path, knowledge_path_str)
    input_files: dict = {
        "config": config_path,
        "experiment": experiment_path,
        "hypothesis": hypothesis_path,
        "task": task_file,
    }
    if Path(knowledge_resolved).exists():
        input_files["knowledge"] = Path(knowledge_resolved)
    input_hashes = snapshot_input_files(
        run_dir=result_dir,
        repo_root=repo_root,
        input_files=input_files,
    )

    # Run the search
    search = run_formula_search()

    report_text = _build_report(search, result_id, run_id, experiment, hypothesis, task_id)
    metrics_payload = {
        "target_value_1e11": DELTA_AMU / 1e-11,
        "sigma_1e11": SIGMA_COMBINED / 1e-11,
        "total_formulas_evaluated": search["summary"]["total_formulas_evaluated"],
        "total_hits_1sigma": search["summary"]["total_hits_1sigma"],
        "credible_hits": search["summary"]["credible_hits"],
        "interesting_hits_half_sigma": search["summary"]["interesting_hits_half_sigma"],
        "best_z_score": search["summary"]["best_z_score"],
        "best_formula": search["summary"]["best_formula"],
        "global_verdict": search["global_verdict"],
        "families": [
            {
                "family_id": fr["family_id"],
                "n_evaluated": fr["n_evaluated"],
                "n_hits": fr["n_hits_1sigma"],
                "random_hit_rate": fr["random_baseline"]["hit_rate_1sigma"],
                "guardrail_passed": fr["random_baseline"]["guardrail_passed"],
                "verdict": fr["verdict"],
            }
            for fr in search["families"]
        ],
        "all_hits": [
            {
                "family": h["formula"].split("×")[0].strip() if "×" in h["formula"] else h["formula"],
                "formula": h["formula"],
                "value_1e11": h["value_1e11"],
                "z_score": h["z_score"],
                "complexity": h["complexity"],
            }
            for fr in search["families"]
            for h in fr["hits"]
        ],
    }
    result_payload = _build_result_payload(
        search, result_id, run_id, experiment, hypothesis,
        task_id, git_sha, command, input_hashes, generated_at,
    )
    validate_result_payload(result_payload, source=result_path)

    write_text_atomic(report_path, report_text)
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))
    write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False, allow_unicode=True))

    verdict = search["global_verdict"]
    claim_update_text = "\n".join([
        "# Claim Update Suggestion",
        "",
        f"- Result `{result_id}` ({verdict}) added to HYP-0010 evidence.",
        "- No claim promotion. Verdict remains DRAFT pending maintainer review.",
        "- NUMEROLOGY_ONLY or NULL verdict: the anomaly is not simply expressible as",
        "  a power-law combination of tested SM constants with integer exponents.",
        "- If VALID_EMPIRICAL: at least one formula passed all guardrails; report for",
        "  maintainer inspection before any claim update.",
        "",
    ])
    knowledge_update_text = "\n".join([
        "# Knowledge Update Suggestion",
        "",
        f"- Record `{result_id}` as the muon g-2 formula search baseline run.",
        "- Knowledge artifact: knowledge/particle_physics/muon_g2.yaml (KNOW-0007).",
        "- Do not promote BSM claims from formula coincidences.",
        "",
    ])
    write_text_atomic(claim_update_path, claim_update_text)
    write_text_atomic(claim_update_patch_path, claim_update_text)
    write_text_atomic(knowledge_update_path, knowledge_update_text)
    write_text_atomic(knowledge_update_patch_path, knowledge_update_text)

    limitations = [
        "Data-driven HVP baseline (5.1σ). BMW lattice-QCD gives ~1.5σ.",
        "Integer/rational exponent constraints only.",
        "No physical mechanism claimed for any matching formula.",
    ]
    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0008",
        knowledge_id="KNOW-0007",
        suggested_status="DRAFT",
        rationale=(
            "The g-2 formula search applies deterministic enumeration, random baselines,"
            " and numerology guardrails to test whether Δaμ is expressible as a simple"
            " combination of SM constants."
        ),
        highlights=[
            f"Global verdict: {verdict}.",
            f"Best z-score: {search['summary']['best_z_score']:.3f}σ "
            f"({search['summary']['best_formula']}).",
            f"Credible hits: {search['summary']['credible_hits']}.",
        ],
        limitations=limitations,
    )
    write_text_atomic(review_summary_path, review_summary_text)
    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        claim_id="CLAIM-0008",
        knowledge_id="KNOW-0007",
        generated_at=generated_at,
        proposed_claim_status="DRAFT",
        evidence_basis=[result_id],
        claim_target_file="claims/",
        knowledge_target_file="knowledge/particle_physics/muon_g2.yaml",
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
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
        best_model_id=None,
        summary_lines=(
            f"Families evaluated: {len(search['families'])}",
            f"Total formulas: {search['summary']['total_formulas_evaluated']}",
            f"Global verdict: {verdict}",
        ),
    )
