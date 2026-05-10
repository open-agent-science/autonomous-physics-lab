from __future__ import annotations

from pathlib import Path

from physics_lab.registry.microtask_queue_summary import refresh_microtask_queue_summary


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    readme = root / "tasks" / "microtasks" / "README.md"
    refresh_microtask_queue_summary(readme, root)
    print(f"Updated {readme.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
