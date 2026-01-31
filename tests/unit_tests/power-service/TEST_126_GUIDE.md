# Test #126 Execution Guide
## WiFi Auto-Connect on Reboot - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_126_wifi_auto_connect.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi auto-reconnection after reboot:
1. Verifies credentials persist across reboot
2. Confirms automatic connection attempt on boot
3. Validates successful reconnection
4. Tests connection timing

### Why This Matters
- Ensures seamless reconnection after power loss
- Validates credential persistence
- Critical for unattended operation

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi already configured and connected
- Ethernet connection to CM4 (for test control)

### Pre-Test Setup
Run Test #125 first to provision WiFi credentials.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

**Note:** This test may require a reboot cycle.

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_126_wifi_auto_connect.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #126: WiFi Auto-Connect on Reboot
======================================================================

[STEP 1] Verify Current Connection
----------------------------------------------------------------------
  State: WIFI_CONNECTED
  SSID: TestNetwork

[STEP 2] Initiate Reboot (or verify post-reboot)
----------------------------------------------------------------------
  Rebooting system...
  (Wait for system to come back online)

[STEP 3] Verify Auto-Reconnection
----------------------------------------------------------------------
  State: WIFI_CONNECTED
  SSID: TestNetwork
  Auto-connected: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Not connected after reboot
- Verify credentials were saved (not just in memory)
- Check if network is available during boot
- Verify auto-connect is enabled

### Issue: Test hangs waiting for reboot
- SSH connection lost during reboot is expected
- Test should reconnect after reboot completes

---

## Related Tests
- **Test #125:** WiFi provision and connect
- **Test #127:** WiFi out-of-range recovery
