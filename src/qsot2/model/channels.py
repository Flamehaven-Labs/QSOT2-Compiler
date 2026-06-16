"""Physics engine: KrausChannel, BackgroundField, MetricToChannelMap.

V2 physics is pulled from the TOE QGB pipeline:
  BackgroundField -> MetricToChannelMap -> KrausChannel
  p(Riemann) = 1 - exp(-alpha * ||Riemann||_F)

The channel mapping uses a compact Riemann-norm proxy for tidal curvature.
The Riemann data itself is non-derived: some backgrounds use hand-set toy
constants and the curved (de Sitter/AdS5/Godel) cases copy the Ricci matrix
(see each builder's riemann_source and the curvature_provenance manifest).
Ricci curvature is reserved for beta/admissibility classification.
Alpha (sensitivity) remains a free phenomenological calibration parameter,
not a first-principles constant. See qgb.py docstring for sensitivity analysis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np

# Pauli basis
_I = np.eye(2, dtype=complex)
_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
_Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


@dataclass
class KrausChannel:
    """CPTP quantum channel represented as Kraus operators."""

    kraus_ops: List[np.ndarray]
    channel_type: str = "depolarizing"
    p: float = 0.0
    R_norm: float = 0.0

    def apply(self, rho: np.ndarray) -> np.ndarray:
        """E(rho) = sum_i K_i rho K_i^dagger."""
        result = np.zeros_like(rho, dtype=complex)
        for K in self.kraus_ops:
            result += K @ rho @ K.conj().T
        return result

    @property
    def completeness_error(self) -> float:
        """||sum_i K_i^dagger K_i - I||_F (0 for a valid CPTP channel)."""
        D = self.kraus_ops[0].shape[0]
        total = sum(K.conj().T @ K for K in self.kraus_ops)
        return float(np.linalg.norm(total - np.eye(D, dtype=complex), "fro"))

    @property
    def dim(self) -> int:
        return self.kraus_ops[0].shape[0]

    @classmethod
    def identity(cls) -> "KrausChannel":
        """Identity channel (zero noise, flat spacetime)."""
        return cls(kraus_ops=[_I.copy()], channel_type="depolarizing", p=0.0, R_norm=0.0)


def _make_depolarizing_kraus(p: float) -> List[np.ndarray]:
    """Depolarizing channel: E(rho) = (1-p)rho + (p/3)(X rho X + Y rho Y + Z rho Z)."""
    p = float(np.clip(p, 0.0, 1.0))
    coeff = math.sqrt(p / 3.0)
    return [
        math.sqrt(1.0 - p) * _I,
        coeff * _X,
        coeff * _Y,
        coeff * _Z,
    ]


def _make_dephasing_kraus(p: float) -> List[np.ndarray]:
    """Dephasing channel: E(rho) = (1-p)rho + p*Z rho Z."""
    p = float(np.clip(p, 0.0, 1.0))
    return [
        math.sqrt(1.0 - p) * _I,
        math.sqrt(p) * _Z,
    ]


@dataclass
class BackgroundField:
    """Minimal representation of a classical spacetime background."""

    name: str
    G: np.ndarray
    ricci_matrix: np.ndarray
    riemann_matrix: np.ndarray | None = None

    ricci_norm: float = 0.0
    einstein_residual_norm: float = 0.0
    stress_energy_norm: float = 0.0

    cosmological_constant: float | None = None

    is_symbolic_ricci_flat: bool = False
    is_conformal_background: bool = False

    has_ctc: bool = False
    ctc_discriminant: float = 0.0

    gs_anomaly_flag: bool = False
    gs_anomaly_reason: str | None = None

    # Provenance of riemann_matrix construction. "exact_zero_minkowski" is genuine;
    # "toy_placeholder_constants" (hand-set entries) and "copied_from_ricci_proxy"
    # (riemann_matrix = ricci.copy()) mark non-derived toy curvature.
    riemann_source: str | None = None

    numeric_residual_is_physical: bool = False
    D: int = 10

    def __post_init__(self) -> None:
        # Compute numerical norm if not provided
        if self.ricci_norm == 0.0 and self.ricci_matrix is not None:
            self.ricci_norm = float(np.linalg.norm(self.ricci_matrix, "fro"))
        # Sync has_ctc and ctc_discriminant
        if self.ctc_discriminant > 0.0:
            self.has_ctc = True

    @property
    def riemann_norm(self) -> float:
        """Frobenius norm of the Riemann tensor matrix (representing tidal forces)."""
        if self.riemann_matrix is not None:
            return float(np.linalg.norm(self.riemann_matrix, "fro"))
        return self.ricci_norm


class MetricToChannelMap:
    """Maps a BackgroundField to a KrausChannel."""

    def __init__(self, sensitivity: float = 0.1, channel_type: str = "depolarizing"):
        if not (0.0 < sensitivity <= 100.0):
            raise ValueError(f"sensitivity must be in (0, 100], got {sensitivity}")
        if channel_type not in ("depolarizing", "dephasing"):
            raise ValueError("channel_type must be 'depolarizing' or 'dephasing'")
        self.sensitivity = sensitivity
        self.channel_type = channel_type

    def to_channel(self, bg: BackgroundField, channel_type: str | None = None) -> KrausChannel:
        """Convert a BackgroundField to a KrausChannel via the curvature-noise mapping.

        Note: We map Riemann curvature norm (tidal forces) to the channel rather than
        Ricci curvature, ensuring that Ricci-flat vacuums (e.g. Schwarzschild) still
        induce physical decoherence.
        """
        ctype = channel_type or self.channel_type
        R_norm = bg.riemann_norm
        p = 1.0 - math.exp(-self.sensitivity * R_norm)

        if ctype == "depolarizing":
            ops = _make_depolarizing_kraus(p)
        else:
            ops = _make_dephasing_kraus(p)

        return KrausChannel(
            kraus_ops=ops,
            channel_type=ctype,
            p=p,
            R_norm=R_norm,
        )

    def gravitational_decoherence(
        self,
        bg: BackgroundField,
        observer_velocity: float = 0.0,
        channel_type: str | None = None,
    ) -> dict:
        """Compute channel with Lorentz boost applied to the noise parameter."""
        if not (0.0 <= observer_velocity < 1.0):
            raise ValueError(f"observer_velocity must be in [0, 1), got {observer_velocity}")

        ctype = channel_type or self.channel_type
        R_norm = bg.riemann_norm
        p_curv = 1.0 - math.exp(-self.sensitivity * R_norm)

        g00 = float(bg.G[0, 0])
        if g00 < 0:
            gamma_grav = 1.0 / math.sqrt(max(-g00, 1e-12))
        else:
            gamma_grav = 1.0

        if observer_velocity > 0:
            beta = min(observer_velocity, 0.9999)
            gamma_boost = 1.0 / math.sqrt(1.0 - beta**2)
        else:
            gamma_boost = 1.0

        gamma_total = gamma_grav * gamma_boost
        p_eff = 1.0 - (1.0 - p_curv) ** gamma_total
        p_eff = float(np.clip(p_eff, 0.0, 1.0 - 1e-12))

        if ctype == "depolarizing":
            ops = _make_depolarizing_kraus(p_eff)
        else:
            ops = _make_dephasing_kraus(p_eff)

        channel = KrausChannel(
            kraus_ops=ops,
            channel_type=ctype,
            p=p_eff,
            R_norm=R_norm,
        )
        return {
            "channel": channel,
            "p_curvature": p_curv,
            "p_effective": p_eff,
            "R_norm": R_norm,
            "alpha": self.sensitivity,
            "g00": g00,
            "gamma_gravitational": gamma_grav,
            "gamma_boost": gamma_boost,
            "gamma_total": gamma_total,
            "observer_velocity": observer_velocity,
        }


def _build_flat(D: int = 10) -> BackgroundField:
    """Flat Minkowski background: zero Ricci and Riemann tensor."""
    G = np.diag([-1.0] + [1.0] * (D - 1))
    return BackgroundField(
        name="flat",
        riemann_source="exact_zero_minkowski",
        G=G,
        ricci_matrix=np.zeros((D, D)),
        riemann_matrix=np.zeros((D, D)),
        ricci_norm=0.0,
        einstein_residual_norm=0.0,
        stress_energy_norm=0.0,
        cosmological_constant=0.0,
        is_symbolic_ricci_flat=True,
        is_conformal_background=True,
        has_ctc=False,
        gs_anomaly_flag=False,
        D=D,
    )


def _build_schwarzschild(D: int = 10) -> BackgroundField:
    """Schwarzschild background: theoretically Ricci-flat vacuum, but contains non-zero Riemann tidal curvature."""
    G = np.diag([-1.0 / 3.0] + [1.0] * (D - 1))
    ricci = np.zeros((D, D))  # Ricci-flat vacuum solution
    riemann = np.zeros((D, D))
    riemann[0, 0] = 0.001
    riemann[1, 1] = 0.001
    return BackgroundField(
        name="schwarzschild",
        riemann_source="toy_placeholder_constants",
        G=G,
        ricci_matrix=ricci,
        riemann_matrix=riemann,
        ricci_norm=0.0,
        einstein_residual_norm=0.0,
        stress_energy_norm=0.0,
        cosmological_constant=0.0,
        is_symbolic_ricci_flat=True,
        is_conformal_background=True,
        has_ctc=False,
        gs_anomaly_flag=False,
        D=D,
    )


def _build_de_sitter(D: int = 10) -> BackgroundField:
    """de Sitter background: positive cosmological constant, non-zero Ricci and Riemann curvature."""
    G = np.diag([-1.0] + [1.0] * (D - 1))
    ricci = np.eye(D) * 0.5
    return BackgroundField(
        name="de_sitter",
        riemann_source="copied_from_ricci_proxy",
        G=G,
        ricci_matrix=ricci,
        riemann_matrix=ricci.copy(),
        einstein_residual_norm=0.0,
        stress_energy_norm=0.0,
        cosmological_constant=0.5,
        is_symbolic_ricci_flat=False,
        is_conformal_background=False,
        has_ctc=False,
        gs_anomaly_flag=False,
        D=D,
    )


def _build_ads5(D: int = 10) -> BackgroundField:
    """AdS5 background: negative cosmological constant, non-zero Ricci and Riemann curvature."""
    G = np.diag([-1.0] + [1.0] * (D - 1))
    ricci = -np.eye(D) * 0.4
    return BackgroundField(
        name="ads5",
        riemann_source="copied_from_ricci_proxy",
        G=G,
        ricci_matrix=ricci,
        riemann_matrix=ricci.copy(),
        einstein_residual_norm=0.0,
        stress_energy_norm=0.0,
        cosmological_constant=-0.4,
        is_symbolic_ricci_flat=False,
        is_conformal_background=True,
        has_ctc=False,
        gs_anomaly_flag=False,
        D=D,
    )


def _build_eguchi_hanson(D: int = 10) -> BackgroundField:
    """Eguchi-Hanson background: Ricci-flat instanton, non-zero Riemann curvature, contains gravitational anomaly."""
    G = np.diag([-1.0] + [1.0] * (D - 1))
    ricci = np.zeros((D, D))  # Ricci-flat vacuum instanton
    riemann = np.zeros((D, D))
    riemann[0, 1] = riemann[1, 0] = 0.002
    return BackgroundField(
        name="eguchi_hanson",
        riemann_source="toy_placeholder_constants",
        G=G,
        ricci_matrix=ricci,
        riemann_matrix=riemann,
        ricci_norm=0.0,
        einstein_residual_norm=0.0,
        stress_energy_norm=0.0,
        cosmological_constant=0.0,
        is_symbolic_ricci_flat=True,
        is_conformal_background=True,
        has_ctc=False,
        gs_anomaly_flag=True,
        gs_anomaly_reason="topological_anomaly_proxy",
        D=D,
    )


def _build_godel_universe(D: int = 10) -> BackgroundField:
    """Godel universe: rotating dust, non-zero Ricci/Riemann curvature, contains CTCs."""
    G = np.diag([-1.0] + [1.0] * (D - 1))
    ricci = np.eye(D) * 0.3
    return BackgroundField(
        name="godel_universe",
        riemann_source="copied_from_ricci_proxy",
        G=G,
        ricci_matrix=ricci,
        riemann_matrix=ricci.copy(),
        einstein_residual_norm=0.0,
        stress_energy_norm=0.3,
        cosmological_constant=0.0,
        is_symbolic_ricci_flat=False,
        is_conformal_background=False,
        has_ctc=True,
        gs_anomaly_flag=False,
        D=D,
    )


BACKGROUND_BUILDERS = {
    "flat": _build_flat,
    "schwarzschild": _build_schwarzschild,
    "de_sitter": _build_de_sitter,
    "ads5": _build_ads5,
    "eguchi_hanson": _build_eguchi_hanson,
    "godel_universe": _build_godel_universe,
}
