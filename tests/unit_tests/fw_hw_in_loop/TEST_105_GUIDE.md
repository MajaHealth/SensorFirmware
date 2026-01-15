# Test Case #105: Soft Shutdown Handshake (ACK Accepted) - Execution Guide

## Quick Start

```bash
# Run Test #105
pytest tests/unit_tests/fw_hw_in_loop/test_105_soft_shutdown_handshake.py -v -s

# Run all FW hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all network tests
pytest tests/unit_tests/ -m network -v
```

## Test Overview

**Test ID:** #105
**Category:** FW Hardware-in-Loop Test
**Component:** CM4 GPIO trigger + Firmware + Mock App (TCP/IP)
**Automation Level:** Partially automated (requires manual switch press) + Mock application

### What This Test Validates

- ✅ Firmware detects short press of OFF switch
- ✅ Firmware sends "close" message to application via TCP/IP
- ✅ Mock application receives shutdown request
- ✅ Mock application sends ACK "shutdown complete"
- ✅ Firmware receives acknowledgment
- ✅ Firmware initiates controlled soft shutdown
- ✅ System logs "CDSS soft shutdown" event
- ✅ Complete handshake sequence executes correctly

### Test Approach

This test validates the **critical soft shutdown handshake** mechanism that ensures graceful system shutdown:

```
Shutdown Handshake Sequence:

User          GPIO        Firmware       TCP/IP      Mock App      System
 │             │             │             │            │             │
 │ Press       │             │             │            │             │
 │ Switch      │             │             │            │             │
 ├────────────>│             │             │            │             │
 │             │  Detect     │             │            │             │
 │             ├────────────>│             │            │             │
 │             │             │  "close"    │            │             │
 │             │             ├────────────>│───────────>│             │
 │             │             │             │            │ Save        │
 │             │             │             │            │ Data        │
 │             │             │    ACK      │            │             │
 │             │             │<────────────│<───────────┤             │
 │             │             │ "shutdown   │            │             │
 │             │             │  complete"  │            │             │
 │             │             │ Shutdown    │            │             │
 │             │             ├─────────────────────────────────────────>│
 │             │             │             │            │  Power Off  │
```

**Timeline:**
```
0ms:   User presses switch
10ms:  Firmware detects press (after debounce)
15ms:  Firmware sends "close" via TCP/IP
20ms:  Mock app receives "close"
520ms: Mock app sends ACK (after 500ms cleanup delay)
525ms: Firmware receives ACK
530ms: Firmware initiates shutdown
535ms: System logs "CDSS soft shutdown"
```

### Why Soft Shutdown is Critical

**Hard Shutdown (Power Cut):**
- ❌ Immediate power loss
- ❌ Application killed mid-operation
- ❌ Open files corrupted
- ❌ Database inconsistency
- ❌ Filesystem errors
- ❌ No cleanup performed

**Soft Shutdown (Handshake):**
- ✅ Application notified in advance
- ✅ Graceful termination with cleanup
- ✅ Data saved properly
- ✅ Resources released correctly
- ✅ Filesystem synced safely
- ✅ Clean shutdown logs

## Prerequisites

### Hardware Requirements

**Required:**
- Raspberry Pi CM4 (or compatible)
- Physical OFF switch connected to GPIO
- Network connectivity (for TCP/IP)

**GPIO Setup:**
```
GPIO 17 (input) ────[Pull-up]──── 3.3V
                         │
                     [Switch]
                         │
                        GND

Switch OFF (default): GPIO reads HIGH
Switch ON (pressed):  GPIO reads LOW
```

### Software Requirements

**Required:**
- Linux OS (Raspberry Pi OS)
- Python 3.7+
- pytest
- Network stack (TCP/IP)

**Optional:**
- RPi.GPIO library (recommended)
- Root/sudo access (for full shutdown detection)
- Firmware service running on port 8765

### Installing Dependencies

```bash
# Install RPi.GPIO
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

# Install pytest
pip3 install pytest

# Verify network
ping -c 1 127.0.0.1
```

### Mock Application

This test includes a built-in mock application that simulates the real application:

```python
class MockApplication:
    """Simulates real application"""

    def start(self):
        # Start TCP server on port 8765
        # Listen for "close" message
        # Send ACK "shutdown_complete"

    def handle_close_message(self):
        # Simulate data saving (500ms)
        # Send ACK to firmware
```

**Mock App Features:**
- TCP server on configurable port (default 8765)
- Automatic ACK response to "close" message
- Configurable delay (simulates cleanup time)
- Message logging with timestamps
- Thread-safe operation

## Running the Test

### Method 1: Direct Execution

```bash
# Navigate to test directory
cd tests/unit_tests/fw_hw_in_loop/

# Run Test #105 with verbose output
pytest test_105_soft_shutdown_handshake.py -v -s

# Run as Python script
python3 test_105_soft_shutdown_handshake.py
```

### Method 2: Run with Markers

```bash
# Run all hardware-in-loop tests
pytest tests/unit_tests/fw_hw_in_loop/ -m hardware -v

# Run all network tests
pytest tests/unit_tests/ -m network -v

# Run only Test #105
pytest tests/unit_tests/fw_hw_in_loop/ -k "test_105" -v -s
```

### Method 3: Run as Part of Test Suite

```bash
# Run all FW HIL tests
pytest tests/unit_tests/fw_hw_in_loop/ -v

# Run all unit tests
pytest tests/unit_tests/ -v
```

## Expected Output

### Successful Test Execution

```
======================================================================
Test Case #105: Soft Shutdown Handshake (ACK Accepted)
======================================================================

PURPOSE:
  Verify complete soft shutdown handshake mechanism

HANDSHAKE FLOW:
  1. Switch press → Firmware detects
  2. Firmware → 'close' → Mock App
  3. Mock App → 'ACK' → Firmware
  4. Firmware → Initiate shutdown

CONFIGURATION:
  GPIO Pin: 17
  TCP Port: 8765
  Short Press: 0.5s
======================================================================

[STEP 1] Check Prerequisites
----------------------------------------------------------------------
✓ Running on Linux
⚠️  WARNING: Not running as root
   Shutdown detection may be limited

[STEP 2] Initialize Mock Application
----------------------------------------------------------------------
Mock app started on 127.0.0.1:8765
✓ Mock application started
[2025-01-15 15:00:00.000] Mock app started

[STEP 3] Initialize GPIO
----------------------------------------------------------------------
[2025-01-15 15:00:00.100] ✓ GPIO 17 configured
✓ GPIO initialized

[STEP 4] Establish Firmware → Mock App Connection
----------------------------------------------------------------------
Note: In real system, firmware connects to app at startup
      For this test, we simulate the connection
Mock app: Connection from ('127.0.0.1', 52341)
✓ Connection established (firmware ← → mock app)
[2025-01-15 15:00:00.600] Connection established

[STEP 5] Simulate Short Press of OFF Switch
----------------------------------------------------------------------
[2025-01-15 15:00:00.800] Simulating switch press for 0.5s...

📋 MANUAL ACTION REQUIRED:
   Please press the OFF switch for 0.5s

   Press ENTER after pressing the switch...
[User presses switch and ENTER]

[2025-01-15 15:00:05.000] Switch press detected
✓ Switch press detected
  Duration: 0.523s
  Classification: SHORT PRESS ✓
[2025-01-15 15:00:05.000] Short press detected

[STEP 6] Firmware Sends 'close' Message
----------------------------------------------------------------------
Sending message: 'close'
[2025-01-15 15:00:05.100] Sent: close
✓ 'close' message sent

[STEP 7] Verify Mock App Receives 'close'
----------------------------------------------------------------------
Mock app received: close
✓ Mock app received message
  Message: 'close'
  Timestamp: 2025-01-15T15:00:05.105
  ✓ PASS: Received expected 'close' message
[2025-01-15 15:00:05.105] Mock app received 'close'

[STEP 8] Mock App Sends ACK 'shutdown complete'
----------------------------------------------------------------------
Waiting 0.5s before sending ACK...
(Simulating app cleanup time)
Mock app sent: ACK:shutdown_complete
✓ Mock app sent ACK
  Message: 'ACK:shutdown_complete'
  Timestamp: 2025-01-15T15:00:05.610

[STEP 9] Firmware Receives ACK 'shutdown complete'
----------------------------------------------------------------------
✓ Firmware received message
  Message: 'ACK:shutdown_complete'
  ✓ PASS: Received expected ACK
[2025-01-15 15:00:05.615] ACK received

[STEP 10] Verify Controlled Shutdown Initiated
----------------------------------------------------------------------

⚠️  WARNING: This test does NOT actually shutdown the system
   In production, firmware would call: system('shutdown -h now')
   For testing, we only verify the shutdown WOULD be initiated

Simulating shutdown command execution...
[2025-01-15 15:00:05.700] CDSS soft shutdown initiated
✓ Shutdown log entries created (simulated)

📊 Shutdown Verification:
  ✓ Switch press detected (short press)
  ✓ 'close' message sent to application
  ✓ Application acknowledged shutdown
  ✓ Shutdown sequence would be initiated
  ✓ Logs include 'CDSS soft shutdown'

[Cleanup]
----------------------------------------------------------------------
Mock app stopped
✓ Cleanup completed

======================================================================
TEST RESULT: ✓ PASS
======================================================================

📊 Test Summary:
  Total messages received by mock app: 1
  Total messages sent by mock app: 1

✓ Acceptance Criteria Verification:
  ✓ Short press detected correctly
  ✓ Mock app receives 'close'
  ✓ Firmware receives ACK 'shutdown complete'
  ✓ Controlled power-off sequence initiated
  ✓ Logs include 'CDSS soft shutdown'

📋 Message Log:
  Received by Mock App:
    [2025-01-15T15:00:05.105] close

  Sent by Mock App:
    [2025-01-15T15:00:05.610] ACK:shutdown_complete

📄 Test log: /tmp/shutdown_handshake_test.log
======================================================================

PASSED                                                           [100%]
```

### Failed Test Examples

**Mock App Did Not Receive 'close':**
```
[STEP 7] Verify Mock App Receives 'close'
----------------------------------------------------------------------
✗ FAIL: Mock app did not receive 'close' message

FAILED - Mock app did not receive 'close' message

Possible causes:
  - Network connection broken
  - Message not sent correctly
  - Mock app not listening
```

**Timeout Waiting for ACK:**
```
[STEP 9] Firmware Receives ACK 'shutdown complete'
----------------------------------------------------------------------
✗ FAIL: Timeout waiting for ACK from mock app

FAILED - Timeout waiting for ACK from mock app

Possible causes:
  - Mock app crashed
  - Network issue
  - ACK message not sent
  - Timeout too short
```

**Unexpected Message Received:**
```
[STEP 7] Verify Mock App Receives 'close'
----------------------------------------------------------------------
✓ Mock app received message
  Message: 'status'
  ✗ FAIL: Expected 'close', got 'status'

FAILED - Expected 'close', got 'status'
```

## Troubleshooting

### Issue 1: Connection Refused

**Error:**
```
Failed to connect to mock app: [Errno 111] Connection refused
```

**Cause:** Mock app server not started or port in use

**Solutions:**

```bash
# Check if port is already in use
netstat -tuln | grep 8765
# or
lsof -i :8765

# Kill process using the port
sudo kill <PID>

# Try different port
# Edit test_config:
'mock_app_port': 8766,  # Use different port
```

### Issue 2: Mock App Not Receiving Messages

**Problem:** Mock app starts but doesn't receive "close" message

**Diagnosis:**

```bash
# Test TCP connection manually
nc -zv 127.0.0.1 8765

# Send test message
echo "test" | nc 127.0.0.1 8765

# Check firewall
sudo iptables -L -n | grep 8765
```

**Solutions:**

1. **Check network interface:**
   ```bash
   # Verify loopback is up
   ip addr show lo

   # Should show:
   # lo: <LOOPBACK,UP,LOWER_UP>
   #     inet 127.0.0.1/8 scope host lo
   ```

2. **Test with telnet:**
   ```bash
   telnet 127.0.0.1 8765
   # Type: close
   # Should see connection and response
   ```

3. **Enable debug logging:**
   ```python
   # In mock app, add:
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Issue 3: ACK Not Received by Firmware

**Problem:** Mock app sends ACK but firmware doesn't receive it

**Diagnosis:**

```python
# Check mock app messages
print("Messages sent:", self.mock_app.messages_sent)

# Check socket state
import socket
print("Socket state:", firmware_client.getsockopt(
    socket.SOL_SOCKET, socket.SO_ERROR))
```

**Solutions:**

1. **Increase timeout:**
   ```python
   'message_timeout': 10,  # Increase from 5 to 10 seconds
   ```

2. **Check message format:**
   ```python
   # Verify ACK message format
   expected_ack = 'shutdown_complete'
   received_ack = data.decode('utf-8').strip()
   print(f"Expected: '{expected_ack}'")
   print(f"Received: '{received_ack}'")
   ```

3. **Test bidirectional communication:**
   ```bash
   # Terminal 1: Start server
   nc -l 8765

   # Terminal 2: Connect client
   nc 127.0.0.1 8765

   # Type messages in both terminals
   # Verify bidirectional communication works
   ```

### Issue 4: GPIO Switch Not Detected

**Problem:** Physical switch press not detected

**Solutions:**

**Check GPIO state:**
```bash
# Monitor GPIO
watch -n 0.1 cat /sys/class/gpio/gpio17/value

# Press switch and observe value change
# Should go: 1 (released) → 0 (pressed) → 1 (released)
```

**Test GPIO manually:**
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Press switch...")
while True:
    state = GPIO.input(17)
    print(f"GPIO state: {state}", end='\r')
    time.sleep(0.1)
```

**See Test #102 Guide** for comprehensive GPIO troubleshooting.

### Issue 5: Test Hangs Waiting for User Input

**Problem:** Test waits indefinitely for switch press

**Solution:**

This is expected behavior - test requires manual switch press. Options:

1. **Manual Testing:** Press physical switch when prompted
2. **Automated Testing:** Use GPIO loopback (connect output to input)
3. **Skip Manual Steps:** Modify test to skip manual press (for CI/CD)

**Automated GPIO Press:**
```python
# Setup GPIO output for automated testing
GPIO.setup(27, GPIO.OUT)  # Output pin
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input pin
# Connect GPIO 27 to GPIO 17

# Simulate press
GPIO.output(27, GPIO.LOW)
time.sleep(0.5)
GPIO.output(27, GPIO.HIGH)
```

### Issue 6: Shutdown Not Actually Initiated

**Problem:** Test passes but system doesn't shutdown

**Explanation:** This is **normal** for the test. The test verifies the handshake mechanism but does NOT actually shutdown the system (to avoid disrupting testing).

**In Production:**
```python
# Real firmware would execute:
import subprocess
subprocess.run(['shutdown', '-h', 'now'])

# Or:
os.system('shutdown -h now')
```

**For Testing:**
- Test validates handshake completes correctly
- Shutdown command is NOT executed (simulated only)
- Prevents test from shutting down the test system
- Check logs to verify shutdown would have been called

### Issue 7: Permission Denied for Shutdown

**Error:**
```
⚠️  WARNING: Not running as root
   Shutdown detection may be limited
```

**Explanation:** Test detects limited permissions but continues

**Solutions:**

1. **Run with sudo (not recommended for regular testing):**
   ```bash
   sudo pytest test_105_soft_shutdown_handshake.py -v -s
   ```

2. **Use systemd user service (production approach):**
   ```bash
   # Grant shutdown permission to specific user
   sudo visudo
   # Add line:
   # myuser ALL=(ALL) NOPASSWD: /sbin/shutdown

3. **Accept limited detection:**
   - Test still validates handshake
   - Shutdown simulation works
   - Full shutdown requires root

## Test Configuration

### Default Configuration

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # GPIO Configuration
        'switch_gpio_pin': 17,
        'gpio_mode': 'BCM',
        'pull_resistor': 'PULL_UP',

        # Press timing
        'short_press_duration': 0.5,    # 500ms short press
        'debounce_time': 0.05,

        # TCP/IP Configuration
        'mock_app_host': '127.0.0.1',
        'mock_app_port': 8765,
        'connection_timeout': 10,
        'message_timeout': 5,

        # Expected messages
        'expected_close_message': 'close',
        'expected_ack_message': 'shutdown_complete',

        # Shutdown detection
        'shutdown_command_check': True,
        'shutdown_log_keywords': [
            'CDSS soft shutdown',
            'soft shutdown',
            'shutdown initiated',
            'controlled shutdown'
        ],

        # Timing
        'ack_delay': 0.5,               # Mock app delay before ACK
        'shutdown_detection_timeout': 5,

        # Logging
        'enable_logging': True,
        'log_file': '/tmp/shutdown_handshake_test.log',
        'system_log_file': '/var/log/syslog',
    }
```

### Customization Examples

**Example 1: Different GPIO Pin**
```python
'switch_gpio_pin': 27,  # BCM GPIO 27 instead of 17
```

**Example 2: Different TCP Port**
```python
'mock_app_port': 9000,  # Use port 9000 instead of 8765
```

**Example 3: Longer ACK Delay**
```python
'ack_delay': 2.0,  # 2 seconds delay (simulate slow app cleanup)
```

**Example 4: Different Message Protocol**
```python
'expected_close_message': 'shutdown_request',
'expected_ack_message': 'ready_for_shutdown',
```

**Example 5: Custom Shutdown Keywords**
```python
'shutdown_log_keywords': [
    'graceful shutdown',
    'system poweroff',
    'shutdown sequence started'
],
```

## Comparison with Related Tests

| Aspect | Test #102 (State) | Test #103 (Timing) | Test #105 (Shutdown) | Test #106 (Denied)* |
|--------|-------------------|--------------------|-----------------------|---------------------|
| **Focus** | GPIO reading | Press timing | Shutdown handshake | ACK timeout/deny |
| **Network** | No | No | **Yes (TCP/IP)** | **Yes (TCP/IP)** |
| **Application** | No | No | **Mock app** | **Mock app** |
| **Shutdown** | No | No | **Yes (simulated)** | **Partial** |
| **Complexity** | Simple | Medium | **Advanced** | **Advanced** |
| **Duration** | ~2-3 min | ~3-5 min | ~3-5 min | ~3-5 min |

*Test #106 is planned - tests NACK or timeout scenarios

### When to Use Test #105

- ✅ Validate complete shutdown handshake flow
- ✅ Test firmware-application communication
- ✅ Verify graceful shutdown mechanism
- ✅ Validate message protocol
- ✅ Test TCP/IP connectivity
- ✅ Integration testing before production

### When Test #105 is NOT Sufficient

- ❌ Testing actual system shutdown (requires production system)
- ❌ Testing timeout scenarios (use Test #106)
- ❌ Testing NACK/denial responses (use Test #106)
- ❌ Testing network failures
- ❌ Long-duration stability testing

## Advanced Usage

### Testing with Real Firmware

Replace mock application with real firmware service:

```python
# Instead of MockApplication, connect to real firmware
import socket

firmware_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
firmware_socket.connect(('192.168.1.100', 8765))  # Real firmware IP

# Send close message
firmware_socket.send(b'close\n')

# Receive response
response = firmware_socket.recv(1024).decode()
print(f"Firmware response: {response}")
```

### Testing Different Shutdown Scenarios

Extend test to cover multiple scenarios:

```python
def test_shutdown_scenarios(self):
    """Test various shutdown scenarios"""

    scenarios = [
        {
            'name': 'Normal ACK',
            'ack_message': 'ACK:shutdown_complete',
            'ack_delay': 0.5,
            'expected_result': 'shutdown'
        },
        {
            'name': 'Slow ACK',
            'ack_message': 'ACK:shutdown_complete',
            'ack_delay': 3.0,  # Slow application
            'expected_result': 'shutdown'
        },
        {
            'name': 'NACK busy',
            'ack_message': 'NACK:busy',
            'ack_delay': 0.5,
            'expected_result': 'cancelled'
        },
    ]

    for scenario in scenarios:
        print(f"\nTesting: {scenario['name']}")
        # Run test with specific parameters
        # Verify expected result
```

### Integration with Real Application

Test with actual application instead of mock:

```python
# Start real application
import subprocess

app_process = subprocess.Popen(['/path/to/real_app'])

try:
    # Wait for app to start
    time.sleep(2)

    # Run shutdown handshake test
    # Real app will respond to close message

finally:
    # Cleanup
    app_process.terminate()
    app_process.wait()
```

### Monitoring Shutdown Sequence

Log detailed shutdown sequence:

```python
import psutil

def monitor_shutdown_sequence():
    """Monitor system during shutdown"""

    # Monitor CPU
    cpu_before = psutil.cpu_percent(interval=1)

    # Monitor processes
    processes_before = len(psutil.pids())

    # Trigger shutdown
    # ...

    # Monitor changes
    cpu_after = psutil.cpu_percent(interval=1)
    processes_after = len(psutil.pids())

    print(f"CPU: {cpu_before}% → {cpu_after}%")
    print(f"Processes: {processes_before} → {processes_after}")
```

## CI/CD Integration

### GitLab CI Example

```yaml
test:fw-hil:shutdown-handshake:
  stage: test
  tags:
    - cm4
    - hardware
    - hil
  script:
    - sudo apt-get update && sudo apt-get install -y python3-rpi.gpio

    # Start test
    - pytest test_105_soft_shutdown_handshake.py -v -s

    # Upload logs
    - mkdir -p artifacts
    - cp /tmp/shutdown_handshake_test.log artifacts/

  artifacts:
    when: always
    paths:
      - artifacts/
    expire_in: 7 days
  when: manual  # Manual trigger (requires switch press)
  allow_failure: false  # Critical test must pass
```

### GitHub Actions Example

```yaml
name: FW HIL - Shutdown Handshake

on:
  workflow_dispatch:

jobs:
  test-shutdown:
    runs-on: [self-hosted, cm4, hardware]

    steps:
      - uses: actions/checkout@v3

      - name: Install Dependencies
        run: |
          pip install -r tests/requirements.txt
          sudo apt-get install -y python3-rpi.gpio

      - name: Run Shutdown Handshake Test
        run: |
          pytest test_105_soft_shutdown_handshake.py -v -s

      - name: Upload Test Log
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: shutdown-handshake-log
          path: /tmp/shutdown_handshake_test.log
```

## Use Cases

### Use Case 1: Medical Device Shutdown

**Scenario:** Medical device requires graceful shutdown to save patient data

**Requirements:**
- Application must save all sensor data
- Database must be properly closed
- Configuration must be saved
- No data loss during shutdown

**Test validates:**
- Application receives shutdown notification
- Application has time to save data (500ms)
- Shutdown only proceeds after ACK
- Critical data integrity maintained

### Use Case 2: Industrial Control System

**Scenario:** Industrial controller must safely shut down equipment

**Requirements:**
- Equipment must return to safe state
- Processes must be stopped in correct order
- Logs must be written
- Emergency procedures followed

**Test validates:**
- Controller receives shutdown signal
- Safe state procedures execute
- System confirms completion before power off

### Use Case 3: Data Logger

**Scenario:** Data logger must flush buffers before shutdown

**Requirements:**
- All buffered data written to storage
- Ongoing measurements completed
- Files properly closed
- Metadata updated

**Test validates:**
- Logger notified of shutdown
- Time provided for buffer flush
- Confirmation before power cut

### Use Case 4: Networked System

**Scenario:** System must notify network before going offline

**Requirements:**
- Send "going offline" message to network
- Close network connections gracefully
- Update status on server
- Clean disconnect from peers

**Test validates:**
- Application handles shutdown notification
- Network cleanup occurs
- System confirms ready for power off

## Summary

Test #105 validates soft shutdown handshake mechanism by:

1. ✅ **Switch Detection** - Firmware detects short press of OFF switch
2. ✅ **Close Notification** - Firmware sends "close" message via TCP/IP
3. ✅ **Message Reception** - Mock application receives shutdown request
4. ✅ **Application Cleanup** - Mock app simulates data saving (500ms delay)
5. ✅ **ACK Response** - Mock app sends "ACK:shutdown_complete"
6. ✅ **ACK Reception** - Firmware receives acknowledgment
7. ✅ **Shutdown Initiation** - Firmware initiates controlled shutdown
8. ✅ **Logging** - System logs "CDSS soft shutdown" event

**Key Features:**
- Semi-automated (requires manual switch press)
- Built-in mock application (TCP server)
- Configurable timing and messages
- Comprehensive logging
- Validates complete handshake flow
- Safe for testing (doesn't actually shutdown)

**Test Duration:** ~3-5 minutes

**Pass Criteria:**
- Switch press detected (short press < 1s)
- "close" message sent and received
- ACK sent and received
- Shutdown sequence initiated (simulated)
- Logs include shutdown event

**Critical for:**
- Data integrity during shutdown
- Graceful application termination
- System health and reliability
- User experience (predictable shutdown)

**Why This Matters:**
- Prevents data corruption
- Ensures clean shutdown
- Maintains system integrity
- Required for production systems

For questions or issues, check the logs:
- Test log: `/tmp/shutdown_handshake_test.log`
- System log: `/var/log/syslog` or `journalctl`
