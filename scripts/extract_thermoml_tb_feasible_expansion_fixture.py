#!/usr/bin/env python3
"""Extract the frozen TASK-1091 ThermoML Tb feasible-expansion fixture.

The extractor reads one checksum-pinned private ThermoML archive without
unpacking it, reproduces the TASK-1084 count contract, preserves the 38
eligible rows from the existing bounded fixture, and selects additions without
using Tb values or model outcomes. It emits at most 74 attributed factual rows,
not a normalized ThermoML corpus.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import tarfile
from typing import Any

import yaml

try:
    from scripts.preflight_thermoml_tb_80row_identity_counts import (
        ALLOWED_ATOMIC_NUMBERS,
        EXPECTED_ARCHIVE_SHA256,
        EXPECTED_ARCHIVE_SIZE,
        GROUP_KEY_BY_ID,
        SELECTED_FAMILIES,
        SIMPLE_FAMILY_ELEMENTS,
        ThermoMLDependencies,
        _family,
        _load_thermoml_dependencies,
        _property_name,
    )
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from preflight_thermoml_tb_80row_identity_counts import (  # type: ignore[no-redef]
        ALLOWED_ATOMIC_NUMBERS,
        EXPECTED_ARCHIVE_SHA256,
        EXPECTED_ARCHIVE_SIZE,
        GROUP_KEY_BY_ID,
        SELECTED_FAMILIES,
        SIMPLE_FAMILY_ELEMENTS,
        ThermoMLDependencies,
        _family,
        _load_thermoml_dependencies,
        _property_name,
    )


EXPECTED_CONTRACT_ID = "thermoml-tb-availability-capped-expansion-v1"
EXPECTED_CONFLICT_ROW_IDS = {"TML-TB-0006", "TML-TB-0014"}
MAX_ROWS_PER_ARTICLE = 5
MINIMUM_TOTAL_ROWS = 64
MINIMUM_NEW_IDENTITIES = 24
MINIMUM_ROWS_PER_FAMILY = 6
MINIMUM_EFFECTIVE_ROWS = 64.0
EXTRACTOR_PATH = "scripts/extract_thermoml_tb_feasible_expansion_fixture.py"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(archive: Path) -> dict[str, Any]:
    size = archive.stat().st_size
    digest = sha256_file(archive)
    if size != EXPECTED_ARCHIVE_SIZE or digest != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(f"ThermoML archive pin mismatch: size={size}, sha256={digest}")
    return {"filename": archive.name, "size_bytes": size, "sha256": digest}


def scan_archive(
    archive: Path,
    dependencies: ThermoMLDependencies,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    observations: list[dict[str, Any]] = []
    counters: Counter[str] = Counter()
    chem = dependencies.chem

    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            if not (member.isfile() and member.name.endswith(".json")):
                continue
            counters["archive_json_files"] += 1
            extracted = tar.extractfile(member)
            if extracted is None:
                counters["unreadable_json_members"] += 1
                continue
            raw = extracted.read()
            if b"Normal boiling temperature, K" not in raw:
                continue
            counters["normal_boiling_files"] += 1
            document = json.loads(raw)
            compounds = {
                item.get("RegNum", {}).get("nOrgNum"): item
                for item in document.get("Compound", [])
            }
            source_doi = str(
                document.get("Citation", {}).get("sDOI") or member.name[:-5]
            )

            for block in document.get("PureOrMixtureData", []):
                normal_numbers = {
                    prop.get("nPropNumber")
                    for prop in block.get("Property", [])
                    if _property_name(prop) == "Normal boiling temperature, K"
                }
                if not normal_numbers:
                    continue
                counters["normal_boiling_data_blocks"] += 1
                components = block.get("Component", [])
                if len(components) != 1:
                    counters["mixture_or_multicomponent_blocks"] += 1
                    continue
                compound = compounds.get(components[0].get("RegNum", {}).get("nOrgNum"))
                if not compound:
                    counters["missing_component_record_blocks"] += 1
                    continue
                inchi = compound.get("sStandardInChI")
                inchi_key = compound.get("sStandardInChIKey")
                if not inchi or not inchi_key:
                    counters["missing_standard_identity_blocks"] += 1
                    continue
                mol = chem.MolFromInchi(inchi)
                if mol is None:
                    counters["inchi_parse_failed_blocks"] += 1
                    continue
                counters["identified_single_component_blocks"] += 1
                if len(chem.GetMolFrags(mol)) != 1 or chem.GetFormalCharge(mol) != 0:
                    counters["charged_or_multifragment_blocks"] += 1
                    continue
                atom_numbers = {atom.GetAtomicNum() for atom in mol.GetAtoms()}
                if not atom_numbers <= ALLOWED_ATOMIC_NUMBERS:
                    counters["unsupported_element_blocks"] += 1
                    continue
                joback = dependencies.joback(mol=mol)
                if not joback.success:
                    counters["joback_out_of_coverage_blocks"] += 1
                    continue
                group_ids = {int(group_id) for group_id in joback.counts}
                if not group_ids <= set(GROUP_KEY_BY_ID):
                    counters["joback_group_table_mismatch_blocks"] += 1
                    continue
                family = _family(mol, chem)
                if not family:
                    counters["unclassified_family_blocks"] += 1
                    continue
                names = compound.get("sCommonName") or [inchi_key]
                group_counts = {
                    GROUP_KEY_BY_ID[int(group_id)]: int(value)
                    for group_id, value in sorted(joback.counts.items())
                }

                for values in block.get("NumValues", []):
                    for prop_value in values.get("PropertyValue", []):
                        if prop_value.get("nPropNumber") not in normal_numbers:
                            continue
                        if "nPropValue" not in prop_value:
                            counters["missing_numeric_tb_values"] += 1
                            continue
                        counters["raw_normal_boiling_observations"] += 1
                        uncertainty = prop_value.get("CombinedUncertainty", {}).get(
                            "nCombExpandUncertValue"
                        )
                        observations.append(
                            {
                                "inchi_key": str(inchi_key),
                                "standard_inchi": str(inchi),
                                "common_name": str(names[0]),
                                "formula": str(compound.get("sFormulaMolec", "")),
                                "family": family,
                                "atomic_numbers": sorted(atom_numbers),
                                "molecular_weight_g_mol": round(float(joback.MW), 6),
                                "experimental_tb_k": float(prop_value["nPropValue"]),
                                "expanded_uncertainty_k": (
                                    float(uncertainty) if uncertainty is not None else None
                                ),
                                "source_doi": source_doi,
                                "source_member": member.name,
                                "joback_group_counts": group_counts,
                            }
                        )
    return observations, counters


def representatives_from_observations(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_identity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        by_identity[row["inchi_key"]].append(row)

    representatives: list[dict[str, Any]] = []
    for inchi_key in sorted(by_identity):
        identity_rows = by_identity[inchi_key]
        chosen = min(
            identity_rows,
            key=lambda row: (
                row["expanded_uncertainty_k"] is None,
                row["expanded_uncertainty_k"]
                if row["expanded_uncertainty_k"] is not None
                else math.inf,
                row["source_doi"],
                row["experimental_tb_k"],
            ),
        )
        values = [row["experimental_tb_k"] for row in identity_rows]
        representative = {
            key: value for key, value in chosen.items() if key != "atomic_numbers"
        }
        representative.update(
            {
                "observation_count": len(identity_rows),
                "observed_tb_span_k": round(max(values) - min(values), 6),
                "conflicting_observations": bool(max(values) - min(values) > 1.0),
                "selection_rule": (
                    "smallest_reported_expanded_uncertainty_then_source_doi"
                ),
            }
        )
        family = representative["family"]
        if (
            family in SELECTED_FAMILIES
            and set(chosen["atomic_numbers"]) <= SIMPLE_FAMILY_ELEMENTS[family]
        ):
            representatives.append(representative)
    return representatives


def admissible_counts(representatives: list[dict[str, Any]]) -> dict[str, int]:
    counts = dict.fromkeys(SELECTED_FAMILIES, 0)
    for row in representatives:
        if row["conflicting_observations"] or row["expanded_uncertainty_k"] is None:
            continue
        counts[row["family"]] += 1
    return counts


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return payload


def validate_frozen_inputs(
    contract: dict[str, Any],
    existing_fixture: dict[str, Any],
    observed_counts: dict[str, int],
) -> list[dict[str, Any]]:
    if contract.get("contract_id") != EXPECTED_CONTRACT_ID:
        raise ValueError("Unexpected feasible-expansion contract identity")
    if contract.get("verdict") != "REVISED_CONTRACT_READY_NO_SCORE":
        raise ValueError("Frozen contract is not in its reviewed ready state")
    if contract.get("benchmark_authorized") is not False:
        raise ValueError("Extraction task must not authorize benchmark scoring")

    caps = contract.get("family_caps", [])
    if tuple(item.get("family") for item in caps) != SELECTED_FAMILIES:
        raise ValueError("Frozen family order or taxonomy drifted")
    expected_counts = {
        item["family"]: int(item["admissible_non_conflict_count"]) for item in caps
    }
    if observed_counts != expected_counts:
        raise ValueError(
            f"Archive count replay drift: expected={expected_counts}, observed={observed_counts}"
        )

    rows = existing_fixture.get("rows", [])
    expected_row_count = int(contract["existing_surface"]["row_count"])
    if len(rows) != expected_row_count or expected_row_count != 40:
        raise ValueError("Historical fixture row count drifted")
    conflict_ids = {
        row["row_id"] for row in rows if row.get("conflicting_observations") is True
    }
    if conflict_ids != EXPECTED_CONFLICT_ROW_IDS:
        raise ValueError(f"Historical conflict set drifted: {sorted(conflict_ids)}")
    if len({row["inchi_key"] for row in rows}) != len(rows):
        raise ValueError("Historical fixture contains duplicate identities")

    retained = [
        dict(row) for row in rows if row.get("conflicting_observations") is not True
    ]
    if len(retained) != contract["existing_surface"]["preserved_existing_row_count"]:
        raise ValueError("Preserved historical row count drifted")
    expected_retained = {
        item["family"]: int(item["preserved_eligible_row_count"]) for item in caps
    }
    if dict(Counter(row["family"] for row in retained)) != expected_retained:
        raise ValueError("Preserved family counts drifted")
    if max(Counter(row["source_doi"] for row in retained).values()) > MAX_ROWS_PER_ARTICLE:
        raise ValueError("Preserved historical rows already exceed the article cap")
    return retained


def quantile_target_indices(size: int, count: int) -> list[int]:
    if count < 1 or size < count:
        raise ValueError(f"Cannot choose {count} quantiles from {size} candidates")
    if count == 1:
        return [round((size - 1) / 2)]
    indices = [round(index * (size - 1) / (count - 1)) for index in range(count)]
    if len(set(indices)) != count:
        raise ValueError("Molecular-weight quantiles produced duplicate target indices")
    return indices


def select_additions(
    candidates: list[dict[str, Any]],
    count: int,
    article_counts: Counter[str],
) -> tuple[list[dict[str, Any]], list[dict[str, int]]]:
    ordered = sorted(
        candidates,
        key=lambda row: (row["molecular_weight_g_mol"], row["inchi_key"]),
    )
    selected: list[dict[str, Any]] = []
    selected_indices: set[int] = set()
    trace: list[dict[str, int]] = []

    for target in quantile_target_indices(len(ordered), count):
        chosen_index: int | None = None
        for offset in range(len(ordered)):
            candidate_index = (target + offset) % len(ordered)
            if candidate_index in selected_indices:
                continue
            candidate = ordered[candidate_index]
            if article_counts[candidate["source_doi"]] >= MAX_ROWS_PER_ARTICLE:
                continue
            chosen_index = candidate_index
            break
        if chosen_index is None:
            raise ValueError("Article cap prevents deterministic quantile selection")
        chosen = dict(ordered[chosen_index])
        selected.append(chosen)
        selected_indices.add(chosen_index)
        article_counts[chosen["source_doi"]] += 1
        trace.append(
            {
                "target_index": target,
                "selected_index": chosen_index,
                "forward_steps": (chosen_index - target) % len(ordered),
            }
        )
    return selected, trace


def effective_family_weighted_rows(family_counts: dict[str, int]) -> float:
    return 64.0 / sum(1.0 / family_counts[family] for family in SELECTED_FAMILIES)


def build_fixture(
    *,
    archive_metadata: dict[str, Any],
    contract_path: Path,
    contract: dict[str, Any],
    existing_fixture_path: Path,
    existing_fixture: dict[str, Any],
    representatives: list[dict[str, Any]],
    counters: Counter[str],
    dependencies: ThermoMLDependencies,
) -> dict[str, Any]:
    observed_counts = admissible_counts(representatives)
    retained = validate_frozen_inputs(contract, existing_fixture, observed_counts)
    all_existing_identities = {
        row["inchi_key"] for row in existing_fixture.get("rows", [])
    }
    admissible = [
        row
        for row in representatives
        if not row["conflicting_observations"]
        and row["expanded_uncertainty_k"] is not None
        and row["inchi_key"] not in all_existing_identities
    ]
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in admissible:
        by_family[row["family"]].append(row)

    article_counts: Counter[str] = Counter(row["source_doi"] for row in retained)
    caps = {item["family"]: item for item in contract["family_caps"]}
    additions: list[dict[str, Any]] = []
    selection_trace: dict[str, list[dict[str, int]]] = {}
    candidate_counts: dict[str, int] = {}
    for family in SELECTED_FAMILIES:
        candidates = by_family[family]
        candidate_counts[family] = len(candidates)
        family_additions, trace = select_additions(
            candidates,
            int(caps[family]["maximum_additions"]),
            article_counts,
        )
        additions.extend(family_additions)
        selection_trace[family] = trace

    output_rows: list[dict[str, Any]] = []
    for row in retained:
        preserved = dict(row)
        legacy_row_id = preserved.pop("row_id")
        output_rows.append(
            {
                "row_id": "",
                "fixture_origin": "retained_task0851",
                "legacy_row_id": legacy_row_id,
                **preserved,
            }
        )
    for row in additions:
        output_rows.append(
            {"row_id": "", "fixture_origin": "task1091_addition", **row}
        )
    output_rows.sort(
        key=lambda row: (
            SELECTED_FAMILIES.index(row["family"]),
            row["molecular_weight_g_mol"],
            row["inchi_key"],
        )
    )
    for index, row in enumerate(output_rows, start=1):
        row["row_id"] = f"TML-TB-FE-{index:04d}"

    family_counts = dict(Counter(row["family"] for row in output_rows))
    effective_rows = effective_family_weighted_rows(family_counts)
    row_count = len(output_rows)
    new_count = len(additions)
    max_article_rows = max(Counter(row["source_doi"] for row in output_rows).values())
    if row_count > int(contract["selected_option"]["maximum_total_rows"]):
        raise ValueError("Fixture exceeds the frozen row ceiling")
    if row_count < MINIMUM_TOTAL_ROWS or new_count < MINIMUM_NEW_IDENTITIES:
        raise ValueError("Fixture fails the total-row or new-identity floor")
    if min(family_counts.values()) < MINIMUM_ROWS_PER_FAMILY:
        raise ValueError("Fixture fails the per-family information floor")
    if set(family_counts) != set(SELECTED_FAMILIES):
        raise ValueError("Fixture does not preserve all eight families")
    if effective_rows < MINIMUM_EFFECTIVE_ROWS:
        raise ValueError("Fixture fails the equal-family effective-row floor")
    if max_article_rows > MAX_ROWS_PER_ARTICLE:
        raise ValueError("Fixture exceeds the source-article cap")

    screening_counts = Counter(counters)
    screening_counts["selected_family_observations"] = sum(
        row["observation_count"] for row in representatives
    )
    screening_counts["selected_family_representatives"] = len(representatives)
    return {
        "schema_version": "1",
        "task_id": "TASK-1091",
        "dataset_id": "thermoml-tb-feasible-expansion-v1",
        "verdict": "FIXTURE_EXTRACTION_PASS",
        "contract": {
            "contract_id": EXPECTED_CONTRACT_ID,
            "path": contract_path.as_posix(),
            "sha256": sha256_file(contract_path),
            "existing_fixture_path": existing_fixture_path.as_posix(),
            "existing_fixture_sha256": sha256_file(existing_fixture_path),
        },
        "source": {
            "source_id": "nist-trc-thermoml-archive",
            "product": "NIST TRC ThermoML Archive",
            "doi": "10.18434/mds2-2422",
            "archive_filename": archive_metadata["filename"],
            "archive_size_bytes": archive_metadata["size_bytes"],
            "archive_sha256": archive_metadata["sha256"],
            "archive_bytes_committed": False,
            "attribution": (
                "Data from the NIST TRC ThermoML Archive (DOI "
                "10.18434/mds2-2422), available with permission of the journal "
                "publishers; NIST does not critically evaluate deposited values."
            ),
        },
        "extraction": {
            "rdkit_version": dependencies.rdkit_version,
            "thermo_version": dependencies.thermo_version,
            "property": "Normal boiling temperature, K",
            "retained_existing_rows": len(retained),
            "new_identity_rows": new_count,
            "total_rows": row_count,
            "family_order": list(SELECTED_FAMILIES),
            "family_counts": family_counts,
            "candidate_counts_after_existing_identity_exclusion": candidate_counts,
            "selection_rule": (
                "family-local molecular-weight quantile targets with InChIKey "
                "tie-breaking; advance cyclically in candidate order only when "
                "an identity is used or the five-row article cap is reached"
            ),
            "selection_trace": selection_trace,
            "all_existing_fixture_identities_excluded_from_addition_pool": True,
            "conflict_flagged_legacy_rows_excluded": sorted(
                EXPECTED_CONFLICT_ROW_IDS
            ),
            "max_rows_per_source_article": max_article_rows,
            "equal_family_weighted_effective_row_count": round(effective_rows, 6),
            "screening_counts": dict(sorted(screening_counts.items())),
            "selection_is_value_blind_to_tb_and_model_outcomes": True,
        },
        "rights": {
            "reuse_status": "limited_factual_extract_with_attribution",
            "covered_by_repo_license": False,
            "max_public_rows_total": 80,
            "max_rows_per_source_article": MAX_ROWS_PER_ARTICLE,
            "source_bytes_redistribution": False,
            "raw_archive_or_xml_json_committed": False,
            "normalized_corpus_committed": False,
            "external_dataset_release_allowed": False,
        },
        "output_routing": {
            "source_readiness": "fixture_ready_for_separate_frozen_benchmark",
            "benchmark_scoring": "not_attempted",
            "gate_a": "not_attempted",
            "gate_b": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "existing_results_changed": False,
        },
        "rows": output_rows,
    }


def write_yaml(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        yaml.safe_dump(
            payload,
            sort_keys=False,
            allow_unicode=False,
            width=1000,
        ).encode("utf-8")
    )


def build_release_manifest(
    *,
    fixture_path: Path,
    fixture: dict[str, Any],
    contract_path: Path,
    existing_fixture_path: Path,
    extractor_path: Path,
) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "task_id": "TASK-1091",
        "release_id": "thermoml-tb-feasible-expansion-v1",
        "verdict": "FIXTURE_EXTRACTION_PASS",
        "fixture": {
            "path": fixture_path.as_posix(),
            "sha256": sha256_file(fixture_path),
            "size_bytes": fixture_path.stat().st_size,
            "row_count": fixture["extraction"]["total_rows"],
            "retained_existing_rows": fixture["extraction"]["retained_existing_rows"],
            "new_identity_rows": fixture["extraction"]["new_identity_rows"],
        },
        "frozen_inputs": {
            "contract_path": contract_path.as_posix(),
            "contract_sha256": sha256_file(contract_path),
            "existing_fixture_path": existing_fixture_path.as_posix(),
            "existing_fixture_sha256": sha256_file(existing_fixture_path),
            "source_archive_filename": fixture["source"]["archive_filename"],
            "source_archive_size_bytes": fixture["source"]["archive_size_bytes"],
            "source_archive_sha256": fixture["source"]["archive_sha256"],
        },
        "implementation": {
            "extractor_path": EXTRACTOR_PATH,
            "extractor_sha256": sha256_file(extractor_path),
        },
        "checks": {
            "archive_pin_match": True,
            "count_contract_reproduced": True,
            "conflict_rows_excluded": True,
            "article_cap_pass": True,
            "family_caps_pass": True,
            "minimum_total_rows_pass": True,
            "minimum_new_identities_pass": True,
            "equal_family_information_floor_pass": True,
            "selection_value_blind": True,
        },
        "rights": fixture["rights"],
        "output_routing": fixture["output_routing"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--existing-fixture", type=Path, required=True)
    parser.add_argument("--fixture-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    args = parser.parse_args()

    archive_metadata = verify_archive(args.archive)
    dependencies = _load_thermoml_dependencies()
    contract = load_yaml(args.contract)
    existing_fixture = load_yaml(args.existing_fixture)
    observations, counters = scan_archive(args.archive, dependencies)
    representatives = representatives_from_observations(observations)
    fixture = build_fixture(
        archive_metadata=archive_metadata,
        contract_path=args.contract,
        contract=contract,
        existing_fixture_path=args.existing_fixture,
        existing_fixture=existing_fixture,
        representatives=representatives,
        counters=counters,
        dependencies=dependencies,
    )
    write_yaml(fixture, args.fixture_output)
    manifest = build_release_manifest(
        fixture_path=args.fixture_output,
        fixture=fixture,
        contract_path=args.contract,
        existing_fixture_path=args.existing_fixture,
        extractor_path=Path(__file__).resolve(),
    )
    write_yaml(manifest, args.manifest_output)
    print(
        json.dumps(
            {
                "verdict": fixture["verdict"],
                "row_count": fixture["extraction"]["total_rows"],
                "retained_existing_rows": fixture["extraction"][
                    "retained_existing_rows"
                ],
                "new_identity_rows": fixture["extraction"]["new_identity_rows"],
                "family_counts": fixture["extraction"]["family_counts"],
                "max_rows_per_source_article": fixture["extraction"][
                    "max_rows_per_source_article"
                ],
                "equal_family_weighted_effective_row_count": fixture["extraction"][
                    "equal_family_weighted_effective_row_count"
                ],
                "fixture_sha256": manifest["fixture"]["sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
