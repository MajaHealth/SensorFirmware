# Test #123 Execution Guide
## Brightness Invalid/Corrupted Values - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_123_brightness_invalid_values.py -v -s
```

---

## Test Overview

### What This Test Does
Validates handling of invalid brightness values:
1. Tests negative values (-1, -100)
2. Tests values above maximum (101, 200, 999)
3. Tests non-numeric values (strings, null)
4. Verifies error responses or clamping

### Why This Matters
- Ensures robust error handling
- Prevents crashes from invalid input
- Validates input sanitization

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- Display with controllable backlight
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to send invalid brightness values via `/sys/class/backlight/` on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_123_brightness_invalid_values.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #123: Brightness Invalid/Corrupted Values
======================================================================

[STEP 1] Test Negative Value (-1)
----------------------------------------------------------------------
  Set: -1
  Result: Clamped to 0 OR error response -> PASS

[STEP 2] Test Over Maximum (150)
----------------------------------------------------------------------
  Set: 150
  Result: Clamped to 100 OR error response -> PASS

[STEP 3] Test Non-Numeric ("abc")
----------------------------------------------------------------------
  Set: "abc"
  Result: Error response OR ignored -> PASS

[STEP 4] Test Null Value
----------------------------------------------------------------------
  Set: null
  Result: Error response OR ignored -> PASS

[STEP 5] Verify Service Stability
----------------------------------------------------------------------
  Service still responsive: True
  No crash detected: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Service crashes on invalid input
- This is a failure - service should handle gracefully
- Report as security/robustness bug

### Issue: No error response
- Check if clamping is used instead of errors
- Both approaches are valid

---

## Related Tests
- **Test #120:** Backlight range clamping
- **Test #122:** Brightness valid values
