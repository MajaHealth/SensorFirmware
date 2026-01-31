# Test #113 Execution Guide
## Battery Discharge Monitoring - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_113_battery_discharge.py -v -s
```

---

## Test Overview

### What This Test Does
Validates battery discharge monitoring functionality:
1. Verifies battery level decreases during discharge
2. Confirms voltage readings correlate with charge level
3. Tests low battery threshold detection
4. Validates discharge rate calculations

### Why This Matters
- Ensures accurate battery life predictions
- Prevents unexpected shutdowns from undetected low battery
- Validates power management decisions

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- Battery connected and discharging (not plugged into charger)
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
# From laptop - tests connect to CM4 over TCP
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_113_battery_discharge.py -v -s
```

### Method 2: Using run-tests-remote.sh
```bash
./scripts/run-tests-remote.sh 192.168.1.4 tests/unit_tests/power-service/test_113_battery_discharge.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #113: Battery Discharge Monitoring
======================================================================

[STEP 1] Get Initial Battery Status
----------------------------------------------------------------------
  Battery Level: 85%
  Voltage: 3.95V
  Charging: False

[STEP 2] Monitor Discharge Over Time
----------------------------------------------------------------------
  Reading 1: 85% @ 3.95V
  Reading 2: 84% @ 3.94V
  ...

[STEP 3] Verify Discharge Rate
----------------------------------------------------------------------
  Discharge detected: Yes
  Rate: ~1% per minute (under load)

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Battery level not changing
- Ensure device is unplugged from charger
- Run a CPU-intensive task to increase discharge rate
- Wait longer between readings (battery updates may be slow)

### Issue: Connection refused
- Verify power-service is running: `ssh pi@$PI_TARGET_IP systemctl status power-service`
- Check port 501 is accessible

---

## Related Tests
- **Test #114:** Battery recharge monitoring
- **Test #115:** Charge control enable/disable
- **Test #206:** Battery info response schema
