#!/usr/bin/env python3
"""
Test Case #30: CM4 Enumeration on PC
Category: HW Component Test
Component: CM4

Tests that CM4 can be successfully enumerated when connected to PC via USB.
"""

import subprocess
import time
import pytest
import os
import sys

# Add common path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))

from test_results_generator import TestResultsGenerator, StepStatus


class TestCM4Enumeration:
    """HW Component Test - CM4 Enumeration"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for CM4 enumeration test"""
        return {
            'usb_detection_timeout': 30,
            'rpiboot_timeout': 60,
            'storage_wait_time': 3,
            'expected_vendor_ids': ['0a5c:2711', '0a5c:2764', 'Broadcom'],
            'enable_logging': True,
            'log_file': '/tmp/test_030_cm4_enumeration.log',
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

    def check_rpiboot_installed(self):
        """Check if rpiboot is installed"""
        result = subprocess.run(['which', 'rpiboot'],
                              capture_output=True)
        return result.returncode == 0

    def detect_cm4_usb(self, config):
        """Detect CM4 USB device"""
        self.log_message("Waiting for CM4 USB device...", config)

        timeout = config['usb_detection_timeout']
        start = time.time()

        usb_detected = False
        detected_device = None

        while (time.time() - start) < timeout:
            result = subprocess.run(['lsusb'],
                                  capture_output=True,
                                  text=True)

            # Check for Broadcom vendor or specific device ID
            for vendor_id in config['expected_vendor_ids']:
                if vendor_id in result.stdout:
                    usb_detected = True
                    detected_device = vendor_id
                    break

            if usb_detected:
                break

            elapsed = int(time.time() - start)
            if elapsed % 5 == 0:
                self.log_message(f"  Still waiting... ({elapsed}s elapsed)", config)

            time.sleep(1)

        return usb_detected, detected_device

    def run_rpiboot(self, config):
        """Run rpiboot to enumerate CM4"""
        self.log_message("Running rpiboot...", config)

        try:
            result = subprocess.run(['sudo', 'rpiboot'],
                                  capture_output=True,
                                  text=True,
                                  timeout=config['rpiboot_timeout'])

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", "rpiboot timed out"

    def check_storage_enumeration(self, config):
        """Check if CM4 storage is enumerated"""
        self.log_message("Checking for enumerated storage...", config)

        # Wait for storage to appear
        time.sleep(config['storage_wait_time'])

        result = subprocess.run(['lsblk'],
                              capture_output=True,
                              text=True)

        # Check for various possible device names
        storage_found = False
        device_name = None

        # Check for mmcblk (eMMC)
        if 'mmcblk' in result.stdout:
            storage_found = True
            device_name = 'mmcblk (eMMC)'

        # Check for sd* (SD card reader)
        elif 'sd' in result.stdout:
            # More specific check to avoid false positives
            for line in result.stdout.split('\n'):
                if line.startswith('sd') and 'disk' in line.lower():
                    storage_found = True
                    device_name = 'sd* (USB mass storage)'
                    break

        return storage_found, device_name, result.stdout

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    def test_030_cm4_enumeration_on_pc(self, test_config):
        """
        Test Case #30: CM4 enumeration on PC

        Test Setup: PC, CM4, cables
        Acceptance Criteria: CM4 enumerates successfully on PC as expected

        IMPORTANT: Manual steps required before running this test:
        1. Connect CM4 to PC via USB (use USB slave/device port on CM4)
        2. Ensure CM4 is in USB boot mode (disable eMMC boot)
        3. Power on CM4

        What this test validates:
        - CM4 is detected as USB device
        - rpiboot can enumerate the CM4
        - CM4 storage appears as block device
        """

        # Initialize Test Results Generator
        results = TestResultsGenerator(
            test_id="030",
            test_name="CM4 Enumeration on PC",
            category="HW Component Test"
        )

        # Add acceptance criteria
        results.add_acceptance_criterion(
            "CM4 detected as USB device",
            "USB device 0a5c:2711 or 0a5c:2764 detected"
        )
        results.add_acceptance_criterion(
            "rpiboot enumeration successful",
            "rpiboot completes without error"
        )
        results.add_acceptance_criterion(
            "CM4 storage enumerated",
            "Block device (mmcblk or sd*) appears"
        )

        # Start test
        results.start_test()

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Track overall test status
        test_passed = True
        failure_reason = ""

        # ================================================================
        # STEP 1: Verify Prerequisites
        # ================================================================
        step1 = results.add_step(1, "Verify Prerequisites", "Check if rpiboot is installed")
        step1.start()

        print("\n[STEP 1] Verify Prerequisites")
        print("-" * 70)

        # Check if rpiboot is installed
        if not self.check_rpiboot_installed():
            step1.failed("rpiboot not installed")
            results.finish_test(False, "rpiboot not installed. Install with: sudo apt install rpiboot")
            pytest.skip("rpiboot not installed. Install with: sudo apt install rpiboot")

        print("rpiboot is installed")
        self.log_message("rpiboot is installed", test_config)
        step1.passed("rpiboot is installed")

        # ================================================================
        # STEP 2: Manual Setup Instructions
        # ================================================================
        step2 = results.add_step(2, "Manual Setup", "User confirms CM4 is connected and powered")
        step2.start()

        print("\n[STEP 2] Manual Setup Required")
        print("-" * 70)
        print("\nMANUAL ACTIONS REQUIRED:")
        print("   1. Connect CM4 to PC via USB (slave/device port)")
        print("   2. Ensure CM4 is in USB boot mode")
        print("   3. Power on CM4")
        print("\n   The test will wait up to 30 seconds for USB detection...")
        print("")

        response = input("   Have you completed the setup? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            step2.skipped("User did not confirm setup")
            results.finish_test(False, "Manual setup not completed by user")
            pytest.skip("Manual setup not completed")

        print("\nManual setup confirmed")
        step2.passed("User confirmed CM4 is connected")

        # ================================================================
        # STEP 3: Detect CM4 USB Device
        # ================================================================
        step3 = results.add_step(3, "Detect CM4 USB Device", "Wait for CM4 USB device detection")
        step3.start()

        print("\n[STEP 3] Detect CM4 USB Device")
        print("-" * 70)

        usb_detected, detected_device = self.detect_cm4_usb(test_config)

        if not usb_detected:
            error_msg = f"CM4 USB device not detected after {test_config['usb_detection_timeout']}s"
            step3.failed(error_msg)
            results.update_acceptance_criterion(
                "CM4 detected as USB device",
                "Not detected",
                False
            )
            test_passed = False
            failure_reason = error_msg

            results.finish_test(False, failure_reason)
            pytest.fail(
                f"{error_msg}\n"
                "Ensure CM4 is:\n"
                "  - Connected via USB\n"
                "  - In USB boot mode\n"
                "  - Powered on"
            )

        print(f"CM4 USB device detected: {detected_device}")
        self.log_message(f"USB device detected: {detected_device}", test_config)
        step3.passed(f"USB device detected: {detected_device}")
        results.update_acceptance_criterion(
            "CM4 detected as USB device",
            f"Detected: {detected_device}",
            True
        )

        # ================================================================
        # STEP 4: Run rpiboot
        # ================================================================
        step4 = results.add_step(4, "Run rpiboot", "Execute rpiboot to enumerate CM4")
        step4.start()

        print("\n[STEP 4] Run rpiboot")
        print("-" * 70)

        success, stdout, stderr = self.run_rpiboot(test_config)

        if not success:
            error_msg = f"rpiboot failed: {stderr}"
            step4.failed(error_msg)
            results.update_acceptance_criterion(
                "rpiboot enumeration successful",
                f"Failed: {stderr}",
                False
            )
            test_passed = False
            failure_reason = error_msg

            results.finish_test(False, failure_reason)
            pytest.fail(
                f"rpiboot failed:\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

        print("rpiboot completed successfully")
        self.log_message("rpiboot completed", test_config)
        step4.passed("rpiboot completed successfully")
        results.update_acceptance_criterion(
            "rpiboot enumeration successful",
            "Completed without error",
            True
        )

        if stdout:
            print(f"\nrpiboot output:\n{stdout}")

        # ================================================================
        # STEP 5: Verify Storage Enumeration
        # ================================================================
        step5 = results.add_step(5, "Verify Storage Enumeration", "Check if CM4 storage appears as block device")
        step5.start()

        print("\n[STEP 5] Verify Storage Enumeration")
        print("-" * 70)

        storage_found, device_name, lsblk_output = self.check_storage_enumeration(test_config)

        if not storage_found:
            error_msg = "CM4 storage not enumerated"
            step5.failed(error_msg, f"Expected mmcblk* or sd* device\nDetected:\n{lsblk_output}")
            results.update_acceptance_criterion(
                "CM4 storage enumerated",
                "Not found",
                False
            )
            test_passed = False
            failure_reason = error_msg

            print("\nBlock devices detected:")
            print(lsblk_output)

            results.finish_test(False, failure_reason)
            pytest.fail(
                "CM4 storage not enumerated\n"
                "Expected to find mmcblk* or sd* device"
            )

        print(f"CM4 storage enumerated: {device_name}")
        self.log_message(f"Storage enumerated: {device_name}", test_config)
        step5.passed(f"Storage enumerated: {device_name}")
        results.update_acceptance_criterion(
            "CM4 storage enumerated",
            f"Found: {device_name}",
            True
        )

        print("\nDetected block devices:")
        print(lsblk_output)

        # ================================================================
        # Finish Test and Generate Report
        # ================================================================
        results.finish_test(True, "CM4 enumerated successfully on PC")

        # Also print legacy format for compatibility
        print("\n" + "=" * 70)
        print("TEST RESULT: PASS")
        print("=" * 70)
        print("\nAcceptance Criteria Verification:")
        print("  [PASS] CM4 detected as USB device")
        print("  [PASS] rpiboot enumeration successful")
        print("  [PASS] CM4 storage enumerated as block device")
        print("  [PASS] CM4 enumerated successfully on PC as expected")

        if test_config.get('enable_logging'):
            print(f"\nTest log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
