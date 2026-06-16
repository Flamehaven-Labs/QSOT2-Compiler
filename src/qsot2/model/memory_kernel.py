"""Transfer Tensor Method (TTM) for non-Markovianity quantification.

Ported from Flamehaven-TOE.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

_ALPHA_DEFAULT: float = 0.5
_EPSILON_BASE: float = 1e-6


def dynamic_ttm_threshold(ricci_norm: float, alpha: float = _ALPHA_DEFAULT) -> float:
    """Compute dynamic TTM threshold: epsilon_eff = epsilon_base * exp(-alpha * |R|)."""
    import math

    return _EPSILON_BASE * math.exp(-alpha * abs(ricci_norm))


def trace_dist(A: np.ndarray, B: np.ndarray) -> float:
    """Compute Trace Distance: 0.5 * sum(|eigenvalues(A - B)|)."""
    diff = A - B
    diff = (diff + diff.conj().T) / 2.0  # enforce Hermitian for stability
    vals = np.linalg.eigvalsh(diff)
    return 0.5 * float(np.sum(np.abs(vals)))


def compute_memory_kernel(
    rhos: List[np.ndarray],
    channels: List,
    ricci_norm: float = 0.0,
    alpha: float = _ALPHA_DEFAULT,
) -> Dict[str, Any]:
    """Compute Non-Markovianity via TTM: deviation from Markovian prediction.

    The detection threshold is reported with full provenance: the formula, the
    base epsilon, the alpha, the ricci_norm actually fed in, and whether the
    curvature scaling was engaged (ricci_norm != 0). With ricci_norm == 0 the
    formula reduces to the flat reference epsilon_base.
    """
    deviations = []
    accumulated_nm = 0.0
    steps = min(len(rhos) - 1, len(channels))

    for t in range(steps):
        rho_curr = rhos[t]
        rho_real_next = rhos[t + 1]
        rho_pred_next = channels[t].apply(rho_curr)
        dev = trace_dist(rho_real_next, rho_pred_next)
        deviations.append(dev)
        accumulated_nm += dev

    threshold = dynamic_ttm_threshold(ricci_norm=ricci_norm, alpha=alpha)
    depth = 0
    current_streak = 0
    for d in deviations:
        if d > threshold:
            current_streak += 1
            depth = max(depth, current_streak)
        else:
            current_streak = 0

    return {
        "nm_measure": accumulated_nm,
        "depth": depth,
        "profile": deviations,
        "threshold_used": threshold,
        "threshold_formula": "epsilon_eff = epsilon_base * exp(-alpha * |ricci_norm|)",
        "threshold_epsilon_base": _EPSILON_BASE,
        "threshold_alpha": alpha,
        "threshold_ricci_norm": float(ricci_norm),
        "threshold_curvature_engaged": ricci_norm != 0.0,
    }
