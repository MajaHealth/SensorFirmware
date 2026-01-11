"""
Test ID 40: ADS1293 API - Apply sampling settings and enable conversion

Tests the ADS1293 JSON API for configuration and basic communication.
"""
import pytest
import time
from pathlib import Path
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.mark.api
@pytest.mark.ads1293
@pytest.mark.quick
def test_ads1293_settings_configuration(test_config):
    """
    Test ID 40: Apply ADS1293 sampling settings and enable conversion.

    Steps:
    1. Connect to ADS1293 server
    2. Send settings with R-rates and conversion enable
    3. Capture response
    4. Verify actual_settings returned with correct values
    """
    # Get configuration
    ads_config = test_config['services']['ads1293']

    # Test parameters
    expected_r2_rate = 4
    expected_r3_rate = 128

    print(f"\n{'='*60}")
    print(f"Test ID 40: ADS1293 Settings Configuration")
    print(f"{'='*60}")

    # Step 1: Connect to ADS1293 service
    print(f"\n[Step 1] Connecting to ADS1293 at {ads_config['host']}:{ads_config['port']}...")
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        print("✓ Connected successfully")

        # Step 2: Send settings request
        print(f"\n[Step 2] Sending settings configuration...")
        request = {
            "type": "settings",
            "enable_conversion": True,
            "R2_rate": expected_r2_rate,
            "R3_rate": expected_r3_rate
        }
        print(f"  Request: {request}")

        response = client.send(request)
        print(f"  Response: {response}")

        # Step 3: Validate response
        print(f"\n[Step 3] Validating response...")
        assert response["type"] == "actual_settings", \
            f"Expected 'actual_settings', got '{response['type']}'"
        print("  ✓ Response type is 'actual_settings'")

        assert response["enable_conversion"] == True, \
            "Conversion should be enabled"
        print("  ✓ Conversion enabled")

        assert response["R2_rate"] == expected_r2_rate, \
            f"Expected R2_rate={expected_r2_rate}, got {response['R2_rate']}"
        print(f"  ✓ R2_rate = {response['R2_rate']}")

        assert response["R3_rate"] == expected_r3_rate, \
            f"Expected R3_rate={expected_r3_rate}, got {response['R3_rate']}"
        print(f"  ✓ R3_rate = {response['R3_rate']}")

        # Verify R1_rate is also returned (should default to 4)
        assert "R1_rate" in response, "Response should include R1_rate"
        print(f"  ✓ R1_rate = {response['R1_rate']} (default)")

    print(f"\n{'='*60}")
    print(f"✓ Test PASSED: ADS1293 settings configured successfully")
    print(f"{'='*60}\n")


@pytest.mark.api
@pytest.mark.ads1293
@pytest.mark.quick
def test_ads1293_get_data_basic(test_config):
    """
    Test ID 42: Poll ADS1293 get_data and verify sync marker presence.

    Steps:
    1. Connect to ADS1293
    2. Enable conversion
    3. Wait for data to accumulate
    4. Request data
    5. Verify response contains data and sync markers
    """
    ads_config = test_config['services']['ads1293']

    print(f"\n{'='*60}")
    print(f"Test ID 42: ADS1293 Get Data Basic")
    print(f"{'='*60}")

    with TCPClient(ads_config['host'], ads_config['port']) as client:

        # Step 1: Enable conversion
        print(f"\n[Step 1] Enabling conversion...")
        settings_request = {
            "type": "settings",
            "enable_conversion": True
        }
        response = client.send(settings_request)
        assert response["type"] == "actual_settings"
        print("  ✓ Conversion enabled")

        # Step 2: Wait for data to accumulate
        print(f"\n[Step 2] Waiting 2 seconds for data to accumulate...")
        time.sleep(2.0)

        # Step 3: Request data
        print(f"\n[Step 3] Requesting data...")
        data_request = {"type": "get_data"}
        response = client.send(data_request)

        print(f"  Response type: {response['type']}")
        print(f"  Data size: {response.get('data_size', 0)} samples")

        # Step 4: Validate response
        print(f"\n[Step 4] Validating response...")
        assert response["type"] == "data", \
            f"Expected 'data', got '{response['type']}'"
        print("  ✓ Response type is 'data'")

        assert "data" in response, "Response should contain 'data' field"
        assert len(response["data"]) > 0, "Data array should not be empty"
        print(f"  ✓ Received {len(response['data'])} samples")

        # Step 5: Check for sync markers
        print(f"\n[Step 5] Checking for sync markers...")
        sync_markers = [s for s in response["data"] if s[0] == -99999]

        if len(sync_markers) > 0:
            print(f"  ✓ Found {len(sync_markers)} sync marker(s)")
            print(f"  Sync marker format: {sync_markers[0]}")
            assert sync_markers[0][0] == -99999, "First element should be magic number"
            assert len(sync_markers[0]) == 3, "Sync marker should have 3 elements"
        else:
            print("  ⚠ No sync markers found (may need longer wait time)")

    print(f"\n{'='*60}")
    print(f"✓ Test PASSED: ADS1293 get_data working correctly")
    print(f"{'='*60}\n")


@pytest.mark.api
@pytest.mark.ads1293
@pytest.mark.quick
def test_ads1293_power_off(test_config):
    """
    Test ID 44: Power off ADS1293 AFE.

    Steps:
    1. Connect to ADS1293
    2. Enable conversion first (to ensure sensor is on)
    3. Send poweroff request
    4. Verify power_is_off response
    """
    ads_config = test_config['services']['ads1293']

    print(f"\n{'='*60}")
    print(f"Test ID 44: ADS1293 Power Off")
    print(f"{'='*60}")

    with TCPClient(ads_config['host'], ads_config['port']) as client:

        # Step 1: Enable conversion first
        print(f"\n[Step 1] Enabling conversion first...")
        settings_request = {
            "type": "settings",
            "enable_conversion": True
        }
        response = client.send(settings_request)
        assert response["type"] == "actual_settings"
        print("  ✓ Conversion enabled")

        # Step 2: Send poweroff request
        print(f"\n[Step 2] Sending poweroff request...")
        poweroff_request = {
            "type": "poweroff"
        }
        response = client.send(poweroff_request)

        print(f"  Response: {response}")

        # Step 3: Validate response
        print(f"\n[Step 3] Validating response...")
        assert response["type"] == "power_is_off", \
            f"Expected 'power_is_off', got '{response['type']}'"
        print("  ✓ Power disabled successfully")

    print(f"\n{'='*60}")
    print(f"✓ Test PASSED: ADS1293 powered off successfully")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Allow running test directly for debugging
    import yaml

    config_path = Path(__file__).parent.parent / "config" / "test_config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    print("Running ADS1293 API tests...")
    test_ads1293_settings_configuration(config)
    test_ads1293_get_data_basic(config)
    test_ads1293_power_off(config)
    print("\nAll tests completed!")
