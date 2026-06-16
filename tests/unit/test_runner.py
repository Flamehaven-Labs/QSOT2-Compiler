"""Unit tests for ExperimentRunner and phase execution (math-verification phases only)."""

from __future__ import annotations

from qsot2.core.runner import ExperimentRunner


def test_runner_all_enabled(sample_config):
    # Enable all (math) phases to verify runner integration end-to-end.
    for phase in sample_config.phases:
        phase.enabled = True

    runner = ExperimentRunner(sample_config)
    res = runner.run()

    assert res is not None
    assert "flat_rest_purity_is_1" in res.checks
    assert "schwarzschild_purity_decays" in res.checks
    assert "boost_accelerates_purity_decay" in res.checks
    assert "kd_basis_optimization_ran" in res.checks
    assert "memory_kernel_selftest_detects_injected_backflow" in res.checks

    # Governance / engineering phases are gone: no rust or scientific-audit checks.
    assert not any(k.startswith("rust_") for k in res.checks)
    assert not any(k.startswith("scientific_audit_") for k in res.checks)
    assert "dqe_covenant_validated" not in res.checks

    # Retained gate-physics observations.
    schwarz_verify = res.observations["schwarzschild_verify"]
    assert schwarz_verify["physics"]["ricci_norm"] == 0.0
    assert schwarz_verify["physics"]["riemann_norm"] > 0.0

    desitter_verify = res.observations["desitter_verify"]
    assert desitter_verify["physics"]["brst_proxy_ok"] is False

    godel_verify = res.observations["godel_verify"]
    assert godel_verify["physics"]["ctc_status"] == "DETECTED"


def test_runner_skips(sample_config):
    # Disable all phases -> all required checks SKIPPED -> verdict FAIL.
    for phase in sample_config.phases:
        phase.enabled = False

    runner = ExperimentRunner(sample_config)
    res = runner.run()

    assert all(status == "SKIPPED" for status in res.checks.values())
    assert res.verdict == "FAIL"


def test_runner_skips_optional_only(sample_config):
    # Keep required phases enabled, disable optional Phase 4 (KD).
    for phase in sample_config.phases:
        phase.enabled = phase.id != "phase4_kd_governance"

    runner = ExperimentRunner(sample_config)
    res = runner.run()

    assert res.checks["kd_basis_optimization_ran"] == "SKIPPED"
    assert res.verdict == "DEGRADED_PASS"
