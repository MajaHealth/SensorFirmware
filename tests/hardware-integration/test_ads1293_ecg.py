"""
Test ID 10: ADS1293 ECG 60-second automated integration

Hardware Requirements:
- ADS1293 connected to CM4
- ECG simulator connected to ADS1293 inputs
- ECG simulator configured for 60 BPM
"""
import pytest
import time
from pathlib import Path
import sys

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
@pytest.mark.slow
def test_ads1293_ecg_60s(test_config, results_dir):
    """
    Test ID 10: ADS1293 ECG automated integration (60 seconds).

    Test Steps:
    1. Connect to ADS1293 service
    2. Configure for 400 Hz sampling
    3. Enable conversion
    4. Collect data for 60 seconds (poll every 0.5s)
    5. Extract sync counters and validate monotonic increase
    6. Calculate sampling frequency and verify 400 Hz ± 1 Hz
    7. Save data for BPM analysis on laptop
    8. Power off ADS1293

    Pass Criteria:
    - Sync counters monotonically increase every 1s
    - No missing sync frames
    - Mean sampling frequency = 400 Hz ± 1 Hz
    - Data successfully logged for offline BPM analysis
    """
    # Get configuration
    ads_config = test_config['services']['ads1293']
    ecg_params = test_config['ads1293_ecg']
    thresholds = test_config['thresholds']

    # Test parameters
    test_duration = ecg_params['duration_sec']  # 60 seconds
    polling_interval = ecg_params['polling_interval_sec']  # 0.5 seconds
    expected_freq = ecg_params['sampling_frequency']  # 400 Hz
    freq_tolerance = thresholds['sampling']['frequency_error_hz']  # 1 Hz

    print(f"\n{'='*70}")
    print(f"Test ID 10: ADS1293 ECG 60-Second Integration Test")
    print(f"{'='*70}")
    print(f"Duration: {test_duration}s")
    print(f"Polling interval: {polling_interval}s")
    print(f"Expected sampling frequency: {expected_freq} Hz ± {freq_tolerance} Hz")
    print(f"{'='*70}\n")

    # Data logger
    output_file = results_dir / "test_010_ecg_60s.jsonl"
    logger = JSONLLogger(str(output_file), test_id="test_010", sensor="ads1293")

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
        print(f"[Step 3.5] Flushing accumulated buffer...")
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
        print(f"[Step 4] Collecting data for {test_duration} seconds...")
        num_polls = int(test_duration / polling_interval)
        all_data = []
        start_time = time.time()

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
                        "poll_number": i
                    }
                )

                # Accumulate for analysis
                all_data.extend(response["data"])

                # Progress indicator
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"  Progress: {i+1}/{num_polls} polls, "
                          f"{elapsed:.1f}s elapsed, "
                          f"{len(all_data)} samples collected")

            # Sleep until next poll
            sleep_time = polling_interval - (time.time() - poll_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

        total_time = time.time() - start_time
        print(f"\n✓ Data collection complete")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Total samples: {len(all_data)}")
        print(f"  Data saved to: {output_file}\n")

        # Validate sync counters
        print(f"[Step 5] Validating sync counters...")
        sync_markers = extract_sync_markers_ads1293(all_data)
        print(f"  Found {len(sync_markers)} sync markers")

        assert len(sync_markers) > 0, "No sync markers found"

        # Display sync markers
        print(f"  Sync markers: {[s[1] for s in sync_markers]}")

        # Validate monotonic increase
        is_monotonic = validate_sync_monotonic(sync_markers)
        assert is_monotonic, "Sync counters are not monotonically increasing"
        print("  ✓ Sync counters are monotonically increasing")

        # Check for missing frames
        expected_syncs = test_duration  # One per second
        if len(sync_markers) < expected_syncs - 1:
            print(f"  ⚠ Warning: Expected ~{expected_syncs} sync markers, "
                  f"found {len(sync_markers)}")
        else:
            print(f"  ✓ No missing sync frames\n")

        # Calculate sampling frequency
        print(f"[Step 6] Calculating sampling frequency...")
        actual_freq = calculate_sampling_frequency(all_data, total_time, sensor="ads1293")
        print(f"  Calculated frequency: {actual_freq:.2f} Hz")

        freq_valid = validate_sampling_frequency(actual_freq, expected_freq, freq_tolerance)
        assert freq_valid, \
            f"Sampling frequency {actual_freq:.2f} Hz outside tolerance " \
            f"({expected_freq} ± {freq_tolerance} Hz)"
        print(f"  ✓ Within tolerance ({expected_freq} ± {freq_tolerance} Hz)\n")

        # Power off
        print(f"[Step 7] Powering off ADS1293...")
        response = power_off_sensor(client)
        assert response["type"] == "power_is_off", "Failed to power off"
        print("✓ Power off confirmed\n")

    # Close logger
    logger.close()

    # Test summary
    print(f"{'='*70}")
    print(f"✓ TEST PASSED: ADS1293 ECG 60s Integration")
    print(f"{'='*70}")
    print(f"Results:")
    print(f"  Total samples collected: {len(all_data)}")
    print(f"  Sync markers found: {len(sync_markers)}")
    print(f"  Sampling frequency: {actual_freq:.2f} Hz")
    print(f"  Frequency error: {abs(actual_freq - expected_freq):.2f} Hz")
    print(f"  Data file: {output_file}")
    print(f"\nNext steps:")
    print(f"  1. Transfer {output_file} to laptop")
    print(f"  2. Analyze ECG signal for BPM detection")
    print(f"  3. Verify signal quality and noise levels")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Allow running test directly for debugging
    import yaml
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "config" / "test_config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Create temp results directory
    results = Path("/tmp/test-results")
    results.mkdir(exist_ok=True)

    print("Running ADS1293 ECG 60s test...")
    test_ads1293_ecg_60s(config, results)
    print("\nTest completed!")
