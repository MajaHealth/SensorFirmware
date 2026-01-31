# Test #207 Execution Guide
## Charge Disable State Verification - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_207_charge_disable_state.py -v -s
```

---

## Test Overview

### What This Test Does
Validates charge disable state is correctly reported:
1. Disables charging via API
2. Verifies charge_enabled field is false
3. Confirms battery is not charging when disabled
4. Tests state persistence

### Why This Matters
- Ensures charge control state is accurately reported
- Validates API consistency between set and get
- Confirms hardware responds to charge control

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- Battery with charge control support
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

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_207_charge_disable_state.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #207: Charge Disable State Verification
======================================================================

[STEP 1] Disable Charging
----------------------------------------------------------------------
  Sending: {"type": "settings", "charge_enable": false}
  Response: success

[STEP 2] Verify Charge State
----------------------------------------------------------------------
  Sending: {"type": "get_battery_info"}
  charge_enabled: false -> PASS
  charging: false -> PASS

[STEP 3] Restore Charging
----------------------------------------------------------------------
  Sending: {"type": "settings", "charge_enable": true}
  charge_enabled: true -> PASS

TEST RESULT: PASS
```

---

## Troubleshooting

### Issue: charge_enabled always true
- Hardware may not support charge control
- Check if power-service implements charge control

### Issue: State doesn't persist
- Check power-service implementation
- May need hardware-level verification

---

## Related Tests
- **Test #115:** Charge control enable/disable
- **Test #206:** Battery info response schema
