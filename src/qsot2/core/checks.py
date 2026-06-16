"""Central registry for all experiment checks and required flags."""

from __future__ import annotations

# List of required checks that must pass (or not be skipped) to get a PASS verdict
REQUIRED_CHECKS = {
    # Phase 0: Temporal Axioms
    "temporal_axiom_linearity_holds",
    "temporal_axiom_cptp_completeness_holds",
    "temporal_axiom_trace_preservation_holds",
    "temporal_axiom_conditionability_holds",
    "temporal_axiom_density_validity_holds",
    # Phase 1: Flat Baselines
    "flat_rest_purity_is_1",
    "flat_rest_entropy_is_0",
    "flat_gate_passes",
    "flat_boost_purity_is_1",
    "flat_ctc_is_clear",
    # Phase 2: Curvature Noise
    "schwarzschild_purity_decays",
    "desitter_purity_decays",
    "ads5_purity_decays",
    "eguchi_hanson_purity_decays",
    "desitter_gate_fails",
    "godel_gate_fails_and_ctc_detected",
    "eguchi_hanson_gate_fails_gs",
    "schwarzschild_entropy_positive",
    "desitter_entropy_positive",
    "ads5_entropy_positive",
    "eguchi_hanson_entropy_positive",
    "schwarzschild_curvature_positive",
    "desitter_curvature_positive",
    "ads5_curvature_positive",
    "eguchi_hanson_curvature_positive",
    # Phase 3: Relativistic Boosts
    "boost_accelerates_purity_decay",
    "boost_amplifies_noise_parameter",
    "gamma_boost_greater_than_1",
    "gamma_grav_greater_than_1",
    "gamma_total_combines_effects",
    # Phase 5: TTM (memory-proxy self-test)
    "memory_kernel_selftest_detects_injected_backflow",
}

# Grouping of checks by phase ID
PHASE_CHECKS = {
    "phase0_temporal_axioms": [
        "temporal_axiom_linearity_holds",
        "temporal_axiom_cptp_completeness_holds",
        "temporal_axiom_trace_preservation_holds",
        "temporal_axiom_conditionability_holds",
        "temporal_axiom_density_validity_holds",
    ],
    "phase1_flat_baselines": [
        "flat_rest_purity_is_1",
        "flat_rest_entropy_is_0",
        "flat_gate_passes",
        "flat_boost_purity_is_1",
        "flat_ctc_is_clear",
    ],
    "phase2_curvature_noise": [
        "schwarzschild_purity_decays",
        "desitter_purity_decays",
        "ads5_purity_decays",
        "eguchi_hanson_purity_decays",
        "desitter_gate_fails",
        "godel_gate_fails_and_ctc_detected",
        "eguchi_hanson_gate_fails_gs",
        "schwarzschild_entropy_positive",
        "desitter_entropy_positive",
        "ads5_entropy_positive",
        "eguchi_hanson_entropy_positive",
        "schwarzschild_curvature_positive",
        "desitter_curvature_positive",
        "ads5_curvature_positive",
        "eguchi_hanson_curvature_positive",
    ],
    "phase3_boosts": [
        "boost_accelerates_purity_decay",
        "boost_amplifies_noise_parameter",
        "gamma_boost_greater_than_1",
        "gamma_grav_greater_than_1",
        "gamma_total_combines_effects",
    ],
    "phase4_kd_governance": [
        "kd_basis_optimization_ran",
        "kd_returns_basis_angles",
        "kd_optimization_converged",
        "kd_relative_signal_recorded",
    ],
    "phase5_ttm_accessibility": [
        "memory_kernel_selftest_detects_injected_backflow",
    ],
}
