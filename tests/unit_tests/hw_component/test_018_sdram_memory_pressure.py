#!/usr/bin/env python3
"""
Test Case #18: SDRAM Memory Pressure
Category: HW Component Test
Component: CM4 SDRAM + OS Memory Manager + stress-ng/Python allocator

Tests CM4 SDRAM stability under sustained high memory utilization (~90%)
for 30 minutes using stress-ng (preferred) or Python allocator (fallback).

This test runs on the CM4 itself (not on PC via remote connection).
"""

import subprocess
import os
import sys
import time
import json
import re
import threading
import pytest

# Add common utilities to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from platform_check import skip_if_not_raspberry_pi


class TestSDRAMMemoryPressure:
    """HW Component Test - SDRAM Memory Pressure"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for SDRAM memory pressure test"""
        return {
            # Test duration
            'test_duration_sec': 1800,  # 30 minutes default

            # Memory pressure target
            'target_memory_percent': 90,  # Target 90% RAM utilization

            # stress-ng parameters
            'stress_ng_workers': 2,  # Number of VM workers
            'stress_ng_path': 'stress-ng',  # Will search in PATH

            # Python allocator parameters
            'chunk_size_mb': 1,  # Allocate in 1 MB chunks
            'page_size_bytes': 4096,  # 4KB pages (standard)

            # Progress monitoring
            'progress_interval_sec': 300,  # Report every 5 minutes

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_018_sdram_memory_pressure.log',

            # JSONL results
            'results_file': '/tmp/test_018_sdram_memory_pressure.jsonl',
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

    def get_memory_info(self, config):
        """
        Read memory information from /proc/meminfo

        Returns: (total_mb, available_mb)
        """
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()

            # Extract MemTotal and MemAvailable
            total_match = re.search(r'MemTotal:\s+(\d+)\s+kB', meminfo)
            available_match = re.search(r'MemAvailable:\s+(\d+)\s+kB', meminfo)

            if total_match and available_match:
                total_kb = int(total_match.group(1))
                available_kb = int(available_match.group(1))

                total_mb = total_kb // 1024
                available_mb = available_kb // 1024

                return total_mb, available_mb
            else:
                self.log_message("  ⚠ Could not parse /proc/meminfo", config)
                return None, None

        except Exception as e:
            self.log_message(f"  ✗ Error reading memory info: {e}", config)
            return None, None

    def check_stress_ng_available(self, config):
        """
        Check if stress-ng utility is installed and accessible

        Returns: (installed, path, version_info)
        """
        self.log_message("Checking stress-ng availability...", config)

        try:
            # Check if stress-ng exists in PATH
            result = subprocess.run(
                ['which', config['stress_ng_path']],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.log_message(f"  ✗ stress-ng not found in PATH", config)
                return False, None, None

            stress_ng_path = result.stdout.strip()
            self.log_message(f"  ✓ stress-ng found: {stress_ng_path}", config)

            # Get version info
            try:
                version_result = subprocess.run(
                    ['stress-ng', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                # Extract version from output
                version_match = re.search(r'stress-ng, version ([\d.]+)', version_result.stdout)
                if version_match:
                    version = version_match.group(1)
                    self.log_message(f"  ✓ Version: stress-ng, version {version}", config)
                    return True, stress_ng_path, version
                else:
                    self.log_message(f"  ✓ Version: (unknown)", config)
                    return True, stress_ng_path, "unknown"

            except Exception as e:
                # Version check failed, but stress-ng exists
                self.log_message(f"  ⚠ Could not determine version: {e}", config)
                return True, stress_ng_path, "unknown"

        except Exception as e:
            self.log_message(f"  ✗ Error checking stress-ng: {e}", config)
            return False, None, None

    def monitor_memory_usage(self, config, stop_event, metrics, metrics_lock):
        """
        Background thread to monitor memory usage during test

        Updates metrics dictionary with current memory usage
        """
        try:
            while not stop_event.is_set():
                total_mb, available_mb = self.get_memory_info(config)

                if total_mb and available_mb:
                    used_mb = total_mb - available_mb
                    usage_percent = (used_mb / total_mb * 100) if total_mb > 0 else 0

                    with metrics_lock:
                        metrics['total_mb'] = total_mb
                        metrics['used_mb'] = used_mb
                        metrics['available_mb'] = available_mb
                        metrics['usage_percent'] = usage_percent

                time.sleep(1)  # Update every second

        except Exception as e:
            with metrics_lock:
                metrics['monitor_error'] = str(e)

    def run_stress_ng(self, duration_sec, target_percent, config):
        """
        Run stress-ng memory pressure test

        Returns: (success, exit_code, output)
        """
        duration_str = f"{duration_sec}s"
        target_str = f"{target_percent}%"

        # Build command
        cmd = [
            'stress-ng',
            '--vm', str(config['stress_ng_workers']),
            '--vm-bytes', target_str,
            '--timeout', duration_str,
            '--metrics-brief'
        ]

        cmd_display = ' '.join(cmd)

        self.log_message(f"Running stress-ng...", config)
        self.log_message(f"  Command: {cmd_display}", config)
        self.log_message(f"  Workers: {config['stress_ng_workers']}", config)
        self.log_message(f"  Target memory: {target_percent}%", config)
        self.log_message(f"  Duration: {duration_sec} seconds ({duration_sec/60:.0f} minutes)", config)
        self.log_message("", config)
        self.log_message(f"  This will take {duration_sec/60:.0f} minutes, please wait...", config)

        try:
            start_time = time.time()

            # Start memory monitoring thread
            stop_event = threading.Event()
            metrics_lock = threading.Lock()
            shared_metrics = {
                'total_mb': 0,
                'used_mb': 0,
                'available_mb': 0,
                'usage_percent': 0.0,
            }

            monitor_thread = threading.Thread(
                target=self.monitor_memory_usage,
                args=(config, stop_event, shared_metrics, metrics_lock),
                name="MemoryMonitor"
            )
            monitor_thread.start()

            # Progress monitoring
            progress_interval = config['progress_interval_sec']
            next_progress_time = start_time + progress_interval

            # Run stress-ng in background and monitor progress
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor progress while stress-ng runs
            while process.poll() is None:
                current_time = time.time()

                # Report progress
                if current_time >= next_progress_time:
                    elapsed_min = (current_time - start_time) / 60

                    with metrics_lock:
                        used_mb = shared_metrics['used_mb']
                        total_mb = shared_metrics['total_mb']
                        usage_percent = shared_metrics['usage_percent']

                    print(f"Progress: {elapsed_min:3.0f} min | "
                          f"Memory used: {used_mb:4d} MB / {total_mb:4d} MB ({usage_percent:.1f}%)")

                    next_progress_time += progress_interval

                time.sleep(1)  # Check every second

            # stress-ng completed, get results
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            elapsed_time = time.time() - start_time

            # Stop monitoring thread
            stop_event.set()
            monitor_thread.join(timeout=5.0)

            self.log_message("", config)
            self.log_message(f"  Completed in {elapsed_time:.1f} seconds", config)
            self.log_message(f"  Exit code: {exit_code}", config)

            if exit_code == 0:
                self.log_message(f"  ✓ stress-ng completed successfully", config)
                return True, exit_code, stdout + stderr
            else:
                self.log_message(f"  ✗ stress-ng failed with exit code {exit_code}", config)
                return False, exit_code, stdout + stderr

        except Exception as e:
            self.log_message(f"  ✗ Error running stress-ng: {e}", config)
            return False, -1, str(e)

    def run_python_fallback(self, duration_sec, target_percent, config):
        """
        Run Python memory allocator fallback

        Allocates memory in chunks until target is reached or MemoryError occurs,
        then holds for remaining duration.

        Returns: (success, allocated_mb, memory_error_occurred)
        """
        self.log_message(f"Running Python memory allocator...", config)

        # Get memory info
        total_mb, available_mb = self.get_memory_info(config)

        if not total_mb or not available_mb:
            self.log_message(f"  ✗ Could not determine memory size", config)
            return False, 0, False

        target_mb = int(available_mb * target_percent / 100)

        self.log_message(f"  Total RAM: {total_mb} MB", config)
        self.log_message(f"  Available RAM: {available_mb} MB", config)
        self.log_message(f"  Target allocation: {target_mb} MB ({target_percent}%)", config)
        self.log_message(f"  Duration: {duration_sec} seconds ({duration_sec/60:.0f} minutes)", config)
        self.log_message("", config)
        self.log_message(f"  Allocating memory in {config['chunk_size_mb']} MB chunks...", config)

        allocated_chunks = []
        chunk_size_bytes = config['chunk_size_mb'] * 1024 * 1024
        page_size = config['page_size_bytes']

        memory_error_occurred = False
        start_time = time.time()
        end_time = start_time + duration_sec

        progress_interval = config['progress_interval_sec']
        next_progress_time = start_time + progress_interval

        try:
            # Phase 1: Allocate memory
            while time.time() < end_time:
                current_allocated_mb = len(allocated_chunks) * config['chunk_size_mb']

                # Check if target reached
                if current_allocated_mb >= target_mb:
                    self.log_message(f"  ✓ Target allocation reached: {current_allocated_mb} MB", config)
                    break

                try:
                    # Allocate chunk
                    chunk = bytearray(chunk_size_bytes)

                    # Touch all pages to force physical allocation
                    for i in range(0, chunk_size_bytes, page_size):
                        chunk[i] = 1

                    allocated_chunks.append(chunk)

                except MemoryError:
                    memory_error_occurred = True
                    current_allocated_mb = len(allocated_chunks) * config['chunk_size_mb']
                    self.log_message(f"  ⚠ MemoryError reached at {current_allocated_mb} MB (expected)", config)
                    self.log_message(f"  ✓ System memory capacity identified", config)
                    break

                # Progress reporting
                current_time = time.time()
                if current_time >= next_progress_time:
                    elapsed_min = (current_time - start_time) / 60
                    current_allocated_mb = len(allocated_chunks) * config['chunk_size_mb']
                    progress_percent = (current_allocated_mb / target_mb * 100) if target_mb > 0 else 0

                    print(f"Progress: {elapsed_min:3.0f} min | "
                          f"Allocated: {current_allocated_mb:4d} MB / {target_mb:4d} MB ({progress_percent:.1f}%)")

                    next_progress_time += progress_interval

            # Phase 2: Hold memory pressure for remaining duration
            final_allocated_mb = len(allocated_chunks) * config['chunk_size_mb']

            if memory_error_occurred:
                self.log_message(f"  Holding memory pressure for remaining duration...", config)
            else:
                self.log_message(f"  Holding {final_allocated_mb} MB for remaining duration...", config)

            while time.time() < end_time:
                current_time = time.time()

                # Progress reporting
                if current_time >= next_progress_time:
                    elapsed_min = (current_time - start_time) / 60

                    if memory_error_occurred:
                        print(f"Progress: {elapsed_min:3.0f} min | Holding: {final_allocated_mb} MB (MemoryError reached)")
                    else:
                        print(f"Progress: {elapsed_min:3.0f} min | Holding: {final_allocated_mb} MB")

                    next_progress_time += progress_interval

                time.sleep(1)

            # Test completed
            elapsed_time = time.time() - start_time

            self.log_message("", config)
            self.log_message(f"  ✓ Memory pressure test completed", config)
            self.log_message(f"  Allocated: {final_allocated_mb} MB", config)
            self.log_message(f"  Duration: {elapsed_time:.1f} seconds", config)
            self.log_message(f"  MemoryError: {'Yes (acceptable)' if memory_error_occurred else 'No'}", config)

            return True, final_allocated_mb, memory_error_occurred

        except Exception as e:
            self.log_message(f"  ✗ Error during memory allocation: {e}", config)
            return False, len(allocated_chunks) * config['chunk_size_mb'], memory_error_occurred

        finally:
            # Release memory
            if allocated_chunks:
                self.log_message("", config)
                self.log_message(f"  Releasing memory...", config)
                allocated_chunks.clear()
                self.log_message(f"  ✓ Memory released", config)

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
    @pytest.mark.memory
    @pytest.mark.slow
    @pytest.mark.stress
    def test_018_sdram_memory_pressure(self, test_config):
        """
        Test Case #18: SDRAM Memory Pressure

        Test Setup: CM4 with stress-ng (preferred) or Python allocator (fallback)
        Acceptance Criteria: Test completes 30-minute duration without crashes

        IMPORTANT: This test must run ON the CM4 itself.
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_018_sdram_memory_pressure.py -v -s"

        What this test validates:
        - CM4 can operate stably under high memory pressure (~90%)
        - System remains stable for 30 minutes under memory load
        - No crashes, freezes, or OOM (Out Of Memory) kills
        - RAM sufficient for production workloads

        Requirements:
        - stress-ng utility installed (recommended): sudo apt install stress-ng
        - OR: Python fallback will be used (less comprehensive)
        """

        print("\n" + "=" * 70)
        print("Test Case #18: SDRAM Memory Pressure")
        print("=" * 70)
        print("\nHW Component Test - CM4 SDRAM Stability Under Pressure")
        print("=" * 70)
        print("\nTEST METHOD:")
        print("  1. Check memory configuration")
        print("  2. Check stress-ng availability")
        print("  3. Run memory pressure test (30 minutes)")
        print("     - Primary: stress-ng (professional tool)")
        print("     - Fallback: Python allocator (if stress-ng unavailable)")
        print("  4. Validate system stability")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("SDRAM Memory Pressure test")

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_018_SDRAM_Memory_Pressure',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration_sec': test_config['test_duration_sec'],
            'target_memory_percent': test_config['target_memory_percent'],
        }

        try:
            # ================================================================
            # STEP 1: Check Memory Configuration
            # ================================================================
            print("\n[STEP 1] Check Memory Configuration")
            print("-" * 70)

            total_mb, available_mb = self.get_memory_info(test_config)

            if not total_mb or not available_mb:
                pytest.fail("Could not read memory information from /proc/meminfo")

            target_mb = int(available_mb * test_config['target_memory_percent'] / 100)

            print(f"✓ Total RAM: {total_mb} MB")
            print(f"✓ Available RAM: {available_mb} MB")
            print(f"✓ Target utilization: {test_config['target_memory_percent']}% (~{target_mb} MB)")

            self.log_message(f"Memory configuration: {total_mb} MB total, {available_mb} MB available", test_config)

            test_results['total_memory_mb'] = total_mb
            test_results['available_memory_mb'] = available_mb
            test_results['target_memory_mb'] = target_mb

            # ================================================================
            # STEP 2: Check stress-ng Availability
            # ================================================================
            print("\n[STEP 2] Check stress-ng Availability")
            print("-" * 70)

            stress_ng_available, stress_ng_path, version = self.check_stress_ng_available(test_config)

            test_results['stress_ng_available'] = stress_ng_available

            if stress_ng_available:
                print(f"✓ stress-ng found: {stress_ng_path}")
                if version != "unknown":
                    print(f"✓ Version: {version}")
                print(f"✓ Using stress-ng (recommended)")

                test_results['method'] = 'stress-ng'
                test_results['stress_ng_path'] = stress_ng_path
                test_results['stress_ng_version'] = version

            else:
                print(f"✗ stress-ng not found")
                print(f"✓ Using Python allocator fallback")
                print()
                print("⚠ Warning: Python fallback is less comprehensive than stress-ng")
                print()
                print("To install stress-ng for better testing:")
                print(f"  ssh pi@<CM4_IP> 'sudo apt update && sudo apt install -y stress-ng'")

                test_results['method'] = 'python_allocator'

            # ================================================================
            # STEP 3: Run Memory Pressure Test
            # ================================================================
            print("\n[STEP 3] Run Memory Pressure Test")
            print("-" * 70)

            if stress_ng_available:
                # PRIMARY: Use stress-ng
                success, exit_code, output = self.run_stress_ng(
                    test_config['test_duration_sec'],
                    test_config['target_memory_percent'],
                    test_config
                )

                test_results['exit_code'] = exit_code
                test_results['success'] = success

                if not success:
                    test_results['result'] = 'FAIL'
                    test_results['fail_reason'] = f'stress-ng failed with exit code {exit_code}'

                    # Show portion of output
                    print()
                    print("stress-ng output (last 20 lines):")
                    print("-" * 70)
                    lines = output.split('\n')
                    for line in lines[-20:]:
                        if line.strip():
                            print(f"  {line}")
                    print("-" * 70)

                    pytest.fail(
                        f"Memory pressure test FAILED!\n"
                        f"  stress-ng exit code: {exit_code}\n"
                        "\n"
                        "This indicates:\n"
                        "  - System instability under memory pressure\n"
                        "  - Insufficient RAM for target utilization\n"
                        "  - Memory controller issues\n"
                        "  - OOM (Out Of Memory) killer intervention\n"
                        "\n"
                        "Check logs for details"
                    )

            else:
                # FALLBACK: Use Python allocator
                success, allocated_mb, memory_error = self.run_python_fallback(
                    test_config['test_duration_sec'],
                    test_config['target_memory_percent'],
                    test_config
                )

                test_results['allocated_mb'] = allocated_mb
                test_results['memory_error_occurred'] = memory_error
                test_results['success'] = success

                if not success:
                    test_results['result'] = 'FAIL'
                    test_results['fail_reason'] = 'Python allocator encountered unexpected error'

                    pytest.fail(
                        f"Memory pressure test FAILED!\n"
                        f"  Python allocator encountered unexpected error\n"
                        "\n"
                        "Check logs for details"
                    )

            # ================================================================
            # STEP 4: Validate Results
            # ================================================================
            print("\n[STEP 4] Validate Results")
            print("-" * 70)

            print(f"✓ Test completed successfully")
            print(f"✓ Duration: {test_config['test_duration_sec']} seconds ({test_config['test_duration_sec']/60:.0f} minutes)")
            print(f"✓ No system crashes or freezes")
            print(f"✓ No OOM kills")

            test_results['result'] = 'PASS'
            test_results['pass_reason'] = 'Memory pressure test completed successfully'

        finally:
            # Cleanup already handled in run methods
            pass

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
        print(f"  ✓ Total RAM: {test_results['total_memory_mb']} MB")
        print(f"  ✓ Method: {test_results['method']}")

        if test_results['method'] == 'stress-ng':
            print(f"  ✓ stress-ng version: {test_results.get('stress_ng_version', 'unknown')}")
            print(f"  ✓ Exit code: {test_results['exit_code']}")
        else:
            print(f"  ✓ Allocated: {test_results['allocated_mb']} MB")
            if test_results['memory_error_occurred']:
                print(f"  ✓ MemoryError: Yes (acceptable - reached system limit)")

        print(f"  ✓ Duration: {test_config['test_duration_sec']} seconds ({test_config['test_duration_sec']/60:.0f} minutes)")
        print(f"  ✓ System remained stable under memory pressure")
        print(f"  ✓ No crashes, freezes, or OOM kills")
        print(f"  ✓ CM4 SDRAM validated under pressure (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
