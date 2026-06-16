# QSOT2

[![CI](https://github.com/Flamehaven-Labs/QSOT2-Compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/Flamehaven-Labs/QSOT2-Compiler/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Claim scope: mathematical-consistency only](https://img.shields.io/badge/claim%20scope-mathematical--consistency%20only-orange.svg)](docs/SCOPE.md)

**QSOT** stands for **Quantum State Over Time**. **QSOT2** is a bounded **mathematical-consistency verifier** for a *phenomenological* quantum-channel model of curved-spacetime backgrounds. It checks that the model's quantum-mechanical machinery is **internally consistent and reproducible** — and nothing more. It does **not** claim new physics, first-principles grounding, or external physical validation, and it does not need to: the deliverable is *mathematical-consistency verification*, which is sufficient on its own terms.

## Lineage

- **QSOT Compiler (v1)** — an intentional high-formality "slop" artifact: formal-looking, effectively non-running, scientifically hollow.
- **QSOT-Harness (v2, published, DOI [10.5281/zenodo.20703548](https://doi.org/10.5281/zenodo.20703548))** — the honest reconstruction: made it run; hardened provenance, reproducibility, and result-surface honesty; and added an epistemic-governance shell. Kept, unchanged, as the published **combined** snapshot.
- **QSOT2 (this repo)** — re-scopes to the original intent: the **mathematical verification core**, cleanly separated. The heavy governance layer is lifted out to its own future line (`flamehaven-sci-governance`), leaving QSOT2 focused and legible.

## What this is / is not

- **Is:** a working, tested verifier of the *internal mathematical consistency* of a phenomenological spacetime-to-quantum-channel model — temporal-state axioms checked to machine epsilon (linearity, CPTP completeness, trace preservation, conditionability, density validity), CPTP channel construction, a flat-relative Kirkwood-Dirac comparison, and a TTM-inspired memory proxy — plus the repair of v1's execution and structural failures.
- **Is not:** a physics proof, a Theory of Everything, a new physical law, or a governance demonstration. A passing check means *model-internal mathematical consistency under stated assumptions* — nothing more.

## Status

Initial migration complete. The model + math-verification harness (Phases 0-5) is ported from QSOT-Harness `src/qsot_v2/`; the governance machinery is deferred, and the Rust vector-search sidecar (former Phase 6) is kept under `experimental/` and is **not** part of the verdict. A reference run yields `DEGRADED_PASS` over 35 checks — the only degraded check is the Kirkwood-Dirac optimizer's fixed-budget non-convergence, surfaced honestly. Test migration is the next step. See [`docs/MIGRATION_FROM_V2.md`](docs/MIGRATION_FROM_V2.md) and [`docs/SCOPE.md`](docs/SCOPE.md).
