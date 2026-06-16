"""Kirkwood-Dirac and Temporal-State candidate principle axioms checks."""

from __future__ import annotations

from typing import Callable, List

import numpy as np


class TemporalStateAxiomVerifier:
    """Mathematical verifier for the Temporal-State candidate principle axioms."""

    def __init__(self, atol: float = 1e-12, rtol: float = 1e-10):
        self.atol = atol
        self.rtol = rtol

    def check_linearity(
        self,
        rho_a: np.ndarray,
        rho_b: np.ndarray,
        map_fn: Callable[[np.ndarray], np.ndarray],
        alpha: float = 0.5,
    ) -> bool:
        """Axiom: Linearity. The mapping over time must behave linearly over state mixtures."""
        mixed_rho = alpha * rho_a + (1 - alpha) * rho_b
        out_mixed = map_fn(mixed_rho)
        out_linear = alpha * map_fn(rho_a) + (1 - alpha) * map_fn(rho_b)
        return np.allclose(out_mixed, out_linear, atol=self.atol, rtol=self.rtol)

    def check_cptp_completeness(self, kraus_operators: List[np.ndarray]) -> bool:
        """Axiom: CPTP Completeness Condition. sum(K_i^\\dagger K_i) == I."""
        if not kraus_operators:
            return False
        dim = kraus_operators[0].shape[0]
        sum_k_dagger_k = sum(np.dot(k.conj().T, k) for k in kraus_operators)
        return np.allclose(sum_k_dagger_k, np.eye(dim), atol=self.atol, rtol=self.rtol)

    def check_trace_preservation_on_states(
        self, kraus_operators: List[np.ndarray], test_states: List[np.ndarray]
    ) -> bool:
        """Axiom: Actual trace preservation on target states. Tr(E(rho)) == 1."""
        if not kraus_operators or not test_states:
            return False
        for rho in test_states:
            evolved = sum(k @ rho @ k.conj().T for k in kraus_operators)
            trace_val = np.trace(evolved).real
            if not np.isclose(trace_val, 1.0, atol=self.atol, rtol=self.rtol):
                return False
        return True

    # --- Conditionability (Composition Consistency) ---
    def check_sequential_replay_consistency(
        self,
        rho_i: np.ndarray,
        rho_next: np.ndarray,
        channel_fn: Callable[[np.ndarray], np.ndarray],
    ) -> bool:
        """Verify 1-step trajectory replay matches channel: rho_{i+1} ~= E_i(rho_i).

        The conditionability check verifies trajectory and composed-channel consistency under the implemented model.
        It does not by itself prove a physical theorem about time.
        """
        return np.allclose(channel_fn(rho_i), rho_next, atol=self.atol, rtol=self.rtol)

    def check_two_step_conditionability(
        self,
        rho_i: np.ndarray,
        rho_next_next: np.ndarray,
        channel_a: Callable[[np.ndarray], np.ndarray],
        channel_b: Callable[[np.ndarray], np.ndarray],
    ) -> bool:
        """Verify 2-step composition: rho_{i+2} ~= E_{i+1}(E_i(rho_i)).

        The conditionability check verifies trajectory and composed-channel consistency under the implemented model.
        It does not by itself prove a physical theorem about time.
        """
        return np.allclose(
            channel_b(channel_a(rho_i)), rho_next_next, atol=self.atol, rtol=self.rtol
        )

    def check_composed_channel_consistency(
        self,
        rho0: np.ndarray,
        channel_a: Callable[[np.ndarray], np.ndarray],
        channel_b: Callable[[np.ndarray], np.ndarray],
        composed_channel: Callable[[np.ndarray], np.ndarray],
    ) -> bool:
        """Verify composed evolution matches sequential composition: E_b(E_a(rho)) ~= E_ba(rho).

        The conditionability check verifies trajectory and composed-channel consistency under the implemented model.
        It does not by itself prove a physical theorem about time.
        """
        seq_evolved = channel_b(channel_a(rho0))
        comp_evolved = composed_channel(rho0)
        return np.allclose(seq_evolved, comp_evolved, atol=self.atol, rtol=self.rtol)

    # --- Density Matrix Validity ---
    def check_density_validity(self, rho: np.ndarray) -> bool:
        """Verify density matrix physical properties: Hermitian, Trace=1, and PSD."""
        if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
            return False
        hermitian = np.allclose(rho, rho.conj().T, atol=self.atol, rtol=self.rtol)
        trace_ok = np.isclose(np.trace(rho).real, 1.0, atol=self.atol, rtol=self.rtol)
        rho_h = (rho + rho.conj().T) / 2
        eigvals = np.linalg.eigvalsh(rho_h)
        psd = np.all(eigvals >= -self.atol)
        return bool(hermitian and trace_ok and psd)

    def check_density_validity_on_trajectory(self, rhos: List[np.ndarray]) -> bool:
        """Verify density validity for all states in a sequence."""
        return all(self.check_density_validity(rho) for rho in rhos)
