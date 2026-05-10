from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physics_lab.registry.microtask_queue_summary import refresh_microtask_queue_summary  # noqa: E402


def main() -> int:
    root = ROOT
    readme = root / "tasks" / "microtasks" / "README.md"
    refresh_microtask_queue_summary(readme, root)
    print(f"Updated {readme.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
