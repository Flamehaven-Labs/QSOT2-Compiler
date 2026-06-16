"""Pytest configuration and fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from qsot2.core.config import ExperimentConfig, OutputConfig, PhaseConfig
from qsot2.model import BackgroundField


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def sample_config():
    return ExperimentConfig(
        experiment_id="test-exp-01",
        version="0.1.0",
        description="Test experiment",
        backgrounds=["flat", "schwarzschild"],
        sensitivity=0.1,
        boost_beta=0.5,
        steps=2,
        phases=[
            PhaseConfig(id="phase0_temporal_axioms", enabled=True),
            PhaseConfig(id="phase1_flat_baselines", enabled=True),
            PhaseConfig(id="phase2_curvature_noise", enabled=True),
            PhaseConfig(id="phase3_boosts", enabled=False),
            PhaseConfig(id="phase4_kd_governance", enabled=False),
            PhaseConfig(id="phase5_ttm_accessibility", enabled=False),
        ],
        output=OutputConfig(formats=["json", "md"], dir="reports"),
    )


@pytest.fixture
def flat_background():
    D = 10
    G = np.diag([-1.0] + [1.0] * (D - 1))
    return BackgroundField(
        name="flat",
        G=G,
        ricci_matrix=np.zeros((D, D)),
        ctc_discriminant=0.0,
        D=D,
    )
