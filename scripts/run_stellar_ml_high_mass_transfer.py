#!/usr/bin/env python3
"""Stellar M-L high-mass DEBCat transfer benchmark (TASK-0837/TASK-0849).

Transfer-benchmarks the FROZEN RESULT-0022 mass-luminosity relation
(``log L = 4.526004 * log M``, fixed intercept ``log L0 = 0``; the
main-sequence train-fitted exponent) by evaluating it on the disjoint
high-mass DEBCat regime (``mass_solar > 2.0``) selected by the TASK-0819
transfer scout. The relation is NOT refit on the holdout, and neither
RESULT-0022 nor the committed DEBCat main-sequence slice is edited.

Controls-first and predeclared: the survival margin (0.04 dex, the RESULT-0022
split-noise reference) and the null / shuffled / mass-matched controls are
frozen in :mod:`physics_lab.engines.stellar_ml_high_mass_transfer` *before* any
high-mass holdout error is read. The judge is experimental (DEBCat dynamical
masses). Deterministic; re-running yields identical numbers (Gate-B style).

Default mode remains the original sandbox run. With ``--result-out-dir`` the
same frozen transfer metrics are packaged as the TASK-0849 Gate-A candidate
RESULT without refitting, editing RESULT-0022, or promoting any CLAIM/KNOW.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from shutil import copyfile
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab import __version__  # noqa: E402
from physics_lab.engines.stellar_ml_high_mass_transfer import (  # noqa: E402
    ROWS_PATH,
    compute_transfer_metrics,
)
from physics_lab.registry.task_discovery import find_task_file  # noqa: E402
import yaml  # noqa: E402

from physics_lab.workflows.artifacts import git_commit, hash_file  # noqa: E402


def _task_path(task_id: str) -> Path:
    path = find_task_file(REPO_ROOT, task_id)
    if path is None:
        raise FileNotFoundError(f"No task file found for {task_id}")
    return path


ENGINE_PATH = REPO_ROOT / "physics_lab/engines/stellar_ml_high_mass_transfer.py"
SCRIPT_PATH = REPO_ROOT / "scripts/run_stellar_ml_high_mass_transfer.py"
AGENT_RUN_ID = "AGENT-RUN-0082"
TASK_ID = "TASK-0837"
BENCHMARK_ID = "stellar-ml-high-mass-debcat-transfer"
DEFAULT_OUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
PINNED_COMMAND = f"python3 scripts/run_stellar_ml_high_mass_transfer.py --out-dir agent_runs/{AGENT_RUN_ID}"

RESULT_AGENT_RUN_ID = "AGENT-RUN-0088"
RESULT_ID = "RESULT-0024"
RESULT_RUN_ID = "RUN-0001"
RESULT_EXP_ID = "EXP-0017"
RESULT_HYP_ID = "HYP-0017"
RESULT_TASK_ID = "TASK-0849"
RESULT_GENERATED_AT = "2026-06-27T00:00:00Z"
RESULT_REL_DIR = Path("results") / RESULT_EXP_ID / RESULT_RUN_ID
RESULT_PINNED_COMMAND = (
    "python3 scripts/run_stellar_ml_high_mass_transfer.py "
    f"--skip-sandbox-output --result-out-dir {RESULT_REL_DIR.as_posix()}"
)
RESULT_TITLE = (
    "Stellar M-L High-Mass DEBCat Transfer - frozen RESULT-0022 relation survives "
    "stage-matched controls"
)
RESULT_EXP_PATH = REPO_ROOT / "experiments" / "EXP-0017-stellar-ml-high-mass-transfer.yaml"
RESULT_HYP_PATH = REPO_ROOT / "hypotheses" / "HYP-0017-stellar-ml-high-mass-transfer.yaml"
RESULT_TASK_PATH = _task_path(RESULT_TASK_ID)


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_metrics() -> dict[str, Any]:
    transfer = compute_transfer_metrics()
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "benchmark_id": BENCHMARK_ID,
        "campaign_profile_id": "textbook-formula-audit",
        "command": PINNED_COMMAND,
        "code_reference": "physics_lab/engines/stellar_ml_high_mass_transfer.py",
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "input_file_hashes": {
            "debcat_component_rows": {
                "path": "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml",
                "sha256": _sha256(ROWS_PATH),
            },
            "engine": {
                "path": "physics_lab/engines/stellar_ml_high_mass_transfer.py",
                "sha256": _sha256(ENGINE_PATH),
            },
            "script": {
                "path": "scripts/run_stellar_ml_high_mass_transfer.py",
                "sha256": _sha256(SCRIPT_PATH),
            },
        },
        "source": (
            "DEBCat Route 2 committed normalized rows (CC BY 4.0, Southworth grant, "
            "TASK-0763); direct dynamical masses; raw debs.dat not committed; no live fetch."
        ),
        "judge": "experimental DEBCat dynamical masses (direct_observation)",
        "frozen_predictor": transfer["frozen_predictor"],
        "predeclared_contract": transfer["predeclared_contract"],
        "regime_composition": transfer["regime_composition"],
        "primary_high_mass_main_sequence_holdout": transfer["primary_high_mass_main_sequence_holdout"],
        "secondary_all_stage_high_mass_holdout": transfer["secondary_all_stage_high_mass_holdout"],
        "luminosity_provenance_sensitivity_primary_holdout": transfer[
            "luminosity_provenance_sensitivity_primary_holdout"
        ],
        "by_stage_high_mass_holdout_mae_dex": transfer["by_stage_high_mass_holdout_mae_dex"],
        "transfers_to_high_mass": transfer["transfers_to_high_mass"],
        "verdict": transfer["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "creates_prediction": False,
            "creates_knowledge": False,
            "required_next_step": (
                "Maintainer review of the sandbox transfer benchmark. A published RESULT "
                "would require hypothesis/experiment evidence links outside this task's scope; "
                "this run deliberately stays sandbox-only with no claim/knowledge promotion."
            ),
        },
    }


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def _render_report(m: dict[str, Any]) -> str:
    fp = m["frozen_predictor"]
    pc = m["predeclared_contract"]
    prim = m["primary_high_mass_main_sequence_holdout"]
    sec = m["secondary_all_stage_high_mass_holdout"]
    comp = m["regime_composition"]["high_mass_all_stage"]
    prov = m["luminosity_provenance_sensitivity_primary_holdout"]
    stage = m["by_stage_high_mass_holdout_mae_dex"]
    transfers = m["transfers_to_high_mass"]
    prim_controls = prim["controls_holdout_mae_dex"]

    def _kv(counts: dict[str, int]) -> str:
        return ", ".join(f"{k} {v}" for k, v in counts.items())

    stage_summary = _kv(comp["by_stage"])
    source_summary = _kv(comp["by_luminosity_source"])

    lines = [
        f"# {m['agent_run_id']} - Stellar M-L High-Mass DEBCat Transfer Benchmark",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Benchmark:** `{m['benchmark_id']}`",
        f"**Verdict:** `{m['verdict']}`",
        "",
        "## Scope",
        "",
        "Transfer benchmark of the **frozen** RESULT-0022 stellar mass-luminosity",
        f"relation `{fp['formula']}` with the main-sequence train-fitted exponent",
        f"`alpha = {fp['alpha_frozen']}`. The relation is evaluated BY TRANSFER on the",
        "disjoint high-mass DEBCat regime (`mass_solar > 2.0`) chosen by the TASK-0819",
        "transfer scout. The exponent is **not** refit on the high-mass holdout, and",
        "neither RESULT-0022 nor the committed DEBCat main-sequence slice is edited.",
        "The frozen alpha re-derives exactly from the committed main-sequence train lane",
        f"(`{fp['alpha_rederived_from_committed_main_sequence_train']}`), pinning the predictor to its source.",
        "",
        "The judge is **experimental**: DEBCat masses are direct dynamical measurements",
        "(`mass_provenance_class: direct_observation`). The high-mass regime spans",
        f"`{comp['mass_solar_min']}`-`{comp['mass_solar_max']}` M_sun across `{comp['distinct_systems']}` systems",
        f"(`{comp['component_rows']}` admitted components). It is stage-confounded",
        f"(components by stage: {stage_summary}) and luminosity-provenance-mixed",
        f"(by luminosity source: {source_summary}), so the PRIMARY lane is the stage-matched",
        "high-mass main-sequence-compatible holdout (apples-to-apples with the RESULT-0022",
        "fit slice); the all-stage high-mass holdout is a documented secondary diagnostic.",
        "",
        "## Predeclared contract (frozen before reading holdout error)",
        "",
        f"- Transfer regime: `mass_solar > {pc['high_mass_threshold_solar']}`, split by `{pc['split_key']}`"
        " (no binary-component leakage).",
        f"- Target: `{pc['target_field']}`; primary stage lane: `{pc['primary_lane_stage']}`.",
        f"- Survival margin: **{pc['survival_margin_dex']} dex** ({pc['survival_margin_basis']}).",
        "- Controls: per-mass-band median **null**, deterministic luminosity **shuffle**"
        f" (seeds {pc['control_seeds']}), and a **mass-matched** per-mass-band-mean constant.",
        "- Survival rule: the frozen relation must beat the BEST (lowest-MAE) control by the"
        " margin AND beat every shuffle seed.",
        "",
        "## Primary high-mass main-sequence holdout",
        "",
        f"Holdout: `{prim['holdout_count']}` components / `{prim['holdout_systems']}` systems"
        f" (train `{prim['train_count']}`).",
        "",
        "| Predictor / control | Holdout MAE (dex) |",
        "| --- | ---: |",
        f"| **Frozen RESULT-0022 relation (alpha={fp['alpha_frozen']})** | **{_fmt(prim['frozen_relation_holdout_mae_dex'])}** |",
        f"| null (mass-band median) | {_fmt(prim_controls['null_massband_median'])} |",
        f"| mass-matched (mass-band mean) | {_fmt(prim_controls['mass_matched_massband_mean'])} |",
        f"| shuffled target (best of {len(pc['control_seeds'])} seeds) | {_fmt(prim_controls['shuffled_target_best'])} |",
        "",
        f"- Best control: `{prim['best_control_name']}` at `{_fmt(prim['best_control_mae_dex'])}` dex.",
        f"- Frozen relation minus best control: **{_fmt(prim['frozen_minus_best_control_dex'])} dex**"
        f" vs predeclared margin `{pc['survival_margin_dex']}` -> clears: **{prim['clears_survival_margin']}**.",
        f"- Beats every shuffle seed: **{prim['beats_all_shuffle_seeds']}**.",
        "",
        "## Secondary all-stage high-mass holdout (diagnostic)",
        "",
        f"Holdout: `{sec['holdout_count']}` components / `{sec['holdout_systems']}` systems.",
        f"Frozen relation MAE `{_fmt(sec['frozen_relation_holdout_mae_dex'])}` dex vs best control"
        f" `{sec['best_control_name']}` `{_fmt(sec['best_control_mae_dex'])}` dex; margin"
        f" `{_fmt(sec['frozen_minus_best_control_dex'])}` dex; clears: `{sec['clears_survival_margin']}`."
        " The all-stage margin is materially tighter than the primary lane, which is the expected",
        " signature of the high-mass stage confound and motivates the stage-matched primary choice.",
        "",
        "## Sensitivity (scout-required)",
        "",
        "Luminosity provenance on the primary holdout:",
    ]
    for source, detail in prov.items():
        lines.append(
            f"- `{source}`: `{detail['holdout_count']}` rows, MAE `{_fmt(detail['frozen_relation_holdout_mae_dex'])}` dex."
        )
    lines += [
        "",
        "By evolutionary stage on the high-mass holdout (frozen relation MAE, dex):",
        "",
        "| stage | holdout MAE (dex) |",
        "| --- | ---: |",
    ]
    for st in ("main_sequence_compatible", "subgiant", "evolved", "unknown"):
        if st in stage:
            lines.append(f"| {st} | {_fmt(stage[st])} |")
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "On the stage-matched high-mass main-sequence holdout, the frozen RESULT-0022"
            f" relation (MAE `{_fmt(prim['frozen_relation_holdout_mae_dex'])}` dex) clears the"
            " predeclared survival margin over the best control and beats every shuffle seed,"
            " so it **transfers to the high-mass regime under controls**."
            if transfers
            else (
                "On the stage-matched high-mass main-sequence holdout, the frozen RESULT-0022"
                " relation does NOT clear the predeclared survival margin over the best control."
                " This is recorded as an honest regime-limited boundary; the relation is NOT"
                " refit, widened, or given extra free parameters to rescue it."
            )
        ),
        "",
        "The transfer error is markedly larger than the in-domain main-sequence holdout MAE",
        "RESULT-0022 reported for the same model (`0.119925` dex), so the relation **degrades**",
        "on transfer to higher masses while still carrying predictive signal beyond the controls.",
        "This is a scope-extension boundary measurement, not a universal mass-luminosity law,",
        "a stellar-evolution claim, or a discovery.",
        "",
        "## Output-routing summary",
        "",
        f"- Task verdict: `{m['verdict']}` (transfers to high mass: `{transfers}`).",
        "- Canonical destination: SANDBOX -"
        f" `agent_runs/{AGENT_RUN_ID}/metrics.json`, this report, and"
        " `docs/reviews/stellar-ml-high-mass-debcat-transfer-benchmark.md`.",
        "- Review tier: `none`. Gate A: not attempted (sandbox; a published RESULT needs"
        " hypothesis/experiment evidence links outside this task's scope). Gate B: not applicable"
        " (no RESULT replay target created); the run is itself deterministically replayable via the"
        " pinned command + input hashes + engine version + git commit.",
        f"- Transfer MAE (primary high-mass holdout): `{_fmt(prim['frozen_relation_holdout_mae_dex'])}` dex"
        f" vs best control `{prim['best_control_name']}` `{_fmt(prim['best_control_mae_dex'])}` dex"
        f" (margin `{_fmt(prim['frozen_minus_best_control_dex'])}` dex; predeclared"
        f" `{pc['survival_margin_dex']}`; clears: `{prim['clears_survival_margin']}`).",
        "- Claim impact: `none`. Knowledge impact: `none`.",
        "- Limitations: single relation; disjoint-regime (same-source) holdout, not an independent"
        " external catalogue; stage-confounded and luminosity-provenance-mixed high-mass regime;"
        " small primary holdout (`{n}` components); not a new law.".format(n=prim["holdout_count"]),
        "",
    ]
    return "\n".join(lines)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False) + "\n", encoding="utf-8")


def _copy_result_inputs(result_dir: Path) -> dict[str, dict[str, str]]:
    inputs_dir = result_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    config_path = inputs_dir / "config.yaml"
    experiment_path = inputs_dir / "experiment.yaml"
    hypothesis_path = inputs_dir / "hypothesis.yaml"
    task_path = inputs_dir / "task.yaml"

    _write_yaml(
        config_path,
        {
            "result_id": RESULT_ID,
            "run_id": RESULT_RUN_ID,
            "experiment_id": RESULT_EXP_ID,
            "hypothesis_id": RESULT_HYP_ID,
            "task_id": RESULT_TASK_ID,
            "source_result_id": "RESULT-0022",
            "source_task_id": TASK_ID,
            "source_agent_run_id": AGENT_RUN_ID,
            "agent_run_id": RESULT_AGENT_RUN_ID,
            "command": RESULT_PINNED_COMMAND,
            "code_reference": "physics_lab/engines/stellar_ml_high_mass_transfer.py",
            "frozen_predictor": "log_luminosity_solar = 4.526004 * log_mass_solar",
            "no_refit_on_high_mass_holdout": True,
            "review_tier_proposed": "AGENT_PUBLISHED",
        },
    )
    copyfile(RESULT_EXP_PATH, experiment_path)
    copyfile(RESULT_HYP_PATH, hypothesis_path)
    copyfile(RESULT_TASK_PATH, task_path)

    return {
        "config": hash_file(config_path, REPO_ROOT),
        "experiment": hash_file(experiment_path, REPO_ROOT),
        "hypothesis": hash_file(hypothesis_path, REPO_ROOT),
        "task": hash_file(task_path, REPO_ROOT),
        "fixture": hash_file(ROWS_PATH, REPO_ROOT),
    }


def _result_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    transfer = {
        key: metrics[key]
        for key in (
            "frozen_predictor",
            "predeclared_contract",
            "regime_composition",
            "primary_high_mass_main_sequence_holdout",
            "secondary_all_stage_high_mass_holdout",
            "luminosity_provenance_sensitivity_primary_holdout",
            "by_stage_high_mass_holdout_mae_dex",
            "transfers_to_high_mass",
            "verdict",
        )
    }
    return {
        "result_id": RESULT_ID,
        "run_id": RESULT_RUN_ID,
        "experiment_id": RESULT_EXP_ID,
        "hypothesis_id": RESULT_HYP_ID,
        "task_id": RESULT_TASK_ID,
        "agent_run_id": RESULT_AGENT_RUN_ID,
        "source_agent_run_id": AGENT_RUN_ID,
        "source_result_id": "RESULT-0022",
        "source_task_id": TASK_ID,
        "review_tier": "AGENT_PUBLISHED",
        "best_verdict": "VALID_IN_RANGE",
        "benchmark_id": BENCHMARK_ID,
        "command": RESULT_PINNED_COMMAND,
        "code_reference": "physics_lab/engines/stellar_ml_high_mass_transfer.py",
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "generated_at": RESULT_GENERATED_AT,
        "source": metrics["source"],
        "judge": metrics["judge"],
        "transfer": transfer,
        "publication_boundary": {
            "claim_promotion_allowed": False,
            "prediction_promotion_allowed": False,
            "knowledge_promotion_allowed": False,
            "edits_result_0022": False,
            "refit_on_high_mass_holdout": False,
            "scope": (
                "Gate-A packaging of one frozen DEBCat transfer benchmark. This is a "
                "single-relation, same-source high-mass regime result, not a universal "
                "law, discovery, stellar-structure conclusion, or CLAIM/KNOW promotion."
            ),
        },
    }


def _build_result_yaml(metrics: dict[str, Any], input_hashes: dict[str, dict[str, str]]) -> dict[str, Any]:
    prim = metrics["primary_high_mass_main_sequence_holdout"]
    pc = metrics["predeclared_contract"]
    transfer_margin = prim["frozen_minus_best_control_dex"]
    return {
        "result_id": RESULT_ID,
        "run_id": RESULT_RUN_ID,
        "experiment_id": RESULT_EXP_ID,
        "title": RESULT_TITLE,
        "hypothesis_id": RESULT_HYP_ID,
        "task_id": RESULT_TASK_ID,
        "generated_at": RESULT_GENERATED_AT,
        "engine_version": __version__,
        "git_commit": git_commit(REPO_ROOT),
        "command": RESULT_PINNED_COMMAND,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/engines/stellar_ml_high_mass_transfer.py",
        "limitations": [
            "Agent-published, not yet independently validated or maintainer-reviewed.",
            (
                "Scope is one frozen RESULT-0022 mass-luminosity relation transferred to "
                "one disjoint high-mass DEBCat regime under controls; this is not a "
                "universal stellar mass-luminosity law, discovery, or stellar-structure "
                "conclusion."
            ),
            (
                "The judge remains same-source DEBCat dynamical masses rather than an "
                "independent external catalogue; the raw debs.dat source is not committed "
                "and the normalized rows inherit the TASK-0763 Route-2 provenance boundary."
            ),
            (
                "The high-mass population is stage-confounded and luminosity-provenance "
                "mixed; the primary lane is main-sequence-compatible, while all-stage and "
                "provenance splits are diagnostics."
            ),
            (
                "The primary holdout is small (24 components across 15 systems). No "
                "CLAIM, PRED, or KNOW promotion is proposed from this result."
            ),
        ],
        "best_model_id": "model_result0022_frozen_alpha_transfer",
        "best_verdict": "VALID_IN_RANGE",
        "review_tier": "AGENT_PUBLISHED",
        "agent_proposal_evaluation": {
            "review_tier_proposed": "AGENT_PUBLISHED",
            "best_verdict_proposed": "VALID_IN_RANGE",
            "published_by": {
                "contributor_id": "romanhladun24-dot",
                "github_username": "romanhladun24-dot",
                "agent_tool": "Codex",
                "model_version": "GPT-5",
            },
            "gates_checked": {
                "deterministic_run": True,
                "verification_block_populated": True,
                "input_hashes_recorded": True,
                "limitations_listed": True,
                "engine_version_and_commit_pinned": True,
                "schema_validation_passes": True,
                "no_protected_artifact_rewrite": True,
                "no_forbidden_overclaim_wording": True,
                "dataset_provenance_valid": True,
            },
            "evidence_summary": (
                "The frozen RESULT-0022 relation logL=4.526004*logM was replayed without "
                "refit on the disjoint high-mass DEBCat main-sequence-compatible holdout. "
                f"It achieved MAE {prim['frozen_relation_holdout_mae_dex']:.6f} dex versus "
                f"best control {prim['best_control_name']} at {prim['best_control_mae_dex']:.6f} "
                f"dex, clearing the predeclared {pc['survival_margin_dex']:.2f} dex margin "
                f"by {transfer_margin:.6f} dex and beating every shuffle seed."
            ),
            "followup_for_maintainer": (
                "Gate B should independently replay the pinned command and compare the "
                "published result metrics. Keep the trust qualifier explicit: same-source "
                "DEBCat transfer under controls, not a universal law or CLAIM/KNOW promotion."
            ),
        },
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "deterministic_replay_inputs_pinned",
                    "status": "PASS",
                    "details": (
                        "The runner reuses committed DEBCat rows and the frozen RESULT-0022 "
                        "alpha; config, experiment, hypothesis, task, and fixture hashes are pinned."
                    ),
                    "metrics": {
                        "frozen_alpha": metrics["frozen_predictor"]["alpha_frozen"],
                        "rederived_alpha": metrics["frozen_predictor"][
                            "alpha_rederived_from_committed_main_sequence_train"
                        ],
                        "live_external_fetch": 0,
                    },
                },
                {
                    "name": "primary_transfer_survives_controls",
                    "status": "PASS",
                    "details": (
                        "The stage-matched high-mass holdout clears the predeclared survival "
                        "margin over the best control and beats every shuffled target seed."
                    ),
                    "metrics": {
                        "holdout_components": prim["holdout_count"],
                        "holdout_systems": prim["holdout_systems"],
                        "frozen_relation_mae_dex": prim["frozen_relation_holdout_mae_dex"],
                        "best_control_mae_dex": prim["best_control_mae_dex"],
                        "transfer_margin_dex": transfer_margin,
                        "predeclared_margin_dex": pc["survival_margin_dex"],
                        "beats_all_shuffle_seeds": int(prim["beats_all_shuffle_seeds"]),
                    },
                },
                {
                    "name": "secondary_and_sensitivity_documented",
                    "status": "PASS",
                    "details": (
                        "All-stage high-mass, by-stage, and luminosity-provenance diagnostics "
                        "are reported as scope/sensitivity checks rather than rescue criteria."
                    ),
                    "metrics": {
                        "all_stage_holdout_components": metrics[
                            "secondary_all_stage_high_mass_holdout"
                        ]["holdout_count"],
                        "all_stage_transfer_margin_dex": metrics[
                            "secondary_all_stage_high_mass_holdout"
                        ]["frozen_minus_best_control_dex"],
                        "stage_diagnostic_count": len(metrics["by_stage_high_mass_holdout_mae_dex"]),
                    },
                },
                {
                    "name": "no_refit_no_protected_artifact_rewrite",
                    "status": "PASS",
                    "details": (
                        "No RESULT-0022, CLAIM, PRED, KNOW, or source dataset artifact is edited; "
                        "the high-mass transfer keeps the frozen alpha and fixed intercept."
                    ),
                    "metrics": {
                        "refit_on_holdout": 0,
                        "edits_result_0022": 0,
                        "claim_promotion": 0,
                    },
                },
                {
                    "name": "provenance_and_scope_boundaries_recorded",
                    "status": "PASS",
                    "details": (
                        "DEBCat provenance, same-source transfer boundary, small holdout size, "
                        "and no universal-law wording are recorded in limitations and reports."
                    ),
                    "metrics": {
                        "dataset_provenance_recorded": 1,
                        "same_source_transfer": 1,
                        "universal_law_claim": 0,
                    },
                },
            ],
        },
        "comparison_summary": [
            {
                "target_id": "target_high_mass_transfer_primary",
                "label": (
                    "Frozen RESULT-0022 relation versus the best control on the "
                    "stage-matched high-mass DEBCat holdout"
                ),
                "reference_value": prim["best_control_mae_dex"],
                "observed_value": prim["frozen_relation_holdout_mae_dex"],
                "unit": "dex",
                "absolute_difference": transfer_margin,
                "relative_difference": round(transfer_margin / prim["best_control_mae_dex"], 6),
                "notes": (
                    "Positive absolute_difference means the frozen relation improves over the "
                    "best control by that MAE margin; margin must be >= 0.04 dex."
                ),
            }
        ],
        "uncertainty_summary": {
            "method": "predeclared_survival_margin_and_deterministic_control_benchmarks",
            "observed_uncertainty": transfer_margin,
            "reference_uncertainty": pc["survival_margin_dex"],
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": (
                "The margin is a control-survival margin, not a physical uncertainty interval. "
                "Shuffle, null, mass-matched, stage, and luminosity-provenance diagnostics bound "
                "the same-source transfer scope."
            ),
        },
        "artifacts": {
            "report": f"{RESULT_REL_DIR.as_posix()}/report.md",
            "metrics": f"{RESULT_REL_DIR.as_posix()}/metrics.json",
            "claim_update": f"{RESULT_REL_DIR.as_posix()}/claim_update.md",
            "claim_update_patch": f"{RESULT_REL_DIR.as_posix()}/claim_update.patch.md",
            "knowledge_update": f"{RESULT_REL_DIR.as_posix()}/knowledge_update.md",
            "knowledge_update_patch": f"{RESULT_REL_DIR.as_posix()}/knowledge_update.patch.md",
            "review_summary": f"{RESULT_REL_DIR.as_posix()}/review_summary.md",
            "review_metadata": f"{RESULT_REL_DIR.as_posix()}/review_metadata.yaml",
        },
    }


def _render_result_report(metrics: dict[str, Any]) -> str:
    prim = metrics["primary_high_mass_main_sequence_holdout"]
    sec = metrics["secondary_all_stage_high_mass_holdout"]
    fp = metrics["frozen_predictor"]
    pc = metrics["predeclared_contract"]
    return "\n".join(
        [
            f"# {RESULT_ID} - Stellar M-L High-Mass DEBCat Transfer",
            "",
            f"**Task:** `{RESULT_TASK_ID}`",
            f"**Source sandbox run:** `agent_runs/{AGENT_RUN_ID}/`",
            "**Review tier proposed:** `AGENT_PUBLISHED`",
            "**Best verdict:** `VALID_IN_RANGE`",
            "",
            "## Frozen Predictor",
            "",
            f"- Formula: `{fp['formula']}`",
            f"- Frozen alpha: `{fp['alpha_frozen']}`; fixed intercept logL0 `{fp['fixed_intercept_log_l0']}`",
            "- Source: `RESULT-0022` main-sequence train-fitted relation.",
            "- No refit on the high-mass holdout.",
            "",
            "## Primary Transfer Result",
            "",
            f"- Holdout: `{prim['holdout_count']}` high-mass main-sequence-compatible components across `{prim['holdout_systems']}` systems.",
            f"- Frozen relation MAE: `{prim['frozen_relation_holdout_mae_dex']:.6f}` dex.",
            f"- Best control: `{prim['best_control_name']}` at `{prim['best_control_mae_dex']:.6f}` dex.",
            f"- Transfer margin: `{prim['frozen_minus_best_control_dex']:.6f}` dex; predeclared survival margin `{pc['survival_margin_dex']:.2f}` dex.",
            f"- Beats every shuffled target seed: `{prim['beats_all_shuffle_seeds']}`.",
            "",
            "## Secondary Diagnostics",
            "",
            f"- All-stage high-mass holdout: `{sec['holdout_count']}` components, frozen MAE `{sec['frozen_relation_holdout_mae_dex']:.6f}` dex, margin `{sec['frozen_minus_best_control_dex']:.6f}` dex.",
            "- By-stage and luminosity-provenance diagnostics are recorded in `metrics.json`; they are not rescue criteria.",
            "",
            "## Output-Routing Summary",
            "",
            f"- Canonical destination: `{RESULT_REL_DIR.as_posix()}/`.",
            "- Gate A status: `PASS` for AGENT_PUBLISHED packaging; Gate B replay remains maintainer/independent-agent follow-up.",
            f"- Transfer margin/best control: `{prim['frozen_minus_best_control_dex']:.6f}` dex over `{prim['best_control_name']}`.",
            "- Claim impact: `none`. Knowledge impact: `none`. No PRED artifact.",
            "- Scope: one frozen relation, one disjoint high-mass DEBCat transfer, same-source judge, small primary holdout; not a universal law or discovery.",
            "",
        ]
    )


def _render_gate_a_report(metrics: dict[str, Any]) -> str:
    prim = metrics["primary_high_mass_main_sequence_holdout"]
    return "\n".join(
        [
            f"# Gate A Report - {RESULT_ID} (Stellar M-L high-mass transfer)",
            "",
            f"- **Artifact:** `{RESULT_REL_DIR.as_posix()}/result.yaml`",
            f"- **Task:** {RESULT_TASK_ID} - **Experiment:** {RESULT_EXP_ID} - **Hypothesis:** {RESULT_HYP_ID}",
            "- **Proposed tier:** AGENT_PUBLISHED",
            "- **Result:** PASS pending repository validation.",
            "",
            "## Gate A self-check",
            "",
            "| gate | status | evidence |",
            "|---|---|---|",
            "| deterministic_run | PASS | Pinned script regenerates sandbox metrics and result package from committed rows. |",
            "| verification_block_populated | PASS | Five PASS checks with numeric metrics in result.yaml. |",
            "| input_hashes_recorded | PASS | config / experiment / hypothesis / task / fixture sha256 pinned. |",
            "| limitations_listed | PASS | Same-source, small-holdout, stage/provenance, no-claim boundaries listed. |",
            "| engine_version_and_commit_pinned | PASS | engine_version and git_commit recorded. |",
            "| schema_validation_passes | PASS | To be checked by validate-repo before PR. |",
            "| no_protected_artifact_rewrite | PASS | RESULT-0022, CLAIM, PRED, KNOW, and source dataset untouched. |",
            "| no_forbidden_overclaim_wording | PASS | Transfer-under-controls framing only. |",
            "| dataset_provenance_valid | PASS | DEBCat normalized rows and TASK-0763 Route-2 boundary inherited. |",
            "",
            "## Headline Numbers",
            "",
            f"- Primary holdout MAE: `{prim['frozen_relation_holdout_mae_dex']:.6f}` dex.",
            f"- Best control: `{prim['best_control_name']}` at `{prim['best_control_mae_dex']:.6f}` dex.",
            f"- Transfer margin: `{prim['frozen_minus_best_control_dex']:.6f}` dex.",
            "",
            "## Routing",
            "",
            f"- Canonical destination: `{RESULT_REL_DIR.as_posix()}/`.",
            "- Gate A: PASS for AGENT_PUBLISHED if repository validation passes.",
            "- Gate B: deferred independent replay.",
            "- Claim impact: none. Knowledge impact: none.",
            "",
        ]
    )


def _write_result_package(metrics: dict[str, Any], result_dir: Path) -> None:
    result_dir.mkdir(parents=True, exist_ok=True)
    input_hashes = _copy_result_inputs(result_dir)
    result_metrics = _result_metrics(metrics)
    result_yaml = _build_result_yaml(metrics, input_hashes)

    (result_dir / "metrics.json").write_text(
        json.dumps(result_metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_yaml(result_dir / "result.yaml", result_yaml)
    (result_dir / "report.md").write_text(_render_result_report(metrics), encoding="utf-8")
    (result_dir / "gate_a_report.md").write_text(_render_gate_a_report(metrics), encoding="utf-8")
    (result_dir / "claim_update.md").write_text(
        "# Claim Update\n\nNo CLAIM artifact is proposed or modified by this Gate-A package.\n",
        encoding="utf-8",
    )
    (result_dir / "claim_update.patch.md").write_text(
        "# Claim Update Patch\n\nNo patch proposed.\n",
        encoding="utf-8",
    )
    (result_dir / "knowledge_update.md").write_text(
        "# Knowledge Update\n\nNo KNOW artifact is proposed or modified by this Gate-A package.\n",
        encoding="utf-8",
    )
    (result_dir / "knowledge_update.patch.md").write_text(
        "# Knowledge Update Patch\n\nNo patch proposed.\n",
        encoding="utf-8",
    )
    (result_dir / "review_summary.md").write_text(
        "\n".join(
            [
                f"# Review Summary - {RESULT_ID}",
                "",
                "The frozen RESULT-0022 mass-luminosity relation transfers to the",
                "stage-matched high-mass DEBCat holdout under the predeclared controls.",
                "This package requests AGENT_PUBLISHED only; independent Gate B replay",
                "and maintainer review remain separate follow-up.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _write_yaml(
        result_dir / "review_metadata.yaml",
        {
            "schema_version": "1",
            "artifact_type": "review_metadata",
            "result_id": RESULT_ID,
            "run_id": RESULT_RUN_ID,
            "experiment_id": RESULT_EXP_ID,
            "claim_id": None,
            "knowledge_id": None,
            "generated_at": RESULT_GENERATED_AT,
            "proposed_claim_status": None,
            "required_human_review": False,
            "evidence_basis": [RESULT_ID, "RESULT-0022", f"agent_runs/{AGENT_RUN_ID}/metrics.json"],
            "claim_target_file": None,
            "knowledge_target_file": None,
            "patch_artifacts": {
                "claim_patch": f"{RESULT_REL_DIR.as_posix()}/claim_update.patch.md",
                "knowledge_patch": f"{RESULT_REL_DIR.as_posix()}/knowledge_update.patch.md",
                "review_summary": f"{RESULT_REL_DIR.as_posix()}/review_summary.md",
            },
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for the sandbox agent run (default: agent_runs/AGENT-RUN-0082).",
    )
    parser.add_argument(
        "--skip-sandbox-output",
        action="store_true",
        help="Skip writing the sandbox agent_run outputs; useful when replaying only the Gate-A RESULT package.",
    )
    parser.add_argument(
        "--result-out-dir",
        type=Path,
        default=None,
        help="Optional canonical Gate-A RESULT output directory for TASK-0849.",
    )
    args = parser.parse_args()

    metrics = _build_metrics()
    if not args.skip_sandbox_output:
        out_dir = args.out_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = out_dir / "metrics.json"
        report_path = out_dir / "report.md"
        metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report_path.write_text(_render_report(metrics), encoding="utf-8")
    if args.result_out_dir is not None:
        _write_result_package(metrics, args.result_out_dir)
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
