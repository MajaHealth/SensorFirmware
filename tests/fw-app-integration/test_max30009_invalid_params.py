"""
Test Case 32: MAX30009 Invalid Settings Parameters Handling

Category: FW-APP Integration
Components: MAX30009 AFE + Firmware MAX30009 service

Test Steps:
1. Connect to MAX30009 server
2. Send settings request with invalid parameters:
   - Invalid stimulate_current string value
   - Invalid filter token
   - Out-of-range frequency values
3. Capture all responses and logs

Pass Criteria:
- Behavior documented (spec clarification required)
- Firmware responds with error or silently ignores invalid values
"""

import pytest
import sys
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
@pytest.mark.invalid_params
@pytest.mark.quick
def test_invalid_stimulate_current(max30009_client):
    """
    Test Case 32.1: Invalid stimulate_current string value.

    Valid values based on code analysis: "64uA", "128uA", "256uA", "640uA", "1.28mA"
    Invalid: "999uA", "invalid", "100mA", etc.
    """

    print("\n[Test] Invalid stimulate_current parameter")

    # Send settings with invalid current value
    settings_request = {
        "type": "settings",
        "stimulate_current": "999uA",  # Invalid value
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "measure_enable": False
    }

    response = max30009_client.send(settings_request)
    print(f"Response to invalid stimulate_current: {response}")

    # Document behavior (spec clarification needed)
    # Possible responses:
    # 1. {"type": "error settings JSON"} - explicit error
    # 2. {"type": "actual_settings", ...} - silently ignored, used default
    # 3. Connection closes / timeout

    assert 'type' in response, "Response missing 'type' field"

    if response['type'] == 'error settings JSON':
        print("✓ Firmware returns explicit error for invalid current")
    elif response['type'] == 'actual_settings':
        print("⚠ Firmware silently ignored invalid current (returned actual_settings)")
        print(f"  Actual current used: {response.get('stimulate_current', 'N/A')}")
    elif response['type'] == 'error JSON':
        print("✓ Firmware returns generic JSON error")
    else:
        print(f"⚠ Unexpected response type: {response['type']}")

    # Log for spec clarification
    print("\n[SPEC CLARIFICATION NEEDED]")
    print(f"  Invalid parameter: stimulate_current='999uA'")
    print(f"  Firmware response: {response}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.invalid_params
@pytest.mark.quick
def test_invalid_filter_token(max30009_client):
    """
    Test Case 32.2: Invalid filter token.

    Valid filter values: "bypass", specific filter types
    Invalid: "invalid_filter", "unknown", random strings
    """

    print("\n[Test] Invalid filter token")

    settings_request = {
        "type": "settings",
        "out_LP_filter": "invalid_filter_token",  # Invalid
        "measure_enable": False
    }

    response = max30009_client.send(settings_request)
    print(f"Response to invalid filter: {response}")

    assert 'type' in response, "Response missing 'type' field"

    # Document behavior
    print("\n[SPEC CLARIFICATION NEEDED]")
    print(f"  Invalid parameter: out_LP_filter='invalid_filter_token'")
    print(f"  Firmware response: {response}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.invalid_params
@pytest.mark.quick
def test_out_of_range_frequency(max30009_client):
    """
    Test Case 32.3: Out-of-range frequency values.

    Based on code: MIN_MEASURE_FREQ and MAX_MEASURE_FREQ exist
    Test extreme values: 0, negative, very large numbers
    """

    print("\n[Test] Out-of-range frequency values")

    test_cases = [
        {"freq": 0, "desc": "zero frequency"},
        {"freq": -1000, "desc": "negative frequency"},
        {"freq": 999999999, "desc": "extremely large frequency"}
    ]

    for test in test_cases:
        print(f"\n  Testing {test['desc']}: {test['freq']} Hz")

        settings_request = {
            "type": "settings",
            "stimulate_frequency": test['freq'],
            "measure_enable": False
        }

        response = max30009_client.send(settings_request)
        print(f"    Response: {response}")

        assert 'type' in response, "Response missing 'type' field"

        if response['type'] == 'actual_settings':
            actual_freq = response.get('stimulate_frequency', 'N/A')
            print(f"    ⚠ Firmware clamped/corrected to: {actual_freq} Hz")
        elif response['type'] == 'error settings JSON':
            print(f"    ✓ Firmware rejected with error")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.invalid_params
@pytest.mark.quick
def test_missing_required_parameters(max30009_client):
    """
    Test Case 32.4: Missing required parameters.

    Send minimal settings request, omitting optional fields.
    """

    print("\n[Test] Minimal settings (missing optional parameters)")

    settings_request = {
        "type": "settings",
        "measure_enable": False
        # All other parameters omitted
    }

    response = max30009_client.send(settings_request)
    print(f"Response to minimal settings: {response}")

    assert 'type' in response, "Response missing 'type' field"

    if response['type'] == 'actual_settings':
        print("✓ Firmware uses defaults for missing parameters")
        print(f"  Defaults used: {response}")
    else:
        print(f"⚠ Unexpected response: {response}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.invalid_params
@pytest.mark.quick
@pytest.mark.skip(reason="Malformed JSON may crash firmware service")
def test_invalid_json_structure(max30009_client):
    """
    Test Case 32.5: Completely invalid JSON structure.

    Send malformed JSON to test error handling.

    SKIPPED: This test sends malformed JSON which may crash the firmware service.
    Need to verify firmware can handle JSON parse errors gracefully.
    """

    print("\n[Test] Invalid JSON structure")

    # Send raw string instead of using send
    malformed_json = '{"type": "settings", "invalid'  # Truncated JSON

    max30009_client.socket.sendall((malformed_json + '\n').encode())

    try:
        import time
        time.sleep(1.0)

        # Try to receive response
        response_data = b''
        max30009_client.socket.settimeout(2.0)
        while b'\n' not in response_data:
            chunk = max30009_client.socket.recv(4096)
            if not chunk:
                break
            response_data += chunk

        if response_data:
            response_str = response_data.decode('utf-8').strip()
            print(f"Response to malformed JSON: {response_str}")
        else:
            print("  No response (connection likely closed)")

    except Exception as e:
        print(f"  Exception caught: {e}")
        print("  ⚠ Firmware may not handle malformed JSON gracefully")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.invalid_params
@pytest.mark.quick
def test_multiple_invalid_parameters(max30009_client):
    """
    Test Case 32.6: Multiple invalid parameters in single request.

    Combine multiple invalid values to test error priority.
    """

    print("\n[Test] Multiple invalid parameters")

    settings_request = {
        "type": "settings",
        "stimulate_current": "invalid_current",
        "out_LP_filter": "invalid_filter",
        "stimulate_frequency": -5000,
        "measure_enable": False
    }

    response = max30009_client.send(settings_request)
    print(f"Response to multiple invalid params: {response}")

    assert 'type' in response, "Response missing 'type' field"

    # Document which error is reported first (if any)
    print("\n[SPEC CLARIFICATION NEEDED]")
    print(f"  Multiple invalid parameters sent")
    print(f"  Firmware response: {response}")
    print(f"  Question: Does firmware validate all params or stop at first error?")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.invalid_params
@pytest.mark.quick
def test_valid_then_invalid_sequence(max30009_client):
    """
    Test Case 32.7: Valid settings followed by invalid settings.

    Ensure invalid request doesn't corrupt valid state.
    """

    print("\n[Test] Valid → Invalid → Valid sequence")

    # Step 1: Send minimal valid settings
    print("\n  [Step 1] Sending valid settings (minimal)...")
    valid_request = {
        "type": "settings",
        "measure_enable": False
    }

    response = max30009_client.send(valid_request)
    print(f"    Response: {response}")

    assert 'type' in response, "Response missing 'type' field"
    assert response['type'] == 'actual_settings', \
        f"Valid request failed. Got: {response['type']}"
    print(f"    ✓ Valid settings accepted")

    # Step 2: Send invalid settings
    print("\n  [Step 2] Sending invalid settings...")
    invalid_request = {
        "type": "settings",
        "stimulate_current": "invalid_value",
        "measure_enable": False
    }

    response = max30009_client.send(invalid_request)
    print(f"    Response: {response['type']}")

    # Step 3: Verify can still send valid settings
    print("\n  [Step 3] Sending valid settings again...")
    response = max30009_client.send(valid_request)

    assert response['type'] == 'actual_settings', \
        "Firmware state corrupted by invalid request"
    print(f"    ✓ Firmware still accepts valid settings after invalid request")
