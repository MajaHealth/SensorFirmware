"""
Test Case 41: Invalid ADS1293 Rate Parameters Handling

Category: FW-APP Integration
Components: ADS1293 AFE + Firmware ADS1293 service
Test Name: Invalid ADS1293 rate parameters handling

Prerequisites:
- DUT with ADS1293 service reachable on port 1293
- Log capture enabled

Pass Criteria:
- Record observed responses for invalid parameter values
- Document firmware behavior for spec clarification
"""

import pytest
import sys
from pathlib import Path

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
@pytest.mark.invalid_params
@pytest.mark.quick
def test_invalid_r1_rate(ads1293_client):
    """
    Test Case 41.1: Invalid R1_rate values

    Valid R1_rate values: 2, 4
    Test invalid values: 0, 1, 3, 5, 8, 16, -1
    """
    print("\n" + "="*70)
    print("Test Case 41.1: Invalid R1_rate Parameter Tests")
    print("="*70)

    valid_r1_values = [2, 4]
    invalid_r1_values = [0, 1, 3, 5, 8, 16, -1, 100]

    print(f"\nValid R1_rate values (per spec): {valid_r1_values}")
    print(f"Testing invalid R1_rate values: {invalid_r1_values}\n")

    results = []

    for r1_val in invalid_r1_values:
        print(f"[Test] Sending R1_rate = {r1_val}")

        request = {
            "type": "settings",
            "enable_conversion": True,
            "R1_rate": r1_val,
            "R2_rate": 8,
            "R3_rate": 128
        }

        response = ads1293_client.send_json(request)

        print(f"  Request:  {request}")
        print(f"  Response: {response}")

        results.append({
            'parameter': 'R1_rate',
            'invalid_value': r1_val,
            'request': request,
            'response': response,
            'response_type': response.get('type', 'unknown')
        })
        print()

    # Summary
    print("\n" + "="*70)
    print("R1_rate Invalid Parameter Test Summary:")
    print("="*70)
    for result in results:
        print(f"R1_rate={result['invalid_value']:4d} -> Response type: '{result['response_type']}'")

    return results


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.invalid_params
@pytest.mark.quick
def test_invalid_r2_rate(ads1293_client):
    """
    Test Case 41.2: Invalid R2_rate values

    Valid R2_rate values: 4, 5, 6, 8
    Test invalid values: 0, 1, 2, 3, 7, 9, 16, -1
    """
    print("\n" + "="*70)
    print("Test Case 41.2: Invalid R2_rate Parameter Tests")
    print("="*70)

    valid_r2_values = [4, 5, 6, 8]
    invalid_r2_values = [0, 1, 2, 3, 7, 9, 16, 32, -1, 100]

    print(f"\nValid R2_rate values (per spec): {valid_r2_values}")
    print(f"Testing invalid R2_rate values: {invalid_r2_values}\n")

    results = []

    for r2_val in invalid_r2_values:
        print(f"[Test] Sending R2_rate = {r2_val}")

        request = {
            "type": "settings",
            "enable_conversion": True,
            "R1_rate": 4,
            "R2_rate": r2_val,
            "R3_rate": 128
        }

        response = ads1293_client.send_json(request)

        print(f"  Request:  {request}")
        print(f"  Response: {response}")

        results.append({
            'parameter': 'R2_rate',
            'invalid_value': r2_val,
            'request': request,
            'response': response,
            'response_type': response.get('type', 'unknown')
        })
        print()

    # Summary
    print("\n" + "="*70)
    print("R2_rate Invalid Parameter Test Summary:")
    print("="*70)
    for result in results:
        print(f"R2_rate={result['invalid_value']:4d} -> Response type: '{result['response_type']}'")

    return results


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.invalid_params
@pytest.mark.quick
def test_invalid_r3_rate(ads1293_client):
    """
    Test Case 41.3: Invalid R3_rate values

    Valid R3_rate values: 4, 6, 8, 12, 16, 32, 64, 128
    Test invalid values: 0, 1, 2, 3, 5, 7, 9, 10, 11, 13-15, 17-31, 33-63, 65-127, 129+
    """
    print("\n" + "="*70)
    print("Test Case 41.3: Invalid R3_rate Parameter Tests")
    print("="*70)

    valid_r3_values = [4, 6, 8, 12, 16, 32, 64, 128]
    invalid_r3_values = [0, 1, 2, 3, 5, 7, 9, 10, 11, 13, 14, 15, 17, 20, 24, 31, 33, 48, 63, 65, 100, 127, 129, 256, -1]

    print(f"\nValid R3_rate values (per spec): {valid_r3_values}")
    print(f"Testing invalid R3_rate values: {invalid_r3_values}\n")

    results = []

    for r3_val in invalid_r3_values:
        print(f"[Test] Sending R3_rate = {r3_val}")

        request = {
            "type": "settings",
            "enable_conversion": True,
            "R1_rate": 4,
            "R2_rate": 8,
            "R3_rate": r3_val
        }

        response = ads1293_client.send_json(request)

        print(f"  Request:  {request}")
        print(f"  Response: {response}")

        results.append({
            'parameter': 'R3_rate',
            'invalid_value': r3_val,
            'request': request,
            'response': response,
            'response_type': response.get('type', 'unknown')
        })
        print()

    # Summary
    print("\n" + "="*70)
    print("R3_rate Invalid Parameter Test Summary:")
    print("="*70)
    for result in results:
        print(f"R3_rate={result['invalid_value']:4d} -> Response type: '{result['response_type']}'")

    return results


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.invalid_params
@pytest.mark.quick
def test_multiple_invalid_rates(ads1293_client):
    """
    Test Case 41.4: Multiple invalid rate parameters simultaneously

    Test combinations of invalid R1, R2, R3 values
    """
    print("\n" + "="*70)
    print("Test Case 41.4: Multiple Invalid Rate Parameters")
    print("="*70)

    test_cases = [
        {"R1_rate": 3, "R2_rate": 7, "R3_rate": 10, "description": "All invalid"},
        {"R1_rate": 100, "R2_rate": 200, "R3_rate": 300, "description": "All very large invalid"},
        {"R1_rate": -1, "R2_rate": -2, "R3_rate": -3, "description": "All negative"},
        {"R1_rate": 0, "R2_rate": 0, "R3_rate": 0, "description": "All zero"},
    ]

    results = []

    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {idx}] {test_case['description']}")

        request = {
            "type": "settings",
            "enable_conversion": True,
            "R1_rate": test_case["R1_rate"],
            "R2_rate": test_case["R2_rate"],
            "R3_rate": test_case["R3_rate"]
        }

        response = ads1293_client.send_json(request)

        print(f"  Request:  {request}")
        print(f"  Response: {response}")

        results.append({
            'description': test_case['description'],
            'request': request,
            'response': response,
            'response_type': response.get('type', 'unknown')
        })

    # Summary
    print("\n" + "="*70)
    print("Multiple Invalid Parameters Test Summary:")
    print("="*70)
    for result in results:
        print(f"{result['description']:30s} -> Response type: '{result['response_type']}'")

    return results


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.invalid_params
@pytest.mark.quick
def test_missing_rate_parameters(ads1293_client):
    """
    Test Case 41.5: Missing rate parameters (use defaults)

    Test behavior when R1_rate, R2_rate, or R3_rate are omitted
    According to spec, defaults are: R1=4, R2=8, R3=128
    """
    print("\n" + "="*70)
    print("Test Case 41.5: Missing Rate Parameters (Default Behavior)")
    print("="*70)

    test_cases = [
        {
            "description": "All rates omitted (all defaults)",
            "request": {
                "type": "settings",
                "enable_conversion": True
            }
        },
        {
            "description": "Only R1 omitted (R1=4 default)",
            "request": {
                "type": "settings",
                "enable_conversion": True,
                "R2_rate": 8,
                "R3_rate": 128
            }
        },
        {
            "description": "Only R2 omitted (R2=8 default)",
            "request": {
                "type": "settings",
                "enable_conversion": True,
                "R1_rate": 4,
                "R3_rate": 128
            }
        },
        {
            "description": "Only R3 omitted (R3=128 default)",
            "request": {
                "type": "settings",
                "enable_conversion": True,
                "R1_rate": 4,
                "R2_rate": 8
            }
        }
    ]

    results = []

    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {idx}] {test_case['description']}")

        response = ads1293_client.send_json(test_case['request'])

        print(f"  Request:  {test_case['request']}")
        print(f"  Response: {response}")

        # Check if defaults were applied
        if response.get('type') == 'actual_settings':
            r1_used = response.get('R1_rate', 'not_returned')
            r2_used = response.get('R2_rate', 'not_returned')
            r3_used = response.get('R3_rate', 'not_returned')
            print(f"  Applied:  R1={r1_used}, R2={r2_used}, R3={r3_used}")

        results.append({
            'description': test_case['description'],
            'request': test_case['request'],
            'response': response,
            'response_type': response.get('type', 'unknown')
        })

    # Summary
    print("\n" + "="*70)
    print("Missing Parameters Test Summary:")
    print("="*70)
    for result in results:
        print(f"{result['description']:40s} -> Response type: '{result['response_type']}'")

    return results


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
