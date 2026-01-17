# Test Case #108: Shutdown Initiated Status Message to App

## Category: FW Hardware-in-Loop Test

## Quick Reference

```bash
# Run test
pytest tests/unit_tests/fw_hw_in_loop/test_108_shutdown_initiated_status.py -v -s

# Run with specific markers
pytest -m "hardware and network" tests/unit_tests/fw_hw_in_loop/test_108_shutdown_initiated_status.py -v -s
```

## Test Overview

| Attribute | Value |
|-----------|-------|
| **Test ID** | 108 |
| **Category** | FW Hardware-in-Loop |
| **Component** | Firmware + Mock App (TCP/IP) |
| **Duration** | ~10-15 seconds |
| **Automation** | Semi-automated (manual switch press) |
| **Hardware Required** | GPIO access, OFF switch |

## Purpose

This test verifies that firmware properly sends a **"shutdown initiated"** status message to the application during the shutdown sequence:

1. **Status Message Transmission** - Firmware sends status to app via TCP/IP
2. **Application Notification** - App receives confirmation that shutdown is starting
3. **Logging** - Firmware logs the transmission for audit trail

---

## Message Sequence Overview

### Complete Shutdown Handshake

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SHUTDOWN MESSAGE SEQUENCE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Switch       Firmware                    Application               │
│    │              │                            │                    │
│    │──PRESS──────>│                            │                    │
│    │              │                            │                    │
│    │              │────── "close" ────────────>│  Phase 1: Request  │
│    │              │                            │                    │
│    │              │<───── "ACK" ──────────────│  Phase 2: ACK      │
│    │              │                            │                    │
│    │              │─"shutdown initiated"──────>│  Phase 3: STATUS   │
│    │              │        ↑                   │       (THIS TEST)  │
│    │              │        │                   │                    │
│    │              │   [LOG: Sent status]       │                    │
│    │              │                            │                    │
│    │         [SHUTDOWN]                        │  Phase 4: Execute  │
│    │              │                            │                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### What This Test Validates

| Phase | Message | Direction | Validated |
|-------|---------|-----------|-----------|
| 1 | "close" | Firmware → App | Prerequisite |
| 2 | "ACK" | App → Firmware | Prerequisite |
| **3** | **"shutdown initiated"** | **Firmware → App** | **THIS TEST** |
| 4 | Shutdown execution | - | Not in scope |

---

## Why Status Messages Are Important

### 1. Application Awareness

```
Without Status Message:
┌─────────────────────────────────────────────┐
│  App sends ACK...                           │
│  Then what? Did shutdown start? Failed?     │
│  App doesn't know! User is confused.        │
└─────────────────────────────────────────────┘

With Status Message:
┌─────────────────────────────────────────────┐
│  App sends ACK...                           │
│  App receives "shutdown initiated"          │
│  App knows: "Shutdown is happening!"        │
│  App can display: "Shutting down..."        │
└─────────────────────────────────────────────┘
```

### 2. Debugging & Diagnostics

```
Scenario: Device didn't shut down properly

With logged status messages:
┌─────────────────────────────────────────────┐
│  10:30:45.100  Received close request       │
│  10:30:45.200  Sent ACK to firmware         │
│  10:30:45.300  Received "shutdown initiated"│ ← Proves firmware got ACK
│  10:30:45.400  [No shutdown executed]       │ ← Problem is AFTER status
│                                              │
│  Diagnosis: Shutdown command failed         │
└─────────────────────────────────────────────┘

Without logged status messages:
┌─────────────────────────────────────────────┐
│  10:30:45.100  Received close request       │
│  10:30:45.200  Sent ACK to firmware         │
│  [Nothing else...]                          │
│                                              │
│  Diagnosis: Did firmware get ACK? Unknown.  │
│             Did it try to shutdown? Unknown.│
└─────────────────────────────────────────────┘
```

### 3. Coordinated Shutdown

```
Multi-Component System:

Firmware                Application              External Device
   │                        │                        │
   │──"shutdown initiated"─>│                        │
   │                        │──"shutdown_notify"────>│
   │                        │                        │
   │                   [Save data]             [Safe state]
   │                        │                        │
   │                   [Close files]           [Disconnect]
   │                        │                        │
   │                        │<──"ready"─────────────│
   │                        │                        │
   │<───"cleanup done"──────│                        │
   │                        │                        │
[Execute shutdown]
```

### 4. User Feedback

```
User Experience WITHOUT status:
┌─────────────────────────────────┐
│  User: *presses button*         │
│  App: [nothing visible]         │
│  User: "Did it work?"           │
│  User: *presses again*          │
│  User: *presses again*          │
│  → Potential issues             │
└─────────────────────────────────┘

User Experience WITH status:
┌─────────────────────────────────┐
│  User: *presses button*         │
│  App: "Shutting down..."        │
│  User: "Great, it's working"    │
│  → Clean experience             │
└─────────────────────────────────┘
```

---

## Message Protocol

### Expected Status Messages

The test accepts any of these formats:

```
Primary Format:
"shutdown initiated"
"shutdown_initiated"

Alternative Formats:
"STATUS:shutdown_initiated"
"SHUTTING_DOWN"
"BEGIN_SHUTDOWN"
"initiating shutdown"
"shutdown starting"
```

### Message Validation

```python
# Test validates message contains both keywords:
if 'shutdown' in message.lower() and 'initiated' in message.lower():
    # PASS: Valid shutdown initiated message
```

### Protocol Example

```
Firmware → App:
  Message: "shutdown_initiated"
  Encoding: UTF-8
  Protocol: TCP/IP
  Port: 8765 (configurable)

App receives:
  Raw bytes: b'shutdown_initiated'
  Decoded: "shutdown_initiated"
  Action: Display status to user
```

---

## Timing Diagram

```
Time (ms)    Event                                    Phase
─────────────────────────────────────────────────────────────────
   0         User presses switch
             │
  10         Firmware detects press
             │
  15         Firmware → "close" → App                 Phase 1
             │
  20         App receives "close"
             │
 320         App → "ACK" → Firmware                   Phase 2
             │
 325         Firmware receives ACK
             │
 330 ───────►Firmware → "shutdown initiated" → App   Phase 3 (THIS TEST)
             │
 335         Firmware logs: "Sent shutdown status"    Logging
             │
 340         App receives "shutdown initiated"
             │
 345         Firmware executes: shutdown -h now       Phase 4
             │
 350         System begins shutdown
─────────────────────────────────────────────────────────────────

Critical Window: 330ms - 340ms
  ✓ Status message must be sent
  ✓ Transmission must be logged
  ✓ App must receive notification
```

---

## Test Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TEST #108 ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   OFF Switch    │  GPIO 17 (BCM)                                 │
│  │   (Manual)      │  Triggers shutdown sequence                    │
│  └────────┬────────┘                                                │
│           │                                                         │
│           │ SHORT PRESS                                             │
│           ▼                                                         │
│  ┌─────────────────┐          ┌─────────────────┐                   │
│  │    Firmware     │──────────│   Mock App      │                   │
│  │   (Simulated)   │  TCP/IP  │   (Server)      │                   │
│  │                 │  Port    │                 │                   │
│  │  1. Send close  │  8765    │  1. Receive     │                   │
│  │  2. Get ACK     │──────────│     close       │                   │
│  │  3. Send status │          │  2. Send ACK    │                   │
│  │  4. Log it      │          │  3. Receive     │                   │
│  │                 │          │     status  ←   │ TEST VALIDATES    │
│  └────────┬────────┘          └─────────────────┘                   │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │   Log Files     │                                                │
│  │                 │                                                │
│  │  - Test log     │  /tmp/shutdown_status_test.log                 │
│  │  - Firmware log │  /tmp/firmware_test.log                        │
│  │  - System log   │  /var/log/syslog                               │
│  └─────────────────┘                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### MockApplication Role

```python
class MockApplication:
    """
    Mock application that receives shutdown status messages.

    Key behaviors:
    1. Listen for connections on TCP port 8765
    2. Receive "close" message
    3. Auto-respond with "ACK:shutdown_complete"
    4. Receive "shutdown initiated" status ← TEST FOCUS
    5. Track all messages for verification
    """
```

---

## Test Configuration

```python
test_config = {
    # GPIO Configuration
    'switch_gpio_pin': 17,
    'gpio_mode': 'BCM',
    'pull_resistor': 'PULL_UP',

    # Press timing
    'short_press_duration': 0.5,

    # TCP/IP Configuration
    'mock_app_host': '127.0.0.1',
    'mock_app_port': 8765,

    # Expected messages
    'expected_close_message': 'close',
    'expected_shutdown_initiated_keywords': [
        'shutdown initiated',
        'shutdown_initiated',
        'initiating shutdown',
        'shutdown starting',
        'begin shutdown',
    ],

    # Timing
    'message_wait_timeout': 5.0,
    'ack_delay': 0.3,

    # Logging
    'enable_logging': True,
    'log_file': '/tmp/test_108_shutdown_initiated_status.log',
    'firmware_log_file': '/var/log/syslog',

    # Log keywords to search for
    'firmware_log_keywords': [
        'shutdown initiated',
        'sent shutdown status',
        'transmitted shutdown',
        'shutdown message sent',
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
│  - Check for required permissions                                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Initialize Mock Application                                │
├─────────────────────────────────────────────────────────────────────┤
│  - Start TCP server on port 8765                                    │
│  - Configure auto-ACK for "close" messages                          │
│  - Begin message tracking                                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Initialize GPIO                                            │
├─────────────────────────────────────────────────────────────────────┤
│  - Configure GPIO 17 as input                                       │
│  - Enable pull-up resistor                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Establish Connection                                       │
├─────────────────────────────────────────────────────────────────────┤
│  - Connect firmware client to mock app                              │
│  - Verify connection established                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: Trigger Shutdown Sequence                                  │
├─────────────────────────────────────────────────────────────────────┤
│  - User presses OFF switch (manual)                                 │
│  - Firmware detects switch press                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: Send "close" Message                                       │
├─────────────────────────────────────────────────────────────────────┤
│  - Firmware sends "close" to app                                    │
│  - Verify message sent successfully                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 7: Receive ACK                                                │
├─────────────────────────────────────────────────────────────────────┤
│  - Wait for ACK from mock app                                       │
│  - Verify ACK received within timeout                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 8: Send "shutdown initiated" Status (TEST FOCUS)              │
├─────────────────────────────────────────────────────────────────────┤
│  - Firmware sends "shutdown_initiated" to app                       │
│  - Record send timestamp                                            │
│  - Log transmission                                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 9: Verify Mock App Receives Status                            │
├─────────────────────────────────────────────────────────────────────┤
│  - Check mock app received "shutdown initiated"                     │
│  - Verify message content matches expected                          │
│  - Record receive timestamp                                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 10: Verify Firmware Logs Transmission                         │
├─────────────────────────────────────────────────────────────────────┤
│  - Check firmware log file for status entry                         │
│  - Verify log contains transmission info                            │
│  - Check system logs if available                                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 11: Verify Complete Message Sequence                          │
├─────────────────────────────────────────────────────────────────────┤
│  - List all messages received by mock app                           │
│  - Verify correct order: close → ACK → status                       │
│  - Display message timeline                                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLEANUP & RESULTS                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  - Close TCP connection                                             │
│  - Stop mock application                                            │
│  - Cleanup GPIO                                                     │
│  - Report test results                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

| Criterion | Expected | Verification Method |
|-----------|----------|---------------------|
| Status message received | "shutdown initiated" (or equivalent) | Mock app message log |
| Message timing | After ACK, before shutdown | Message timestamps |
| Transmission logged | Entry in firmware log | Log file search |
| Message sequence | close → ACK → status | Order verification |

### Pass/Fail Criteria

```
PASS Conditions (ALL must be true):
  ✓ Mock app receives "shutdown initiated" message
  ✓ Firmware logs the transmission
  ✓ Message sent after ACK received
  ✓ Message contains shutdown/initiated keywords

FAIL Conditions (ANY triggers failure):
  ✗ No status message received by mock app
  ✗ Status message sent before ACK
  ✗ No log entry for transmission
  ✗ Timeout waiting for status message
```

---

## Logging Requirements

### Firmware Log Entry

```
Format:
[TIMESTAMP] [SHUTDOWN] Sent status to app: shutdown initiated

Example:
2026-01-15 10:30:45.330 [SHUTDOWN] Sent status to app: shutdown_initiated
```

### Required Log Elements

| Element | Description | Example |
|---------|-------------|---------|
| Timestamp | ISO format with milliseconds | 2026-01-15 10:30:45.330 |
| Category | Log category/level | [SHUTDOWN] |
| Action | What was done | Sent status to app |
| Content | Message content | shutdown_initiated |

### Log Files Used

```
Test Log:     /tmp/test_108_shutdown_initiated_status.log
Firmware Log: /tmp/firmware_test.log
System Log:   /var/log/syslog (if available)
```

---

## Running the Test

### Basic Execution

```bash
# Navigate to project root
cd /home/kranti/sensor_test_project

# Run test
pytest tests/unit_tests/fw_hw_in_loop/test_108_shutdown_initiated_status.py -v -s
```

### With Markers

```bash
# Run all hardware tests
pytest -m hardware tests/unit_tests/ -v -s

# Run all network tests
pytest -m network tests/unit_tests/ -v -s

# Run this specific test
pytest tests/unit_tests/fw_hw_in_loop/test_108_shutdown_initiated_status.py::TestShutdownInitiatedStatus::test_108_shutdown_initiated_status -v -s
```

### Expected Output

```
=======================================================================
Test Case #108: Shutdown Initiated Status Message to App
=======================================================================

PURPOSE:
  Verify firmware sends 'shutdown initiated' status to app

MESSAGE FLOW:
  1. Switch press → Firmware
  2. Firmware → 'close' → App
  3. App → 'ACK' → Firmware
  4. Firmware → 'shutdown initiated' → App (TEST FOCUS)
  5. Firmware logs the transmission

CONFIGURATION:
  GPIO Pin: 17
  TCP Port: 8765
=======================================================================

[STEP 1] Check Prerequisites
----------------------------------------------------------------------
✓ Running on Linux

[STEP 2] Initialize Mock Application
----------------------------------------------------------------------
Mock app started on 127.0.0.1:8765
✓ Mock application started
  Mock app will automatically ACK shutdown requests

[STEP 3] Initialize GPIO
----------------------------------------------------------------------
✓ GPIO initialized

[STEP 4] Establish Firmware → Mock App Connection
----------------------------------------------------------------------
✓ Connection established

[STEP 5] Trigger Shutdown Sequence
----------------------------------------------------------------------

📋 MANUAL ACTION:
   Press the OFF switch briefly (0.5s)
   Press ENTER after pressing switch...

✓ Switch press detected

[STEP 6] Send 'close' Message
----------------------------------------------------------------------
✓ Sent: 'close'

[STEP 7] Receive ACK from Mock App
----------------------------------------------------------------------
Mock app received: close
  → Detected: CLOSE message
Mock app sent: ACK:shutdown_complete
✓ Received ACK: 'ACK:shutdown_complete'

[STEP 8] Send 'shutdown initiated' Status Message
----------------------------------------------------------------------
Firmware sending status: 'shutdown_initiated'
✓ Status message sent
  Message: 'shutdown_initiated'
  Timestamp: 2026-01-15T10:30:45.330000

[STEP 9] Verify Mock App Receives Status Message
----------------------------------------------------------------------
Mock app received: shutdown_initiated
  → Detected: SHUTDOWN INITIATED message ✓
✓ Mock app received status message
  Message: 'shutdown_initiated'
  Timestamp: 2026-01-15T10:30:45.340000
  ✓ PASS: 'shutdown initiated' message received

[STEP 10] Verify Firmware Logs Transmission
----------------------------------------------------------------------
Checking firmware logs for status transmission...
✓ Firmware log entry found
  Log file: /tmp/firmware_test.log
  Entry: 2026-01-15 10:30:45.335 firmware[12345]: Sent shutdown status to application: shutdown_initiated
  ✓ PASS: Transmission logged

Checking system logs...
  ℹ️  No entries in system log (using test log)

[STEP 11] Verify Complete Message Sequence
----------------------------------------------------------------------

📊 Message Flow Summary:
======================================================================

Total messages received: 2

Message Timeline:
  1. [2026-01-15T10:30:45.100000] close
  2. [2026-01-15T10:30:45.340000] shutdown_initiated

✓ Sequence Verification:
  ✓ 'close' message received
  ✓ 'shutdown initiated' message received
  ✓ Correct order: 'close' before 'shutdown initiated'

[Cleanup]
----------------------------------------------------------------------
Mock app stopped
✓ Cleanup completed

=======================================================================
TEST RESULT: ✓ PASS
=======================================================================

✓ Acceptance Criteria Verification:
  ✓ Mock app receives 'shutdown initiated' status message
  ✓ Firmware logs the transmission of shutdown status
  ✓ Message sent after ACK received
  ✓ Complete shutdown handshake sequence validated

📊 Test Statistics:
  Total messages received: 2
  'close' received: Yes
  'shutdown initiated' received: Yes

📄 Test log: /tmp/test_108_shutdown_initiated_status.log
📄 Firmware log: /tmp/firmware_test.log
=======================================================================
```

---

## Troubleshooting

### 1. Status Message Not Received

**Problem:** Mock app did not receive "shutdown initiated" message

**Possible Causes:**
- Message not sent by firmware
- Network issue between firmware and app
- Timeout too short

**Solutions:**
```bash
# Increase timeout
test_config['message_wait_timeout'] = 10.0

# Check network connectivity
nc -zv 127.0.0.1 8765

# Verify mock app is running
netstat -tlnp | grep 8765
```

### 2. Log Entry Not Found

**Problem:** Firmware log doesn't show transmission

**Possible Causes:**
- Logging disabled in firmware
- Wrong log file location
- Log rotation cleared entry

**Solutions:**
```bash
# Check test log
cat /tmp/firmware_test.log

# Check system logs
journalctl -n 100 | grep -i shutdown

# Verify logging enabled
test_config['enable_logging'] = True
```

### 3. Wrong Message Sequence

**Problem:** Messages received out of order

**Possible Causes:**
- Network latency
- Thread timing issues
- Firmware logic error

**Solutions:**
```bash
# Check message timestamps
# They should be in order: close < ACK < shutdown_initiated

# Add delays between messages
time.sleep(0.5)  # After each message
```

### 4. Connection Failed

**Problem:** Cannot connect to mock app

**Possible Causes:**
- Mock app not started
- Port already in use
- Firewall blocking

**Solutions:**
```bash
# Check if port is available
lsof -i :8765

# Kill existing process
fuser -k 8765/tcp

# Check firewall
sudo iptables -L
```

### 5. ACK Not Received

**Problem:** Timeout waiting for ACK

**Possible Causes:**
- Mock app not sending ACK
- ACK sent but not received
- Connection dropped

**Solutions:**
```bash
# Check mock app logs
# Verify ACK is being sent

# Increase ACK timeout
test_config['ack_delay'] = 1.0

# Test with manual ACK
# Disable auto-ACK and send manually
```

---

## Relationship to Other Tests

### Test Sequence

```
Test #105: Soft Shutdown Handshake (ACK Accepted)
├── Tests complete handshake: close → ACK → shutdown
└── Focus: ACK acceptance

Test #106: Soft Shutdown Denied/Timeout
├── Tests ACK timeout handling
└── Focus: What happens when ACK not received

Test #107: Hard Shutdown Bypass
├── Tests long press bypass
└── Focus: NO messages to app

Test #108: Shutdown Initiated Status (THIS TEST)
├── Tests status message transmission
└── Focus: "shutdown initiated" message + logging
```

### Comparison

| Test | Messages to App | ACK | Status Message | Logging |
|------|-----------------|-----|----------------|---------|
| #105 | close | Required | Implied | Not focus |
| #106 | close | Timeout | Not sent | Not focus |
| #107 | None | None | None | Hard shutdown log |
| **#108** | **close + status** | **Required** | **Focus** | **Focus** |

---

## Real-World Applications

### Medical Device

```
ECG Monitor Shutdown Sequence:

1. User presses OFF button
2. Firmware → "close" → App
3. App → "ACK" (after saving patient data)
4. Firmware → "shutdown initiated" → App
   └── App displays: "Saving data... Shutting down"
5. System powers off

Why status message matters:
- Patient knows data was saved
- Audit log for compliance
- Debugging if shutdown fails
```

### Industrial Controller

```
Factory Controller Shutdown:

1. Operator requests shutdown
2. Firmware → "close" → App
3. App → "ACK" (after stopping motors)
4. Firmware → "shutdown initiated" → App
   └── App → Alerts other systems
   └── SCADA receives notification
5. Coordinated shutdown

Why status message matters:
- Other systems can prepare
- Safety protocols engaged
- Audit trail for incidents
```

---

## CI/CD Integration

### GitLab CI Example

```yaml
test:shutdown_status:
  stage: test
  tags:
    - hardware
    - network
  script:
    - pytest tests/unit_tests/fw_hw_in_loop/test_108_shutdown_initiated_status.py -v -s --junitxml=test_108_report.xml
  artifacts:
    reports:
      junit: test_108_report.xml
    paths:
      - /tmp/test_108_shutdown_initiated_status.log
      - /tmp/firmware_test.log
    when: always
  allow_failure: false
  timeout: 60s
```

---

## Summary

**Test #108** validates the **"shutdown initiated" status message** transmission:

- **Purpose**: Verify app receives notification that shutdown is starting
- **Focus**: Message transmission + logging
- **Trigger**: Short press → close → ACK → **status message**
- **Verification**: Mock app receives message + firmware logs it

This test ensures the application layer is properly informed when shutdown begins, enabling:
- User feedback (UI can show "Shutting down...")
- Coordinated shutdown (other systems notified)
- Debugging (audit trail if shutdown fails)
- Compliance (documented shutdown sequence)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEST #108 QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Run:     pytest .../test_108_shutdown_initiated_status.py -v -s    │
│                                                                     │
│  Message Flow:                                                      │
│    Switch → Firmware → "close" → App                                │
│                     ← "ACK" ←                                       │
│                     → "shutdown initiated" → (TEST FOCUS)           │
│                                                                     │
│  Verifies:                                                          │
│    ✓ App receives "shutdown initiated" status                       │
│    ✓ Firmware logs the transmission                                 │
│    ✓ Correct message sequence                                       │
│                                                                     │
│  GPIO:    17 (switch input)                                         │
│                                                                     │
│  Port:    8765 (TCP/IP)                                             │
│                                                                     │
│  Logs:    /tmp/test_108_shutdown_initiated_status.log               │
│           /tmp/firmware_test.log                                    │
│                                                                     │
│  Duration: ~10-15 seconds                                           │
│                                                                     │
│  Key Point:                                                         │
│    This test focuses on the STATUS MESSAGE sent AFTER ACK,          │
│    confirming shutdown is actually starting.                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
