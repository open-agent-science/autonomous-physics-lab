import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "data/materials/oqmd_live_api_2026-07-14_split.yaml"
P = ("train", "validation", "holdout")
TARGET = {"train": 120, "validation": 26, "holdout": 26}
SOURCE = "af8991aefda6f408a3ad33251aa5564f5fed37a7d527b696d68442971bc978a4"


def load():
    return json.loads(SPLIT.read_text(encoding="utf-8"))


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def test_attestation_and_source_identity():
    d = load()
    a = d["session"]["attestation"]
    assert (
        d["task_id"] == "TASK-1053"
        and d["source"]["declared_source_sha256"] == SOURCE
        and d["source"]["identifier_only_input_row_count"] == 172
    )
    assert d["source"]["identifier_only_input_fields"] == [
        "entry_id",
        "reduced_composition",
        "spacegroup",
    ]
    assert all(
        a[k] is False
        for k in (
            "target_fields_accessed",
            "target_summaries_or_metrics_computed",
            "repository_normalized_or_raw_files_accessed",
            "git_accessed",
            "github_accessed",
            "network_accessed",
        )
    )


def test_reproducible_order_assignment_and_manifests():
    d = load()
    groups = d["ordered_group_manifest"]
    rows = d["ordered_row_manifest"]
    salt = d["algorithm"]["salt"]
    assert groups == sorted(
        groups,
        key=lambda g: (
            sha(f"{salt}|{g['reduced_composition']}"),
            g["reduced_composition"].encode(),
        ),
    )
    assert [g["ordinal"] for g in groups] == list(range(1, len(groups) + 1)) and [
        r["ordinal"] for r in rows
    ] == list(range(1, len(rows) + 1))
    assigned = dict.fromkeys(P, 0)
    expected = {}
    for g in groups:
        assert g["ordering_sha256"] == sha(f"{salt}|{g['reduced_composition']}")
        n = g["row_count"]

        def score(c):
            after = {p: assigned[p] + (n if p == c else 0) for p in P}
            return (sum(abs(TARGET[p] - after[p]) for p in P), P.index(c))

        chosen = min(P, key=score)
        assert g["partition"] == chosen
        assigned[chosen] += n
        expected[g["reduced_composition"]] = chosen
    assert assigned == TARGET and Counter(r["partition"] for r in rows) == Counter(TARGET)
    by_group = defaultdict(list)
    by_comp = defaultdict(set)
    for r in rows:
        by_group[r["group_ordinal"]].append(r)
        by_comp[r["reduced_composition"]].add(r["partition"])
        assert r["partition"] == expected[r["reduced_composition"]]
    for g in groups:
        assert (
            len(by_group[g["ordinal"]]) == g["row_count"]
            and [r["entry_id"] for r in by_group[g["ordinal"]]] == g["entry_ids"]
        )
    assert all(len(v) == 1 for v in by_comp.values()) and len({r["entry_id"] for r in rows}) == 172
    for p in P:
        m = d["split_manifests"][p]
        assert m["group_ordinals"] == [g["ordinal"] for g in groups if g["partition"] == p]
        assert m["row_ordinals"] == [r["ordinal"] for r in rows if r["partition"] == p] and m[
            "entry_ids"
        ] == [r["entry_id"] for r in rows if r["partition"] == p]


def test_leakage_holdout_counts_and_verdict():
    d = load()
    v = d["verification"]
    assert d["counts"]["rows_by_partition"] == TARGET
    assert (
        v["composition_groups_atomic"]
        and v["spacegroup_variants_of_same_composition_coassigned"]
        and not v["cross_partition_composition_leakage"]
    )
    assert (
        v["holdout_minimum_rows"] == 24
        and d["counts"]["rows_by_partition"]["holdout"] >= 24
        and v["holdout_minimum_satisfied"]
    )
    assert v["targets_reached_exactly"] and d["verdict"] == "SPLIT_READY_FOR_BENCHMARK_PREFLIGHT"
