# Test #120 Execution Guide
## Backlight Range and Clamping - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_120_backlight_range_clamping.py -v -s
```

---

## Test Overview

### What This Test Does
Validates backlight brightness control:
1. Tests full brightness range (0-100%)
2. Verifies minimum brightness clamp
3. Verifies maximum brightness clamp
4. Tests out-of-range value handling

### Why This Matters
- Ensures brightness control works correctly
- Validates safety clamping for hardware protection
- Confirms API handles invalid values gracefully

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- Display with controllable backlight
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to control backlight via `/sys/class/backlight/` on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_120_backlight_range_clamping.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #120: Backlight Range and Clamping
======================================================================

[STEP 1] Test Minimum Brightness
----------------------------------------------------------------------
  Set brightness: 0
  Actual brightness: 0 (or minimum safe value)
  Clamped: Yes (if hardware minimum exists)

[STEP 2] Test Maximum Brightness
----------------------------------------------------------------------
  Set brightness: 100
  Actual brightness: 100

[STEP 3] Test Out-of-Range (Below)
----------------------------------------------------------------------
  Set brightness: -50
  Actual brightness: 0 (clamped)

[STEP 4] Test Out-of-Range (Above)
----------------------------------------------------------------------
  Set brightness: 150
  Actual brightness: 100 (clamped)

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Brightness doesn't change
- Verify display supports software brightness control
- Check if backlight is PWM controlled
- Some displays have fixed backlight

### Issue: Clamping not working
- Check firmware implements clamping
- May be a regression - report as bug

---

## Related Tests
- **Test #121:** Backlight rapid toggle
- **Test #122:** Brightness valid values
- **Test #123:** Brightness invalid values
