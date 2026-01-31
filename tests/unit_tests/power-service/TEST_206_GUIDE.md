# Test #206 Execution Guide
## Battery Info Response Schema - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_206_batt_info_response_schema.py -v -s
```

---

## Test Overview

### What This Test Does
Validates the JSON schema of battery info responses:
1. Verifies all required fields are present
2. Validates field types (int, float, bool, string)
3. Checks value ranges are valid
4. Tests response format consistency

### Why This Matters
- Ensures API contract is maintained
- Validates data types for application parsing
- Catches schema regressions early

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
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
pytest tests/unit_tests/power-service/test_206_batt_info_response_schema.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #206: Battery Info Response Schema
======================================================================

[STEP 1] Request Battery Info
----------------------------------------------------------------------
  Sending: {"type": "get_battery_info"}
  Response received

[STEP 2] Validate Schema
----------------------------------------------------------------------
  Field 'type': present, type=str -> PASS
  Field 'battery_level': present, type=int, range=0-100 -> PASS
  Field 'voltage': present, type=float, range=2.5-4.5 -> PASS
  Field 'charging': present, type=bool -> PASS
  Field 'charge_enabled': present, type=bool -> PASS

TEST RESULT: PASS
```

---

## Expected Response Schema

```json
{
  "type": "battery_info",
  "battery_level": 85,
  "voltage": 3.95,
  "charging": true,
  "charge_enabled": true,
  "temperature": 25.5
}
```

### Required Fields
| Field | Type | Range | Description |
|-------|------|-------|-------------|
| type | string | "battery_info" | Response type identifier |
| battery_level | int | 0-100 | Battery percentage |
| voltage | float | 2.5-4.5 | Battery voltage in V |
| charging | bool | true/false | Currently charging |

---

## Troubleshooting

### Issue: Missing fields
- Check power-service version supports all fields
- Some fields may be optional based on hardware

### Issue: Invalid types
- Firmware may have regression; check recent changes
- Report schema mismatch as a bug

---

## Related Tests
- **Test #113:** Battery discharge monitoring
- **Test #207:** Charge disable state
