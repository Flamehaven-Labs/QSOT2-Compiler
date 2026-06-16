"""Single-qubit quantum simulator matching standard QuantumCircuit and QuantumState.

Pure numpy implementation: no external quantum framework required.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

# Pauli gates
_I = np.eye(2, dtype=complex)
_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
_Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


@dataclass
class QuantumState:
    """Single-qubit density matrix wrapper."""

    rho: np.ndarray

    def __post_init__(self) -> None:
        self.rho = np.asarray(self.rho, dtype=complex)
        if self.rho.shape != (2, 2):
            raise ValueError(f"rho must be (2,2), got {self.rho.shape}")

    @classmethod
    def ground(cls) -> "QuantumState":
        """Pure |0><0| state."""
        return cls(np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex))

    @classmethod
    def excited(cls) -> "QuantumState":
        """Pure |1><1| state."""
        return cls(np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex))

    @classmethod
    def maximally_mixed(cls) -> "QuantumState":
        """Maximally mixed state I/2 (maximum entropy)."""
        return cls(np.eye(2, dtype=complex) / 2.0)

    @classmethod
    def from_bloch(cls, theta: float, phi: float = 0.0) -> "QuantumState":
        """Pure state from Bloch sphere angles."""
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        psi = np.array([c, math.cos(phi) * s + 1j * math.sin(phi) * s], dtype=complex)
        rho = np.outer(psi, psi.conj())
        return cls(rho)

    @property
    def purity(self) -> float:
        """Tr(rho^2) in [0.5, 1.0]."""
        return float(np.trace(self.rho @ self.rho).real)

    @property
    def coherence(self) -> float:
        """Off-diagonal element magnitude |rho_01|."""
        return float(abs(self.rho[0, 1]))

    def is_pure(self, atol: float = 1e-9) -> bool:
        return abs(self.purity - 1.0) < atol

    @property
    def von_neumann_entropy(self) -> float:
        """Von Neumann entropy S(rho) = -Tr(rho log rho)."""
        vals = np.linalg.eigvalsh(self.rho)
        vals = vals[vals > 1e-15]
        # Entropy is non-negative by definition; clamp to avoid serializing -0.0
        # for pure states (where -sum(1*log 1) yields negative zero).
        return max(0.0, float(-np.sum(vals * np.log(vals))))

    @property
    def bloch_vector(self) -> np.ndarray:
        rx = 2.0 * self.rho[0, 1].real
        ry = 2.0 * self.rho[0, 1].imag
        rz = float((self.rho[0, 0] - self.rho[1, 1]).real)
        return np.array([rx, ry, rz])


class QuantumCircuit:
    """Lightweight single-qubit circuit simulator."""

    def __init__(self, initial_state: Optional[QuantumState] = None) -> None:
        start = initial_state if initial_state is not None else QuantumState.ground()
        self._state: QuantumState = start
        self._history: List[QuantumState] = [start]

    @property
    def state(self) -> QuantumState:
        return self._state

    @property
    def history(self) -> List[QuantumState]:
        return list(self._history)

    def apply_unitary(self, U: np.ndarray) -> "QuantumCircuit":
        rho_new = U @ self._state.rho @ U.conj().T
        self._state = QuantumState(rho_new)
        self._history.append(self._state)
        return self

    def apply_channel(self, channel) -> "QuantumCircuit":
        rho_new = channel.apply(self._state.rho)
        self._state = QuantumState(rho_new)
        self._history.append(self._state)
        return self

    def evolve_through_background(
        self,
        bg,
        steps: int = 5,
        channel_type: str = "depolarizing",
        sensitivity: float = 0.1,
    ) -> List[QuantumState]:
        from qsot2.model.channels import MetricToChannelMap

        mapper = MetricToChannelMap(sensitivity=sensitivity)
        channel = mapper.to_channel(bg, channel_type=channel_type)

        states = [self._state]
        for _ in range(steps):
            self.apply_channel(channel)
            states.append(self._state)

        return states

    def purity_history(self) -> List[float]:
        return [s.purity for s in self._history]

    def coherence_history(self) -> List[float]:
        return [s.coherence for s in self._history]

    def reset(self, state: Optional[QuantumState] = None) -> "QuantumCircuit":
        start = state if state is not None else QuantumState.ground()
        self._state = start
        self._history = [start]
        return self
