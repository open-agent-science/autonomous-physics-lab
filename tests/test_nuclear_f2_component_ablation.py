from __future__ import annotations

from scripts.run_nuclear_f2_component_ablation import run_f2_component_ablation


def test_f2_component_ablation_uses_bounded_slate() -> None:
    metrics = run_f2_component_ablation()

    assert metrics["task_id"] == "TASK-0625"
    assert metrics["ablation_contract"]["variant_count"] == 13
    assert metrics["variants"]["full_f2_reference"]["decision"][
        "candidate_full_known_mae_improvement_mev"
    ] == 0.200411
    assert set(metrics["variants"]) >= {
        "full_f2_reference",
        "without_doubly_magic_near",
        "only_mid_shell_neutron_rich",
    }
    assert metrics["controls"]["controls_reused_because_inputs_unchanged"] is True


def test_f2_component_ablation_keeps_diagnostic_only_ceiling() -> None:
    metrics = run_f2_component_ablation()

    assert metrics["outcome"]["classification"] in {
        "COMPONENT_SURVIVES_MARGIN",
        "COMPONENT_DIAGNOSTIC_ONLY",
        "AGGREGATE_FRAGILE",
        "DO_NOT_PROMOTE",
    }
    assert metrics["output_routing"]["result_impact"] == "no RESULT artifact created"
    assert metrics["output_routing"]["claim_impact"] == "none"
    assert not any(
        variant["decision"]["survival_margin_clears"]
        for key, variant in metrics["variants"].items()
        if key.startswith("only_")
    )
