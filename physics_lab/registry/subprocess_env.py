"""Reusable subprocess environment helpers."""

from __future__ import annotations

import os
from typing import Mapping


def env_with_overrides(
    env: Mapping[str, str] | None = None,
    **overrides: str | None,
) -> dict[str, str]:
    """Return an inherited child environment with explicit overrides applied.

    Subprocess tests often need to simulate one proxy, PATH, or token value while
    preserving dependency discovery from the active Python process. Passing a
    tiny replacement ``env={...}`` is reserved for tests whose point is to verify
    dependency loss or missing-tool behavior.
    """
    env_map = dict(os.environ if env is None else env)
    for name, value in overrides.items():
        if value is None:
            env_map.pop(name, None)
        else:
            env_map[name] = value
    return env_map
