"""Phase 6: Rust turbovec."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from qsot2.core.checks import PHASE_CHECKS

if TYPE_CHECKING:
    from qsot2.core.phase_context import PhaseContext


def run_phase6(ctx: PhaseContext) -> None:
    """Execute Phase 6 checks."""
    # Prepare mock/real test vectors
    rng = np.random.default_rng(42)
    dim = 128
    n_domains = 10
    domains = rng.normal(size=(n_domains, dim)).astype(np.float32)
    domains /= np.linalg.norm(domains, axis=1, keepdims=True)
    query = rng.normal(size=dim).astype(np.float32)
    query /= np.linalg.norm(query)
    exact_sims = np.dot(domains, query).astype(np.float32).tolist()

    test_vectors = {
        "dim": dim,
        "domain_embeddings": domains.tolist(),
        "query_embedding": query.tolist(),
        "exact_similarities": exact_sims,
    }

    # Rust sidecar directory is at src/qsot2/rust_sidecar
    sidecar_dir = Path(__file__).resolve().parents[2] / "rust_sidecar"
    test_vectors_path = sidecar_dir.parent / "test_vectors.json"
    result_path = sidecar_dir.parent / "rust_verify_result.json"

    # Cleanup existing results
    if result_path.exists():
        result_path.unlink()

    # Write test vectors
    test_vectors_path.write_text(json.dumps(test_vectors, indent=2))

    # Check if Cargo is installed by running cargo check/build/run
    rust_ran_successfully = False
    rust_stdout = ""
    try:
        # Build and run Cargo
        res = subprocess.run(
            ["cargo", "run", "--release"],
            cwd=str(sidecar_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        rust_ran_successfully = True
        rust_stdout = res.stdout
    except Exception as e:
        rust_stdout = str(e)
        if hasattr(e, "stderr") and e.stderr:
            rust_stdout += "\nStderr:\n" + e.stderr
        if hasattr(e, "stdout") and e.stdout:
            rust_stdout += "\nStdout:\n" + e.stdout

    ctx.result.checks["rust_verify_binary_runs"] = "PASS" if rust_ran_successfully else "FAIL"
    ctx.result.observations["rust_verify_stdout"] = rust_stdout

    if rust_ran_successfully and result_path.exists():
        try:
            res_data = json.loads(result_path.read_text())
            ctx.result.checks["rust_turbovec_verdict_is_pass"] = (
                "PASS" if res_data["verdict"] == "PASS" else "FAIL"
            )
            ctx.result.checks["rust_turbovec_ingested_correct_count"] = (
                "PASS" if res_data["checks"]["turbovec_ingested_correct_count"] else "FAIL"
            )
            ctx.result.checks["rust_turbovec_quantization_error_within_bounds"] = (
                "PASS"
                if res_data["checks"]["turbovec_quantization_error_within_bounds"]
                else "FAIL"
            )
            ctx.result.observations["rust_turbovec_result"] = res_data
        except Exception as ex:
            ctx.result.checks["rust_turbovec_verdict_is_pass"] = "FAIL"
            ctx.result.checks["rust_turbovec_ingested_correct_count"] = "FAIL"
            ctx.result.checks["rust_turbovec_quantization_error_within_bounds"] = "FAIL"
            ctx.result.observations["rust_parse_error"] = str(ex)
    else:
        ctx.result.checks["rust_verify_binary_runs"] = "FAIL"
        ctx.result.checks["rust_turbovec_verdict_is_pass"] = "FAIL"
        ctx.result.checks["rust_turbovec_ingested_correct_count"] = "FAIL"
        ctx.result.checks["rust_turbovec_quantization_error_within_bounds"] = "FAIL"
        ctx.result.observations["rust_turbovec_note"] = (
            "Rust verification did not run or failed to generate result."
        )

    # Clean up
    if test_vectors_path.exists():
        test_vectors_path.unlink()
    if result_path.exists():
        result_path.unlink()


def skip_phase6(ctx: PhaseContext) -> None:
    """Skip Phase 6 checks."""
    for c in PHASE_CHECKS["phase6_rust_turbovec"]:
        ctx.result.checks[c] = "SKIPPED"
