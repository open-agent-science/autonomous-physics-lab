from __future__ import annotations

from pathlib import Path

from physics_lab.registry.reviews_policy import (
    build_reviews_inventory,
    render_reviews_inventory,
    root_review_additions_from_name_status,
)


def test_root_review_guard_only_flags_new_flat_root_files() -> None:
    lines = [
        "A\tdocs/reviews/new-flat-review.md",
        "A\tdocs/reviews/nuclear/new-sharded-review.md",
        "A\tdocs/reviews/README.md",
        "M\tdocs/reviews/existing-flat-review.md",
        "R100\tdocs/notes/old.md\tdocs/reviews/renamed-flat-review.md",
        "C100\tdocs/notes/old.md\tdocs/reviews/workflow/copied-sharded-review.md",
    ]

    assert root_review_additions_from_name_status(lines) == (
        "docs/reviews/new-flat-review.md",
        "docs/reviews/renamed-flat-review.md",
    )


def test_reviews_inventory_recurses_and_keeps_legacy_root_group(tmp_path: Path) -> None:
    reviews = tmp_path / "docs" / "reviews"
    reviews.mkdir(parents=True)
    (reviews / "README.md").write_text("policy\n", encoding="utf-8")
    (reviews / "legacy-review.md").write_text("# Legacy\n", encoding="utf-8")
    (reviews / "nuclear").mkdir()
    (reviews / "nuclear" / "new-review.md").write_text("# Nuclear\n", encoding="utf-8")

    inventory = build_reviews_inventory(tmp_path)

    assert inventory.total_files == 2
    assert inventory.counts_by_group == {"legacy-root": 1, "nuclear": 1}
    assert "legacy-root: 1" in render_reviews_inventory(inventory)
    assert "nuclear: 1" in render_reviews_inventory(inventory)
