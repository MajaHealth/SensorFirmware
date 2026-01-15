# Test Case #104: Debounce Robustness Against Bouncing Input - Execution Guide

## Quick Start

```bash
# Run Test #104
pytest tests/unit_tests/fw_hw_in_loop/test_104_debounce_robustness.py -v -s

# Run all FW hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v
```

## Test Overview

**Test ID:** #104
**Category:** FW Hardware-in-Loop Test
**Component:** Contact-based switch + Firmware
**Automation Level:** Partially automated (simulated bouncing) + Manual testing option

### What This Test Validates

- ✅ Debounce algorithm filters mechanical switch bounce
- ✅ Only one press event detected per physical press
- ✅ Multiple rapid transitions (bounces) are ignored
- ✅ Bounce during press is filtered out
- ✅ Bounce during release is filtered out
- ✅ No false triggers from noisy signals
- ✅ Debounce timing is appropriate (50ms standard)

### Test Approach

This test validates debouncing using **two methods**:

**Method 1: Simulated Bouncing (Automated)**
- Uses second GPIO to generate realistic bouncing signal
- Simulates 5 bounces over 20ms during press
- Simulates 5 bounces over 20ms during release
- Monitors input GPIO and counts transitions
- Applies software debounce and verifies only 1 press detected

**Method 2: Real Switch Testing (Manual)**
- User presses actual mechanical switch
- Monitors for natural contact bounce
- Records raw transition count
- Applies debounce filter
- Verifies only 1 press detected despite bouncing

### Switch Bounce Explained

**What is Switch Bounce?**

When a mechanical switch is pressed, the metal contacts don't make clean contact immediately. Instead, they "bounce" - making and breaking contact multiple times over 5-20 milliseconds.

```
Raw Signal (no debounce):

PRESS ↓                              RELEASE ↑
  │   ╱╲╱╲╱╲                            ╱╲╱╲╱╲
  │  ╱  ╲  ╲                           ╱  ╲  ╲
──┴─╱────╲──╲─────────────────────────╱────╲──╲────
HIGH  Bounces                         Bounces  HIGH

Without debouncing: Detected as MULTIPLE presses!

Debounced Signal (with 50ms debounce):

PRESS ↓                              RELEASE ↑
  │                                      │
  │                                      │
──┴──────────────────────────────────────┴────
HIGH    Stable LOW (pressed)           HIGH

With debouncing: Only ONE press detected ✓
```

### Debounce Algorithm

**Time-based Debounce:**

```python
last_state = read_gpio()
last_change_time = now()

while True:
    current_state = read_gpio()
    current_time = now()

    if current_state != last_state:
        if (current_time - last_change_time) > DEBOUNCE_TIME:
            # Enough time passed - accept new state
            trigger_event(current_state)
            last_state = current_state

        last_change_time = current_time
```

**Key Principle:** Ignore all state changes for DEBOUNCE_TIME (e.g., 50ms) after the first change is detected.

## Prerequisites

### Hardware Requirements

**Minimum (Automated Test):**
- Raspberry Pi CM4
- Two GPIO pins available:
  - GPIO 17: Input (monitor signal)
  - GPIO 27: Output (generate bouncing signal)
- Wire connecting GPIO 27 output to GPIO 17 input

**Recommended (Full Test):**
- Above hardware plus
- Physical momentary button/switch
- Breadboard and wires

**Hardware Setup for Automated Test:**

```
     CM4 Module
   ┌─────────────┐
   │             │
   │ GPIO 27 ────┼──────┐ (Output - Stimulus)
   │  (out)      │      │
   │             │      │
   │ GPIO 17 ────┼──────┘ (Input - Monitor)
   │  (in)       │
   │             │
   │ GND         ├────── Optional physical switch
   │             │
   └─────────────┘

GPIO 27 generates bouncing signal
GPIO 17 monitors the signal
```

**Hardware Setup for Manual Test:**

```
     CM4 Module
   ┌─────────────┐
   │             │
   │ GPIO 17 ────┼──────[Pull-up]──── 3.3V
   │  (in)       │            │
   │             │        [Button]
   │ GND         ├────────────┘
   │             │
   └─────────────┘

Physical button naturally produces bounce
```

### Software Requirements

**Required:**
- Linux OS (Raspberry Pi OS)
- Python 3.7+
- pytest

**Optional:**
- RPi.GPIO library (recommended)
- Root/sudo access (for GPIO operations)

### Installing Dependencies

```bash
# Install RPi.GPIO
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
groups  # Should include 'gpio'
```

## Running the Test

### Method 1: Direct Execution

```bash
# Navigate to test directory
cd tests/unit_tests/fw_hw_in_loop/

# Run Test #104 with verbose output
pytest test_104_debounce_robustness.py -v -s

# Run as Python script
python3 test_104_debounce_robustness.py
```

### Method 2: Run with Markers

```bash
# Run all hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all GPIO tests
pytest tests/unit_tests/ -m gpio -v

# Run only Test #104
pytest tests/unit_tests/fw_hw_in_loop/ -k "test_104" -v -s
```

### Method 3: Run as Part of Test Suite

```bash
# Run all FW HIL tests
pytest tests/unit_tests/fw_hw_in_loop/ -v

# Run all unit tests
pytest tests/unit_tests/ -v
```

## Expected Output

### Successful Test Execution (Automated)

```
======================================================================
Test Case #104: Debounce Robustness Against Bouncing Input
======================================================================

PURPOSE:
  Verify firmware debounce handles noisy/bouncing signals

DEBOUNCE PARAMETERS:
  Debounce time: 50ms
  Bounce duration: 20ms
  Bounce count: 5

HARDWARE:
  Input GPIO: 17
  Stimulus GPIO: 27
======================================================================

[STEP 1] Check Prerequisites
----------------------------------------------------------------------
✓ Running on Linux
✓ Device: Raspberry Pi Compute Module 4 Rev 1.0

[STEP 2] Initialize GPIO
----------------------------------------------------------------------
[2025-01-15 14:00:00.000] ✓ GPIO 17 (input) configured with PULL_UP
[2025-01-15 14:00:00.000] ✓ GPIO 27 (output) configured for bounce simulation
Initial GPIO state: 1
✓ GPIO initialized

[STEP 3] Test Simulated Bouncing (Automated)
----------------------------------------------------------------------

Simulating bouncing switch press with GPIO stimulus...
[2025-01-15 14:00:01.000] Monitoring GPIO for 2.0s...
[2025-01-15 14:00:01.200] Simulating bouncing press...
[2025-01-15 14:00:01.200]   Phase 1: Press with bounce
[2025-01-15 14:00:01.220]   Phase 2: Stable pressed state
[2025-01-15 14:00:01.720]   Phase 3: Release with bounce
[2025-01-15 14:00:01.740]   Phase 4: Stable released state

[2025-01-15 14:00:01.204]   Transition: 1 → 0 at 1736943601.204
[2025-01-15 14:00:01.208]   Transition: 0 → 1 at 1736943601.208
[2025-01-15 14:00:01.212]   Transition: 1 → 0 at 1736943601.212
[2025-01-15 14:00:01.216]   Transition: 0 → 1 at 1736943601.216
[2025-01-15 14:00:01.220]   Transition: 1 → 0 at 1736943601.220
... (10 more bounces during press)
[2025-01-15 14:00:01.724]   Transition: 0 → 1 at 1736943601.724
[2025-01-15 14:00:01.728]   Transition: 1 → 0 at 1736943601.728
... (10 more bounces during release)
[2025-01-15 14:00:01.744]   Transition: 0 → 1 at 1736943601.744

📊 Raw Signal Analysis:
   Total transitions detected: 22

   Raw transition timeline:
        0.0ms: LOW
        4.0ms: HIGH
        8.0ms: LOW
       12.0ms: HIGH
       16.0ms: LOW
     (press bouncing continues...)
      520.0ms: HIGH
      524.0ms: LOW
      528.0ms: HIGH
     (release bouncing continues...)
      544.0ms: HIGH

📊 Debounced Signal Analysis:
   Debounced transitions: 2

   Debounced transition timeline:
        0.0ms: LOW
      520.0ms: HIGH

📊 Press Event Detection:
   Detected press events: 1
   Expected press events: 1
   ✓ PASS: Exactly 1 press detected (correct debouncing)
   ✓ PASS: Transition count within limits (2 ≤ 2)

[STEP 4] Test Real Mechanical Switch (Manual)
----------------------------------------------------------------------

📋 MANUAL TEST:
   This tests debouncing with a real mechanical switch
   which naturally produces contact bounce

Do you want to perform manual switch test? (y/n): n

⚠️  Manual test skipped by user

[STEP 5] Verify Event Logging
----------------------------------------------------------------------
✓ Transition log contains 22 entries
  Log file: /tmp/gpio_transitions.log

  Sample entries (first 5):
    1736943601.204000,0
    1736943601.208000,1
    1736943601.212000,0
    1736943601.216000,1
    1736943601.220000,0

[Cleanup]
----------------------------------------------------------------------
✓ GPIO resources released

======================================================================
TEST RESULT: ✓ PASS
======================================================================

Acceptance Criteria Verification:
  ✓ Debounced switch status remains stable
  ✓ Only single action triggered per physical press
  ✓ False triggers from bouncing are ignored
  ✓ Debounce algorithm filters noise correctly

📄 Test log: /tmp/debounce_test.log
📄 Transition log: /tmp/gpio_transitions.log
======================================================================

PASSED                                                           [100%]
```

### Successful Test with Manual Switch Test

```
[STEP 4] Test Real Mechanical Switch (Manual)
----------------------------------------------------------------------

📋 MANUAL TEST:
   This tests debouncing with a real mechanical switch
   which naturally produces contact bounce

Do you want to perform manual switch test? (y/n): y

📋 INSTRUCTIONS:
   1. Press ENTER to start monitoring
   2. Press the physical switch ONCE
   3. Monitoring will automatically stop after 2 seconds

Press ENTER to start monitoring...
[User presses ENTER and then physical button]

[2025-01-15 14:00:10.000] Monitoring GPIO for 2.0s...
[2025-01-15 14:00:10.456]   Transition: 1 → 0 at 1736943610.456
[2025-01-15 14:00:10.460]   Transition: 0 → 1 at 1736943610.460
[2025-01-15 14:00:10.464]   Transition: 1 → 0 at 1736943610.464
[2025-01-15 14:00:10.789]   Transition: 0 → 1 at 1736943610.789
[2025-01-15 14:00:10.793]   Transition: 1 → 0 at 1736943610.793
[2025-01-15 14:00:10.797]   Transition: 0 → 1 at 1736943610.797

📊 Manual Test Results:
   Raw transitions detected: 6
   Debounced transitions: 2
   Detected press events: 1
   ✓ PASS: Single press detected correctly

   Bounce Analysis:
     Extra transitions due to bounce: 4
     Bounce successfully filtered: ✓
```

### Failed Test Examples

**Multiple Presses Detected (Debounce Failure):**
```
📊 Press Event Detection:
   Detected press events: 3
   Expected press events: 1
   ✗ FAIL: Multiple presses detected (3)

FAILED - Debounce algorithm failed - detected 3 presses instead of 1

Possible causes:
  - Debounce time too short (increase from 50ms to 100ms)
  - Polling rate too slow
  - Hardware issue
```

**No Press Detected:**
```
📊 Press Event Detection:
   Detected press events: 0
   Expected press events: 1
   ✗ FAIL: No press detected

FAILED - Debounce algorithm failed - no press detected

Possible causes:
  - Stimulus GPIO not connected
  - GPIO wiring issue
  - Debounce time too long
```

## Troubleshooting

### Issue 1: No Transitions Detected

**Error:**
```
Total transitions detected: 0
```

**Possible Causes:**
1. GPIO 27 (output) not connected to GPIO 17 (input)
2. GPIO pins not configured correctly
3. Permissions issue

**Solutions:**

```bash
# Verify GPIO wiring
# Connect GPIO 27 to GPIO 17 with jumper wire

# Test GPIO output manually
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Testing GPIO connection...")
for i in range(5):
    GPIO.output(27, GPIO.LOW)
    time.sleep(0.1)
    print(f"Set LOW, Read: {GPIO.input(17)}")

    GPIO.output(27, GPIO.HIGH)
    time.sleep(0.1)
    print(f"Set HIGH, Read: {GPIO.input(17)}")

GPIO.cleanup()
EOF

# Expected output: Read value should match output value
```

### Issue 2: Too Many Presses Detected

**Problem:** Debounce algorithm detects multiple presses instead of one

**Possible Causes:**
1. Debounce time too short
2. Bounce duration longer than expected
3. Algorithm implementation issue

**Solutions:**

**Increase debounce time:**
```python
'debounce_time': 0.1,  # Increase from 0.05 to 100ms
```

**Analyze bounce characteristics:**
```bash
# Check transition log for timing
cat /tmp/gpio_transitions.log

# Calculate time between transitions
python3 << 'EOF'
with open('/tmp/gpio_transitions.log', 'r') as f:
    lines = f.readlines()

timestamps = [float(line.split(',')[0]) for line in lines]

if len(timestamps) > 1:
    for i in range(1, len(timestamps)):
        delta = (timestamps[i] - timestamps[i-1]) * 1000  # ms
        print(f"Transition {i}: {delta:.1f}ms after previous")
EOF

# If transitions are > 50ms apart, increase debounce time
```

### Issue 3: Switch Bounces Not Filtered

**Problem:** Raw transitions show bouncing but debounce doesn't filter them

**Diagnosis:**

Check if bounces occur within debounce window:

```python
# Analyze transition log
import csv

with open('/tmp/gpio_transitions.log', 'r') as f:
    reader = csv.reader(f)
    transitions = [(float(row[0]), int(row[1])) for row in reader]

# Check time between consecutive transitions
for i in range(1, len(transitions)):
    time_diff = (transitions[i][0] - transitions[i-1][0]) * 1000
    print(f"Transition {i}: {time_diff:.1f}ms")

    if time_diff < 50:
        print(f"  ⚠️  Bounce within debounce window!")
```

**Solution:**

If bounces occur > 50ms apart (outside debounce window), they will be detected as separate events. This indicates:
- Switch has unusually long bounce duration
- Need longer debounce time
- Or switch is faulty

```python
# Increase debounce time
'debounce_time': 0.1,  # 100ms

# Or use different switch
```

### Issue 4: Stimulus GPIO Not Working

**Error:**
```
⚠️  No stimulus GPIO configured - cannot simulate bounce
```

**Cause:** GPIO 27 not available or not configured

**Solutions:**

```bash
# Check if GPIO 27 is available
ls -la /sys/class/gpio/gpio27

# If not, try different GPIO pin
# Edit test_config:
'stimulus_gpio_pin': 22,  # Use GPIO 22 instead

# Verify no other process is using GPIO 27
sudo lsof | grep gpio27
```

### Issue 5: Permission Denied

**Error:**
```
[Errno 13] Permission denied: '/dev/gpiomem'
```

**Solution:**

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and back in

# Or run with sudo (not recommended for production)
sudo pytest test_104_debounce_robustness.py -v -s
```

### Issue 6: Inconsistent Results

**Problem:** Sometimes passes, sometimes fails

**Possible Causes:**
1. System load affecting timing
2. Polling rate too slow
3. Bounce characteristics varying

**Solutions:**

**Reduce system load:**
```bash
# Check system load
uptime

# Close unnecessary applications
# Stop non-critical services
```

**Increase polling rate:**
```python
'poll_interval': 0.0005,  # Reduce from 0.001 to 0.5ms
```

**Run multiple test cycles:**
```bash
# Run test 10 times to check consistency
for i in {1..10}; do
    echo "Run $i:"
    pytest test_104_debounce_robustness.py -v -s
done
```

### Issue 7: Real Switch Shows No Bounce

**Problem:** Manual test shows very few transitions

**Explanation:** This is actually **good news**! Some high-quality switches have:
- Gold-plated contacts (less bounce)
- Internal debounce circuitry
- Precision manufacturing

**Verification:**

```bash
# Check if any bounce is present
cat /tmp/gpio_transitions.log

# If only 2 transitions (press + release), switch is very clean
# This validates debounce won't cause issues
```

**Note:** Most switches DO bounce. If no bounce is detected:
- Try different switch
- Or accept that this particular switch is high-quality
- Test still validates debounce algorithm works

## Test Configuration

### Default Configuration

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # GPIO Configuration
        'switch_gpio_pin': 17,      # Input pin
        'stimulus_gpio_pin': 27,    # Output pin (bounce generator)
        'gpio_mode': 'BCM',
        'pull_resistor': 'PULL_UP',

        # Debounce parameters
        'debounce_time': 0.05,      # 50ms debounce window
        'min_stable_time': 0.03,    # 30ms minimum stable

        # Bounce simulation
        'bounce_duration': 0.020,    # 20ms total bounce
        'bounce_count': 5,           # 5 bounces
        'bounce_interval': 0.004,    # 4ms between bounces

        # Test parameters
        'test_press_count': 5,
        'press_interval': 1.0,

        # Monitoring
        'monitor_duration': 2.0,     # 2 second monitoring
        'poll_interval': 0.001,      # 1ms poll rate

        # Expected behavior
        'max_allowed_triggers': 1,
        'max_state_changes': 2,      # Press + Release

        # Logging
        'enable_logging': True,
        'log_file': '/tmp/debounce_test.log',
        'event_log_file': '/tmp/debounce_events.log',
        'transition_log_file': '/tmp/gpio_transitions.log',
    }
```

### Customization Examples

**Example 1: Longer Debounce Time**
```python
'debounce_time': 0.1,  # 100ms for noisy environments
```

**Example 2: More Aggressive Bouncing**
```python
'bounce_count': 10,          # 10 bounces instead of 5
'bounce_duration': 0.040,    # 40ms instead of 20ms
'bounce_interval': 0.004,    # 4ms between each
```

**Example 3: Different GPIO Pins**
```python
'switch_gpio_pin': 22,       # BCM GPIO 22
'stimulus_gpio_pin': 23,     # BCM GPIO 23
```

**Example 4: Faster Polling**
```python
'poll_interval': 0.0005,     # 0.5ms (2000 Hz polling)
```

**Example 5: Keyboard-style Debounce**
```python
'debounce_time': 0.01,       # 10ms (fast response)
'bounce_count': 3,           # Fewer bounces expected
```

## Comparison with Related Tests

| Aspect | Test #102 (State) | Test #103 (Timing) | Test #104 (Debounce) |
|--------|-------------------|--------------------|-----------------------|
| **Focus** | State reading | Press duration | Bounce filtering |
| **Measurement** | ON/OFF state | Milliseconds | Transition count |
| **Validation** | Correct state | Correct classification | Single event |
| **Bounce Handling** | Implicit | Implicit | **Explicit** |
| **Test Method** | Manual | Manual (timed) | Automated + Manual |
| **Complexity** | Simple | Medium | Advanced |
| **Duration** | ~2-3 min | ~3-5 min | ~2-4 min |

### When to Use Test #104

- ✅ Validate debounce algorithm implementation
- ✅ Test bounce filtering effectiveness
- ✅ Verify no false triggers from noisy signals
- ✅ Measure bounce characteristics of switches
- ✅ Production qualification of switch hardware
- ✅ Debug multiple-press issues

### When Test #104 is NOT Sufficient

- ❌ Testing basic GPIO functionality (use Test #102)
- ❌ Testing press timing classification (use Test #103)
- ❌ Testing interrupt-based debounce
- ❌ Testing analog signal debounce
- ❌ High-frequency signal analysis (> 1kHz)

## Advanced Usage

### Bounce Characterization

Measure actual bounce characteristics of your switch:

```python
#!/usr/bin/env python3
"""Characterize switch bounce"""
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Press button and hold...")
input("Press ENTER then press button...")

transitions = []
last_state = GPIO.input(17)
start_time = time.time()

# Monitor for 2 seconds
while (time.time() - start_time) < 2.0:
    current_state = GPIO.input(17)

    if current_state != last_state:
        timestamp = time.time() - start_time
        transitions.append((timestamp, current_state))
        last_state = current_state

    time.sleep(0.0001)  # 0.1ms polling

GPIO.cleanup()

# Analyze bounce
if len(transitions) > 0:
    print(f"\nTotal transitions: {len(transitions)}")
    print("\nTransition timeline:")

    for i, (ts, state) in enumerate(transitions[:20]):
        print(f"  {ts*1000:6.1f}ms: {'HIGH' if state else 'LOW '}")

    # Calculate bounce duration
    if len(transitions) >= 2:
        bounce_start = transitions[0][0]
        bounce_end = transitions[-1][0]
        bounce_duration = (bounce_end - bounce_start) * 1000

        print(f"\nBounce duration: {bounce_duration:.1f}ms")
        print(f"Recommended debounce time: {bounce_duration * 1.5:.1f}ms")
```

### Testing Different Debounce Algorithms

Compare different debounce implementations:

```python
def time_based_debounce(transitions, debounce_time):
    """Time-based: ignore changes within debounce window"""
    debounced = []
    last_time = 0

    for ts, state in transitions:
        if (ts - last_time) >= debounce_time:
            debounced.append((ts, state))
            last_time = ts

    return debounced

def state_based_debounce(transitions, sample_count):
    """State-based: require N consistent readings"""
    debounced = []
    state_buffer = deque(maxlen=sample_count)

    for ts, state in transitions:
        state_buffer.append(state)

        if len(state_buffer) == sample_count:
            if all(s == state for s in state_buffer):
                debounced.append((ts, state))

    return debounced

def integrator_debounce(transitions, threshold):
    """Integrator: increment/decrement counter"""
    debounced = []
    counter = threshold // 2
    last_output = None

    for ts, state in transitions:
        if state == 0:  # LOW (pressed)
            counter = max(0, counter - 1)
        else:  # HIGH (released)
            counter = min(threshold, counter + 1)

        # Output changes when counter hits limits
        output = 0 if counter == 0 else (1 if counter == threshold else last_output)

        if output != last_output and output is not None:
            debounced.append((ts, output))
            last_output = output

    return debounced

# Test all algorithms
print("Time-based:", len(time_based_debounce(transitions, 0.05)))
print("State-based:", len(state_based_debounce(transitions, 5)))
print("Integrator:", len(integrator_debounce(transitions, 10)))
```

### Production Testing with Solenoid

Automate bounce testing for production:

```python
import RPi.GPIO as GPIO
import time

SOLENOID_PIN = 27  # Controls mechanical actuator
SENSE_PIN = 17     # Monitors switch output

def automated_bounce_test(press_count=100):
    """Test switch bounce characteristics over many cycles"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOLENOID_PIN, GPIO.OUT)
    GPIO.setup(SENSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    bounce_stats = []

    for i in range(press_count):
        # Actuate solenoid to press button
        GPIO.output(SOLENOID_PIN, GPIO.HIGH)

        # Monitor transitions
        transitions = []
        last_state = GPIO.input(SENSE_PIN)
        start = time.time()

        while (time.time() - start) < 0.1:  # 100ms window
            state = GPIO.input(SENSE_PIN)
            if state != last_state:
                transitions.append(time.time())
                last_state = state

        GPIO.output(SOLENOID_PIN, GPIO.LOW)

        # Record bounce count
        bounce_stats.append(len(transitions))
        time.sleep(0.5)  # Wait between presses

    GPIO.cleanup()

    # Analyze
    print(f"Tested {press_count} presses")
    print(f"Average bounces: {sum(bounce_stats) / len(bounce_stats):.1f}")
    print(f"Max bounces: {max(bounce_stats)}")
    print(f"Min bounces: {min(bounce_stats)}")

automated_bounce_test()
```

## CI/CD Integration

### GitLab CI Example

```yaml
test:fw-hil:debounce:
  stage: test
  tags:
    - cm4
    - hardware
    - hil
  script:
    - sudo apt-get update && sudo apt-get install -y python3-rpi.gpio

    # Connect GPIO 27 to GPIO 17 for automated test
    - echo "Ensure GPIO 27 is wired to GPIO 17"

    # Run automated debounce test
    - pytest test_104_debounce_robustness.py -v -s

    # Upload logs
    - mkdir -p artifacts
    - cp /tmp/debounce_test.log artifacts/
    - cp /tmp/gpio_transitions.log artifacts/

  artifacts:
    when: always
    paths:
      - artifacts/
    expire_in: 7 days
  allow_failure: false  # Debounce must work correctly
```

### GitHub Actions Example

```yaml
name: FW HIL - Debounce Test

on:
  push:
    paths:
      - 'firmware/gpio/**'
      - 'tests/fw_hw_in_loop/test_104_**'

jobs:
  test-debounce:
    runs-on: [self-hosted, cm4, hardware]

    steps:
      - uses: actions/checkout@v3

      - name: Install Dependencies
        run: |
          pip install -r tests/requirements.txt
          sudo apt-get install -y python3-rpi.gpio

      - name: Verify GPIO Wiring
        run: |
          echo "Checking GPIO 27 -> GPIO 17 connection..."
          # Add hardware verification script

      - name: Run Debounce Test
        run: |
          pytest test_104_debounce_robustness.py -v -s

      - name: Upload Transition Log
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: gpio-transitions
          path: /tmp/gpio_transitions.log
```

## Use Cases

### Use Case 1: Switch Qualification

**Scenario:** Qualify new switch model for production

**Procedure:**
1. Run Test #104 with new switch
2. Analyze bounce characteristics
3. Verify debounce algorithm handles bounce
4. Document bounce duration for spec

### Use Case 2: Firmware Debounce Validation

**Scenario:** Validate firmware debounce implementation

**Procedure:**
1. Run automated test with simulated bouncing
2. Verify only 1 press detected despite 22 transitions
3. Confirm debounce time is appropriate
4. Test passes = debounce working correctly

### Use Case 3: Field Failure Investigation

**Scenario:** Users report "double-click" issue

**Diagnosis:**
1. Run Test #104 to reproduce issue
2. Check if multiple presses detected
3. Analyze transition log for bounce patterns
4. Determine if debounce time needs increase

### Use Case 4: Production Line Testing

**Scenario:** Validate every unit's switch operation

**Automation:**
1. Use solenoid to actuate button
2. Run automated debounce test
3. Verify bounce < 20ms
4. Flag units with excessive bounce

## Summary

Test #104 validates firmware debounce robustness by:

1. ✅ **Bounce Simulation** - Generates realistic bouncing signal (5 bounces over 20ms)
2. ✅ **Transition Monitoring** - Records all GPIO state changes with 1ms precision
3. ✅ **Debounce Application** - Applies 50ms time-based debounce algorithm
4. ✅ **Event Counting** - Verifies exactly 1 press detected despite 20+ transitions
5. ✅ **Manual Testing** - Optional test with real mechanical switch
6. ✅ **Logging** - Records all transitions for post-test analysis

**Key Features:**
- Partially automated (simulated bouncing) + manual option
- Realistic bounce simulation (5 bounces, 4ms interval)
- Millisecond-accurate transition logging
- Software debounce validation
- Supports both RPi.GPIO and sysfs
- Comprehensive bounce characterization

**Test Duration:** ~2-4 minutes

**Pass Criteria:**
- Raw signal shows multiple transitions (bouncing present)
- Debounced signal shows only 2 transitions (press + release)
- Exactly 1 press event detected
- No false triggers

**Hardware Requirements:**
- Two GPIO pins (27 for stimulus, 17 for monitoring)
- Wire connecting output to input
- Optional: Physical button for manual test

**Debounce Times:**
- Standard buttons: 50ms
- Keyboards: 10ms
- Toggle switches: 100ms
- This test uses: 50ms (standard)

For questions or issues, check the logs:
- Test log: `/tmp/debounce_test.log`
- Transition log: `/tmp/gpio_transitions.log`
