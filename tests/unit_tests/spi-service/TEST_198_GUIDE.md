# Test #198 Execution Guide
## MAX30009 Sync Counter Scaling - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_198_max30009_sync_counter_scaling.py -v -s
```

---

## Test Overview

### What This Test Does
Validates MAX30009 sync counter behavior:
1. Verifies sync counter increments correctly
2. Tests counter scaling with sampling rate
3. Validates counter rollover behavior
4. Checks counter correlation with real time

### Why This Matters
- Ensures accurate sample counting
- Validates timing calculations
- Critical for data analysis

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with spi-service running
- MAX30009 bio-impedance sensor connected
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_198_max30009_sync_counter_scaling.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #198: MAX30009 Sync Counter Scaling
======================================================================

[STEP 1] Get Initial Counter
----------------------------------------------------------------------
  Initial counter: 1000
  Sampling rate: 100 Hz

[STEP 2] Collect Samples and Track Counter
----------------------------------------------------------------------
  Sample 1: counter = 1001
  Sample 2: counter = 1002
  ...
  Sample 100: counter = 1100
  Counter increment: +100 over 100 samples
  Expected: +100
  Match: True

[STEP 3] Validate Time Correlation
----------------------------------------------------------------------
  Elapsed time: 1.00 seconds
  Counter delta: 100
  Calculated rate: 100 Hz
  Expected rate: 100 Hz
  Accuracy: 100%

[STEP 4] Test Counter Scaling at Different Rates
----------------------------------------------------------------------
  Rate 50 Hz: 50 counts/sec -> PASS
  Rate 100 Hz: 100 counts/sec -> PASS
  Rate 200 Hz: 200 counts/sec -> PASS

TEST RESULT: PASS
```

---

## Counter Specifications

| Sampling Rate | Counts per Second |
|--------------|-------------------|
| 50 Hz | 50 |
| 100 Hz | 100 |
| 200 Hz | 200 |
| 400 Hz | 400 |

---

## Troubleshooting

### Issue: Counter not incrementing
- Check if counter feature is enabled
- Verify firmware version
- May be configuration issue

### Issue: Wrong scaling
- Check sampling rate setting
- Verify counter interpretation
- May be endianness issue

### Issue: Counter jumps/skips
- Data may be dropped
- Check buffer overflow
- SPI communication issues

---

## Related Tests
- **Test #196:** MAX30009 data envelope
- **Test #197:** MAX30009 sync mark
