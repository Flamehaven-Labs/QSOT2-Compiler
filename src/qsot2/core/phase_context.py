"""Context and state classes shared between experiment phases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

    from qsot2.core.config import ExperimentConfig
    from qsot2.core.results import ExperimentResult


@dataclass
class RunnerState:
    """Shared mutable state passed between execution phases."""

    flat_final_rho: np.ndarray | None = None
    desitter_final_rho: np.ndarray | None = None


@dataclass
class PhaseContext:
    """Execution context containing configuration, results, and shared state."""

    config: ExperimentConfig
    result: ExperimentResult
    state: RunnerState
