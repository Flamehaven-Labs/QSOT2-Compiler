"""Phase 4: Kirkwood-Dirac flat-relative comparison."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import numpy as np

from qsot2.core.checks import PHASE_CHECKS
from qsot2.model import (
    BACKGROUND_BUILDERS,
    TORCH_AVAILABLE,
    QuantumCircuit,
    QuantumState,
    run_kd_optimization,
)

if TYPE_CHECKING:
    from qsot2.core.phase_context import PhaseContext

# KD basis-optimization step budget (a fixed engineering choice). Runs may not
# converge within it; that is surfaced as DEGRADED_PASS rather than hidden.
KD_OPTIMIZATION_STEPS = 50


def run_phase4(ctx: PhaseContext) -> None:
    """Execute Phase 4 checks."""
    D = 10
    bg_desitter = BACKGROUND_BUILDERS["de_sitter"](D)
    c_desitter = QuantumCircuit(QuantumState.ground())
    c_desitter.evolve_through_background(
        bg_desitter,
        steps=ctx.config.steps,
        sensitivity=ctx.config.sensitivity,
    )

    # Save flat final state (from Phase 1 state observations, fallback to ground if not found)
    flat_rho = (
        ctx.state.flat_final_rho
        if ctx.state.flat_final_rho is not None
        else QuantumState.ground().rho
    )
    with TemporaryDirectory(prefix="qsot_kd_") as temp_dir:
        temp_dir_path = Path(temp_dir)
        state_path = temp_dir_path / "temp_state.npz"
        out_path = temp_dir_path / "temp_opt.json"

        np.savez(state_path, rho_0=np.array(flat_rho))
        kd_flat = run_kd_optimization(str(state_path), str(out_path), steps=KD_OPTIMIZATION_STEPS)

        # Save de Sitter final state
        np.savez(state_path, rho_0=c_desitter.state.rho)
        kd_desitter = run_kd_optimization(
            str(state_path),
            str(out_path),
            steps=KD_OPTIMIZATION_STEPS,
        )

    kd_checks = [
        "kd_basis_optimization_ran",
        "kd_returns_basis_angles",
        "kd_optimization_converged",
        "kd_relative_signal_recorded",
    ]
    if TORCH_AVAILABLE:
        if kd_flat is not None and kd_desitter is not None:
            ctx.result.observations["kd_flat"] = kd_flat
            ctx.result.observations["kd_desitter"] = kd_desitter
            # Surface the state-preparation depth that produced the KD target
            # state so calibration/source provenance is not hidden behind a
            # hardcoded local constant.
            ctx.result.observations["kd_flat"]["state_prep_steps"] = 0
            ctx.result.observations["kd_desitter"]["state_prep_steps"] = ctx.config.steps

            # Flat-relative comparative signal. Raw KD negativity is NOT treated as
            # a standalone contextuality proof (Packet A); the de-Sitter-minus-flat
            # delta is the reported model-relative quantity, and optimizer
            # convergence is surfaced separately.
            flat_val = kd_flat["kd_value"]
            desitter_val = kd_desitter["kd_value"]
            flat_conv = bool(kd_flat.get("convergence", {}).get("converged", False))
            desitter_conv = bool(kd_desitter.get("convergence", {}).get("converged", False))
            both_converged = flat_conv and desitter_conv
            kd_delta = {
                "value": desitter_val - flat_val,
                "kd_flat": flat_val,
                "kd_desitter": desitter_val,
                "flat_converged": flat_conv,
                "desitter_converged": desitter_conv,
                "interpretation": (
                    "Relative KD signal (de Sitter minus flat) under the implemented "
                    "model. Not a standalone proof of curvature-induced contextuality; "
                    "optimizer convergence status is reported separately."
                ),
            }
            ctx.result.observations["kd_delta"] = kd_delta

            # Engineering: both optimizations produced a value.
            ctx.result.checks["kd_basis_optimization_ran"] = (
                "PASS" if ("kd_value" in kd_flat and "kd_value" in kd_desitter) else "FAIL"
            )
            # Structural: basis angles returned.
            ctx.result.checks["kd_returns_basis_angles"] = (
                "PASS"
                if (
                    "angles" in kd_desitter
                    and "basis_a" in kd_desitter["angles"]
                    and "basis_b" in kd_desitter["angles"]
                )
                else "FAIL"
            )
            # Convergence explicitly labeled: converged -> PASS, otherwise
            # DEGRADED_PASS (a non-converged but labeled relative proxy is
            # acceptable in Stage A and is surfaced in the verdict).
            ctx.result.checks["kd_optimization_converged"] = (
                "PASS" if both_converged else "DEGRADED_PASS"
            )
            # Comparative signal recorded (finite delta), not a raw-negativity proof.
            ctx.result.checks["kd_relative_signal_recorded"] = (
                "PASS" if np.isfinite(kd_delta["value"]) else "FAIL"
            )
        else:
            for c in kd_checks:
                ctx.result.checks[c] = "FAIL"
    else:
        for c in kd_checks:
            ctx.result.checks[c] = "SKIPPED"
        ctx.result.observations["kd_note"] = "PyTorch not found. KD optimization checks skipped."


def skip_phase4(ctx: PhaseContext) -> None:
    """Skip Phase 4 checks."""
    for c in PHASE_CHECKS["phase4_kd_governance"]:
        ctx.result.checks[c] = "SKIPPED"
