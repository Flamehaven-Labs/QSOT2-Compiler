# QSOT2 — a mathematical-consistency verifier

[![CI](https://github.com/Flamehaven-Labs/QSOT2-Compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/Flamehaven-Labs/QSOT2-Compiler/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20763331.svg)](https://doi.org/10.5281/zenodo.20763331)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Claim scope: mathematical-consistency only](https://img.shields.io/badge/claim%20scope-mathematical--consistency%20only-orange.svg)](docs/SCOPE.md)
[![Verdict: DEGRADED_PASS (honest)](https://img.shields.io/badge/reference%20run-DEGRADED__PASS%20(34%2F0%2F0%2F1)-yellow.svg)](reports/result.json)

**QSOT** = **Quantum State Over Time**. **QSOT2** takes a *phenomenological* quantum-channel model of curved-spacetime backgrounds and answers exactly one question, deterministically and reproducibly:

> Is the model's quantum-mechanical machinery **internally consistent** — do its channels stay CPTP, its states stay valid density matrices, its temporal-state axioms hold to machine epsilon — and are the headline numbers it reports **honest about what they are**?

That is the entire deliverable. QSOT2 makes **no** claim of new physics, first-principles grounding, or external physical validation, and it does not need to — *mathematical-consistency verification is a complete claim on its own terms*. The curvature→channel mapping is an explicit ansatz with one free parameter; that is a **scope statement, not a defect** (see [`docs/SCOPE.md`](docs/SCOPE.md)).

---

## Why you might find this interesting (even if you don't care about spacetime)

QSOT2 is a small (~30 source files, NumPy-only) but complete **reference architecture for an honest verification harness**. If you build math-computing or scientific-software tooling, the parts worth reading are the patterns, not the physics:

- **Axiom checks to machine epsilon.** Five temporal-state axioms (linearity, CPTP completeness, trace preservation, conditionability, density validity) are verified as exact algebraic invariants — every reported deviation is `≤ 4.4 × 10⁻¹⁶`. This is what "the quantum mechanics holds together" looks like when you actually measure it instead of asserting it.
- **A detector that tests itself before it trusts the model.** The non-Markovianity proxy is split into a *synthetic self-test* (inject known information backflow → must register `nm = 1.41 × 10⁻⁴`) and the *model trajectory* (`nm = 0`, Markovian by construction). The harness proves its own instrument works before reporting a model number — so a `0` means "no backflow," not "broken detector."
- **A negative result that is surfaced, not buried.** The overall verdict is `DEGRADED_PASS`, on purpose: the Kirkwood-Dirac flat-baseline optimizer does **not** converge inside its fixed 50-step budget, and the run says so in the verdict, the schema, and this README. Nothing is rounded up to `PASS`.
- **A lean, machine-readable result contract.** Every run emits one JSON artifact under schema `qsot2.math_consistency.experiment_result.v1` carrying a fixed **4-field claim boundary**. The result is content-deterministic (byte-stable except for `generated_at`) and provenance is anchored to a **canonical-LF SHA-256**, so two machines agree on the hash regardless of CRLF/LF.
- **An enforced import boundary.** `src/qsot2/model/` (the math) must not import the governance/reporting layers. The separation is the point: this repo is the math core lifted out of a heavier predecessor (see [Lineage](#lineage)).

If you have ever wanted a worked example of "how do I write a verifier that is honest about exactly what a passing check means," this is meant to be that example.

---

## Quick start

```bash
git clone https://github.com/Flamehaven-Labs/QSOT2-Compiler
cd QSOT2-Compiler
pip install -e ".[dev]"          # numpy only at runtime; dev extras add pytest/ruff

python run_experiment.py --config configs/experiment.yaml --out reports
```

The runner prints a per-phase summary and ends with the verdict (exit code `0` for `PASS`/`DEGRADED_PASS`, `1` for `FAIL`):

```
Overall Verdict: DEGRADED_PASS
  Passed: 34 / Failed: 0 / Skipped: 0 / Degraded: 1
-> Generated JSON: reports/result.json
```

The single degraded check is `kd_optimization_converged` (flat baseline) — see [Known limits](#known-limits).

---

## What it computes, by phase

Six phases over six backgrounds (flat, Schwarzschild, de Sitter, AdS₅, Eguchi-Hanson, Gödel). Curvature drives a single-qubit channel through the ansatz `p = 1 − exp(−α·‖Riemann‖_F)`, and every phase emits checks into one result.

| Phase | What it does | Representative measured output |
|---|---|---|
| **0 — temporal axioms** | Verifies the 5 temporal-state axioms as algebraic invariants | all deviations `≤ 4.4e-16` (linearity `1.1e-16`, CPTP `1.6e-16`, trace `4.4e-16`, conditionability/composition/replay `0`) |
| **1 — flat baselines** | Rest-frame purity/entropy with no curvature (control) | flat purity `≈ 1.0` (no decoherence with zero curvature) |
| **2 — curvature noise** | Purity decay / entropy growth per curved background | Schwarzschild `0.99943`, de Sitter `0.63607`, AdS₅ `0.67764`, Eguchi-Hanson `0.99887` |
| **3 — relativistic boosts** | CPTP composition under Lorentz boosts (`boost_beta`) | composed-channel deviation `0` (composition stays CPTP) |
| **4 — Kirkwood-Dirac** | Basis-optimized flat-relative KD comparison | `kd_delta = +0.1230` (de Sitter − flat); flat baseline **non-converged** → `DEGRADED_PASS` |
| **5 — TTM memory proxy** | Synthetic backflow self-test vs. model trajectory | self-test `nm = 1.41e-4` (detects injected backflow); model `nm = 0` (Markovian) |

All figures above are the reference run committed in [`reports/result.json`](reports/result.json); re-running reproduces them (modulo the `generated_at` timestamp).

---

## What a passing check means — and what it does not

QSOT2 deliberately separates the claims it *verifies* from the ones it merely *runs on top of*:

| Statement | QSOT2 … |
|---|---|
| The model's channels are CPTP and its states are valid density matrices (axioms hold to machine epsilon) | **verifies** — exact algebraic invariants |
| The reported per-background purity/entropy and KD-delta are reproducible outputs of the implemented model | **verifies** — deterministic, hash-anchored |
| The non-Markovianity detector actually detects injected backflow | **verifies** — synthetic self-test, separate from the model number |
| `kd_delta` is a proof of curvature-induced quantum contextuality | **does not claim** — it is a model-relative comparative signal only |
| The curvature→channel ansatz (`α`) is derived from general relativity / first principles | **does not claim** — it is a phenomenological calibration parameter |
| Any of this is an external physical prediction or a quantum-gravity result | **does not claim** — `claim_boundary.external_physical_validation_provided = false` |

A green QSOT2 run means **model-internal mathematical consistency under stated assumptions** — nothing more, nothing less.

---

## Architecture

```
src/qsot2/
  model/      # the math: axioms, background curvature, CPTP channels, quantum ops,
              #   KD optimizer, memory kernel, beta-residual, classification, falsification
              #   (MUST NOT import core/ governance or reports/)
  core/       # the harness: config, runner, phase_context, per-phase checks,
              #   claim_boundary, results, phases/phase0..phase5
  cli/        # argparse entrypoint -> ExperimentRunner -> ReportRenderer
  reports/    # JSON / Markdown / (optional) PDF renderers
experimental/ # phase6.py + rust_sidecar — vector-search sidecar, NOT part of the verdict
```

The result schema `qsot2.math_consistency.experiment_result.v1` is intentionally lean: a `checks` map (name → `PASS`/`DEGRADED_PASS`/`FAIL`/`SKIPPED`), an `observations` block with full numerical provenance, a `summary` tally, and a **4-field** `claim_boundary`:

```json
{
  "external_physical_validation_provided": false,
  "first_principles_derivation_provided": false,
  "mathematical_consistency_scope_only": true,
  "phenomenological_model": true
}
```

No 7-class evidence taxonomy, no calibration manifest, no audit-backend surfacing — that machinery is deliberately *out of scope* and lifted to a separate line (see [Lineage](#lineage)).

---

## Reproducibility

- **Deterministic.** A re-run is byte-identical except for the `generated_at` timestamp; not faked, just disclosed.
- **Hash-anchored to canonical LF.** Provenance hashes are computed over LF-normalized bytes (the git blob), so they match across Windows/Unix checkouts regardless of working-tree line endings.
- **Tested.** 50 unit tests, 96% line coverage (`>= 90%` gate), green on CI. Run locally:

```bash
pytest -q
ruff check src tests
```

---

## Known limits

- **Not a physics result.** No external validity, no first-principles derivation, no new law. The curvature→channel map is a phenomenological ansatz.
- **KD flat-baseline non-convergence.** The Kirkwood-Dirac optimizer does not converge within its fixed 50-step budget on the flat baseline; this is the sole `DEGRADED_PASS` and is reported, not hidden.
- **`phase6` / Rust sidecar are experimental.** They live under `experimental/` and are excluded from the verdict.

---

## Lineage

QSOT2 is the **math-verification line** of a three-line program:

- **QSOT Compiler (v1)** — an intentional high-formality "slop" artifact: formal-looking, effectively non-running, scientifically hollow. The thing being corrected.
- **QSOT-Harness (v2)** — the honest reconstruction: made it run; hardened provenance, reproducibility, and result-surface honesty; added an epistemic-governance shell. Kept unchanged as the published **combined** snapshot. Public release `v2.1.2`, DOI [10.5281/zenodo.20665824](https://doi.org/10.5281/zenodo.20665824).
- **QSOT2 (this repo)** — re-scoped to the original intent: the **mathematical verification core**, cleanly separated. The governance layer is lifted to its own future line (`flamehaven-sci-governance`), leaving QSOT2 focused and legible.

Refactoring here is *meaning separation*, not a repudiation of prior work — QSOT-Harness produced real, reviewer-approved results. See [`docs/QSOT_ROADMAP.md`](docs/QSOT_ROADMAP.md) and [`docs/MIGRATION_FROM_V2.md`](docs/MIGRATION_FROM_V2.md).

---

## Status

`0.1.2` — current repository line after post-release paper/layout cleanup. The latest
DOI-bearing Zenodo release remains `0.1.1`, DOI
[10.5281/zenodo.20763331](https://doi.org/10.5281/zenodo.20763331). Migration complete
(model + Phases 0-5 ported from QSOT-Harness `src/qsot_v2/`), tests migrated (50 passing, 96%
coverage), reference run green at `DEGRADED_PASS`.

## Documentation

- [`docs/SCOPE.md`](docs/SCOPE.md) — what "mathematical-consistency only" means and why it is the whole deliverable.
- [`docs/QSOT_ROADMAP.md`](docs/QSOT_ROADMAP.md) — the three-line program and staged gates.
- [`docs/MIGRATION_FROM_V2.md`](docs/MIGRATION_FROM_V2.md) — what was ported from QSOT-Harness, what was deferred.
- [`paper/main.tex`](paper/main.tex) — companion manuscript (LaTeX).

## Citation

Preferred metadata lives in [`CITATION.cff`](CITATION.cff). The current repository line is
`0.1.2`; the latest DOI-bearing QSOT2 release remains `0.1.1`, DOI
[10.5281/zenodo.20763331](https://doi.org/10.5281/zenodo.20763331).
**Citing QSOT2 is not a substitute for citing QSOT-Harness** (DOI
[10.5281/zenodo.20665824](https://doi.org/10.5281/zenodo.20665824)) where the published
combined snapshot lives.

## License

MIT — see [LICENSE](LICENSE). [Flamehaven Labs](https://github.com/Flamehaven-Labs).
