#!/usr/bin/env python
"""Wrapper entrypoint script to execute the QSOT2 experiment runner."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to python path to run without installing
src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from qsot2.cli.run_experiment import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
