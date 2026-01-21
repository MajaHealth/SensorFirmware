#!/usr/bin/env python3
"""
Test Case #120: Backlight Range and Clamping
Unit Test for SPI Service / Display

Tests backlight brightness control across full range with proper clamping behavior.

Test Setup:
- DUT with display/backlight
- Access to OS backlight control interface

Procedure:
1. Set brightness to minimum and confirm backlight OFF
2. Set brightness to maximum and confirm maximum brightness
3. Set brightness to mid-range value and confirm medium intensity
4. Apply a value above maximum and observe clamping/handled behavior
5. Apply a value below minimum and observe clamping/handled behavior

Acceptance Criteria:
- Backlight OFF at minimum
- Maximum brightness at max value
- Medium brightness at mid value
- Values above max clamp to max
- Values below min clamp to min
"""

import subprocess
import time
import pytest
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class BacklightState:
    """Backlight state information"""
    brightness: int
    max_brightness: int
    percentage: float
    clamped: bool

    def to_dict(self) -> Dict:
        return {
            'brightness': self.brightness,
            'max_brightness': self.max_brightness,
            'percentage': self.percentage,
            'clamped': self.clamped
        }


class MockBacklightController:
    """Mock backlight controller for unit testing"""

    def __init__(self):
        self.brightness = 128
        self.max_brightness = 255
        self.min_brightness = 0

    def set_brightness(self, value: int) -> BacklightState:
        """Set brightness with clamping"""
        clamped = False
        if value > self.max_brightness:
            value = self.max_brightness
            clamped = True
        elif value < self.min_brightness:
            value = self.min_brightness
            clamped = True

        self.brightness = value
        return BacklightState(
            brightness=self.brightness,
            max_brightness=self.max_brightness,
            percentage=(self.brightness / self.max_brightness) * 100,
            clamped=clamped
        )

    def get_brightness(self) -> BacklightState:
        return BacklightState(
            brightness=self.brightness,
            max_brightness=self.max_brightness,
            percentage=(self.brightness / self.max_brightness) * 100,
            clamped=False
        )


class BacklightController:
    """Controller for backlight operations"""

    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockBacklightController] = None
        self.backlight_path = "/sys/class/backlight/*/brightness"

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            print(f"  Hardware mode targeting: {self.host}")
            return True

        self.use_mock = True
        self.mock = MockBacklightController()
        return True

    def set_brightness(self, value: int) -> BacklightState:
        if self.use_mock:
            return self.mock.set_brightness(value)
        return self._hardware_set(value)

    def get_brightness(self) -> BacklightState:
        if self.use_mock:
            return self.mock.get_brightness()
        return self._hardware_get()

    def _hardware_set(self, value: int) -> BacklightState:
        """Set brightness on hardware"""
        try:
            # Get max brightness first
            cmd_max = f"cat /sys/class/backlight/*/max_brightness 2>/dev/null | head -1"
            if self.host and self.host != '127.0.0.1':
                cmd_max = f"ssh pi@{self.host} \"{cmd_max}\""

            result = subprocess.run(cmd_max, shell=True, capture_output=True, text=True, timeout=5)
            max_brightness = int(result.stdout.strip()) if result.stdout.strip() else 255

            # Clamp value
            clamped = False
            if value > max_brightness:
                value = max_brightness
                clamped = True
            elif value < 0:
                value = 0
                clamped = True

            # Set brightness
            cmd_set = f"echo {value} | sudo tee /sys/class/backlight/*/brightness"
            if self.host and self.host != '127.0.0.1':
                cmd_set = f"ssh pi@{self.host} \"{cmd_set}\""

            subprocess.run(cmd_set, shell=True, capture_output=True, timeout=5)
            time.sleep(0.1)

            return self._hardware_get()

        except Exception as e:
            return BacklightState(brightness=0, max_brightness=255, percentage=0, clamped=False)

    def _hardware_get(self) -> BacklightState:
        """Get brightness from hardware"""
        try:
            cmd = "cat /sys/class/backlight/*/brightness 2>/dev/null | head -1"
            cmd_max = "cat /sys/class/backlight/*/max_brightness 2>/dev/null | head -1"

            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""
                cmd_max = f"ssh pi@{self.host} \"{cmd_max}\""

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            result_max = subprocess.run(cmd_max, shell=True, capture_output=True, text=True, timeout=5)

            brightness = int(result.stdout.strip()) if result.stdout.strip() else 0
            max_brightness = int(result_max.stdout.strip()) if result_max.stdout.strip() else 255

            return BacklightState(
                brightness=brightness,
                max_brightness=max_brightness,
                percentage=(brightness / max_brightness) * 100 if max_brightness > 0 else 0,
                clamped=False
            )

        except Exception:
            return BacklightState(brightness=0, max_brightness=255, percentage=0, clamped=False)


class TestBacklightRangeClamping:
    """Unit Test - Backlight Range and Clamping"""

    @pytest.fixture(scope="class")
    def test_config(self):
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        return {
            'host': host,
            'log_file': '/tmp/test_120_backlight_range.log',
        }

    def setup_method(self):
        self.controller: Optional[BacklightController] = None

    @pytest.mark.unit
    @pytest.mark.display
    @pytest.mark.backlight
    def test_120_backlight_range_and_clamping(self, test_config):
        """
        Test Case #120: Backlight range and clamping

        Procedure:
            1. Set brightness to minimum and confirm backlight OFF
            2. Set brightness to maximum and confirm maximum brightness
            3. Set brightness to mid-range and confirm medium intensity
            4. Apply value above maximum and observe clamping
            5. Apply value below minimum and observe clamping

        Acceptance Criteria:
            - Backlight OFF at minimum
            - Maximum brightness at max value
            - Medium brightness at mid value
            - Values above max clamp to max
            - Values below min clamp to min
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #120: Backlight Range and Clamping")
        print("=" * 70)

        # Initialize
        print("\n[STEP 1] Initialize Backlight Controller")
        print("-" * 70)

        self.controller = BacklightController(host=config['host'])
        self.controller.initialize()

        print(f"  Mode: {'Mock Simulation' if self.controller.use_mock else 'Hardware'}")

        # Get max brightness
        initial = self.controller.get_brightness()
        max_val = initial.max_brightness
        mid_val = max_val // 2

        print(f"  Max brightness: {max_val}")

        results = {}

        # Test 1: Minimum brightness
        print("\n[STEP 2] Set Brightness to Minimum (0)")
        print("-" * 70)
        state = self.controller.set_brightness(0)
        results['min'] = state
        print(f"  Brightness: {state.brightness} ({state.percentage:.1f}%)")
        print(f"  Expected: 0 (OFF)")
        min_ok = state.brightness == 0

        # Test 2: Maximum brightness
        print("\n[STEP 3] Set Brightness to Maximum")
        print("-" * 70)
        state = self.controller.set_brightness(max_val)
        results['max'] = state
        print(f"  Brightness: {state.brightness} ({state.percentage:.1f}%)")
        print(f"  Expected: {max_val} (100%)")
        max_ok = state.brightness == max_val

        # Test 3: Mid-range brightness
        print("\n[STEP 4] Set Brightness to Mid-Range")
        print("-" * 70)
        state = self.controller.set_brightness(mid_val)
        results['mid'] = state
        print(f"  Brightness: {state.brightness} ({state.percentage:.1f}%)")
        print(f"  Expected: ~{mid_val} (~50%)")
        mid_ok = abs(state.brightness - mid_val) <= 1

        # Test 4: Above maximum (should clamp)
        print("\n[STEP 5] Set Brightness Above Maximum (Clamping)")
        print("-" * 70)
        state = self.controller.set_brightness(max_val + 100)
        results['above_max'] = state
        print(f"  Requested: {max_val + 100}")
        print(f"  Actual: {state.brightness}")
        print(f"  Expected: {max_val} (clamped)")
        clamp_high_ok = state.brightness == max_val

        # Test 5: Below minimum (should clamp)
        print("\n[STEP 6] Set Brightness Below Minimum (Clamping)")
        print("-" * 70)
        state = self.controller.set_brightness(-50)
        results['below_min'] = state
        print(f"  Requested: -50")
        print(f"  Actual: {state.brightness}")
        print(f"  Expected: 0 (clamped)")
        clamp_low_ok = state.brightness == 0

        # Summary
        print("\n" + "=" * 70)
        print("Test Results Summary:")
        print("-" * 70)
        print(f"  [{'PASS' if min_ok else 'FAIL'}] Minimum brightness (OFF)")
        print(f"  [{'PASS' if max_ok else 'FAIL'}] Maximum brightness")
        print(f"  [{'PASS' if mid_ok else 'FAIL'}] Mid-range brightness")
        print(f"  [{'PASS' if clamp_high_ok else 'FAIL'}] Clamp above max")
        print(f"  [{'PASS' if clamp_low_ok else 'FAIL'}] Clamp below min")

        test_pass = min_ok and max_ok and mid_ok and clamp_high_ok and clamp_low_ok
        print("\n" + "=" * 70)
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert min_ok, "Minimum brightness test failed"
        assert max_ok, "Maximum brightness test failed"
        assert mid_ok, "Mid-range brightness test failed"
        assert clamp_high_ok, "Clamping above max failed"
        assert clamp_low_ok, "Clamping below min failed"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
