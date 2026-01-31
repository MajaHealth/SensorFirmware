# Test #117 Execution Guide
## Display Power Mode - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_117_display_power_mode.py -v -s
```

---

## Test Overview

### What This Test Does
Validates display power state management:
1. Tests display on/off control
2. Verifies power state reporting
3. Confirms power mode transitions
4. Tests standby/sleep modes

### Why This Matters
- Enables power saving when display not needed
- Validates display wake-up functionality
- Ensures smooth power state transitions

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- DSI display connected
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to query display power state (`xrandr`, `fbset`, `/sys`) on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_117_display_power_mode.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #117: Display Power Mode
======================================================================

[STEP 1] Get Current Power State
----------------------------------------------------------------------
  Power state: ON
  Display active: True

[STEP 2] Set Display to Standby
----------------------------------------------------------------------
  Sending power mode: standby
  Power state: STANDBY

[STEP 3] Wake Display
----------------------------------------------------------------------
  Sending power mode: on
  Power state: ON
  Display active: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Display doesn't turn off
- Check if display supports power control
- Verify backlight is not hardwired to always-on

### Issue: Display doesn't wake up
- May need power cycle
- Check display driver supports power modes

---

## Related Tests
- **Test #116:** DSI display detection
- **Test #120:** Backlight range clamping
