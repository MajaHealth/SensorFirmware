#!/usr/bin/env python3
"""
Test Case #15: eMMC I/O Latency Under Logging
Category: HW-FW Integration Test
Component: CM4 eMMC + OS Logging I/O + Acquisition Simulator Thread

Tests eMMC I/O latency under concurrent load by simulating real-time
sensor data acquisition (400 Hz) while generating heavy logging activity.

This test runs on the CM4 itself (not on PC via remote connection).
"""

import subprocess
import os
import sys
import time
import json
import struct
import math
import threading
import pytest

# Add common utilities to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from platform_check import skip_if_not_raspberry_pi


class TestEMMCIOLatency:
    """HW-FW Integration Test - eMMC I/O Latency Under Logging"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for eMMC I/O latency test"""
        return {
            # Test duration
            'test_duration_sec': 60,  # 60 seconds default (can adjust)

            # Acquisition parameters (simulates ADS1293 + MAX30009)
            'target_sample_rate_hz': 400,  # 400 Hz sampling
            'ecg_channels': 3,  # ADS1293: 3 channels × 24-bit
            'icg_channels': 4,  # MAX30009: 4 channels × 24-bit
            'bytes_per_sample': 28,  # (3+4) × 4 bytes = 28 bytes

            # Buffering (realistic firmware behavior)
            'buffer_size_samples': 100,  # Flush every 100 samples (250ms)

            # Logging stress parameters
            'log_burst_frequency_hz': 10,  # 10 log bursts per second
            'log_burst_size_bytes': 1024,  # 1 KB per burst

            # Test location
            'test_location': '/tmp',

            # Pass/fail criteria
            'sample_rate_tolerance_hz': 1.0,  # ±1 Hz acceptable

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_015_emmc_io_latency.log',

            # JSONL results
            'results_file': '/tmp/test_015_emmc_io_latency.jsonl',
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

    def generate_ecg_sample(self, sample_num, sample_rate):
        """
        Generate simulated ECG sample (3 channels × 24-bit)

        Returns: 12 bytes (3 × 4 bytes, using int32 for simplicity)
        """
        # Simple sine wave simulation
        t = sample_num / sample_rate  # Time in seconds
        bpm = 60
        heart_rate_hz = bpm / 60.0

        # Lead I, II, III (simulate realistic ECG values)
        lead1 = int(512 + 400 * math.sin(2 * math.pi * heart_rate_hz * t))
        lead2 = int(512 + 350 * math.sin(2 * math.pi * heart_rate_hz * t + 0.5))
        lead3 = int(512 + 300 * math.sin(2 * math.pi * heart_rate_hz * t + 1.0))

        # Pack as 3 × 32-bit integers (simplified from 24-bit)
        return struct.pack('<III', lead1, lead2, lead3)

    def generate_icg_sample(self, sample_num, sample_rate):
        """
        Generate simulated ICG sample (4 channels × 24-bit)

        Returns: 16 bytes (4 × 4 bytes, using int32 for simplicity)
        """
        # Simple sine wave simulation with different phase
        t = sample_num / sample_rate
        freq = 1.2  # 1.2 Hz respiratory rate

        # 4 ICG channels
        ch1 = int(2048 + 1000 * math.sin(2 * math.pi * freq * t))
        ch2 = int(2048 + 900 * math.sin(2 * math.pi * freq * t + 0.3))
        ch3 = int(2048 + 800 * math.sin(2 * math.pi * freq * t + 0.6))
        ch4 = int(2048 + 700 * math.sin(2 * math.pi * freq * t + 0.9))

        # Pack as 4 × 32-bit integers (simplified from 24-bit)
        return struct.pack('<IIII', ch1, ch2, ch3, ch4)

    def acquisition_simulator_thread(self, config, metrics, stop_event, metrics_lock):
        """
        Acquisition simulator thread - generates samples at 400 Hz

        This simulates the real-time acquisition behavior of spi-service
        collecting data from ADS1293 (ECG) and MAX30009 (ICG).
        """
        sample_rate = config['target_sample_rate_hz']
        sample_interval = 1.0 / sample_rate  # 0.0025 seconds (2.5ms)
        buffer_size = config['buffer_size_samples']

        # Files for acquisition data
        acquisition_file = os.path.join(
            config['test_location'],
            f"acquisition_data_{int(time.time())}.bin"
        )

        try:
            # Open acquisition data file
            data_file = open(acquisition_file, 'wb')

            # Sample buffer
            sample_buffer = []

            # Timing tracking (use scheduled approach, not naive sleep)
            start_time = time.time()
            sample_count = 0
            max_lag = 0.0

            while not stop_event.is_set():
                # Calculate scheduled time for this sample
                scheduled_time = start_time + (sample_count * sample_interval)

                # Wait until scheduled time (busy-wait for precision)
                current_time = time.time()
                if current_time < scheduled_time:
                    sleep_time = scheduled_time - current_time
                    if sleep_time > 0.001:  # If > 1ms, use sleep
                        time.sleep(sleep_time - 0.0005)  # Sleep most of it
                    # Busy-wait for remaining time
                    while time.time() < scheduled_time:
                        pass

                # Record actual sample time
                actual_time = time.time()
                lag = actual_time - scheduled_time

                # Track max lag
                if lag > max_lag:
                    max_lag = lag

                # Generate ECG + ICG sample
                ecg_data = self.generate_ecg_sample(sample_count, sample_rate)
                icg_data = self.generate_icg_sample(sample_count, sample_rate)

                # Combine into single sample
                sample_data = ecg_data + icg_data

                # Add to buffer
                sample_buffer.append(sample_data)

                sample_count += 1

                # Flush buffer when full
                if len(sample_buffer) >= buffer_size:
                    # Write all buffered samples
                    for sample in sample_buffer:
                        data_file.write(sample)

                    # Flush to disk
                    data_file.flush()
                    os.fsync(data_file.fileno())

                    # Clear buffer
                    sample_buffer = []

            # Final flush
            if sample_buffer:
                for sample in sample_buffer:
                    data_file.write(sample)
                data_file.flush()
                os.fsync(data_file.fileno())

            # Update metrics (thread-safe)
            with metrics_lock:
                metrics['sample_count'] = sample_count
                metrics['max_lag'] = max_lag
                metrics['acquisition_file'] = acquisition_file
                metrics['acquisition_error'] = None

            data_file.close()

        except Exception as e:
            with metrics_lock:
                metrics['acquisition_error'] = str(e)
            if 'data_file' in locals():
                try:
                    data_file.close()
                except:
                    pass

    def logging_stress_thread(self, config, metrics, stop_event, metrics_lock):
        """
        Logging stress thread - generates bursts of log activity with fsync

        This simulates worst-case logging behavior with frequent fsync
        calls that compete with acquisition I/O.
        """
        burst_interval = 1.0 / config['log_burst_frequency_hz']
        burst_size = config['log_burst_size_bytes']

        # Log file for stress testing
        stress_log_file = os.path.join(
            config['test_location'],
            f"stress_log_{int(time.time())}.log"
        )

        try:
            burst_count = 0

            while not stop_event.is_set():
                # Generate log burst
                timestamp = time.time()
                log_message = f"[{timestamp:.6f}] Log burst {burst_count}: " + ("X" * (burst_size - 50)) + "\n"

                # Write to file
                with open(stress_log_file, 'a') as f:
                    f.write(log_message)
                    f.flush()
                    os.fsync(f.fileno())  # Force immediate write (blocks!)

                burst_count += 1

                # Wait for next burst
                time.sleep(burst_interval)

            # Update metrics (thread-safe)
            with metrics_lock:
                metrics['log_burst_count'] = burst_count
                metrics['stress_log_file'] = stress_log_file
                metrics['logging_error'] = None

        except Exception as e:
            with metrics_lock:
                metrics['logging_error'] = str(e)

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
    @pytest.mark.storage
    @pytest.mark.timing
    @pytest.mark.slow
    def test_015_emmc_io_latency_under_logging(self, test_config):
        """
        Test Case #15: eMMC I/O Latency Under Logging

        Test Setup: CM4 with eMMC storage, multi-threaded simulator
        Acceptance Criteria: Achieved sample rate error ≤ 1 Hz relative to 400 Hz

        IMPORTANT: This test must run ON the CM4 itself.
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_015_emmc_io_latency.py -v -s"

        What this test validates:
        - eMMC can handle concurrent real-time acquisition + logging
        - 400 Hz sample rate maintained within ±1 Hz tolerance
        - Logging activity doesn't degrade acquisition timing
        - Real-world firmware operation is viable on this hardware
        """

        print("\n" + "=" * 70)
        print("Test Case #15: eMMC I/O Latency Under Logging")
        print("=" * 70)
        print("\nHW-FW Integration Test - eMMC + Acquisition + Logging")
        print("=" * 70)
        print("\nTEST METHOD:")
        print("  1. Start acquisition simulator thread (400 Hz)")
        print("  2. Start logging stress thread (concurrent I/O)")
        print("  3. Run for test duration (concurrent operation)")
        print("  4. Stop threads and evaluate timing metrics")
        print("  5. Verify achieved sample rate ≤ 1 Hz error")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("eMMC I/O Latency test")

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_015_eMMC_IO_Latency_Under_Logging',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration_sec': test_config['test_duration_sec'],
            'target_sample_rate_hz': test_config['target_sample_rate_hz'],
            'sample_rate_tolerance_hz': test_config['sample_rate_tolerance_hz'],
        }

        # Thread synchronization
        stop_event = threading.Event()
        metrics_lock = threading.Lock()
        shared_metrics = {
            'sample_count': 0,
            'max_lag': 0.0,
            'log_burst_count': 0,
            'acquisition_error': None,
            'logging_error': None,
        }

        acquisition_thread = None
        logging_thread = None

        try:
            # ================================================================
            # STEP 1: Initialize Test
            # ================================================================
            print("\n[STEP 1] Initialize Test")
            print("-" * 70)

            expected_samples = test_config['target_sample_rate_hz'] * test_config['test_duration_sec']

            print(f"Test duration: {test_config['test_duration_sec']} seconds")
            print(f"Target sample rate: {test_config['target_sample_rate_hz']} Hz")
            print(f"Expected samples: {expected_samples}")
            print(f"Buffer size: {test_config['buffer_size_samples']} samples")
            print(f"Log burst frequency: {test_config['log_burst_frequency_hz']} Hz")
            print(f"Pass/fail tolerance: ±{test_config['sample_rate_tolerance_hz']} Hz")

            self.log_message(f"Test initialized - Duration: {test_config['test_duration_sec']}s", test_config)

            # ================================================================
            # STEP 2: Start Acquisition Simulator Thread
            # ================================================================
            print("\n[STEP 2] Start Acquisition Simulator Thread")
            print("-" * 70)

            acquisition_thread = threading.Thread(
                target=self.acquisition_simulator_thread,
                args=(test_config, shared_metrics, stop_event, metrics_lock),
                name="AcquisitionSimulator"
            )

            acquisition_thread.start()
            print(f"✓ Acquisition thread started (400 Hz sampling)")
            self.log_message("Acquisition simulator thread started", test_config)

            # ================================================================
            # STEP 3: Start Logging Stress Thread
            # ================================================================
            print("\n[STEP 3] Start Logging Stress Thread")
            print("-" * 70)

            logging_thread = threading.Thread(
                target=self.logging_stress_thread,
                args=(test_config, shared_metrics, stop_event, metrics_lock),
                name="LoggingStress"
            )

            logging_thread.start()
            print(f"✓ Logging stress thread started ({test_config['log_burst_frequency_hz']} Hz)")
            self.log_message("Logging stress thread started", test_config)

            # ================================================================
            # STEP 4: Run Test for Duration
            # ================================================================
            print("\n[STEP 4] Running Concurrent I/O Test")
            print("-" * 70)
            print(f"Test running for {test_config['test_duration_sec']} seconds...")
            print("(Progress updated every 5 seconds)")
            print()

            test_start = time.time()
            test_end = test_start + test_config['test_duration_sec']

            # Progress monitoring
            last_progress_time = test_start
            progress_interval = 5.0  # Report every 5 seconds

            while time.time() < test_end:
                time.sleep(0.1)  # Check every 100ms

                # Progress report
                current_time = time.time()
                if current_time - last_progress_time >= progress_interval:
                    elapsed = current_time - test_start
                    remaining = test_end - current_time

                    with metrics_lock:
                        samples = shared_metrics['sample_count']
                        max_lag = shared_metrics['max_lag']

                    if elapsed > 0:
                        current_rate = samples / elapsed
                        print(f"Progress: {elapsed:5.0f}s | Samples: {samples:6d} | "
                              f"Lag: {max_lag*1000:5.1f}ms | Rate: {current_rate:6.1f} Hz")

                    last_progress_time = current_time

            # ================================================================
            # STEP 5: Stop Threads and Evaluate
            # ================================================================
            print("\n[STEP 5] Stop Threads and Evaluate Metrics")
            print("-" * 70)

            # Signal threads to stop
            stop_event.set()

            # Wait for threads to finish
            if acquisition_thread:
                acquisition_thread.join(timeout=5.0)
            if logging_thread:
                logging_thread.join(timeout=5.0)

            print("✓ All threads stopped")

            # Get final metrics
            actual_duration = time.time() - test_start

            with metrics_lock:
                actual_samples = shared_metrics['sample_count']
                max_lag = shared_metrics['max_lag']
                log_bursts = shared_metrics['log_burst_count']
                acquisition_error = shared_metrics['acquisition_error']
                logging_error = shared_metrics['logging_error']

            # Check for thread errors
            if acquisition_error:
                pytest.fail(f"Acquisition thread error: {acquisition_error}")

            if logging_error:
                # Logging errors are warnings, not failures
                print(f"  ⚠ Warning: Logging thread error: {logging_error}")

            # Calculate metrics
            achieved_rate = actual_samples / actual_duration if actual_duration > 0 else 0
            rate_error = abs(achieved_rate - test_config['target_sample_rate_hz'])

            # Calculate data sizes
            bytes_per_sample = test_config['bytes_per_sample']
            acquisition_data_kb = (actual_samples * bytes_per_sample) / 1024
            logging_data_kb = (log_bursts * test_config['log_burst_size_bytes']) / 1024

            print()
            self.log_message("Test completed - Evaluating metrics", test_config)
            self.log_message(f"  Expected samples: {expected_samples}", test_config)
            self.log_message(f"  Actual samples: {actual_samples}", test_config)
            self.log_message(f"  Achieved rate: {achieved_rate:.2f} Hz", test_config)
            self.log_message(f"  Rate error: {rate_error:.2f} Hz", test_config)
            self.log_message(f"  Max lag: {max_lag*1000:.2f} ms", test_config)
            self.log_message(f"  Log bursts: {log_bursts}", test_config)
            self.log_message(f"  Acquisition data: {acquisition_data_kb:.1f} KB", test_config)
            self.log_message(f"  Logging data: {logging_data_kb:.1f} KB", test_config)

            print(f"  Expected samples: {expected_samples}")
            print(f"  Actual samples: {actual_samples}")
            print(f"  Achieved rate: {achieved_rate:.2f} Hz")
            print(f"  Rate error: {rate_error:.2f} Hz")
            print(f"  Max lag: {max_lag*1000:.2f} ms")
            print(f"  Log bursts: {log_bursts}")

            # Store in results
            test_results['expected_samples'] = expected_samples
            test_results['actual_samples'] = actual_samples
            test_results['actual_duration_sec'] = actual_duration
            test_results['achieved_rate_hz'] = achieved_rate
            test_results['rate_error_hz'] = rate_error
            test_results['max_lag_ms'] = max_lag * 1000
            test_results['log_burst_count'] = log_bursts
            test_results['acquisition_data_kb'] = acquisition_data_kb
            test_results['logging_data_kb'] = logging_data_kb

            # ================================================================
            # Validate Pass/Fail Criteria
            # ================================================================
            print()
            print("-" * 70)
            print("Pass/Fail Validation")
            print("-" * 70)

            tolerance = test_config['sample_rate_tolerance_hz']

            if rate_error <= tolerance:
                test_results['result'] = 'PASS'
                test_results['pass_reason'] = f'Rate error ({rate_error:.2f} Hz) within tolerance (±{tolerance} Hz)'

                print(f"✓ PASS: Rate error ({rate_error:.2f} Hz) ≤ {tolerance} Hz")
            else:
                test_results['result'] = 'FAIL'
                test_results['fail_reason'] = f'Rate error ({rate_error:.2f} Hz) exceeds tolerance (±{tolerance} Hz)'

                pytest.fail(
                    f"Sample rate error exceeds tolerance!\n"
                    f"  Target rate: {test_config['target_sample_rate_hz']} Hz\n"
                    f"  Achieved rate: {achieved_rate:.2f} Hz\n"
                    f"  Rate error: {rate_error:.2f} Hz (> {tolerance} Hz tolerance)\n"
                    f"  Max lag: {max_lag*1000:.2f} ms\n"
                    "\n"
                    "This indicates:\n"
                    "  - eMMC cannot sustain concurrent I/O load\n"
                    "  - Logging fsync() blocks acquisition writes\n"
                    "  - Real-world firmware would experience timing degradation\n"
                    "\n"
                    "Recommendations:\n"
                    "  - Reduce logging frequency in firmware\n"
                    "  - Use asynchronous logging (avoid fsync on critical path)\n"
                    "  - Consider faster eMMC (Class 10 or UHS-I)\n"
                    "  - Optimize buffer sizes and flush intervals"
                )

        finally:
            # ================================================================
            # Cleanup
            # ================================================================
            print("\n[STEP 6] Cleanup")
            print("-" * 70)

            # Ensure threads are stopped
            if not stop_event.is_set():
                stop_event.set()

            if acquisition_thread and acquisition_thread.is_alive():
                acquisition_thread.join(timeout=2.0)

            if logging_thread and logging_thread.is_alive():
                logging_thread.join(timeout=2.0)

            # Remove test files
            with metrics_lock:
                acquisition_file = shared_metrics.get('acquisition_file')
                stress_log_file = shared_metrics.get('stress_log_file')

            if acquisition_file and os.path.exists(acquisition_file):
                try:
                    file_size = os.path.getsize(acquisition_file)
                    os.remove(acquisition_file)
                    print(f"✓ Removed acquisition file ({file_size / 1024:.1f} KB)")
                except Exception as e:
                    print(f"  ⚠ Could not remove {acquisition_file}: {e}")

            if stress_log_file and os.path.exists(stress_log_file):
                try:
                    file_size = os.path.getsize(stress_log_file)
                    os.remove(stress_log_file)
                    print(f"✓ Removed stress log file ({file_size / 1024:.1f} KB)")
                except Exception as e:
                    print(f"  ⚠ Could not remove {stress_log_file}: {e}")

        # ================================================================
        # Save Results to JSONL
        # ================================================================
        self.save_results_jsonl(test_results, test_config)

        # ================================================================
        # Test Result Summary
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ Target sample rate: {test_config['target_sample_rate_hz']} Hz")
        print(f"  ✓ Achieved sample rate: {test_results['achieved_rate_hz']:.2f} Hz")
        print(f"  ✓ Rate error: {test_results['rate_error_hz']:.2f} Hz (within ±{tolerance} Hz tolerance)")
        print(f"  ✓ Max timing lag: {test_results['max_lag_ms']:.2f} ms")
        print(f"  ✓ Samples collected: {test_results['actual_samples']} / {test_results['expected_samples']}")
        print(f"  ✓ eMMC I/O latency validated under concurrent load (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
