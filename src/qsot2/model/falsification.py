"""Falsification harness orchestrating Phase 0 axiom checks."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from qsot2.model.channels import BACKGROUND_BUILDERS, MetricToChannelMap
from qsot2.model.quantum import QuantumCircuit, QuantumState
from qsot2.model.axioms import TemporalStateAxiomVerifier


def run_phase0_checks(sensitivity: float, boost_beta: float) -> Dict[str, Any]:
    """Execute the Phase 0 Temporal-State Axiom Contract checks under stress.

    Evaluates linearity, completeness, trace preservation, conditionability, and density
    validity across flat, curved (Schwarzschild/de Sitter), rest, and relativistic boosted observer frames.
    """
    verifier = TemporalStateAxiomVerifier()

    # 1. Generate test states (ground state, |+> state, and random Ginibre states)
    test_states = [
        QuantumState.ground().rho,
        QuantumState.from_bloch(np.pi / 2, 0.0).rho,
    ]
    # Add random density matrices
    rng = np.random.default_rng(42)
    for _ in range(3):
        x = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
        rho_random = x @ x.conj().T
        rho_random /= np.trace(rho_random)
        test_states.append(rho_random)

    # 2. Build test background & channels (Minkowski, Schwarzschild, de Sitter, Eguchi-Hanson)
    bg_flat = BACKGROUND_BUILDERS["flat"](10)
    bg_schwarz = BACKGROUND_BUILDERS["schwarzschild"](10)
    bg_desitter = BACKGROUND_BUILDERS["de_sitter"](10)
    bg_eguchi = BACKGROUND_BUILDERS["eguchi_hanson"](10)

    mapper = MetricToChannelMap(sensitivity=sensitivity)

    # Stress test channel scenarios:
    #   A. Flat rest depolarizing
    #   B. Flat boosted dephasing (using boost_beta)
    #   C. Schwarzschild rest depolarizing
    #   D. de Sitter rest dephasing
    #   E. Eguchi-Hanson rest depolarizing (mathematical validity verify)
    scenarios = [
        {"bg": bg_flat, "vel": 0.0, "type": "depolarizing"},
        {"bg": bg_flat, "vel": boost_beta, "type": "dephasing"},
        {"bg": bg_schwarz, "vel": 0.0, "type": "depolarizing"},
        {"bg": bg_desitter, "vel": 0.0, "type": "dephasing"},
        {"bg": bg_eguchi, "vel": 0.0, "type": "depolarizing"},
    ]

    linearity_ok = True
    cptp_ok = True
    trace_ok = True
    cond_ok = True
    replay_1_ok = True
    replay_2_ok = True
    density_ok = True

    linearity_max_dev = 0.0
    cptp_max_dev = 0.0
    trace_max_dev = 0.0
    composed_max_dev = 0.0
    replay_1_max_dev = 0.0
    replay_2_max_dev = 0.0

    scenario_observations = []

    for spec in scenarios:
        bg = spec["bg"]
        vel = spec["vel"]
        ctype = spec["type"]

        info = mapper.gravitational_decoherence(bg, observer_velocity=vel, channel_type=ctype)
        ch = info["channel"]
        kraus_ops = ch.kraus_ops

        def single_step_map(rho: np.ndarray, kraus_ops=kraus_ops) -> np.ndarray:
            return sum(k @ rho @ k.conj().T for k in kraus_ops)

        def composed_map_fn(rho: np.ndarray, ch=ch) -> np.ndarray:
            circuit = QuantumCircuit(QuantumState(rho))
            for _ in range(2):
                circuit.apply_channel(ch)
            return circuit.state.rho

        # Linearity
        curr_lin_ok = verifier.check_linearity(test_states[0], test_states[1], single_step_map)
        linearity_ok = linearity_ok and curr_lin_ok
        lin_dev = float(
            np.linalg.norm(
                0.5 * single_step_map(test_states[0])
                + 0.5 * single_step_map(test_states[1])
                - single_step_map(0.5 * test_states[0] + 0.5 * test_states[1])
            )
        )
        linearity_max_dev = max(linearity_max_dev, lin_dev)

        # CPTP Completeness
        curr_cptp_ok = verifier.check_cptp_completeness(kraus_ops)
        cptp_ok = cptp_ok and curr_cptp_ok
        cptp_dev = ch.completeness_error
        cptp_max_dev = max(cptp_max_dev, cptp_dev)

        # Trace Preservation
        curr_trace_ok = verifier.check_trace_preservation_on_states(kraus_ops, test_states)
        trace_ok = trace_ok and curr_trace_ok
        scenario_trace_dev = 0.0
        for state_rho in test_states:
            trace_val = np.trace(single_step_map(state_rho)).real
            scenario_trace_dev = max(scenario_trace_dev, abs(trace_val - 1.0))
        trace_max_dev = max(trace_max_dev, scenario_trace_dev)

        # Composed Channel Consistency (E_b E_a = E_ba)
        curr_cond_ok = verifier.check_composed_channel_consistency(
            test_states[2], single_step_map, single_step_map, composed_map_fn
        )
        cond_ok = cond_ok and curr_cond_ok
        comp_dev = float(
            np.linalg.norm(
                single_step_map(single_step_map(test_states[2])) - composed_map_fn(test_states[2])
            )
        )
        composed_max_dev = max(composed_max_dev, comp_dev)

        # Trajectory Replay (Conditionability)
        circuit = QuantumCircuit(QuantumState(test_states[3]))
        circuit.apply_channel(ch)
        circuit.apply_channel(ch)
        rho_0 = test_states[3]
        rho_1 = circuit.history[1].rho
        rho_2 = circuit.history[2].rho

        curr_rep1_ok = verifier.check_sequential_replay_consistency(rho_0, rho_1, single_step_map)
        curr_rep2_ok = verifier.check_two_step_conditionability(
            rho_0, rho_2, single_step_map, single_step_map
        )
        replay_1_ok = replay_1_ok and curr_rep1_ok
        replay_2_ok = replay_2_ok and curr_rep2_ok

        rep1_dev = float(np.linalg.norm(single_step_map(rho_0) - rho_1))
        rep2_dev = float(np.linalg.norm(single_step_map(single_step_map(rho_0)) - rho_2))
        replay_1_max_dev = max(replay_1_max_dev, rep1_dev)
        replay_2_max_dev = max(replay_2_max_dev, rep2_dev)

        # Density Matrix Validity
        trajectory = [s.rho for s in circuit.history]
        curr_density_ok = verifier.check_density_validity_on_trajectory(trajectory)
        density_ok = density_ok and curr_density_ok

        scenario_observations.append(
            {
                "background": bg.name,
                "observer_velocity": float(vel),
                "channel_type": ctype,
                "linearity_deviation": float(lin_dev),
                "cptp_deviation": float(cptp_dev),
                "trace_max_deviation": float(scenario_trace_dev),
                "composed_channel_deviation": float(comp_dev),
                "sequential_replay_deviation": float(rep1_dev),
                "two_step_conditionability_deviation": float(rep2_dev),
                "density_validity": bool(curr_density_ok),
            }
        )

    conditionability_holds = cond_ok and replay_1_ok and replay_2_ok

    checks = {
        "temporal_axiom_linearity_holds": "PASS" if linearity_ok else "FAIL",
        "temporal_axiom_cptp_completeness_holds": "PASS" if cptp_ok else "FAIL",
        "temporal_axiom_trace_preservation_holds": "PASS" if trace_ok else "FAIL",
        "temporal_axiom_conditionability_holds": "PASS" if conditionability_holds else "FAIL",
        "temporal_axiom_density_validity_holds": "PASS" if density_ok else "FAIL",
    }

    observations = {
        "linearity_max_deviation": linearity_max_dev,
        "cptp_completeness_max_deviation": cptp_max_dev,
        "trace_preservation_max_deviation": trace_max_dev,
        "composed_channel_max_deviation": composed_max_dev,
        "sequential_replay_max_deviation": replay_1_max_dev,
        "two_step_conditionability_max_deviation": replay_2_max_dev,
        "phase0_sensitivity_used": sensitivity,
        "phase0_boost_beta_used": boost_beta,
        "phase0_scenarios": scenario_observations,
    }

    return {
        "checks": checks,
        "observations": observations,
    }
