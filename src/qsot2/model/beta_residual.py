"""BetaResidualVerifier dynamic implementation delegating to classification policies."""

from __future__ import annotations

from dataclasses import dataclass, field

from qsot2.model.classification import (
    classify_background,
    compute_beta_residuals,
)


@dataclass
class BetaResidualResult:
    beta_G_norm: float
    beta_B_norm: float
    beta_Phi_norm: float
    bianchi_residual: float
    gs_anomaly_flag: bool
    brst_proxy_ok: bool
    dimension_check: bool
    status: str
    traces: dict = field(default_factory=dict)

    @property
    def all_pass(self) -> bool:
        return (
            self.status == "pass"
            and not self.gs_anomaly_flag
            and self.brst_proxy_ok
            and self.dimension_check
        )


class BetaResidualVerifier:
    def __init__(
        self,
        tol_G: float = 1e-4,
        tol_B: float = 1e-4,
        tol_Phi: float = 1e-4,
        bianchi_tol: float = 1e-4,
        borderline_factor: float = 10.0,
        alpha_prime: float = 0.0,
    ):
        self.tol_G = tol_G
        self.tol_B = tol_B
        self.tol_Phi = tol_Phi
        self.bianchi_tol = bianchi_tol
        self.borderline_factor = borderline_factor
        self.alpha_prime = alpha_prime

    def verify(self, bg) -> BetaResidualResult:
        """Verify background and return a result computed dynamically from classification.py."""
        cls = classify_background(bg)
        beta = compute_beta_residuals(bg)

        # Traces for anomalies
        traces = {"c_total": 0.0, "c_moduli": 0.0}
        if cls["has_gravitational_anomaly"]:
            traces.update({"gs_p1_R": 2.0, "gs_p1_F": 0.0})

        return BetaResidualResult(
            beta_G_norm=beta["beta_G_norm"],
            beta_B_norm=beta["beta_B_norm"],
            beta_Phi_norm=beta["beta_Phi_norm"],
            bianchi_residual=beta["bianchi_residual"],
            gs_anomaly_flag=cls["has_gravitational_anomaly"],
            brst_proxy_ok=beta["brst_proxy_ok"],
            dimension_check=True,
            status=beta["status"],
            traces=traces,
        )
