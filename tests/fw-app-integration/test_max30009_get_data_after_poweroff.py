"""
Test Case 38: MAX30009 get_data after poweroff returns no_measure

Tests that get_data returns no_measure after MAX30009 is powered off.

Test Steps:
1. Send poweroff and confirm power_is_off response
2. Send get_data request
3. Capture and validate response

Pass Criteria:
- poweroff returns {"type":"power_is_off"}
- get_data returns {"type":"no_measure"}

Based on firmware: MAX30009_process.cpp lines 346-349
- get_data checks if _meas_mode == MMD_MEASURING
- After poweroff, device is not in measurement mode
- Returns {"type":"no_measure"}
"""
import pytest
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


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_get_data_after_poweroff(max30009_client):
    """
    Test Case 38: get_data after poweroff returns no_measure.

    Verifies that after powering off MAX30009, get_data correctly
    returns no_measure response indicating device is not measuring.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 38: get_data After Poweroff Returns no_measure")
    print(f"{'='*70}")

    # Step 1: Send poweroff and confirm response
    print(f"\n[Step 1] Sending poweroff command...")
    poweroff_request = {"type": "poweroff"}
    response = max30009_client.send(poweroff_request)

    print(f"Poweroff response: {response}")
    assert response.get('type') == 'power_is_off', \
        f"Expected 'power_is_off', got '{response.get('type')}'"
    print(f"✓ Power is off")

    # Step 2: Send get_data request
    print(f"\n[Step 2] Sending get_data request...")
    get_data_request = {"type": "get_data"}
    response = max30009_client.send(get_data_request)

    # Step 3: Validate response
    print(f"\n[Step 3] Validating response...")
    print(f"Response: {response}")

    assert response.get('type') == 'no_measure', \
        f"Expected 'no_measure', got '{response.get('type')}'"

    print(f"✓ Response is 'no_measure' (PASS)")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 38 PASSED")
    print(f"{'='*70}")
    print(f"Summary:")
    print(f"  - Step 1: poweroff → power_is_off ✓")
    print(f"  - Step 2: get_data → no_measure ✓")
    print(f"  - After poweroff, device not in measurement mode")
    print(f"{'='*70}")
