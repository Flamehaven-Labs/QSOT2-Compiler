"""CLI entrypoint for running QSOT V2 experiments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from qsot2.core.checks import PHASE_CHECKS
from qsot2.core.config import PHASE_IDS, ExperimentConfig
from qsot2.core.runner import ExperimentRunner
from qsot2.reports.renderer import ReportRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QSOT Compiler V2 — CLI-First Experiment Runner & Report Generator"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/experiment.yaml",
        help="Path to the experiment.yaml configuration file",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Override the output directory specified in the config",
    )
    parser.add_argument(
        "--format",
        type=str,
        nargs="+",
        default=None,
        choices=["json", "md", "pdf"],
        help="Override the output formats (json, md, pdf)",
    )
    parser.add_argument(
        "--phases",
        type=str,
        nargs="+",
        default=None,
        choices=list(PHASE_IDS),
        help="Specific phases to run (overrides the config)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}", file=sys.stderr)
        return 1

    try:
        config = ExperimentConfig.from_yaml(config_path)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return 1

    # Overrides
    if args.out:
        config.output.dir = args.out
    if args.format:
        config.output.formats = args.format
    if args.phases:
        # Disable all phases not explicitly chosen
        for phase in config.phases:
            phase.enabled = phase.id in args.phases

    print("=" * 70)
    print(f"Starting Experiment: {config.experiment_id} (v{config.version})")
    print(f"Description: {config.description}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Enabled Phases: {', '.join(config.enabled_phases)}")
    print("=" * 70)

    # Initialize and run
    runner = ExperimentRunner(config)
    result = runner.run()

    # Render reports
    renderer = ReportRenderer()
    paths = renderer.render(result, config.output_dir, config.output.formats)

    # Print summary output to console
    print("\n" + "=" * 70)
    print("Execution Summary:")
    print("-" * 70)

    # Phase group reporting using central registry
    total_phases = len(PHASE_CHECKS)
    for idx, (phase_id, checks) in enumerate(PHASE_CHECKS.items(), 1):
        phase_num = idx - 1
        if phase_id in config.enabled_phases:
            # Count status
            phase_statuses = [result.checks.get(c, "SKIPPED") for c in checks]
            n_pass = sum(1 for s in phase_statuses if s == "PASS")
            n_fail = sum(1 for s in phase_statuses if s == "FAIL")
            n_skipped = sum(1 for s in phase_statuses if s == "SKIPPED")
            n_degraded = sum(1 for s in phase_statuses if s == "DEGRADED_PASS")

            status_str = "PASS"
            if n_fail > 0:
                status_str = "FAIL"
            elif n_degraded > 0:
                status_str = "DEGRADED_PASS"
            elif n_skipped == len(checks):
                status_str = "SKIPPED"

            phase_title = phase_id.split("_", 1)[1].replace("_", " ").title()
            print(
                f"[{idx}/{total_phases}] Phase {phase_num}: {phase_title} ... {status_str} (PASS: {n_pass}/{len(checks)})"
            )
        else:
            phase_title = phase_id.split("_", 1)[1].replace("_", " ").title()
            print(f"[{idx}/{total_phases}] Phase {phase_num}: {phase_title} ... SKIPPED")

    print("-" * 70)
    print(f"✓ Overall Verdict: {result.verdict}")
    print(
        f"  Passed: {result.passed} / Failed: {result.failed} / Skipped: {result.skipped} / Degraded: {result.degraded}"
    )
    print("-" * 70)
    for fmt, path in paths.items():
        print(f"→ Generated {fmt.upper()}: {path}")
    print("=" * 70)

    # Return 0 for PASS/DEGRADED_PASS, 1 for FAIL
    return 0 if result.verdict in ["PASS", "DEGRADED_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
