"""Unit tests for background verification, beta residuals, and classification."""

from __future__ import annotations

import numpy as np
import pytest

from qsot2.model import BackgroundField, BetaResidualVerifier, run_background_verify
from qsot2.model.classification import classify_background, compute_admissibility


def test_run_background_verify():
    flat = run_background_verify("flat")[0]
    assert flat["gate"] == "PASS"
    assert flat["physics"]["ricci_norm"] == 0.0

    sch = run_background_verify("schwarzschild")[0]
    assert sch["gate"] == "PASS"

    ds = run_background_verify("de_sitter")[0]
    assert ds["gate"] == "FAIL"

    ads = run_background_verify("ads5")[0]
    assert ads["gate"] == "PASS"

    eh = run_background_verify("eguchi_hanson")[0]
    assert eh["gate"] == "FAIL"
    assert eh["physics"]["gs_anomaly_flag"] is True

    godel = run_background_verify("godel_universe")[0]
    assert godel["gate"] == "FAIL"
    assert godel["physics"]["ctc_status"] == "DETECTED"

    with pytest.raises(ValueError):
        run_background_verify("invalid_preset")


def test_run_background_verify_provenance():
    # R1.x provenance surfaced in the verify physics block.
    ds = run_background_verify("de_sitter")[0]
    assert ds["policy_reason_code"] == "nonzero_beta_residual"
    assert ds["physics"]["riemann_source"] == "copied_from_ricci_proxy"
    assert ds["physics"]["riemann_is_toy"] is True

    eh = run_background_verify("eguchi_hanson")[0]
    assert eh["physics"]["gs_anomaly_reason"] == "topological_anomaly_proxy"


def test_beta_residual_verifier(flat_background):
    verifier = BetaResidualVerifier()
    flat_background.is_symbolic_ricci_flat = True
    flat_background.is_conformal_background = True
    res_flat = verifier.verify(flat_background)
    assert res_flat.all_pass
    assert res_flat.status == "pass"

    sch_bg = BackgroundField(
        name="schwarzschild",
        G=np.diag([-1.0, 1.0]),
        ricci_matrix=np.eye(2) * 0.1,
        is_symbolic_ricci_flat=False,
    )
    res_sch = verifier.verify(sch_bg)
    assert not res_sch.all_pass
    assert res_sch.status == "fail"

    eh_bg = BackgroundField(
        name="eguchi_hanson",
        G=np.diag([-1.0, 1.0]),
        ricci_matrix=np.eye(2) * 0.1,
        gs_anomaly_flag=True,
        gs_anomaly_reason="topological_anomaly_proxy",
    )
    res_eh = verifier.verify(eh_bg)
    assert res_eh.gs_anomaly_flag is True


def test_classification_coverage():
    class MockBgWithMatrix:
        ricci_matrix = np.eye(2) * 0.5
        cosmological_constant = 0.5
        is_conformal_background = False
        has_ctc = False
        gs_anomaly_flag = False
        D = 10
        G = np.diag([-1.0, 1.0])

    cls1 = classify_background(MockBgWithMatrix())
    assert cls1["ricci_norm"] > 0.0

    class MockBgEmpty:
        D = 4
        G = np.diag([-1.0, 1.0])

    cls2 = classify_background(MockBgEmpty())
    assert cls2["ricci_norm"] == 0.0

    class MockNonVacuumBg:
        ricci_norm = 1.5
        D = 10
        G = np.diag([-1.0, 1.0])
        is_conformal_background = False
        has_ctc = False
        gs_anomaly_flag = False

    adm = compute_admissibility(MockNonVacuumBg())
    assert adm["admissibility"] == 0.2
    assert adm["reason"] == "nonzero_beta_residual"
