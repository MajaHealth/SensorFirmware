# Test #36 Execution Guide
## SSH Accessibility - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #36
pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v -s
```

---

## Test Overview

### What This Test Does
Validates that SSH is properly configured and accessible on the CM4 for remote management.

### Test Steps
1. **SSH Service Status**: Checks if SSH service is running and enabled
2. **Port Listening**: Verifies SSH port (22) is listening on network interfaces
3. **Banner Check**: Validates SSH responds with proper protocol banner
4. **Configuration Check**: Reviews SSH server configuration (informational)
5. **Host Keys Check**: Verifies SSH host keys exist (informational)
6. **Firewall Check**: Checks firewall rules for SSH (informational)
7. **Active Connections**: Shows current SSH connections (informational)

### Why This Matters
- Enables remote management and deployment
- Required for CI/CD pipelines
- Essential for production monitoring
- Validates provisioning was successful
- Confirms network security configuration

---

## Automation Level

### ✅ **100% Automated!**

Test #36 is **fully automated** when run on CM4 with SSH enabled:

```
No manual steps required!
✓ Runs automatically on CM4
✓ No hardware setup needed
✓ No user interaction required
✓ Suitable for CI/CD
✓ Fast execution (~3-5 seconds)
```

**Note:** If SSH is not enabled, you'll need to enable it first (one-time manual step during provisioning).

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 (any variant)
- ✅ CM4 IO Board or carrier board
- ✅ Power supply
- ✅ Network connection (Ethernet or Wi-Fi)

### Software Required
- ✅ Operating system installed and booted on CM4
- ✅ **SSH server installed** (`openssh-server`)
- ✅ **SSH service enabled** (via provisioning)
- ✅ pytest installed on CM4
- ✅ Network configured (local or remote access)

### SSH Setup (One-Time)

If SSH is not enabled yet:

```bash
# Method 1: Using raspi-config (recommended for first-time setup)
sudo raspi-config
# Navigate to: Interface Options → SSH → Enable

# Method 2: Using systemctl
sudo systemctl enable ssh
sudo systemctl start ssh

# Method 3: Create empty file in boot partition (before first boot)
# On SD card or eMMC boot partition, create: /boot/ssh
```

---

## Running Test #36

### Method 1: SSH and Run Directly (Recommended)

```bash
# From your laptop
ssh pi@192.168.x.x

# On CM4
cd ~/sensor_test_project
source venv/bin/activate

# Run test
pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v -s
```

### Method 2: Use Remote Script

```bash
# From your laptop
./scripts/run-unit-test-remote.sh 192.168.x.x test_036
```

### Method 3: One-Liner via SSH

```bash
# From your laptop
ssh pi@192.168.x.x "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v -s"
```

---

## Expected Output

### Successful Test Run (SSH Fully Configured)

```
==================================================================
Test Case #36: SSH Accessibility
==================================================================

HW Component Test - SSH Service
==================================================================

[STEP 1] Check SSH Service Status
----------------------------------------------------------------------
[2026-01-15 16:00:00] Checking SSH service status...
[2026-01-15 16:00:00]   ✓ Service 'ssh' is active
[2026-01-15 16:00:00]   Service enabled: enabled
✓ SSH service is running
  Service name: ssh
  Enabled: enabled

[STEP 2] Check SSH Port Listening
----------------------------------------------------------------------
[2026-01-15 16:00:00] Checking if SSH port 22 is listening on localhost...
[2026-01-15 16:00:00]   ✓ Port 22 is listening on localhost
[2026-01-15 16:00:00] Checking if SSH port 22 is listening on 0.0.0.0...
[2026-01-15 16:00:00]   ✓ Port 22 is listening on 0.0.0.0
✓ SSH port listening on 2/2 interfaces

[STEP 3] Check SSH Banner Response
----------------------------------------------------------------------
[2026-01-15 16:00:01] Checking SSH banner on localhost:22...
[2026-01-15 16:00:01]   ✓ SSH banner: SSH-2.0-OpenSSH_8.4p1 Raspbian-5+deb11u3
✓ SSH banner received
  Banner: SSH-2.0-OpenSSH_8.4p1 Raspbian-5+deb11u3

[STEP 4] Check SSH Server Configuration (Informational)
----------------------------------------------------------------------
[2026-01-15 16:00:01] Checking SSH server configuration...
[2026-01-15 16:00:01]   Port: 22
[2026-01-15 16:00:01]   PermitRootLogin: prohibit-password
[2026-01-15 16:00:01]   PasswordAuthentication: yes
[2026-01-15 16:00:01]   PubkeyAuthentication: yes
✓ SSH configuration retrieved
  Port: 22
  PermitRootLogin: prohibit-password
  PasswordAuth: yes
  PubkeyAuth: yes

[STEP 5] Check SSH Host Keys (Informational)
----------------------------------------------------------------------
[2026-01-15 16:00:01] Checking SSH host keys...
[2026-01-15 16:00:01]   ✓ RSA host key exists
[2026-01-15 16:00:01]   ✓ ECDSA host key exists
[2026-01-15 16:00:01]   ✓ ED25519 host key exists
✓ SSH host keys found: RSA, ECDSA, ED25519

[STEP 6] Check Firewall Rules (Informational)
----------------------------------------------------------------------
[2026-01-15 16:00:02] Checking firewall rules for SSH...
[2026-01-15 16:00:02]   SSH port not specifically mentioned in iptables
[2026-01-15 16:00:02]   ✓ No DROP/REJECT rules found
✓ Firewall rules checked

[STEP 7] Check Active SSH Connections (Informational)
----------------------------------------------------------------------
[2026-01-15 16:00:02] Checking current SSH connections...
[2026-01-15 16:00:02]   Current SSH connections: 1
[2026-01-15 16:00:02]     ESTAB 0 0 192.168.1.100:22 192.168.1.50:54321
✓ Active SSH connections: 1

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ SSH service is running (service: ssh)
  ✓ SSH service is enabled (status: enabled)
  ✓ SSH port 22 is listening
  ✓ SSH banner response valid
  ✓ SSH is enabled and accessible (PASS)

📄 Test log: /tmp/test_036_ssh_accessibility.log
==================================================================

====================== 1 passed in 3.12s ======================
```

### Failed Test (SSH Service Not Running)

```
[STEP 1] Check SSH Service Status
----------------------------------------------------------------------
[2026-01-15 16:00:00] Checking SSH service status...
[2026-01-15 16:00:00]   Service 'ssh' status: inactive
[2026-01-15 16:00:00]   Service 'sshd' status: inactive

FAILED - SSH service is not running

Possible causes:
  - SSH not installed (install: sudo apt install openssh-server)
  - Service disabled (enable: sudo systemctl enable ssh)
  - Service stopped (start: sudo systemctl start ssh)
  - Service failed to start (check: sudo systemctl status ssh)
```

### Failed Test (Port Not Listening)

```
[STEP 2] Check SSH Port Listening
----------------------------------------------------------------------
[2026-01-15 16:00:00] Checking if SSH port 22 is listening on localhost...
[2026-01-15 16:00:00]   ✗ Port 22 is NOT listening on localhost (error code: 111)
[2026-01-15 16:00:00] Checking if SSH port 22 is listening on 0.0.0.0...
[2026-01-15 16:00:00]   ✗ Port 22 is NOT listening on 0.0.0.0 (error code: 111)

FAILED - SSH port 22 is not listening on any interface

Possible causes:
  - SSH configured on different port
  - SSH service not fully started
  - Network interfaces not configured
  - Check SSH config: sudo sshd -T | grep port
```

### Failed Test (Invalid Banner)

```
[STEP 3] Check SSH Banner Response
----------------------------------------------------------------------
[2026-01-15 16:00:01] Checking SSH banner on localhost:22...
[2026-01-15 16:00:11]   ✗ Connection timeout to localhost:22

FAILED - SSH banner check failed: Timeout

Possible causes:
  - SSH not responding on port
  - SSH handshake failing
  - Firewall blocking connections
  - SSH service misconfigured
```

---

## Troubleshooting

### Issue 1: SSH Service Not Installed

**Error:**
```
SSH service is not running
Could not check service 'ssh': No such file or directory
```

**Solution:**
```bash
# Install OpenSSH server
sudo apt update
sudo apt install openssh-server

# Enable and start the service
sudo systemctl enable ssh
sudo systemctl start ssh

# Verify service is running
sudo systemctl status ssh
```

### Issue 2: SSH Service Disabled

**Error:**
```
SSH service is not running
Service 'ssh' status: inactive
```

**Solution:**
```bash
# Enable SSH to start on boot
sudo systemctl enable ssh

# Start SSH now
sudo systemctl start ssh

# Verify it's running
systemctl is-active ssh
# Should output: active
```

### Issue 3: SSH Configured on Different Port

**Error:**
```
SSH port 22 is not listening on any interface
```

**Check current SSH port:**
```bash
# Check SSH configuration
sudo sshd -T | grep port

# Or check config file
grep "^Port" /etc/ssh/sshd_config

# Check what's listening
sudo ss -tlnp | grep sshd
```

**Solution:**
If SSH is on a different port, either:

**Option 1:** Change test configuration to match
```python
# Edit test file
'ssh_port': 2222,  # Your custom port
```

**Option 2:** Change SSH back to port 22
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set or uncomment:
Port 22

# Restart SSH
sudo systemctl restart ssh
```

### Issue 4: Firewall Blocking SSH

**Error:**
```
Connection timeout to localhost:22
```

**Check firewall:**
```bash
# Check if firewall is active
sudo iptables -L -n | grep -i ssh
sudo iptables -L -n | grep 22

# Check for DROP rules
sudo iptables -L INPUT -n | grep DROP
```

**Solution:**
```bash
# Allow SSH through firewall
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Or if using ufw
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Save rules (Debian/Ubuntu)
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### Issue 5: No SSH Host Keys

**Warning:**
```
⚠ No SSH host keys found (this may be a problem)
```

**Solution:**
```bash
# Regenerate SSH host keys
sudo ssh-keygen -A

# Restart SSH service
sudo systemctl restart ssh

# Verify keys exist
ls -la /etc/ssh/ssh_host_*
```

### Issue 6: Permission Denied for sshd -T

**Warning:**
```
⚠ Could not read SSH config (exit code: 1)
This may require sudo privileges
```

**Explanation:**
- This is **informational only** and doesn't fail the test
- Reading full SSH config requires root privileges
- Test still passes if SSH is working

**Optional fix:**
```bash
# Run test with sudo (not recommended)
sudo pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v

# Or just accept the warning (test still passes)
```

### Issue 7: SSH Works but Test Fails on WSL2

**Problem:**
Running test on WSL2 instead of CM4.

**Solution:**
This test **must run on CM4**, not on WSL2:
```bash
# Run remotely on CM4
export PI_IP=192.168.x.x
./scripts/run-unit-test-remote.sh $PI_IP test_036
```

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
    # SSH connection parameters
    'ssh_port': 22,
    'ssh_service_name': 'ssh',  # 'ssh' or 'sshd'
    'timeout': 10,

    # Test users (informational)
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
```

### Customizing Configuration

Edit the test file to customize:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # Custom SSH port
        'ssh_port': 2222,

        # Skip informational checks
        'check_config': False,
        'check_keys': False,
        'check_firewall': False,

        # Test specific interfaces
        'test_interfaces': ['192.168.1.100', 'localhost'],

        # Longer timeout for slow networks
        'timeout': 30,
    }
```

---

## Comparison: Network-Related Tests

| Aspect | Test #35 | Test #36 |
|--------|----------|----------|
| **Test Name** | Internet Connectivity | SSH Accessibility |
| **Purpose** | Validate internet access | Validate SSH access |
| **Tests** | DNS, Ping, HTTP | SSH service, port, banner |
| **Runs On** | CM4 | CM4 |
| **Automation** | 100% | 100% |
| **Duration** | ~5-10 sec | ~3-5 sec |
| **Requirements** | Internet connection | SSH enabled |
| **CI/CD Ready** | ✅ Yes | ✅ Yes |

---

## CI/CD Integration

### ✅ Suitable for CI/CD

Test #36 is **fully automated** and perfect for CI/CD:

```yaml
# GitLab CI example (if runner is on CM4)
test:ssh:
  stage: test
  script:
    - pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v
  tags:
    - raspberry-pi-cm4
  only:
    - merge_requests
```

### Using Remote CM4 for CI/CD

```yaml
# Run test on remote CM4 from CI
test:ssh:remote:
  stage: test
  script:
    - export PI_IP=192.168.1.100
    - ./scripts/run-unit-test-remote.sh $PI_IP test_036
  tags:
    - linux
  only:
    - merge_requests
```

### Post-Provisioning Validation

Validate SSH after provisioning:

```bash
# After provisioning CM4
./scripts/provision-cm4.sh

# Validate SSH is accessible
./scripts/run-unit-test-remote.sh $PI_IP test_036
```

---

## Test Duration

- **Typical:** 3-5 seconds
- **Fast:** Fully automated, no delays
- **Network-dependent:** May take longer on slow networks
- **Informational checks:** Add ~1-2 seconds

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ SSH service is running
2. ✓ SSH service is enabled for boot
3. ✓ SSH port is listening on at least one interface
4. ✓ SSH responds with valid SSH protocol banner

### Test FAILS ✗ if:
- SSH service is not running
- SSH service exists but is inactive
- SSH port is not listening on any interface
- SSH does not respond with valid banner

### Informational Only (Not Failures):
- Cannot read SSH configuration (sudo required)
- Cannot read SSH host keys (permission issue)
- Cannot check firewall rules (sudo required)
- No active SSH connections (normal if no one connected)

---

## Running from WSL2/Laptop

### ❌ Cannot Run Locally on WSL2

This test **must run on CM4** because:
- Test validates CM4's SSH service
- WSL2 SSH configuration is different
- Test checks CM4-specific settings

### ✅ Run Remotely on CM4

```bash
# From WSL2/laptop, run test on CM4
export PI_IP=192.168.x.x
./scripts/run-unit-test-remote.sh $PI_IP test_036
```

**Irony:** You're using SSH to test if SSH is working! This proves SSH is accessible, but the test validates the configuration details.

---

## Related Tests

- **Test #30:** CM4 enumeration on PC (USB boot mode)
- **Test #31:** eMMC detection (normal boot)
- **Test #32:** OS flashing to eMMC (USB boot mode, destructive)
- **Test #33:** Boot verification (normal boot)
- **Test #35:** Internet connectivity (normal boot)
- **Test #36:** SSH accessibility ← You are here
- **Test #106:** Soft shutdown handling (normal boot, GPIO)

---

## Advanced Usage

### Test After Changing SSH Configuration

```bash
# After editing /etc/ssh/sshd_config
sudo systemctl restart ssh

# Validate changes
pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v
```

### Validate SSH on Multiple CM4s

```bash
# Test multiple devices
for ip in 192.168.1.{100..110}; do
    echo "Testing $ip..."
    ./scripts/run-unit-test-remote.sh $ip test_036
done
```

### Security Audit

Use test output to audit SSH security settings:

```bash
# Run test and save output
pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v \
  | tee ssh_audit.txt

# Review configuration
grep -A 5 "SSH Server Configuration" ssh_audit.txt
```

### Monitor SSH Service Health

```bash
# Run test periodically
while true; do
    pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v \
      --tb=short | tee -a /var/log/ssh_monitor.log
    sleep 3600  # Every hour
done
```

---

## SSH Security Best Practices

While this test validates SSH is accessible, consider these security improvements:

### 1. Disable Password Authentication
```bash
# Edit /etc/ssh/sshd_config
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart ssh
```

### 2. Disable Root Login
```bash
# Edit /etc/ssh/sshd_config
PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh
```

### 3. Change Default Port (Optional)
```bash
# Edit /etc/ssh/sshd_config
Port 2222

# Restart SSH
sudo systemctl restart ssh

# Update test configuration
'ssh_port': 2222,
```

### 4. Use Fail2Ban
```bash
# Install fail2ban
sudo apt install fail2ban

# Configure for SSH
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Summary

**Test #36** validates SSH accessibility on CM4:
- ✅ **Fully automated** (no manual steps after SSH enabled)
- ✅ Runs **ON CM4**
- ✅ Tests SSH service, port, and banner
- ✅ Provides configuration audit (informational)
- ✅ Checks host keys and firewall (informational)
- ✅ Shows active connections (informational)
- ✅ Suitable for **CI/CD**
- ✅ Fast execution (~3-5 seconds)

**Run command:**
```bash
# On CM4:
pytest tests/unit_tests/hw_component/test_036_ssh_accessibility.py -v -s

# Remote from laptop:
./scripts/run-unit-test-remote.sh $PI_IP test_036
```

**Prerequisites:**
- CM4 booted and running
- SSH service installed and enabled
- Network configured
- (This test assumes you already have SSH access to run it!)

---

**Test #36 is ready to use and fully automated! 🎉**
