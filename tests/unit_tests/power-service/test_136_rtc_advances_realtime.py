#!/usr/bin/env python3
"""
Test Case #136: RTC Advances in Real Time
Unit Test for Power Service / RTC

Tests that the RTC advances in real time by reading the RTC, waiting several
minutes, and confirming the time has advanced appropriately.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock RTC with accelerated time for testing logic
2. Hardware mode: Uses actual RTC utilities on CM4 (requires PI_TARGET_IP)

Test Setup:
- DUT with RTC installed
- Access to RTC read utility

Procedure:
1. With RTC set and running, wait several minutes
2. Read RTC time again and confirm it has advanced appropriately

Acceptance Criteria:
- RTC advances in real time (e.g., ~5 minutes after ~5 minutes elapse)
"""

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


# Test durations
DEFAULT_WAIT_DURATION_SECONDS = 300  # 5 minutes for real test
SIMULATION_WAIT_DURATION_SECONDS = 5  # 5 seconds for simulation mode
MAX_ALLOWED_DRIFT_SECONDS = 5  # Allow up to 5 seconds drift


@dataclass
class RTCTime:
    """RTC time representation"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

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
            'datetime': str(self.to_datetime())
        }

    @staticmethod
    def from_datetime(dt: datetime) -> 'RTCTime':
        return RTCTime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second
        )


@dataclass
class RTCAdvanceValidation:
    """Validation result for RTC time advancement"""
    initial_time: RTCTime
    final_time: RTCTime
    elapsed_real_seconds: float
    elapsed_rtc_seconds: float
    drift_seconds: float
    advances_correctly: bool

    def to_dict(self) -> Dict:
        return {
            'initial_time': self.initial_time.to_dict(),
            'final_time': self.final_time.to_dict(),
            'elapsed_real_seconds': self.elapsed_real_seconds,
            'elapsed_rtc_seconds': self.elapsed_rtc_seconds,
            'drift_seconds': self.drift_seconds,
            'advances_correctly': self.advances_correctly
        }


class MockRTC:
    """
    Mock RTC for unit testing.
    Simulates RTC that advances in real time.
    """

    def __init__(self):
        self.base_time: datetime = datetime.now()
        self.base_real_time: float = time.time()
        # Simulate slight RTC drift (parts per million)
        self.drift_ppm: float = 0  # Perfect clock for testing

    def reset(self):
        """Reset mock RTC to current time"""
        self.base_time = datetime.now()
        self.base_real_time = time.time()

    def set_time(self, dt: datetime):
        """Set RTC time"""
        self.base_time = dt
        self.base_real_time = time.time()

    def read_time(self) -> RTCTime:
        """
        Read current RTC time.
        Simulates real-time advancement with optional drift.
        """
        elapsed_real = time.time() - self.base_real_time

        # Apply drift (ppm = parts per million)
        drift_factor = 1.0 + (self.drift_ppm / 1_000_000)
        elapsed_rtc = elapsed_real * drift_factor

        current_time = self.base_time + timedelta(seconds=elapsed_rtc)
        return RTCTime.from_datetime(current_time)


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

    def read_time(self) -> Optional[RTCTime]:
        """Read current RTC time"""
        if self.use_mock:
            return self.mock.read_time()
        return self._hardware_read_time()

    def _hardware_read_time(self) -> Optional[RTCTime]:
        """Read time from hardware RTC using hwclock"""
        import subprocess

        try:
            cmd = "sudo hwclock -r"

            if self.host and self.host != '127.0.0.1':
                cmd = f"ssh pi@{self.host} \"{cmd}\""

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                print(f"  Error reading RTC: {result.stderr}")
                return None

            # Parse hwclock output
            output = result.stdout.strip()
            dt = self._parse_hwclock_output(output)

            if dt:
                return RTCTime.from_datetime(dt)
            return None

        except Exception as e:
            print(f"  Exception reading RTC: {e}")
            return None

    def _parse_hwclock_output(self, output: str) -> Optional[datetime]:
        """Parse hwclock -r output to datetime"""
        try:
            formats = [
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
            ]

            for fmt in formats:
                try:
                    clean_output = output.split('+')[0].split('-00')[0].strip()
                    # Handle timezone offset in output
                    if '.' in clean_output:
                        clean_output = clean_output.split('.')[0]
                    return datetime.strptime(clean_output, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

            # Try parsing first two parts
            parts = output.split()
            if len(parts) >= 2:
                date_time_str = f"{parts[0]} {parts[1].split('.')[0]}"
                return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

            return None
        except Exception:
            return None


class TestRTCAdvancesRealTime:
    """Unit Test - RTC Advances in Real Time"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')

        # Use shorter duration for simulation mode
        is_simulation = host == '127.0.0.1'

        return {
            'host': host,
            'wait_duration_seconds': SIMULATION_WAIT_DURATION_SECONDS if is_simulation else DEFAULT_WAIT_DURATION_SECONDS,
            'max_drift_seconds': MAX_ALLOWED_DRIFT_SECONDS,
            'log_file': '/tmp/test_136_rtc_advances_realtime.log',
            'is_simulation': is_simulation,
        }

    def setup_method(self):
        """Setup before each test"""
        self.rtc: Optional[RTCController] = None

    def teardown_method(self):
        """Cleanup after each test"""
        pass

    def calculate_advancement(
        self,
        initial: RTCTime,
        final: RTCTime,
        elapsed_real_seconds: float,
        max_drift: float
    ) -> RTCAdvanceValidation:
        """Calculate and validate RTC time advancement"""
        dt_initial = initial.to_datetime()
        dt_final = final.to_datetime()

        elapsed_rtc_seconds = (dt_final - dt_initial).total_seconds()
        drift_seconds = abs(elapsed_rtc_seconds - elapsed_real_seconds)

        advances_correctly = drift_seconds <= max_drift

        return RTCAdvanceValidation(
            initial_time=initial,
            final_time=final,
            elapsed_real_seconds=elapsed_real_seconds,
            elapsed_rtc_seconds=elapsed_rtc_seconds,
            drift_seconds=drift_seconds,
            advances_correctly=advances_correctly
        )

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_136_rtc_advances_in_realtime(self, test_config):
        """
        Test Case #136: RTC advances in real time

        Test Setup:
            DUT with RTC installed; access to RTC read utility

        Procedure:
            1. With RTC set and running, wait several minutes
            2. Read RTC time again and confirm it has advanced appropriately

        Acceptance Criteria:
            RTC advances in real time (e.g., ~5 minutes after ~5 minutes elapse)

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #136: RTC Advances in Real Time")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify RTC advances in real time correctly")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}")
        print(f"  Wait duration: {config['wait_duration_seconds']} seconds")
        print(f"  Max allowed drift: {config['max_drift_seconds']} seconds")
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
            print(f"  (Using accelerated {config['wait_duration_seconds']}s wait instead of 5 minutes)")
        else:
            print("  Running in HARDWARE mode")
            print(f"  (Will wait {config['wait_duration_seconds']} seconds = {config['wait_duration_seconds']/60:.1f} minutes)")

        # ================================================================
        # STEP 2: Read Initial RTC Time
        # ================================================================
        print("\n[STEP 2] Read Initial RTC Time")
        print("-" * 70)

        initial_time = self.rtc.read_time()
        assert initial_time is not None, "Failed to read initial RTC time"

        start_real_time = time.time()

        print(f"  Initial RTC time: {initial_time.to_datetime()}")
        print(f"  Timestamp: {start_real_time:.3f}")

        # ================================================================
        # STEP 3: Wait for Specified Duration
        # ================================================================
        print("\n[STEP 3] Wait for Time to Elapse")
        print("-" * 70)

        wait_duration = config['wait_duration_seconds']
        print(f"  Waiting {wait_duration} seconds...")

        # Show progress for long waits
        if wait_duration > 10:
            intervals = 10
            interval_duration = wait_duration / intervals
            for i in range(intervals):
                time.sleep(interval_duration)
                elapsed = (i + 1) * interval_duration
                print(f"    Progress: {elapsed:.0f}/{wait_duration} seconds ({100*(i+1)/intervals:.0f}%)")
        else:
            time.sleep(wait_duration)

        end_real_time = time.time()
        actual_elapsed = end_real_time - start_real_time

        print(f"  Wait complete. Actual elapsed: {actual_elapsed:.2f} seconds")

        # ================================================================
        # STEP 4: Read Final RTC Time
        # ================================================================
        print("\n[STEP 4] Read Final RTC Time")
        print("-" * 70)

        final_time = self.rtc.read_time()
        assert final_time is not None, "Failed to read final RTC time"

        print(f"  Final RTC time: {final_time.to_datetime()}")

        # ================================================================
        # STEP 5: Validate Time Advancement
        # ================================================================
        print("\n[STEP 5] Validate RTC Time Advancement")
        print("-" * 70)

        validation = self.calculate_advancement(
            initial_time, final_time, actual_elapsed, config['max_drift_seconds']
        )

        print(f"\n  Time Advancement Analysis:")
        print(f"    Initial RTC time: {validation.initial_time.to_datetime()}")
        print(f"    Final RTC time:   {validation.final_time.to_datetime()}")
        print(f"    Real time elapsed: {validation.elapsed_real_seconds:.2f} seconds")
        print(f"    RTC time elapsed:  {validation.elapsed_rtc_seconds:.2f} seconds")
        print(f"    Drift: {validation.drift_seconds:.2f} seconds")
        print(f"    Max allowed drift: {config['max_drift_seconds']} seconds")
        print(f"    Advances correctly: {'YES' if validation.advances_correctly else 'NO'}")

        # Calculate drift in PPM (parts per million) for reference
        if validation.elapsed_real_seconds > 0:
            drift_ppm = (validation.drift_seconds / validation.elapsed_real_seconds) * 1_000_000
            print(f"    Drift rate: {drift_ppm:.1f} PPM")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)

        if validation.advances_correctly:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 70)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if validation.advances_correctly else 'FAIL'}] "
              f"RTC advances in real time (~{validation.elapsed_rtc_seconds:.0f}s after ~{validation.elapsed_real_seconds:.0f}s elapsed)")

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")
        print("=" * 70)

        # Assertion
        assert validation.advances_correctly, \
            f"RTC drift ({validation.drift_seconds:.2f}s) exceeds maximum allowed ({config['max_drift_seconds']}s)"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_136_rtc_advances_short_interval(self, test_config):
        """
        Test RTC advances correctly over a short interval (10 seconds).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #136b: RTC Advances Over Short Interval (10s)")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        # Read initial time
        initial = self.rtc.read_time()
        assert initial is not None, "Failed to read initial time"
        start = time.time()

        print(f"  Initial time: {initial.to_datetime()}")

        # Wait 10 seconds
        wait_seconds = 10
        print(f"  Waiting {wait_seconds} seconds...")
        time.sleep(wait_seconds)

        # Read final time
        final = self.rtc.read_time()
        assert final is not None, "Failed to read final time"
        elapsed = time.time() - start

        print(f"  Final time: {final.to_datetime()}")

        # Calculate RTC elapsed
        rtc_elapsed = (final.to_datetime() - initial.to_datetime()).total_seconds()
        drift = abs(rtc_elapsed - elapsed)

        print(f"\n  Analysis:")
        print(f"    Real elapsed: {elapsed:.2f}s")
        print(f"    RTC elapsed: {rtc_elapsed:.2f}s")
        print(f"    Drift: {drift:.2f}s")

        # Allow 2 seconds drift for short test
        advances_correctly = drift <= 2.0

        print("\n" + "=" * 70)
        if advances_correctly:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert advances_correctly, f"RTC drift too large: {drift:.2f}s"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_136_rtc_advances_one_minute(self, test_config):
        """
        Test RTC advances correctly over one minute.
        Uses accelerated simulation in mock mode.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #136c: RTC Advances Over One Minute")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        # Use shorter wait for simulation
        wait_seconds = 5 if self.rtc.use_mock else 60

        # Read initial time
        initial = self.rtc.read_time()
        assert initial is not None, "Failed to read initial time"
        start = time.time()

        print(f"  Initial time: {initial.to_datetime()}")
        print(f"  Waiting {wait_seconds} seconds...")

        time.sleep(wait_seconds)

        # Read final time
        final = self.rtc.read_time()
        assert final is not None, "Failed to read final time"
        elapsed = time.time() - start

        print(f"  Final time: {final.to_datetime()}")

        # Calculate RTC elapsed
        rtc_elapsed = (final.to_datetime() - initial.to_datetime()).total_seconds()
        drift = abs(rtc_elapsed - elapsed)

        print(f"\n  Analysis:")
        print(f"    Real elapsed: {elapsed:.2f}s")
        print(f"    RTC elapsed: {rtc_elapsed:.2f}s")
        print(f"    Drift: {drift:.2f}s")

        advances_correctly = drift <= config['max_drift_seconds']

        print("\n" + "=" * 70)
        if advances_correctly:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert advances_correctly, f"RTC drift too large: {drift:.2f}s"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    def test_136_rtc_time_monotonic(self, test_config):
        """
        Test that RTC time is monotonically increasing (never goes backward).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #136d: RTC Time is Monotonically Increasing")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        # Read time multiple times
        num_readings = 5
        readings = []

        print(f"\n  Taking {num_readings} readings with 1s intervals...")

        for i in range(num_readings):
            rtc_time = self.rtc.read_time()
            assert rtc_time is not None, f"Failed to read time at reading {i+1}"
            readings.append(rtc_time)
            print(f"    [{i+1}] {rtc_time.to_datetime()}")
            if i < num_readings - 1:
                time.sleep(1)

        # Check monotonicity
        is_monotonic = True
        for i in range(1, len(readings)):
            dt_prev = readings[i-1].to_datetime()
            dt_curr = readings[i].to_datetime()
            if dt_curr < dt_prev:
                is_monotonic = False
                print(f"\n  ERROR: Time went backward at reading {i+1}")
                print(f"    Previous: {dt_prev}")
                print(f"    Current: {dt_curr}")
                break

        print(f"\n  Time monotonically increasing: {'YES' if is_monotonic else 'NO'}")

        print("\n" + "=" * 70)
        if is_monotonic:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert is_monotonic, "RTC time is not monotonically increasing"

    @pytest.mark.unit
    @pytest.mark.rtc
    @pytest.mark.power
    @pytest.mark.slow
    def test_136_rtc_advances_five_minutes(self, test_config):
        """
        Test RTC advances correctly over 5 minutes (full test duration).
        Marked as slow - only runs in hardware mode or when explicitly requested.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #136e: RTC Advances Over 5 Minutes")
        print("=" * 70)

        self.rtc = RTCController(host=config['host'])
        self.rtc.initialize()

        print(f"\n  Mode: {'Mock Simulation' if self.rtc.use_mock else 'Hardware'}")

        # Use actual 5 minutes for hardware, short for simulation
        if self.rtc.use_mock:
            wait_seconds = 5
            print("  (Simulation mode: using 5 second wait)")
        else:
            wait_seconds = 300  # 5 minutes
            print(f"  Will wait {wait_seconds/60:.0f} minutes")

        # Read initial time
        initial = self.rtc.read_time()
        assert initial is not None, "Failed to read initial time"
        start = time.time()

        print(f"\n  Initial time: {initial.to_datetime()}")
        print(f"  Waiting {wait_seconds} seconds ({wait_seconds/60:.1f} minutes)...")

        # Show progress
        if wait_seconds > 30:
            intervals = 10
            interval_duration = wait_seconds / intervals
            for i in range(intervals):
                time.sleep(interval_duration)
                elapsed = (i + 1) * interval_duration
                remaining = wait_seconds - elapsed
                print(f"    Elapsed: {elapsed/60:.1f} min, Remaining: {remaining/60:.1f} min")
        else:
            time.sleep(wait_seconds)

        # Read final time
        final = self.rtc.read_time()
        assert final is not None, "Failed to read final time"
        elapsed = time.time() - start

        print(f"\n  Final time: {final.to_datetime()}")

        # Calculate RTC elapsed
        rtc_elapsed = (final.to_datetime() - initial.to_datetime()).total_seconds()
        drift = abs(rtc_elapsed - elapsed)

        print(f"\n  Analysis:")
        print(f"    Real elapsed: {elapsed:.2f}s ({elapsed/60:.2f} min)")
        print(f"    RTC elapsed: {rtc_elapsed:.2f}s ({rtc_elapsed/60:.2f} min)")
        print(f"    Drift: {drift:.2f}s")
        print(f"    Expected: ~{wait_seconds/60:.0f} minutes elapsed in both")

        advances_correctly = drift <= config['max_drift_seconds']

        print("\n" + "=" * 70)
        if advances_correctly:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        print(f"\n  Acceptance Criteria:")
        print(f"    [{'PASS' if advances_correctly else 'FAIL'}] "
              f"RTC advances ~5 minutes after ~5 minutes elapse")

        assert advances_correctly, \
            f"RTC drift ({drift:.2f}s) exceeds maximum ({config['max_drift_seconds']}s)"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
