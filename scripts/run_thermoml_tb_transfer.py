"""TASK-0841 bounded ThermoML Tb transfer benchmark runner (local-fetch posture).

This runner audits the FROZEN Joback Tb estimator (``physics_lab.engines.joback_tb``)
under the maintainer-approved ThermoML local-fetch posture. It is structured as a
two-stage gate:

1. IMPLEMENTATION-FIDELITY GATE (always run): reproduce the frozen 25-compound
   Joback Tb fidelity fixture with zero mismatches. If any mismatch is found,
   the run STOPS at ``IMPLEMENTATION_INCONCLUSIVE`` and no transfer metric is
   computed -- an off-by-one group assignment must not masquerade as a method
   failure.

2. LOCAL-FETCH + FAMILY-STRATIFIED TRANSFER (only if the fetch is executed):
   attempt the approved local fetch of the pinned ThermoML archive within bounds,
   parse Tb for selected pure compounds, then evaluate the frozen estimator by
   leave-one-family-out transfer against the declared controls.

By default ``--fetch-executed`` is ``no``: this runner does NOT download the
~181 MB archive and does NOT parse a Tb corpus. A faithful Tb corpus extraction
(InChI identity resolution, dedup, family classification, deterministic group
decomposition) is the deferred bounded row-curation task; performing a rushed
parse here would risk fabricating benchmark numbers, which is forbidden. When the
fetch is not executed, the runner delivers the frozen implementation + the
zero-mismatch fidelity fixture + the pinned source manifest reference + the
family-stratified selection/control protocol + replay instructions, and reports
the bounded verdict ``IMPLEMENTATION_INCONCLUSIVE`` with an explicit
``fetch_executed: no`` record. That is a complete, valid bounded outcome.

The runner does not write canonical ``results/``, ``claims/``, ``knowledge/``,
``prediction_registry/`` artifacts, does not promote any claim, does not relicense
ThermoML values, and uses no discovery wording. APL fits nothing here: it audits a
frozen published estimator's out-of-family transfer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.joback_tb import (  # noqa: E402
    FIDELITY_TOLERANCE_K,
    JOBACK_BASE_JR1987,
    evaluate_fidelity_fixture,
)

AGENT_RUN_ID = "AGENT-RUN-0084"
TASK_ID = "TASK-0841"
BENCHMARK_ID = "thermoml-bounded-tb-transfer"
ENGINE_VERSION = "0.1.0"

# Pinned official ThermoML source (cross-verified from the NIST PDR component
# metadata AND the authoritative .sha256 sidecar on 2026-06-26; see the source
# manifest data/thermophysical/source_manifest.yaml).
THERMOML_DOI = "10.18434/mds2-2422"
THERMOML_PDR = "https://data.nist.gov/od/id/mds2-2422"
THERMOML_ARCHIVE_URL = "https://data.nist.gov/od/ds/mds2-2422/ThermoML.v2020-09-30.tgz"
THERMOML_ARCHIVE_FILENAME = "ThermoML.v2020-09-30.tgz"
THERMOML_ARCHIVE_SIZE_BYTES = 189433115
THERMOML_PUBLISHED_SHA256 = (
    "231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2"
)
THERMOML_PRODUCT_VERSION = "1.2.6"

SOURCE_MANIFEST_REL = "data/thermophysical/source_manifest.yaml"
ENGINE_REL = "physics_lab/engines/joback_tb.py"

# Frozen chemical-family taxonomy for the leave-one-family-out split, by
# canonical functional-group priority (highest-priority group present wins).
# Frozen in the TASK-0833 scout note BEFORE any transfer error is read.
FROZEN_FAMILY_TAXONOMY: tuple[str, ...] = (
    "acids",
    "esters/lactones",
    "aldehydes",
    "ketones",
    "alcohols/phenols",
    "ethers",
    "nitriles",
    "amines",
    "nitro",
    "thiols/sulfides",
    "halocarbons",
    "aromatic hydrocarbons",
    "alkenes/alkynes",
    "alkanes/cycloalkanes",
)

# Declared controls for the (conditional) transfer evaluation. These are the
# baselines the frozen Joback estimator is scored against; they are described
# here and only *executed* when the fetch is executed and a parsed corpus exists.
DECLARED_CONTROLS: tuple[dict[str, str], ...] = (
    {
        "control_id": "global_median",
        "description": (
            "Predict every held-out compound's Tb as the global median Tb of the "
            "training (non-held-out-family) compounds. Null baseline."
        ),
    },
    {
        "control_id": "molecular_weight_only",
        "description": (
            "Predict Tb from a molecular-weight-only regression fit on the training "
            "families (size-only baseline; tests whether Joback beats bulk size)."
        ),
    },
    {
        "control_id": "nearest_homolog",
        "description": (
            "Predict Tb as the Tb of the nearest training homolog (closest "
            "molecular weight within the nearest compatible series)."
        ),
    },
    {
        "control_id": "shuffled_group_counts",
        "description": (
            "Joback applied to group counts randomly permuted across compounds "
            "(seed-controlled); breaks the structure -> Tb link while preserving "
            "the group-count marginal. Falsification control."
        ),
    },
    {
        "control_id": "within_family_constant",
        "description": (
            "Predict every held-out compound's Tb as the held-out family's own "
            "mean Tb (an oracle-ish within-family constant; upper bound on what a "
            "family-label-only predictor achieves)."
        ),
    },
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:  # pragma: no cover - git not available
        return "UNKNOWN"


def _input_file_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel in (ENGINE_REL, SOURCE_MANIFEST_REL):
        path = REPO_ROOT / rel
        if path.exists():
            hashes[rel] = f"sha256:{_sha256_file(path)}"
        else:
            hashes[rel] = "MISSING"
    return hashes


def build_metrics(*, fetch_executed: bool) -> dict[str, Any]:
    """Build the bounded benchmark metrics payload.

    The fidelity gate is always evaluated. The transfer evaluation is only
    populated when ``fetch_executed`` is true and a parsed corpus is supplied
    (not implemented in this bounded slice; see the module docstring).
    """

    fidelity = evaluate_fidelity_fixture(tolerance_k=FIDELITY_TOLERANCE_K)

    # Implementation-fidelity gate decides whether transfer is even allowed.
    if not fidelity.passed:
        verdict = "IMPLEMENTATION_INCONCLUSIVE"
        gate_reason = (
            f"fidelity fixture mismatch: {fidelity.mismatch_count} of "
            f"{fidelity.compound_count} compounds exceed {fidelity.tolerance_k} K"
        )
        transfer: dict[str, Any] = {
            "executed": False,
            "reason": "fidelity gate failed; transfer not computed",
        }
    elif not fetch_executed:
        # Fidelity clean, but the approved local fetch + corpus parse were not
        # executed in this bounded slice -> IMPLEMENTATION_INCONCLUSIVE by the
        # local-fetch posture. No transfer numbers are fabricated.
        verdict = "IMPLEMENTATION_INCONCLUSIVE"
        gate_reason = (
            "fidelity gate clean (0 mismatches); approved local fetch + Tb corpus "
            "parse not executed in this bounded slice, so no transfer metric is "
            "computed and none is fabricated"
        )
        transfer = {
            "executed": False,
            "reason": (
                "local fetch not executed (archive ~181 MB; faithful Tb corpus "
                "extraction with InChI identity resolution, dedup, family "
                "classification, and deterministic group decomposition is the "
                "deferred bounded row-curation task). Per the local-fetch posture "
                "this is a complete, valid IMPLEMENTATION_INCONCLUSIVE outcome."
            ),
            "declared_split": "leave_one_family_out",
            "declared_family_taxonomy": list(FROZEN_FAMILY_TAXONOMY),
            "declared_controls": list(DECLARED_CONTROLS),
            "declared_reporting": {
                "aggregation": "compound_level",
                "uncertainty_aware_error": True,
                "covered_groups_only_subset_separated": True,
                "out_of_coverage_excluded": True,
            },
            "per_family_outcome": "inconclusive (transfer not executed)",
        }
    else:  # pragma: no cover - corpus parse is out of this bounded slice
        raise NotImplementedError(
            "fetch_executed=yes path requires a parsed, license-cleared ThermoML "
            "Tb corpus (the deferred bounded row-curation task). This runner does "
            "not parse a corpus; rerun once the corpus artifact exists."
        )

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "benchmark_id": BENCHMARK_ID,
        "engine_version": ENGINE_VERSION,
        "git_commit": _git_commit(),
        "verdict": verdict,
        "gate_reason": gate_reason,
        "property_in_scope": "normal_boiling_point_Tb_only",
        "tc_excluded_reason": (
            "Joback Tc depends on Tb (Tc = Tb * [...]); auditing Tc with an "
            "experimental Tb substituted is an information-leakage path. Tb has no "
            "such upstream dependency in Joback (structure-only), so it is the "
            "clean first axis."
        ),
        "fetch_executed": "yes" if fetch_executed else "no",
        "frozen_estimator": {
            "name": "Joback & Reid (1987) Tb group-contribution estimator",
            "formula": "Tb = base + sum_i n_i * dTb_i (K)",
            "scoring_intercept_recommended_k": JOBACK_BASE_JR1987,
            "code_reference": ENGINE_REL,
            "note": (
                "Frozen published estimator; APL fits nothing. The audit measures "
                "whether this frozen estimator transfers under specified family "
                "holdouts -- not whether Joback's method is right or wrong."
            ),
        },
        "fidelity_gate": {
            "passed": fidelity.passed,
            "tolerance_k": fidelity.tolerance_k,
            "compound_count": fidelity.compound_count,
            "mismatch_count": fidelity.mismatch_count,
            "max_abs_error_k": fidelity.max_abs_error_k,
            "match_criterion": (
                "computed Tb within tolerance of each compound's published "
                "PREDICTED Tb, using that compound's own source intercept "
                "(198.2 canonical Joback&Reid or 198.12 molecularknowledge)"
            ),
            "rows": [
                {
                    "name": r.name,
                    "smiles": r.smiles,
                    "group_sum_k": r.group_sum_k,
                    "base": r.base,
                    "computed_tb_k": r.computed_tb_k,
                    "published_tb_k": r.published_tb_k,
                    "abs_error_k": r.abs_error_k,
                    "match": r.match,
                }
                for r in fidelity.rows
            ],
        },
        "transfer": transfer,
        "source": {
            "product": "NIST TRC ThermoML / Data Archive",
            "doi": THERMOML_DOI,
            "product_version": THERMOML_PRODUCT_VERSION,
            "pdr_landing": THERMOML_PDR,
            "archive_url": THERMOML_ARCHIVE_URL,
            "archive_filename": THERMOML_ARCHIVE_FILENAME,
            "archive_size_bytes": THERMOML_ARCHIVE_SIZE_BYTES,
            "official_published_sha256": THERMOML_PUBLISHED_SHA256,
            "sha256_provenance": (
                "NIST-published checksum, cross-verified 2026-06-26 from the PDR "
                "component metadata and the authoritative .tgz.sha256 sidecar. NOT "
                "an APL-computed-from-downloaded-bytes hash: archive not fetched."
            ),
            "apl_computed_sha256": "PENDING_FIRST_FETCH",
            "manifest": SOURCE_MANIFEST_REL,
        },
        "rights_determination": {
            "local_analysis_allowed": "yes",
            "source_bytes_redistribution": "no",
            "derived_rows_publication": "conditional",
            "substantial_extraction_review_required": "yes",
            "covered_by_repo_license": "false",
            "citation_required": (
                "Cite the ThermoML Archive per NIST TRC request; facts extractable "
                "with attribution, file bytes not re-hosted."
            ),
        },
        "replay": {
            "command": (
                "python3 scripts/run_thermoml_tb_transfer.py "
                "--output-dir agent_runs/AGENT-RUN-0084"
            ),
            "code_reference": "scripts/run_thermoml_tb_transfer.py",
            "engine_reference": ENGINE_REL,
            "input_file_hashes": _input_file_hashes(),
            "engine_version": ENGINE_VERSION,
            "git_commit": _git_commit(),
        },
        "limitations": [
            "Tb-only; Tc excluded for Joback leakage.",
            "Frozen published Joback estimator audited; APL fits nothing and no "
            "discovery is claimed.",
            "Fetch not executed in this bounded slice: no ThermoML Tb corpus was "
            "parsed and no transfer metric was computed (none fabricated).",
            "Family-holdout transfer scope is declared (leave-one-family-out vs "
            "five controls) but conditional on the deferred license-cleared "
            "corpus-parse/row-curation task.",
            "Fidelity fixture is solvent/hydrocarbon/oxygenate-heavy and does not "
            "stress Joback's rare heteroatom-ring/multifunctional groups at scale.",
            "Two intercept conventions exist (198.2 canonical vs 198.12 in one "
            "reference table); a future scoring run must pin one (recommend 198.2).",
        ],
        "output_routing": {
            "task_verdict": verdict,
            "canonical_destination": "sandbox_agent_run_plus_review_note",
            "review_tier": "none",
            "gate_a_status": "not_attempted_bounded_inconclusive",
            "gate_b_status": "replayable_metadata_recorded_transfer_not_executed",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "fetch_executed": "yes" if fetch_executed else "no",
        },
    }


def render_report(metrics: dict[str, Any]) -> str:
    fid = metrics["fidelity_gate"]
    src = metrics["source"]
    rights = metrics["rights_determination"]
    lines: list[str] = []
    lines.append(f"# {AGENT_RUN_ID} - ThermoML bounded Tb transfer benchmark")
    lines.append("")
    lines.append(f"**Task:** `{TASK_ID}`")
    lines.append(f"**Benchmark:** `{metrics['benchmark_id']}`")
    lines.append(f"**Verdict:** `{metrics['verdict']}`")
    lines.append(f"**Fetch executed:** `{metrics['fetch_executed']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        "Bounded audit of the FROZEN Joback Tb estimator under the "
        "maintainer-approved ThermoML local-fetch posture. The "
        "implementation-fidelity gate is evaluated first; the family-stratified "
        "transfer evaluation runs only when the approved local fetch + Tb corpus "
        "parse are executed. APL fits nothing: it audits whether the frozen "
        "published estimator transfers under specified family holdouts, not "
        "whether Joback's method is right or wrong. No claim, prediction, "
        "knowledge entry, or discovery is promoted."
    )
    lines.append("")
    lines.append("## Implementation-fidelity gate (FIRST)")
    lines.append("")
    lines.append(
        f"- Result: **{'PASS' if fid['passed'] else 'FAIL'}** - "
        f"{fid['compound_count']} compounds, {fid['mismatch_count']} mismatches, "
        f"max abs error {fid['max_abs_error_k']} K (tolerance {fid['tolerance_k']} K)."
    )
    lines.append(f"- Match criterion: {fid['match_criterion']}.")
    lines.append("")
    lines.append("| Compound | base | computed Tb (K) | published Tb (K) | abs err (K) | match |")
    lines.append("| --- | ---: | ---: | ---: | ---: | :---: |")
    for r in fid["rows"]:
        lines.append(
            f"| {r['name']} | {r['base']} | {r['computed_tb_k']} | "
            f"{r['published_tb_k']} | {r['abs_error_k']} | "
            f"{'Y' if r['match'] else 'N'} |"
        )
    lines.append("")
    lines.append("## Transfer evaluation")
    lines.append("")
    transfer = metrics["transfer"]
    if transfer["executed"]:
        lines.append("Transfer executed (see metrics.json for per-family detail).")
    else:
        lines.append(f"- Status: **not executed** - {transfer['reason']}")
        if "declared_split" in transfer:
            lines.append(f"- Declared split: `{transfer['declared_split']}`.")
            lines.append(
                "- Declared family taxonomy (frozen before any error reading): "
                + ", ".join(transfer["declared_family_taxonomy"])
                + "."
            )
            lines.append("- Declared controls:")
            for ctrl in transfer["declared_controls"]:
                lines.append(f"  - `{ctrl['control_id']}`: {ctrl['description']}")
            lines.append(
                "- Per-family outcome: " + transfer["per_family_outcome"] + "."
            )
    lines.append("")
    lines.append("## Pinned source")
    lines.append("")
    lines.append(f"- Product: {src['product']} (DOI `{src['doi']}`, version `{src['product_version']}`).")
    lines.append(f"- PDR landing: {src['pdr_landing']}")
    lines.append(f"- Archive: `{src['archive_filename']}` ({src['archive_size_bytes']} bytes).")
    lines.append(f"- Official published SHA-256: `{src['official_published_sha256']}`")
    lines.append(f"  - Provenance: {src['sha256_provenance']}")
    lines.append(f"  - APL-computed-from-fetched-bytes SHA-256: `{src['apl_computed_sha256']}`.")
    lines.append(f"- Source manifest: `{src['manifest']}`.")
    lines.append("")
    lines.append("## Rights determination (3-question framework)")
    lines.append("")
    lines.append(f"- local_analysis_allowed: `{rights['local_analysis_allowed']}`")
    lines.append(f"- source_bytes_redistribution: `{rights['source_bytes_redistribution']}`")
    lines.append(f"- derived_rows_publication: `{rights['derived_rows_publication']}`")
    lines.append(
        f"- substantial_extraction_review_required: "
        f"`{rights['substantial_extraction_review_required']}`"
    )
    lines.append(f"- covered_by_repo_license: `{rights['covered_by_repo_license']}`")
    lines.append(f"- {rights['citation_required']}")
    lines.append("")
    lines.append("## Replay (Gate-B-replayable)")
    lines.append("")
    rep = metrics["replay"]
    lines.append(f"- Command: `{rep['command']}`")
    lines.append(f"- Code reference: `{rep['code_reference']}`")
    lines.append(f"- Engine reference: `{rep['engine_reference']}`")
    lines.append(f"- Engine version: `{rep['engine_version']}`")
    lines.append(f"- Git commit: `{rep['git_commit']}`")
    lines.append("- Input file hashes:")
    for rel, h in rep["input_file_hashes"].items():
        lines.append(f"  - `{rel}`: `{h}`")
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    for lim in metrics["limitations"]:
        lines.append(f"- {lim}")
    lines.append("")
    lines.append("## Output-routing summary")
    lines.append("")
    routing = metrics["output_routing"]
    lines.append(f"- Task verdict: `{routing['task_verdict']}`.")
    lines.append(f"- Fetch executed: `{routing['fetch_executed']}`.")
    lines.append(f"- Canonical destination: `{routing['canonical_destination']}`.")
    lines.append(f"- Review tier: `{routing['review_tier']}`.")
    lines.append(f"- Gate A status: `{routing['gate_a_status']}`.")
    lines.append(f"- Gate B status: `{routing['gate_b_status']}`.")
    lines.append(f"- Claim impact: `{routing['claim_impact']}`.")
    lines.append(f"- Knowledge impact: `{routing['knowledge_impact']}`.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "agent_runs" / AGENT_RUN_ID,
        help="directory to write metrics.json and report.md",
    )
    parser.add_argument(
        "--fetch-executed",
        choices=("yes", "no"),
        default="no",
        help=(
            "whether the approved local ThermoML fetch + Tb corpus parse were "
            "executed (default: no -> bounded IMPLEMENTATION_INCONCLUSIVE)"
        ),
    )
    args = parser.parse_args(argv)

    metrics = build_metrics(fetch_executed=(args.fetch_executed == "yes"))
    report = render_report(metrics)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(report + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
