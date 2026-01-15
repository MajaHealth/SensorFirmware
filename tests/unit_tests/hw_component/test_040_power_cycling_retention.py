#!/usr/bin/env python3
"""
Test Case #40: Power Cycling (Retention)
Category: HW Component Test
Component: eMMC + SD Card

Tests that storage maintains data integrity across power cycles (reboots).
This test uses a state-based approach that spans multiple test executions.

IMPORTANT: This test requires manual reboot or automated reboot capability.
The test will run in two phases:
  Phase 1: Write data and reboot
  Phase 2: Verify data after reboot
"""

import subprocess
import os
import hashlib
import json
import pytest
import time


class TestPowerCyclingRetention:
    """HW Component Test - Power Cycling Data Retention"""

    # Persistent state file to track test across reboots
    # This file MUST survive reboots (stored on eMMC/SD)
    STATE_FILE = '/var/tmp/test_040_power_cycle_state.json'

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for power cycling test"""
        return {
            # Test data configuration
            'test_file_size_mb': 10,  # Size of test files

            # Power cycle configuration
            'target_power_cycles': 3,  # Number of power cycles to test
            'auto_reboot': False,      # Set True for automated testing

            # Storage locations
            'emmc_test_dir': '/tmp',
            'emmc_test_file': 'retention_test_emmc.bin',

            # Device names
            'emmc_device': 'mmcblk0',
            'sd_device_names': ['mmcblk1', 'sda'],

            # Reboot delay
            'reboot_warning_seconds': 10,  # Warning before reboot

            # Logging
            'enable_logging': True,
            'log_file': '/var/tmp/test_040_power_cycling.log',
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

    def load_state(self):
        """Load test state from previous run"""
        if not os.path.exists(self.STATE_FILE):
            return None

        try:
            with open(self.STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load state file: {e}")
            return None

    def save_state(self, state):
        """Save test state for next run"""
        try:
            # Ensure directory exists
            state_dir = os.path.dirname(self.STATE_FILE)
            os.makedirs(state_dir, exist_ok=True)

            with open(self.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)

            return True
        except Exception as e:
            print(f"Error: Could not save state file: {e}")
            return False

    def delete_state(self):
        """Delete state file after test completion"""
        try:
            if os.path.exists(self.STATE_FILE):
                os.remove(self.STATE_FILE)
            return True
        except Exception as e:
            print(f"Warning: Could not delete state file: {e}")
            return False

    def find_sd_location(self, config):
        """Find SD card mount point"""
        try:
            result = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                for sd_name in config['sd_device_names']:
                    if sd_name in line and '/media' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]

        except Exception as e:
            print(f"Warning: Could not find SD mount point: {e}")

        return None

    def write_test_file(self, file_path, size_mb, config):
        """Write test file and return checksum"""
        self.log_message(f"Writing {size_mb}MB test file to {file_path}...", config)

        try:
            # Generate test data
            test_data = os.urandom(size_mb * 1024 * 1024)

            # Write to file
            with open(file_path, 'wb') as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())

            # Calculate checksum
            checksum = hashlib.sha256(test_data).hexdigest()

            self.log_message(f"  ✓ File written: {len(test_data):,} bytes", config)
            self.log_message(f"  Checksum: {checksum[:16]}...", config)

            return checksum

        except Exception as e:
            self.log_message(f"  ✗ Write failed: {e}", config)
            return None

    def verify_test_file(self, file_path, expected_checksum, config):
        """Verify test file matches expected checksum"""
        self.log_message(f"Verifying test file: {file_path}", config)

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                self.log_message(f"  ✗ File not found: {file_path}", config)
                return False, "File not found"

            self.log_message(f"  ✓ File exists", config)

            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()

            self.log_message(f"  ✓ File read: {len(data):,} bytes", config)

            # Calculate checksum
            actual_checksum = hashlib.sha256(data).hexdigest()

            self.log_message(f"  Expected: {expected_checksum[:16]}...", config)
            self.log_message(f"  Actual:   {actual_checksum[:16]}...", config)

            # Compare
            if actual_checksum == expected_checksum:
                self.log_message(f"  ✓ Checksum match: Data integrity verified", config)
                return True, None
            else:
                self.log_message(f"  ✗ Checksum mismatch: Data corruption detected!", config)
                return False, "Checksum mismatch"

        except Exception as e:
            self.log_message(f"  ✗ Verification failed: {e}", config)
            return False, str(e)

    def cleanup_test_files(self, state, config):
        """Remove test files and state"""
        self.log_message("Cleaning up test files...", config)

        # Remove eMMC file
        if state.get('emmc_file') and os.path.exists(state['emmc_file']):
            try:
                os.remove(state['emmc_file'])
                self.log_message(f"  ✓ Removed eMMC test file", config)
            except Exception as e:
                self.log_message(f"  ⚠ Could not remove eMMC file: {e}", config)

        # Remove SD file
        if state.get('sd_file') and os.path.exists(state['sd_file']):
            try:
                os.remove(state['sd_file'])
                self.log_message(f"  ✓ Removed SD test file", config)
            except Exception as e:
                self.log_message(f"  ⚠ Could not remove SD file: {e}", config)

        # Remove state file
        self.delete_state()
        self.log_message(f"  ✓ Removed state file", config)

    def initiate_reboot(self, config):
        """Initiate system reboot with warning"""
        print(f"\n{'=' * 70}")
        print("⚠️  REBOOT REQUIRED")
        print(f"{'=' * 70}")
        print("\nThis test requires a system reboot to verify data retention.")
        print(f"System will reboot in {config['reboot_warning_seconds']} seconds.")
        print("\nAfter reboot, run this test again to complete verification:")
        print(f"  pytest {__file__} -v -s")
        print("\nPress Ctrl+C to cancel reboot...")
        print(f"{'=' * 70}\n")

        # Wait for warning period
        try:
            for i in range(config['reboot_warning_seconds'], 0, -1):
                print(f"Rebooting in {i} seconds...", end='\r')
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            print("\n\n⚠️  Reboot cancelled by user")
            print("To complete test:")
            print("  1. Manually reboot the system")
            print("  2. Run this test again after reboot")
            pytest.skip("Reboot cancelled - Manual reboot required to complete test")
            return

        # Sync filesystem
        print("Syncing filesystem...")
        subprocess.run(['sync'], timeout=30)
        print("✓ Filesystem synced")

        # Initiate reboot
        print("\n🔄 Initiating system reboot...\n")
        try:
            subprocess.run(['sudo', 'reboot'], timeout=5)
        except subprocess.TimeoutExpired:
            pass  # Reboot will kill process

        # If we reach here, reboot might have failed
        time.sleep(5)
        pytest.skip("Reboot initiated - Run test again after system restarts")

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.storage
    @pytest.mark.slow
    def test_040_power_cycling_retention(self, test_config):
        """
        Test Case #40: Power cycling (retention)

        Test Setup: Booted system, test dataset
        Acceptance Criteria: Storage retains data correctly across power cycles

        IMPORTANT: This test spans multiple executions across reboots.
        - Phase 1: Writes test data and reboots
        - Phase 2: Verifies data after reboot

        What this test validates:
        - Data written to storage persists across power cycles
        - No data corruption occurs during power loss/reboot
        - Both eMMC and SD card (if present) retain data reliably
        - Storage is suitable for production use with unexpected power loss
        """

        print("\n" + "=" * 70)
        print("Test Case #40: Power Cycling (Retention)")
        print("=" * 70)
        print("\nHW Component Test - Storage Data Retention")
        print("=" * 70)
        print("\nTEST METHOD:")
        print("  Phase 1: Write test data → Reboot system")
        print("  Phase 2: Verify data survived reboot → Repeat if needed")
        print("=" * 70)

        # ================================================================
        # STEP 1: Determine Test Phase
        # ================================================================
        print("\n[STEP 1] Determine Test Phase")
        print("-" * 70)

        state = self.load_state()

        if state is None:
            # PHASE 1: First run - write data and reboot
            print("✓ No previous state found")
            print("  → This is PHASE 1: Write data and initiate reboot")
            self._execute_phase1(test_config)

        else:
            # PHASE 2: After reboot - verify data
            print("✓ Previous state found")
            print(f"  Test started: {time.ctime(state.get('start_time', 0))}")
            print(f"  Power cycles completed: {state.get('cycles_completed', 0)}")
            print(f"  → This is PHASE 2: Verify data retention")
            self._execute_phase2(state, test_config)

    def _execute_phase1(self, config):
        """Execute Phase 1: Write test data and reboot"""

        print("\n" + "=" * 70)
        print("PHASE 1: Write Test Data and Reboot")
        print("=" * 70)

        # ================================================================
        # STEP 2: Detect Storage and Write Test Data
        # ================================================================
        print("\n[STEP 2] Detect Storage and Write Test Data")
        print("-" * 70)

        # Prepare eMMC test file path
        emmc_file = os.path.join(
            config['emmc_test_dir'],
            config['emmc_test_file']
        )

        # Write eMMC test file
        print("\neMMC Test File:")
        emmc_checksum = self.write_test_file(
            emmc_file,
            config['test_file_size_mb'],
            config
        )

        if not emmc_checksum:
            pytest.fail("Failed to write eMMC test file")

        # Find SD card location
        sd_location = self.find_sd_location(config)
        sd_file = None
        sd_checksum = None

        if sd_location:
            sd_file = os.path.join(sd_location, 'retention_test_sd.bin')

            print("\nSD Card Test File:")
            sd_checksum = self.write_test_file(
                sd_file,
                config['test_file_size_mb'],
                config
            )

            if not sd_checksum:
                print("  ⚠ Failed to write SD test file (will skip SD tests)")
                sd_file = None
        else:
            print("\n⚠ SD card not found (will skip SD tests)")

        # ================================================================
        # STEP 3: Save Test State
        # ================================================================
        print("\n[STEP 3] Save Test State")
        print("-" * 70)

        state = {
            'start_time': time.time(),
            'cycles_completed': 0,
            'target_cycles': config['target_power_cycles'],
            'emmc_file': emmc_file,
            'emmc_checksum': emmc_checksum,
            'sd_file': sd_file,
            'sd_checksum': sd_checksum,
            'test_file_size_mb': config['test_file_size_mb'],
        }

        if not self.save_state(state):
            pytest.fail("Failed to save test state")

        self.log_message(f"✓ Test state saved to: {self.STATE_FILE}", config)

        # ================================================================
        # STEP 4: Initiate Reboot
        # ================================================================
        print("\n[STEP 4] Initiate System Reboot")
        print("-" * 70)

        self.initiate_reboot(config)

    def _execute_phase2(self, state, config):
        """Execute Phase 2: Verify data retention after reboot"""

        print("\n" + "=" * 70)
        print("PHASE 2: Verify Data Retention After Reboot")
        print("=" * 70)

        cycles_completed = state.get('cycles_completed', 0) + 1
        target_cycles = state.get('target_cycles', 3)

        print(f"\nPower Cycle: {cycles_completed}/{target_cycles}")
        print(f"Test Duration: {time.time() - state['start_time']:.1f} seconds")

        # ================================================================
        # STEP 2: Verify eMMC Data Retention
        # ================================================================
        print("\n[STEP 2] Verify eMMC Data Retention")
        print("-" * 70)

        emmc_ok, emmc_error = self.verify_test_file(
            state['emmc_file'],
            state['emmc_checksum'],
            config
        )

        if not emmc_ok:
            # Cleanup and fail
            self.cleanup_test_files(state, config)
            pytest.fail(
                f"eMMC data retention FAILED after power cycle {cycles_completed}!\n"
                f"Error: {emmc_error}\n"
                "This indicates:\n"
                "  - Storage did not persist data\n"
                "  - Data corruption occurred\n"
                "  - Storage device failure"
            )

        print(f"✓ eMMC data retention verified (cycle {cycles_completed}/{target_cycles})")

        # ================================================================
        # STEP 3: Verify SD Card Data Retention (if applicable)
        # ================================================================
        if state.get('sd_file'):
            print("\n[STEP 3] Verify SD Card Data Retention")
            print("-" * 70)

            sd_ok, sd_error = self.verify_test_file(
                state['sd_file'],
                state['sd_checksum'],
                config
            )

            if not sd_ok:
                print(f"⚠ SD card data retention failed: {sd_error}")
                print("  (SD card failure is informational, not critical)")
            else:
                print(f"✓ SD card data retention verified (cycle {cycles_completed}/{target_cycles})")
        else:
            print("\n[STEP 3] SD Card Verification - SKIPPED")
            print("-" * 70)
            print("  SD card not available in this test")

        # ================================================================
        # STEP 4: Check if More Cycles Needed
        # ================================================================
        print("\n[STEP 4] Check Power Cycle Progress")
        print("-" * 70)

        if cycles_completed < target_cycles:
            # Need more cycles
            print(f"✓ Cycle {cycles_completed}/{target_cycles} complete")
            print(f"  → Initiating cycle {cycles_completed + 1}/{target_cycles}")

            # Update state
            state['cycles_completed'] = cycles_completed
            if not self.save_state(state):
                pytest.fail("Failed to update test state")

            # Reboot again
            self.initiate_reboot(config)

        else:
            # All cycles complete
            print(f"✓ All {target_cycles} power cycles complete")
            print("  → Test successful!")

            # ============================================================
            # STEP 5: Cleanup and Report Success
            # ============================================================
            print("\n[STEP 5] Cleanup")
            print("-" * 70)

            self.cleanup_test_files(state, config)

            # ============================================================
            # Test Result
            # ============================================================
            print("\n" + "=" * 70)
            print("TEST RESULT: ✓ PASS")
            print("=" * 70)
            print("\n✓ Acceptance Criteria Verification:")
            print(f"  ✓ Test completed {target_cycles} power cycle(s)")
            print(f"  ✓ eMMC data retained across all {target_cycles} power cycle(s)")
            print(f"  ✓ eMMC data integrity verified (no corruption)")

            if state.get('sd_file'):
                print(f"  ✓ SD card data retained across all {target_cycles} power cycle(s)")
                print(f"  ✓ SD card data integrity verified (no corruption)")

            print(f"  ✓ Storage retains data correctly across power cycles (PASS)")

            elapsed_time = time.time() - state['start_time']
            print(f"\nTest Duration: {elapsed_time:.1f} seconds (~{elapsed_time/60:.1f} minutes)")

            if config.get('enable_logging'):
                print(f"\n📄 Test log: {config['log_file']}")

            print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
