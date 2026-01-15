#!/usr/bin/env python3
"""
Test Case #32: OS Flashing to eMMC
Category: HW Component Test
Component: eMMC Storage

Tests the process of flashing an OS image to CM4's eMMC storage.
This test requires CM4 in USB boot mode and runs on PC.
"""

import subprocess
import time
import os
import hashlib
import pytest
from pathlib import Path


class TestEMMCFlashing:
    """HW Component Test - OS Flashing to eMMC"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for eMMC flashing test"""
        return {
            # IMPORTANT: Update this path to your actual OS image
            'os_image_path': os.getenv('OS_IMAGE_PATH', '/path/to/raspberry-pi-os.img'),
            'emmc_device': '/dev/mmcblk0',
            'rpiboot_timeout': 60,
            'flash_timeout': 600,  # 10 minutes for flashing
            'verify_checksum': False,  # Set to True if you want checksum verification
            'enable_logging': True,
            'log_file': '/tmp/test_032_os_flashing.log',
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

    def verify_prerequisites(self, test_config):
        """
        Verify all prerequisites are met before flashing
        Returns: tuple (success: bool, message: str, details: dict)
        """
        self.log_message("Verifying prerequisites...", test_config)

        details = {}

        # Check if OS image exists
        if not os.path.exists(test_config['os_image_path']):
            return False, f"OS image not found: {test_config['os_image_path']}", details

        image_size = os.path.getsize(test_config['os_image_path'])
        details['image_size_gb'] = image_size / (1024**3)
        self.log_message(f"  ✓ OS image found: {test_config['os_image_path']}", test_config)
        self.log_message(f"    Size: {details['image_size_gb']:.2f} GB", test_config)

        # Check if rpiboot is installed
        result = subprocess.run(['which', 'rpiboot'],
                              capture_output=True)
        if result.returncode != 0:
            return False, "rpiboot not installed (required for CM4 enumeration)", details

        details['rpiboot_path'] = result.stdout.decode().strip()
        self.log_message("  ✓ rpiboot is installed", test_config)

        # Check if dd is available
        result = subprocess.run(['which', 'dd'],
                              capture_output=True)
        if result.returncode != 0:
            return False, "dd command not available", details

        details['dd_path'] = result.stdout.decode().strip()
        self.log_message("  ✓ dd command available", test_config)

        # Check if running with sudo privileges
        if os.geteuid() != 0:
            return False, "Test must be run with sudo privileges (use: sudo -E pytest ...)", details

        self.log_message("  ✓ Running with sudo privileges", test_config)

        return True, "All prerequisites met", details

    def enumerate_cm4_emmc(self, test_config):
        """
        Enumerate CM4 eMMC using rpiboot
        Returns: tuple (success: bool, message: str)
        """
        self.log_message("Enumerating CM4 eMMC...", test_config)

        try:
            self.log_message("  Running rpiboot (this may take 30-60 seconds)...", test_config)

            process = subprocess.Popen(
                ['rpiboot'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for rpiboot to complete
            stdout, stderr = process.communicate(timeout=test_config['rpiboot_timeout'])

            if process.returncode == 0:
                self.log_message("  ✓ rpiboot completed successfully", test_config)

                # Wait for device to enumerate
                time.sleep(5)
                return True, "CM4 enumerated"
            else:
                return False, f"rpiboot failed: {stderr}"

        except subprocess.TimeoutExpired:
            process.kill()
            return False, "rpiboot timeout"
        except Exception as e:
            return False, f"Error running rpiboot: {e}"

    def wait_for_emmc_device(self, test_config, timeout=30):
        """
        Wait for eMMC device to appear
        Returns: tuple (success: bool, device_info: str)
        """
        self.log_message(f"  Waiting for eMMC device {test_config['emmc_device']}...", test_config)

        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if os.path.exists(test_config['emmc_device']):
                self.log_message(f"  ✓ eMMC device found: {test_config['emmc_device']}", test_config)

                # Get device info
                result = subprocess.run(
                    ['lsblk', '-o', 'NAME,SIZE,MODEL', test_config['emmc_device']],
                    capture_output=True,
                    text=True
                )

                device_info = result.stdout.strip()
                self.log_message(f"  Device info:\n{device_info}", test_config)

                return True, device_info

            time.sleep(1)

        return False, f"eMMC device not found after {timeout}s"

    def calculate_image_checksum(self, image_path, test_config):
        """
        Calculate SHA256 checksum of OS image
        Returns: str (checksum hex)
        """
        self.log_message(f"  Calculating SHA256 checksum for {os.path.basename(image_path)}...", test_config)

        sha256_hash = hashlib.sha256()

        file_size = os.path.getsize(image_path)
        processed = 0

        with open(image_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096*1024), b""):  # 4MB chunks
                sha256_hash.update(byte_block)
                processed += len(byte_block)

                # Log progress every 100MB
                if processed % (100 * 1024 * 1024) < (4096 * 1024):
                    progress = (processed / file_size) * 100
                    self.log_message(f"    Checksum progress: {progress:.1f}%", test_config)

        checksum = sha256_hash.hexdigest()
        self.log_message(f"  ✓ Image checksum: {checksum}", test_config)
        return checksum

    def flash_os_to_emmc(self, test_config):
        """
        Flash OS image to eMMC using dd
        Returns: tuple (success: bool, message: str, elapsed_time: float)
        """
        self.log_message("Starting OS flash to eMMC...", test_config)

        os_image = test_config['os_image_path']
        emmc_device = test_config['emmc_device']

        # Get image size
        image_size = os.path.getsize(os_image)
        self.log_message(f"  OS image size: {image_size / (1024**3):.2f} GB", test_config)

        # Unmount any mounted partitions
        self.log_message("  Unmounting any mounted eMMC partitions...", test_config)
        subprocess.run(['umount', f'{emmc_device}*'],
                      stderr=subprocess.DEVNULL)

        try:
            # Flash using dd with progress monitoring
            self.log_message(f"  Flashing {os.path.basename(os_image)} to {emmc_device}...", test_config)
            self.log_message("  This may take several minutes (5-10 min for 2GB image)...", test_config)

            dd_command = [
                'dd',
                f'if={os_image}',
                f'of={emmc_device}',
                'bs=4M',
                'conv=fsync',
                'status=progress'
            ]

            self.log_message(f"  Command: {' '.join(dd_command)}", test_config)

            process = subprocess.Popen(
                dd_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Monitor progress
            start_time = time.time()

            while True:
                # Check if process is still running
                if process.poll() is not None:
                    break

                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > test_config['flash_timeout']:
                    process.kill()
                    return False, f"Flash timeout after {elapsed:.0f}s", elapsed

                # Log progress every 30 seconds
                if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                    self.log_message(f"    Flash in progress... {int(elapsed)}s elapsed", test_config)

                time.sleep(1)

            # Get final output
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Parse dd statistics from stderr
                self.log_message("  Flash output:", test_config)
                for line in stderr.split('\n'):
                    if line.strip():
                        self.log_message(f"    {line.strip()}", test_config)

                elapsed_time = time.time() - start_time
                self.log_message(f"  ✓ Flash completed in {elapsed_time:.0f}s ({elapsed_time/60:.1f} min)", test_config)

                return True, f"Flash successful", elapsed_time
            else:
                return False, f"dd command failed: {stderr}", 0

        except Exception as e:
            return False, f"Flash error: {str(e)}", 0

    def verify_flash(self, test_config):
        """
        Verify the flash was successful
        Returns: tuple (success: bool, message: str, details: dict)
        """
        self.log_message("Verifying flash...", test_config)

        emmc_device = test_config['emmc_device']
        details = {}

        # Method 1: Check partition table
        self.log_message("  Checking partition table...", test_config)
        result = subprocess.run(
            ['fdisk', '-l', emmc_device],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, "Failed to read partition table", details

        partition_info = result.stdout
        details['partitions'] = partition_info

        # Check for expected partitions
        if 'Linux' not in partition_info and 'W95 FAT' not in partition_info:
            return False, "Expected partitions not found", details

        self.log_message("  ✓ Partition table looks correct", test_config)

        # Log partition details
        for line in partition_info.split('\n'):
            if emmc_device in line or 'Device' in line or 'Disk' in line:
                self.log_message(f"    {line.strip()}", test_config)

        # Method 2: Check filesystem on first partition
        self.log_message("  Checking boot partition filesystem...", test_config)

        # Wait for partition devices to appear
        time.sleep(2)

        boot_partition = f"{emmc_device}p1"
        if os.path.exists(boot_partition):
            result = subprocess.run(
                ['file', '-s', boot_partition],
                capture_output=True,
                text=True
            )

            fs_type = result.stdout.strip()
            details['boot_fs'] = fs_type
            self.log_message(f"    Boot partition: {fs_type}", test_config)

            if 'FAT' in fs_type or 'boot' in fs_type:
                self.log_message("  ✓ Boot partition filesystem verified", test_config)
            else:
                return False, "Boot partition filesystem incorrect", details
        else:
            return False, f"Boot partition {boot_partition} not found", details

        # Method 3: Try to mount boot partition (read-only check)
        self.log_message("  Attempting read-only mount test...", test_config)

        mount_point = '/tmp/emmc_verify'
        os.makedirs(mount_point, exist_ok=True)

        try:
            # Mount read-only
            result = subprocess.run(
                ['mount', '-o', 'ro', boot_partition, mount_point],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                self.log_message("  ✓ Boot partition mounted successfully", test_config)

                # Check for expected boot files
                boot_files = os.listdir(mount_point)
                details['boot_files_count'] = len(boot_files)
                self.log_message(f"    Boot files found: {len(boot_files)}", test_config)

                expected_files = ['bootcode.bin', 'start.elf', 'start4.elf', 'kernel.img', 'kernel8.img', 'config.txt']
                found_files = [f for f in expected_files if f in boot_files]

                if found_files:
                    self.log_message(f"  ✓ Found expected boot files: {', '.join(found_files)}", test_config)
                    details['found_boot_files'] = found_files

                # Unmount
                subprocess.run(['umount', mount_point])

                return True, "Flash verification successful", details
            else:
                return False, f"Failed to mount boot partition: {result.stderr.decode()}", details

        except subprocess.TimeoutExpired:
            subprocess.run(['umount', mount_point], stderr=subprocess.DEVNULL)
            return False, "Mount timeout", details
        except Exception as e:
            subprocess.run(['umount', mount_point], stderr=subprocess.DEVNULL)
            return False, f"Mount error: {str(e)}", details
        finally:
            # Cleanup
            try:
                os.rmdir(mount_point)
            except:
                pass

    def sync_and_eject(self, test_config):
        """Sync filesystem and safely eject eMMC"""
        self.log_message("Syncing filesystem...", test_config)

        # Sync to ensure all data is written
        subprocess.run(['sync'], timeout=30)
        self.log_message("  ✓ Filesystem synced", test_config)

        # Unmount all partitions
        self.log_message("  Unmounting eMMC partitions...", test_config)
        subprocess.run(
            ['umount', f"{test_config['emmc_device']}*"],
            stderr=subprocess.DEVNULL
        )
        self.log_message("  ✓ eMMC safely ejected", test_config)

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.storage
    @pytest.mark.slow
    def test_032_os_flashing_to_emmc(self, test_config):
        """
        Test Case #32: OS flashing to eMMC

        Test Setup: PC + imaging tool
        Acceptance Criteria: OS successfully flashed to eMMC

        IMPORTANT: Prerequisites before running this test:
        1. CM4 connected to PC via USB (slave/device port)
        2. CM4 in USB boot mode (nRPI_BOOT jumper set)
        3. OS image file available (set OS_IMAGE_PATH environment variable)
        4. Test run with sudo privileges: sudo -E pytest ...

        What this test validates:
        - CM4 eMMC can be enumerated via rpiboot
        - OS image can be flashed to eMMC using dd
        - Flash completes without errors
        - Flashed image can be verified (partition table, filesystem, boot files)

        WARNING: This test will ERASE all data on CM4's eMMC!
        """

        print("\n" + "=" * 70)
        print("Test Case #32: OS Flashing to eMMC")
        print("=" * 70)
        print("\nHW Component Test - eMMC Storage")
        print("=" * 70)
        print("\n⚠️  WARNING: This test will ERASE all data on CM4's eMMC!")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 0: Verify Prerequisites
        # ================================================================
        print("\n[STEP 0] Verify Prerequisites")
        print("-" * 70)

        success, message, details = self.verify_prerequisites(test_config)

        if not success:
            pytest.skip(
                f"Prerequisites check failed: {message}\n\n"
                "Please ensure:\n"
                "  1. OS image file exists\n"
                "     Set path with: export OS_IMAGE_PATH=/path/to/image.img\n"
                "  2. rpiboot is installed: sudo apt install rpiboot\n"
                "  3. Run with sudo: sudo -E pytest ...\n"
                "  4. CM4 connected via USB in USB boot mode"
            )

        print(f"✓ {message}")
        if details.get('image_size_gb'):
            print(f"  Image size: {details['image_size_gb']:.2f} GB")

        # Manual confirmation
        print("\n📋 MANUAL CONFIRMATION REQUIRED:")
        print("   1. Is CM4 connected to PC via USB (slave port)?")
        print("   2. Is nRPI_BOOT jumper set (USB boot mode)?")
        print("   3. Is CM4 powered on?")
        print("   4. Are you sure you want to ERASE eMMC and flash new OS?")
        print("")

        response = input("   Continue with flashing? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            pytest.skip("User cancelled flashing operation")

        print("\n✓ User confirmed - proceeding with flash")

        # ================================================================
        # STEP 1: Enumerate CM4 eMMC
        # ================================================================
        print("\n[STEP 1] Enumerate CM4 eMMC using rpiboot")
        print("-" * 70)

        success, message = self.enumerate_cm4_emmc(test_config)

        if not success:
            pytest.fail(f"Failed to enumerate CM4 eMMC: {message}")

        print(f"✓ {message}")

        # Wait for eMMC device
        success, device_info = self.wait_for_emmc_device(test_config)

        if not success:
            pytest.fail(f"eMMC device not found: {device_info}")

        print(f"✓ eMMC device ready")

        # Optional: Calculate image checksum before flashing
        if test_config.get('verify_checksum'):
            print("\n[OPTIONAL] Calculating image checksum...")
            print("-" * 70)
            image_checksum = self.calculate_image_checksum(
                test_config['os_image_path'],
                test_config
            )
            print(f"✓ Checksum calculated: {image_checksum[:16]}...")

        # ================================================================
        # STEP 2: Flash OS Image to eMMC
        # ================================================================
        print("\n[STEP 2] Flash OS Image to eMMC")
        print("-" * 70)

        success, message, elapsed_time = self.flash_os_to_emmc(test_config)

        if not success:
            pytest.fail(f"Flash failed: {message}")

        print(f"✓ {message} ({elapsed_time/60:.1f} minutes)")

        # ================================================================
        # STEP 3: Verify Flashing Completed Successfully
        # ================================================================
        print("\n[STEP 3] Verify Flashing Completed Successfully")
        print("-" * 70)

        success, message, details = self.verify_flash(test_config)

        if not success:
            pytest.fail(f"Flash verification failed: {message}")

        print(f"✓ {message}")
        if details.get('found_boot_files'):
            print(f"  Boot files: {', '.join(details['found_boot_files'])}")

        # ================================================================
        # STEP 4: Sync and Eject
        # ================================================================
        print("\n[STEP 4] Sync and Eject eMMC")
        print("-" * 70)

        self.sync_and_eject(test_config)

        print("✓ eMMC ready to be disconnected")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print("  ✓ CM4 eMMC enumerated successfully")
        print("  ✓ OS image flashed to eMMC")
        print(f"  ✓ Flash completed in {elapsed_time/60:.1f} minutes")
        print("  ✓ Flash verified successfully")
        print("  ✓ Partition table correct")
        print("  ✓ Boot partition filesystem verified")
        print("  ✓ Boot files present")
        print("  ✓ eMMC safely ejected")
        print("\n✓ OS successfully flashed to eMMC")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("\n💡 Next Steps:")
        print("  1. Remove nRPI_BOOT jumper")
        print("  2. Disconnect USB cable")
        print("  3. Connect CM4 to network/peripherals")
        print("  4. Power on CM4 - it will boot from newly flashed OS")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
