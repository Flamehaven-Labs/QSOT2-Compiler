# QSOT2 Scope

## One-line purpose

QSOT2 verifies the **internal mathematical consistency** of a phenomenological quantum-channel model of curved-spacetime backgrounds, and is the clean re-scoping of the original QSOT intent (catch v1's failures; check that the toy model at least holds together mathematically).

## Why "mathematical consistency" is the whole deliverable

The spacetime-curvature -> quantum-channel mapping is a **phenomenological ansatz** with a free calibration parameter (`alpha`); it is not derived from first principles, and QSOT2 makes **no quantitative physical prediction**. That is **by design, not a deficiency**: phenomenological models are a legitimate scientific mode, and the contribution here is verifying that the model's quantum mechanics is internally consistent and reproducible. The `alpha`/grounding caveats are therefore **scope statements, not apologies**.

## Is / is not

**Is**
- A bounded verifier of mathematical invariants (temporal-state axioms to machine epsilon).
- A repair of v1's execution failure and structural slop, now deterministic, tested, reproducible.
- A phenomenological-model runner whose outputs are honest about what they are.

**Is not**
- A physics proof, a new theory, or external experimental validation.
- A governance/epistemic-labeling showcase — that layer is deferred to a separate library (`flamehaven-sci-governance`).

## Governance posture (deliberately minimal)

QSOT2 keeps only a **minimal claim-boundary statement** in its output. The full epistemic-governance machinery from QSOT-Harness (7-class evidence taxonomy, calibration manifest, scientific-audit backend surfacing, accessibility scoring, ledger integration) is **out of scope** for QSOT2 and is lifted into its own line. Reason: in QSOT-Harness the governance shell grew until it obscured the verification core; QSOT2 exists to keep the two legible by separating them.

## Relationship to the published QSOT-Harness

QSOT-Harness (DOI 10.5281/zenodo.20703548) remains the immutable published **combined** snapshot. QSOT2 does not modify it. QSOT2 is a forward, re-scoped line — refactoring as *meaning separation*, not a repudiation of prior work, which produced real, reviewer-approved results.
