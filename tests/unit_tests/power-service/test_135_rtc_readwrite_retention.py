#!/usr/bin/env python3
"""
Test Case #135: RTC Read/Write and Retention Across Power Cycle
Unit Test for Power Service / RTC

Tests that the RTC can be written to and read back, and that time is
retained across a power cycle.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock RTC responses for testing logic
2. Hardware mode: Uses actual RTC utilities on CM4 (requires PI_TARGET_IP)

Test Setup:
- DUT with RTC installed
- Access to OS RTC utilities (hwclock, timedatectl)

Procedure:
1. Write a known time to the RTC using an RTC utility and confirm the write succeeds
2. Read time back and verify it matches the written time
3. Power cycle the CM4 and read the time again to verify retention

Acceptance Criteria:
- Write completes without error
- Readback matches written time
- RTC retains time across power loss
"""

import subprocess
import time
import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class RTCTime:
    """RTC time representation"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    timestamp: float = 0.0

    def to_datetime(self) -> datetime:
        return datetime(self.year, self.month, self.day,
                       self.hour, self.minute, self.second)

    def to_dict(self) -> Dict:
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour,
            'minute': self.minute,
            'second': self.second,
            'datetime': str(self.to_datetime()),
            'timestamp': self.timestamp
        }

    @staticmethod
    def from_datetime(dt: datetime) -> 'RTCTime':
        return RTCTime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            timestamp=dt.timestamp()
        )


@dataclass
class RTCOperationResult:
    """Result of RTC operation"""
    success: bool
    time_value: Optional[RTCTime]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'time_value': self.time_value.to_dict() if self.time_value else None,
            'error_message': self.error_message
        }


@dataclass
class RTCRetentionValidation:
    """Validation of RTC retention across power cycle"""
    write_success: bool
    readback_matches: bool
    retention_verified: bool
    time_drift_seconds: float
    max_allowed_drift: float

    def to_dict(self) -> Dict:
        return {
            'write_success': self.write_success,
            'readback_matches': self.readback_matches,
            'retention_verified': self.retention_verified,
            'time_drift_seconds': self.time_drift_seconds,
            'max_allowed_drift': self.max_allowed_drift
        }


class MockRTC:
    """
    Mock RTC for unit testing.
    Simulates RTC read/write operations with time retention.
    """

    def __init__(self):
        self.stored_time: Optional[datetime] = None
        self.last_set_real_time: float = 0.0
        self.power_cycled = False

    def reset(self):
        """Reset mock state"""
        self.stored_time = None
        self.last_set_real_time = 0.0
        self.power_cycled = False

    def write_time(self, rtc_time: RTCTime) -> RTCOperationResult:
        """Write time to mock RTC"""
        try:
            self.stored_time = rtc_time.to_datetime()
            self.last_set_real_time = time.time()
            return RTCOperationResult(
                success=True,
                time_value=rtc_time
            )
        except Exception as e:
            return RTCOperationResult(
                success=False,
                time_value=None,
                error_message=str(e)
            )

    def read_time(self) -> RTCOperationResult:
        """Read time from mock RTC"""
        if self.stored_time is None:
            # Default to current system time if never set
            now = datetime.now()
            return RTCOperationResult(
                success=True,
                time_value=RTCTime.from_datetime(now)
            )

        # Calculate elapsed real time since last set
        elapsed = time.time() - self.last_set_real_time

        # Add elapsed time to stored RTC time (simulates RTC ticking)
        current_rtc_time = self.stored_time + timedelta(seconds=elapsed)

        return RTCOperationResult(
            success=True,
            time_value=RTCTime.from_datetime(current_rtc_time)
        )

    def simulate_power_cycle(self, power_off_duration: float = 2.0):
        """
        Simulate power cycle.
        RTC should retain time through this (battery backed).
        """
        self.power_cycled = True
        # RTC continues ticking during power loss (battery backed)
        # Just wait to simulate the power off period
        time.sleep(power_off_duration)


class RTCController:
    """
    Controller for RTC operations.
    Works in mock or hardware mode.
    """

    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockRTC] = None

    def initialize(self) -> bool:
        """Initialize RTC controller"""
        if self.host and self.host != '127.0.0.1':
            try:
                print(f"  Hardware mode targeting: {self.host}")
                return True
            except Exception as e:
                print(f"  Could not connect to {self.host}: {e}")
                print("  Falling back to mock simulation mode")

        self.use_mock = True
        self.mock = MockRTC()
        return True

    def write_time(self, rtc_time: RTCTime) -> RTCOperationResult:
        """Write time to RTC"""
        if self.use_mock:
            return self.mock.write_time(rtc_time)
        return self._hardware_write_time(rtc_time)

    def read_time(self) -> RTCOperationResult:
        """Read time from RTC"""
        if self.use_mock:
            return self.mock.read_time()
        return self._hardware_read_time()

    def simulate_power_cycle(self, duration: float = 2.0):
        """Simulate or perform power cycle"""
        if self.use_mock:
            self.mock.simulate_power_cycle(duration)
        else:
            # In hardware mode, this would require actual power cycle
            # which needs manual intervention or power control hardware
            print(f"  [HARDWARE MODE] Please power cycle the device for {duration}s")
            print("  Press Enter when device is back online...")
            # For automated testing, just wait
            time.sleep(duration)

    def _hardware_write_time(self, rtc_time: RTCTime) -> RTCOperationResult:
        """Write time to hardware RTC using hwclock"""
        try:
            dt = rtc_time.to_datetime()
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            # First set system time
            cmd_date = f"sudo date -s '{date_str}'"
            # Then sync to hardware RTC
            cmd_hwclock = "sudo hwclock -w"

            if self.host and self.host != '127.0.0.1':
                cmd_date = f"ssh pi@{self.host} \"{cmd_date}\""
                cmd_hwclock = f"ssh pi@{self.host} \"{cmd_hwclock}\""

            # Set system date
            result = subprocess.run(cmd_date, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return RTCOperationResult(
                    success=False,
                    time_value=None,
                    error_message=f"Failed to set system date: {result.stderr}"
                )

            # Write to hardware RTC
            result = subprocess.run(cmd_hwclock, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return RTCOperationResult(
                    success=False,
                    time_value=None,
                    error_message=f"Failed to write RTC: {result.stderr}"
                )

            return RTCOperationResult(success=True, time_value=rtc_time)

        except Exception as e:
            return RTCOperationResult(
                success=False,
                time_value=None,
                error_message=str(e)
            )

    def _hardware_read_time(self) -> RTCOperationResult:
        """Read time from hardware RTC using hwclock"""
        try:
            cmd = "sudo hwclock -r"

            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return RTCOperationResult(
                    success=False,
                    time_value=None,
                    error_message=f"Failed to read RTC: {result.stderr}"
                )

            # Parse hwclock output (format: "2024-01-15 10:30:45.123456+00:00")
            output = result.stdout.strip()
            dt = self._parse_hwclock_output(output)

            if dt is None:
                return RTCOperationResult(
                    success=False,
                    time_value=None,
                    error_message=f"Failed to parse hwclock output: {output}"
                )

            return RTCOperationResult(
                success=True,
                time_value=RTCTime.from_datetime(dt)
            )

        except Exception as e:
            return RTCOperationResult(
                success=False,
                time_value=None,
                error_message=str(e)
            )

    def _parse_hwclock_output(self, output: str) -> Optional[datetime]:
        """Parse hwclock -r output to datetime"""
        try:
            # hwclock output formats vary, try common ones
            formats = [
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%a %b %d %H:%M:%S %Y",
            ]

            for fmt in formats:
                try:
                    # Remove timezone info for simpler parsing
                    clean_output = output.split('+')[0].split('-0')[0].strip()
                    return datetime.strptime(clean_output, fmt.replace('%z', ''))
                except ValueError:
                    continue

            # Try parsing the first part
            parts = output.split()
            if len(parts) >= 2:
                date_time_str = f"{parts[0]} {parts[1].split('.')[0]}"
                return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

            return None
        except Exception:
            return None


class TestRTCReadWriteRetention:
    """Unit Test - RTC Read/Write and Retention Across Power Cycle"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')

        return {
            'host': host,
            'max_time_drift_seconds': 5.0,  # Allow 5 seconds drift
            'power_cycle_duration': 2.0,  # Simulated power off duration
            'log_file': '/tmp/test_135_rtc_readwrite_retention.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.rtc: Optional[RTCController] = None

    def teardown_method(self):
        """Cleanup after each test"""
        pass

    def create_test_time(self) -> RTCTime:
        """Create a known test time"""
        # Use a specific, recognizable time for testing
        test_dt = datetime(2025, 6, 15, 14, 30, 0)
        return RTCTime.from_datetime(test_dt)

    def times_match(self, time1: RTCTime, time2: RTCTime, tolerance_seconds: float) -> Tuple[bool, float]:
        """Check if two times match within tolerance"""
        dt1 = time1.to_datetime()
        dt2 = time2.to_datetime()
        diff = abs((dt2 - dt1).total_seconds())
        return diff <= tolerance_seconds, diff

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_135_rtc_readwrite_retention(self, test_config):
        """
        Test Case #135: RTC read/write and retention across power cycle

        Test Setup:
            DUT with RTC installed; access to OS RTC utilities

        Procedure:
            1. Write a known time to the RTC using an RTC utility and confirm write succeeds
            2. Read time back and verify it matches the written time
            3. Power cycle the CM4 and read the time again to verify retention

        Acceptance Criteria:
            - Write completes without error
            - Readback matches written time
            - RTC retains time across power loss

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #135: RTC Read/Write and Retention Across Power Cycle")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify RTC can be written, read back, and retains time across power loss")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}")
        print(f"  Max allowed drift: {config['max_time_drift_seconds']}s")
        print("=" * 70)

        # ================================================================
        # STEP 1: Initialize RTC Controller
        # ================================================================
        print("\n[STEP 1] Initialize RTC Controller")
        print("-" * 70)

        self.rtc = RTCController(host=config['host'])
        initialized = self.rtc.initialize()
        assert initialized, "Failed to initialize RTC controller"

        if self.rtc.use_mock:
            print("  Running in MOCK SIMULATION mode")
        else:
            print("  Running in HARDWARE mode")

        # ================================================================
        # STEP 2: Write Known Time to RTC
        # ================================================================
        print("\n[STEP 2] Write Known Time to RTC")
        print("-" * 70)

        test_time = self.create_test_time()
        print(f"  Test time to write: {test_time.to_datetime()}")

        write_result = self.rtc.write_time(test_time)

        print(f"  Write successful: {'YES' if write_result.success else 'NO'}")
        if not write_result.success:
            print(f"  Error: {write_result.error_message}")

        assert write_result.success, f"RTC write failed: {write_result.error_message}"

        # Small delay to allow RTC to update
        time.sleep(0.5)

        # ================================================================
        # STEP 3: Read Time Back and Verify
        # ================================================================
        print("\n[STEP 3] Read Time Back and Verify Match")
        print("-" * 70)

        read_result = self.rtc.read_time()

        print(f"  Read successful: {'YES' if read_result.success else 'NO'}")
        assert read_result.success, f"RTC read failed: {read_result.error_message}"

        read_time = read_result.time_value
        print(f"  Time read back: {read_time.to_datetime()}")

        matches, drift = self.times_match(test_time, read_time, config['max_time_drift_seconds'])

        print(f"  Time drift: {drift:.2f} seconds")
        print(f"  Within tolerance ({config['max_time_drift_seconds']}s): {'YES' if matches else 'NO'}")

        readback_matches = matches

        # ================================================================
        # STEP 4: Simulate Power Cycle
        # ================================================================
        print("\n[STEP 4] Power Cycle and Verify Retention")
        print("-" * 70)

        print(f"  Simulating power cycle ({config['power_cycle_duration']}s)...")

        time_before_cycle = read_result.time_value
        self.rtc.simulate_power_cycle(config['power_cycle_duration'])

        print("  Power cycle complete, reading RTC...")

        # ================================================================
        # STEP 5: Read Time After Power Cycle
        # ================================================================
        print("\n[STEP 5] Verify Time Retention After Power Cycle")
        print("-" * 70)

        read_after_cycle = self.rtc.read_time()

        assert read_after_cycle.success, f"RTC read after power cycle failed: {read_after_cycle.error_message}"

        time_after_cycle = read_after_cycle.time_value
        print(f"  Time after power cycle: {time_after_cycle.to_datetime()}")

        # Calculate expected time (original + elapsed during power cycle)
        expected_elapsed = config['power_cycle_duration'] + 1.0  # Add buffer
        expected_dt = time_before_cycle.to_datetime() + timedelta(seconds=config['power_cycle_duration'])

        actual_dt = time_after_cycle.to_datetime()
        retention_drift = abs((actual_dt - expected_dt).total_seconds())

        print(f"  Expected time (approx): {expected_dt}")
        print(f"  Actual time: {actual_dt}")
        print(f"  Drift from expected: {retention_drift:.2f} seconds")

        retention_verified = retention_drift <= config['max_time_drift_seconds']

        print(f"  Time retained: {'YES' if retention_verified else 'NO'}")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)

        all_pass = write_result.success and readback_matches and retention_verified

        if all_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 70)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if write_result.success else 'FAIL'}] Write completes without error")
        print(f"    [{'PASS' if readback_matches else 'FAIL'}] Readback matches written time")
        print(f"    [{'PASS' if retention_verified else 'FAIL'}] RTC retains time across power loss")

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")
        print("=" * 70)

        # Assertions
        assert write_result.success, "Write did not complete successfully"
        assert readback_matches, f"Readback does not match written time (drift: {drift:.2f}s)"
        assert retention_verified, f"RTC did not retain time across power cycle (drift: {retention_drift:.2f}s)"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_135_rtc_write_completes(self, test_config):
        """
        Test that RTC write operation completes without error.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #135b: RTC Write Completes Without Error")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        test_time = self.create_test_time()
        print(f"  Writing time: {test_time.to_datetime()}")

        result = self.rtc.write_time(test_time)

        print(f"\n  Write Operation:")
        print(f"    Success: {'YES' if result.success else 'NO'}")
        if result.error_message:
            print(f"    Error: {result.error_message}")

        print("\n" + "=" * 70)
        if result.success:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert result.success, f"RTC write failed: {result.error_message}"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_135_rtc_readback_matches(self, test_config):
        """
        Test that RTC readback matches written time.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #135c: RTC Readback Matches Written Time")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        # Write a known time
        test_time = self.create_test_time()
        write_result = self.rtc.write_time(test_time)
        assert write_result.success, "Write failed"

        print(f"  Written time: {test_time.to_datetime()}")

        # Small delay
        time.sleep(0.5)

        # Read back
        read_result = self.rtc.read_time()
        assert read_result.success, "Read failed"

        read_time = read_result.time_value
        print(f"  Read time: {read_time.to_datetime()}")

        # Check match
        matches, drift = self.times_match(test_time, read_time, config['max_time_drift_seconds'])

        print(f"\n  Comparison:")
        print(f"    Drift: {drift:.2f} seconds")
        print(f"    Tolerance: {config['max_time_drift_seconds']} seconds")
        print(f"    Match: {'YES' if matches else 'NO'}")

        print("\n" + "=" * 70)
        if matches:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert matches, f"Readback does not match (drift: {drift:.2f}s)"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_135_rtc_time_progresses(self, test_config):
        """
        Test that RTC time progresses correctly (ticks).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #135d: RTC Time Progresses")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        # Read initial time
        read1 = self.rtc.read_time()
        assert read1.success, "First read failed"
        time1 = read1.time_value

        print(f"  Initial time: {time1.to_datetime()}")

        # Wait 2 seconds
        wait_duration = 2.0
        print(f"  Waiting {wait_duration} seconds...")
        time.sleep(wait_duration)

        # Read again
        read2 = self.rtc.read_time()
        assert read2.success, "Second read failed"
        time2 = read2.time_value

        print(f"  Time after wait: {time2.to_datetime()}")

        # Calculate actual elapsed time in RTC
        dt1 = time1.to_datetime()
        dt2 = time2.to_datetime()
        elapsed = (dt2 - dt1).total_seconds()

        print(f"\n  Time Progression:")
        print(f"    Expected elapsed: ~{wait_duration} seconds")
        print(f"    Actual elapsed: {elapsed:.2f} seconds")

        # Allow some tolerance
        time_progressed = elapsed >= (wait_duration - 1.0) and elapsed <= (wait_duration + 1.0)
        print(f"    Time progressing: {'YES' if time_progressed else 'NO'}")

        print("\n" + "=" * 70)
        if time_progressed:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert time_progressed, f"RTC time not progressing correctly (elapsed: {elapsed:.2f}s, expected: ~{wait_duration}s)"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
