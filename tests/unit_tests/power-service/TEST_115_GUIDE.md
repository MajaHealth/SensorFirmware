# Test #115 Execution Guide
## Charge Control Enable/Disable - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_115_charge_control.py -v -s
```

---

## Test Overview

### What This Test Does
Validates charge control functionality:
1. Tests enabling charging via API
2. Tests disabling charging via API
3. Verifies charge state changes correctly
4. Confirms battery responds to charge control commands

### Why This Matters
- Allows software control of charging for battery health
- Enables charge limiting for longevity
- Validates power management API functionality

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- Battery with charge control capability
- Charger connected (to test enable/disable)
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
pytest tests/unit_tests/power-service/test_115_charge_control.py -v -s
```

### Method 2: Using run-tests-remote.sh
```bash
./scripts/run-tests-remote.sh 192.168.1.4 tests/unit_tests/power-service/test_115_charge_control.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #115: Charge Control Enable/Disable
======================================================================

[STEP 1] Get Initial Charge State
----------------------------------------------------------------------
  Charging enabled: True
  Battery Level: 75%

[STEP 2] Disable Charging
----------------------------------------------------------------------
  Sending: {"type": "settings", "charge_enable": false}
  Response: {"type": "settings_response", "success": true}
  Charging enabled: False

[STEP 3] Re-enable Charging
----------------------------------------------------------------------
  Sending: {"type": "settings", "charge_enable": true}
  Response: {"type": "settings_response", "success": true}
  Charging enabled: True

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: Charge control not responding
- Verify power-service supports charge control
- Check if hardware supports software charge control
- Some battery controllers don't support this feature

### Issue: State doesn't change
- Hardware may not support charge control
- Check power-service logs for errors

---

## Related Tests
- **Test #113:** Battery discharge monitoring
- **Test #114:** Battery recharge monitoring
- **Test #207:** Charge disable state verification
