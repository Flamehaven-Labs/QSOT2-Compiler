"""Unit tests for Temporal-State Axioms verifier and Phase 0 checks."""

from __future__ import annotations

import numpy as np

from qsot2.model.axioms import TemporalStateAxiomVerifier
from qsot2.model.falsification import run_phase0_checks


def test_linearity_passes_for_valid_kraus_channel():
    verifier = TemporalStateAxiomVerifier()
    kraus = [np.eye(2)]

    def valid_map(rho):
        return sum(k @ rho @ k.conj().T for k in kraus)

    rho_a = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_b = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)

    assert verifier.check_linearity(rho_a, rho_b, valid_map) is True


def test_linearity_fails_for_nonlinear_map():
    verifier = TemporalStateAxiomVerifier()

    def nonlinear_map(rho):
        return rho @ rho

    rho_a = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_b = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)

    assert verifier.check_linearity(rho_a, rho_b, nonlinear_map) is False


def test_cptp_completeness_fails_for_broken_kraus():
    verifier = TemporalStateAxiomVerifier()

    broken_kraus = [0.5 * np.eye(2)]
    assert verifier.check_cptp_completeness(broken_kraus) is False
    assert verifier.check_cptp_completeness([]) is False


def test_trace_preservation_fails_for_leaky_channel():
    verifier = TemporalStateAxiomVerifier()

    leaky_kraus = [np.sqrt(0.9) * np.eye(2)]
    test_states = [np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)]

    assert verifier.check_trace_preservation_on_states(leaky_kraus, test_states) is False


def test_conditionability_passes_for_composed_channels():
    verifier = TemporalStateAxiomVerifier()

    def identity_map(rho):
        return rho

    rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    assert (
        verifier.check_composed_channel_consistency(rho0, identity_map, identity_map, identity_map)
        is True
    )


def test_conditionability_fails_for_mismatched_external_trajectory():
    verifier = TemporalStateAxiomVerifier()

    rho_i = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_next = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)

    def identity_map(rho):
        return rho

    assert verifier.check_sequential_replay_consistency(rho_i, rho_next, identity_map) is False


def test_density_validity_rejects_non_psd_matrix():
    verifier = TemporalStateAxiomVerifier()

    non_psd = np.array([[0.5, 1.5], [1.5, 0.5]], dtype=complex)
    assert verifier.check_density_validity(non_psd) is False


def test_run_phase0_checks_integration():
    res = run_phase0_checks(sensitivity=0.1, boost_beta=0.5)
    assert "checks" in res
    assert "observations" in res
    assert all(status == "PASS" for status in res["checks"].values())
