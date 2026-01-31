# Test #114 Execution Guide
## Battery Recharge Monitoring - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_114_battery_recharge.py -v -s
```

---

## Test Overview

### What This Test Does
Validates battery charging functionality:
1. Verifies battery level increases during charging
2. Confirms charging state detection
3. Tests full charge detection
4. Validates charge rate monitoring

### Why This Matters
- Ensures charging system works correctly
- Validates full charge detection for battery health
- Confirms charging state reporting to applications

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- Battery connected and charging (plugged into charger)
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

### Environment Setup
```bash
export PI_TARGET_IP=192.168.1.4  # Your CM4 IP
```

---

## Running the Test

### Method 1: Remote TCP (Recommended)
```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_114_battery_recharge.py -v -s
```

### Method 2: Using run-tests-remote.sh
```bash
./scripts/run-tests-remote.sh 192.168.1.4 tests/unit_tests/power-service/test_114_battery_recharge.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #114: Battery Recharge Monitoring
======================================================================

[STEP 1] Verify Charging State
----------------------------------------------------------------------
  Charging: True
  Battery Level: 45%
  Voltage: 3.85V

[STEP 2] Monitor Charge Progress
----------------------------------------------------------------------
  Reading 1: 45% @ 3.85V (charging)
  Reading 2: 46% @ 3.86V (charging)
  ...

[STEP 3] Verify Charge Rate
----------------------------------------------------------------------
  Charge detected: Yes
  Charging properly: Yes

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Not detecting charging
- Verify charger is connected and providing power
- Check charging LED indicator on hardware
- Verify battery is not already at 100%

### Issue: Battery level not increasing
- Charging may be slow; wait longer between readings
- Check if device is consuming more power than charger provides

---

## Related Tests
- **Test #113:** Battery discharge monitoring
- **Test #115:** Charge control enable/disable
- **Test #207:** Charge disable state
