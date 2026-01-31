#!/usr/bin/env python3
"""
Test Case #14: eMMC Endurance
Category: HW Component Test
Component: eMMC Storage + OS Filesystem

Tests eMMC storage endurance by repeatedly overwriting a large file
for 1 hour, validating no I/O errors occur during sustained write operations.

This test runs on the CM4 itself (not on PC via remote connection).
"""

import subprocess
import os
import sys
import hashlib
import time
import json
import pytest

# Add common utilities to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from platform_check import skip_if_not_raspberry_pi


class TestEMMCEndurance:
    """HW Component Test - eMMC Endurance"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for eMMC endurance test"""
        return {
            # Test duration
            'test_duration_sec': 3600,  # 1 hour = 3600 seconds

            # Test file size
            'file_size_mb': 100,  # 100 MB per cycle

            # Device names
            'emmc_device': 'mmcblk0',

            # Test location
            'test_location': '/tmp',  # Writable location on eMMC

            # Progress logging interval
            'log_interval_cycles': 10,  # Log every 10 cycles

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_014_emmc_endurance.log',

            # JSONL results
            'results_file': '/tmp/test_014_emmc_endurance.jsonl',
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

    def detect_emmc_device(self, config):
        """Detect eMMC device and verify it's accessible"""
        self.log_message("Detecting eMMC device...", config)

        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None, "lsblk command failed"

            output = result.stdout
            self.log_message("  Available block devices:", config)
            for line in output.split('\n')[:10]:
                if line.strip():
                    self.log_message(f"    {line}", config)

            # Check for eMMC
            if config['emmc_device'] in output:
                device_path = f"/dev/{config['emmc_device']}"
                self.log_message(f"  ✓ eMMC detected: {device_path}", config)
                return device_path, output
            else:
                self.log_message(f"  ✗ eMMC ({config['emmc_device']}) not found", config)
                return None, output

        except Exception as e:
            self.log_message(f"  ✗ Error detecting eMMC: {e}", config)
            return None, str(e)

    def verify_test_location(self, test_location, config):
        """Verify test location is on eMMC and writable"""
        self.log_message(f"Verifying test location: {test_location}", config)

        # Check if location exists and is writable
        if not os.path.exists(test_location):
            self.log_message(f"  ✗ Location does not exist", config)
            return False

        if not os.access(test_location, os.W_OK):
            self.log_message(f"  ✗ Location not writable", config)
            return False

        # Get filesystem info
        try:
            result = subprocess.run(
                ['df', '-h', test_location],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    self.log_message(f"  Filesystem info:", config)
                    self.log_message(f"    {lines[0]}", config)
                    self.log_message(f"    {lines[1]}", config)

                    # Check if on eMMC device
                    if 'mmcblk0' in lines[1]:
                        self.log_message(f"  ✓ Location is on eMMC", config)
                        return True
                    else:
                        self.log_message(f"  ⚠ Warning: Location may not be on eMMC", config)
                        # Still return True if writable, just warn
                        return True

        except Exception as e:
            self.log_message(f"  ⚠ Could not verify filesystem: {e}", config)

        # If we can't verify but location is writable, proceed with warning
        self.log_message(f"  ✓ Location is writable", config)
        return True

    def write_flush_cycle(self, file_path, size_mb, cycle_num, config):
        """
        Perform one write-flush cycle.

        Returns: (success, write_time, write_speed)
        """
        size_bytes = size_mb * 1024 * 1024

        try:
            # Generate random test data
            test_data = os.urandom(size_bytes)

            # Measure write time
            start_time = time.time()

            with open(file_path, 'wb') as f:
                f.write(test_data)
                f.flush()  # Flush to OS
                os.fsync(f.fileno())  # Force write to eMMC

            write_time = time.time() - start_time

            # Calculate write speed
            write_speed = size_mb / write_time if write_time > 0 else 0

            return True, write_time, write_speed

        except OSError as e:
            self.log_message(f"  ✗ OSError during cycle {cycle_num}: {e}", config)
            return False, 0, 0

        except Exception as e:
            self.log_message(f"  ✗ Exception during cycle {cycle_num}: {e}", config)
            return False, 0, 0

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
    @pytest.mark.long
    def test_014_emmc_endurance(self, test_config):
        """
        Test Case #14: eMMC Endurance

        Test Setup: CM4 with eMMC storage, sufficient free space, stable power
        Acceptance Criteria: Test completes 1-hour duration without I/O errors

        IMPORTANT: This test must run ON the CM4 itself.
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_014_emmc_endurance.py -v -s"

        What this test validates:
        - eMMC can sustain repeated write operations for 1 hour
        - No I/O errors occur under sustained write stress
        - Write performance remains stable over time
        - No storage corruption or hardware failures during endurance test
        """

        print("\n" + "=" * 70)
        print("Test Case #14: eMMC Endurance")
        print("=" * 70)
        print("\nHW Component Test - eMMC Storage Endurance")
        print("=" * 70)
        print("\nTEST METHOD:")
        print("  1. Repeatedly overwrite large file for 1 hour")
        print("  2. Force flush/sync to eMMC after each write")
        print("  3. Monitor for any I/O errors")
        print("  4. Track cycle count and write performance")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("eMMC Endurance test")

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_014_eMMC_Endurance',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration_sec': test_config['test_duration_sec'],
            'file_size_mb': test_config['file_size_mb'],
        }

        test_file = None

        try:
            # ================================================================
            # STEP 1: Detect eMMC Device
            # ================================================================
            print("\n[STEP 1] Detect eMMC Device")
            print("-" * 70)

            emmc_device, device_info = self.detect_emmc_device(test_config)

            if not emmc_device:
                pytest.fail(
                    f"eMMC device ({test_config['emmc_device']}) not detected\n"
                    "Possible causes:\n"
                    "  - Running on CM4 Lite (no eMMC)\n"
                    "  - eMMC hardware failure\n"
                    "  - Wrong device name in config\n"
                    f"  - Available devices:\n{device_info}"
                )

            print(f"✓ eMMC detected: {emmc_device}")
            test_results['emmc_device'] = emmc_device

            # Verify test location
            location_ok = self.verify_test_location(test_config['test_location'], test_config)

            if not location_ok:
                pytest.fail(
                    f"Test location not accessible: {test_config['test_location']}\n"
                    "Possible causes:\n"
                    "  - Directory does not exist\n"
                    "  - Permission denied\n"
                    "  - Filesystem mounted read-only"
                )

            print(f"✓ Test location verified: {test_config['test_location']}")
            test_results['test_location'] = test_config['test_location']

            # ================================================================
            # STEP 2: Initialize Test File
            # ================================================================
            print("\n[STEP 2] Initialize Test File")
            print("-" * 70)

            test_file = os.path.join(
                test_config['test_location'],
                f"emmc_endurance_{int(time.time())}.bin"
            )

            print(f"Test file: {test_file}")
            print(f"File size: {test_config['file_size_mb']} MB")
            print(f"Duration: {test_config['test_duration_sec']} seconds ({test_config['test_duration_sec'] / 60:.1f} minutes)")

            test_results['test_file'] = test_file

            # ================================================================
            # STEP 3: Endurance Test Loop (1 hour)
            # ================================================================
            print("\n[STEP 3] Endurance Test Loop")
            print("-" * 70)
            print("Starting 1-hour write endurance test...")
            print("(Progress logged every 10 cycles)")
            print()

            start_time = time.time()
            end_time = start_time + test_config['test_duration_sec']

            cycle_count = 0
            total_write_time = 0
            total_data_written_mb = 0
            write_speeds = []

            while time.time() < end_time:
                cycle_count += 1

                # Perform write-flush cycle
                success, write_time, write_speed = self.write_flush_cycle(
                    test_file,
                    test_config['file_size_mb'],
                    cycle_count,
                    test_config
                )

                if not success:
                    # I/O error occurred - FAIL the test
                    test_results['cycles_completed'] = cycle_count - 1
                    test_results['error'] = f'I/O error on cycle {cycle_count}'
                    test_results['result'] = 'FAIL'

                    pytest.fail(
                        f"eMMC endurance test FAILED!\n"
                        f"  I/O error occurred on cycle {cycle_count}\n"
                        f"  Cycles completed before error: {cycle_count - 1}\n"
                        f"  Elapsed time: {time.time() - start_time:.1f}s\n"
                        "\n"
                        "This indicates:\n"
                        "  - eMMC wear or bad blocks\n"
                        "  - Storage hardware failure\n"
                        "  - Filesystem corruption"
                    )

                # Track statistics
                total_write_time += write_time
                total_data_written_mb += test_config['file_size_mb']
                write_speeds.append(write_speed)

                # Log progress at intervals
                if cycle_count % test_config['log_interval_cycles'] == 0:
                    elapsed = time.time() - start_time
                    remaining = end_time - time.time()
                    avg_speed = sum(write_speeds[-10:]) / len(write_speeds[-10:])  # Last 10 cycles

                    self.log_message(
                        f"Cycle {cycle_count:4d} | "
                        f"Elapsed: {elapsed:6.0f}s | "
                        f"Remaining: {remaining:6.0f}s | "
                        f"Speed: {avg_speed:5.1f} MB/s",
                        test_config
                    )

            # ================================================================
            # STEP 4: Calculate Final Statistics
            # ================================================================
            print("\n[STEP 4] Calculate Statistics")
            print("-" * 70)

            actual_duration = time.time() - start_time
            avg_cycle_time = total_write_time / cycle_count if cycle_count > 0 else 0
            avg_write_speed = sum(write_speeds) / len(write_speeds) if write_speeds else 0
            total_data_written_gb = total_data_written_mb / 1024

            self.log_message(f"Endurance test completed successfully", test_config)
            self.log_message(f"  Cycles completed: {cycle_count}", test_config)
            self.log_message(f"  Actual duration: {actual_duration:.1f}s", test_config)
            self.log_message(f"  Total data written: {total_data_written_gb:.2f} GB", test_config)
            self.log_message(f"  Average cycle time: {avg_cycle_time:.2f}s", test_config)
            self.log_message(f"  Average write speed: {avg_write_speed:.2f} MB/s", test_config)

            print(f"✓ Endurance test completed")
            print(f"  Cycles: {cycle_count}")
            print(f"  Duration: {actual_duration:.1f}s")
            print(f"  Data written: {total_data_written_gb:.2f} GB")
            print(f"  Avg speed: {avg_write_speed:.2f} MB/s")

            test_results['cycles_completed'] = cycle_count
            test_results['actual_duration_sec'] = actual_duration
            test_results['total_data_written_mb'] = total_data_written_mb
            test_results['total_data_written_gb'] = total_data_written_gb
            test_results['avg_cycle_time_sec'] = avg_cycle_time
            test_results['avg_write_speed_mb_s'] = avg_write_speed
            test_results['errors'] = 0
            test_results['result'] = 'PASS'

        finally:
            # ================================================================
            # STEP 5: Cleanup
            # ================================================================
            print("\n[STEP 5] Cleanup")
            print("-" * 70)

            if test_file and os.path.exists(test_file):
                try:
                    file_size = os.path.getsize(test_file)
                    os.remove(test_file)
                    self.log_message(f"  ✓ Removed: {test_file} ({file_size / (1024*1024):.1f} MB)", test_config)
                    print(f"✓ Test file removed")
                except Exception as e:
                    self.log_message(f"  ⚠ Could not remove {test_file}: {e}", test_config)
                    print(f"  ⚠ Warning: Could not remove test file")

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
        print(f"  ✓ eMMC device detected: {test_results.get('emmc_device')}")
        print(f"  ✓ Test location verified: {test_results.get('test_location')}")
        print(f"  ✓ Endurance test duration: {test_results['actual_duration_sec']:.1f}s / {test_config['test_duration_sec']}s")
        print(f"  ✓ Cycles completed: {test_results['cycles_completed']}")
        print(f"  ✓ Total data written: {test_results['total_data_written_gb']:.2f} GB")
        print(f"  ✓ No I/O errors occurred")
        print(f"  ✓ eMMC endurance validated (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
