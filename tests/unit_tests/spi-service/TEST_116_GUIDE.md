# Test #116 Execution Guide
## DSI Display Detection and Initialization - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_116_dsi_display_detect_init.py -v -s
```

---

## Test Overview

### What This Test Does
Validates DSI display detection and initialization:
1. Detects presence of DSI display
2. Verifies display initialization sequence
3. Confirms display is ready for rendering
4. Tests display info reporting

### Why This Matters
- Ensures display is properly detected on boot
- Validates initialization for UI rendering
- Catches display driver issues early

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- DSI display connected
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to check system logs (`dmesg`) and display status on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_116_dsi_display_detect_init.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #116: DSI Display Detection and Initialization
======================================================================

[STEP 1] Check Display Presence
----------------------------------------------------------------------
  Display detected: True
  Display type: DSI
  Resolution: 800x480

[STEP 2] Verify Initialization
----------------------------------------------------------------------
  Display initialized: True
  Ready for rendering: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Display not detected
- Verify DSI ribbon cable is connected properly
- Check display power supply
- Verify display is enabled in config.txt

### Issue: Initialization fails
- Check display driver is loaded
- Verify /dev/dri devices exist

---

## Related Tests
- **Test #117:** Display power mode
- **Test #119:** DSI display absent detection
- **Test #120:** Backlight range clamping
