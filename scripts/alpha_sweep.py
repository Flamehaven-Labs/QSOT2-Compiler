"""Reproducible alpha (sensitivity) sweep for the flat-relative KD signal.

Runs the QSOT2 pipeline at several alpha values and records the flat-relative
Kirkwood-Dirac delta. The flat baseline is curvature-free (Riemann norm zero),
so its channel is the identity for every alpha and its KD value is
alpha-independent; only the de Sitter branch responds to alpha. As de Sitter
decoheres toward the maximally mixed state its KD optimum approaches zero, so
the reported delta saturates toward the magnitude of the (fixed) flat KD value.

This script does NOT call the report renderer, so the frozen reference artifact
reports/result.json is never overwritten. Output: reports/sweep_alpha.json.

Run: python scripts/alpha_sweep.py  (PyTorch required for the KD optimizer).
"""

from __future__ import annotations

import json
from pathlib import Path

from qsot2.core.config import ExperimentConfig
from qsot2.core.runner import ExperimentRunner
from qsot2.core.phases.phase4 import KD_OPTIMIZATION_STEPS

ALPHAS = [0.01, 0.1, 1.0]
CONFIG_PATH = Path("configs/experiment.yaml")
OUT_PATH = Path("reports/sweep_alpha.json")


def main() -> int:
    rows = []
    for alpha in ALPHAS:
        config = ExperimentConfig.from_yaml(CONFIG_PATH)
        config.sensitivity = alpha
        # Phase 4 builds and evolves de Sitter itself and falls back to the ground
        # state for the flat branch; the flat channel is the identity, so enabling
        # only Phase 4 reproduces the same kd_flat / kd_desitter as the full run.
        for phase in config.phases:
            phase.enabled = phase.id == "phase4_kd_governance"
        result = ExperimentRunner(config).run()
        kd = result.observations["kd_delta"]
        rows.append(
            {
                "alpha": alpha,
                "kd_flat": kd["kd_flat"],
                "kd_desitter": kd["kd_desitter"],
                "kd_delta": kd["value"],
                "flat_converged": kd["flat_converged"],
                "desitter_converged": kd["desitter_converged"],
            }
        )
        print(f"alpha={alpha}: kd_delta={kd['value']:.6f} (flat={kd['kd_flat']:.6f}, dS={kd['kd_desitter']:.6f})")

    out = {
        "schema_id": "qsot2.math_consistency.alpha_sweep.v1",
        "description": (
            "Flat-relative KD delta across an alpha sweep. The flat baseline is "
            "alpha-independent (zero curvature -> identity channel); de Sitter "
            "decoheres with alpha, so kd_delta saturates toward |kd_flat|."
        ),
        "kd_optimization_steps": KD_OPTIMIZATION_STEPS,
        "backgrounds": ["flat", "de_sitter"],
        "sweep": rows,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"-> wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
