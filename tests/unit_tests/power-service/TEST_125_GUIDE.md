# Test #125 Execution Guide
## WiFi Provision and Connect - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_125_wifi_provision_connect.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi provisioning and connection:
1. Provisions WiFi credentials via API
2. Initiates connection to network
3. Verifies state transitions (CONNECTING -> CONNECTED)
4. Confirms successful connection

### Why This Matters
- Core WiFi setup functionality
- Validates provisioning API
- Ensures reliable connection establishment

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi capability
- **Test WiFi network available** (Router A)
- Ethernet connection to CM4 (for test control)

### Test Configuration
Edit test or use environment variables:
```bash
export TEST_WIFI_SSID="YourTestNetwork"
export TEST_WIFI_PASSWORD="YourPassword"
```

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
export TEST_WIFI_SSID="YourNetwork"
export TEST_WIFI_PASSWORD="YourPassword"
pytest tests/unit_tests/power-service/test_125_wifi_provision_connect.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #125: WiFi Provision and Connect
======================================================================

[STEP 1] Provision WiFi Credentials
----------------------------------------------------------------------
  SSID: TestNetwork
  Sending credentials...
  Response: success

[STEP 2] Initiate Connection
----------------------------------------------------------------------
  State: WIFI_CONNECTING

[STEP 3] Wait for Connection
----------------------------------------------------------------------
  Waiting up to 30 seconds...
  State: WIFI_CONNECTED
  IP Address: 192.168.1.150

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Connection times out
- Verify SSID and password are correct
- Check WiFi network is in range
- Verify network accepts new connections

### Issue: Wrong password error
- Double-check password
- Check for special characters that may need escaping

---

## Related Tests
- **Test #124:** WiFi no credentials state
- **Test #126:** WiFi auto-connect on reboot
- **Test #128:** WiFi switch network
