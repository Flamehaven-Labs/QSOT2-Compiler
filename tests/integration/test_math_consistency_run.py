"""Integration test: a full QSOT2 reference run over the shipped config.

Asserts the lean-schema contract and (when torch is available) numeric parity with
the QSOT-Harness r1 math engine. Governance surfaces must be absent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from qsot2.core.config import ExperimentConfig
from qsot2.core.runner import ExperimentRunner
from qsot2.model import TORCH_AVAILABLE

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "experiment.yaml"


@pytest.fixture(scope="module")
def run_result():
    config = ExperimentConfig.from_yaml(CONFIG_PATH)
    return ExperimentRunner(config).run()


def test_lean_schema_contract(run_result):
    d = run_result.to_dict()
    assert d["schema_id"] == "qsot2.math_consistency.experiment_result.v1"
    assert d["claim_boundary"] == {
        "external_physical_validation_provided": False,
        "first_principles_derivation_provided": False,
        "mathematical_consistency_scope_only": True,
        "phenomenological_model": True,
    }
    for governance_key in ("evidence_classes", "audit_context", "calibration"):
        assert governance_key not in d
    assert "accessibility_scores" not in d["observations"]
    assert not any(k.startswith("rust_") for k in d["checks"])
    assert not any(k.startswith("scientific_audit_") for k in d["checks"])


def test_verdict_and_check_total(run_result):
    assert run_result.verdict == "DEGRADED_PASS"
    assert run_result.total == 35


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="KD numerics require torch")
def test_numeric_parity_with_harness_r1(run_result):
    o = run_result.observations
    assert o["kd_flat"]["kd_value"] == pytest.approx(-0.1234429933, abs=1e-6)
    assert o["kd_desitter"]["kd_value"] == pytest.approx(-0.0004734070, abs=1e-5)
    assert o["kd_delta"]["value"] == pytest.approx(0.1229695863, abs=1e-5)
    assert o["memory_kernel"]["nm_measure"] == pytest.approx(1.41e-4, abs=1e-5)
    assert o["memory_kernel_model_trajectory"]["nm_measure"] == 0.0
    # KD reported value is the optimizer best objective (R0.1 semantics).
    assert o["kd_flat"]["kd_value"] == pytest.approx(o["kd_flat"]["convergence"]["best_value"])


def test_background_purity_parity(run_result):
    o = run_result.observations
    assert o["schwarz_purity"] == pytest.approx(0.9994346, abs=1e-5)
    assert o["desitter_purity"] == pytest.approx(0.6360681, abs=1e-5)
    assert o["ads_purity"] == pytest.approx(0.6776356, abs=1e-5)
    assert o["eguchi_purity"] == pytest.approx(0.9988699, abs=1e-5)


def test_axiom_deviations_machine_epsilon(run_result):
    o = run_result.observations
    assert o["linearity_max_deviation"] < 1e-9
    assert o["cptp_completeness_max_deviation"] < 1e-9
    assert o["trace_preservation_max_deviation"] < 1e-9
