"""Unit tests for the TTM-inspired memory proxy."""

from __future__ import annotations

import numpy as np
import pytest

from qsot2.model import KrausChannel
from qsot2.model.memory_kernel import (
    compute_memory_kernel,
    dynamic_ttm_threshold,
    trace_dist,
)


def test_dynamic_ttm_threshold():
    val_0 = dynamic_ttm_threshold(0.0)
    val_1 = dynamic_ttm_threshold(1.0)
    assert val_0 == 1e-6
    assert val_1 < val_0


def test_trace_dist():
    A = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    B = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
    assert trace_dist(A, B) == pytest.approx(1.0)
    assert trace_dist(A, A) == pytest.approx(0.0)


def test_compute_memory_kernel():
    rhos = [
        np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex),
        np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex),
        np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex),  # coherence backflow
    ]
    ch = KrausChannel.identity()
    res = compute_memory_kernel(rhos, [ch, ch], ricci_norm=0.0)
    assert res["nm_measure"] > 0.0
    assert res["depth"] > 0
    assert len(res["profile"]) == 2
    # Threshold provenance is surfaced.
    assert res["threshold_curvature_engaged"] is False
    assert "threshold_formula" in res
