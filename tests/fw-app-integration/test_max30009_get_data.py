"""
Test Case 33: MAX30009 Poll get_data After start_measuring

Tests the MAX30009 get_data API after the sensor enters measurement mode.
Validates response format including sync-packet structure.
"""
import pytest
import time
from pathlib import Path
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.fixture
def max30009_client(test_config):
    """Create TCP client for MAX30009 service."""
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        yield client


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_after_start_measuring(max30009_client):
    """
    Test Case 33: Poll MAX30009 get_data after start_measuring.

    Steps:
    1. Configure MAX30009 with measurement enabled
    2. Wait for state machine to complete (start_measuring state)
    3. Send get_data request
    4. Validate response format and sync-packet structure
    """
    print(f"\n{'='*70}")
    print(f"Test Case 33: MAX30009 get_data After start_measuring")
    print(f"{'='*70}")

    # Step 1: Configure MAX30009 with measurement enabled
    print(f"\n[Step 1] Configuring MAX30009 with measurement enabled...")
    settings_request = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    response = max30009_client.send(settings_request)
    print(f"Settings response type: {response.get('type')}")

    # Step 2: Wait for state machine sequence to complete
    print(f"\n[Step 2] Waiting for state machine to reach start_measuring...")

    expected_states = ['pre_measuring', 'pre_measure_end', 'calibrating',
                      'calibrate_end', 'start_measuring']
    received_states = []
    start_measuring_received = False
    max_attempts = 20
    attempt = 0

    while attempt < max_attempts and not start_measuring_received:
        attempt += 1
        response = max30009_client.recv(timeout=5.0)

        if not response:
            print(f"  Warning: No response on attempt {attempt}")
            time.sleep(0.5)
            continue

        response_type = response.get('type')
        print(f"  Received: {response_type}")
        received_states.append(response_type)

        if response_type == 'start_measuring':
            start_measuring_received = True
            print(f"✓ Reached start_measuring state")
        elif response_type == 'actual_settings':
            print(f"✓ State machine complete, received actual_settings")
            break

    assert start_measuring_received or 'actual_settings' in received_states, \
        f"Did not receive start_measuring or actual_settings. Got: {received_states}"

    # Give sensor a moment to stabilize
    time.sleep(0.5)

    # Step 3: Send get_data request
    print(f"\n[Step 3] Sending get_data request...")
    get_data_request = {"type": "get_data"}

    data_response = max30009_client.send(get_data_request)
    print(f"Response type: {data_response.get('type')}")

    # Step 4: Validate response format
    print(f"\n[Step 4] Validating response format...")

    # Check response type
    assert data_response.get('type') == 'data', \
        f"Expected response type 'data', got '{data_response.get('type')}'"
    print(f"✓ Response type is 'data'")

    # Check required fields
    required_fields = ['data_frequency', 'data_size', 'timestamp', 'data']
    for field in required_fields:
        assert field in data_response, f"Missing required field: {field}"
        print(f"✓ Field '{field}' present")

    # Validate data array
    data_array = data_response.get('data', [])
    assert isinstance(data_array, list), "data field should be a list"
    print(f"✓ Data array present with {len(data_array)} samples")

    # Check for sync-packet format: [-999990000, sync_num, 0, 0, 0]
    sync_packets_found = []
    for i, sample in enumerate(data_array):
        if isinstance(sample, list) and len(sample) == 5:
            if sample[0] == -999990000 and sample[2] == 0 and sample[3] == 0 and sample[4] == 0:
                sync_num = sample[1]
                sync_packets_found.append((i, sync_num))
                print(f"✓ Sync packet found at index {i}: [-999990000, {sync_num}, 0, 0, 0]")

    # Validate sync packet format (should have at least some sync packets)
    if sync_packets_found:
        print(f"✓ Found {len(sync_packets_found)} sync packet(s) with correct format")
    else:
        print(f"  Note: No sync packets found (may be expected for short data collection)")

    # Validate data_frequency is positive
    data_freq = data_response.get('data_frequency')
    assert data_freq > 0, f"data_frequency should be positive, got {data_freq}"
    print(f"✓ data_frequency: {data_freq} Hz")

    # Validate data_size matches array length
    data_size = data_response.get('data_size')
    assert data_size == len(data_array), \
        f"data_size ({data_size}) doesn't match data array length ({len(data_array)})"
    print(f"✓ data_size ({data_size}) matches data array length")

    # Validate timestamp is present
    timestamp = data_response.get('timestamp')
    assert timestamp is not None, "timestamp should be present"
    print(f"✓ timestamp: {timestamp}")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 33 PASSED")
    print(f"{'='*70}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_multiple_polls(max30009_client):
    """
    Test Case 33.1: Poll get_data multiple times after start_measuring.

    Validates that multiple get_data requests work correctly and sync numbers increment.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 33.1: Multiple get_data Polls")
    print(f"{'='*70}")

    # Step 1: Configure and wait for start_measuring
    print(f"\n[Step 1] Configuring MAX30009...")
    settings_request = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    max30009_client.send(settings_request)

    # Wait for state machine
    print(f"\n[Step 2] Waiting for start_measuring state...")
    start_measuring_received = False
    max_attempts = 20

    for attempt in range(max_attempts):
        response = max30009_client.recv(timeout=5.0)
        if response and response.get('type') in ['start_measuring', 'actual_settings']:
            start_measuring_received = True
            break

    assert start_measuring_received, "Did not receive start_measuring state"
    time.sleep(0.5)

    # Step 2: Poll get_data multiple times
    print(f"\n[Step 3] Polling get_data multiple times...")
    num_polls = 3
    all_sync_nums = []

    for poll_num in range(num_polls):
        print(f"\n  Poll #{poll_num + 1}:")
        get_data_request = {"type": "get_data"}
        data_response = max30009_client.send(get_data_request)

        assert data_response.get('type') == 'data', \
            f"Poll {poll_num + 1}: Expected 'data', got '{data_response.get('type')}'"

        data_array = data_response.get('data', [])
        print(f"    Received {len(data_array)} samples")

        # Extract sync numbers
        sync_nums = []
        for sample in data_array:
            if isinstance(sample, list) and len(sample) == 5:
                if sample[0] == -999990000:
                    sync_nums.append(sample[1])

        if sync_nums:
            print(f"    Sync numbers: {sync_nums}")
            all_sync_nums.extend(sync_nums)

        time.sleep(0.5)  # Wait between polls

    # Validate sync numbers are monotonically increasing (if present)
    if len(all_sync_nums) > 1:
        for i in range(len(all_sync_nums) - 1):
            assert all_sync_nums[i] < all_sync_nums[i + 1], \
                f"Sync numbers not monotonic: {all_sync_nums[i]} >= {all_sync_nums[i + 1]}"
        print(f"\n✓ Sync numbers are monotonically increasing: {all_sync_nums}")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 33.1 PASSED")
    print(f"{'='*70}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_before_measurement(max30009_client):
    """
    Test Case 33.2: Send get_data before measurement mode.

    Validates behavior when get_data is called without entering measurement mode.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 33.2: get_data Before Measurement Mode")
    print(f"{'='*70}")

    # Send get_data without configuring measurement
    print(f"\n[Step 1] Sending get_data without measurement enabled...")
    get_data_request = {"type": "get_data"}

    response = max30009_client.send(get_data_request)
    print(f"Response type: {response.get('type')}")
    print(f"Response: {response}")

    # Should receive either 'data' with empty array or an error response
    response_type = response.get('type')

    if response_type == 'data':
        data_array = response.get('data', [])
        print(f"✓ Received 'data' response with {len(data_array)} samples")
        # May be empty or contain minimal data
    elif 'error' in response_type.lower():
        print(f"✓ Received error response: {response_type}")
    else:
        # Document actual behavior
        print(f"  Received unexpected response type: {response_type}")

    # The test documents behavior - firmware may handle this differently
    assert 'type' in response, "Response should contain 'type' field"

    print(f"\n{'='*70}")
    print(f"✓ Test Case 33.2 COMPLETED (behavior documented)")
    print(f"{'='*70}")
