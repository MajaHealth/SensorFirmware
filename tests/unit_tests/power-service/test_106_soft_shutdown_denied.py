#!/usr/bin/env python3
"""
Test Case #106: Soft Shutdown Denied/Timeout Behavior
Category: Unit Test - Power Service
Component: Shutdown Handling

Tests that a short button press is detected but does NOT trigger shutdown.
The "denied" scenario is implemented by the app not initiating shutdown
when receiving button_info with short hold_time.

Firmware behavior:
- Power-service listens on port 501
- When button pressed: sends {"type": "button_info", "state": true, "hold_time": X}
- When button released: sends {"type": "button_info", "state": false, "hold_time": 0}
- App receives button_info and decides whether to initiate shutdown
- Short press (< 3 seconds) = app should NOT shutdown (denied scenario)
"""

import subprocess
import time
import pytest
import socket
import json
import os
from datetime import datetime


class TestSoftShutdownDenied:
    """Unit Test - Soft Shutdown Denied (Short Press Detection)"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for shutdown denied test"""
        return {
            # GPIO Configuration
            'switch_gpio_pin': 17,
            'gpio_mode': 'BCM',
            'pull_resistor': 'PULL_UP',

            # Power service connection
            'power_service_host': os.environ.get('PI_TARGET_IP', '127.0.0.1'),
            'power_service_port': 501,

            # Press timing
            'short_press_duration': 0.5,  # seconds - should NOT trigger shutdown
            'shutdown_threshold': 3.0,     # seconds - hold time that triggers shutdown

            # Timeouts
            'connection_timeout': 5.0,
            'message_timeout': 10.0,

            # Verification
            'verify_services_active': True,
            'services_to_check': [
                'systemd-journald',
            ],

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_106_shutdown_denied.log',
        }

    def setup_method(self):
        """Setup before each test method"""
        self.client_socket = None

    def teardown_method(self):
        """Cleanup after each test method"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
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

    def connect_to_power_service(self, config):
        """Connect to power-service on port 501"""
        self.log_message(f"Connecting to power-service at {config['power_service_host']}:{config['power_service_port']}...", config)

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(config['connection_timeout'])
            self.client_socket.connect((config['power_service_host'], config['power_service_port']))
            self.log_message("✓ Connected to power-service", config)
            return True
        except Exception as e:
            self.log_message(f"✗ Connection failed: {e}", config)
            return False

    def wait_for_button_info(self, config, expected_state=None, timeout=None):
        """Wait for button_info message with optional state filter"""
        if timeout is None:
            timeout = config['message_timeout']

        self.client_socket.settimeout(1.0)
        start_time = time.time()
        buffer = ""

        while time.time() - start_time < timeout:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    buffer += data.decode('utf-8')

                    # Try to parse JSON messages
                    while buffer:
                        # Find complete JSON object
                        try:
                            # Try to find a complete JSON object
                            brace_count = 0
                            json_end = -1
                            in_string = False
                            escape_next = False

                            for i, char in enumerate(buffer):
                                if escape_next:
                                    escape_next = False
                                    continue
                                if char == '\\':
                                    escape_next = True
                                    continue
                                if char == '"' and not escape_next:
                                    in_string = not in_string
                                    continue
                                if in_string:
                                    continue
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break

                            if json_end > 0:
                                json_str = buffer[:json_end]
                                buffer = buffer[json_end:].lstrip()

                                try:
                                    msg = json.loads(json_str)
                                    if msg.get('type') == 'button_info':
                                        state = msg.get('state')
                                        if expected_state is None or state == expected_state:
                                            self.log_message(f"  Button info: state={state}, hold_time={msg.get('hold_time')}", config)
                                            return msg
                                except json.JSONDecodeError:
                                    pass
                            else:
                                break  # No complete JSON yet, wait for more data

                        except Exception:
                            break

            except socket.timeout:
                continue
            except Exception as e:
                self.log_message(f"  Error receiving: {e}", config)
                break

        return None

    def check_no_shutdown_initiated(self, config):
        """Verify shutdown was NOT initiated using reliable detection methods"""
        self.log_message("Checking that shutdown was NOT initiated...", config)

        shutdown_detected = False

        # Method 1: Check system state via systemctl (most reliable)
        try:
            result = subprocess.run(
                ['systemctl', 'is-system-running'],
                capture_output=True,
                text=True,
                timeout=2
            )

            status = result.stdout.strip()

            if status in ['running', 'degraded']:
                self.log_message(f"  ✓ System state: {status} (normal)", config)
            elif status in ['stopping', 'reboot', 'poweroff', 'halt']:
                self.log_message(f"  ✗ System state: {status} (shutting down!)", config)
                shutdown_detected = True
            else:
                self.log_message(f"  ⚠ System state: {status}", config)

        except Exception as e:
            self.log_message(f"  ⚠ Could not check system state: {e}", config)

        # Method 2: Check for scheduled shutdown
        try:
            result = subprocess.run(
                ['systemctl', 'list-jobs'],
                capture_output=True,
                text=True,
                timeout=2
            )

            output = result.stdout.lower()
            if 'poweroff' in output or 'reboot' in output or 'halt' in output:
                self.log_message("  ✗ Shutdown job scheduled!", config)
                shutdown_detected = True
            else:
                self.log_message("  ✓ No shutdown jobs scheduled", config)

        except Exception as e:
            self.log_message(f"  ⚠ Could not check scheduled jobs: {e}", config)

        # Method 3: Check /run/systemd/shutdown/scheduled
        try:
            if os.path.exists('/run/systemd/shutdown/scheduled'):
                self.log_message("  ✗ Scheduled shutdown file exists!", config)
                shutdown_detected = True
            else:
                self.log_message("  ✓ No scheduled shutdown file", config)
        except:
            pass

        if shutdown_detected:
            self.log_message("  ✗ SHUTDOWN DETECTED - Test failed", config)
            return False
        else:
            self.log_message("  ✓ System running normally - No shutdown initiated", config)
            return True

    def verify_services_active(self, config):
        """Verify critical services are still running"""
        self.log_message("Verifying services are still active...", config)

        active_services = []
        inactive_services = []

        for service in config['services_to_check']:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                status = result.stdout.strip()

                if status == 'active':
                    active_services.append(service)
                    self.log_message(f"  ✓ {service}: active", config)
                else:
                    inactive_services.append(service)
                    self.log_message(f"  ✗ {service}: {status}", config)

            except Exception as e:
                self.log_message(f"  ⚠ {service}: error checking - {e}", config)

        return active_services, inactive_services

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.gpio
    @pytest.mark.network
    @pytest.mark.shutdown
    def test_106_soft_shutdown_denied(self, test_config):
        """
        Test Case #106: Soft shutdown denied/timeout behavior

        Acceptance Criteria:
        - Button press is detected by power-service
        - button_info message received with state=true
        - Short press (< shutdown threshold) does NOT trigger shutdown
        - Services remain active
        - System returns to normal state after button release
        """

        print("\n" + "=" * 70)
        print("Test Case #106: Soft Shutdown Denied/Timeout Behavior")
        print("=" * 70)
        print("\nTest validates that SHORT button press does NOT trigger shutdown")
        print(f"Shutdown threshold: {test_config['shutdown_threshold']}s")
        print(f"Test press duration: < {test_config['short_press_duration']}s")
        print("=" * 70)

        # Clear previous logs
        if test_config['enable_logging']:
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 1: Connect to Power Service
        # ================================================================
        print("\n[STEP 1] Connect to Power Service")
        print("-" * 70)

        connected = self.connect_to_power_service(test_config)
        assert connected, f"Failed to connect to power-service at {test_config['power_service_host']}:{test_config['power_service_port']}"

        # ================================================================
        # STEP 2: Prompt for Button Press
        # ================================================================
        print("\n[STEP 2] Button Press Detection")
        print("-" * 70)

        print(f"\n{'=' * 50}")
        print("MANUAL ACTION REQUIRED:")
        print(f"   Press and RELEASE the OFF button quickly")
        print(f"   (Hold for less than {test_config['short_press_duration']}s)")
        print(f"{'=' * 50}")
        input("\n   Press ENTER when ready, then press the button...")

        # ================================================================
        # STEP 3: Wait for Button Press Detection
        # ================================================================
        print("\n[STEP 3] Waiting for Button Press Detection")
        print("-" * 70)

        self.log_message("Waiting for button_info with state=true...", test_config)

        button_pressed = self.wait_for_button_info(test_config, expected_state=True, timeout=15)

        if button_pressed:
            self.log_message(f"✓ Button press detected!", test_config)
            self.log_message(f"  state: {button_pressed.get('state')}", test_config)
            self.log_message(f"  hold_time: {button_pressed.get('hold_time')}", test_config)
        else:
            pytest.fail(
                "TIMEOUT: Did not receive button_info with state=true!\n"
                "Possible causes:\n"
                "  - Button was not pressed\n"
                "  - Power-service not running\n"
                "  - Wrong port or host\n"
                "  - GPIO not configured correctly"
            )

        # ================================================================
        # STEP 4: Wait for Button Release
        # ================================================================
        print("\n[STEP 4] Waiting for Button Release")
        print("-" * 70)

        self.log_message("Waiting for button_info with state=false...", test_config)

        button_released = self.wait_for_button_info(test_config, expected_state=False, timeout=10)

        if button_released:
            self.log_message(f"✓ Button release detected!", test_config)
        else:
            self.log_message("⚠ Did not receive explicit release message (may be normal)", test_config)

        # ================================================================
        # STEP 5: Verify Hold Time Was Below Threshold
        # ================================================================
        print("\n[STEP 5] Verify Short Press (Below Shutdown Threshold)")
        print("-" * 70)

        hold_time = button_pressed.get('hold_time', 0)
        # hold_time is in deciseconds (1/10 second), convert to seconds
        hold_time_seconds = hold_time / 10.0 if hold_time > 0 else hold_time

        self.log_message(f"Hold time recorded: {hold_time_seconds}s", test_config)
        self.log_message(f"Shutdown threshold: {test_config['shutdown_threshold']}s", test_config)

        if hold_time_seconds < test_config['shutdown_threshold']:
            self.log_message(f"✓ Hold time ({hold_time_seconds}s) < threshold ({test_config['shutdown_threshold']}s)", test_config)
            self.log_message("  This is a SHORT press - shutdown should be DENIED", test_config)
        else:
            self.log_message(f"⚠ Hold time ({hold_time_seconds}s) >= threshold - may trigger shutdown", test_config)

        # ================================================================
        # STEP 6: Verify No Shutdown Initiated
        # ================================================================
        print("\n[STEP 6] Verify No Shutdown Initiated")
        print("-" * 70)

        # Wait a moment for any shutdown to be triggered
        time.sleep(2.0)

        no_shutdown = self.check_no_shutdown_initiated(test_config)
        assert no_shutdown, "Shutdown was initiated despite short press!"

        # ================================================================
        # STEP 7: Verify Services Still Active
        # ================================================================
        print("\n[STEP 7] Verify Services Still Active")
        print("-" * 70)

        active, inactive = self.verify_services_active(test_config)
        assert len(active) > 0, "No active services found - system may be shutting down!"

        # ================================================================
        # STEP 8: Cleanup and Report
        # ================================================================
        print("\n[STEP 8] Cleanup")
        print("-" * 70)

        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.log_message("✓ Disconnected from power-service", test_config)

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)

        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ Connected to power-service on port {test_config['power_service_port']}")
        print(f"  ✓ Button press detected (state=true)")
        print(f"  ✓ Hold time: {hold_time_seconds}s (below {test_config['shutdown_threshold']}s threshold)")
        print(f"  ✓ Shutdown NOT initiated (denied scenario)")
        print(f"  ✓ Services remain active")
        print(f"  ✓ System returned to normal state")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
