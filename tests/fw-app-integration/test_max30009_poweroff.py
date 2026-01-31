"""
Test Case 37: MAX30009 Power Off AFE

Tests the poweroff command which disables power to the MAX30009 AFE chip.

Test Steps:
1. Connect to MAX30009 server
2. Send poweroff request
3. Capture response

Pass Criteria:
- Response is {"type":"power_is_off"}

Based on firmware: MAX30009_process.cpp lines 356-360
- Calls set_power_state(false) to disable GPIO power
- Calls max30009_ext_MUX_obj.off_all_out() to disable MUX outputs
- Returns {"type":"power_is_off"}
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


@pytest.mark.fw_app
@pytest.mark.max30009
@pytest.mark.quick
def test_max30009_poweroff(max30009_client):
    """
    Test Case 37: MAX30009 poweroff command.

    Sends poweroff request and validates response.
    The poweroff command disables power to the MAX30009 AFE chip.
    """
    print(f"\n{'='*70}")
    print(f"Test Case 37: MAX30009 Power Off AFE")
    print(f"{'='*70}")

    # Step 1: Send poweroff request
    print(f"\n[Step 1] Sending poweroff request...")
    poweroff_request = {"type": "poweroff"}

    response = max30009_client.send(poweroff_request)
    print(f"Response: {response}")

    # Step 2: Validate response
    print(f"\n[Step 2] Validating response...")
    assert response.get('type') == 'power_is_off', \
        f"Expected 'power_is_off', got '{response.get('type')}'"

    print(f"✓ Received: {{'type': 'power_is_off'}}")

    print(f"\n{'='*70}")
    print(f"✓ Test Case 37 PASSED")
    print(f"{'='*70}")
    print(f"Summary:")
    print(f"  - Command sent: poweroff")
    print(f"  - Response: power_is_off")
    print(f"  - MAX30009 AFE power disabled")
    print(f"{'='*70}")
