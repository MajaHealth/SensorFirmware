"""
pytest configuration and shared fixtures
"""
import pytest
import yaml
import os
import json
from pathlib import Path
from typing import Dict, List


def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    config.addinivalue_line(
        "markers", "hardware: tests that require actual hardware sensors"
    )
    config.addinivalue_line(
        "markers", "ads1293: tests for ADS1293 ECG sensor"
    )
    config.addinivalue_line(
        "markers", "max30009: tests for MAX30009 BIOZ sensor"
    )
    config.addinivalue_line(
        "markers", "ws2812: tests for WS2812 LED controller"
    )
    config.addinivalue_line(
        "markers", "quick: quick tests (< 5 minutes)"
    )
    config.addinivalue_line(
        "markers", "slow: slow tests (5-60 minutes)"
    )
    config.addinivalue_line(
        "markers", "long: long-duration tests (> 1 hour)"
    )
    config.addinivalue_line(
        "markers", "api: API/protocol validation tests"
    )
    config.addinivalue_line(
        "markers", "fw_app: firmware-application integration tests"
    )
    config.addinivalue_line(
        "markers", "invalid_params: invalid parameter handling tests"
    )

@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from YAML file."""
    config_path = Path(__file__).parent / "config" / "test_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Allow overriding service host via environment variable
    # This enables remote testing without modifying YAML
    target_host = os.getenv('PI_TARGET_IP')
    if target_host:
        for service in config['services'].values():
            service['host'] = target_host

    return config

@pytest.fixture(scope="session")
def results_dir(tmp_path_factory):
    """Create results directory for test outputs."""
    results = tmp_path_factory.mktemp("test-results")
    return results

@pytest.fixture
def service_ports(test_config):
    """Get service port configuration."""
    return test_config['services']

@pytest.fixture
def thresholds(test_config):
    """Get pass/fail thresholds."""
    return test_config['thresholds']


# ============================================================================
# Automatic Analysis Pipeline
# ============================================================================

# Global list to track test data files generated during session
_test_data_files: List[Dict] = []


def detect_sensor_type(filepath: Path) -> str:
    """
    Auto-detect sensor type from JSONL data file.

    Returns:
        'ecg' for ADS1293 ECG data
        'bioz' for MAX30009 bioimpedance data
        'unknown' if cannot determine
    """
    try:
        with open(filepath, 'r') as f:
            # Read first few lines to detect type
            for i, line in enumerate(f):
                if i >= 10:  # Check first 10 lines
                    break
                try:
                    record = json.loads(line)

                    # Check for ADS1293 ECG indicators
                    if record.get('sensor') == 'ads1293':
                        return 'ecg'
                    if 'ch1' in record or 'ch2' in record or 'ch3' in record:
                        return 'ecg'

                    # Check for MAX30009 BIOZ indicators
                    if record.get('sensor') == 'max30009':
                        return 'bioz'
                    if 'real' in record or 'imaginary' in record:
                        return 'bioz'
                    if 'impedance' in str(record).lower():
                        return 'bioz'

                except json.JSONDecodeError:
                    continue

        # Fallback: check filename patterns
        filename = filepath.name.lower()
        if 'ecg' in filename or 'ads1293' in filename:
            return 'ecg'
        if 'bioz' in filename or 'max30009' in filename or 'impedance' in filename:
            return 'bioz'

    except Exception as e:
        print(f"Warning: Could not detect sensor type for {filepath}: {e}")

    return 'unknown'


def extract_expected_bpm(filepath: Path) -> float:
    """
    Extract expected BPM from filename or test metadata.

    Examples:
        test_011_ecg_1hr_bpm60.jsonl -> 60.0
        test_010_ecg_60s.jsonl -> None (not specified)
    """
    filename = filepath.name.lower()

    # Pattern: bpm60, bpm-60, bpm_60
    import re
    match = re.search(r'bpm[-_]?(\d+)', filename)
    if match:
        return float(match.group(1))

    # Check first line metadata
    try:
        with open(filepath, 'r') as f:
            first_line = f.readline()
            record = json.loads(first_line)
            if 'expected_bpm' in record:
                return float(record['expected_bpm'])
    except:
        pass

    return None


def run_ecg_analysis(filepath: Path, output_dir: Path):
    """Run automated ECG analysis on test data file."""
    try:
        # Import analyzer
        import sys
        analysis_dir = Path(__file__).parent / "analysis"
        sys.path.insert(0, str(analysis_dir))

        from analyze_ecg import ECGAnalyzer

        # Detect expected BPM from filename
        expected_bpm = extract_expected_bpm(filepath)

        print(f"\n{'='*70}")
        print(f"AUTO-ANALYSIS: ECG Data")
        print(f"{'='*70}")
        print(f"Input: {filepath.name}")
        if expected_bpm:
            print(f"Expected BPM: {expected_bpm}")
        print(f"Output: {output_dir}")
        print(f"{'='*70}\n")

        # Create analyzer
        analyzer = ECGAnalyzer(sampling_rate=400)

        # Load data
        print("Loading data...")
        analyzer.load_jsonl(str(filepath))
        print(f"✓ Loaded {analyzer.total_samples} samples\n")

        # Analyze
        print("Analyzing ECG signal...")
        results = analyzer.analyze(
            channel_num=1,
            filter_cutoff=40.0,
            expected_bpm=expected_bpm
        )

        # Print summary
        print("\n--- Analysis Results ---")
        print(f"Duration: {results['duration_sec']:.1f}s")
        print(f"Mean HR: {results['heart_rate']['mean_bpm']:.2f} bpm")
        print(f"HR Std: {results['heart_rate']['std_bpm']:.2f} bpm")
        print(f"R-peaks: {results['heart_rate']['peak_count']}")

        if expected_bpm:
            print(f"Expected: {expected_bpm} bpm")
            print(f"Error: {results['heart_rate']['bpm_error']:.2f} bpm")

        print(f"RMS: {results['signal_stats']['rms']:.2f} µV")
        print(f"Sync valid: {results['sync_validation']['is_valid']}")

        # Generate output files
        test_id = filepath.stem  # e.g., "test_010_ecg_60s"

        # Save metrics JSON
        metrics_file = output_dir / f"{test_id}_ecg_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Metrics saved: {metrics_file.name}")

        # Generate plots
        waveform_file = output_dir / f"{test_id}_ecg_waveform.png"
        analyzer.plot_waveform(channel_num=1, output_file=str(waveform_file))
        print(f"✓ Waveform plot: {waveform_file.name}")

        hr_file = output_dir / f"{test_id}_ecg_hr_analysis.png"
        analyzer.plot_hr_analysis(channel_num=1, output_file=str(hr_file))
        print(f"✓ HR analysis plot: {hr_file.name}")

        print(f"\n{'='*70}")
        print(f"ECG Analysis Complete")
        print(f"{'='*70}\n")

        return True

    except Exception as e:
        print(f"\n✗ ECG Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_bioz_analysis(filepath: Path, output_dir: Path):
    """Run automated BIOZ analysis on test data file."""
    try:
        # Import analyzer
        import sys
        analysis_dir = Path(__file__).parent / "analysis"
        sys.path.insert(0, str(analysis_dir))

        from analyze_bioz import BIOZAnalyzer

        print(f"\n{'='*70}")
        print(f"AUTO-ANALYSIS: BIOZ Data")
        print(f"{'='*70}")
        print(f"Input: {filepath.name}")
        print(f"Output: {output_dir}")
        print(f"{'='*70}\n")

        # Create analyzer
        analyzer = BIOZAnalyzer()

        # Load data
        print("Loading data...")
        analyzer.load_jsonl(str(filepath))
        print(f"✓ Loaded {len(analyzer.df)} impedance measurements\n")

        # Try to detect reference model from filename or metadata
        # Common patterns: "82_82_100nF", "resistor_101ohm", etc.
        # For now, just analyze without reference (show raw data only)
        print("Note: Auto-detection of reference model not yet implemented")
        print("      Analyzing raw impedance data only (no error metrics)")

        # Analyze
        print("\nAnalyzing BIOZ signal...")
        results = analyzer.analyze(freq_min=1000, freq_max=500000)

        # Print summary
        print("\n--- Analysis Results ---")
        print(f"Total measurements: {results['total_measurements']}")
        print(f"Frequency range: {results['frequency_range']['min_hz']:.0f} - "
              f"{results['frequency_range']['max_hz']:.0f} Hz")

        if 'config_stats' in results:
            print(f"Configurations tested: {len(results['config_stats'])}")

        # Generate output files
        test_id = filepath.stem

        # Save metrics JSON
        metrics_file = output_dir / f"{test_id}_bioz_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Metrics saved: {metrics_file.name}")

        # Generate Cole-Cole plot
        cole_file = output_dir / f"{test_id}_cole_cole.png"
        analyzer.plot_cole_cole(output_file=str(cole_file),
                               title=f'Cole-Cole Plot: {test_id}')
        print(f"✓ Cole-Cole plot: {cole_file.name}")

        print(f"\n{'='*70}")
        print(f"BIOZ Analysis Complete")
        print(f"{'='*70}\n")

        return True

    except Exception as e:
        print(f"\n✗ BIOZ Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook called after each test phase (setup, call, teardown).
    Track test data files generated during tests.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process after test execution (not setup/teardown)
    if report.when != "call":
        return

    # Check if test has results_dir fixture and created data files
    if hasattr(item, 'funcargs') and 'results_dir' in item.funcargs:
        results_dir = item.funcargs['results_dir']

        # Find JSONL files in results directory
        for jsonl_file in Path(results_dir).glob("*.jsonl"):
            # Check if file has substantial data (> 1KB)
            if jsonl_file.stat().st_size > 1024:
                _test_data_files.append({
                    'filepath': jsonl_file,
                    'test_name': item.nodeid,
                    'passed': report.outcome == 'passed'
                })


def pytest_sessionfinish(session, exitstatus):
    """
    Hook called after all tests finish.
    Automatically run analysis on collected data files.
    """
    if not _test_data_files:
        return

    print("\n" + "="*70)
    print("AUTOMATIC ANALYSIS PIPELINE")
    print("="*70)
    print(f"Found {len(_test_data_files)} test data files to analyze\n")

    # Create analysis output directory
    analysis_dir = Path("/tmp/test-results/analysis")
    analysis_dir.mkdir(parents=True, exist_ok=True)

    for file_info in _test_data_files:
        filepath = file_info['filepath']

        print(f"\n--- {filepath.name} ---")
        print(f"Test: {file_info['test_name']}")
        print(f"Status: {'PASSED' if file_info['passed'] else 'FAILED'}")

        # Detect sensor type
        sensor_type = detect_sensor_type(filepath)
        print(f"Detected type: {sensor_type.upper()}")

        # Run appropriate analyzer
        if sensor_type == 'ecg':
            run_ecg_analysis(filepath, analysis_dir)
        elif sensor_type == 'bioz':
            run_bioz_analysis(filepath, analysis_dir)
        else:
            print(f"Skipping: Unknown sensor type")

    print("\n" + "="*70)
    print(f"Analysis outputs saved to: {analysis_dir}")
    print("="*70 + "\n")
