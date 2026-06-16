"""Phase executors for all 8 experiment phases."""

from __future__ import annotations

from qsot2.core.phases.phase0 import run_phase0, skip_phase0
from qsot2.core.phases.phase1 import run_phase1, skip_phase1
from qsot2.core.phases.phase2 import run_phase2, skip_phase2
from qsot2.core.phases.phase3 import run_phase3, skip_phase3
from qsot2.core.phases.phase4 import run_phase4, skip_phase4
from qsot2.core.phases.phase5 import run_phase5, skip_phase5

__all__ = [
    "run_phase0",
    "skip_phase0",
    "run_phase1",
    "skip_phase1",
    "run_phase2",
    "skip_phase2",
    "run_phase3",
    "skip_phase3",
    "run_phase4",
    "skip_phase4",
    "run_phase5",
    "skip_phase5",
]
