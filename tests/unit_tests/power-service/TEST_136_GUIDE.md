# Test #136 Execution Guide
## RTC Advances in Real Time - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_136_rtc_advances_realtime.py -v -s
```

---

## Test Overview

### What This Test Does
Validates RTC time advances correctly:
1. Reads initial RTC time
2. Waits a known duration
3. Reads RTC time again
4. Verifies elapsed time matches

### Why This Matters
- Ensures RTC is running (not frozen)
- Validates timekeeping accuracy
- Detects stopped or drifting RTCs

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- RTC module with battery
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_136_rtc_advances_realtime.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #136: RTC Advances in Real Time
======================================================================

[STEP 1] Read Initial Time
----------------------------------------------------------------------
  RTC Time: 2026-01-25 12:30:00

[STEP 2] Wait 10 Seconds
----------------------------------------------------------------------
  Waiting...
  Elapsed: 10.0 seconds

[STEP 3] Read Final Time
----------------------------------------------------------------------
  RTC Time: 2026-01-25 12:30:10
  RTC advanced: 10 seconds
  Expected: 10 seconds ± 1 second
  Accuracy: Within tolerance

TEST RESULT: PASS
```

---

## Accuracy Expectations

| Test Duration | Acceptable Drift |
|--------------|------------------|
| 10 seconds | ± 1 second |
| 60 seconds | ± 2 seconds |
| 1 hour | ± 5 seconds |

---

## Troubleshooting

### Issue: RTC not advancing
- RTC may have stopped (dead battery)
- Crystal oscillator failure
- Check RTC status registers

### Issue: Significant drift
- RTC crystal quality varies
- Temperature affects accuracy
- Consider calibration

### Issue: Time jumps backwards
- RTC time may have been reset
- Battery may have failed momentarily

---

## Related Tests
- **Test #134:** RTC I2C presence
- **Test #135:** RTC read/write retention
