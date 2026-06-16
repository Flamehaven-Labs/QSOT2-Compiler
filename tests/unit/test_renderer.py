"""Unit tests for the report renderer (JSON + Markdown)."""

from __future__ import annotations

import json

from qsot2.core.results import ExperimentResult
from qsot2.reports.renderer import ReportRenderer


def test_render_json_and_markdown(tmp_dir):
    result = ExperimentResult(experiment_id="render-test")
    result.checks = {"flat_rest_purity_is_1": "PASS"}
    result.observations = {"flat_rest_purities": [1.0, 1.0]}

    renderer = ReportRenderer()
    paths = renderer.render(result, tmp_dir, formats=["json", "md"])

    assert paths["json"].exists()
    assert paths["md"].exists()

    data = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert data["schema_id"] == "qsot2.math_consistency.experiment_result.v1"
    assert data["claim_boundary"]["mathematical_consistency_scope_only"] is True
    assert "evidence_classes" not in data

    md = paths["md"].read_text(encoding="utf-8")
    assert "QSOT2" in md
    # The lean report must not surface governance sections.
    for term in ("Audit Backend Context", "Calibration (free parameters)"):
        assert term not in md
