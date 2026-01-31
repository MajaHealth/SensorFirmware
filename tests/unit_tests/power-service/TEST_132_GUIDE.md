# Test #132 Execution Guide
## WiFi Status Logging - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_132_wifi_status_logging.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi status logging functionality:
1. Triggers WiFi state changes
2. Verifies log entries are created
3. Checks timestamp accuracy
4. Validates log format

### Why This Matters
- Enables debugging of connectivity issues
- Provides audit trail for network events
- Helps diagnose intermittent problems

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi configured
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_132_wifi_status_logging.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #132: WiFi Status Logging
======================================================================

[STEP 1] Trigger State Change
----------------------------------------------------------------------
  Disconnecting from WiFi...
  State: WIFI_DISCONNECTED

[STEP 2] Check Log Entry
----------------------------------------------------------------------
  Log file: /var/log/power-service.log
  Entry found: [2026-01-25 10:30:15] WiFi state: DISCONNECTED
  Timestamp valid: True
  Format correct: True

[STEP 3] Trigger Reconnection
----------------------------------------------------------------------
  Reconnecting...
  State: WIFI_CONNECTED
  Log entry: [2026-01-25 10:30:25] WiFi state: CONNECTED (SSID: TestNetwork)

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: No log entries
- Check if logging is enabled in power-service
- Verify log file path and permissions

### Issue: Missing timestamps
- Check system time is set correctly
- Verify log format configuration

---

## Related Tests
- **Test #131:** WiFi polling interval
- **Test #133:** WiFi status to app
