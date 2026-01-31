# Test #122 Execution Guide
## Brightness Valid Values - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_122_brightness_valid_values.py -v -s
```

---

## Test Overview

### What This Test Does
Validates handling of valid brightness values:
1. Tests brightness values 0, 25, 50, 75, 100
2. Verifies each value is accepted
3. Confirms readback matches set value
4. Tests boundary values

### Why This Matters
- Ensures full brightness range works
- Validates API accepts all valid values
- Confirms get/set consistency

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- Display with controllable backlight
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to set/get brightness via `/sys/class/backlight/` on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_122_brightness_valid_values.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #122: Brightness Valid Values
======================================================================

[STEP 1] Test Brightness = 0
----------------------------------------------------------------------
  Set: 0, Get: 0 -> PASS

[STEP 2] Test Brightness = 25
----------------------------------------------------------------------
  Set: 25, Get: 25 -> PASS

[STEP 3] Test Brightness = 50
----------------------------------------------------------------------
  Set: 50, Get: 50 -> PASS

[STEP 4] Test Brightness = 75
----------------------------------------------------------------------
  Set: 75, Get: 75 -> PASS

[STEP 5] Test Brightness = 100
----------------------------------------------------------------------
  Set: 100, Get: 100 -> PASS

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Readback doesn't match
- Check if hardware quantizes brightness levels
- Some displays only support discrete levels (e.g., 0, 33, 66, 100)

### Issue: Value rejected
- Check API documentation for valid range
- May be firmware regression

---

## Related Tests
- **Test #120:** Backlight range clamping
- **Test #123:** Brightness invalid values
