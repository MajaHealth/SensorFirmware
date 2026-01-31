# Test #135 Execution Guide
## RTC Read/Write Retention - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_135_rtc_readwrite_retention.py -v -s
```

---

## Test Overview

### What This Test Does
Validates RTC read/write and data retention:
1. Writes a known time value to RTC
2. Reads back and verifies
3. Tests retention across power cycle (optional)
4. Validates time format handling

### Why This Matters
- Ensures RTC can store time accurately
- Validates read/write functionality
- Critical for persistent timekeeping

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- RTC module with battery backup
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_135_rtc_readwrite_retention.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #135: RTC Read/Write Retention
======================================================================

[STEP 1] Write Test Time
----------------------------------------------------------------------
  Writing: 2026-01-25 12:30:45
  Write successful: True

[STEP 2] Read Back Time
----------------------------------------------------------------------
  Read: 2026-01-25 12:30:46
  Time matches (within 2 seconds): True

[STEP 3] Verify Retention
----------------------------------------------------------------------
  Waiting 5 seconds...
  Read: 2026-01-25 12:30:51
  Time advanced correctly: True
  Retention verified: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Write fails
- Check I2C communication
- Verify RTC is not write-protected
- Some RTCs have write-protect pins

### Issue: Time drifts significantly
- RTC crystal may be faulty
- Check battery voltage
- Temperature extremes affect accuracy

---

## Related Tests
- **Test #134:** RTC I2C presence
- **Test #136:** RTC advances in real time
