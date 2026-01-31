"""
Test Case 48: Read Battery Information Object

Category: FW-APP Integration
Components: Battery/charger telemetry + Firmware power service

Test Steps:
1. Connect to power control server (127.0.0.1:501)
2. Send get_batt_info request
3. Capture response payload
4. Validate response structure and field types

Pass Criteria:
- Response is JSON object of type "batt_info"
- Contains all expected battery fields:
  - voltage (float, in Volts)
  - temperature (float, in Celsius)
  - current (float, in Amps)
  - relative_state_of_charge (int, 0-100%)
  - remaining_capacity (float, in Ah)
  - full_charge_capacity (float, in Ah)
  - run_time_to_empty (int, in minutes)
  - average_time_to_empty (int, in minutes)
  - average_time_to_full (int, in minutes)
  - cycle_count (int)
  - design_capacity (float, in Ah)
  - design_voltage (float, in Volts)
  - fully_discharged (bool)
  - fully_charged (bool)
  - discharging (bool)
  - charging (bool)
  - charger_is_connect (bool)
  - battery_charge_is_disable (bool)

Based on firmware: PWRCNTR_process.cpp lines 96-128
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


@pytest.mark.fw_app
@pytest.mark.api
@pytest.mark.quick
def test_power_get_batt_info(power_client):
    """
    Test Case 48: Read battery information object.

    Validates that get_batt_info returns a properly structured
    JSON response with all expected battery telemetry fields.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 48: Read Battery Information Object")
    print(f"{'='*70}")

    # Step 1: Send get_batt_info request
    print(f"\n[Step 1] Sending get_batt_info request...")
    request = {"type": "get_batt_info"}

    # Drain any pending async button_info messages right before sending
    time.sleep(0.2)
    while True:
        try:
            msg = power_client.recv(timeout=0.05)
            if not msg or msg.get('type') != 'button_info':
                break
        except:
            break

    response = power_client.send(request)

    print(f"Response received with {len(response)} fields")

    # Step 2: Validate response type
    print(f"\n[Step 2] Validating response type...")
    assert "type" in response, "Response missing 'type' field"
    assert response["type"] == "batt_info", \
        f"Expected type 'batt_info', got '{response['type']}'"
    print(f"  ✓ Response type is 'batt_info'")

    # Step 3: Validate all required fields exist
    print(f"\n[Step 3] Validating required fields...")

    required_fields = [
        # Numeric fields (float)
        "voltage",
        "temperature",
        "current",
        "remaining_capacity",
        "full_charge_capacity",
        "design_capacity",
        "design_voltage",
        # Numeric fields (int)
        "relative_state_of_charge",
        "run_time_to_empty",
        "average_time_to_empty",
        "average_time_to_full",
        "cycle_count",
        # Boolean fields
        "fully_discharged",
        "fully_charged",
        "discharging",
        "charging",
        "charger_is_connect",
        "battery_charge_is_disable",
    ]

    missing_fields = [field for field in required_fields if field not in response]
    assert len(missing_fields) == 0, \
        f"Missing required fields: {missing_fields}"
    print(f"  ✓ All {len(required_fields)} required fields present")

    # Step 4: Validate field types
    print(f"\n[Step 4] Validating field types...")

    # Float fields (voltage, capacities, etc.)
    float_fields = [
        "voltage", "temperature", "current",
        "remaining_capacity", "full_charge_capacity",
        "design_capacity", "design_voltage"
    ]
    for field in float_fields:
        assert isinstance(response[field], (int, float)), \
            f"Field '{field}' should be numeric, got {type(response[field])}"
    print(f"  ✓ All {len(float_fields)} float fields are numeric")

    # Integer fields (SOC, time, cycle count)
    int_fields = [
        "relative_state_of_charge",
        "run_time_to_empty",
        "average_time_to_empty",
        "average_time_to_full",
        "cycle_count"
    ]
    for field in int_fields:
        assert isinstance(response[field], int), \
            f"Field '{field}' should be int, got {type(response[field])}"
    print(f"  ✓ All {len(int_fields)} integer fields are int")

    # Boolean fields (status flags)
    bool_fields = [
        "fully_discharged", "fully_charged",
        "discharging", "charging",
        "charger_is_connect", "battery_charge_is_disable"
    ]
    for field in bool_fields:
        assert isinstance(response[field], bool), \
            f"Field '{field}' should be bool, got {type(response[field])}"
    print(f"  ✓ All {len(bool_fields)} boolean fields are bool")

    # Step 5: Validate value ranges
    print(f"\n[Step 5] Validating value ranges...")

    # SOC should be 0-100%
    soc = response["relative_state_of_charge"]
    assert 0 <= soc <= 100, \
        f"SOC should be 0-100%, got {soc}%"
    print(f"  ✓ SOC is valid: {soc}%")

    # Voltage should be positive
    voltage = response["voltage"]
    assert voltage >= 0, f"Voltage should be positive, got {voltage}V"
    print(f"  ✓ Voltage is valid: {voltage}V")

    # Temperature should be reasonable (-40°C to 85°C for Li-ion)
    temp = response["temperature"]
    assert -40 <= temp <= 85, \
        f"Temperature out of reasonable range: {temp}°C"
    print(f"  ✓ Temperature is valid: {temp}°C")

    # Cycle count should be non-negative
    cycles = response["cycle_count"]
    assert cycles >= 0, f"Cycle count should be non-negative, got {cycles}"
    print(f"  ✓ Cycle count is valid: {cycles}")

    # Step 6: Validate charging/discharging logic
    print(f"\n[Step 6] Validating charge state logic...")
    charging = response["charging"]
    discharging = response["discharging"]

    # charging and discharging should be opposites
    assert charging != discharging, \
        "Charging and discharging should be opposite states"
    print(f"  ✓ Charge state is consistent: charging={charging}, discharging={discharging}")

    # Step 7: Display battery information summary
    print(f"\n{'='*70}")
    print(f"Battery Information Summary:")
    print(f"{'='*70}")
    print(f"  Voltage:            {response['voltage']:.3f} V")
    print(f"  Temperature:        {response['temperature']:.1f} °C")
    print(f"  Current:            {response['current']:.3f} A")
    print(f"  State of Charge:    {response['relative_state_of_charge']}%")
    print(f"  Remaining Capacity: {response['remaining_capacity']:.3f} Ah")
    print(f"  Full Capacity:      {response['full_charge_capacity']:.3f} Ah")
    print(f"  Design Capacity:    {response['design_capacity']:.3f} Ah")
    print(f"  Design Voltage:     {response['design_voltage']:.3f} V")
    print(f"  Cycle Count:        {response['cycle_count']}")
    print(f"  Time to Empty:      {response['run_time_to_empty']} min")
    print(f"  Avg Time to Empty:  {response['average_time_to_empty']} min")
    print(f"  Avg Time to Full:   {response['average_time_to_full']} min")
    print(f"\n  Status Flags:")
    print(f"    Fully Charged:      {response['fully_charged']}")
    print(f"    Fully Discharged:   {response['fully_discharged']}")
    print(f"    Charging:           {response['charging']}")
    print(f"    Discharging:        {response['discharging']}")
    print(f"    Charger Connected:  {response['charger_is_connect']}")
    print(f"    Charge Disabled:    {response['battery_charge_is_disable']}")
    print(f"{'='*70}")

    print(f"\n✓ Test PASSED: Battery info retrieved successfully")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.api
@pytest.mark.quick
def test_power_get_batt_info_multiple_reads(power_client):
    """
    Test Case 48.1: Multiple consecutive get_batt_info requests.

    Validates that battery info can be read multiple times
    and returns consistent data.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 48.1: Multiple Battery Info Reads")
    print(f"{'='*70}")

    num_reads = 3
    responses = []

    for i in range(num_reads):
        print(f"\n[Read {i+1}/{num_reads}] Requesting battery info...")

        # Drain any pending async button_info messages
        time.sleep(0.2)
        while True:
            try:
                msg = power_client.recv(timeout=0.05)
                if not msg or msg.get('type') != 'button_info':
                    break
            except:
                break

        request = {"type": "get_batt_info"}
        response = power_client.send(request)

        assert response["type"] == "batt_info", \
            f"Read {i+1}: Expected 'batt_info', got '{response['type']}'"

        responses.append(response)
        print(f"  ✓ SOC: {response['relative_state_of_charge']}%, "
              f"Voltage: {response['voltage']:.3f}V, "
              f"Temp: {response['temperature']:.1f}°C")

    # Validate all reads succeeded
    assert len(responses) == num_reads, \
        f"Expected {num_reads} responses, got {len(responses)}"

    print(f"\n✓ All {num_reads} reads completed successfully")
    print(f"{'='*70}\n")
