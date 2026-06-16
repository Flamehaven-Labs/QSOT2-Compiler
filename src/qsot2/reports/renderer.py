"""ReportRenderer — renders ExperimentResult into JSON, Markdown, and PDF."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from qsot2.core.results import ExperimentResult

logger = logging.getLogger(__name__)


class ReportRenderer:
    """Handles rendering of experiment results to file artifacts."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).resolve().parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))

    def render(
        self, result: ExperimentResult, out_dir: Path, formats: List[str]
    ) -> Dict[str, Path]:
        """Render the result into all requested formats and save to out_dir."""
        out_dir.mkdir(parents=True, exist_ok=True)
        paths = {}

        # Always render json
        json_path = out_dir / "result.json"
        paths["json"] = self._render_json(result, json_path)

        # Render md
        md_path = out_dir / "report.md"
        if "md" in formats:
            paths["md"] = self._render_markdown(result, md_path)

        # Render pdf (requires pandoc)
        if "pdf" in formats and "md" in paths:
            pdf_path = out_dir / "report.pdf"
            pdf_res = self._render_pdf(paths["md"], pdf_path)
            if pdf_res:
                paths["pdf"] = pdf_res

        return paths

    def _render_json(self, result: ExperimentResult, path: Path) -> Path:
        data = result.to_dict()
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        logger.info("Wrote JSON report to: %s", path)
        return path

    def _render_markdown(self, result: ExperimentResult, path: Path) -> Path:
        template = self.env.get_template("experiment_report.md.j2")
        rendered = template.render(
            verdict=result.verdict,
            generated_at=result.generated_at.isoformat(),
            total=result.total,
            passed=result.passed,
            degraded=result.degraded,
            skipped=result.skipped,
            failed=result.failed,
            checks=result.checks,
        )
        path.write_text(rendered, encoding="utf-8")
        logger.info("Wrote Markdown report to: %s", path)
        return path

    def _render_pdf(self, md_path: Path, pdf_path: Path) -> Path | None:
        try:
            # Try running pandoc to convert MD to PDF
            # Pandoc uses pdflatex or weasyprint/wkhtmltopdf under the hood if specified,
            # but standard pdf engine will do.
            subprocess.run(
                ["pandoc", str(md_path), "-o", str(pdf_path)],
                check=True,
                capture_output=True,
            )
            logger.info("Wrote PDF report to: %s", pdf_path)
            return pdf_path
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            logger.warning("Pandoc PDF generation skipped: %s", e)
            return None
