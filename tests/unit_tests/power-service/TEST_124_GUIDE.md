# Test #124 Execution Guide
## WiFi No Credentials State - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_124_wifi_no_credentials.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi state when no credentials are configured:
1. Clears any existing WiFi credentials
2. Verifies state is WIFI_NO_CREDENTIALS
3. Confirms device is not attempting to connect
4. Tests state reporting to API

### Why This Matters
- Ensures clear state indication for setup flow
- Validates credential management
- Confirms proper initial state

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi capability (built-in or USB adapter)
- Network connection to CM4 (via Ethernet for test)

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_124_wifi_no_credentials.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #124: WiFi No Credentials State
======================================================================

[STEP 1] Clear WiFi Credentials
----------------------------------------------------------------------
  Sending: {"type": "wifi_clear_credentials"}
  Response: success

[STEP 2] Check WiFi Status
----------------------------------------------------------------------
  Sending: {"type": "get_wifi_status"}
  State: WIFI_NO_CREDENTIALS
  Connected: False

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: State shows WIFI_DISCONNECTED instead
- Credentials may still be stored
- Try power cycling after clearing credentials

### Issue: Connection refused
- Ensure testing via Ethernet, not WiFi
- Verify power-service is running

---

## Related Tests
- **Test #125:** WiFi provision and connect
- **Test #130:** WiFi false credentials handling
