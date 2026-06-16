"""Phase 2: Curvature Noise."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qsot2.core.checks import PHASE_CHECKS
from qsot2.model import (
    BACKGROUND_BUILDERS,
    QuantumCircuit,
    QuantumState,
    run_background_verify,
)

if TYPE_CHECKING:
    from qsot2.core.phase_context import PhaseContext


def run_phase2(ctx: PhaseContext) -> None:
    """Execute Phase 2 checks."""
    D = 10
    bg_schwarz = BACKGROUND_BUILDERS["schwarzschild"](D)
    bg_desitter = BACKGROUND_BUILDERS["de_sitter"](D)
    bg_ads = BACKGROUND_BUILDERS["ads5"](D)
    bg_eguchi = BACKGROUND_BUILDERS["eguchi_hanson"](D)

    # Evolve states
    c_schwarz = QuantumCircuit(QuantumState.ground())
    s_schwarz = c_schwarz.evolve_through_background(
        bg_schwarz, steps=ctx.config.steps, sensitivity=ctx.config.sensitivity
    )

    c_desitter = QuantumCircuit(QuantumState.ground())
    s_desitter = c_desitter.evolve_through_background(
        bg_desitter, steps=ctx.config.steps, sensitivity=ctx.config.sensitivity
    )

    c_ads = QuantumCircuit(QuantumState.ground())
    s_ads = c_ads.evolve_through_background(
        bg_ads, steps=ctx.config.steps, sensitivity=ctx.config.sensitivity
    )

    c_eguchi = QuantumCircuit(QuantumState.ground())
    s_eguchi = c_eguchi.evolve_through_background(
        bg_eguchi, steps=ctx.config.steps, sensitivity=ctx.config.sensitivity
    )

    # Decay checks
    ctx.result.checks["schwarzschild_purity_decays"] = (
        "PASS" if s_schwarz[-1].purity < 1.0 else "FAIL"
    )
    ctx.result.checks["desitter_purity_decays"] = "PASS" if s_desitter[-1].purity < 1.0 else "FAIL"
    ctx.result.checks["ads5_purity_decays"] = "PASS" if s_ads[-1].purity < 1.0 else "FAIL"
    ctx.result.checks["eguchi_hanson_purity_decays"] = (
        "PASS" if s_eguchi[-1].purity < 1.0 else "FAIL"
    )

    ctx.result.observations["schwarz_purity"] = s_schwarz[-1].purity
    ctx.result.observations["desitter_purity"] = s_desitter[-1].purity
    ctx.result.observations["ads_purity"] = s_ads[-1].purity
    ctx.result.observations["eguchi_purity"] = s_eguchi[-1].purity

    # Entropy positive checks
    ctx.result.checks["schwarzschild_entropy_positive"] = (
        "PASS" if s_schwarz[-1].von_neumann_entropy > 0.0 else "FAIL"
    )
    ctx.result.checks["desitter_entropy_positive"] = (
        "PASS" if s_desitter[-1].von_neumann_entropy > 0.0 else "FAIL"
    )
    ctx.result.checks["ads5_entropy_positive"] = (
        "PASS" if s_ads[-1].von_neumann_entropy > 0.0 else "FAIL"
    )
    ctx.result.checks["eguchi_hanson_entropy_positive"] = (
        "PASS" if s_eguchi[-1].von_neumann_entropy > 0.0 else "FAIL"
    )

    ctx.result.observations["schwarz_entropy"] = s_schwarz[-1].von_neumann_entropy
    ctx.result.observations["desitter_entropy"] = s_desitter[-1].von_neumann_entropy
    ctx.result.observations["ads_entropy"] = s_ads[-1].von_neumann_entropy
    ctx.result.observations["eguchi_entropy"] = s_eguchi[-1].von_neumann_entropy
    ctx.state.desitter_final_rho = s_desitter[-1].rho

    # Gate verification reports
    desitter_verify = run_background_verify("de_sitter")[0]
    godel_verify = run_background_verify("godel_universe")[0]
    eguchi_verify = run_background_verify("eguchi_hanson")[0]
    schwarz_verify = run_background_verify("schwarzschild")[0]
    ads_verify = run_background_verify("ads5")[0]

    ctx.result.checks["desitter_gate_fails"] = (
        "PASS" if desitter_verify["gate"] == "FAIL" else "FAIL"
    )
    ctx.result.checks["godel_gate_fails_and_ctc_detected"] = (
        "PASS"
        if (
            godel_verify["gate"] == "FAIL"
            and godel_verify["physics"]["ctc_status"].upper() == "DETECTED"
        )
        else "FAIL"
    )
    ctx.result.checks["eguchi_hanson_gate_fails_gs"] = (
        "PASS"
        if (
            eguchi_verify["gate"] == "FAIL" and eguchi_verify["physics"]["gs_anomaly_flag"] is True
        )
        else "FAIL"
    )

    ctx.result.observations["desitter_verify"] = desitter_verify
    ctx.result.observations["godel_verify"] = godel_verify
    ctx.result.observations["eguchi_verify"] = eguchi_verify
    ctx.result.observations["schwarzschild_verify"] = schwarz_verify
    ctx.result.observations["ads5_verify"] = ads_verify

    # Curvature positive checks
    ctx.result.checks["schwarzschild_curvature_positive"] = (
        "PASS" if schwarz_verify["physics"]["riemann_norm"] > 0.0 else "FAIL"
    )
    ctx.result.checks["desitter_curvature_positive"] = (
        "PASS" if desitter_verify["physics"]["riemann_norm"] > 0.0 else "FAIL"
    )
    ctx.result.checks["ads5_curvature_positive"] = (
        "PASS" if ads_verify["physics"]["riemann_norm"] > 0.0 else "FAIL"
    )
    ctx.result.checks["eguchi_hanson_curvature_positive"] = (
        "PASS" if eguchi_verify["physics"]["riemann_norm"] > 0.0 else "FAIL"
    )


def skip_phase2(ctx: PhaseContext) -> None:
    """Skip Phase 2 checks."""
    for c in PHASE_CHECKS["phase2_curvature_noise"]:
        ctx.result.checks[c] = "SKIPPED"
