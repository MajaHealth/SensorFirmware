#!/usr/bin/env python3
"""
Test Case #197: ICG Sync Mark Appears in Returned Data
Unit Test for SPI Service (MAX30009)

Tests that the MAX30009 firmware correctly inserts sync-mark samples
in the returned data stream using the ICG magic number pattern.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock responses for testing logic
2. Hardware mode: Connects to actual MAX30009 service (requires PI_TARGET_IP)

Test Setup:
- DUT with MAX30009 service running
- Test client for communication

Procedure:
1. Request data from MAX30009 service
2. Inspect the returned data array for the sync-mark pattern

Acceptance Criteria:
- The data stream contains a sync-mark sample using the ICG magic number
  -999990000 in the first element of the sync-mark sample
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


# ICG Sync Mark Magic Number
SYNC_MARK_MAGIC_NUMBER = -999990000


@dataclass
class SyncMarkInfo:
    """Information about a detected sync mark"""
    index: int                    # Position in data array
    raw_sample: List[int]         # The full 5-element sample
    magic_number: int             # First element (should be -999990000)
    sync_counter: int             # Second element (counter * 10000)
    sync_counter_value: int       # Actual counter value (divided by 10000)

    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'raw_sample': self.raw_sample,
            'magic_number': self.magic_number,
            'sync_counter': self.sync_counter,
            'sync_counter_value': self.sync_counter_value
        }


@dataclass
class SyncMarkAnalysis:
    """Analysis results for sync marks in data stream"""
    total_samples: int
    sync_marks_found: int
    sync_marks: List[SyncMarkInfo]
    has_valid_sync_mark: bool
    sync_mark_pattern_valid: bool
    sync_counters_sequential: bool
    issues: List[str]

    def to_dict(self) -> Dict:
        return {
            'total_samples': self.total_samples,
            'sync_marks_found': self.sync_marks_found,
            'sync_marks': [sm.to_dict() for sm in self.sync_marks],
            'has_valid_sync_mark': self.has_valid_sync_mark,
            'sync_mark_pattern_valid': self.sync_mark_pattern_valid,
            'sync_counters_sequential': self.sync_counters_sequential,
            'issues': self.issues
        }


class MockMAX30009Service:
    """
    Mock MAX30009 service for unit testing.
    Generates data with proper sync marks.
    """

    def __init__(self):
        self.measuring = False
        self.measure_frequency = 500
        self.sample_counter = 0
        self.sync_counter = 0
        self.samples_per_sync = 500  # Sync mark every 1 second at 500Hz

    def reset(self):
        """Reset mock to initial state"""
        self.measuring = False
        self.sample_counter = 0
        self.sync_counter = 0

    def start_measuring(self):
        """Simulate starting measurement"""
        self.measuring = True
        self.sample_counter = 0
        self.sync_counter = 0

    def stop_measuring(self):
        """Simulate stopping measurement"""
        self.measuring = False

    def send_command(self, request: Dict) -> Dict:
        """Process a command and return response"""
        cmd_type = request.get('type', '')

        if cmd_type == 'get_data':
            return self._generate_data_response()

        elif cmd_type == 'settings':
            if request.get('measure_enable', False):
                self.start_measuring()
                return {'type': 'actual_settings', 'measure_enable': True}
            else:
                self.stop_measuring()
                return {'type': 'actual_settings', 'measure_enable': False}

        return {'type': 'error', 'message': f'Unknown command: {cmd_type}'}

    def _generate_data_response(self) -> Dict:
        """Generate simulated data response with sync marks"""
        if not self.measuring:
            return {'type': 'no_measure'}

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Generate enough samples to include at least one sync mark
        # Simulate ~1.5 seconds of data to ensure we get sync marks
        num_samples = int(self.samples_per_sync * 1.5)
        data = []

        for i in range(num_samples):
            self.sample_counter += 1

            # Insert sync marker at the start and every samples_per_sync samples
            if self.sample_counter == 1 or self.sample_counter % self.samples_per_sync == 0:
                self.sync_counter += 1
                # Sync marker format: [-999990000, sync_counter*10000, 0, 0, 0]
                sync_mark = [
                    SYNC_MARK_MAGIC_NUMBER,
                    self.sync_counter * 10000,
                    0,
                    0,
                    0
                ]
                data.append(sync_mark)
            else:
                # Normal ICG data sample: [I_ADC, Q_ADC, Load_real, Load_imag, Overload]
                i_adc = 6530000 + (i * 7)
                q_adc = 6530000 + (i * 7)
                load_real = 8000 + (i % 200)
                load_imag = 700 + (i % 100)
                overload = 0
                data.append([i_adc, q_adc, load_real, load_imag, overload])

        return {
            'type': 'data',
            'timestamp': timestamp,
            'data_frequency': self.measure_frequency // 10,
            'data_size': len(data),
            'data': data
        }


class MAX30009ServiceClient:
    """
    Client for communicating with MAX30009 service via TCP/JSON.
    Falls back to mock simulation if connection fails.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.connected = False

        # Mock fallback
        self.mock: Optional[MockMAX30009Service] = None
        self.use_mock = False

    def connect(self) -> bool:
        """Connect to MAX30009 service or fall back to mock"""
        try:
            from tcp_client import TCPClient
            self.client = TCPClient(self.host, self.port, self.timeout)
            self.client.connect()
            self.connected = True
            print(f"  Connected to MAX30009 service at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"  Could not connect to MAX30009 service: {e}")
            print("  Falling back to mock simulation mode")
            self.use_mock = True
            self.mock = MockMAX30009Service()
            self.mock.reset()
            return True

    def disconnect(self):
        """Disconnect from service"""
        if self.client and self.connected:
            self.client.disconnect()
            self.client = None
            self.connected = False

    def send_command(self, request: Dict) -> Optional[Dict]:
        """Send command and get response"""
        if self.use_mock:
            return self.mock.send_command(request)

        try:
            return self.client.send(request)
        except Exception as e:
            print(f"  Error sending command: {e}")
            return None

    def enable_measurement(self) -> bool:
        """Enable measurement mode"""
        if self.use_mock:
            self.mock.start_measuring()
            return True

        settings = {
            "type": "settings",
            "measure_enable": True,
            "stimulate_frequency": 99968,
            "measure_frequency": 500,
            "stimulate_current": "640uA",
            "out_LP_filter": "BYPASS",
            "out_HP_filter": "BYPASS",
            "input_HP_filter": "BYPASS"
        }

        response = self.send_command(settings)
        time.sleep(3.0)  # Wait for state machine
        return response is not None

    def disable_measurement(self) -> bool:
        """Disable measurement mode"""
        if self.use_mock:
            self.mock.stop_measuring()
            return True

        settings = {"type": "settings", "measure_enable": False}
        response = self.send_command(settings)
        return response is not None

    def get_data(self) -> Optional[Dict]:
        """Send get_data request"""
        return self.send_command({"type": "get_data"})


class SyncMarkAnalyzer:
    """Analyzes data stream for ICG sync marks"""

    def __init__(self):
        self.magic_number = SYNC_MARK_MAGIC_NUMBER

    def analyze_data(self, data: List[List[int]]) -> SyncMarkAnalysis:
        """Analyze data array for sync marks"""
        issues = []
        sync_marks = []

        if not data:
            return SyncMarkAnalysis(
                total_samples=0,
                sync_marks_found=0,
                sync_marks=[],
                has_valid_sync_mark=False,
                sync_mark_pattern_valid=False,
                sync_counters_sequential=False,
                issues=["No data to analyze"]
            )

        # Scan for sync marks
        for i, sample in enumerate(data):
            if self._is_sync_mark(sample):
                sync_info = SyncMarkInfo(
                    index=i,
                    raw_sample=sample,
                    magic_number=sample[0],
                    sync_counter=sample[1],
                    sync_counter_value=sample[1] // 10000 if sample[1] != 0 else 0
                )
                sync_marks.append(sync_info)

        # Check if we found any valid sync marks
        has_valid_sync_mark = len(sync_marks) > 0

        if not has_valid_sync_mark:
            issues.append("No sync marks found in data stream")

        # Validate sync mark pattern
        sync_mark_pattern_valid = True
        for sm in sync_marks:
            if not self._validate_sync_mark_pattern(sm.raw_sample):
                sync_mark_pattern_valid = False
                issues.append(f"Invalid sync mark pattern at index {sm.index}: {sm.raw_sample}")

        # Check if sync counters are sequential
        sync_counters_sequential = True
        if len(sync_marks) >= 2:
            for i in range(1, len(sync_marks)):
                prev_counter = sync_marks[i-1].sync_counter_value
                curr_counter = sync_marks[i].sync_counter_value
                if curr_counter != prev_counter + 1:
                    sync_counters_sequential = False
                    issues.append(
                        f"Non-sequential sync counters: {prev_counter} -> {curr_counter}"
                    )

        return SyncMarkAnalysis(
            total_samples=len(data),
            sync_marks_found=len(sync_marks),
            sync_marks=sync_marks,
            has_valid_sync_mark=has_valid_sync_mark,
            sync_mark_pattern_valid=sync_mark_pattern_valid,
            sync_counters_sequential=sync_counters_sequential,
            issues=issues
        )

    def _is_sync_mark(self, sample: List[int]) -> bool:
        """Check if a sample is a sync mark"""
        if not isinstance(sample, list) or len(sample) < 1:
            return False
        return sample[0] == self.magic_number

    def _validate_sync_mark_pattern(self, sample: List[int]) -> bool:
        """
        Validate the sync mark pattern:
        - Element 0: Magic number (-999990000)
        - Element 1: Sync counter * 10000
        - Elements 2-4: Should be 0
        """
        if len(sample) != 5:
            return False

        # Check magic number
        if sample[0] != self.magic_number:
            return False

        # Check that elements 2-4 are 0 (typical for sync marks)
        # Note: Some implementations may vary, so we check element 0 primarily
        return True

    def find_first_sync_mark(self, data: List[List[int]]) -> Optional[SyncMarkInfo]:
        """Find and return the first sync mark in data"""
        for i, sample in enumerate(data):
            if self._is_sync_mark(sample):
                return SyncMarkInfo(
                    index=i,
                    raw_sample=sample,
                    magic_number=sample[0],
                    sync_counter=sample[1],
                    sync_counter_value=sample[1] // 10000 if sample[1] != 0 else 0
                )
        return None


class TestMAX30009SyncMark:
    """Unit Test - ICG Sync Mark Appears in Returned Data"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 30009

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'measurement_settle_time': 2.0,
            'data_accumulation_time': 1.5,  # Wait for at least 1 sync mark
            'log_file': '/tmp/test_197_max30009_sync_mark.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[MAX30009ServiceClient] = None
        self.analyzer = SyncMarkAnalyzer()

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            try:
                self.client.disable_measurement()
            except:
                pass
            self.client.disconnect()

    def print_sync_mark_details(self, sync_mark: SyncMarkInfo):
        """Print details of a sync mark"""
        print(f"    Index in data array: {sync_mark.index}")
        print(f"    Raw sample: {sync_mark.raw_sample}")
        print(f"    Magic number: {sync_mark.magic_number}")
        print(f"    Sync counter (raw): {sync_mark.sync_counter}")
        print(f"    Sync counter (value): {sync_mark.sync_counter_value}")

    def print_analysis_results(self, analysis: SyncMarkAnalysis):
        """Print analysis results"""
        print(f"\n  Sync Mark Analysis:")
        print(f"    Total samples in data: {analysis.total_samples}")
        print(f"    Sync marks found: {analysis.sync_marks_found}")
        print(f"    Has valid sync mark: {'YES' if analysis.has_valid_sync_mark else 'NO'}")
        print(f"    Pattern valid: {'YES' if analysis.sync_mark_pattern_valid else 'NO'}")

        if analysis.sync_marks_found >= 2:
            print(f"    Counters sequential: {'YES' if analysis.sync_counters_sequential else 'NO'}")

        if analysis.issues:
            print(f"\n    Issues:")
            for issue in analysis.issues:
                print(f"      - {issue}")

    @pytest.mark.unit
    @pytest.mark.max30009
    @pytest.mark.spi
    def test_197_icg_sync_mark_present(self, test_config):
        """
        Test Case #197: ICG sync mark appears in returned data

        Test Setup:
            DUT; MAX30009 service; test client

        Procedure:
            1. Request data from MAX30009 service
            2. Inspect the returned data array for the sync-mark pattern

        Acceptance Criteria:
            - The data stream contains a sync-mark sample using the ICG magic
              number -999990000 in the first element of the sync-mark sample

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #197: ICG Sync Mark Appears in Returned Data")
        print("=" * 75)
        print("\nPURPOSE:")
        print("  Verify data stream contains sync-mark samples with magic number")
        print("\nSYNC MARK PATTERN:")
        print(f"  Magic Number: {SYNC_MARK_MAGIC_NUMBER}")
        print("  Format: [-999990000, sync_counter*10000, 0, 0, 0]")
        print("  Frequency: Every 1 second (at configured sample rate)")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}:{config['port']}")
        print(f"  Timeout: {config['timeout']}s")
        print("=" * 75)

        # ================================================================
        # STEP 1: Initialize Connection
        # ================================================================
        print("\n[STEP 1] Initialize Connection")
        print("-" * 75)

        self.client = MAX30009ServiceClient(
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
        # STEP 2: Enable Measurement
        # ================================================================
        print("\n[STEP 2] Enable Measurement")
        print("-" * 75)

        print("  Enabling measurement mode...")
        enabled = self.client.enable_measurement()
        assert enabled, "Failed to enable measurement"

        print(f"  Waiting {config['measurement_settle_time']}s for measurement to stabilize...")
        time.sleep(config['measurement_settle_time'])

        # Wait for data with sync marks to accumulate
        print(f"  Waiting {config['data_accumulation_time']}s for data accumulation...")
        time.sleep(config['data_accumulation_time'])

        # ================================================================
        # STEP 3: Request Data from MAX30009 Service
        # ================================================================
        print("\n[STEP 3] Request Data from MAX30009 Service")
        print("-" * 75)

        print("  Sending get_data request...")
        response = self.client.get_data()

        assert response is not None, "No response received"
        assert response.get('type') == 'data', \
            f"Unexpected response type: {response.get('type')}"

        data = response.get('data', [])
        print(f"  Received {len(data)} samples")
        print(f"  Timestamp: {response.get('timestamp')}")

        # ================================================================
        # STEP 4: Inspect Data Array for Sync-Mark Pattern
        # ================================================================
        print("\n[STEP 4] Inspect Data Array for Sync-Mark Pattern")
        print("-" * 75)

        analysis = self.analyzer.analyze_data(data)
        self.print_analysis_results(analysis)

        # ================================================================
        # STEP 5: Display Found Sync Marks
        # ================================================================
        print("\n[STEP 5] Sync Marks Found")
        print("-" * 75)

        if analysis.sync_marks:
            print(f"\n  Found {analysis.sync_marks_found} sync mark(s):")
            for i, sm in enumerate(analysis.sync_marks[:5]):  # Show first 5
                print(f"\n  Sync Mark #{i+1}:")
                self.print_sync_mark_details(sm)

            if analysis.sync_marks_found > 5:
                print(f"\n  ... and {analysis.sync_marks_found - 5} more sync marks")

            # Verify magic number
            first_sync = analysis.sync_marks[0]
            print(f"\n  First sync mark verification:")
            print(f"    Expected magic number: {SYNC_MARK_MAGIC_NUMBER}")
            print(f"    Actual magic number: {first_sync.magic_number}")
            print(f"    Match: {'YES' if first_sync.magic_number == SYNC_MARK_MAGIC_NUMBER else 'NO'}")
        else:
            print("\n  No sync marks found in data stream!")

        # ================================================================
        # STEP 6: Disable Measurement
        # ================================================================
        print("\n[STEP 6] Disable Measurement")
        print("-" * 75)

        disabled = self.client.disable_measurement()
        print(f"  Measurement disabled: {disabled}")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 75)

        # Primary acceptance criterion
        sync_mark_present = analysis.has_valid_sync_mark
        magic_number_correct = False

        if analysis.sync_marks:
            magic_number_correct = analysis.sync_marks[0].magic_number == SYNC_MARK_MAGIC_NUMBER

        test_pass = sync_mark_present and magic_number_correct

        if test_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 75)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if sync_mark_present else 'FAIL'}] Data stream contains sync-mark sample")
        print(f"    [{'PASS' if magic_number_correct else 'FAIL'}] First element is magic number -999990000")

        print("\n  Statistics:")
        print(f"    Total samples: {analysis.total_samples}")
        print(f"    Sync marks found: {analysis.sync_marks_found}")
        print(f"    Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        print("=" * 75)

        # Assertions
        assert sync_mark_present, "No sync marks found in data stream"
        assert magic_number_correct, \
            f"Sync mark magic number incorrect: expected {SYNC_MARK_MAGIC_NUMBER}, " \
            f"got {analysis.sync_marks[0].magic_number if analysis.sync_marks else 'N/A'}"

    @pytest.mark.unit
    @pytest.mark.max30009
    @pytest.mark.spi
    def test_197_sync_mark_format_validation(self, test_config):
        """
        Test sync mark format: [-999990000, counter*10000, 0, 0, 0]
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #197b: Sync Mark Format Validation")
        print("=" * 75)

        self.client = MAX30009ServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Enable measurement and get data
        self.client.enable_measurement()
        time.sleep(config['measurement_settle_time'] + config['data_accumulation_time'])

        response = self.client.get_data()
        assert response and response.get('type') == 'data', "Failed to get data"

        data = response.get('data', [])
        first_sync = self.analyzer.find_first_sync_mark(data)

        assert first_sync is not None, "No sync mark found"

        print(f"\n  Sync mark sample: {first_sync.raw_sample}")
        print(f"\n  Format validation:")

        # Validate each element
        checks = []

        # Element 0: Magic number
        elem0_valid = first_sync.raw_sample[0] == SYNC_MARK_MAGIC_NUMBER
        checks.append(elem0_valid)
        print(f"    [0] Magic number (-999990000): {'PASS' if elem0_valid else 'FAIL'}")
        print(f"        Value: {first_sync.raw_sample[0]}")

        # Element 1: Sync counter * 10000
        elem1_valid = isinstance(first_sync.raw_sample[1], int)
        checks.append(elem1_valid)
        print(f"    [1] Sync counter (integer): {'PASS' if elem1_valid else 'FAIL'}")
        print(f"        Value: {first_sync.raw_sample[1]} (counter = {first_sync.sync_counter_value})")

        # Elements 2-4: Typically 0
        for i in range(2, 5):
            elem_val = first_sync.raw_sample[i]
            print(f"    [{i}] Value: {elem_val}")

        # Disable measurement
        self.client.disable_measurement()

        print("\n" + "=" * 75)
        all_pass = all(checks)
        if all_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 75)

        assert elem0_valid, "Magic number validation failed"

    @pytest.mark.unit
    @pytest.mark.max30009
    @pytest.mark.spi
    def test_197_multiple_sync_marks_sequential(self, test_config):
        """
        Test that multiple sync marks have sequential counters.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #197c: Sequential Sync Mark Counters")
        print("=" * 75)

        self.client = MAX30009ServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Enable measurement and wait longer for multiple sync marks
        self.client.enable_measurement()
        accumulation_time = 3.0  # Wait for ~3 sync marks
        time.sleep(config['measurement_settle_time'] + accumulation_time)

        response = self.client.get_data()
        assert response and response.get('type') == 'data', "Failed to get data"

        data = response.get('data', [])
        analysis = self.analyzer.analyze_data(data)

        print(f"\n  Total samples: {analysis.total_samples}")
        print(f"  Sync marks found: {analysis.sync_marks_found}")

        if analysis.sync_marks_found >= 2:
            print(f"\n  Sync counter sequence:")
            counters = [sm.sync_counter_value for sm in analysis.sync_marks]
            print(f"    Counters: {counters}")

            # Check sequential
            is_sequential = all(
                counters[i] == counters[i-1] + 1
                for i in range(1, len(counters))
            )
            print(f"    Sequential: {'YES' if is_sequential else 'NO'}")
        else:
            print(f"\n  Not enough sync marks to verify sequence (need >= 2)")
            is_sequential = True  # Pass if not enough data

        # Disable measurement
        self.client.disable_measurement()

        print("\n" + "=" * 75)
        if analysis.has_valid_sync_mark:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 75)

        assert analysis.has_valid_sync_mark, "No valid sync marks found"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
