"""Unit tests for the KD optimizer module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from qsot2.model.optimizer import TORCH_AVAILABLE, run_kd_optimization


def test_kd_optimization():
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        state_path = temp_dir / "state.npz"
        out_path = temp_dir / "opt.json"

        rho = np.eye(2, dtype=complex) / 2.0
        np.savez(state_path, rho_0=rho)

        res = run_kd_optimization(str(state_path), str(out_path), steps=5)

        if TORCH_AVAILABLE:
            assert res is not None
            assert "kd_value" in res
            assert "raw_kd_negative_in_optimized_basis" in res
            # Deprecated, misleading fields must not reappear.
            assert "is_negative" not in res
            assert "contextuality_proxy" not in res
            # Best-state semantics: reported value is the best observed objective.
            conv = res["convergence"]
            assert "best_value" in conv and "last_value" in conv
            assert abs(res["kd_value"] - conv["best_value"]) < 1e-12
            assert out_path.exists()
        else:
            assert res is None
            assert out_path.exists()


def test_kd_missing_state():
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        state_path = temp_dir / "nonexistent.npz"
        out_path = temp_dir / "opt.json"

        res = run_kd_optimization(str(state_path), str(out_path), steps=5)
        assert res is None
        assert out_path.exists()
