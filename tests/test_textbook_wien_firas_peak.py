from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from physics_lab.engines.textbook_wien_firas_peak import (
    ADMISSIBLE_VERDICTS,
    REFERENCE_TEMPERATURE_K,
    WIEN_WAVELENGTH_DISPLACEMENT_M_K,
    build_spectral_points,
    evaluate_wien_firas_peak,
    load_firas_rows,
    reference_wavelength_peak_m,
)
from physics_lab.registry.agent_replay_validation import ReplayIdentity, validate_agent_published_result


ROOT = Path(__file__).resolve().parents[1]
FIRAS_ROWS = ROOT / "data" / "textbook_formula_audit" / "wien_firas" / "firas_monopole_rows.yaml"
EXAMPLE_PATH = ROOT / "examples" / "textbook_firas_wien_peak_consistency.yaml"


@pytest.fixture(scope="module")
def dataset() -> dict:
    return load_firas_rows(FIRAS_ROWS)


def test_reference_peak_matches_frozen_constant() -> None:
    assert reference_wavelength_peak_m(REFERENCE_TEMPERATURE_K) == pytest.approx(
        WIEN_WAVELENGTH_DISPLACEMENT_M_K / REFERENCE_TEMPERATURE_K
    )


def test_verdict_is_consistent_in_scope_and_admissible(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    assert metric.verdict in ADMISSIBLE_VERDICTS
    assert metric.verdict == "CONSISTENT_IN_SCOPE"


def test_wavelength_peak_close_to_reference_after_jacobian(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    # Interpolated peak should agree tightly; raw-bin within the loose tolerance.
    assert metric.interpolated_relative_difference < 0.005
    assert metric.raw_bin_relative_difference < 0.02
    # Reference is ~1.063 mm (= 9.4 cm^-1) per the source-route note.
    assert metric.reference_wavelength_peak_m == pytest.approx(1.0632e-3, rel=1e-3)


def test_frequency_domain_peak_is_distinct_from_wavelength_peak(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    # Frequency-domain peak (~5.45 cm^-1 / ~163 GHz) differs from the
    # wavelength-domain peak (~9.5 cm^-1): Wien non-invariance via the Jacobian.
    assert metric.frequency_domain_peak_wavenumber_cm_inverse == pytest.approx(5.45)
    assert (
        metric.frequency_domain_peak_wavenumber_cm_inverse
        < metric.wavelength_domain_peak_raw_bin_wavenumber_cm_inverse
    )
    assert metric.controls["frequency_domain_peak_distinct"] is True


def test_no_jacobian_relabel_control_is_rejected(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    # Relabelling the B_nu argmax directly as a wavelength peak is badly wrong.
    assert metric.no_jacobian_relabel_relative_difference > 0.5
    assert metric.controls["no_jacobian_relabel_rejected"] is True


def test_wrong_temperature_control_is_rejected(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    assert metric.wrong_temperature_relative_difference >= 0.05
    assert metric.controls["wrong_temperature_rejected"] is True


def test_all_controls_pass(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    assert all(metric.controls.values())


def test_spectral_points_apply_unit_conversions(dataset: dict) -> None:
    points = build_spectral_points(dataset)
    first = points[0]
    # 2.27 cm^-1 -> 227 m^-1; lambda = 1/227 m.
    assert first.wavenumber_m_inverse == pytest.approx(227.0)
    assert first.wavelength_m == pytest.approx(1.0 / 227.0)
    assert first.frequency_hz == pytest.approx(299_792_458.0 * 227.0)


def test_residual_only_product_yields_inconclusive_semantics(dataset: dict) -> None:
    residual_like = copy.deepcopy(dataset)
    for row in residual_like["rows"]:
        row["monopole_intensity_class"] = "source_reported_residual"
    metric = evaluate_wien_firas_peak(residual_like)
    assert metric.verdict == "INCONCLUSIVE_PRODUCT_SEMANTICS"
    assert metric.controls["absolute_product_gate"] is False


def test_run_is_deterministic(dataset: dict) -> None:
    first = evaluate_wien_firas_peak(dataset)
    second = evaluate_wien_firas_peak(dataset)
    assert first == second


def test_cli_run_writes_gate_b_replayable_result0023(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "run",
            str(EXAMPLE_PATH),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    result_path = tmp_path / "EXP-0016" / "RUN-0001" / "result.yaml"
    metrics_path = tmp_path / "EXP-0016" / "RUN-0001" / "metrics.json"
    payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    replay_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    committed_metrics = json.loads(
        (ROOT / "results" / "EXP-0016" / "RUN-0001" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )

    assert payload["command"] == "physics-lab run examples/textbook_firas_wien_peak_consistency.yaml"
    assert payload["review_tier"] == "AGENT_PUBLISHED"
    assert payload["best_verdict"] == "VALID_IN_RANGE"
    assert payload["best_model_id"] == "model_firas_wien_wavelength_peak"
    assert payload["agent_proposal_evaluation"]["published_by"]["agent_tool"] == "Claude Code"
    assert replay_metrics["primary_metric"] == committed_metrics["primary_metric"]
    assert replay_metrics["controls_all_passed"] == committed_metrics["controls_all_passed"]


def test_gate_b_replay_helper_accepts_result0023_packaging(tmp_path: Path) -> None:
    committed = ROOT / "results" / "EXP-0016" / "RUN-0001" / "result.yaml"
    replay = validate_agent_published_result(
        committed,
        root=ROOT,
        replayed_by=ReplayIdentity(
            contributor_id="codex",
            github_username="gladunrv",
            agent_tool="Codex",
            model_version="gpt-5-codex",
        ),
        output_dir=tmp_path / "replay",
    )
    assert replay.ok, [issue.message for issue in replay.issues]
