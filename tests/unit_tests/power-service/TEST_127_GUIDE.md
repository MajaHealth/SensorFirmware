# Test #127 Execution Guide
## WiFi Out-of-Range Recovery - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_127_wifi_out_of_range_recovery.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi recovery when network returns:
1. Simulates network becoming unavailable
2. Verifies state changes to WIFI_DISCONNECTED
3. Simulates network returning
4. Confirms automatic reconnection

### Why This Matters
- Ensures resilience to temporary outages
- Validates automatic recovery
- Critical for mobile or unreliable network environments

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi configured and connected
- Ability to toggle WiFi network (turn router on/off)
- Ethernet connection to CM4 (for test control)

### Manual Steps Required
This test requires manually toggling the WiFi network.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_127_wifi_out_of_range_recovery.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #127: WiFi Out-of-Range Recovery
======================================================================

[STEP 1] Verify Initial Connection
----------------------------------------------------------------------
  State: WIFI_CONNECTED

[STEP 2] Simulate Network Loss
----------------------------------------------------------------------
  → Please turn OFF the WiFi router now
  Press Enter when done...

  State: WIFI_DISCONNECTED
  Disconnect detected: True

[STEP 3] Simulate Network Return
----------------------------------------------------------------------
  → Please turn ON the WiFi router now
  Press Enter when done...

  Waiting for reconnection (up to 60 seconds)...
  State: WIFI_CONNECTED
  Recovery successful: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Doesn't detect disconnect
- May take 30-60 seconds to detect
- Check WiFi keep-alive settings

### Issue: Doesn't auto-reconnect
- Check if auto-reconnect is enabled
- Verify network is broadcasting SSID

---

## Related Tests
- **Test #126:** WiFi auto-connect on reboot
- **Test #129:** WiFi fallback when unavailable
