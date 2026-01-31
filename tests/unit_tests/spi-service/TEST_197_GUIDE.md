# Test #197 Execution Guide
## MAX30009 Sync Mark Validation - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_197_max30009_sync_mark.py -v -s
```

---

## Test Overview

### What This Test Does
Validates MAX30009 sync mark functionality:
1. Collects data stream with sync marks
2. Verifies sync marks appear at expected intervals
3. Validates sync mark format (e.g., [999, 999, 999])
4. Tests timing accuracy of sync marks

### Why This Matters
- Enables data synchronization with other sensors
- Validates timing accuracy
- Critical for multi-sensor applications

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
pytest tests/unit_tests/spi-service/test_197_max30009_sync_mark.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #197: MAX30009 Sync Mark Validation
======================================================================

[STEP 1] Start Data Collection
----------------------------------------------------------------------
  Collecting for 5 seconds...
  Total samples: 520

[STEP 2] Identify Sync Marks
----------------------------------------------------------------------
  Sync marks found: 5
  Expected: 5 (1 per second)
  Sync mark format: [999, 999, 999]

[STEP 3] Validate Sync Timing
----------------------------------------------------------------------
  Interval 1: 1.002s
  Interval 2: 0.998s
  Interval 3: 1.001s
  Interval 4: 0.999s
  Average: 1.000s
  Tolerance: ± 10ms
  All within tolerance: True

TEST RESULT: PASS
```

---

## Sync Mark Specification

| Parameter | Value |
|-----------|-------|
| Format | [999, 999, 999] |
| Interval | 1 second |
| Tolerance | ± 10ms |

---

## Troubleshooting

### Issue: No sync marks found
- Verify sync mark feature is enabled
- Check firmware version supports sync marks
- Verify data format parsing

### Issue: Wrong interval
- Check sampling rate configuration
- Verify timer accuracy
- May indicate firmware issue

---

## Related Tests
- **Test #196:** MAX30009 data envelope
- **Test #198:** MAX30009 sync counter scaling
