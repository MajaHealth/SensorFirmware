# Test #128 Execution Guide
## WiFi Switch Network - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_128_wifi_switch_network.py -v -s
```

---

## Test Overview

### What This Test Does
Validates switching between WiFi networks:
1. Connects to Network A
2. Provisions credentials for Network B
3. Switches connection to Network B
4. Verifies successful switch

### Why This Matters
- Enables network migration
- Validates multi-network support
- Tests credential replacement

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- **Two WiFi networks available** (Router A and Router B)
- Ethernet connection to CM4 (for test control)

### Test Configuration
```bash
export TEST_WIFI_SSID_A="NetworkA"
export TEST_WIFI_PASSWORD_A="PasswordA"
export TEST_WIFI_SSID_B="NetworkB"
export TEST_WIFI_PASSWORD_B="PasswordB"
```

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_128_wifi_switch_network.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #128: WiFi Switch Network
======================================================================

[STEP 1] Connect to Network A
----------------------------------------------------------------------
  SSID: NetworkA
  State: WIFI_CONNECTED

[STEP 2] Provision Network B
----------------------------------------------------------------------
  SSID: NetworkB
  Credentials saved: True

[STEP 3] Switch to Network B
----------------------------------------------------------------------
  Disconnecting from NetworkA...
  Connecting to NetworkB...
  State: WIFI_CONNECTED
  Current SSID: NetworkB

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Can't connect to second network
- Verify both networks are in range
- Check credentials for Network B

### Issue: Still connected to Network A
- Explicit disconnect may be required
- Check if firmware supports network switching

---

## Related Tests
- **Test #125:** WiFi provision and connect
- **Test #129:** WiFi fallback when unavailable
