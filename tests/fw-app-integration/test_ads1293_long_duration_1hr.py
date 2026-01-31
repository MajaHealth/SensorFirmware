"""
Test Case 46: ADS1293 Long-Duration 1-Hour Data Collection

Category: FW-APP Integration
Components: ADS1293 + Firmware + ECG Simulator

Test Steps:
1. Configure ADS1293 for 400 Hz sampling
2. Send get_data every 0.5s for 1 hour and record
3. Extract sync counters and compute effective sampling frequency
4. Log sample counts, timestamps, sync counters, and signal quality metrics
5. Power off

Pass Criteria:
- Sync counters monotonically increase every 1 second with no missing frames
- Mean sampling frequency is 400 Hz ±1 Hz
- Signal integrity matches BPM (if simulator connected)
- Poweroff returns power_is_off
"""

import pytest
import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from data_logger import JSONLLogger
from analysis_runner import run_analysis


SYNC_MAGIC = -99999


@pytest.fixture
def ads1293_client(test_config):
    """Create TCP client for ADS1293 service with cleanup."""
    ads_config = test_config['services']['ads1293']
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        yield client

        # Cleanup: Power off sensor
        try:
            response = client.send({"type": "poweroff"})
            print(f"\n[Cleanup] Poweroff response: {response.get('type', 'unknown')}")
        except:
            pass


@pytest.fixture
def results_dir():
    """Create results directory for JSONL data logging."""
    results_path = Path.home() / "sensor-test-data" / "data"
    results_path.mkdir(parents=True, exist_ok=True)
    return results_path


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.long
@pytest.mark.timeout(7200)
def test_ads1293_long_duration_1hr(test_config, results_dir, ads1293_client):
    """
    Test Case 46: ADS1293 1-hour long-duration data collection at 0.5s polling.

    Validates:
    - Sync counter integrity over 3600 syncs (1 hour)
    - Sampling frequency accuracy (400 Hz ±1 Hz)
    - No missing or duplicated sync frames
    - Signal quality and BPM detection
    - Clean poweroff after extended operation
    """

    # Load test parameters
    ecg_params = test_config['ads1293_ecg']
    thresholds = test_config['thresholds']

    test_duration = ecg_params['long_duration_sec']
    polling_interval = 0.5
    r2_rate = ecg_params['r2_rate']
    r3_rate = ecg_params['r3_rate']
    expected_fs = ecg_params['sampling_frequency']
    freq_tolerance = thresholds['sampling']['frequency_error_hz']

    # Calculate R1_rate for target frequency
    # fs = 128000 / (R1 × R2 × R3)
    # For R2=4, R3=16: R1 = 128000 / (400 × 64) = 5
    r1_rate = 5

    print(f"\n{'='*70}")
    print(f"Test Case 46: ADS1293 1-Hour Long-Duration Data Collection")
    print(f"{'='*70}")
    print(f"Duration: {test_duration} seconds (1 hour)")
    print(f"Polling Interval: {polling_interval}s")
    print(f"Expected Sampling Frequency: {expected_fs} Hz")
    print(f"Expected Syncs: ~{test_duration} (1 per second)")
    print(f"{'='*70}\n")

    # Step 1: Configure ADS1293
    print(f"[Step 1] Configuring ADS1293...")

    settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": r2_rate,
        "R3_rate": r3_rate
    }

    response = ads1293_client.send(settings)
    assert response["type"] == "actual_settings", \
        f"Configuration failed: {response}"

    actual_r1 = response.get('R1_rate', r1_rate)
    actual_r2 = response.get('R2_rate', r2_rate)
    actual_r3 = response.get('R3_rate', r3_rate)

    calculated_fs = 128000 / (actual_r1 * actual_r2 * actual_r3)

    print(f"  ✓ ADS1293 configured")
    print(f"    - R1={actual_r1}, R2={actual_r2}, R3={actual_r3}")
    print(f"    - Calculated sampling frequency: {calculated_fs:.1f} Hz")
    print(f"    - Conversion enabled: {response.get('enable_conversion')}")
    print(f"    - Power enabled: {response.get('power_enable')}\n")

    # Step 2: Stabilization
    print(f"[Step 2] Waiting for sensor stabilization...")
    time.sleep(2.0)
    print(f"  ✓ Sensor ready\n")

    # Step 3: Flush accumulated buffer
    print(f"[Step 3] Flushing accumulated buffer...")
    total_flushed = 0
    flush_attempts = 3

    for attempt in range(flush_attempts):
        flush_response = ads1293_client.send({"type": "get_data"})
        if flush_response["type"] == "data":
            flushed_count = len(flush_response["data"])
            total_flushed += flushed_count
            if flushed_count > 0:
                print(f"  Flush attempt {attempt + 1}: {flushed_count} samples")
            time.sleep(0.2)
        else:
            break

    print(f"  ✓ Flushed {total_flushed} accumulated samples\n")

    # Step 4: Collect data for 1 hour
    print(f"[Step 4] Collecting data for {test_duration} seconds (1 hour)...")
    print(f"  Polling every {polling_interval}s")
    print(f"  Expected polls: {int(test_duration / polling_interval)}")
    print(f"  This will take approximately 1 hour. Progress updates every 5 minutes.\n")

    # Initialize JSONL logger (standard practice: ~/sensor-test-data/data/ecg/)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_file = results_dir / "data" / "ecg" / f"test_046_ads1293_1hr_{timestamp}.jsonl"
    jsonl_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Logging data to: {jsonl_file}\n")

    # Collection loop
    num_polls = int(test_duration / polling_interval)
    all_samples = []
    sync_markers = []

    collection_start = time.time()
    last_progress_time = collection_start

    # Initialize logger and write metadata
    logger = JSONLLogger(str(jsonl_file), test_id="test_046", sensor="ads1293")

    metadata = {
        "type": "metadata",
        "test_case": "TC-046",
        "test_name": "ADS1293 1-hour long-duration",
        "duration_sec": test_duration,
        "polling_interval_sec": polling_interval,
        "expected_fs": expected_fs,
        "r1_rate": actual_r1,
        "r2_rate": actual_r2,
        "r3_rate": actual_r3,
        "start_time": collection_start
    }
    logger.write_raw(metadata)

    for poll_num in range(num_polls):
        poll_start = time.time()

        # Get data
        response = ads1293_client.send({"type": "get_data"})
        poll_end = time.time()

        assert response["type"] == "data", \
            f"Poll {poll_num}: Expected 'data', got '{response.get('type')}'"

        samples = response["data"]

        # Log to JSONL
        log_entry = {
            "type": "data",
            "poll_num": poll_num,
            "timestamp": poll_start,
            "sample_count": len(samples),
            "data": samples
        }
        logger.write_raw(log_entry)

        # Extract sync markers and regular samples
        for sample in samples:
            if sample[0] == SYNC_MAGIC:
                sync_markers.append(sample)
            else:
                all_samples.append(sample)

        # Progress update every 5 minutes
        elapsed = time.time() - collection_start
        if elapsed - (last_progress_time - collection_start) >= 300:  # 5 minutes
            progress_pct = (poll_num / num_polls) * 100
            print(f"  Progress: {progress_pct:.1f}% ({poll_num}/{num_polls} polls) "
                  f"- Elapsed: {elapsed/60:.1f} min - "
                  f"Samples: {len(all_samples)}, Syncs: {len(sync_markers)}")
            last_progress_time = time.time()

        # Maintain polling interval
        sleep_time = polling_interval - (poll_end - poll_start)
        if sleep_time > 0:
            time.sleep(sleep_time)

    collection_end = time.time()
    actual_duration = collection_end - collection_start

    print(f"\n  ✓ Collection complete")
    print(f"    - Actual duration: {actual_duration:.2f}s ({actual_duration/60:.2f} min)")
    print(f"    - Total samples: {len(all_samples)}")
    print(f"    - Total sync markers: {len(sync_markers)}")
    print(f"    - Data saved to: {jsonl_file}\n")

    # Step 5: Validate sync counter sequence
    print(f"[Step 5] Validating sync counter sequence...")

    sync_numbers = [marker[1] for marker in sync_markers]

    assert len(sync_markers) >= test_duration - 2, \
        f"Expected ~{test_duration} sync markers, got {len(sync_markers)}"
    assert len(sync_markers) <= test_duration + 2, \
        f"Too many sync markers: expected ~{test_duration}, got {len(sync_markers)}"

    print(f"  ✓ Sync marker count: {len(sync_markers)} (within expected range)")

    # Check monotonically increasing
    for i in range(len(sync_numbers) - 1):
        assert sync_numbers[i] < sync_numbers[i+1], \
            f"Sync numbers not monotonically increasing at index {i}: " \
            f"{sync_numbers[i]} >= {sync_numbers[i+1]}"

    print(f"  ✓ Monotonically increasing")

    # Check for missing frames (consecutive sequence)
    missing_frames = []
    for i in range(len(sync_numbers) - 1):
        diff = sync_numbers[i+1] - sync_numbers[i]
        if diff != 1:
            missing_frames.append((sync_numbers[i], sync_numbers[i+1], diff))

    assert len(missing_frames) == 0, \
        f"Missing sync frames detected: {missing_frames}"

    print(f"  ✓ No missing frames (consecutive sequence)")

    # Check for duplicates
    assert len(sync_numbers) == len(set(sync_numbers)), \
        f"Duplicated sync frames detected"

    print(f"  ✓ No duplicated frames")
    print(f"    - Sync range: {sync_numbers[0]} to {sync_numbers[-1]}\n")

    # Step 6: Validate sampling frequency
    print(f"[Step 6] Validating sampling frequency...")

    total_samples = len(all_samples)
    total_syncs = len(sync_markers)

    # Duration measured by sync markers (1 sync per second)
    measured_duration = total_syncs
    measured_fs = total_samples / measured_duration

    fs_error = abs(measured_fs - expected_fs)

    print(f"  Total samples: {total_samples}")
    print(f"  Total syncs: {total_syncs}")
    print(f"  Measured duration: {measured_duration}s")
    print(f"  Measured sampling frequency: {measured_fs:.2f} Hz")
    print(f"  Expected: {expected_fs} Hz ± {freq_tolerance} Hz")
    print(f"  Error: {fs_error:.2f} Hz")

    assert fs_error <= freq_tolerance, \
        f"Sampling frequency error {fs_error:.2f} Hz exceeds tolerance {freq_tolerance} Hz"

    print(f"  ✓ Sampling frequency within tolerance\n")

    # Step 7: Optional BPM validation (informational only)
    print(f"[Step 7] Signal quality check...")
    print(f"  Note: BPM validation requires ECG simulator connection")
    print(f"  Skipping automated BPM detection (can be done post-processing)")
    print(f"  ✓ Data available for offline analysis\n")

    # Step 8: Power off
    print(f"[Step 8] Powering off ADS1293...")

    poweroff_response = ads1293_client.send({"type": "poweroff"})

    assert poweroff_response["type"] == "power_is_off", \
        f"Expected 'power_is_off', got '{poweroff_response.get('type')}'"

    print(f"  ✓ Poweroff successful\n")

    # Write final metadata
    final_metadata = {
        "type": "metadata",
        "test_result": "PASS",
        "actual_duration_sec": actual_duration,
        "total_samples": total_samples,
        "total_syncs": total_syncs,
        "measured_fs": measured_fs,
        "fs_error": fs_error,
        "sync_range": [sync_numbers[0], sync_numbers[-1]],
        "end_time": collection_end
    }
    logger.write_raw(final_metadata)

    # Run analysis script to generate plots
    run_analysis("analyze_ecg.py", jsonl_file)

    # Summary
    print(f"{'='*70}")
    print(f"Test Summary - TC-046")
    print(f"{'='*70}")
    print(f"Duration:              {actual_duration:.2f}s ({actual_duration/60:.2f} min)")
    print(f"Total Samples:         {total_samples}")
    print(f"Total Sync Markers:    {total_syncs}")
    print(f"Sync Range:            {sync_numbers[0]} to {sync_numbers[-1]}")
    print(f"Measured Fs:           {measured_fs:.2f} Hz")
    print(f"Expected Fs:           {expected_fs} Hz ± {freq_tolerance} Hz")
    print(f"Fs Error:              {fs_error:.2f} Hz")
    print(f"Data File:             {jsonl_file}")
    print(f"Result:                PASS ✓")
    print(f"{'='*70}\n")
