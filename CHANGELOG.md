# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-06-19

### Changed

- Promoted the repository line to `0.1.2` to separate the current working surface from the
  DOI-bearing `0.1.1` publication snapshot.
- Rewrote the paper's reproducibility surface around an artifact traceability table with
  DOI anchor, schema IDs, and canonical-LF SHA-256 hashes.
- Strengthened the paper bibliography/front matter: abstract restored, references added,
  and section-level citations inserted for open quantum systems, Kirkwood--Dirac, the
  TTM source method, and the QSOT-Harness predecessor.
- Tightened the paper PDF layout for the traceability table and added an explicit
  disclaimer for legacy governance-like field names retained in serialized artifacts for
  backward compatibility only.
- Updated the tracked `paper/main.pdf` to match the latest paper source.

### Notes

- `0.1.2` is the current repository line.
- The latest DOI-bearing QSOT2 release remains `0.1.1`,
  DOI [10.5281/zenodo.20763331](https://doi.org/10.5281/zenodo.20763331).

## [0.1.1] - 2026-06-19

### Changed

- Final paper wording aligned with the frozen code/artifact surface.
- QSOT2 paper table labels clarified background ordering and unified `AdS5` notation.
- The alpha-sweep interpretation now foregrounds the non-robustness warning before the
  numeric sequence.
- Acknowledgements wording trimmed to remove defensive institutional language.

### Notes

- Published as the Zenodo-backed QSOT2 release:
  DOI [10.5281/zenodo.20763331](https://doi.org/10.5281/zenodo.20763331).

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
- Zenodo DOI: [10.5281/zenodo.20742042](https://doi.org/10.5281/zenodo.20742042).

[0.1.0]: https://github.com/Flamehaven-Labs/QSOT2-Compiler/releases/tag/v0.1.0
[0.1.1]: https://github.com/Flamehaven-Labs/QSOT2-Compiler/releases/tag/v0.1.1
[0.1.2]: https://github.com/Flamehaven-Labs/QSOT2-Compiler/compare/v0.1.1...main
