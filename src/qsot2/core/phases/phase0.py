"""Phase 0: Temporal-State Axioms verifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qsot2.core.checks import PHASE_CHECKS
from qsot2.model.falsification import run_phase0_checks

if TYPE_CHECKING:
    from qsot2.core.phase_context import PhaseContext


def run_phase0(ctx: PhaseContext) -> None:
    """Execute Phase 0 checks."""
    res = run_phase0_checks(ctx.config.sensitivity, ctx.config.boost_beta)
    ctx.result.checks.update(res["checks"])
    ctx.result.observations.update(res["observations"])


def skip_phase0(ctx: PhaseContext) -> None:
    """Skip Phase 0 checks."""
    for c in PHASE_CHECKS["phase0_temporal_axioms"]:
        ctx.result.checks[c] = "SKIPPED"
