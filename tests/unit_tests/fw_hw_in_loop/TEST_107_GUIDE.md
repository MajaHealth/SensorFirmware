# Test Case #107: Hard Shutdown Bypass (Long Press)

## Category: FW Hardware-in-Loop Test

## Quick Reference

```bash
# Run test
pytest tests/unit_tests/fw_hw_in_loop/test_107_hard_shutdown_bypass.py -v -s

# Run with specific markers
pytest -m "hardware and gpio" tests/unit_tests/fw_hw_in_loop/test_107_hard_shutdown_bypass.py -v -s
```

## Test Overview

| Attribute | Value |
|-----------|-------|
| **Test ID** | 107 |
| **Category** | FW Hardware-in-Loop |
| **Component** | CM4 GPIO trigger + Firmware |
| **Duration** | ~10-15 seconds |
| **Automation** | Semi-automated (manual long press or simulated) |
| **Hardware Required** | GPIO access, OFF switch |

## Purpose

This test verifies that a **LONG PRESS** of the OFF switch:

1. **Bypasses the application handshake** - No "close" message sent
2. **Triggers immediate power down** - No waiting for ACK
3. **Logs the hard shutdown event** - Audit trail for debugging
4. **Does NOT perform graceful termination** - No "shutdown complete" exchange

---

## Hard Shutdown vs Graceful Shutdown

### Comparison Table

| Aspect | Graceful Shutdown (Short Press) | Hard Shutdown (Long Press) |
|--------|--------------------------------|---------------------------|
| **Press Duration** | 0.5 - 1 second | 3+ seconds |
| **App Notification** | Yes ("close" message) | No |
| **ACK Required** | Yes | No |
| **Data Saving** | App has time to save | No time - immediate |
| **Total Time** | 500ms - 2 seconds | ~100ms after detection |
| **Use Case** | Normal shutdown | Emergency / App unresponsive |
| **Log Entry** | "CDSS soft shutdown" | "[GPIO] Hard shutdown triggered - Step 1" |

### Visual Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GRACEFUL SHUTDOWN (Test #105)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  User          Firmware              Application                        │
│    │               │                      │                             │
│    │──SHORT PRESS──│                      │                             │
│    │   (0.5-1s)    │                      │                             │
│    │               │───── "close" ───────→│                             │
│    │               │                      │ (saves data)                │
│    │               │                      │ (closes connections)        │
│    │               │←─── "ACK" ──────────│                             │
│    │               │                      │                             │
│    │               │─"shutdown initiated"→│                             │
│    │               │                      │                             │
│    │          [SHUTDOWN]                  │                             │
│    │               │                      │                             │
│                                                                         │
│  Timeline: ~500ms - 2 seconds                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    HARD SHUTDOWN (Test #107) - THIS TEST                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  User          Firmware              Application                        │
│    │               │                      │                             │
│    │──LONG PRESS───│                      │                             │
│    │   (3+ sec)    │                      │                             │
│    │               │                      │                             │
│    │   [DETECTED]  │                      │                             │
│    │               │                      │                             │
│    │          [LOG: Hard shutdown]        │                             │
│    │               │                      │                             │
│    │          [IMMEDIATE SHUTDOWN]        │  (NOT notified!)            │
│    │               │                      │                             │
│    │          [POWER OFF]                 │                             │
│    │               │                      │                             │
│                                                                         │
│  Timeline: ~100ms after detection                                       │
│  NO MESSAGES TO APPLICATION!                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Timing Diagram

```
LONG PRESS TIMELINE:

Time (ms)    Event
─────────────────────────────────────────────────────────────────────
   0         User presses OFF button (GPIO goes LOW)
             │
 500         Still held... (short press threshold passed)
             │
1000         Still held...
             │
2000         Still held...
             │
3000 ───────►LONG PRESS DETECTED (threshold reached)
             │
3010         Firmware logs: "[GPIO] Hard shutdown triggered - Step 1"
             │
3020         Firmware initiates immediate power off
             │
             │  ╔══════════════════════════════════════════╗
             │  ║  NO "close" message sent!                ║
             │  ║  NO ACK expected!                        ║
             │  ║  NO waiting for application!             ║
             │  ╚══════════════════════════════════════════╝
             │
3050         Power rails disabled
             │
3100         Device OFF
─────────────────────────────────────────────────────────────────────

Total time from detection to OFF: ~100ms
Application is NOT involved!
```

---

## Why Hard Shutdown Exists

### Use Cases

1. **Application Unresponsive**
   - App has crashed or frozen
   - App not responding to "close" message
   - Graceful shutdown timeout exceeded
   - Cannot wait indefinitely

2. **Emergency Situations**
   - Safety concern requires immediate power off
   - User needs to stop device NOW
   - Override normal shutdown sequence
   - Critical error recovery

3. **Development/Testing**
   - Force restart during debugging
   - Recover from stuck states
   - Test power management
   - Clear hung processes

4. **Battery Critical**
   - Battery too low for graceful shutdown
   - Need to preserve remaining power
   - Fast shutdown to protect hardware

### Real-World Scenarios

```
┌──────────────────────────────────────────────────────────────────┐
│  SCENARIO 1: Medical Device - App Frozen                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Situation:                                                      │
│    - ECG monitoring app has frozen                               │
│    - Patient data displayed but app unresponsive                 │
│    - Graceful shutdown fails (no ACK received)                   │
│                                                                  │
│  Action:                                                         │
│    - User holds OFF button for 3+ seconds                        │
│    - Hard shutdown triggered                                     │
│    - Device powers off immediately                               │
│                                                                  │
│  Result:                                                         │
│    - Device can be restarted fresh                               │
│    - Unsaved data may be lost (acceptable tradeoff)              │
│    - User regains control of device                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  SCENARIO 2: Industrial Controller - Safety Override             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Situation:                                                      │
│    - Unexpected behavior detected                                │
│    - Need to stop device immediately                             │
│    - Cannot wait for graceful shutdown                           │
│                                                                  │
│  Action:                                                         │
│    - Operator holds STOP button (3+ seconds)                     │
│    - Hard shutdown bypasses all software                         │
│    - Power cut immediately                                       │
│                                                                  │
│  Result:                                                         │
│    - Device stopped within 100ms                                 │
│    - Safety ensured                                              │
│    - Can investigate after restart                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Test Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TEST #107 ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   OFF Switch    │  GPIO 17 (BCM)                                 │
│  │   (Simulated)   │  Pull-up resistor                              │
│  └────────┬────────┘                                                │
│           │                                                         │
│           │ LONG PRESS (3+ seconds)                                 │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │    Firmware     │  Detects long press                            │
│  │   (Simulated)   │  Logs: "[GPIO] Hard shutdown triggered"        │
│  │                 │  Initiates immediate power off                 │
│  └────────┬────────┘                                                │
│           │                                                         │
│           │ NO MESSAGES!                                            │
│           │                                                         │
│  ┌────────┴────────┐                                                │
│  │  Mock App       │  Port 8766                                     │
│  │  (Monitoring)   │  Should receive NOTHING                        │
│  │                 │  Verifies bypass worked                        │
│  └─────────────────┘                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### MockApplication Role

In Test #107, the MockApplication serves a **verification purpose**:

```python
class MockApplication:
    """
    Mock application that monitors for any shutdown messages.
    For Test #107, this should NOT receive any messages.

    Purpose:
    - Start TCP server (same as graceful shutdown test)
    - Monitor for any incoming messages
    - Verify that NO messages are received
    - Confirm hard shutdown bypassed the app

    Expected behavior:
    - messages_received = []  (empty!)
    - received_close = False
    - received_any_message = False
    - ack_sent = False
    """
```

---

## Test Configuration

```python
test_config = {
    # GPIO Configuration
    'switch_gpio_pin': 17,           # BCM pin for OFF switch
    'power_status_gpio_pin': 27,     # BCM pin to monitor power
    'gpio_mode': 'BCM',
    'pull_resistor': 'PULL_UP',

    # Press timing
    'long_press_duration': 3.0,      # 3 seconds = hard shutdown
    'short_press_duration': 0.5,     # 0.5 seconds = graceful (for reference)

    # TCP/IP Configuration
    'mock_app_host': '127.0.0.1',
    'mock_app_port': 8766,           # Different from Test #105

    # Timing
    'power_down_timeout': 5.0,       # Max wait for power down
    'message_wait_timeout': 2.0,     # Wait to catch any messages

    # Logging
    'enable_logging': True,
    'log_file': '/tmp/hard_shutdown_test.log',
    'firmware_log_file': '/var/log/syslog',

    # Expected log entry
    'expected_log_entry': '[GPIO] Hard shutdown triggered - Step 1',

    # Forbidden messages (should NOT appear)
    'forbidden_messages': [
        'close',
        'shutdown_initiated',
        'graceful',
        'ACK',
    ],
}
```

---

## Test Steps

### Step-by-Step Execution

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: Check Prerequisites                                        │
├─────────────────────────────────────────────────────────────────────┤
│  - Verify running on Linux                                          │
│  - Check for root permissions (optional)                            │
│  - Verify GPIO access available                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Initialize Mock Application                                │
├─────────────────────────────────────────────────────────────────────┤
│  - Start TCP server on port 8766                                    │
│  - Begin monitoring for any messages                                │
│  - Note: Should receive NOTHING during this test                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Initialize GPIO                                            │
├─────────────────────────────────────────────────────────────────────┤
│  - Configure GPIO 17 as output (to simulate switch)                 │
│  - Configure GPIO 27 as input (to monitor power status)             │
│  - Set initial state HIGH (button not pressed)                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Verify Initial State                                       │
├─────────────────────────────────────────────────────────────────────┤
│  - Confirm mock app has received no messages (count = 0)            │
│  - Verify device is powered on                                      │
│  - Clear any previous log files                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: Simulate LONG Press (3+ seconds)                           │
├─────────────────────────────────────────────────────────────────────┤
│  - Press button (GPIO LOW)                                          │
│  - Hold for 3+ seconds                                              │
│  - Release button (GPIO HIGH)                                       │
│  - Record actual press duration                                     │
│  - Verify duration meets threshold                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: Firmware Detects Hard Shutdown                             │
├─────────────────────────────────────────────────────────────────────┤
│  - Firmware recognizes long press pattern                           │
│  - Logs: "[GPIO] Hard shutdown triggered - Step 1"                  │
│  - Bypasses application communication                               │
│  - Initiates immediate power down sequence                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 7: Verify NO Messages Sent to App                             │
├─────────────────────────────────────────────────────────────────────┤
│  - Wait briefly for any messages (2 seconds)                        │
│  - Check mock app message count (should be 0)                       │
│  - Verify no "close" message received                               │
│  - Verify no "shutdown initiated" received                          │
│  - PASS if no messages received                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 8: Verify NO ACK Expected/Received                            │
├─────────────────────────────────────────────────────────────────────┤
│  - Confirm mock app did not send ACK                                │
│  - Confirm no ACK was expected by firmware                          │
│  - PASS if no ACK exchange occurred                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 9: Verify Immediate Power Down                                │
├─────────────────────────────────────────────────────────────────────┤
│  - Monitor power status GPIO                                        │
│  - Wait for power down (max 5 seconds)                              │
│  - Record time to power down                                        │
│  - Verify power down was "immediate" (< 1 second)                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 10: Verify Firmware Logs                                      │
├─────────────────────────────────────────────────────────────────────┤
│  - Check system logs (journalctl, syslog)                           │
│  - Search for: "[GPIO] Hard shutdown triggered - Step 1"            │
│  - Verify hard shutdown was logged correctly                        │
│  - Check test firmware log file                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 11: Verify NO Graceful Termination                            │
├─────────────────────────────────────────────────────────────────────┤
│  - Check for graceful shutdown indicators                           │
│  - Verify NO "close" message                                        │
│  - Verify NO "shutdown initiated"                                   │
│  - Verify NO ACK sent                                               │
│  - PASS if none detected                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLEANUP & RESULTS                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  - Stop mock application                                            │
│  - Cleanup GPIO                                                     │
│  - Report test results                                              │
│  - Display acceptance criteria verification                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

| Criterion | Expected | Verification Method |
|-----------|----------|---------------------|
| Long press detected | ≥ 3.0 seconds | Timer measurement |
| "close" message sent | NO | Mock app message count = 0 |
| ACK received | NO | Mock app ack_sent = False |
| Power down timing | Immediate (< 1s) | GPIO monitoring |
| Log entry present | "[GPIO] Hard shutdown triggered - Step 1" | Log file search |
| Graceful termination | None observed | No shutdown exchange messages |

### Pass/Fail Criteria

```
PASS Conditions (ALL must be true):
  ✓ Long press duration ≥ 3.0 seconds
  ✓ Mock app received 0 messages
  ✓ No "close" message detected
  ✓ No ACK was sent or received
  ✓ Device powered down immediately
  ✓ Log contains hard shutdown entry
  ✓ No graceful termination indicators

FAIL Conditions (ANY triggers failure):
  ✗ Press duration < 3.0 seconds (not a long press)
  ✗ Mock app received any message
  ✗ "close" message was sent
  ✗ ACK was exchanged
  ✗ Power down took > 5 seconds
  ✗ Expected log entry not found
  ✗ Graceful shutdown indicators detected
```

---

## Hardware Setup

### GPIO Connections

```
┌─────────────────────────────────────────────────────────────────────┐
│                      RASPBERRY PI CM4                               │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      GPIO HEADER                             │   │
│  │                                                              │   │
│  │  GPIO 17 (BCM) ──────────┬──────────── OFF Switch           │   │
│  │  Pin 11                  │                                   │   │
│  │                          │                                   │   │
│  │                        [10kΩ]  Pull-up resistor              │   │
│  │                          │     (internal or external)        │   │
│  │                          │                                   │   │
│  │  3.3V ───────────────────┘                                   │   │
│  │                                                              │   │
│  │                                                              │   │
│  │  GPIO 27 (BCM) ──────────────────────── Power Status         │   │
│  │  Pin 13                                 (monitor)            │   │
│  │                                                              │   │
│  │                                                              │   │
│  │  GND ────────────────────────────────── Common Ground        │   │
│  │  Pin 6, 9, 14, 20, 25, 30, 34, 39                            │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Switch Behavior

```
Switch States:

IDLE (Not Pressed):
  GPIO 17 = HIGH (pulled up to 3.3V)

PRESSED:
  GPIO 17 = LOW (connected to GND through switch)

Detection Logic:
  if GPIO_LOW for < 1 second → SHORT PRESS (graceful shutdown)
  if GPIO_LOW for ≥ 3 seconds → LONG PRESS (hard shutdown)
```

---

## Log Entry Requirements

### Expected Firmware Log

```
Format:
[GPIO] Hard shutdown triggered - Step 1

Full log line example:
2026-01-15 10:30:45.123 firmware[12345]: [GPIO] Hard shutdown triggered - Step 1
```

### Log Entry Breakdown

| Component | Description |
|-----------|-------------|
| `[GPIO]` | Indicates GPIO-triggered event |
| `Hard shutdown` | Distinguishes from graceful/soft shutdown |
| `triggered` | Event was initiated |
| `Step 1` | First step in hard shutdown sequence |

### Why "Step 1"?

The hard shutdown may have multiple steps:
- **Step 1**: Trigger detected, bypass app
- **Step 2**: Disable peripherals (optional)
- **Step 3**: Power rails off

For Test #107, we only verify Step 1 (the trigger detection).

---

## Running the Test

### Basic Execution

```bash
# Navigate to project root
cd /home/kranti/sensor_test_project

# Run test
pytest tests/unit_tests/fw_hw_in_loop/test_107_hard_shutdown_bypass.py -v -s
```

### With Markers

```bash
# Run all hardware tests
pytest -m hardware tests/unit_tests/ -v -s

# Run all GPIO tests
pytest -m gpio tests/unit_tests/ -v -s

# Run this specific test
pytest tests/unit_tests/fw_hw_in_loop/test_107_hard_shutdown_bypass.py::TestHardShutdownBypass::test_107_hard_shutdown_bypass -v -s
```

### Expected Output

```
=======================================================================
Test Case #107: Hard Shutdown Bypass (Long Press)
=======================================================================

PURPOSE:
  Verify long press bypasses app handshake and triggers immediate shutdown

EXPECTED BEHAVIOR:
  1. Long press (3+ seconds) detected
  2. NO 'close' message to app
  3. NO ACK expected/received
  4. Immediate power down
  5. Log: '[GPIO] Hard shutdown triggered - Step 1'

CONFIGURATION:
  GPIO Pin: 17
  Long Press Duration: 3.0s
  Mock App Port: 8766 (should receive NO messages)
=======================================================================

[STEP 1] Check Prerequisites
----------------------------------------------------------------------
✓ Running on Linux

[STEP 2] Initialize Mock Application
----------------------------------------------------------------------
  Note: Mock app should receive NO messages during hard shutdown
Mock app started on 127.0.0.1:8766
✓ Mock application started
  ℹ️  Mock app will monitor for any messages (expecting NONE)

[STEP 3] Initialize GPIO
----------------------------------------------------------------------
✓ GPIO initialized

[STEP 4] Verify Initial State
----------------------------------------------------------------------
✓ Mock app message count: 0 (expected: 0)
✓ Device is powered on

[STEP 5] Simulate LONG Press (Hard Shutdown Trigger)
----------------------------------------------------------------------

  ⏱️  Long press duration: 3.0s
  📌 This should trigger HARD shutdown (bypass app)

📋 MANUAL ACTION:
   Press and HOLD the OFF switch for 3.0 seconds (LONG PRESS)
   This should trigger HARD shutdown (bypass app)
   Press ENTER after performing long press...

✓ Long press completed
  Duration: 3.00s
  Threshold: 3.0s
  ✓ Duration meets long press threshold

[STEP 6] Firmware Detects Hard Shutdown
----------------------------------------------------------------------
✓ Firmware detected long press
  → Logged: '[GPIO] Hard shutdown triggered - Step 1'
  → Bypassing application handshake
  → Initiating immediate power down

[STEP 7] Verify NO Messages Sent to Mock App
----------------------------------------------------------------------
  Messages received by mock app: 0
  'close' message received: No ✓
  'shutdown initiated' received: No ✓

  ✓ PASS: No messages sent to application
  ✓ Application handshake was bypassed correctly

[STEP 8] Verify NO ACK Expected/Received
----------------------------------------------------------------------
  ACK sent by mock app: No ✓

  ✓ PASS: No ACK was sent
  ✓ No ACK was expected (hard shutdown)

[STEP 9] Verify Immediate Power Down
----------------------------------------------------------------------

📋 VERIFICATION:
   Did the device power down immediately?
   Enter 'y' for yes, 'n' for no: y

✓ Device powered down
  Time to power down: 0.50s
  ✓ PASS: Power down was immediate

[STEP 10] Verify Firmware Logs
----------------------------------------------------------------------
  Expected log entry: '[GPIO] Hard shutdown triggered - Step 1'

✓ Found 1 matching log entries:
  → 2026-01-15 10:30:45.123 firmware[12345]: [GPIO] Hard shutdown triggered - Step 1

  ✓ PASS: Hard shutdown trigger logged correctly

[STEP 11] Verify NO Graceful Termination Exchange
----------------------------------------------------------------------
  Checking for graceful shutdown indicators:
    close message: ✓ Not detected
    shutdown initiated: ✓ Not detected
    ACK sent: ✓ Not detected
    any message: ✓ Not detected

  ✓ PASS: No graceful termination exchange observed

[Cleanup]
----------------------------------------------------------------------
Mock app stopped
✓ Cleanup completed

=======================================================================
TEST RESULT: ✓ PASS
=======================================================================

✓ Acceptance Criteria Verification:
  ✓ Long press detected correctly
  ✓ No 'close' message sent to app
  ✓ No ACK expected/received
  ✓ Device powers down immediately
  ✓ Log includes: '[GPIO] Hard shutdown triggered - Step 1'
  ✓ No graceful termination or 'shutdown complete' exchange observed

📊 Test Statistics:
  Long press duration: 3.00s
  Messages to app: 0 (expected: 0)
  ACK exchanged: No
  Shutdown type: HARD (bypassed app)

📄 Test log: /tmp/hard_shutdown_test.log
📄 Firmware log: /tmp/firmware_test.log
=======================================================================
```

---

## Troubleshooting

### 1. Mock App Receives Messages

**Problem:** Mock app received messages during hard shutdown test

**Possible Causes:**
- Press duration too short (treated as graceful shutdown)
- Firmware not correctly detecting long press
- Threshold configuration mismatch

**Solutions:**
```bash
# Verify press duration
# Ensure button held for full 3 seconds

# Check firmware threshold configuration
# Default: 3.0 seconds for hard shutdown

# Increase press duration
test_config['long_press_duration'] = 4.0  # Try 4 seconds
```

### 2. Log Entry Not Found

**Problem:** Expected log entry not in firmware logs

**Possible Causes:**
- Firmware logging not enabled
- Log rotation cleared entry
- Wrong log file location

**Solutions:**
```bash
# Check firmware log manually
journalctl -n 100 | grep -i "hard shutdown"
cat /var/log/syslog | grep -i "hard shutdown"
cat /tmp/firmware_test.log

# Verify logging is enabled
# Check firmware configuration
```

### 3. Power Down Not Detected

**Problem:** Cannot verify immediate power down

**Possible Causes:**
- GPIO monitoring not configured
- Simulation mode active
- Power status GPIO incorrect

**Solutions:**
```bash
# Check power status GPIO
cat /sys/class/gpio/gpio27/value

# Manual verification in simulation mode
# Answer 'y' when prompted about power down
```

### 4. GPIO Access Denied

**Problem:** Permission denied accessing GPIO

**Solutions:**
```bash
# Add user to gpio group
sudo usermod -aG gpio $USER

# Or run with sudo
sudo pytest tests/unit_tests/fw_hw_in_loop/test_107_hard_shutdown_bypass.py -v -s

# Check GPIO permissions
ls -la /sys/class/gpio/
ls -la /dev/gpiochip*
```

### 5. Press Duration Too Short

**Problem:** Long press not recognized as long press

**Possible Causes:**
- Timing measurement inaccurate
- Button released early
- System lag during timing

**Solutions:**
```bash
# Increase press duration slightly
test_config['long_press_duration'] = 3.5  # 3.5 seconds

# Hold button extra time to ensure threshold met
# Count "one-one-thousand, two-one-thousand, three-one-thousand"
```

---

## Relationship to Test #105 and #106

### Test Comparison

| Test | Shutdown Type | App Involved | ACK Required | Press Duration |
|------|---------------|--------------|--------------|----------------|
| #105 | Graceful (ACK accepted) | Yes | Yes | Short (0.5s) |
| #106 | Graceful (ACK denied) | Yes | Yes (timeout) | Short (0.5s) |
| #107 | Hard (bypass) | No | No | Long (3s) |

### Test Sequence

```
Recommended testing order:

1. Test #105 - Graceful Shutdown (ACK Accepted)
   ├── Verify normal shutdown flow works
   └── Confirm app handshake functions

2. Test #106 - Graceful Shutdown (ACK Denied/Timeout)
   ├── Verify timeout handling works
   └── Confirm recovery from unresponsive app

3. Test #107 - Hard Shutdown (Long Press)  ← THIS TEST
   ├── Verify bypass mechanism works
   └── Confirm emergency shutdown available
```

### Code Reuse

Test #107 reuses the `MockApplication` class from Test #105 but uses it differently:

```python
# Test #105 - MockApplication sends messages:
mock_app.start()
# ... firmware connects, sends "close"
# mock_app receives "close", sends ACK

# Test #107 - MockApplication monitors only:
mock_app.start()
# ... firmware does NOT connect
# mock_app receives NOTHING (verifies bypass)
```

---

## CI/CD Integration

### GitLab CI Example

```yaml
test:hard_shutdown:
  stage: test
  tags:
    - hardware
    - gpio
  script:
    - pytest tests/unit_tests/fw_hw_in_loop/test_107_hard_shutdown_bypass.py -v -s --junitxml=test_107_report.xml
  artifacts:
    reports:
      junit: test_107_report.xml
    paths:
      - /tmp/hard_shutdown_test.log
      - /tmp/firmware_test.log
    when: always
  allow_failure: false
  timeout: 60s
```

### Automated Test Considerations

For fully automated testing (without manual button press):

```python
# In test_config, configure for automation:
test_config = {
    # Use GPIO simulation
    'use_gpio_simulation': True,

    # Or configure hardware button presser
    'hardware_button_presser': {
        'enabled': True,
        'gpio_control_pin': 22,  # GPIO to control button presser
    }
}
```

---

## Summary

**Test #107** validates the **hard shutdown bypass mechanism** which is a critical safety feature:

- **Purpose**: Emergency power off without waiting for application
- **Trigger**: Long press of OFF switch (≥ 3 seconds)
- **Behavior**: Bypass application handshake, immediate power down
- **Verification**: No messages to app, correct log entry, fast shutdown

This test complements Test #105 (graceful shutdown) and Test #106 (shutdown timeout) to provide complete coverage of the shutdown subsystem.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEST #107 QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Run:     pytest .../test_107_hard_shutdown_bypass.py -v -s         │
│                                                                     │
│  Trigger: LONG PRESS (3+ seconds)                                   │
│                                                                     │
│  Expect:                                                            │
│    ✓ No messages to app                                             │
│    ✓ No ACK exchange                                                │
│    ✓ Immediate power down                                           │
│    ✓ Log: "[GPIO] Hard shutdown triggered - Step 1"                 │
│                                                                     │
│  GPIO:    17 (switch), 27 (power status)                            │
│                                                                     │
│  Port:    8766 (mock app monitoring)                                │
│                                                                     │
│  Logs:    /tmp/hard_shutdown_test.log                               │
│           /tmp/firmware_test.log                                    │
│                                                                     │
│  Duration: ~10-15 seconds                                           │
│                                                                     │
│  Key Difference from #105/#106:                                     │
│    - BYPASSES application entirely                                  │
│    - NO TCP communication                                           │
│    - IMMEDIATE shutdown                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
