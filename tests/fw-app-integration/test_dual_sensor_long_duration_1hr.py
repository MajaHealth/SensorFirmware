"""
Test Case 47: Dual Sensor Long-Duration Simultaneous Acquisition (1 Hour)

Category: FW-APP Integration
Components: ADS1293 + MAX30009 + Firmware

Test Steps:
1. Ensure both sensor servers are reachable
2. Configure ADS1293 for 400 Hz and enable conversion
3. Configure MAX30009 for 400 Hz and confirm meas_state sequence
4. Send get_data to both servers every 0.5s for 1 hour
5. Extract sync counters from both streams and verify integrity
6. Compute effective sampling frequency for both sensors
7. Compute drift using sync alignment
8. Power off both sensors

Pass Criteria:
- Both streams show sync counters monotonically increasing every 1 second
- No missing/duplicate sync frames over 1 hour
- Mean sampling frequency for both sensors is 400 Hz ±1 Hz
- Drift is computed and reported
- Poweroff returns power_is_off for both sensors
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


# Sync marker magic numbers
ECG_SYNC_MAGIC = -99999
ICG_SYNC_MAGIC = -999990000
ICG_SCALING_FACTOR = 10000


def drain_async_messages(client, timeout=0.5):
    """Drain async meas_state messages from MAX30009."""
    time.sleep(0.2)
    drained = 0
    while drained < 20:
        try:
            msg = client.recv(timeout=0.1)
            if not msg:
                break
            if msg.get('type') in ['meas_state', 'data']:
                drained += 1
                continue
            break
        except:
            break
    return drained


def send_and_wait_for_response(client, request, expected_type, timeout_attempts=20):
    """Send request and wait for expected response, filtering async messages."""
    import json as json_module

    client.socket.sendall((json_module.dumps(request) + '\n').encode())

    for attempt in range(timeout_attempts):
        try:
            response = client.recv(timeout=0.5)

            if not response:
                time.sleep(0.1)
                continue

            if response.get('type') == expected_type:
                return response

            if response.get('type') in ['meas_state', 'data']:
                continue

            return response

        except Exception:
            continue

    return {"type": "timeout", "error": f"No {expected_type} response"}


@pytest.fixture
def results_dir():
    """
    Create organized results directory structure.

    Standard practice: ~/sensor-test-data/{data,analysis,logs}/{ecg,bioz,drift}/
    """
    base_dir = Path.home() / "sensor-test-data"

    # Create subdirectories
    (base_dir / "data" / "ecg").mkdir(parents=True, exist_ok=True)
    (base_dir / "data" / "bioz").mkdir(parents=True, exist_ok=True)
    (base_dir / "analysis" / "drift").mkdir(parents=True, exist_ok=True)
    (base_dir / "logs").mkdir(parents=True, exist_ok=True)

    return base_dir


@pytest.fixture
def ads1293_client(test_config):
    """Create TCP client for ADS1293 service with cleanup."""
    ads_config = test_config['services']['ads1293']
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        yield client

        # Cleanup: Power off sensor
        try:
            response = client.send({"type": "poweroff"})
            print(f"\n[Cleanup ADS1293] Poweroff response: {response.get('type', 'unknown')}")
        except:
            pass


@pytest.fixture
def max30009_client(test_config):
    """Create TCP client for MAX30009 service with cleanup."""
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        # Drain pending async messages
        drain_async_messages(client)
        yield client

        # Cleanup: Power off sensor
        try:
            response = send_and_wait_for_response(client, {"type": "poweroff"}, "power_is_off")
            print(f"\n[Cleanup MAX30009] Poweroff response: {response.get('type', 'unknown')}")
        except:
            pass


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.max30009
@pytest.mark.long
@pytest.mark.timeout(7200)
def test_dual_sensor_long_duration_1hr(test_config, results_dir, ads1293_client, max30009_client):
    """
    Test Case 47: Dual sensor simultaneous acquisition for 1 hour.

    Validates:
    - Sync counter integrity for both sensors over 3600 syncs
    - Sampling frequency accuracy (400 Hz ±1 Hz) for both
    - No missing or duplicated sync frames
    - Drift measurement between sensors
    - Clean poweroff after extended operation
    """

    # Load test parameters
    ecg_params = test_config['ads1293_ecg']
    icg_params = test_config['max30009_icg']
    thresholds = test_config['thresholds']

    test_duration = ecg_params['long_duration_sec']
    polling_interval = 0.5
    r2_rate = ecg_params['r2_rate']
    r3_rate = ecg_params['r3_rate']
    expected_fs = ecg_params['sampling_frequency']
    freq_tolerance = thresholds['sampling']['frequency_error_hz']
    drift_tolerance = thresholds['sync_counter_tolerance_ms']

    stim_freq_khz = icg_params['stim_frequency_khz']
    stim_current_ua = icg_params['current_ua']

    # Calculate R1_rate for target frequency
    r1_rate = 5

    print(f"\n{'='*70}")
    print(f"Test Case 47: Dual Sensor 1-Hour Simultaneous Acquisition")
    print(f"{'='*70}")
    print(f"Duration: {test_duration} seconds (1 hour)")
    print(f"Polling Interval: {polling_interval}s")
    print(f"Expected Sampling Frequency: {expected_fs} Hz (both sensors)")
    print(f"Expected Syncs: ~{test_duration} per sensor (1 per second)")
    print(f"Drift Tolerance: {drift_tolerance} ms")
    print(f"{'='*70}\n")

    # Create timestamped output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ecg_file = results_dir / "data" / "ecg" / f"test_047_dual_sensor_ecg_{timestamp}.jsonl"
    bioz_file = results_dir / "data" / "bioz" / f"test_047_dual_sensor_bioz_{timestamp}.jsonl"
    drift_file = results_dir / "analysis" / "drift" / f"test_047_drift_analysis_{timestamp}.json"

    print(f"Output Files:")
    print(f"  ECG:   {ecg_file}")
    print(f"  BIOZ:  {bioz_file}")
    print(f"  Drift: {drift_file}\n")

    # Step 1: Verify reachability
    print(f"[Step 1] Verifying sensor server reachability...")

    try:
        ads_status = ads1293_client.send({"type": "get_settings"})
        assert ads_status["type"] == "actual_settings", f"ADS1293 not reachable: {ads_status}"
        print(f"  ✓ ADS1293 service reachable on port 1293")
    except Exception as e:
        pytest.fail(f"ADS1293 service not reachable: {e}")

    try:
        drain_async_messages(max30009_client)
        max_status = send_and_wait_for_response(max30009_client, {"type": "get_settings"}, "actual_settings")
        assert max_status["type"] == "actual_settings", f"MAX30009 not reachable: {max_status}"
        print(f"  ✓ MAX30009 service reachable on port 30009\n")
    except Exception as e:
        pytest.fail(f"MAX30009 service not reachable: {e}")

    # Step 2: Configure ADS1293
    print(f"[Step 2] Configuring ADS1293...")

    ads_settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": r2_rate,
        "R3_rate": r3_rate
    }

    ads_response = ads1293_client.send(ads_settings)
    assert ads_response["type"] == "actual_settings", \
        f"ADS1293 configuration failed: {ads_response}"

    actual_r1 = ads_response.get('R1_rate', r1_rate)
    actual_r2 = ads_response.get('R2_rate', r2_rate)
    actual_r3 = ads_response.get('R3_rate', r3_rate)
    calculated_fs_ecg = 128000 / (actual_r1 * actual_r2 * actual_r3)

    print(f"  ✓ ADS1293 configured")
    print(f"    - R1={actual_r1}, R2={actual_r2}, R3={actual_r3}")
    print(f"    - Calculated sampling frequency: {calculated_fs_ecg:.1f} Hz\n")

    # Step 3: Configure MAX30009
    print(f"[Step 3] Configuring MAX30009...")

    drain_async_messages(max30009_client)

    max_settings = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": stim_freq_khz * 1000,
        "measure_frequency": expected_fs,
        "stimulate_current": f"{stim_current_ua}uA"
    }

    max_response = send_and_wait_for_response(max30009_client, max_settings, "actual_settings")
    assert max_response["type"] == "actual_settings", \
        f"MAX30009 configuration failed: {max_response}"

    print(f"  ✓ MAX30009 configured")
    print(f"    - Measurement frequency: {max_response['measure_frequency']} Hz")
    print(f"    - Stimulation: {stim_freq_khz} kHz, {stim_current_ua} µA\n")

    drain_async_messages(max30009_client)

    # Step 4: Stabilization
    print(f"[Step 4] Waiting for sensor stabilization...")
    time.sleep(2.0)
    print(f"  ✓ Sensors ready\n")

    # Step 5: Flush buffers
    print(f"[Step 5] Flushing accumulated buffers...")

    # Flush ADS1293
    total_flushed_ecg = 0
    for attempt in range(3):
        flush_response = ads1293_client.send({"type": "get_data"})
        if flush_response["type"] == "data":
            flushed_count = len(flush_response["data"])
            total_flushed_ecg += flushed_count
            if flushed_count > 0:
                print(f"  ADS1293 flush attempt {attempt + 1}: {flushed_count} samples")
            time.sleep(0.2)

    # Flush MAX30009
    total_flushed_bioz = 0
    drain_async_messages(max30009_client)
    for attempt in range(3):
        flush_response = send_and_wait_for_response(max30009_client, {"type": "get_data"}, "data")
        if flush_response["type"] == "data":
            flushed_count = len(flush_response["data"])
            total_flushed_bioz += flushed_count
            if flushed_count > 0:
                print(f"  MAX30009 flush attempt {attempt + 1}: {flushed_count} samples")
            time.sleep(0.2)

    print(f"  ✓ ADS1293: Flushed {total_flushed_ecg} samples")
    print(f"  ✓ MAX30009: Flushed {total_flushed_bioz} samples\n")

    # Step 6: Collect data for 1 hour
    print(f"[Step 6] Collecting simultaneous data for {test_duration} seconds (1 hour)...")
    print(f"  Polling both sensors every {polling_interval}s")
    print(f"  Expected polls: {int(test_duration / polling_interval)} per sensor")
    print(f"  Progress updates every 5 minutes\n")

    # Initialize loggers
    ecg_logger = JSONLLogger(str(ecg_file), test_id="test_047", sensor="ads1293")
    bioz_logger = JSONLLogger(str(bioz_file), test_id="test_047", sensor="max30009")

    # Write metadata
    ecg_metadata = {
        "type": "metadata",
        "test_case": "TC-047",
        "test_name": "Dual sensor 1-hour simultaneous acquisition",
        "sensor": "ads1293",
        "duration_sec": test_duration,
        "polling_interval_sec": polling_interval,
        "expected_fs": expected_fs,
        "r1_rate": actual_r1,
        "r2_rate": actual_r2,
        "r3_rate": actual_r3,
        "calculated_fs": calculated_fs_ecg,
        "start_time": time.time()
    }
    ecg_logger.write_raw(ecg_metadata)

    bioz_metadata = {
        "type": "metadata",
        "test_case": "TC-047",
        "test_name": "Dual sensor 1-hour simultaneous acquisition",
        "sensor": "max30009",
        "duration_sec": test_duration,
        "polling_interval_sec": polling_interval,
        "expected_fs": expected_fs,
        "stim_frequency_khz": stim_freq_khz,
        "stim_current_ua": stim_current_ua,
        "start_time": time.time()
    }
    bioz_logger.write_raw(bioz_metadata)

    # Collection loop
    num_polls = int(test_duration / polling_interval)
    ecg_samples = []
    bioz_samples = []
    ecg_syncs = []
    bioz_syncs = []
    ecg_sync_timestamps = {}
    bioz_sync_timestamps = {}

    collection_start = time.time()
    last_progress_time = collection_start

    for poll_num in range(num_polls):
        poll_start = time.time()

        # Poll ADS1293
        t_ecg_start = time.time()
        ecg_response = ads1293_client.send({"type": "get_data"})
        t_ecg_end = time.time()
        t_ecg = (t_ecg_start + t_ecg_end) / 2.0

        assert ecg_response["type"] == "data", \
            f"Poll {poll_num} ADS1293: Expected 'data', got '{ecg_response.get('type')}'"

        ecg_data = ecg_response["data"]

        # Log ECG data
        ecg_logger.write_data(
            data=ecg_data,
            metadata={
                "poll_num": poll_num,
                "timestamp": t_ecg,
                "sample_count": len(ecg_data)
            }
        )

        # Extract ECG sync markers
        for sample in ecg_data:
            if sample[0] == ECG_SYNC_MAGIC:
                sync_num = sample[1]
                ecg_syncs.append(sample)
                if sync_num not in ecg_sync_timestamps:
                    ecg_sync_timestamps[sync_num] = t_ecg
            else:
                ecg_samples.append(sample)

        # Poll MAX30009
        drain_async_messages(max30009_client)
        t_bioz_start = time.time()
        bioz_response = send_and_wait_for_response(max30009_client, {"type": "get_data"}, "data")
        t_bioz_end = time.time()
        t_bioz = (t_bioz_start + t_bioz_end) / 2.0

        assert bioz_response["type"] == "data", \
            f"Poll {poll_num} MAX30009: Expected 'data', got '{bioz_response.get('type')}'"

        bioz_data = bioz_response["data"]

        # Log BIOZ data
        bioz_logger.write_data(
            data=bioz_data,
            metadata={
                "poll_num": poll_num,
                "timestamp": t_bioz,
                "sample_count": len(bioz_data)
            }
        )

        # Extract BIOZ sync markers
        for sample in bioz_data:
            if sample[0] == ICG_SYNC_MAGIC:
                sync_num = sample[1] // ICG_SCALING_FACTOR
                bioz_syncs.append(sample)
                if sync_num not in bioz_sync_timestamps:
                    bioz_sync_timestamps[sync_num] = t_bioz
            else:
                bioz_samples.append(sample)

        # Progress update every 5 minutes
        elapsed = time.time() - collection_start
        if elapsed - (last_progress_time - collection_start) >= 300:
            progress_pct = (poll_num / num_polls) * 100
            print(f"  Progress: {progress_pct:.1f}% ({poll_num}/{num_polls} polls) - "
                  f"Elapsed: {elapsed/60:.1f} min")
            print(f"    ECG: {len(ecg_samples)} samples, {len(ecg_syncs)} syncs")
            print(f"    BIOZ: {len(bioz_samples)} samples, {len(bioz_syncs)} syncs")
            last_progress_time = time.time()

        # Maintain polling interval
        poll_duration = time.time() - poll_start
        sleep_time = polling_interval - poll_duration
        if sleep_time > 0:
            time.sleep(sleep_time)

    collection_end = time.time()
    actual_duration = collection_end - collection_start

    ecg_logger.close()
    bioz_logger.close()

    print(f"\n  ✓ Collection complete")
    print(f"    - Actual duration: {actual_duration:.2f}s ({actual_duration/60:.2f} min)")
    print(f"    - ECG: {len(ecg_samples)} samples, {len(ecg_syncs)} syncs")
    print(f"    - BIOZ: {len(bioz_samples)} samples, {len(bioz_syncs)} syncs\n")

    # Step 7: Validate ADS1293 sync sequence
    print(f"[Step 7] Validating ADS1293 sync sequence...")

    ecg_sync_numbers = [marker[1] for marker in ecg_syncs]

    assert len(ecg_syncs) >= test_duration - 2, \
        f"ADS1293: Expected ~{test_duration} sync markers, got {len(ecg_syncs)}"

    # Monotonically increasing
    for i in range(len(ecg_sync_numbers) - 1):
        assert ecg_sync_numbers[i] < ecg_sync_numbers[i+1], \
            f"ADS1293: Sync not monotonic at index {i}"

    # Consecutive (no gaps)
    missing_ecg = []
    for i in range(len(ecg_sync_numbers) - 1):
        diff = ecg_sync_numbers[i+1] - ecg_sync_numbers[i]
        if diff != 1:
            missing_ecg.append((ecg_sync_numbers[i], ecg_sync_numbers[i+1]))

    assert len(missing_ecg) == 0, f"ADS1293: Missing sync frames: {missing_ecg}"

    # No duplicates
    assert len(ecg_sync_numbers) == len(set(ecg_sync_numbers)), \
        f"ADS1293: Duplicated sync frames"

    print(f"  ✓ ADS1293 sync validation passed")
    print(f"    - Sync count: {len(ecg_syncs)}")
    print(f"    - Sync range: {ecg_sync_numbers[0]} to {ecg_sync_numbers[-1]}")
    print(f"    - Monotonic: Yes")
    print(f"    - Consecutive: Yes")
    print(f"    - Duplicates: None\n")

    # Step 8: Validate MAX30009 sync sequence
    print(f"[Step 8] Validating MAX30009 sync sequence...")

    bioz_sync_numbers = [marker[1] // ICG_SCALING_FACTOR for marker in bioz_syncs]

    assert len(bioz_syncs) >= test_duration - 2, \
        f"MAX30009: Expected ~{test_duration} sync markers, got {len(bioz_syncs)}"

    # Monotonically increasing
    for i in range(len(bioz_sync_numbers) - 1):
        assert bioz_sync_numbers[i] < bioz_sync_numbers[i+1], \
            f"MAX30009: Sync not monotonic at index {i}"

    # Consecutive (no gaps)
    missing_bioz = []
    for i in range(len(bioz_sync_numbers) - 1):
        diff = bioz_sync_numbers[i+1] - bioz_sync_numbers[i]
        if diff != 1:
            missing_bioz.append((bioz_sync_numbers[i], bioz_sync_numbers[i+1]))

    assert len(missing_bioz) == 0, f"MAX30009: Missing sync frames: {missing_bioz}"

    # No duplicates
    assert len(bioz_sync_numbers) == len(set(bioz_sync_numbers)), \
        f"MAX30009: Duplicated sync frames"

    print(f"  ✓ MAX30009 sync validation passed")
    print(f"    - Sync count: {len(bioz_syncs)}")
    print(f"    - Sync range: {bioz_sync_numbers[0]} to {bioz_sync_numbers[-1]}")
    print(f"    - Monotonic: Yes")
    print(f"    - Consecutive: Yes")
    print(f"    - Duplicates: None\n")

    # Write sync summaries to JSONL files
    with open(ecg_file, 'a') as f:
        ecg_sync_summary = {
            "type": "sync_summary",
            "sync_count": len(ecg_syncs),
            "sync_range": [ecg_sync_numbers[0], ecg_sync_numbers[-1]],
            "missing_frames": missing_ecg,
            "duplicate_count": len(ecg_sync_numbers) - len(set(ecg_sync_numbers))
        }
        f.write(json.dumps(ecg_sync_summary) + '\n')

    with open(bioz_file, 'a') as f:
        bioz_sync_summary = {
            "type": "sync_summary",
            "sync_count": len(bioz_syncs),
            "sync_range": [bioz_sync_numbers[0], bioz_sync_numbers[-1]],
            "missing_frames": missing_bioz,
            "duplicate_count": len(bioz_sync_numbers) - len(set(bioz_sync_numbers))
        }
        f.write(json.dumps(bioz_sync_summary) + '\n')

    # Step 9: Validate sampling frequencies
    print(f"[Step 9] Validating sampling frequencies...")

    # ADS1293
    ecg_duration_measured = len(ecg_syncs)
    ecg_fs_measured = len(ecg_samples) / ecg_duration_measured
    ecg_fs_error = abs(ecg_fs_measured - expected_fs)

    print(f"  ADS1293:")
    print(f"    - Total samples: {len(ecg_samples)}")
    print(f"    - Duration (syncs): {ecg_duration_measured}s")
    print(f"    - Measured Fs: {ecg_fs_measured:.2f} Hz")
    print(f"    - Expected: {expected_fs} Hz ± {freq_tolerance} Hz")
    print(f"    - Error: {ecg_fs_error:.2f} Hz")

    assert ecg_fs_error <= freq_tolerance, \
        f"ADS1293: Fs error {ecg_fs_error:.2f} Hz exceeds tolerance {freq_tolerance} Hz"

    print(f"    ✓ Within tolerance\n")

    # MAX30009
    bioz_duration_measured = len(bioz_syncs)
    bioz_fs_measured = len(bioz_samples) / bioz_duration_measured
    bioz_fs_error = abs(bioz_fs_measured - expected_fs)

    print(f"  MAX30009:")
    print(f"    - Total samples: {len(bioz_samples)}")
    print(f"    - Duration (syncs): {bioz_duration_measured}s")
    print(f"    - Measured Fs: {bioz_fs_measured:.2f} Hz")
    print(f"    - Expected: {expected_fs} Hz ± {freq_tolerance} Hz")
    print(f"    - Error: {bioz_fs_error:.2f} Hz")

    assert bioz_fs_error <= freq_tolerance, \
        f"MAX30009: Fs error {bioz_fs_error:.2f} Hz exceeds tolerance {freq_tolerance} Hz"

    print(f"    ✓ Within tolerance\n")

    # Step 10: Calculate drift
    print(f"[Step 10] Calculating sync marker drift...")

    # Find common sync_num values
    ecg_sync_set = set(ecg_sync_numbers)
    bioz_sync_set = set(bioz_sync_numbers)
    common_sync_nums = ecg_sync_set & bioz_sync_set

    assert len(common_sync_nums) >= test_duration - 10, \
        f"Too few common sync markers: {len(common_sync_nums)} (expected ~{test_duration})"

    print(f"  Common sync markers: {len(common_sync_nums)}")

    # Calculate drift for each common sync
    drift_data = []
    for sync_num in sorted(common_sync_nums):
        t_ecg = ecg_sync_timestamps[sync_num]
        t_bioz = bioz_sync_timestamps[sync_num]
        drift_ms = abs(t_ecg - t_bioz) * 1000.0

        drift_data.append({
            "sync_num": sync_num,
            "ecg_timestamp": t_ecg,
            "bioz_timestamp": t_bioz,
            "drift_ms": drift_ms
        })

    # Drift statistics
    drift_values = [d["drift_ms"] for d in drift_data]
    max_drift = max(drift_values)
    mean_drift = sum(drift_values) / len(drift_values)

    # Calculate standard deviation
    variance = sum((x - mean_drift) ** 2 for x in drift_values) / len(drift_values)
    std_drift = variance ** 0.5

    # Calculate median
    sorted_drifts = sorted(drift_values)
    n = len(sorted_drifts)
    median_drift = sorted_drifts[n // 2] if n % 2 == 1 else (sorted_drifts[n // 2 - 1] + sorted_drifts[n // 2]) / 2

    print(f"  Drift Statistics:")
    print(f"    - Max drift: {max_drift:.2f} ms")
    print(f"    - Mean drift: {mean_drift:.2f} ms")
    print(f"    - Std drift: {std_drift:.2f} ms")
    print(f"    - Median drift: {median_drift:.2f} ms")
    print(f"    - Tolerance: {drift_tolerance} ms")

    assert max_drift < drift_tolerance, \
        f"Max drift {max_drift:.2f}ms exceeds tolerance {drift_tolerance}ms"

    print(f"    ✓ Drift within tolerance\n")

    # Write drift analysis
    drift_analysis = {
        "test_case": "TC-047",
        "test_name": "Dual sensor 1-hour simultaneous acquisition",
        "timestamp": timestamp,
        "common_sync_count": len(common_sync_nums),
        "ecg_sync_range": [ecg_sync_numbers[0], ecg_sync_numbers[-1]],
        "bioz_sync_range": [bioz_sync_numbers[0], bioz_sync_numbers[-1]],
        "drift_statistics": {
            "max_drift_ms": max_drift,
            "mean_drift_ms": mean_drift,
            "std_drift_ms": std_drift,
            "median_drift_ms": median_drift,
            "tolerance_ms": drift_tolerance
        },
        "drift_samples": drift_data[:100]  # First 100 samples for reference
    }

    with open(drift_file, 'w') as f:
        json.dump(drift_analysis, f, indent=2)

    print(f"  ✓ Drift analysis saved to: {drift_file}\n")

    # Step 11: Power off both sensors
    print(f"[Step 11] Powering off both sensors...")

    # Power off ADS1293
    ecg_poweroff = ads1293_client.send({"type": "poweroff"})
    assert ecg_poweroff["type"] == "power_is_off", \
        f"ADS1293: Expected 'power_is_off', got '{ecg_poweroff.get('type')}'"
    print(f"  ✓ ADS1293 powered off")

    # Power off MAX30009
    drain_async_messages(max30009_client)
    bioz_poweroff = send_and_wait_for_response(max30009_client, {"type": "poweroff"}, "power_is_off")
    assert bioz_poweroff["type"] == "power_is_off", \
        f"MAX30009: Expected 'power_is_off', got '{bioz_poweroff.get('type')}'"
    print(f"  ✓ MAX30009 powered off\n")

    # Write final metadata
    with open(ecg_file, 'a') as f:
        final_ecg_metadata = {
            "type": "metadata",
            "test_result": "PASS",
            "actual_duration_sec": actual_duration,
            "total_samples": len(ecg_samples),
            "total_syncs": len(ecg_syncs),
            "measured_fs": ecg_fs_measured,
            "fs_error": ecg_fs_error,
            "sync_range": [ecg_sync_numbers[0], ecg_sync_numbers[-1]],
            "end_time": collection_end
        }
        f.write(json.dumps(final_ecg_metadata) + '\n')

    with open(bioz_file, 'a') as f:
        final_bioz_metadata = {
            "type": "metadata",
            "test_result": "PASS",
            "actual_duration_sec": actual_duration,
            "total_samples": len(bioz_samples),
            "total_syncs": len(bioz_syncs),
            "measured_fs": bioz_fs_measured,
            "fs_error": bioz_fs_error,
            "sync_range": [bioz_sync_numbers[0], bioz_sync_numbers[-1]],
            "end_time": collection_end
        }
        f.write(json.dumps(final_bioz_metadata) + '\n')

    # Summary
    print(f"{'='*70}")
    print(f"Test Summary - TC-047")
    print(f"{'='*70}")
    print(f"Duration:              {actual_duration:.2f}s ({actual_duration/60:.2f} min)")
    print(f"")
    print(f"ADS1293 (ECG):")
    print(f"  Total Samples:       {len(ecg_samples)}")
    print(f"  Total Syncs:         {len(ecg_syncs)}")
    print(f"  Sync Range:          {ecg_sync_numbers[0]} to {ecg_sync_numbers[-1]}")
    print(f"  Measured Fs:         {ecg_fs_measured:.2f} Hz")
    print(f"  Fs Error:            {ecg_fs_error:.2f} Hz")
    print(f"")
    print(f"MAX30009 (BIOZ):")
    print(f"  Total Samples:       {len(bioz_samples)}")
    print(f"  Total Syncs:         {len(bioz_syncs)}")
    print(f"  Sync Range:          {bioz_sync_numbers[0]} to {bioz_sync_numbers[-1]}")
    print(f"  Measured Fs:         {bioz_fs_measured:.2f} Hz")
    print(f"  Fs Error:            {bioz_fs_error:.2f} Hz")
    print(f"")
    print(f"Synchronization:")
    print(f"  Common Syncs:        {len(common_sync_nums)}")
    print(f"  Max Drift:           {max_drift:.2f} ms")
    print(f"  Mean Drift:          {mean_drift:.2f} ms")
    print(f"  Tolerance:           {drift_tolerance} ms")
    print(f"")
    print(f"Output Files:")
    print(f"  ECG Data:            {ecg_file}")
    print(f"  BIOZ Data:           {bioz_file}")
    print(f"  Drift Analysis:      {drift_file}")
    print(f"")
    print(f"Result:                PASS ✓")
    print(f"{'='*70}\n")
