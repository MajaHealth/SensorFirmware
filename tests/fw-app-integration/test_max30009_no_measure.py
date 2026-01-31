"""
Test Case 34: MAX30009 get_data When Not Measuring Returns no_measure

Tests that get_data returns {"type":"no_measure"} when MAX30009 is not in measurement mode.

Test Steps:
1) Ensure MAX30009 is not in measurement mode (e.g., prior to start_measuring or
   after measurement is stopped/powered off)
2) Send get_data request
3) Capture response

Pass Criteria:
Response is {"type":"no_measure"} when not in measurement mode.
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

    Note: The max30009_cleanup fixture (from conftest.py) ensures clean state
    before and after this test runs.
    """
    max_config = test_config['services']['max30009']

    with TCPClient(max_config['host'], max_config['port']) as client:
        yield client


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_not_measuring_fresh_connection(max30009_client):
    """
    Test Case 34: get_data when not measuring (fresh connection).

    Ensures MAX30009 is not in measurement mode (fixture ensures MMD_STOP state).
    Sends get_data request and verifies response is "no_measure".

    Note: Fixture already stopped measurement and cleared state, so firmware
    should be in MMD_STOP state when test starts.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 34: get_data When Not Measuring (Fresh Connection)")
    print(f"{'='*70}")

    # Step 1: Verify not in measurement mode (fixture already ensured this)
    print(f"\n[Step 1] Firmware state prepared by fixture")
    print(f"✓ Fixture stopped measurement and cleared async messages")
    print(f"✓ State should be MMD_STOP")

    # Step 2: Send get_data request
    print(f"\n[Step 2] Sending get_data request...")
    get_data_request = {"type": "get_data"}
    response = max30009_client.send(get_data_request)

    # Step 3: Capture and validate response
    print(f"\n[Step 3] Validating response...")
    print(f"Response: {response}")

    # Pass criteria: Response is {"type":"no_measure"}
    assert response.get('type') == 'no_measure', \
        f"Expected 'no_measure', got '{response.get('type')}'"

    print(f"✓ Response is 'no_measure' (PASS)")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 34 PASSED")
    print(f"{'='*70}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_not_measuring_after_stop(max30009_client):
    """
    Test Case 34: get_data when not measuring (after stopping measurement).

    Ensures MAX30009 is not in measurement mode by setting measure_enable=False.
    Sends get_data request and verifies response is "no_measure".
    """
    print(f"\n{'='*70}")
    print(f"Test Case 34: get_data When Not Measuring (After Stop)")
    print(f"{'='*70}")

    # Step 1: Ensure not in measurement mode (send settings with measure_enable=False)
    print(f"\n[Step 1] Stopping measurement (measure_enable=False)...")
    settings_request = {
        "type": "settings",
        "measure_enable": False,
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    response = max30009_client.send(settings_request)
    print(f"Settings response: {response.get('type')}")
    assert response.get('type') == 'actual_settings', \
        f"Expected 'actual_settings', got '{response.get('type')}'"
    print(f"✓ State is MMD_STOP (measurement stopped)")

    # Step 2: Send get_data request
    print(f"\n[Step 2] Sending get_data request...")
    get_data_request = {"type": "get_data"}
    response = max30009_client.send(get_data_request)

    # Step 3: Capture and validate response
    print(f"\n[Step 3] Validating response...")
    print(f"Response: {response}")

    # Pass criteria: Response is {"type":"no_measure"}
    assert response.get('type') == 'no_measure', \
        f"Expected 'no_measure', got '{response.get('type')}'"

    print(f"✓ Response is 'no_measure' (PASS)")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 34 PASSED")
    print(f"{'='*70}")


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_not_measuring_after_poweroff(max30009_client):
    """
    Test Case 34: get_data when not measuring (after poweroff).

    Ensures MAX30009 is not in measurement mode by sending poweroff command.
    Sends get_data request and verifies response is "no_measure".
    """
    print(f"\n{'='*70}")
    print(f"Test Case 34: get_data When Not Measuring (After Poweroff)")
    print(f"{'='*70}")

    # Step 1: Ensure not in measurement mode (send poweroff)
    print(f"\n[Step 1] Sending poweroff command...")
    poweroff_request = {"type": "poweroff"}
    response = max30009_client.send(poweroff_request)

    print(f"Poweroff response: {response.get('type')}")
    assert response.get('type') == 'power_is_off', \
        f"Expected 'power_is_off', got '{response.get('type')}'"
    print(f"✓ Power is off (not in measurement mode)")

    # Step 2: Send get_data request
    print(f"\n[Step 2] Sending get_data request...")
    get_data_request = {"type": "get_data"}
    response = max30009_client.send(get_data_request)

    # Step 3: Capture and validate response
    print(f"\n[Step 3] Validating response...")
    print(f"Response: {response}")

    # Pass criteria: Response is {"type":"no_measure"}
    assert response.get('type') == 'no_measure', \
        f"Expected 'no_measure', got '{response.get('type')}'"

    print(f"✓ Response is 'no_measure' (PASS)")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 34 PASSED")
    print(f"{'='*70}")
