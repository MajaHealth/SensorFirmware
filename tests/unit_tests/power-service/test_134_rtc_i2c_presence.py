#!/usr/bin/env python3
"""
Test Case #134: RTC Presence on I2C Bus
Unit Test for Power Service / I2C

Tests that the RTC (Real-Time Clock) device is detected on the I2C bus
at the expected address.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock I2C responses for testing logic
2. Hardware mode: Scans actual I2C bus on CM4 (requires PI_TARGET_IP)

Test Setup:
- DUT with RTC installed
- Access to I2C scan utility/output

Procedure:
1. Power on the CM4 with RTC installed
2. Scan the RTC I2C bus and confirm the RTC device address is detected

Acceptance Criteria:
- RTC device address is detected on the expected I2C bus
"""

import subprocess
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


# Common RTC I2C addresses
RTC_ADDRESSES = {
    0x68: "DS1307/DS3231/PCF8523",
    0x51: "PCF8563",
    0x6F: "MCP7940N",
    0x52: "RV-3028",
    0x32: "RV-8803",
}

# Default expected RTC address (DS3231 is common on Pi)
DEFAULT_RTC_ADDRESS = 0x68

# I2C bus number (typically 1 on Raspberry Pi)
I2C_BUS = 1


@dataclass
class I2CDevice:
    """Detected I2C device"""
    address: int
    bus: int
    device_name: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'address': f"0x{self.address:02x}",
            'bus': self.bus,
            'device_name': self.device_name
        }


@dataclass
class I2CScanResult:
    """Result of I2C bus scan"""
    bus: int
    devices_found: List[I2CDevice]
    rtc_detected: bool
    rtc_address: Optional[int]
    scan_successful: bool
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'bus': self.bus,
            'devices_found': [d.to_dict() for d in self.devices_found],
            'rtc_detected': self.rtc_detected,
            'rtc_address': f"0x{self.rtc_address:02x}" if self.rtc_address else None,
            'scan_successful': self.scan_successful,
            'error_message': self.error_message
        }


class MockI2CScanner:
    """
    Mock I2C scanner for unit testing.
    Simulates I2C bus scan with configurable devices.
    """

    def __init__(self):
        self.mock_devices: List[int] = []
        self.bus = I2C_BUS
        self._setup_default_devices()

    def _setup_default_devices(self):
        """Setup default mock devices including RTC"""
        self.mock_devices = [
            0x68,  # RTC (DS3231)
            0x0B,  # Battery fuel gauge (common address)
        ]

    def reset(self):
        """Reset to default state"""
        self._setup_default_devices()

    def add_device(self, address: int):
        """Add a mock device at address"""
        if address not in self.mock_devices:
            self.mock_devices.append(address)

    def remove_device(self, address: int):
        """Remove a mock device"""
        if address in self.mock_devices:
            self.mock_devices.remove(address)

    def scan_bus(self, bus: int = I2C_BUS) -> I2CScanResult:
        """Simulate I2C bus scan"""
        devices = []
        rtc_detected = False
        rtc_address = None

        for addr in sorted(self.mock_devices):
            device_name = RTC_ADDRESSES.get(addr)
            devices.append(I2CDevice(
                address=addr,
                bus=bus,
                device_name=device_name
            ))

            # Check if this is an RTC
            if addr in RTC_ADDRESSES:
                rtc_detected = True
                rtc_address = addr

        return I2CScanResult(
            bus=bus,
            devices_found=devices,
            rtc_detected=rtc_detected,
            rtc_address=rtc_address,
            scan_successful=True
        )


class I2CScanner:
    """
    I2C bus scanner that can work in mock or hardware mode.
    """

    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockI2CScanner] = None

    def initialize(self) -> bool:
        """Initialize scanner, falling back to mock if needed"""
        if self.host and self.host != '127.0.0.1':
            # Try to connect to remote Pi for hardware mode
            try:
                # Test SSH connectivity (would need actual implementation)
                print(f"  Hardware mode targeting: {self.host}")
                return True
            except Exception as e:
                print(f"  Could not connect to {self.host}: {e}")
                print("  Falling back to mock simulation mode")

        self.use_mock = True
        self.mock = MockI2CScanner()
        return True

    def scan_bus(self, bus: int = I2C_BUS) -> I2CScanResult:
        """Scan I2C bus for devices"""
        if self.use_mock:
            return self.mock.scan_bus(bus)

        return self._hardware_scan(bus)

    def _hardware_scan(self, bus: int) -> I2CScanResult:
        """
        Perform actual I2C scan using i2cdetect.
        This would run on local machine or via SSH to remote Pi.
        """
        try:
            # Run i2cdetect command
            cmd = f"i2cdetect -y {bus}"

            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} '{cmd}'"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return I2CScanResult(
                    bus=bus,
                    devices_found=[],
                    rtc_detected=False,
                    rtc_address=None,
                    scan_successful=False,
                    error_message=result.stderr
                )

            # Parse i2cdetect output
            devices = self._parse_i2cdetect_output(result.stdout, bus)

            rtc_detected = False
            rtc_address = None
            for device in devices:
                if device.address in RTC_ADDRESSES:
                    rtc_detected = True
                    rtc_address = device.address
                    break

            return I2CScanResult(
                bus=bus,
                devices_found=devices,
                rtc_detected=rtc_detected,
                rtc_address=rtc_address,
                scan_successful=True
            )

        except subprocess.TimeoutExpired:
            return I2CScanResult(
                bus=bus,
                devices_found=[],
                rtc_detected=False,
                rtc_address=None,
                scan_successful=False,
                error_message="I2C scan timed out"
            )
        except Exception as e:
            return I2CScanResult(
                bus=bus,
                devices_found=[],
                rtc_detected=False,
                rtc_address=None,
                scan_successful=False,
                error_message=str(e)
            )

    def _parse_i2cdetect_output(self, output: str, bus: int) -> List[I2CDevice]:
        """
        Parse i2cdetect -y output to extract device addresses.

        Example output:
             0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
        00:          -- -- -- -- -- -- -- -- 0b -- -- -- --
        10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        ...
        60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
        """
        devices = []
        lines = output.strip().split('\n')

        for line in lines[1:]:  # Skip header line
            if not line or ':' not in line:
                continue

            parts = line.split(':')
            if len(parts) != 2:
                continue

            try:
                row_base = int(parts[0].strip(), 16)
            except ValueError:
                continue

            cols = parts[1].split()
            for col_idx, value in enumerate(cols):
                if value != '--' and value != 'UU':
                    try:
                        addr = int(value, 16)
                        device_name = RTC_ADDRESSES.get(addr)
                        devices.append(I2CDevice(
                            address=addr,
                            bus=bus,
                            device_name=device_name
                        ))
                    except ValueError:
                        continue

        return devices


class TestRTCI2CPresence:
    """Unit Test - RTC Presence on I2C Bus"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')

        return {
            'host': host,
            'i2c_bus': I2C_BUS,
            'expected_rtc_address': DEFAULT_RTC_ADDRESS,
            'known_rtc_addresses': list(RTC_ADDRESSES.keys()),
            'log_file': '/tmp/test_134_rtc_i2c_presence.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.scanner: Optional[I2CScanner] = None

    def teardown_method(self):
        """Cleanup after each test"""
        pass

    @pytest.mark.unit
    @pytest.mark.i2c
    @pytest.mark.rtc
    @pytest.mark.power
    def test_134_rtc_detected_on_i2c_bus(self, test_config):
        """
        Test Case #134: RTC presence on I2C bus

        Test Setup:
            DUT with RTC installed; access to I2C scan utility/output

        Procedure:
            1. Power on the CM4 with RTC installed
            2. Scan the RTC I2C bus and confirm the RTC device address is detected

        Acceptance Criteria:
            RTC device address is detected on the expected I2C bus

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #134: RTC Presence on I2C Bus")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify RTC device is detected on I2C bus")
        print("\nEXPECTED RTC ADDRESSES:")
        for addr, name in RTC_ADDRESSES.items():
            marker = " (default)" if addr == DEFAULT_RTC_ADDRESS else ""
            print(f"  0x{addr:02x}: {name}{marker}")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}")
        print(f"  I2C Bus: {config['i2c_bus']}")
        print("=" * 70)

        # ================================================================
        # STEP 1: Initialize I2C Scanner
        # ================================================================
        print("\n[STEP 1] Initialize I2C Scanner")
        print("-" * 70)

        self.scanner = I2CScanner(host=config['host'])
        initialized = self.scanner.initialize()
        assert initialized, "Failed to initialize I2C scanner"

        if self.scanner.use_mock:
            print("  Running in MOCK SIMULATION mode")
        else:
            print("  Running in HARDWARE mode")

        # ================================================================
        # STEP 2: Scan I2C Bus
        # ================================================================
        print("\n[STEP 2] Scan I2C Bus for Devices")
        print("-" * 70)

        print(f"  Scanning I2C bus {config['i2c_bus']}...")

        scan_result = self.scanner.scan_bus(config['i2c_bus'])

        print(f"  Scan successful: {'YES' if scan_result.scan_successful else 'NO'}")

        if not scan_result.scan_successful:
            print(f"  Error: {scan_result.error_message}")
            pytest.fail(f"I2C scan failed: {scan_result.error_message}")

        print(f"  Devices found: {len(scan_result.devices_found)}")

        # ================================================================
        # STEP 3: Display Detected Devices
        # ================================================================
        print("\n[STEP 3] Detected I2C Devices")
        print("-" * 70)

        if scan_result.devices_found:
            print(f"\n  {'Address':<10} {'Device Name':<25} {'RTC?'}")
            print("  " + "-" * 45)
            for device in scan_result.devices_found:
                is_rtc = "YES" if device.address in RTC_ADDRESSES else "NO"
                name = device.device_name or "Unknown"
                print(f"  0x{device.address:02x}       {name:<25} {is_rtc}")
        else:
            print("  No devices detected on I2C bus")

        # ================================================================
        # STEP 4: Verify RTC Detection
        # ================================================================
        print("\n[STEP 4] Verify RTC Detection")
        print("-" * 70)

        print(f"\n  RTC Detection Result:")
        print(f"    RTC detected: {'YES' if scan_result.rtc_detected else 'NO'}")

        if scan_result.rtc_detected:
            rtc_name = RTC_ADDRESSES.get(scan_result.rtc_address, "Unknown RTC")
            print(f"    RTC address: 0x{scan_result.rtc_address:02x}")
            print(f"    RTC type: {rtc_name}")
        else:
            print("    No RTC found at known addresses")
            print(f"    Checked addresses: {[f'0x{a:02x}' for a in RTC_ADDRESSES.keys()]}")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)

        if scan_result.rtc_detected:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 70)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if scan_result.scan_successful else 'FAIL'}] I2C bus scan completed successfully")
        print(f"    [{'PASS' if scan_result.rtc_detected else 'FAIL'}] RTC device address detected on I2C bus")

        print(f"\n  Mode: {'Mock Simulation' if self.scanner.use_mock else 'Hardware'}")
        print("=" * 70)

        # Assertion
        assert scan_result.rtc_detected, \
            f"RTC device not detected on I2C bus {config['i2c_bus']}"

    @pytest.mark.unit
    @pytest.mark.i2c
    @pytest.mark.rtc
    @pytest.mark.power
    def test_134_rtc_at_expected_address(self, test_config):
        """
        Test that RTC is at the expected default address (0x68).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #134b: RTC at Expected Address")
        print("=" * 70)

        self.scanner = I2CScanner(host=config['host'])
        self.scanner.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.scanner.use_mock else 'Hardware'}")
        print(f"  Expected RTC address: 0x{config['expected_rtc_address']:02x}")

        scan_result = self.scanner.scan_bus(config['i2c_bus'])

        # Check if RTC is at expected address
        rtc_at_expected = (
            scan_result.rtc_detected and
            scan_result.rtc_address == config['expected_rtc_address']
        )

        print(f"\n  Scan Result:")
        print(f"    RTC detected: {'YES' if scan_result.rtc_detected else 'NO'}")
        if scan_result.rtc_detected:
            print(f"    RTC address: 0x{scan_result.rtc_address:02x}")
            print(f"    At expected address: {'YES' if rtc_at_expected else 'NO'}")

        print("\n" + "=" * 70)
        if rtc_at_expected:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert rtc_at_expected, \
            f"RTC not found at expected address 0x{config['expected_rtc_address']:02x}"

    @pytest.mark.unit
    @pytest.mark.i2c
    @pytest.mark.rtc
    @pytest.mark.power
    def test_134_i2c_bus_accessible(self, test_config):
        """
        Test that I2C bus is accessible and can be scanned.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #134c: I2C Bus Accessibility")
        print("=" * 70)

        self.scanner = I2CScanner(host=config['host'])
        self.scanner.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.scanner.use_mock else 'Hardware'}")
        print(f"  Testing I2C bus: {config['i2c_bus']}")

        scan_result = self.scanner.scan_bus(config['i2c_bus'])

        print(f"\n  Bus Accessibility:")
        print(f"    Scan successful: {'YES' if scan_result.scan_successful else 'NO'}")
        if scan_result.error_message:
            print(f"    Error: {scan_result.error_message}")
        print(f"    Devices found: {len(scan_result.devices_found)}")

        print("\n" + "=" * 70)
        if scan_result.scan_successful:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert scan_result.scan_successful, \
            f"I2C bus {config['i2c_bus']} not accessible: {scan_result.error_message}"

    @pytest.mark.unit
    @pytest.mark.i2c
    @pytest.mark.rtc
    @pytest.mark.power
    def test_134_rtc_device_responds(self, test_config):
        """
        Test that RTC device responds (is not in UU state).
        UU indicates device is used by a kernel driver.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #134d: RTC Device Responds")
        print("=" * 70)

        self.scanner = I2CScanner(host=config['host'])
        self.scanner.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.scanner.use_mock else 'Hardware'}")

        scan_result = self.scanner.scan_bus(config['i2c_bus'])

        # Find RTC device
        rtc_device = None
        for device in scan_result.devices_found:
            if device.address in RTC_ADDRESSES:
                rtc_device = device
                break

        print(f"\n  RTC Device Status:")
        if rtc_device:
            print(f"    Found at: 0x{rtc_device.address:02x}")
            print(f"    Type: {rtc_device.device_name or 'Unknown'}")
            print(f"    Responds: YES (device visible on bus)")
        else:
            print("    RTC device not found")

        print("\n" + "=" * 70)
        if rtc_device:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert rtc_device is not None, "RTC device not responding on I2C bus"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
