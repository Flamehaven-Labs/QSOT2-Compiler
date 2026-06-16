# Migration from QSOT-Harness (`qsot_v2`) to QSOT2

Source: the QSOT-Harness repository (`src/qsot_v2/`) at the published r1 line
(source commit `c0f6c6a`, artifact canonical-LF `1498610f`, DOI 10.5281/zenodo.20703548).

QSOT2 ports the **model + harness** layers and **defers** the governance layer. This is a
re-scoping, not a rewrite: the migrated code is the reviewer-approved r1 code, cleaned of
governance imports.

## Ports into QSOT2 (`src/qsot2/`)

**model/** (physics / math core)
- `physics/quantum.py` -> `model/quantum.py`
- `physics/channels.py` -> `model/channels.py`
- `physics/optimizer.py` -> `model/optimizer.py`  (KD; keeps the R0.1 best-objective fix)
- `physics/memory_kernel.py` -> `model/memory_kernel.py`  (TTM-inspired proxy)
- `physics/background.py`, `beta_residual.py`, `classification.py` -> `model/`
- `theory/axioms.py`, `theory/falsification.py` -> `model/`

**core/** (harness skeleton)
- `core/config.py`, `runner.py`, `results.py`, `phase_context.py`, `checks.py`
- `core/phases/phase0..phase5` (the math-verification phases)
- `cli/run_experiment.py`
- `configs/experiment.yaml`

**minimal governance kept**
- a single claim-boundary statement in the output (lightweight honesty header), derived
  from `theory/claim_boundary.py` but trimmed to the boundary booleans only.

## Deferred to `flamehaven-sci-governance` (NOT in QSOT2)

- `core/evidence.py` (7-class evidence taxonomy)
- `core/calibration.py` (calibration manifest)
- `theory/claim_boundary.py` (full machinery beyond the minimal header)
- `physics/scientific_audit.py` + `core/phases/phase7.py` (audit backend surfacing)
- `physics/accessibility.py` (heuristic compliance score)
- ledger / sanitizer (already separate: `flamehaven-audit-reports`)

Consequence: QSOT2's pipeline is the math-verification phases (no Phase 7 audit); the
result schema is leaner. Check counts will differ from QSOT-Harness's 50 — that is expected.

## Acceptance criteria for the migration

- Ported model/harness code imports **nothing** from the deferred governance modules
  (one-way boundary; verifiable by grep/AST).
- The retained mathematical checks reproduce the **same numeric values** as QSOT-Harness r1
  for the same inputs (temporal-axiom deviations at machine epsilon; KD `kd_delta` +0.1230,
  `kd_desitter` -0.0005; memory self-test nm 1.41e-4; model nm 0; purity/entropy unchanged).
- Test suite green; coverage gate retained (>=90%).

## Out of scope for QSOT2 (kept for a possible future line)

- First-principles grounding of the curvature->channel map (would be a genuine physics
  research effort, e.g. building on Pikovski et al. gravitational decoherence).
- Generalizing the harness/governance into a reusable product (that is the
  `flamehaven-sci-governance` line, where the strongest QSOT-Harness asset is elevated).
- Phase 6 (Rust `turbovec` vector-search sidecar): a non-mathematical engineering test.
  Moved to `experimental/` and removed from the required pipeline and the verdict. The
  source is retained as an optional/experimental path; it must not drive QSOT2's headline
  verdict, which is determined by the mathematical phases (0-5) only.
