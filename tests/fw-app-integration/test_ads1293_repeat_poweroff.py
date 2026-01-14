"""
Test Case 45: Repeat Poweroff Then Re-enable Conversion

Category: FW-APP Integration
Components: ADS1293 AFE + Firmware ADS1293 service

Test Steps:
1. Send poweroff and confirm response
2. Send settings to re-enable conversion
3. Capture actual_settings

Pass Criteria:
- poweroff returns power_is_off
- Subsequent settings returns actual_settings
"""

import pytest
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.fixture
def ads1293_client(test_config):
    """Create TCP client for ADS1293 service."""
    ads_config = test_config['services']['ads1293']
    client = TCPClient(ads_config['host'], ads_config['port'])
    client.connect()
    yield client
    client.close()


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_repeat_poweroff_then_reenable(ads1293_client):
    """
    Test Case 45: Repeat poweroff then re-enable conversion.

    Validates that:
    1. poweroff command works and returns power_is_off
    2. Can re-enable conversion after poweroff
    3. actual_settings returned after re-enabling
    """

    # Step 1: Send poweroff
    print("\n[Step 1] Sending poweroff command...")
    poweroff_request = {
        "type": "poweroff"
    }

    response = ads1293_client.send_json(poweroff_request)

    print(f"Poweroff response: {response}")

    # Validate poweroff response
    assert 'type' in response, "Response missing 'type' field"
    assert response['type'] == 'power_is_off', \
        f"Expected 'power_is_off', got '{response['type']}'"

    print("✓ Poweroff successful")

    # Step 2: Re-enable conversion
    print("\n[Step 2] Re-enabling conversion...")
    settings_request = {
        "type": "settings",
        "enable_conversion": True,
        "R2_rate": 4,
        "R3_rate": 16
    }

    response = ads1293_client.send_json(settings_request)

    print(f"Settings response: {response}")

    # Step 3: Validate actual_settings returned
    assert 'type' in response, "Response missing 'type' field"
    assert response['type'] == 'actual_settings', \
        f"Expected 'actual_settings', got '{response['type']}'"

    assert 'enable_conversion' in response, "Response missing 'enable_conversion'"
    assert response['enable_conversion'] == True, \
        "Conversion not enabled"

    assert 'R2_rate' in response, "Response missing 'R2_rate'"
    assert 'R3_rate' in response, "Response missing 'R3_rate'"

    print("✓ Re-enabled conversion successfully")
    print(f"✓ Actual settings: enable_conversion={response['enable_conversion']}, "
          f"R2_rate={response['R2_rate']}, R3_rate={response['R3_rate']}")


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_multiple_poweroff_cycles(ads1293_client):
    """
    Test Case 45.1: Multiple poweroff/re-enable cycles.

    Validates that poweroff and re-enable can be repeated multiple times.
    """

    print("\n[Test] Multiple poweroff/re-enable cycles...")

    num_cycles = 3

    for i in range(1, num_cycles + 1):
        print(f"\n--- Cycle {i}/{num_cycles} ---")

        # Poweroff
        poweroff_request = {"type": "poweroff"}
        response = ads1293_client.send_json(poweroff_request)

        assert response['type'] == 'power_is_off', \
            f"Cycle {i}: poweroff failed"
        print(f"  ✓ Poweroff successful")

        # Re-enable
        settings_request = {
            "type": "settings",
            "enable_conversion": True,
            "R2_rate": 4,
            "R3_rate": 16
        }
        response = ads1293_client.send_json(settings_request)

        assert response['type'] == 'actual_settings', \
            f"Cycle {i}: re-enable failed"
        assert response['enable_conversion'] == True, \
            f"Cycle {i}: conversion not enabled"
        print(f"  ✓ Re-enable successful")

    print(f"\n✓ All {num_cycles} cycles completed successfully")


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
def test_poweroff_then_settings_disabled(ads1293_client):
    """
    Test Case 45.2: Poweroff then send settings with enable_conversion=False.

    Validates behavior when enabling conversion is explicitly set to False
    after poweroff.
    """

    print("\n[Test] Poweroff then settings with enable_conversion=False...")

    # Step 1: Poweroff
    poweroff_request = {"type": "poweroff"}
    response = ads1293_client.send_json(poweroff_request)

    assert response['type'] == 'power_is_off'
    print("✓ Poweroff successful")

    # Step 2: Send settings with enable_conversion=False
    settings_request = {
        "type": "settings",
        "enable_conversion": False,
        "R2_rate": 4,
        "R3_rate": 16
    }
    response = ads1293_client.send_json(settings_request)

    print(f"Settings response: {response}")

    assert response['type'] == 'actual_settings', \
        f"Expected 'actual_settings', got '{response['type']}'"
    assert response['enable_conversion'] == False, \
        "Expected enable_conversion=False"

    print("✓ Settings accepted with enable_conversion=False")
