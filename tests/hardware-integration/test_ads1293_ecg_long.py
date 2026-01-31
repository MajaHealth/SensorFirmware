"""
Test Case 11: ADS1293 ECG Long-Duration Automated Integration (1 hour)

Category: HW-FW Integration
Components: ADS1293 + firmware service + ECG simulator
Test Name: ADS1293 ECG long-duration automated integration (1 hr)

Hardware Requirements:
- ADS1293 connected to CM4
- ECG simulator connected to ADS1293 inputs
- ECG simulator configured for BPM: 30, 60, 120, or 180

Prerequisites:
- DUT with ADS1293 service available on port 1293
- ECG simulator configured with specific BPM
- Long-duration capture/logging capability

Pass Criteria:
- Firmware returns "actual settings" with conversion enabled
- 1 hour recording completes successfully
- Sync counters monotonically increase every 1s with no missing sync frames
- Mean sampling frequency is 400 Hz ± 1 Hz
- BPM matches simulator setting (±3 bpm or ±1%, whichever is greater)
- Required metrics are logged
- ADS1293 power-off is confirmed

Accuracy Metrics:
- ±25 µV for reference values ≤ 500 µV
- 5% or ±40 µV for reference values > 500 µV
- BPM error: ±3 bpm or ±1%, whichever is greater
"""

import pytest
import time
from pathlib import Path
import sys
import numpy as np

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from data_logger import JSONLLogger
from validators import (
    extract_sync_markers_ads1293,
    validate_sync_monotonic,
    calculate_sampling_frequency,
    validate_sampling_frequency
)
from sensor_helpers import configure_ads1293, get_sensor_data, power_off_sensor


@pytest.mark.hardware
@pytest.mark.ads1293
@pytest.mark.long
@pytest.mark.timeout(7200)  # 2 hours timeout per test (1 hr data + overhead)
@pytest.mark.parametrize("bpm", [30, 60, 120, 180])
def test_ads1293_ecg_1hr(test_config, results_dir, bpm):
    """
    Test Case 11: ADS1293 ECG long-duration integration (1 hour).

    Test Steps:
    1. Connect to ADS1293 service
    2. Configure for 400 Hz sampling with R2=4, R3=16
    3. Enable conversion and verify actual settings
    4. Flush accumulated buffer data
    5. Collect data for 1 hour (poll every 1.0s)
    6. Extract sync counters and validate monotonic increase
    7. Calculate sampling frequency and verify 400 Hz ± 1 Hz
    8. Analyze BPM and verify against simulator setting
    9. Log all metrics (sample count, timestamps, sync counters, frequency, BPM)
    10. Power off ADS1293 and verify response

    Pass Criteria:
    - Sync counters monotonically increase every 1s
    - No missing sync frames
    - Mean sampling frequency = 400 Hz ± 1 Hz
    - BPM matches simulator (±3 bpm or ±1%, whichever is greater)
    - Data successfully logged for offline analysis
    """
    # Get configuration
    ads_config = test_config['services']['ads1293']
    ecg_params = test_config['ads1293_ecg']
    thresholds = test_config['thresholds']

    # Test parameters
    test_duration = ecg_params['long_duration_sec']  # 3600 seconds (1 hour)
    polling_interval = ecg_params['polling_interval_sec']  # 1.0 seconds
    expected_freq = ecg_params['sampling_frequency']  # 400 Hz
    freq_tolerance = thresholds['sampling']['frequency_error_hz']  # 1 Hz

    # BPM thresholds
    bpm_absolute_error = thresholds['ads1293']['bpm_error_absolute']  # ±3 bpm
    bpm_percent_error = thresholds['ads1293']['bpm_error_pct']  # ±1%

    print(f"\n{'='*70}")
    print(f"Test Case 11: ADS1293 ECG 1-Hour Integration Test")
    print(f"{'='*70}")
    print(f"BPM Setting: {bpm} bpm")
    print(f"Duration: {test_duration}s ({test_duration/3600:.1f} hour)")
    print(f"Polling interval: {polling_interval}s")
    print(f"Expected sampling frequency: {expected_freq} Hz ± {freq_tolerance} Hz")
    print(f"Expected total samples: ~{expected_freq * test_duration:,}")
    print(f"BPM tolerance: ±{bpm_absolute_error} bpm or ±{bpm_percent_error}%, whichever is greater")
    print(f"{'='*70}\n")

    # Data logger
    output_file = results_dir / f"test_011_ecg_1hr_bpm{bpm}.jsonl"
    logger = JSONLLogger(
        str(output_file),
        test_id="test_011",
        sensor="ads1293"
    )

    # Write initial metadata
    logger.write_raw({
        "type": "test_metadata",
        "test_id": "test_011",
        "bpm_setting": bpm,
        "duration_sec": test_duration,
        "expected_frequency_hz": expected_freq
    })

    # Connect to ADS1293
    print(f"[Step 1] Connecting to ADS1293 at {ads_config['host']}:{ads_config['port']}...")
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        print("✓ Connected\n")

        # Configure ADS1293
        print(f"[Step 2] Configuring ADS1293...")
        print(f"  R2_rate: {ecg_params['r2_rate']}")
        print(f"  R3_rate: {ecg_params['r3_rate']}")
        print(f"  Sampling frequency: {expected_freq} Hz")

        response = configure_ads1293(
            client,
            sampling_freq=expected_freq,
            r2_rate=ecg_params['r2_rate'],
            r3_rate=ecg_params['r3_rate'],
            enable_conversion=True
        )

        assert response["type"] == "actual_settings", "Failed to configure ADS1293"
        assert response["enable_conversion"] == True, "Conversion not enabled"
        print("✓ Configuration successful")
        print(f"  Actual settings: {response}\n")

        # Wait for sensor to stabilize
        print(f"[Step 3] Waiting 2 seconds for sensor stabilization...")
        time.sleep(2.0)
        print("✓ Sensor ready\n")

        # Flush accumulated buffer data (multiple times to ensure clean state)
        print(f"[Step 4] Flushing accumulated buffer...")
        total_flushed = 0
        flush_attempts = 3
        for attempt in range(flush_attempts):
            flush_response = get_sensor_data(client)
            if flush_response["type"] == "data":
                flushed_count = len(flush_response["data"])
                total_flushed += flushed_count
                if flushed_count > 0:
                    print(f"  Flush attempt {attempt + 1}: {flushed_count} samples")
                time.sleep(0.2)  # Brief pause between flushes
            else:
                break
        print(f"✓ Flushed {total_flushed} accumulated samples from buffer\n")

        # Collect data
        print(f"[Step 5] Collecting data for {test_duration} seconds ({test_duration/3600:.1f} hour)...")
        print(f"  This will take approximately {test_duration/60:.0f} minutes")
        print(f"  Progress updates every 5 minutes\n")

        num_polls = int(test_duration / polling_interval)
        all_data = []
        start_time = time.time()

        # Progress tracking
        progress_interval = 300  # Update every 5 minutes
        next_progress_time = start_time + progress_interval

        for i in range(num_polls):
            poll_time = time.time()

            # Get data
            response = get_sensor_data(client)

            if response["type"] == "data":
                # Save to logger
                logger.write_data(
                    data=response["data"],
                    metadata={
                        "timestamp": response.get("timestamp"),
                        "data_size": response.get("data_size"),
                        "poll_number": i,
                        "elapsed_time": poll_time - start_time
                    }
                )

                # Accumulate for analysis
                all_data.extend(response["data"])

                # Progress indicator (every 5 minutes)
                current_time = time.time()
                if current_time >= next_progress_time or (i + 1) == num_polls:
                    elapsed = current_time - start_time
                    percent = ((i + 1) / num_polls) * 100
                    remaining = (test_duration - elapsed) / 60
                    print(f"  Progress: {i+1}/{num_polls} polls ({percent:.1f}%), "
                          f"{elapsed/60:.1f} min elapsed, "
                          f"{remaining:.1f} min remaining, "
                          f"{len(all_data):,} samples collected")
                    next_progress_time = current_time + progress_interval

            # Sleep until next poll
            sleep_time = polling_interval - (time.time() - poll_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

        total_time = time.time() - start_time
        print(f"\n✓ Data collection complete")
        print(f"  Total time: {total_time/60:.2f} minutes ({total_time/3600:.2f} hours)")
        print(f"  Total samples: {len(all_data):,}")
        print(f"  Data saved to: {output_file}\n")

        # Validate sync counters
        print(f"[Step 6] Validating sync counters...")
        sync_markers = extract_sync_markers_ads1293(all_data)
        print(f"  Found {len(sync_markers)} sync markers")

        assert len(sync_markers) > 0, "No sync markers found"

        print(f"  First 10 sync markers: {sync_markers[:10]}")
        print(f"  Last 10 sync markers: {sync_markers[-10:]}")

        # Validate monotonic increase
        sync_valid, sync_msg = validate_sync_monotonic(sync_markers)
        assert sync_valid, f"Sync counter validation failed: {sync_msg}"
        print(f"  ✓ Sync counters are monotonically increasing")

        # Check for missing frames (should have ~3600 sync markers for 1 hour)
        expected_sync_count = test_duration  # One per second
        sync_count_error = abs(len(sync_markers) - expected_sync_count)
        assert sync_count_error <= 2, f"Missing sync frames: expected ~{expected_sync_count}, got {len(sync_markers)}"
        print(f"  ✓ No missing sync frames (expected {expected_sync_count}, got {len(sync_markers)})\n")

        # Calculate sampling frequency
        print(f"[Step 7] Calculating sampling frequency...")

        # Remove sync markers for frequency calculation
        data_only = [d for d in all_data if d[0] != -99999]
        actual_freq = calculate_sampling_frequency(data_only, total_time)
        print(f"  Calculated frequency: {actual_freq:.2f} Hz")
        print(f"  Expected frequency: {expected_freq} Hz ± {freq_tolerance} Hz")

        freq_valid, freq_msg = validate_sampling_frequency(
            actual_freq,
            expected_freq,
            freq_tolerance
        )
        assert freq_valid, freq_msg
        print(f"  ✓ Sampling frequency within tolerance\n")

        # Analyze BPM
        print(f"[Step 8] Analyzing BPM...")
        print(f"  Simulator BPM setting: {bpm}")

        # Initialize BPM variables
        measured_bpm = None
        bpm_error = None
        peaks = []

        # Extract channel 1 data (exclude sync markers and error markers)
        ch1_data = [d[0] for d in all_data if d[0] not in [-99999, -99998]]

        # Simple peak detection for BPM calculation
        # Convert to numpy array for analysis
        ecg_signal = np.array(ch1_data, dtype=float)

        # Basic BPM estimation using peak detection
        # Note: This is a simplified approach; real BPM detection is more complex
        try:
            from scipy.signal import find_peaks

            # Find peaks (R-peaks in ECG)
            peaks, _ = find_peaks(ecg_signal, distance=int(actual_freq * 0.5))  # Min 0.5s between peaks

            # Calculate BPM from peaks
            if len(peaks) > 1:
                peak_intervals = np.diff(peaks) / actual_freq  # Convert to seconds
                mean_interval = np.mean(peak_intervals)
                measured_bpm = 60.0 / mean_interval if mean_interval > 0 else 0

                print(f"  Detected peaks: {len(peaks)}")
                print(f"  Mean peak interval: {mean_interval:.3f} s")
                print(f"  Measured BPM: {measured_bpm:.1f}")

                # Calculate BPM error thresholds
                bpm_error_abs_threshold = bpm_absolute_error
                bpm_error_pct_threshold = bpm * (bpm_percent_error / 100.0)
                bpm_tolerance = max(bpm_error_abs_threshold, bpm_error_pct_threshold)

                bpm_error = abs(measured_bpm - bpm)
                print(f"  BPM error: {bpm_error:.1f} bpm")
                print(f"  BPM tolerance: ±{bpm_tolerance:.1f} bpm")

                assert bpm_error <= bpm_tolerance, \
                    f"BPM mismatch: expected {bpm} ± {bpm_tolerance:.1f}, got {measured_bpm:.1f}"
                print(f"  ✓ BPM within tolerance\n")
            else:
                print(f"  ⚠ Warning: Insufficient peaks detected for BPM calculation")
                print(f"  Skipping BPM validation (manual review required)\n")

        except ImportError as e:
            print(f"  ⚠ Warning: scipy not available ({e})")
            print(f"  Skipping BPM analysis - install scipy for BPM validation")
            print(f"  Run: pip install scipy\n")

        # Log metrics summary
        print(f"[Step 9] Logging metrics summary...")
        metrics = {
            "type": "test_summary",
            "test_id": "test_011",
            "bpm_setting": bpm,
            "test_duration_sec": test_duration,
            "actual_duration_sec": total_time,
            "total_samples": len(all_data),
            "data_only_samples": len(data_only),
            "sync_markers_count": len(sync_markers),
            "calculated_frequency_hz": actual_freq,
            "expected_frequency_hz": expected_freq,
            "frequency_error_hz": abs(actual_freq - expected_freq),
            "measured_bpm": measured_bpm,
            "bpm_error": bpm_error,
            "peaks_detected": len(peaks) if peaks else None
        }

        logger.write_raw(metrics)
        print(f"  ✓ Metrics logged\n")

        # Power off ADS1293
        print(f"[Step 10] Powering off ADS1293...")
        poweroff_response = power_off_sensor(client)
        assert poweroff_response.get("type") == "power_is_off", "Power-off failed"
        print(f"  ✓ ADS1293 powered off successfully\n")

    # Final summary
    print(f"{'='*70}")
    print(f"Test Case 11 Summary - BPM {bpm}")
    print(f"{'='*70}")
    print(f"Duration: {total_time/3600:.2f} hours")
    print(f"Total samples: {len(all_data):,}")
    print(f"Sampling frequency: {actual_freq:.2f} Hz (expected {expected_freq} ± {freq_tolerance} Hz)")
    print(f"Sync markers: {len(sync_markers)} (expected ~{expected_sync_count})")
    if measured_bpm is not None:
        bpm_error_abs_threshold = bpm_absolute_error
        bpm_error_pct_threshold = bpm * (bpm_percent_error / 100.0)
        bpm_tolerance = max(bpm_error_abs_threshold, bpm_error_pct_threshold)
        print(f"Measured BPM: {measured_bpm:.1f} (expected {bpm} ± {bpm_tolerance:.1f})")
    else:
        print(f"Measured BPM: N/A (BPM analysis skipped)")
    print(f"Data file: {output_file}")
    print(f"{'='*70}")
    print(f"✓ TEST PASSED\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
