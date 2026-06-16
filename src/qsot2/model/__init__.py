"""QSOT2 model layer: quantum state/channels, curvature backgrounds, the KD
optimizer, the TTM-inspired memory proxy, and gate-physics classification.

This layer is governance-free: it must not import audit / evidence / calibration
/ accessibility concerns. The harness composes it; the model never depends on the
harness or on governance.
"""

from __future__ import annotations

from qsot2.model.background import run_background_verify
from qsot2.model.beta_residual import BetaResidualVerifier
from qsot2.model.channels import (
    BACKGROUND_BUILDERS,
    BackgroundField,
    KrausChannel,
    MetricToChannelMap,
)
from qsot2.model.memory_kernel import compute_memory_kernel
from qsot2.model.optimizer import TORCH_AVAILABLE, run_kd_optimization
from qsot2.model.quantum import QuantumCircuit, QuantumState

__all__ = [
    "BackgroundField",
    "KrausChannel",
    "MetricToChannelMap",
    "BACKGROUND_BUILDERS",
    "QuantumCircuit",
    "QuantumState",
    "run_background_verify",
    "BetaResidualVerifier",
    "run_kd_optimization",
    "TORCH_AVAILABLE",
    "compute_memory_kernel",
]
