"""
Test Case 43: ADS1293 get_data Before Configuration/Conversion

Category: FW-APP Integration
Components: ADS1293 AFE + Firmware ADS1293 service
Test Name: get_data before configuration/conversion

Prerequisites:
- DUT with ADS1293 service reachable on port 1293

Pass Criteria:
- Record observed responses for requirement clarification
- Document firmware behavior when get_data is called before enable_conversion
- No crashes or hangs
"""

import pytest
import time
from pathlib import Path
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.fixture
def ads1293_client(test_config):
    """Create TCP client connected to ADS1293 service."""
    config = test_config['services']['ads1293']
    with TCPClient(config['host'], config['port']) as client:
        yield client


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_get_data_no_configuration(ads1293_client):
    """
    Test Case 43.1: Call get_data without any prior configuration.

    Test Steps:
    1. Connect to ADS1293 service (fresh connection)
    2. Immediately send get_data without any settings
    3. Record response
    4. Document behavior
    """
    print(f"\n{'='*70}")
    print(f"Test Case 43.1: get_data Without Any Configuration")
    print(f"{'='*70}\n")

    print(f"[Step 1] Connected to ADS1293 service")
    print(f"  No settings or configuration sent\n")

    # Step 2: Send get_data without any prior configuration
    print(f"[Step 2] Sending get_data without configuration...")
    request = {"type": "get_data"}
    print(f"  Request: {request}")

    response = ads1293_client.send(request)
    print(f"  Response: {response}\n")

    # Step 3: Document the response
    print(f"[Step 3] Analyzing response...")
    print(f"  Response type: {response.get('type', 'MISSING')}")

    if response.get('type') == 'data':
        data_size = len(response.get('data', []))
        print(f"  ✓ Received 'data' response")
        print(f"  Data size: {data_size} samples")
        if data_size > 0:
            print(f"  First sample: {response['data'][0]}")
            print(f"  Last sample: {response['data'][-1]}")
    elif response.get('type') == 'error':
        print(f"  ✓ Received 'error' response")
        print(f"  Error message: {response.get('message', 'N/A')}")
    elif response.get('type') == 'no_measure':
        print(f"  ✓ Received 'no_measure' response")
        print(f"  Indicates sensor not configured")
    else:
        print(f"  ⚠ Unexpected response type: {response.get('type')}")

    # Step 4: Record findings
    print(f"\n[Step 4] Test Results:")
    print(f"  Behavior: Firmware responds with type='{response.get('type')}'")
    print(f"  Connection: Stable (no crash/hang)")

    # Document the behavior (test always passes, just documents behavior)
    assert 'type' in response, "Response should contain 'type' field"

    print(f"\n{'='*70}")
    print(f"✓ Test COMPLETED: Behavior documented")
    print(f"{'='*70}\n")

    return {
        'test_case': '43.1',
        'scenario': 'get_data without configuration',
        'response_type': response.get('type'),
        'response': response
    }


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_get_data_after_poweroff(ads1293_client):
    """
    Test Case 43.2: Call get_data after poweroff.

    Test Steps:
    1. Enable conversion first
    2. Send poweroff command
    3. Call get_data after poweroff
    4. Record response
    """
    print(f"\n{'='*70}")
    print(f"Test Case 43.2: get_data After Poweroff")
    print(f"{'='*70}\n")

    # Step 1: Enable conversion first
    print(f"[Step 1] Enabling conversion...")
    settings_request = {
        "type": "settings",
        "enable_conversion": True
    }
    response = ads1293_client.send(settings_request)
    print(f"  Response: {response}")
    assert response["type"] == "actual_settings"
    print(f"  ✓ Conversion enabled\n")

    # Step 2: Power off
    print(f"[Step 2] Sending poweroff command...")
    poweroff_request = {"type": "poweroff"}
    response = ads1293_client.send(poweroff_request)
    print(f"  Response: {response}")
    assert response["type"] == "power_is_off"
    print(f"  ✓ Sensor powered off\n")

    # Step 3: Try to get data after poweroff
    print(f"[Step 3] Sending get_data after poweroff...")
    get_data_request = {"type": "get_data"}
    response = ads1293_client.send(get_data_request)
    print(f"  Response: {response}\n")

    # Step 4: Document the response
    print(f"[Step 4] Analyzing response...")
    print(f"  Response type: {response.get('type', 'MISSING')}")

    if response.get('type') == 'data':
        data_size = len(response.get('data', []))
        print(f"  Received 'data' response")
        print(f"  Data size: {data_size} samples")
        if data_size == 0:
            print(f"  ✓ Empty data (expected after poweroff)")
        else:
            print(f"  ⚠ Received data even after poweroff ({data_size} samples)")
    elif response.get('type') == 'error':
        print(f"  ✓ Received 'error' response")
        print(f"  Error message: {response.get('message', 'N/A')}")
    elif response.get('type') == 'no_measure':
        print(f"  ✓ Received 'no_measure' response")
    else:
        print(f"  Response type: {response.get('type')}")

    print(f"\n[Step 5] Test Results:")
    print(f"  Behavior: get_data after poweroff returns type='{response.get('type')}'")

    assert 'type' in response, "Response should contain 'type' field"

    print(f"\n{'='*70}")
    print(f"✓ Test COMPLETED: Behavior documented")
    print(f"{'='*70}\n")

    return {
        'test_case': '43.2',
        'scenario': 'get_data after poweroff',
        'response_type': response.get('type'),
        'response': response
    }


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_get_data_conversion_disabled(ads1293_client):
    """
    Test Case 43.3: Call get_data with enable_conversion=False.

    Test Steps:
    1. Send settings with enable_conversion=False
    2. Call get_data
    3. Record response
    """
    print(f"\n{'='*70}")
    print(f"Test Case 43.3: get_data With Conversion Disabled")
    print(f"{'='*70}\n")

    # Step 1: Configure with conversion disabled
    print(f"[Step 1] Configuring with enable_conversion=False...")
    settings_request = {
        "type": "settings",
        "enable_conversion": False
    }
    response = ads1293_client.send(settings_request)
    print(f"  Response: {response}")
    assert response["type"] == "actual_settings"
    print(f"  ✓ Conversion disabled\n")

    # Step 2: Try to get data
    print(f"[Step 2] Sending get_data with conversion disabled...")
    get_data_request = {"type": "get_data"}
    response = ads1293_client.send(get_data_request)
    print(f"  Response: {response}\n")

    # Step 3: Document the response
    print(f"[Step 3] Analyzing response...")
    print(f"  Response type: {response.get('type', 'MISSING')}")

    if response.get('type') == 'data':
        data_size = len(response.get('data', []))
        print(f"  Received 'data' response")
        print(f"  Data size: {data_size} samples")
        if data_size == 0:
            print(f"  ✓ Empty data (expected when conversion disabled)")
        else:
            print(f"  ⚠ Received data even with conversion disabled ({data_size} samples)")
    elif response.get('type') == 'error':
        print(f"  ✓ Received 'error' response")
        print(f"  Error message: {response.get('message', 'N/A')}")
    elif response.get('type') == 'no_measure':
        print(f"  ✓ Received 'no_measure' response")
    else:
        print(f"  Response type: {response.get('type')}")

    print(f"\n[Step 4] Test Results:")
    print(f"  Behavior: get_data with conversion disabled returns type='{response.get('type')}'")

    assert 'type' in response, "Response should contain 'type' field"

    print(f"\n{'='*70}")
    print(f"✓ Test COMPLETED: Behavior documented")
    print(f"{'='*70}\n")

    return {
        'test_case': '43.3',
        'scenario': 'get_data with enable_conversion=False',
        'response_type': response.get('type'),
        'response': response
    }


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_multiple_get_data_no_config(ads1293_client):
    """
    Test Case 43.4: Call get_data multiple times without configuration.

    Test Steps:
    1. Call get_data 3 times in succession without any configuration
    2. Record all responses
    3. Check if behavior is consistent
    """
    print(f"\n{'='*70}")
    print(f"Test Case 43.4: Multiple get_data Calls Without Configuration")
    print(f"{'='*70}\n")

    responses = []

    print(f"[Step 1] Sending get_data 3 times without configuration...\n")

    for i in range(3):
        print(f"  Call {i+1}/3:")
        request = {"type": "get_data"}
        response = ads1293_client.send(request)
        responses.append(response)
        print(f"    Response type: {response.get('type')}")
        if response.get('type') == 'data':
            print(f"    Data size: {len(response.get('data', []))} samples")
        print()

        # Small delay between requests
        time.sleep(0.1)

    # Step 2: Analyze consistency
    print(f"[Step 2] Analyzing consistency...")
    response_types = [r.get('type') for r in responses]
    print(f"  Response types: {response_types}")

    if len(set(response_types)) == 1:
        print(f"  ✓ Consistent behavior: All responses have type='{response_types[0]}'")
    else:
        print(f"  ⚠ Inconsistent behavior: Multiple response types detected")

    print(f"\n[Step 3] Test Results:")
    print(f"  All responses received successfully")
    print(f"  No crashes or hangs observed")

    print(f"\n{'='*70}")
    print(f"✓ Test COMPLETED: Behavior documented")
    print(f"{'='*70}\n")

    return {
        'test_case': '43.4',
        'scenario': 'multiple get_data without configuration',
        'response_types': response_types,
        'consistent': len(set(response_types)) == 1
    }


if __name__ == "__main__":
    # Allow running test directly for debugging
    import yaml

    config_path = Path(__file__).parent.parent / "config" / "test_config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Create mock client for standalone testing
    class MockTestConfig:
        def __init__(self, config):
            self.config = config
        def __getitem__(self, key):
            return self.config[key]

    test_cfg = MockTestConfig(config)

    print("Running ADS1293 get_data before configuration tests...")
    print("=" * 70)

    with TCPClient(config['services']['ads1293']['host'],
                   config['services']['ads1293']['port']) as client:

        # Mock fixture
        class MockFixture:
            def __init__(self, client):
                self.client = client
            def send_json(self, data):
                return self.client.send(data)

        fixture = MockFixture(client)

        print("\nTest 43.1: get_data without configuration")
        test_get_data_no_configuration(fixture)

        print("\nTest 43.2: get_data after poweroff")
        test_get_data_after_poweroff(fixture)

        print("\nTest 43.3: get_data with conversion disabled")
        test_get_data_conversion_disabled(fixture)

        print("\nTest 43.4: multiple get_data without configuration")
        test_multiple_get_data_no_config(fixture)

    print("\n" + "=" * 70)
    print("All tests completed!")
