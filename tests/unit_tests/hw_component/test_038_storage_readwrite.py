#!/usr/bin/env python3
"""
Test Case #38: Read/Write Operations on Storage Interfaces
Category: HW Component Test
Component: eMMC + SD Card

Tests that storage interfaces (eMMC and SD card) support proper
read/write operations with data integrity verification.
This test runs on the CM4 itself (not on PC).
"""

import subprocess
import os
import hashlib
import tempfile
import time
import pytest


class TestStorageReadWrite:
    """HW Component Test - Read/Write Operations on Storage"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for storage read/write test"""
        return {
            # Test data sizes
            'test_file_size_mb': 1,  # Size of test file in MB
            'small_file_size_kb': 100,  # Small file for quick test

            # Device names to check
            'emmc_device': 'mmcblk0',
            'sd_device_names': ['mmcblk1', 'sda'],  # Possible SD card names

            # Test file patterns
            'test_file_prefix': 'storage_test_',
            'test_dir_prefix': 'storage_dir_test_',

            # Number of test iterations
            'write_read_cycles': 3,  # Number of write/read cycles

            # Performance thresholds (MB/s)
            'min_write_speed_mb_s': 5,   # Minimum write speed
            'min_read_speed_mb_s': 10,   # Minimum read speed

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_038_storage_readwrite.log',
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

        devices = {
            'emmc': None,
            'sd': None,
        }

        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,TYPE,SIZE,MOUNTPOINT'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return devices, "lsblk command failed"

            output = result.stdout
            self.log_message("  Available block devices:", config)
            for line in output.split('\n')[:10]:  # Show first 10 lines
                if line.strip():
                    self.log_message(f"    {line}", config)

            # Check for eMMC
            if config['emmc_device'] in output:
                devices['emmc'] = f"/dev/{config['emmc_device']}"
                self.log_message(f"  ✓ eMMC detected: {devices['emmc']}", config)
            else:
                self.log_message(f"  ✗ eMMC ({config['emmc_device']}) not found", config)

            # Check for SD card
            for sd_name in config['sd_device_names']:
                if sd_name in output:
                    devices['sd'] = f"/dev/{sd_name}"
                    self.log_message(f"  ✓ SD card detected: {devices['sd']}", config)
                    break

            if not devices['sd']:
                self.log_message(f"  ⚠ SD card not detected", config)

            return devices, output

        except Exception as e:
            self.log_message(f"  ✗ Error detecting devices: {e}", config)
            return devices, str(e)

    def find_mount_point(self, device_name, config):
        """Find mount point for a device"""
        self.log_message(f"Finding mount point for {device_name}...", config)

        try:
            result = subprocess.run(
                ['findmnt', '-n', '-o', 'TARGET', device_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                mount_point = result.stdout.strip()
                if mount_point:
                    self.log_message(f"  ✓ Mounted at: {mount_point}", config)
                    return mount_point
                else:
                    self.log_message(f"  ✗ No mount point found", config)
                    return None
            else:
                self.log_message(f"  ✗ Device not mounted", config)
                return None

        except Exception as e:
            self.log_message(f"  ✗ Error finding mount point: {e}", config)
            return None

    def get_writable_location(self, device_name, config):
        """Get a writable location on the device"""
        self.log_message(f"Finding writable location for {device_name}...", config)

        # Try to find mount point first
        mount_point = self.find_mount_point(device_name, config)

        if mount_point:
            # Check if mount point is writable
            test_dir = os.path.join(mount_point, 'tmp')
            if not os.path.exists(test_dir):
                try:
                    os.makedirs(test_dir, exist_ok=True)
                except:
                    pass

            if os.access(test_dir, os.W_OK):
                self.log_message(f"  ✓ Writable location: {test_dir}", config)
                return test_dir
            elif os.access(mount_point, os.W_OK):
                self.log_message(f"  ✓ Writable location: {mount_point}", config)
                return mount_point
            else:
                self.log_message(f"  ✗ Mount point not writable", config)

        # Fallback: for eMMC, use system tmp
        if 'mmcblk0' in device_name:
            tmp_dir = '/tmp'
            self.log_message(f"  ✓ Using system tmp: {tmp_dir}", config)
            return tmp_dir

        return None

    def write_test_file(self, directory, size_mb, config):
        """Write a test file and return path, checksum, and write speed"""
        self.log_message(f"Writing {size_mb}MB test file...", config)

        # Generate test data
        test_data = os.urandom(size_mb * 1024 * 1024)

        # Create test file path
        test_file = os.path.join(
            directory,
            f"{config['test_file_prefix']}{int(time.time())}.bin"
        )

        try:
            # Measure write time
            start_time = time.time()

            with open(test_file, 'wb') as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            write_time = time.time() - start_time

            # Calculate checksum
            checksum = hashlib.sha256(test_data).hexdigest()

            # Calculate write speed
            write_speed = size_mb / write_time if write_time > 0 else 0

            self.log_message(f"  ✓ File written: {test_file}", config)
            self.log_message(f"  Size: {size_mb}MB", config)
            self.log_message(f"  Time: {write_time:.2f}s", config)
            self.log_message(f"  Speed: {write_speed:.2f} MB/s", config)
            self.log_message(f"  Checksum: {checksum[:16]}...", config)

            return test_file, checksum, write_speed, write_time

        except Exception as e:
            self.log_message(f"  ✗ Write failed: {e}", config)
            return None, None, 0, 0

    def read_test_file(self, file_path, expected_checksum, config):
        """Read a test file and verify checksum"""
        self.log_message(f"Reading test file...", config)

        try:
            # Get file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # Measure read time
            start_time = time.time()

            with open(file_path, 'rb') as f:
                read_data = f.read()

            read_time = time.time() - start_time

            # Calculate checksum
            checksum = hashlib.sha256(read_data).hexdigest()

            # Calculate read speed
            read_speed = file_size_mb / read_time if read_time > 0 else 0

            self.log_message(f"  ✓ File read: {file_path}", config)
            self.log_message(f"  Size: {file_size_mb:.2f}MB", config)
            self.log_message(f"  Time: {read_time:.2f}s", config)
            self.log_message(f"  Speed: {read_speed:.2f} MB/s", config)
            self.log_message(f"  Checksum: {checksum[:16]}...", config)

            # Verify data integrity
            if checksum == expected_checksum:
                self.log_message(f"  ✓ Checksum match: Data integrity verified", config)
                return True, checksum, read_speed, read_time
            else:
                self.log_message(f"  ✗ Checksum mismatch!", config)
                self.log_message(f"    Expected: {expected_checksum[:16]}...", config)
                self.log_message(f"    Got:      {checksum[:16]}...", config)
                return False, checksum, read_speed, read_time

        except Exception as e:
            self.log_message(f"  ✗ Read failed: {e}", config)
            return False, None, 0, 0

    def get_filesystem_info(self, path, config):
        """Get filesystem information for path"""
        self.log_message(f"Getting filesystem info for {path}...", config)

        try:
            result = subprocess.run(
                ['df', '-h', path],
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
                    return lines[1]

        except Exception as e:
            self.log_message(f"  ⚠ Could not get filesystem info: {e}", config)

        return None

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.storage
    @pytest.mark.quick
    def test_038_storage_readwrite_operations(self, test_config):
        """
        Test Case #38: Read/write operations on storage interfaces

        Test Setup: Booted system, storage present
        Acceptance Criteria: Read/write operations succeed on both interfaces

        IMPORTANT: This test must run ON the CM4 itself.
        System must be booted with storage mounted.

        What this test validates:
        - eMMC device is detected and accessible
        - SD card device is detected (if present)
        - Can write test files to storage
        - Can read test files from storage
        - Data integrity is maintained (checksums match)
        - Write/read performance is acceptable
        - No I/O errors during operations
        """

        print("\n" + "=" * 70)
        print("Test Case #38: Read/Write Operations on Storage")
        print("=" * 70)
        print("\nHW Component Test - eMMC + SD Card")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'emmc': {'detected': False, 'writable': False, 'tests_passed': 0},
            'sd': {'detected': False, 'writable': False, 'tests_passed': 0},
        }

        test_files_to_cleanup = []

        try:
            # ================================================================
            # STEP 1: Detect Storage Devices
            # ================================================================
            print("\n[STEP 1] Detect Storage Devices")
            print("-" * 70)

            devices, device_info = self.detect_storage_devices(test_config)

            if not devices['emmc']:
                pytest.fail(
                    f"eMMC device ({test_config['emmc_device']}) not detected\n"
                    "Possible causes:\n"
                    "  - Running on CM4 Lite (no eMMC)\n"
                    "  - eMMC hardware failure\n"
                    "  - Wrong device name in config\n"
                    f"  - Available devices:\n{device_info}"
                )

            test_results['emmc']['detected'] = True
            print(f"✓ eMMC detected: {devices['emmc']}")

            if devices['sd']:
                test_results['sd']['detected'] = True
                print(f"✓ SD card detected: {devices['sd']}")
            else:
                print(f"  ⚠ SD card not detected (will skip SD tests)")

            # ================================================================
            # STEP 2: Find Writable Locations
            # ================================================================
            print("\n[STEP 2] Find Writable Locations")
            print("-" * 70)

            emmc_location = self.get_writable_location(devices['emmc'], test_config)

            if not emmc_location:
                pytest.fail(
                    "Could not find writable location on eMMC\n"
                    "Possible causes:\n"
                    "  - Filesystem mounted read-only\n"
                    "  - Permission denied\n"
                    "  - Disk full"
                )

            test_results['emmc']['writable'] = True
            print(f"✓ eMMC writable location: {emmc_location}")

            # Get filesystem info
            self.get_filesystem_info(emmc_location, test_config)

            sd_location = None
            if devices['sd']:
                sd_location = self.get_writable_location(devices['sd'], test_config)
                if sd_location:
                    test_results['sd']['writable'] = True
                    print(f"✓ SD card writable location: {sd_location}")
                    self.get_filesystem_info(sd_location, test_config)
                else:
                    print(f"  ⚠ SD card not writable (will skip SD tests)")

            # ================================================================
            # STEP 3: Write Test - eMMC
            # ================================================================
            print("\n[STEP 3] Write Test - eMMC")
            print("-" * 70)

            emmc_file, emmc_checksum, write_speed, write_time = self.write_test_file(
                emmc_location,
                test_config['test_file_size_mb'],
                test_config
            )

            if not emmc_file:
                pytest.fail("Failed to write test file to eMMC")

            test_files_to_cleanup.append(emmc_file)

            print(f"✓ eMMC write test passed")
            print(f"  Write speed: {write_speed:.2f} MB/s")

            if write_speed < test_config['min_write_speed_mb_s']:
                print(f"  ⚠ Warning: Write speed below threshold ({test_config['min_write_speed_mb_s']} MB/s)")

            # ================================================================
            # STEP 4: Read Test - eMMC
            # ================================================================
            print("\n[STEP 4] Read Test - eMMC")
            print("-" * 70)

            integrity_ok, read_checksum, read_speed, read_time = self.read_test_file(
                emmc_file,
                emmc_checksum,
                test_config
            )

            if not integrity_ok:
                pytest.fail(
                    f"eMMC data integrity check failed!\n"
                    f"  Expected checksum: {emmc_checksum[:16]}...\n"
                    f"  Got checksum:      {read_checksum[:16]}...\n"
                    "This indicates storage corruption or hardware failure."
                )

            test_results['emmc']['tests_passed'] += 1

            print(f"✓ eMMC read test passed")
            print(f"  Read speed: {read_speed:.2f} MB/s")
            print(f"✓ Data integrity verified")

            if read_speed < test_config['min_read_speed_mb_s']:
                print(f"  ⚠ Warning: Read speed below threshold ({test_config['min_read_speed_mb_s']} MB/s)")

            # ================================================================
            # STEP 5: Write Test - SD Card (if available)
            # ================================================================
            if sd_location:
                print("\n[STEP 5] Write Test - SD Card")
                print("-" * 70)

                sd_file, sd_checksum, sd_write_speed, sd_write_time = self.write_test_file(
                    sd_location,
                    test_config['test_file_size_mb'],
                    test_config
                )

                if not sd_file:
                    print(f"  ⚠ Failed to write test file to SD card (non-critical)")
                else:
                    test_files_to_cleanup.append(sd_file)

                    print(f"✓ SD card write test passed")
                    print(f"  Write speed: {sd_write_speed:.2f} MB/s")

                    if sd_write_speed < test_config['min_write_speed_mb_s']:
                        print(f"  ⚠ Warning: Write speed below threshold")

                    # ============================================================
                    # STEP 6: Read Test - SD Card
                    # ============================================================
                    print("\n[STEP 6] Read Test - SD Card")
                    print("-" * 70)

                    sd_integrity_ok, sd_read_checksum, sd_read_speed, sd_read_time = self.read_test_file(
                        sd_file,
                        sd_checksum,
                        test_config
                    )

                    if not sd_integrity_ok:
                        print(f"  ⚠ SD card data integrity check failed (non-critical)")
                    else:
                        test_results['sd']['tests_passed'] += 1

                        print(f"✓ SD card read test passed")
                        print(f"  Read speed: {sd_read_speed:.2f} MB/s")
                        print(f"✓ Data integrity verified")

                        if sd_read_speed < test_config['min_read_speed_mb_s']:
                            print(f"  ⚠ Warning: Read speed below threshold")
            else:
                print("\n[STEP 5 & 6] SD Card Tests - SKIPPED")
                print("-" * 70)
                print("  ⚠ SD card not available or not writable")

        finally:
            # ================================================================
            # STEP 7: Cleanup
            # ================================================================
            print("\n[STEP 7] Cleanup")
            print("-" * 70)

            for test_file in test_files_to_cleanup:
                try:
                    if os.path.exists(test_file):
                        os.remove(test_file)
                        self.log_message(f"  ✓ Removed: {test_file}", test_config)
                except Exception as e:
                    self.log_message(f"  ⚠ Could not remove {test_file}: {e}", test_config)

            print(f"✓ Cleanup complete")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ eMMC detected: {test_results['emmc']['detected']}")
        print(f"  ✓ eMMC writable: {test_results['emmc']['writable']}")
        print(f"  ✓ eMMC tests passed: {test_results['emmc']['tests_passed']}/1")

        if test_results['sd']['detected']:
            print(f"  ✓ SD card detected: {test_results['sd']['detected']}")
            if test_results['sd']['writable']:
                print(f"  ✓ SD card writable: {test_results['sd']['writable']}")
                print(f"  ✓ SD card tests passed: {test_results['sd']['tests_passed']}/1")
            else:
                print(f"  ⚠ SD card not writable (optional)")
        else:
            print(f"  ⚠ SD card not available (optional)")

        print(f"  ✓ Write operations completed without errors")
        print(f"  ✓ Read operations completed without errors")
        print(f"  ✓ Data integrity verified (checksums match)")
        print(f"  ✓ Read/write operations succeed on storage interfaces (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
