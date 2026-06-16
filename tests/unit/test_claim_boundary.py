"""Unit test for the minimal QSOT2 claim boundary (no governance machinery)."""

from __future__ import annotations

from qsot2.core.claim_boundary import CLAIM_BOUNDARY


def test_claim_boundary_is_minimal_four_field():
    assert CLAIM_BOUNDARY == {
        "external_physical_validation_provided": False,
        "first_principles_derivation_provided": False,
        "mathematical_consistency_scope_only": True,
        "phenomenological_model": True,
    }


def test_claim_boundary_has_no_governance_machinery():
    # The minimal header must not grow back into a governance shell.
    assert len(CLAIM_BOUNDARY) == 4
    for key in ("evidence_classes", "audit_context", "calibration", "accessibility"):
        assert key not in CLAIM_BOUNDARY
