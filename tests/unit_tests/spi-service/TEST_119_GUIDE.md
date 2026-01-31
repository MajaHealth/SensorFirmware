# Test #119 Execution Guide
## DSI Display Absent Detection - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run (with display disconnected)
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_119_dsi_display_absent.py -v -s
```

---

## Test Overview

### What This Test Does
Validates behavior when DSI display is not connected:
1. Detects display absence gracefully
2. Reports "not connected" status
3. Does not crash or hang
4. Handles missing display appropriately

### Why This Matters
- Ensures graceful degradation without display
- Validates error handling for missing hardware
- Prevents crashes on headless systems

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- **DSI display DISCONNECTED** (or never connected)
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to check system logs (`dmesg`) for display absence detection.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

**Important:** Run this test with display disconnected or on a CM4 without DSI display.

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_119_dsi_display_absent.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #119: DSI Display Absent Detection
======================================================================

[STEP 1] Check Display Status
----------------------------------------------------------------------
  Display detected: False
  Status: "not_connected" or "absent"

[STEP 2] Verify Graceful Handling
----------------------------------------------------------------------
  No crash: True
  No hang: True
  Error message: "No DSI display detected"

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Test says display is present
- Verify DSI cable is actually disconnected
- Check if HDMI is being detected as display

### Issue: Service crashes
- This is a failure - service should handle missing display gracefully
- Report as bug

---

## Related Tests
- **Test #116:** DSI display detection (with display connected)
- **Test #117:** Display power mode
