#!/usr/bin/env python3
"""Build the source-gated NMD-0003 AME2020 measured training dataset."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml


SOURCE_SHA256 = "e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
SOURCE_BYTE_SIZE = 472648
SOURCE_URL = "https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt"
SOURCE_PAGE = "https://amdc.impcas.ac.cn/web/masseval.html"
ACCESS_DATE = "2026-06-01"

ELEMENT_NAMES = {
    "H": "hydrogen",
    "He": "helium",
    "Li": "lithium",
    "Be": "beryllium",
    "B": "boron",
    "C": "carbon",
    "N": "nitrogen",
    "O": "oxygen",
    "F": "fluorine",
    "Ne": "neon",
    "Na": "sodium",
    "Mg": "magnesium",
    "Al": "aluminium",
    "Si": "silicon",
    "P": "phosphorus",
    "S": "sulfur",
    "Cl": "chlorine",
    "Ar": "argon",
    "K": "potassium",
    "Ca": "calcium",
    "Sc": "scandium",
    "Ti": "titanium",
    "V": "vanadium",
    "Cr": "chromium",
    "Mn": "manganese",
    "Fe": "iron",
    "Co": "cobalt",
    "Ni": "nickel",
    "Cu": "copper",
    "Zn": "zinc",
    "Ga": "gallium",
    "Ge": "germanium",
    "As": "arsenic",
    "Se": "selenium",
    "Br": "bromine",
    "Kr": "krypton",
    "Rb": "rubidium",
    "Sr": "strontium",
    "Y": "yttrium",
    "Zr": "zirconium",
    "Nb": "niobium",
    "Mo": "molybdenum",
    "Tc": "technetium",
    "Ru": "ruthenium",
    "Rh": "rhodium",
    "Pd": "palladium",
    "Ag": "silver",
    "Cd": "cadmium",
    "In": "indium",
    "Sn": "tin",
    "Sb": "antimony",
    "Te": "tellurium",
    "I": "iodine",
    "Xe": "xenon",
    "Cs": "caesium",
    "Ba": "barium",
    "La": "lanthanum",
    "Ce": "cerium",
    "Pr": "praseodymium",
    "Nd": "neodymium",
    "Pm": "promethium",
    "Sm": "samarium",
    "Eu": "europium",
    "Gd": "gadolinium",
    "Tb": "terbium",
    "Dy": "dysprosium",
    "Ho": "holmium",
    "Er": "erbium",
    "Tm": "thulium",
    "Yb": "ytterbium",
    "Lu": "lutetium",
    "Hf": "hafnium",
    "Ta": "tantalum",
    "W": "tungsten",
    "Re": "rhenium",
    "Os": "osmium",
    "Ir": "iridium",
    "Pt": "platinum",
    "Au": "gold",
    "Hg": "mercury",
    "Tl": "thallium",
    "Pb": "lead",
    "Bi": "bismuth",
    "Po": "polonium",
    "At": "astatine",
    "Rn": "radon",
    "Fr": "francium",
    "Ra": "radium",
    "Ac": "actinium",
    "Th": "thorium",
    "Pa": "protactinium",
    "U": "uranium",
    "Np": "neptunium",
    "Pu": "plutonium",
    "Am": "americium",
    "Cm": "curium",
    "Bk": "berkelium",
    "Cf": "californium",
    "Es": "einsteinium",
    "Fm": "fermium",
    "Md": "mendelevium",
    "No": "nobelium",
    "Lr": "lawrencium",
    "Rf": "rutherfordium",
    "Db": "dubnium",
    "Sg": "seaborgium",
    "Bh": "bohrium",
    "Hs": "hassium",
    "Mt": "meitnerium",
    "Ds": "darmstadtium",
    "Rg": "roentgenium",
    "Cn": "copernicium",
    "Nh": "nihonium",
    "Fl": "flerovium",
    "Mc": "moscovium",
    "Lv": "livermorium",
    "Ts": "tennessine",
    "Og": "oganesson",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_primary_holdout_ids(path: Path) -> set[str]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        str(entry["nuclide_id"])
        for entry in payload["entries"]
        if bool(entry["included_in_time_split_holdout"])
    }


def _has_estimated_or_missing_value(line: str) -> bool:
    fields = (
        line[28:42],
        line[42:54],
        line[110:123],
        line[123:135],
    )
    return any("#" in field or "*" in field for field in fields)


def _atomic_mass_u(line: str) -> float:
    integer_micro_u = int(line[106:109])
    fractional_micro_u = float(line[110:123].strip().replace(" ", ""))
    return (integer_micro_u * 1_000_000.0 + fractional_micro_u) / 1_000_000.0


def parse_measured_entries(source_path: Path, primary_holdout_ids: set[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    counts = {
        "source_data_rows": 0,
        "z0_rows_excluded": 0,
        "estimated_or_missing_rows_excluded": 0,
        "primary_holdout_rows_excluded": 0,
    }

    for line_number, line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), start=1):
        if line_number <= 36 or len(line) < 123:
            continue
        try:
            z = int(line[9:14])
            n = int(line[4:9])
            a = int(line[14:19])
        except ValueError:
            continue

        counts["source_data_rows"] += 1
        if z == 0:
            counts["z0_rows_excluded"] += 1
            continue

        symbol = line[20:23].strip()
        nuclide_id = f"{symbol}-{a}"
        if _has_estimated_or_missing_value(line):
            counts["estimated_or_missing_rows_excluded"] += 1
            continue
        if nuclide_id in primary_holdout_ids:
            counts["primary_holdout_rows_excluded"] += 1
            continue
        if nuclide_id in seen:
            raise ValueError(f"Duplicate NMD-0003 nuclide id after filtering: {nuclide_id}")
        seen.add(nuclide_id)

        entries.append(
            {
                "nuclide_id": nuclide_id,
                "element": ELEMENT_NAMES[symbol],
                "symbol": symbol,
                "Z": z,
                "N": n,
                "A": a,
                "evaluation": "measured",
                "source_entry": f"mass_1.mas20:line-{line_number}",
                "notes": (
                    "AME2020 unrounded mass table row with no # estimated-value marker "
                    "in mass-excess or atomic-mass fields; primary post-AME2020 "
                    "holdout ids are excluded from this training surface."
                ),
                "mass_excess_keV": float(line[28:42]),
                "mass_excess_uncertainty_keV": float(line[42:54]),
                "atomic_mass_u": _atomic_mass_u(line),
                "atomic_mass_uncertainty_u": float(line[123:135]) / 1_000_000.0,
            }
        )

    return entries, counts


def _dataset_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "dataset_id": "NMD-0003",
        "title": "AME2020 measured-row nuclear-mass training surface",
        "status": "curated",
        "description": (
            "Source-gated AME2020 measured-row training surface for Nuclear Mass "
            "Surface factory and residual diagnostics. Rows with AME2020 # "
            "estimated-value markers and primary post-AME2020 holdout nuclides "
            "are excluded from this training dataset."
        ),
        "source_policy": (
            "Pinned AME2020 ASCII mass table parsed from the IAEA AMDC mirror. "
            "The raw source file is not vendored; its URL, checksum, byte size, "
            "format notes, citation, and redistribution boundary are recorded in "
            "data/nuclear_masses/nmd-0003-source-manifest.yaml. Default training "
            "eligibility is measured rows only."
        ),
        "source_dataset": {
            "authority": "Atomic Mass Data Center / AMDC",
            "version": "AME2020 mass_1.mas20, unrounded atomic mass table",
            "citation": (
                "W.J. Huang, M. Wang, F.G. Kondev, G. Audi, and S. Naimi, "
                "The AME 2020 atomic mass evaluation (I), Chinese Physics C 45, "
                "030002 (2021); M. Wang, W.J. Huang, F.G. Kondev, G. Audi, and "
                "S. Naimi, The AME 2020 atomic mass evaluation (II), Chinese "
                "Physics C 45, 030003 (2021)."
            ),
            "url": SOURCE_URL,
            "accessed_on": ACCESS_DATE,
            "checksum_sha256": SOURCE_SHA256,
            "checksum_scope": "Raw AME2020 mass_1.mas20.txt source artifact bytes from IAEA AMDC mirror.",
            "license_note": (
                "Structured row values are committed for APL validation; the raw "
                "AMDC ASCII file is not vendored. AMDC asks users to cite the "
                "original AME2020 papers rather than the electronic files."
            ),
        },
        "entries": entries,
    }


def _source_manifest_payload(
    *,
    dataset_sha256: str,
    split_sha256: str | None,
    counts: dict[str, int],
    training_count: int,
    primary_holdout_count: int,
) -> dict[str, Any]:
    return {
        "manifest_id": "NMD-0003-SOURCE-MANIFEST",
        "task_id": "TASK-0516",
        "dataset_id": "NMD-0003",
        "status": "review_ready_source_manifest",
        "created_on": ACCESS_DATE,
        "source": {
            "authority": "Atomic Mass Data Center / AMDC",
            "official_page": SOURCE_PAGE,
            "retrieval_url": SOURCE_URL,
            "mirror_role": "IAEA Nuclear Data Services AMDC mirror",
            "version": "AME2020 mass_1.mas20 unrounded atomic mass table",
            "sha256": SOURCE_SHA256,
            "byte_size": SOURCE_BYTE_SIZE,
            "accessed_on": ACCESS_DATE,
            "format_note": (
                "Fixed-width AME2020 mass table; header records # as an estimated "
                "(non-experimental) value marker."
            ),
        },
        "citation": {
            "part_i": "Chinese Physics C 45, 030002 (2021), doi:10.1088/1674-1137/abddb0",
            "part_ii": "Chinese Physics C 45, 030003 (2021), doi:10.1088/1674-1137/abddaf",
            "citation_rule": "Cite the AME2020 papers rather than the electronic files.",
        },
        "redistribution_boundary": {
            "raw_source_vendored": False,
            "committed_values": "Normalized measured row values needed for deterministic APL validation.",
            "note": (
                "The source manifest pins the raw artifact checksum and retrieval "
                "location; the repository commits structured row values, not the "
                "publisher/AMDC raw ASCII artifact."
            ),
        },
        "filtering": {
            "source_data_rows": counts["source_data_rows"],
            "z0_rows_excluded": counts["z0_rows_excluded"],
            "estimated_or_missing_rows_excluded": counts["estimated_or_missing_rows_excluded"],
            "primary_post_ame2020_holdout_rows_excluded": counts["primary_holdout_rows_excluded"],
            "primary_post_ame2020_holdout_row_count": primary_holdout_count,
            "committed_training_row_count": training_count,
            "measured_rule": (
                "A row is eligible only when mass-excess and atomic-mass value and "
                "uncertainty fields contain no # estimated-value marker and no * "
                "not-calculable marker."
            ),
        },
        "committed_artifacts": {
            "training_dataset": "data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml",
            "training_dataset_sha256": dataset_sha256,
            "split_manifest": "data/nuclear_masses/nmd-0003-split-manifest.yaml",
            "split_manifest_sha256": split_sha256,
        },
        "claim_ceiling": (
            "Source-curated training dataset only. No candidate metric, benchmark "
            "result, prediction, claim, or knowledge artifact is promoted."
        ),
    }


def _split_manifest_payload(
    *,
    entries: list[dict[str, Any]],
    primary_holdout_ids: set[str],
    dataset_sha256: str,
    counts: dict[str, int],
) -> dict[str, Any]:
    training_ids = [str(entry["nuclide_id"]) for entry in entries]
    return {
        "split_manifest_id": "NMD-0003-SPLIT-MANIFEST",
        "task_id": "TASK-0516",
        "dataset_id": "NMD-0003",
        "status": "frozen_split_manifest",
        "created_on": ACCESS_DATE,
        "source_dataset": "data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml",
        "source_dataset_sha256": dataset_sha256,
        "training_split": {
            "name": "ame2020_measured_training_excluding_post_ame2020_primary_holdout",
            "row_count": len(training_ids),
            "eligibility": [
                "AME2020 row has no # estimated-value marker in mass-excess value.",
                "AME2020 row has no # estimated-value marker in mass-excess uncertainty.",
                "AME2020 row has no # estimated-value marker in atomic-mass value.",
                "AME2020 row has no # estimated-value marker in atomic-mass uncertainty.",
                "Nuclide id is not a primary post-AME2020 holdout id.",
                "Z > 0; the free neutron row is excluded from the nuclear training surface.",
            ],
            "nuclide_ids": training_ids,
        },
        "excluded_splits": {
            "primary_post_ame2020_holdout": {
                "source": "data/nuclear_masses/post_ame2020_holdout.yaml",
                "row_count": len(primary_holdout_ids),
                "excluded_from_training": True,
                "nuclide_ids": sorted(primary_holdout_ids),
            },
            "ame2020_estimated_or_missing_rows": {
                "row_count": counts["estimated_or_missing_rows_excluded"],
                "excluded_from_training": True,
                "reason": "AME2020 # estimated-value marker or * not-calculable marker.",
            },
            "z0_rows": {
                "row_count": counts["z0_rows_excluded"],
                "excluded_from_training": True,
                "reason": "Z=0 free-neutron row is outside the nuclide training split.",
            },
        },
        "holdout_boundary": (
            "post_ame2020_holdout.yaml remains a retrospective time-split holdout "
            "surface and is not absorbed into NMD-0003 training."
        ),
    }


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def build(source_file: Path, holdout_file: Path, output_dir: Path) -> None:
    source_sha = _sha256(source_file)
    if source_sha != SOURCE_SHA256:
        raise ValueError(f"Unexpected source SHA-256 for {source_file}: {source_sha}")
    if source_file.stat().st_size != SOURCE_BYTE_SIZE:
        raise ValueError(f"Unexpected source byte size for {source_file}: {source_file.stat().st_size}")

    primary_holdout_ids = _load_primary_holdout_ids(holdout_file)
    entries, counts = parse_measured_entries(source_file, primary_holdout_ids)

    dataset_path = output_dir / "nmd-0003-ame2020-measured-training.yaml"
    split_path = output_dir / "nmd-0003-split-manifest.yaml"
    source_manifest_path = output_dir / "nmd-0003-source-manifest.yaml"

    _write_yaml(dataset_path, _dataset_payload(entries))
    dataset_sha = _sha256(dataset_path)

    _write_yaml(
        split_path,
        _split_manifest_payload(
            entries=entries,
            primary_holdout_ids=primary_holdout_ids,
            dataset_sha256=dataset_sha,
            counts=counts,
        ),
    )
    split_sha = _sha256(split_path)

    _write_yaml(
        source_manifest_path,
        _source_manifest_payload(
            dataset_sha256=dataset_sha,
            split_sha256=split_sha,
            counts=counts,
            training_count=len(entries),
            primary_holdout_count=len(primary_holdout_ids),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file", required=True, type=Path)
    parser.add_argument(
        "--holdout-file",
        default=Path("data/nuclear_masses/post_ame2020_holdout.yaml"),
        type=Path,
    )
    parser.add_argument("--output-dir", default=Path("data/nuclear_masses"), type=Path)
    args = parser.parse_args()
    build(args.source_file, args.holdout_file, args.output_dir)


if __name__ == "__main__":
    main()
