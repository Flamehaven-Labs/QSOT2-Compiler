"""Smoke test for the CLI entrypoint."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from qsot2.cli.run_experiment import main

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "experiment.yaml"


def test_cli_main_generates_artifacts(tmp_dir, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_experiment", "--config", str(CONFIG_PATH), "--out", str(tmp_dir), "--format", "json"],
    )
    rc = main()
    assert rc == 0  # DEGRADED_PASS -> exit 0
    result_path = tmp_dir / "result.json"
    assert result_path.exists()
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert data["schema_id"] == "qsot2.math_consistency.experiment_result.v1"
    assert data["verdict"] == "DEGRADED_PASS"


def test_cli_missing_config(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run_experiment", "--config", "does_not_exist.yaml"])
    assert main() == 1
