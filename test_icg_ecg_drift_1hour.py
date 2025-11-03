#!/usr/bin/env python3
"""
ICG-ECG 1-Hour Drift Analysis Test - Enhanced Debug Version

This script tests a single ICG/ECG configuration for 1 hour with comprehensive
debugging to identify timing drift, sample count discrepancies, and missing sync markers.

Test Configuration:
- ICG: 400 Hz, stimulate_table_index=4, stimulate_frequency=7
- ECG: R2=4, R3=16 (400 Hz)
- Duration: 1 hour (3600 seconds)
- Data request interval: Configurable (default: 0.2 seconds)

Enhanced Logging:
- Request log: Every get_data call with timing
- Sync analysis: Detailed per-marker analysis
- Anomaly report: Human-readable summary

Usage:
    python3 test_icg_ecg_drift_1hour.py [host] [threshold_ms] [data_interval_s]

Arguments:
    host            - IP address or hostname (default: localhost)
    threshold_ms    - Sync threshold in milliseconds (default: 50.0)
    data_interval_s - Data request interval in seconds (default: 0.2)

Examples:
    python3 test_icg_ecg_drift_1hour.py
    python3 test_icg_ecg_drift_1hour.py localhost 50 1.0
    python3 test_icg_ecg_drift_1hour.py localhost 10 0.5

Output:
    - requests_log_*.csv: Every request/response logged
    - sync_analysis_*.csv: Detailed per-sync-marker analysis
    - anomalies_report_*.txt: Human-readable anomaly summary
    - icg_ecg_drift_1hour_results_*.json: Complete test data
"""

import socket
import json
import time
import sys
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os


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
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
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


class DriftTester:
    """Tests long-term drift between ICG and ECG data streams with comprehensive debugging"""

    def __init__(self, host: str = "localhost", sync_threshold_ms: float = 50.0,
                 data_interval_seconds: float = 0.2):
        self.host = host
        self.icg_client = DeviceClient(host, 30009, "ICG (MAX30009)")
        self.ecg_client = DeviceClient(host, 1293, "ECG (ADS1293)")

        # Configurable parameters
        self.sync_threshold_ms = sync_threshold_ms
        self.sync_threshold = sync_threshold_ms / 1000.0
        self.data_interval = data_interval_seconds

        # Test configuration
        self.icg_config = {
            "type": "settings",
            "power_enable": True,
            "measure_enable": True,
            "measure_frequency": 400,
            "stimulate_table_index": 4,
            "stimulate_frequency": 7,
            "ext_MUX_state": 1,
            "out_HP_filter": 0,
            "out_LP_filter": 0
        }

        self.ecg_config = {
            "type": "settings",
            "power_enable": True,
            "enable_conversion": True,
            "R2_rate": 4,
            "R3_rate": 16
        }

        self.icg_sampling_rate = 400
        self.ecg_sampling_rate = 400
        self.expected_samples_per_interval = 400
        self.test_duration = 3600

        # CSV file handles
        self.requests_csv_filename = None
        self.requests_csv_file = None
        self.requests_csv_writer = None

        self.sync_csv_filename = None
        self.sync_csv_file = None
        self.sync_csv_writer = None

        self.anomaly_report_filename = None
        self.anomaly_report_file = None

        # Tracking variables
        self.test_start_time = None
        self.request_counter = 0

        # Anomaly tracking
        self.anomalies = {
            'missing_icg_syncs': [],
            'missing_ecg_syncs': [],
            'sample_count_icg': [],
            'sample_count_ecg': [],
            'time_interval_issues': [],
            'multiple_syncs_icg': [],
            'multiple_syncs_ecg': [],
            'no_data_icg': [],
            'no_data_ecg': [],
            'sync_mismatch': []
        }

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
        config = self.icg_config.copy()
        config["power_enable"] = False
        config["measure_enable"] = False
        response = self.icg_client.send_command(config)
        return response is not None

    def stop_ecg(self) -> bool:
        """Stop ECG conversion"""
        config = self.ecg_config.copy()
        config["enable_conversion"] = False
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

    def configure_devices(self) -> bool:
        """Configure both devices with test settings"""
        print("  Configuring ICG...")
        print(f"    measure_freq={self.icg_config['measure_frequency']}Hz, "
              f"stim_table_idx={self.icg_config['stimulate_table_index']}, "
              f"stim_freq={self.icg_config['stimulate_frequency']}")

        icg_response = self.icg_client.send_command(self.icg_config)
        if not icg_response:
            print("  ✗ Failed to configure ICG")
            return False

        print("  Configuring ECG...")
        print(f"    R2={self.ecg_config['R2_rate']}, R3={self.ecg_config['R3_rate']}")

        ecg_response = self.ecg_client.send_command(self.ecg_config)
        if not ecg_response:
            print("  ✗ Failed to configure ECG")
            return False

        print("  ✓ Both devices configured")
        return True

    def collect_data(self, duration: int = 3600) -> Tuple[List, List]:
        """Collect data from both sensors with comprehensive logging"""
        print(f"  Starting data collection for {duration} seconds ({duration/60:.1f} minutes)...")

        icg_data_sets = []
        ecg_data_sets = []

        start_time = time.time()
        self.test_start_time = start_time
        last_progress_time = start_time

        while time.time() - start_time < duration:
            self.request_counter += 1

            # Request timing
            request_time_utc = datetime.utcnow()
            elapsed_time = time.time() - start_time

            # Get ICG data with timing
            icg_request_start = time.time()
            icg_data = self.icg_client.get_data()
            icg_response_time_utc = datetime.utcnow()
            icg_request_duration = (time.time() - icg_request_start) * 1000

            # Get ECG data with timing
            ecg_request_start = time.time()
            ecg_data = self.ecg_client.get_data()
            ecg_response_time_utc = datetime.utcnow()
            ecg_request_duration = (time.time() - ecg_request_start) * 1000

            # Initialize packet metadata
            icg_firmware_ts = None
            icg_packet_samples = 0
            icg_sync_count = 0
            icg_sync_numbers = []

            ecg_firmware_ts = None
            ecg_packet_samples = 0
            ecg_sync_count = 0
            ecg_sync_numbers = []

            # Process ICG data
            if icg_data and 'data' in icg_data:
                try:
                    if 'timestamp' in icg_data:
                        icg_firmware_ts = parse_firmware_timestamp(icg_data['timestamp'])
                    else:
                        icg_firmware_ts = time.time()

                    icg_packet_samples = len(icg_data['data'])

                    # Count sync markers
                    for sample in icg_data['data']:
                        if isinstance(sample, (list, tuple)) and len(sample) > 0:
                            if sample[0] == -999990000:
                                icg_sync_count += 1
                                if len(sample) >= 2:
                                    sync_num = sample[1] // 10000
                                    icg_sync_numbers.append(sync_num)

                    icg_data_sets.append({
                        'timestamp': icg_firmware_ts,
                        'data': icg_data['data'],
                        'request_id': self.request_counter,
                        'request_time_utc': request_time_utc
                    })
                except Exception as e:
                    print(f"    Warning: ICG data processing error: {e}")
            else:
                self.anomalies['no_data_icg'].append({
                    'request_id': self.request_counter,
                    'timestamp': request_time_utc
                })

            # Process ECG data
            if ecg_data and 'data' in ecg_data:
                try:
                    if 'timestamp' in ecg_data:
                        ecg_firmware_ts = parse_firmware_timestamp(ecg_data['timestamp'])
                    else:
                        ecg_firmware_ts = time.time()

                    ecg_packet_samples = len(ecg_data['data'])

                    # Count sync markers
                    for sample in ecg_data['data']:
                        if isinstance(sample, (list, tuple)) and len(sample) > 0:
                            if sample[0] == -99999:
                                ecg_sync_count += 1
                                if len(sample) >= 2:
                                    sync_num = sample[1]
                                    ecg_sync_numbers.append(sync_num)

                    ecg_data_sets.append({
                        'timestamp': ecg_firmware_ts,
                        'data': ecg_data['data'],
                        'request_id': self.request_counter,
                        'request_time_utc': request_time_utc
                    })
                except Exception as e:
                    print(f"    Warning: ECG data processing error: {e}")
            else:
                self.anomalies['no_data_ecg'].append({
                    'request_id': self.request_counter,
                    'timestamp': request_time_utc
                })

            # Check for anomalies
            if icg_sync_count > 1:
                self.anomalies['multiple_syncs_icg'].append({
                    'request_id': self.request_counter,
                    'timestamp': request_time_utc,
                    'sync_numbers': icg_sync_numbers
                })
                print(f"    ⚠️  ANOMALY: Multiple ICG syncs in request {self.request_counter}: {icg_sync_numbers}")

            if ecg_sync_count > 1:
                self.anomalies['multiple_syncs_ecg'].append({
                    'request_id': self.request_counter,
                    'timestamp': request_time_utc,
                    'sync_numbers': ecg_sync_numbers
                })
                print(f"    ⚠️  ANOMALY: Multiple ECG syncs in request {self.request_counter}: {ecg_sync_numbers}")

            # Log request
            self.log_request(
                self.request_counter, request_time_utc, elapsed_time,
                icg_response_time_utc, icg_request_duration, icg_firmware_ts,
                icg_packet_samples, icg_sync_count, icg_sync_numbers,
                ecg_response_time_utc, ecg_request_duration, ecg_firmware_ts,
                ecg_packet_samples, ecg_sync_count, ecg_sync_numbers
            )

            # Progress indicator
            current_time = time.time()
            if current_time - last_progress_time >= 60:
                elapsed = current_time - start_time
                remaining = duration - elapsed
                print(f"    Progress: {elapsed/60:.1f}/{duration/60:.1f} min "
                      f"(Requests: {self.request_counter}, ICG: {len(icg_data_sets)}, "
                      f"ECG: {len(ecg_data_sets)}, Remaining: {remaining/60:.1f} min)")
                last_progress_time = current_time

            time.sleep(self.data_interval)

        print(f"  ✓ Data collection complete: {self.request_counter} requests, "
              f"ICG={len(icg_data_sets)} packets, ECG={len(ecg_data_sets)} packets")
        return icg_data_sets, ecg_data_sets

    def log_request(self, request_id, request_time_utc, elapsed_time_s,
                   icg_response_time, icg_duration, icg_firmware_ts, icg_samples,
                   icg_sync_count, icg_sync_nums,
                   ecg_response_time, ecg_duration, ecg_firmware_ts, ecg_samples,
                   ecg_sync_count, ecg_sync_nums):
        """Log a single request to the requests CSV"""
        if not self.requests_csv_writer:
            return

        icg_sync_str = ','.join(map(str, icg_sync_nums)) if icg_sync_nums else ''
        ecg_sync_str = ','.join(map(str, ecg_sync_nums)) if ecg_sync_nums else ''

        anomaly_multi_icg = icg_sync_count > 1
        anomaly_multi_ecg = ecg_sync_count > 1
        anomaly_no_icg = icg_samples == 0
        anomaly_no_ecg = ecg_samples == 0

        notes = []
        if anomaly_multi_icg:
            notes.append(f"Multi-ICG:{icg_sync_str}")
        if anomaly_multi_ecg:
            notes.append(f"Multi-ECG:{ecg_sync_str}")
        if anomaly_no_icg:
            notes.append("No-ICG")
        if anomaly_no_ecg:
            notes.append("No-ECG")

        self.requests_csv_writer.writerow([
            request_id,
            request_time_utc.isoformat() if request_time_utc else '',
            f"{elapsed_time_s:.1f}",
            icg_response_time.isoformat() if icg_response_time else '',
            f"{icg_duration:.1f}" if icg_duration is not None else '',
            f"{icg_firmware_ts:.6f}" if icg_firmware_ts is not None else '',
            icg_samples,
            icg_sync_count,
            icg_sync_str,
            ecg_response_time.isoformat() if ecg_response_time else '',
            f"{ecg_duration:.1f}" if ecg_duration is not None else '',
            f"{ecg_firmware_ts:.6f}" if ecg_firmware_ts is not None else '',
            ecg_samples,
            ecg_sync_count,
            ecg_sync_str,
            'TRUE' if anomaly_multi_icg else 'FALSE',
            'TRUE' if anomaly_multi_ecg else 'FALSE',
            'TRUE' if anomaly_no_icg else 'FALSE',
            'TRUE' if anomaly_no_ecg else 'FALSE',
            ';'.join(notes)
        ])
        self.requests_csv_file.flush()

    def extract_sync_marks_detailed(self, data_sets: List, device_type: str,
                                    sampling_rate: float) -> Dict[int, Dict]:
        """Extract sync marks with comprehensive metadata

        Returns dict: {sync_num: {...metadata...}}
        """
        sync_marks = {}
        magic = -999990000 if device_type == 'ICG' else -99999

        for packet_idx, data_set in enumerate(data_sets):
            firmware_timestamp = data_set['timestamp']
            data_array = data_set['data']
            total_samples = len(data_array)
            request_id = data_set.get('request_id', 0)
            request_time_utc = data_set.get('request_time_utc', None)

            for position, sample in enumerate(data_array):
                if isinstance(sample, (list, tuple)) and len(sample) > 0:
                    if sample[0] == magic:
                        if len(sample) >= 2:
                            sync_num = sample[1] // 10000 if device_type == 'ICG' else sample[1]

                            # Calculate sample-accurate timestamp
                            samples_after_sync = total_samples - position - 1
                            time_offset = samples_after_sync / sampling_rate
                            calculated_timestamp = firmware_timestamp - time_offset

                            sync_marks[sync_num] = {
                                'found': True,
                                'request_id': request_id,
                                'request_time_utc': request_time_utc,
                                'firmware_timestamp': firmware_timestamp,
                                'position_in_packet': position,
                                'total_samples_in_packet': total_samples,
                                'samples_before_sync': position,
                                'samples_after_sync': samples_after_sync,
                                'calculated_timestamp': calculated_timestamp,
                                'packet_index': packet_idx
                            }

        return sync_marks

    def analyze_sync_markers(self, icg_data_sets: List, ecg_data_sets: List):
        """Comprehensive sync marker analysis with CSV logging"""
        print("  Analyzing sync markers...")

        # Extract all sync markers with metadata
        icg_syncs = self.extract_sync_marks_detailed(icg_data_sets, 'ICG', self.icg_sampling_rate)
        ecg_syncs = self.extract_sync_marks_detailed(ecg_data_sets, 'ECG', self.ecg_sampling_rate)

        print(f"    ICG sync markers found: {len(icg_syncs)}")
        print(f"    ECG sync markers found: {len(ecg_syncs)}")

        # Get all sync numbers
        all_sync_nums = sorted(set(icg_syncs.keys()) | set(ecg_syncs.keys()))

        if not all_sync_nums:
            print("  ✗ No sync markers found")
            return

        # Calculate sample counts between consecutive syncs
        icg_sample_counts = self.calculate_samples_between_syncs(icg_data_sets, icg_syncs, 'ICG')
        ecg_sample_counts = self.calculate_samples_between_syncs(ecg_data_sets, ecg_syncs, 'ECG')

        # Track previous sync for time intervals
        prev_icg_time = None
        prev_ecg_time = None
        cumulative_drift = 0

        # Analyze each sync number
        for sync_num in all_sync_nums:
            icg_info = icg_syncs.get(sync_num, {'found': False})
            ecg_info = ecg_syncs.get(sync_num, {'found': False})

            # Calculate elapsed time
            if icg_info['found']:
                elapsed_time = icg_info['calculated_timestamp'] - self.test_start_time
            elif ecg_info['found']:
                elapsed_time = ecg_info['calculated_timestamp'] - self.test_start_time
            else:
                elapsed_time = 0

            # Sample counts
            icg_samples_since_last = icg_sample_counts.get(sync_num, None)
            ecg_samples_since_last = ecg_sample_counts.get(sync_num, None)

            icg_sample_dev = (icg_samples_since_last - self.expected_samples_per_interval) if icg_samples_since_last else None
            ecg_sample_dev = (ecg_samples_since_last - self.expected_samples_per_interval) if ecg_samples_since_last else None

            # Time intervals
            icg_time_interval = None
            ecg_time_interval = None

            if icg_info['found'] and prev_icg_time is not None:
                icg_time_interval = icg_info['calculated_timestamp'] - prev_icg_time
                prev_icg_time = icg_info['calculated_timestamp']
            elif icg_info['found']:
                prev_icg_time = icg_info['calculated_timestamp']

            if ecg_info['found'] and prev_ecg_time is not None:
                ecg_time_interval = ecg_info['calculated_timestamp'] - prev_ecg_time
                prev_ecg_time = ecg_info['calculated_timestamp']
            elif ecg_info['found']:
                prev_ecg_time = ecg_info['calculated_timestamp']

            # Pairing analysis
            paired = icg_info['found'] and ecg_info['found']
            time_diff_ms = None
            if paired:
                time_diff = abs(icg_info['calculated_timestamp'] - ecg_info['calculated_timestamp'])
                time_diff_ms = time_diff * 1000
                cumulative_drift += time_diff_ms

            # Anomaly detection
            anomaly_icg_missing = not icg_info['found'] and sync_num in ecg_syncs
            anomaly_ecg_missing = not ecg_info['found'] and sync_num in icg_syncs
            anomaly_icg_sample = icg_sample_dev is not None and abs(icg_sample_dev) > 20
            anomaly_ecg_sample = ecg_sample_dev is not None and abs(ecg_sample_dev) > 20
            anomaly_time_interval = (icg_time_interval and abs(icg_time_interval - 1.0) > 0.05) or \
                                   (ecg_time_interval and abs(ecg_time_interval - 1.0) > 0.05)

            # Track anomalies
            if anomaly_icg_missing:
                self.anomalies['missing_icg_syncs'].append(sync_num)
            if anomaly_ecg_missing:
                self.anomalies['missing_ecg_syncs'].append(sync_num)
            if anomaly_icg_sample:
                self.anomalies['sample_count_icg'].append({'sync_num': sync_num, 'count': icg_samples_since_last})
            if anomaly_ecg_sample:
                self.anomalies['sample_count_ecg'].append({'sync_num': sync_num, 'count': ecg_samples_since_last})
            if anomaly_time_interval:
                self.anomalies['time_interval_issues'].append({
                    'sync_num': sync_num,
                    'icg_interval': icg_time_interval,
                    'ecg_interval': ecg_time_interval
                })

            # Build anomaly description
            anomaly_desc = []
            if anomaly_icg_missing:
                anomaly_desc.append("ICG missing")
            if anomaly_ecg_missing:
                anomaly_desc.append("ECG missing")
            if anomaly_icg_sample:
                anomaly_desc.append(f"ICG samples:{icg_samples_since_last}")
            if anomaly_ecg_sample:
                anomaly_desc.append(f"ECG samples:{ecg_samples_since_last}")
            if anomaly_time_interval:
                if icg_time_interval:
                    anomaly_desc.append(f"ICG interval:{icg_time_interval:.3f}s")
                if ecg_time_interval:
                    anomaly_desc.append(f"ECG interval:{ecg_time_interval:.3f}s")

            # Write to sync CSV
            self.write_sync_analysis_row(
                sync_num, elapsed_time,
                icg_info, icg_samples_since_last, icg_sample_dev, icg_time_interval,
                ecg_info, ecg_samples_since_last, ecg_sample_dev, ecg_time_interval,
                paired, time_diff_ms, cumulative_drift,
                anomaly_icg_missing, anomaly_ecg_missing,
                anomaly_icg_sample, anomaly_ecg_sample, anomaly_time_interval,
                ';'.join(anomaly_desc)
            )

        print(f"  ✓ Sync analysis complete: {len(all_sync_nums)} markers analyzed")

    def calculate_samples_between_syncs(self, data_sets: List, sync_marks: Dict, device_type: str) -> Dict:
        """Calculate sample counts between consecutive sync markers"""
        magic = -999990000 if device_type == 'ICG' else -99999
        sample_counts = {}

        sorted_syncs = sorted(sync_marks.items())

        for i in range(len(sorted_syncs) - 1):
            sync_num1, info1 = sorted_syncs[i]
            sync_num2, info2 = sorted_syncs[i + 1]

            packet_idx1 = info1['packet_index']
            packet_idx2 = info2['packet_index']
            pos1 = info1['position_in_packet']
            pos2 = info2['position_in_packet']

            sample_count = 0

            # Same packet
            if packet_idx1 == packet_idx2:
                sample_count = pos2 - pos1 - 1
            else:
                # Samples after first sync in its packet
                sample_count += (info1['total_samples_in_packet'] - pos1 - 1)

                # All samples in intermediate packets
                for packet_idx in range(packet_idx1 + 1, packet_idx2):
                    if packet_idx < len(data_sets):
                        data_array = data_sets[packet_idx]['data']
                        for sample in data_array:
                            if isinstance(sample, (list, tuple)) and len(sample) > 0:
                                if sample[0] != magic:
                                    sample_count += 1

                # Samples before second sync in its packet
                sample_count += pos2

            sample_counts[sync_num1] = sample_count

        return sample_counts

    def write_sync_analysis_row(self, sync_num, elapsed_time,
                                icg_info, icg_samples, icg_sample_dev, icg_interval,
                                ecg_info, ecg_samples, ecg_sample_dev, ecg_interval,
                                paired, time_diff_ms, cumulative_drift,
                                anom_icg_miss, anom_ecg_miss, anom_icg_samp, anom_ecg_samp,
                                anom_interval, anom_desc):
        """Write a single row to sync analysis CSV"""
        if not self.sync_csv_writer:
            return

        self.sync_csv_writer.writerow([
            sync_num,
            f"{elapsed_time:.1f}",
            'TRUE' if icg_info['found'] else 'FALSE',
            icg_info.get('request_id', ''),
            icg_info.get('request_time_utc').isoformat() if icg_info.get('request_time_utc') else '',
            f"{icg_info.get('firmware_timestamp', 0):.6f}" if icg_info['found'] else '',
            icg_info.get('position_in_packet', ''),
            icg_info.get('total_samples_in_packet', ''),
            icg_info.get('samples_before_sync', ''),
            icg_info.get('samples_after_sync', ''),
            f"{icg_info.get('calculated_timestamp', 0):.6f}" if icg_info['found'] else '',
            icg_samples if icg_samples is not None else '',
            f"{icg_sample_dev:+d}" if icg_sample_dev is not None else '',
            f"{icg_interval:.3f}" if icg_interval is not None else '',
            'TRUE' if ecg_info['found'] else 'FALSE',
            ecg_info.get('request_id', ''),
            ecg_info.get('request_time_utc').isoformat() if ecg_info.get('request_time_utc') else '',
            f"{ecg_info.get('firmware_timestamp', 0):.6f}" if ecg_info['found'] else '',
            ecg_info.get('position_in_packet', ''),
            ecg_info.get('total_samples_in_packet', ''),
            ecg_info.get('samples_before_sync', ''),
            ecg_info.get('samples_after_sync', ''),
            f"{ecg_info.get('calculated_timestamp', 0):.6f}" if ecg_info['found'] else '',
            ecg_samples if ecg_samples is not None else '',
            f"{ecg_sample_dev:+d}" if ecg_sample_dev is not None else '',
            f"{ecg_interval:.3f}" if ecg_interval is not None else '',
            'TRUE' if paired else 'FALSE',
            f"{time_diff_ms:.3f}" if time_diff_ms is not None else '',
            f"{cumulative_drift:.3f}",
            'TRUE' if anom_icg_miss else 'FALSE',
            'TRUE' if anom_ecg_miss else 'FALSE',
            'TRUE' if anom_icg_samp else 'FALSE',
            'TRUE' if anom_ecg_samp else 'FALSE',
            'TRUE' if anom_interval else 'FALSE',
            anom_desc
        ])
        self.sync_csv_file.flush()

    def generate_anomaly_report(self):
        """Generate human-readable anomaly report"""
        print("  Generating anomaly report...")

        report = []
        report.append("="*80)
        report.append("ICG-ECG DRIFT ANALYSIS - ANOMALY REPORT")
        report.append("="*80)
        report.append("")

        # Test summary
        report.append("TEST SUMMARY")
        report.append("-" * 80)
        report.append(f"Test Start: {datetime.fromtimestamp(self.test_start_time).isoformat()}")
        report.append(f"Test Duration: {self.test_duration} seconds ({self.test_duration/60:.1f} minutes)")
        report.append(f"Total Requests: {self.request_counter}")
        report.append(f"Data Request Interval: {self.data_interval} seconds")
        report.append(f"ICG Sampling Rate: {self.icg_sampling_rate} Hz")
        report.append(f"ECG Sampling Rate: {self.ecg_sampling_rate} Hz")
        report.append("")

        # Anomaly statistics
        report.append("ANOMALY STATISTICS")
        report.append("-" * 80)

        total_anomalies = sum([
            len(self.anomalies['missing_icg_syncs']),
            len(self.anomalies['missing_ecg_syncs']),
            len(self.anomalies['sample_count_icg']),
            len(self.anomalies['sample_count_ecg']),
            len(self.anomalies['time_interval_issues']),
            len(self.anomalies['multiple_syncs_icg']),
            len(self.anomalies['multiple_syncs_ecg']),
            len(self.anomalies['no_data_icg']),
            len(self.anomalies['no_data_ecg'])
        ])

        report.append(f"Total Anomalies Detected: {total_anomalies}")
        report.append("")

        # Missing sync markers
        if self.anomalies['missing_icg_syncs']:
            report.append(f"Missing ICG Sync Markers: {len(self.anomalies['missing_icg_syncs'])}")
            report.append(f"  Sync numbers: {self.anomalies['missing_icg_syncs'][:50]}")
            if len(self.anomalies['missing_icg_syncs']) > 50:
                report.append(f"  ... and {len(self.anomalies['missing_icg_syncs']) - 50} more")
        else:
            report.append("Missing ICG Sync Markers: 0")

        if self.anomalies['missing_ecg_syncs']:
            report.append(f"Missing ECG Sync Markers: {len(self.anomalies['missing_ecg_syncs'])}")
            report.append(f"  Sync numbers: {self.anomalies['missing_ecg_syncs'][:50]}")
            if len(self.anomalies['missing_ecg_syncs']) > 50:
                report.append(f"  ... and {len(self.anomalies['missing_ecg_syncs']) - 50} more")
        else:
            report.append("Missing ECG Sync Markers: 0")

        report.append("")

        # Sample count issues
        if self.anomalies['sample_count_icg']:
            report.append(f"ICG Sample Count Issues: {len(self.anomalies['sample_count_icg'])}")
            for issue in self.anomalies['sample_count_icg'][:10]:
                report.append(f"  Sync {issue['sync_num']}: {issue['count']} samples "
                            f"(expected {self.expected_samples_per_interval})")
            if len(self.anomalies['sample_count_icg']) > 10:
                report.append(f"  ... and {len(self.anomalies['sample_count_icg']) - 10} more")
        else:
            report.append("ICG Sample Count Issues: 0")

        if self.anomalies['sample_count_ecg']:
            report.append(f"ECG Sample Count Issues: {len(self.anomalies['sample_count_ecg'])}")
            for issue in self.anomalies['sample_count_ecg'][:10]:
                report.append(f"  Sync {issue['sync_num']}: {issue['count']} samples "
                            f"(expected {self.expected_samples_per_interval})")
            if len(self.anomalies['sample_count_ecg']) > 10:
                report.append(f"  ... and {len(self.anomalies['sample_count_ecg']) - 10} more")
        else:
            report.append("ECG Sample Count Issues: 0")

        report.append("")

        # Multiple syncs in packet
        if self.anomalies['multiple_syncs_icg']:
            report.append(f"Multiple ICG Syncs in Single Packet: {len(self.anomalies['multiple_syncs_icg'])}")
            for anomaly in self.anomalies['multiple_syncs_icg'][:10]:
                report.append(f"  Request {anomaly['request_id']}: {anomaly['sync_numbers']}")
            if len(self.anomalies['multiple_syncs_icg']) > 10:
                report.append(f"  ... and {len(self.anomalies['multiple_syncs_icg']) - 10} more")
        else:
            report.append("Multiple ICG Syncs in Single Packet: 0")

        if self.anomalies['multiple_syncs_ecg']:
            report.append(f"Multiple ECG Syncs in Single Packet: {len(self.anomalies['multiple_syncs_ecg'])}")
            for anomaly in self.anomalies['multiple_syncs_ecg'][:10]:
                report.append(f"  Request {anomaly['request_id']}: {anomaly['sync_numbers']}")
            if len(self.anomalies['multiple_syncs_ecg']) > 10:
                report.append(f"  ... and {len(self.anomalies['multiple_syncs_ecg']) - 10} more")
        else:
            report.append("Multiple ECG Syncs in Single Packet: 0")

        report.append("")

        # No data received
        if self.anomalies['no_data_icg']:
            report.append(f"No ICG Data Received: {len(self.anomalies['no_data_icg'])} requests")
        if self.anomalies['no_data_ecg']:
            report.append(f"No ECG Data Received: {len(self.anomalies['no_data_ecg'])} requests")

        report.append("")

        # Timing issues
        if self.anomalies['time_interval_issues']:
            report.append(f"Time Interval Issues: {len(self.anomalies['time_interval_issues'])}")
            for issue in self.anomalies['time_interval_issues'][:10]:
                if issue.get('icg_interval'):
                    report.append(f"  Sync {issue['sync_num']}: ICG interval {issue['icg_interval']:.3f}s")
                if issue.get('ecg_interval'):
                    report.append(f"  Sync {issue['sync_num']}: ECG interval {issue['ecg_interval']:.3f}s")
            if len(self.anomalies['time_interval_issues']) > 10:
                report.append(f"  ... and {len(self.anomalies['time_interval_issues']) - 10} more")
        else:
            report.append("Time Interval Issues: 0")

        report.append("")
        report.append("="*80)
        report.append("RECOMMENDATIONS")
        report.append("="*80)

        if self.anomalies['multiple_syncs_icg'] or self.anomalies['multiple_syncs_ecg']:
            report.append("- Buffer overflow detected: Multiple sync markers in single packet")
            report.append("  → Increase firmware buffer size or reduce sampling rate")

        if self.anomalies['sample_count_icg'] or self.anomalies['sample_count_ecg']:
            report.append("- Sample drops detected: Counts deviate from expected 400")
            report.append("  → Check firmware buffer management and SPI timing")

        if self.anomalies['missing_icg_syncs'] or self.anomalies['missing_ecg_syncs']:
            report.append("- Missing sync markers: Gaps in sync number sequence")
            report.append("  → Check firmware sync injection timing and buffer flow")

        if self.anomalies['time_interval_issues']:
            report.append("- Timing drift detected: Intervals deviate from 1.0 second")
            report.append("  → Check system clock stability and timing loops")

        report.append("")
        report.append("="*80)

        # Write to file
        with open(self.anomaly_report_filename, 'w') as f:
            f.write('\n'.join(report))

        print(f"  ✓ Anomaly report saved: {self.anomaly_report_filename}")

    def init_requests_csv(self):
        """Initialize requests log CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.requests_csv_filename = f"requests_log_{timestamp}.csv"
        self.requests_csv_file = open(self.requests_csv_filename, 'w', newline='')
        self.requests_csv_writer = csv.writer(self.requests_csv_file)

        self.requests_csv_writer.writerow([
            'request_id', 'request_time_utc', 'elapsed_time_s',
            'icg_response_time_utc', 'icg_request_duration_ms', 'icg_firmware_timestamp',
            'icg_packet_samples', 'icg_sync_count', 'icg_sync_numbers',
            'ecg_response_time_utc', 'ecg_request_duration_ms', 'ecg_firmware_timestamp',
            'ecg_packet_samples', 'ecg_sync_count', 'ecg_sync_numbers',
            'anomaly_multiple_icg_syncs', 'anomaly_multiple_ecg_syncs',
            'anomaly_no_icg_data', 'anomaly_no_ecg_data', 'notes'
        ])
        self.requests_csv_file.flush()
        print(f"  Requests log: {self.requests_csv_filename}")

    def init_sync_csv(self):
        """Initialize sync analysis CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sync_csv_filename = f"sync_analysis_{timestamp}.csv"
        self.sync_csv_file = open(self.sync_csv_filename, 'w', newline='')
        self.sync_csv_writer = csv.writer(self.sync_csv_file)

        self.sync_csv_writer.writerow([
            'sync_num', 'elapsed_time_s',
            'icg_found', 'icg_request_id', 'icg_request_time_utc', 'icg_firmware_timestamp',
            'icg_position_in_packet', 'icg_total_samples_in_packet',
            'icg_samples_before_sync', 'icg_samples_after_sync', 'icg_calculated_timestamp',
            'icg_samples_since_last_sync', 'icg_sample_deviation', 'icg_time_since_last_sync',
            'ecg_found', 'ecg_request_id', 'ecg_request_time_utc', 'ecg_firmware_timestamp',
            'ecg_position_in_packet', 'ecg_total_samples_in_packet',
            'ecg_samples_before_sync', 'ecg_samples_after_sync', 'ecg_calculated_timestamp',
            'ecg_samples_since_last_sync', 'ecg_sample_deviation', 'ecg_time_since_last_sync',
            'paired', 'time_diff_ms', 'drift_cumulative_ms',
            'anomaly_icg_missing', 'anomaly_ecg_missing',
            'anomaly_icg_sample_count', 'anomaly_ecg_sample_count',
            'anomaly_time_interval', 'anomaly_description'
        ])
        self.sync_csv_file.flush()
        print(f"  Sync analysis log: {self.sync_csv_filename}")

    def init_anomaly_report(self):
        """Initialize anomaly report file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.anomaly_report_filename = f"anomalies_report_{timestamp}.txt"
        print(f"  Anomaly report: {self.anomaly_report_filename}")

    def close_all_files(self):
        """Close all open files"""
        if self.requests_csv_file:
            self.requests_csv_file.close()
        if self.sync_csv_file:
            self.sync_csv_file.close()

    def save_json_results(self, icg_syncs_count: int, ecg_syncs_count: int) -> str:
        """Save complete results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"icg_ecg_drift_1hour_results_{timestamp}.json"

        output = {
            'test_name': 'ICG-ECG 1-Hour Drift Analysis (Enhanced Debug)',
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': self.test_duration,
            'configuration': {
                'icg': self.icg_config,
                'ecg': self.ecg_config,
                'icg_sampling_rate': self.icg_sampling_rate,
                'ecg_sampling_rate': self.ecg_sampling_rate,
                'sync_threshold_ms': self.sync_threshold_ms,
                'data_interval_seconds': self.data_interval
            },
            'results': {
                'total_requests': self.request_counter,
                'icg_sync_count': icg_syncs_count,
                'ecg_sync_count': ecg_syncs_count,
                'anomaly_summary': {
                    'missing_icg_syncs': len(self.anomalies['missing_icg_syncs']),
                    'missing_ecg_syncs': len(self.anomalies['missing_ecg_syncs']),
                    'sample_count_issues_icg': len(self.anomalies['sample_count_icg']),
                    'sample_count_issues_ecg': len(self.anomalies['sample_count_ecg']),
                    'multiple_syncs_icg': len(self.anomalies['multiple_syncs_icg']),
                    'multiple_syncs_ecg': len(self.anomalies['multiple_syncs_ecg']),
                    'no_data_icg': len(self.anomalies['no_data_icg']),
                    'no_data_ecg': len(self.anomalies['no_data_ecg']),
                    'time_interval_issues': len(self.anomalies['time_interval_issues'])
                }
            },
            'output_files': {
                'requests_log': self.requests_csv_filename,
                'sync_analysis': self.sync_csv_filename,
                'anomaly_report': self.anomaly_report_filename
            }
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"  ✓ Results saved to: {filename}")
        return filename

    def run_test(self) -> bool:
        """Run the complete 1-hour drift test with enhanced debugging"""
        print("\n" + "="*80)
        print("ICG-ECG 1-HOUR DRIFT ANALYSIS TEST (ENHANCED DEBUG)")
        print("="*80)
        print(f"Test duration: {self.test_duration} seconds ({self.test_duration/60:.1f} minutes)")
        print(f"Sync threshold: {self.sync_threshold_ms} ms")
        print(f"Data interval: {self.data_interval} seconds")
        print(f"Expected samples between markers: {self.expected_samples_per_interval}")
        print("="*80)

        # Initialize CSV files
        self.init_requests_csv()
        self.init_sync_csv()
        self.init_anomaly_report()

        # Connect to devices
        if not self.connect_all():
            print("✗ Failed to connect to devices. Exiting.")
            self.close_all_files()
            return False

        try:
            # Prepare devices
            print("\nPreparing devices...")
            print("  Stopping devices...")
            self.stop_icg()
            self.stop_ecg()

            time.sleep(2)
            self.flush_buffers()

            # Configure devices
            if not self.configure_devices():
                print("✗ Failed to configure devices. Exiting.")
                return False

            # Wait for stabilization
            print("  Waiting 2 seconds for devices to stabilize...")
            time.sleep(2)

            # Collect data for 1 hour
            print("\nStarting data collection...")
            icg_data, ecg_data = self.collect_data(duration=self.test_duration)

            # Analyze sync markers (writes to sync_analysis CSV)
            print("\nAnalyzing sync markers...")
            self.analyze_sync_markers(icg_data, ecg_data)

            # Generate anomaly report
            self.generate_anomaly_report()

            # Save JSON results
            print("\nSaving results...")
            icg_syncs = self.extract_sync_marks_detailed(icg_data, 'ICG', self.icg_sampling_rate)
            ecg_syncs = self.extract_sync_marks_detailed(ecg_data, 'ECG', self.ecg_sampling_rate)
            json_filename = self.save_json_results(len(icg_syncs), len(ecg_syncs))

            # Print summary
            print("\n" + "="*80)
            print("TEST COMPLETE")
            print("="*80)
            print(f"\nOutput files generated:")
            print(f"  1. {self.requests_csv_filename} - Request log ({self.request_counter} requests)")
            print(f"  2. {self.sync_csv_filename} - Sync analysis")
            print(f"  3. {self.anomaly_report_filename} - Anomaly report")
            print(f"  4. {json_filename} - JSON results")
            print("\n" + "="*80)

            return True

        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
            print("Saving partial results...")
            return False
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close_all_files()
            self.disconnect_all()


def main():
    """Main entry point"""

    # Parse command line arguments
    host = "localhost"
    sync_threshold_ms = 50.0
    data_interval_seconds = 0.2

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            sync_threshold_ms = float(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid threshold value '{sys.argv[2]}'. Using default 50ms.")
    if len(sys.argv) > 3:
        try:
            data_interval_seconds = float(sys.argv[3])
            if data_interval_seconds <= 0:
                print(f"Error: Data interval must be positive. Using default 0.2s.")
                data_interval_seconds = 0.2
        except ValueError:
            print(f"Error: Invalid data interval '{sys.argv[3]}'. Using default 0.2s.")
            data_interval_seconds = 0.2

    print(f"Connecting to services on: {host}")
    print(f"Sync threshold: {sync_threshold_ms}ms")
    print(f"Data request interval: {data_interval_seconds}s")

    # Create tester and run test
    tester = DriftTester(host=host, sync_threshold_ms=sync_threshold_ms,
                        data_interval_seconds=data_interval_seconds)
    success = tester.run_test()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
