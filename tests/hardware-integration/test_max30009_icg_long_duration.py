"""
Test Case 9: MAX30009 ICG Long-Duration Integration

Hardware integration test for MAX30009 bioimpedance sensor with 1-hour continuous
measurement. Validates long-term stability, drift characteristics, and sustained
accuracy.

Test Flow:
1. Clear and generate base table
2. Connect 100Ω resistor load
3. Configure sensor (20 kHz, 1.28µA, 400 Hz sampling)
4. Monitor state transitions
5. Record 1 hour of continuous data (~1.44M samples)
6. Validate sync markers (monotonic, 1/sec)
7. Validate sampling frequency (400 ± 1 Hz)
8. Analyze drift and stability over time
9. Power off

Duration: ~1 hour 20 minutes (base table + 60 min recording)

Pass Criteria:
- Sync markers monotonically increasing every 1 second
- Sampling frequency 400 Hz ± 1 Hz throughout entire duration
- Impedance drift ≤ 5% over 1 hour
- No missing or duplicate sync markers
- Continuous data stream with no gaps
"""

import pytest
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from data_logger import JSONLLogger
from analysis_runner import run_analysis


# Test configuration
RESISTOR_LOAD_OHM = 100
RECORDING_DURATION = 3600.0  # 1 hour in seconds
POLLING_INTERVAL = 0.5       # seconds between data polls
SAMPLING_RATE = 400          # Hz
STIMULATION_FREQUENCY = 20000  # 20 kHz
STIMULATION_CURRENT = "1.28uA"

# Expected values for 100Ω resistor at 20 kHz
EXPECTED_R = 100.0
EXPECTED_Z = 100.0  # Pure resistor
EXPECTED_XC = 0.0
EXPECTED_PHA = 0.0

# ICG constants
ICG_SYNC_MAGIC = -999990000
ICG_SCALING_FACTOR = 10000

# Validation thresholds
MAX_DRIFT_PERCENT = 5.0  # Maximum allowed drift over 1 hour
SAMPLING_FREQ_TOLERANCE = 1.0  # Hz


def descale_icg_sample(sample: List[int]) -> List[float]:
    """Convert scaled ICG sample to engineering units."""
    return [val / ICG_SCALING_FACTOR for val in sample]


def monitor_state_transitions(client, expected_states: List[str], timeout: float = 30.0):
    """
    Monitor MAX30009 state transitions.

    Returns list of observed states with timestamps.
    """
    print(f"  [Monitoring state transitions...]")
    print(f"    Expected: {' → '.join(expected_states)}")

    observed_states = []
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            msg = client.recv(timeout=0.5)
            if msg and msg.get('type') == 'meas_state':
                state = msg.get('state')
                elapsed = time.time() - start_time
                observed_states.append({'state': state, 'time': elapsed})
                print(f"    [{elapsed:.2f}s] State: {state}")

                # Check if we've seen all expected states
                if len(observed_states) >= len(expected_states):
                    break
        except:
            continue

    # Validate sequence
    observed_sequence = [s['state'] for s in observed_states]
    all_states_observed = all(state in observed_sequence for state in expected_states)

    if all_states_observed:
        print(f"    ✓ All expected states observed in sequence")
    else:
        print(f"    ⚠ Warning: Not all states observed within {timeout}s")

    return observed_states


def collect_long_duration_data(client, duration: float, polling_interval: float,
                                logger: JSONLLogger) -> Dict[str, Any]:
    """
    Collect data for extended duration with progress tracking.

    Streams data to JSONL file and tracks progress every 60 seconds.
    Returns summary statistics.
    """
    print(f"\n  [Recording data for {duration/60:.1f} minutes...]")
    print(f"    Progress updates every 60 seconds")
    print(f"    Polling every {polling_interval}s")

    start_time = time.time()
    last_progress_time = start_time
    poll_count = 0
    total_samples = 0
    sync_count = 0
    data_count = 0

    # Stream data using logger
    while time.time() - start_time < duration:
        poll_count += 1
        current_time = time.time()
        elapsed = current_time - start_time

        # Get data
        request = {"type": "get_data"}
        response = client.send(request)

        if response.get('type') != 'data':
            print(f"    ⚠ Unexpected response: {response.get('type')}")
            time.sleep(polling_interval)
            continue

        samples = response.get('data', [])
        total_samples += len(samples)

        # Write samples using logger
        for sample in samples:
            is_sync = (len(sample) >= 5 and sample[0] == ICG_SYNC_MAGIC)
            if is_sync:
                sync_count += 1
            else:
                data_count += 1

            record = {
                'type': 'data',
                'elapsed_sec': elapsed,
                'sample': sample,
                'is_sync': is_sync
            }
            logger.write_raw(record)

            # Progress update every 60 seconds
            if current_time - last_progress_time >= 60.0:
                minutes_elapsed = elapsed / 60
                minutes_remaining = (duration - elapsed) / 60
                percent_complete = (elapsed / duration) * 100

                print(f"    [{minutes_elapsed:.1f} min] {percent_complete:.1f}% complete "
                      f"({sync_count} sync, {data_count} data samples) "
                      f"[~{minutes_remaining:.1f} min remaining]")

                last_progress_time = current_time

            # Sleep until next poll
            time.sleep(polling_interval)

    final_elapsed = time.time() - start_time

    print(f"  ✓ Collected {total_samples} samples in {final_elapsed:.2f}s")
    print(f"    Sync markers: {sync_count}")
    print(f"    Data samples: {data_count}")
    print(f"    Polls: {poll_count}")

    return {
        'total_samples': total_samples,
        'sync_count': sync_count,
        'data_count': data_count,
        'duration_sec': final_elapsed,
        'poll_count': poll_count
    }


def analyze_time_series_data(data_file: Path) -> Dict[str, Any]:
    """
    Analyze time-series data for drift and stability.

    Reads JSONL file and calculates:
    - Sync marker validation
    - Sampling frequency over time
    - Impedance drift
    - Stability metrics
    """
    print(f"\n  [Analyzing time-series data...]")

    # Load data
    sync_markers = []
    data_samples = []

    with open(data_file, 'r') as f:
        for line in f:
            record = json.loads(line)
            if record.get('type') == 'data':
                sample = record['sample']
                elapsed = record['elapsed_sec']

                if record['is_sync']:
                    sync_num = sample[1] // ICG_SCALING_FACTOR
                    sync_markers.append({
                        'sync_num': sync_num,
                        'elapsed_sec': elapsed,
                        'raw': sample
                    })
                else:
                    descaled = descale_icg_sample(sample)
                    data_samples.append({
                        'elapsed_sec': elapsed,
                        'real': descaled[0],
                        'mag': descaled[1],
                        'imag': descaled[2],
                        'angle': descaled[3]
                    })

    print(f"    Loaded {len(sync_markers)} sync markers, {len(data_samples)} data samples")

    # Validate sync markers
    print(f"\n  [Sync Marker Validation]")
    sync_validation = validate_sync_markers_long(sync_markers)

    # Validate sampling frequency
    print(f"\n  [Sampling Frequency Validation]")
    fs_validation = validate_sampling_frequency_long(data_samples, sync_markers)

    # Drift analysis
    print(f"\n  [Drift Analysis]")
    drift_analysis = analyze_drift(data_samples)

    # Stability metrics
    print(f"\n  [Stability Metrics]")
    stability_metrics = calculate_stability_metrics(data_samples)

    return {
        'sync_validation': sync_validation,
        'fs_validation': fs_validation,
        'drift_analysis': drift_analysis,
        'stability_metrics': stability_metrics
    }


def validate_sync_markers_long(sync_markers: List[Dict]) -> Dict[str, Any]:
    """Validate sync marker sequence for long duration."""
    sync_numbers = [s['sync_num'] for s in sync_markers]

    # Check monotonic increase
    is_monotonic = all(sync_numbers[i] < sync_numbers[i+1]
                      for i in range(len(sync_numbers)-1))

    # Check for gaps
    expected_count = sync_numbers[-1] - sync_numbers[0] + 1
    actual_count = len(sync_numbers)
    has_gaps = (actual_count != expected_count)

    # Check timing (should be ~1 per second)
    if len(sync_markers) >= 2:
        time_span = sync_markers[-1]['elapsed_sec'] - sync_markers[0]['elapsed_sec']
        expected_markers = int(time_span)
        timing_accurate = abs(actual_count - expected_markers) <= 2
    else:
        timing_accurate = False

    print(f"    Total sync markers: {len(sync_markers)}")
    print(f"    Sync number range: {sync_numbers[0]} to {sync_numbers[-1]}")
    print(f"    Monotonic: {'✓' if is_monotonic else '✗'}")
    print(f"    No gaps: {'✓' if not has_gaps else '✗'}")
    print(f"    Timing accurate: {'✓' if timing_accurate else '✗'}")

    return {
        'valid': is_monotonic and not has_gaps and timing_accurate,
        'is_monotonic': is_monotonic,
        'has_gaps': has_gaps,
        'timing_accurate': timing_accurate,
        'sync_count': len(sync_markers),
        'sync_range': [sync_numbers[0], sync_numbers[-1]]
    }


def validate_sampling_frequency_long(data_samples: List[Dict],
                                     sync_markers: List[Dict]) -> Dict[str, Any]:
    """Validate sampling frequency over entire duration."""
    if len(sync_markers) < 2:
        return {'valid': False, 'error': 'Not enough sync markers'}

    # Calculate overall sampling frequency
    actual_duration = len(sync_markers) - 1
    total_samples = len(data_samples)
    actual_fs = total_samples / actual_duration
    error = abs(actual_fs - SAMPLING_RATE)
    within_tolerance = error <= SAMPLING_FREQ_TOLERANCE

    print(f"    Duration: {actual_duration} seconds")
    print(f"    Total samples: {total_samples}")
    print(f"    Actual sampling rate: {actual_fs:.2f} Hz")
    print(f"    Expected: {SAMPLING_RATE} Hz ± {SAMPLING_FREQ_TOLERANCE} Hz")
    print(f"    Error: {error:.2f} Hz")
    print(f"    {'✓' if within_tolerance else '✗'} Within tolerance")

    return {
        'valid': within_tolerance,
        'actual_fs': actual_fs,
        'expected_fs': SAMPLING_RATE,
        'error': error,
        'duration_sec': actual_duration
    }


def analyze_drift(data_samples: List[Dict]) -> Dict[str, Any]:
    """Analyze impedance drift over time."""
    import numpy as np

    # Extract time series
    times = np.array([s['elapsed_sec'] for s in data_samples])
    R_values = np.array([s['real'] for s in data_samples])
    Z_values = np.array([s['mag'] for s in data_samples])

    # Calculate drift using linear regression
    R_coef = np.polyfit(times, R_values, 1)
    Z_coef = np.polyfit(times, Z_values, 1)

    # Drift in Ω/hour
    R_drift_per_hour = R_coef[0] * 3600
    Z_drift_per_hour = Z_coef[0] * 3600

    # Percent drift relative to mean
    R_mean = np.mean(R_values)
    Z_mean = np.mean(Z_values)
    R_drift_percent = (R_drift_per_hour / R_mean) * 100
    Z_drift_percent = (Z_drift_per_hour / Z_mean) * 100

    print(f"    Resistance drift: {R_drift_per_hour:.3f} Ω/hour ({R_drift_percent:.2f}%)")
    print(f"    Impedance drift: {Z_drift_per_hour:.3f} Ω/hour ({Z_drift_percent:.2f}%)")
    print(f"    Threshold: ≤ {MAX_DRIFT_PERCENT}%")

    drift_acceptable = (abs(R_drift_percent) <= MAX_DRIFT_PERCENT and
                        abs(Z_drift_percent) <= MAX_DRIFT_PERCENT)

    print(f"    {'✓' if drift_acceptable else '✗'} Drift within acceptable range")

    return {
        'R_drift_per_hour': R_drift_per_hour,
        'R_drift_percent': R_drift_percent,
        'Z_drift_per_hour': Z_drift_per_hour,
        'Z_drift_percent': Z_drift_percent,
        'drift_acceptable': drift_acceptable,
        'R_mean': R_mean,
        'Z_mean': Z_mean
    }


def calculate_stability_metrics(data_samples: List[Dict]) -> Dict[str, Any]:
    """Calculate stability metrics over 10-minute windows."""
    import numpy as np

    # Group samples into 10-minute windows
    window_duration = 600  # 10 minutes
    times = np.array([s['elapsed_sec'] for s in data_samples])
    max_time = times[-1]
    num_windows = int(max_time / window_duration)

    window_stats = []

    for i in range(num_windows):
        start_time = i * window_duration
        end_time = (i + 1) * window_duration

        # Extract samples in this window
        mask = (times >= start_time) & (times < end_time)
        window_R = np.array([s['real'] for s, m in zip(data_samples, mask) if m])
        window_Z = np.array([s['mag'] for s, m in zip(data_samples, mask) if m])

        if len(window_R) > 0:
            window_stats.append({
                'window': i + 1,
                'start_min': start_time / 60,
                'R_mean': np.mean(window_R),
                'R_std': np.std(window_R),
                'Z_mean': np.mean(window_Z),
                'Z_std': np.std(window_Z)
            })

    # Calculate overall stability
    R_means = np.array([w['R_mean'] for w in window_stats])
    Z_means = np.array([w['Z_mean'] for w in window_stats])

    R_stability = np.std(R_means)  # Ω
    Z_stability = np.std(Z_means)  # Ω

    print(f"    Number of 10-min windows: {len(window_stats)}")
    print(f"    R stability (std of window means): {R_stability:.3f} Ω")
    print(f"    Z stability (std of window means): {Z_stability:.3f} Ω")

    return {
        'window_stats': window_stats,
        'R_stability': R_stability,
        'Z_stability': Z_stability,
        'num_windows': len(window_stats)
    }


@pytest.mark.hardware
@pytest.mark.max30009
@pytest.mark.long
def test_max30009_long_duration(max30009_client, max30009_cleanup, results_dir):
    """
    Test Case 9: MAX30009 ICG Long-Duration Integration.

    1-hour continuous measurement with 100Ω resistor load.
    Validates long-term stability and drift characteristics.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 9: MAX30009 ICG Long-Duration Integration")
    print(f"{'='*70}")
    print(f"\nResistor Load: {RESISTOR_LOAD_OHM} Ω")
    print(f"Duration: {RECORDING_DURATION/60:.0f} minutes")
    print(f"Expected sampling rate: {SAMPLING_RATE} Hz")

    # Setup data file (standard practice: ~/sensor-test-data/data/bioz/)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_file = Path(results_dir) / "data" / "bioz" / f"test_009_long_duration_{timestamp}.jsonl"
    data_file.parent.mkdir(parents=True, exist_ok=True)

    # Initialize logger and write metadata
    logger = JSONLLogger(str(data_file), test_id="test_009", sensor="max30009")

    metadata = {
        'type': 'metadata',
        'test_case': 'TC-009',
        'test_name': 'MAX30009 ICG Long-Duration Integration',
        'timestamp': timestamp,
        'resistor_ohm': RESISTOR_LOAD_OHM,
        'duration_sec': RECORDING_DURATION,
        'sampling_rate': SAMPLING_RATE,
        'stimulation_frequency': STIMULATION_FREQUENCY,
        'stimulation_current': STIMULATION_CURRENT,
        'expected_values': {
            'R': EXPECTED_R,
            'Z': EXPECTED_Z,
            'Xc': EXPECTED_XC,
            'PhA': EXPECTED_PHA
        }
    }
    logger.write_raw(metadata)

    # Step 1: Clear base table
    print(f"\n[Step 1] Clearing base table...")
    clear_request = {"type": "clear_base_table"}
    clear_response = max30009_client.send(clear_request)
    assert clear_response["type"] == "base_table_cleared", \
        f"Failed to clear base table: {clear_response}"
    print(f"  ✓ Base table cleared")

    # Step 2: Generate base table
    print(f"\n[Step 2] Generating base table (calibration)...")
    build_request = {"type": "build_base_table"}
    build_response = max30009_client.send(build_request)
    assert build_response["type"] == "build_base_table_started", \
        f"Failed to start base table generation: {build_response}"
    print(f"  ✓ Base table generation started")

    # Monitor calibration progress
    calib_count = 0
    start_time = time.time()

    while calib_count < 100:
        msg = max30009_client.recv(timeout=2.0)
        if msg and msg.get('type') == 'calib_data':
            calib_count += 1
            if calib_count % 20 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {calib_count}/100 calibrations ({elapsed:.1f}s)")

    elapsed = time.time() - start_time
    print(f"  ✓ Base table generation complete ({elapsed:.1f}s, 100 calibrations)")

    # Step 3: User prompt to connect resistor
    print(f"\n[Step 3] Hardware Setup")
    print(f"{'='*70}")
    print(f"\n*** PLEASE CONNECT {RESISTOR_LOAD_OHM} Ω RESISTOR NOW ***")
    print(f"Press Enter when ready...")
    input()

    # Step 4: Configure sensor
    print(f"\n[Step 4] Configuring MAX30009...")
    settings = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": STIMULATION_FREQUENCY,
        "measure_frequency": SAMPLING_RATE,
        "stimulate_current": STIMULATION_CURRENT
    }

    settings_response = max30009_client.send(settings)
    assert settings_response["type"] == "actual_settings", \
        f"Configuration failed: {settings_response}"
    print(f"  ✓ Configured: {STIMULATION_FREQUENCY} Hz, {STIMULATION_CURRENT}")

    # Step 5: Monitor state transitions
    expected_states = ['pre_measuring', 'pre_measure_end', 'calibrating',
                      'calibrate_end', 'start_measuring']
    state_transitions = monitor_state_transitions(max30009_client, expected_states)

    # Step 6: Collect long-duration data
    collection_summary = collect_long_duration_data(
        max30009_client,
        RECORDING_DURATION,
        POLLING_INTERVAL,
        logger
    )

    # Step 7: Analyze data
    analysis_results = analyze_time_series_data(data_file)

    # Write summary to file
    summary = {
        'type': 'summary',
        'collection': collection_summary,
        'analysis': analysis_results
    }
    logger.write_raw(summary)

    # Run analysis script to generate plots
    run_analysis("analyze_icg_long_duration.py", data_file)

    # Step 8: Power off
    print(f"\n[Step 5] Powering off MAX30009...")
    poweroff_request = {"type": "settings", "measure_enable": False}
    poweroff_response = max30009_client.send(poweroff_request)
    assert poweroff_response["type"] == "actual_settings"
    print(f"  ✓ MAX30009 powered off")

    # Validation
    print(f"\n[Step 6] Validation")
    print(f"{'='*70}")

    sync_valid = analysis_results['sync_validation']['valid']
    fs_valid = analysis_results['fs_validation']['valid']
    drift_ok = analysis_results['drift_analysis']['drift_acceptable']

    print(f"  Sync markers: {'✓ PASS' if sync_valid else '✗ FAIL'}")
    print(f"  Sampling frequency: {'✓ PASS' if fs_valid else '✗ FAIL'}")
    print(f"  Drift: {'✓ PASS' if drift_ok else '✗ FAIL'}")

    all_pass = sync_valid and fs_valid and drift_ok

    if all_pass:
        print(f"\n✓ Test PASSED: All validation criteria met")
    else:
        print(f"\n✗ Test FAILED: See validation details above")

    print(f"{'='*70}")
    print(f"Data saved to: {data_file}")
    print(f"{'='*70}\n")

    assert all_pass, "Test validation failed"
