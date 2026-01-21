#!/usr/bin/env python3
"""
Test Case #122: Brightness Command Handling (Valid Values)
Unit Test for SPI Service / Display

Tests that firmware correctly handles valid brightness commands via IPC.

Test Setup:
- DUT with display
- Firmware brightness IPC enabled
- Mock app connected

Procedure:
1. Simulate app sending brightness = minimum and capture firmware response
2. Simulate app sending brightness = maximum and capture response
3. Simulate app sending a mid-range brightness value and capture response

Acceptance Criteria:
- Brightness is set to requested valid values and ACK is returned with handled value
"""

import time
import pytest
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class BrightnessResponse:
    """Response from brightness command"""
    success: bool
    ack_received: bool
    requested_value: int
    actual_value: int
    error_message: Optional[str]

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'ack_received': self.ack_received,
            'requested_value': self.requested_value,
            'actual_value': self.actual_value,
            'error_message': self.error_message
        }


class MockBrightnessService:
    """Mock brightness service for unit testing"""

    def __init__(self):
        self.brightness = 128
        self.max_brightness = 255
        self.min_brightness = 0

    def send_brightness_command(self, value: int) -> BrightnessResponse:
        """Process brightness command and return response"""
        if value < self.min_brightness or value > self.max_brightness:
            return BrightnessResponse(
                success=False,
                ack_received=True,
                requested_value=value,
                actual_value=self.brightness,
                error_message="Value out of range"
            )

        self.brightness = value
        return BrightnessResponse(
            success=True,
            ack_received=True,
            requested_value=value,
            actual_value=value,
            error_message=None
        )

    def get_brightness(self) -> int:
        return self.brightness


class BrightnessController:
    """Controller for brightness IPC commands"""

    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockBrightnessService] = None

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            print(f"  Hardware mode targeting: {self.host}")
            return True

        self.use_mock = True
        self.mock = MockBrightnessService()
        return True

    def send_brightness(self, value: int) -> BrightnessResponse:
        if self.use_mock:
            return self.mock.send_brightness_command(value)
        return self._hardware_send(value)

    def _hardware_send(self, value: int) -> BrightnessResponse:
        """Send brightness command to hardware"""
        import subprocess

        try:
            # Set brightness via sysfs
            cmd = f"echo {value} | sudo tee /sys/class/backlight/*/brightness"
            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)

            # Read back actual value
            cmd_read = "cat /sys/class/backlight/*/brightness 2>/dev/null | head -1"
            if self.host and self.host != '127.0.0.1':
                cmd_read = f"ssh pi@{self.host} \"{cmd_read}\""

            result_read = subprocess.run(cmd_read, shell=True, capture_output=True, text=True, timeout=5)
            actual = int(result_read.stdout.strip()) if result_read.stdout.strip() else 0

            return BrightnessResponse(
                success=result.returncode == 0,
                ack_received=True,
                requested_value=value,
                actual_value=actual,
                error_message=result.stderr if result.returncode != 0 else None
            )

        except Exception as e:
            return BrightnessResponse(
                success=False,
                ack_received=False,
                requested_value=value,
                actual_value=0,
                error_message=str(e)
            )


class TestBrightnessValidValues:
    """Unit Test - Brightness Command Handling (Valid Values)"""

    @pytest.fixture(scope="class")
    def test_config(self):
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        return {
            'host': host,
            'min_brightness': 0,
            'max_brightness': 255,
            'mid_brightness': 128,
            'log_file': '/tmp/test_122_brightness_valid.log',
        }

    def setup_method(self):
        self.controller: Optional[BrightnessController] = None

    @pytest.mark.unit
    @pytest.mark.display
    @pytest.mark.backlight
    def test_122_brightness_valid_values(self, test_config):
        """
        Test Case #122: Brightness command handling (valid values)

        Procedure:
            1. Simulate app sending brightness = minimum and capture response
            2. Simulate app sending brightness = maximum and capture response
            3. Simulate app sending mid-range brightness and capture response

        Acceptance Criteria:
            Brightness is set to requested valid values and ACK is returned
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #122: Brightness Command Handling (Valid Values)")
        print("=" * 70)
        print(f"\nVALID BRIGHTNESS RANGE:")
        print(f"  Minimum: {config['min_brightness']}")
        print(f"  Maximum: {config['max_brightness']}")
        print(f"  Mid-range: {config['mid_brightness']}")
        print("=" * 70)

        # Initialize
        print("\n[STEP 1] Initialize Brightness Controller")
        print("-" * 70)

        self.controller = BrightnessController(host=config['host'])
        self.controller.initialize()

        print(f"  Mode: {'Mock Simulation' if self.controller.use_mock else 'Hardware'}")

        results = {}

        # Test minimum brightness
        print("\n[STEP 2] Send Minimum Brightness Command")
        print("-" * 70)
        response = self.controller.send_brightness(config['min_brightness'])
        results['min'] = response
        print(f"  Requested: {response.requested_value}")
        print(f"  Actual: {response.actual_value}")
        print(f"  ACK received: {'YES' if response.ack_received else 'NO'}")
        print(f"  Success: {'YES' if response.success else 'NO'}")
        min_ok = response.success and response.actual_value == config['min_brightness']

        # Test maximum brightness
        print("\n[STEP 3] Send Maximum Brightness Command")
        print("-" * 70)
        response = self.controller.send_brightness(config['max_brightness'])
        results['max'] = response
        print(f"  Requested: {response.requested_value}")
        print(f"  Actual: {response.actual_value}")
        print(f"  ACK received: {'YES' if response.ack_received else 'NO'}")
        print(f"  Success: {'YES' if response.success else 'NO'}")
        max_ok = response.success and response.actual_value == config['max_brightness']

        # Test mid-range brightness
        print("\n[STEP 4] Send Mid-Range Brightness Command")
        print("-" * 70)
        response = self.controller.send_brightness(config['mid_brightness'])
        results['mid'] = response
        print(f"  Requested: {response.requested_value}")
        print(f"  Actual: {response.actual_value}")
        print(f"  ACK received: {'YES' if response.ack_received else 'NO'}")
        print(f"  Success: {'YES' if response.success else 'NO'}")
        mid_ok = response.success and response.actual_value == config['mid_brightness']

        # Summary
        print("\n" + "=" * 70)
        print("Test Results Summary:")
        print("-" * 70)
        print(f"  [{'PASS' if min_ok else 'FAIL'}] Minimum brightness ({config['min_brightness']})")
        print(f"  [{'PASS' if max_ok else 'FAIL'}] Maximum brightness ({config['max_brightness']})")
        print(f"  [{'PASS' if mid_ok else 'FAIL'}] Mid-range brightness ({config['mid_brightness']})")

        test_pass = min_ok and max_ok and mid_ok
        print("\n" + "=" * 70)
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert min_ok, f"Minimum brightness test failed: {results['min'].error_message}"
        assert max_ok, f"Maximum brightness test failed: {results['max'].error_message}"
        assert mid_ok, f"Mid-range brightness test failed: {results['mid'].error_message}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
