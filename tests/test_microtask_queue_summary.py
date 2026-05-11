from __future__ import annotations

import textwrap
from pathlib import Path

from physics_lab.registry.microtask_queue_summary import (
    SUMMARY_END,
    SUMMARY_START,
    load_microtask_queue_summaries,
    refresh_microtask_queue_summary,
    render_microtask_queue_summary_table,
)


def _write_queue(root: Path, name: str = "example-queue") -> Path:
    path = root / "tasks" / "microtasks" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            f"""\
            queue_id: {name}
            campaign: example-campaign
            campaign_status: active
            selection_guidance:
              - "Prefer narrow reviewable work."
            microtasks:
              - id: EX-001
                campaign: example-campaign
                title: First item
                type: note
                estimated_effort: 10-20 minutes
                recommended_for:
                  - codex
                autonomy_level:
                  - agent_can_complete
                expected_output: "One note."
                validation:
                  - "State scope."
                risk_level: low
              - id: EX-002
                campaign: example-campaign
                title: Retired item
                type: note
                status: retired
                status_reason: "Covered by a newer canonical task."
                estimated_effort: 10-20 minutes
                recommended_for:
                  - codex
                autonomy_level:
                  - agent_can_complete
                expected_output: "One note."
                validation:
                  - "State scope."
                risk_level: medium
            """
        ),
        encoding="utf-8",
    )
    return path


def test_load_microtask_queue_summaries_reads_queue_metadata(tmp_path: Path) -> None:
    _write_queue(tmp_path)

    summaries = load_microtask_queue_summaries(tmp_path)

    assert len(summaries) == 1
    assert summaries[0].queue_id == "example-queue"
    assert summaries[0].microtask_count == 2
    assert summaries[0].available_count == 1
    assert summaries[0].completed_count == 0
    assert summaries[0].retired_count == 1
    assert summaries[0].risk_levels == ("low",)


def test_render_microtask_queue_summary_table_links_to_queue_file(tmp_path: Path) -> None:
    _write_queue(tmp_path)
    summaries = load_microtask_queue_summaries(tmp_path)

    table = render_microtask_queue_summary_table(summaries)

    assert "[`example-queue`](example-queue.yaml)" in table
    assert "example-campaign" in table
    assert "1 / 2" in table
    assert "`active`" in table
    assert "Prefer narrow reviewable work." in table


def test_refresh_microtask_queue_summary_replaces_marked_section(tmp_path: Path) -> None:
    _write_queue(tmp_path)
    readme = tmp_path / "tasks" / "microtasks" / "README.md"
    readme.write_text(
        textwrap.dedent(
            f"""\
            # Scientific Microtask Queues

            {SUMMARY_START}

            old table

            {SUMMARY_END}
            """
        ),
        encoding="utf-8",
    )

    refresh_microtask_queue_summary(readme, tmp_path)

    updated = readme.read_text(encoding="utf-8")
    assert "old table" not in updated
    assert "[`example-queue`](example-queue.yaml)" in updated
