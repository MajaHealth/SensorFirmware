"""
Test Case 43: Dual Sensor Sync Marker Temporal Alignment

Validates that sync markers with common sync_num values appear in ECG and ICG
streams within 50ms of each other (laptop-side timestamp measurement).
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


ECG_SYNC_MAGIC = -99999
ICG_SYNC_MAGIC = -999990000
ICG_SCALING_FACTOR = 10000
TIMESTAMP_THRESHOLD_MS = 50.0


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
def ads1293_client(test_config):
    ads_config = test_config['services']['ads1293']
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        yield client
        try:
            client.send({"type": "poweroff"})
            time.sleep(0.2)
        except:
            pass


@pytest.fixture
def max30009_client(test_config, max30009_cleanup):
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        drain_async_messages(client)
        yield client


@pytest.mark.fw_app
@pytest.mark.quick
@pytest.mark.ads1293
@pytest.mark.max30009
def test_sync_marker_temporal_alignment(ads1293_client, max30009_client):
    """
    Test Case 43: Verify temporal alignment of sync markers between ECG and ICG.

    Pass criteria: Max time delta for common sync_num < 50ms
    """

    print(f"\n{'='*70}")
    print(f"Test Case 43: Sync Marker Temporal Alignment")
    print(f"{'='*70}")

    # Configure ADS1293
    print(f"\n[Step 1] Configuring ADS1293...")

    ads_settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": 4,
        "R3_rate": 16
    }

    ads_response = ads1293_client.send(ads_settings)
    assert ads_response["type"] == "actual_settings"
    print(f"  ✓ ADS1293 configured")

    # Configure MAX30009
    print(f"\n[Step 2] Configuring MAX30009...")

    drain_async_messages(max30009_client)

    max_settings = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    max_response = send_and_wait_for_response(max30009_client, max_settings, "actual_settings")
    assert max_response["type"] == "actual_settings"
    print(f"  ✓ MAX30009 configured")

    drain_async_messages(max30009_client)

    # Stabilization
    print(f"\n[Step 3] Waiting for sensor stabilization...")
    time.sleep(2.0)

    # Flush buffers
    print(f"\n[Step 4] Flushing initial buffers...")

    ads_flush = ads1293_client.send({"type": "get_data"})
    assert ads_flush["type"] == "data"
    print(f"  ✓ ADS1293 flushed")

    drain_async_messages(max30009_client)
    max_flush = send_and_wait_for_response(max30009_client, {"type": "get_data"}, "data")
    assert max_flush["type"] == "data"
    print(f"  ✓ MAX30009 flushed")

    # Collect timestamped data
    print(f"\n[Step 5] Collecting timestamped data for 12 seconds...")

    ecg_timestamps = []
    icg_timestamps = []

    test_duration = 12
    poll_interval = 1.0
    num_polls = int(test_duration / poll_interval)

    for poll in range(num_polls):
        poll_start = time.time()

        # Poll ADS1293
        t_ecg_start = time.time()
        ecg_response = ads1293_client.send({"type": "get_data"})
        t_ecg_end = time.time()
        t_ecg = (t_ecg_start + t_ecg_end) / 2.0

        if ecg_response["type"] == "data":
            ecg_syncs = [s[1] for s in ecg_response["data"] if s[0] == ECG_SYNC_MAGIC]
            for sync_num in ecg_syncs:
                ecg_timestamps.append((sync_num, t_ecg))

        # Poll MAX30009
        drain_async_messages(max30009_client)
        t_icg_start = time.time()
        icg_response = send_and_wait_for_response(max30009_client, {"type": "get_data"}, "data")
        t_icg_end = time.time()
        t_icg = (t_icg_start + t_icg_end) / 2.0

        if icg_response["type"] == "data":
            icg_syncs = [s[1] // ICG_SCALING_FACTOR for s in icg_response["data"] if s[0] == ICG_SYNC_MAGIC]
            for sync_num in icg_syncs:
                icg_timestamps.append((sync_num, t_icg))

        # Maintain poll interval
        elapsed = time.time() - poll_start
        if elapsed < poll_interval:
            time.sleep(poll_interval - elapsed)

    print(f"  ✓ Collected {len(ecg_timestamps)} ECG sync timestamps")
    print(f"  ✓ Collected {len(icg_timestamps)} ICG sync timestamps")

    # Build lookup dictionaries
    print(f"\n[Step 6] Analyzing temporal alignment...")

    ecg_dict = {}
    for sync_num, timestamp in ecg_timestamps:
        if sync_num not in ecg_dict:
            ecg_dict[sync_num] = timestamp

    icg_dict = {}
    for sync_num, timestamp in icg_timestamps:
        if sync_num not in icg_dict:
            icg_dict[sync_num] = timestamp

    # Find common sync_num values
    common_sync_nums = set(ecg_dict.keys()) & set(icg_dict.keys())

    assert len(common_sync_nums) >= 8, \
        f"Need at least 8 common sync markers, got {len(common_sync_nums)}"

    print(f"  ✓ Found {len(common_sync_nums)} common sync_num values")

    # Calculate time deltas
    deltas = []
    for sync_num in sorted(common_sync_nums):
        t_ecg = ecg_dict[sync_num]
        t_icg = icg_dict[sync_num]
        delta_ms = abs(t_ecg - t_icg) * 1000.0
        deltas.append((sync_num, delta_ms))

    # Compute statistics
    delta_values = [d[1] for d in deltas]
    max_delta_ms = max(delta_values)
    mean_delta_ms = sum(delta_values) / len(delta_values)

    print(f"\n[Step 7] Temporal alignment results:")
    print(f"  Common sync markers: {len(common_sync_nums)}")
    print(f"  Max delta: {max_delta_ms:.2f} ms")
    print(f"  Mean delta: {mean_delta_ms:.2f} ms")
    print(f"  Threshold: {TIMESTAMP_THRESHOLD_MS} ms")

    # Display per-sync deltas
    print(f"\n  Sync-by-sync deltas:")
    for sync_num, delta_ms in deltas[:5]:
        print(f"    sync_num={sync_num:3d}: {delta_ms:6.2f} ms")
    if len(deltas) > 5:
        print(f"    ... ({len(deltas) - 5} more)")

    # Assertion
    assert max_delta_ms < TIMESTAMP_THRESHOLD_MS, \
        f"Max time delta {max_delta_ms:.2f}ms exceeds {TIMESTAMP_THRESHOLD_MS}ms threshold"

    print(f"\n{'='*70}")
    print(f"Temporal Alignment Summary:")
    print(f"{'='*70}")
    print(f"  ECG sync markers:   {len(ecg_timestamps)}")
    print(f"  ICG sync markers:   {len(icg_timestamps)}")
    print(f"  Common sync_nums:   {len(common_sync_nums)}")
    print(f"  Max delta:          {max_delta_ms:.2f} ms")
    print(f"  Mean delta:         {mean_delta_ms:.2f} ms")
    print(f"  Threshold:          {TIMESTAMP_THRESHOLD_MS} ms")
    print(f"  Result:             PASS ✓")
    print(f"{'='*70}\n")
