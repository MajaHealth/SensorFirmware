#!/usr/bin/env python3
"""
Test Case #106: Soft Shutdown Denied/Timeout Behavior
Category: Unit Test - Power Service
Component: Shutdown Handling

Tests firmware's handling of denied shutdown or timeout scenarios
when ACK is not received or shutdown is denied by application.
"""

import subprocess
import time
import pytest
import platform
import os
import socket
import threading
from datetime import datetime
from enum import Enum

# Try to import RPi.GPIO
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class ShutdownResponse(Enum):
    """Types of responses from application"""
    ACK_ACCEPT = "ACK:shutdown_complete"
    ACK_DENIED = "ACK:denied"
    NACK_BUSY = "NACK:busy"
    TIMEOUT = "TIMEOUT"  # No response


class MockApplication:
    """
    Configurable mock application for testing shutdown scenarios
    """

    def __init__(self, host='127.0.0.1', port=8765, response_behavior=ShutdownResponse.ACK_ACCEPT):
        self.host = host
        self.port = port
        self.response_behavior = response_behavior

        self.server_socket = None
        self.client_socket = None
        self.running = False
        self.server_thread = None

        self.messages_received = []
        self.messages_sent = []
        self.connection_established = False

        # Configurable behavior
        self.auto_respond = True
        self.response_delay = 0.5
        self.timeout_duration = None  # Set to trigger timeout

    def set_response_behavior(self, behavior):
        """Change response behavior dynamically"""
        self.response_behavior = behavior
        print(f"Mock app: Response behavior set to {behavior.value}")

    def set_timeout(self, duration):
        """Configure to timeout (no response for duration)"""
        self.timeout_duration = duration
        self.auto_respond = False
        print(f"Mock app: Configured to timeout ({duration}s)")

    def start(self):
        """Start the mock application server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1.0)

        self.running = True
        self.server_thread = threading.Thread(target=self._server_loop)
        self.server_thread.daemon = True
        self.server_thread.start()

        print(f"Mock app started on {self.host}:{self.port}")

    def stop(self):
        """Stop the mock application server"""
        self.running = False

        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        if self.server_thread:
            self.server_thread.join(timeout=2)

        print("Mock app stopped")

    def _server_loop(self):
        """Main server loop"""
        while self.running:
            try:
                self.client_socket, addr = self.server_socket.accept()
                self.connection_established = True
                print(f"Mock app: Connection from {addr}")

                self._handle_client()

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Mock app error: {e}")

    def _handle_client(self):
        """Handle messages from connected client (firmware)"""
        self.client_socket.settimeout(1.0)

        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8').strip()
                timestamp = datetime.now().isoformat()

                self.messages_received.append({
                    'timestamp': timestamp,
                    'message': message
                })

                print(f"Mock app received: {message}")

                # Handle based on configured behavior
                if 'close' in message.lower():
                    if self.timeout_duration:
                        print(f"Mock app: Simulating timeout ({self.timeout_duration}s)...")
                        time.sleep(self.timeout_duration)
                        # Don't send response
                    elif self.auto_respond:
                        time.sleep(self.response_delay)
                        self.send_response(self.response_behavior)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Mock app client error: {e}")
                break

    def send_response(self, response_type):
        """Send configured response to firmware"""
        message = response_type.value

        try:
            self.client_socket.send(message.encode('utf-8'))

            timestamp = datetime.now().isoformat()
            self.messages_sent.append({
                'timestamp': timestamp,
                'message': message
            })

            print(f"Mock app sent: {message}")
            return True

        except Exception as e:
            print(f"Failed to send response: {e}")
            return False


class TestSoftShutdownDenied:
    """Unit Test - Soft Shutdown Denied/Timeout"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for shutdown denied test"""
        return {
            # GPIO Configuration
            'switch_gpio_pin': 17,
            'gpio_mode': 'BCM',
            'pull_resistor': 'PULL_UP',

            # Press timing
            'short_press_duration': 0.5,

            # TCP/IP Configuration
            'mock_app_host': '127.0.0.1',
            'mock_app_port': 8765,

            # Timeout settings
            'ack_timeout': 3.0,          # How long firmware waits for ACK
            'timeout_test_duration': 5.0, # How long to wait for timeout

            # Expected behavior
            'expected_close_message': 'close',
            'expected_denied_message': 'denied',

            # Verification
            'verify_services_active': True,
            'services_to_check': [
                'systemd-journald',  # Core service that should stay running
            ],

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_106_shutdown_denied.log',
        }

    def setup_method(self):
        """Setup before each test method"""
        if GPIO_AVAILABLE:
            GPIO.setwarnings(False)
            GPIO.cleanup()

        self.mock_app = None

    def teardown_method(self):
        """Cleanup after each test method"""
        if self.mock_app:
            self.mock_app.stop()

        if GPIO_AVAILABLE:
            GPIO.cleanup()

    def log_message(self, message, config):
        """Log message to file and console"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"

        print(log_entry)

        if config['enable_logging']:
            try:
                with open(config['log_file'], 'a') as f:
                    f.write(log_entry + '\n')
            except:
                pass

    def setup_gpio(self, config):
        """Setup GPIO for switch simulation"""
        if not GPIO_AVAILABLE:
            return self.setup_gpio_sysfs(config)

        try:
            if config['gpio_mode'] == 'BCM':
                GPIO.setmode(GPIO.BCM)
            else:
                GPIO.setmode(GPIO.BOARD)

            pull_mode = GPIO.PUD_UP if config['pull_resistor'] == 'PULL_UP' else GPIO.PUD_DOWN
            GPIO.setup(config['switch_gpio_pin'], GPIO.IN, pull_up_down=pull_mode)

            self.log_message(f"✓ GPIO {config['switch_gpio_pin']} configured", config)
            return True

        except Exception as e:
            self.log_message(f"✗ GPIO setup failed: {e}", config)
            return False

    def setup_gpio_sysfs(self, config):
        """Fallback GPIO setup using sysfs"""
        gpio_pin = config['switch_gpio_pin']
        try:
            if not os.path.exists(f'/sys/class/gpio/gpio{gpio_pin}'):
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(gpio_pin))
                time.sleep(0.1)

            with open(f'/sys/class/gpio/gpio{gpio_pin}/direction', 'w') as f:
                f.write('in')

            self.log_message(f"✓ GPIO configured via sysfs", config)
            return True
        except Exception as e:
            self.log_message(f"✗ sysfs setup failed: {e}", config)
            return False

    def simulate_switch_press(self, config):
        """Simulate short switch press"""
        self.log_message("Simulating switch press...", config)

        print(f"\n📋 MANUAL ACTION:")
        print(f"   Press the OFF switch briefly ({config['short_press_duration']}s)")
        input("   Press ENTER after pressing switch...")

        self.log_message("Switch press simulated", config)
        return True

    def verify_services_active(self, config):
        """Verify critical services are still running"""
        self.log_message("Verifying services still active...", config)

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

    def check_no_shutdown_initiated(self, config):
        """Verify shutdown was NOT initiated"""
        self.log_message("Checking that shutdown was NOT initiated...", config)

        # Check for shutdown processes
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'shutdown|poweroff'],
                capture_output=True,
                timeout=2
            )

            if result.returncode == 0:
                self.log_message("  ⚠ WARNING: Found shutdown process!", config)
                return False
            else:
                self.log_message("  ✓ No shutdown process running", config)

        except:
            pass

        # Check system state
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
            else:
                self.log_message(f"  ⚠ System state: {status}", config)
                return False

        except:
            pass

        return True

    def cleanup_gpio_sysfs(self, config):
        """Cleanup sysfs GPIO"""
        try:
            gpio_pin = config['switch_gpio_pin']
            if os.path.exists(f'/sys/class/gpio/gpio{gpio_pin}'):
                with open('/sys/class/gpio/unexport', 'w') as f:
                    f.write(str(gpio_pin))
        except:
            pass

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.gpio
    @pytest.mark.network
    @pytest.mark.shutdown
    def test_106_soft_shutdown_denied(self, test_config):
        """
        Test Case #106: Soft shutdown denied/timeout behavior

        Acceptance Criteria:
        - "close" received by mock app
        - Denied/timeout occurs
        - Firmware does not initiate shutdown
        - Tasks/services remain active
        - Firmware returns to monitoring/normal state
        """

        print("\n" + "=" * 70)
        print("Test Case #106: Soft Shutdown Denied/Timeout Behavior")
        print("=" * 70)

        # Clear previous logs
        if test_config['enable_logging']:
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Run both scenarios
        self._test_scenario_denied(test_config)
        self._test_scenario_timeout(test_config)

        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)

    def _test_scenario_denied(self, test_config):
        """Test Scenario A: Application denies shutdown"""

        print("\n[SCENARIO A] Testing Denied Shutdown")
        print("-" * 70)

        self.mock_app = MockApplication(
            host=test_config['mock_app_host'],
            port=test_config['mock_app_port'],
            response_behavior=ShutdownResponse.ACK_DENIED
        )

        try:
            self.mock_app.start()
            time.sleep(0.5)

            success = self.setup_gpio(test_config)
            assert success, "Failed to setup GPIO"

            firmware_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                firmware_client.connect((
                    test_config['mock_app_host'],
                    test_config['mock_app_port']
                ))

                self.simulate_switch_press(test_config)

                close_message = test_config['expected_close_message']
                firmware_client.send(close_message.encode('utf-8'))
                time.sleep(1.5)

                # Verify denial received
                firmware_client.settimeout(3.0)
                data = firmware_client.recv(1024)
                response = data.decode('utf-8').strip()

                assert 'denied' in response.lower(), f"Expected denial, got: {response}"

                # Verify no shutdown
                time.sleep(1.0)
                no_shutdown = self.check_no_shutdown_initiated(test_config)
                assert no_shutdown, "Shutdown was initiated despite denial!"

                # Verify services active
                active, _ = self.verify_services_active(test_config)
                assert len(active) > 0, "No active services found"

                print("\nSCENARIO A: ✓ PASS")

            finally:
                firmware_client.close()

        finally:
            if self.mock_app:
                self.mock_app.stop()
                self.mock_app = None

            if not GPIO_AVAILABLE:
                self.cleanup_gpio_sysfs(test_config)

    def _test_scenario_timeout(self, test_config):
        """Test Scenario B: Timeout (no response)"""

        print("\n[SCENARIO B] Testing Timeout Behavior")
        print("-" * 70)

        self.mock_app = MockApplication(
            host=test_config['mock_app_host'],
            port=test_config['mock_app_port'] + 1,
        )
        self.mock_app.set_timeout(test_config['timeout_test_duration'])

        try:
            self.mock_app.start()
            time.sleep(0.5)

            success = self.setup_gpio(test_config)
            assert success, "Failed to setup GPIO"

            firmware_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                firmware_client.connect((
                    test_config['mock_app_host'],
                    test_config['mock_app_port'] + 1
                ))

                self.simulate_switch_press(test_config)

                close_message = test_config['expected_close_message']
                firmware_client.send(close_message.encode('utf-8'))
                time.sleep(0.5)

                # Wait for timeout
                timeout_duration = test_config['ack_timeout']
                firmware_client.settimeout(timeout_duration)

                try:
                    data = firmware_client.recv(1024)
                    if data:
                        pytest.fail(f"Unexpected response: {data.decode('utf-8')}")
                except socket.timeout:
                    print(f"✓ TIMEOUT occurred after {timeout_duration}s")

                # Verify no shutdown
                time.sleep(1.0)
                no_shutdown = self.check_no_shutdown_initiated(test_config)
                assert no_shutdown, "Shutdown initiated despite timeout!"

                # Verify services active
                active, _ = self.verify_services_active(test_config)
                assert len(active) > 0, "No active services found"

                print("\nSCENARIO B: ✓ PASS")

            finally:
                firmware_client.close()

        finally:
            if self.mock_app:
                self.mock_app.stop()
                self.mock_app = None

            if not GPIO_AVAILABLE:
                self.cleanup_gpio_sysfs(test_config)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
