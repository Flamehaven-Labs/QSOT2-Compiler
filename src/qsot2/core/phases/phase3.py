"""Phase 3: Relativistic Boosts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qsot2.core.checks import PHASE_CHECKS
from qsot2.model import (
    BACKGROUND_BUILDERS,
    MetricToChannelMap,
    QuantumCircuit,
    QuantumState,
)

if TYPE_CHECKING:
    from qsot2.core.phase_context import PhaseContext


def run_phase3(ctx: PhaseContext) -> None:
    """Execute Phase 3 checks."""
    D = 10
    bg_ads = BACKGROUND_BUILDERS["ads5"](D)
    bg_schwarz = BACKGROUND_BUILDERS["schwarzschild"](D)
    mapper = MetricToChannelMap(sensitivity=ctx.config.sensitivity)

    # Rest frame AdS5
    ads_rest = mapper.gravitational_decoherence(bg_ads, observer_velocity=0.0)
    c_rest = QuantumCircuit(QuantumState.ground()).apply_channel(ads_rest["channel"])
    p_rest = c_rest.state.purity

    # Boosted AdS5
    ads_boost = mapper.gravitational_decoherence(bg_ads, observer_velocity=ctx.config.boost_beta)
    c_boost = QuantumCircuit(QuantumState.ground()).apply_channel(ads_boost["channel"])
    p_boost = c_boost.state.purity

    ctx.result.checks["boost_accelerates_purity_decay"] = "PASS" if p_boost < p_rest else "FAIL"
    ctx.result.checks["boost_amplifies_noise_parameter"] = (
        "PASS" if ads_boost["p_effective"] > ads_boost["p_curvature"] else "FAIL"
    )
    ctx.result.checks["gamma_boost_greater_than_1"] = (
        "PASS" if ads_boost["gamma_boost"] > 1.0 else "FAIL"
    )
    ctx.result.observations["ads_boost_info"] = {
        k: v for k, v in ads_boost.items() if k != "channel"
    }

    # Schwarzschild boost
    schwarz_rest = mapper.gravitational_decoherence(bg_schwarz, observer_velocity=0.0)
    ctx.result.checks["gamma_grav_greater_than_1"] = (
        "PASS" if schwarz_rest["gamma_gravitational"] > 1.0 else "FAIL"
    )
    ctx.result.checks["gamma_total_combines_effects"] = (
        "PASS" if ads_boost["gamma_total"] > 1.0 else "FAIL"
    )
    ctx.result.observations["schwarz_rest_info"] = {
        k: v for k, v in schwarz_rest.items() if k != "channel"
    }


def skip_phase3(ctx: PhaseContext) -> None:
    """Skip Phase 3 checks."""
    for c in PHASE_CHECKS["phase3_boosts"]:
        ctx.result.checks[c] = "SKIPPED"
