"""
Test Case 51: Malformed/Unknown Power-Control Message Handling (TBD)

Category: FW-APP Integration
Components: Firmware power service

Test Steps:
1. Connect to power control server (127.0.0.1:501)
2. Send various unsupported/unknown/malformed messages
3. Capture responses and document behavior

Pass Criteria:
- Document observed behavior for spec clarification
- Verify service doesn't crash on invalid input
- Verify service continues to accept valid commands after errors

Based on firmware: PWRCNTR_process.cpp lines 78-171
Error handling returns: {"type": "error JSON"}
"""

import pytest
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.fixture
def power_client(test_config):
    """
    Create TCP client for power service.

    Note: Power service sends async button_info messages when button
    state changes. We drain these messages before yielding the client
    to ensure clean request/response communication.
    """
    import time

    power_config = test_config['services']['power']
    with TCPClient(power_config['host'], power_config['port']) as client:
        # Drain any pending async button_info messages
        time.sleep(0.2)
        drain_attempts = 0
        while drain_attempts < 5:
            try:
                msg = client.recv(timeout=0.1)
                if not msg:
                    break
                # Ignore button_info messages
                if msg.get('type') == 'button_info':
                    drain_attempts += 1
                    continue
                break
            except:
                break

        yield client


def drain_async_messages(client):
    """Helper function to drain async button_info messages."""
    import time
    time.sleep(0.2)
    while True:
        try:
            msg = client.recv(timeout=0.05)
            if not msg or msg.get('type') != 'button_info':
                break
        except:
            break


def send_and_get_response(client, request, max_retries=10):
    """
    Send request and get response, filtering out async button_info messages.

    Since button_info messages arrive every ~100ms, we need to keep draining
    them until we get our actual response.
    """
    import json

    # Send the request
    client.socket.sendall((json.dumps(request) + '\n').encode())

    # Keep receiving until we get a non-button_info message
    for _ in range(max_retries):
        try:
            response = client.recv(timeout=0.5)
            if response and response.get('type') != 'button_info':
                return response
            # Got button_info, keep looping
        except:
            break

    # Fallback: return last received message or error
    return {"type": "timeout", "error": "No response after filtering button_info"}


@pytest.mark.fw_app
@pytest.mark.invalid_params
@pytest.mark.quick
def test_power_unknown_command_type(power_client):
    """
    Test Case 51.1: Unknown command type.

    Documents behavior when sending a valid JSON message with
    an unknown/unsupported command type.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 51.1: Unknown Command Type")
    print(f"{'='*70}")

    # Send unknown command type
    print(f"\n[Test] Sending unknown command type...")
    drain_async_messages(power_client)

    request = {"type": "invalid_command"}
    print(f"Request: {request}")

    response = send_and_get_response(power_client, request)
    print(f"Response: {response}")

    # Document observed behavior
    print(f"\n[Observed Behavior]")
    print(f"  Response type: {response.get('type')}")
    assert "type" in response, "Response should contain 'type' field"
    assert response["type"] == "error JSON", \
        f"Expected 'error JSON', got '{response['type']}'"
    print(f"  ✓ Service returned error response: {response}")

    # Verify service still works with valid command
    print(f"\n[Recovery Test] Sending valid command to verify service health...")
    drain_async_messages(power_client)

    valid_request = {"type": "get_batt_info"}
    valid_response = send_and_get_response(power_client,valid_request)

    assert valid_response["type"] == "batt_info", \
        "Service should still accept valid commands after error"
    print(f"  ✓ Service recovered and processed valid command")

    print(f"\n{'='*70}")
    print(f"DOCUMENTED BEHAVIOR:")
    print(f"  Unknown command → Returns: {response}")
    print(f"  Service continues operating normally")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.invalid_params
@pytest.mark.quick
def test_power_missing_type_field(power_client):
    """
    Test Case 51.2: Missing 'type' field.

    Documents behavior when sending JSON without required 'type' field.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 51.2: Missing 'type' Field")
    print(f"{'='*70}")

    # Send JSON without 'type' field
    print(f"\n[Test] Sending JSON without 'type' field...")
    drain_async_messages(power_client)

    request = {"foo": "bar", "value": 123}
    print(f"Request: {request}")

    response = send_and_get_response(power_client,request)
    print(f"Response: {response}")

    # Document observed behavior
    print(f"\n[Observed Behavior]")
    assert "type" in response, "Response should contain 'type' field"
    assert response["type"] == "error JSON", \
        f"Expected 'error JSON', got '{response['type']}'"
    print(f"  ✓ Service returned error response: {response}")

    # Verify service recovery
    print(f"\n[Recovery Test] Verifying service still operational...")
    drain_async_messages(power_client)

    valid_request = {"type": "get_batt_info"}
    valid_response = send_and_get_response(power_client,valid_request)

    assert valid_response["type"] == "batt_info"
    print(f"  ✓ Service recovered successfully")

    print(f"\n{'='*70}")
    print(f"DOCUMENTED BEHAVIOR:")
    print(f"  Missing 'type' field → Returns: {response}")
    print(f"  Service continues operating normally")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.invalid_params
@pytest.mark.quick
def test_power_empty_json(power_client):
    """
    Test Case 51.3: Empty JSON object.

    Documents behavior when sending empty JSON: {}
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 51.3: Empty JSON Object")
    print(f"{'='*70}")

    # Send empty JSON
    print(f"\n[Test] Sending empty JSON object...")
    drain_async_messages(power_client)

    request = {}
    print(f"Request: {request}")

    response = send_and_get_response(power_client,request)
    print(f"Response: {response}")

    # Document observed behavior
    print(f"\n[Observed Behavior]")
    assert "type" in response, "Response should contain 'type' field"
    assert response["type"] == "error JSON", \
        f"Expected 'error JSON', got '{response['type']}'"
    print(f"  ✓ Service returned error response: {response}")

    # Verify service recovery
    print(f"\n[Recovery Test] Verifying service health...")
    drain_async_messages(power_client)

    valid_request = {"type": "get_batt_info"}
    valid_response = send_and_get_response(power_client,valid_request)

    assert valid_response["type"] == "batt_info"
    print(f"  ✓ Service operational")

    print(f"\n{'='*70}")
    print(f"DOCUMENTED BEHAVIOR:")
    print(f"  Empty JSON → Returns: {response}")
    print(f"  Service continues operating normally")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.invalid_params
@pytest.mark.quick
def test_power_invalid_type_value(power_client):
    """
    Test Case 51.4: Invalid 'type' value (non-string).

    Documents behavior when 'type' field contains non-string value.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 51.4: Invalid 'type' Value (Non-String)")
    print(f"{'='*70}")

    # Send JSON with numeric type
    print(f"\n[Test] Sending 'type' as number instead of string...")
    drain_async_messages(power_client)

    request = {"type": 123}
    print(f"Request: {request}")

    response = send_and_get_response(power_client,request)
    print(f"Response: {response}")

    # Document observed behavior
    print(f"\n[Observed Behavior]")
    assert "type" in response, "Response should contain 'type' field"
    assert response["type"] == "error JSON", \
        f"Expected 'error JSON', got '{response['type']}'"
    print(f"  ✓ Service returned error response: {response}")

    # Verify service recovery
    print(f"\n[Recovery Test] Verifying service recovery...")
    drain_async_messages(power_client)

    valid_request = {"type": "get_batt_info"}
    valid_response = send_and_get_response(power_client,valid_request)

    assert valid_response["type"] == "batt_info"
    print(f"  ✓ Service recovered")

    print(f"\n{'='*70}")
    print(f"DOCUMENTED BEHAVIOR:")
    print(f"  Invalid type value → Returns: {response}")
    print(f"  Service continues operating normally")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.invalid_params
@pytest.mark.quick
def test_power_multiple_invalid_messages(power_client):
    """
    Test Case 51.5: Multiple consecutive invalid messages.

    Documents behavior when sending multiple invalid messages in sequence.
    Verifies service remains stable under repeated error conditions.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 51.5: Multiple Consecutive Invalid Messages")
    print(f"{'='*70}")

    invalid_messages = [
        {"type": "unknown_cmd_1"},
        {"type": "unknown_cmd_2"},
        {"invalid": "field"},
        {},
        {"type": None},
    ]

    print(f"\n[Test] Sending {len(invalid_messages)} invalid messages...")

    for i, request in enumerate(invalid_messages, 1):
        print(f"\n  Message {i}/{len(invalid_messages)}: {request}")
        drain_async_messages(power_client)

        response = send_and_get_response(power_client,request)
        print(f"  Response: {response}")

        assert "type" in response, f"Message {i}: Response missing 'type'"
        assert response["type"] == "error JSON", \
            f"Message {i}: Expected 'error JSON', got '{response['type']}'"
        print(f"  ✓ Correct error response")

    # Final recovery test
    print(f"\n[Recovery Test] Verifying service still operational after {len(invalid_messages)} errors...")
    drain_async_messages(power_client)

    valid_request = {"type": "get_batt_info"}
    valid_response = send_and_get_response(power_client,valid_request)

    assert valid_response["type"] == "batt_info", \
        "Service should recover after multiple errors"
    print(f"  ✓ Service fully recovered and operational")

    print(f"\n{'='*70}")
    print(f"DOCUMENTED BEHAVIOR:")
    print(f"  Service handles multiple consecutive errors gracefully")
    print(f"  Each invalid message returns: {{'type': 'error JSON'}}")
    print(f"  Service remains stable and continues operation")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.invalid_params
@pytest.mark.quick
def test_power_error_response_summary(power_client):
    """
    Test Case 51: Summary - Malformed/Unknown Message Handling.

    Comprehensive test documenting all error scenarios and behaviors
    for specification clarification.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 51: Malformed/Unknown Message Handling - SUMMARY")
    print(f"{'='*70}")

    test_cases = [
        {
            "description": "Unknown command type",
            "request": {"type": "nonexistent_command"},
        },
        {
            "description": "Missing 'type' field",
            "request": {"data": "no_type_field"},
        },
        {
            "description": "Empty JSON object",
            "request": {},
        },
        {
            "description": "Type is null",
            "request": {"type": None},
        },
        {
            "description": "Type is boolean",
            "request": {"type": True},
        },
        {
            "description": "Type is array",
            "request": {"type": ["array"]},
        },
    ]

    print(f"\n[Testing {len(test_cases)} error scenarios]\n")

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['description']}")
        print(f"   Request: {test_case['request']}")

        drain_async_messages(power_client)
        response = send_and_get_response(power_client,test_case['request'])

        print(f"   Response: {response}")

        result = {
            "scenario": test_case['description'],
            "request": test_case['request'],
            "response": response,
            "response_type": response.get('type'),
        }
        results.append(result)

        assert response.get('type') == "error JSON", \
            f"Scenario '{test_case['description']}' should return 'error JSON'"
        print(f"   ✓ Returned 'error JSON'\n")

    # Verify service health after all errors
    print(f"[Final Health Check]")
    drain_async_messages(power_client)

    health_request = {"type": "get_batt_info"}
    health_response = send_and_get_response(power_client,health_request)

    assert health_response["type"] == "batt_info", \
        "Service should be operational after all error scenarios"
    print(f"✓ Service operational after {len(test_cases)} error scenarios")

    # Print summary for documentation
    print(f"\n{'='*70}")
    print(f"DOCUMENTED BEHAVIOR SUMMARY FOR SPEC CLARIFICATION:")
    print(f"{'='*70}")
    print(f"\n1. Error Response Format:")
    print(f"   All invalid messages return: {{'type': 'error JSON'}}")
    print(f"\n2. Service Stability:")
    print(f"   ✓ Does NOT crash on invalid input")
    print(f"   ✓ Does NOT disconnect client")
    print(f"   ✓ Continues accepting commands after errors")
    print(f"\n3. Error Scenarios Tested:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['scenario']}: '{result['response_type']}'")
    print(f"\n4. Recommendation:")
    print(f"   Standardize error response to include error details:")
    print(f"   {{'type': 'error', 'error': 'description', 'code': 'ERROR_CODE'}}")
    print(f"{'='*70}\n")

    print(f"✓ Test PASSED: All error scenarios documented")
    print(f"{'='*70}\n")
