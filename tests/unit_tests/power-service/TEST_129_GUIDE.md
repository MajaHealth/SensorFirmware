# Test #129 Execution Guide
## WiFi Fallback When Unavailable - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_129_wifi_fallback.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi fallback behavior:
1. Configures primary network (unavailable)
2. Verifies fallback to secondary network
3. Tests priority-based network selection
4. Confirms graceful degradation

### Why This Matters
- Ensures connectivity with backup networks
- Validates network priority handling
- Critical for reliability

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- **Secondary WiFi network available**
- Primary network unavailable or out of range
- Ethernet connection to CM4 (for test control)

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_129_wifi_fallback.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #129: WiFi Fallback When Unavailable
======================================================================

[STEP 1] Configure Primary Network (Unavailable)
----------------------------------------------------------------------
  Primary SSID: UnavailableNetwork
  Connection attempt: Failed (expected)

[STEP 2] Verify Fallback Behavior
----------------------------------------------------------------------
  Trying secondary network...
  State: WIFI_CONNECTED
  Connected to: BackupNetwork

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: No fallback occurs
- Verify secondary network is configured
- Check if fallback is implemented in firmware

### Issue: Connects to wrong network
- Check network priority settings

---

## Related Tests
- **Test #127:** WiFi out-of-range recovery
- **Test #128:** WiFi switch network
