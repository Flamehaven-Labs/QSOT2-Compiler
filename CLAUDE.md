# QSOT2 project guidance

Project-specific discipline for this repository:

## Scope discipline (the reason this repo exists)
- QSOT2 verifies **mathematical-consistency** of a phenomenological model. It does **not**
  claim new physics or first-principles grounding. Keep `alpha`/ansatz caveats as scope
  statements, not apologies.
- **No governance creep.** Evidence taxonomy, calibration manifest, scientific audit,
  accessibility scoring, and ledger integration belong to `flamehaven-sci-governance`, not
  here. Keep only a minimal claim-boundary statement in output. If a change starts growing a
  governance shell, stop and flag it.
- One-way module boundary: `model/` must not import harness/governance concerns; the harness
  may import the model.

## Code
- Python source ASCII-only in strings and comments.
- Numeric outputs are reference truth; keep them reproducible. Do not embed environment-
  dependent values (e.g. elapsed time) as expected output.
- Do not modify the published QSOT-Harness artifact (DOI 10.5281/zenodo.20703548); QSOT2 is a
  separate forward line.
