"""Kirkwood-Dirac quasi-probability optimizer (PyTorch).

Searches measurement basis angles (theta, phi) for the most KD-negative
real part of a state. KD negativity in the searched basis is a standard
property of single-qubit states -- not a contextuality witness and not a
curvature claim (see `raw_kd_negative_in_optimized_basis` in the output).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_PATIENCE = 20

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:

    class QuantumOptimizer(torch.nn.Module):
        """Differentiable Bloch-angle search for KD negativity.

        Learns basis angles (theta_a, phi_a, theta_b, phi_b) via Adam
        to minimize Re(Tr(P_b P_a rho)). The result is a raw model-relative
        quantity, not evidence of non-classicality.
        """

        def __init__(self, rho_np: np.ndarray):
            super().__init__()
            self.rho = torch.tensor(rho_np, dtype=torch.complex128)
            torch.manual_seed(42)
            self.theta_a = torch.nn.Parameter((torch.rand(1) * np.pi).to(dtype=torch.float64))
            self.phi_a = torch.nn.Parameter((torch.rand(1) * 2 * np.pi).to(dtype=torch.float64))
            self.theta_b = torch.nn.Parameter((torch.rand(1) * np.pi).to(dtype=torch.float64))
            self.phi_b = torch.nn.Parameter((torch.rand(1) * 2 * np.pi).to(dtype=torch.float64))

        def get_projector(self, theta, phi):
            c = torch.cos(theta / 2)
            s = torch.sin(theta / 2)
            phase = torch.exp(1j * phi)
            psi = torch.stack([c, phase * s]).squeeze()
            if psi.dim() == 0:
                psi = psi.unsqueeze(0)
            return torch.outer(psi, psi.conj())

        def forward(self):
            Pa = self.get_projector(self.theta_a, self.phi_a)
            Pb = self.get_projector(self.theta_b, self.phi_b)
            return torch.trace(Pb @ Pa @ self.rho).real


def run_kd_optimization(
    state_path: str,
    out_path: str,
    *,
    steps: int = 200,
    lr: float = 0.1,
    patience: int = DEFAULT_PATIENCE,
    min_delta: float = 1e-6,
) -> Optional[Dict[str, Any]]:
    """Gradient-based Kirkwood-Dirac basis optimization (PyTorch Adam) with early stopping.

    The reported value is always the best observed objective (not the last-step
    value); best/last are recorded separately so non-converged runs are auditable.
    """
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not found -- KD optimization skipped.")
        Path(out_path).write_text(
            json.dumps({"kd_value": 0.0, "error": "torch_missing"}, indent=2)
        )
        return None

    try:
        with np.load(state_path) as data:
            keys = sorted(k for k in data.keys() if k.startswith("rho_"))
            if not keys:
                raise ValueError(f"No rho states in {state_path}")
            rho = data[keys[-1]]
    except (FileNotFoundError, KeyError, OSError, ValueError) as e:
        logger.error("Failed to load state: %s", e)
        Path(out_path).write_text(json.dumps({"kd_value": 0.0, "error": str(e)}, indent=2))
        return None

    model = QuantumOptimizer(rho)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    best_value = float("inf")
    best_step = 0
    best_state = None
    no_improve = 0
    final_step = 0

    for i in range(steps):
        opt.zero_grad()
        val = model()
        current = val.item()
        # Snapshot the best objective together with the parameters that produced
        # it, captured BEFORE stepping so best_state corresponds to best_value.
        if current < best_value - min_delta:
            best_value = current
            best_step = i + 1
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        val.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        opt.step()

        final_step = i + 1
        if no_improve >= patience:
            break

    # Objective at the last visited parameters (P_final, after the final step).
    last_value = model().item()
    converged = no_improve >= patience

    # Fold the final-step parameters into best tracking: a still-improving
    # (non-converged) run reaches its best at the very last step, which the
    # in-loop pre-step evaluation does not capture.
    if best_state is None or last_value < best_value:
        best_value = last_value
        best_step = final_step
        best_state = {k: v.clone() for k, v in model.state_dict().items()}

    # Always report the best observed objective, regardless of convergence: load the
    # best parameters so kd_value AND the basis angles correspond to it.
    model.load_state_dict(best_state)
    reported_value = model().item()

    result = {
        "kd_value": reported_value,
        # Raw, self-disclaiming flag: the optimizer found a non-trivially negative
        # KD real part in the basis it searched. This is a standard property of
        # single-qubit states, NOT a curvature signal or a contextuality witness.
        # Replaces the deprecated `is_negative` / `contextuality_proxy` fields.
        "raw_kd_negative_in_optimized_basis": reported_value < -1e-6,
        "convergence": {
            "converged": converged,
            "final_step": final_step,
            "total_steps": steps,
            "best_step": best_step,
            "best_value": best_value,
            "last_value": last_value,
        },
        "angles": {
            "basis_a": {
                "theta": float(model.theta_a.item()),
                "phi": float(model.phi_a.item()),
            },
            "basis_b": {
                "theta": float(model.theta_b.item()),
                "phi": float(model.phi_b.item()),
            },
        },
        "target_state_index": keys[-1],
    }

    Path(out_path).write_text(json.dumps(result, indent=2))
    return result
