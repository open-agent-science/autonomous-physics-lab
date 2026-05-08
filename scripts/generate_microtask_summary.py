from pathlib import Path
from collections import Counter
import yaml

MICROTASK_DIR = Path("tasks/microtasks")


def load_queue(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def summarize_queue(data: dict) -> dict:
    microtasks = data.get("microtasks", [])

    risk_counter = Counter(
        item.get("risk_level", "unknown")
        for item in microtasks
    )

    return {
        "queue_id": data.get("queue_id", "unknown"),
        "campaign_status": data.get("campaign_status", "unknown"),
        "task_count": len(microtasks),
        "low": risk_counter.get("low", 0),
        "medium": risk_counter.get("medium", 0),
        "high": risk_counter.get("high", 0),
    }


def generate_table(rows: list[dict]) -> str:
    lines = [
        "## Queue Summary",
        "",
        "| Queue ID | Campaign Status | Tasks | Low | Medium | High |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['queue_id']} "
            f"| {row['campaign_status']} "
            f"| {row['task_count']} "
            f"| {row['low']} "
            f"| {row['medium']} "
            f"| {row['high']} |"
        )

    return "\n".join(lines)


def main():
    rows = []

    for path in sorted(MICROTASK_DIR.glob("*.yaml")):
        data = load_queue(path)
        rows.append(summarize_queue(data))

    print(generate_table(rows))


if __name__ == "__main__":
    main()