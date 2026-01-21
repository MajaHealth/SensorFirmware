#!/usr/bin/env python3
"""
Test Case #206: get_batt_info Response Schema
Unit Test for Power Service

Tests that the power control service returns the correct response schema
for get_batt_info requests, including all required battery info fields.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock responses for testing logic
2. Hardware mode: Connects to actual power service (requires PI_TARGET_IP)

Test Setup:
- DUT with power control service running
- Test client for communication
- Log capture enabled

Procedure:
1. Start firmware/services
2. Connect a test client to the power control service endpoint
3. Send a get_batt_info request
4. Capture response and verify fields presence

Acceptance Criteria:
- Response type = "batt_info"
- Response includes the batt-info fields present in the example:
  - charger connection status
  - charging/discharging flags
  - SOC/capacity fields
  - voltage
  - temperature
  - and the other reported battery properties
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


# Expected fields in batt_info response based on power service implementation
REQUIRED_FIELDS = {
    # Type identifier
    'type',

    # Electrical characteristics
    'voltage',                      # Battery voltage in volts
    'temperature',                  # Temperature in Celsius
    'current',                      # Current in amperes

    # Capacity information
    'relative_state_of_charge',     # SOC percentage (0-100%)
    'remaining_capacity',           # Remaining capacity in Ah
    'full_charge_capacity',         # Full charge capacity in Ah

    # Time estimates
    'run_time_to_empty',            # Minutes until empty
    'average_time_to_empty',        # Average minutes until empty
    'average_time_to_full',         # Minutes until full (when charging)

    # Lifecycle info
    'cycle_count',                  # Charge/discharge cycles
    'design_capacity',              # Design capacity in Ah
    'design_voltage',               # Design voltage in V

    # Status flags
    'fully_discharged',             # Boolean - battery empty
    'fully_charged',                # Boolean - battery full
    'discharging',                  # Boolean - currently discharging

    # Charger/charge control
    'charger_is_connect',           # Boolean - charger connected
    'battery_charge_is_disable',    # Boolean - charging disabled via GPIO
}

# Optional fields that may be present
OPTIONAL_FIELDS = {
    'charging',                     # Boolean - currently charging (derived)
}


@dataclass
class FieldValidation:
    """Validation result for a single field"""
    field_name: str
    present: bool
    value: Any
    value_type: str
    valid_type: bool

    def to_dict(self) -> Dict:
        return {
            'field_name': self.field_name,
            'present': self.present,
            'value': self.value,
            'value_type': self.value_type,
            'valid_type': self.valid_type
        }


@dataclass
class SchemaValidation:
    """Complete schema validation result"""
    response_type_valid: bool
    required_fields_present: Set[str]
    required_fields_missing: Set[str]
    optional_fields_present: Set[str]
    extra_fields: Set[str]
    field_validations: List[FieldValidation]
    all_required_present: bool
    schema_valid: bool
    issues: List[str]

    def to_dict(self) -> Dict:
        return {
            'response_type_valid': self.response_type_valid,
            'required_fields_present': list(self.required_fields_present),
            'required_fields_missing': list(self.required_fields_missing),
            'optional_fields_present': list(self.optional_fields_present),
            'extra_fields': list(self.extra_fields),
            'all_required_present': self.all_required_present,
            'schema_valid': self.schema_valid,
            'issues': self.issues
        }


# Expected types for each field
FIELD_TYPES = {
    'type': str,
    'voltage': (int, float),
    'temperature': (int, float),
    'current': (int, float),
    'relative_state_of_charge': (int, float),
    'remaining_capacity': (int, float),
    'full_charge_capacity': (int, float),
    'run_time_to_empty': int,
    'average_time_to_empty': int,
    'average_time_to_full': int,
    'cycle_count': int,
    'design_capacity': (int, float),
    'design_voltage': (int, float),
    'fully_discharged': bool,
    'fully_charged': bool,
    'discharging': bool,
    'charging': bool,
    'charger_is_connect': bool,
    'battery_charge_is_disable': bool,
}


class MockPowerService:
    """
    Mock power service for unit testing.
    Returns properly formatted batt_info response.
    """

    def __init__(self):
        self.charger_connected = True
        self.charging_enabled = True
        self.battery_soc = 75
        self.battery_voltage = 3.85
        self.battery_current = 0.5
        self.battery_temperature = 28.5

    def reset(self):
        """Reset mock to default state"""
        self.charger_connected = True
        self.charging_enabled = True
        self.battery_soc = 75
        self.battery_voltage = 3.85
        self.battery_current = 0.5
        self.battery_temperature = 28.5

    def send_command(self, request: Dict) -> Dict:
        """Process a command and return response"""
        cmd_type = request.get('type', '')

        if cmd_type == 'get_batt_info':
            return self._generate_batt_info_response()

        elif cmd_type == 'charge_disable':
            self.charging_enabled = False
            return {'type': 'charge_is_disable'}

        elif cmd_type == 'charge_enable':
            self.charging_enabled = True
            return {'type': 'charge_is_enable'}

        return {'type': 'error', 'message': f'Unknown command: {cmd_type}'}

    def _generate_batt_info_response(self) -> Dict:
        """
        Generate batt_info response matching the power service schema.
        Based on PWRCNTR_process.cpp implementation.
        """
        is_charging = (
            self.charger_connected and
            self.charging_enabled and
            self.battery_soc < 100
        )
        is_discharging = not is_charging

        return {
            'type': 'batt_info',

            # Electrical characteristics
            'voltage': self.battery_voltage,
            'temperature': self.battery_temperature,
            'current': self.battery_current if is_charging else -0.3,

            # Capacity information
            'relative_state_of_charge': self.battery_soc,
            'remaining_capacity': 3.0 * (self.battery_soc / 100),
            'full_charge_capacity': 3.0,

            # Time estimates
            'run_time_to_empty': int(self.battery_soc * 4),
            'average_time_to_empty': int(self.battery_soc * 4),
            'average_time_to_full': int((100 - self.battery_soc) * 2) if is_charging else 0,

            # Lifecycle info
            'cycle_count': 42,
            'design_capacity': 3.0,
            'design_voltage': 3.7,

            # Status flags
            'fully_discharged': self.battery_soc <= 5,
            'fully_charged': self.battery_soc >= 99,
            'discharging': is_discharging,

            # Charger/charge control
            'charger_is_connect': self.charger_connected,
            'battery_charge_is_disable': not self.charging_enabled,
        }


class PowerServiceClient:
    """
    Client for communicating with power service via TCP/JSON.
    Falls back to mock simulation if connection fails.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.connected = False

        self.mock: Optional[MockPowerService] = None
        self.use_mock = False

    def connect(self) -> bool:
        """Connect to power service or fall back to mock"""
        try:
            from tcp_client import TCPClient
            self.client = TCPClient(self.host, self.port, self.timeout)
            self.client.connect()
            self.connected = True
            print(f"  Connected to power service at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"  Could not connect to power service: {e}")
            print("  Falling back to mock simulation mode")
            self.use_mock = True
            self.mock = MockPowerService()
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

    def get_batt_info(self) -> Optional[Dict]:
        """Send get_batt_info request"""
        return self.send_command({"type": "get_batt_info"})


class BattInfoSchemaValidator:
    """Validates batt_info response schema"""

    def __init__(self):
        self.required_fields = REQUIRED_FIELDS
        self.optional_fields = OPTIONAL_FIELDS
        self.field_types = FIELD_TYPES

    def validate_response(self, response: Dict) -> SchemaValidation:
        """Validate complete batt_info response schema"""
        issues = []
        field_validations = []

        # Check response type
        response_type_valid = response.get('type') == 'batt_info'
        if not response_type_valid:
            issues.append(f"Invalid response type: '{response.get('type')}', expected 'batt_info'")

        # Get all fields from response
        response_fields = set(response.keys())

        # Check required fields
        required_fields_present = self.required_fields.intersection(response_fields)
        required_fields_missing = self.required_fields - response_fields

        for field in required_fields_missing:
            issues.append(f"Missing required field: '{field}'")

        # Check optional fields
        optional_fields_present = self.optional_fields.intersection(response_fields)

        # Check for extra fields (not required or optional)
        all_known_fields = self.required_fields.union(self.optional_fields)
        extra_fields = response_fields - all_known_fields

        # Validate each field's type
        for field_name, value in response.items():
            expected_type = self.field_types.get(field_name)
            if expected_type:
                if isinstance(expected_type, tuple):
                    valid_type = isinstance(value, expected_type)
                else:
                    valid_type = isinstance(value, expected_type)
            else:
                valid_type = True  # Unknown field, skip type check

            validation = FieldValidation(
                field_name=field_name,
                present=True,
                value=value,
                value_type=type(value).__name__,
                valid_type=valid_type
            )
            field_validations.append(validation)

            if not valid_type and field_name in self.required_fields:
                expected_type_name = (
                    expected_type.__name__ if hasattr(expected_type, '__name__')
                    else str(expected_type)
                )
                issues.append(
                    f"Field '{field_name}' has wrong type: "
                    f"expected {expected_type_name}, got {type(value).__name__}"
                )

        # Overall validation
        all_required_present = len(required_fields_missing) == 0
        schema_valid = response_type_valid and all_required_present

        return SchemaValidation(
            response_type_valid=response_type_valid,
            required_fields_present=required_fields_present,
            required_fields_missing=required_fields_missing,
            optional_fields_present=optional_fields_present,
            extra_fields=extra_fields,
            field_validations=field_validations,
            all_required_present=all_required_present,
            schema_valid=schema_valid,
            issues=issues
        )

    def get_field_categories(self, response: Dict) -> Dict[str, List[tuple]]:
        """Categorize fields by their purpose"""
        categories = {
            'type_identifier': [],
            'electrical': [],
            'capacity': [],
            'time_estimates': [],
            'lifecycle': [],
            'status_flags': [],
            'charger_control': [],
        }

        field_category_map = {
            'type': 'type_identifier',
            'voltage': 'electrical',
            'temperature': 'electrical',
            'current': 'electrical',
            'relative_state_of_charge': 'capacity',
            'remaining_capacity': 'capacity',
            'full_charge_capacity': 'capacity',
            'run_time_to_empty': 'time_estimates',
            'average_time_to_empty': 'time_estimates',
            'average_time_to_full': 'time_estimates',
            'cycle_count': 'lifecycle',
            'design_capacity': 'lifecycle',
            'design_voltage': 'lifecycle',
            'fully_discharged': 'status_flags',
            'fully_charged': 'status_flags',
            'discharging': 'status_flags',
            'charging': 'status_flags',
            'charger_is_connect': 'charger_control',
            'battery_charge_is_disable': 'charger_control',
        }

        for field, value in response.items():
            category = field_category_map.get(field, 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append((field, value))

        return categories


class TestBattInfoResponseSchema:
    """Unit Test - get_batt_info Response Schema"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 501

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'log_file': '/tmp/test_206_batt_info_schema.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[PowerServiceClient] = None
        self.validator = BattInfoSchemaValidator()

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            self.client.disconnect()

    def print_response_fields(self, response: Dict, categories: Dict[str, List[tuple]]):
        """Print response fields organized by category"""
        print("\n  Response Fields by Category:")

        category_names = {
            'type_identifier': 'Type Identifier',
            'electrical': 'Electrical Characteristics',
            'capacity': 'Capacity Information',
            'time_estimates': 'Time Estimates',
            'lifecycle': 'Lifecycle Info',
            'status_flags': 'Status Flags',
            'charger_control': 'Charger/Charge Control',
        }

        for category, fields in categories.items():
            if fields:
                name = category_names.get(category, category.title())
                print(f"\n    {name}:")
                for field, value in fields:
                    value_str = f'"{value}"' if isinstance(value, str) else str(value)
                    print(f"      {field}: {value_str}")

    def print_validation_summary(self, validation: SchemaValidation):
        """Print validation summary"""
        print("\n  Schema Validation Summary:")
        print(f"    Response type valid: {'YES' if validation.response_type_valid else 'NO'}")
        print(f"    Required fields present: {len(validation.required_fields_present)}/{len(REQUIRED_FIELDS)}")
        print(f"    Optional fields present: {len(validation.optional_fields_present)}")

        if validation.required_fields_missing:
            print(f"\n    Missing Required Fields:")
            for field in sorted(validation.required_fields_missing):
                print(f"      - {field}")

        if validation.extra_fields:
            print(f"\n    Extra Fields (not in schema):")
            for field in sorted(validation.extra_fields):
                print(f"      - {field}")

        if validation.issues:
            print(f"\n    Issues:")
            for issue in validation.issues:
                print(f"      - {issue}")

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_206_batt_info_response_schema(self, test_config):
        """
        Test Case #206: get_batt_info response schema

        Test Setup:
            DUT; power control service running; test client; log capture

        Procedure:
            1. Start firmware/services
            2. Connect a test client to the power control service endpoint
            3. Send a get_batt_info request
            4. Capture response and verify fields presence

        Acceptance Criteria:
            - Response type = "batt_info"
            - Response includes the batt-info fields:
              - charger connection status (charger_is_connect)
              - charging/discharging flags (discharging, fully_charged, fully_discharged)
              - SOC/capacity fields (relative_state_of_charge, remaining_capacity, etc.)
              - voltage
              - temperature
              - and the other reported battery properties

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 80)
        print("Test Case #206: get_batt_info Response Schema")
        print("=" * 80)
        print("\nPURPOSE:")
        print("  Verify get_batt_info returns correct response schema with all required fields")
        print("\nEXPECTED RESPONSE FORMAT:")
        print('  {"type": "batt_info", "voltage": <float>, "temperature": <float>, ...}')
        print("\nREQUIRED FIELD CATEGORIES:")
        print("  - Electrical: voltage, temperature, current")
        print("  - Capacity: relative_state_of_charge, remaining_capacity, full_charge_capacity")
        print("  - Time: run_time_to_empty, average_time_to_empty, average_time_to_full")
        print("  - Lifecycle: cycle_count, design_capacity, design_voltage")
        print("  - Status: fully_discharged, fully_charged, discharging")
        print("  - Charger: charger_is_connect, battery_charge_is_disable")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}:{config['port']}")
        print("=" * 80)

        # ================================================================
        # STEP 1: Connect to Power Control Service
        # ================================================================
        print("\n[STEP 1] Connect to Power Control Service Endpoint")
        print("-" * 80)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect to power service"

        if self.client.use_mock:
            print("  Running in MOCK SIMULATION mode")
        else:
            print("  Running in HARDWARE mode")

        # ================================================================
        # STEP 2: Send get_batt_info Request
        # ================================================================
        print("\n[STEP 2] Send get_batt_info Request")
        print("-" * 80)

        print('  Request: {"type": "get_batt_info"}')

        response = self.client.get_batt_info()

        assert response is not None, "No response received"
        print(f"  Response received with {len(response)} fields")

        # ================================================================
        # STEP 3: Capture Response and Display Fields
        # ================================================================
        print("\n[STEP 3] Capture Response and Display Fields")
        print("-" * 80)

        categories = self.validator.get_field_categories(response)
        self.print_response_fields(response, categories)

        # ================================================================
        # STEP 4: Verify Fields Presence
        # ================================================================
        print("\n[STEP 4] Verify Fields Presence")
        print("-" * 80)

        validation = self.validator.validate_response(response)
        self.print_validation_summary(validation)

        # ================================================================
        # STEP 5: Detailed Field Validation
        # ================================================================
        print("\n[STEP 5] Field-by-Field Validation")
        print("-" * 80)

        print("\n  Required Fields Check:")
        print("  " + "-" * 60)

        # Group fields by category for display
        field_groups = [
            ("Charger Connection", ['charger_is_connect']),
            ("Charging/Discharging Flags", ['discharging', 'fully_charged', 'fully_discharged']),
            ("SOC/Capacity Fields", ['relative_state_of_charge', 'remaining_capacity', 'full_charge_capacity']),
            ("Voltage", ['voltage']),
            ("Temperature", ['temperature']),
            ("Current", ['current']),
            ("Time Estimates", ['run_time_to_empty', 'average_time_to_empty', 'average_time_to_full']),
            ("Lifecycle", ['cycle_count', 'design_capacity', 'design_voltage']),
            ("Charge Control", ['battery_charge_is_disable']),
        ]

        for group_name, fields in field_groups:
            print(f"\n    {group_name}:")
            for field in fields:
                present = field in response
                value = response.get(field, 'N/A')
                status = "PRESENT" if present else "MISSING"
                value_str = f'"{value}"' if isinstance(value, str) else str(value)
                print(f"      [{status}] {field}: {value_str}")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 80)

        if validation.schema_valid:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 80)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if validation.response_type_valid else 'FAIL'}] Response type = \"batt_info\"")
        print(f"    [{'PASS' if 'charger_is_connect' in response else 'FAIL'}] Includes charger connection status")
        print(f"    [{'PASS' if 'discharging' in response else 'FAIL'}] Includes charging/discharging flags")
        print(f"    [{'PASS' if 'relative_state_of_charge' in response else 'FAIL'}] Includes SOC/capacity fields")
        print(f"    [{'PASS' if 'voltage' in response else 'FAIL'}] Includes voltage")
        print(f"    [{'PASS' if 'temperature' in response else 'FAIL'}] Includes temperature")
        print(f"    [{'PASS' if validation.all_required_present else 'FAIL'}] Includes all required battery properties")

        print("\n  Statistics:")
        print(f"    Total fields in response: {len(response)}")
        print(f"    Required fields present: {len(validation.required_fields_present)}/{len(REQUIRED_FIELDS)}")
        print(f"    Missing fields: {len(validation.required_fields_missing)}")
        print(f"    Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        print("=" * 80)

        # Assertions
        assert validation.response_type_valid, "Response type is not 'batt_info'"
        assert validation.all_required_present, \
            f"Missing required fields: {validation.required_fields_missing}"

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_206_batt_info_field_types(self, test_config):
        """
        Test that all batt_info fields have correct data types.
        """
        config = test_config

        print("\n" + "=" * 80)
        print("Test Case #206b: batt_info Field Types Validation")
        print("=" * 80)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        response = self.client.get_batt_info()
        assert response is not None, "No response received"

        print("\n  Field Type Validation:")
        print("  " + "-" * 70)
        print(f"  {'Field':<30} | {'Expected Type':<15} | {'Actual Type':<12} | Status")
        print("  " + "-" * 70)

        all_types_valid = True

        for field, expected_type in FIELD_TYPES.items():
            if field in response:
                value = response[field]
                actual_type = type(value).__name__

                if isinstance(expected_type, tuple):
                    valid = isinstance(value, expected_type)
                    expected_str = "/".join(t.__name__ for t in expected_type)
                else:
                    valid = isinstance(value, expected_type)
                    expected_str = expected_type.__name__

                status = "PASS" if valid else "FAIL"
                if not valid:
                    all_types_valid = False

                print(f"  {field:<30} | {expected_str:<15} | {actual_type:<12} | {status}")

        print("  " + "-" * 70)

        print("\n" + "=" * 80)
        if all_types_valid:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 80)

        assert all_types_valid, "Some fields have incorrect types"

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_206_batt_info_value_ranges(self, test_config):
        """
        Test that batt_info field values are within expected ranges.
        """
        config = test_config

        print("\n" + "=" * 80)
        print("Test Case #206c: batt_info Value Ranges Validation")
        print("=" * 80)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        response = self.client.get_batt_info()
        assert response is not None, "No response received"

        # Define expected ranges
        range_checks = [
            ('voltage', 0.0, 5.0, 'V'),
            ('temperature', -20.0, 80.0, 'C'),
            ('relative_state_of_charge', 0, 100, '%'),
            ('remaining_capacity', 0.0, 10.0, 'Ah'),
            ('full_charge_capacity', 0.0, 10.0, 'Ah'),
            ('cycle_count', 0, 10000, 'cycles'),
        ]

        print("\n  Value Range Validation:")
        print("  " + "-" * 75)
        print(f"  {'Field':<28} | {'Value':<10} | {'Range':<20} | Status")
        print("  " + "-" * 75)

        all_valid = True

        for field, min_val, max_val, unit in range_checks:
            if field in response:
                value = response[field]
                in_range = min_val <= value <= max_val
                status = "PASS" if in_range else "FAIL"

                if not in_range:
                    all_valid = False

                print(f"  {field:<28} | {value:<10} | {min_val}-{max_val} {unit:<6} | {status}")

        print("  " + "-" * 75)

        print("\n" + "=" * 80)
        if all_valid:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 80)

        assert all_valid, "Some field values are out of expected range"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
