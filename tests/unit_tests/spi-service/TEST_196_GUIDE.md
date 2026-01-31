# Test #196 Execution Guide
## MAX30009 Data Envelope Validation - Unit Test

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_196_max30009_data_envelope.py -v -s
```

---

## Test Overview

### What This Test Does
Validates MAX30009 bio-impedance data envelope:
1. Collects data samples from MAX30009
2. Verifies data values are within valid range
3. Checks for proper envelope characteristics
4. Validates signal quality indicators

### Why This Matters
- Ensures sensor produces valid readings
- Validates data quality for medical applications
- Catches hardware or configuration issues

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4 with spi-service running
- MAX30009 bio-impedance sensor connected
- Electrodes properly attached (for valid readings)
- Network connection to CM4

### Software Required
```bash
pip install pytest pyyaml numpy
```

### Environment Setup
```bash
export PI_TARGET_IP=192.168.1.4  # Your CM4 IP
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_196_max30009_data_envelope.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #196: MAX30009 Data Envelope Validation
======================================================================

[STEP 1] Initialize MAX30009
----------------------------------------------------------------------
  Sensor initialized: True
  Sampling rate: 100 Hz

[STEP 2] Collect Data Samples
----------------------------------------------------------------------
  Collecting 500 samples...
  Samples received: 500

[STEP 3] Validate Data Envelope
----------------------------------------------------------------------
  Min value: 1200
  Max value: 3800
  Mean value: 2450
  Valid range (0-4095): True
  No saturation: True
  No clipping: True

[STEP 4] Check Signal Quality
----------------------------------------------------------------------
  SNR estimate: 25 dB
  Quality: Good

TEST RESULT: PASS
```

---

## Data Envelope Specifications

| Parameter | Expected Range | Notes |
|-----------|---------------|-------|
| Raw ADC | 0 - 4095 | 12-bit ADC |
| Typical range | 500 - 3500 | With electrodes |
| No-signal | ~2048 | Baseline |

---

## Troubleshooting

### Issue: Data saturated (all max/min)
- Check electrode connections
- Verify sensor gain settings
- May indicate hardware fault

### Issue: Flat signal (no variation)
- Electrodes may not be attached
- Check SPI communication
- Verify sensor is configured

### Issue: Noisy data
- Check electrode impedance
- Verify shielding
- Check power supply noise

---

## Related Tests
- **Test #197:** MAX30009 sync mark
- **Test #198:** MAX30009 sync counter scaling
