#!/usr/bin/env python3
"""
Test Case #17: SDRAM Memtester
Category: HW Component Test
Component: CM4 SDRAM + OS + memtester utility

Tests CM4 SDRAM integrity using the memtester utility, which performs
comprehensive memory testing including stuck address, random value,
and various comparison tests.

This test runs on the CM4 itself (not on PC via remote connection).
"""

import subprocess
import os
import sys
import time
import json
import re
import pytest

# Add common utilities to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
from platform_check import skip_if_not_raspberry_pi


class TestSDRAMMemtester:
    """HW Component Test - SDRAM Memtester"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for SDRAM memtester test"""
        return {
            # Memtester parameters
            'memory_size_mb': 100,  # Test 100 MB of RAM (adjust as needed)
            'iterations': 1,        # Number of test loops

            # Memtester path
            'memtester_path': 'memtester',  # Will search in PATH

            # Sudo requirement
            'require_sudo': True,   # memtester needs elevated privileges

            # Timeout
            'timeout_sec': 600,     # 10 minute timeout (100MB ~2min typical)

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_017_sdram_memtester.log',

            # JSONL results
            'results_file': '/tmp/test_017_sdram_memtester.jsonl',
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

    def check_memtester_installed(self, config):
        """
        Check if memtester utility is installed and accessible

        Returns: (installed, path, version_info)
        """
        self.log_message("Checking memtester installation...", config)

        try:
            # Check if memtester exists in PATH
            result = subprocess.run(
                ['which', config['memtester_path']],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.log_message(f"  ✗ memtester not found in PATH", config)
                return False, None, None

            memtester_path = result.stdout.strip()
            self.log_message(f"  ✓ memtester found: {memtester_path}", config)

            # Get version info
            try:
                version_result = subprocess.run(
                    ['memtester', '--help'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                # Extract version from output
                version_match = re.search(r'memtester version ([\d.]+)', version_result.stderr)
                if version_match:
                    version = version_match.group(1)
                    self.log_message(f"  ✓ Version: memtester version {version}", config)
                    return True, memtester_path, version
                else:
                    self.log_message(f"  ✓ Version: (unknown)", config)
                    return True, memtester_path, "unknown"

            except Exception as e:
                # Version check failed, but memtester exists
                self.log_message(f"  ⚠ Could not determine version: {e}", config)
                return True, memtester_path, "unknown"

        except Exception as e:
            self.log_message(f"  ✗ Error checking memtester: {e}", config)
            return False, None, None

    def check_sudo_available(self, config):
        """
        Check if sudo is available and accessible

        Returns: (available, can_run_passwordless)
        """
        try:
            # Check if sudo exists
            result = subprocess.run(
                ['which', 'sudo'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, False

            # Check if sudo works without password (non-blocking check)
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, True  # Passwordless sudo available
            else:
                return True, False  # sudo exists but needs password

        except Exception as e:
            return False, False

    def run_memtester(self, memory_size_mb, iterations, config):
        """
        Run memtester utility

        Returns: (success, exit_code, stdout, stderr, errors_detected)
        """
        size_str = f"{memory_size_mb}M"
        iterations_str = str(iterations)

        # Build command
        if config['require_sudo']:
            cmd = ['sudo', 'memtester', size_str, iterations_str]
            cmd_display = f"sudo memtester {size_str} {iterations_str}"
        else:
            cmd = ['memtester', size_str, iterations_str]
            cmd_display = f"memtester {size_str} {iterations_str}"

        self.log_message(f"Running memtester...", config)
        self.log_message(f"  Command: {cmd_display}", config)
        self.log_message(f"  Memory: {memory_size_mb} MB", config)
        self.log_message(f"  Iterations: {iterations}", config)
        self.log_message(f"  Timeout: {config['timeout_sec']} seconds", config)
        self.log_message("", config)
        self.log_message("  This may take several minutes, please wait...", config)

        try:
            start_time = time.time()

            # Run memtester
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config['timeout_sec']
            )

            elapsed_time = time.time() - start_time

            # memtester writes output to both stdout and stderr
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode

            # Combine output for parsing
            full_output = stdout + stderr

            self.log_message("", config)
            self.log_message(f"  Completed in {elapsed_time:.1f} seconds", config)
            self.log_message(f"  Exit code: {exit_code}", config)

            # Parse for errors
            errors_detected = self.parse_memtester_output(full_output, config)

            if exit_code == 0 and not errors_detected:
                success = True
            else:
                success = False

            return success, exit_code, stdout, stderr, errors_detected

        except subprocess.TimeoutExpired:
            self.log_message(f"  ✗ memtester timed out after {config['timeout_sec']} seconds", config)
            return False, -1, "", "Timeout", True

        except Exception as e:
            self.log_message(f"  ✗ Error running memtester: {e}", config)
            return False, -1, "", str(e), True

    def parse_memtester_output(self, output, config):
        """
        Parse memtester output to detect errors

        Returns: True if errors detected, False if all tests passed
        """
        # Look for failure patterns
        failure_patterns = [
            r'FAILURE',
            r'error',
            r'ERROR',
            r'failed',
            r'FAILED',
        ]

        # Look for success patterns
        success_pattern = r'Done\.'

        errors_found = []

        for pattern in failure_patterns:
            matches = re.findall(f'.*{pattern}.*', output, re.IGNORECASE)
            if matches:
                errors_found.extend(matches)

        if errors_found:
            self.log_message("  ✗ Errors detected in memtester output:", config)
            for error in errors_found[:5]:  # Show first 5 errors
                self.log_message(f"    {error.strip()}", config)
            if len(errors_found) > 5:
                self.log_message(f"    ... and {len(errors_found) - 5} more errors", config)
            return True

        # Check if test completed successfully
        if re.search(success_pattern, output):
            self.log_message("  ✓ memtester completed successfully", config)
            return False
        else:
            # Unexpected output - no "Done." and no explicit failures
            self.log_message("  ⚠ Unexpected memtester output (no 'Done.' marker)", config)
            return True  # Treat as error

    def save_results_jsonl(self, results, config):
        """Save test results to JSONL file"""
        try:
            results_file = config.get('results_file')
            if results_file:
                with open(results_file, 'w') as f:
                    f.write(json.dumps(results) + '\n')
                self.log_message(f"  ✓ Results saved to: {results_file}", config)
        except Exception as e:
            self.log_message(f"  ⚠ Could not save results: {e}", config)

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.memory
    @pytest.mark.quick
    def test_017_sdram_memtester(self, test_config):
        """
        Test Case #17: SDRAM Memtester

        Test Setup: CM4 with memtester utility installed
        Acceptance Criteria: memtester returns exit code 0 with no errors

        IMPORTANT: This test must run ON the CM4 itself.
        Use: ssh pi@$PI_IP "cd /path/to/repo && pytest tests/unit_tests/hw_component/test_017_sdram_memtester.py -v -s"

        What this test validates:
        - CM4 SDRAM integrity
        - No stuck bits or addressing errors
        - Memory controller functioning correctly
        - RAM suitable for production use

        Requirements:
        - memtester utility installed (sudo apt install memtester)
        - sudo access (memtester requires root privileges)
        """

        print("\n" + "=" * 70)
        print("Test Case #17: SDRAM Memtester")
        print("=" * 70)
        print("\nHW Component Test - CM4 SDRAM Integrity")
        print("=" * 70)
        print("\nTEST METHOD:")
        print("  1. Check memtester utility installed")
        print("  2. Run memtester with configured size/iterations")
        print("  3. Parse output for errors")
        print("  4. Verify exit code 0 and no errors detected")
        print("=" * 70)

        # CRITICAL: Skip test if not running on Raspberry Pi
        skip_if_not_raspberry_pi("SDRAM Memtester test")

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # Test results tracking
        test_results = {
            'type': 'test_result',
            'test_case': 'Test_017_SDRAM_Memtester',
            'timestamp': time.time(),
            'timestamp_str': time.strftime("%Y-%m-%d %H:%M:%S"),
            'memory_size_mb': test_config['memory_size_mb'],
            'iterations': test_config['iterations'],
        }

        try:
            # ================================================================
            # STEP 1: Check memtester Installation
            # ================================================================
            print("\n[STEP 1] Check memtester Installation")
            print("-" * 70)

            installed, memtester_path, version = self.check_memtester_installed(test_config)

            if not installed:
                # memtester not installed - provide instructions
                print()
                print("✗ memtester utility not found")
                print()
                print("To install memtester on CM4:")
                print(f"  ssh pi@$PI_IP 'sudo apt update && sudo apt install -y memtester'")
                print()
                print("Or on the CM4 directly:")
                print("  sudo apt update && sudo apt install -y memtester")

                test_results['result'] = 'SKIP'
                test_results['skip_reason'] = 'memtester utility not installed'

                pytest.skip(
                    "memtester utility not installed\n"
                    "\n"
                    "To install:\n"
                    "  sudo apt update && sudo apt install -y memtester\n"
                )

            print(f"✓ memtester found: {memtester_path}")
            if version != "unknown":
                print(f"✓ Version: {version}")

            test_results['memtester_path'] = memtester_path
            test_results['memtester_version'] = version

            # ================================================================
            # STEP 2: Check sudo Access
            # ================================================================
            print("\n[STEP 2] Check sudo Access")
            print("-" * 70)

            sudo_available, passwordless = self.check_sudo_available(test_config)

            if not sudo_available:
                self.log_message("✗ sudo not available", test_config)
                pytest.fail(
                    "sudo command not found\n"
                    "memtester requires root privileges to run"
                )

            if passwordless:
                print("✓ sudo available (passwordless)")
                self.log_message("sudo available (passwordless)", test_config)
            else:
                print("⚠ sudo available but may require password")
                print("  If test hangs, configure passwordless sudo:")
                print("  echo 'pi ALL=(ALL) NOPASSWD: /usr/bin/memtester' | sudo tee /etc/sudoers.d/memtester")
                self.log_message("sudo available (may require password)", test_config)

            # ================================================================
            # STEP 3: Run memtester
            # ================================================================
            print("\n[STEP 3] Run memtester")
            print("-" * 70)
            print(f"Testing {test_config['memory_size_mb']} MB of RAM × {test_config['iterations']} iteration(s)")
            print("This may take several minutes...")
            print()

            success, exit_code, stdout, stderr, errors_detected = self.run_memtester(
                test_config['memory_size_mb'],
                test_config['iterations'],
                test_config
            )

            # Store output in results
            test_results['exit_code'] = exit_code
            test_results['errors_detected'] = errors_detected

            # ================================================================
            # STEP 4: Evaluate Results
            # ================================================================
            print("\n[STEP 4] Evaluate Results")
            print("-" * 70)

            if success:
                print(f"✓ memtester exit code: {exit_code} (success)")
                print(f"✓ No errors detected")
                print(f"✓ All memory tests passed")

                test_results['result'] = 'PASS'
                test_results['pass_reason'] = 'memtester completed with exit code 0, no errors detected'

            else:
                print(f"✗ memtester exit code: {exit_code}")

                if errors_detected:
                    print(f"✗ Memory errors detected!")

                    test_results['result'] = 'FAIL'
                    test_results['fail_reason'] = f'memtester detected errors (exit code: {exit_code})'

                    # Show portion of output
                    print()
                    print("memtester output (last 20 lines):")
                    print("-" * 70)
                    combined_output = stdout + stderr
                    lines = combined_output.split('\n')
                    for line in lines[-20:]:
                        if line.strip():
                            print(f"  {line}")
                    print("-" * 70)

                    pytest.fail(
                        f"SDRAM errors detected by memtester!\n"
                        f"  Exit code: {exit_code}\n"
                        f"  Errors found: Yes\n"
                        "\n"
                        "This indicates:\n"
                        "  - Defective RAM chip\n"
                        "  - Bad solder joints\n"
                        "  - Memory controller issues\n"
                        "  - Hardware failure requiring replacement\n"
                        "\n"
                        "Recommendations:\n"
                        "  - Replace CM4 module\n"
                        "  - Check for physical damage\n"
                        "  - Test with known-good CM4\n"
                        "  - Review manufacturing quality"
                    )

                else:
                    # Non-zero exit but no explicit errors (timeout, crash, etc.)
                    print(f"✗ memtester failed (non-zero exit code)")

                    test_results['result'] = 'FAIL'
                    test_results['fail_reason'] = f'memtester failed with exit code {exit_code}'

                    pytest.fail(
                        f"memtester failed with exit code {exit_code}\n"
                        "Check logs for details"
                    )

        finally:
            # Save results
            pass

        # ================================================================
        # Save Results to JSONL
        # ================================================================
        self.save_results_jsonl(test_results, test_config)

        # ================================================================
        # Test Result Summary
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ memtester installed: {test_results.get('memtester_path')}")
        if test_results.get('memtester_version') != "unknown":
            print(f"  ✓ memtester version: {test_results.get('memtester_version')}")
        print(f"  ✓ Memory tested: {test_config['memory_size_mb']} MB")
        print(f"  ✓ Iterations: {test_config['iterations']}")
        print(f"  ✓ Exit code: {test_results['exit_code']} (success)")
        print(f"  ✓ No errors detected")
        print(f"  ✓ CM4 SDRAM validated (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        if test_config.get('results_file'):
            print(f"📄 Results: {test_config['results_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
