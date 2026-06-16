"""Phase 1: Flat Baselines."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qsot2.core.checks import PHASE_CHECKS
from qsot2.model import (
    BACKGROUND_BUILDERS,
    MetricToChannelMap,
    QuantumCircuit,
    QuantumState,
    run_background_verify,
)

if TYPE_CHECKING:
    from qsot2.core.phase_context import PhaseContext


def run_phase1(ctx: PhaseContext) -> None:
    """Execute Phase 1 checks."""
    D = 10
    bg_flat = BACKGROUND_BUILDERS["flat"](D)

    # flat_rest_purity_is_1, flat_rest_entropy_is_0
    circuit = QuantumCircuit(QuantumState.ground())
    states = circuit.evolve_through_background(
        bg_flat, steps=ctx.config.steps, sensitivity=ctx.config.sensitivity
    )
    purities = [s.purity for s in states]
    entropies = [s.von_neumann_entropy for s in states]

    ctx.result.checks["flat_rest_purity_is_1"] = (
        "PASS" if all(abs(p - 1.0) < 1e-12 for p in purities) else "FAIL"
    )
    ctx.result.checks["flat_rest_entropy_is_0"] = (
        "PASS" if all(e < 1e-12 for e in entropies) else "FAIL"
    )
    ctx.result.observations["flat_rest_purities"] = purities
    ctx.result.observations["flat_rest_entropies"] = entropies
    ctx.state.flat_final_rho = states[-1].rho

    # flat_gate_passes & flat_ctc_is_clear
    flat_verify = run_background_verify("flat")[0]
    ctx.result.checks["flat_gate_passes"] = "PASS" if flat_verify["gate"] == "PASS" else "FAIL"
    ctx.result.checks["flat_ctc_is_clear"] = (
        "PASS" if flat_verify["physics"]["ctc_status"] == "CLEAR" else "FAIL"
    )
    ctx.result.observations["flat_verify"] = flat_verify

    # flat_boost_purity_is_1
    mapper = MetricToChannelMap(sensitivity=ctx.config.sensitivity)
    flat_boost = mapper.gravitational_decoherence(
        bg_flat, observer_velocity=ctx.config.boost_beta, channel_type="depolarizing"
    )
    ch_boost = flat_boost["channel"]
    circuit_boost = QuantumCircuit(QuantumState.ground())
    for _ in range(ctx.config.steps):
        circuit_boost.apply_channel(ch_boost)
    purities_boost = [s.purity for s in circuit_boost.history]
    ctx.result.checks["flat_boost_purity_is_1"] = (
        "PASS" if all(abs(p - 1.0) < 1e-12 for p in purities_boost) else "FAIL"
    )
    ctx.result.observations["flat_boost_purities"] = purities_boost


def skip_phase1(ctx: PhaseContext) -> None:
    """Skip Phase 1 checks."""
    for c in PHASE_CHECKS["phase1_flat_baselines"]:
        ctx.result.checks[c] = "SKIPPED"
