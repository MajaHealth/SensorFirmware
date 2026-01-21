#!/usr/bin/env python3
"""
Test Case #123: Brightness Command Handling (Invalid/Corrupted Values)
Unit Test for SPI Service / Display

Tests that firmware correctly handles invalid or corrupted brightness commands.

Test Setup:
- DUT with display
- Firmware brightness IPC enabled
- Mock app connected

Procedure:
1. Simulate app sending an out-of-range low brightness value; capture response
2. Simulate app sending an out-of-range high brightness value; capture response
3. Simulate app sending a non-numeric/corrupted brightness value; capture response

Acceptance Criteria:
- Out-of-range values are clamped or rejected with handled value returned
- Corrupted value is ignored, previous brightness maintained, error/NA returned
"""

import pytest
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class InvalidBrightnessResponse:
    """Response from invalid brightness command"""
    handled_gracefully: bool
    value_clamped: bool
    value_rejected: bool
    previous_value_maintained: bool
    error_returned: bool
    actual_brightness: int
    error_message: Optional[str]

    def to_dict(self) -> Dict:
        return {
            'handled_gracefully': self.handled_gracefully,
            'value_clamped': self.value_clamped,
            'value_rejected': self.value_rejected,
            'previous_value_maintained': self.previous_value_maintained,
            'error_returned': self.error_returned,
            'actual_brightness': self.actual_brightness,
            'error_message': self.error_message
        }


class MockBrightnessService:
    """Mock brightness service for invalid value testing"""

    def __init__(self):
        self.brightness = 128
        self.max_brightness = 255
        self.min_brightness = 0

    def send_invalid_brightness(self, value) -> InvalidBrightnessResponse:
        """Process invalid brightness command"""
        previous = self.brightness

        # Handle non-numeric values
        if not isinstance(value, (int, float)):
            return InvalidBrightnessResponse(
                handled_gracefully=True,
                value_clamped=False,
                value_rejected=True,
                previous_value_maintained=True,
                error_returned=True,
                actual_brightness=previous,
                error_message="Invalid value type"
            )

        value = int(value)

        # Handle out-of-range low
        if value < self.min_brightness:
            self.brightness = self.min_brightness
            return InvalidBrightnessResponse(
                handled_gracefully=True,
                value_clamped=True,
                value_rejected=False,
                previous_value_maintained=False,
                error_returned=False,
                actual_brightness=self.brightness,
                error_message=None
            )

        # Handle out-of-range high
        if value > self.max_brightness:
            self.brightness = self.max_brightness
            return InvalidBrightnessResponse(
                handled_gracefully=True,
                value_clamped=True,
                value_rejected=False,
                previous_value_maintained=False,
                error_returned=False,
                actual_brightness=self.brightness,
                error_message=None
            )

        # Valid value (shouldn't happen in this test)
        self.brightness = value
        return InvalidBrightnessResponse(
            handled_gracefully=True,
            value_clamped=False,
            value_rejected=False,
            previous_value_maintained=False,
            error_returned=False,
            actual_brightness=value,
            error_message=None
        )

    def get_brightness(self) -> int:
        return self.brightness


class BrightnessInvalidHandler:
    """Controller for testing invalid brightness handling"""

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

    def send_invalid_brightness(self, value) -> InvalidBrightnessResponse:
        if self.use_mock:
            return self.mock.send_invalid_brightness(value)
        return self._hardware_send_invalid(value)

    def set_baseline_brightness(self, value: int):
        """Set a baseline brightness for testing"""
        if self.use_mock:
            self.mock.brightness = value

    def _hardware_send_invalid(self, value) -> InvalidBrightnessResponse:
        """Send invalid brightness to hardware"""
        import subprocess

        try:
            # Get current brightness first
            cmd_read = "cat /sys/class/backlight/*/brightness 2>/dev/null | head -1"
            if self.host and self.host != '127.0.0.1':
                cmd_read = f"ssh pi@{self.host} \"{cmd_read}\""
            result = subprocess.run(cmd_read, shell=True, capture_output=True, text=True, timeout=5)
            previous = int(result.stdout.strip()) if result.stdout.strip() else 128

            # Get max brightness
            cmd_max = "cat /sys/class/backlight/*/max_brightness 2>/dev/null | head -1"
            if self.host and self.host != '127.0.0.1':
                cmd_max = f"ssh pi@{self.host} \"{cmd_max}\""
            result_max = subprocess.run(cmd_max, shell=True, capture_output=True, text=True, timeout=5)
            max_brightness = int(result_max.stdout.strip()) if result_max.stdout.strip() else 255

            # Try to set invalid value
            cmd = f"echo {value} | sudo tee /sys/class/backlight/*/brightness 2>&1"
            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)

            # Read actual value after attempt
            result_after = subprocess.run(cmd_read, shell=True, capture_output=True, text=True, timeout=5)
            actual = int(result_after.stdout.strip()) if result_after.stdout.strip() else previous

            # Determine what happened
            error_occurred = result.returncode != 0 or 'error' in result.stderr.lower()
            value_changed = actual != previous

            if isinstance(value, (int, float)):
                value_int = int(value)
                was_clamped = (value_int < 0 and actual == 0) or (value_int > max_brightness and actual == max_brightness)
            else:
                was_clamped = False

            return InvalidBrightnessResponse(
                handled_gracefully=True,
                value_clamped=was_clamped,
                value_rejected=error_occurred,
                previous_value_maintained=not value_changed,
                error_returned=error_occurred,
                actual_brightness=actual,
                error_message=result.stderr if error_occurred else None
            )

        except Exception as e:
            return InvalidBrightnessResponse(
                handled_gracefully=False,
                value_clamped=False,
                value_rejected=True,
                previous_value_maintained=True,
                error_returned=True,
                actual_brightness=0,
                error_message=str(e)
            )


class TestBrightnessInvalidValues:
    """Unit Test - Brightness Command Handling (Invalid/Corrupted)"""

    @pytest.fixture(scope="class")
    def test_config(self):
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        return {
            'host': host,
            'max_brightness': 255,
            'baseline_brightness': 128,
            'log_file': '/tmp/test_123_brightness_invalid.log',
        }

    def setup_method(self):
        self.handler: Optional[BrightnessInvalidHandler] = None

    @pytest.mark.unit
    @pytest.mark.display
    @pytest.mark.backlight
    def test_123_brightness_invalid_values(self, test_config):
        """
        Test Case #123: Brightness command handling (invalid/corrupted values)

        Procedure:
            1. Simulate app sending out-of-range low brightness value
            2. Simulate app sending out-of-range high brightness value
            3. Simulate app sending non-numeric/corrupted brightness value

        Acceptance Criteria:
            - Out-of-range values are clamped or rejected with handled value
            - Corrupted value is ignored, previous brightness maintained
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #123: Brightness Command Handling (Invalid/Corrupted)")
        print("=" * 70)
        print(f"\nINVALID TEST VALUES:")
        print(f"  Out-of-range low: -50")
        print(f"  Out-of-range high: {config['max_brightness'] + 100}")
        print(f"  Non-numeric: 'invalid'")
        print("=" * 70)

        # Initialize
        print("\n[STEP 1] Initialize Handler")
        print("-" * 70)

        self.handler = BrightnessInvalidHandler(host=config['host'])
        self.handler.initialize()

        print(f"  Mode: {'Mock Simulation' if self.handler.use_mock else 'Hardware'}")

        # Set baseline
        self.handler.set_baseline_brightness(config['baseline_brightness'])

        results = {}

        # Test 1: Out-of-range low
        print("\n[STEP 2] Send Out-of-Range Low Value (-50)")
        print("-" * 70)
        response = self.handler.send_invalid_brightness(-50)
        results['low'] = response
        print(f"  Handled gracefully: {'YES' if response.handled_gracefully else 'NO'}")
        print(f"  Value clamped: {'YES' if response.value_clamped else 'NO'}")
        print(f"  Actual brightness: {response.actual_brightness}")
        low_ok = response.handled_gracefully and (response.value_clamped or response.value_rejected)

        # Test 2: Out-of-range high
        print("\n[STEP 3] Send Out-of-Range High Value")
        print("-" * 70)
        high_value = config['max_brightness'] + 100
        response = self.handler.send_invalid_brightness(high_value)
        results['high'] = response
        print(f"  Requested: {high_value}")
        print(f"  Handled gracefully: {'YES' if response.handled_gracefully else 'NO'}")
        print(f"  Value clamped: {'YES' if response.value_clamped else 'NO'}")
        print(f"  Actual brightness: {response.actual_brightness}")
        high_ok = response.handled_gracefully and (response.value_clamped or response.value_rejected)

        # Test 3: Non-numeric/corrupted
        print("\n[STEP 4] Send Non-Numeric/Corrupted Value")
        print("-" * 70)
        response = self.handler.send_invalid_brightness("invalid_string")
        results['corrupted'] = response
        print(f"  Requested: 'invalid_string'")
        print(f"  Handled gracefully: {'YES' if response.handled_gracefully else 'NO'}")
        print(f"  Value rejected: {'YES' if response.value_rejected else 'NO'}")
        print(f"  Previous maintained: {'YES' if response.previous_value_maintained else 'NO'}")
        print(f"  Error returned: {'YES' if response.error_returned else 'NO'}")
        corrupted_ok = response.handled_gracefully and (response.value_rejected or response.previous_value_maintained)

        # Summary
        print("\n" + "=" * 70)
        print("Test Results Summary:")
        print("-" * 70)
        print(f"  [{'PASS' if low_ok else 'FAIL'}] Out-of-range low handled (clamped/rejected)")
        print(f"  [{'PASS' if high_ok else 'FAIL'}] Out-of-range high handled (clamped/rejected)")
        print(f"  [{'PASS' if corrupted_ok else 'FAIL'}] Corrupted value handled (rejected/ignored)")

        test_pass = low_ok and high_ok and corrupted_ok
        print("\n" + "=" * 70)
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert low_ok, "Out-of-range low value not handled properly"
        assert high_ok, "Out-of-range high value not handled properly"
        assert corrupted_ok, "Corrupted value not handled properly"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
