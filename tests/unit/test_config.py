"""Unit tests for ExperimentConfig class."""

from __future__ import annotations

from pathlib import Path

import pytest

from qsot2.core.config import ExperimentConfig, OutputConfig


def test_valid_config(sample_config):
    assert sample_config.experiment_id == "test-exp-01"
    assert sample_config.enabled_phases == [
        "phase0_temporal_axioms",
        "phase1_flat_baselines",
        "phase2_curvature_noise",
    ]
    assert sample_config.output_dir == Path("reports")


def test_invalid_background():
    with pytest.raises(ValueError, match="Unknown backgrounds"):
        ExperimentConfig(
            experiment_id="test",
            version="1.0",
            description="",
            backgrounds=["invalid_bg"],
            sensitivity=0.1,
            boost_beta=0.5,
            steps=3,
            phases=[],
            output=OutputConfig(),
        )


def test_invalid_sensitivity():
    with pytest.raises(ValueError, match="sensitivity must be in"):
        ExperimentConfig(
            experiment_id="test",
            version="1.0",
            description="",
            backgrounds=["flat"],
            sensitivity=0.0,
            boost_beta=0.5,
            steps=3,
            phases=[],
            output=OutputConfig(),
        )


def test_invalid_boost_beta():
    with pytest.raises(ValueError, match="boost_beta must be in"):
        ExperimentConfig(
            experiment_id="test",
            version="1.0",
            description="",
            backgrounds=["flat"],
            sensitivity=0.1,
            boost_beta=1.0,
            steps=3,
            phases=[],
            output=OutputConfig(),
        )


def test_invalid_steps():
    with pytest.raises(ValueError, match="steps must be"):
        ExperimentConfig(
            experiment_id="test",
            version="1.0",
            description="",
            backgrounds=["flat"],
            sensitivity=0.1,
            boost_beta=0.5,
            steps=0,
            phases=[],
            output=OutputConfig(),
        )


def test_invalid_output_format():
    with pytest.raises(ValueError, match="Unknown output formats"):
        ExperimentConfig(
            experiment_id="test",
            version="1.0",
            description="",
            backgrounds=["flat"],
            sensitivity=0.1,
            boost_beta=0.5,
            steps=3,
            phases=[],
            output=OutputConfig(formats=["invalid"]),
        )


def test_from_yaml(tmp_dir):
    yaml_content = """
experiment_id: test-yaml
version: "1.5"
description: "Yaml description"
backgrounds:
  - flat
sensitivity: 0.5
boost_beta: 0.1
steps: 5
phases:
  - id: phase1_flat_baselines
    enabled: true
  - id: phase2_curvature_noise
    enabled: false
output:
  formats:
    - json
  dir: custom_out
"""
    config_file = tmp_dir / "experiment.yaml"
    config_file.write_text(yaml_content)

    config = ExperimentConfig.from_yaml(config_file)
    assert config.experiment_id == "test-yaml"
    assert config.version == "1.5"
    assert config.sensitivity == 0.5
    assert config.enabled_phases == ["phase1_flat_baselines"]
    assert config.output.formats == ["json"]
    assert config.output_dir == Path("custom_out")


def test_from_yaml_defaults(tmp_dir):
    yaml_content = """
experiment_id: test-defaults
"""
    config_file = tmp_dir / "experiment.yaml"
    config_file.write_text(yaml_content)

    config = ExperimentConfig.from_yaml(config_file)
    assert config.experiment_id == "test-defaults"
    assert "phase1_flat_baselines" in config.enabled_phases
    assert config.output.formats == ["json", "md"]
