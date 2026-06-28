#!/usr/bin/env python3
"""Extract the bounded TASK-0851 Tb audit fixture from a verified ThermoML archive.

This source-replay tool requires ``pip install -e '.[thermoml]'``. It never
extracts the archive tree and emits only forty value-blind selected factual rows,
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
    from rdkit import Chem, __version__ as rdkit_version
    from thermo import __version__ as thermo_version
    from thermo.group_contribution.joback import Joback
except ImportError as exc:  # pragma: no cover - optional source-replay dependency
    raise SystemExit("Install source-replay dependencies with: pip install -e '.[thermoml]'") from exc

EXPECTED_ARCHIVE_SHA256 = "231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2"
EXPECTED_ARCHIVE_SIZE = 189_433_115
ROWS_PER_FAMILY = 5
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
    1: "-CH3", 2: "-CH2-", 3: ">CH-", 4: ">C<", 5: "=CH2", 6: "=CH-",
    7: "=C<", 8: "=C=", 9: "#CH", 10: "#C-", 11: "ring -CH2-",
    12: "ring >CH-", 13: "ring >C<", 14: "ring =CH-", 15: "ring =C<",
    16: "-F", 17: "-Cl", 18: "-Br", 19: "-I", 20: "-OH (alcohol)",
    21: "-OH (phenol)", 22: "-O- (non-ring)", 23: "ring -O-",
    24: ">C=O (non-ring)", 25: "ring >C=O", 26: "O=CH- (aldehyde)",
    27: "-COOH (acid)", 28: "-COO- (ester)", 29: "=O (other than above)",
    30: "-NH2", 31: ">NH (non-ring)", 32: "ring >NH", 33: ">N- (non-ring)",
    34: "-N= (non-ring)", 35: "ring -N=", 36: "=NH", 37: "-CN",
    38: "-NO2", 39: "-SH", 40: "-S- (non-ring)", 41: "ring -S-",
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _property_name(prop: dict[str, Any]) -> str | None:
    groups = prop.get("Property-MethodID", {}).get("PropertyGroup", {})
    for value in groups.values():
        if isinstance(value, dict) and value.get("ePropName"):
            return str(value["ePropName"])
    return None


def _family(mol: Any) -> str | None:
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
        if mol.HasSubstructMatch(Chem.MolFromSmarts(smarts)):
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


def _quantile_select(rows: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: (row["molecular_weight_g_mol"], row["inchi_key"]))
    if len(ordered) < count:
        raise ValueError(f"Need at least {count} rows, found {len(ordered)}")
    indices = [round(index * (len(ordered) - 1) / (count - 1)) for index in range(count)]
    if len(set(indices)) != count:
        raise ValueError("Molecular-weight quantile selection produced duplicate indices")
    return [ordered[index] for index in indices]


def extract_fixture(archive: Path) -> dict[str, Any]:
    archive_size = archive.stat().st_size
    archive_sha = _sha256(archive)
    if archive_size != EXPECTED_ARCHIVE_SIZE or archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(
            f"ThermoML archive pin mismatch: size={archive_size}, sha256={archive_sha}"
        )

    observations: list[dict[str, Any]] = []
    counters: Counter[str] = Counter()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            if not (member.isfile() and member.name.endswith(".json")):
                continue
            counters["archive_json_files"] += 1
            raw = tar.extractfile(member).read()  # type: ignore[union-attr]
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
                components = block.get("Component", [])
                if len(components) != 1:
                    continue
                normal_numbers = {
                    prop.get("nPropNumber")
                    for prop in block.get("Property", [])
                    if _property_name(prop) == "Normal boiling temperature, K"
                }
                if not normal_numbers:
                    continue
                compound = compounds.get(
                    components[0].get("RegNum", {}).get("nOrgNum")
                )
                if not compound:
                    continue
                inchi = compound.get("sStandardInChI")
                inchi_key = compound.get("sStandardInChIKey")
                if not inchi or not inchi_key:
                    counters["missing_standard_identity_blocks"] += 1
                    continue
                mol = Chem.MolFromInchi(inchi)
                if mol is None:
                    counters["inchi_parse_failed_blocks"] += 1
                    continue
                counters["identified_single_component_blocks"] += 1
                if len(Chem.GetMolFrags(mol)) != 1 or Chem.GetFormalCharge(mol) != 0:
                    counters["charged_or_multifragment_blocks"] += 1
                    continue
                atom_numbers = {atom.GetAtomicNum() for atom in mol.GetAtoms()}
                if not atom_numbers <= ALLOWED_ATOMIC_NUMBERS:
                    counters["unsupported_element_blocks"] += 1
                    continue
                joback = Joback(mol=mol)
                if not joback.success:
                    counters["joback_out_of_coverage_blocks"] += 1
                    continue
                family = _family(mol)
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
                                "source_doi": doi,
                                "source_member": member.name,
                                "joback_group_counts": group_counts,
                            }
                        )

    by_identity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        by_identity[row["inchi_key"]].append(row)
    counters["joback_covered_observations"] = len(observations)
    counters["joback_covered_unique_compounds"] = len(by_identity)

    representatives: list[dict[str, Any]] = []
    for identity_rows in by_identity.values():
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
        representative = {key: value for key, value in chosen.items() if key != "atomic_numbers"}
        representative.update(
            {
                "observation_count": len(identity_rows),
                "observed_tb_span_k": round(max(values) - min(values), 6),
                "conflicting_observations": bool(max(values) - min(values) > 1.0),
                "selection_rule": "smallest_reported_expanded_uncertainty_then_source_doi",
            }
        )
        if (
            representative["family"] in SELECTED_FAMILIES
            and set(chosen["atomic_numbers"])
            <= SIMPLE_FAMILY_ELEMENTS[representative["family"]]
        ):
            representatives.append(representative)

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in representatives:
        by_family[row["family"]].append(row)
    selected: list[dict[str, Any]] = []
    candidate_counts: dict[str, int] = {}
    for family in SELECTED_FAMILIES:
        candidate_counts[family] = len(by_family[family])
        for row in _quantile_select(by_family[family], ROWS_PER_FAMILY):
            selected.append({"row_id": f"TML-TB-{len(selected) + 1:04d}", **row})

    return {
        "schema_version": "1",
        "task_id": "TASK-0851",
        "dataset_id": "thermoml-tb-bounded-family-audit-v1",
        "source": {
            "product": "NIST TRC ThermoML Archive",
            "doi": "10.18434/mds2-2422",
            "archive_filename": archive.name,
            "archive_size_bytes": archive_size,
            "archive_sha256": archive_sha,
            "archive_bytes_committed": False,
            "attribution": "Data from the NIST TRC ThermoML Archive, available with permission of the journal publishers; NIST does not critically evaluate deposited values.",
        },
        "extraction": {
            "rdkit_version": rdkit_version,
            "thermo_version": thermo_version,
            "property": "Normal boiling temperature, K",
            "scoring_intercept_k": 198.2,
            "selection_is_value_blind_to_joback_error": True,
            "dedup_rule": "smallest reported expanded uncertainty, then source DOI and value",
            "family_selection_rule": f"{ROWS_PER_FAMILY} molecular-weight quantile rows per predeclared simple family",
            "selected_families": list(SELECTED_FAMILIES),
            "candidate_counts_by_family": candidate_counts,
            "screening_counts": dict(sorted(counters.items())),
        },
        "rights": {
            "local_analysis_allowed": True,
            "source_bytes_redistribution": False,
            "derived_rows_publication": "conditional_bounded_factual_extract",
            "substantial_corpus_committed": False,
        },
        "rows": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = extract_fixture(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=1000).encode("utf-8")
    )
    print(json.dumps({
        "dataset_id": payload["dataset_id"],
        "row_count": len(payload["rows"]),
        "families": payload["extraction"]["selected_families"],
        "archive_sha256": payload["source"]["archive_sha256"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
