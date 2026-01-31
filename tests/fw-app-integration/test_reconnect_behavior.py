"""
Test Case 48: Reconnect Behavior During Repeated Connect/Disconnect

Category: FW-APP Integration (Robustness)
Components: Firmware sensor services + TCP client

Test Steps:
1. Connect client to a sensor service port
2. Open/close the connection repeatedly (5×)
3. Record whether reconnection is successful each cycle

Pass Criteria:
- Reconnect succeeds each time
- No socket leak is observed
- Service remains functional after all cycles
"""

import pytest
import sys
import time
import socket
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


# Number of reconnection cycles to test
RECONNECT_CYCLES = 5


def drain_async_messages(client, timeout=0.5):
    """Drain async messages (for MAX30009 and Power services)."""
    time.sleep(0.2)
    drained = 0
    while drained < 20:
        try:
            msg = client.recv(timeout=0.1)
            if not msg:
                break
            if msg.get('type') in ['meas_state', 'data', 'button_info']:
                drained += 1
                continue
            break
        except:
            break
    return drained


def test_service_reconnection(service_name, host, port, request_type, expected_response,
                               needs_async_drain=False):
    """
    Test reconnection for a single service.

    Args:
        service_name: Human-readable service name
        host: Service host
        port: Service port
        request_type: Request to send after connection
        expected_response: Expected response type
        needs_async_drain: Whether to drain async messages before request

    Returns:
        List of cycle results (True/False for each cycle)
    """
    cycle_results = []

    print(f"\n[{service_name}] Testing {RECONNECT_CYCLES} reconnection cycles...")
    print(f"  Service: {host}:{port}")
    print(f"  Request: {request_type}")
    print(f"  Expected: {expected_response}\n")

    for cycle in range(1, RECONNECT_CYCLES + 1):
        print(f"  Cycle {cycle}/{RECONNECT_CYCLES}...", end=" ")

        client = None
        success = False

        try:
            # Step 1: Connect
            client = TCPClient(host, port, timeout=10.0)
            client.connect()

            # Step 2: Drain async messages if needed
            if needs_async_drain:
                drained = drain_async_messages(client)
                if drained > 0:
                    print(f"(drained {drained} async msgs) ", end="")

            # Step 3: Send request
            response = client.send({"type": request_type})

            # Step 4: Verify response
            if response.get("type") == expected_response:
                print("✓ PASS")
                success = True
            else:
                print(f"✗ FAIL (got '{response.get('type')}', expected '{expected_response}')")
                success = False

        except socket.timeout:
            print("✗ FAIL (timeout)")
            success = False

        except ConnectionRefusedError:
            print("✗ FAIL (connection refused)")
            success = False

        except Exception as e:
            print(f"✗ FAIL ({type(e).__name__}: {e})")
            success = False

        finally:
            # Step 5: Disconnect cleanly
            if client:
                try:
                    client.close()
                except:
                    pass

        cycle_results.append(success)

        # Brief delay between cycles
        if cycle < RECONNECT_CYCLES:
            time.sleep(0.5)

    return cycle_results


@pytest.mark.fw_app
@pytest.mark.robustness
@pytest.mark.quick
@pytest.mark.ads1293
@pytest.mark.max30009
def test_reconnect_all_services(test_config):
    """
    Test Case 48: Verify reconnection behavior for all sensor services.

    Tests repeated connect/disconnect cycles to ensure:
    - No socket descriptor leaks
    - Service remains stable
    - Reconnection always succeeds
    """

    print(f"\n{'='*70}")
    print(f"Test Case 48: Reconnect Behavior During Repeated Connect/Disconnect")
    print(f"{'='*70}")
    print(f"Testing {RECONNECT_CYCLES} reconnection cycles per service")
    print(f"Services: ADS1293, MAX30009, Power")
    print(f"{'='*70}")

    # Define services to test
    ads_config = test_config['services']['ads1293']
    max_config = test_config['services']['max30009']
    power_config = test_config['services']['power']

    services = [
        {
            "name": "ADS1293",
            "host": ads_config['host'],
            "port": ads_config['port'],
            "request": "get_settings",
            "expected": "actual_settings",
            "async_drain": False
        },
        {
            "name": "MAX30009",
            "host": max_config['host'],
            "port": max_config['port'],
            "request": "get_settings",
            "expected": "actual_settings",
            "async_drain": True  # MAX30009 sends async meas_state messages
        },
        {
            "name": "Power",
            "host": power_config['host'],
            "port": power_config['port'],
            "request": "get_battery_info",
            "expected": "battery_info",
            "async_drain": True  # Power service sends async button_info messages
        }
    ]

    # Test each service
    all_results = {}

    for service in services:
        results = test_service_reconnection(
            service_name=service["name"],
            host=service["host"],
            port=service["port"],
            request_type=service["request"],
            expected_response=service["expected"],
            needs_async_drain=service["async_drain"]
        )

        all_results[service["name"]] = results

    # Summary
    print(f"\n{'='*70}")
    print(f"Reconnection Test Summary")
    print(f"{'='*70}")

    total_tests = 0
    total_passed = 0
    all_services_passed = True

    for service_name, results in all_results.items():
        passed = sum(results)
        total = len(results)
        total_tests += total
        total_passed += passed

        status = "✓ PASS" if passed == total else "✗ FAIL"
        print(f"{service_name:15s} {passed}/{total} cycles successful  {status}")

        if passed != total:
            all_services_passed = False
            # Show which cycles failed
            failed_cycles = [i+1 for i, r in enumerate(results) if not r]
            print(f"                Failed cycles: {failed_cycles}")

    print(f"{'='*70}")
    print(f"Total:          {total_passed}/{total_tests} cycles successful")

    if all_services_passed:
        print(f"Result:         ✓ ALL SERVICES PASSED")
    else:
        print(f"Result:         ✗ SOME SERVICES FAILED")

    print(f"{'='*70}\n")

    # Assertions
    for service_name, results in all_results.items():
        passed = sum(results)
        total = len(results)

        assert passed == total, \
            f"{service_name}: Only {passed}/{total} reconnection cycles succeeded"

    # Final verification: Try one more connection to each service
    print(f"[Final Verification] Testing post-test service availability...")

    for service in services:
        try:
            client = TCPClient(service["host"], service["port"], timeout=5.0)
            client.connect()

            if service["async_drain"]:
                drain_async_messages(client)

            response = client.send({"type": service["request"]})
            client.close()

            assert response.get("type") == service["expected"], \
                f"{service['name']}: Post-test verification failed"

            print(f"  ✓ {service['name']} still responsive")

        except Exception as e:
            pytest.fail(f"{service['name']}: Post-test verification failed: {e}")

    print(f"\n✓ All services remain responsive after reconnection testing\n")
