"""Unit tests for ExperimentResult class."""

from __future__ import annotations

import numpy as np

from qsot2.core.results import ExperimentResult, _sanitize


def test_result_verdict_pass():
    result = ExperimentResult(experiment_id="test")
    result.checks = {
        "flat_rest_purity_is_1": "PASS",
        "flat_rest_entropy_is_0": "PASS",
    }
    assert result.verdict == "PASS"
    assert result.total == 2
    assert result.passed == 2
    assert result.failed == 0
    assert result.skipped == 0
    assert result.degraded == 0


def test_result_verdict_fail():
    result = ExperimentResult(experiment_id="test")
    result.checks = {
        "flat_rest_purity_is_1": "PASS",
        "flat_rest_entropy_is_0": "FAIL",
    }
    assert result.verdict == "FAIL"
    assert result.passed == 1
    assert result.failed == 1


def test_result_verdict_degraded():
    result = ExperimentResult(experiment_id="test")
    result.checks = {
        "flat_rest_purity_is_1": "PASS",
        "flat_rest_entropy_is_0": "DEGRADED_PASS",
    }
    assert result.verdict == "DEGRADED_PASS"
    assert result.passed == 1
    assert result.degraded == 1


def test_result_verdict_skipped_optional():
    result = ExperimentResult(experiment_id="test")
    result.checks = {
        "flat_rest_purity_is_1": "PASS",
        "some_optional_check": "SKIPPED",
    }
    assert result.verdict == "DEGRADED_PASS"
    assert result.skipped == 1


def test_set_verdict():
    result = ExperimentResult(experiment_id="test")
    result.set_verdict("DEGRADED_PASS")
    assert result.verdict == "DEGRADED_PASS"


def test_sanitize_numpy():
    data = {
        "int_val": np.int64(42),
        "float_val": np.float64(3.14),
        "bool_val": np.bool_(True),
        "arr_val": np.array([1, 2, 3]),
        "nested": {"nested_arr": np.array([[1.0, 2.0]])},
    }
    sanitized = _sanitize(data)
    assert isinstance(sanitized["int_val"], int)
    assert isinstance(sanitized["float_val"], float)
    assert isinstance(sanitized["bool_val"], bool)
    assert isinstance(sanitized["arr_val"], list)
    assert isinstance(sanitized["nested"]["nested_arr"], list)
    assert sanitized["arr_val"] == [1, 2, 3]
    assert sanitized["nested"]["nested_arr"] == [[1.0, 2.0]]


def test_to_dict_lean_qsot2_schema():
    result = ExperimentResult(experiment_id="test")
    result.checks = {"check1": "PASS"}
    result.observations = {"obs1": np.array([0.5])}
    d = result.to_dict()
    assert d["experiment_id"] == "test"
    assert d["verdict"] == "PASS"
    assert d["summary"]["pass"] == 1
    assert d["checks"] == {"check1": "PASS"}
    assert d["observations"] == {"obs1": [0.5]}
    # Lean QSOT2 schema: new id + minimal claim boundary + no governance blocks.
    assert d["schema_id"] == "qsot2.math_consistency.experiment_result.v1"
    assert d["claim_boundary"]["mathematical_consistency_scope_only"] is True
    for governance_key in ("evidence_classes", "audit_context", "calibration"):
        assert governance_key not in d
