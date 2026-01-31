# Test #134 Execution Guide
## RTC I2C Presence Detection - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_134_rtc_i2c_presence.py -v -s
```

---

## Test Overview

### What This Test Does
Validates RTC presence on I2C bus:
1. Scans I2C bus for RTC device
2. Verifies RTC responds at expected address (0x68)
3. Confirms I2C communication works
4. Tests device identification

### Why This Matters
- Ensures RTC hardware is connected
- Validates I2C bus functionality
- Required for timekeeping features

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with power-service running
- RTC module connected via I2C
- Default I2C address: 0x68 (DS3231, DS1307, etc.)
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_134_rtc_i2c_presence.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #134: RTC I2C Presence Detection
======================================================================

[STEP 1] Scan I2C Bus
----------------------------------------------------------------------
  Scanning I2C bus 1...
  Device found at address: 0x68

[STEP 2] Verify RTC Response
----------------------------------------------------------------------
  Address: 0x68
  Device responds: True
  Device type: RTC (DS3231 compatible)

TEST RESULT: PASS
```

---

## Common RTC Addresses

| Address | Device |
|---------|--------|
| 0x68 | DS3231, DS1307, PCF8523 |
| 0x51 | PCF8563 |
| 0x6F | MCP7940 |

---

## Troubleshooting

### Issue: RTC not found
- Verify I2C is enabled: `sudo raspi-config`
- Check wiring (SDA, SCL, VCC, GND)
- Verify with `i2cdetect -y 1`

### Issue: Wrong address detected
- Some RTCs use different addresses
- Check RTC module documentation

---

## Related Tests
- **Test #135:** RTC read/write retention
- **Test #136:** RTC advances in real time
