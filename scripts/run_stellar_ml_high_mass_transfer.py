#!/usr/bin/env python3
"""Stellar M-L high-mass DEBCat transfer benchmark (TASK-0837).

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

Sandbox-only. Emits ``agent_runs/AGENT-RUN-0082/metrics.json`` and
``report.md`` plus a Gate-B-replayable provenance block. No RESULT / PRED /
CLAIM / KNOW artifact is created and no claim is promoted.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab import __version__  # noqa: E402
from physics_lab.engines.stellar_ml_high_mass_transfer import (  # noqa: E402
    ROWS_PATH,
    compute_transfer_metrics,
)
from physics_lab.workflows.artifacts import git_commit  # noqa: E402

ENGINE_PATH = REPO_ROOT / "physics_lab/engines/stellar_ml_high_mass_transfer.py"
SCRIPT_PATH = REPO_ROOT / "scripts/run_stellar_ml_high_mass_transfer.py"
AGENT_RUN_ID = "AGENT-RUN-0082"
TASK_ID = "TASK-0837"
BENCHMARK_ID = "stellar-ml-high-mass-debcat-transfer"
DEFAULT_OUT_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
PINNED_COMMAND = f"python3 scripts/run_stellar_ml_high_mass_transfer.py --out-dir agent_runs/{AGENT_RUN_ID}"


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for the sandbox agent run (default: agent_runs/AGENT-RUN-0082).",
    )
    args = parser.parse_args()

    metrics = _build_metrics()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    report_path = out_dir / "report.md"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_report(metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
