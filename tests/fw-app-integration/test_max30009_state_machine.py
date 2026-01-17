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

    # Step 2: Send settings request with measurement enabled
    print("\n[Step 1] Sending measurement settings...")
    settings_request = {
        "type": "settings",
        "measure_enable": True,
        # Add required parameters based on MAX30009 protocol
        # These should match your JSON protocol specification
    }

    response = max30009_client.send(settings_request)
    print(f"Initial response: {response}")

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
        if 'meas_state' in response:
            state = response['meas_state']
            captured_states.append(state)
            print(f"    → State: {state}")

        # Check for actual_settings
        if response.get('type') == 'actual_settings':
            actual_settings_received = True
            print(f"    → Received actual_settings")
            break

        time.sleep(0.2)

    # Step 4: Validate state machine sequence
    print("\n[Step 3] Validating state machine sequence...")
    print(f"Expected states: {expected_states}")
    print(f"Captured states: {captured_states}")

    # Verify all expected states were received in order
    for i, expected_state in enumerate(expected_states):
        assert i < len(captured_states), \
            f"Missing state: {expected_state}. Only got {len(captured_states)} states."

        assert captured_states[i] == expected_state, \
            f"State mismatch at position {i}: expected '{expected_state}', got '{captured_states[i]}'"

        print(f"  ✓ State {i+1}/{len(expected_states)}: {expected_state}")

    # Verify actual_settings was received
    assert actual_settings_received, \
        "actual_settings message not received after state machine sequence"

    print("\n✓ State machine sequence completed successfully")
    print("✓ actual_settings received")
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
    max30009_client.send(settings_request)

    states_with_timing = []
    actual_settings_received = False
    max_wait = 10.0  # Maximum 10 seconds for entire sequence

    while (time.time() - start_time) < max_wait:
        response = max30009_client.recv_json(timeout=2.0)

        if not response:
            continue

        timestamp = time.time() - start_time

        if 'meas_state' in response:
            states_with_timing.append({
                'state': response['meas_state'],
                'time': timestamp
            })
            print(f"  {timestamp:.2f}s: {response['meas_state']}")

        if response.get('type') == 'actual_settings':
            actual_settings_received = True
            print(f"  {timestamp:.2f}s: actual_settings")
            break

    total_time = time.time() - start_time

    # Verify sequence completed
    assert len(states_with_timing) == 5, \
        f"Expected 5 state transitions, got {len(states_with_timing)}"

    assert actual_settings_received, \
        "actual_settings not received"

    # Verify reasonable timing (adjust based on actual firmware behavior)
    assert total_time < max_wait, \
        f"State machine took too long: {total_time:.2f}s"

    print(f"\n✓ Complete sequence took {total_time:.2f}s")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_settings_without_measurement(max30009_client):
    """
    Test Case 31.2: Send settings with measurement_enabled=False.

    Validates behavior when measurement is not enabled.
    """

    print("\n[Test] Settings without measurement enabled")

    settings_request = {
        "type": "settings",
        "measure_enable": False,
    }

    response = max30009_client.send(settings_request)
    print(f"Response: {response}")

    # Should receive actual_settings immediately without state machine
    assert response.get('type') == 'actual_settings', \
        f"Expected 'actual_settings', got '{response.get('type')}'"

    assert response.get('measure_enable') == False, \
        "Expected measure_enable=False in response"

    print("✓ Received actual_settings without state machine sequence")
