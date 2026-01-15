# Test #106 Execution Guide
## Soft Shutdown Denied/Timeout Behavior - Unit Test

---

## Quick Start

```bash
# From project root
cd /home/kranti/sensor_test_project

# Activate virtual environment
source venv/bin/activate

# Run the test
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

---

## Test Overview

### What This Test Does
Verifies that firmware correctly handles scenarios where:
1. **Scenario A:** Application **denies** a shutdown request
2. **Scenario B:** Application **doesn't respond** (timeout)

In both cases, firmware must:
- ✓ Cancel the shutdown
- ✓ Keep all services running
- ✓ Return to normal monitoring state

### Why This Matters
- Protects data integrity during critical operations
- Prevents system hang on unresponsive applications
- Ensures graceful recovery from communication failures

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 with firmware installed
- ✅ GPIO-connected OFF switch (default: GPIO 17)
- ✅ Network connection between laptop and CM4

### Software Required
```bash
# Install dependencies
pip install pytest RPi.GPIO

# Or install all test requirements
pip install -r tests/requirements.txt
```

### Firmware Must Be Running
```bash
# Check firmware status on CM4
ssh pi@$PI_IP systemctl status spi-service
ssh pi@$PI_IP systemctl status power-service
```

---

## Step-by-Step Execution

### Step 1: Setup Environment
```bash
# Set CM4 IP address
export PI_IP=192.168.x.x  # Replace with your CM4's IP

# Navigate to project root
cd /home/kranti/sensor_test_project

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Verify Test File Location
```bash
# Test should be in unit_tests folder
ls -l tests/unit_tests/power-service/test_106_soft_shutdown_denied.py

# Should output:
# -rw-r--r-- 1 user user <size> <date> test_106_soft_shutdown_denied.py
```

### Step 3: Run the Test
```bash
# Run with verbose output
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s

# Alternative: Run from tests directory
cd tests
pytest unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

### Step 4: Interact with Test

When you see this prompt:
```
📋 MANUAL ACTION:
   Press the OFF switch briefly (0.5s)
   Press ENTER after pressing switch...
```

**Do this:**
1. Physically press the OFF switch on CM4
2. Hold for about 0.5 seconds
3. Release the switch
4. Press ENTER on your keyboard

You will see this prompt **TWICE** (once per scenario).

---

## Expected Output

### Successful Test Run

```
==================================================================
Test Case #106: Soft Shutdown Denied/Timeout Behavior
==================================================================

[SCENARIO A] Testing Denied Shutdown
----------------------------------------------------------------------
[STEP A1] Initialize Mock App (Denial Mode)
Mock app started on 127.0.0.1:8765
✓ Mock app started (configured to deny shutdown)

[STEP A2] Initialize GPIO
✓ GPIO 17 configured

[STEP A3] Establish Firmware → Mock App Connection
✓ Connection established

[STEP A4] Simulate Switch Press
📋 MANUAL ACTION:
   Press the OFF switch briefly (0.5s)
   Press ENTER after pressing switch...
[Press switch, then ENTER]
✓ Switch press detected

[STEP A5] Send 'close' Message
✓ Sent: 'close'

[STEP A6] Verify Mock App Receives 'close'
Mock app received: close
✓ Mock app received: 'close'

[STEP A7] Mock App Sends 'denied' Response
Mock app sent: ACK:denied
✓ Mock app sent: 'ACK:denied'

[STEP A8] Firmware Receives Denial
✓ Firmware received: 'ACK:denied'

[STEP A9] Verify Shutdown NOT Initiated
✓ No shutdown process running
✓ System state: running (normal)
✓ PASS: Shutdown was NOT initiated (correct)

[STEP A10] Verify Services Still Active
✓ systemd-journald: active
📊 Service Status:
  Active services: 1
  Inactive services: 0
  ✓ PASS: Services remain active

SCENARIO A RESULT: ✓ PASS
----------------------------------------------------------------------

[SCENARIO B] Testing Timeout Behavior
----------------------------------------------------------------------
[STEP B1] Initialize Mock App (Timeout Mode)
Mock app started on 127.0.0.1:8766
✓ Mock app started (configured to timeout - no response)

[STEP B4] Simulate Switch Press
📋 MANUAL ACTION:
   Press the OFF switch briefly (0.5s)
   Press ENTER after pressing switch...
[Press switch, then ENTER]

[STEP B5] Send 'close' Message
✓ Sent: 'close'

[STEP B6] Verify Mock App Receives 'close'
✓ Mock app received: 'close'

[STEP B7] Wait for ACK Timeout
Waiting for ACK timeout (3.0s)...
(Mock app configured to NOT respond)
✓ TIMEOUT occurred after 3.0s (expected)

[STEP B8] Verify Firmware Cancels Shutdown After Timeout
✓ PASS: Shutdown was NOT initiated (correct)

[STEP B9] Verify Services Still Active
✓ systemd-journald: active
📊 Service Status:
  Active services: 1
  Inactive services: 0
  ✓ PASS: Services remain active

SCENARIO B RESULT: ✓ PASS
----------------------------------------------------------------------

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Overall Acceptance Criteria Verification:
  ✓ Scenario A: Denied shutdown handled correctly
  ✓ Scenario B: Timeout handled correctly
  ✓ Firmware does not initiate shutdown in error cases
  ✓ Services remain active after denial/timeout
  ✓ Firmware returns to normal monitoring state

📄 Test log: /tmp/test_106_shutdown_denied.log
==================================================================

====================== 1 passed in 25.34s ======================
```

---

## Test Configuration

### Default Configuration
Located in `test_config` fixture inside the test file:

```python
{
    'switch_gpio_pin': 17,              # GPIO pin number
    'gpio_mode': 'BCM',                  # BCM or BOARD
    'short_press_duration': 0.5,         # Seconds
    'mock_app_host': '127.0.0.1',        # Localhost
    'mock_app_port': 8765,               # TCP port
    'ack_timeout': 3.0,                  # ACK timeout in seconds
    'services_to_check': [               # Services to verify
        'systemd-journald',
    ],
    'log_file': '/tmp/test_106_shutdown_denied.log',
}
```

### Customizing Configuration

Edit the test file to change configuration:

```python
# tests/unit_tests/power-service/test_106_soft_shutdown_denied.py

@pytest.fixture(scope="class")
def test_config(self):
    return {
        'switch_gpio_pin': 27,        # Change GPIO pin
        'mock_app_port': 9999,        # Change port
        'ack_timeout': 5.0,           # Longer timeout
    }
```

---

## Running Test Variations

### Run Only Scenario A (Denied)
```bash
# Not directly supported, but can modify test to skip Scenario B
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py::TestSoftShutdownDenied::test_106_soft_shutdown_denied -v -s
```

### Run with Different Markers
```bash
# Run all unit tests
pytest tests/unit_tests/ -m unit -v

# Run all hardware tests
pytest tests/unit_tests/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v

# Run all shutdown tests
pytest tests/unit_tests/ -m shutdown -v
```

### Run with More Verbose Output
```bash
# Extra verbose
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -vv -s

# With full traceback
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s --tb=long
```

---

## Troubleshooting

### Issue 1: GPIO Permission Denied
**Error:**
```
PermissionError: [Errno 13] Permission denied: '/sys/class/gpio/export'
```

**Solution:**
```bash
# Option 1: Add user to gpio group
sudo usermod -a -G gpio $USER
# Then log out and back in

# Option 2: Run with sudo (not recommended)
sudo -E pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

### Issue 2: Port Already in Use
**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8765
lsof -i :8765

# Kill the process
kill <PID>

# Or wait a few seconds and retry
```

### Issue 3: RPi.GPIO Not Available
**Info:**
```
ImportWarning: RPi.GPIO not available, falling back to sysfs
```

**This is OK** - The test automatically uses sysfs GPIO as fallback.

### Issue 4: Connection Timeout
**Error:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Check:**
```bash
# Verify mock app is starting
# Look for "Mock app started on..." in test output

# Check firewall
sudo iptables -L

# Verify port is not blocked
nc -zv 127.0.0.1 8765
```

### Issue 5: Services Not Found
**Warning:**
```
⚠ systemd-journald: error checking
```

**This is usually OK** - Test still validates no shutdown occurred.

---

## Test Results & Logs

### Test Log Location
```bash
# View test log
cat /tmp/test_106_shutdown_denied.log

# Tail log in real-time
tail -f /tmp/test_106_shutdown_denied.log
```

### Log Contents
- Timestamped entries of all test actions
- GPIO configuration details
- Network connection events
- Mock app message exchanges
- Service status checks
- Shutdown verification results

---

## Test Duration

- **Scenario A (Denied):** ~10-15 seconds
- **Scenario B (Timeout):** ~15-20 seconds (includes 3s timeout)
- **Total:** ~30-40 seconds

---

## Success Criteria

### Test PASSES ✓ if:
1. Mock app receives "close" message in both scenarios
2. Scenario A: Firmware receives and handles "ACK:denied"
3. Scenario B: Firmware times out after 3 seconds
4. **No shutdown initiated** in either scenario
5. **All services remain active**
6. Firmware returns to normal state

### Test FAILS ✗ if:
- Shutdown is initiated despite denial/timeout
- Services are stopped
- System hangs waiting for response
- Firmware crashes

---

## Related Documentation

- **Main Test Suite:** [tests/README.md](../../README.md)
- **Unit Tests Overview:** [tests/unit_tests/README.md](../README.md)
- **Development Guide:** [CLAUDE.md](../../../CLAUDE.md)
- **Test #105:** Soft shutdown ACK accepted (companion test)

---

## Continuous Integration

### Running in CI Pipeline

```yaml
# Example GitLab CI
test:unit:
  stage: test
  script:
    - pip install -r tests/requirements.txt
    - pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
```

---

## Support

For issues or questions:
1. Review this guide
2. Check [TROUBLESHOOTING](#troubleshooting) section
3. Review test logs: `/tmp/test_106_shutdown_denied.log`
4. Check firmware logs on CM4: `journalctl -u spi-service -u power-service`

---

## Summary

This unit test validates **critical firmware behavior**:
- ✅ Applications can prevent shutdowns during critical operations
- ✅ System doesn't hang on unresponsive applications
- ✅ Graceful recovery from communication failures
- ✅ User maintains control over shutdown timing

**Total test time:** ~30-40 seconds
**Manual interaction:** 2x switch press (once per scenario)
**Expected result:** PASS (both scenarios)
