"""
Analysis Runner - Auto-execute analysis scripts after test completion

This module provides utilities for automatically running analysis scripts
on test data, with the ability to skip analysis during development for
faster iteration.

Usage:
    from analysis_runner import run_analysis, should_skip_analysis

    # At end of test
    if not should_skip_analysis():
        run_analysis("analyze_cole_cole.py", results_file)

Environment Variables:
    SKIP_ANALYSIS=1  - Skip all analysis (default: run analysis)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def should_skip_analysis() -> bool:
    """
    Check if analysis should be skipped based on environment variable.

    Returns:
        bool: True if SKIP_ANALYSIS=1, False otherwise

    Examples:
        SKIP_ANALYSIS=1 pytest test.py  # Skips analysis
        pytest test.py                   # Runs analysis (default)
    """
    return os.environ.get('SKIP_ANALYSIS', '0') == '1'


def run_analysis(script_name: str,
                 jsonl_file: Path,
                 timeout: int = 300,
                 analysis_dir: Optional[Path] = None) -> bool:
    """
    Run analysis script on JSONL data file.

    Args:
        script_name: Name of analysis script in tests/analysis/
                    (e.g., "analyze_cole_cole.py")
        jsonl_file: Path to JSONL data file to analyze
        timeout: Maximum seconds to wait for analysis (default 300 = 5 min)
        analysis_dir: Optional override for analysis script directory
                     (default: tests/analysis/)

    Returns:
        bool: True if analysis succeeded, False if failed or skipped

    Examples:
        run_analysis("analyze_cole_cole.py",
                    Path("~/sensor-test-data/data/calib/test_007.jsonl"))

        run_analysis("analyze_ecg.py", ecg_file, timeout=600)
    """

    # Check if analysis should be skipped
    if should_skip_analysis():
        print(f"\n[Analysis] Skipped (SKIP_ANALYSIS=1)")
        print(f"           To analyze later, run:")
        print(f"           python tests/analysis/{script_name} {jsonl_file}")
        return False

    # Determine analysis script path
    if analysis_dir is None:
        # Default: tests/analysis/ directory relative to this file
        # This file is at: tests/common/analysis_runner.py
        # Target is at:    tests/analysis/<script_name>
        analysis_dir = Path(__file__).parent.parent / "analysis"

    script_path = analysis_dir / script_name

    # Verify script exists
    if not script_path.exists():
        print(f"\n[Analysis] ⚠ Warning: Analysis script not found")
        print(f"           Expected: {script_path}")
        print(f"           Skipping analysis")
        return False

    # Verify data file exists
    jsonl_path = Path(jsonl_file)
    if not jsonl_path.exists():
        print(f"\n[Analysis] ⚠ Warning: Data file not found")
        print(f"           Expected: {jsonl_path}")
        print(f"           Skipping analysis")
        return False

    # Run analysis script
    print(f"\n[Analysis] Running {script_name}...")
    print(f"           Input: {jsonl_path.name}")
    print(f"           This may take up to {timeout}s...")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(jsonl_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(script_path.parent)  # Run from analysis directory
        )

        if result.returncode == 0:
            print(f"[Analysis] ✓ Complete")

            # Show analysis output (last 10 lines)
            if result.stdout:
                output_lines = result.stdout.strip().split('\n')
                if len(output_lines) > 10:
                    print(f"           Output (last 10 lines):")
                    for line in output_lines[-10:]:
                        print(f"           {line}")
                else:
                    for line in output_lines:
                        print(f"           {line}")

            return True
        else:
            print(f"[Analysis] ✗ Failed (exit code {result.returncode})")
            print(f"           Error output:")
            for line in result.stderr.strip().split('\n'):
                print(f"           {line}")
            print(f"           Note: Test still passed, only analysis failed")
            return False

    except subprocess.TimeoutExpired:
        print(f"[Analysis] ⚠ Timeout after {timeout}s")
        print(f"           Analysis took too long, terminating")
        print(f"           You can run manually later:")
        print(f"           python tests/analysis/{script_name} {jsonl_file}")
        return False

    except Exception as e:
        print(f"[Analysis] ✗ Error: {type(e).__name__}: {e}")
        print(f"           Note: Test still passed, only analysis failed")
        return False


def get_analysis_output_dir(base_dir: Path, analysis_type: str) -> Path:
    """
    Get standard output directory for analysis results.

    Args:
        base_dir: Base sensor-test-data directory
        analysis_type: Type of analysis (e.g., "cole_cole", "ecg", "drift")

    Returns:
        Path: Output directory for analysis results

    Example:
        output_dir = get_analysis_output_dir(
            Path.home() / "sensor-test-data",
            "cole_cole"
        )
        # Returns: ~/sensor-test-data/analysis/cole_cole/
    """
    output_dir = base_dir / "analysis" / analysis_type
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
