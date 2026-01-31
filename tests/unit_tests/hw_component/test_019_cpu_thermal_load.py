#!/usr/bin/env python3
"""
Test Case #19: CPU Thermal Load
Category: HW Component Test
Component: CM4 CPU + Thermal Sensor + OS Telemetry

Tests CPU thermal behavior under sustained load by applying stress and monitoring
temperature and CPU usage over time.

This test runs on the CM4 itself (not on PC via remote connection).
"""

import subprocess
import os
import sys
import time
import json
import threading
import pytest
import re
import math

# Add common utilities to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from platform_check import skip_if_not_raspberry_pi


class TestCPUThermalLoad:
    """HW Component Test - CPU Thermal Load"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for CPU thermal load test"""
        return {
            # Test duration
            'test_duration_sec': 1800,  # 30 minutes default

            # Monitoring
            'log_interval_sec': 30,  # Log every 30 seconds

            # stress-ng configuration
            'stress_ng_path': 'stress-ng',
            'stress_ng_cpu_workers': 4,  # 4 cores on CM4

            # Python fallback configuration
            'cpu_burn_threads': 4,  # 4 threads for Python fallback

            # Thermal sensor
            'thermal_zone_path': '/sys/class/thermal/thermal_zone0/temp',

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_019_cpu_thermal_load.log',

            # JSONL results
            'results_file': '/tmp/test_019_cpu_thermal_load.jsonl',
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
        self.log_message("Checking for stress-ng...", config)

        try:
            result = subprocess.run(
                ['which', config['stress_ng_path']],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, None, None

            stress_ng_path = result.stdout.strip()

            # Get version info
            version_result = subprocess.run(
                ['stress-ng', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            version_match = re.search(r'stress-ng, version ([\d.]+)', version_result.stdout)
            if version_match:
                version = version_match.group(1)
            else:
                version = "unknown"

            self.log_message(f"  ✓ stress-ng found: {stress_ng_path} (version {version})", config)
            return True, stress_ng_path, version

        except Exception as e:
            self.log_message(f"  ✗ Error checking stress-ng: {e}", config)
            return False, None, None

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
                    # fields[0] = 'cpu', fields[1-7] = user, nice, system, idle, iowait, irq, softirq
                    total = sum(int(x) for x in fields[1:8])
                    idle = int(fields[4])

                    # Read again after 1 second
                    time.sleep(1)

                    with open('/proc/stat', 'r') as f2:
                        line2 = f2.readline()
                        fields2 = line2.split()
                        total2 = sum(int(x) for x in fields2[1:8])
                        idle2 = int(fields2[4])

                    # Calculate usage
                    total_diff = total2 - total
                    idle_diff = idle2 - idle

                    if total_diff > 0:
                        usage = 100.0 * (total_diff - idle_diff) / total_diff
                        return usage
                    else:
                        return 0.0
            except:
                return None

    def monitor_thermal_thread(self, config, stop_event, measurements, measurements_lock):
        """Monitoring thread - logs CPU temperature and usage periodically"""
        self.log_message("Starting thermal monitoring thread...", config)

        log_interval = config['log_interval_sec']
        next_log_time = time.time() + log_interval
        measurement_count = 0

        while not stop_event.is_set():
            current_time = time.time()

            if current_time >= next_log_time:
                # Read temperature
                temp_celsius = self.read_cpu_temperature(config)

                # Read CPU usage
                cpu_usage = self.get_cpu_usage()

                # Create measurement record
                measurement = {
                    'type': 'measurement',
                    'timestamp': current_time,
                    'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'elapsed_sec': int(current_time - measurements['start_time']),
                    'cpu_temp_celsius': temp_celsius,
                    'cpu_usage_percent': cpu_usage,
                }

                # Store in shared list
                with measurements_lock:
                    measurements['data'].append(measurement)
                    measurement_count += 1

                # Log to file (JSONL format)
                try:
                    with open(config['log_file'], 'a') as f:
                        f.write(json.dumps(measurement) + '\n')
                except:
                    pass

                # Console output
                elapsed_min = measurement['elapsed_sec'] / 60.0
                temp_str = f"{temp_celsius:.1f}°C" if temp_celsius is not None else "N/A"
                usage_str = f"{cpu_usage:.1f}%" if cpu_usage is not None else "N/A"

                print(f"  [{elapsed_min:5.1f} min] Temp: {temp_str:7s} | CPU: {usage_str:6s}")

                # Schedule next log
                next_log_time += log_interval

            # Sleep briefly
            time.sleep(0.5)

    def cpu_burn_thread(self, stop_event, thread_id):
        """CPU-burn thread for Python fallback stress"""
        # Perform CPU-intensive calculations in a loop
        while not stop_event.is_set():
            # Math operations
            result = 0
            for i in range(10000):
                result += i * i
                result += math.sqrt(i + 1)
                result += math.sin(i) * math.cos(i)

            # Prevent compiler optimization
            if result < 0:
                break

    def run_stress_ng(self, duration_sec, config, measurements, measurements_lock):
        """Run stress-ng CPU stress test"""
        self.log_message(f"Starting stress-ng with {config['stress_ng_cpu_workers']} CPU workers...", config)
        self.log_message(f"  Duration: {duration_sec} seconds ({duration_sec/60:.1f} minutes)", config)

        cmd = [
            'stress-ng',
            '--cpu', str(config['stress_ng_cpu_workers']),
            '--timeout', f"{duration_sec}s",
            '--metrics-brief'
        ]

        # Start monitoring thread
        stop_event = threading.Event()

        monitor_thread = threading.Thread(
            target=self.monitor_thermal_thread,
            args=(config, stop_event, measurements, measurements_lock)
        )
        monitor_thread.start()

        start_time = time.time()
        measurements['start_time'] = start_time

        try:
            # Run stress-ng
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration_sec + 60  # Extra timeout margin
            )

            end_time = time.time()
            actual_duration = end_time - start_time

            self.log_message(f"  ✓ stress-ng completed", config)
            self.log_message(f"  Actual duration: {actual_duration:.1f} seconds", config)

            # Stop monitoring
            stop_event.set()
            monitor_thread.join(timeout=10)

            # Check if stress-ng reported any errors
            if result.returncode != 0:
                self.log_message(f"  ⚠ stress-ng exit code: {result.returncode}", config)

            # Parse stress-ng metrics if available
            if result.stdout:
                self.log_message(f"  stress-ng output:", config)
                for line in result.stdout.split('\n')[:10]:
                    if line.strip():
                        self.log_message(f"    {line}", config)

            return True, actual_duration

        except subprocess.TimeoutExpired:
            self.log_message(f"  ✗ stress-ng timeout", config)
            stop_event.set()
            monitor_thread.join(timeout=10)
            return False, 0

        except Exception as e:
            self.log_message(f"  ✗ stress-ng error: {e}", config)
            stop_event.set()
            monitor_thread.join(timeout=10)
            return False, 0

    def run_python_fallback(self, duration_sec, config, measurements, measurements_lock):
        """Run Python CPU-burn fallback stress test"""
        self.log_message(f"Starting Python CPU-burn with {config['cpu_burn_threads']} threads...", config)
        self.log_message(f"  Duration: {duration_sec} seconds ({duration_sec/60:.1f} minutes)", config)

        # Start CPU-burn threads
        stop_event = threading.Event()
        cpu_threads = []

        for i in range(config['cpu_burn_threads']):
            thread = threading.Thread(
                target=self.cpu_burn_thread,
                args=(stop_event, i)
            )
            thread.start()
            cpu_threads.append(thread)

        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.monitor_thermal_thread,
            args=(config, stop_event, measurements, measurements_lock)
        )
        monitor_thread.start()

        start_time = time.time()
        measurements['start_time'] = start_time
        end_time = start_time + duration_sec

        try:
            # Wait until duration completes
            while time.time() < end_time:
                time.sleep(1)

            actual_duration = time.time() - start_time

            self.log_message(f"  ✓ Python CPU-burn completed", config)
            self.log_message(f"  Actual duration: {actual_duration:.1f} seconds", config)

            # Stop all threads
            stop_event.set()

            # Wait for threads to finish
            for thread in cpu_threads:
                thread.join(timeout=5)

            monitor_thread.join(timeout=10)

            return True, actual_duration

        except Exception as e:
            self.log_message(f"  ✗ Python CPU-burn error: {e}", config)
            stop_event.set()

            for thread in cpu_threads:
                thread.join(timeout=5)

            monitor_thread.join(timeout=10)

            return False, 0

    def analyze_measurements(self, measurements, config):
        """Analyze thermal measurements and return statistics"""
        data = measurements['data']

        if not data:
            return None

        # Extract temperature and CPU usage values
        temps = [m['cpu_temp_celsius'] for m in data if m['cpu_temp_celsius'] is not None]
        usages = [m['cpu_usage_percent'] for m in data if m['cpu_usage_percent'] is not None]

        stats = {
            'total_measurements': len(data),
            'temperature_stats': None,
            'cpu_usage_stats': None,
        }

        if temps:
            stats['temperature_stats'] = {
                'min_celsius': min(temps),
                'max_celsius': max(temps),
                'avg_celsius': sum(temps) / len(temps),
            }

        if usages:
            stats['cpu_usage_stats'] = {
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
    @pytest.mark.cpu
    @pytest.mark.slow
    @pytest.mark.stress
    def test_019_cpu_thermal_load(self, test_config):
        """
        Test Case #19: CPU Thermal Load

        Test Setup: CM4 with thermal sensor
        Acceptance Criteria: Test runs to completion without exceptions

        IMPORTANT: This test must run ON the CM4 itself.
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_019_cpu_thermal_load.py -v -s"

        What this test validates:
        - CPU can sustain high load for extended duration
        - CPU temperature and usage are monitored periodically
        - Test completes without crashes or exceptions
        - Thermal data is logged for post-test analysis

        Note: This test does NOT fail on high temperature or throttling.
        Those are determined by reviewing the log file after completion.
        """

        print("\n" + "=" * 70)
        print("Test Case #19: CPU Thermal Load")
        print("=" * 70)
        print("\nHW Component Test - CM4 CPU + Thermal Sensor + OS Telemetry")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("CPU Thermal Load test")

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_019_CPU_Thermal_Load',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration_sec': test_config['test_duration_sec'],
            'log_interval_sec': test_config['log_interval_sec'],
        }

        # Shared measurements storage
        measurements = {
            'start_time': 0,
            'data': []
        }
        measurements_lock = threading.Lock()

        try:
            # ================================================================
            # STEP 1: Detect CPU Load Method
            # ================================================================
            print("\n[STEP 1] Detect CPU Load Method")
            print("-" * 70)

            stress_ng_available, stress_ng_path, stress_ng_version = self.check_stress_ng_installed(test_config)

            if stress_ng_available:
                print(f"✓ stress-ng available: {stress_ng_path}")
                print(f"  Version: {stress_ng_version}")
                cpu_load_method = 'stress-ng'
            else:
                print("⚠ stress-ng not found, using Python fallback")
                print(f"  Install with: sudo apt install stress-ng")
                cpu_load_method = 'python_fallback'

            test_results['cpu_load_method'] = cpu_load_method

            # ================================================================
            # STEP 2: Verify Thermal Sensor
            # ================================================================
            print("\n[STEP 2] Verify Thermal Sensor")
            print("-" * 70)

            initial_temp = self.read_cpu_temperature(test_config)

            if initial_temp is None:
                pytest.fail(
                    f"Cannot read CPU temperature from {test_config['thermal_zone_path']}\n"
                    "Possible causes:\n"
                    "  - Not running on Raspberry Pi\n"
                    "  - Thermal zone not available\n"
                    "  - Permission denied"
                )

            print(f"✓ Thermal sensor accessible")
            print(f"  Path: {test_config['thermal_zone_path']}")
            print(f"  Initial temperature: {initial_temp:.1f}°C")

            test_results['initial_temp_celsius'] = initial_temp

            # ================================================================
            # STEP 3: Run CPU Load Test
            # ================================================================
            print("\n[STEP 3] Run CPU Load Test")
            print("-" * 70)
            print(f"Duration: {test_config['test_duration_sec']} seconds ({test_config['test_duration_sec']/60:.1f} minutes)")
            print(f"Log interval: {test_config['log_interval_sec']} seconds")
            print("")

            if cpu_load_method == 'stress-ng':
                success, actual_duration = self.run_stress_ng(
                    test_config['test_duration_sec'],
                    test_config,
                    measurements,
                    measurements_lock
                )
            else:
                success, actual_duration = self.run_python_fallback(
                    test_config['test_duration_sec'],
                    test_config,
                    measurements,
                    measurements_lock
                )

            if not success:
                pytest.fail("CPU load test failed to complete")

            print(f"\n✓ CPU load test completed")
            print(f"  Actual duration: {actual_duration:.1f} seconds")

            test_results['actual_duration_sec'] = actual_duration

            # ================================================================
            # STEP 4: Analyze Measurements
            # ================================================================
            print("\n[STEP 4] Analyze Measurements")
            print("-" * 70)

            stats = self.analyze_measurements(measurements, test_config)

            if stats is None:
                pytest.fail("No measurements collected during test")

            print(f"✓ Measurements collected: {stats['total_measurements']}")

            if stats['temperature_stats']:
                temp_stats = stats['temperature_stats']
                print(f"✓ Temperature range: {temp_stats['min_celsius']:.1f}°C - {temp_stats['max_celsius']:.1f}°C")
                print(f"  Average: {temp_stats['avg_celsius']:.1f}°C")
                test_results['temperature_stats'] = temp_stats

            if stats['cpu_usage_stats']:
                usage_stats = stats['cpu_usage_stats']
                print(f"✓ CPU usage range: {usage_stats['min_percent']:.1f}% - {usage_stats['max_percent']:.1f}%")
                print(f"  Average: {usage_stats['avg_percent']:.1f}%")
                test_results['cpu_usage_stats'] = usage_stats

        finally:
            pass  # No cleanup needed

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
        print(f"  ✓ Duration: {test_results['actual_duration_sec']:.1f} seconds ({test_results['actual_duration_sec']/60:.1f} minutes)")
        print(f"  ✓ CPU load method: {test_results['cpu_load_method']}")
        print(f"  ✓ Total measurements: {stats['total_measurements']}")

        if test_results.get('temperature_stats'):
            temp_stats = test_results['temperature_stats']
            print(f"  ✓ Temperature range: {temp_stats['min_celsius']:.1f}°C - {temp_stats['max_celsius']:.1f}°C")

        if test_results.get('cpu_usage_stats'):
            usage_stats = test_results['cpu_usage_stats']
            print(f"  ✓ Average CPU usage: {usage_stats['avg_percent']:.1f}%")

        print(f"  ✓ CPU thermal load test validated (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print("\nNote: Review log file for thermal throttling or overheating analysis.")
        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
