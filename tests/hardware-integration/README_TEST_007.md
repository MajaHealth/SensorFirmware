# Test Case 7: MAX30009 Cole-Cole BCA Integration

## Overview

Comprehensive hardware integration test for MAX30009 bioimpedance sensor with RC model circuit validation.

**Test Flow:**
1. Clear base table
2. Generate base table (100-point calibration)
3. Sweep through 11 frequencies (500 Hz to 450 kHz)
4. Monitor firmware state transitions
5. Collect impedance data at each frequency
6. Analyze results and generate plots
7. Validate against RC model values

**Duration:** ~20-30 minutes

---

## Hardware Requirements

### 1. MAX30009 Sensor
- Physical MAX30009 module connected to Raspberry Pi CM4
- SPI interface configured
- Power supplied

### 2. RC Model Circuit

Test circuit should be connected to MAX30009 measurement terminals.

**Example configuration:**
```
├─ R1 (82Ω) ──┬─ R2 (82Ω) ──┬─ MAX30009
              │              │
              └─ C (100nF) ──┘
```

**Update RC model parameters in test file:**
```python
RC_MODEL = {
    "description": "82_82_100nF",
    "R0": 164.0,      # Total resistance (82 + 82 = 164Ω)
    "Rinf": 0.0,      # High-frequency resistance
    "C": 100e-9,      # Capacitance (100 nF)
}
```

### 3. Known RC Values

For validation, you need precise measurements of:
- **R0**: DC resistance (Ω)
- **C**: Capacitance (F)
- Optional: **Rinf** for complex models

---

## Test Configuration

Edit [test_max30009_cole_cole.py](test_max30009_cole_cole.py:33-44):

```python
# Frequency sweep points
FREQUENCIES_HZ = [
    500, 1000, 2000, 5000, 10000,
    20000, 50000, 100000, 200000,
    300000, 450000
]

# Measurement parameters
MEASUREMENT_DURATION = 5.0  # seconds per frequency
POLLING_INTERVAL = 0.5      # seconds between polls
SAMPLING_RATE = 400          # Hz
STIMULATION_CURRENT = "64uA"

# RC model (update with your actual values)
RC_MODEL = {
    "description": "82_82_100nF",
    "R0": 164.0,
    "Rinf": 0.0,
    "C": 100e-9
}
```

---

## Running the Test

### Step 1: Build and Deploy Firmware

```bash
# Build firmware
./scripts/build-and-deploy.sh

# Verify services are running
ssh pi@$PI_IP systemctl status spi-service
```

### Step 2: Run Test Case 7

```bash
# From laptop (remote testing)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_cole_cole.py -v

# Or with full pytest output
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_cole_cole.py -vv -s
```

**Expected output:**
```
Test Case 7: MAX30009 Cole-Cole BCA Integration
======================================================================

RC Model: 82_82_100nF
R0 = 164.0 Ω
C = 100.0 nF

[Step 1] Clearing base table...
  ✓ Base table cleared

[Step 2] Generating base table (calibration)...
  ✓ Base table generation started
  Progress: 20/100 calibrations (3.2s)
  Progress: 40/100 calibrations (6.5s)
  ...
  ✓ Base table generation complete (18.3s, 100 calibrations)

[Step 3] Frequency Sweep
----------------------------------------------------------------------
Frequency 1/11: 500 Hz
----------------------------------------------------------------------
  [Configuring sensor...]
  ✓ Configured: 500 Hz
  [Monitoring state transitions...]
    Expected: pre_measuring → pre_measure_end → calibrating → calibrate_end → start_measuring
    [0.12s] State: pre_measuring
    [0.34s] State: pre_measure_end
    ...
    ✓ All expected states observed in sequence
  [Collecting data for 5.0s...]
    [0.5s] Poll 1: 200 samples
    [1.0s] Poll 2: 200 samples
    ...
  ✓ Collected 2000 samples in 7.23s
  [Statistics]
    Real:  164.23 ± 1.45 Ω
    Mag:   2455.67 ± 12.34 Ω
    ...

... [repeat for all 11 frequencies] ...

[Step 4] Powering off MAX30009...
  ✓ MAX30009 powered off

[Step 5] Analysis and Validation
======================================================================
  Calculating errors vs RC model...
  500 Hz:
    R error:   0.23 Ω
    Z error:   0.45 Ω
    ...

  [Mean Absolute Errors]
    Resistance MAE:  1.23 Ω  (Pass: ≤ 2 Ω)
    Impedance MAE:   2.45 Ω  (Pass: ≤ 3 Ω)
    Reactance MAE:   0.67 Ω  (Pass: ≤ 1 Ω)
    Phase Angle MAE: 0.15°   (Pass: ≤ 0.2°)

  [Validation]
    ✓ Impedance MAE ≤ 3 Ω
    ✓ Resistance MAE ≤ 2 Ω
    ✓ Reactance MAE ≤ 1 Ω
    ✓ Phase Angle MAE ≤ 0.2°

✓ Test PASSED: All validation criteria met
======================================================================
```

### Step 3: Automatic Analysis

After test completion, pytest automatically generates plots via the analysis pipeline in [conftest.py](../conftest.py:384-450).

**Generated files:**
```
/tmp/test-results/analysis/
├── test_007_cole_cole_<timestamp>_impedance_vs_freq.png
├── test_007_cole_cole_<timestamp>_cole_cole.png
└── test_007_cole_cole_<timestamp>_errors.png
```

### Step 4: Manual Analysis (if needed)

```bash
# Run analyzer on saved JSONL data
python tests/analysis/analyze_cole_cole.py /tmp/test-results/data/test_007_cole_cole_<timestamp>.jsonl
```

---

## Understanding the Results

### 1. Impedance vs Frequency Plots

Four subplots showing measured vs expected:
- **R vs f**: Resistance should be constant across frequencies for resistive circuit
- **Z vs f**: Impedance magnitude decreases as frequency increases (capacitive reactance)
- **Xc vs f**: Reactance becomes less negative at higher frequencies
- **PhA vs f**: Phase angle approaches 0° at high frequencies

### 2. Cole-Cole Plot

**X-Y plot**: Xc (imaginary) vs R (real)
- Semicircle shape indicates simple RC circuit
- **R0**: Intersection with R-axis at low frequency (DC resistance)
- **Rinf**: Intersection with R-axis at high frequency
- **Deviation from semicircle**: Indicates frequency-dependent effects

**Annotations:**
- Color coding shows frequency progression
- Text box displays R0/Rinf values and errors

### 3. Error Plots

Four subplots showing absolute errors vs frequency:
- Red dashed line: Pass/fail threshold
- Green dashed line: Mean absolute error (MAE)
- Points above red line indicate frequencies with excessive error

---

## Pass Criteria

Test passes if all MAE values meet thresholds:

| Parameter | Threshold | Typical Good Value |
|-----------|-----------|-------------------|
| Impedance MAE | ≤ 3 Ω | < 1 Ω |
| Resistance MAE | ≤ 2 Ω | < 0.5 Ω |
| Reactance MAE | ≤ 1 Ω | < 0.3 Ω |
| Phase Angle MAE | ≤ 0.2° | < 0.1° |

**If test fails:**
1. Check RC circuit connections
2. Verify RC values are accurate (measure with DMM/LCR meter)
3. Check MAX30009 calibration status
4. Review error plots to identify problematic frequencies
5. Check for noise/interference at specific frequencies

---

## Troubleshooting

### Connection Closed During Test

**Symptom:** Test fails with "Connection closed" during frequency config

**Cause:** MAX30009 firmware closes connection when hardware init fails

**Solution:**
1. Verify MAX30009 hardware is connected
2. Check SPI interface is working: `ls /dev/spidev*`
3. Check GPIO pins are accessible
4. Review firmware logs for hardware errors

### Base Table Generation Hangs

**Symptom:** Timeout during Step 2 (base table generation)

**Cause:** Hardware not providing FIFO data for calibration

**Solution:**
1. Ensure MAX30009 is powered and responding
2. Check RC circuit is connected (provides load for calibration)
3. Verify SPI communication is working
4. Try manual test: `./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_build_base_table.py`

### High Error Values

**Symptom:** Test passes validation but MAE is near threshold

**Possible causes:**
1. **Inaccurate RC values**: Measure components with precision LCR meter
2. **Frequency-dependent effects**: Parasitic inductance/capacitance at high frequencies
3. **Thermal drift**: Allow circuit to stabilize before testing
4. **Contact resistance**: Check connection quality
5. **Calibration issues**: Regenerate base table

### State Transitions Not Observed

**Symptom:** Warning "Timeout after 30s" during state monitoring

**Impact:** Test may still pass if data collection succeeds

**Not critical:** State monitoring is for validation only. If data is collected successfully, test can proceed.

---

## Data Files

### JSONL Output Format

```json
{"type": "metadata", "test_case": "Test_007_Cole_Cole_Integration", ...}
{"type": "frequency_summary", "frequency": 500, "statistics": {...}, ...}
{"type": "data", "frequency": 500, "sample": [real, mag, imag, angle, overload]}
{"type": "data", "frequency": 500, "sample": [...]}
...
{"type": "analysis", "errors": [...], "MAE": {...}}
```

**Fields:**
- **metadata**: Test configuration and RC model
- **frequency_summary**: Statistics for each frequency point
- **data**: Individual impedance samples (scaled by 10000)
- **analysis**: Error calculations and MAE values

---

## Integration with CI/CD

### Pytest Markers

```python
@pytest.mark.hardware   # Requires physical hardware
@pytest.mark.max30009   # MAX30009-specific test
@pytest.mark.long       # Long duration (>1 hour typical marker threshold)
```

**Run only hardware tests:**
```bash
pytest -m hardware
```

**Skip hardware tests (CI without hardware):**
```bash
pytest -m "not hardware"
```

### Automated Analysis

The pytest hook in `conftest.py` automatically:
1. Detects JSONL files > 1KB
2. Identifies sensor type (MAX30009/BIOZ)
3. Runs appropriate analyzer
4. Generates plots in `/tmp/test-results/analysis/`

**Disable auto-analysis:**
```python
# In conftest.py, comment out pytest_sessionfinish hook
```

---

## Related Tests

- **Test 35**: [test_max30009_build_base_table.py](test_max30009_build_base_table.py) - Base table generation only
- **Test 12**: test_max30009_poweroff_reenable.py - Power cycling
- **FW-APP Tests**: tests/fw-app-integration/test_max30009_*.py - Protocol validation

---

## References

- **Firmware**: services/spi-service/MAX30009_LIB/
- **Protocol**: JSON_PROTOCOL_REFERENCE.md
- **Cole-Cole Theory**: [Wikipedia: Cole-Cole Equation](https://en.wikipedia.org/wiki/Cole%E2%80%93Cole_equation)
- **Bioimpedance**: Standard reference resistors (370Ω internal calibration)
