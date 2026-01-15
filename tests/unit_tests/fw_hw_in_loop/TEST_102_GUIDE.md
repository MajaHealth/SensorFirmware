# Test Case #102: Switch State Readback (OFF/ON) - Execution Guide

## Quick Start

```bash
# Run Test #102
pytest tests/unit_tests/fw_hw_in_loop/test_102_switch_state_readback.py -v -s

# Run all FW hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v
```

## Test Overview

**Test ID:** #102
**Category:** FW Hardware-in-Loop Test
**Component:** Contact-based switch + CM4 GPIO + Firmware
**Automation Level:** Semi-automated (requires manual switch operation)

### What This Test Validates

- ✅ GPIO input is properly configured
- ✅ Switch OFF state is correctly detected (reads HIGH with pull-up)
- ✅ Switch ON state is correctly detected (reads LOW with pull-up)
- ✅ State transitions are reliable (OFF → ON → OFF)
- ✅ No false readings due to noise/bouncing (debounced readings)
- ✅ GPIO subsystem is functional

### Test Approach

This is a **Hardware-in-Loop (HIL)** test that validates the entire signal chain:

```
Physical Switch → GPIO Input → Software Reading → Verification
```

**Detection Methods:**
1. **Primary:** RPi.GPIO library (if available)
2. **Fallback:** sysfs GPIO interface (/sys/class/gpio)

**Debouncing Strategy:**
- Multiple samples (default: 3 readings)
- Sample interval (default: 20ms between readings)
- Returns most common value to filter noise

## Prerequisites

### Hardware Requirements

**Required Hardware:**
- Raspberry Pi CM4 (or compatible)
- Contact-based switch (momentary or toggle)
- Connecting wires

**Recommended (optional):**
- 10kΩ pull-up resistor (if not using internal pull-up)
- Breadboard for prototyping
- Multimeter for debugging

### Hardware Setup

**Pull-up Configuration (default):**

```
     CM4 Module
   ┌─────────────┐
   │             │
   │ 3.3V        ├──────[Internal Pull-up]──────┐
   │             │                               │
   │ GPIO 17     ├───────────────────────────────┤
   │ (BCM mode)  │                               │
   │             │                            [Switch]
   │ GND         ├────────────────────────────────┘
   │             │
   └─────────────┘

When switch is OPEN (OFF):  GPIO reads HIGH (1)
When switch is CLOSED (ON): GPIO reads LOW (0) - connects to GND
```

**Alternative: Pull-down Configuration:**

```
     CM4 Module
   ┌─────────────┐
   │             │
   │ 3.3V        ├──────────┐
   │             │          │
   │ GPIO 17     ├──────┐   │
   │ (BCM mode)  │      │   │
   │             │   [Switch]
   │ GND         ├──────[Internal Pull-down]
   │             │
   └─────────────┘

When switch is OPEN (OFF):  GPIO reads LOW (0)
When switch is CLOSED (ON): GPIO reads HIGH (1) - connects to 3.3V
```

**Physical Pin Mapping:**

| BCM GPIO | Physical Pin | Description |
|----------|--------------|-------------|
| GPIO 17  | Pin 11       | Switch input (default) |
| 3.3V     | Pin 1 or 17  | Power (if needed) |
| GND      | Pin 6, 9, 14, 20, 25, 30, 34, 39 | Ground |

**To change GPIO pin:** Edit `test_config` fixture:
```python
'switch_gpio_pin': 27,  # Change to your desired BCM GPIO number
```

### Software Requirements

**Required:**
- Linux OS (Raspberry Pi OS recommended)
- Python 3.7+
- pytest

**Optional (but recommended):**
- RPi.GPIO library (for better GPIO control)
- Root/sudo access (for some GPIO operations)

### Installing RPi.GPIO

```bash
# On Raspberry Pi OS
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

# Or via pip
pip3 install RPi.GPIO

# Verify installation
python3 -c "import RPi.GPIO as GPIO; print('RPi.GPIO version:', GPIO.VERSION)"
```

### GPIO Permissions

```bash
# Add user to gpio group (avoid needing sudo)
sudo usermod -a -G gpio $USER

# Log out and log back in for group change to take effect

# Verify GPIO access
ls -la /dev/gpiomem
# Should show: crw-rw---- 1 root gpio ...

# Alternative: Run tests with sudo (not recommended for production)
sudo pytest tests/unit_tests/fw_hw_in_loop/test_102_switch_state_readback.py -v -s
```

## Running the Test

### Method 1: Direct Execution

```bash
# Navigate to test directory
cd tests/unit_tests/fw_hw_in_loop/

# Run Test #102 with verbose output
pytest test_102_switch_state_readback.py -v -s

# Run with detailed traceback on failure
pytest test_102_switch_state_readback.py -v -s --tb=long

# Run as Python script directly
python3 test_102_switch_state_readback.py
```

### Method 2: Run with Markers

```bash
# Run all hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v

# Run only Test #102
pytest tests/unit_tests/fw_hw_in_loop/ -k "test_102" -v -s
```

### Method 3: Run as Part of Test Suite

```bash
# Run all firmware hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -v

# Run all unit tests
pytest tests/unit_tests/ -v
```

## Expected Output

### Successful Test Execution

```
======================================================================
Test Case #102: Switch State Readback (OFF/ON)
======================================================================

PURPOSE:
  Verify contact-based switch state can be read via GPIO

HARDWARE REQUIRED:
  - Switch connected to GPIO 17
  - Pull resistor: PULL_UP
======================================================================

[STEP 1] Check Prerequisites
----------------------------------------------------------------------
✓ Running on Linux
✓ Device: Raspberry Pi Compute Module 4 Rev 1.0
✓ Using RPi.GPIO library

[STEP 2] Initialize GPIO
----------------------------------------------------------------------
Configuring GPIO 17 as input...
Pull resistor: PULL_UP
GPIO numbering: BCM
[2025-01-15 11:00:00] ✓ GPIO 17 configured as input with PULL_UP
✓ GPIO initialized successfully
  Initial GPIO state: 1

[STEP 3] Test Switch OFF State
----------------------------------------------------------------------

📋 MANUAL ACTION REQUIRED:
   Please ensure the switch is in the OFF position
   (Expected GPIO value: 1)

Press ENTER when ready (timeout: 60s)...
[User presses ENTER]

Reading GPIO state 3 times...
GPIO reading (switch OFF): 1
[2025-01-15 11:00:05] Switch OFF - GPIO state: 1
✓ PASS: GPIO correctly reads 1 when switch is OFF
[2025-01-15 11:00:05] Switch OFF state: VERIFIED

[STEP 4] Test Switch ON State
----------------------------------------------------------------------

📋 MANUAL ACTION REQUIRED:
   Please set the switch to the ON position
   (Expected GPIO value: 0)

Press ENTER when ready (timeout: 60s)...
[User presses switch and ENTER]

Reading GPIO state 3 times...
GPIO reading (switch ON): 0
[2025-01-15 11:00:10] Switch ON - GPIO state: 0
✓ PASS: GPIO correctly reads 0 when switch is ON
[2025-01-15 11:00:10] Switch ON state: VERIFIED

[STEP 5] Test State Transition Reliability
----------------------------------------------------------------------

Testing state transitions: OFF → ON → OFF

📋 Set switch to OFF position
Press ENTER when ready (timeout: 30s)...
  GPIO reading: 1 (expected: 1)
  ✓ Transition to OFF: VERIFIED
[2025-01-15 11:00:15] Transition to OFF: GPIO=1 (OK)

📋 Set switch to ON position
Press ENTER when ready (timeout: 30s)...
  GPIO reading: 0 (expected: 0)
  ✓ Transition to ON: VERIFIED
[2025-01-15 11:00:20] Transition to ON: GPIO=0 (OK)

📋 Set switch to OFF position
Press ENTER when ready (timeout: 30s)...
  GPIO reading: 1 (expected: 1)
  ✓ Transition to OFF: VERIFIED
[2025-01-15 11:00:25] Transition to OFF: GPIO=1 (OK)

✓ All state transitions verified successfully

[STEP 6] Cleanup
----------------------------------------------------------------------
✓ GPIO resources released
[2025-01-15 11:00:25] Test completed - GPIO cleaned up

======================================================================
TEST RESULT: ✓ PASS
======================================================================

Acceptance Criteria Verification:
  ✓ GPIO 17 initialized successfully
  ✓ GPIO reads 1 when switch is OFF
  ✓ GPIO reads 0 when switch is ON
  ✓ State transitions are reliable
  ✓ No false readings detected

📄 Test log saved to: /tmp/switch_test.log
======================================================================

PASSED                                                           [100%]
```

### Test with Fallback Method (sysfs)

```
[STEP 1] Check Prerequisites
----------------------------------------------------------------------
⚠️  RPi.GPIO not available - will use alternative methods
✓ Running on Linux
✓ Using sysfs GPIO method (fallback)

[STEP 2] Initialize GPIO
----------------------------------------------------------------------
[2025-01-15 11:00:00] ✓ GPIO 17 configured via sysfs
✓ GPIO initialized successfully
  Initial GPIO state: 1
```

### Failed Test Examples

**GPIO Setup Failure:**
```
[STEP 2] Initialize GPIO
----------------------------------------------------------------------
[2025-01-15 11:00:00] ✗ GPIO setup failed: [Errno 13] Permission denied: '/dev/gpiomem'

FAILED - Failed to setup GPIO

Possible causes:
  - Insufficient permissions (add user to 'gpio' group)
  - GPIO already in use by another process
  - Hardware issue with GPIO controller
```

**Wrong Switch State Reading:**
```
[STEP 3] Test Switch OFF State
----------------------------------------------------------------------
GPIO reading (switch OFF): 0
[2025-01-15 11:00:05] Switch OFF - GPIO state: 0
[2025-01-15 11:00:05] ERROR: GPIO state mismatch for switch OFF!
  Expected: 1
  Actual: 0
  Check: Pull resistor configuration, switch wiring

FAILED - GPIO state mismatch for switch OFF!
```

**User Timeout:**
```
[STEP 3] Test Switch OFF State
----------------------------------------------------------------------

📋 MANUAL ACTION REQUIRED:
   Please ensure the switch is in the OFF position
   (Expected GPIO value: 1)

Press ENTER when ready (timeout: 60s)...

⏱️  Timeout waiting for user input

SKIPPED - User did not confirm within timeout
```

## Troubleshooting

### Issue 1: Permission Denied Errors

**Error:**
```
[Errno 13] Permission denied: '/dev/gpiomem'
```

**Cause:** User does not have GPIO access permissions

**Solutions:**

```bash
# Solution 1: Add user to gpio group (recommended)
sudo usermod -a -G gpio $USER
newgrp gpio  # Or log out and log back in

# Verify group membership
groups
# Should show: ... gpio ...

# Solution 2: Run with sudo (not recommended for production)
sudo pytest test_102_switch_state_readback.py -v -s

# Solution 3: Check /dev/gpiomem permissions
ls -la /dev/gpiomem
# Should show: crw-rw---- 1 root gpio

# If permissions are wrong, fix them
sudo chmod 660 /dev/gpiomem
sudo chgrp gpio /dev/gpiomem
```

### Issue 2: GPIO Reads Wrong Value

**Problem:** Switch OFF reads 0 instead of 1 (or vice versa)

**Possible Causes:**
1. Wrong pull resistor configuration
2. Switch wired incorrectly
3. GPIO pin already configured differently

**Diagnosis:**

```bash
# Check current GPIO state manually
cat /sys/class/gpio/gpio17/value

# Check GPIO direction
cat /sys/class/gpio/gpio17/direction
# Should show: in

# Use multimeter to check voltage
# - Switch OFF (with pull-up): Should read ~3.3V
# - Switch ON (with pull-up): Should read ~0V
```

**Solutions:**

**If switch is wired opposite (active HIGH instead of active LOW):**
```python
# Change expected values in test_config
'switch_off_expected': 0,  # Changed from 1
'switch_on_expected': 1,   # Changed from 0
```

**If pull resistor is wrong:**
```python
# Change pull resistor configuration
'pull_resistor': 'PULL_DOWN',  # Changed from PULL_UP
'switch_off_expected': 0,
'switch_on_expected': 1,
```

### Issue 3: Erratic/Unstable Readings

**Problem:** GPIO readings fluctuate or are inconsistent

**Possible Causes:**
1. Switch bounce (mechanical contacts bouncing)
2. Electrical noise
3. Missing or weak pull resistor
4. Long wires acting as antenna

**Solutions:**

**Increase debounce time:**
```python
'debounce_time': 0.1,      # Increase from 0.05s
'read_samples': 5,         # Increase from 3
'sample_interval': 0.05,   # Increase from 0.02s
```

**Add hardware debounce capacitor:**
```
GPIO Pin ────┬──── Switch ──── GND
             │
            ===
           0.1μF  (ceramic capacitor)
             │
            GND
```

**Use external pull-up resistor:**
```
3.3V ──── 10kΩ ──── GPIO Pin ──── Switch ──── GND
```

**Check wiring:**
- Use shorter wires
- Twist signal and ground wires together
- Keep wires away from power lines and motors
- Use shielded cables for long runs

### Issue 4: RPi.GPIO Not Available

**Error:**
```
⚠️  RPi.GPIO not available - will use alternative methods
```

**Cause:** RPi.GPIO library not installed

**Solution:**

```bash
# Install RPi.GPIO
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

# Or via pip
pip3 install RPi.GPIO

# Verify installation
python3 -c "import RPi.GPIO as GPIO; print('OK')"
```

**Note:** Test will automatically fall back to sysfs method if RPi.GPIO is not available. This is acceptable but RPi.GPIO is preferred for better control.

### Issue 5: GPIO Already in Use

**Error:**
```
RuntimeWarning: This channel is already in use
```

**Cause:** GPIO pin is being used by another process or wasn't cleaned up

**Solutions:**

```bash
# Find processes using GPIO
sudo lsof | grep gpio

# Kill process using GPIO
sudo kill <PID>

# Or use cleanup in Python
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.cleanup()"

# Check if GPIO is exported in sysfs
ls /sys/class/gpio/
# If gpio17 exists, unexport it
echo 17 | sudo tee /sys/class/gpio/unexport

# Disable GPIO warnings (not recommended, but useful for testing)
# Add to test code:
GPIO.setwarnings(False)
```

### Issue 6: Wrong GPIO Pin Number

**Problem:** Test doesn't respond to switch

**Cause:** Using wrong GPIO numbering mode or wrong pin

**Verify GPIO Pin Mapping:**

```bash
# Install gpio utility
sudo apt-get install -y raspi-gpio

# Show all GPIO states
raspi-gpio get

# Check specific GPIO
raspi-gpio get 17
# Output: GPIO 17: level=1 fsel=0 alt=0 func=INPUT pull=UP

# Or use Python
python3 << EOF
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print(f"GPIO 17 state: {GPIO.input(17)}")
GPIO.cleanup()
EOF
```

**BCM vs BOARD Numbering:**

| Mode | Description | Example |
|------|-------------|---------|
| BCM  | Broadcom SOC channel numbers | GPIO 17 |
| BOARD | Physical pin numbers on header | Pin 11 |

**Test uses BCM mode by default.** If your wiring uses physical pin numbers:

```python
# Convert physical pin to BCM GPIO
# Physical Pin 11 = BCM GPIO 17
# Physical Pin 13 = BCM GPIO 27

# Or change test to use BOARD mode
'gpio_mode': 'BOARD',
'switch_gpio_pin': 11,  # Physical pin number
```

### Issue 7: Test Times Out Waiting for Input

**Problem:** Test skips due to timeout

**Cause:** User doesn't press ENTER within 60 seconds

**Solutions:**

**Increase timeout:**
```python
# In wait_for_user_input() calls, increase timeout
if not self.wait_for_user_input("Ready?", timeout=120):  # 2 minutes
```

**Or run test in non-interactive mode:**
- Not directly supported for this test as it requires manual switch operation
- Consider automating with electronic switch (relay, FET) for production testing

## Test Configuration

### Default Configuration

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # GPIO Configuration
        'switch_gpio_pin': 17,      # BCM GPIO 17 (Physical pin 11)
        'gpio_mode': 'BCM',         # BCM or BOARD numbering

        # Pull resistor configuration
        'pull_resistor': 'PULL_UP',  # PULL_UP or PULL_DOWN

        # Expected states (for PULL_UP configuration)
        'switch_off_expected': 1,    # HIGH when switch open
        'switch_on_expected': 0,     # LOW when switch closed

        # Timing
        'debounce_time': 0.05,       # 50ms debounce delay
        'read_samples': 3,           # Number of samples to read
        'sample_interval': 0.02,     # 20ms between samples

        # Logging
        'enable_logging': True,
        'log_file': '/tmp/switch_test.log',
    }
```

### Customization Examples

**Example 1: Different GPIO Pin**
```python
'switch_gpio_pin': 27,  # BCM GPIO 27 (Physical pin 13)
```

**Example 2: Pull-down Configuration (Active HIGH)**
```python
'pull_resistor': 'PULL_DOWN',
'switch_off_expected': 0,  # LOW when switch open
'switch_on_expected': 1,   # HIGH when switch connects to 3.3V
```

**Example 3: Physical Pin Numbering**
```python
'gpio_mode': 'BOARD',
'switch_gpio_pin': 11,  # Physical pin 11 (BCM GPIO 17)
```

**Example 4: More Aggressive Debouncing**
```python
'debounce_time': 0.1,      # 100ms debounce
'read_samples': 5,         # 5 samples
'sample_interval': 0.05,   # 50ms between samples
```

**Example 5: Custom Log Location**
```python
'log_file': '/var/log/switch_test.log',  # System log directory
```

## Comparison with Related Tests

| Aspect | Test #102 (Switch State) | Test #103 (Button Press)* | Test #104 (Switch Timing)* |
|--------|--------------------------|---------------------------|----------------------------|
| **Component** | Contact switch + GPIO | Button + GPIO + Interrupt | Switch + GPIO + Timing |
| **Detection** | Polling-based reading | Interrupt-driven (edge) | Time measurement |
| **States** | ON/OFF (steady state) | Press event (transient) | Press duration |
| **Debouncing** | Software (multi-sample) | Hardware + software | Hardware + software |
| **User Action** | Manual operation required | Manual press required | Manual with timing |
| **Automation** | Semi-automated | Semi-automated | Semi-automated |
| **Duration** | ~2-3 minutes | ~1-2 minutes | ~3-5 minutes |

*Tests #103 and #104 are hypothetical examples for comparison

### When to Use Test #102

- ✅ Validate basic GPIO input functionality
- ✅ Test contact-based switch detection
- ✅ Verify pull resistor configuration
- ✅ Debug switch wiring issues
- ✅ Production line GPIO testing
- ✅ Firmware GPIO driver validation

### When Test #102 is NOT Sufficient

- ❌ Testing interrupt-driven button presses (use Test #103)
- ❌ Measuring switch timing/debounce characteristics (use Test #104)
- ❌ Testing analog sensors (use ADC tests)
- ❌ High-frequency input testing
- ❌ Multiple GPIO simultaneous testing

## Advanced Usage

### Automated Testing with Electronic Switch

For production testing, replace manual switch with relay/FET:

```python
# Add electronic switch control
import RPi.GPIO as GPIO

CONTROL_PIN = 27  # GPIO to control relay/FET
GPIO.setup(CONTROL_PIN, GPIO.OUT)

def set_switch_state(state):
    """Control electronic switch"""
    GPIO.output(CONTROL_PIN, state)
    time.sleep(0.1)  # Wait for relay to settle

# In test:
set_switch_state(GPIO.LOW)   # Switch OFF
time.sleep(0.1)
# Read and verify OFF state

set_switch_state(GPIO.HIGH)  # Switch ON
time.sleep(0.1)
# Read and verify ON state
```

### Integration with Firmware Service

Test firmware service that reads switch state:

```python
import socket
import json

def read_switch_via_firmware(host='localhost', port=5001):
    """Read switch state via firmware TCP service"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # Send request
        request = json.dumps({"type": "get_switch_state"})
        s.sendall((request + '\n').encode())

        # Receive response
        response = s.recv(1024).decode().strip()
        data = json.loads(response)

        return data['switch_state']

# Use in test
firmware_state = read_switch_via_firmware()
gpio_state = read_gpio_rpi(test_config)

assert firmware_state == gpio_state, "Firmware/GPIO state mismatch"
```

### Continuous Monitoring Mode

Monitor switch state continuously:

```python
def monitor_switch_continuous(duration_sec=10):
    """Monitor switch state for specified duration"""
    print(f"Monitoring switch for {duration_sec} seconds...")
    print("Press Ctrl+C to stop\n")

    try:
        start_time = time.time()
        last_state = None

        while time.time() - start_time < duration_sec:
            state = GPIO.input(17)

            if state != last_state:
                timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                state_name = "OFF" if state == 1 else "ON"
                print(f"[{timestamp}] Switch: {state_name} (GPIO={state})")
                last_state = state

            time.sleep(0.01)  # 10ms polling

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

# Usage
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
monitor_switch_continuous(duration_sec=30)
GPIO.cleanup()
```

## CI/CD Integration

### GitLab CI Example

```yaml
test:fw-hil:switch-readback:
  stage: test
  tags:
    - cm4
    - hardware
    - hil
  script:
    # Ensure RPi.GPIO is installed
    - sudo apt-get update && sudo apt-get install -y python3-rpi.gpio

    # Add user to gpio group (if not already)
    - sudo usermod -a -G gpio gitlab-runner || true

    # Run Test #102 (manual step - requires physical interaction)
    # This would typically be run in a lab environment with operator
    - echo "⚠️  Test #102 requires manual switch operation"
    - echo "Run manually: pytest test_102_switch_state_readback.py -v -s"

    # Upload test log as artifact
    - mkdir -p artifacts
    - cp /tmp/switch_test.log artifacts/ || true
  artifacts:
    when: always
    paths:
      - artifacts/
    expire_in: 7 days
  when: manual  # Require manual trigger due to hardware interaction
  allow_failure: true
```

### GitHub Actions Example

```yaml
name: FW Hardware-in-Loop Tests

on:
  workflow_dispatch:  # Manual trigger only

jobs:
  test-switch-readback:
    runs-on: [self-hosted, cm4, hardware]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: |
          pip install -r tests/requirements.txt
          sudo apt-get update
          sudo apt-get install -y python3-rpi.gpio

      - name: Add User to GPIO Group
        run: |
          sudo usermod -a -G gpio runner
          newgrp gpio

      - name: Manual Test Instructions
        run: |
          echo "========================================="
          echo "Test #102 requires manual operation"
          echo "========================================="
          echo ""
          echo "To run test manually:"
          echo "  cd tests/unit_tests/fw_hw_in_loop/"
          echo "  pytest test_102_switch_state_readback.py -v -s"
          echo ""
          echo "Ensure switch is connected to GPIO 17"

      - name: Upload Test Log (if exists)
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-102-log
          path: /tmp/switch_test.log
```

**Note:** Hardware-in-loop tests requiring manual interaction are typically run in lab environments rather than fully automated CI/CD pipelines.

## Use Cases

### Use Case 1: Production Line Testing

**Scenario:** Validate GPIO functionality during CM4 board manufacturing

**Approach:**
- Use automated electronic switch (relay controlled by test fixture)
- Run test as part of automated test sequence
- Log results to production database
- Flag boards with GPIO failures

### Use Case 2: Field Service Verification

**Scenario:** Technician validates switch functionality at customer site

**Approach:**
- Technician carries laptop with test suite
- Connect to CM4 via network or direct connection
- Run Test #102 manually operating the switch
- Verify GPIO reads correct states
- Provide immediate pass/fail feedback

### Use Case 3: Firmware Development

**Scenario:** Firmware developer implements GPIO input driver

**Approach:**
- Use Test #102 to validate GPIO driver implementation
- Test different GPIO pins and configurations
- Verify debouncing algorithm effectiveness
- Ensure proper resource cleanup

### Use Case 4: Troubleshooting Customer Issues

**Scenario:** Customer reports switch not working

**Approach:**
- Request customer to run Test #102
- Review test log to diagnose issue:
  - GPIO permissions?
  - Wrong pin configuration?
  - Hardware wiring issue?
  - Pull resistor problem?
- Provide targeted troubleshooting steps

## Summary

Test #102 validates contact-based switch state readback via CM4 GPIO by:

1. ✅ **GPIO Initialization** - Configure GPIO as input with pull resistor
2. ✅ **OFF State Detection** - Verify GPIO reads HIGH when switch is OFF
3. ✅ **ON State Detection** - Verify GPIO reads LOW when switch is ON
4. ✅ **State Transition Validation** - Test OFF → ON → OFF reliability
5. ✅ **Debouncing** - Filter noise with multiple sample readings
6. ✅ **Resource Cleanup** - Properly release GPIO resources

**Key Features:**
- Semi-automated (manual switch operation required)
- Supports both RPi.GPIO and sysfs fallback methods
- Configurable GPIO pin, pull resistor, and debouncing
- Comprehensive logging and diagnostics
- Works with both BCM and BOARD pin numbering

**Test Duration:** ~2-3 minutes (depends on user interaction speed)

**Pass Criteria:**
- GPIO configured successfully
- Switch OFF state reads expected value (1 with pull-up)
- Switch ON state reads expected value (0 with pull-up)
- All state transitions verified correctly
- No false readings detected

**Hardware Requirements:**
- Contact-based switch connected to GPIO 17 (configurable)
- Proper pull resistor configuration (internal or external)
- Reliable ground connection

For questions or issues, refer to the troubleshooting section or check the test log at `/tmp/switch_test.log`.
