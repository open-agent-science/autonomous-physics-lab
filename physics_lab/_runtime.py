"""Central Python runtime requirement for Autonomous Physics Lab.

This module is the single source of truth for the minimum supported Python
version (it mirrors ``requires-python`` in ``pyproject.toml``). It is intentionally
dependency-free and avoids Python 3.10+ syntax so it can be imported and run under
an unsupported interpreter and still produce a clear, actionable message instead of
a cryptic ``SyntaxError`` or ``TypeError`` from newer language features.

APL is intentionally single-runtime at Python 3.11+. This guard exists to make that
requirement legible and fast-failing; it is not a compatibility shim for older
interpreters.
"""

from __future__ import annotations

import sys

# Single source of truth. Keep in sync with pyproject.toml requires-python.
MINIMUM_PYTHON = (3, 11)
MINIMUM_PYTHON_DISPLAY = "3.11"


def is_supported(version_info=sys.version_info):
    """Return ``True`` when ``version_info`` meets the minimum supported Python."""
    return tuple(version_info[:2]) >= MINIMUM_PYTHON


def current_version_display(version_info=sys.version_info):
    """Return a human ``major.minor.micro`` string for ``version_info``."""
    return "{0}.{1}.{2}".format(version_info[0], version_info[1], version_info[2])


def unsupported_message(version_info=sys.version_info):
    """Return an actionable message for running under an unsupported interpreter."""
    return (
        "Autonomous Physics Lab requires Python {required}+, but this interpreter "
        "is Python {current} ({executable}).\n"
        "Set up a {required}+ virtual environment and install the project:\n"
        "    python{required} -m venv .venv\n"
        "    # activate: 'source .venv/bin/activate' (macOS/Linux) or "
        "'.venv\\Scripts\\activate' (Windows)\n"
        '    pip install -e ".[dev]"\n'
        "APL is intentionally single-runtime; do not add Python <{required} "
        "compatibility shims."
    ).format(
        required=MINIMUM_PYTHON_DISPLAY,
        current=current_version_display(version_info),
        executable=sys.executable,
    )


def enforce(version_info=sys.version_info):
    """Raise ``RuntimeError`` with actionable guidance on an unsupported Python.

    Call this at the start of CLI and helper entry points that would otherwise
    fail with a cryptic error under an older interpreter.
    """
    if not is_supported(version_info):
        raise RuntimeError(unsupported_message(version_info))
