#!/usr/bin/env python3
"""
Test Case #102: Switch State Readback (OFF/ON)
Category: FW Hardware-in-Loop Test
Component: Contact-based switch + CM4 GPIO + Firmware

Tests contact-based switch connected to CM4 GPIO for proper state reading.
Validates OFF and ON state detection with debouncing.

This test requires manual switch operation (semi-automated).
"""

import subprocess
import time
import pytest
import platform
import os

# Try to import RPi.GPIO (only available on Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - will use alternative methods")


class TestSwitchStateReadback:
    """FW Hardware-in-Loop Test - Switch State Readback"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for switch state test"""
        return {
            # GPIO Configuration
            'switch_gpio_pin': 17,  # BCM GPIO 17 (Physical pin 11)
            'gpio_mode': 'BCM',     # BCM or BOARD numbering

            # Pull resistor configuration
            'pull_resistor': 'PULL_UP',  # PULL_UP or PULL_DOWN
            # PULL_UP: Switch connects to GND when pressed (active LOW)
            # PULL_DOWN: Switch connects to 3.3V when pressed (active HIGH)

            # Expected states
            'switch_off_expected': 1,  # Expected GPIO value when switch is OFF
            'switch_on_expected': 0,   # Expected GPIO value when switch is ON
            # Note: These values depend on pull resistor configuration
            # PULL_UP: OFF=HIGH(1), ON=LOW(0)
            # PULL_DOWN: OFF=LOW(0), ON=HIGH(1)

            # Timing
            'debounce_time': 0.05,     # 50ms debounce delay
            'read_samples': 3,         # Number of samples to read
            'sample_interval': 0.02,   # 20ms between samples

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_102_switch_state_readback.log',
        }

    def setup_method(self):
        """Setup before each test method"""
        if GPIO_AVAILABLE:
            # Clean up any previous GPIO setup
            GPIO.setwarnings(False)
            GPIO.cleanup()

    def teardown_method(self):
        """Cleanup after each test method"""
        if GPIO_AVAILABLE:
            GPIO.cleanup()

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

    def setup_gpio_rpi(self, config):
        """
        Setup GPIO using RPi.GPIO library
        Returns: bool (success)
        """
        try:
            # Set GPIO mode
            if config['gpio_mode'] == 'BCM':
                GPIO.setmode(GPIO.BCM)
            else:
                GPIO.setmode(GPIO.BOARD)

            # Configure pull resistor
            if config['pull_resistor'] == 'PULL_UP':
                pull_mode = GPIO.PUD_UP
            elif config['pull_resistor'] == 'PULL_DOWN':
                pull_mode = GPIO.PUD_DOWN
            else:
                pull_mode = GPIO.PUD_OFF

            # Setup pin as input with pull resistor
            GPIO.setup(config['switch_gpio_pin'], GPIO.IN, pull_up_down=pull_mode)

            self.log_message(
                f"✓ GPIO {config['switch_gpio_pin']} configured as input "
                f"with {config['pull_resistor']}",
                config
            )

            return True

        except Exception as e:
            self.log_message(f"✗ GPIO setup failed: {e}", config)
            return False

    def read_gpio_rpi(self, config):
        """
        Read GPIO state using RPi.GPIO
        Returns: int (0 or 1) or None on error
        """
        try:
            state = GPIO.input(config['switch_gpio_pin'])
            return state
        except Exception as e:
            self.log_message(f"✗ GPIO read failed: {e}", config)
            return None

    def setup_gpio_sysfs(self, config):
        """
        Setup GPIO using sysfs (fallback method)
        Returns: bool (success)
        """
        gpio_pin = config['switch_gpio_pin']

        try:
            # Export GPIO if not already exported
            if not os.path.exists(f'/sys/class/gpio/gpio{gpio_pin}'):
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(gpio_pin))
                time.sleep(0.1)  # Wait for export

            # Set direction to input
            with open(f'/sys/class/gpio/gpio{gpio_pin}/direction', 'w') as f:
                f.write('in')

            self.log_message(
                f"✓ GPIO {gpio_pin} configured via sysfs",
                config
            )

            return True

        except Exception as e:
            self.log_message(f"✗ GPIO sysfs setup failed: {e}", config)
            return False

    def read_gpio_sysfs(self, config):
        """
        Read GPIO state using sysfs
        Returns: int (0 or 1) or None on error
        """
        gpio_pin = config['switch_gpio_pin']

        try:
            with open(f'/sys/class/gpio/gpio{gpio_pin}/value', 'r') as f:
                value = int(f.read().strip())
            return value
        except Exception as e:
            self.log_message(f"✗ GPIO sysfs read failed: {e}", config)
            return None

    def cleanup_gpio_sysfs(self, config):
        """Cleanup GPIO sysfs"""
        gpio_pin = config['switch_gpio_pin']
        try:
            if os.path.exists(f'/sys/class/gpio/gpio{gpio_pin}'):
                with open('/sys/class/gpio/unexport', 'w') as f:
                    f.write(str(gpio_pin))
        except:
            pass

    def read_gpio_stable(self, config, read_func):
        """
        Read GPIO multiple times to ensure stable reading
        Returns: int (most common value) or None
        """
        readings = []

        for i in range(config['read_samples']):
            value = read_func(config)
            if value is not None:
                readings.append(value)

            if i < config['read_samples'] - 1:
                time.sleep(config['sample_interval'])

        if not readings:
            return None

        # Return most common value (debounced)
        return max(set(readings), key=readings.count)

    def wait_for_user_input(self, prompt, timeout=60):
        """
        Wait for user to press Enter with timeout
        Returns: bool (True if user pressed Enter, False if timeout)
        """
        print(f"\n{prompt}")
        print(f"Press ENTER when ready (timeout: {timeout}s)...")

        try:
            # Use select on Linux for timeout
            if platform.system() == 'Linux':
                import select
                import sys
                i, o, e = select.select([sys.stdin], [], [], timeout)
                if i:
                    input()
                    return True
                else:
                    print("\n⏱️  Timeout waiting for user input")
                    return False
            else:
                # Simple input on other platforms
                input()
                return True

        except Exception as e:
            print(f"Error waiting for input: {e}")
            return False

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.gpio
    @pytest.mark.cm4
    def test_102_switch_state_readback(self, test_config):
        """
        Test Case #102: Switch state readback (OFF/ON)

        Test Setup: DUT with contact-based switch wired to CM4 GPIO; logging enabled
        Acceptance Criteria:
        - GPIO reads OFF when switch is OFF
        - GPIO reads ON when switch is ON

        IMPORTANT: This test requires manual switch operation.
        Test is semi-automated - requires physical interaction with hardware.

        What this test validates:
        - GPIO input configuration
        - Switch OFF state detection (HIGH with pull-up)
        - Switch ON state detection (LOW with pull-up)
        - State transition reliability
        - Debounced readings (no false states)
        - GPIO resource management
        """

        print("\n" + "=" * 70)
        print("Test Case #102: Switch State Readback (OFF/ON)")
        print("=" * 70)
        print("\nFW Hardware-in-Loop Test")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify contact-based switch state can be read via GPIO")
        print("\nHARDWARE REQUIRED:")
        print(f"  - Switch connected to GPIO {test_config['switch_gpio_pin']}")
        print(f"  - Pull resistor: {test_config['pull_resistor']}")
        print("\nWIRING (Pull-up configuration):")
        print("  CM4 GPIO Pin ----[Pull-up]---- 3.3V")
        print("       |")
        print("   [Switch]")
        print("       |")
        print("      GND")
        print("\n  Switch OFF (OPEN):   GPIO reads HIGH (1)")
        print("  Switch ON (CLOSED):  GPIO reads LOW (0)")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 1: Check Prerequisites
        # ================================================================
        print("\n[STEP 1] Check Prerequisites")
        print("-" * 70)
        self.log_message("Starting switch state readback test", test_config)

        # Check OS
        if platform.system() != "Linux":
            pytest.skip(
                f"Test must run on Linux (Raspberry Pi). "
                f"Current OS: {platform.system()}"
            )

        print(f"✓ Running on Linux")
        self.log_message(f"Platform: {platform.system()}", test_config)

        # Check if we're on Raspberry Pi
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                print(f"✓ Device: {model.strip()}")
                self.log_message(f"Device: {model.strip()}", test_config)
        except:
            print("⚠️  Could not verify Raspberry Pi model")

        # Determine GPIO method to use
        use_rpi_gpio = GPIO_AVAILABLE

        if use_rpi_gpio:
            print("✓ Using RPi.GPIO library")
            setup_func = self.setup_gpio_rpi
            read_func = self.read_gpio_rpi
        else:
            print("✓ Using sysfs GPIO method (fallback)")
            setup_func = self.setup_gpio_sysfs
            read_func = self.read_gpio_sysfs

        # ================================================================
        # STEP 2: Initialize GPIO
        # ================================================================
        print("\n[STEP 2] Initialize GPIO")
        print("-" * 70)
        print(f"Configuring GPIO {test_config['switch_gpio_pin']} as input...")
        print(f"Pull resistor: {test_config['pull_resistor']}")
        print(f"GPIO numbering: {test_config['gpio_mode']}")

        success = setup_func(test_config)
        assert success, "Failed to setup GPIO"

        # Initial GPIO read to verify setup
        time.sleep(0.1)
        initial_state = read_func(test_config)

        if initial_state is not None:
            print(f"✓ GPIO initialized successfully")
            print(f"  Initial GPIO state: {initial_state}")
            self.log_message(f"Initial GPIO state: {initial_state}", test_config)
        else:
            pytest.fail("Failed to read initial GPIO state")

        try:
            # ============================================================
            # STEP 3: Test Switch OFF State
            # ============================================================
            print("\n[STEP 3] Test Switch OFF State")
            print("-" * 70)
            print("\n📋 MANUAL ACTION REQUIRED:")
            print(f"   Please ensure the switch is in the OFF position")
            print(f"   (Expected GPIO value: {test_config['switch_off_expected']})")

            if not self.wait_for_user_input("Ready to read switch OFF state?"):
                pytest.skip("User did not confirm within timeout")

            # Wait for debounce
            time.sleep(test_config['debounce_time'])

            # Read GPIO state multiple times
            print(f"\nReading GPIO state {test_config['read_samples']} times...")
            switch_off_state = self.read_gpio_stable(test_config, read_func)

            if switch_off_state is None:
                pytest.fail("Failed to read GPIO state for switch OFF")

            print(f"GPIO reading (switch OFF): {switch_off_state}")
            self.log_message(
                f"Switch OFF - GPIO state: {switch_off_state}",
                test_config
            )

            # Verify expected state
            if switch_off_state == test_config['switch_off_expected']:
                print(f"✓ PASS: GPIO correctly reads {switch_off_state} when switch is OFF")
                self.log_message("Switch OFF state: VERIFIED", test_config)
            else:
                error_msg = (
                    f"GPIO state mismatch for switch OFF!\n"
                    f"  Expected: {test_config['switch_off_expected']}\n"
                    f"  Actual: {switch_off_state}\n"
                    f"  Check: Pull resistor configuration, switch wiring"
                )
                self.log_message(f"ERROR: {error_msg}", test_config)
                pytest.fail(error_msg)

            # ============================================================
            # STEP 4: Test Switch ON State
            # ============================================================
            print("\n[STEP 4] Test Switch ON State")
            print("-" * 70)
            print("\n📋 MANUAL ACTION REQUIRED:")
            print(f"   Please set the switch to the ON position")
            print(f"   (Expected GPIO value: {test_config['switch_on_expected']})")

            if not self.wait_for_user_input("Ready to read switch ON state?"):
                pytest.skip("User did not confirm within timeout")

            # Wait for debounce
            time.sleep(test_config['debounce_time'])

            # Read GPIO state multiple times
            print(f"\nReading GPIO state {test_config['read_samples']} times...")
            switch_on_state = self.read_gpio_stable(test_config, read_func)

            if switch_on_state is None:
                pytest.fail("Failed to read GPIO state for switch ON")

            print(f"GPIO reading (switch ON): {switch_on_state}")
            self.log_message(
                f"Switch ON - GPIO state: {switch_on_state}",
                test_config
            )

            # Verify expected state
            if switch_on_state == test_config['switch_on_expected']:
                print(f"✓ PASS: GPIO correctly reads {switch_on_state} when switch is ON")
                self.log_message("Switch ON state: VERIFIED", test_config)
            else:
                error_msg = (
                    f"GPIO state mismatch for switch ON!\n"
                    f"  Expected: {test_config['switch_on_expected']}\n"
                    f"  Actual: {switch_on_state}\n"
                    f"  Check: Pull resistor configuration, switch wiring"
                )
                self.log_message(f"ERROR: {error_msg}", test_config)
                pytest.fail(error_msg)

            # ============================================================
            # STEP 5: Test State Transition Reliability
            # ============================================================
            print("\n[STEP 5] Test State Transition Reliability")
            print("-" * 70)
            print("\nTesting state transitions: OFF → ON → OFF")

            transitions = [
                ('OFF', test_config['switch_off_expected']),
                ('ON', test_config['switch_on_expected']),
                ('OFF', test_config['switch_off_expected']),
            ]

            for position, expected_value in transitions:
                print(f"\n📋 Set switch to {position} position")
                if not self.wait_for_user_input(f"Ready?", timeout=30):
                    pytest.skip("User did not confirm within timeout")

                time.sleep(test_config['debounce_time'])
                state = self.read_gpio_stable(test_config, read_func)

                print(f"  GPIO reading: {state} (expected: {expected_value})")

                if state == expected_value:
                    print(f"  ✓ Transition to {position}: VERIFIED")
                    self.log_message(
                        f"Transition to {position}: GPIO={state} (OK)",
                        test_config
                    )
                else:
                    error_msg = f"State transition failed: {position}"
                    self.log_message(f"ERROR: {error_msg}", test_config)
                    pytest.fail(error_msg)

            print("\n✓ All state transitions verified successfully")

        finally:
            # ============================================================
            # STEP 6: Cleanup
            # ============================================================
            print("\n[STEP 6] Cleanup")
            print("-" * 70)

            if not use_rpi_gpio:
                self.cleanup_gpio_sysfs(test_config)

            print("✓ GPIO resources released")
            self.log_message("Test completed - GPIO cleaned up", test_config)

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ GPIO {test_config['switch_gpio_pin']} initialized successfully")
        print(f"  ✓ GPIO reads {test_config['switch_off_expected']} when switch is OFF")
        print(f"  ✓ GPIO reads {test_config['switch_on_expected']} when switch is ON")
        print("  ✓ State transitions are reliable")
        print("  ✓ No false readings detected")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)

        self.log_message("=" * 50, test_config)
        self.log_message("TEST RESULT: PASS", test_config)
        self.log_message("=" * 50, test_config)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
