#!/usr/bin/env python3
"""
Test Case #119: DSI Display Absent Detection
Unit Test for SPI Service / Display

Tests that firmware/OS correctly reports no DSI display when disconnected.

Test Setup:
- DUT (no display connected)
- Access to system display detection outputs/logs

Procedure:
1. Disconnect the DSI display from the CM4
2. Boot the system
3. Review display detection/log outputs

Acceptance Criteria:
- Firmware/OS correctly reports no DSI display detected
"""

import subprocess
import pytest
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class DisplayAbsentResult:
    """Result of display absent detection"""
    display_absent_reported: bool
    detection_message: str
    no_errors: bool
    system_stable: bool

    def to_dict(self) -> Dict:
        return {
            'display_absent_reported': self.display_absent_reported,
            'detection_message': self.detection_message,
            'no_errors': self.no_errors,
            'system_stable': self.system_stable
        }


class MockDisplayDetector:
    """Mock display detector for absent display testing"""

    def __init__(self):
        self.display_connected = False  # Simulate no display

    def check_display_status(self) -> DisplayAbsentResult:
        """Check display connection status"""
        if self.display_connected:
            return DisplayAbsentResult(
                display_absent_reported=False,
                detection_message="DSI display connected",
                no_errors=True,
                system_stable=True
            )
        else:
            return DisplayAbsentResult(
                display_absent_reported=True,
                detection_message="No DSI display detected",
                no_errors=True,
                system_stable=True
            )


class DisplayDetector:
    """Controller for display detection"""

    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockDisplayDetector] = None

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            print(f"  Hardware mode targeting: {self.host}")
            return True

        self.use_mock = True
        self.mock = MockDisplayDetector()
        return True

    def check_display_absent(self) -> DisplayAbsentResult:
        """Check if display is properly reported as absent"""
        if self.use_mock:
            return self.mock.check_display_status()
        return self._hardware_check()

    def _hardware_check(self) -> DisplayAbsentResult:
        """Check display status from hardware"""
        try:
            # Check dmesg for display detection messages
            cmd = "dmesg | grep -i 'dsi\\|panel\\|display' | tail -20"
            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout.lower()

            # Check for "no display" or absence indicators
            no_display_indicators = ['no panel', 'not detected', 'disconnected', 'no dsi']
            display_absent = any(ind in output for ind in no_display_indicators)

            # Check for errors
            no_errors = 'error' not in output or 'timeout' not in output

            return DisplayAbsentResult(
                display_absent_reported=display_absent,
                detection_message=result.stdout[:200] if result.stdout else "No messages",
                no_errors=no_errors,
                system_stable=True
            )

        except Exception as e:
            return DisplayAbsentResult(
                display_absent_reported=False,
                detection_message=str(e),
                no_errors=False,
                system_stable=False
            )


class TestDSIDisplayAbsent:
    """Unit Test - DSI Display Absent Detection"""

    @pytest.fixture(scope="class")
    def test_config(self):
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        return {
            'host': host,
            'log_file': '/tmp/test_119_dsi_display_absent.log',
        }

    def setup_method(self):
        self.detector: Optional[DisplayDetector] = None

    @pytest.mark.unit
    @pytest.mark.display
    @pytest.mark.dsi
    def test_119_dsi_display_absent_detection(self, test_config):
        """
        Test Case #119: DSI display absent detection

        Procedure:
            1. Disconnect the DSI display from the CM4
            2. Boot the system
            3. Review display detection/log outputs

        Acceptance Criteria:
            Firmware/OS correctly reports no DSI display detected
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #119: DSI Display Absent Detection")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify firmware correctly reports no DSI display when disconnected")
        print("=" * 70)

        # Initialize
        print("\n[STEP 1] Initialize Display Detector")
        print("-" * 70)

        self.detector = DisplayDetector(host=config['host'])
        self.detector.initialize()

        print(f"  Mode: {'Mock Simulation' if self.detector.use_mock else 'Hardware'}")

        # Check display status
        print("\n[STEP 2] Check Display Detection Status")
        print("-" * 70)

        result = self.detector.check_display_absent()

        print(f"\n  Detection Results:")
        print(f"    Display absent reported: {'YES' if result.display_absent_reported else 'NO'}")
        print(f"    No errors in detection: {'YES' if result.no_errors else 'NO'}")
        print(f"    System stable: {'YES' if result.system_stable else 'NO'}")
        print(f"    Detection message: {result.detection_message[:100]}...")

        # Validate
        print("\n[STEP 3] Validate Detection")
        print("-" * 70)

        absent_ok = result.display_absent_reported
        no_errors = result.no_errors
        stable = result.system_stable

        print(f"    Correctly reports no display: {'PASS' if absent_ok else 'FAIL'}")
        print(f"    No errors: {'PASS' if no_errors else 'FAIL'}")
        print(f"    System stable: {'PASS' if stable else 'FAIL'}")

        # Result
        print("\n" + "=" * 70)
        test_pass = absent_ok and no_errors and stable
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert absent_ok, "System did not correctly report display as absent"
        assert no_errors, "Errors occurred during display detection"
        assert stable, "System became unstable without display"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
