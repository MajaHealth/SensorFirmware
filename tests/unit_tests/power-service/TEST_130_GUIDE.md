# Test #130 Execution Guide
## WiFi False Credentials Handling - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_130_wifi_false_credentials.py -v -s
```

---

## Test Overview

### What This Test Does
Validates handling of incorrect WiFi credentials:
1. Provisions invalid/wrong password
2. Attempts connection
3. Verifies appropriate error state
4. Confirms no infinite retry loop

### Why This Matters
- Ensures clear error indication
- Prevents battery drain from endless retries
- Validates user feedback mechanism

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi network in range
- Ethernet connection to CM4 (for test control)

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_130_wifi_false_credentials.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #130: WiFi False Credentials Handling
======================================================================

[STEP 1] Provision Invalid Credentials
----------------------------------------------------------------------
  SSID: RealNetwork
  Password: WrongPassword123
  Credentials saved: True

[STEP 2] Attempt Connection
----------------------------------------------------------------------
  State: WIFI_CONNECTING
  ...
  State: WIFI_AUTH_FAILED or WIFI_DISCONNECTED
  Error: Authentication failed

[STEP 3] Verify No Retry Loop
----------------------------------------------------------------------
  Retry count limited: True
  State stable: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: No auth failed state
- May show as generic DISCONNECTED
- Check firmware error reporting

### Issue: Infinite retry loop
- This is a failure - report as bug
- Should stop after reasonable attempts

---

## Related Tests
- **Test #124:** WiFi no credentials state
- **Test #125:** WiFi provision and connect
