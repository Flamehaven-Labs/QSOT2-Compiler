"""Minimal claim boundary for QSOT2.

This is a *scope statement*, not a governance shell. QSOT2 deliberately keeps only
these three booleans; the full epistemic-governance machinery (evidence taxonomy,
calibration manifest, audit-backend surfacing) lives in a separate library.
"""

CLAIM_BOUNDARY = {
    # No external physical validation is performed or claimed.
    "external_physical_validation_provided": False,
    # The curvature -> quantum-channel map is a phenomenological ansatz, not derived.
    "first_principles_derivation_provided": False,
    # The deliverable is internal mathematical-consistency verification only.
    "mathematical_consistency_scope_only": True,
    # The model is phenomenological.
    "phenomenological_model": True,
}
