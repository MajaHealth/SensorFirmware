"""
Test Case 49: MAX30009 get_data Polling Before Measurement Started

Category: FW-APP Integration (Robustness)
Components: MAX30009 + Firmware + Client

Test Steps:
1. Do not enable measurement
2. Send get_data every 0.5s for 60 seconds while remaining out of measurement mode
3. Capture all responses

Pass Criteria:
- Each response is "no_measure" while not in measurement mode
- Service remains stable and responsive
- No crashes or invalid states
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


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

            # Filter async messages
            if response.get('type') in ['meas_state', 'data']:
                continue

            return response

        except Exception:
            continue

    return {"type": "timeout", "error": f"No {expected_type} response"}


@pytest.fixture
def max30009_client(test_config):
    """Create TCP client for MAX30009 service with cleanup."""
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        # Drain initial async messages
        drain_async_messages(client)
        yield client

        # Note: No poweroff cleanup needed since measurement was never enabled


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
@pytest.mark.robustness
def test_max30009_get_data_before_measurement(test_config, max30009_client):
    """
    Test Case 49: Verify get_data returns no_measure when measurement not enabled.

    Validates:
    - Service correctly rejects get_data when not measuring
    - Consistent "no_measure" responses over extended polling
    - Service stability under repeated invalid requests
    - No state corruption or crashes
    """

    test_duration = 60  # seconds
    polling_interval = 0.5  # seconds
    num_polls = int(test_duration / polling_interval)

    print(f"\n{'='*70}")
    print(f"Test Case 49: get_data Polling Before Measurement Started")
    print(f"{'='*70}")
    print(f"Duration: {test_duration} seconds")
    print(f"Polling Interval: {polling_interval}s")
    print(f"Expected Polls: {num_polls}")
    print(f"Expected Response: 'no_measure' for all polls")
    print(f"{'='*70}\n")

    # IMPORTANT: Do NOT enable measurement
    # This is the key to this test - we intentionally skip configuration
    print(f"[Step 1] Skipping measurement configuration (intentional)")
    print(f"  Measurement state: DISABLED")
    print(f"  Testing service behavior when polled without measurement enabled\n")

    # Poll get_data repeatedly
    print(f"[Step 2] Polling get_data every {polling_interval}s for {test_duration}s...")
    print(f"  Progress updates every 10 seconds\n")

    responses = []
    start_time = time.time()
    last_progress_time = start_time

    for poll_num in range(num_polls):
        poll_start = time.time()

        # Drain any async messages first
        drain_async_messages(max30009_client)

        # Send get_data request
        response = send_and_wait_for_response(
            max30009_client,
            {"type": "get_data"},
            "no_measure"
        )

        responses.append(response)

        # Immediate validation
        response_type = response.get("type")

        if response_type != "no_measure":
            # Critical failure - unexpected response
            pytest.fail(
                f"Poll {poll_num + 1}/{num_polls}: Expected 'no_measure', "
                f"got '{response_type}'\n"
                f"Full response: {response}"
            )

        # Progress update every 10 seconds
        elapsed = time.time() - start_time
        if elapsed - (last_progress_time - start_time) >= 10.0:
            progress_pct = ((poll_num + 1) / num_polls) * 100
            print(f"  Progress: {progress_pct:.1f}% ({poll_num + 1}/{num_polls} polls) - "
                  f"Elapsed: {elapsed:.1f}s - All responses: no_measure ✓")
            last_progress_time = time.time()

        # Maintain polling interval
        poll_duration = time.time() - poll_start
        sleep_time = polling_interval - poll_duration
        if sleep_time > 0:
            time.sleep(sleep_time)

    end_time = time.time()
    actual_duration = end_time - start_time

    print(f"\n  ✓ Polling complete")
    print(f"    - Actual duration: {actual_duration:.2f}s")
    print(f"    - Total polls: {len(responses)}")
    print(f"    - All responses: no_measure\n")

    # Step 3: Validate all responses
    print(f"[Step 3] Validating all {len(responses)} responses...")

    no_measure_count = sum(1 for r in responses if r.get("type") == "no_measure")
    other_responses = [r for r in responses if r.get("type") != "no_measure"]

    print(f"  no_measure responses: {no_measure_count}/{len(responses)}")

    if other_responses:
        print(f"  ✗ Unexpected responses found:")
        for i, resp in enumerate(other_responses[:5]):  # Show first 5
            print(f"    {i+1}. {resp}")
        if len(other_responses) > 5:
            print(f"    ... and {len(other_responses) - 5} more")

    assert no_measure_count == len(responses), \
        f"Expected all {len(responses)} responses to be 'no_measure', " \
        f"but {len(other_responses)} were different"

    print(f"  ✓ All responses are 'no_measure'\n")

    # Step 4: Verify service still responsive
    print(f"[Step 4] Verifying service remains responsive...")

    drain_async_messages(max30009_client)

    # Try get_settings to verify service is still working
    settings_response = send_and_wait_for_response(
        max30009_client,
        {"type": "get_settings"},
        "actual_settings"
    )

    assert settings_response.get("type") == "actual_settings", \
        f"Post-test verification failed: Expected 'actual_settings', " \
        f"got '{settings_response.get('type')}'"

    print(f"  ✓ Service still responsive")
    print(f"    - get_settings returned: {settings_response.get('type')}")
    print(f"    - Measurement enabled: {settings_response.get('measure_enable')}\n")

    # Step 5: Optional - Enable measurement and verify it works
    print(f"[Step 5] Verifying measurement can be enabled after test...")

    drain_async_messages(max30009_client)

    enable_request = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": 20000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    enable_response = send_and_wait_for_response(
        max30009_client,
        enable_request,
        "actual_settings"
    )

    assert enable_response.get("type") == "actual_settings", \
        f"Failed to enable measurement: {enable_response}"

    assert enable_response.get("measure_enable") is True, \
        f"Measurement not enabled: {enable_response}"

    print(f"  ✓ Measurement enabled successfully")
    print(f"    - Configuration accepted")
    print(f"    - Service state: Valid\n")

    # Drain meas_state messages after enabling
    drain_async_messages(max30009_client)

    # Get one data sample to confirm it works
    data_response = send_and_wait_for_response(
        max30009_client,
        {"type": "get_data"},
        "data"
    )

    assert data_response.get("type") == "data", \
        f"Expected 'data' after enabling measurement, got '{data_response.get('type')}'"

    print(f"  ✓ get_data now returns 'data' (measurement working)")
    print(f"    - Sample count: {len(data_response.get('data', []))}\n")

    # Cleanup: Power off
    drain_async_messages(max30009_client)
    poweroff_response = send_and_wait_for_response(
        max30009_client,
        {"type": "poweroff"},
        "power_is_off"
    )

    assert poweroff_response.get("type") == "power_is_off", \
        f"Poweroff failed: {poweroff_response}"

    print(f"  ✓ Cleanup: Powered off successfully\n")

    # Summary
    print(f"{'='*70}")
    print(f"Test Summary - TC-049")
    print(f"{'='*70}")
    print(f"Test Duration:         {actual_duration:.2f}s")
    print(f"Total Polls:           {len(responses)}")
    print(f"no_measure Responses:  {no_measure_count}/{len(responses)}")
    print(f"Unexpected Responses:  {len(other_responses)}")
    print(f"Service Stability:     ✓ Remained responsive")
    print(f"Post-Test State:       ✓ Valid (measurement can be enabled)")
    print(f"Result:                PASS ✓")
    print(f"{'='*70}\n")
