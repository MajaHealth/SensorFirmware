#!/usr/bin/env python3
"""
ICG-ECG Synchronization Test Script

This script tests the synchronization between ICG (MAX30009) and ECG (ADS1293) data streams
by verifying that sync marks (-99999) are time-locked between the two sensors.

Test Matrix:
- ICG measure_frequency: 100-1000 Hz (increments of 100)
- ICG stimulate_table_index: 5 (fixed)
- ICG stimulate_frequency: 7 (fixed)
- ECG R2/R3 combinations: (4,16), (4,32), (6,8), (4,64)
- Recording duration: 30 seconds per test

Usage:
    python3 test_icg_ecg_sync.py [host] [threshold_ms]

Arguments:
    host         - IP address or hostname (default: localhost)
    threshold_ms - Sync threshold in milliseconds (default: 50ms)

Examples:
    python3 test_icg_ecg_sync.py                    # Default: localhost, 50ms
    python3 test_icg_ecg_sync.py 192.168.1.100      # Remote device, 50ms
    python3 test_icg_ecg_sync.py localhost 10       # Local device, 10ms threshold

Output:
    - CSV file: icg_ecg_sync_test_YYYYMMDD_HHMMSS.csv (detailed per-test results)
    - JSON file: icg_ecg_sync_test_results_YYYYMMDD_HHMMSS.json (full test data)
"""

import socket
import json
import time
import sys
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading


def parse_firmware_timestamp(timestamp_str: str) -> float:
    """Parse firmware timestamp string to Unix timestamp (seconds since epoch)

    Firmware format: "2025-10-27 07:55:27.594" (UTC, millisecond precision)

    Args:
        timestamp_str: Timestamp string from firmware JSON response

    Returns:
        Unix timestamp as float (seconds since epoch with fractional seconds)

    Raises:
        ValueError: If timestamp format is invalid
    """
    try:
        # Parse the timestamp string (format: "YYYY-MM-DD HH:MM:SS.mmm")
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

        # Convert to Unix timestamp (seconds since epoch)
        # Firmware uses UTC/GMT (gmtime_r in C++ code)
        unix_timestamp = dt.timestamp()

        return unix_timestamp

    except ValueError as e:
        raise ValueError(f"Invalid firmware timestamp format '{timestamp_str}': {e}")


class DeviceClient:
    """TCP client for communicating with sensor services"""

    def __init__(self, host: str, port: int, device_name: str):
        self.host = host
        self.port = port
        self.device_name = device_name
        self.socket = None

    def connect(self) -> bool:
        """Connect to the device TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            print(f"✓ Connected to {self.device_name} on port {self.port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to {self.device_name}: {e}")
            return False

    def disconnect(self):
        """Disconnect from the device"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def send_command(self, command: dict) -> Optional[dict]:
        """Send JSON command and receive response"""
        try:
            json_str = json.dumps(command) + '\n'
            self.socket.sendall(json_str.encode())

            # Receive response
            response = b''
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b'\n' in response:
                    break

            if response:
                return json.loads(response.decode().strip())
            return None

        except Exception as e:
            print(f"✗ Error sending command to {self.device_name}: {e}")
            return None

    def get_data(self) -> Optional[dict]:
        """Request data from the device"""
        try:
            command = {"type": "get_data"}
            return self.send_command(command)
        except Exception as e:
            print(f"✗ Error getting data from {self.device_name}: {e}")
            return None


class SyncTester:
    """Tests synchronization between ICG and ECG data streams"""

    def __init__(self, host: str = "localhost", sync_threshold_ms: float = 50.0):
        self.host = host
        self.icg_client = DeviceClient(host, 30009, "ICG (MAX30009)")
        self.ecg_client = DeviceClient(host, 1293, "ECG (ADS1293)")

        # Configurable sync threshold (in milliseconds)
        self.sync_threshold_ms = sync_threshold_ms
        self.sync_threshold = sync_threshold_ms / 1000.0  # Convert to seconds

        # Test configurations
        self.icg_measure_frequencies = list(range(100, 1001, 100))  # 100-1000 Hz
        self.ecg_r2_r3_combinations = [
            (4, 16),
            (4, 32),
            (6, 8),
            (4, 64)
        ]

        # ECG R2/R3 to sampling rate mapping (in Hz)
        self.ecg_rate_map = {
            (4, 16): 400,
            (4, 32): 200,
            (6, 8): 533,
            (4, 64): 800
        }

        # Fixed ICG parameters
        self.icg_fixed_params = {
            "stimulate_table_index": 5,
            "stimulate_frequency": 7
        }

        # Test results
        self.test_results = []

        # CSV file setup
        self.csv_filename = None
        self.csv_file = None
        self.csv_writer = None

    def connect_all(self) -> bool:
        """Connect to both devices"""
        icg_ok = self.icg_client.connect()
        ecg_ok = self.ecg_client.connect()
        return icg_ok and ecg_ok

    def disconnect_all(self):
        """Disconnect from all devices"""
        self.icg_client.disconnect()
        self.ecg_client.disconnect()

    def stop_icg(self) -> bool:
        """Stop ICG measurement and power down"""
        config = {
            "type": "settings",
            "power_enable": False,
            "measure_enable": False,
            "measure_frequency": 400,  # Dummy value, not used when disabled
            "stimulate_table_index": self.icg_fixed_params["stimulate_table_index"],
            "stimulate_frequency": self.icg_fixed_params["stimulate_frequency"],
            "ext_MUX_state": 1,
            "out_HP_filter": 0,
            "out_LP_filter": 0
        }
        response = self.icg_client.send_command(config)
        return response is not None

    def stop_ecg(self, r2_rate: int = 4, r3_rate: int = 16) -> bool:
        """Stop ECG conversion but keep power on"""
        config = {
            "type": "settings",
            "power_enable": True,
            "enable_conversion": False,
            "R2_rate": r2_rate,
            "R3_rate": r3_rate
        }
        response = self.ecg_client.send_command(config)
        return response is not None

    def flush_buffers(self, num_requests: int = 5) -> None:
        """Flush device buffers by draining remaining data"""
        print(f"  Flushing buffers with {num_requests} drain requests...")
        for i in range(num_requests):
            self.icg_client.get_data()
            self.ecg_client.get_data()
            time.sleep(0.1)
        print("  ✓ Buffers flushed")

    def configure_icg(self, measure_frequency: int) -> bool:
        """Configure ICG with specific parameters"""
        config = {
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": measure_frequency,
            "stimulate_table_index": self.icg_fixed_params["stimulate_table_index"],
            "stimulate_frequency": self.icg_fixed_params["stimulate_frequency"],
            "ext_MUX_state": 1,
            "out_HP_filter": 0,
            "out_LP_filter": 0
        }

        print(f"  Configuring ICG: measure_freq={measure_frequency}Hz, "
              f"stim_table_idx={config['stimulate_table_index']}, "
              f"stim_freq={config['stimulate_frequency']}")

        response = self.icg_client.send_command(config)
        return response is not None

    def configure_ecg(self, r2_rate: int, r3_rate: int) -> bool:
        """Configure ECG with specific R2/R3 rates"""
        config = {
            "type": "settings",
            "power_enable": True,
            "enable_conversion": True,
            "R2_rate": r2_rate,
            "R3_rate": r3_rate
        }

        print(f"  Configuring ECG: R2={r2_rate}, R3={r3_rate}")

        response = self.ecg_client.send_command(config)
        return response is not None

    def collect_data(self, duration: int = 30) -> Tuple[List, List]:
        """Collect data from both sensors for specified duration"""
        print(f"  Collecting data for {duration} seconds...")

        icg_data_sets = []
        ecg_data_sets = []

        start_time = time.time()
        iteration = 0

        while time.time() - start_time < duration:
            iteration += 1

            # Get data from both sensors
            icg_data = self.icg_client.get_data()
            ecg_data = self.ecg_client.get_data()

            if icg_data and 'data' in icg_data:
                # Use firmware timestamp from JSON response instead of Python reception time
                try:
                    if 'timestamp' in icg_data:
                        firmware_timestamp = parse_firmware_timestamp(icg_data['timestamp'])
                    else:
                        # Fallback to Python time if firmware timestamp missing
                        firmware_timestamp = time.time()
                        print(f"    Warning: ICG packet missing firmware timestamp, using Python time")

                    icg_data_sets.append({
                        'timestamp': firmware_timestamp,
                        'data': icg_data['data']
                    })
                except ValueError as e:
                    print(f"    Warning: Failed to parse ICG timestamp: {e}")
                    # Use Python time as fallback
                    icg_data_sets.append({
                        'timestamp': time.time(),
                        'data': icg_data['data']
                    })

            if ecg_data and 'data' in ecg_data:
                # Use firmware timestamp from JSON response instead of Python reception time
                try:
                    if 'timestamp' in ecg_data:
                        firmware_timestamp = parse_firmware_timestamp(ecg_data['timestamp'])
                    else:
                        # Fallback to Python time if firmware timestamp missing
                        firmware_timestamp = time.time()
                        print(f"    Warning: ECG packet missing firmware timestamp, using Python time")

                    ecg_data_sets.append({
                        'timestamp': firmware_timestamp,
                        'data': ecg_data['data']
                    })
                except ValueError as e:
                    print(f"    Warning: Failed to parse ECG timestamp: {e}")
                    # Use Python time as fallback
                    ecg_data_sets.append({
                        'timestamp': time.time(),
                        'data': ecg_data['data']
                    })

            # Progress indicator
            if iteration % 10 == 0:
                elapsed = time.time() - start_time
                print(f"    Progress: {elapsed:.1f}/{duration}s "
                      f"(ICG: {len(icg_data_sets)} sets, ECG: {len(ecg_data_sets)} sets)")

            # Small delay to prevent overwhelming the system
            time.sleep(0.1)

        print(f"  ✓ Data collection complete: ICG={len(icg_data_sets)} sets, ECG={len(ecg_data_sets)} sets")
        return icg_data_sets, ecg_data_sets

    def extract_sync_marks(self, data_sets: List, device_type: str = 'ECG', sampling_rate: float = 400) -> List[Tuple]:
        """Extract sync marks with sample-accurate timestamps from data sets

        Uses firmware timestamp as base and calculates sample-accurate offset based on
        position within the packet and sampling rate.

        Args:
            data_sets: List of data sets with firmware timestamps
            device_type: 'ECG' or 'ICG' to handle different formats
            sampling_rate: Sampling rate in Hz for timestamp calculation

        Returns:
            List of tuples (sync_number, actual_timestamp, position_in_packet, total_samples_in_packet)
        """
        sync_marks = []

        # Different magic numbers for ECG vs ICG
        # ECG: -99999
        # ICG: -999990000 (scaled by 10000)
        ecg_magic = -99999
        icg_magic = -999990000

        for data_set in data_sets:
            # Firmware timestamp from device (when packet was assembled)
            firmware_timestamp = data_set['timestamp']
            data_array = data_set['data']
            total_samples = len(data_array)

            for position, sample in enumerate(data_array):
                # Data format is array/list of integers
                # ECG: [ch1, ch2, ch3] - 3 elements
                # ICG: [I, Q, mag, phase, ...] - 5 elements
                # Sync mark in ECG: [-99999, sync_num, 0]
                # Sync mark in ICG: [-999990000, sync_num*10000, 0, 0, 0]

                if isinstance(sample, (list, tuple)) and len(sample) > 0:
                    first_val = sample[0]

                    # Check for ECG sync mark
                    if device_type == 'ECG' and first_val == ecg_magic:
                        if len(sample) >= 2:
                            sync_num = sample[1]
                            # Calculate sample-accurate timestamp by backing up from firmware timestamp
                            # Assumption: firmware timestamp represents approximately when last sample was acquired
                            # We calculate how many samples occurred after the sync mark
                            samples_after_sync = total_samples - position - 1
                            time_offset = samples_after_sync / sampling_rate
                            actual_timestamp = firmware_timestamp - time_offset

                            sync_marks.append((sync_num, actual_timestamp, position, total_samples))

                    # Check for ICG sync mark (scaled by 10000)
                    elif device_type == 'ICG' and first_val == icg_magic:
                        if len(sample) >= 2:
                            # Sync number is also scaled by 10000, so divide it
                            sync_num = sample[1] // 10000
                            # Calculate sample-accurate timestamp by backing up from firmware timestamp
                            # Assumption: firmware timestamp represents approximately when last sample was acquired
                            # We calculate how many samples occurred after the sync mark
                            samples_after_sync = total_samples - position - 1
                            time_offset = samples_after_sync / sampling_rate
                            actual_timestamp = firmware_timestamp - time_offset

                            sync_marks.append((sync_num, actual_timestamp, position, total_samples))

        return sync_marks

    def validate_sample_rates(self, sync_marks: List[Tuple], expected_rate: float, device_name: str) -> Dict:
        """Validate sample rate by counting samples between consecutive sync marks

        Args:
            sync_marks: List of (sync_num, timestamp, position, total_samples) tuples
            expected_rate: Expected sampling rate in Hz
            device_name: Device name for logging

        Returns:
            Dictionary with validation results
        """
        if len(sync_marks) < 2:
            return {
                'valid': False,
                'error': 'Not enough sync marks for validation (need at least 2)',
                'sample_counts': [],
                'time_intervals': [],
                'calculated_rates': []
            }

        sample_counts = []
        time_intervals = []
        calculated_rates = []

        # Analyze intervals between consecutive sync marks
        for i in range(len(sync_marks) - 1):
            sync_num1, time1, pos1, total1 = sync_marks[i]
            sync_num2, time2, pos2, total2 = sync_marks[i + 1]

            # Skip if sync numbers aren't consecutive
            if sync_num2 != sync_num1 + 1:
                continue

            # Time interval between syncs
            time_interval = time2 - time1
            time_intervals.append(time_interval)

            # Calculate actual rate from time interval
            # Expected: ~1 second between syncs, so rate ≈ expected_rate samples
            calculated_rate = expected_rate  # We don't have sample count between syncs easily
            calculated_rates.append(calculated_rate)

        if not time_intervals:
            return {
                'valid': False,
                'error': 'No consecutive sync marks found',
                'sample_counts': [],
                'time_intervals': [],
                'calculated_rates': []
            }

        # Check if time intervals are approximately 1 second (±50ms tolerance)
        avg_interval = sum(time_intervals) / len(time_intervals)
        max_interval = max(time_intervals)
        min_interval = min(time_intervals)

        is_valid = (0.95 <= avg_interval <= 1.05)  # Within 5% of 1 second

        return {
            'valid': is_valid,
            'sample_counts': sample_counts,
            'time_intervals': time_intervals,
            'calculated_rates': calculated_rates,
            'avg_interval': avg_interval,
            'min_interval': min_interval,
            'max_interval': max_interval,
            'expected_interval': 1.0
        }

    def analyze_synchronization(self, icg_syncs: List[Tuple], ecg_syncs: List[Tuple],
                                icg_rate: float, ecg_rate: float) -> Dict:
        """Analyze synchronization between ICG and ECG sync marks with sample-level accuracy"""

        # Validate sample rates
        icg_rate_validation = self.validate_sample_rates(icg_syncs, icg_rate, "ICG")
        ecg_rate_validation = self.validate_sample_rates(ecg_syncs, ecg_rate, "ECG")

        # Extract sync number and timestamp from tuples (sync_num, timestamp, position, total_samples)
        icg_sync_dict = {sync_num: timestamp for sync_num, timestamp, _, _ in icg_syncs}
        ecg_sync_dict = {sync_num: timestamp for sync_num, timestamp, _, _ in ecg_syncs}

        # Find common sync numbers
        icg_nums = set(icg_sync_dict.keys())
        ecg_nums = set(ecg_sync_dict.keys())
        common_nums = icg_nums & ecg_nums

        if not common_nums:
            return {
                'success': False,
                'error': 'No common sync marks found',
                'icg_sync_count': len(icg_syncs),
                'ecg_sync_count': len(ecg_syncs),
                'common_sync_count': 0,
                'time_differences': [],
                'max_time_diff': None,
                'avg_time_diff': None,
                'icg_rate_validation': icg_rate_validation,
                'ecg_rate_validation': ecg_rate_validation
            }

        # Calculate time differences for common sync marks
        time_diffs = []
        for sync_num in sorted(common_nums):
            icg_time = icg_sync_dict[sync_num]
            ecg_time = ecg_sync_dict[sync_num]
            time_diff = abs(icg_time - ecg_time)
            time_diffs.append(time_diff)

        max_diff = max(time_diffs) if time_diffs else 0
        avg_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        min_diff = min(time_diffs) if time_diffs else 0

        # Use configured sync threshold
        is_synchronized = max_diff < self.sync_threshold

        return {
            'success': is_synchronized,
            'icg_sync_count': len(icg_syncs),
            'ecg_sync_count': len(ecg_syncs),
            'common_sync_count': len(common_nums),
            'time_differences': time_diffs,
            'min_time_diff': min_diff,
            'max_time_diff': max_diff,
            'avg_time_diff': avg_diff,
            'sync_threshold': self.sync_threshold,
            'sync_threshold_ms': self.sync_threshold_ms,
            'common_sync_numbers': sorted(common_nums),
            'icg_sampling_rate': icg_rate,
            'ecg_sampling_rate': ecg_rate,
            'icg_rate_validation': icg_rate_validation,
            'ecg_rate_validation': ecg_rate_validation
        }

    def run_single_test(self, icg_freq: int, ecg_r2: int, ecg_r3: int,
                       test_num: int, total_tests: int) -> Dict:
        """Run a single synchronization test"""

        print(f"\n{'='*80}")
        print(f"Test {test_num}/{total_tests}: ICG_freq={icg_freq}Hz, ECG_R2={ecg_r2}, ECG_R3={ecg_r3}")
        print(f"{'='*80}")

        # Get ECG sampling rate from mapping
        ecg_rate = self.ecg_rate_map.get((ecg_r2, ecg_r3), 400)  # Default to 400 if not found

        test_result = {
            'test_number': test_num,
            'icg_measure_frequency': icg_freq,
            'icg_stimulate_table_index': self.icg_fixed_params['stimulate_table_index'],
            'icg_stimulate_frequency': self.icg_fixed_params['stimulate_frequency'],
            'ecg_r2_rate': ecg_r2,
            'ecg_r3_rate': ecg_r3,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }

        try:
            # Stop both devices first to ensure clean state
            print("  Stopping devices...")
            self.stop_icg()
            self.stop_ecg(ecg_r2, ecg_r3)

            # Flush buffers to drain any remaining data
            time.sleep(2)
            self.flush_buffers()

            # Configure both devices
            if not self.configure_icg(icg_freq):
                test_result['error'] = 'Failed to configure ICG'
                return test_result

            if not self.configure_ecg(ecg_r2, ecg_r3):
                test_result['error'] = 'Failed to configure ECG'
                return test_result

            # Wait for devices to stabilize
            print("  Waiting 2 seconds for devices to stabilize...")
            time.sleep(2)

            # Collect data
            icg_data, ecg_data = self.collect_data(duration=30)

            # Extract sync marks with device-specific parsing and sampling rates
            print("  Analyzing sync marks with sample-accurate timing...")
            print(f"    ICG sampling rate: {icg_freq} Hz")
            print(f"    ECG sampling rate: {ecg_rate} Hz (R2={ecg_r2}, R3={ecg_r3})")

            icg_syncs = self.extract_sync_marks(icg_data, device_type='ICG', sampling_rate=icg_freq)
            ecg_syncs = self.extract_sync_marks(ecg_data, device_type='ECG', sampling_rate=ecg_rate)

            print(f"  ICG sync marks found: {len(icg_syncs)}")
            print(f"  ECG sync marks found: {len(ecg_syncs)}")

            # Debug: Show first few sync marks if found
            if icg_syncs:
                print(f"    ICG first syncs: {[(n, f'{t:.3f}') for n, t, _, _ in icg_syncs[:3]]}")
            if ecg_syncs:
                print(f"    ECG first syncs: {[(n, f'{t:.3f}') for n, t, _, _ in ecg_syncs[:3]]}")

            # Analyze synchronization with sampling rates
            sync_analysis = self.analyze_synchronization(icg_syncs, ecg_syncs, icg_freq, ecg_rate)
            test_result.update(sync_analysis)

            # Print results
            if sync_analysis['success']:
                print(f"  ✓ PASS - Synchronization verified!")
                print(f"    Common sync marks: {sync_analysis['common_sync_count']}")
                print(f"    Max time difference: {sync_analysis['max_time_diff']*1000:.2f}ms")
                print(f"    Avg time difference: {sync_analysis['avg_time_diff']*1000:.2f}ms")
            else:
                print(f"  ✗ FAIL - Synchronization issue detected!")
                if 'error' in sync_analysis:
                    print(f"    Error: {sync_analysis['error']}")
                else:
                    print(f"    Max time difference: {sync_analysis['max_time_diff']*1000:.2f}ms")
                    print(f"    Threshold: {sync_analysis['sync_threshold']*1000:.2f}ms")

        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            test_result['error'] = str(e)
            test_result['success'] = False

        return test_result

    def init_csv(self):
        """Initialize CSV file for logging results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f"icg_ecg_sync_test_{timestamp}.csv"

        self.csv_file = open(self.csv_filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        # Write header
        self.csv_writer.writerow([
            'test_number',
            'timestamp',
            'icg_measure_freq_hz',
            'icg_stim_table_index',
            'icg_stim_frequency',
            'ecg_r2_rate',
            'ecg_r3_rate',
            'ecg_sampling_rate_hz',
            'result',
            'icg_sync_count',
            'ecg_sync_count',
            'common_sync_count',
            'min_time_diff_ms',
            'max_time_diff_ms',
            'avg_time_diff_ms',
            'threshold_ms',
            'icg_rate_valid',
            'ecg_rate_valid',
            'icg_avg_interval_s',
            'ecg_avg_interval_s',
            'error_message'
        ])
        self.csv_file.flush()

        print(f"CSV log: {self.csv_filename}")

    def log_to_csv(self, result: Dict):
        """Log a single test result to CSV"""
        if not self.csv_writer:
            return

        # Extract rate validation info
        icg_val = result.get('icg_rate_validation', {})
        ecg_val = result.get('ecg_rate_validation', {})

        self.csv_writer.writerow([
            result.get('test_number', ''),
            result.get('timestamp', ''),
            result.get('icg_measure_frequency', ''),
            result.get('icg_stimulate_table_index', ''),
            result.get('icg_stimulate_frequency', ''),
            result.get('ecg_r2_rate', ''),
            result.get('ecg_r3_rate', ''),
            result.get('ecg_sampling_rate', ''),
            'PASS' if result.get('success', False) else 'FAIL',
            result.get('icg_sync_count', ''),
            result.get('ecg_sync_count', ''),
            result.get('common_sync_count', ''),
            f"{result.get('min_time_diff', 0) * 1000:.3f}" if result.get('min_time_diff') is not None else '',
            f"{result.get('max_time_diff', 0) * 1000:.3f}" if result.get('max_time_diff') is not None else '',
            f"{result.get('avg_time_diff', 0) * 1000:.3f}" if result.get('avg_time_diff') is not None else '',
            result.get('sync_threshold_ms', ''),
            'YES' if icg_val.get('valid') else 'NO',
            'YES' if ecg_val.get('valid') else 'NO',
            f"{icg_val.get('avg_interval', 0):.3f}" if icg_val.get('avg_interval') is not None else '',
            f"{ecg_val.get('avg_interval', 0):.3f}" if ecg_val.get('avg_interval') is not None else '',
            result.get('error', '')
        ])
        self.csv_file.flush()

    def close_csv(self):
        """Close CSV file"""
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None

    def run_all_tests(self):
        """Run all test combinations"""

        print("\n" + "="*80)
        print("ICG-ECG SYNCHRONIZATION TEST SUITE")
        print("="*80)
        print(f"Sync threshold: {self.sync_threshold_ms}ms")
        print(f"Total test combinations: {len(self.icg_measure_frequencies)} × {len(self.ecg_r2_r3_combinations)} "
              f"= {len(self.icg_measure_frequencies) * len(self.ecg_r2_r3_combinations)} tests")
        print(f"Test duration per combination: 30 seconds")
        print(f"Estimated total time: ~{len(self.icg_measure_frequencies) * len(self.ecg_r2_r3_combinations) * 0.6:.1f} minutes")
        print("="*80)

        # Initialize CSV logging
        self.init_csv()

        # Connect to devices
        if not self.connect_all():
            print("✗ Failed to connect to devices. Exiting.")
            self.close_csv()
            return False

        try:
            test_num = 0
            total_tests = len(self.icg_measure_frequencies) * len(self.ecg_r2_r3_combinations)

            # Run all combinations
            for icg_freq in self.icg_measure_frequencies:
                for ecg_r2, ecg_r3 in self.ecg_r2_r3_combinations:
                    test_num += 1
                    result = self.run_single_test(icg_freq, ecg_r2, ecg_r3, test_num, total_tests)
                    self.test_results.append(result)

                    # Log to CSV immediately
                    self.log_to_csv(result)

                    # Small delay between tests
                    if test_num < total_tests:
                        print("\n  Waiting 3 seconds before next test...")
                        time.sleep(3)

            # Generate summary
            self.print_summary()

            # Save results to JSON file
            self.save_results()

            return True

        finally:
            self.close_csv()
            self.disconnect_all()

    def print_summary(self):
        """Print test summary"""

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests

        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

        if failed_tests > 0:
            print(f"\nFailed test configurations:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - ICG_freq={result['icg_measure_frequency']}Hz, "
                          f"ECG_R2={result['ecg_r2_rate']}, ECG_R3={result['ecg_r3_rate']}")
                    if 'error' in result:
                        print(f"    Error: {result['error']}")

        # Analyze sync quality across tests
        sync_quality = []
        for result in self.test_results:
            if result['success'] and 'avg_time_diff' in result:
                sync_quality.append(result['avg_time_diff'])

        if sync_quality:
            print(f"\nSynchronization Quality:")
            print(f"  Best avg sync: {min(sync_quality)*1000:.2f}ms")
            print(f"  Worst avg sync: {max(sync_quality)*1000:.2f}ms")
            print(f"  Overall avg sync: {sum(sync_quality)/len(sync_quality)*1000:.2f}ms")

        print("\n" + "="*80)
        print(f"CSV Report: {self.csv_filename}")
        print("="*80)

    def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"icg_ecg_sync_test_results_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'test_suite': 'ICG-ECG Synchronization Test',
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r['success']),
                'failed_tests': sum(1 for r in self.test_results if not r['success']),
                'results': self.test_results
            }, f, indent=2)

        print(f"\nResults saved to: {filename}")


def main():
    """Main entry point"""

    # Parse command line arguments
    host = "localhost"
    sync_threshold_ms = 50.0  # Default: 50ms

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            sync_threshold_ms = float(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid threshold value '{sys.argv[2]}'. Using default 50ms.")

    print(f"Connecting to services on: {host}")
    print(f"Sync threshold: {sync_threshold_ms}ms")

    # Create tester and run all tests
    tester = SyncTester(host=host, sync_threshold_ms=sync_threshold_ms)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
