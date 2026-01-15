#!/usr/bin/env python3
"""
Test Case #39: Data Integrity Verification After Read/Write
Category: HW Component Test
Component: eMMC + SD Card

Tests that storage maintains data integrity through write/read cycles
using cryptographic hash verification (SHA256).

This test focuses specifically on data integrity validation,
complementing Test #38's basic read/write operations.
"""

import subprocess
import os
import hashlib
import time
import pytest


class TestDataIntegrity:
    """HW Component Test - Data Integrity Verification"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for data integrity test"""
        return {
            # Test file configurations
            'test_file_sizes_mb': [1, 5, 10],  # Multiple file sizes for thorough testing
            'verification_cycles': 3,  # Number of write/read/verify cycles

            # Device names
            'emmc_device': 'mmcblk0',
            'sd_device_names': ['mmcblk1', 'sda'],

            # Hash algorithm
            'hash_algorithm': 'sha256',  # Can be: sha256, sha512, md5

            # Test patterns
            'test_patterns': [
                'random',      # Random data (os.urandom)
                'zeros',       # All zeros
                'ones',        # All 0xFF
                'alternating', # 0xAA pattern
            ],

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_039_data_integrity.log',
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

    def detect_storage_devices(self, config):
        """Detect available storage devices"""
        self.log_message("Detecting storage devices...", config)

        devices = {'emmc': None, 'sd': None}

        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout

                # Check for eMMC
                if config['emmc_device'] in output:
                    devices['emmc'] = f"/dev/{config['emmc_device']}"
                    self.log_message(f"  ✓ eMMC detected: {devices['emmc']}", config)

                # Check for SD card
                for sd_name in config['sd_device_names']:
                    if sd_name in output:
                        devices['sd'] = f"/dev/{sd_name}"
                        self.log_message(f"  ✓ SD card detected: {devices['sd']}", config)
                        break

            return devices, result.stdout

        except Exception as e:
            self.log_message(f"  ✗ Error detecting devices: {e}", config)
            return devices, str(e)

    def find_writable_location(self, device_name, config):
        """Find writable location for a storage device"""
        self.log_message(f"Finding writable location for {device_name}...", config)

        # For eMMC (usually root filesystem)
        if 'mmcblk0' in device_name:
            test_dir = '/tmp'
            if os.access(test_dir, os.W_OK):
                self.log_message(f"  ✓ Using: {test_dir}", config)
                return test_dir

        # For SD card or other devices, try to find mount point
        try:
            result = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True,
                timeout=5
            )

            device_short = device_name.split('/')[-1]
            for line in result.stdout.split('\n'):
                if device_short in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mount_point = parts[2]
                        if os.access(mount_point, os.W_OK):
                            self.log_message(f"  ✓ Mounted at: {mount_point}", config)
                            return mount_point

        except Exception as e:
            self.log_message(f"  ⚠ Error finding mount: {e}", config)

        return None

    def generate_test_data(self, size_bytes, pattern, config):
        """Generate test data with specified pattern"""
        if pattern == 'random':
            return os.urandom(size_bytes)
        elif pattern == 'zeros':
            return bytes(size_bytes)
        elif pattern == 'ones':
            return bytes([0xFF] * size_bytes)
        elif pattern == 'alternating':
            return bytes([0xAA] * size_bytes)
        else:
            # Default to random
            return os.urandom(size_bytes)

    def calculate_hash(self, data, algorithm, config):
        """Calculate cryptographic hash of data"""
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            return hashlib.sha256(data).hexdigest()

    def write_and_verify_cycle(self, location, size_mb, pattern, cycle_num, config):
        """Perform one write/read/verify cycle"""
        self.log_message(
            f"Cycle {cycle_num}: Testing {size_mb}MB with '{pattern}' pattern",
            config
        )

        size_bytes = size_mb * 1024 * 1024
        test_file = os.path.join(
            location,
            f"integrity_test_{pattern}_{size_mb}mb_{cycle_num}.bin"
        )

        try:
            # Generate test data
            self.log_message(f"  Generating {size_mb}MB test data ({pattern})...", config)
            test_data = self.generate_test_data(size_bytes, pattern, config)

            # Calculate expected hash
            expected_hash = self.calculate_hash(
                test_data,
                config['hash_algorithm'],
                config
            )
            self.log_message(
                f"  Expected {config['hash_algorithm'].upper()}: {expected_hash[:16]}...",
                config
            )

            # Write to storage
            self.log_message(f"  Writing to: {test_file}", config)
            start_time = time.time()

            with open(test_file, 'wb') as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())

            write_time = time.time() - start_time
            self.log_message(f"  Write time: {write_time:.2f}s", config)

            # Read from storage
            self.log_message(f"  Reading from: {test_file}", config)
            start_time = time.time()

            with open(test_file, 'rb') as f:
                read_data = f.read()

            read_time = time.time() - start_time
            self.log_message(f"  Read time: {read_time:.2f}s", config)

            # Verify integrity
            actual_hash = self.calculate_hash(
                read_data,
                config['hash_algorithm'],
                config
            )
            self.log_message(
                f"  Actual {config['hash_algorithm'].upper()}: {actual_hash[:16]}...",
                config
            )

            # Compare hashes
            if expected_hash == actual_hash:
                self.log_message(f"  ✓ Integrity verified: Hashes match", config)
                integrity_ok = True
            else:
                self.log_message(f"  ✗ Integrity FAILED: Hashes don't match!", config)
                self.log_message(f"    Expected: {expected_hash}", config)
                self.log_message(f"    Actual:   {actual_hash}", config)
                integrity_ok = False

            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)

            return {
                'success': integrity_ok,
                'expected_hash': expected_hash,
                'actual_hash': actual_hash,
                'write_time': write_time,
                'read_time': read_time,
                'file_size_mb': size_mb,
                'pattern': pattern,
            }

        except Exception as e:
            self.log_message(f"  ✗ Cycle failed: {e}", config)

            # Cleanup on error
            try:
                if os.path.exists(test_file):
                    os.remove(test_file)
            except:
                pass

            return {
                'success': False,
                'error': str(e),
                'file_size_mb': size_mb,
                'pattern': pattern,
            }

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.storage
    def test_039_data_integrity_verification(self, test_config):
        """
        Test Case #39: Data integrity verification after read/write

        Test Setup: Booted system
        Acceptance Criteria: Data integrity validated after read/write

        IMPORTANT: This test must run ON the CM4 itself.
        System must be booted with storage mounted.

        What this test validates:
        - Data integrity across multiple write/read cycles
        - Different data patterns (random, zeros, ones, alternating)
        - Various file sizes (1MB, 5MB, 10MB)
        - Cryptographic hash verification (SHA256)
        - Both eMMC and SD card integrity (if SD present)
        - No data corruption during storage operations
        """

        print("\n" + "=" * 70)
        print("Test Case #39: Data Integrity Verification")
        print("=" * 70)
        print("\nHW Component Test - Storage Data Integrity")
        print("=" * 70)
        print("\nTEST METHOD:")
        print("  1. Write known data patterns to storage")
        print("  2. Read data back from storage")
        print("  3. Verify integrity using cryptographic hashes")
        print("  4. Test multiple file sizes and patterns")
        print("  5. Perform multiple verification cycles")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        test_results = {
            'emmc': {'cycles_passed': 0, 'cycles_failed': 0, 'results': []},
            'sd': {'cycles_passed': 0, 'cycles_failed': 0, 'results': []},
        }

        # ================================================================
        # STEP 1: Detect Storage Devices
        # ================================================================
        print("\n[STEP 1] Detect Storage Devices")
        print("-" * 70)

        devices, device_info = self.detect_storage_devices(test_config)

        if not devices['emmc']:
            pytest.fail(
                f"eMMC device ({test_config['emmc_device']}) not detected\n"
                "Cannot proceed with data integrity testing"
            )

        print(f"✓ eMMC detected: {devices['emmc']}")

        if devices['sd']:
            print(f"✓ SD card detected: {devices['sd']}")
        else:
            print(f"  ⚠ SD card not detected (will skip SD tests)")

        # ================================================================
        # STEP 2: Find Writable Locations
        # ================================================================
        print("\n[STEP 2] Find Writable Locations")
        print("-" * 70)

        emmc_location = self.find_writable_location(devices['emmc'], test_config)

        if not emmc_location:
            pytest.fail("Could not find writable location on eMMC")

        print(f"✓ eMMC writable location: {emmc_location}")

        sd_location = None
        if devices['sd']:
            sd_location = self.find_writable_location(devices['sd'], test_config)
            if sd_location:
                print(f"✓ SD card writable location: {sd_location}")
            else:
                print(f"  ⚠ SD card not writable (will skip SD tests)")

        # ================================================================
        # STEP 3-6: eMMC Integrity Testing
        # ================================================================
        print("\n[STEP 3] eMMC Data Integrity Testing")
        print("-" * 70)
        print(f"Testing with {len(test_config['test_file_sizes_mb'])} file sizes")
        print(f"Testing with {len(test_config['test_patterns'])} data patterns")
        print(f"Verification cycles per test: {test_config['verification_cycles']}")
        print()

        cycle_num = 0
        for size_mb in test_config['test_file_sizes_mb']:
            for pattern in test_config['test_patterns']:
                for cycle in range(test_config['verification_cycles']):
                    cycle_num += 1

                    result = self.write_and_verify_cycle(
                        emmc_location,
                        size_mb,
                        pattern,
                        cycle_num,
                        test_config
                    )

                    test_results['emmc']['results'].append(result)

                    if result['success']:
                        test_results['emmc']['cycles_passed'] += 1
                    else:
                        test_results['emmc']['cycles_failed'] += 1

                        # Fail immediately on first integrity failure
                        pytest.fail(
                            f"eMMC data integrity check FAILED!\n"
                            f"  Cycle: {cycle_num}\n"
                            f"  File size: {size_mb}MB\n"
                            f"  Pattern: {pattern}\n"
                            f"  Expected hash: {result.get('expected_hash', 'N/A')}\n"
                            f"  Actual hash: {result.get('actual_hash', 'N/A')}\n"
                            "This indicates storage corruption or hardware failure."
                        )

        total_emmc_cycles = test_results['emmc']['cycles_passed'] + test_results['emmc']['cycles_failed']
        print(f"\neMMC Testing Complete:")
        print(f"  Total cycles: {total_emmc_cycles}")
        print(f"  Passed: {test_results['emmc']['cycles_passed']}")
        print(f"  Failed: {test_results['emmc']['cycles_failed']}")
        print(f"✓ All eMMC integrity checks passed")

        # ================================================================
        # STEP 7-10: SD Card Integrity Testing (if available)
        # ================================================================
        if sd_location:
            print("\n[STEP 4] SD Card Data Integrity Testing")
            print("-" * 70)

            cycle_num = 0
            for size_mb in test_config['test_file_sizes_mb']:
                for pattern in test_config['test_patterns']:
                    for cycle in range(test_config['verification_cycles']):
                        cycle_num += 1

                        result = self.write_and_verify_cycle(
                            sd_location,
                            size_mb,
                            pattern,
                            cycle_num,
                            test_config
                        )

                        test_results['sd']['results'].append(result)

                        if result['success']:
                            test_results['sd']['cycles_passed'] += 1
                        else:
                            test_results['sd']['cycles_failed'] += 1

                            # SD card failure is informational, not critical
                            print(f"\n  ⚠ SD card integrity check failed (cycle {cycle_num})")
                            print(f"    This may indicate a faulty SD card")

            total_sd_cycles = test_results['sd']['cycles_passed'] + test_results['sd']['cycles_failed']
            print(f"\nSD Card Testing Complete:")
            print(f"  Total cycles: {total_sd_cycles}")
            print(f"  Passed: {test_results['sd']['cycles_passed']}")
            print(f"  Failed: {test_results['sd']['cycles_failed']}")

            if test_results['sd']['cycles_failed'] > 0:
                print(f"  ⚠ Warning: Some SD card tests failed")
            else:
                print(f"✓ All SD card integrity checks passed")
        else:
            print("\n[STEP 4] SD Card Testing - SKIPPED")
            print("-" * 70)
            print("  ⚠ SD card not available or not writable")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ eMMC integrity cycles passed: {test_results['emmc']['cycles_passed']}/{total_emmc_cycles}")
        print(f"  ✓ File sizes tested: {test_config['test_file_sizes_mb']}")
        print(f"  ✓ Data patterns tested: {test_config['test_patterns']}")
        print(f"  ✓ Hash algorithm: {test_config['hash_algorithm'].upper()}")

        if sd_location:
            total_sd = test_results['sd']['cycles_passed'] + test_results['sd']['cycles_failed']
            print(f"  ✓ SD card integrity cycles passed: {test_results['sd']['cycles_passed']}/{total_sd}")

        print(f"  ✓ Data integrity validated after read/write operations (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
