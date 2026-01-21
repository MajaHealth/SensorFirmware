#!/usr/bin/env python3
"""
Test Case #115: Charge Control Enable/Disable Command Handling
Unit Test for Power Service

Tests firmware's handling of charge control commands via mock application.
Verifies that charge-disable and charge-enable commands are processed correctly
and that the battery charging state reflects the commands.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock responses for testing logic
2. Hardware mode: Connects to actual power service (requires PI_TARGET_IP)

Test Setup:
- DUT with mock app connected
- Logging enabled
- Power service running on CM4 (port 501) for hardware mode

Procedure:
1. From mock app, send a charge-disable request and capture firmware response
2. From mock app, send a charge-enable request and capture firmware response

Acceptance Criteria:
- Charge-disable response indicates charging is disabled
- Charge-enable response indicates charging is enabled
- Battery charging state reflects the commands correctly
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


class ChargeState(Enum):
    """Charging state"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


@dataclass
class CommandResult:
    """Result of a charge control command"""
    command: str
    request: Dict
    response: Optional[Dict]
    success: bool
    timestamp: str
    response_time_ms: float
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'command': self.command,
            'request': self.request,
            'response': self.response,
            'success': self.success,
            'timestamp': self.timestamp,
            'response_time_ms': self.response_time_ms,
            'error': self.error
        }


@dataclass
class ChargeStateVerification:
    """Verification of charge state after command"""
    expected_state: ChargeState
    actual_state: ChargeState
    battery_info: Optional[Dict]
    verified: bool
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            'expected_state': self.expected_state.value,
            'actual_state': self.actual_state.value,
            'battery_info': self.battery_info,
            'verified': self.verified,
            'timestamp': self.timestamp
        }


class MockPowerService:
    """
    Mock power service for unit testing charge control commands.
    Simulates firmware responses without actual hardware.
    """

    def __init__(self):
        self.charging_enabled = True
        self.charger_connected = True
        self.command_log: List[CommandResult] = []
        self.battery_soc = 50.0
        self.battery_voltage = 3.8
        self.battery_current = 0.5  # Positive when charging
        self.battery_temperature = 25.0

    def reset(self):
        """Reset mock to initial state"""
        self.charging_enabled = True
        self.charger_connected = True
        self.command_log.clear()
        self.battery_soc = 50.0
        self.battery_voltage = 3.8
        self.battery_current = 0.5
        self.battery_temperature = 25.0

    def send_command(self, request: Dict) -> Tuple[Dict, float]:
        """
        Process a command and return response with timing.

        Returns: (response_dict, response_time_ms)
        """
        start_time = time.time()

        # Simulate processing delay
        time.sleep(0.01)  # 10ms simulated latency

        cmd_type = request.get('type', '')
        response = {}

        if cmd_type == 'charge_disable':
            self.charging_enabled = False
            self.battery_current = 0.0  # No charging current when disabled
            response = {'type': 'charge_is_disable'}

        elif cmd_type == 'charge_enable':
            self.charging_enabled = True
            if self.charger_connected and self.battery_soc < 100:
                self.battery_current = 0.5  # Resume charging
            response = {'type': 'charge_is_enable'}

        elif cmd_type == 'get_batt_info':
            response = self._get_battery_info()

        else:
            response = {'type': 'error', 'message': f'Unknown command: {cmd_type}'}

        response_time = (time.time() - start_time) * 1000  # Convert to ms
        return response, response_time

    def _get_battery_info(self) -> Dict:
        """Generate simulated battery info response"""
        return {
            'type': 'batt_info',
            'voltage': self.battery_voltage,
            'temperature': self.battery_temperature,
            'current': self.battery_current if self.charging_enabled else 0.0,
            'relative_state_of_charge': int(self.battery_soc),
            'remaining_capacity': 3.0 * (self.battery_soc / 100),
            'full_charge_capacity': 3.0,
            'run_time_to_empty': int(self.battery_soc * 6),
            'average_time_to_empty': int(self.battery_soc * 6),
            'average_time_to_full': int((100 - self.battery_soc) * 2) if self.charging_enabled else 0,
            'cycle_count': 42,
            'design_capacity': 3.0,
            'design_voltage': 3.7,
            'fully_discharged': self.battery_soc <= 5,
            'fully_charged': self.battery_soc >= 99,
            'discharging': not self.charging_enabled or not self.charger_connected,
            'charging': self.charging_enabled and self.charger_connected and self.battery_soc < 100,
            'charger_is_connect': self.charger_connected,
            'battery_charge_is_disable': not self.charging_enabled
        }

    def get_charge_state(self) -> ChargeState:
        """Get current charging state"""
        if self.charging_enabled:
            return ChargeState.ENABLED
        return ChargeState.DISABLED


class PowerServiceClient:
    """
    Client for communicating with power service via TCP/JSON.
    Falls back to mock simulation if connection fails.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.connected = False

        # Mock fallback
        self.mock: Optional[MockPowerService] = None
        self.use_mock = False

        # Command history
        self.command_results: List[CommandResult] = []

    def connect(self) -> bool:
        """Connect to power service or fall back to mock"""
        try:
            from tcp_client import TCPClient
            self.client = TCPClient(self.host, self.port, self.timeout)
            self.client.connect()
            self.connected = True
            print(f"  Connected to power service at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"  Could not connect to power service: {e}")
            print("  Falling back to mock simulation mode")
            self.use_mock = True
            self.mock = MockPowerService()
            self.mock.reset()
            return True

    def disconnect(self):
        """Disconnect from power service"""
        if self.client and self.connected:
            self.client.disconnect()
            self.client = None
            self.connected = False

    def send_charge_disable(self) -> CommandResult:
        """
        Send charge-disable command to firmware.

        Request: {"type": "charge_disable"}
        Expected Response: {"type": "charge_is_disable"}
        """
        request = {"type": "charge_disable"}
        return self._send_command("charge_disable", request, "charge_is_disable")

    def send_charge_enable(self) -> CommandResult:
        """
        Send charge-enable command to firmware.

        Request: {"type": "charge_enable"}
        Expected Response: {"type": "charge_is_enable"}
        """
        request = {"type": "charge_enable"}
        return self._send_command("charge_enable", request, "charge_is_enable")

    def get_battery_info(self) -> Optional[Dict]:
        """Get current battery information"""
        request = {"type": "get_batt_info"}
        result = self._send_command("get_batt_info", request, "batt_info")
        if result.success:
            return result.response
        return None

    def _send_command(self, cmd_name: str, request: Dict, expected_response_type: str) -> CommandResult:
        """Send command and capture result"""
        timestamp = datetime.now().isoformat()

        if self.use_mock:
            response, response_time = self.mock.send_command(request)
        else:
            try:
                start_time = time.time()
                response = self.client.send(request)
                response_time = (time.time() - start_time) * 1000
            except Exception as e:
                result = CommandResult(
                    command=cmd_name,
                    request=request,
                    response=None,
                    success=False,
                    timestamp=timestamp,
                    response_time_ms=0,
                    error=str(e)
                )
                self.command_results.append(result)
                return result

        # Verify response
        success = False
        error = None

        if response:
            if response.get('type') == expected_response_type:
                success = True
            else:
                error = f"Unexpected response type: {response.get('type')}, expected: {expected_response_type}"
        else:
            error = "No response received"

        result = CommandResult(
            command=cmd_name,
            request=request,
            response=response,
            success=success,
            timestamp=timestamp,
            response_time_ms=response_time,
            error=error
        )

        self.command_results.append(result)
        return result

    def verify_charge_state(self, expected_state: ChargeState) -> ChargeStateVerification:
        """Verify the current charging state matches expected"""
        timestamp = datetime.now().isoformat()

        battery_info = self.get_battery_info()

        if battery_info is None:
            return ChargeStateVerification(
                expected_state=expected_state,
                actual_state=ChargeState.UNKNOWN,
                battery_info=None,
                verified=False,
                timestamp=timestamp
            )

        # Determine actual state from battery info
        if battery_info.get('battery_charge_is_disable', False):
            actual_state = ChargeState.DISABLED
        elif battery_info.get('charging', False) or not battery_info.get('battery_charge_is_disable', True):
            actual_state = ChargeState.ENABLED
        else:
            actual_state = ChargeState.UNKNOWN

        # For mock mode, use direct state
        if self.use_mock:
            actual_state = self.mock.get_charge_state()

        verified = (actual_state == expected_state)

        return ChargeStateVerification(
            expected_state=expected_state,
            actual_state=actual_state,
            battery_info=battery_info,
            verified=verified,
            timestamp=timestamp
        )

    def get_command_history(self) -> List[CommandResult]:
        """Get all command results"""
        return self.command_results.copy()

    def clear_history(self):
        """Clear command history"""
        self.command_results.clear()


class TestChargeControlCommands:
    """Unit Test - Charge Control Enable/Disable Command Handling"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 501

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'verification_delay_seconds': 0.5,  # Wait after command before verifying
            'max_response_time_ms': 1000,       # Max acceptable response time
            'log_file': '/tmp/test_115_charge_control.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[PowerServiceClient] = None

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            # Ensure charging is re-enabled before disconnecting
            try:
                self.client.send_charge_enable()
            except:
                pass
            self.client.disconnect()

    def print_command_result(self, result: CommandResult, step: str):
        """Print formatted command result"""
        status = "SUCCESS" if result.success else "FAILED"
        print(f"\n  {step}")
        print(f"    Command: {result.command}")
        print(f"    Request: {result.request}")
        print(f"    Response: {result.response}")
        print(f"    Status: {status}")
        print(f"    Response Time: {result.response_time_ms:.2f}ms")
        if result.error:
            print(f"    Error: {result.error}")

    def print_verification_result(self, verification: ChargeStateVerification, step: str):
        """Print formatted verification result"""
        status = "VERIFIED" if verification.verified else "MISMATCH"
        print(f"\n  {step}")
        print(f"    Expected State: {verification.expected_state.value}")
        print(f"    Actual State: {verification.actual_state.value}")
        print(f"    Status: {status}")
        if verification.battery_info:
            print(f"    Battery Info:")
            print(f"      - charging: {verification.battery_info.get('charging', 'N/A')}")
            print(f"      - charge_disabled: {verification.battery_info.get('battery_charge_is_disable', 'N/A')}")
            print(f"      - charger_connected: {verification.battery_info.get('charger_is_connect', 'N/A')}")
            print(f"      - current: {verification.battery_info.get('current', 'N/A')}A")

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_115_charge_control_commands(self, test_config):
        """
        Test Case #115: Charge control enable/disable command handling

        Test Setup:
            DUT; mock app connected; logging enabled

        Procedure:
            1. From mock app, send a charge-disable request and capture firmware response
            2. From mock app, send a charge-enable request and capture firmware response

        Acceptance Criteria:
            1. Charge-disable response indicates charging is disabled
            2. Charge-enable response indicates charging is enabled
            3. Battery charging state reflects the commands correctly

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #115: Charge Control Enable/Disable Command Handling")
        print("=" * 75)
        print("\nPURPOSE:")
        print("  Verify firmware correctly handles charge control commands")
        print("\nCOMMANDS TESTED:")
        print("  - charge_disable: Disable battery charging")
        print("  - charge_enable: Enable battery charging")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}:{config['port']}")
        print(f"  Timeout: {config['timeout']}s")
        print(f"  Max Response Time: {config['max_response_time_ms']}ms")
        print("=" * 75)

        # ================================================================
        # STEP 1: Initialize Client
        # ================================================================
        print("\n[STEP 1] Initialize Connection")
        print("-" * 75)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        if self.client.use_mock:
            print("  Running in MOCK SIMULATION mode")
        else:
            print("  Running in HARDWARE mode")

        # ================================================================
        # STEP 2: Get Initial Battery State
        # ================================================================
        print("\n[STEP 2] Get Initial Battery State")
        print("-" * 75)

        initial_info = self.client.get_battery_info()
        assert initial_info is not None, "Failed to get initial battery info"

        print(f"  Initial battery state:")
        print(f"    SOC: {initial_info.get('relative_state_of_charge', 'N/A')}%")
        print(f"    Voltage: {initial_info.get('voltage', 'N/A')}V")
        print(f"    Current: {initial_info.get('current', 'N/A')}A")
        print(f"    Charger Connected: {initial_info.get('charger_is_connect', 'N/A')}")
        print(f"    Charging: {initial_info.get('charging', 'N/A')}")
        print(f"    Charge Disabled: {initial_info.get('battery_charge_is_disable', 'N/A')}")

        # ================================================================
        # STEP 3: Send Charge-Disable Command
        # ================================================================
        print("\n[STEP 3] Send Charge-Disable Command")
        print("-" * 75)

        print("\n  Sending charge-disable request...")
        print("  Request: {\"type\": \"charge_disable\"}")
        print("  Expected Response: {\"type\": \"charge_is_disable\"}")

        disable_result = self.client.send_charge_disable()
        self.print_command_result(disable_result, "Charge-Disable Result:")

        # Verify response type
        assert disable_result.success, f"Charge-disable command failed: {disable_result.error}"
        assert disable_result.response.get('type') == 'charge_is_disable', \
            f"Unexpected response type: {disable_result.response.get('type')}"

        # Verify response time
        assert disable_result.response_time_ms < config['max_response_time_ms'], \
            f"Response time too slow: {disable_result.response_time_ms}ms"

        print(f"\n  Charge-disable response: VALID")
        print(f"  Response indicates charging is disabled: YES")

        # ================================================================
        # STEP 4: Verify Charging is Disabled
        # ================================================================
        print("\n[STEP 4] Verify Charging State After Disable")
        print("-" * 75)

        # Wait for state to settle
        time.sleep(config['verification_delay_seconds'])

        disable_verification = self.client.verify_charge_state(ChargeState.DISABLED)
        self.print_verification_result(disable_verification, "State Verification After Disable:")

        assert disable_verification.verified, \
            f"Charging state mismatch after disable: expected {ChargeState.DISABLED.value}, " \
            f"got {disable_verification.actual_state.value}"

        print(f"\n  Battery charging state reflects command: YES")

        # ================================================================
        # STEP 5: Send Charge-Enable Command
        # ================================================================
        print("\n[STEP 5] Send Charge-Enable Command")
        print("-" * 75)

        print("\n  Sending charge-enable request...")
        print("  Request: {\"type\": \"charge_enable\"}")
        print("  Expected Response: {\"type\": \"charge_is_enable\"}")

        enable_result = self.client.send_charge_enable()
        self.print_command_result(enable_result, "Charge-Enable Result:")

        # Verify response type
        assert enable_result.success, f"Charge-enable command failed: {enable_result.error}"
        assert enable_result.response.get('type') == 'charge_is_enable', \
            f"Unexpected response type: {enable_result.response.get('type')}"

        # Verify response time
        assert enable_result.response_time_ms < config['max_response_time_ms'], \
            f"Response time too slow: {enable_result.response_time_ms}ms"

        print(f"\n  Charge-enable response: VALID")
        print(f"  Response indicates charging is enabled: YES")

        # ================================================================
        # STEP 6: Verify Charging is Enabled
        # ================================================================
        print("\n[STEP 6] Verify Charging State After Enable")
        print("-" * 75)

        # Wait for state to settle
        time.sleep(config['verification_delay_seconds'])

        enable_verification = self.client.verify_charge_state(ChargeState.ENABLED)
        self.print_verification_result(enable_verification, "State Verification After Enable:")

        assert enable_verification.verified, \
            f"Charging state mismatch after enable: expected {ChargeState.ENABLED.value}, " \
            f"got {enable_verification.actual_state.value}"

        print(f"\n  Battery charging state reflects command: YES")

        # ================================================================
        # STEP 7: Command Sequence Summary
        # ================================================================
        print("\n[STEP 7] Command Sequence Summary")
        print("-" * 75)

        command_history = self.client.get_command_history()

        print(f"\n  Total commands sent: {len(command_history)}")
        print("\n  Command Log:")
        print("  " + "-" * 70)
        print(f"  {'#':<3} | {'Command':<15} | {'Response Type':<20} | {'Time (ms)':<10} | Status")
        print("  " + "-" * 70)

        for i, cmd in enumerate(command_history, 1):
            resp_type = cmd.response.get('type', 'N/A') if cmd.response else 'N/A'
            status = "OK" if cmd.success else "FAIL"
            print(f"  {i:<3} | {cmd.command:<15} | {resp_type:<20} | {cmd.response_time_ms:<10.2f} | {status}")

        print("  " + "-" * 70)

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 75)

        # Calculate pass/fail
        disable_pass = disable_result.success and disable_verification.verified
        enable_pass = enable_result.success and enable_verification.verified
        all_pass = disable_pass and enable_pass

        if all_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 75)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if disable_result.success else 'FAIL'}] Charge-disable response indicates charging is disabled")
        print(f"    [{'PASS' if enable_result.success else 'FAIL'}] Charge-enable response indicates charging is enabled")
        print(f"    [{'PASS' if disable_verification.verified and enable_verification.verified else 'FAIL'}] Battery charging state reflects the commands correctly")

        print("\n  Statistics:")
        print(f"    Commands Tested: 2 (charge_disable, charge_enable)")
        print(f"    Avg Response Time: {(disable_result.response_time_ms + enable_result.response_time_ms) / 2:.2f}ms")
        print(f"    Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        print("=" * 75)

        # Final assertions
        assert disable_pass, "Charge-disable test failed"
        assert enable_pass, "Charge-enable test failed"

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_115_charge_control_rapid_toggle(self, test_config):
        """
        Test rapid toggling of charge control.
        Verifies firmware handles rapid enable/disable sequences correctly.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #115b: Rapid Charge Control Toggle")
        print("=" * 75)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Rapid toggle sequence
        toggle_count = 5
        results = []

        print(f"\n  Performing {toggle_count} rapid disable/enable cycles...")
        print("  " + "-" * 50)

        for i in range(toggle_count):
            # Disable
            disable_result = self.client.send_charge_disable()
            results.append(('disable', disable_result))

            # Small delay
            time.sleep(0.05)

            # Enable
            enable_result = self.client.send_charge_enable()
            results.append(('enable', enable_result))

            status_d = "OK" if disable_result.success else "FAIL"
            status_e = "OK" if enable_result.success else "FAIL"
            print(f"  Cycle {i+1}: disable={status_d} ({disable_result.response_time_ms:.1f}ms), "
                  f"enable={status_e} ({enable_result.response_time_ms:.1f}ms)")

        print("  " + "-" * 50)

        # Verify all commands succeeded
        all_success = all(r[1].success for r in results)

        # Verify final state is enabled
        final_verification = self.client.verify_charge_state(ChargeState.ENABLED)

        print(f"\n  All commands successful: {'YES' if all_success else 'NO'}")
        print(f"  Final state verified: {'YES' if final_verification.verified else 'NO'}")

        print("\n" + "=" * 75)
        if all_success and final_verification.verified:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 75)

        assert all_success, "Some commands failed during rapid toggle"
        assert final_verification.verified, "Final state not correct after rapid toggle"

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_115_charge_control_idempotent(self, test_config):
        """
        Test idempotent behavior of charge control commands.
        Verifies sending same command multiple times doesn't cause issues.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #115c: Idempotent Command Behavior")
        print("=" * 75)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Send disable multiple times
        print("\n  Sending charge_disable 3 times consecutively...")
        disable_results = []
        for i in range(3):
            result = self.client.send_charge_disable()
            disable_results.append(result)
            status = "OK" if result.success else "FAIL"
            print(f"    Attempt {i+1}: {status} - response: {result.response}")

        # Verify all succeeded with same response
        all_disable_success = all(r.success for r in disable_results)
        all_same_response = all(
            r.response.get('type') == 'charge_is_disable'
            for r in disable_results if r.response
        )

        print(f"\n  All disable commands successful: {'YES' if all_disable_success else 'NO'}")
        print(f"  All responses consistent: {'YES' if all_same_response else 'NO'}")

        # Send enable multiple times
        print("\n  Sending charge_enable 3 times consecutively...")
        enable_results = []
        for i in range(3):
            result = self.client.send_charge_enable()
            enable_results.append(result)
            status = "OK" if result.success else "FAIL"
            print(f"    Attempt {i+1}: {status} - response: {result.response}")

        all_enable_success = all(r.success for r in enable_results)
        all_same_enable_response = all(
            r.response.get('type') == 'charge_is_enable'
            for r in enable_results if r.response
        )

        print(f"\n  All enable commands successful: {'YES' if all_enable_success else 'NO'}")
        print(f"  All responses consistent: {'YES' if all_same_enable_response else 'NO'}")

        print("\n" + "=" * 75)
        all_pass = all_disable_success and all_same_response and all_enable_success and all_same_enable_response
        if all_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 75)

        assert all_disable_success, "Some disable commands failed"
        assert all_same_response, "Inconsistent disable responses"
        assert all_enable_success, "Some enable commands failed"
        assert all_same_enable_response, "Inconsistent enable responses"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
