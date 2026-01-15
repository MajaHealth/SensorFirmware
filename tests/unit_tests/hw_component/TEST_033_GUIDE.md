# Test #33 Execution Guide
## Boot Verification (Kernel/Messages) - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #33
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v -s
```

---

## Test Overview

### What This Test Does
Validates that the CM4 has booted correctly by analyzing kernel messages, system logs, and boot performance metrics.

### Key Features
- **System Boot Verification**: Checks uptime and boot completion
- **Display Detection**: Verifies display is detected (optional check)
- **Kernel Message Analysis**: Captures and analyzes dmesg output
- **System Journal Analysis**: Reviews systemd journal logs
- **Error Detection**: Scans for critical errors, warnings, and failures
- **Expected Message Verification**: Confirms essential boot messages are present
- **Boot Performance Analysis**: Measures boot time and service startup
- **Service Status Verification**: Checks critical services are running

### Why This Matters
- Ensures CM4 boots without critical errors
- Validates kernel initialization is successful
- Confirms essential services start correctly
- Detects hardware detection issues
- Provides boot performance metrics
- Essential for production readiness

---

## Automation Level

### ✅ **100% Automated!**

Test #33 is **fully automated** when run on booted CM4:

```
No manual steps required!
✓ Runs automatically on booted CM4
✓ No hardware setup needed
✓ No user interaction required
✓ Suitable for CI/CD (on CM4 runners)
✓ Can run immediately after boot
```

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 (any variant)
- ✅ CM4 IO Board or carrier board
- ✅ Power supply
- ✅ Network connection (for SSH)
- ✅ **System must be fully booted**

### Software Required
- ✅ Operating system installed and booted on CM4
- ✅ pytest installed on CM4
- ✅ SSH access to CM4
- ✅ `systemd` running (standard on Raspberry Pi OS)

### Permissions Required
- ✅ User must be able to run `dmesg` (may need sudo in some configs)
- ✅ Access to `journalctl` logs
- ✅ Read access to `/sys/class/drm/card*/status`

---

## Running Test #33

### Method 1: SSH and Run Directly (Recommended)

```bash
# From your laptop
ssh pi@192.168.x.x

# On CM4
cd ~/sensor_test_project
source venv/bin/activate

# Run test
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v -s
```

### Method 2: Use Remote Script

```bash
# From your laptop
./scripts/run-unit-test-remote.sh 192.168.x.x test_033
```

### Method 3: One-Liner via SSH

```bash
# From your laptop
ssh pi@192.168.x.x "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v -s"
```

---

## Expected Output

### Successful Test Run

```
==================================================================
Test Case #33: Boot Verification (Kernel/Messages)
==================================================================

HW Component Test - Boot Process Validation
==================================================================

[STEP 1] Verify System is Booted
----------------------------------------------------------------------
[2026-01-15 14:30:00] Checking if system is booted...
[2026-01-15 14:30:00]   System uptime:  14:30:00 up  1:45,  1 user,  load average: 0.15, 0.18, 0.12
[2026-01-15 14:30:00]   Boot time: 2026-01-15 12:45:00
✓ System is booted
  Uptime:  14:30:00 up  1:45,  1 user,  load average: 0.15, 0.18, 0.12
  Boot time: 2026-01-15 12:45:00

[STEP 2] Check Display Detection (Optional)
----------------------------------------------------------------------
[2026-01-15 14:30:00] Checking display detection via /sys/class/drm...
[2026-01-15 14:30:00]   Display card0-HDMI-A-1: connected
✓ Display detected (informational only)
  Status: connected

[STEP 3] Capture Kernel Messages (dmesg)
----------------------------------------------------------------------
[2026-01-15 14:30:00] Attempting to capture dmesg...
[2026-01-15 14:30:00]   Method 1: dmesg
[2026-01-15 14:30:00]   ✓ dmesg captured: 3542 lines
✓ Kernel messages captured
  Method: dmesg
  Lines captured: 3542

[STEP 4] Capture System Journal (journalctl)
----------------------------------------------------------------------
[2026-01-15 14:30:01] Capturing systemd journal for current boot...
[2026-01-15 14:30:01]   ✓ Journal captured: 1247 lines
✓ System journal captured
  Lines: 1247

[STEP 5] Analyze Logs for Errors and Warnings
----------------------------------------------------------------------
[2026-01-15 14:30:01] Analyzing kernel messages for errors...
[2026-01-15 14:30:01]   Scanning 3542 lines for errors/warnings...
[2026-01-15 14:30:02]   Found 0 critical errors
[2026-01-15 14:30:02]   Found 0 errors
[2026-01-15 14:30:02]   Found 3 warnings
[2026-01-15 14:30:02]   Found 0 ignored patterns

Analysis Results:
  Critical errors: 0
  Errors: 0
  Warnings: 3
  Ignored patterns: 0

Warnings found:
  [Line 1523] [   12.345678] Warning: MMC1 CRC error detected (transient)
  [Line 2041] [   18.123456] Warning: USB power surge on port 1
  [Line 2834] [   25.678901] Warning: Temperature threshold approached: 65.2°C

✓ No critical errors found in logs

[2026-01-15 14:30:02] Analyzing system journal for errors...
[2026-01-15 14:30:02]   Scanning 1247 lines for errors/warnings...
[2026-01-15 14:30:02]   Found 0 critical errors
[2026-01-15 14:30:02]   Found 0 errors
[2026-01-15 14:30:02]   Found 1 warnings

Journal Analysis:
  Critical errors: 0
  Errors: 0
  Warnings: 1

✓ No critical errors in journal

[STEP 6] Check for Expected Boot Messages
----------------------------------------------------------------------
[2026-01-15 14:30:02] Checking for expected boot messages...
[2026-01-15 14:30:02]   ✓ Found: 'Booting Linux' (line 15)
[2026-01-15 14:30:02]   ✓ Found: 'Linux version' (line 18)
[2026-01-15 14:30:02]   ✓ Found: 'Command line:' (line 22)
[2026-01-15 14:30:02]   ✓ Found: 'systemd.*running' (line 2156)
[2026-01-15 14:30:02]   ✓ Found: 'Reached target.*Multi-User System' (line 2789)

Expected Messages Found: 5/5 (100%)
✓ All expected boot messages found

[STEP 7] Analyze Boot Performance
----------------------------------------------------------------------
[2026-01-15 14:30:02] Analyzing boot performance with systemd-analyze...
[2026-01-15 14:30:03]   Boot time breakdown:
[2026-01-15 14:30:03]     Firmware:     2.134s
[2026-01-15 14:30:03]     Loader:       1.456s
[2026-01-15 14:30:03]     Kernel:       3.789s
[2026-01-15 14:30:03]     Userspace:   12.345s
[2026-01-15 14:30:03]     Total:       19.724s

✓ Boot performance analysis complete
  Total boot time: 19.724s

Slowest services:
  1. networking.service (4.523s)
  2. systemd-udev-settle.service (3.234s)
  3. dhcpcd.service (2.156s)

[STEP 8] Verify Critical Services Status
----------------------------------------------------------------------
[2026-01-15 14:30:03] Checking status of critical services...
[2026-01-15 14:30:03]   ✓ systemd-journald.service: active
[2026-01-15 14:30:03]   ✓ systemd-udevd.service: active
[2026-01-15 14:30:03]   ✓ networking.service: active
[2026-01-15 14:30:03]   ✓ ssh.service: active

Critical Services Status: 4/4 active (100%)
✓ All critical services are running

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ System booted successfully
  ✓ Display detected (optional)
  ✓ Kernel messages captured (3542 lines)
  ✓ System journal captured (1247 lines)
  ✓ No critical errors found
  ✓ All expected boot messages present (5/5)
  ✓ Boot performance analyzed (19.7s total)
  ✓ All critical services running (4/4)
  ✓ Boot verification PASSED

📄 Test log: /tmp/test_033_boot_verification.log
==================================================================

====================== 1 passed in 4.12s ======================
```

### Failed Test (Critical Errors Found)

```
[STEP 5] Analyze Logs for Errors and Warnings
----------------------------------------------------------------------
[2026-01-15 14:30:02]   Found 2 critical errors
[2026-01-15 14:30:02]   Found 5 errors

Critical Errors:
  [Line 234] [    2.345678] Kernel panic - not syncing: VFS: Unable to mount root fs
  [Line 456] [    4.567890] Oops: 0000 [#1] SMP ARM

FAILED - Critical errors found in boot logs
  Critical errors: 2
  Errors: 5

Boot process has critical issues that must be addressed.
```

### Failed Test (Missing Expected Messages)

```
[STEP 6] Check for Expected Boot Messages
----------------------------------------------------------------------
Expected Messages Found: 2/5 (40%)

✗ Missing boot messages:
  - 'systemd.*running' (not found)
  - 'Reached target.*Multi-User System' (not found)
  - 'Login prompt' (not found)

FAILED - Critical boot messages missing
Expected at least 60% of boot messages to be present.
This indicates an incomplete or failed boot process.
```

### Failed Test (Critical Services Down)

```
[STEP 8] Verify Critical Services Status
----------------------------------------------------------------------
[2026-01-15 14:30:03]   ✓ systemd-journald.service: active
[2026-01-15 14:30:03]   ✗ systemd-udevd.service: failed
[2026-01-15 14:30:03]   ✗ networking.service: inactive
[2026-01-15 14:30:03]   ✓ ssh.service: active

Critical Services Status: 2/4 active (50%)

FAILED - Critical services not running
Expected at least 75% of services to be active.

Failed services:
  - systemd-udevd.service: failed (code=exited, status=1/FAILURE)
  - networking.service: inactive (dead)
```

---

## Troubleshooting

### Issue 1: Permission Denied for dmesg

**Error:**
```
[Errno 13] Permission denied: 'dmesg'
```

**Cause:**
Some systems require root privileges to read kernel ring buffer.

**Solution:**
```bash
# Option 1: Add user to appropriate group
sudo usermod -a -G adm $USER

# Option 2: Configure sysctl
sudo sysctl kernel.dmesg_restrict=0

# Option 3: Run test with sudo (not recommended)
sudo pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v
```

### Issue 2: No dmesg Command Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'dmesg'
```

**Solution:**
```bash
# Install util-linux package
sudo apt update
sudo apt install util-linux
```

### Issue 3: systemd-analyze Not Available

**Error:**
```
FileNotFoundError: 'systemd-analyze'
```

**Cause:**
Not running systemd or systemd tools not installed.

**Solution:**
```bash
# Verify systemd is running
ps -p 1 -o comm=

# Should output: systemd

# If not systemd, this test may not work on your system
```

### Issue 4: Too Many Warnings (False Positives)

**Problem:**
Test reports many warnings that are actually benign (bluetooth, rfkill, etc.)

**Solution:**
Edit test configuration to add ignore patterns:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        'ignore_patterns': [
            r'rfkill',           # Bluetooth radio management
            r'bluetooth',        # BT initialization warnings
            r'bcm43xx',         # WiFi firmware warnings
            r'snd_bcm2835',     # Audio driver warnings
            r'dwc2.*usb',       # USB warnings (transient)
        ],
    }
```

### Issue 5: Display Not Detected (But Working)

**Error:**
```
Display detection check - informational only
  No displays detected
```

**Explanation:**
- This is an **informational check only** (not a failure)
- Display may work even if not detected via `/sys/class/drm`
- CM4 without HDMI connected will show this
- Test continues regardless

**Solution:**
- If display is working, ignore this message
- Connect HDMI display if you want detection to succeed

### Issue 6: Test Runs Too Slowly

**Problem:**
Test takes > 10 seconds to complete.

**Possible Causes:**
- Large dmesg buffer (many boot cycles)
- Large systemd journal
- Slow disk I/O

**Solution:**
```bash
# Clear old journal entries
sudo journalctl --vacuum-time=1d

# Clear dmesg buffer (requires reboot)
# Or just reboot to start fresh

# Run test immediately after boot for fastest results
```

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
    'enable_logging': True,
    'log_file': '/tmp/test_033_boot_verification.log',

    # Error detection patterns (regex)
    'error_patterns': [
        r'\berror\b',
        r'\bfail(ed)?\b',
        r'\bpanic\b',
        r'\boops\b',
        r'\bwarning\b',
        r'\bcritical\b',
        r'\bfatal\b',
    ],

    # Patterns to ignore (known false positives)
    'ignore_patterns': [
        r'rfkill',        # Bluetooth radio management (benign)
        r'bluetooth',     # BT initialization warnings
        r'bcm43xx',      # WiFi firmware warnings
    ],

    # Expected boot messages (regex)
    'expected_messages': [
        r'Booting Linux',
        r'Linux version',
        r'Command line:',
        r'systemd.*running',
        r'Reached target.*Multi-User System',
    ],

    # Critical services to check
    'critical_services': [
        'systemd-journald.service',
        'systemd-udevd.service',
        'networking.service',
        'ssh.service',
    ],

    # Display detection (optional check)
    'check_display': True,
    'display_paths': [
        '/sys/class/drm/card0-HDMI-A-1/status',
        '/sys/class/drm/card1-HDMI-A-1/status',
        '/sys/class/drm/card0-DSI-1/status',
    ],
}
```

### Customizing Configuration

Edit the test file to customize behavior:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # Add custom error patterns
        'error_patterns': [
            r'\berror\b',
            r'\bmy_custom_error\b',  # Your custom pattern
        ],

        # Add custom ignore patterns
        'ignore_patterns': [
            r'rfkill',
            r'my_benign_warning',    # Your benign warning
        ],

        # Add custom expected messages
        'expected_messages': [
            r'Booting Linux',
            r'My Custom Service Started',  # Your service
        ],

        # Add custom critical services
        'critical_services': [
            'systemd-journald.service',
            'my-custom-service.service',  # Your service
        ],
    }
```

---

## Comparison: Test #30 vs #31 vs #32 vs #33

| Aspect | Test #30 | Test #31 | Test #32 | Test #33 |
|--------|----------|----------|----------|----------|
| **Test Name** | CM4 Enumeration | eMMC Detection | OS Flashing | Boot Verification |
| **Runs On** | PC | CM4 | PC | CM4 |
| **CM4 State** | USB boot mode | Normal boot | USB boot mode | Normal boot |
| **OS Running** | No | Yes | No | Yes |
| **Automation** | 40% | 100% | 60% | **100%** |
| **Manual Steps** | Hardware setup | None | Hardware + confirm | None |
| **CI/CD Ready** | ❌ No | ✅ Yes | ❌ No | ✅ **Yes** |
| **Purpose** | USB enumeration | eMMC present | Flash OS | Boot validation |
| **Destructive** | ❌ No | ❌ No | ✅ **Yes** | ❌ No |
| **Duration** | ~2-5 min | ~2-4 sec | ~10-30 min | ~4-8 sec |

---

## CI/CD Integration

### ✅ Suitable for CI/CD

Test #33 is **fully automated** and perfect for CI/CD **if your CI runner is on CM4**:

```yaml
# GitLab CI example (if runner is on CM4)
test:boot-verification:
  stage: test
  script:
    - pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v
  tags:
    - raspberry-pi-cm4
  only:
    - merge_requests
```

### Using Remote CM4 for CI/CD

```yaml
# Run test on remote CM4 from CI
test:boot:remote:
  stage: test
  script:
    - export PI_IP=192.168.1.100
    - ./scripts/run-unit-test-remote.sh $PI_IP test_033
  tags:
    - linux
```

### Post-Boot Validation

Test #33 is ideal for validating a fresh boot:

```bash
# Reboot CM4 and immediately validate boot
ssh pi@$PI_IP "sudo reboot"
sleep 60  # Wait for boot
./scripts/run-unit-test-remote.sh $PI_IP test_033
```

---

## Test Duration

- **Typical:** 4-8 seconds
- **Fast:** Fully automated, no waiting
- **No manual interaction required**
- **Scales with log size** (larger logs = longer analysis)

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ System is booted
2. ✓ Kernel messages captured successfully
3. ✓ System journal captured successfully
4. ✓ **No critical errors** found (panic, oops, fatal)
5. ✓ At least **60% of expected boot messages** are present
6. ✓ At least **75% of critical services** are active
7. ✓ Boot performance metrics collected successfully

### Test FAILS ✗ if:
- System not booted
- Cannot capture kernel messages or journal
- **Critical errors** found in logs (panic, oops, fatal)
- Less than 60% of expected boot messages found
- Less than 75% of critical services are active

### Informational Only (Not Failures):
- Display not detected
- Non-critical warnings in logs
- Slow boot time (reported but not failed)

---

## Running from WSL2/Laptop

### ❌ Cannot Run Locally on WSL2

This test **must run on CM4** because:
- WSL2 doesn't have CM4's kernel messages
- WSL2 has different boot process
- Test validates actual CM4 hardware boot

### ✅ Run Remotely on CM4

```bash
# From WSL2/laptop, run test on CM4
export PI_IP=192.168.x.x
./scripts/run-unit-test-remote.sh $PI_IP test_033
```

---

## Related Tests

- **Test #30:** CM4 enumeration on PC (USB boot mode)
- **Test #31:** eMMC detection (normal boot)
- **Test #32:** OS flashing to eMMC (USB boot mode, destructive)
- **Test #33:** Boot verification ← You are here
- **Test #106:** Soft shutdown handling (normal boot, GPIO)

---

## Advanced Usage

### Run After Every Boot

```bash
# Add to /etc/rc.local or systemd service
cd ~/sensor_test_project
source venv/bin/activate
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v \
  --tb=short > /tmp/boot_test_result.txt 2>&1
```

### Capture Boot Logs for Analysis

```bash
# Save logs before running test
dmesg > /tmp/dmesg_before_test.txt
journalctl -b > /tmp/journal_before_test.txt

# Run test
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v -s
```

### Compare Multiple Boots

```bash
# Boot 1
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v | tee boot1.log

# Reboot
sudo reboot

# Boot 2 (after reboot)
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v | tee boot2.log

# Compare
diff boot1.log boot2.log
```

---

## Summary

**Test #33** validates CM4 boot process:
- ✅ **Fully automated** (no manual steps!)
- ✅ Runs **ON CM4** after boot
- ✅ Analyzes kernel messages and journal
- ✅ Detects critical errors and warnings
- ✅ Verifies expected boot messages
- ✅ Checks critical services
- ✅ Measures boot performance
- ✅ Suitable for **CI/CD** (on CM4 runners)
- ✅ Fast execution (~4-8 seconds)

**Run command:**
```bash
# On CM4:
pytest tests/unit_tests/hw_component/test_033_boot_verification.py -v -s

# Remote from laptop:
./scripts/run-unit-test-remote.sh $PI_IP test_033
```

**Prerequisites:**
- CM4 fully booted
- SSH access (for remote execution)
- systemd running
- Access to dmesg and journalctl

---

**Test #33 is ready to use and fully automated! 🎉**
