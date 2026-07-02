#!/usr/bin/env python3
"""Count-only local preflight for the TASK-0906 ThermoML 80-row Tb expansion.

The helper reads a maintainer-provided, checksum-pinned ThermoML archive and
emits only aggregate identity/family/exclusion counts. It does not extract the
archive tree, publish selected identities, write ThermoML rows, or expose Tb
values in its public payload.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import tarfile
from typing import Any


EXPECTED_ARCHIVE_SHA256 = "231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2"
EXPECTED_ARCHIVE_SIZE = 189_433_115
TARGET_ROWS_PER_FAMILY = 10
CONFLICT_THRESHOLD_K = 1.0
SELECTED_FAMILIES = (
    "acids",
    "esters/lactones",
    "ketones",
    "alcohols/phenols",
    "ethers",
    "halocarbons",
    "aromatic hydrocarbons",
    "alkanes/cycloalkanes",
)

# thermo Joback group id -> the repository's frozen Joback table key.
GROUP_KEY_BY_ID = {
    1: "-CH3",
    2: "-CH2-",
    3: ">CH-",
    4: ">C<",
    5: "=CH2",
    6: "=CH-",
    7: "=C<",
    8: "=C=",
    9: "#CH",
    10: "#C-",
    11: "ring -CH2-",
    12: "ring >CH-",
    13: "ring >C<",
    14: "ring =CH-",
    15: "ring =C<",
    16: "-F",
    17: "-Cl",
    18: "-Br",
    19: "-I",
    20: "-OH (alcohol)",
    21: "-OH (phenol)",
    22: "-O- (non-ring)",
    23: "ring -O-",
    24: ">C=O (non-ring)",
    25: "ring >C=O",
    26: "O=CH- (aldehyde)",
    27: "-COOH (acid)",
    28: "-COO- (ester)",
    29: "=O (other than above)",
    30: "-NH2",
    31: ">NH (non-ring)",
    32: "ring >NH",
    33: ">N- (non-ring)",
    34: "-N= (non-ring)",
    35: "ring -N=",
    36: "=NH",
    37: "-CN",
    38: "-NO2",
    39: "-SH",
    40: "-S- (non-ring)",
    41: "ring -S-",
}
ALLOWED_ATOMIC_NUMBERS = {1, 6, 7, 8, 9, 15, 16, 17, 35, 53}
SIMPLE_FAMILY_ELEMENTS = {
    "acids": {1, 6, 8},
    "esters/lactones": {1, 6, 8},
    "ketones": {1, 6, 8},
    "alcohols/phenols": {1, 6, 8},
    "ethers": {1, 6, 8},
    "halocarbons": {1, 6, 9, 17, 35, 53},
    "aromatic hydrocarbons": {1, 6},
    "alkanes/cycloalkanes": {1, 6},
}
FORBIDDEN_PUBLIC_KEYS = {
    "rows",
    "observations",
    "experimental_tb_k",
    "standard_inchi",
    "source_member",
    "selected_identities",
}


@dataclass(frozen=True)
class ArchiveMetadata:
    filename: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class Observation:
    inchi_key: str
    family: str
    atomic_numbers: tuple[int, ...]
    molecular_weight_g_mol: float
    experimental_tb_k: float
    expanded_uncertainty_k: float | None
    source_doi: str
    source_member: str


@dataclass(frozen=True)
class ThermoMLDependencies:
    chem: Any
    joback: Any
    rdkit_version: str
    thermo_version: str


def _load_thermoml_dependencies() -> ThermoMLDependencies:
    try:
        from rdkit import Chem, __version__ as rdkit_version
        from thermo import __version__ as thermo_version
        from thermo.group_contribution.joback import Joback
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise SystemExit(
            "Install source-replay dependencies with: pip install -e '.[thermoml]'"
        ) from exc
    return ThermoMLDependencies(Chem, Joback, rdkit_version, thermo_version)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(archive: Path) -> ArchiveMetadata:
    size = archive.stat().st_size
    digest = _sha256(archive)
    if size != EXPECTED_ARCHIVE_SIZE or digest != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(f"ThermoML archive pin mismatch: size={size}, sha256={digest}")
    return ArchiveMetadata(filename=archive.name, size_bytes=size, sha256=digest)


def _property_name(prop: dict[str, Any]) -> str | None:
    groups = prop.get("Property-MethodID", {}).get("PropertyGroup", {})
    for value in groups.values():
        if isinstance(value, dict) and value.get("ePropName"):
            return str(value["ePropName"])
    return None


def _family(mol: Any, chem: Any) -> str | None:
    """Apply the frozen highest-priority functional-family taxonomy."""
    patterns = (
        ("acids", "[CX3](=O)[OX2H1]"),
        ("esters/lactones", "[CX3](=O)[OX2][#6]"),
        ("aldehydes", "[CX3H1](=O)[#6,H]"),
        ("ketones", "[#6][CX3](=O)[#6]"),
        ("alcohols/phenols", "[OX2H1][#6]"),
        ("ethers", "[#6][OX2][#6]"),
        ("nitriles", "[CX2]#N"),
        ("nitro", "[N+](=O)[O-]"),
        ("thiols/sulfides", "[#16]"),
        ("halocarbons", "[F,Cl,Br,I]"),
    )
    for name, smarts in patterns:
        if mol.HasSubstructMatch(chem.MolFromSmarts(smarts)):
            return name
    if any(atom.GetAtomicNum() == 7 for atom in mol.GetAtoms()):
        return "amines"
    atomic_numbers = {atom.GetAtomicNum() for atom in mol.GetAtoms()}
    if atomic_numbers <= {6} and any(atom.GetIsAromatic() for atom in mol.GetAtoms()):
        return "aromatic hydrocarbons"
    if atomic_numbers <= {6} and any(
        bond.GetBondTypeAsDouble() > 1.0 for bond in mol.GetBonds()
    ):
        return "alkenes/alkynes"
    if atomic_numbers <= {6}:
        return "alkanes/cycloalkanes"
    return None


def _zero_family_counts() -> dict[str, int]:
    return dict.fromkeys(SELECTED_FAMILIES, 0)


def _representatives_by_identity(observations: list[Observation]) -> dict[str, Observation]:
    by_identity: dict[str, list[Observation]] = defaultdict(list)
    for row in observations:
        by_identity[row.inchi_key].append(row)

    representatives: dict[str, Observation] = {}
    for inchi_key, rows in by_identity.items():
        representatives[inchi_key] = min(
            rows,
            key=lambda row: (
                row.expanded_uncertainty_k is None,
                row.expanded_uncertainty_k
                if row.expanded_uncertainty_k is not None
                else math.inf,
                row.source_doi,
                row.experimental_tb_k,
            ),
        )
    return representatives


def summarize_observations(
    observations: list[Observation],
    counters: Counter[str],
    archive: ArchiveMetadata,
    *,
    rdkit_version: str,
    thermo_version: str,
) -> dict[str, Any]:
    by_identity: dict[str, list[Observation]] = defaultdict(list)
    for row in observations:
        by_identity[row.inchi_key].append(row)

    counters = Counter(counters)
    counters["joback_covered_observations"] = len(observations)
    counters["joback_covered_unique_compounds"] = len(by_identity)
    representatives = _representatives_by_identity(observations)

    pre_conflict_counts = _zero_family_counts()
    admitted_counts = _zero_family_counts()
    conflict_counts = _zero_family_counts()
    missing_uncertainty_counts = _zero_family_counts()
    exclusion_counts: Counter[str] = Counter()

    for inchi_key, representative in representatives.items():
        family = representative.family
        atomic_numbers = set(representative.atomic_numbers)
        if family not in SELECTED_FAMILIES:
            exclusion_counts["outside_selected_family_identities"] += 1
            continue
        if not atomic_numbers <= SIMPLE_FAMILY_ELEMENTS[family]:
            exclusion_counts["selected_family_element_mismatch_identities"] += 1
            continue

        pre_conflict_counts[family] += 1
        identity_values = [row.experimental_tb_k for row in by_identity[inchi_key]]
        if max(identity_values) - min(identity_values) > CONFLICT_THRESHOLD_K:
            conflict_counts[family] += 1
            exclusion_counts["conflict_flagged_identities"] += 1
            continue
        if representative.expanded_uncertainty_k is None:
            missing_uncertainty_counts[family] += 1
            exclusion_counts["missing_uncertainty_identities"] += 1
            continue

        admitted_counts[family] += 1

    underpopulated = {
        family: {
            "admissible_count": count,
            "needed": TARGET_ROWS_PER_FAMILY,
            "shortfall": TARGET_ROWS_PER_FAMILY - count,
        }
        for family, count in admitted_counts.items()
        if count < TARGET_ROWS_PER_FAMILY
    }
    count_feasibility = (
        "FAMILY_UNDERPOPULATED" if underpopulated else "80_ROW_EXPANSION_FEASIBLE"
    )
    verdict = count_feasibility if underpopulated else "RIGHTS_DECISION_STILL_BLOCKS"
    payload = {
        "schema_version": "1",
        "task_id": "TASK-0906",
        "source": {
            "product": "NIST TRC ThermoML Archive",
            "doi": "10.18434/mds2-2422",
            "archive_filename": archive.filename,
            "archive_size_bytes": archive.size_bytes,
            "archive_sha256": archive.sha256,
            "archive_bytes_committed": False,
        },
        "extraction": {
            "rdkit_version": rdkit_version,
            "thermo_version": thermo_version,
            "property": "Normal boiling temperature, K",
            "target_rows_per_family": TARGET_ROWS_PER_FAMILY,
            "selected_families": list(SELECTED_FAMILIES),
            "conflict_threshold_k": CONFLICT_THRESHOLD_K,
            "dedup_rule": "smallest_reported_expanded_uncertainty_then_source_doi",
            "selection_rule_if_feasible": "molecular_weight_quantiles_after_count_preflight",
            "no_values_emitted": True,
            "no_rows_emitted": True,
        },
        "counts": {
            "screening_counts": dict(sorted(counters.items())),
            "selected_family_identity_counts_before_conflict_or_uncertainty_exclusion": (
                pre_conflict_counts
            ),
            "conflict_flagged_identity_counts_by_family": conflict_counts,
            "missing_uncertainty_identity_counts_by_family": missing_uncertainty_counts,
            "admissible_non_conflict_identity_counts_by_family": admitted_counts,
            "representative_exclusion_counts": dict(sorted(exclusion_counts.items())),
            "underpopulated_families": underpopulated,
        },
        "verdict": verdict,
        "count_feasibility": count_feasibility,
        "rights": {
            "local_analysis_allowed": True,
            "source_bytes_redistribution": False,
            "derived_rows_publication": "conditional",
            "rights_decision_still_required_for_public_rows": True,
        },
        "output_routing": {
            "canonical_destination": "docs/reviews/thermoml-tb-80row-local-count-preflight.md",
            "result_artifact": "none",
            "prediction_artifact": "none",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_0026_changed": False,
        },
    }
    assert_value_free_payload(payload)
    return payload


def _forbidden_keys(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_PUBLIC_KEYS:
                found.add(key)
            found.update(_forbidden_keys(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_forbidden_keys(item))
    return found


def assert_value_free_payload(payload: dict[str, Any]) -> None:
    forbidden = _forbidden_keys(payload)
    if forbidden:
        raise ValueError(f"Public payload contains value-bearing keys: {sorted(forbidden)}")


def preflight_counts_from_archive(archive_path: Path) -> dict[str, Any]:
    archive = verify_archive(archive_path)
    deps = _load_thermoml_dependencies()

    observations: list[Observation] = []
    counters: Counter[str] = Counter()
    with tarfile.open(archive_path, "r:gz") as tar:
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
            doi = str(document.get("Citation", {}).get("sDOI") or member.name[:-5])
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
                mol = deps.chem.MolFromInchi(inchi)
                if mol is None:
                    counters["inchi_parse_failed_blocks"] += 1
                    continue
                counters["identified_single_component_blocks"] += 1
                if len(deps.chem.GetMolFrags(mol)) != 1 or deps.chem.GetFormalCharge(mol) != 0:
                    counters["charged_or_multifragment_blocks"] += 1
                    continue
                atom_numbers = {atom.GetAtomicNum() for atom in mol.GetAtoms()}
                if not atom_numbers <= ALLOWED_ATOMIC_NUMBERS:
                    counters["unsupported_element_blocks"] += 1
                    continue
                joback = deps.joback(mol=mol)
                if not joback.success:
                    counters["joback_out_of_coverage_blocks"] += 1
                    continue
                if not {int(group_id) for group_id in joback.counts} <= set(GROUP_KEY_BY_ID):
                    counters["joback_group_table_mismatch_blocks"] += 1
                    continue
                family = _family(mol, deps.chem)
                if not family:
                    counters["unclassified_family_blocks"] += 1
                    continue

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
                            Observation(
                                inchi_key=str(inchi_key),
                                family=family,
                                atomic_numbers=tuple(sorted(atom_numbers)),
                                molecular_weight_g_mol=float(joback.MW),
                                experimental_tb_k=float(prop_value["nPropValue"]),
                                expanded_uncertainty_k=(
                                    float(uncertainty) if uncertainty is not None else None
                                ),
                                source_doi=doi,
                                source_member=member.name,
                            )
                        )

    return summarize_observations(
        observations,
        counters,
        archive,
        rdkit_version=deps.rdkit_version,
        thermo_version=deps.thermo_version,
    )


def _source_archive_not_available_payload(archive: Path) -> dict[str, Any]:
    payload = {
        "schema_version": "1",
        "task_id": "TASK-0906",
        "source": {
            "expected_archive_filename": "ThermoML.v2020-09-30.tgz",
            "expected_archive_size_bytes": EXPECTED_ARCHIVE_SIZE,
            "expected_archive_sha256": EXPECTED_ARCHIVE_SHA256,
            "requested_archive_path": str(archive),
            "archive_bytes_committed": False,
        },
        "verdict": "SOURCE_ARCHIVE_NOT_AVAILABLE",
        "counts": {},
        "output_routing": {
            "canonical_destination": "docs/reviews/thermoml-tb-80row-local-count-preflight.md",
            "result_artifact": "none",
            "prediction_artifact": "none",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_0026_changed": False,
        },
    }
    assert_value_free_payload(payload)
    return payload


def _write_payload(payload: dict[str, Any], output: Path | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.archive.exists():
        _write_payload(_source_archive_not_available_payload(args.archive), args.output)
        return 2

    payload = preflight_counts_from_archive(args.archive)
    _write_payload(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())