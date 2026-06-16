"""ExperimentResult and CheckStatus types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal

CheckStatus = Literal["PASS", "FAIL", "SKIPPED", "DEGRADED_PASS"]
Verdict = Literal["PASS", "FAIL", "DEGRADED_PASS"]


@dataclass
class ExperimentResult:
    """Full result of one experiment run."""

    experiment_id: str
    schema_id: str = "qsot2.math_consistency.experiment_result.v1"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # check_id -> status
    checks: Dict[str, CheckStatus] = field(default_factory=dict)
    # check_id -> arbitrary observation data
    observations: Dict[str, Any] = field(default_factory=dict)
    _verdict: Verdict | None = field(default=None, repr=False)

    @property
    def verdict(self) -> Verdict:
        """Compute verdict from check statuses.

        Rules (in priority order):
          FAIL:          any check is FAIL, or any *required* check is SKIPPED
          DEGRADED_PASS: any check is DEGRADED_PASS, or any optional check is SKIPPED
          PASS:          all required checks are PASS
        """
        if self._verdict is not None:
            return self._verdict
        return self._compute_verdict()

    def set_verdict(self, v: Verdict) -> None:
        self._verdict = v

    def _compute_verdict(self) -> Verdict:
        statuses = list(self.checks.values())
        if "FAIL" in statuses:
            return "FAIL"
        if "DEGRADED_PASS" in statuses or "SKIPPED" in statuses:
            return "DEGRADED_PASS"
        return "PASS"

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def passed(self) -> int:
        return sum(1 for s in self.checks.values() if s == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for s in self.checks.values() if s == "FAIL")

    @property
    def skipped(self) -> int:
        return sum(1 for s in self.checks.values() if s == "SKIPPED")

    @property
    def degraded(self) -> int:
        return sum(1 for s in self.checks.values() if s == "DEGRADED_PASS")

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        from qsot2.core.claim_boundary import CLAIM_BOUNDARY

        return {
            "schema_id": self.schema_id,
            "experiment_id": self.experiment_id,
            "generated_at": self.generated_at.isoformat(),
            "verdict": self.verdict,
            "claim_boundary": CLAIM_BOUNDARY,
            "summary": {
                "total": self.total,
                "pass": self.passed,
                "fail": self.failed,
                "skipped": self.skipped,
                "degraded_pass": self.degraded,
            },
            "checks": self.checks,
            "observations": _sanitize(self.observations),
        }


def _sanitize(obj: Any) -> Any:
    """Recursively convert numpy types to Python natives for JSON serialization."""
    try:
        import numpy as np

        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    return obj
