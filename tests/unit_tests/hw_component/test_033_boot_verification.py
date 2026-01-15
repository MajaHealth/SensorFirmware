#!/usr/bin/env python3
"""
Test Case #33: Boot Verification (kernel/messages)
Category: HW Component Test
Component: CM4 + Display

Tests that CM4 boots properly by analyzing kernel messages and system logs.
This test runs ON the CM4 after it has booted.
"""

import subprocess
import time
import re
import pytest
from datetime import datetime
from pathlib import Path


class TestBootVerification:
    """HW Component Test - Boot Verification (kernel/messages)"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for boot verification test"""
        return {
            'dmesg_log_path': '/tmp/boot_dmesg.log',
            'enable_logging': True,
            'log_file': '/tmp/test_033_boot_verification.log',

            # Error patterns to check for
            'error_patterns': [
                r'\berror\b',
                r'\bfail(ed)?\b',
                r'\bpanic\b',
                r'\boops\b',
                r'\bwarning\b',
                r'\btimeout\b',
                r'\bcritical\b',
            ],

            # Ignore patterns (false positives)
            'ignore_patterns': [
                r'rfkill',  # Known benign warnings
                r'bluetooth',
                r'bcm43xx',  # WiFi chip warnings (often benign)
            ],

            # Expected boot messages (success indicators)
            'expected_messages': [
                r'Booting Linux',
                r'Starting kernel',
                r'Freeing unused kernel',
                r'systemd.*running',
                r'Reached target.*Multi-User',
            ],
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

    def check_system_booted(self, test_config):
        """
        Verify system is fully booted
        Returns: tuple (success: bool, uptime: str, boot_time: str)
        """
        self.log_message("Checking if system is fully booted...", test_config)

        try:
            # Check boot time
            result = subprocess.run(
                ['uptime', '-s'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                boot_time = result.stdout.strip()
                self.log_message(f"  System booted at: {boot_time}", test_config)

                # Get current uptime
                result = subprocess.run(
                    ['uptime', '-p'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                uptime = result.stdout.strip()
                self.log_message(f"  Current uptime: {uptime}", test_config)

                return True, uptime, boot_time
            else:
                return False, "", ""

        except Exception as e:
            self.log_message(f"  Error checking boot status: {e}", test_config)
            return False, "", ""

    def check_display_detected(self, test_config):
        """
        Verify display is connected and detected
        Returns: tuple (detected: bool, details: list)
        """
        self.log_message("Checking if display is detected...", test_config)

        methods_tried = []
        display_found = False

        # Method 1: Check /sys/class/drm for display
        try:
            drm_path = Path('/sys/class/drm')
            if drm_path.exists():
                displays = list(drm_path.glob('card*-DSI-*')) + list(drm_path.glob('card*-HDMI-*'))
                if displays:
                    self.log_message(f"  ✓ Display found via DRM: {[d.name for d in displays]}", test_config)
                    display_found = True
                    methods_tried.append(f"DRM: Found {len(displays)} display(s)")
                else:
                    methods_tried.append("DRM: No displays found")
        except Exception as e:
            methods_tried.append(f"DRM: Error - {e}")

        # Method 2: Check framebuffer devices
        try:
            fb_devices = list(Path('/dev').glob('fb*'))
            if fb_devices:
                self.log_message(f"  ✓ Framebuffer devices: {[d.name for d in fb_devices]}", test_config)
                display_found = True
                methods_tried.append(f"Framebuffer: Found {len(fb_devices)} device(s)")
            else:
                methods_tried.append("Framebuffer: No devices")
        except Exception as e:
            methods_tried.append(f"Framebuffer: Error - {e}")

        # Method 3: Check dmesg for display messages
        try:
            result = subprocess.run(
                ['dmesg'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                display_keywords = ['DSI', 'HDMI', 'framebuffer', 'drm']
                found_keywords = [kw for kw in display_keywords if kw in result.stdout]

                if found_keywords:
                    self.log_message(f"  ✓ Found display keywords in dmesg: {found_keywords}", test_config)
                    display_found = True
                    methods_tried.append(f"dmesg: Found {', '.join(found_keywords)}")
                else:
                    methods_tried.append("dmesg: No display keywords")
        except Exception as e:
            methods_tried.append(f"dmesg: Error - {e}")

        if display_found:
            self.log_message("  ✓ Display is connected and detected", test_config)
        else:
            self.log_message("  ⚠ Display not detected (may not be connected)", test_config)

        return display_found, methods_tried

    def capture_dmesg(self, test_config):
        """
        Capture kernel messages (dmesg)
        Returns: tuple (success: bool, dmesg_output: str)
        """
        self.log_message("Capturing kernel messages (dmesg)...", test_config)

        try:
            result = subprocess.run(
                ['dmesg', '--time-format', 'iso'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                dmesg_output = result.stdout

                # Save to file
                with open(test_config['dmesg_log_path'], 'w') as f:
                    f.write(dmesg_output)

                line_count = len(dmesg_output.splitlines())
                self.log_message(f"  ✓ dmesg captured ({line_count} lines)", test_config)
                self.log_message(f"  Saved to: {test_config['dmesg_log_path']}", test_config)

                return True, dmesg_output
            else:
                return False, ""

        except Exception as e:
            self.log_message(f"  Error capturing dmesg: {e}", test_config)
            return False, ""

    def capture_journalctl(self, test_config):
        """
        Capture systemd journal for current boot
        Returns: tuple (success: bool, journal_output: str)
        """
        self.log_message("Capturing systemd journal for current boot...", test_config)

        try:
            result = subprocess.run(
                ['journalctl', '-b', '0', '--no-pager'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                journal_output = result.stdout
                line_count = len(journal_output.splitlines())
                self.log_message(f"  ✓ Journal captured ({line_count} lines)", test_config)
                return True, journal_output
            else:
                return False, ""

        except FileNotFoundError:
            self.log_message("  ⚠ journalctl not available", test_config)
            return False, ""
        except Exception as e:
            self.log_message(f"  Error capturing journal: {e}", test_config)
            return False, ""

    def check_for_errors(self, log_content, test_config):
        """
        Check log content for errors
        Returns: tuple (errors: list, warnings: list)
        """
        self.log_message("  Analyzing logs for errors and warnings...", test_config)

        errors = []
        warnings = []

        for line_num, line in enumerate(log_content.splitlines(), 1):
            line_lower = line.lower()

            # Skip if matches ignore pattern
            skip_line = False
            for ignore_pattern in test_config['ignore_patterns']:
                if re.search(ignore_pattern, line_lower):
                    skip_line = True
                    break

            if skip_line:
                continue

            # Check for error patterns
            for pattern in test_config['error_patterns']:
                if re.search(pattern, line_lower):
                    # Categorize by severity
                    if any(kw in line_lower for kw in ['error', 'fail', 'panic', 'oops', 'critical']):
                        errors.append({
                            'line_num': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
                    else:
                        warnings.append({
                            'line_num': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
                    break

        self.log_message(f"  Found {len(errors)} errors and {len(warnings)} warnings", test_config)

        return errors, warnings

    def check_expected_messages(self, log_content, test_config):
        """
        Check for expected boot success messages
        Returns: tuple (found: list, missing: list)
        """
        self.log_message("  Checking for expected boot messages...", test_config)

        found = []
        missing = []

        for expected in test_config['expected_messages']:
            if re.search(expected, log_content, re.IGNORECASE):
                found.append(expected)
                self.log_message(f"    ✓ Found: {expected}", test_config)
            else:
                missing.append(expected)
                self.log_message(f"    ✗ Missing: {expected}", test_config)

        return found, missing

    def analyze_boot_time(self, test_config):
        """
        Analyze boot time using systemd-analyze
        Returns: dict with boot analysis
        """
        self.log_message("Analyzing boot performance...", test_config)

        analysis = {}

        try:
            # Get boot time
            result = subprocess.run(
                ['systemd-analyze', 'time'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                boot_time_info = result.stdout.strip()
                self.log_message(f"  {boot_time_info}", test_config)
                analysis['boot_time'] = boot_time_info

            # Get top slow services
            result = subprocess.run(
                ['systemd-analyze', 'blame'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                blame_lines = result.stdout.splitlines()[:5]  # Top 5
                analysis['slow_services'] = blame_lines

                self.log_message("  Top 5 slowest services:", test_config)
                for line in blame_lines:
                    self.log_message(f"    {line}", test_config)

        except FileNotFoundError:
            self.log_message("  ⚠ systemd-analyze not available", test_config)
        except Exception as e:
            self.log_message(f"  Warning: {e}", test_config)

        return analysis

    def check_critical_services(self, test_config):
        """
        Check status of critical system services
        Returns: dict with service statuses
        """
        self.log_message("Checking critical system services...", test_config)

        critical_services = [
            'systemd-journald',
            'systemd-logind',
            'dbus',
        ]

        service_status = {}

        for service in critical_services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                status = result.stdout.strip()
                service_status[service] = status

                if status == 'active':
                    self.log_message(f"  ✓ {service}: active", test_config)
                else:
                    self.log_message(f"  ⚠ {service}: {status}", test_config)

            except Exception as e:
                self.log_message(f"  ⚠ {service}: Error - {e}", test_config)
                service_status[service] = 'unknown'

        return service_status

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.quick
    def test_033_boot_verification(self, test_config):
        """
        Test Case #33: Boot verification (kernel/messages)

        Test Setup: Display connected, boot media present
        Acceptance Criteria: Device boots as intended; kernel/messages show no errors

        IMPORTANT: This test must run ON the CM4 after it has booted.

        What this test validates:
        - System is fully booted and operational
        - Display is detected (informational)
        - No critical kernel errors in dmesg
        - Expected boot messages are present
        - Critical system services are running
        - Boot performance is reasonable

        This is a **100% automated** test that analyzes the current boot.
        """

        print("\n" + "=" * 70)
        print("Test Case #33: Boot Verification (kernel/messages)")
        print("=" * 70)
        print("\nHW Component Test - CM4 + Display")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 1: Verify System is Fully Booted
        # ================================================================
        print("\n[STEP 1] Verify System is Fully Booted")
        print("-" * 70)

        success, uptime, boot_time = self.check_system_booted(test_config)

        if not success:
            pytest.fail("System not properly booted")

        print(f"✓ System booted at: {boot_time}")
        print(f"✓ Current uptime: {uptime}")

        # ================================================================
        # STEP 2: Check Display Detection
        # ================================================================
        print("\n[STEP 2] Check Display Detection")
        print("-" * 70)

        display_detected, display_methods = self.check_display_detected(test_config)

        if display_detected:
            print("✓ Display detected")
        else:
            print("⚠ Display not detected (may not be connected)")

        print(f"  Detection methods: {', '.join(display_methods)}")

        # ================================================================
        # STEP 3: Capture Kernel Messages (dmesg)
        # ================================================================
        print("\n[STEP 3] Capture Kernel Messages (dmesg)")
        print("-" * 70)

        success, dmesg_output = self.capture_dmesg(test_config)

        if not success:
            pytest.fail("Failed to capture dmesg")

        print(f"✓ dmesg captured ({len(dmesg_output.splitlines())} lines)")

        # ================================================================
        # STEP 4: Capture systemd Journal
        # ================================================================
        print("\n[STEP 4] Capture systemd Journal")
        print("-" * 70)

        journal_success, journal_output = self.capture_journalctl(test_config)

        if journal_success:
            print(f"✓ Journal captured ({len(journal_output.splitlines())} lines)")
        else:
            print("⚠ Journal not available")

        # ================================================================
        # STEP 5: Analyze Logs for Errors
        # ================================================================
        print("\n[STEP 5] Analyze Logs for Errors and Warnings")
        print("-" * 70)

        dmesg_errors, dmesg_warnings = self.check_for_errors(dmesg_output, test_config)

        journal_errors = []
        journal_warnings = []
        if journal_success:
            journal_errors, journal_warnings = self.check_for_errors(journal_output, test_config)

        all_errors = dmesg_errors + journal_errors
        all_warnings = dmesg_warnings + journal_warnings

        print(f"  Total errors: {len(all_errors)}")
        print(f"  Total warnings: {len(all_warnings)}")

        # ================================================================
        # STEP 6: Check Expected Boot Messages
        # ================================================================
        print("\n[STEP 6] Verify Expected Boot Messages")
        print("-" * 70)

        found_messages, missing_messages = self.check_expected_messages(dmesg_output, test_config)

        print(f"✓ Found {len(found_messages)}/{len(test_config['expected_messages'])} expected messages")

        # ================================================================
        # STEP 7: Analyze Boot Performance
        # ================================================================
        print("\n[STEP 7] Analyze Boot Performance")
        print("-" * 70)

        boot_analysis = self.analyze_boot_time(test_config)

        if boot_analysis.get('boot_time'):
            print(f"✓ Boot time: {boot_analysis['boot_time']}")

        # ================================================================
        # STEP 8: Check Critical Services
        # ================================================================
        print("\n[STEP 8] Check Critical System Services")
        print("-" * 70)

        service_status = self.check_critical_services(test_config)

        active_services = sum(1 for s in service_status.values() if s == 'active')
        print(f"✓ {active_services}/{len(service_status)} critical services active")

        # ================================================================
        # Generate Report
        # ================================================================
        print("\n" + "=" * 70)
        print("BOOT VERIFICATION REPORT")
        print("=" * 70)

        # Show critical errors (if any)
        critical_errors = [
            e for e in all_errors
            if any(kw in e['content'].lower() for kw in ['panic', 'oops', 'fatal'])
        ]

        if critical_errors:
            print(f"\n❌ CRITICAL ERRORS: {len(critical_errors)}")
            for i, error in enumerate(critical_errors[:5], 1):
                print(f"  {i}. Line {error['line_num']}: {error['content'][:80]}")
        else:
            print("\n✅ No critical errors found")

        # Show non-critical errors (if any)
        if all_errors and not critical_errors:
            print(f"\n⚠️  NON-CRITICAL ERRORS: {len(all_errors)}")
            for i, error in enumerate(all_errors[:3], 1):
                print(f"  {i}. {error['content'][:80]}")

        # Show warnings summary
        if all_warnings:
            print(f"\n⚠️  WARNINGS: {len(all_warnings)} (see log for details)")

        print("=" * 70)

        # ================================================================
        # Test Assertions
        # ================================================================
        print("\n[Test Assertions]")
        print("-" * 70)

        # Assertion 1: No critical errors
        if critical_errors:
            pytest.fail(
                f"Critical boot errors found: {len(critical_errors)} errors\n"
                f"First error: {critical_errors[0]['content']}"
            )

        print("✓ No critical errors found")

        # Assertion 2: Most expected messages present
        success_rate = len(found_messages) / len(test_config['expected_messages'])

        if success_rate < 0.6:
            pytest.fail(
                f"Only {success_rate:.0%} of expected boot messages found\n"
                f"Missing: {missing_messages}"
            )

        print(f"✓ {success_rate:.0%} of expected boot messages present")

        # Assertion 3: Critical services running
        service_success_rate = active_services / len(service_status)

        if service_success_rate < 0.75:
            pytest.fail(f"Only {service_success_rate:.0%} of critical services active")

        print(f"✓ {service_success_rate:.0%} of critical services active")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ System booted successfully ({uptime})")
        print(f"  ✓ Display detected: {display_detected}")
        print(f"  ✓ No critical kernel errors")
        print(f"  ✓ {len(found_messages)} expected boot messages present")
        print(f"  ✓ {active_services} critical services active")
        print(f"  ⚠ {len(all_warnings)} warnings (non-critical)")
        print("\n✓ Device boots as intended; kernel/messages show no critical errors")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")
            print(f"📄 dmesg log: {test_config['dmesg_log_path']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
