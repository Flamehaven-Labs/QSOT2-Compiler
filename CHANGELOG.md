# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-18

First tagged release of QSOT2 — the re-scoped **mathematical-consistency
verification** line of the QSOT program, cleanly separated from its predecessor
QSOT-Harness (DOI [10.5281/zenodo.20665824](https://doi.org/10.5281/zenodo.20665824)).

QSOT2 verifies the internal mathematical consistency of a phenomenological model
that maps curved-spacetime curvature norms to single-qubit quantum channels. It
is **model-consistency only**: no external-physical-validity, first-principles,
or quantum-gravity claim, and not peer-reviewed.

### Added

- Model core (`src/qsot2/model/`): temporal-state axioms, background curvature,
  CPTP channels, quantum ops, Kirkwood-Dirac optimizer, memory kernel,
  beta-residual, classification, falsification. The model layer does not import
  the governance/reporting layers (enforced import boundary).
- Verification harness (`src/qsot2/core/`): config, runner, phase context,
  per-phase checks, claim boundary, results, and Phases 0-5.
- CLI (`run_experiment.py` / `qsot2-run`) emitting a lean machine-readable
  result under schema `qsot2.math_consistency.experiment_result.v1` with a fixed
  four-field claim boundary.
- 50 unit tests, 96% line coverage (>= 90% gate), green on CI.

### Verification (reference run)

- Verdict: `DEGRADED_PASS` — 34 PASS / 0 FAIL / 0 SKIPPED / 1 DEGRADED_PASS over
  35 checks and six spacetime backgrounds (flat, Schwarzschild, de Sitter, AdS5,
  Eguchi-Hanson, Goedel).
- Temporal-state axioms hold to machine epsilon (all deviations <= 4.4e-16).
- Per-background purity: Schwarzschild 0.99943, de Sitter 0.63607, AdS5 0.67764,
  Eguchi-Hanson 0.99887.
- Kirkwood-Dirac flat-relative signal `kd_delta = +0.1230` (de Sitter minus flat).
- TTM-inspired non-Markovianity proxy: synthetic self-test `nm = 1.41e-4`
  (detects injected backflow); model trajectory `nm = 0` (Markovian by construction).
- The single degraded check is `kd_optimization_converged`: the flat-baseline KD
  optimizer does not converge within its fixed 50-step budget. Surfaced, not hidden.

### Scope / known limits

- Phenomenological ansatz `p = 1 - exp(-alpha * ||Riemann||_F)`; `alpha` is a free
  calibration parameter, not first-principles-derived.
- `experimental/` (former `phase6` + Rust sidecar) is excluded from the verdict.

### Notes

- Re-scoped from QSOT-Harness `src/qsot_v2/` with clean, separate git history;
  the epistemic-governance layer is deferred to a separate library
  (`flamehaven-sci-governance`).
- The Zenodo DOI for this release is minted on publish and added to
  `CITATION.cff` + `README.md` in a follow-up.

[0.1.0]: https://github.com/Flamehaven-Labs/QSOT2-Compiler/releases/tag/v0.1.0
