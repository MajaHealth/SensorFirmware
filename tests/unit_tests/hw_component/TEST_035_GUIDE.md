# Test #35 Execution Guide
## Internet Connectivity Check - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #35
pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v -s
```

---

## Test Overview

### What This Test Does
Validates that the CM4 has working internet connectivity via Wi-Fi (or Ethernet) by testing multiple connectivity layers.

### Test Layers
1. **Network Interface**: Checks if network interface is up with IP address
2. **Default Gateway**: Verifies routing is configured
3. **Wi-Fi Info**: Gets connection details (SSID, signal strength)
4. **DNS Resolution**: Tests DNS lookup to external domains
5. **Ping Connectivity**: Tests ICMP connectivity to external IPs
6. **HTTP/HTTPS Fetch**: Tests actual web access

### Why This Matters
- Validates network configuration is correct
- Ensures firmware can access cloud services
- Confirms DNS, routing, and firewall settings
- Essential for OTA updates and remote monitoring
- Verifies production deployment readiness

---

## Automation Level

### ✅ **100% Automated!**

Test #35 is **fully automated** when run on CM4 with internet:

```
No manual steps required!
✓ Runs automatically on CM4
✓ No hardware connection needed (if already on Wi-Fi)
✓ No user interaction required
✓ Suitable for CI/CD (if CM4 has internet)
✓ Fast execution (~5-10 seconds)
```

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 (any variant)
- ✅ CM4 IO Board or carrier board
- ✅ Power supply
- ✅ **Wi-Fi connected** (or Ethernet cable)
- ✅ **Router with internet access**

### Software Required
- ✅ Operating system installed and booted on CM4
- ✅ pytest installed on CM4
- ✅ SSH access to CM4
- ✅ Wi-Fi configured and connected
- ✅ Network tools installed (`ping`, `ip`, `iwconfig`)

### Network Requirements
- ✅ CM4 connected to Wi-Fi or Ethernet
- ✅ Router providing DHCP (or static IP configured)
- ✅ Router connected to internet
- ✅ DNS servers accessible (usually auto-configured)
- ✅ No firewall blocking outbound traffic

---

## Running Test #35

### Method 1: SSH and Run Directly (Recommended)

```bash
# From your laptop
ssh pi@192.168.x.x

# On CM4
cd ~/sensor_test_project
source venv/bin/activate

# Run test
pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v -s
```

### Method 2: Use Remote Script

```bash
# From your laptop
./scripts/run-unit-test-remote.sh 192.168.x.x test_035
```

### Method 3: One-Liner via SSH

```bash
# From your laptop
ssh pi@192.168.x.x "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v -s"
```

---

## Expected Output

### Successful Test Run (Full Internet Access)

```
==================================================================
Test Case #35: Internet Connectivity Check
==================================================================

HW Component Test - Wi-Fi Internet Connectivity
==================================================================

[STEP 1] Check Network Interface Status
----------------------------------------------------------------------
[2026-01-15 15:00:00] Checking network interface status...
[2026-01-15 15:00:00]   Interface wlan0: 192.168.1.100/24
✓ Network interface active
  Interfaces: wlan0

[STEP 2] Check Default Gateway
----------------------------------------------------------------------
[2026-01-15 15:00:00] Checking default gateway...
[2026-01-15 15:00:00]   ✓ Default gateway: default via 192.168.1.1 dev wlan0
✓ Default gateway configured

[STEP 3] Get Wi-Fi Connection Info (Informational)
----------------------------------------------------------------------
[2026-01-15 15:00:00] Getting Wi-Fi connection info...
[2026-01-15 15:00:00]   Connected to: MyHomeNetwork
[2026-01-15 15:00:00]   Signal level: -45 dBm
✓ Wi-Fi information retrieved
  SSID: MyHomeNetwork
  Signal: -45 dBm

[STEP 4] Test DNS Resolution
----------------------------------------------------------------------
[2026-01-15 15:00:01] Resolving DNS for google.com...
[2026-01-15 15:00:01]   ✓ Resolved to: 142.250.185.46, 2607:f8b0:4004:c07::71
[2026-01-15 15:00:01] Resolving DNS for cloudflare.com...
[2026-01-15 15:00:01]   ✓ Resolved to: 104.16.132.229, 104.16.133.229
[2026-01-15 15:00:01] Resolving DNS for 1.1.1.1...
[2026-01-15 15:00:01]   ✓ Resolved to: 1.1.1.1

DNS Resolution Summary: 3/3 successful
✓ DNS resolution working (3/3 targets)

[STEP 5] Test Ping Connectivity
----------------------------------------------------------------------
[2026-01-15 15:00:02] Pinging Google DNS (8.8.8.8)...
[2026-01-15 15:00:03]   3 packets transmitted, 3 received, 0% packet loss, time 2003ms
[2026-01-15 15:00:03]   ✓ Packet loss: 0.0%
[2026-01-15 15:00:03]   ✓ Ping successful
[2026-01-15 15:00:03] Pinging Cloudflare DNS (1.1.1.1)...
[2026-01-15 15:00:04]   3 packets transmitted, 3 received, 0% packet loss, time 2004ms
[2026-01-15 15:00:04]   ✓ Packet loss: 0.0%
[2026-01-15 15:00:04]   ✓ Ping successful

Ping Summary: 2/2 successful
✓ Ping connectivity working (2/2 targets)

[STEP 6] Test HTTP/HTTPS Fetch
----------------------------------------------------------------------
[2026-01-15 15:00:05] Fetching Google HTTP (http://www.google.com)...
[2026-01-15 15:00:05]   ✓ HTTP 200 - Received 100 bytes
[2026-01-15 15:00:06] Fetching Cloudflare HTTPS (https://www.cloudflare.com)...
[2026-01-15 15:00:06]   ✓ HTTP 200 - Received 100 bytes

HTTP Fetch Summary: 2/2 successful
✓ HTTP/HTTPS fetch working (2/2 targets)

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ Network interface up and configured
  ✓ Default gateway configured
  ✓ DNS resolution working (3/3)
  ✓ Ping connectivity working (2/2)
  ✓ HTTP/HTTPS access working (2/2)
  ✓ Internet connectivity accessible (PASS)

📄 Test log: /tmp/test_035_internet_connectivity.log
==================================================================

====================== 1 passed in 6.45s ======================
```

### Successful Test with Warnings (High Packet Loss)

```
[STEP 5] Test Ping Connectivity
----------------------------------------------------------------------
[2026-01-15 15:00:03]   3 packets transmitted, 2 received, 33% packet loss, time 2003ms
[2026-01-15 15:00:03]   ⚠ High packet loss: 33.0%

Ping Summary: 2/2 successful

⚠ High packet loss detected:
  - Google DNS: 33.0% loss
✓ Ping connectivity working (2/2 targets)

==================================================================
TEST RESULT: ✓ PASS
==================================================================

⚠ Warnings:
  - High packet loss: Google DNS: 33.0% loss
```

### Failed Test (No Network Interface)

```
[STEP 1] Check Network Interface Status
----------------------------------------------------------------------
[2026-01-15 15:00:00] Checking network interface status...

FAILED - Network interface check failed: No active network interfaces found

Possible causes:
  - No network interface up
  - No IP address assigned
  - Wi-Fi not connected
  - Network cable unplugged (if using Ethernet)
```

### Failed Test (No DNS Resolution)

```
[STEP 4] Test DNS Resolution
----------------------------------------------------------------------
[2026-01-15 15:00:01] Resolving DNS for google.com...
[2026-01-15 15:00:01]   ✗ DNS resolution failed: [Errno -2] Name or service not known
[2026-01-15 15:00:01] Resolving DNS for cloudflare.com...
[2026-01-15 15:00:01]   ✗ DNS resolution failed: [Errno -2] Name or service not known
[2026-01-15 15:00:01] Resolving DNS for 1.1.1.1...
[2026-01-15 15:00:01]   ✗ DNS resolution failed: [Errno -2] Name or service not known

DNS Resolution Summary: 0/3 successful

FAILED - DNS resolution failed for all targets

Possible causes:
  - DNS server not configured
  - No route to DNS server
  - Firewall blocking DNS (port 53)
  - Internet connection down
```

### Failed Test (No Internet - Ping Failed)

```
[STEP 5] Test Ping Connectivity
----------------------------------------------------------------------
[2026-01-15 15:00:03] Pinging Google DNS (8.8.8.8)...
[2026-01-15 15:00:18]   ✗ Ping timeout after 15s
[2026-01-15 15:00:18] Pinging Cloudflare DNS (1.1.1.1)...
[2026-01-15 15:00:33]   ✗ Ping timeout after 15s

Ping Summary: 0/2 successful

FAILED - Ping failed to all targets

Possible causes:
  - No internet connectivity
  - Firewall blocking ICMP
  - Router blocking outbound traffic
  - Network cable/Wi-Fi issue
```

---

## Troubleshooting

### Issue 1: Wi-Fi Not Connected

**Error:**
```
Network interface check failed: No active network interfaces found
```

**Check Wi-Fi status:**
```bash
# Check if Wi-Fi is up
ifconfig wlan0

# Check Wi-Fi connection
iwconfig wlan0

# Check available networks
sudo iwlist wlan0 scan | grep ESSID

# Connect to Wi-Fi
sudo raspi-config  # Navigate to Network Options > Wi-Fi
```

**Or configure via command line:**
```bash
# Edit wpa_supplicant
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add network:
network={
    ssid="YourNetworkName"
    psk="YourPassword"
}

# Restart networking
sudo systemctl restart dhcpcd
sudo wpa_cli -i wlan0 reconfigure
```

### Issue 2: No IP Address Assigned

**Error:**
```
Network interface up but no IP address assigned
```

**Solutions:**
```bash
# Check DHCP client status
sudo systemctl status dhcpcd

# Restart DHCP client
sudo systemctl restart dhcpcd

# Request new IP
sudo dhclient -r wlan0
sudo dhclient wlan0

# Or manually assign IP
sudo ifconfig wlan0 192.168.1.100 netmask 255.255.255.0
sudo route add default gw 192.168.1.1
```

### Issue 3: DNS Not Working

**Error:**
```
DNS resolution failed for all targets
```

**Check DNS configuration:**
```bash
# Check resolv.conf
cat /etc/resolv.conf

# Should contain nameserver entries like:
# nameserver 8.8.8.8
# nameserver 1.1.1.1
```

**Fix DNS:**
```bash
# Temporarily set DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# Permanently set DNS (if using dhcpcd)
sudo nano /etc/dhcpcd.conf
# Add: static domain_name_servers=8.8.8.8 1.1.1.1

# Restart networking
sudo systemctl restart dhcpcd
```

### Issue 4: Ping Works but HTTP Fails

**Error:**
```
DNS resolution working
Ping connectivity working
HTTP fetch failed to all targets
```

**Possible causes:**
- Firewall blocking HTTP/HTTPS ports (80, 443)
- Proxy required
- Router blocking HTTP traffic

**Solutions:**
```bash
# Check if ports are blocked
telnet www.google.com 80
telnet www.google.com 443

# Check firewall rules
sudo iptables -L

# Test with curl
curl -v http://www.google.com
curl -v https://www.google.com

# If proxy required, set environment variables
export http_proxy="http://proxy.example.com:8080"
export https_proxy="http://proxy.example.com:8080"
```

### Issue 5: Weak Wi-Fi Signal

**Warning:**
```
Signal: -75 dBm
High packet loss: 60%
```

**Interpretation:**
- Signal strength (dBm):
  - **-30 to -50**: Excellent
  - **-50 to -60**: Good
  - **-60 to -70**: Fair
  - **-70 to -80**: Weak
  - **Below -80**: Very poor

**Solutions:**
- Move CM4 closer to router
- Add external Wi-Fi antenna
- Reduce interference (move away from microwaves, etc.)
- Switch to 5GHz band if available
- Use Ethernet cable instead

### Issue 6: iwconfig Command Not Found

**Error:**
```
Note: Could not get Wi-Fi info: [Errno 2] No such file or directory: 'iwconfig'
```

**Solution:**
```bash
# Install wireless-tools
sudo apt update
sudo apt install wireless-tools
```

**Note:** This is informational only - test will still pass without Wi-Fi info.

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
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
```

### Customizing Configuration

Edit the test file to customize targets and thresholds:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # Test your own servers
        'dns_targets': [
            'yourcompany.com',
            'api.yourservice.com',
        ],

        'ping_targets': [
            {'host': '192.168.1.1', 'name': 'Local Router'},
            {'host': 'api.yourservice.com', 'name': 'Your API Server'},
        ],

        'http_targets': [
            {'url': 'https://api.yourservice.com/health', 'name': 'API Health Check'},
        ],

        # Adjust for slower connections
        'ping_timeout': 30,
        'http_timeout': 20,
        'ping_max_loss': 75,  # More tolerant of packet loss
    }
```

---

## Comparison: Network-Related Tests

| Aspect | Test #35 |
|--------|----------|
| **Test Name** | Internet Connectivity |
| **Runs On** | CM4 |
| **CM4 State** | Normal boot, Wi-Fi connected |
| **OS Running** | Yes |
| **Automation** | **100%** |
| **Manual Steps** | None (if Wi-Fi pre-configured) |
| **CI/CD Ready** | ✅ Yes (if CM4 has internet) |
| **Purpose** | Validate internet access |
| **Tests** | Network, DNS, Ping, HTTP |
| **Duration** | ~5-10 seconds |

---

## CI/CD Integration

### ✅ Suitable for CI/CD

Test #35 is **fully automated** and can run in CI/CD **if your CM4 has internet access**:

```yaml
# GitLab CI example (if runner is on CM4 with internet)
test:internet:
  stage: test
  script:
    - pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v
  tags:
    - raspberry-pi-cm4
    - network
  only:
    - merge_requests
```

### Using Remote CM4 for CI/CD

```yaml
# Run test on remote CM4 from CI
test:internet:remote:
  stage: test
  script:
    - export PI_IP=192.168.1.100
    - ./scripts/run-unit-test-remote.sh $PI_IP test_035
  tags:
    - linux
  only:
    - merge_requests
```

### Network Validation in Deployment Pipeline

```bash
# After deploying firmware, validate network connectivity
./scripts/build-and-deploy.sh
./scripts/run-unit-test-remote.sh $PI_IP test_035

# Or combined with other tests
./scripts/run-unit-test-remote.sh $PI_IP -m "cm4 and quick"
```

---

## Test Duration

- **Typical:** 5-10 seconds
- **Fast:** Fully automated, no waiting
- **Network-dependent:** May take longer on slow connections
- **Timeout protection:** Won't hang forever (15s ping timeout, 10s HTTP timeout)

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ Network interface is up with IP address
2. ✓ Default gateway is configured
3. ✓ At least **1 DNS target** resolves successfully
4. ✓ At least **1 ping target** responds
5. ✓ At least **1 HTTP target** returns data
6. ✓ Internet connectivity is accessible

### Test FAILS ✗ if:
- No network interface is up
- No IP address assigned
- No default gateway configured
- **All DNS resolutions fail**
- **All ping tests fail**
- **All HTTP fetches fail**

### Informational Only (Not Failures):
- Wi-Fi info not retrievable
- High packet loss (warning but not failure if < 100%)
- Some targets fail (as long as at least 1 succeeds per category)

---

## Running from WSL2/Laptop

### ❌ Cannot Run Locally on WSL2

This test **must run on CM4** because:
- Test validates CM4's network connectivity
- WSL2's network is different from CM4's
- Test checks CM4's Wi-Fi hardware

### ✅ Run Remotely on CM4

```bash
# From WSL2/laptop, run test on CM4
export PI_IP=192.168.x.x
./scripts/run-unit-test-remote.sh $PI_IP test_035
```

**Note:** The laptop must be able to reach CM4 via SSH, which means CM4 already has some network connectivity. This test validates **internet** access, not just local network access.

---

## Related Tests

- **Test #30:** CM4 enumeration on PC (USB boot mode)
- **Test #31:** eMMC detection (normal boot)
- **Test #32:** OS flashing to eMMC (USB boot mode, destructive)
- **Test #33:** Boot verification (normal boot)
- **Test #35:** Internet connectivity ← You are here
- **Test #106:** Soft shutdown handling (normal boot, GPIO)

---

## Advanced Usage

### Test from Multiple Locations

```bash
# Test from home network
ssh pi@home-cm4 "cd ~/sensor_test_project && pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v"

# Test from office network
ssh pi@office-cm4 "cd ~/sensor_test_project && pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v"

# Compare connectivity quality
```

### Continuous Monitoring

```bash
# Run test every hour
while true; do
    pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v \
      --tb=short | tee -a /var/log/internet_monitor.log
    sleep 3600
done
```

### Test After Network Changes

```bash
# After changing Wi-Fi network
sudo wpa_cli -i wlan0 reconfigure
sleep 10  # Wait for connection
pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v

# After router reboot
sleep 60  # Wait for router
pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v
```

### Custom Target Testing

Create a custom test configuration for your infrastructure:

```python
# test_my_infrastructure.py
import pytest
from test_035_internet_connectivity import TestInternetConnectivity

class TestMyInfrastructure(TestInternetConnectivity):

    @pytest.fixture(scope="class")
    def test_config(self):
        return {
            'dns_targets': ['api.mycompany.com'],
            'ping_targets': [
                {'host': 'api.mycompany.com', 'name': 'My API'},
            ],
            'http_targets': [
                {'url': 'https://api.mycompany.com/health', 'name': 'Health Check'},
            ],
            'ping_timeout': 10,
            'http_timeout': 10,
            'ping_count': 5,
            'ping_max_loss': 20,
        }
```

---

## Summary

**Test #35** validates CM4 internet connectivity:
- ✅ **Fully automated** (no manual steps if Wi-Fi pre-configured)
- ✅ Runs **ON CM4** after boot
- ✅ Tests multiple connectivity layers (interface, gateway, DNS, ping, HTTP)
- ✅ Provides detailed diagnostics for troubleshooting
- ✅ Suitable for **CI/CD** (if CM4 has internet)
- ✅ Fast execution (~5-10 seconds)
- ✅ Network-quality warnings (packet loss)

**Run command:**
```bash
# On CM4:
pytest tests/unit_tests/hw_component/test_035_internet_connectivity.py -v -s

# Remote from laptop:
./scripts/run-unit-test-remote.sh $PI_IP test_035
```

**Prerequisites:**
- CM4 booted and running
- Wi-Fi connected (or Ethernet)
- Router with internet access
- SSH access (for remote execution)

---

**Test #35 is ready to use and fully automated! 🎉**
