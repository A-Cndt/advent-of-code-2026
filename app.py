"""Entry point of the Advent of Code solver.

This file contains no business logic: it checks the environment, prepares the
project layout and then delegates to the modules of the ``src`` package:

* ``src.aoc_core``: files, network access and execution of the solutions;
* ``src.aoc_gui``: PySide6 graphical interface.

Usage ::

    pip install -r requirements.txt
    python app.py
"""

# =============================================================================
# 1. IMPORTS
# =============================================================================
from __future__ import annotations

import sys

# =============================================================================
# 2. CONFIGURATION
# =============================================================================
MIN_PYTHON = (3, 9)  # minimum supported Python version


# =============================================================================
# 3. ENVIRONMENT CHECKS
# =============================================================================
def check_python_version() -> None:
    """Stop the program if the Python version is too old.

    :raises SystemExit: if Python is older than ``MIN_PYTHON``
    """
    if sys.version_info < MIN_PYTHON:
        required = ".".join(map(str, MIN_PYTHON))
        sys.exit(f"Python {required} or newer is required.")


# =============================================================================
# 4. MAIN FUNCTION
# =============================================================================
def main() -> int:
    """Prepare the project, then start the graphical interface.

    :return: exit code of the program (0 = success)
    :rtype: int
    """
    check_python_version()

    # The modules are imported here (not at the top of the file) so that a
    # clear message can be displayed when a dependency is missing.
    try:
        from src import aoc_core
        from src.aoc_gui import run
    except ModuleNotFoundError as exc:
        if (exc.name or "").split(".")[0] == "PySide6":
            print(
                "PySide6 is not installed.\n"
                "Install the dependencies with: "
                "pip install -r requirements.txt",
                file=sys.stderr,
            )
            return 1
        raise

    aoc_core.ensure_project_layout()
    return run()


# =============================================================================
# 5. ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    sys.exit(main())
