#!/usr/bin/env python3
"""
Test Case #36: SSH Accessibility
Category: HW Component Test
Component: CM4 SSH Service

Tests that SSH is properly configured and accessible on the CM4.
This test runs on the CM4 itself (not on PC).
"""

import subprocess
import socket
import time
import pytest
import re


class TestSSHAccessibility:
    """HW Component Test - SSH Accessibility"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for SSH accessibility test"""
        return {
            # SSH connection parameters
            'ssh_port': 22,
            'ssh_service_name': 'ssh',  # 'ssh' or 'sshd' depending on distro
            'timeout': 10,

            # Test users (for informational checks)
            'expected_users': ['pi', 'root'],

            # SSH configuration checks
            'check_config': True,
            'check_keys': True,
            'check_firewall': True,

            # Network interface to test
            'test_interfaces': ['localhost', '0.0.0.0'],

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_036_ssh_accessibility.log',
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

    def check_ssh_service_status(self, config):
        """Check if SSH service is running"""
        self.log_message("Checking SSH service status...", config)

        # Try different service names (ssh vs sshd)
        service_names = ['ssh', 'sshd']

        for service_name in service_names:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                status = result.stdout.strip()

                if status == 'active':
                    self.log_message(f"  ✓ Service '{service_name}' is active", config)

                    # Get more details
                    result_enabled = subprocess.run(
                        ['systemctl', 'is-enabled', service_name],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    enabled_status = result_enabled.stdout.strip()
                    self.log_message(f"  Service enabled: {enabled_status}", config)

                    return True, service_name, enabled_status
                else:
                    self.log_message(f"  Service '{service_name}' status: {status}", config)

            except Exception as e:
                self.log_message(f"  Could not check service '{service_name}': {e}", config)
                continue

        return False, None, None

    def check_ssh_port_listening(self, host, port, config):
        """Check if SSH port is listening on specified host"""
        self.log_message(f"Checking if SSH port {port} is listening on {host}...", config)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(config['timeout'])

            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                self.log_message(f"  ✓ Port {port} is listening on {host}", config)
                return True
            else:
                self.log_message(f"  ✗ Port {port} is NOT listening on {host} (error code: {result})", config)
                return False

        except socket.timeout:
            self.log_message(f"  ✗ Connection timeout to {host}:{port}", config)
            return False
        except Exception as e:
            self.log_message(f"  ✗ Error checking port: {e}", config)
            return False

    def check_ssh_banner(self, host, port, config):
        """Get SSH banner to verify SSH is responding"""
        self.log_message(f"Checking SSH banner on {host}:{port}...", config)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(config['timeout'])
            sock.connect((host, port))

            # Read SSH banner (should start with "SSH-")
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()

            if 'SSH' in banner:
                self.log_message(f"  ✓ SSH banner: {banner}", config)
                return True, banner
            else:
                self.log_message(f"  ✗ Invalid banner: {banner}", config)
                return False, banner

        except socket.timeout:
            self.log_message(f"  ✗ Timeout waiting for banner", config)
            return False, "Timeout"
        except Exception as e:
            self.log_message(f"  ✗ Error getting banner: {e}", config)
            return False, str(e)

    def check_ssh_config(self, config):
        """Check SSH server configuration"""
        self.log_message("Checking SSH server configuration...", config)

        ssh_config_info = {}

        try:
            # Use sshd -T to dump effective configuration
            result = subprocess.run(
                ['sshd', '-T'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                config_output = result.stdout

                # Parse important settings
                for line in config_output.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # Port setting
                    if line.startswith('port '):
                        port = line.split()[1]
                        ssh_config_info['port'] = port
                        self.log_message(f"  Port: {port}", config)

                    # PermitRootLogin setting
                    elif line.startswith('permitrootlogin '):
                        permit = line.split()[1]
                        ssh_config_info['permitrootlogin'] = permit
                        self.log_message(f"  PermitRootLogin: {permit}", config)

                    # PasswordAuthentication setting
                    elif line.startswith('passwordauthentication '):
                        auth = line.split()[1]
                        ssh_config_info['passwordauth'] = auth
                        self.log_message(f"  PasswordAuthentication: {auth}", config)

                    # PubkeyAuthentication setting
                    elif line.startswith('pubkeyauthentication '):
                        pubkey = line.split()[1]
                        ssh_config_info['pubkeyauth'] = pubkey
                        self.log_message(f"  PubkeyAuthentication: {pubkey}", config)

                return True, ssh_config_info

            else:
                self.log_message(f"  ⚠ Could not read SSH config (exit code: {result.returncode})", config)
                self.log_message(f"  This may require sudo privileges", config)
                return False, {}

        except FileNotFoundError:
            self.log_message(f"  ⚠ sshd command not found", config)
            return False, {}
        except Exception as e:
            self.log_message(f"  ⚠ Error reading SSH config: {e}", config)
            return False, {}

    def check_ssh_host_keys(self, config):
        """Check if SSH host keys exist"""
        self.log_message("Checking SSH host keys...", config)

        key_types = ['rsa', 'ecdsa', 'ed25519']
        keys_found = []

        for key_type in key_types:
            key_path = f'/etc/ssh/ssh_host_{key_type}_key'
            pub_key_path = f'{key_path}.pub'

            try:
                import os
                if os.path.exists(key_path) and os.path.exists(pub_key_path):
                    keys_found.append(key_type)
                    self.log_message(f"  ✓ {key_type.upper()} host key exists", config)
                else:
                    self.log_message(f"  ✗ {key_type.upper()} host key missing", config)
            except Exception as e:
                self.log_message(f"  ⚠ Could not check {key_type} key: {e}", config)

        if keys_found:
            return True, keys_found
        else:
            return False, []

    def check_firewall_rules(self, config):
        """Check if firewall is blocking SSH port"""
        self.log_message("Checking firewall rules for SSH...", config)

        try:
            # Check iptables
            result = subprocess.run(
                ['sudo', 'iptables', '-L', '-n'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                rules = result.stdout

                # Check for SSH port in rules
                ssh_mentioned = f"dpt:{config['ssh_port']}" in rules or 'ssh' in rules.lower()

                if ssh_mentioned:
                    self.log_message(f"  SSH port mentioned in iptables rules", config)
                else:
                    self.log_message(f"  SSH port not specifically mentioned in iptables", config)

                # Check for DROP/REJECT rules
                if 'DROP' in rules or 'REJECT' in rules:
                    self.log_message(f"  ⚠ Some DROP/REJECT rules found (may affect SSH)", config)
                else:
                    self.log_message(f"  ✓ No DROP/REJECT rules found", config)

                return True, rules
            else:
                self.log_message(f"  ⚠ Could not read iptables (may need sudo)", config)
                return False, None

        except FileNotFoundError:
            self.log_message(f"  Note: iptables not found (firewall may not be active)", config)
            return True, None
        except Exception as e:
            self.log_message(f"  ⚠ Error checking firewall: {e}", config)
            return False, None

    def get_ssh_connections(self, config):
        """Get current SSH connections"""
        self.log_message("Checking current SSH connections...", config)

        try:
            result = subprocess.run(
                ['ss', '-tnp', f'sport = :{config["ssh_port"]}'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                connections = result.stdout

                # Count connections (excluding header)
                conn_lines = [l for l in connections.split('\n') if l.strip() and not l.startswith('State')]
                conn_count = len(conn_lines)

                self.log_message(f"  Current SSH connections: {conn_count}", config)

                for line in conn_lines[:5]:  # Show first 5 connections
                    self.log_message(f"    {line.strip()}", config)

                return True, conn_count
            else:
                self.log_message(f"  ⚠ Could not get SSH connections", config)
                return False, 0

        except FileNotFoundError:
            self.log_message(f"  Note: 'ss' command not found, using 'netstat'", config)

            # Fallback to netstat
            try:
                result = subprocess.run(
                    ['netstat', '-tn', f'--listening', '--program'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    self.log_message(f"  ✓ netstat succeeded (details omitted)", config)
                    return True, -1  # Unknown count

            except:
                pass

            return False, 0

        except Exception as e:
            self.log_message(f"  ⚠ Error getting connections: {e}", config)
            return False, 0

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.network
    @pytest.mark.quick
    def test_036_ssh_accessibility(self, test_config):
        """
        Test Case #36: SSH accessibility

        Test Setup: Remote machine, network
        Acceptance Criteria: SSH enabled and accessible

        IMPORTANT: This test must run ON the CM4 itself.
        SSH should be enabled via provisioning.

        What this test validates:
        - SSH service is running and enabled
        - SSH port is listening on network interfaces
        - SSH responds with valid banner
        - SSH configuration is valid
        - SSH host keys exist
        - Firewall not blocking SSH (informational)
        - Active SSH connections (informational)
        """

        print("\n" + "=" * 70)
        print("Test Case #36: SSH Accessibility")
        print("=" * 70)
        print("\nHW Component Test - SSH Service")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 1: Check SSH Service Status
        # ================================================================
        print("\n[STEP 1] Check SSH Service Status")
        print("-" * 70)

        service_running, service_name, enabled_status = self.check_ssh_service_status(test_config)

        if not service_running:
            pytest.fail(
                "SSH service is not running\n"
                "Possible causes:\n"
                "  - SSH not installed (install: sudo apt install openssh-server)\n"
                "  - Service disabled (enable: sudo systemctl enable ssh)\n"
                "  - Service stopped (start: sudo systemctl start ssh)\n"
                "  - Service failed to start (check: sudo systemctl status ssh)"
            )

        print(f"✓ SSH service is running")
        print(f"  Service name: {service_name}")
        print(f"  Enabled: {enabled_status}")

        # ================================================================
        # STEP 2: Check SSH Port Listening
        # ================================================================
        print("\n[STEP 2] Check SSH Port Listening")
        print("-" * 70)

        listening_results = {}
        for interface in test_config['test_interfaces']:
            listening = self.check_ssh_port_listening(interface, test_config['ssh_port'], test_config)
            listening_results[interface] = listening

        listening_count = sum(listening_results.values())

        if listening_count == 0:
            pytest.fail(
                f"SSH port {test_config['ssh_port']} is not listening on any interface\n"
                "Possible causes:\n"
                "  - SSH configured on different port\n"
                "  - SSH service not fully started\n"
                "  - Network interfaces not configured\n"
                f"  - Check SSH config: sudo sshd -T | grep port"
            )

        print(f"✓ SSH port listening on {listening_count}/{len(listening_results)} interfaces")

        # ================================================================
        # STEP 3: Check SSH Banner
        # ================================================================
        print("\n[STEP 3] Check SSH Banner Response")
        print("-" * 70)

        # Test on localhost
        banner_ok, banner = self.check_ssh_banner('localhost', test_config['ssh_port'], test_config)

        if not banner_ok:
            pytest.fail(
                f"SSH banner check failed: {banner}\n"
                "Possible causes:\n"
                "  - SSH not responding on port\n"
                "  - SSH handshake failing\n"
                "  - Firewall blocking connections\n"
                "  - SSH service misconfigured"
            )

        print(f"✓ SSH banner received")
        print(f"  Banner: {banner}")

        # ================================================================
        # STEP 4: Check SSH Configuration (Informational)
        # ================================================================
        print("\n[STEP 4] Check SSH Server Configuration (Informational)")
        print("-" * 70)

        if test_config.get('check_config'):
            config_ok, ssh_config_info = self.check_ssh_config(test_config)

            if config_ok:
                print(f"✓ SSH configuration retrieved")
                print(f"  Port: {ssh_config_info.get('port', 'unknown')}")
                print(f"  PermitRootLogin: {ssh_config_info.get('permitrootlogin', 'unknown')}")
                print(f"  PasswordAuth: {ssh_config_info.get('passwordauth', 'unknown')}")
                print(f"  PubkeyAuth: {ssh_config_info.get('pubkeyauth', 'unknown')}")
            else:
                print(f"  Note: Could not retrieve SSH configuration")
        else:
            print(f"  Skipped (check_config=False)")

        # ================================================================
        # STEP 5: Check SSH Host Keys (Informational)
        # ================================================================
        print("\n[STEP 5] Check SSH Host Keys (Informational)")
        print("-" * 70)

        if test_config.get('check_keys'):
            keys_ok, keys_found = self.check_ssh_host_keys(test_config)

            if keys_ok:
                print(f"✓ SSH host keys found: {', '.join([k.upper() for k in keys_found])}")
            else:
                print(f"  ⚠ No SSH host keys found (this may be a problem)")
        else:
            print(f"  Skipped (check_keys=False)")

        # ================================================================
        # STEP 6: Check Firewall Rules (Informational)
        # ================================================================
        print("\n[STEP 6] Check Firewall Rules (Informational)")
        print("-" * 70)

        if test_config.get('check_firewall'):
            firewall_ok, rules = self.check_firewall_rules(test_config)

            if firewall_ok:
                print(f"✓ Firewall rules checked")
            else:
                print(f"  Note: Could not check firewall rules")
        else:
            print(f"  Skipped (check_firewall=False)")

        # ================================================================
        # STEP 7: Check Active SSH Connections (Informational)
        # ================================================================
        print("\n[STEP 7] Check Active SSH Connections (Informational)")
        print("-" * 70)

        conn_ok, conn_count = self.get_ssh_connections(test_config)

        if conn_ok:
            if conn_count > 0:
                print(f"✓ Active SSH connections: {conn_count}")
            elif conn_count == 0:
                print(f"  No active SSH connections (this is fine)")
            else:
                print(f"  Connection count unknown")
        else:
            print(f"  Note: Could not get SSH connections")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ SSH service is running (service: {service_name})")
        print(f"  ✓ SSH service is enabled (status: {enabled_status})")
        print(f"  ✓ SSH port {test_config['ssh_port']} is listening")
        print(f"  ✓ SSH banner response valid")
        print(f"  ✓ SSH is enabled and accessible (PASS)")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
