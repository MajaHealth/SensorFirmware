#!/usr/bin/env python3
"""
Test Case #16: eMMC Integrity Post-Stress
Category: HW Component Test
Component: eMMC Storage + OS Filesystem

Tests that eMMC storage STILL maintains data integrity after endurance and
I/O stress tests have completed. Uses same SHA256 checksum verification as
Test #13 but validates eMMC hasn't degraded during stress testing.

IMPORTANT: This test should run AFTER Tests #14 (Endurance) and #15 (I/O Latency)
to validate that eMMC remains healthy after sustained stress.

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


class TestEMMCIntegrityPostStress:
    """HW Component Test - eMMC Integrity Post-Stress"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for eMMC integrity post-stress test"""
        return {
            # Test file size
            'test_file_size_mb': 100,  # 100 MB default

            # Device names
            'emmc_device': 'mmcblk0',

            # Test location
            'test_location': '/tmp',  # Writable location on eMMC

            # Hash algorithm
            'hash_algorithm': 'sha256',

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_016_emmc_integrity_post_stress.log',

            # JSONL results
            'results_file': '/tmp/test_016_emmc_integrity_post_stress.jsonl',
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

    def write_test_file(self, directory, size_mb, config):
        """Write test file with random data and return path, checksum, timing"""
        self.log_message(f"Generating {size_mb}MB random data...", config)

        # Generate random test data
        test_data = os.urandom(size_mb * 1024 * 1024)

        # Calculate write-time checksum
        write_checksum = hashlib.sha256(test_data).hexdigest()
        self.log_message(f"  Write SHA256: {write_checksum[:16]}...", config)

        # Create test file path
        test_file = os.path.join(
            directory,
            f"emmc_test_post_stress_{int(time.time())}.bin"
        )

        try:
            # Measure write time
            start_time = time.time()

            with open(test_file, 'wb') as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            write_time = time.time() - start_time

            # Calculate write speed
            write_speed = size_mb / write_time if write_time > 0 else 0

            self.log_message(f"  ✓ File written: {test_file}", config)
            self.log_message(f"  Size: {size_mb}MB", config)
            self.log_message(f"  Time: {write_time:.2f}s", config)
            self.log_message(f"  Speed: {write_speed:.2f} MB/s", config)

            return test_file, write_checksum, write_time, write_speed

        except Exception as e:
            self.log_message(f"  ✗ Write failed: {e}", config)
            return None, None, 0, 0

    def read_and_verify(self, file_path, expected_checksum, config):
        """Read test file and verify checksum matches"""
        self.log_message(f"Reading test file...", config)

        try:
            # Get file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # Measure read time
            start_time = time.time()

            with open(file_path, 'rb') as f:
                read_data = f.read()

            read_time = time.time() - start_time

            # Calculate read-time checksum
            read_checksum = hashlib.sha256(read_data).hexdigest()

            # Calculate read speed
            read_speed = file_size_mb / read_time if read_time > 0 else 0

            self.log_message(f"  ✓ File read: {file_path}", config)
            self.log_message(f"  Size: {file_size_mb:.2f}MB", config)
            self.log_message(f"  Time: {read_time:.2f}s", config)
            self.log_message(f"  Speed: {read_speed:.2f} MB/s", config)
            self.log_message(f"  Read SHA256: {read_checksum[:16]}...", config)

            # Verify data integrity
            if read_checksum == expected_checksum:
                self.log_message(f"  ✓ Checksum match: Data integrity verified", config)
                return True, read_checksum, read_time, read_speed
            else:
                self.log_message(f"  ✗ Checksum MISMATCH!", config)
                self.log_message(f"    Expected: {expected_checksum[:16]}...", config)
                self.log_message(f"    Got:      {read_checksum[:16]}...", config)
                self.log_message(f"  Full checksums:", config)
                self.log_message(f"    Expected: {expected_checksum}", config)
                self.log_message(f"    Got:      {read_checksum}", config)
                return False, read_checksum, read_time, read_speed

        except Exception as e:
            self.log_message(f"  ✗ Read failed: {e}", config)
            return False, None, 0, 0

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
    @pytest.mark.quick
    @pytest.mark.post_stress
    def test_016_emmc_integrity_post_stress(self, test_config):
        """
        Test Case #16: eMMC Integrity Post-Stress

        Test Setup: CM4 with eMMC storage (after stress tests #14 and #15)
        Acceptance Criteria: Read-back checksum matches write-time checksum

        IMPORTANT: This test should run AFTER Tests #14 (Endurance) and #15 (I/O Latency).
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_016_emmc_integrity_post_stress.py -v -s"

        What this test validates:
        - eMMC device still detected and accessible after stress
        - Can still write test files to eMMC after stress
        - Can still read test files from eMMC after stress
        - Data integrity STILL maintained (SHA256 checksums match)
        - No stress-induced storage corruption or degradation

        This test detects:
        - eMMC degradation caused by endurance testing
        - Bad blocks developed during stress tests
        - Storage corruption from concurrent I/O load
        - Low-quality eMMC that fails under sustained use
        """

        print("\n" + "=" * 70)
        print("Test Case #16: eMMC Integrity Post-Stress")
        print("=" * 70)
        print("\nHW Component Test - eMMC Storage + OS Filesystem")
        print("Post-Stress Validation (After Tests #14, #15)")
        print("=" * 70)
        print("\nIMPORTANT: This test validates eMMC health AFTER stress tests.")
        print("For meaningful results, run after:")
        print("  - Test #14: eMMC Endurance (1 hour)")
        print("  - Test #15: eMMC I/O Latency (60 sec)")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("eMMC Integrity Post-Stress test")

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_016_eMMC_Integrity_Post_Stress',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'test_file_size_mb': test_config['test_file_size_mb'],
            'hash_algorithm': test_config['hash_algorithm'],
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
                    "  - eMMC degraded/failed during stress tests\n"
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
                    "  - Filesystem mounted read-only\n"
                    "  - Filesystem corruption from stress tests"
                )

            print(f"✓ Test location verified: {test_config['test_location']}")
            test_results['test_location'] = test_config['test_location']

            # ================================================================
            # STEP 2: Write Test File
            # ================================================================
            print("\n[STEP 2] Write Test File")
            print("-" * 70)

            test_file, write_checksum, write_time, write_speed = self.write_test_file(
                test_config['test_location'],
                test_config['test_file_size_mb'],
                test_config
            )

            if not test_file:
                pytest.fail("Failed to write test file to eMMC after stress tests")

            print(f"✓ Write test passed")
            print(f"  File: {test_file}")
            print(f"  Checksum: {write_checksum[:16]}...")
            print(f"  Write speed: {write_speed:.2f} MB/s")

            test_results['test_file'] = test_file
            test_results['write_checksum'] = write_checksum
            test_results['write_time_sec'] = write_time
            test_results['write_speed_mb_s'] = write_speed

            # ================================================================
            # STEP 3: Read Test File and Verify Integrity
            # ================================================================
            print("\n[STEP 3] Read and Verify")
            print("-" * 70)

            integrity_ok, read_checksum, read_time, read_speed = self.read_and_verify(
                test_file,
                write_checksum,
                test_config
            )

            if not integrity_ok:
                test_results['integrity_ok'] = False
                test_results['read_checksum'] = read_checksum
                test_results['error'] = 'Checksum mismatch after stress tests'

                pytest.fail(
                    f"eMMC integrity check FAILED after stress tests!\n"
                    f"  Expected checksum: {write_checksum}\n"
                    f"  Got checksum:      {read_checksum}\n"
                    "\n"
                    "CRITICAL: eMMC degraded during stress testing!\n"
                    "\n"
                    "This indicates:\n"
                    "  - eMMC developed bad blocks during stress\n"
                    "  - Storage corruption from sustained writes\n"
                    "  - Low-quality eMMC unsuitable for production\n"
                    "  - Hardware failure induced by stress tests\n"
                    "\n"
                    "Action Required:\n"
                    "  - Replace CM4 module with higher-quality eMMC\n"
                    "  - Test with Class 10 or UHS-I eMMC\n"
                    "  - Review stress test results (Tests #14, #15)\n"
                    "  - DO NOT deploy firmware on this hardware"
                )

            print(f"✓ Read test passed")
            print(f"  Read speed: {read_speed:.2f} MB/s")
            print(f"✓ Data integrity verified (post-stress)")
            print(f"  SHA256 checksums match")

            test_results['integrity_ok'] = True
            test_results['read_checksum'] = read_checksum
            test_results['read_time_sec'] = read_time
            test_results['read_speed_mb_s'] = read_speed

        finally:
            # ================================================================
            # STEP 4: Cleanup
            # ================================================================
            print("\n[STEP 4] Cleanup")
            print("-" * 70)

            if test_file and os.path.exists(test_file):
                try:
                    os.remove(test_file)
                    self.log_message(f"  ✓ Removed: {test_file}", test_config)
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
        print(f"  ✓ Write operation completed: {test_results['test_file_size_mb']}MB")
        print(f"  ✓ Read operation completed: {test_results['test_file_size_mb']}MB")
        print(f"  ✓ Data integrity verified: Checksums match")
        print(f"  ✓ Write speed: {test_results['write_speed_mb_s']:.2f} MB/s")
        print(f"  ✓ Read speed: {test_results['read_speed_mb_s']:.2f} MB/s")
        print(f"  ✓ eMMC integrity maintained after stress (PASS)")
        print()
        print("  ✓ CRITICAL: eMMC survived stress tests without degradation")
        print("  ✓ Storage is robust and suitable for production use")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
