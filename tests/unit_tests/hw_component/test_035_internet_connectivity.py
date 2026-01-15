#!/usr/bin/env python3
"""
Test Case #35: Internet Connectivity Check
Category: HW Component Test
Component: Wi-Fi (CM4)

Tests that the CM4 has working internet connectivity via Wi-Fi.
This test runs on the CM4 itself (not on PC).
"""

import subprocess
import socket
import time
import pytest
from urllib import request
from urllib.error import URLError, HTTPError


class TestInternetConnectivity:
    """HW Component Test - Internet Connectivity"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Configuration for internet connectivity test"""
        return {
            # DNS test targets
            'dns_targets': [
                'google.com',
                'cloudflare.com',
                '1.1.1.1',
            ],

            # Ping test targets
            'ping_targets': [
                {'host': '8.8.8.8', 'name': 'Google DNS'},
                {'host': '1.1.1.1', 'name': 'Cloudflare DNS'},
            ],

            # HTTP/HTTPS test targets
            'http_targets': [
                {'url': 'http://www.google.com', 'name': 'Google HTTP'},
                {'url': 'https://www.cloudflare.com', 'name': 'Cloudflare HTTPS'},
            ],

            # Timeout values
            'ping_timeout': 15,
            'http_timeout': 10,
            'dns_timeout': 5,

            # Ping parameters
            'ping_count': 3,
            'ping_max_loss': 50,  # Max acceptable packet loss percentage

            # Logging
            'enable_logging': True,
            'log_file': '/tmp/test_035_internet_connectivity.log',
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

    def check_network_interface(self, config):
        """Check if network interface is up and has IP"""
        self.log_message("Checking network interface status...", config)

        try:
            # Get all network interfaces
            result = subprocess.run(['ip', 'addr', 'show'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)

            if result.returncode != 0:
                return False, "Failed to get network interfaces"

            # Look for wlan0 or eth0 with inet address
            interfaces_found = []
            current_interface = None
            has_ip = False

            for line in result.stdout.split('\n'):
                # Interface line (e.g., "2: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP>")
                if ': ' in line and not line.startswith(' '):
                    parts = line.split(': ')
                    if len(parts) >= 2:
                        current_interface = parts[1].split('@')[0]
                        if 'UP' in line:
                            interfaces_found.append(current_interface)

                # IP address line (e.g., "    inet 192.168.1.100/24")
                if 'inet ' in line and current_interface:
                    ip_part = line.strip().split()[1]
                    self.log_message(f"  Interface {current_interface}: {ip_part}", config)
                    has_ip = True

            if not interfaces_found:
                return False, "No active network interfaces found"

            if not has_ip:
                return False, "Network interface up but no IP address assigned"

            return True, interfaces_found

        except Exception as e:
            return False, str(e)

    def check_dns_resolution(self, target, config):
        """Check if DNS resolution works for a target"""
        self.log_message(f"Resolving DNS for {target}...", config)

        try:
            # Attempt DNS resolution
            result = socket.getaddrinfo(target, 80, socket.AF_UNSPEC, socket.SOCK_STREAM)

            if result:
                # Extract IP addresses
                ips = [addr[4][0] for addr in result]
                self.log_message(f"  ✓ Resolved to: {', '.join(set(ips))}", config)
                return True, ips
            else:
                return False, "No results returned"

        except socket.gaierror as e:
            self.log_message(f"  ✗ DNS resolution failed: {e}", config)
            return False, str(e)
        except Exception as e:
            self.log_message(f"  ✗ Unexpected error: {e}", config)
            return False, str(e)

    def check_ping(self, target, config):
        """Check if ping works to a target"""
        self.log_message(f"Pinging {target['name']} ({target['host']})...", config)

        try:
            result = subprocess.run(
                ['ping', '-c', str(config['ping_count']), '-W', '2', target['host']],
                capture_output=True,
                text=True,
                timeout=config['ping_timeout']
            )

            if result.returncode == 0:
                # Parse ping statistics
                output = result.stdout
                for line in output.split('\n'):
                    if 'packets transmitted' in line:
                        self.log_message(f"  {line.strip()}", config)

                    # Extract packet loss percentage
                    if '% packet loss' in line:
                        try:
                            loss_str = line.split('%')[0].split()[-1]
                            packet_loss = float(loss_str)

                            if packet_loss > config['ping_max_loss']:
                                self.log_message(f"  ⚠ High packet loss: {packet_loss}%", config)
                                return True, {'success': True, 'high_loss': True, 'loss': packet_loss}
                            else:
                                self.log_message(f"  ✓ Packet loss: {packet_loss}%", config)
                                return True, {'success': True, 'high_loss': False, 'loss': packet_loss}
                        except:
                            pass

                self.log_message(f"  ✓ Ping successful", config)
                return True, {'success': True}

            else:
                self.log_message(f"  ✗ Ping failed (exit code {result.returncode})", config)
                return False, result.stderr

        except subprocess.TimeoutExpired:
            self.log_message(f"  ✗ Ping timeout after {config['ping_timeout']}s", config)
            return False, "Timeout"
        except Exception as e:
            self.log_message(f"  ✗ Ping error: {e}", config)
            return False, str(e)

    def check_http_fetch(self, target, config):
        """Check if HTTP/HTTPS fetch works"""
        self.log_message(f"Fetching {target['name']} ({target['url']})...", config)

        try:
            response = request.urlopen(target['url'], timeout=config['http_timeout'])
            status_code = response.getcode()

            if status_code == 200:
                # Read a small amount to verify content
                content = response.read(100)
                self.log_message(f"  ✓ HTTP {status_code} - Received {len(content)} bytes", config)
                return True, {'status': status_code, 'content_length': len(content)}
            else:
                self.log_message(f"  ⚠ Unexpected status: {status_code}", config)
                return True, {'status': status_code, 'unexpected': True}

        except HTTPError as e:
            self.log_message(f"  ✗ HTTP error {e.code}: {e.reason}", config)
            return False, f"HTTP {e.code}: {e.reason}"
        except URLError as e:
            self.log_message(f"  ✗ URL error: {e.reason}", config)
            return False, str(e.reason)
        except Exception as e:
            self.log_message(f"  ✗ Fetch error: {e}", config)
            return False, str(e)

    def check_default_gateway(self, config):
        """Check if default gateway is configured"""
        self.log_message("Checking default gateway...", config)

        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)

            if result.returncode == 0 and result.stdout.strip():
                gateway_info = result.stdout.strip()
                self.log_message(f"  ✓ Default gateway: {gateway_info}", config)
                return True, gateway_info
            else:
                self.log_message(f"  ✗ No default gateway configured", config)
                return False, "No default gateway"

        except Exception as e:
            self.log_message(f"  ✗ Error checking gateway: {e}", config)
            return False, str(e)

    def get_wifi_info(self, config):
        """Get Wi-Fi connection information"""
        self.log_message("Getting Wi-Fi connection info...", config)

        wifi_info = {}

        try:
            # Try using iwconfig
            result = subprocess.run(['iwconfig', 'wlan0'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'ESSID:' in line:
                        essid = line.split('ESSID:')[1].strip().strip('"')
                        wifi_info['ssid'] = essid
                        self.log_message(f"  Connected to: {essid}", config)
                    elif 'Signal level=' in line:
                        signal = line.split('Signal level=')[1].split()[0]
                        wifi_info['signal'] = signal
                        self.log_message(f"  Signal level: {signal}", config)

        except Exception as e:
            self.log_message(f"  Note: Could not get Wi-Fi info: {e}", config)

        return wifi_info

    @pytest.mark.unit
    @pytest.mark.hardware
    @pytest.mark.cm4
    @pytest.mark.network
    @pytest.mark.quick
    def test_035_internet_connectivity(self, test_config):
        """
        Test Case #35: Internet connectivity check

        Test Setup: Test router with internet (Wi-Fi connected)
        Acceptance Criteria: Internet connectivity accessible

        IMPORTANT: This test must run ON the CM4 itself, not on a PC.
        CM4 must be connected to Wi-Fi with internet access.

        What this test validates:
        - Network interface is up with IP address
        - Default gateway is configured
        - DNS resolution works
        - Can ping external hosts
        - Can fetch web pages via HTTP/HTTPS
        - Wi-Fi connection is active (informational)
        """

        print("\n" + "=" * 70)
        print("Test Case #35: Internet Connectivity Check")
        print("=" * 70)
        print("\nHW Component Test - Wi-Fi Internet Connectivity")
        print("=" * 70)

        # Clear previous logs
        if test_config.get('enable_logging'):
            try:
                open(test_config['log_file'], 'w').close()
            except:
                pass

        # ================================================================
        # STEP 1: Check Network Interface
        # ================================================================
        print("\n[STEP 1] Check Network Interface Status")
        print("-" * 70)

        interface_up, interface_info = self.check_network_interface(test_config)

        if not interface_up:
            pytest.fail(
                f"Network interface check failed: {interface_info}\n"
                "Possible causes:\n"
                "  - No network interface up\n"
                "  - No IP address assigned\n"
                "  - Wi-Fi not connected\n"
                "  - Network cable unplugged (if using Ethernet)"
            )

        print(f"✓ Network interface active")
        print(f"  Interfaces: {', '.join(interface_info)}")

        # ================================================================
        # STEP 2: Check Default Gateway
        # ================================================================
        print("\n[STEP 2] Check Default Gateway")
        print("-" * 70)

        gateway_ok, gateway_info = self.check_default_gateway(test_config)

        if not gateway_ok:
            pytest.fail(
                f"No default gateway configured\n"
                "This usually means:\n"
                "  - DHCP failed to assign gateway\n"
                "  - Static IP misconfigured\n"
                "  - Router not responding"
            )

        print(f"✓ Default gateway configured")

        # ================================================================
        # STEP 3: Get Wi-Fi Information (Informational)
        # ================================================================
        print("\n[STEP 3] Get Wi-Fi Connection Info (Informational)")
        print("-" * 70)

        wifi_info = self.get_wifi_info(test_config)

        if wifi_info:
            print(f"✓ Wi-Fi information retrieved")
            if 'ssid' in wifi_info:
                print(f"  SSID: {wifi_info['ssid']}")
            if 'signal' in wifi_info:
                print(f"  Signal: {wifi_info['signal']}")
        else:
            print(f"  Note: Could not retrieve Wi-Fi info (may be using Ethernet)")

        # ================================================================
        # STEP 4: Test DNS Resolution
        # ================================================================
        print("\n[STEP 4] Test DNS Resolution")
        print("-" * 70)

        dns_results = {}
        for target in test_config['dns_targets']:
            success, result = self.check_dns_resolution(target, test_config)
            dns_results[target] = success

        dns_success_count = sum(dns_results.values())
        dns_total = len(dns_results)

        print(f"\nDNS Resolution Summary: {dns_success_count}/{dns_total} successful")

        if dns_success_count == 0:
            pytest.fail(
                "DNS resolution failed for all targets\n"
                "Possible causes:\n"
                "  - DNS server not configured\n"
                "  - No route to DNS server\n"
                "  - Firewall blocking DNS (port 53)\n"
                "  - Internet connection down"
            )

        print(f"✓ DNS resolution working ({dns_success_count}/{dns_total} targets)")

        # ================================================================
        # STEP 5: Test Ping Connectivity
        # ================================================================
        print("\n[STEP 5] Test Ping Connectivity")
        print("-" * 70)

        ping_results = {}
        high_loss_warnings = []

        for target in test_config['ping_targets']:
            success, result = self.check_ping(target, test_config)
            ping_results[target['name']] = success

            if success and isinstance(result, dict) and result.get('high_loss'):
                high_loss_warnings.append(f"{target['name']}: {result['loss']}% loss")

        ping_success_count = sum(ping_results.values())
        ping_total = len(ping_results)

        print(f"\nPing Summary: {ping_success_count}/{ping_total} successful")

        if high_loss_warnings:
            print(f"\n⚠ High packet loss detected:")
            for warning in high_loss_warnings:
                print(f"  - {warning}")

        if ping_success_count == 0:
            pytest.fail(
                "Ping failed to all targets\n"
                "Possible causes:\n"
                "  - No internet connectivity\n"
                "  - Firewall blocking ICMP\n"
                "  - Router blocking outbound traffic\n"
                "  - Network cable/Wi-Fi issue"
            )

        print(f"✓ Ping connectivity working ({ping_success_count}/{ping_total} targets)")

        # ================================================================
        # STEP 6: Test HTTP/HTTPS Fetch
        # ================================================================
        print("\n[STEP 6] Test HTTP/HTTPS Fetch")
        print("-" * 70)

        http_results = {}
        for target in test_config['http_targets']:
            success, result = self.check_http_fetch(target, test_config)
            http_results[target['name']] = success

        http_success_count = sum(http_results.values())
        http_total = len(http_results)

        print(f"\nHTTP Fetch Summary: {http_success_count}/{http_total} successful")

        if http_success_count == 0:
            pytest.fail(
                "HTTP fetch failed to all targets\n"
                "Possible causes:\n"
                "  - No internet connectivity\n"
                "  - Firewall blocking HTTP/HTTPS (ports 80/443)\n"
                "  - DNS working but routing issue\n"
                "  - Proxy configuration required"
            )

        print(f"✓ HTTP/HTTPS fetch working ({http_success_count}/{http_total} targets)")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)
        print("TEST RESULT: ✓ PASS")
        print("=" * 70)
        print("\n✓ Acceptance Criteria Verification:")
        print(f"  ✓ Network interface up and configured")
        print(f"  ✓ Default gateway configured")
        print(f"  ✓ DNS resolution working ({dns_success_count}/{dns_total})")
        print(f"  ✓ Ping connectivity working ({ping_success_count}/{ping_total})")
        print(f"  ✓ HTTP/HTTPS access working ({http_success_count}/{http_total})")
        print(f"  ✓ Internet connectivity accessible (PASS)")

        if high_loss_warnings:
            print(f"\n⚠ Warnings:")
            for warning in high_loss_warnings:
                print(f"  - High packet loss: {warning}")

        if test_config.get('enable_logging'):
            print(f"\n📄 Test log: {test_config['log_file']}")

        print("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
