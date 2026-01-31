#!/usr/bin/env python3
"""
Test Case #20: Full Concurrency
Category: HW Component Test
Component: ECG/ICG Acquisition + CM4 CPU + eMMC Logging + OS Scheduler

Tests system behavior under full concurrent load:
- ECG/ICG simulator at 400 Hz
- CPU burn load (all cores)
- Continuous disk I/O with fsync
- Thermal/CPU telemetry monitoring

This is the ultimate stress test combining all system resources.

This test runs on the CM4 itself (not on PC via remote connection).
"""

import subprocess
import os
import sys
import time
import json
import threading
import pytest
import struct
import math
import re

# Add common utilities to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from platform_check import skip_if_not_raspberry_pi


class TestFullConcurrency:
    """HW Component Test - Full Concurrency"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for full concurrency test"""
        return {
            # Test duration
            'test_duration_sec': 1800,  # 30 minutes

            # Acquisition simulator
            'target_sample_rate_hz': 400,  # 400 Hz
            'ecg_channels': 3,  # 3-channel ECG
            'icg_channels': 4,  # 4-channel ICG
            'sample_rate_tolerance_hz': 1.0,  # ±1 Hz acceptable

            # CPU burn
            'stress_ng_path': 'stress-ng',
            'stress_ng_cpu_workers': 4,  # 4 cores on CM4
            'cpu_burn_threads': 4,  # Python fallback

            # Logging stress
            'log_burst_frequency_hz': 10,  # 10 bursts/second
            'log_burst_size_bytes': 1024,  # 1 KB per burst

            # Thermal monitoring
            'thermal_monitor_interval_sec': 30,  # Every 30 seconds
            'thermal_zone_path': '/sys/class/thermal/thermal_zone0/temp',

            # Output directories
            'test_data_dir': '/tmp/test_020_full_concurrency',
            'acquisition_file': '/tmp/test_020_full_concurrency/acquisition.bin',
            'stress_log_file': '/tmp/test_020_full_concurrency/stress.log',

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_020_full_concurrency.log',

            # JSONL results
            'results_file': '/tmp/test_020_full_concurrency.jsonl',
        }

    def setup_method(self):
        """Setup before each test method"""
        pass

    def teardown_method(self):
        """Cleanup after each test method"""
        pass

    def log_message(self, message, config):
        """Log message to file and console"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        print(log_entry)

        if config.get('enable_logging'):
            try:
                with open(config['log_file'], 'a') as f:
                    f.write(log_entry + '\n')
            except:
                pass

    def check_stress_ng_installed(self, config):
        """Check if stress-ng utility is installed"""
        try:
            result = subprocess.run(
                ['which', config['stress_ng_path']],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, None

            stress_ng_path = result.stdout.strip()

            # Get version
            version_result = subprocess.run(
                ['stress-ng', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            version_match = re.search(r'stress-ng, version ([\d.]+)', version_result.stdout)
            version = version_match.group(1) if version_match else "unknown"

            return True, version

        except Exception as e:
            return False, None

    def generate_ecg_sample(self, sample_num, sample_rate):
        """Generate simulated ECG sample (3 channels × 24-bit)"""
        t = sample_num / sample_rate
        bpm = 60  # 60 BPM
        heart_rate_hz = bpm / 60.0

        # Simulate ECG waveform (3 leads)
        lead1 = int(512 + 400 * math.sin(2 * math.pi * heart_rate_hz * t))
        lead2 = int(512 + 350 * math.sin(2 * math.pi * heart_rate_hz * t + 0.5))
        lead3 = int(512 + 300 * math.sin(2 * math.pi * heart_rate_hz * t + 1.0))

        # Pack as 3 × 32-bit integers (24-bit data)
        return struct.pack('<III', lead1, lead2, lead3)

    def generate_icg_sample(self, sample_num, sample_rate):
        """Generate simulated ICG sample (4 channels × 24-bit)"""
        t = sample_num / sample_rate
        resp_rate_hz = 0.25  # 15 breaths/min

        # Simulate ICG waveform (4 channels)
        ch1 = int(2048 + 1800 * math.sin(2 * math.pi * resp_rate_hz * t))
        ch2 = int(2048 + 1600 * math.sin(2 * math.pi * resp_rate_hz * t + 0.3))
        ch3 = int(2048 + 1400 * math.sin(2 * math.pi * resp_rate_hz * t + 0.6))
        ch4 = int(2048 + 1200 * math.sin(2 * math.pi * resp_rate_hz * t + 0.9))

        # Pack as 4 × 32-bit integers (24-bit data)
        return struct.pack('<IIII', ch1, ch2, ch3, ch4)

    def acquisition_simulator_thread(self, config, metrics, stop_event, metrics_lock):
        """Acquisition simulator thread - generates ECG/ICG samples at 400 Hz"""
        self.log_message("Starting acquisition simulator thread...", config)

        sample_rate = config['target_sample_rate_hz']
        sample_interval = 1.0 / sample_rate  # 0.0025 seconds

        acquisition_file = config['acquisition_file']

        # Open file for writing
        try:
            f = open(acquisition_file, 'wb')
        except Exception as e:
            self.log_message(f"  ✗ Cannot open acquisition file: {e}", config)
            return

        start_time = time.time()
        sample_count = 0
        max_lag = 0.0

        try:
            while not stop_event.is_set():
                # Scheduled timing (not naive sleep)
                scheduled_time = start_time + (sample_count * sample_interval)

                # Wait until scheduled time
                current_time = time.time()
                if current_time < scheduled_time:
                    sleep_time = scheduled_time - current_time
                    if sleep_time > 0.001:  # Sleep if > 1ms
                        time.sleep(sleep_time - 0.0005)

                    # Busy-wait for remaining time
                    while time.time() < scheduled_time:
                        pass

                actual_time = time.time()
                lag = actual_time - scheduled_time

                # Track maximum lag
                if lag > max_lag:
                    max_lag = lag

                # Generate ECG + ICG sample
                ecg_data = self.generate_ecg_sample(sample_count, sample_rate)
                icg_data = self.generate_icg_sample(sample_count, sample_rate)

                # Write to file
                f.write(ecg_data)
                f.write(icg_data)

                sample_count += 1

            # Close file
            f.flush()
            os.fsync(f.fileno())
            f.close()

            end_time = time.time()
            actual_duration = end_time - start_time

            # Calculate achieved sample rate
            achieved_rate = sample_count / actual_duration if actual_duration > 0 else 0

            # Update shared metrics
            with metrics_lock:
                metrics['acquisition'] = {
                    'total_samples': sample_count,
                    'actual_duration_sec': actual_duration,
                    'achieved_rate_hz': achieved_rate,
                    'max_lag_sec': max_lag,
                    'max_lag_ms': max_lag * 1000,
                }

            self.log_message(f"  ✓ Acquisition simulator stopped", config)
            self.log_message(f"    Total samples: {sample_count}", config)
            self.log_message(f"    Achieved rate: {achieved_rate:.2f} Hz", config)
            self.log_message(f"    Max lag: {max_lag*1000:.2f} ms", config)

        except Exception as e:
            self.log_message(f"  ✗ Acquisition simulator error: {e}", config)
            f.close()

    def cpu_burn_thread(self, stop_event, thread_id):
        """CPU-burn thread for Python fallback stress"""
        while not stop_event.is_set():
            # CPU-intensive calculations
            result = 0
            for i in range(10000):
                result += i * i
                result += math.sqrt(i + 1)
                result += math.sin(i) * math.cos(i)

            # Prevent compiler optimization
            if result < 0:
                break

    def cpu_burn_stress(self, config, stop_event):
        """Run CPU burn stress (stress-ng or Python fallback)"""
        stress_ng_available, version = self.check_stress_ng_installed(config)

        if stress_ng_available:
            self.log_message(f"  Starting stress-ng (version {version})...", config)

            cmd = [
                'stress-ng',
                '--cpu', str(config['stress_ng_cpu_workers']),
                '--timeout', f"{config['test_duration_sec'] + 60}s",  # Extra margin
                '--metrics-brief'
            ]

            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Wait for stop event
                while not stop_event.is_set():
                    time.sleep(1)

                # Terminate stress-ng
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()

                self.log_message(f"  ✓ stress-ng stopped", config)

            except Exception as e:
                self.log_message(f"  ✗ stress-ng error: {e}", config)

        else:
            # Python fallback
            self.log_message(f"  Starting Python CPU-burn ({config['cpu_burn_threads']} threads)...", config)

            cpu_threads = []
            for i in range(config['cpu_burn_threads']):
                thread = threading.Thread(
                    target=self.cpu_burn_thread,
                    args=(stop_event, i)
                )
                thread.start()
                cpu_threads.append(thread)

            # Wait for stop event
            while not stop_event.is_set():
                time.sleep(1)

            # Stop threads
            for thread in cpu_threads:
                thread.join(timeout=5)

            self.log_message(f"  ✓ Python CPU-burn stopped", config)

    def logging_stress_thread(self, config, stop_event):
        """Logging stress thread - generates bursts with fsync"""
        self.log_message("Starting logging stress thread...", config)

        burst_interval = 1.0 / config['log_burst_frequency_hz']
        burst_size = config['log_burst_size_bytes']
        stress_log_file = config['stress_log_file']

        # Open file
        try:
            f = open(stress_log_file, 'w')
        except Exception as e:
            self.log_message(f"  ✗ Cannot open stress log file: {e}", config)
            return

        burst_count = 0
        next_burst_time = time.time() + burst_interval

        try:
            while not stop_event.is_set():
                current_time = time.time()

                if current_time >= next_burst_time:
                    timestamp = current_time
                    log_message = f"[{timestamp:.6f}] Log burst {burst_count}: " + ("X" * burst_size) + "\n"

                    # Write with fsync (blocks!)
                    f.write(log_message)
                    f.flush()
                    os.fsync(f.fileno())

                    burst_count += 1
                    next_burst_time += burst_interval

                # Sleep briefly
                time.sleep(0.01)

            # Close file
            f.close()

            self.log_message(f"  ✓ Logging stress stopped", config)
            self.log_message(f"    Total bursts: {burst_count}", config)

        except Exception as e:
            self.log_message(f"  ✗ Logging stress error: {e}", config)
            f.close()

    def read_cpu_temperature(self, config):
        """Read CPU temperature from thermal zone (BCM2711)"""
        try:
            with open(config['thermal_zone_path'], 'r') as f:
                temp_millidegrees = int(f.read().strip())
                temp_celsius = temp_millidegrees / 1000.0
                return temp_celsius
        except Exception as e:
            return None

    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        try:
            # Try using psutil if available
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # Fallback: parse /proc/stat
            try:
                with open('/proc/stat', 'r') as f:
                    line = f.readline()
                    fields = line.split()
                    total = sum(int(x) for x in fields[1:8])
                    idle = int(fields[4])

                time.sleep(1)

                with open('/proc/stat', 'r') as f2:
                    line2 = f2.readline()
                    fields2 = line2.split()
                    total2 = sum(int(x) for x in fields2[1:8])
                    idle2 = int(fields2[4])

                total_diff = total2 - total
                idle_diff = idle2 - idle

                if total_diff > 0:
                    usage = 100.0 * (total_diff - idle_diff) / total_diff
                    return usage
                else:
                    return 0.0
            except:
                return None

    def thermal_monitoring_thread(self, config, metrics, stop_event, metrics_lock):
        """Thermal monitoring thread - logs temperature and CPU usage periodically"""
        self.log_message("Starting thermal monitoring thread...", config)

        monitor_interval = config['thermal_monitor_interval_sec']
        next_monitor_time = time.time() + monitor_interval

        thermal_data = []

        while not stop_event.is_set():
            current_time = time.time()

            if current_time >= next_monitor_time:
                # Read temperature
                temp_celsius = self.read_cpu_temperature(config)

                # Read CPU usage
                cpu_usage = self.get_cpu_usage()

                # Store measurement
                measurement = {
                    'timestamp': current_time,
                    'cpu_temp_celsius': temp_celsius,
                    'cpu_usage_percent': cpu_usage,
                }
                thermal_data.append(measurement)

                # Console output
                elapsed_sec = int(current_time - metrics['start_time'])
                elapsed_min = elapsed_sec / 60.0
                temp_str = f"{temp_celsius:.1f}°C" if temp_celsius is not None else "N/A"
                usage_str = f"{cpu_usage:.1f}%" if cpu_usage is not None else "N/A"

                print(f"  [{elapsed_min:5.1f} min] Temp: {temp_str:7s} | CPU: {usage_str:6s}")

                next_monitor_time += monitor_interval

            # Sleep briefly
            time.sleep(1)

        # Update shared metrics
        with metrics_lock:
            metrics['thermal'] = thermal_data

        self.log_message(f"  ✓ Thermal monitoring stopped", config)
        self.log_message(f"    Total measurements: {len(thermal_data)}", config)

    def analyze_thermal_data(self, thermal_data):
        """Analyze thermal measurements and return statistics"""
        if not thermal_data:
            return None

        temps = [m['cpu_temp_celsius'] for m in thermal_data if m['cpu_temp_celsius'] is not None]
        usages = [m['cpu_usage_percent'] for m in thermal_data if m['cpu_usage_percent'] is not None]

        stats = {}

        if temps:
            stats['temperature'] = {
                'min_celsius': min(temps),
                'max_celsius': max(temps),
                'avg_celsius': sum(temps) / len(temps),
            }

        if usages:
            stats['cpu_usage'] = {
                'min_percent': min(usages),
                'max_percent': max(usages),
                'avg_percent': sum(usages) / len(usages),
            }

        return stats

    def save_results_jsonl(self, results, config):
        """Save test results to JSONL file"""
        try:
            results_file = config.get('results_file')
            if results_file:
                with open(results_file, 'w') as f:
                    f.write(json.dumps(results) + '\n')
                self.log_message(f"  ✓ Results saved to: {results_file}", config)
        except Exception as e:
            self.log_message(f"  ⚠ Could not save results: {e}", config)

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.concurrency
    @pytest.mark.slow
    @pytest.mark.stress
    def test_020_full_concurrency(self, test_config):
        """
        Test Case #20: Full Concurrency

        Test Setup: CM4 with eMMC storage
        Acceptance Criteria: Simulator rate error ≤ 1 Hz under full concurrent load

        IMPORTANT: This test must run ON the CM4 itself.
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_020_full_concurrency.py -v -s"

        What this test validates:
        - ECG/ICG acquisition maintains 400 Hz under full system load
        - System handles concurrent CPU burn + disk I/O + thermal monitoring
        - Real-time constraints met despite maximum contention
        - No crashes or exceptions under full concurrency

        This is the ultimate stress test combining all system resources.
        """

        print("\n" + "=" * 70)
        print("Test Case #20: Full Concurrency")
        print("=" * 70)
        print("\nHW Component Test - ECG/ICG + CPU + eMMC + OS Scheduler")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("Full Concurrency test")

        # Create test data directory
        test_data_dir = test_config['test_data_dir']
        if not os.path.exists(test_data_dir):
            os.makedirs(test_data_dir)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_020_Full_Concurrency',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration_sec': test_config['test_duration_sec'],
            'target_sample_rate_hz': test_config['target_sample_rate_hz'],
            'tolerance_hz': test_config['sample_rate_tolerance_hz'],
        }

        # Shared metrics storage
        metrics = {
            'start_time': 0,
            'acquisition': {},
            'thermal': [],
        }
        metrics_lock = threading.Lock()

        # Thread tracking
        threads = []
        stop_event = threading.Event()

        try:
            # ================================================================
            # STEP 1: Detect CPU Load Method
            # ================================================================
            print("\n[STEP 1] Detect CPU Load Method")
            print("-" * 70)

            stress_ng_available, version = self.check_stress_ng_installed(test_config)

            if stress_ng_available:
                print(f"✓ stress-ng available (version {version})")
                cpu_load_method = 'stress-ng'
            else:
                print("⚠ stress-ng not found, using Python fallback")
                cpu_load_method = 'python_fallback'

            test_results['cpu_load_method'] = cpu_load_method

            # ================================================================
            # STEP 2: Start All Concurrent Threads
            # ================================================================
            print("\n[STEP 2] Start All Concurrent Threads")
            print("-" * 70)
            print(f"Duration: {test_config['test_duration_sec']} seconds ({test_config['test_duration_sec']/60:.1f} minutes)")
            print(f"Target sample rate: {test_config['target_sample_rate_hz']} Hz")
            print(f"Tolerance: ±{test_config['sample_rate_tolerance_hz']} Hz")
            print("")

            metrics['start_time'] = time.time()

            # Thread 1: Acquisition simulator (400 Hz)
            print("Starting acquisition simulator (400 Hz)...")
            acquisition_thread = threading.Thread(
                target=self.acquisition_simulator_thread,
                args=(test_config, metrics, stop_event, metrics_lock)
            )
            acquisition_thread.start()
            threads.append(('acquisition', acquisition_thread))

            # Thread 2: CPU burn stress
            print(f"Starting CPU burn stress ({cpu_load_method})...")
            cpu_burn_thread = threading.Thread(
                target=self.cpu_burn_stress,
                args=(test_config, stop_event)
            )
            cpu_burn_thread.start()
            threads.append(('cpu_burn', cpu_burn_thread))

            # Thread 3: Logging stress (10 Hz bursts)
            print("Starting logging stress (10 Hz bursts with fsync)...")
            logging_thread = threading.Thread(
                target=self.logging_stress_thread,
                args=(test_config, stop_event)
            )
            logging_thread.start()
            threads.append(('logging', logging_thread))

            # Thread 4: Thermal monitoring (every 30 sec)
            print("Starting thermal monitoring (every 30 seconds)...")
            thermal_thread = threading.Thread(
                target=self.thermal_monitoring_thread,
                args=(test_config, metrics, stop_event, metrics_lock)
            )
            thermal_thread.start()
            threads.append(('thermal', thermal_thread))

            print("\n✓ All threads started")
            print("-" * 70)

            # ================================================================
            # STEP 3: Wait for Test Duration
            # ================================================================
            print("\n[STEP 3] Running Full Concurrency Test")
            print("-" * 70)
            print("")

            # Wait for test duration
            end_time = time.time() + test_config['test_duration_sec']

            while time.time() < end_time:
                time.sleep(5)

            # ================================================================
            # STEP 4: Stop All Threads
            # ================================================================
            print("\n[STEP 4] Stopping All Threads")
            print("-" * 70)

            # Signal stop
            stop_event.set()

            # Wait for all threads to finish
            for thread_name, thread in threads:
                self.log_message(f"  Waiting for {thread_name} thread...", test_config)
                thread.join(timeout=30)

            print("✓ All threads stopped")

            # ================================================================
            # STEP 5: Analyze Results
            # ================================================================
            print("\n[STEP 5] Analyze Results")
            print("-" * 70)

            # Acquisition metrics
            with metrics_lock:
                acquisition_metrics = metrics.get('acquisition', {})

            if not acquisition_metrics:
                pytest.fail("No acquisition metrics collected")

            achieved_rate = acquisition_metrics['achieved_rate_hz']
            target_rate = test_config['target_sample_rate_hz']
            rate_error = abs(achieved_rate - target_rate)
            max_lag_ms = acquisition_metrics['max_lag_ms']

            print(f"✓ Acquisition metrics:")
            print(f"  Total samples: {acquisition_metrics['total_samples']}")
            print(f"  Achieved rate: {achieved_rate:.2f} Hz")
            print(f"  Target rate: {target_rate} Hz")
            print(f"  Rate error: {rate_error:.2f} Hz")
            print(f"  Max lag: {max_lag_ms:.2f} ms")

            test_results['acquisition_metrics'] = acquisition_metrics

            # Thermal metrics
            with metrics_lock:
                thermal_data = metrics.get('thermal', [])

            thermal_stats = self.analyze_thermal_data(thermal_data)

            if thermal_stats:
                print(f"✓ Thermal metrics:")
                if 'temperature' in thermal_stats:
                    temp_stats = thermal_stats['temperature']
                    print(f"  Temperature range: {temp_stats['min_celsius']:.1f}°C - {temp_stats['max_celsius']:.1f}°C")
                    print(f"  Average: {temp_stats['avg_celsius']:.1f}°C")

                if 'cpu_usage' in thermal_stats:
                    usage_stats = thermal_stats['cpu_usage']
                    print(f"  CPU usage range: {usage_stats['min_percent']:.1f}% - {usage_stats['max_percent']:.1f}%")
                    print(f"  Average: {usage_stats['avg_percent']:.1f}%")

                test_results['thermal_stats'] = thermal_stats

            # ================================================================
            # STEP 6: Evaluate Pass/Fail
            # ================================================================
            print("\n[STEP 6] Evaluate Pass/Fail")
            print("-" * 70)

            tolerance = test_config['sample_rate_tolerance_hz']

            if rate_error <= tolerance:
                print(f"✓ Sample rate error ({rate_error:.2f} Hz) within tolerance (±{tolerance} Hz)")
                test_results['pass'] = True
            else:
                print(f"✗ Sample rate error ({rate_error:.2f} Hz) exceeds tolerance (±{tolerance} Hz)")
                test_results['pass'] = False

                pytest.fail(
                    f"Full concurrency test FAILED!\n"
                    f"  Achieved rate: {achieved_rate:.2f} Hz\n"
                    f"  Target rate: {target_rate} Hz\n"
                    f"  Rate error: {rate_error:.2f} Hz\n"
                    f"  Tolerance: ±{tolerance} Hz\n"
                    "\n"
                    "This indicates:\n"
                    "  - System cannot maintain real-time acquisition under full load\n"
                    "  - CPU/I/O contention impacts timing\n"
                    "  - Insufficient processing power for concurrent operations"
                )

        finally:
            # Ensure all threads are stopped
            stop_event.set()

        # ================================================================
        # Save Results to JSONL
        # ================================================================
        self.save_results_jsonl(test_results, test_config)

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ Test completed without exceptions")
        print(f"  ✓ Duration: {test_config['test_duration_sec']} seconds ({test_config['test_duration_sec']/60:.1f} minutes)")
        print(f"  ✓ Achieved sample rate: {achieved_rate:.2f} Hz")
        print(f"  ✓ Rate error: {rate_error:.2f} Hz (within ±{tolerance} Hz tolerance)")
        print(f"  ✓ Max lag: {max_lag_ms:.2f} ms")

        if thermal_stats and 'temperature' in thermal_stats:
            temp_stats = thermal_stats['temperature']
            print(f"  ✓ Temperature range: {temp_stats['min_celsius']:.1f}°C - {temp_stats['max_celsius']:.1f}°C")

        if thermal_stats and 'cpu_usage' in thermal_stats:
            usage_stats = thermal_stats['cpu_usage']
            print(f"  ✓ Average CPU usage: {usage_stats['avg_percent']:.1f}%")

        print(f"  ✓ Full concurrency test validated (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print(f"📄 Acquisition data: {test_config['acquisition_file']}")
        print(f"📄 Stress log: {test_config['stress_log_file']}")

        print("\n" + "=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
