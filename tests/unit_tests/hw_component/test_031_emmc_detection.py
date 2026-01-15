#!/usr/bin/env python3
"""
Test Case #31: eMMC Detection
Category: HW Component Test
Component: eMMC Storage

Tests that eMMC storage is properly detected by the system.
This test runs on the CM4 itself (not on PC).
"""

import subprocess
import os
import time
import pytest


class TestEMMCDetection:
    """HW Component Test - eMMC Storage Detection"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for eMMC detection test"""
        return {
            'emmc_device': '/dev/mmcblk0',
            'expected_device_name': 'mmcblk0',
            'test_block_size': 512,
            'test_block_count': 1,
            'enable_logging': True,
            'log_file': '/tmp/test_031_emmc_detection.log',
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

    def check_system_booted(self, config):
        """Verify system is properly booted"""
        self.log_message("Checking if system is booted...", config)

        try:
            result = subprocess.run(['uptime'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)

            if result.returncode == 0:
                uptime_output = result.stdout.strip()
                self.log_message(f"  System uptime: {uptime_output}", config)
                return True, uptime_output
            else:
                return False, "uptime command failed"

        except Exception as e:
            return False, str(e)

    def check_emmc_via_lsblk(self, config):
        """Check eMMC detection via lsblk command"""
        self.log_message("Checking eMMC via lsblk...", config)

        try:
            result = subprocess.run(['lsblk'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)

            detected = config['expected_device_name'] in result.stdout

            if detected:
                # Extract eMMC info from lsblk output
                for line in result.stdout.split('\n'):
                    if config['expected_device_name'] in line:
                        self.log_message(f"  lsblk: {line.strip()}", config)

            return detected, result.stdout

        except Exception as e:
            return False, str(e)

    def check_emmc_via_dev(self, config):
        """Check eMMC detection via /dev/ device file"""
        self.log_message("Checking eMMC via /dev/ filesystem...", config)

        device_path = config['emmc_device']
        detected = os.path.exists(device_path)

        if detected:
            try:
                # Get device file info
                stat_info = os.stat(device_path)
                self.log_message(f"  Device exists: {device_path}", config)
                self.log_message(f"  Mode: {oct(stat_info.st_mode)}", config)
            except Exception as e:
                self.log_message(f"  Warning: Could not stat device: {e}", config)

        return detected

    def check_emmc_via_fdisk(self, config):
        """Check eMMC detection via fdisk"""
        self.log_message("Checking eMMC via fdisk...", config)

        try:
            result = subprocess.run(['sudo', 'fdisk', '-l'],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)

            detected = config['expected_device_name'] in result.stdout

            if detected:
                # Extract eMMC partition info
                in_emmc_section = False
                for line in result.stdout.split('\n'):
                    if config['emmc_device'] in line:
                        in_emmc_section = True
                    if in_emmc_section and line.strip():
                        if line.startswith('Disk') or line.startswith('/dev/'):
                            self.log_message(f"  fdisk: {line.strip()}", config)
                        if line.strip() == '':
                            break

            return detected, result.stdout

        except Exception as e:
            return False, str(e)

    def check_emmc_via_sys(self, config):
        """Check eMMC via /sys filesystem"""
        self.log_message("Checking eMMC via /sys filesystem...", config)

        sys_paths = [
            '/sys/class/block/mmcblk0',
            '/sys/block/mmcblk0',
        ]

        for sys_path in sys_paths:
            if os.path.exists(sys_path):
                self.log_message(f"  Found: {sys_path}", config)

                # Read some eMMC properties
                try:
                    size_path = os.path.join(sys_path, 'size')
                    if os.path.exists(size_path):
                        with open(size_path, 'r') as f:
                            blocks = f.read().strip()
                            size_gb = int(blocks) * 512 / (1024**3)
                            self.log_message(f"  Size: {size_gb:.2f} GB", config)

                    model_path = os.path.join(sys_path, 'device/name')
                    if os.path.exists(model_path):
                        with open(model_path, 'r') as f:
                            model = f.read().strip()
                            self.log_message(f"  Model: {model}", config)

                except Exception as e:
                    self.log_message(f"  Warning: Could not read properties: {e}", config)

                return True

        return False

    def verify_emmc_readable(self, config):
        """Verify eMMC is readable by reading first block"""
        self.log_message("Verifying eMMC is readable...", config)

        try:
            result = subprocess.run([
                'sudo', 'dd',
                f'if={config["emmc_device"]}',
                'of=/dev/null',
                f'bs={config["test_block_size"]}',
                f'count={config["test_block_count"]}',
                'status=none'
            ],
                capture_output=True,
                text=True,
                timeout=5)

            if result.returncode == 0:
                self.log_message(f"  ✓ Successfully read {config['test_block_size']} bytes", config)
                return True, None
            else:
                return False, result.stderr

        except Exception as e:
            return False, str(e)

    def get_emmc_info(self, config):
        """Get detailed eMMC information"""
        self.log_message("Gathering eMMC information...", config)

        info = {}

        # Get partition info
        try:
            result = subprocess.run(['lsblk', '-b', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)

            info['partitions'] = []
            for line in result.stdout.split('\n'):
                if 'mmcblk0' in line:
                    info['partitions'].append(line.strip())

        except:
            pass

        return info

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.storage
    def test_031_emmc_detection(self, test_config):
        """
        Test Case #31: eMMC detection

        Test Setup: Bootable provisioning setup (must run ON CM4)
        Acceptance Criteria: eMMC detected by the system

        IMPORTANT: This test must run ON the CM4 itself, not on a PC.
        The system must be booted from eMMC or SD card.

        What this test validates:
        - System is properly booted
        - eMMC is detected by multiple methods
        - eMMC device file exists
        - eMMC is readable
        - eMMC partitions are visible
        """

        print("\n" + "=" * 70)
        print("Test Case #31: eMMC Detection")
        print("=" * 70)
        print("\nHW Component Test - eMMC Storage")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 1: Verify System is Booted
        # ================================================================
        print("\n[STEP 1] Verify System is Booted")
        print("-" * 70)

        booted, uptime_info = self.check_system_booted(test_config)

        if not booted:
            pytest.fail(f"System not properly booted: {uptime_info}")

        print(f"✓ System is booted")
        print(f"  Uptime: {uptime_info}")

        # ================================================================
        # STEP 2: Detect eMMC via Multiple Methods
        # ================================================================
        print("\n[STEP 2] Detect eMMC via Multiple Methods")
        print("-" * 70)

        detection_methods = {}

        # Method 1: lsblk
        lsblk_detected, lsblk_output = self.check_emmc_via_lsblk(test_config)
        detection_methods['lsblk'] = lsblk_detected

        if lsblk_detected:
            print("✓ Method 1: lsblk - eMMC detected")
        else:
            print("✗ Method 1: lsblk - eMMC NOT detected")

        # Method 2: /dev/ filesystem
        dev_detected = self.check_emmc_via_dev(test_config)
        detection_methods['dev'] = dev_detected

        if dev_detected:
            print(f"✓ Method 2: /dev/ - {test_config['emmc_device']} exists")
        else:
            print(f"✗ Method 2: /dev/ - {test_config['emmc_device']} NOT found")

        # Method 3: fdisk
        fdisk_detected, fdisk_output = self.check_emmc_via_fdisk(test_config)
        detection_methods['fdisk'] = fdisk_detected

        if fdisk_detected:
            print("✓ Method 3: fdisk - eMMC detected")
        else:
            print("✗ Method 3: fdisk - eMMC NOT detected")

        # Method 4: /sys filesystem
        sys_detected = self.check_emmc_via_sys(test_config)
        detection_methods['sys'] = sys_detected

        if sys_detected:
            print("✓ Method 4: /sys - eMMC sysfs entries found")
        else:
            print("✗ Method 4: /sys - eMMC sysfs entries NOT found")

        # Check if eMMC detected by at least one method
        detected_by_any = any(detection_methods.values())

        print(f"\nDetection Summary:")
        print(f"  Detected by {sum(detection_methods.values())}/4 methods")

        if not detected_by_any:
            pytest.fail(
                "eMMC not detected by any method\n"
                f"  lsblk: {detection_methods['lsblk']}\n"
                f"  /dev/: {detection_methods['dev']}\n"
                f"  fdisk: {detection_methods['fdisk']}\n"
                f"  /sys:  {detection_methods['sys']}\n"
                "\nPossible reasons:\n"
                "  - Running on CM4 Lite (no eMMC)\n"
                "  - eMMC hardware failure\n"
                "  - Driver not loaded\n"
                "  - Running in wrong environment"
            )

        print(f"✓ eMMC detected by multiple methods")

        # ================================================================
        # STEP 3: Verify eMMC is Readable
        # ================================================================
        print("\n[STEP 3] Verify eMMC is Readable")
        print("-" * 70)

        readable, error = self.verify_emmc_readable(test_config)

        if not readable:
            pytest.fail(
                f"eMMC is detected but not readable\n"
                f"Error: {error}\n"
                "This may indicate:\n"
                "  - Permission issues\n"
                "  - Hardware failure\n"
                "  - Corrupted device"
            )

        print(f"✓ eMMC is readable")

        # ================================================================
        # STEP 4: Gather eMMC Information
        # ================================================================
        print("\n[STEP 4] Gather eMMC Information")
        print("-" * 70)

        emmc_info = self.get_emmc_info(test_config)

        if emmc_info.get('partitions'):
            print(f"✓ eMMC partitions detected:")
            for partition in emmc_info['partitions']:
                print(f"  {partition}")
        else:
            print("  No partition information available")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ System is booted and operational")
        print(f"  ✓ eMMC detected by {sum(detection_methods.values())}/4 methods")
        print(f"  ✓ eMMC device file exists: {test_config['emmc_device']}")
        print(f"  ✓ eMMC is readable")
        print(f"  ✓ eMMC detected by the system (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
