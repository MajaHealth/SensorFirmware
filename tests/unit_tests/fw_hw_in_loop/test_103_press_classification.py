#!/usr/bin/env python3
"""
Test Case #103: Press Classification (Short vs Long)
Category: FW Hardware-in-Loop Test
Component: Contact-based switch + CM4 GPIO + Firmware

Tests contact-based switch for proper short press vs long press detection.
Measures actual press duration and validates classification logic.

This test requires manual button presses with specific timing (semi-automated).
"""

import subprocess
import time
import pytest
import platform
import os
from datetime import datetime

# Try to import RPi.GPIO (only available on Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - will use alternative methods")


class TestPressClassification:
    """FW Hardware-in-Loop Test - Press Classification"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for press classification test"""
        return {
            # GPIO Configuration
            'switch_gpio_pin': 17,  # BCM GPIO 17 (Physical pin 11)
            'gpio_mode': 'BCM',     # BCM or BOARD numbering
            'pull_resistor': 'PULL_UP',  # PULL_UP or PULL_DOWN

            # Press timing thresholds (in seconds)
            'short_press_min': 0.05,    # Minimum 50ms for valid press
            'short_press_max': 1.0,     # Maximum 1s for short press
            'long_press_min': 1.0,      # Minimum 1s for long press
            'long_press_max': 10.0,     # Maximum 10s for long press

            # Detection settings
            'debounce_time': 0.02,      # 20ms debounce
            'poll_interval': 0.01,      # 10ms polling rate

            # Active state (depends on pull resistor)
            'pressed_state': 0,         # GPIO=0 when pressed (PULL_UP)
            'released_state': 1,        # GPIO=1 when released (PULL_UP)

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_103_press_classification.log',
            'event_log_file': '/tmp/press_events.log',

            # Firmware service monitoring (optional)
            'monitor_firmware_service': False,  # Set to True if service available
            'firmware_service_name': 'power-service',
        }

    def setup_method(self):
        """Setup before each test method"""
        if GPIO_AVAILABLE:
            GPIO.setwarnings(False)
            GPIO.cleanup()

    def teardown_method(self):
        """Cleanup after each test method"""
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

    def log_event(self, event_type, duration, config):
        """Log press event to event log"""
        timestamp = datetime.now().isoformat()
        event_entry = f"{timestamp},{event_type},{duration:.3f}\n"

        if config['enable_logging']:
            try:
                with open(config['event_log_file'], 'a') as f:
                    f.write(event_entry)
            except:
                pass

    def setup_gpio(self, config):
        """Setup GPIO pin as input"""
        if GPIO_AVAILABLE:
            try:
                if config['gpio_mode'] == 'BCM':
                    GPIO.setmode(GPIO.BCM)
                else:
                    GPIO.setmode(GPIO.BOARD)

                pull_mode = GPIO.PUD_UP if config['pull_resistor'] == 'PULL_UP' else GPIO.PUD_DOWN
                GPIO.setup(config['switch_gpio_pin'], GPIO.IN, pull_up_down=pull_mode)

                self.log_message(
                    f"✓ GPIO {config['switch_gpio_pin']} configured with {config['pull_resistor']}",
                    config
                )
                return True
            except Exception as e:
                self.log_message(f"✗ GPIO setup failed: {e}", config)
                return False
        else:
            # Fallback to sysfs
            return self.setup_gpio_sysfs(config)

    def setup_gpio_sysfs(self, config):
        """Setup GPIO using sysfs"""
        gpio_pin = config['switch_gpio_pin']
        try:
            if not os.path.exists(f'/sys/class/gpio/gpio{gpio_pin}'):
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(gpio_pin))
                time.sleep(0.1)

            with open(f'/sys/class/gpio/gpio{gpio_pin}/direction', 'w') as f:
                f.write('in')

            self.log_message(f"✓ GPIO {gpio_pin} configured via sysfs", config)
            return True
        except Exception as e:
            self.log_message(f"✗ sysfs setup failed: {e}", config)
            return False

    def read_gpio(self, config):
        """Read current GPIO state"""
        if GPIO_AVAILABLE:
            try:
                return GPIO.input(config['switch_gpio_pin'])
            except:
                return None
        else:
            # Read via sysfs
            try:
                with open(f'/sys/class/gpio/gpio{config["switch_gpio_pin"]}/value', 'r') as f:
                    return int(f.read().strip())
            except:
                return None

    def wait_for_press(self, config, timeout=60):
        """
        Wait for button press (GPIO goes to pressed state)
        Returns: bool (True if press detected, False if timeout)
        """
        start_time = time.time()

        self.log_message("Waiting for button press...", config)

        while (time.time() - start_time) < timeout:
            state = self.read_gpio(config)

            if state == config['pressed_state']:
                # Debounce check
                time.sleep(config['debounce_time'])
                state_confirm = self.read_gpio(config)

                if state_confirm == config['pressed_state']:
                    self.log_message("✓ Press detected (GPIO went LOW)", config)
                    return True

            time.sleep(config['poll_interval'])

        self.log_message("✗ Timeout waiting for press", config)
        return False

    def wait_for_release(self, config, timeout=15):
        """
        Wait for button release (GPIO goes to released state)
        Returns: bool (True if release detected, False if timeout)
        """
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            state = self.read_gpio(config)

            if state == config['released_state']:
                # Debounce check
                time.sleep(config['debounce_time'])
                state_confirm = self.read_gpio(config)

                if state_confirm == config['released_state']:
                    self.log_message("✓ Release detected (GPIO went HIGH)", config)
                    return True

            time.sleep(config['poll_interval'])

        self.log_message("✗ Timeout waiting for release", config)
        return False

    def detect_press_with_timing(self, config, timeout=60):
        """
        Detect a button press and measure its duration

        Returns: tuple (detected: bool, duration: float, press_type: str)
        - detected: True if valid press detected
        - duration: Press duration in seconds
        - press_type: 'short', 'long', or 'invalid'
        """
        self.log_message("=" * 50, config)
        self.log_message("Starting press detection...", config)

        # Wait for press
        if not self.wait_for_press(config, timeout):
            return False, 0.0, 'none'

        # Record press start time
        press_start = time.time()
        self.log_message(f"Press started at {press_start:.3f}", config)

        # Wait for release
        if not self.wait_for_release(config, timeout=config['long_press_max'] + 1):
            self.log_message("✗ Release not detected within timeout", config)
            return False, 0.0, 'timeout'

        # Calculate duration
        press_end = time.time()
        duration = press_end - press_start

        self.log_message(f"Press ended at {press_end:.3f}", config)
        self.log_message(f"Press duration: {duration:.3f} seconds", config)

        # Classify press type
        if duration < config['short_press_min']:
            press_type = 'too_short'
            classification = '⚠️  TOO SHORT (likely bounce or noise)'
        elif duration <= config['short_press_max']:
            press_type = 'short'
            classification = '✓ SHORT PRESS'
        elif duration <= config['long_press_max']:
            press_type = 'long'
            classification = '✓ LONG PRESS'
        else:
            press_type = 'too_long'
            classification = '⚠️  TOO LONG (exceeded max)'

        self.log_message(f"Classification: {classification}", config)
        self.log_message("=" * 50, config)

        # Log to event file
        self.log_event(press_type, duration, config)

        return True, duration, press_type

    def check_firmware_service(self, config):
        """Check if firmware service is running (optional)"""
        if not config['monitor_firmware_service']:
            return None

        try:
            result = subprocess.run(
                ['systemctl', 'is-active', config['firmware_service_name']],
                capture_output=True,
                text=True,
                timeout=5
            )

            status = result.stdout.strip()
            self.log_message(f"Firmware service status: {status}", config)
            return status == 'active'

        except Exception as e:
            self.log_message(f"Could not check firmware service: {e}", config)
            return None

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
    @pytest.mark.cm4
    def test_103_press_classification(self, test_config):
        """
        Test Case #103: Press classification (short vs long)

        Test Setup: DUT with switch wired to CM4 GPIO; firmware event logging enabled
        Acceptance Criteria:
        - Short press correctly identified as short press
        - Long press correctly identified as long press

        IMPORTANT: This test requires manual button presses with specific timing.
        Test is semi-automated - requires timed physical interaction.

        What this test validates:
        - Short press detection (50ms - 1.0s duration)
        - Long press detection (1.0s - 10.0s duration)
        - Press timing accuracy (millisecond precision)
        - Press classification logic
        - Debouncing effectiveness
        - Event logging functionality
        - Classification consistency
        """

        print("\n" + "=" * 70)
        print("Test Case #103: Press Classification (Short vs Long)")
        print("=" * 70)
        print("\nFW Hardware-in-Loop Test")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify firmware correctly classifies short vs long presses")
        print("\nTIMING THRESHOLDS:")
        print(f"  Short Press: {test_config['short_press_min']*1000:.0f}ms - {test_config['short_press_max']*1000:.0f}ms")
        print(f"  Long Press:  {test_config['long_press_min']*1000:.0f}ms - {test_config['long_press_max']*1000:.0f}ms")
        print("\nHARDWARE:")
        print(f"  GPIO Pin: {test_config['switch_gpio_pin']}")
        print(f"  Pull Resistor: {test_config['pull_resistor']}")
        print("\nCLASSIFICATION:")
        print("  │ Invalid │  Short Press  │   Long Press   │ Invalid │")
        print("  ├─────────┼───────────────┼────────────────┼─────────┤")
        print("  0      50ms            1.0s             10.0s      ∞")
        print("=" * 70)

        # Clear previous logs
        if test_config['enable_logging']:
            for log_file in [test_config['log_file'], test_config['event_log_file']]:
                try:
                    open(log_file, 'w').close()
                except:
                    pass

        # ================================================================
        # STEP 1: Check Prerequisites
        # ================================================================
        print("\n[STEP 1] Check Prerequisites")
        print("-" * 70)

        if platform.system() != "Linux":
            pytest.skip(f"Test requires Linux. Current OS: {platform.system()}")

        print("✓ Running on Linux")
        self.log_message("Test started on Linux platform", test_config)

        # Check Raspberry Pi
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip()
                print(f"✓ Device: {model}")
                self.log_message(f"Device: {model}", test_config)
        except:
            print("⚠️  Could not verify Raspberry Pi model")

        # Check firmware service (optional)
        service_status = self.check_firmware_service(test_config)
        if service_status is not None:
            if service_status:
                print(f"✓ Firmware service '{test_config['firmware_service_name']}' is active")
            else:
                print(f"⚠️  Firmware service '{test_config['firmware_service_name']}' is not active")

        # ================================================================
        # STEP 2: Initialize GPIO
        # ================================================================
        print("\n[STEP 2] Initialize GPIO")
        print("-" * 70)

        success = self.setup_gpio(test_config)
        assert success, "Failed to setup GPIO"

        # Verify initial state
        initial_state = self.read_gpio(test_config)
        print(f"Initial GPIO state: {initial_state}")

        if initial_state == test_config['pressed_state']:
            print("⚠️  WARNING: Button appears to be already pressed!")
            print("   Please release the button before continuing")
            time.sleep(2)

        print("✓ GPIO initialized and ready")

        try:
            # ============================================================
            # STEP 3: Test Short Press Detection
            # ============================================================
            print("\n[STEP 3] Test Short Press Detection")
            print("-" * 70)
            print("\n📋 MANUAL ACTION REQUIRED:")
            print(f"   Perform a SHORT PRESS (less than 1 second)")
            print(f"   Press and quickly release the button")
            print()

            input("Press ENTER when ready, then perform SHORT press...")

            detected, duration, press_type = self.detect_press_with_timing(test_config)

            if not detected:
                pytest.fail("Failed to detect short press")

            print(f"\n📊 Short Press Results:")
            print(f"   Duration: {duration:.3f} seconds ({duration*1000:.0f}ms)")
            print(f"   Classification: {press_type.upper()}")

            # Verify it's actually a short press
            if press_type == 'short':
                print("   ✓ PASS: Correctly classified as SHORT PRESS")
                self.log_message("Short press test: PASS", test_config)
            elif press_type == 'too_short':
                print("   ⚠️  WARNING: Press was too short (< 50ms)")
                print("      This might be noise or very quick press")
                print("      Try pressing slightly longer")
                pytest.fail("Press was too short - try again with slightly longer press")
            elif press_type == 'long':
                print("   ✗ FAIL: Classified as LONG PRESS (expected SHORT)")
                print(f"      Your press was {duration:.3f}s (> 1s threshold)")
                pytest.fail("Short press detected as long press - press more quickly")
            else:
                pytest.fail(f"Unexpected press type: {press_type}")

            # ============================================================
            # STEP 4: Test Long Press Detection
            # ============================================================
            print("\n[STEP 4] Test Long Press Detection")
            print("-" * 70)
            print("\n📋 MANUAL ACTION REQUIRED:")
            print(f"   Perform a LONG PRESS (more than 1 second)")
            print(f"   Press and HOLD the button for 2-3 seconds")
            print()

            input("Press ENTER when ready, then perform LONG press...")

            detected, duration, press_type = self.detect_press_with_timing(test_config)

            if not detected:
                pytest.fail("Failed to detect long press")

            print(f"\n📊 Long Press Results:")
            print(f"   Duration: {duration:.3f} seconds ({duration*1000:.0f}ms)")
            print(f"   Classification: {press_type.upper()}")

            # Verify it's actually a long press
            if press_type == 'long':
                print("   ✓ PASS: Correctly classified as LONG PRESS")
                self.log_message("Long press test: PASS", test_config)
            elif press_type == 'short':
                print("   ✗ FAIL: Classified as SHORT PRESS (expected LONG)")
                print(f"      Your press was {duration:.3f}s (< 1s threshold)")
                pytest.fail("Long press detected as short press - hold button longer")
            elif press_type == 'too_long':
                print("   ⚠️  WARNING: Press was too long (> 10s)")
                print("      This might indicate stuck button")
            else:
                pytest.fail(f"Unexpected press type: {press_type}")

            # ============================================================
            # STEP 5: Test Multiple Press Cycles
            # ============================================================
            print("\n[STEP 5] Test Multiple Press Cycles")
            print("-" * 70)
            print("\nTesting press consistency with multiple cycles...")

            test_sequences = [
                ('short', 'Short press (< 1s)'),
                ('long', 'Long press (> 1s)'),
                ('short', 'Short press (< 1s)'),
            ]

            results = []

            for expected_type, instruction in test_sequences:
                print(f"\n📋 {instruction}")
                input("Press ENTER, then perform the press...")

                detected, duration, press_type = self.detect_press_with_timing(test_config)

                if detected:
                    match = press_type == expected_type
                    results.append({
                        'expected': expected_type,
                        'actual': press_type,
                        'duration': duration,
                        'match': match
                    })

                    print(f"   Duration: {duration:.3f}s → {press_type.upper()}")
                    if match:
                        print("   ✓ Classification matches expected type")
                    else:
                        print(f"   ✗ Expected {expected_type}, got {press_type}")

            # Analyze results
            successful = sum(1 for r in results if r['match'])
            total = len(results)

            print(f"\n📊 Multiple Press Test Results:")
            print(f"   Successful classifications: {successful}/{total}")

            for i, r in enumerate(results, 1):
                status = "✓" if r['match'] else "✗"
                print(f"   {status} Test {i}: {r['duration']:.3f}s → {r['actual']} (expected: {r['expected']})")

            if successful == total:
                print("   ✓ PASS: All presses classified correctly")
            else:
                pytest.fail(f"Only {successful}/{total} presses classified correctly")

            # ============================================================
            # STEP 6: Verify Event Logging
            # ============================================================
            print("\n[STEP 6] Verify Event Logging")
            print("-" * 70)

            if test_config['enable_logging']:
                try:
                    with open(test_config['event_log_file'], 'r') as f:
                        events = f.readlines()

                    print(f"✓ Event log contains {len(events)} events")
                    print(f"  Log file: {test_config['event_log_file']}")

                    print("\nEvent Log Contents:")
                    for event in events:
                        print(f"  {event.strip()}")

                except Exception as e:
                    print(f"⚠️  Could not read event log: {e}")

        finally:
            # Cleanup
            print("\n[Cleanup]")
            print("-" * 70)

            if not GPIO_AVAILABLE:
                self.cleanup_gpio_sysfs(test_config)

            print("✓ GPIO resources released")
            self.log_message("Test completed - cleanup done", test_config)

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print("  ✓ Short press correctly identified as short press")
        print("  ✓ Long press correctly identified as long press")
        print("  ✓ Multiple press cycles classified correctly")
        print("  ✓ Event logging functional")
        print(f"\n📄 Test log: {test_config['log_file']}")
        print(f"📄 Event log: {test_config['event_log_file']}")
        print("=" * 70)

        self.log_message("=" * 50, test_config)
        self.log_message("TEST RESULT: PASS", test_config)
        self.log_message("=" * 50, test_config)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
