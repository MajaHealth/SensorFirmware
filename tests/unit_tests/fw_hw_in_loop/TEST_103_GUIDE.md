# Test Case #103: Press Classification (Short vs Long) - Execution Guide

## Quick Start

```bash
# Run Test #103
pytest tests/unit_tests/fw_hw_in_loop/test_103_press_classification.py -v -s

# Run all FW hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v
```

## Test Overview

**Test ID:** #103
**Category:** FW Hardware-in-Loop Test
**Component:** Contact-based switch + CM4 GPIO + Firmware
**Automation Level:** Semi-automated (requires manual button presses with specific timing)

### What This Test Validates

- ✅ Short press detection (50ms - 1.0s duration)
- ✅ Long press detection (1.0s - 10.0s duration)
- ✅ Press timing accuracy (measures actual press duration)
- ✅ Press classification logic (distinguishes short from long)
- ✅ Debouncing effectiveness (filters out noise < 50ms)
- ✅ Event logging (records press events with timestamps)
- ✅ Consistency across multiple press cycles

### Test Approach

This test measures the **actual duration** of button presses and validates that the firmware/software correctly classifies them:

```
Press Detection Flow:

1. Wait for GPIO to go LOW (button pressed)
2. Record timestamp T1
3. Wait for GPIO to go HIGH (button released)
4. Record timestamp T2
5. Calculate duration = T2 - T1
6. Classify press:
   - If 50ms ≤ duration ≤ 1s → SHORT PRESS ✓
   - If 1s < duration ≤ 10s → LONG PRESS ✓
   - Otherwise → INVALID
7. Log event with timestamp and classification
```

### Press Classification Thresholds

```
│ Invalid │  Short Press  │   Long Press   │ Invalid │
├─────────┼───────────────┼────────────────┼─────────┤
0      50ms            1.0s             10.0s      ∞

Too Short:  < 50ms   (noise/bounce - rejected)
Short Press: 50ms-1s  (quick actions)
Long Press:  1s-10s   (critical actions like shutdown)
Too Long:   > 10s    (stuck button - error)
```

## Prerequisites

### Hardware Requirements

**Required:**
- Raspberry Pi CM4 (or compatible)
- Contact-based switch/button (momentary)
- Connecting wires
- Ability to perform timed button presses

**Optional:**
- Stopwatch or timer (to practice press timing)
- Oscilloscope (for debugging timing issues)

### Hardware Setup

**Button Wiring (Pull-up configuration):**

```
     CM4 Module
   ┌─────────────┐
   │             │
   │ 3.3V        ├──────[Internal Pull-up]──────┐
   │             │                               │
   │ GPIO 17     ├───────────────────────────────┤
   │ (BCM mode)  │                               │
   │             │                            [Button]
   │ GND         ├────────────────────────────────┘
   │             │
   └─────────────┘

Button Released: GPIO reads HIGH (1)
Button Pressed:  GPIO reads LOW (0) - connects to GND
```

**Physical Pin Mapping:**

| BCM GPIO | Physical Pin | Description |
|----------|--------------|-------------|
| GPIO 17  | Pin 11       | Button input (default) |
| GND      | Pin 6, 9, 14, 20, 25, 30, 34, 39 | Ground |

### Software Requirements

**Required:**
- Linux OS (Raspberry Pi OS recommended)
- Python 3.7+
- pytest

**Optional:**
- RPi.GPIO library (recommended for better GPIO control)
- Firmware power-service running (for service monitoring)

### Installing RPi.GPIO

```bash
# On Raspberry Pi OS
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

# Or via pip
pip3 install RPi.GPIO

# Verify
python3 -c "import RPi.GPIO as GPIO; print('OK')"
```

### GPIO Permissions

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and log back in

# Verify
groups  # Should show 'gpio'
```

## Running the Test

### Method 1: Direct Execution

```bash
# Navigate to test directory
cd tests/unit_tests/fw_hw_in_loop/

# Run Test #103 with verbose output
pytest test_103_press_classification.py -v -s

# Run as Python script
python3 test_103_press_classification.py
```

### Method 2: Run with Markers

```bash
# Run all hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v

# Run only Test #103
pytest tests/unit_tests/fw_hw_in_loop/ -k "test_103" -v -s
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
Test Case #103: Press Classification (Short vs Long)
======================================================================

PURPOSE:
  Verify firmware correctly classifies short vs long presses

TIMING THRESHOLDS:
  Short Press: 50ms - 1000ms
  Long Press:  1000ms - 10000ms

HARDWARE:
  GPIO Pin: 17
  Pull Resistor: PULL_UP
======================================================================

[STEP 1] Check Prerequisites
----------------------------------------------------------------------
✓ Running on Linux
✓ Device: Raspberry Pi Compute Module 4 Rev 1.0
✓ Firmware service 'power-service' is active

[STEP 2] Initialize GPIO
----------------------------------------------------------------------
[2025-01-15 12:00:00.000] ✓ GPIO 17 configured with PULL_UP
Initial GPIO state: 1
✓ GPIO initialized and ready

[STEP 3] Test Short Press Detection
----------------------------------------------------------------------

📋 MANUAL ACTION REQUIRED:
   Perform a SHORT PRESS (less than 1 second)
   Press and quickly release the button

Press ENTER when ready, then perform SHORT press...
[User presses ENTER and performs quick press]

[2025-01-15 12:00:05.000] ==================================================
[2025-01-15 12:00:05.000] Starting press detection...
[2025-01-15 12:00:05.000] Waiting for button press...
[2025-01-15 12:00:06.123] ✓ Press detected (GPIO went LOW)
[2025-01-15 12:00:06.123] Press started at 1736943606.123
[2025-01-15 12:00:06.456] ✓ Release detected (GPIO went HIGH)
[2025-01-15 12:00:06.456] Press ended at 1736943606.456
[2025-01-15 12:00:06.456] Press duration: 0.333 seconds
[2025-01-15 12:00:06.456] Classification: ✓ SHORT PRESS
[2025-01-15 12:00:06.456] ==================================================

📊 Short Press Results:
   Duration: 0.333 seconds (333ms)
   Classification: SHORT
   ✓ PASS: Correctly classified as SHORT PRESS

[STEP 4] Test Long Press Detection
----------------------------------------------------------------------

📋 MANUAL ACTION REQUIRED:
   Perform a LONG PRESS (more than 1 second)
   Press and HOLD the button for 2-3 seconds

Press ENTER when ready, then perform LONG press...
[User presses ENTER and holds button for 2 seconds]

[2025-01-15 12:00:10.000] ==================================================
[2025-01-15 12:00:10.000] Starting press detection...
[2025-01-15 12:00:10.000] Waiting for button press...
[2025-01-15 12:00:11.234] ✓ Press detected (GPIO went LOW)
[2025-01-15 12:00:11.234] Press started at 1736943611.234
[2025-01-15 12:00:13.567] ✓ Release detected (GPIO went HIGH)
[2025-01-15 12:00:13.567] Press ended at 1736943613.567
[2025-01-15 12:00:13.567] Press duration: 2.333 seconds
[2025-01-15 12:00:13.567] Classification: ✓ LONG PRESS
[2025-01-15 12:00:13.567] ==================================================

📊 Long Press Results:
   Duration: 2.333 seconds (2333ms)
   Classification: LONG
   ✓ PASS: Correctly classified as LONG PRESS

[STEP 5] Test Multiple Press Cycles
----------------------------------------------------------------------

Testing press consistency with multiple cycles...

📋 Short press (< 1s)
Press ENTER, then perform the press...
[User performs short press]
   Duration: 0.412s → SHORT
   ✓ Classification matches expected type

📋 Long press (> 1s)
Press ENTER, then perform the press...
[User performs long press]
   Duration: 1.876s → LONG
   ✓ Classification matches expected type

📋 Short press (< 1s)
Press ENTER, then perform the press...
[User performs short press]
   Duration: 0.298s → SHORT
   ✓ Classification matches expected type

📊 Multiple Press Test Results:
   Successful classifications: 3/3
   ✓ Test 1: 0.412s → short (expected: short)
   ✓ Test 2: 1.876s → long (expected: long)
   ✓ Test 3: 0.298s → short (expected: short)
   ✓ PASS: All presses classified correctly

[STEP 6] Verify Event Logging
----------------------------------------------------------------------
✓ Event log contains 5 events
  Log file: /tmp/press_events.log

Event Log Contents:
  2025-01-15T12:00:06.456,short,0.333
  2025-01-15T12:00:13.567,long,2.333
  2025-01-15T12:00:16.789,short,0.412
  2025-01-15T12:00:19.234,long,1.876
  2025-01-15T12:00:22.123,short,0.298

[Cleanup]
----------------------------------------------------------------------
✓ GPIO resources released
[2025-01-15 12:00:25.000] Test completed - cleanup done

======================================================================
TEST RESULT: ✓ PASS
======================================================================

Acceptance Criteria Verification:
  ✓ Short press correctly identified as short press
  ✓ Long press correctly identified as long press
  ✓ Multiple press cycles classified correctly
  ✓ Event logging functional

📄 Test log: /tmp/press_classification_test.log
📄 Event log: /tmp/press_events.log
======================================================================

PASSED                                                           [100%]
```

### Failed Test Examples

**Press Too Short:**
```
[STEP 3] Test Short Press Detection
----------------------------------------------------------------------
📊 Short Press Results:
   Duration: 0.023 seconds (23ms)
   Classification: TOO_SHORT
   ⚠️  WARNING: Press was too short (< 50ms)
      This might be noise or very quick press
      Try pressing slightly longer

FAILED - Press was too short - try again with slightly longer press
```

**Short Press Detected as Long:**
```
📊 Short Press Results:
   Duration: 1.234 seconds (1234ms)
   Classification: LONG
   ✗ FAIL: Classified as LONG PRESS (expected SHORT)
      Your press was 1.234s (> 1s threshold)

FAILED - Short press detected as long press - press more quickly
```

**Long Press Detected as Short:**
```
📊 Long Press Results:
   Duration: 0.876 seconds (876ms)
   Classification: SHORT
   ✗ FAIL: Classified as SHORT PRESS (expected LONG)
      Your press was 0.876s (< 1s threshold)

FAILED - Long press detected as short press - hold button longer
```

**Timeout Waiting for Press:**
```
[2025-01-15 12:00:00.000] Waiting for button press...
[2025-01-15 12:01:00.000] ✗ Timeout waiting for press

FAILED - Failed to detect short press
```

## Troubleshooting

### Issue 1: Press Too Short (< 50ms)

**Error:**
```
Classification: TOO_SHORT
```

**Cause:** Button press duration is less than 50ms (below debounce threshold)

**Solutions:**

1. **Press button more deliberately:**
   - Don't just tap - press and release with clear motion
   - Aim for at least 100-200ms press duration

2. **Adjust debounce threshold (if needed):**
   ```python
   'short_press_min': 0.03,  # Reduce from 0.05 to 30ms
   ```

3. **Check for button bounce:**
   ```bash
   # Monitor GPIO for bounce
   watch -n 0.01 cat /sys/class/gpio/gpio17/value
   # Press button and watch for multiple transitions
   ```

### Issue 2: Cannot Achieve Desired Press Duration

**Problem:** User press duration doesn't match required threshold

**Practice Technique:**

```bash
# Use stopwatch or practice script
python3 << 'EOF'
import time
import sys

print("Press ENTER to start timing...")
input()
print("Button pressed - release when ready...")
start = time.time()
input()
duration = time.time() - start
print(f"Your press duration: {duration:.3f}s ({duration*1000:.0f}ms)")

if duration < 1.0:
    print("  → Classified as SHORT PRESS")
else:
    print("  → Classified as LONG PRESS")
EOF
```

**Tips:**
- **Short press (< 1s):** Quick tap, like pressing a light switch
- **Long press (> 1s):** Count "one thousand one" while holding
- Practice a few times before running the test

### Issue 3: Inconsistent Classifications

**Problem:** Same press duration sometimes classified differently

**Possible Causes:**
1. Button bounce causing erratic timing
2. System load affecting timing accuracy
3. Threshold edge case (press exactly ~1.0s)

**Diagnosis:**

```bash
# Check event log for timing patterns
cat /tmp/press_events.log

# Example output:
# 2025-01-15T12:00:00.000,short,0.987
# 2025-01-15T12:00:05.000,long,1.012
# Note: 0.987s and 1.012s are very close to 1.0s threshold

# Check system load
uptime
# If load is high, wait for system to stabilize
```

**Solutions:**

1. **Avoid threshold edge cases:**
   - For short press: aim for 300-500ms (well below 1s)
   - For long press: aim for 2-3s (well above 1s)

2. **Increase debounce time:**
   ```python
   'debounce_time': 0.05,  # Increase from 0.02s
   ```

3. **Add hysteresis to thresholds:**
   ```python
   'short_press_max': 0.9,   # Changed from 1.0
   'long_press_min': 1.1,    # Changed from 1.0
   # Creates gap: short ends at 0.9s, long starts at 1.1s
   ```

### Issue 4: GPIO Doesn't Detect Press

**Error:**
```
Timeout waiting for button press
```

**Cause:** GPIO not detecting LOW state when button pressed

**Solutions:**

```bash
# Check button wiring
# Measure voltage with multimeter:
# - Button released: Should read ~3.3V on GPIO
# - Button pressed: Should read ~0V on GPIO

# Test GPIO manually
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Monitoring GPIO 17... Press Ctrl+C to stop")
try:
    last_state = None
    while True:
        state = GPIO.input(17)
        if state != last_state:
            timestamp = time.strftime("%H:%M:%S.%f")[:-3]
            state_name = "HIGH (released)" if state == 1 else "LOW (pressed)"
            print(f"[{timestamp}] GPIO changed: {state_name}")
            last_state = state
        time.sleep(0.01)
except KeyboardInterrupt:
    GPIO.cleanup()
EOF
```

### Issue 5: Event Log Not Created

**Problem:** Event log file not found

**Cause:** Permission error or invalid path

**Solutions:**

```bash
# Check log directory permissions
ls -la /tmp/

# Try alternate log location
# Edit test_config:
'event_log_file': f'/home/{os.getenv("USER")}/press_events.log',

# Or disable logging if not critical
'enable_logging': False,
```

### Issue 6: Multiple Press Cycle Test Fails

**Problem:** User makes mistake during multiple press sequence

**Solution:**

The test requires 3 specific presses in sequence. If you make a mistake:

1. **Option 1:** Run test again from the beginning
2. **Option 2:** Modify test to accept fewer cycles:
   ```python
   test_sequences = [
       ('short', 'Short press (< 1s)'),
       ('long', 'Long press (> 1s)'),
       # Remove third press if needed
   ]
   ```

### Issue 7: Firmware Service Not Running

**Warning:**
```
⚠️  Firmware service 'power-service' is not active
```

**Note:** This is informational only. Test can run without firmware service.

**If service monitoring is desired:**

```bash
# Check service status
systemctl status power-service

# Start service
sudo systemctl start power-service

# Enable service to start on boot
sudo systemctl enable power-service

# Or disable service monitoring in test
'monitor_firmware_service': False,
```

## Test Configuration

### Default Configuration

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # GPIO Configuration
        'switch_gpio_pin': 17,      # BCM GPIO 17
        'gpio_mode': 'BCM',         # BCM or BOARD
        'pull_resistor': 'PULL_UP', # PULL_UP or PULL_DOWN

        # Press timing thresholds (seconds)
        'short_press_min': 0.05,    # 50ms minimum
        'short_press_max': 1.0,     # 1s maximum for short
        'long_press_min': 1.0,      # 1s minimum for long
        'long_press_max': 10.0,     # 10s maximum

        # Detection settings
        'debounce_time': 0.02,      # 20ms debounce
        'poll_interval': 0.01,      # 10ms poll rate

        # Active state (PULL_UP configuration)
        'pressed_state': 0,         # GPIO=0 when pressed
        'released_state': 1,        # GPIO=1 when released

        # Logging
        'enable_logging': True,
        'log_file': '/tmp/press_classification_test.log',
        'event_log_file': '/tmp/press_events.log',

        # Firmware service (optional)
        'monitor_firmware_service': False,
        'firmware_service_name': 'power-service',
    }
```

### Customization Examples

**Example 1: Different Timing Thresholds**
```python
# Shorter short press, longer long press
'short_press_max': 0.5,     # Short press: 50-500ms
'long_press_min': 2.0,      # Long press: 2-10s
```

**Example 2: More Aggressive Debouncing**
```python
'debounce_time': 0.05,      # 50ms debounce
'short_press_min': 0.1,     # 100ms minimum (after debounce)
```

**Example 3: Pull-down Configuration (Active HIGH)**
```python
'pull_resistor': 'PULL_DOWN',
'pressed_state': 1,         # GPIO=1 when button connects to 3.3V
'released_state': 0,        # GPIO=0 when released
```

**Example 4: Different GPIO Pin**
```python
'switch_gpio_pin': 27,      # BCM GPIO 27 (Physical pin 13)
```

**Example 5: Enable Firmware Service Monitoring**
```python
'monitor_firmware_service': True,
'firmware_service_name': 'power-service',
```

## Comparison with Related Tests

| Aspect | Test #102 (State Readback) | Test #103 (Press Classification) | Test #104 (Debounce)* |
|--------|---------------------------|-----------------------------------|----------------------|
| **Focus** | GPIO state reading | Press timing and classification | Bounce elimination |
| **Measurement** | State (0 or 1) | Duration (milliseconds) | Bounce count |
| **Validation** | ON vs OFF detection | Short vs Long press | Clean transitions |
| **User Action** | Set switch position | Timed button press | Rapid presses |
| **Timing** | Not measured | Critical (ms accuracy) | Edge transitions |
| **Duration** | ~2-3 minutes | ~3-5 minutes | ~2-3 minutes |

*Test #104 is a hypothetical example for comparison

### When to Use Test #103

- ✅ Validate press timing accuracy
- ✅ Test short vs long press classification
- ✅ Verify firmware timing logic
- ✅ Measure actual press durations
- ✅ Validate debounce effectiveness
- ✅ Test event logging system
- ✅ User interface development

### When Test #103 is NOT Sufficient

- ❌ Testing raw GPIO state (use Test #102)
- ❌ Testing interrupt-based detection
- ❌ Measuring bounce characteristics in detail
- ❌ Testing multiple simultaneous buttons
- ❌ High-frequency press/release testing

## Advanced Usage

### Event Log Analysis

Analyze press patterns from event log:

```python
#!/usr/bin/env python3
"""Analyze press event log"""
import csv
from datetime import datetime

def analyze_press_log(log_file='/tmp/press_events.log'):
    events = []

    with open(log_file, 'r') as f:
        for line in f:
            timestamp, press_type, duration = line.strip().split(',')
            events.append({
                'timestamp': datetime.fromisoformat(timestamp),
                'type': press_type,
                'duration': float(duration)
            })

    # Statistics
    short_presses = [e for e in events if e['type'] == 'short']
    long_presses = [e for e in events if e['type'] == 'long']

    print(f"Total events: {len(events)}")
    print(f"Short presses: {len(short_presses)}")
    print(f"Long presses: {len(long_presses)}")

    if short_presses:
        avg_short = sum(e['duration'] for e in short_presses) / len(short_presses)
        print(f"Average short press duration: {avg_short:.3f}s")

    if long_presses:
        avg_long = sum(e['duration'] for e in long_presses) / len(long_presses)
        print(f"Average long press duration: {avg_long:.3f}s")

if __name__ == '__main__':
    analyze_press_log()
```

### Integration with Firmware Service

Monitor firmware service responses during test:

```python
import socket
import json

def get_firmware_press_event(host='localhost', port=501):
    """Query firmware for last press event"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        request = json.dumps({"type": "get_last_press_event"})
        s.sendall((request + '\n').encode())

        response = s.recv(1024).decode().strip()
        data = json.loads(response)

        return data

# Use in test to compare firmware classification with measured duration
firmware_event = get_firmware_press_event()
measured_duration = 0.456  # From test measurement

print(f"Firmware classification: {firmware_event['press_type']}")
print(f"Measured duration: {measured_duration:.3f}s")
```

### Automated Testing with Solenoid

For production testing, use solenoid to press button with precise timing:

```python
import RPi.GPIO as GPIO
import time

SOLENOID_PIN = 27  # GPIO to control solenoid

def setup_solenoid():
    GPIO.setup(SOLENOID_PIN, GPIO.OUT)
    GPIO.output(SOLENOID_PIN, GPIO.LOW)

def perform_press(duration_sec):
    """Activate solenoid for specified duration"""
    print(f"Performing {duration_sec:.3f}s press...")
    GPIO.output(SOLENOID_PIN, GPIO.HIGH)  # Activate solenoid
    time.sleep(duration_sec)
    GPIO.output(SOLENOID_PIN, GPIO.LOW)   # Deactivate solenoid

# Use in test
setup_solenoid()
perform_press(0.3)  # 300ms short press
time.sleep(1)
perform_press(2.0)  # 2s long press
```

## CI/CD Integration

### GitLab CI Example

```yaml
test:fw-hil:press-classification:
  stage: test
  tags:
    - cm4
    - hardware
    - hil
  script:
    - sudo apt-get update && sudo apt-get install -y python3-rpi.gpio

    # This test requires manual button presses
    # Run in lab environment with operator
    - echo "⚠️  Test #103 requires manual button operation"
    - echo "Operator must perform timed button presses"

    # Or use automated solenoid setup
    - echo "Automated testing requires solenoid hardware"

  when: manual
  allow_failure: true
```

### GitHub Actions Example

```yaml
name: FW HIL - Press Classification

on:
  workflow_dispatch:  # Manual trigger only

jobs:
  test-press-classification:
    runs-on: [self-hosted, cm4, hardware]

    steps:
      - uses: actions/checkout@v3

      - name: Install Dependencies
        run: |
          pip install -r tests/requirements.txt
          sudo apt-get install -y python3-rpi.gpio

      - name: Manual Test Instructions
        run: |
          echo "========================================="
          echo "Test #103 - Press Classification"
          echo "========================================="
          echo ""
          echo "This test requires manual button operation:"
          echo "  1. Short press (< 1s)"
          echo "  2. Long press (> 1s)"
          echo "  3. Multiple press cycles"
          echo ""
          echo "To run:"
          echo "  pytest test_103_press_classification.py -v -s"
```

## Use Cases

### Use Case 1: Power Button Interface

**Scenario:** Implement power button with short/long press functions

**Functions:**
- Short press: Wake display / Show status
- Long press: Shutdown system

**Test validates:**
- Short press (< 1s) detected for wake function
- Long press (> 1s) detected for shutdown function
- No accidental shutdowns from quick presses

### Use Case 2: Medical Device User Interface

**Scenario:** Start/stop recording with button presses

**Functions:**
- Short press: Start recording
- Long press: Stop recording and save

**Test validates:**
- Clear distinction between start and stop actions
- User cannot accidentally stop recording
- Timing accuracy for regulatory compliance

### Use Case 3: Menu Navigation

**Scenario:** Navigate through settings menu

**Functions:**
- Short press: Next menu item
- Long press: Enter/select current item

**Test validates:**
- Responsive navigation (short press < 1s)
- Deliberate selection (long press > 1s)
- No accidental selections

### Use Case 4: Factory Reset Protection

**Scenario:** Require long press for factory reset

**Functions:**
- Short press: Ignored
- Long press (5s): Initiate factory reset

**Test validates:**
- Short presses do not trigger reset
- Only sustained long press initiates reset
- Timing accuracy prevents accidental resets

## Summary

Test #103 validates button press classification on CM4 GPIO by:

1. ✅ **Press Detection** - Detects button press and release events
2. ✅ **Timing Measurement** - Measures actual press duration in milliseconds
3. ✅ **Classification** - Categorizes as short (50ms-1s) or long (1s-10s) press
4. ✅ **Debouncing** - Filters noise and validates clean transitions
5. ✅ **Event Logging** - Records all press events with timestamps
6. ✅ **Consistency** - Validates reliable classification across multiple cycles

**Key Features:**
- Semi-automated (requires timed manual button presses)
- Millisecond timing accuracy
- Supports both RPi.GPIO and sysfs
- Configurable timing thresholds
- Event logging for post-test analysis
- Optional firmware service integration

**Test Duration:** ~3-5 minutes

**Pass Criteria:**
- Short press (50ms-1s) correctly classified
- Long press (1s-10s) correctly classified
- Multiple press cycles consistent
- Event logging functional

**Hardware Requirements:**
- Momentary button connected to GPIO 17
- Proper pull resistor configuration
- Reliable ground connection

**Skills Required:**
- Ability to perform timed button presses
- Understanding of timing thresholds
- Basic troubleshooting if timing is difficult

For questions or issues, refer to the troubleshooting section or check the logs:
- Test log: `/tmp/press_classification_test.log`
- Event log: `/tmp/press_events.log`
