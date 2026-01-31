# Test #208 Execution Guide
## Button Hold Time Progression - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_208_button_hold_time.py -v -s
```

---

## Test Overview

### What This Test Does
Validates button hold_time field progression:
1. Monitors button state during press
2. Verifies hold_time increases while button pressed
3. Validates hold_time is in seconds (or milliseconds)
4. Tests continuous update during hold

### Why This Matters
- Enables long-press detection
- Supports gesture recognition (tap vs hold)
- Critical for shutdown button behavior

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- Physical button connected to GPIO
- Network connection to CM4

### Manual Interaction Required
This test requires **physically pressing the button**.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_208_button_hold_time.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #208: Button Hold Time Progression
======================================================================

[STEP 1] Wait for Button Press
----------------------------------------------------------------------
  → Press and HOLD the button now...

[STEP 2] Monitor Hold Time
----------------------------------------------------------------------
  Button pressed detected
  hold_time at 0.0s: 0
  hold_time at 0.5s: 500
  hold_time at 1.0s: 1000
  hold_time at 1.5s: 1500
  hold_time at 2.0s: 2000

  → You may release the button now

[STEP 3] Validate Progression
----------------------------------------------------------------------
  Hold time increased: True
  Progression linear: True
  Update rate: ~100ms intervals

TEST RESULT: PASS
```

---

## Hold Time Behavior

| Time Held | hold_time Value | Notes |
|-----------|----------------|-------|
| 0s | 0 | Initial press |
| 0.5s | ~500 | Half second |
| 1s | ~1000 | One second |
| 3s | ~3000 | Shutdown threshold (typical) |

---

## Troubleshooting

### Issue: hold_time stays at 0
- Button may not be properly detected
- Check GPIO configuration
- Verify button is connected

### Issue: hold_time jumps erratically
- Debouncing issue
- Check for electrical noise
- Verify GPIO pull-up/pull-down

### Issue: Test times out waiting for press
- Press button within timeout period
- Verify test is looking at correct GPIO

---

## Related Tests
- **Test #209:** Button release state
- **Test #103:** Press classification (tap vs hold)
- **Test #105:** Soft shutdown handshake
