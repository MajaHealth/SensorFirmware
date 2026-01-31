# Test #133 Execution Guide
## WiFi Status Updates to App - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_133_wifi_status_to_app.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi status reporting to applications:
1. Requests WiFi status via API
2. Verifies all status fields are present
3. Confirms real-time accuracy
4. Tests status during state transitions

### Why This Matters
- Enables UI status display
- Provides application feedback
- Critical for user experience

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
pytest tests/unit_tests/power-service/test_133_wifi_status_to_app.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #133: WiFi Status Updates to App
======================================================================

[STEP 1] Request WiFi Status
----------------------------------------------------------------------
  Sending: {"type": "get_wifi_status"}
  Response received

[STEP 2] Validate Status Fields
----------------------------------------------------------------------
  Field 'state': WIFI_CONNECTED -> PASS
  Field 'ssid': TestNetwork -> PASS
  Field 'signal_strength': -45 dBm -> PASS
  Field 'ip_address': 192.168.1.150 -> PASS

[STEP 3] Test Status During Transition
----------------------------------------------------------------------
  Disconnecting...
  State: WIFI_DISCONNECTED
  ssid: null (correct)
  ip_address: null (correct)

TEST RESULT: PASS
```

---

## Expected Response Schema

```json
{
  "type": "wifi_status",
  "state": "WIFI_CONNECTED",
  "ssid": "NetworkName",
  "signal_strength": -45,
  "ip_address": "192.168.1.150",
  "mac_address": "aa:bb:cc:dd:ee:ff"
}
```

### Status States
| State | Description |
|-------|-------------|
| WIFI_NO_CREDENTIALS | No WiFi configured |
| WIFI_DISCONNECTED | Configured but not connected |
| WIFI_CONNECTING | Connection in progress |
| WIFI_CONNECTED | Successfully connected |

---

## Troubleshooting

### Issue: Missing fields
- Check power-service API version
- Some fields may be optional

### Issue: Stale data
- Status may be cached; wait for next poll
- Check polling interval (Test #131)

---

## Related Tests
- **Test #131:** WiFi polling interval
- **Test #132:** WiFi status logging
