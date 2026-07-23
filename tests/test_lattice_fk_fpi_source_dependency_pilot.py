from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/lattice_qcd/fk_fpi_source_manifest.yaml"
GRAPH_PATH = ROOT / "data/lattice_qcd/fk_fpi_dependency_graph.yaml"
NF2P1P1_REVIEW_PATH = (
    ROOT
    / "docs"
    / "reviews"
    / "lattice_qcd"
    / "fk-fpi-nf2p1p1-dependency-edge-resolution.md"
)

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


def _markdown_pair_rows(path: Path) -> dict[str, tuple[str, str, str, str]]:
    rows: dict[str, tuple[str, str, str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith(("| Pair ", "| ---")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 5 and " - " in cells[0]:
            rows[cells[0]] = tuple(cells[1:])
    return rows


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

def test_nf2p1p1_pair_resolution_is_complete_conservative_and_metadata_only() -> None:
    graph = _load(GRAPH_PATH)
    resolution = graph["nf_2p1p1_pair_resolution"]
    publication_ids = resolution["scope_publication_ids"]
    pairs = resolution["pairs"]
    axes = set(resolution["dependency_axes"])
    observed_pairs = {tuple(pair["publications"]) for pair in pairs}
    expected_pairs = {
        tuple(sorted((left, right), key=publication_ids.index))
        for index, left in enumerate(publication_ids)
        for right in publication_ids[index + 1 :]
    }

    assert resolution["task_id"] == "TASK-1079"
    assert resolution["reviewed_at"] == "2026-07-23"
    assert resolution["metadata_only"] is True
    assert len(publication_ids) == 5
    assert resolution["unordered_pair_count"] == len(pairs) == 10
    assert observed_pairs == expected_pairs
    assert axes == {
        "configuration_or_data",
        "scale_setting",
        "normalization_or_renormalization",
        "named_uncertainty_lineage",
    }

    evidence_ids = set(graph["evidence_catalog"])
    fully_unknown = 0
    for pair in pairs:
        assert set(pair["axes"]) == axes
        pair_states = []
        for classification in pair["axes"].values():
            state = classification["state"]
            pair_states.append(state)
            assert state in DEPENDENCE_STATES
            assert classification["evidence_identities"]
            assert set(classification["evidence_identities"]) <= evidence_ids
            assert classification["curator_note"]
        fully_unknown += int(set(pair_states) == {"UNKNOWN"})

    by_pair = {tuple(pair["publications"]): pair["axes"] for pair in pairs}
    fnal_hpqcd = by_pair[("pub-fnal-milc-17", "pub-hpqcd-13a")]
    fnal_callat = by_pair[("pub-fnal-milc-17", "pub-callat-20")]
    hpqcd_callat = by_pair[("pub-hpqcd-13a", "pub-callat-20")]
    etm_pair = by_pair[("pub-etm-14e", "pub-etm-21")]

    assert fnal_hpqcd["configuration_or_data"]["state"] == "CONFIRMED_SHARED"
    assert fnal_callat["configuration_or_data"]["state"] == "CONFIRMED_SHARED"
    assert hpqcd_callat["configuration_or_data"]["state"] == "CONFIRMED_SHARED"
    assert fnal_hpqcd["named_uncertainty_lineage"]["state"] == "CONFIRMED_SHARED"
    assert fnal_callat["named_uncertainty_lineage"]["state"] == "CONFIRMED_SHARED"
    assert hpqcd_callat["named_uncertainty_lineage"]["state"] == "CONFIRMED_SHARED"
    assert hpqcd_callat["scale_setting"]["state"] == "POSSIBLE_SHARED"
    assert etm_pair["configuration_or_data"]["state"] == "CONFIRMED_DISJOINT"
    assert fully_unknown == 6
    assert all(
        pair["axes"]["normalization_or_renormalization"]["state"] == "UNKNOWN"
        for pair in pairs
    )

    average = resolution["evaluated_average_membership"]
    assert average["average_node"] == "flag-2024-nf-2p1p1-fk-fpi"
    assert average["input_publication_ids"] == publication_ids
    assert average["count_average_as_independent_with_inputs"] is False
    assert resolution["verdict"] == "PARTIAL_HOLD_UNKNOWN_EDGES"
    assert not {
        "central_value",
        "value",
        "quoted_uncertainty",
        "average_value",
        "covariance_magnitude",
        "residual",
        "tension",
        "anomaly_score",
    } & _all_keys(resolution)

def test_nf2p1p1_review_table_matches_canonical_graph_states() -> None:
    graph = _load(GRAPH_PATH)
    resolution = graph["nf_2p1p1_pair_resolution"]
    labels = {
        "pub-fnal-milc-17": "FNAL/MILC 17",
        "pub-hpqcd-13a": "HPQCD 13A",
        "pub-etm-14e": "ETM 14E",
        "pub-callat-20": "CalLat 20",
        "pub-etm-21": "ETM 21",
    }
    abbreviations = {
        "CONFIRMED_SHARED": "SHARED",
        "CONFIRMED_DISJOINT": "DISJOINT",
        "POSSIBLE_SHARED": "POSSIBLE",
        "UNKNOWN": "UNKNOWN",
    }
    expected = {}
    for pair in resolution["pairs"]:
        left, right = pair["publications"]
        axes = pair["axes"]
        expected[f"{labels[left]} - {labels[right]}"] = (
            abbreviations[axes["configuration_or_data"]["state"]],
            abbreviations[axes["scale_setting"]["state"]],
            abbreviations[axes["normalization_or_renormalization"]["state"]],
            abbreviations[axes["named_uncertainty_lineage"]["state"]],
        )

    assert _markdown_pair_rows(NF2P1P1_REVIEW_PATH) == expected
