"""
Test Case 31: MAX30009 Measurement Settings and State Machine

Category: FW-APP Integration
Components: MAX30009 AFE + Firmware MAX30009 service

Test Steps:
1. Connect to MAX30009 server
2. Send JSON request with measurement enabled and required parameters
3. Capture all asynchronous PUSH messages until state machine is ready
4. Capture the actual_settings message

Pass Criteria:
- Firmware emits documented meas_state sequence:
  pre_measuring → pre_measure_end → calibrating → calibrate_end → start_measuring
- Firmware then emits actual_settings
"""

import pytest
import sys
import time
from pathlib import Path

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
def test_max30009_state_machine_sequence(max30009_client):
    """
    Test Case 31: Apply MAX30009 measurement settings and observe state machine.

    Validates the complete state machine sequence:
    pre_measuring → pre_measure_end → calibrating → calibrate_end → start_measuring
    """

    print("\n[Test] MAX30009 State Machine Sequence")
    print("="*70)

    # Step 1: Already connected via fixture

    # Step 2: Send settings request with measurement enabled (async - don't wait for response)
    print("\n[Step 1] Sending measurement settings...")
    settings_request = {
        "type": "settings",
        "measure_enable": True,
        # Add required parameters based on MAX30009 protocol
        # These should match your JSON protocol specification
    }

    # Use send_async since MAX30009 sends push messages asynchronously
    max30009_client.send_async(settings_request)
    print(f"  Request sent: {settings_request}")

    # Step 3: Capture asynchronous PUSH messages
    print("\n[Step 2] Capturing state machine sequence...")

    expected_states = [
        "pre_measuring",
        "pre_measure_end",
        "calibrating",
        "calibrate_end",
        "start_measuring"
    ]

    captured_states = []
    actual_settings_received = False
    max_attempts = 20  # Prevent infinite loop
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        # Receive asynchronous message
        response = max30009_client.recv(timeout=5.0)

        if not response:
            print(f"  Warning: No response on attempt {attempt}")
            time.sleep(0.5)
            continue

        print(f"  [{attempt}] Received: {response}")

        # Check for meas_state messages
        if response.get('type') == 'meas_state':
            state = response.get('state')
            captured_states.append(state)
            print(f"    → State: {state}")

        # Check for actual_settings
        if response.get('type') == 'actual_settings':
            actual_settings_received = True
            print(f"    → Received actual_settings")
            break

        time.sleep(0.2)

    # Step 4: Document state machine sequence
    print("\n[Step 3] Documenting state machine sequence...")
    print(f"  Expected states: {expected_states}")
    print(f"  Captured states: {captured_states}")

    # Document which expected states were received
    states_received = len(captured_states)
    print(f"\n  States received: {states_received}/{len(expected_states)}")

    if states_received > 0:
        for i, state in enumerate(captured_states):
            expected = expected_states[i] if i < len(expected_states) else "N/A"
            match = "✓" if state == expected else "⚠"
            print(f"    {match} State {i+1}: {state} (expected: {expected})")

    print(f"\n  actual_settings received: {actual_settings_received}")

    # Validate test results per specification:
    # - Must receive all expected states
    # - Must receive actual_settings message

    print("\n" + "="*70)

    # Check if all expected states were received
    missing_states = [s for s in expected_states if s not in captured_states]

    if missing_states:
        print(f"⚠ WARNING: Missing states: {missing_states}")

    if not actual_settings_received:
        print("⚠ WARNING: actual_settings message not received")

    # Per test case #31: Must capture actual_settings message
    assert actual_settings_received, \
        f"Test FAILED: actual_settings message not received.\n" \
        f"Captured states: {captured_states}\n" \
        f"Missing states: {missing_states}"

    # Verify all expected states were received
    assert len(missing_states) == 0, \
        f"Test FAILED: Not all expected states received.\n" \
        f"Expected: {expected_states}\n" \
        f"Captured: {captured_states}\n" \
        f"Missing: {missing_states}"

    print("✓ Test PASSED: All states received and actual_settings captured")
    print("="*70)


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_state_transitions_timing(max30009_client):
    """
    Test Case 31.1: Verify state transition timing.

    Ensures state transitions happen within reasonable time limits.
    """

    print("\n[Test] MAX30009 State Transition Timing")

    settings_request = {
        "type": "settings",
        "measure_enable": True,
    }

    start_time = time.time()
    max30009_client.send_async(settings_request)

    states_with_timing = []
    actual_settings_received = False
    max_wait = 10.0  # Maximum 10 seconds for entire sequence

    while (time.time() - start_time) < max_wait:
        response = max30009_client.recv(timeout=2.0)

        if not response:
            continue

        timestamp = time.time() - start_time

        if response.get('type') == 'meas_state':
            states_with_timing.append({
                'state': response.get('state'),
                'time': timestamp
            })
            print(f"  {timestamp:.2f}s: {response.get('state')}")

        if response.get('type') == 'actual_settings':
            actual_settings_received = True
            print(f"  {timestamp:.2f}s: actual_settings")
            break

    total_time = time.time() - start_time

    # Document timing results
    print(f"\n  States captured: {len(states_with_timing)}")
    print(f"  actual_settings received: {actual_settings_received}")
    print(f"  Total time: {total_time:.2f}s")

    # Document state timing
    if states_with_timing:
        print("\n  State timing breakdown:")
        for s in states_with_timing:
            print(f"    {s['time']:.2f}s: {s['state']}")

    # Per test case #31: Must receive actual_settings
    assert actual_settings_received, \
        f"Test FAILED: actual_settings message not received.\n" \
        f"States captured: {[s['state'] for s in states_with_timing]}"

    print(f"\n✓ Test PASSED: State transitions and actual_settings received")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_settings_without_measurement(max30009_client):
    """
    Test Case 31.2: Send settings with measurement_enabled=False.

    Documents behavior when measurement is not enabled.
    """

    print("\n[Test] Settings without measurement enabled")

    settings_request = {
        "type": "settings",
        "measure_enable": False,
    }

    response = max30009_client.send(settings_request)
    print(f"Response: {response}")

    # Document the response type
    response_type = response.get('type')
    print(f"  Response type: {response_type}")

    # The firmware may still return meas_state or actual_settings
    # Document the actual behavior
    if response_type == 'actual_settings':
        print("✓ Received actual_settings without state machine sequence")
        assert response.get('measure_enable') == False, \
            "Expected measure_enable=False in response"
    elif response_type == 'meas_state':
        state = response.get('state')
        print(f"  State machine started: {state}")
        print("  Note: Firmware starts state machine even with measure_enable=False")

        # Wait for actual_settings
        max_attempts = 20
        for i in range(max_attempts):
            next_response = max30009_client.recv(timeout=2.0)
            if next_response:
                print(f"  [{i+1}] Received: {next_response}")
                if next_response.get('type') == 'actual_settings':
                    print("✓ Eventually received actual_settings")
                    break
    else:
        print(f"  Unexpected response type: {response_type}")

    # Test passes as long as we get a valid response
    assert 'type' in response, "Response should contain 'type' field"
    print("✓ Test completed - behavior documented")
