#!/usr/bin/env python3
"""
ICG-ECG 1-Hour Drift Analysis Test

This script tests a single ICG/ECG configuration for 1 hour to analyze timing drift
between the two sensors and validate sample rate consistency.

Test Configuration:
- ICG: 400 Hz, stimulate_table_index=4, stimulate_frequency=7
- ECG: R2=4, R3=16 (400 Hz)
- Duration: 1 hour (3600 seconds)
- Data request interval: Configurable (default: 0.2 seconds)

Analysis:
- Drift tracking over time
- Sample count validation (should be 400 between markers)
- Statistical analysis of synchronization quality
- Trend detection (drift increasing/decreasing)

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
    python3 test_icg_ecg_drift_1hour.py 192.168.1.100 50 0.3

Output:
    - CSV file: Detailed per-sync-mark data
    - JSON file: Complete test results and statistics
    - Plot 1: Drift over time
    - Plot 2: Sample count validation
    - Plot 3: Drift distribution histogram
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


class DriftTester:
    """Tests long-term drift between ICG and ECG data streams"""

    def __init__(self, host: str = "localhost", sync_threshold_ms: float = 50.0,
                 data_interval_seconds: float = 0.2):
        self.host = host
        self.icg_client = DeviceClient(host, 30009, "ICG (MAX30009)")
        self.ecg_client = DeviceClient(host, 1293, "ECG (ADS1293)")

        # Configurable sync threshold (in milliseconds)
        self.sync_threshold_ms = sync_threshold_ms
        self.sync_threshold = sync_threshold_ms / 1000.0  # Convert to seconds

        # Configurable data request interval (in seconds)
        self.data_interval = data_interval_seconds

        # Fixed test configuration
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

        # Expected sampling rates
        self.icg_sampling_rate = 400  # Hz
        self.ecg_sampling_rate = 400  # Hz (R2=4, R3=16)
        self.expected_samples_per_interval = 400  # 400 Hz × 1 second

        # Test duration
        self.test_duration = 3600  # 1 hour in seconds

        # CSV file setup
        self.csv_filename = None
        self.csv_file = None
        self.csv_writer = None

        # Results storage
        self.drift_data = []
        self.test_start_time = None

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
        """Collect data from both sensors for specified duration

        Args:
            duration: Collection duration in seconds (default: 3600 = 1 hour)

        Returns:
            Tuple of (icg_data_sets, ecg_data_sets)
        """
        print(f"  Starting data collection for {duration} seconds ({duration/60:.1f} minutes)...")

        icg_data_sets = []
        ecg_data_sets = []

        start_time = time.time()
        self.test_start_time = start_time
        iteration = 0
        last_progress_time = start_time

        while time.time() - start_time < duration:
            iteration += 1

            # Get data from both sensors
            icg_data = self.icg_client.get_data()
            ecg_data = self.ecg_client.get_data()

            if icg_data and 'data' in icg_data:
                try:
                    if 'timestamp' in icg_data:
                        firmware_timestamp = parse_firmware_timestamp(icg_data['timestamp'])
                    else:
                        firmware_timestamp = time.time()
                        print(f"    Warning: ICG packet missing firmware timestamp")

                    icg_data_sets.append({
                        'timestamp': firmware_timestamp,
                        'data': icg_data['data']
                    })
                except ValueError as e:
                    print(f"    Warning: Failed to parse ICG timestamp: {e}")
                    icg_data_sets.append({
                        'timestamp': time.time(),
                        'data': icg_data['data']
                    })

            if ecg_data and 'data' in ecg_data:
                try:
                    if 'timestamp' in ecg_data:
                        firmware_timestamp = parse_firmware_timestamp(ecg_data['timestamp'])
                    else:
                        firmware_timestamp = time.time()
                        print(f"    Warning: ECG packet missing firmware timestamp")

                    ecg_data_sets.append({
                        'timestamp': firmware_timestamp,
                        'data': ecg_data['data']
                    })
                except ValueError as e:
                    print(f"    Warning: Failed to parse ECG timestamp: {e}")
                    ecg_data_sets.append({
                        'timestamp': time.time(),
                        'data': ecg_data['data']
                    })

            # Progress indicator every 60 seconds (1 minute)
            current_time = time.time()
            if current_time - last_progress_time >= 60:
                elapsed = current_time - start_time
                remaining = duration - elapsed
                print(f"    Progress: {elapsed/60:.1f}/{duration/60:.1f} min "
                      f"(ICG: {len(icg_data_sets)} sets, ECG: {len(ecg_data_sets)} sets, "
                      f"Remaining: {remaining/60:.1f} min)")
                last_progress_time = current_time

            # Configurable delay between requests
            time.sleep(self.data_interval)

        print(f"  ✓ Data collection complete: ICG={len(icg_data_sets)} sets, ECG={len(ecg_data_sets)} sets")
        return icg_data_sets, ecg_data_sets

    def extract_sync_marks_with_samples(self, data_sets: List, device_type: str = 'ECG',
                                       sampling_rate: float = 400) -> List[Tuple]:
        """Extract sync marks with sample-accurate timestamps and track sample positions

        Returns:
            List of tuples (sync_number, actual_timestamp, position_in_packet,
                          total_samples_in_packet, packet_index)
        """
        sync_marks = []

        # Different magic numbers for ECG vs ICG
        ecg_magic = -99999
        icg_magic = -999990000

        for packet_index, data_set in enumerate(data_sets):
            firmware_timestamp = data_set['timestamp']
            data_array = data_set['data']
            total_samples = len(data_array)

            for position, sample in enumerate(data_array):
                if isinstance(sample, (list, tuple)) and len(sample) > 0:
                    first_val = sample[0]

                    # Check for ECG sync mark
                    if device_type == 'ECG' and first_val == ecg_magic:
                        if len(sample) >= 2:
                            sync_num = sample[1]
                            # Calculate sample-accurate timestamp
                            samples_after_sync = total_samples - position - 1
                            time_offset = samples_after_sync / sampling_rate
                            actual_timestamp = firmware_timestamp - time_offset

                            sync_marks.append((sync_num, actual_timestamp, position,
                                             total_samples, packet_index))

                    # Check for ICG sync mark (scaled by 10000)
                    elif device_type == 'ICG' and first_val == icg_magic:
                        if len(sample) >= 2:
                            sync_num = sample[1] // 10000
                            # Calculate sample-accurate timestamp
                            samples_after_sync = total_samples - position - 1
                            time_offset = samples_after_sync / sampling_rate
                            actual_timestamp = firmware_timestamp - time_offset

                            sync_marks.append((sync_num, actual_timestamp, position,
                                             total_samples, packet_index))

        return sync_marks

    def count_samples_between_syncs(self, data_sets: List, sync_marks: List,
                                   device_type: str = 'ECG') -> Dict:
        """Count actual samples between consecutive sync marks

        Args:
            data_sets: List of data packets
            sync_marks: List of sync mark tuples (sync_num, timestamp, pos, total, packet_idx)
            device_type: 'ECG' or 'ICG'

        Returns:
            Dict mapping sync_num to sample count between this sync and next sync
        """
        sample_counts = {}

        # Magic numbers to identify sync marks
        ecg_magic = -99999
        icg_magic = -999990000
        magic = ecg_magic if device_type == 'ECG' else icg_magic

        for i in range(len(sync_marks) - 1):
            sync_num1, _, pos1, total1, packet_idx1 = sync_marks[i]
            sync_num2, _, pos2, total2, packet_idx2 = sync_marks[i + 1]

            # Count samples between the two sync marks
            sample_count = 0

            # Case 1: Both syncs in same packet (rare but possible)
            if packet_idx1 == packet_idx2:
                # Samples between pos1 and pos2 (excluding the sync marks themselves)
                sample_count = pos2 - pos1 - 1

            # Case 2: Syncs in different packets
            else:
                # Count samples after first sync in its packet
                sample_count += (total1 - pos1 - 1)

                # Count all samples in intermediate packets
                for packet_idx in range(packet_idx1 + 1, packet_idx2):
                    if packet_idx < len(data_sets):
                        data_array = data_sets[packet_idx]['data']
                        # Count all non-sync samples
                        for sample in data_array:
                            if isinstance(sample, (list, tuple)) and len(sample) > 0:
                                if sample[0] != magic:
                                    sample_count += 1

                # Count samples before second sync in its packet
                sample_count += pos2

            sample_counts[sync_num1] = sample_count

        return sample_counts

    def analyze_drift(self, icg_syncs: List[Tuple], ecg_syncs: List[Tuple],
                     icg_data_sets: List, ecg_data_sets: List) -> Dict:
        """Analyze drift between ICG and ECG over time

        Returns detailed drift analysis with sample count validation
        """
        # Extract sync dictionaries
        icg_sync_dict = {sync_num: (timestamp, pos, total, pkt_idx)
                        for sync_num, timestamp, pos, total, pkt_idx in icg_syncs}
        ecg_sync_dict = {sync_num: (timestamp, pos, total, pkt_idx)
                        for sync_num, timestamp, pos, total, pkt_idx in ecg_syncs}

        # Find common sync numbers
        icg_nums = set(icg_sync_dict.keys())
        ecg_nums = set(ecg_sync_dict.keys())
        common_nums = sorted(icg_nums & ecg_nums)

        if not common_nums:
            return {
                'success': False,
                'error': 'No common sync marks found',
                'drift_data': []
            }

        # Count samples between sync marks
        print("  Counting samples between sync marks...")
        icg_sample_counts = self.count_samples_between_syncs(icg_data_sets, icg_syncs, 'ICG')
        ecg_sample_counts = self.count_samples_between_syncs(ecg_data_sets, ecg_syncs, 'ECG')

        # Analyze each common sync mark
        drift_data = []
        for sync_num in common_nums:
            icg_time, _, _, _ = icg_sync_dict[sync_num]
            ecg_time, _, _, _ = ecg_sync_dict[sync_num]

            time_diff = abs(icg_time - ecg_time)
            elapsed_time = icg_time - self.test_start_time if self.test_start_time else 0

            # Get sample counts
            icg_samples = icg_sample_counts.get(sync_num, None)
            ecg_samples = ecg_sample_counts.get(sync_num, None)

            drift_data.append({
                'sync_num': sync_num,
                'icg_timestamp': icg_time,
                'ecg_timestamp': ecg_time,
                'time_diff_ms': time_diff * 1000,
                'elapsed_time_s': elapsed_time,
                'icg_samples_between': icg_samples,
                'ecg_samples_between': ecg_samples
            })

        # Calculate statistics using standard Python
        time_diffs = [d['time_diff_ms'] for d in drift_data]

        mean_drift = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        min_drift = min(time_diffs) if time_diffs else 0
        max_drift = max(time_diffs) if time_diffs else 0

        # Calculate standard deviation
        if len(time_diffs) > 1:
            variance = sum((x - mean_drift) ** 2 for x in time_diffs) / len(time_diffs)
            std_drift = variance ** 0.5
        else:
            std_drift = 0

        # Simple linear regression for drift trend
        elapsed_times = [d['elapsed_time_s'] for d in drift_data]
        if len(elapsed_times) > 1 and len(time_diffs) > 1:
            # Calculate slope using least squares
            n = len(elapsed_times)
            sum_x = sum(elapsed_times)
            sum_y = sum(time_diffs)
            sum_xy = sum(x * y for x, y in zip(elapsed_times, time_diffs))
            sum_xx = sum(x * x for x in elapsed_times)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            drift_rate = slope * 3600  # ms per hour
        else:
            drift_rate = 0

        # Sample count statistics
        icg_sample_list = [d['icg_samples_between'] for d in drift_data if d['icg_samples_between'] is not None]
        ecg_sample_list = [d['ecg_samples_between'] for d in drift_data if d['ecg_samples_between'] is not None]

        icg_avg_samples = sum(icg_sample_list) / len(icg_sample_list) if icg_sample_list else 0
        ecg_avg_samples = sum(ecg_sample_list) / len(ecg_sample_list) if ecg_sample_list else 0

        # Standard deviation for sample counts
        if len(icg_sample_list) > 1:
            icg_variance = sum((x - icg_avg_samples) ** 2 for x in icg_sample_list) / len(icg_sample_list)
            icg_std_samples = icg_variance ** 0.5
        else:
            icg_std_samples = 0

        if len(ecg_sample_list) > 1:
            ecg_variance = sum((x - ecg_avg_samples) ** 2 for x in ecg_sample_list) / len(ecg_sample_list)
            ecg_std_samples = ecg_variance ** 0.5
        else:
            ecg_std_samples = 0

        return {
            'success': True,
            'drift_data': drift_data,
            'total_sync_marks': len(common_nums),
            'icg_sync_count': len(icg_syncs),
            'ecg_sync_count': len(ecg_syncs),
            'common_sync_count': len(common_nums),
            'statistics': {
                'mean_drift_ms': mean_drift,
                'std_drift_ms': std_drift,
                'min_drift_ms': min_drift,
                'max_drift_ms': max_drift,
                'drift_rate_ms_per_hour': drift_rate,
                'icg_avg_samples_between': icg_avg_samples,
                'icg_std_samples_between': icg_std_samples,
                'ecg_avg_samples_between': ecg_avg_samples,
                'ecg_std_samples_between': ecg_std_samples,
                'expected_samples': self.expected_samples_per_interval
            }
        }

    def print_plot_instructions(self, csv_filename: str, json_filename: str):
        """Print instructions for generating plots on local machine"""
        print("\n" + "="*80)
        print("PLOT GENERATION")
        print("="*80)
        print("Data saved successfully. To generate plots on your local machine:")
        print(f"\n1. Copy these files to your local machine:")
        print(f"   - {csv_filename}")
        print(f"   - {json_filename}")
        print(f"   - plot_drift_results.py")
        print(f"\n2. Run the plotting script:")
        print(f"   python3 plot_drift_results.py {csv_filename}")
        print(f"\n   Or specify JSON file:")
        print(f"   python3 plot_drift_results.py {json_filename}")
        print("\n3. Plots will be generated in the same directory:")
        print("   - drift_over_time_*.png")
        print("   - sample_count_validation_*.png")
        print("   - drift_histogram_*.png")
        print("="*80)

    def init_csv(self):
        """Initialize CSV file for logging results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f"icg_ecg_drift_1hour_{timestamp}.csv"

        self.csv_file = open(self.csv_filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        # Write header
        self.csv_writer.writerow([
            'sync_num',
            'icg_timestamp',
            'ecg_timestamp',
            'time_diff_ms',
            'elapsed_time_s',
            'elapsed_time_min',
            'icg_samples_between',
            'ecg_samples_between',
            'icg_sample_deviation',
            'ecg_sample_deviation'
        ])
        self.csv_file.flush()

        print(f"  CSV log: {self.csv_filename}")

    def write_csv_data(self, drift_data: List[Dict]):
        """Write drift data to CSV"""
        if not self.csv_writer:
            return

        print("  Writing data to CSV...")
        for data_point in drift_data:
            icg_samples = data_point.get('icg_samples_between', None)
            ecg_samples = data_point.get('ecg_samples_between', None)

            # Calculate deviation from expected
            icg_deviation = (icg_samples - self.expected_samples_per_interval) if icg_samples is not None else None
            ecg_deviation = (ecg_samples - self.expected_samples_per_interval) if ecg_samples is not None else None

            self.csv_writer.writerow([
                data_point['sync_num'],
                f"{data_point['icg_timestamp']:.6f}",
                f"{data_point['ecg_timestamp']:.6f}",
                f"{data_point['time_diff_ms']:.3f}",
                f"{data_point['elapsed_time_s']:.1f}",
                f"{data_point['elapsed_time_s'] / 60:.2f}",
                icg_samples if icg_samples is not None else '',
                ecg_samples if ecg_samples is not None else '',
                f"{icg_deviation:+d}" if icg_deviation is not None else '',
                f"{ecg_deviation:+d}" if ecg_deviation is not None else ''
            ])

        self.csv_file.flush()
        print(f"  ✓ CSV written: {self.csv_filename}")

    def close_csv(self):
        """Close CSV file"""
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None

    def save_json_results(self, analysis_result: Dict) -> str:
        """Save complete results to JSON file

        Returns:
            str: Filename of saved JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"icg_ecg_drift_1hour_results_{timestamp}.json"

        output = {
            'test_name': 'ICG-ECG 1-Hour Drift Analysis',
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
            'results': analysis_result,
            'csv_file': self.csv_filename
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"  ✓ Results saved to: {filename}")
        return filename

    def print_summary(self, analysis_result: Dict):
        """Print test summary"""
        print("\n" + "="*80)
        print("1-HOUR DRIFT ANALYSIS SUMMARY")
        print("="*80)

        if not analysis_result['success']:
            print(f"✗ Test failed: {analysis_result.get('error', 'Unknown error')}")
            return

        stats = analysis_result['statistics']

        print(f"\nSync Marks:")
        print(f"  ICG sync marks found: {analysis_result['icg_sync_count']}")
        print(f"  ECG sync marks found: {analysis_result['ecg_sync_count']}")
        print(f"  Common sync marks: {analysis_result['common_sync_count']}")

        print(f"\nDrift Statistics:")
        print(f"  Mean drift: {stats['mean_drift_ms']:.3f} ms")
        print(f"  Std deviation: {stats['std_drift_ms']:.3f} ms")
        print(f"  Min drift: {stats['min_drift_ms']:.3f} ms")
        print(f"  Max drift: {stats['max_drift_ms']:.3f} ms")
        print(f"  Drift rate: {stats['drift_rate_ms_per_hour']:.3f} ms/hour")

        print(f"\nSample Count Validation:")
        print(f"  Expected samples between markers: {stats['expected_samples']}")
        print(f"  ICG average samples: {stats['icg_avg_samples_between']:.1f} "
              f"(±{stats['icg_std_samples_between']:.1f})")
        print(f"  ECG average samples: {stats['ecg_avg_samples_between']:.1f} "
              f"(±{stats['ecg_std_samples_between']:.1f})")

        # Check if drift exceeds threshold
        if stats['max_drift_ms'] > self.sync_threshold_ms:
            print(f"\n⚠ WARNING: Max drift ({stats['max_drift_ms']:.3f} ms) exceeds "
                  f"threshold ({self.sync_threshold_ms} ms)")
        else:
            print(f"\n✓ PASS: All drift values within threshold ({self.sync_threshold_ms} ms)")

        # Check sample count accuracy
        icg_deviation_pct = abs(stats['icg_avg_samples_between'] - stats['expected_samples']) / stats['expected_samples'] * 100
        ecg_deviation_pct = abs(stats['ecg_avg_samples_between'] - stats['expected_samples']) / stats['expected_samples'] * 100

        if icg_deviation_pct > 5 or ecg_deviation_pct > 5:
            print(f"⚠ WARNING: Sample count deviates more than 5% from expected")
            print(f"  ICG deviation: {icg_deviation_pct:.1f}%")
            print(f"  ECG deviation: {ecg_deviation_pct:.1f}%")
        else:
            print(f"✓ PASS: Sample counts within 5% tolerance")

        print("\n" + "="*80)

    def run_test(self) -> bool:
        """Run the complete 1-hour drift test"""
        print("\n" + "="*80)
        print("ICG-ECG 1-HOUR DRIFT ANALYSIS TEST")
        print("="*80)
        print(f"Test duration: {self.test_duration} seconds ({self.test_duration/60:.1f} minutes)")
        print(f"Sync threshold: {self.sync_threshold_ms} ms")
        print(f"Expected samples between markers: {self.expected_samples_per_interval}")
        print("="*80)

        # Initialize CSV
        self.init_csv()

        # Connect to devices
        if not self.connect_all():
            print("✗ Failed to connect to devices. Exiting.")
            self.close_csv()
            return False

        try:
            # Stop devices and flush buffers
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

            # Extract sync marks
            print("\nAnalyzing sync marks with sample-accurate timing...")
            icg_syncs = self.extract_sync_marks_with_samples(icg_data, device_type='ICG',
                                                            sampling_rate=self.icg_sampling_rate)
            ecg_syncs = self.extract_sync_marks_with_samples(ecg_data, device_type='ECG',
                                                            sampling_rate=self.ecg_sampling_rate)

            print(f"  ICG sync marks found: {len(icg_syncs)}")
            print(f"  ECG sync marks found: {len(ecg_syncs)}")

            # Analyze drift
            print("\nAnalyzing drift and sample counts...")
            analysis_result = self.analyze_drift(icg_syncs, ecg_syncs, icg_data, ecg_data)

            # Write to CSV
            if analysis_result['success']:
                self.write_csv_data(analysis_result['drift_data'])

            # Save JSON results
            print("\nSaving results...")
            json_filename = self.save_json_results(analysis_result)

            # Print summary
            self.print_summary(analysis_result)

            # Print instructions for generating plots locally
            self.print_plot_instructions(self.csv_filename, json_filename)

            return analysis_result['success']

        except KeyboardInterrupt:
            print("\n\n⚠ Test interrupted by user (Ctrl+C)")
            print("Saving partial results...")
            return False
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close_csv()
            self.disconnect_all()


def main():
    """Main entry point"""

    # Parse command line arguments
    host = "localhost"
    sync_threshold_ms = 50.0  # Default: 50ms
    data_interval_seconds = 0.2  # Default: 0.2 seconds

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
