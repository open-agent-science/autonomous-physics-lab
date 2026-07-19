from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/lattice_qcd/fk_fpi_source_manifest.yaml"
GRAPH_PATH = ROOT / "data/lattice_qcd/fk_fpi_dependency_graph.yaml"

DEPENDENCE_STATES = {
    "CONFIRMED_SHARED",
    "CONFIRMED_DISJOINT",
    "POSSIBLE_SHARED",
    "UNKNOWN",
}
REQUIRED_PUBLICATION_EDGE_TYPES = {
    "authored_by",
    "uses_ensemble_family",
    "uses_fermion_action",
    "depends_on_scale_setting",
    "depends_on_normalization_or_renormalization",
    "contributes_to_evaluated_average",
}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for child in value.values():
            keys.update(_all_keys(child))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for child in value:
            keys.update(_all_keys(child))
        return keys
    return set()


def test_manifest_freezes_exact_flag_input_set_without_numeric_results() -> None:
    manifest = _load(MANIFEST_PATH)
    freeze = manifest["selection_freeze"]
    publications = manifest["publications"]

    assert manifest["metadata_only"] is True
    assert manifest["contains_central_values"] is False
    assert manifest["contains_uncertainties"] is False
    assert manifest["contains_averages"] is False
    assert freeze["frozen_before_lineage_inspection"] is True
    assert freeze["selected_publication_count"] == len(publications) == 11
    assert freeze["selected_publication_ids"] == [
        row["publication_id"] for row in publications
    ]
    assert {row["flag_identity"]["reference"] for row in publications} == {
        12,
        20,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
    }
    assert not {
        "central_value",
        "value",
        "quoted_uncertainty",
        "average_value",
        "residual",
        "tension",
        "anomaly_score",
    } & _all_keys(manifest)


def test_every_primary_has_identity_conventions_rights_and_citation() -> None:
    manifest = _load(MANIFEST_PATH)
    required_observable = {
        "flavor_content",
        "isospin_qed_treatment",
        "normalization_route",
        "scheme_scale_applicability",
    }
    seen_dois: set[str] = set()
    seen_arxiv: set[str] = set()

    for publication in manifest["publications"]:
        assert publication["publication_role"].startswith("primary_flag_average_input")
        assert required_observable <= set(publication["observable"])
        assert set(publication["simulation"]) == {
            "ensemble_family",
            "fermion_action",
            "scale_setting",
        }
        assert publication["uncertainty_component_names"]
        assert publication["source_locator"]
        assert publication["accessed_at"] == "2026-07-19"
        assert publication["rights_status"] == "metadata_only_no_source_bytes_committed"
        assert "Cite" in publication["citation_requirement"]
        assert publication["doi"] not in seen_dois
        assert publication["arxiv"] not in seen_arxiv
        seen_dois.add(publication["doi"])
        seen_arxiv.add(publication["arxiv"])


def test_graph_nodes_edges_and_evidence_are_closed_and_typed() -> None:
    graph = _load(GRAPH_PATH)
    nodes = graph["nodes"]
    edges = graph["edges"]
    node_ids = {node["node_id"] for node in nodes}
    evidence_ids = set(graph["evidence_catalog"])

    assert len(node_ids) == len(nodes)
    assert {node["node_type"] for node in nodes} == set(graph["node_types"])
    assert len({edge["edge_id"] for edge in edges}) == len(edges)
    for node in nodes:
        assert {
            "node_id",
            "node_type",
            "label",
            "source_identity",
            "rights_status",
            "retrieval_identity",
        } <= set(node)
    for edge in edges:
        assert edge["edge_type"] in graph["edge_types"]
        assert edge["dependence_state"] in DEPENDENCE_STATES
        assert edge["from_node"] in node_ids
        assert edge["to_node"] in node_ids
        assert edge["evidence_identity"] in evidence_ids
        assert edge["curator_note"]


def test_each_publication_is_bound_to_all_required_dependency_axes() -> None:
    manifest = _load(MANIFEST_PATH)
    graph = _load(GRAPH_PATH)
    edges = graph["edges"]

    for publication in manifest["publications"]:
        publication_id = publication["publication_id"]
        edge_types = {
            edge["edge_type"]
            for edge in edges
            if edge["from_node"] == publication_id
        }
        assert REQUIRED_PUBLICATION_EDGE_TYPES <= edge_types


def test_evaluated_averages_link_every_input_and_cannot_be_independent() -> None:
    manifest = _load(MANIFEST_PATH)
    graph = _load(GRAPH_PATH)
    expected_by_average: dict[str, set[str]] = {}
    for publication in manifest["publications"]:
        average_id = publication["flag_identity"]["average_id"]
        expected_by_average.setdefault(average_id, set()).add(
            publication["publication_id"]
        )

    observed_by_average: dict[str, set[str]] = {}
    for edge in graph["edges"]:
        if edge["edge_type"] == "contributes_to_evaluated_average":
            observed_by_average.setdefault(edge["to_node"], set()).add(
                edge["from_node"]
            )

    assert observed_by_average == expected_by_average
    assert graph["evaluated_average_policy"]["linked_primary_count"] == 11
    assert graph["evaluated_average_policy"]["count_average_as_independent_with_inputs"] is False


def test_unresolved_pairs_force_covariance_hold() -> None:
    graph = _load(GRAPH_PATH)
    diagnostics = graph["pair_diagnostics"]
    components = graph["provisional_connected_components"]

    assert diagnostics["unordered_pair_count"] == 55
    assert diagnostics["unresolved_pair_count"] == 49
    assert diagnostics["absence_of_edge_means_independent"] is False
    assert components["independence_certified"] is False
    assert graph["verdict"] == "HOLD_COVARIANCE_UNRESOLVED"
