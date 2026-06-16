# QSOT2 Paper Scaffold

This directory holds the paper line for `qsot2`.

The paper is intentionally scoped as a **mathematical-consistency note** for a
phenomenological curved-spacetime quantum-channel model. It is not a governance
paper and it is not a new-physics paper.

Design rules:

- Keep the paper single-purpose: model verification, not governance architecture.
- Put explicit non-claims in one limits section instead of repeating them everywhere.
- Keep the section order aligned with the retained verification phases.
- Treat reproducibility as important but secondary; the math-verification result is
  the paper's main subject.

Expected top-level structure:

1. scope and background
2. Phase 0 temporal axioms
3. Phases 1--3 model checks
4. Phase 4 KD relative signal
5. Phase 5 TTM-inspired memory proxy
6. consolidated results
7. limits and non-claims
8. reproducibility
9. acknowledgements

The `main.tex` file already wires this structure together.
