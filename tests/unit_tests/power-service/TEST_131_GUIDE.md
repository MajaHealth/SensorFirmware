# Test #131 Execution Guide
## WiFi Polling Interval Cadence - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_131_wifi_polling_interval.py -v -s
```

---

## Test Overview

### What This Test Does
Validates WiFi status polling timing:
1. Measures time between status updates
2. Verifies polling interval matches specification
3. Tests both connected and disconnected states
4. Validates resource usage efficiency

### Why This Matters
- Ensures timely status updates
- Validates power-efficient polling
- Confirms specification compliance

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- WiFi configured
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_131_wifi_polling_interval.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #131: WiFi Polling Interval Cadence
======================================================================

[STEP 1] Measure Polling Interval (Connected)
----------------------------------------------------------------------
  Sample 1: 5.02s
  Sample 2: 4.98s
  Sample 3: 5.01s
  Average: 5.00s
  Expected: 5s ± 0.5s
  Within tolerance: True

[STEP 2] Measure Polling Interval (Disconnected)
----------------------------------------------------------------------
  Sample 1: 10.05s
  Sample 2: 9.95s
  Average: 10.00s
  Expected: 10s ± 1s
  Within tolerance: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Interval too short
- May drain battery faster
- Check power-service configuration

### Issue: Interval too long
- Status updates delayed
- User experience impacted

---

## Related Tests
- **Test #132:** WiFi status logging
- **Test #133:** WiFi status to app
