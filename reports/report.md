# QSOT2 Mathematical-Consistency Verification Report

**Verdict:** `DEGRADED_PASS`
**Generated:** `2026-06-16T02:31:05.091253+00:00`

> [!NOTE]
> **Scope.** QSOT2 verifies the *internal mathematical consistency* of a phenomenological
> quantum-channel model of curved-spacetime backgrounds. It does **not** claim external
> physical validity, first-principles grounding, or new physics. A passing check means
> model-internal mathematical consistency under the stated assumptions.

## Check Summary
- **Total checks:** 35
- **PASS:** 34
- **DEGRADED_PASS:** 1
- **SKIPPED:** 0
- **FAIL:** 0

## Checks

- `temporal_axiom_linearity_holds`: **PASS**
- `temporal_axiom_cptp_completeness_holds`: **PASS**
- `temporal_axiom_trace_preservation_holds`: **PASS**
- `temporal_axiom_conditionability_holds`: **PASS**
- `temporal_axiom_density_validity_holds`: **PASS**
- `flat_rest_purity_is_1`: **PASS**
- `flat_rest_entropy_is_0`: **PASS**
- `flat_gate_passes`: **PASS**
- `flat_ctc_is_clear`: **PASS**
- `flat_boost_purity_is_1`: **PASS**
- `schwarzschild_purity_decays`: **PASS**
- `desitter_purity_decays`: **PASS**
- `ads5_purity_decays`: **PASS**
- `eguchi_hanson_purity_decays`: **PASS**
- `schwarzschild_entropy_positive`: **PASS**
- `desitter_entropy_positive`: **PASS**
- `ads5_entropy_positive`: **PASS**
- `eguchi_hanson_entropy_positive`: **PASS**
- `desitter_gate_fails`: **PASS**
- `godel_gate_fails_and_ctc_detected`: **PASS**
- `eguchi_hanson_gate_fails_gs`: **PASS**
- `schwarzschild_curvature_positive`: **PASS**
- `desitter_curvature_positive`: **PASS**
- `ads5_curvature_positive`: **PASS**
- `eguchi_hanson_curvature_positive`: **PASS**
- `boost_accelerates_purity_decay`: **PASS**
- `boost_amplifies_noise_parameter`: **PASS**
- `gamma_boost_greater_than_1`: **PASS**
- `gamma_grav_greater_than_1`: **PASS**
- `gamma_total_combines_effects`: **PASS**
- `kd_basis_optimization_ran`: **PASS**
- `kd_returns_basis_angles`: **PASS**
- `kd_optimization_converged`: **DEGRADED_PASS**
- `kd_relative_signal_recorded`: **PASS**
- `memory_kernel_selftest_detects_injected_backflow`: **PASS**


## Interpretation

The 35 automated checks verify consistency with the implemented model assumptions:

1. **Temporal-state axioms (Phase 0):** linearity, CPTP completeness, trace preservation, conditionability, and density-matrix validity hold to machine epsilon.
2. **Flat Minkowski baselines (Phase 1):** a qubit evolved through flat spacetime preserves purity ($P = 1.0$) and zero von Neumann entropy.
3. **Curvature noise (Phase 2):** curved backgrounds (Schwarzschild, de Sitter, AdS5, Eguchi-Hanson) induce purity decay and entropy growth via the Riemann-norm channel map -- a phenomenological ansatz, not a derivation; Ricci-flat vacua still pass the admissibility gate.
4. **Relativistic boosts (Phase 3):** boosts amplify the effective noise parameter within the implemented model.
5. **Kirkwood-Dirac, flat-relative (Phase 4):** a bounded basis search reports the de-Sitter-minus-flat KD delta as a relative quantity under the model -- not a contextuality proof. Non-convergence within the fixed step budget is surfaced explicitly as `DEGRADED_PASS`.
6. **TTM-inspired memory proxy (Phase 5):** a detector self-test on a synthetic injected backflow confirms it registers $\text{nm} > 0$; the model's own trajectory is Markovian by construction ($\text{nm} \approx 0$). The self-test validates the detector, not non-Markovian physics in the model.

External physical validity is outside the scope of this report.