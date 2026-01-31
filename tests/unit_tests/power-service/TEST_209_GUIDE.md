# Test #209 Execution Guide
## Button Release State - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_209_button_release_state.py -v -s
```

---

## Test Overview

### What This Test Does
Validates button state after release:
1. Monitors button during press/release cycle
2. Verifies state=false after release
3. Confirms hold_time resets to 0
4. Tests clean state transition

### Why This Matters
- Ensures clean button state transitions
- Validates state reset on release
- Critical for reliable button handling

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- Physical button connected to GPIO
- Network connection to CM4

### Manual Interaction Required
This test requires **physically pressing and releasing the button**.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_209_button_release_state.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #209: Button Release State
======================================================================

[STEP 1] Wait for Button Press
----------------------------------------------------------------------
  → Press the button now...
  Button pressed detected
  state: true
  hold_time: 500

[STEP 2] Wait for Button Release
----------------------------------------------------------------------
  → Release the button now...
  Button released detected

[STEP 3] Verify Release State
----------------------------------------------------------------------
  state: false -> PASS
  hold_time: 0 -> PASS

[STEP 4] Verify State Stability
----------------------------------------------------------------------
  Waiting 1 second...
  state still false: True
  hold_time still 0: True

TEST RESULT: PASS
```

---

## State Transition Diagram

```
     ┌─────────────────────────────────────────┐
     │                                         │
     ▼                                         │
  ┌──────┐  press   ┌──────┐  release   ┌──────┐
  │ IDLE │ ───────► │ HELD │ ─────────► │ IDLE │
  │      │          │      │            │      │
  │state │          │state │            │state │
  │=false│          │=true │            │=false│
  │hold=0│          │hold++│            │hold=0│
  └──────┘          └──────┘            └──────┘
```

---

## Expected Values After Release

| Field | Value | Description |
|-------|-------|-------------|
| state | false | Button not pressed |
| hold_time | 0 | Reset to zero |

---

## Troubleshooting

### Issue: state doesn't become false
- Button may be stuck
- Check for hardware debounce issues
- Verify GPIO configuration

### Issue: hold_time doesn't reset
- May be firmware bug
- Check release detection timing
- Report as issue if persistent

### Issue: State bounces between true/false
- Debounce issue
- Check button quality
- May need hardware debounce capacitor

---

## Related Tests
- **Test #208:** Button hold time progression
- **Test #102:** Switch state readback
- **Test #104:** Debounce robustness
