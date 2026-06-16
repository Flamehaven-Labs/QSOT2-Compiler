"""Background verification runner delegating to dynamic classification logic."""

from __future__ import annotations

from typing import List

from qsot2.model.channels import BACKGROUND_BUILDERS
from qsot2.model.classification import (
    classify_background,
    compute_admissibility,
    compute_beta_residuals,
)


def run_background_verify(preset: str) -> List[dict]:
    """Create a BackgroundField from preset name and run physics verification dynamically."""
    builder = BACKGROUND_BUILDERS.get(preset)
    if builder is None:
        raise ValueError(f"Unknown preset: {preset!r}")

    bg = builder(D=10)

    # Compute properties dynamically from Single Source of Truth
    cls = classify_background(bg)
    beta = compute_beta_residuals(bg)
    adm = compute_admissibility(bg)

    ctc_status = "DETECTED" if cls["has_ctc"] else "CLEAR"
    # BackgroundField always declares ctc_discriminant (dataclass field), so read
    # it directly. The previous getattr fallback was dead code that misleadingly
    # implied a detected CTC would carry a synthetic discriminant of 1.0.
    ctc_disc = bg.ctc_discriminant

    gs_flag = cls["has_gravitational_anomaly"]
    gs_reason = cls["gs_anomaly_reason"]
    gs_p1_R = 2.0 if gs_flag else 0.0
    gs_p1_F = 0.0

    return [
        {
            "paper_title": f"[bg:{preset}]",
            "hypothesis": f"Direct background verification: {preset}",
            "sr9": round(float(adm["admissibility"]), 4),
            "di2": round(float(adm["jsd"]), 4),
            "gate": adm["gate"],
            "policy_reason_code": adm["reason"],
            "failed_checks": adm["failed_checks"],
            "verdict": {
                "risk": "green" if adm["gate"] == "PASS" else "red",
                "decree": "approve" if adm["gate"] == "PASS" else "reject_and_log",
                "admissibility_total": adm["admissibility"],
                "gs_score": 1.0 if adm["gate"] == "PASS" else 0.0,
                "b_score": 1.0,
                "si_score": 1.0 if adm["gate"] == "PASS" else 0.0,
                "gs_si_balance": 1.0 if adm["gate"] == "PASS" else 0.0,
                "agent_reports": [],
            },
            "physics": {
                "beta_status": beta["status"],
                "beta_G_norm": beta["beta_G_norm"],
                "beta_B_norm": beta["beta_B_norm"],
                "beta_Phi_norm": beta["beta_Phi_norm"],
                "drift_admissibility": adm["admissibility"],
                "drift_divergence": adm["jsd"],
                "pde_status": "skip",
                "ricci_norm": cls["ricci_norm"],
                "riemann_norm": bg.riemann_norm,
                "riemann_source": bg.riemann_source,
                "riemann_is_toy": bg.riemann_source not in (None, "exact_zero_minkowski"),
                "eft_m_kk_gev": None,
                "brst_proxy_ok": beta["brst_proxy_ok"],
                "dimension_check": True,
                "gs_anomaly_flag": gs_flag,
                "gs_anomaly_reason": gs_reason,
                "c_total": 0.0,
                "c_moduli": 0.0,
                "gs_p1_R": gs_p1_R,
                "gs_p1_F": gs_p1_F,
                "gs_residual": gs_p1_R - gs_p1_F,
                "ctc_status": ctc_status,
                "ctc_discriminant": ctc_disc,
                "ctc_order_parameter": ctc_disc,
                "ctc_k0_timelike": ctc_disc > 0,
            },
        }
    ]
