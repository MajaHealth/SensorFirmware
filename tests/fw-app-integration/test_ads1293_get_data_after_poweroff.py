"""
Test Case 50: ADS1293 get_data After Poweroff

Category: FW-APP Integration (Robustness)
Components: ADS1293 + Firmware + Client

Test Steps:
1. Send poweroff to ADS1293 and confirm power_is_off
2. Send get_data and capture response

Pass Criteria:
- Behavior not defined in provided ADS1293 examples
- Record observed behavior for requirement clarification
- Service remains stable (no crashes)
- Response is consistent across multiple attempts
"""

import pytest
import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


@pytest.fixture
def ads1293_client(test_config):
    """Create TCP client for ADS1293 service with cleanup."""
    ads_config = test_config['services']['ads1293']
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        yield client

        # Cleanup: Ensure powered off
        try:
            client.send({"type": "poweroff"})
        except:
            pass


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
@pytest.mark.robustness
def test_ads1293_get_data_after_poweroff(test_config, ads1293_client):
    """
    Test Case 50: Document behavior of get_data after ADS1293 poweroff.

    This is an exploratory test - expected behavior is not defined in spec.
    We record actual behavior for requirements clarification.

    Compares to TC-028 (MAX30009 get_data after poweroff) which returns "no_measure".
    """

    ecg_params = test_config['ads1293_ecg']
    r2_rate = ecg_params['r2_rate']
    r3_rate = ecg_params['r3_rate']

    print(f"\n{'='*70}")
    print(f"Test Case 50: ADS1293 get_data After Poweroff")
    print(f"{'='*70}")
    print(f"Purpose: Document undefined behavior for requirements clarification")
    print(f"Comparison: TC-028 (MAX30009) returns 'no_measure' after poweroff")
    print(f"{'='*70}\n")

    # Step 1: Configure ADS1293 and verify it works
    print(f"[Step 1] Configuring ADS1293 and verifying operation...")

    settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": r2_rate,
        "R3_rate": r3_rate
    }

    config_response = ads1293_client.send(settings)
    assert config_response["type"] == "actual_settings", \
        f"Configuration failed: {config_response}"

    print(f"  ✓ Configuration successful")
    print(f"    - R2_rate: {config_response.get('R2_rate')}")
    print(f"    - R3_rate: {config_response.get('R3_rate')}")
    print(f"    - Conversion enabled: {config_response.get('enable_conversion')}\n")

    # Wait for stabilization
    time.sleep(2.0)

    # Get data to verify working
    initial_data = ads1293_client.send({"type": "get_data"})
    assert initial_data["type"] == "data", \
        f"Initial get_data failed: {initial_data}"

    sample_count = len(initial_data.get("data", []))
    print(f"  ✓ get_data returns 'data' (working correctly)")
    print(f"    - Sample count: {sample_count}")
    print(f"    - Service state: OPERATIONAL\n")

    # Step 2: Power off ADS1293
    print(f"[Step 2] Powering off ADS1293...")

    poweroff_response = ads1293_client.send({"type": "poweroff"})

    assert poweroff_response["type"] == "power_is_off", \
        f"Poweroff failed: Expected 'power_is_off', got '{poweroff_response.get('type')}'"

    print(f"  ✓ poweroff returned 'power_is_off'")
    print(f"    - ADS1293 AFE: POWERED OFF")
    print(f"    - Service: Still running (TCP active)\n")

    # Step 3: Attempt get_data after poweroff (multiple times for consistency)
    print(f"[Step 3] Testing get_data after poweroff (5 attempts for consistency)...\n")

    responses = []
    num_attempts = 5

    for attempt in range(1, num_attempts + 1):
        try:
            response = ads1293_client.send({"type": "get_data"})
            responses.append(response)

            response_type = response.get("type", "unknown")
            response_str = json.dumps(response) if len(json.dumps(response)) < 80 else \
                           f'{{"type": "{response_type}", ...}}'

            print(f"  Attempt {attempt}/{num_attempts}: {response_type}")
            print(f"    Response: {response_str}")

        except Exception as e:
            print(f"  Attempt {attempt}/{num_attempts}: EXCEPTION - {type(e).__name__}: {e}")
            responses.append({"type": "exception", "error": str(e)})

        time.sleep(0.5)

    print()

    # Step 4: Analyze consistency
    print(f"[Step 4] Analyzing response consistency...")

    response_types = [r.get("type", "unknown") for r in responses]
    unique_types = set(response_types)

    print(f"  Response types observed: {list(unique_types)}")
    print(f"  Consistency: {len(unique_types)} unique response(s) across {num_attempts} attempts")

    if len(unique_types) == 1:
        print(f"  ✓ CONSISTENT - All responses are '{response_types[0]}'\n")
        consistent = True
    else:
        print(f"  ✗ INCONSISTENT - Multiple response types observed")
        for rtype in unique_types:
            count = response_types.count(rtype)
            print(f"    - '{rtype}': {count}/{num_attempts} times")
        print()
        consistent = False

    assert consistent, \
        f"Inconsistent responses: {response_types}"

    # Step 5: Document observed behavior
    print(f"[Step 5] Documenting observed behavior...\n")

    observed_type = response_types[0]
    full_response = responses[0]

    behavior_report = {
        "test_case": "TC-050",
        "test_name": "ADS1293 get_data after poweroff",
        "component": "ADS1293",
        "scenario": "get_data called after poweroff",
        "observed_response_type": observed_type,
        "full_response_example": full_response,
        "consistency": f"{num_attempts}/{num_attempts} attempts",
        "comparison": {
            "TC-028": "MAX30009 get_data after poweroff",
            "TC-028_behavior": "no_measure",
            "match": observed_type == "no_measure"
        },
        "service_stability": "Stable (no crashes)",
        "timestamp": datetime.now().isoformat()
    }

    print(f"{'='*70}")
    print(f"BEHAVIOR DOCUMENTATION:")
    print(f"{'='*70}")
    print(json.dumps(behavior_report, indent=2))
    print(f"{'='*70}\n")

    # Step 6: Verify service can be restarted
    print(f"[Step 6] Verifying service can be reconfigured after test...")

    # Re-enable conversion
    reconfig_response = ads1293_client.send(settings)

    assert reconfig_response["type"] == "actual_settings", \
        f"Re-configuration failed: {reconfig_response}"

    print(f"  ✓ Re-configuration successful")
    print(f"    - Service can be restarted after poweroff state\n")

    # Wait for stabilization
    time.sleep(2.0)

    # Verify data collection works again
    recovery_data = ads1293_client.send({"type": "get_data"})

    assert recovery_data["type"] == "data", \
        f"Recovery verification failed: {recovery_data}"

    recovery_samples = len(recovery_data.get("data", []))
    print(f"  ✓ get_data returns 'data' after restart")
    print(f"    - Sample count: {recovery_samples}")
    print(f"    - Service recovery: SUCCESSFUL\n")

    # Final poweroff for cleanup
    final_poweroff = ads1293_client.send({"type": "poweroff"})
    assert final_poweroff["type"] == "power_is_off"

    # Summary
    print(f"{'='*70}")
    print(f"Test Summary - TC-050")
    print(f"{'='*70}")
    print(f"Observed Behavior:     '{observed_type}'")
    print(f"Consistency:           {num_attempts}/{num_attempts} attempts")
    print(f"TC-028 Comparison:     {'MATCH' if observed_type == 'no_measure' else 'DIFFERENT'}")
    print(f"  TC-028 (MAX30009):   'no_measure'")
    print(f"  TC-050 (ADS1293):    '{observed_type}'")
    print(f"Service Stability:     ✓ No crashes")
    print(f"Service Recovery:      ✓ Can be restarted")
    print(f"")
    print(f"Recommendation:")
    if observed_type == "no_measure":
        print(f"  Behavior matches MAX30009 pattern.")
        print(f"  Consider documenting 'no_measure' as expected behavior.")
    elif observed_type == "power_is_off":
        print(f"  Explicit poweroff state response.")
        print(f"  Consider documenting as expected behavior.")
    elif observed_type == "data":
        print(f"  Returns data despite being powered off.")
        print(f"  May indicate state tracking issue - investigate further.")
    else:
        print(f"  Unexpected response type: '{observed_type}'")
        print(f"  Review firmware implementation and define requirements.")
    print(f"")
    print(f"Result:                PASS (behavior documented) ✓")
    print(f"{'='*70}\n")

    # Note: Test passes as long as behavior is consistent and service is stable
    # Actual response type doesn't matter for this exploratory test
