"""
MAX30009 Long-Duration Sampling Frequency Validation (400 Hz, 1 Hour)

Validates long-term stability and sampling frequency accuracy over 1-hour
continuous measurement with resistive load.

Configuration: Pulled from test_config.yaml (modular)
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from data_logger import JSONLLogger
from validators import validate_sampling_frequency, validate_sync_monotonic


ICG_SYNC_MAGIC = -999990000
ICG_SCALING_FACTOR = 10000


def drain_async_messages(client):
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
    import json

    client.socket.sendall((json.dumps(request) + '\n').encode())

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
def max30009_client(test_config, max30009_cleanup):
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        drain_async_messages(client)
        yield client


@pytest.mark.hardware
@pytest.mark.max30009
@pytest.mark.long
@pytest.mark.timeout(7200)
def test_max30009_long_duration_400hz(test_config, results_dir, max30009_client):
    """
    1-hour MAX30009 measurement at 400 Hz with resistive load.

    Pass criteria:
    - Sync markers monotonically increasing every 1s
    - Mean sampling frequency = 400 Hz ± 1 Hz
    - Poweroff returns power_is_off
    """

    icg_params = test_config['max30009_icg']
    thresholds = test_config['thresholds']

    test_duration = icg_params['long_duration_sec']
    polling_interval = icg_params['polling_interval_sec']
    expected_freq = icg_params['sampling_frequency']
    freq_tolerance = thresholds['sampling']['frequency_error_hz']
    stim_freq_khz = icg_params['stim_frequency_khz']
    stim_current_ua = icg_params['current_ua']

    print(f"\n{'='*70}")
    print(f"MAX30009 Long-Duration Test (400 Hz, 1 Hour)")
    print(f"{'='*70}")
    print(f"Duration: {test_duration}s ({test_duration/3600:.1f} hour)")
    print(f"Polling interval: {polling_interval}s")
    print(f"Expected frequency: {expected_freq} Hz ± {freq_tolerance} Hz")
    print(f"Stimulation: {stim_freq_khz} kHz, {stim_current_ua} µA")
    print(f"{'='*70}\n")

    output_file = results_dir / "test_max30009_1hr_400hz.jsonl"
    logger = JSONLLogger(
        str(output_file),
        test_id="test_max30009_1hr_400hz",
        sensor="max30009"
    )

    logger.write_raw({
        "type": "test_metadata",
        "test_id": "test_max30009_1hr_400hz",
        "duration_sec": test_duration,
        "expected_frequency_hz": expected_freq,
        "stim_frequency_khz": stim_freq_khz,
        "stim_current_ua": stim_current_ua,
        "polling_interval_sec": polling_interval
    })

    print(f"[Step 1] Configuring MAX30009...")

    drain_async_messages(max30009_client)

    settings = {
        "type": "settings",
        "measure_enable": True,
        "measure_frequency": expected_freq,
        "stimulate_frequency": stim_freq_khz * 1000,
        "stimulate_current": f"{int(stim_current_ua)}uA"
    }

    response = send_and_wait_for_response(max30009_client, settings, "actual_settings")
    assert response["type"] == "actual_settings", f"Config failed: {response}"

    print(f"  ✓ Configuration:")
    print(f"    Sampling: {expected_freq} Hz")
    print(f"    Stimulation: {stim_freq_khz} kHz, {stim_current_ua} µA")

    drain_async_messages(max30009_client)

    print(f"\n[Step 2] Stabilization (3 seconds)...")
    time.sleep(3.0)

    print(f"\n[Step 3] Flushing buffer...")
    for attempt in range(3):
        drain_async_messages(max30009_client)
        flush = send_and_wait_for_response(max30009_client, {"type": "get_data"}, "data")
        if flush["type"] == "data" and len(flush["data"]) > 0:
            print(f"  Flush {attempt + 1}: {len(flush['data'])} samples")
        time.sleep(0.2)

    print(f"\n[Step 4] Collecting data ({test_duration}s = 1 hour)...")
    print(f"  Progress updates every 5 minutes\n")

    num_polls = int(test_duration / polling_interval)
    all_data = []
    start_time = time.time()

    for poll_num in range(num_polls):
        poll_start = time.time()

        drain_async_messages(max30009_client)
        response = send_and_wait_for_response(max30009_client, {"type": "get_data"}, "data")

        if response["type"] == "data":
            logger.write_data(
                data=response["data"],
                metadata={
                    "poll_number": poll_num,
                    "elapsed_time": time.time() - start_time
                }
            )
            all_data.extend(response["data"])

            if (poll_num + 1) % 600 == 0:
                elapsed_min = (time.time() - start_time) / 60.0
                print(f"  {elapsed_min:.1f} min - {len(all_data)} samples")

        sleep_time = polling_interval - (time.time() - poll_start)
        if sleep_time > 0:
            time.sleep(sleep_time)

    total_time = time.time() - start_time

    print(f"\n  ✓ Collection complete:")
    print(f"    Duration: {total_time:.2f}s")
    print(f"    Total samples: {len(all_data)}")

    print(f"\n[Step 5] Extracting sync markers...")

    sync_markers = []
    for idx, sample in enumerate(all_data):
        if sample[0] == ICG_SYNC_MAGIC:
            sync_num = sample[1] // ICG_SCALING_FACTOR
            sync_markers.append((idx, sync_num))

    print(f"  ✓ Found {len(sync_markers)} sync markers")

    expected_syncs = int(test_duration)
    assert len(sync_markers) >= expected_syncs - 10, \
        f"Too few syncs: expected ~{expected_syncs}, got {len(sync_markers)}"
    assert len(sync_markers) <= expected_syncs + 10, \
        f"Too many syncs: expected ~{expected_syncs}, got {len(sync_markers)}"

    print(f"\n[Step 6] Validating sync sequence...")

    sync_nums = [s[1] for s in sync_markers]

    is_monotonic = validate_sync_monotonic(sync_markers)
    assert is_monotonic, "Syncs not monotonic"
    print(f"  ✓ Monotonic")

    for i in range(len(sync_nums) - 1):
        diff = sync_nums[i+1] - sync_nums[i]
        assert diff == 1, f"Gap at sync {sync_nums[i]} → {sync_nums[i+1]}"
    print(f"  ✓ Consecutive (no gaps)")

    assert len(sync_nums) == len(set(sync_nums)), "Duplicate syncs"
    print(f"  ✓ No duplicates")

    print(f"\n[Step 7] Sampling frequency validation...")

    data_samples = len(all_data) - len(sync_markers)
    measured_fs = data_samples / total_time

    print(f"  Data samples: {data_samples}")
    print(f"  Duration: {total_time:.2f}s")
    print(f"  Measured: {measured_fs:.2f} Hz")
    print(f"  Expected: {expected_freq} ± {freq_tolerance} Hz")

    freq_valid = validate_sampling_frequency(measured_fs, expected_freq, freq_tolerance)
    assert freq_valid, \
        f"Frequency {measured_fs:.2f} Hz out of tolerance"
    print(f"  ✓ Within tolerance")

    print(f"\n[Step 8] Powering off...")

    drain_async_messages(max30009_client)
    poweroff = send_and_wait_for_response(max30009_client, {"type": "poweroff"}, "power_is_off")
    assert poweroff["type"] == "power_is_off", f"Poweroff failed: {poweroff}"
    print(f"  ✓ Power off confirmed")

    logger.close()

    print(f"\n{'='*70}")
    print(f"✓ TEST PASSED")
    print(f"{'='*70}")
    print(f"  Samples: {data_samples}")
    print(f"  Syncs: {len(sync_markers)}")
    print(f"  Frequency: {measured_fs:.2f} Hz (error: {abs(measured_fs - expected_freq):.2f} Hz)")
    print(f"  Data: {output_file}")
    print(f"{'='*70}\n")
