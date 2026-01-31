"""
Test Case 39: MAX30009 Repeat poweroff then re-enable measurement

Tests the sequence: poweroff → settings with measure_enable=true.
Verifies firmware can re-enable measurement after poweroff.

Test Steps:
1. Send poweroff and confirm power_is_off response
2. Send settings with measurement enabled
3. Capture meas_state sequence (async messages)

Pass Criteria:
- poweroff returns {"type":"power_is_off"}
- settings with measure_enable=true returns empty string (async state machine starts)
- Async messages show state transitions: pre_measuring → pre_measure_end → calibrating → calibrate_end → start_measuring

**IMPORTANT: This test requires actual MAX30009 hardware.**
Without hardware, the state machine will hang waiting for FIFO data.

Based on firmware: MAX30009_process.cpp lines 106-203
State sequence:
1. MMD_BASE_MEASURE_START → "pre_measuring"
2. MMD_BASE_MEASURING → "pre_measure_end" (after 20 samples)
3. MMD_CALIBRATE_START → "calibrating"
4. MMD_CALIBRATING → "calibrate_end"
5. MMD_MEASURE_START → "start_measuring" + actual_settings
"""
import pytest
import time
from pathlib import Path
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.fixture
def max30009_client(test_config, max30009_cleanup):
    """
    Create TCP client for MAX30009 service.

    Note: The max30009_cleanup fixture ensures clean state before/after test.
    """
    max_config = test_config['services']['max30009']

    with TCPClient(max_config['host'], max_config['port']) as client:
        yield client


@pytest.mark.hardware  # Requires actual MAX30009 hardware
@pytest.mark.max30009
@pytest.mark.slow
def test_max30009_poweroff_then_reenable_measurement(max30009_client):
    """
    Test Case 39: Repeat poweroff then re-enable measurement.

    **REQUIRES HARDWARE:** Needs actual MAX30009 for measurement state machine.

    Tests that MAX30009 can be powered off and then measurement can be
    re-enabled, going through the full state machine sequence.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 39: Poweroff Then Re-enable Measurement")
    print(f"{'='*70}")

    # Step 1: Send poweroff
    print(f"\n[Step 1] Sending poweroff command...")
    poweroff_request = {"type": "poweroff"}
    response = max30009_client.send(poweroff_request)

    print(f"Response: {response}")
    assert response.get('type') == 'power_is_off', \
        f"Expected 'power_is_off', got '{response.get('type')}'"
    print(f"✓ Power is off")

    # Step 2: Re-enable measurement
    print(f"\n[Step 2] Re-enabling measurement...")
    settings_request = {
        "type": "settings",
        "measure_enable": True,
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    # Send settings and consume the immediate empty response
    max30009_client.send_async(settings_request)

    # Firmware sends empty response immediately - consume it
    print(f"Consuming immediate empty response...")
    empty_response = max30009_client.recv(timeout=5.0)
    print(f"Empty response: {empty_response}")
    print(f"✓ Settings sent (async state machine started)")

    # Step 3: Capture async meas_state messages
    print(f"\n[Step 3] Capturing async state transitions...")
    print(f"Expected sequence:")
    print(f"  1. pre_measuring")
    print(f"  2. pre_measure_end")
    print(f"  3. calibrating")
    print(f"  4. calibrate_end")
    print(f"  5. start_measuring + actual_settings")
    print(f"\nWaiting for messages (timeout 30s per message)...\n")

    expected_states = [
        "pre_measuring",
        "pre_measure_end",
        "calibrating",
        "calibrate_end",
        "start_measuring"
    ]

    received_states = []
    timeout_per_message = 30.0  # Long timeout for hardware operations

    for i, expected_state in enumerate(expected_states):
        try:
            msg = max30009_client.recv(timeout=timeout_per_message)

            if not msg:
                raise TimeoutError(f"Timeout waiting for state '{expected_state}'")

            print(f"  [{i+1}] Received: {msg}")

            # Validate message type
            assert msg.get('type') == 'meas_state', \
                f"Expected type 'meas_state', got '{msg.get('type')}'"

            # Validate state
            state = msg.get('state')
            assert state == expected_state, \
                f"Expected state '{expected_state}', got '{state}'"

            received_states.append(state)

            # Last message should include actual_settings
            if state == "start_measuring":
                assert 'stimulate_frequency' in msg, \
                    "start_measuring message should include actual_settings"
                print(f"      ✓ Includes actual_settings")

        except TimeoutError as e:
            print(f"\n✗ TIMEOUT: {e}")
            print(f"  Received {len(received_states)}/{len(expected_states)} states before timeout")
            print(f"  States received: {received_states}")
            raise

    print(f"\n✓ All {len(expected_states)} state transitions received")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 39 PASSED")
    print(f"{'='*70}")
    print(f"Summary:")
    print(f"  - Step 1: poweroff → power_is_off ✓")
    print(f"  - Step 2: settings(measure_enable=true) → async state machine ✓")
    print(f"  - Step 3: All {len(expected_states)} state transitions received ✓")
    print(f"  - Final state: MMD_MEASURING (start_measuring)")
    print(f"{'='*70}")
