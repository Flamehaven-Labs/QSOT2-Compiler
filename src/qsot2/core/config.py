"""ExperimentConfig: loads and validates experiment.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml

BACKGROUND_OPTIONS = frozenset(
    {
        "flat",
        "schwarzschild",
        "de_sitter",
        "ads5",
        "eguchi_hanson",
        "godel_universe",
    }
)

PHASE_IDS = (
    "phase0_temporal_axioms",
    "phase1_flat_baselines",
    "phase2_curvature_noise",
    "phase3_boosts",
    "phase4_kd_governance",
    "phase5_ttm_accessibility",
)


@dataclass
class PhaseConfig:
    id: str
    enabled: bool = True


@dataclass
class OutputConfig:
    formats: List[str] = field(default_factory=lambda: ["json", "md"])
    dir: str = "reports"


@dataclass
class ExperimentConfig:
    """Validated configuration loaded from experiment.yaml."""

    experiment_id: str
    version: str
    description: str
    backgrounds: List[str]
    sensitivity: float  # alpha — free calibration parameter, not derived
    boost_beta: float
    steps: int
    phases: List[PhaseConfig]
    output: OutputConfig

    def __post_init__(self) -> None:
        # Validate backgrounds
        unknown = set(self.backgrounds) - BACKGROUND_OPTIONS
        if unknown:
            raise ValueError(f"Unknown backgrounds: {unknown}. Valid: {BACKGROUND_OPTIONS}")

        # Validate sensitivity
        if not (0.0 < self.sensitivity <= 100.0):
            raise ValueError(f"sensitivity must be in (0, 100], got {self.sensitivity}")

        # Validate boost_beta
        if not (0.0 <= self.boost_beta < 1.0):
            raise ValueError(f"boost_beta must be in [0, 1), got {self.boost_beta}")

        # Validate steps
        if self.steps < 1:
            raise ValueError(f"steps must be >= 1, got {self.steps}")

        # Validate output formats
        valid_formats = {"json", "md", "pdf"}
        bad = set(self.output.formats) - valid_formats
        if bad:
            raise ValueError(f"Unknown output formats: {bad}. Valid: {valid_formats}")

    @property
    def enabled_phases(self) -> List[str]:
        return [p.id for p in self.phases if p.enabled]

    @property
    def output_dir(self) -> Path:
        return Path(self.output.dir)

    @classmethod
    def from_yaml(cls, path: Path) -> "ExperimentConfig":
        """Load and validate from a YAML file."""
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))

        # Parse phases
        phases_raw = raw.get("phases", [])
        if not phases_raw:
            # Default: all phases enabled
            phases = [PhaseConfig(id=pid) for pid in PHASE_IDS]
        else:
            phases = [
                PhaseConfig(
                    id=p["id"],
                    enabled=p.get("enabled", True),
                )
                for p in phases_raw
            ]

        # Parse output
        out_raw = raw.get("output", {})
        output = OutputConfig(
            formats=out_raw.get("formats", ["json", "md"]),
            dir=out_raw.get("dir", "reports"),
        )

        return cls(
            experiment_id=raw["experiment_id"],
            version=str(raw.get("version", "1.0")),
            description=raw.get("description", ""),
            backgrounds=raw.get("backgrounds", ["flat"]),
            sensitivity=float(raw.get("sensitivity", 0.1)),
            boost_beta=float(raw.get("boost_beta", 0.5)),
            steps=int(raw.get("steps", 3)),
            phases=phases,
            output=output,
        )
