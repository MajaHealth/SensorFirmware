# Test #121 Execution Guide
## Backlight Rapid Toggle Robustness - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_121_backlight_rapid_toggle.py -v -s
```

---

## Test Overview

### What This Test Does
Validates backlight robustness under rapid changes:
1. Rapidly toggles backlight on/off
2. Rapidly changes brightness levels
3. Verifies no crashes or hangs
4. Confirms final state is correct

### Why This Matters
- Ensures stability under stress
- Validates PWM controller handles rapid changes
- Catches race conditions in backlight control

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- Display with controllable backlight
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to rapidly toggle backlight via `/sys/class/backlight/` on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_121_backlight_rapid_toggle.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #121: Backlight Rapid Toggle Robustness
======================================================================

[STEP 1] Rapid On/Off Toggle
----------------------------------------------------------------------
  Toggling 50 times at 50ms interval...
  Toggle 1: OFF -> ON
  Toggle 2: ON -> OFF
  ...
  Toggle 50: ON -> OFF
  All toggles completed: True
  Service responsive: True

[STEP 2] Rapid Brightness Changes
----------------------------------------------------------------------
  Cycling brightness 0->100->0 rapidly...
  Cycle complete: True
  No errors: True

[STEP 3] Verify Final State
----------------------------------------------------------------------
  Final brightness: 50 (as set)
  State consistent: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Service becomes unresponsive
- May indicate rate limiting issue
- Check if PWM controller handles rapid changes

### Issue: Final state incorrect
- Race condition in brightness setting
- Report as bug with timing details

---

## Related Tests
- **Test #120:** Backlight range clamping
- **Test #122:** Brightness valid values
