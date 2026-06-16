"""Single Source of Truth for physics background classification and gate verification policies."""

from __future__ import annotations

import math

import numpy as np

# Physical constants and tolerances
RICCI_EPS = 1e-9
EINSTEIN_EPS = 1e-9
STRESS_EPS = 1e-9
BETA_RICCI_SCALE = 0.316227766  # Dimension scale 1 / sqrt(10) for normalized Ricci projection
BETA_EPS = 1e-9


def classify_background(bg) -> dict:
    """Classify background based on explicit physical attributes."""
    is_symbolic = getattr(bg, "is_symbolic_ricci_flat", False)

    # Compute numerical ricci_norm if not explicitly present
    if hasattr(bg, "ricci_norm"):
        ricci_norm = bg.ricci_norm
    elif hasattr(bg, "ricci_matrix") and bg.ricci_matrix is not None:
        ricci_norm = float(np.linalg.norm(bg.ricci_matrix, "fro"))
    else:
        ricci_norm = 0.0

    is_ricci_flat = is_symbolic or ricci_norm <= RICCI_EPS

    cosmological_constant = getattr(bg, "cosmological_constant", None)
    einstein_residual_norm = getattr(bg, "einstein_residual_norm", 0.0)
    stress_energy_norm = getattr(bg, "stress_energy_norm", 0.0)

    is_einstein_space = cosmological_constant is not None and einstein_residual_norm <= EINSTEIN_EPS

    is_vacuum_like = is_ricci_flat or (is_einstein_space and stress_energy_norm <= STRESS_EPS)

    has_ctc = getattr(bg, "has_ctc", False)
    if not has_ctc:
        ctc_disc = getattr(bg, "ctc_discriminant", 0.0)
        has_ctc = ctc_disc > 0.0

    has_anomaly = getattr(bg, "gs_anomaly_flag", False)

    return {
        "is_ricci_flat": is_ricci_flat,
        "is_einstein_space": is_einstein_space,
        "is_vacuum_like": is_vacuum_like,
        "is_conformal_background": getattr(bg, "is_conformal_background", False),
        "has_ctc": has_ctc,
        "has_gravitational_anomaly": has_anomaly,
        "gs_anomaly_reason": getattr(bg, "gs_anomaly_reason", None),
        "ricci_norm": ricci_norm,
        "D": getattr(bg, "D", 10),
    }


def compute_beta_residuals(bg) -> dict:
    """Compute beta function residuals dynamically based on background classification.

    Policy rule table (a project classification, NOT a physical observable):

        vacuum-like AND conformal AND anomaly-free  -> beta_G = 0, brst_ok = True,  status = pass
        otherwise                                   -> beta_G = scale * ||Ricci||,  status = fail

    The de Sitter vs AdS5 asymmetry is driven entirely by ``is_conformal_background``:
    AdS5 is tagged conformal (AdS/CFT conformal-boundary admissibility) and is
    Einstein-vacuum-like, so its beta residual collapses to 0 and it PASSES; de Sitter
    is tagged non-conformal, so its nonzero Ricci projects to a nonzero beta drift and it
    FAILS. This encodes a project admissibility policy, not a statement about the physical
    admissibility of de Sitter space.
    """
    cls = classify_background(bg)

    if cls["is_vacuum_like"] and cls["is_conformal_background"]:
        beta_G_raw = 0.0
    else:
        D = cls.get("D", 10)
        scale = 1.0 / math.sqrt(D) if D > 0 else BETA_RICCI_SCALE
        beta_G_raw = scale * cls["ricci_norm"]

    beta_pass = beta_G_raw <= BETA_EPS and not cls["has_gravitational_anomaly"]

    return {
        "beta_G_norm_raw": beta_G_raw,
        "beta_G_norm": round(beta_G_raw, 3),
        "beta_Phi_norm_raw": beta_G_raw,
        "beta_Phi_norm": round(beta_G_raw, 3),
        "beta_B_norm": 0.0,
        "bianchi_residual_raw": beta_G_raw,
        "bianchi_residual": round(beta_G_raw, 3),
        "brst_proxy_ok": cls["is_vacuum_like"]
        and cls["is_conformal_background"]
        and not cls["has_gravitational_anomaly"],
        "status": "pass" if beta_pass else "fail",
    }


def compute_admissibility(bg) -> dict:
    """Compute admissibility policy scores and failed checks."""
    cls = classify_background(bg)
    beta = compute_beta_residuals(bg)

    failed_checks = []

    if cls["has_ctc"]:
        failed_checks.append("closed_timelike_curves")

    if cls["has_gravitational_anomaly"]:
        failed_checks.append("gravitational_anomaly")

    if beta["beta_G_norm_raw"] > BETA_EPS:
        failed_checks.append("nonzero_beta_residual")

    if not failed_checks:
        score = 1.0
        reason = "all_required_checks_passed"
    elif "closed_timelike_curves" in failed_checks:
        score = 0.0
        reason = "ctc_failure"
    elif "gravitational_anomaly" in failed_checks:
        score = 0.1
        reason = "anomaly_failure"
    else:
        score = 0.2
        reason = "nonzero_beta_residual"

    return {
        "admissibility": score,
        "reason": reason,
        "failed_checks": failed_checks,
        "jsd": round(1.0 - score, 4),
        "gate": "PASS" if score == 1.0 else "FAIL",
    }
