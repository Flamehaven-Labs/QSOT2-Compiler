"""Unit tests for quantum primitives and channel construction."""

from __future__ import annotations

import numpy as np
import pytest

from qsot2.model import (
    BackgroundField,
    KrausChannel,
    MetricToChannelMap,
    QuantumCircuit,
    QuantumState,
)


def test_quantum_state():
    state = QuantumState.ground()
    assert state.purity == 1.0
    assert state.coherence == 0.0
    assert state.is_pure()
    assert state.von_neumann_entropy == 0.0
    assert np.allclose(state.bloch_vector, [0.0, 0.0, 1.0])

    excited = QuantumState.excited()
    assert excited.purity == 1.0
    assert excited.coherence == 0.0
    assert excited.von_neumann_entropy == 0.0
    assert np.allclose(excited.bloch_vector, [0.0, 0.0, -1.0])

    mixed = QuantumState.maximally_mixed()
    assert mixed.purity == 0.5
    assert mixed.coherence == 0.0
    assert abs(mixed.von_neumann_entropy - np.log(2.0)) < 1e-12

    superpos = QuantumState.from_bloch(np.pi / 2, 0.0)
    assert superpos.purity == pytest.approx(1.0)
    assert abs(superpos.coherence - 0.5) < 1e-12
    assert superpos.von_neumann_entropy < 1e-12
    assert np.allclose(superpos.bloch_vector, [1.0, 0.0, 0.0], atol=1e-7)

    with pytest.raises(ValueError):
        QuantumState(np.zeros((3, 3)))


def test_kraus_channel(flat_background):
    mapper = MetricToChannelMap(sensitivity=0.1)
    ch = mapper.to_channel(flat_background)
    assert ch.completeness_error < 1e-12
    assert ch.dim == 2

    ch_id = KrausChannel.identity()
    assert ch_id.completeness_error < 1e-12
    rho = QuantumState.ground().rho
    assert np.allclose(ch_id.apply(rho), rho)


def test_metric_to_channel_map():
    with pytest.raises(ValueError):
        MetricToChannelMap(sensitivity=0.0)
    with pytest.raises(ValueError):
        MetricToChannelMap(channel_type="invalid")

    mapper_depol = MetricToChannelMap(sensitivity=0.1, channel_type="depolarizing")
    mapper_deph = MetricToChannelMap(sensitivity=0.1, channel_type="dephasing")

    sch = BackgroundField(name="schwarz", G=np.diag([-1.0, 1.0]), ricci_matrix=np.eye(2) * 0.1)
    ch_depol = mapper_depol.to_channel(sch)
    ch_deph = mapper_deph.to_channel(sch)
    assert ch_depol.channel_type == "depolarizing"
    assert ch_deph.channel_type == "dephasing"
    assert ch_depol.p > 0.0
    assert ch_deph.p > 0.0


def test_gravitational_decoherence():
    mapper = MetricToChannelMap(sensitivity=0.1)
    bg = BackgroundField(name="test", G=np.diag([-0.5, 1.0]), ricci_matrix=np.eye(2) * 0.1)

    res_rest = mapper.gravitational_decoherence(bg, observer_velocity=0.0)
    assert res_rest["gamma_gravitational"] == pytest.approx(np.sqrt(2.0))
    assert res_rest["gamma_boost"] == 1.0
    assert res_rest["gamma_total"] == pytest.approx(np.sqrt(2.0))

    res_boost = mapper.gravitational_decoherence(bg, observer_velocity=0.5)
    assert res_boost["gamma_boost"] == pytest.approx(1.0 / np.sqrt(0.75))
    assert res_boost["gamma_total"] > res_rest["gamma_total"]
    assert res_boost["p_effective"] > res_rest["p_effective"]

    with pytest.raises(ValueError):
        mapper.gravitational_decoherence(bg, observer_velocity=-0.1)
    with pytest.raises(ValueError):
        mapper.gravitational_decoherence(bg, observer_velocity=1.0)


def test_quantum_circuit(flat_background):
    circuit = QuantumCircuit()
    assert circuit.state.is_pure()
    assert len(circuit.history) == 1

    mapper = MetricToChannelMap(sensitivity=0.1)
    ch = mapper.to_channel(flat_background)
    circuit.apply_channel(ch)
    assert len(circuit.history) == 2

    circuit.reset()
    assert len(circuit.history) == 1

    U = np.array([[0, 1], [1, 0]], dtype=complex)
    circuit.apply_unitary(U)
    assert np.allclose(circuit.state.rho, QuantumState.excited().rho)
    assert len(circuit.purity_history()) == 2
    assert len(circuit.coherence_history()) == 2
