#!/usr/bin/env python3
"""
MAX30009 (ICG/Bioimpedance) Comprehensive Test Suite
For Raspberry Pi - Port 30009

This script tests all MAX30009 functionality and generates detailed CSV reports.
Updated for new parameter names: stimulate_table_index (7 values) and stimulate_frequency (17 values)
"""

import socket
import json
import time
import csv
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import traceback

# ============================================================================
# Configuration
# ============================================================================

HOST = "localhost"
PORT = 30009
TIMEOUT = 10  # seconds

# Updated MAX30009 parameters based on new firmware
FREQUENCY_POINTS = [25, 100, 200, 500, 1000, 5000, 10000, 20000, 50000,
                   100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000]
FREQUENCY_POINTS_COUNT = 17

# Current table: [description, gain_notation]
CURRENT_TABLE = [
    ["64uA", "x10"],
    ["128uA", "x10"],
    ["256uA", "x5"],
    ["640uA", "x2"],
    ["640uA", "x5"],
    ["1.28mA", "x2"],
    ["1.28mA", "x5"]
]
CURRENT_POINTS_COUNT = 7

# External MUX states
MUX_STATES = {
    0: "ALL_OFF",
    1: "4_WIRE",
    2: "2_WIRE",
    3: "CALIBRATE",
    4: "COLE_COLE"
}

# Measure frequency range
MIN_MEASURE_FREQ = 1
MAX_MEASURE_FREQ = 500

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TestResult:
    """Represents a single test result"""
    timestamp: str
    test_suite: str
    test_name: str
    test_id: str
    status: str  # PASS, FAIL, ERROR, SKIP
    duration_ms: float
    expected: str
    actual: str
    error_message: str
    details: str

    def to_dict(self):
        return asdict(self)


class TestReporter:
    """Handles test result collection and CSV report generation"""

    def __init__(self, report_filename: str):
        self.report_filename = report_filename
        self.results: List[TestResult] = []
        self.start_time = datetime.now()

    def add_result(self, result: TestResult):
        self.results.append(result)

    def get_summary(self) -> Dict[str, int]:
        summary = {
            "PASS": 0,
            "FAIL": 0,
            "ERROR": 0,
            "SKIP": 0,
            "TOTAL": len(self.results)
        }
        for result in self.results:
            summary[result.status] = summary.get(result.status, 0) + 1
        return summary

    def save_csv(self):
        """Save results to CSV file"""
        if not self.results:
            logging.warning("No test results to save")
            return

        fieldnames = list(self.results[0].to_dict().keys())

        with open(self.report_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())

        logging.info(f"Test report saved to: {self.report_filename}")

    def print_summary(self):
        """Print test summary to console and log"""
        summary = self.get_summary()
        duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests:  {summary['TOTAL']}")
        print(f"Passed:       {summary['PASS']} ({summary['PASS']/summary['TOTAL']*100:.1f}%)")
        print(f"Failed:       {summary['FAIL']}")
        print(f"Errors:       {summary['ERROR']}")
        print(f"Skipped:      {summary['SKIP']}")
        print(f"Duration:     {duration:.2f} seconds")
        print(f"Report:       {self.report_filename}")
        print("="*70)

        logging.info(f"Test Summary: {summary['PASS']}/{summary['TOTAL']} passed in {duration:.2f}s")


# ============================================================================
# MAX30009 Client
# ============================================================================

class MAX30009Client:
    """Client for communicating with MAX30009 TCP server"""

    def __init__(self, host: str, port: int, timeout: int = 10):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_command(self, command_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send JSON command to MAX30009 and return response

        Returns:
            Dict with response, or None if error
        """
        sock = None
        try:
            logging.debug(f"Connecting to {self.host}:{self.port}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            # Receive welcome message
            welcome = sock.recv(1024)
            logging.debug(f"Server welcome: {welcome.decode().strip()}")

            # Send command
            cmd_str = json.dumps(command_dict)
            logging.debug(f"Sending command: {cmd_str}")
            sock.send((cmd_str + "\n").encode())

            # Receive response
            response_data = sock.recv(65536)
            response_str = response_data.decode().strip()
            logging.debug(f"Received response: {response_str[:200]}...")

            response = json.loads(response_str)
            return response

        except socket.timeout:
            logging.error(f"Socket timeout after {self.timeout}s")
            return None
        except ConnectionRefusedError:
            logging.error(f"Connection refused to {self.host}:{self.port}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in send_command: {e}")
            logging.error(traceback.format_exc())
            return None
        finally:
            if sock:
                sock.close()

    def is_available(self) -> bool:
        """Check if MAX30009 service is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.host, self.port))
            sock.close()
            return True
        except:
            return False


# ============================================================================
# Test Suites
# ============================================================================

class MAX30009TestSuite:
    """Base class for MAX30009 test suites"""

    def __init__(self, client: MAX30009Client, reporter: TestReporter):
        self.client = client
        self.reporter = reporter
        self.suite_name = self.__class__.__name__

    def run_test(self, test_name: str, test_id: str, test_func) -> TestResult:
        """Execute a single test and record result"""
        logging.info(f"Running: {test_id} - {test_name}")
        start_time = time.time()

        try:
            result = test_func()
            duration_ms = (time.time() - start_time) * 1000

            test_result = TestResult(
                timestamp=datetime.now().isoformat(),
                test_suite=self.suite_name,
                test_name=test_name,
                test_id=test_id,
                status=result.get("status", "ERROR"),
                duration_ms=duration_ms,
                expected=result.get("expected", ""),
                actual=result.get("actual", ""),
                error_message=result.get("error", ""),
                details=result.get("details", "")
            )

            logging.info(f"  Result: {test_result.status} ({duration_ms:.1f}ms)")
            if test_result.error_message:
                logging.warning(f"  Error: {test_result.error_message}")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            test_result = TestResult(
                timestamp=datetime.now().isoformat(),
                test_suite=self.suite_name,
                test_name=test_name,
                test_id=test_id,
                status="ERROR",
                duration_ms=duration_ms,
                expected="No exception",
                actual=str(e),
                error_message=str(e),
                details=traceback.format_exc()
            )
            logging.error(f"  Exception: {e}")
            logging.debug(traceback.format_exc())

        self.reporter.add_result(test_result)
        return test_result

    def run_all(self):
        """Override this method in subclasses"""
        raise NotImplementedError


# ============================================================================
# Test Suite 1: Connection Tests
# ============================================================================

class ConnectionTests(MAX30009TestSuite):
    """Test basic TCP connection and error handling"""

    def test_connection_establishment(self):
        """Test basic connection to MAX30009 service"""
        response = self.client.send_command({"type": "settings", "power_enable": False})

        if response is None:
            return {
                "status": "FAIL",
                "expected": "Valid JSON response",
                "actual": "No response",
                "error": "Could not connect to MAX30009 service"
            }

        return {
            "status": "PASS",
            "expected": "Connection successful",
            "actual": "Connection successful",
            "details": f"Response type: {response.get('type', 'unknown')}"
        }

    def test_malformed_json(self):
        """Test server response to malformed JSON"""
        # Can't test this directly with json.dumps, so we skip
        return {
            "status": "SKIP",
            "expected": "error JSON response",
            "actual": "Cannot send malformed JSON via json library",
            "details": "Test requires raw socket manipulation"
        }

    def test_missing_type_field(self):
        """Test server response when 'type' field is missing"""
        response = self.client.send_command({"some_field": "some_value"})

        if response and response.get("type") == "error JSON":
            return {
                "status": "PASS",
                "expected": '{"type":"error JSON"}',
                "actual": json.dumps(response),
                "details": "Server correctly rejected missing type field"
            }
        else:
            return {
                "status": "FAIL",
                "expected": '{"type":"error JSON"}',
                "actual": json.dumps(response) if response else "None",
                "error": "Server did not return error for missing type"
            }

    def test_unknown_command_type(self):
        """Test server response to unknown command type"""
        response = self.client.send_command({"type": "unknown_command_xyz"})

        if response and response.get("type") == "error JSON":
            return {
                "status": "PASS",
                "expected": '{"type":"error JSON"}',
                "actual": json.dumps(response),
                "details": "Server correctly rejected unknown command"
            }
        else:
            return {
                "status": "FAIL",
                "expected": '{"type":"error JSON"}',
                "actual": json.dumps(response) if response else "None",
                "error": "Server did not return error for unknown command"
            }

    def run_all(self):
        """Run all connection tests"""
        logging.info(f"\n{'='*70}")
        logging.info(f"Starting {self.suite_name}")
        logging.info(f"{'='*70}")

        self.run_test("Connection Establishment", "CONN-001",
                     self.test_connection_establishment)
        self.run_test("Malformed JSON", "CONN-002",
                     self.test_malformed_json)
        self.run_test("Missing Type Field", "CONN-003",
                     self.test_missing_type_field)
        self.run_test("Unknown Command Type", "CONN-004",
                     self.test_unknown_command_type)


# ============================================================================
# Test Suite 2: Settings Configuration Tests
# ============================================================================

class SettingsConfigTests(MAX30009TestSuite):
    """Test MAX30009 settings configuration"""

    def test_power_on_minimal(self):
        """Test power on with minimal settings"""
        response = self.client.send_command({"type": "settings", "power_enable": True})

        if response and response.get("type") == "actual_settings" and response.get("power_enable") == True:
            return {
                "status": "PASS",
                "expected": "power_enable=true",
                "actual": f"power_enable={response.get('power_enable')}",
                "details": json.dumps(response)
            }
        else:
            return {
                "status": "FAIL",
                "expected": "power_enable=true",
                "actual": json.dumps(response) if response else "None",
                "error": "Power enable failed"
            }

    def test_enable_measurement_basic(self):
        """Test enabling measurement with basic configuration"""
        response = self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "stimulate_frequency": 5,
            "measure_frequency": 100,
            "stimulate_table_index": 2
        })

        if response and response.get("measure_enable") == True:
            return {
                "status": "PASS",
                "expected": "measure_enable=true",
                "actual": f"measure_enable={response.get('measure_enable')}",
                "details": json.dumps(response)
            }
        else:
            return {
                "status": "FAIL",
                "expected": "measure_enable=true",
                "actual": json.dumps(response) if response else "None",
                "error": "Measurement enable failed"
            }

    def test_all_stimulate_frequencies(self):
        """Test all 17 stimulation frequency indices"""
        results = []

        for freq_idx in range(FREQUENCY_POINTS_COUNT):
            response = self.client.send_command({
                "type": "settings",
                "power_enable": True,
                "measure_enable": True,
                "stimulate_frequency": freq_idx,
                "measure_frequency": 100,
                "stimulate_table_index": 2
            })

            if response and response.get("stimulate_frequency") == freq_idx:
                results.append(f"Index {freq_idx} ({FREQUENCY_POINTS[freq_idx]} Hz): PASS")
            else:
                results.append(f"Index {freq_idx}: FAIL (got {response.get('stimulate_frequency') if response else 'None'})")

        # Check if all passed
        failed = [r for r in results if "FAIL" in r]

        if not failed:
            return {
                "status": "PASS",
                "expected": f"All {FREQUENCY_POINTS_COUNT} frequencies accepted",
                "actual": "All frequencies accepted",
                "details": "; ".join(results)
            }
        else:
            return {
                "status": "FAIL",
                "expected": f"All {FREQUENCY_POINTS_COUNT} frequencies accepted",
                "actual": f"{len(failed)} frequencies failed",
                "error": "; ".join(failed),
                "details": "; ".join(results)
            }

    def test_all_stimulate_table_indices(self):
        """Test all 7 stimulation current table indices"""
        results = []

        for table_idx in range(CURRENT_POINTS_COUNT):
            response = self.client.send_command({
                "type": "settings",
                "power_enable": True,
                "measure_enable": True,
                "stimulate_frequency": 5,
                "measure_frequency": 100,
                "stimulate_table_index": table_idx
            })

            current_desc = CURRENT_TABLE[table_idx][0]
            current_gain = CURRENT_TABLE[table_idx][1]

            if response and response.get("stimulate_table_index") == table_idx:
                results.append(f"Index {table_idx} ({current_desc} {current_gain}): PASS")
            else:
                results.append(f"Index {table_idx}: FAIL (got {response.get('stimulate_table_index') if response else 'None'})")

        failed = [r for r in results if "FAIL" in r]

        if not failed:
            return {
                "status": "PASS",
                "expected": f"All {CURRENT_POINTS_COUNT} table indices accepted",
                "actual": "All table indices accepted",
                "details": "; ".join(results)
            }
        else:
            return {
                "status": "FAIL",
                "expected": f"All {CURRENT_POINTS_COUNT} table indices accepted",
                "actual": f"{len(failed)} indices failed",
                "error": "; ".join(failed),
                "details": "; ".join(results)
            }

    def test_measure_frequency_range(self):
        """Test measure frequency range boundaries"""
        test_freqs = [1, 10, 50, 100, 250, 500]
        results = []

        for freq in test_freqs:
            response = self.client.send_command({
                "type": "settings",
                "power_enable": True,
                "measure_enable": True,
                "measure_frequency": freq
            })

            actual_freq = response.get("measure_frequency") if response else None
            results.append(f"{freq} Hz -> {actual_freq} Hz")

        return {
            "status": "PASS",
            "expected": "Frequencies accepted (may be adjusted)",
            "actual": "Frequencies processed",
            "details": "; ".join(results)
        }

    def test_invalid_frequency_clamping_low(self):
        """Test measure frequency clamping at lower bound"""
        response = self.client.send_command({
            "type": "settings",
            "measure_frequency": 0
        })

        actual = response.get("measure_frequency") if response else None

        if actual and actual >= MIN_MEASURE_FREQ:
            return {
                "status": "PASS",
                "expected": f"Clamped to >= {MIN_MEASURE_FREQ} Hz",
                "actual": f"Set to {actual} Hz",
                "details": "Firmware correctly clamped frequency"
            }
        else:
            return {
                "status": "FAIL",
                "expected": f">= {MIN_MEASURE_FREQ} Hz",
                "actual": str(actual),
                "error": "Frequency not properly clamped"
            }

    def test_invalid_frequency_clamping_high(self):
        """Test measure frequency clamping at upper bound"""
        response = self.client.send_command({
            "type": "settings",
            "measure_frequency": 10000
        })

        actual = response.get("measure_frequency") if response else None

        if actual and actual <= MAX_MEASURE_FREQ:
            return {
                "status": "PASS",
                "expected": f"Clamped to <= {MAX_MEASURE_FREQ} Hz",
                "actual": f"Set to {actual} Hz",
                "details": "Firmware correctly clamped frequency"
            }
        else:
            return {
                "status": "FAIL",
                "expected": f"<= {MAX_MEASURE_FREQ} Hz",
                "actual": str(actual),
                "error": "Frequency not properly clamped"
            }

    def test_external_mux_states(self):
        """Test all 5 external MUX states"""
        results = []

        for state_val, state_name in MUX_STATES.items():
            response = self.client.send_command({
                "type": "settings",
                "power_enable": True,
                "ext_MUX_state": state_val
            })

            if response and response.get("ext_MUX_state") == state_val:
                results.append(f"{state_name} ({state_val}): PASS")
            else:
                results.append(f"{state_name} ({state_val}): FAIL")

        failed = [r for r in results if "FAIL" in r]

        if not failed:
            return {
                "status": "PASS",
                "expected": "All 5 MUX states accepted",
                "actual": "All MUX states accepted",
                "details": "; ".join(results)
            }
        else:
            return {
                "status": "FAIL",
                "expected": "All 5 MUX states accepted",
                "actual": f"{len(failed)} states failed",
                "error": "; ".join(failed)
            }

    def test_partial_settings_update(self):
        """Test partial settings update (only change one field)"""
        # First set full config
        self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 100
        })

        # Now change only measure_enable
        response = self.client.send_command({
            "type": "settings",
            "measure_enable": False
        })

        if response and response.get("measure_enable") == False and response.get("power_enable") == True:
            return {
                "status": "PASS",
                "expected": "measure_enable=false, power_enable=true",
                "actual": f"measure_enable={response.get('measure_enable')}, power_enable={response.get('power_enable')}",
                "details": "Partial update preserved other settings"
            }
        else:
            return {
                "status": "FAIL",
                "expected": "measure_enable=false, power_enable=true",
                "actual": json.dumps(response) if response else "None",
                "error": "Partial update failed"
            }

    def test_complete_configuration(self):
        """Test complete configuration with all parameters"""
        response = self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "stimulate_frequency": 8,
            "measure_frequency": 250,
            "stimulate_table_index": 3,
            "out_LP_filter": 2,
            "out_HP_filter": 1,
            "ext_MUX_state": 1
        })

        if response and response.get("type") == "actual_settings":
            checks = [
                ("power_enable", True),
                ("measure_enable", True),
                ("stimulate_frequency", 8),
                ("stimulate_table_index", 3),
                ("ext_MUX_state", 1)
            ]

            failed_checks = []
            for key, expected_val in checks:
                if response.get(key) != expected_val:
                    failed_checks.append(f"{key}: expected {expected_val}, got {response.get(key)}")

            if not failed_checks:
                return {
                    "status": "PASS",
                    "expected": "All parameters set correctly",
                    "actual": "All parameters verified",
                    "details": json.dumps(response)
                }
            else:
                return {
                    "status": "FAIL",
                    "expected": "All parameters correct",
                    "actual": "; ".join(failed_checks),
                    "error": "Some parameters not set correctly"
                }
        else:
            return {
                "status": "FAIL",
                "expected": "actual_settings response",
                "actual": json.dumps(response) if response else "None",
                "error": "Invalid response"
            }

    def run_all(self):
        """Run all settings configuration tests"""
        logging.info(f"\n{'='*70}")
        logging.info(f"Starting {self.suite_name}")
        logging.info(f"{'='*70}")

        self.run_test("Power On (Minimal)", "SETT-001",
                     self.test_power_on_minimal)
        self.run_test("Enable Measurement (Basic)", "SETT-002",
                     self.test_enable_measurement_basic)
        self.run_test("All Stimulate Frequencies", "SETT-003",
                     self.test_all_stimulate_frequencies)
        self.run_test("All Stimulate Table Indices", "SETT-004",
                     self.test_all_stimulate_table_indices)
        self.run_test("Measure Frequency Range", "SETT-005",
                     self.test_measure_frequency_range)
        self.run_test("Invalid Frequency Clamping (Low)", "SETT-006",
                     self.test_invalid_frequency_clamping_low)
        self.run_test("Invalid Frequency Clamping (High)", "SETT-007",
                     self.test_invalid_frequency_clamping_high)
        self.run_test("External MUX States", "SETT-008",
                     self.test_external_mux_states)
        self.run_test("Partial Settings Update", "SETT-009",
                     self.test_partial_settings_update)
        self.run_test("Complete Configuration", "SETT-010",
                     self.test_complete_configuration)


# ============================================================================
# Test Suite 3: Data Retrieval Tests
# ============================================================================

class DataRetrievalTests(MAX30009TestSuite):
    """Test data retrieval from MAX30009"""

    def test_get_data_when_disabled(self):
        """Test get_data when measurement is disabled"""
        # Disable measurement
        self.client.send_command({
            "type": "settings",
            "measure_enable": False
        })

        # Try to get data
        response = self.client.send_command({"type": "get_data"})

        if response and response.get("type") == "data":
            data_size = response.get("data_size", 0)
            return {
                "status": "PASS",
                "expected": "Empty or minimal data",
                "actual": f"data_size={data_size}",
                "details": "Response received while disabled"
            }
        else:
            return {
                "status": "FAIL",
                "expected": "data response",
                "actual": json.dumps(response) if response else "None",
                "error": "No valid response"
            }

    def test_get_data_when_enabled(self):
        """Test get_data when measurement is enabled"""
        # Enable measurement
        self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 100
        })

        # Wait for data to accumulate
        logging.info("  Waiting 2 seconds for data accumulation...")
        time.sleep(2)

        # Get data
        response = self.client.send_command({"type": "get_data"})

        if response and response.get("type") == "data":
            data_size = response.get("data_size", 0)
            has_timestamp = "timestamp" in response
            has_data_array = "data" in response and isinstance(response["data"], list)

            if data_size > 0 and has_timestamp and has_data_array:
                return {
                    "status": "PASS",
                    "expected": "Valid data response with samples",
                    "actual": f"data_size={data_size}, timestamp={response.get('timestamp')[:19]}",
                    "details": f"Frequency: {response.get('data_frequency')} Hz"
                }
            else:
                return {
                    "status": "FAIL",
                    "expected": "Data with samples",
                    "actual": f"data_size={data_size}",
                    "error": "No data received after 2 seconds"
                }
        else:
            return {
                "status": "FAIL",
                "expected": "data response",
                "actual": json.dumps(response) if response else "None",
                "error": "Invalid response"
            }

    def test_verify_data_point_format(self):
        """Test data point format: [Load_real, Load_mag, Load_imag, Load_angle, overload]"""
        # Enable measurement
        self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 100
        })

        time.sleep(2)
        response = self.client.send_command({"type": "get_data"})

        if response and "data" in response and len(response["data"]) > 0:
            data_points = response["data"]

            # Check first non-sync data point
            valid_points = [pt for pt in data_points if pt[0] != -99999]

            if valid_points:
                first_point = valid_points[0]

                if len(first_point) == 5:
                    return {
                        "status": "PASS",
                        "expected": "5-element array [Load_real, Load_mag, Load_imag, Load_angle, overload]",
                        "actual": f"5 elements: {first_point}",
                        "details": f"Sample point verified: {first_point}"
                    }
                else:
                    return {
                        "status": "FAIL",
                        "expected": "5 elements",
                        "actual": f"{len(first_point)} elements",
                        "error": f"Incorrect format: {first_point}"
                    }
            else:
                return {
                    "status": "FAIL",
                    "expected": "Data points",
                    "actual": "Only sync markers found",
                    "error": "No regular data points"
                }
        else:
            return {
                "status": "FAIL",
                "expected": "Data array",
                "actual": "No data",
                "error": "No data received"
            }

    def test_sync_marker_detection(self):
        """Test sync marker presence and format"""
        # Enable measurement
        self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 100
        })

        # Wait for sync markers (>1 second)
        logging.info("  Waiting 3 seconds for sync markers...")
        time.sleep(3)

        response = self.client.send_command({"type": "get_data"})

        if response and "data" in response:
            data_points = response["data"]

            # Find sync markers (Load_real = -99999)
            sync_markers = [pt for pt in data_points if pt[0] == -99999]

            if len(sync_markers) >= 2:
                sync_nums = [pt[1] for pt in sync_markers]
                return {
                    "status": "PASS",
                    "expected": "At least 2 sync markers in 3 seconds",
                    "actual": f"Found {len(sync_markers)} sync markers: {sync_nums}",
                    "details": f"Sync marker format verified"
                }
            elif len(sync_markers) == 1:
                return {
                    "status": "PASS",
                    "expected": "At least 1 sync marker",
                    "actual": f"Found 1 sync marker: {sync_markers[0][1]}",
                    "details": "May need longer wait for multiple markers"
                }
            else:
                return {
                    "status": "FAIL",
                    "expected": "At least 1 sync marker",
                    "actual": "No sync markers found",
                    "error": f"Total data points: {len(data_points)}"
                }
        else:
            return {
                "status": "FAIL",
                "expected": "Data with sync markers",
                "actual": "No data",
                "error": "No data received"
            }

    def test_continuous_data_polling(self):
        """Test continuous data polling (10 iterations)"""
        # Enable measurement
        self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 100
        })

        poll_results = []
        errors = []

        for i in range(10):
            time.sleep(1)
            response = self.client.send_command({"type": "get_data"})

            if response and response.get("type") == "data":
                data_size = response.get("data_size", 0)
                poll_results.append(data_size)
                logging.info(f"    Poll {i+1}: {data_size} samples")
            else:
                errors.append(f"Poll {i+1} failed")

        if not errors:
            avg_size = sum(poll_results) / len(poll_results)
            return {
                "status": "PASS",
                "expected": "10 successful polls",
                "actual": f"All polls successful, avg={avg_size:.1f} samples",
                "details": f"Sizes: {poll_results}"
            }
        else:
            return {
                "status": "FAIL",
                "expected": "10 successful polls",
                "actual": f"{len(errors)} polls failed",
                "error": "; ".join(errors)
            }

    def test_buffer_overflow(self):
        """Test buffer overflow behavior (wait longer than buffer capacity)"""
        # Enable high frequency measurement
        self.client.send_command({
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 500
        })

        # Wait longer than 3 second buffer capacity
        logging.info("  Waiting 5 seconds to force buffer overflow...")
        time.sleep(5)

        response = self.client.send_command({"type": "get_data"})

        if response and response.get("type") == "data":
            data_size = response.get("data_size", 0)

            # We expect some data, but may have lost oldest samples
            return {
                "status": "PASS",
                "expected": "Data retrieved (may have overflow)",
                "actual": f"data_size={data_size}",
                "details": "Buffer overflow test - some data may be lost"
            }
        else:
            return {
                "status": "FAIL",
                "expected": "Data response",
                "actual": json.dumps(response) if response else "None",
                "error": "No response after overflow"
            }

    def run_all(self):
        """Run all data retrieval tests"""
        logging.info(f"\n{'='*70}")
        logging.info(f"Starting {self.suite_name}")
        logging.info(f"{'='*70}")

        self.run_test("Get Data When Disabled", "DATA-001",
                     self.test_get_data_when_disabled)
        self.run_test("Get Data When Enabled", "DATA-002",
                     self.test_get_data_when_enabled)
        self.run_test("Verify Data Point Format", "DATA-003",
                     self.test_verify_data_point_format)
        self.run_test("Sync Marker Detection", "DATA-004",
                     self.test_sync_marker_detection)
        self.run_test("Continuous Data Polling", "DATA-005",
                     self.test_continuous_data_polling)
        self.run_test("Buffer Overflow Test", "DATA-006",
                     self.test_buffer_overflow)


# ============================================================================
# Test Suite 4: Calibration Tests
# ============================================================================

class CalibrationTests(MAX30009TestSuite):
    """Test calibration functionality"""

    def test_start_calibration(self):
        """Test starting calibration process"""
        response = self.client.send_command({"type": "start_calibrate"})

        if response and response.get("type") == "calibrate_started":
            return {
                "status": "PASS",
                "expected": '{"type":"calibrate_started"}',
                "actual": json.dumps(response),
                "details": "Calibration started successfully"
            }
        else:
            return {
                "status": "FAIL",
                "expected": '{"type":"calibrate_started"}',
                "actual": json.dumps(response) if response else "None",
                "error": "Failed to start calibration"
            }

    def test_commands_during_calibration(self):
        """Test that commands are rejected during calibration"""
        # Start calibration
        self.client.send_command({"type": "start_calibrate"})

        # Try to change settings
        response = self.client.send_command({
            "type": "settings",
            "measure_enable": True
        })

        if response and response.get("type") == "calibrate_runing":
            # Try get_data too
            data_response = self.client.send_command({"type": "get_data"})

            if data_response and data_response.get("type") == "calibrate_runing":
                # Stop calibration for next tests
                self.client.send_command({"type": "stop_calibrate"})

                return {
                    "status": "PASS",
                    "expected": "Commands rejected during calibration",
                    "actual": "Both settings and get_data returned calibrate_runing",
                    "details": "Calibration blocking working correctly"
                }
            else:
                self.client.send_command({"type": "stop_calibrate"})
                return {
                    "status": "FAIL",
                    "expected": "get_data rejected",
                    "actual": json.dumps(data_response) if data_response else "None",
                    "error": "get_data not blocked"
                }
        else:
            self.client.send_command({"type": "stop_calibrate"})
            return {
                "status": "FAIL",
                "expected": "settings rejected",
                "actual": json.dumps(response) if response else "None",
                "error": "settings not blocked"
            }

    def test_stop_calibration(self):
        """Test stopping calibration process"""
        # Start then immediately stop
        self.client.send_command({"type": "start_calibrate"})
        time.sleep(0.5)

        response = self.client.send_command({"type": "stop_calibrate"})

        if response and response.get("type") == "calibrate_stoped":
            return {
                "status": "PASS",
                "expected": '{"type":"calibrate_stoped"}',
                "actual": json.dumps(response),
                "details": "Calibration stopped successfully"
            }
        else:
            return {
                "status": "FAIL",
                "expected": '{"type":"calibrate_stoped"}',
                "actual": json.dumps(response) if response else "None",
                "error": "Failed to stop calibration"
            }

    def test_resume_after_calibration(self):
        """Test resuming normal operation after calibration"""
        # Start and stop calibration
        self.client.send_command({"type": "start_calibrate"})
        time.sleep(0.5)
        self.client.send_command({"type": "stop_calibrate"})

        # Try normal operation
        response = self.client.send_command({
            "type": "settings",
            "measure_enable": True
        })

        if response and response.get("type") == "actual_settings":
            return {
                "status": "PASS",
                "expected": "Normal operation resumed",
                "actual": "Settings accepted after calibration",
                "details": json.dumps(response)
            }
        else:
            return {
                "status": "FAIL",
                "expected": "actual_settings",
                "actual": json.dumps(response) if response else "None",
                "error": "Cannot resume normal operation"
            }

    def test_calibration_coverage(self):
        """Test calibration parameter coverage (informational)"""
        total_combinations = FREQUENCY_POINTS_COUNT * CURRENT_POINTS_COUNT

        return {
            "status": "PASS",
            "expected": f"{total_combinations} calibration combinations possible",
            "actual": f"{FREQUENCY_POINTS_COUNT} frequencies × {CURRENT_POINTS_COUNT} currents = {total_combinations} points",
            "details": f"Frequencies: {FREQUENCY_POINTS_COUNT}, Current indices: {CURRENT_POINTS_COUNT}"
        }

    def run_all(self):
        """Run all calibration tests"""
        logging.info(f"\n{'='*70}")
        logging.info(f"Starting {self.suite_name}")
        logging.info(f"{'='*70}")

        self.run_test("Start Calibration", "CALIB-001",
                     self.test_start_calibration)
        self.run_test("Commands During Calibration", "CALIB-002",
                     self.test_commands_during_calibration)
        self.run_test("Stop Calibration", "CALIB-003",
                     self.test_stop_calibration)
        self.run_test("Resume After Calibration", "CALIB-004",
                     self.test_resume_after_calibration)
        self.run_test("Calibration Coverage", "CALIB-005",
                     self.test_calibration_coverage)


# ============================================================================
# Test Suite 5: Power State Tests
# ============================================================================

class PowerStateTests(MAX30009TestSuite):
    """Test power state transitions"""

    def test_power_off_to_on(self):
        """Test power off to on transition"""
        # Power off
        self.client.send_command({
            "type": "settings",
            "power_enable": False
        })

        time.sleep(0.3)  # Wait for power off

        # Power on
        response = self.client.send_command({
            "type": "settings",
            "power_enable": True
        })

        if response and response.get("power_enable") == True:
            return {
                "status": "PASS",
                "expected": "power_enable=true",
                "actual": f"power_enable={response.get('power_enable')}",
                "details": "Power transition successful (200ms stabilization expected)"
            }
        else:
            return {
                "status": "FAIL",
                "expected": "power_enable=true",
                "actual": json.dumps(response) if response else "None",
                "error": "Power on failed"
            }

    def test_measurement_enable_disable_cycles(self):
        """Test measurement enable/disable cycles (5 times)"""
        errors = []

        for i in range(5):
            # Enable
            response = self.client.send_command({
                "type": "settings",
                "measure_enable": True
            })

            if not response or response.get("measure_enable") != True:
                errors.append(f"Cycle {i+1}: Enable failed")

            time.sleep(0.5)

            # Disable
            response = self.client.send_command({
                "type": "settings",
                "measure_enable": False
            })

            if not response or response.get("measure_enable") != False:
                errors.append(f"Cycle {i+1}: Disable failed")

            time.sleep(0.5)

        if not errors:
            return {
                "status": "PASS",
                "expected": "5 enable/disable cycles",
                "actual": "All 5 cycles successful",
                "details": "Measurement state transitions working"
            }
        else:
            return {
                "status": "FAIL",
                "expected": "5 successful cycles",
                "actual": f"{len(errors)} errors",
                "error": "; ".join(errors)
            }

    def run_all(self):
        """Run all power state tests"""
        logging.info(f"\n{'='*70}")
        logging.info(f"Starting {self.suite_name}")
        logging.info(f"{'='*70}")

        self.run_test("Power Off to On", "PWR-001",
                     self.test_power_off_to_on)
        self.run_test("Measurement Enable/Disable Cycles", "PWR-002",
                     self.test_measurement_enable_disable_cycles)


# ============================================================================
# Main Test Runner
# ============================================================================

def setup_logging(log_filename: str):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)8s] %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("="*70)
    logging.info("MAX30009 Test Suite Started")
    logging.info("="*70)


def main():
    """Main test execution"""
    # Generate filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"max30009_test_report_{timestamp}.csv"
    log_file = f"max30009_test_log_{timestamp}.log"

    # Setup logging
    setup_logging(log_file)

    logging.info(f"Test Report: {report_file}")
    logging.info(f"Log File: {log_file}")
    logging.info("")

    # Initialize components
    client = MAX30009Client(HOST, PORT, TIMEOUT)
    reporter = TestReporter(report_file)

    # Check if service is available
    logging.info("Checking MAX30009 service availability...")
    if not client.is_available():
        logging.error(f"MAX30009 service not available at {HOST}:{PORT}")
        logging.error("Please ensure the SPI_DEV_servise is running")
        sys.exit(1)
    logging.info("MAX30009 service is available")
    logging.info("")

    # Run all test suites
    test_suites = [
        ConnectionTests(client, reporter),
        SettingsConfigTests(client, reporter),
        DataRetrievalTests(client, reporter),
        CalibrationTests(client, reporter),
        PowerStateTests(client, reporter)
    ]

    for suite in test_suites:
        try:
            suite.run_all()
        except Exception as e:
            logging.error(f"Exception in {suite.suite_name}: {e}")
            logging.error(traceback.format_exc())

    # Save results and print summary
    reporter.save_csv()
    reporter.print_summary()

    # Return exit code based on results
    summary = reporter.get_summary()
    if summary["FAIL"] > 0 or summary["ERROR"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
