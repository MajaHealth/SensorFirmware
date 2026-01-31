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

        # Cleanup: Re-enable charging after test
        try:
            time.sleep(0.2)
            while True:
                try:
                    msg = client.recv(timeout=0.05)
                    if not msg or msg.get('type') != 'button_info':
                        break
                except:
                    break

            enable_request = {"type": "charge_enable"}
            client.send(enable_request)
        except:
            pass  # Ignore cleanup errors





@pytest.mark.fw_app
@pytest.mark.api
@pytest.mark.quick
def test_power_charge_enable(power_client):
    """
    Test Case 50: Enable charging via JSON command.

    Validates that charge_enable command properly enables battery
    charging and updates the battery_charge_is_disable status field.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 50: Enable Charging via JSON")
    print(f"{'='*70}")

    # Step 1: First disable charging to have a known starting state
    print(f"\n[Step 1] Disabling charging first (setup)...")

    # Drain pending async messages
    time.sleep(0.2)
    while True:
        try:
            msg = power_client.recv(timeout=0.05)
            if not msg or msg.get('type') != 'button_info':
                break
        except:
            break

    disable_request = {"type": "charge_disable"}
    response = power_client.send(disable_request)
    assert response["type"] == "charge_is_disable"
    print(f"  ✓ Charging disabled (setup complete)")

    # Step 2: Send charge_enable request
    print(f"\n[Step 2] Sending charge_enable request...")

    # Drain pending async messages
    time.sleep(0.2)
    while True:
        try:
            msg = power_client.recv(timeout=0.05)
            if not msg or msg.get('type') != 'button_info':
                break
        except:
            break

    request = {"type": "charge_enable"}
    response = power_client.send(request)

    print(f"Response: {response}")

    # Step 3: Validate charge_enable response
    print(f"\n[Step 3] Validating charge_enable response...")
    assert "type" in response, "Response missing 'type' field"
    assert response["type"] == "charge_is_enable", \
        f"Expected 'charge_is_enable', got '{response['type']}'"
    print(f"  ✓ Charge enable command acknowledged")

    # Step 4: Read battery info to verify charge enable state
    print(f"\n[Step 4] Reading battery info to verify charge state...")

    # Drain pending async messages
    time.sleep(0.2)
    while True:
        try:
            msg = power_client.recv(timeout=0.05)
            if not msg or msg.get('type') != 'button_info':
                break
        except:
            break

    batt_info_request = {"type": "get_batt_info"}
    batt_info = power_client.send(batt_info_request)

    print(f"Battery info received")

    # Step 5: Validate battery_charge_is_disable field
    print(f"\n[Step 5] Validating battery_charge_is_disable status...")
    assert "battery_charge_is_disable" in batt_info, \
        "Battery info missing 'battery_charge_is_disable' field"

    assert batt_info["battery_charge_is_disable"] == False, \
        f"Expected battery_charge_is_disable=False, got {batt_info['battery_charge_is_disable']}"
    print(f"  ✓ Battery charge is enabled: {not batt_info['battery_charge_is_disable']}")

    print(f"\n{'='*70}")
    print(f"Battery Status Summary:")
    print(f"{'='*70}")
    print(f"  Charge Disabled:    {batt_info['battery_charge_is_disable']}")
    print(f"  Charger Connected:  {batt_info['charger_is_connect']}")
    print(f"  Charging:           {batt_info['charging']}")
    print(f"  Discharging:        {batt_info['discharging']}")
    print(f"  SOC:                {batt_info['relative_state_of_charge']}%")
    print(f"{'='*70}")

    print(f"\n✓ Test PASSED: Charging enabled successfully")
    print(f"{'='*70}\n")


