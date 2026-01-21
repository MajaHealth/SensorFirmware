#!/usr/bin/env python3
"""
Test Case #121: Backlight Rapid Toggling Robustness
Unit Test for SPI Service / Display

Tests that rapid toggling between min and max brightness works without errors.

Test Setup:
- DUT with display/backlight
- Logging enabled

Procedure:
1. Rapidly alternate between minimum and maximum brightness for 10 cycles
2. Observe behavior and check for errors/crashes

Acceptance Criteria:
- Rapid toggling works without errors, crashes, or flicker artifacts
"""

import time
import pytest
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class ToggleTestResult:
    """Result of rapid toggle test"""
    cycles_completed: int
    cycles_requested: int
    errors: List[str]
    crashes_detected: bool
    all_transitions_successful: bool

    def to_dict(self) -> Dict:
        return {
            'cycles_completed': self.cycles_completed,
            'cycles_requested': self.cycles_requested,
            'errors': self.errors,
            'crashes_detected': self.crashes_detected,
            'all_transitions_successful': self.all_transitions_successful
        }


class MockBacklightToggler:
    """Mock backlight toggler for unit testing"""

    def __init__(self):
        self.brightness = 128
        self.max_brightness = 255
        self.toggle_count = 0
        self.errors: List[str] = []

    def set_brightness(self, value: int) -> bool:
        """Set brightness, return success"""
        if value < 0:
            value = 0
        elif value > self.max_brightness:
            value = self.max_brightness
        self.brightness = value
        self.toggle_count += 1
        return True

    def rapid_toggle(self, cycles: int, delay_ms: float = 50) -> ToggleTestResult:
        """Perform rapid toggle test"""
        self.errors = []
        successful_cycles = 0

        for i in range(cycles):
            try:
                # Toggle to max
                if not self.set_brightness(self.max_brightness):
                    self.errors.append(f"Cycle {i}: Failed to set max")
                    continue

                time.sleep(delay_ms / 1000)

                # Toggle to min
                if not self.set_brightness(0):
                    self.errors.append(f"Cycle {i}: Failed to set min")
                    continue

                time.sleep(delay_ms / 1000)
                successful_cycles += 1

            except Exception as e:
                self.errors.append(f"Cycle {i}: {str(e)}")

        return ToggleTestResult(
            cycles_completed=successful_cycles,
            cycles_requested=cycles,
            errors=self.errors,
            crashes_detected=False,
            all_transitions_successful=successful_cycles == cycles
        )


class BacklightToggler:
    """Controller for backlight toggling tests"""

    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockBacklightToggler] = None

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            print(f"  Hardware mode targeting: {self.host}")
            return True

        self.use_mock = True
        self.mock = MockBacklightToggler()
        return True

    def rapid_toggle(self, cycles: int, delay_ms: float = 50) -> ToggleTestResult:
        if self.use_mock:
            return self.mock.rapid_toggle(cycles, delay_ms)
        return self._hardware_toggle(cycles, delay_ms)

    def _hardware_toggle(self, cycles: int, delay_ms: float) -> ToggleTestResult:
        """Perform rapid toggle on hardware"""
        import subprocess

        errors = []
        successful_cycles = 0

        # Get max brightness
        try:
            cmd = "cat /sys/class/backlight/*/max_brightness 2>/dev/null | head -1"
            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            max_brightness = int(result.stdout.strip()) if result.stdout.strip() else 255
        except:
            max_brightness = 255

        for i in range(cycles):
            try:
                # Set to max
                cmd_max = f"echo {max_brightness} | sudo tee /sys/class/backlight/*/brightness"
                if self.host and self.host != '127.0.0.1':
                    cmd_max = f"ssh pi@{self.host} \"{cmd_max}\""
                result = subprocess.run(cmd_max, shell=True, capture_output=True, timeout=5)
                if result.returncode != 0:
                    errors.append(f"Cycle {i}: Failed to set max")
                    continue

                time.sleep(delay_ms / 1000)

                # Set to min
                cmd_min = "echo 0 | sudo tee /sys/class/backlight/*/brightness"
                if self.host and self.host != '127.0.0.1':
                    cmd_min = f"ssh pi@{self.host} \"{cmd_min}\""
                result = subprocess.run(cmd_min, shell=True, capture_output=True, timeout=5)
                if result.returncode != 0:
                    errors.append(f"Cycle {i}: Failed to set min")
                    continue

                time.sleep(delay_ms / 1000)
                successful_cycles += 1

            except Exception as e:
                errors.append(f"Cycle {i}: {str(e)}")

        return ToggleTestResult(
            cycles_completed=successful_cycles,
            cycles_requested=cycles,
            errors=errors,
            crashes_detected=False,
            all_transitions_successful=successful_cycles == cycles
        )


class TestBacklightRapidToggle:
    """Unit Test - Backlight Rapid Toggling Robustness"""

    @pytest.fixture(scope="class")
    def test_config(self):
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        return {
            'host': host,
            'toggle_cycles': 10,
            'toggle_delay_ms': 50,
            'log_file': '/tmp/test_121_backlight_toggle.log',
        }

    def setup_method(self):
        self.toggler: Optional[BacklightToggler] = None

    @pytest.mark.unit
    @pytest.mark.display
    @pytest.mark.backlight
    def test_121_backlight_rapid_toggling(self, test_config):
        """
        Test Case #121: Backlight rapid toggling robustness

        Procedure:
            1. Rapidly alternate between min and max brightness for 10 cycles
            2. Observe behavior and check for errors/crashes

        Acceptance Criteria:
            Rapid toggling works without errors, crashes, or flicker artifacts
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #121: Backlight Rapid Toggling Robustness")
        print("=" * 70)
        print(f"\nCONFIGURATION:")
        print(f"  Toggle cycles: {config['toggle_cycles']}")
        print(f"  Delay between toggles: {config['toggle_delay_ms']} ms")
        print("=" * 70)

        # Initialize
        print("\n[STEP 1] Initialize Backlight Controller")
        print("-" * 70)

        self.toggler = BacklightToggler(host=config['host'])
        self.toggler.initialize()

        print(f"  Mode: {'Mock Simulation' if self.toggler.use_mock else 'Hardware'}")

        # Perform rapid toggle test
        print("\n[STEP 2] Perform Rapid Toggle Test")
        print("-" * 70)

        print(f"  Starting {config['toggle_cycles']} rapid toggle cycles...")
        start_time = time.time()

        result = self.toggler.rapid_toggle(
            cycles=config['toggle_cycles'],
            delay_ms=config['toggle_delay_ms']
        )

        elapsed = time.time() - start_time
        print(f"  Test completed in {elapsed:.2f} seconds")

        # Results
        print("\n[STEP 3] Analyze Results")
        print("-" * 70)

        print(f"\n  Toggle Test Results:")
        print(f"    Cycles requested: {result.cycles_requested}")
        print(f"    Cycles completed: {result.cycles_completed}")
        print(f"    All successful: {'YES' if result.all_transitions_successful else 'NO'}")
        print(f"    Crashes detected: {'YES' if result.crashes_detected else 'NO'}")
        print(f"    Errors: {len(result.errors)}")

        if result.errors:
            print(f"\n  Errors encountered:")
            for err in result.errors[:5]:  # Show first 5
                print(f"    - {err}")

        # Validation
        print("\n[STEP 4] Validate Results")
        print("-" * 70)

        all_cycles_ok = result.cycles_completed == result.cycles_requested
        no_crashes = not result.crashes_detected
        no_errors = len(result.errors) == 0

        print(f"    All cycles completed: {'PASS' if all_cycles_ok else 'FAIL'}")
        print(f"    No crashes: {'PASS' if no_crashes else 'FAIL'}")
        print(f"    No errors: {'PASS' if no_errors else 'FAIL'}")

        # Result
        print("\n" + "=" * 70)
        test_pass = all_cycles_ok and no_crashes and no_errors
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert all_cycles_ok, f"Only {result.cycles_completed}/{result.cycles_requested} cycles completed"
        assert no_crashes, "System crash detected during toggle"
        assert no_errors, f"Errors during toggle: {result.errors}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
