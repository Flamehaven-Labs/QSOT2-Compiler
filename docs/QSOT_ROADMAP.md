# QSOT Roadmap

## Purpose of this document

This roadmap fixes the role of each QSOT line and gives QSOT2 a concrete execution plan.

It is intentionally detailed because the project has already passed through multiple
identity shifts:

- `QSOT v1` = intentional slop artifact
- `QSOT-Harness` = honest reconstruction + governance-heavy combined artifact
- `QSOT2` = mathematical-consistency core, separated from the governance shell
- `QSOT3` = future physically ambitious line, only after QSOT2 is stable

The roadmap prevents the same conceptual drift from happening again.

## The three-line program

### QSOT2

**Role:** mathematical-consistency verifier for a phenomenological curved-spacetime
quantum-channel model.

**Primary question:** does the model hold together internally as quantum mechanics
and as executable software?

**Deliberate limits:**

- no new physics claim
- no external physical validation claim
- no governance-heavy shell beyond a minimal claim boundary
- no attempt to make `alpha` physically derived

### QSOT-Harness

**Role:** published combined artifact and governance-rich verification shell.

**Primary question:** how should a scientific software artifact declare what it is,
what it is not, and how its outputs should be interpreted?

**Status:** frozen public line; not the place for major conceptual redefinition.

### QSOT3

**Role:** future physically ambitious line.

**Primary question:** can a narrowed model produce derivable, falsifiable, quantitatively
meaningful physical predictions?

**Entry condition:** QSOT2 must first be stable and legible as a math-verification core.

## Core strategic rule

Do not ask one repo to serve all three roles at once.

The failure mode to avoid is:

- model
- governance
- speculative physics ambition

all sharing one artifact and one paper.

That structure produced the identity confusion that motivated QSOT2 in the first place.

## Why QSOT2 exists

QSOT-Harness proved that the combined system can be made reproducible, provenance-aware,
and epistemically honest. But the governance shell became so heavy that it obscured the
original deliverable:

> verifying that the phenomenological QSOT model is at least mathematically consistent,
> deterministic, and reproducible.

QSOT2 exists to make that core visible again.

It is not a downgrade.
It is a separation of roles.

## Roadmap structure

The roadmap is divided into five stages:

1. identity lock
2. code migration
3. numeric parity
4. publication split
5. future bridge to QSOT3

Each stage has a success condition and a failure condition.

---

## Stage 0. Identity lock

### Goal

Prevent governance creep and speculative-physics creep before code migration expands.

### Required artifacts

- `README.md`
- `docs/SCOPE.md`
- `docs/MIGRATION_FROM_V2.md`
- `CLAUDE.md`

### Must be true

- QSOT2 is described as a **mathematical-consistency verifier**
- governance is explicitly out of scope except for a minimal claim boundary
- no sentence implies that QSOT2 is already the physically ambitious successor line
- no sentence implies that QSOT2 replaces or republishes QSOT-Harness

### Success condition

A new reader can answer, in one sentence, what QSOT2 is:

> a bounded verifier of the internal mathematical consistency of a phenomenological
> quantum-channel model.

### Failure condition

If the README starts sounding like:

- "new physics"
- "governance platform"
- "production scientific audit framework"

then Stage 0 failed.

---

## Stage 1. Code migration into a clean two-layer structure

### Goal

Port the model + harness skeleton from QSOT-Harness into QSOT2 while leaving governance
behind.

### Target structure

```text
src/qsot2/
  model/
    quantum.py
    channels.py
    optimizer.py
    memory_kernel.py
    background.py
    beta_residual.py
    classification.py
    axioms.py
    falsification.py

  core/
    config.py
    results.py
    runner.py
    phase_context.py
    checks.py
    claim_boundary.py
    phases/
      phase0.py
      phase1.py
      phase2.py
      phase3.py
      phase4.py
      phase5.py

  cli/
    run_experiment.py

  reports/
    renderer.py
    templates/
```

### Explicitly excluded from QSOT2

Do not port:

- full evidence taxonomy
- calibration manifest machinery
- scientific audit backend adapter
- accessibility scoring
- phase7 audit layer
- phase6 Rust sidecar in the *required* pipeline (kept under `experimental/`, excluded from the verdict)
- ledger integration

### Import rule

`model/` must not import governance-style code.

In practice:

- no `scientific_audit`
- no `evidence`
- no `calibration`
- no `accessibility`

### Success condition

- import graph is one-way and clean
- `model/` is legible as the actual math/physics core
- `core/` is only the execution skeleton

### Failure condition

If a reviewer cannot tell where the model ends and the shell begins by just opening
`src/qsot2/`, Stage 1 failed.

---

## Stage 2. Numeric parity with QSOT-Harness r1

### Goal

Prove that QSOT2 is a clean re-scoping, not a silent behavioral rewrite.

### Reference line

QSOT-Harness published hardened line:

- source commit: `c0f6c6a`
- public release line: `v2.1.2` / DOI `10.5281/zenodo.20703548`
- reference artifact family rooted in canonical `result.json`

### Required parity checks

For the same config and environment, QSOT2 should reproduce the retained
math-verification numerics:

- temporal-axiom deviations at machine epsilon
- `kd_flat`
- `kd_desitter`
- `kd_delta`
- `memory_kernel.nm_measure`
- `memory_kernel_model_trajectory.nm_measure`
- background purity/entropy values for the retained phases
- Rust sidecar pass/fail if Phase 6 is retained unchanged

### Known intended differences

QSOT2 is allowed to differ in:

- absence of Phase 7
- absence of governance-heavy schema blocks
- total check count
- absence of audit-context surfaces

### Success condition

The retained math engine produces numerically matching results where the model path is
unchanged, while the schema becomes leaner by design.

### Failure condition

If numbers change without an intentional mathematical reason, Stage 2 failed.

---

## Stage 3. Lean schema design

### Goal

Give QSOT2 a result format that is lighter than QSOT-Harness but still honest.

### Minimum output contract

QSOT2 output should include:

- `schema_id`
- `generated_at`
- minimal `claim_boundary`
- `summary`
- `checks`
- `observations`

### Minimal claim boundary

QSOT2 should keep a reduced claim-boundary header such as:

- `external_physical_validation_provided = false`
- `first_principles_derivation_provided = false`
- `mathematical_consistency_scope_only = true`
- `phenomenological_model = true`

This is not governance creep.
It is the minimum honesty header.

### Deliberately absent from QSOT2 schema

- evidence classes
- calibration manifest
- audit context
- backend mode surfacing
- ledger-centric metadata

### Success condition

The result format is simple enough to read as a model-verification artifact, not a
governance protocol transcript.

### Failure condition

If the JSON starts re-growing governance-heavy wrappers until the model becomes visually
secondary again, Stage 3 failed.

---

## Stage 4. Testing and reproducibility contract

### Goal

Keep the rigor of QSOT-Harness without dragging the whole governance apparatus into QSOT2.

### Required test posture

- pytest green
- coverage gate retained (`>= 90%`)
- line-ending discipline preserved (`.gitattributes`)
- deterministic or bounded-deterministic outputs where claimed

### Required documentation

Document:

- exact command to run the experiment
- exact command to run tests
- which retained results should match QSOT-Harness numerically
- which omitted governance outputs are intentionally absent

### Success condition

A reviewer can reproduce QSOT2 as a software artifact without needing ledger or audit
infrastructure.

### Failure condition

If reproducibility in practice still depends on hidden QSOT-Harness governance pieces,
Stage 4 failed.

---

## Stage 5. Publication split

### Goal

Separate the papers that were previously entangled.

### Paper A: QSOT2 note

Working title shape:

> A Mathematical-Consistency Verifier for a Phenomenological Curved-Spacetime
> Quantum-Channel Model

This paper should foreground:

- temporal-state axiom checks
- CPTP/trace/linearity consistency
- KD as bounded flat-relative comparison
- TTM-inspired proxy as a limited diagnostic
- reproducibility

This paper should not foreground:

- governance taxonomy
- backend mode machinery
- ledger architecture

### Paper B: governance paper

This belongs to the separate governance line, not QSOT2 proper.

Its subject is:

- machine-readable epistemic labeling
- claim boundary enforcement
- calibration manifest design
- backend surfacing
- ledger + sanitizer workflow

### Success condition

Each paper has one audience and one principal claim.

### Failure condition

If the QSOT2 paper again spends more time defending what it does not claim than
stating what it does claim, Stage 5 failed.

---

## Stage 6. Bridge to QSOT3

### Goal

Use QSOT2 as the stable launch pad for a more physically ambitious line, without
smuggling that ambition back into QSOT2.

### QSOT3 entry criteria

QSOT3 should only begin once all of the following are true:

1. QSOT2 is stable as a mathematical-consistency verifier
2. the governance shell has a separate home
3. the physical program is narrowed to one model, not a background zoo

### QSOT3 minimum bar

QSOT3 should aim to add what QSOT2 intentionally does not:

- stronger physical motivation or derivation path
- reduced free-parameter arbitrariness
- baseline-comparison experiments
- at least one falsifiable quantitative prediction

### Important rule

Do not sneak QSOT3 requirements into QSOT2.

QSOT2's role is to stabilize the mathematical core.
QSOT3's role is to attempt stronger physical meaning.

---

## Concrete execution order

### Step 1

Finish code migration and import cleanup.

### Step 2

Run parity tests against retained QSOT-Harness math outputs.

### Step 3

Freeze QSOT2's lean schema.

### Step 4

Write the QSOT2 note as a math-verification paper, not a governance paper.

### Step 5

Only after QSOT2 stabilizes, begin formal extraction of governance into its own line.

### Step 6

Only after Step 5, open QSOT3 as a separate physically ambitious program.

---

## Non-goals

QSOT2 is not trying to:

- rescue physical significance by rhetoric
- outgrow QSOT-Harness by adding more governance layers
- publish a stronger-physics claim without a stronger-physics model
- become a combined everything-repo again

---

## Final success criterion

This roadmap succeeds when all three of the following become simultaneously true:

1. `QSOT2` is legible as a standalone mathematical-consistency verifier.
2. `QSOT-Harness` remains a stable published combined artifact rather than a moving target.
3. `QSOT3`, when opened, can pursue physical significance without dragging governance
   and model-legibility problems back into the same repo.
