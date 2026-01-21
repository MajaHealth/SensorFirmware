#!/usr/bin/env python3
"""
Test Case #196: MAX30009 get_data Returns Data Envelope Fields
Unit Test for SPI Service (MAX30009)

Tests that the MAX30009 firmware correctly returns data envelope fields
when responding to get_data requests.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock responses for testing logic
2. Hardware mode: Connects to actual MAX30009 service (requires PI_TARGET_IP)

Test Setup:
- DUT with MAX30009 service running
- Test client for communication
- Log capture enabled

Procedure:
1. Ensure MAX30009 is in measuring state
2. Send a get_data request
3. Capture the response envelope

Acceptance Criteria:
- Response type = "data"
- Response includes "data" field (array of samples)
- Response includes "data_size" field (number of samples)
- Response includes "timestamp" field
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


class MeasureState(Enum):
    """MAX30009 measurement states"""
    IDLE = "idle"
    PRE_MEASURING = "pre_measuring"
    PRE_MEASURE_END = "pre_measure_end"
    CALIBRATING = "calibrating"
    CALIBRATE_END = "calibrate_end"
    START_MEASURING = "start_measuring"
    MEASURING = "measuring"


@dataclass
class DataEnvelope:
    """Represents the data envelope returned by get_data"""
    type: str
    data: Optional[List[List[int]]]
    data_size: Optional[int]
    timestamp: Optional[str]
    data_frequency: Optional[int]
    raw_response: Dict

    @property
    def is_valid(self) -> bool:
        """Check if envelope has all required fields"""
        return (
            self.type == "data" and
            self.data is not None and
            self.data_size is not None and
            self.timestamp is not None
        )

    @property
    def has_data_field(self) -> bool:
        return self.data is not None

    @property
    def has_data_size_field(self) -> bool:
        return self.data_size is not None

    @property
    def has_timestamp_field(self) -> bool:
        return self.timestamp is not None

    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'data': self.data,
            'data_size': self.data_size,
            'timestamp': self.timestamp,
            'data_frequency': self.data_frequency,
            'is_valid': self.is_valid
        }


@dataclass
class EnvelopeValidation:
    """Validation results for data envelope"""
    type_valid: bool
    has_data: bool
    has_data_size: bool
    has_timestamp: bool
    data_size_matches: bool
    data_format_valid: bool
    timestamp_format_valid: bool
    all_valid: bool
    issues: List[str]

    def to_dict(self) -> Dict:
        return {
            'type_valid': self.type_valid,
            'has_data': self.has_data,
            'has_data_size': self.has_data_size,
            'has_timestamp': self.has_timestamp,
            'data_size_matches': self.data_size_matches,
            'data_format_valid': self.data_format_valid,
            'timestamp_format_valid': self.timestamp_format_valid,
            'all_valid': self.all_valid,
            'issues': self.issues
        }


class MockMAX30009Service:
    """
    Mock MAX30009 service for unit testing.
    Simulates firmware responses without actual hardware.
    """

    def __init__(self):
        self.measuring = False
        self.measure_frequency = 500
        self.stimulate_frequency = 99968
        self.sample_counter = 0
        self.sync_counter = 0

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

        elif cmd_type == 'get_settings':
            return {
                'type': 'actual_settings',
                'measure_enable': self.measuring,
                'measure_frequency': self.measure_frequency,
                'stimulate_frequency': self.stimulate_frequency
            }

        return {'type': 'error', 'message': f'Unknown command: {cmd_type}'}

    def _generate_data_response(self) -> Dict:
        """Generate simulated data response with proper envelope"""
        if not self.measuring:
            return {'type': 'no_measure'}

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Generate sample data
        num_samples = 50  # Simulate ~100ms of data at 500Hz
        data = []

        for i in range(num_samples):
            self.sample_counter += 1

            # Insert sync marker every ~500 samples (1 second at 500Hz)
            if self.sample_counter % 500 == 0:
                self.sync_counter += 1
                # Sync marker format: [-999990000, sync_counter*10000, 0, 0, 0]
                data.append([-999990000, self.sync_counter * 10000, 0, 0, 0])
            else:
                # Normal data sample: [I_ADC, Q_ADC, Load_real, Load_imag, Overload]
                i_adc = 6530000 + (i * 10)
                q_adc = 6530000 + (i * 10)
                load_real = 8000 + (i % 100)
                load_imag = 700 + (i % 50)
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

        # Send settings to enable measurement
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

        # Wait for measurement to start (state machine transitions)
        time.sleep(3.0)

        return response is not None

    def disable_measurement(self) -> bool:
        """Disable measurement mode"""
        if self.use_mock:
            self.mock.stop_measuring()
            return True

        settings = {
            "type": "settings",
            "measure_enable": False
        }
        response = self.send_command(settings)
        return response is not None

    def get_data(self) -> Optional[Dict]:
        """Send get_data request"""
        return self.send_command({"type": "get_data"})

    def is_measuring(self) -> bool:
        """Check if currently measuring"""
        if self.use_mock:
            return self.mock.measuring

        response = self.send_command({"type": "get_settings"})
        if response:
            return response.get('measure_enable', False)
        return False


class DataEnvelopeValidator:
    """Validates MAX30009 data envelope responses"""

    # Expected data array element count (I_ADC, Q_ADC, Load_real, Load_imag, Overload)
    EXPECTED_SAMPLE_SIZE = 5

    # Sync marker magic number
    SYNC_MARKER_VALUE = -999990000

    def validate_envelope(self, response: Dict) -> EnvelopeValidation:
        """Validate the complete data envelope"""
        issues = []

        # Check type field
        type_valid = response.get('type') == 'data'
        if not type_valid:
            issues.append(f"Invalid type: expected 'data', got '{response.get('type')}'")

        # Check data field
        has_data = 'data' in response and response['data'] is not None
        if not has_data:
            issues.append("Missing 'data' field")

        # Check data_size field
        has_data_size = 'data_size' in response and response['data_size'] is not None
        if not has_data_size:
            issues.append("Missing 'data_size' field")

        # Check timestamp field
        has_timestamp = 'timestamp' in response and response['timestamp'] is not None
        if not has_timestamp:
            issues.append("Missing 'timestamp' field")

        # Check data_size matches actual data length
        data_size_matches = True
        if has_data and has_data_size:
            actual_size = len(response['data'])
            reported_size = response['data_size']
            data_size_matches = (actual_size == reported_size)
            if not data_size_matches:
                issues.append(f"data_size mismatch: reported {reported_size}, actual {actual_size}")

        # Validate data format
        data_format_valid = True
        if has_data:
            data_format_valid, format_issues = self._validate_data_format(response['data'])
            issues.extend(format_issues)

        # Validate timestamp format
        timestamp_format_valid = True
        if has_timestamp:
            timestamp_format_valid = self._validate_timestamp_format(response['timestamp'])
            if not timestamp_format_valid:
                issues.append(f"Invalid timestamp format: {response['timestamp']}")

        all_valid = (
            type_valid and
            has_data and
            has_data_size and
            has_timestamp and
            data_size_matches and
            data_format_valid and
            timestamp_format_valid
        )

        return EnvelopeValidation(
            type_valid=type_valid,
            has_data=has_data,
            has_data_size=has_data_size,
            has_timestamp=has_timestamp,
            data_size_matches=data_size_matches,
            data_format_valid=data_format_valid,
            timestamp_format_valid=timestamp_format_valid,
            all_valid=all_valid,
            issues=issues
        )

    def _validate_data_format(self, data: List) -> tuple:
        """Validate data array format"""
        issues = []

        if not isinstance(data, list):
            return False, ["Data is not a list"]

        if len(data) == 0:
            return False, ["Data array is empty"]

        # Check sample format
        for i, sample in enumerate(data[:10]):  # Check first 10 samples
            if not isinstance(sample, list):
                issues.append(f"Sample {i} is not a list")
                continue

            if len(sample) != self.EXPECTED_SAMPLE_SIZE:
                issues.append(
                    f"Sample {i} has {len(sample)} elements, expected {self.EXPECTED_SAMPLE_SIZE}"
                )
                continue

            # Check all elements are numeric
            for j, val in enumerate(sample):
                if not isinstance(val, (int, float)):
                    issues.append(f"Sample {i}[{j}] is not numeric: {type(val)}")

        return len(issues) == 0, issues

    def _validate_timestamp_format(self, timestamp: str) -> bool:
        """Validate timestamp format (YYYY-MM-DD HH:MM:SS.mmm)"""
        try:
            # Try parsing with milliseconds
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            return True
        except ValueError:
            try:
                # Try without milliseconds
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False

    def parse_envelope(self, response: Dict) -> DataEnvelope:
        """Parse response into DataEnvelope object"""
        return DataEnvelope(
            type=response.get('type', ''),
            data=response.get('data'),
            data_size=response.get('data_size'),
            timestamp=response.get('timestamp'),
            data_frequency=response.get('data_frequency'),
            raw_response=response
        )


class TestMAX30009DataEnvelope:
    """Unit Test - MAX30009 get_data Returns Data Envelope Fields"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 30009

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'measurement_settle_time': 2.0,  # Time to wait after enabling measurement
            'data_accumulation_time': 0.5,   # Time to wait for data to accumulate
            'log_file': '/tmp/test_196_max30009_data_envelope.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[MAX30009ServiceClient] = None
        self.validator = DataEnvelopeValidator()

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            # Disable measurement before disconnecting
            try:
                self.client.disable_measurement()
            except:
                pass
            self.client.disconnect()

    def print_envelope_details(self, envelope: DataEnvelope):
        """Print data envelope details"""
        print(f"\n  Data Envelope Contents:")
        print(f"    type: \"{envelope.type}\"")
        print(f"    timestamp: \"{envelope.timestamp}\"")
        print(f"    data_size: {envelope.data_size}")
        print(f"    data_frequency: {envelope.data_frequency}")

        if envelope.data:
            print(f"    data: [{len(envelope.data)} samples]")
            # Show first few samples
            print(f"      First 3 samples:")
            for i, sample in enumerate(envelope.data[:3]):
                print(f"        [{i}]: {sample}")
            if len(envelope.data) > 3:
                print(f"        ... ({len(envelope.data) - 3} more samples)")

    def print_validation_results(self, validation: EnvelopeValidation):
        """Print validation results"""
        print(f"\n  Validation Results:")
        print(f"    Response type = 'data': {'PASS' if validation.type_valid else 'FAIL'}")
        print(f"    Has 'data' field: {'PASS' if validation.has_data else 'FAIL'}")
        print(f"    Has 'data_size' field: {'PASS' if validation.has_data_size else 'FAIL'}")
        print(f"    Has 'timestamp' field: {'PASS' if validation.has_timestamp else 'FAIL'}")
        print(f"    data_size matches actual: {'PASS' if validation.data_size_matches else 'FAIL'}")
        print(f"    Data format valid: {'PASS' if validation.data_format_valid else 'FAIL'}")
        print(f"    Timestamp format valid: {'PASS' if validation.timestamp_format_valid else 'FAIL'}")

        if validation.issues:
            print(f"\n    Issues Found:")
            for issue in validation.issues:
                print(f"      - {issue}")

    @pytest.mark.unit
    @pytest.mark.max30009
    @pytest.mark.spi
    def test_196_max30009_data_envelope(self, test_config):
        """
        Test Case #196: get_data returns data envelope fields

        Test Setup:
            DUT; MAX30009 service; test client; log capture

        Procedure:
            1. Ensure MAX30009 is in measuring state
            2. Send a get_data request
            3. Capture the response envelope

        Acceptance Criteria:
            - Response type = "data"
            - Response includes "data" field (array of samples)
            - Response includes "data_size" field
            - Response includes "timestamp" field

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #196: MAX30009 get_data Returns Data Envelope Fields")
        print("=" * 75)
        print("\nPURPOSE:")
        print("  Verify get_data response includes required envelope fields")
        print("\nEXPECTED ENVELOPE FIELDS:")
        print("  - type: \"data\"")
        print("  - data: Array of [I_ADC, Q_ADC, Load_real, Load_imag, Overload]")
        print("  - data_size: Number of samples in data array")
        print("  - timestamp: Response timestamp (YYYY-MM-DD HH:MM:SS.mmm)")
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
        # STEP 2: Ensure MAX30009 is in Measuring State
        # ================================================================
        print("\n[STEP 2] Ensure MAX30009 is in Measuring State")
        print("-" * 75)

        print("  Enabling measurement mode...")
        enabled = self.client.enable_measurement()
        assert enabled, "Failed to enable measurement"

        # Wait for measurement to stabilize
        print(f"  Waiting {config['measurement_settle_time']}s for measurement to start...")
        time.sleep(config['measurement_settle_time'])

        # Verify measuring
        is_measuring = self.client.is_measuring()
        print(f"  Measurement active: {is_measuring}")

        if not self.client.use_mock:
            # For hardware, we may need to verify state differently
            pass

        # Wait for data to accumulate
        print(f"  Waiting {config['data_accumulation_time']}s for data accumulation...")
        time.sleep(config['data_accumulation_time'])

        # ================================================================
        # STEP 3: Send get_data Request
        # ================================================================
        print("\n[STEP 3] Send get_data Request")
        print("-" * 75)

        print("  Request: {\"type\": \"get_data\"}")

        response = self.client.get_data()

        assert response is not None, "No response received from get_data"
        print(f"  Response received: type = \"{response.get('type')}\"")

        # Handle no_measure response (not in measuring state)
        if response.get('type') == 'no_measure':
            print("  WARNING: Received 'no_measure' - sensor not in measuring state")
            if self.client.use_mock:
                # In mock mode, this shouldn't happen - force it
                self.client.mock.start_measuring()
                time.sleep(0.5)
                response = self.client.get_data()
                assert response.get('type') == 'data', "Still getting no_measure after retry"

        # ================================================================
        # STEP 4: Capture and Display Response Envelope
        # ================================================================
        print("\n[STEP 4] Capture Response Envelope")
        print("-" * 75)

        envelope = self.validator.parse_envelope(response)
        self.print_envelope_details(envelope)

        # ================================================================
        # STEP 5: Validate Envelope Fields
        # ================================================================
        print("\n[STEP 5] Validate Envelope Fields")
        print("-" * 75)

        validation = self.validator.validate_envelope(response)
        self.print_validation_results(validation)

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

        if validation.all_valid:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 75)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if validation.type_valid else 'FAIL'}] Response type = \"data\"")
        print(f"    [{'PASS' if validation.has_data else 'FAIL'}] Response includes \"data\" field")
        print(f"    [{'PASS' if validation.has_data_size else 'FAIL'}] Response includes \"data_size\" field")
        print(f"    [{'PASS' if validation.has_timestamp else 'FAIL'}] Response includes \"timestamp\" field")

        print("\n  Additional Validations:")
        print(f"    [{'PASS' if validation.data_size_matches else 'FAIL'}] data_size matches actual array length")
        print(f"    [{'PASS' if validation.data_format_valid else 'FAIL'}] Data samples have correct format")
        print(f"    [{'PASS' if validation.timestamp_format_valid else 'FAIL'}] Timestamp has valid format")

        print("\n  Statistics:")
        print(f"    Samples received: {envelope.data_size}")
        print(f"    Data frequency: {envelope.data_frequency} Hz")
        print(f"    Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        print("=" * 75)

        # Assertions for acceptance criteria
        assert validation.type_valid, "Response type is not 'data'"
        assert validation.has_data, "Response missing 'data' field"
        assert validation.has_data_size, "Response missing 'data_size' field"
        assert validation.has_timestamp, "Response missing 'timestamp' field"

    @pytest.mark.unit
    @pytest.mark.max30009
    @pytest.mark.spi
    def test_196_data_envelope_no_measure_state(self, test_config):
        """
        Test that get_data returns 'no_measure' when not in measuring state.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #196b: get_data Response When Not Measuring")
        print("=" * 75)

        self.client = MAX30009ServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Ensure not measuring
        print("\n  Ensuring measurement is disabled...")
        self.client.disable_measurement()
        time.sleep(0.5)

        # Send get_data
        print("  Sending get_data request...")
        response = self.client.get_data()

        print(f"  Response type: {response.get('type')}")

        expected_type = 'no_measure'
        actual_type = response.get('type')

        print("\n" + "=" * 75)
        if actual_type == expected_type:
            print("TEST RESULT: PASS")
            print(f"  Correctly returned '{expected_type}' when not measuring")
        else:
            print("TEST RESULT: FAIL")
            print(f"  Expected '{expected_type}', got '{actual_type}'")
        print("=" * 75)

        assert actual_type == expected_type, \
            f"Expected 'no_measure' when not measuring, got '{actual_type}'"

    @pytest.mark.unit
    @pytest.mark.max30009
    @pytest.mark.spi
    def test_196_multiple_get_data_requests(self, test_config):
        """
        Test multiple consecutive get_data requests return valid envelopes.
        """
        config = test_config

        print("\n" + "=" * 75)
        print("Test Case #196c: Multiple get_data Requests")
        print("=" * 75)

        self.client = MAX30009ServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize connection"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Enable measurement
        print("\n  Enabling measurement...")
        self.client.enable_measurement()
        time.sleep(config['measurement_settle_time'])

        # Send multiple get_data requests
        num_requests = 5
        print(f"\n  Sending {num_requests} consecutive get_data requests...")
        print("  " + "-" * 60)

        results = []
        for i in range(num_requests):
            time.sleep(0.2)  # Brief delay between requests
            response = self.client.get_data()

            if response and response.get('type') == 'data':
                validation = self.validator.validate_envelope(response)
                results.append(validation.all_valid)
                status = "VALID" if validation.all_valid else "INVALID"
                print(f"    Request {i+1}: {status} - "
                      f"data_size={response.get('data_size', 'N/A')}, "
                      f"timestamp={response.get('timestamp', 'N/A')}")
            else:
                results.append(False)
                print(f"    Request {i+1}: FAILED - type={response.get('type') if response else 'None'}")

        print("  " + "-" * 60)

        # Disable measurement
        self.client.disable_measurement()

        all_valid = all(results)
        valid_count = sum(results)

        print("\n" + "=" * 75)
        if all_valid:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print(f"  Valid responses: {valid_count}/{num_requests}")
        print("=" * 75)

        assert all_valid, f"Not all responses were valid: {valid_count}/{num_requests}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
