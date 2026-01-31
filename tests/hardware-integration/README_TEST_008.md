## Test Case 8: MAX30009 ICG Resistor Load Integration

## Overview

Hardware integration test for MAX30009 bioimpedance sensor with precision resistor loads. Validates measurement accuracy, sync marker generation, and sampling frequency.

**Test Flow:**
1. Clear and generate base table
2. For each resistor (20Ω, 100Ω, 200Ω, 300Ω):
   - Configure sensor (20 kHz, 1.28µA, 400 Hz sampling)
   - Monitor state transitions
   - Record 60 seconds of data
   - Validate sync markers (monotonic, 1/sec)
   - Validate sampling frequency (400 ± 1 Hz)
3. Calculate R and Z errors
4. Power off

**Duration:** ~10 minutes

---

## Hardware Requirements

### 1. MAX30009 Sensor
- Physical MAX30009 module connected to Raspberry Pi CM4
- SPI interface configured
- Power supplied

### 2. Precision Resistor Loads

Test requires 4 precision resistors connected to MAX30009 ICG electrodes.

**Required resistor values:**
- 20 Ω (±1% tolerance or better)
- 100 Ω (±1% tolerance or better)
- 200 Ω (±1% tolerance or better)
- 300 Ω (±1% tolerance or better)

**Connection:**
```
MAX30009 ICG Terminals
    │
    ├─ Terminal A ──┬── Resistor ──┬── Terminal B
    │               │               │
    └───────────────┴───────────────┘
```

**Important:**
- Use precision resistors (±1% or better)
- Measure actual resistance with multimeter
- Short leads minimize inductance
- Clean contacts reduce contact resistance

### 3. Switching Mechanism

Manual or automated switching between resistor values:
- **Manual**: Use jumper wires or switch box
- **Automated**: Relay board (optional)

**Test pauses between loads** to allow manual resistor change.

---

## Test Configuration

Configuration is in [test_max30009_icg_resistor.py](test_max30009_icg_resistor.py:30-46):

```python
# Resistor loads to test
RESISTOR_LOADS_OHM = [20, 100, 200, 300]

# Test parameters
RECORDING_DURATION = 60.0    # seconds per resistor
POLLING_INTERVAL = 0.5       # seconds between data polls
SAMPLING_RATE = 400          # Hz
STIMULATION_FREQUENCY = 20000  # 20 kHz
STIMULATION_CURRENT = "1.28uA"

# For pure resistors at 20 kHz:
# Expected R = resistor value
# Expected Z = resistor value (no reactance)
# Expected Xc = 0 (no capacitive component)
# Expected PhA = 0° (no phase shift)
```

---

## Running the Test

### Step 1: Prepare Resistors

Measure actual resistor values with precision multimeter:
```
20Ω  → Actual: 19.8Ω
100Ω → Actual: 100.2Ω
200Ω → Actual: 199.5Ω
300Ω → Actual: 301.0Ω
```

Update test file if needed (optional - test uses nominal values by default).

### Step 2: Build and Deploy Firmware

```bash
./scripts/build-and-deploy.sh
```

### Step 3: Run Test

```bash
# From laptop (remote testing)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_icg_resistor.py -v

# With full output
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_icg_resistor.py -vv -s
```

**Interactive prompts:**
```
*** PLEASE CONNECT 20 Ω RESISTOR NOW ***
Press Enter when ready...
[Connect 20Ω resistor]
[Press Enter]

[Test runs for 60 seconds...]

*** PLEASE CONNECT 100 Ω RESISTOR NOW ***
Press Enter when ready...
[Disconnect 20Ω, connect 100Ω]
[Press Enter]

... [repeat for 200Ω and 300Ω] ...
```

### Step 4: Expected Output

```
Test Case 8: MAX30009 ICG Resistor Load Integration
======================================================================

[Step 1] Clearing base table...
  ✓ Base table cleared

[Step 2] Generating base table (calibration)...
  ✓ Base table generation started
  Progress: 20/100 calibrations (3.5s)
  ...
  ✓ Base table generation complete (18.7s, 100 calibrations)

[Step 3] Resistor Load Testing
----------------------------------------------------------------------
Resistor Load 1/4: 20 Ω
----------------------------------------------------------------------
*** PLEASE CONNECT 20 Ω RESISTOR NOW ***
Press Enter when ready...

  [Configuring sensor...]
  ✓ Configured: 20000 Hz, 1.28uA

  [Monitoring state transitions...]
    Expected: pre_measuring → pre_measure_end → calibrating → calibrate_end → start_measuring
    [0.15s] State: pre_measuring
    [0.42s] State: pre_measure_end
    ...
    ✓ All expected states observed in sequence

  [Recording data for 60.0s...]
    [0.5s] Poll 1: 200 samples
    [1.0s] Poll 2: 200 samples
    ...
    [60.0s] Poll 120: 200 samples
  ✓ Collected 24560 samples in 63.45s

  [Sync Marker Validation]
    Total samples: 24560
    Sync markers: 60
    Data samples: 24500
    Sync_num sequence: [1, 2, 3, ..., 60]
    ✓ Sync numbers are monotonically increasing
    ✓ Sync numbers increment by exactly 1
    Expected markers: ~60 (1 per second)
    Actual markers: 60
    ✓ Marker count matches expected

  [Sampling Frequency Validation]
    Sync markers: 60
    Actual duration: 59 seconds
    Total data samples: 24500
    Actual sampling rate: 415.25 Hz
    Expected: 400 Hz ± 1 Hz
    ✗ Sampling frequency outside tolerance (error: 15.25 Hz)

  [Statistics]
    Real (R):  19.87 ± 0.23 Ω
    Mag (Z):   19.91 ± 0.25 Ω
    Imag (Xc): 0.12 ± 0.08 Ω
    Angle:     0.03 ± 0.02°

  [Errors]
    R error: 0.13 Ω
    Z error: 0.09 Ω

... [repeat for 100Ω, 200Ω, 300Ω] ...

[Step 4] Powering off MAX30009...
  ✓ MAX30009 powered off

[Step 5] Analysis and Validation
======================================================================
  Calculating overall metrics...

  [Mean Absolute Errors Across All Loads]
    Resistance MAE:  0.45 Ω  (Pass: ≤ 2 Ω)
    Impedance MAE:   0.52 Ω  (Pass: ≤ 3 Ω)

  [Sync Marker Validation Summary]
    ✓ All loads have monotonically increasing sync markers

  [Sampling Frequency Validation Summary]
    ✓ All loads have sampling frequency within 400 ± 1 Hz
      20Ω: 400.15 Hz (error: 0.15 Hz)
     100Ω: 399.87 Hz (error: 0.13 Hz)
     200Ω: 400.23 Hz (error: 0.23 Hz)
     300Ω: 399.95 Hz (error: 0.05 Hz)

  [Validation]
    ✓ Impedance MAE ≤ 3 Ω
    ✓ Resistance MAE ≤ 2 Ω
    ✓ Sync markers monotonically increasing every 1s
    ✓ Sampling frequency 400 Hz ± 1 Hz

✓ Test PASSED: All validation criteria met
======================================================================
```

### Step 5: Automatic Analysis

Plots generated in `/tmp/test-results/analysis/`:
- `test_008_icg_resistor_<timestamp>_impedance_accuracy.png`
- `test_008_icg_resistor_<timestamp>_sampling_freq.png`
- `test_008_icg_resistor_<timestamp>_sync_markers.png`
- `test_008_icg_resistor_<timestamp>_errors.png`

---

## Understanding the Results

### 1. Impedance Accuracy Plot

Two subplots showing measured vs expected:
- **R vs Load**: Resistance should match resistor value across all loads
- **Z vs Load**: Impedance magnitude should equal resistance (no reactance)

**Expected behavior:**
- Linear relationship (measured ≈ expected)
- Small deviations indicate measurement accuracy
- Error annotations show absolute difference

### 2. Sampling Frequency Plot

**Left subplot**: Actual sampling frequency per load
- Should hover around 400 Hz
- Orange dashed lines show ±1 Hz tolerance
- All points should fall within tolerance band

**Right subplot**: Frequency errors
- Bar chart showing error magnitude
- Green bars: Within tolerance (≤ 1 Hz)
- Red bars: Outside tolerance (> 1 Hz)

### 3. Sync Marker Plot

**Left subplot**: Sync marker count
- Blue bars: Actual count
- Orange bars: Expected count (~60 for 60s recording)
- Should be approximately equal

**Right subplot**: Sync number sequence (example load)
- Should show monotonically increasing line
- Text box indicates pass/fail

### 4. Error Summary Plot

**Left subplot**: Resistance errors per load
- Green bars: Within 2 Ω threshold
- Red bars: Exceeds threshold
- Green dashed line: Overall MAE

**Right subplot**: Impedance errors per load
- Green bars: Within 3 Ω threshold
- Red bars: Exceeds threshold
- Green dashed line: Overall MAE

---

## Pass Criteria

Test passes if ALL criteria met:

| Criterion | Threshold | Typical Good Value |
|-----------|-----------|-------------------|
| Resistance MAE | ≤ 2 Ω | < 0.5 Ω |
| Impedance MAE | ≤ 3 Ω | < 0.5 Ω |
| Sync markers | Monotonic, every 1s | Exact 1s intervals |
| Sampling frequency | 400 ± 1 Hz | 400 ± 0.2 Hz |

**If test fails:**
1. Check resistor values are accurate
2. Verify connections are solid (no intermittent contact)
3. Check for noise/interference
4. Verify MAX30009 calibration
5. Review firmware logs

---

## Key Validations

### Sync Marker Validation

**What it validates:**
- Firmware injects sync markers every 1 second
- Sync numbers increment monotonically (1, 2, 3, ...)
- No missing or duplicate markers
- Proper synchronization between firmware and data stream

**How it works:**
```python
# Extract sync markers (magic number: -999990000)
sync_markers = [s for s in samples if s[0] == ICG_SYNC_MAGIC]

# Extract sync numbers (descale by 10000)
sync_numbers = [s[1] // 10000 for s in sync_markers]

# Validate monotonic increase
is_monotonic = all(sync_numbers[i] < sync_numbers[i+1]
                  for i in range(len(sync_numbers)-1))
```

### Sampling Frequency Validation

**What it validates:**
- Actual sampling rate matches configured 400 Hz
- Data acquisition timing is accurate
- Buffer handling maintains correct rate

**How it works:**
```python
# Use sync markers to determine actual duration
actual_duration = len(sync_markers) - 1  # seconds

# Calculate frequency from data samples
actual_fs = len(data_samples) / actual_duration

# Validate within ±1 Hz
error = abs(actual_fs - 400)
assert error <= 1.0
```

**Why ±1 Hz tolerance:**
- Accounts for polling timing variations
- Buffer quantization effects
- TCP transmission delays
- Realistic for integration test

---

## Troubleshooting

### High Resistance Errors

**Symptom:** R_MAE or Z_MAE exceeds threshold

**Possible causes:**
1. **Inaccurate resistor values**: Measure with precision meter
2. **Contact resistance**: Clean terminals, use solid connections
3. **Lead inductance**: Use short, thick wires
4. **Calibration issues**: Regenerate base table
5. **Temperature drift**: Allow circuit to stabilize

**Solutions:**
- Measure actual resistor values and update test
- Use 4-wire measurement if available
- Check for cold solder joints
- Verify stable ambient temperature

### Sampling Frequency Errors

**Symptom:** Actual frequency outside 400 ± 1 Hz

**Possible causes:**
1. **Firmware timing issues**: Check main loop delays
2. **Buffer overflow**: Data accumulation between polls
3. **Polling timing**: Network latency affects POLLING_INTERVAL

**Solutions:**
- Increase POLLING_INTERVAL if buffer is overflowing
- Check firmware for timing bugs
- Verify no other processes interfering with timing
- Monitor CPU usage on CM4

### Non-Monotonic Sync Markers

**Symptom:** Sync numbers don't increment properly

**Possible causes:**
1. **Firmware bug**: Sync marker injection logic
2. **Buffer corruption**: Data integrity issues
3. **TCP packet loss**: Network communication errors

**Solutions:**
- Check firmware sync marker injection code
- Verify SPI communication integrity
- Check network stability
- Review firmware logs

### Missing Sync Markers

**Symptom:** Fewer sync markers than expected

**Possible causes:**
1. **Polling too infrequent**: Missing markers between polls
2. **Buffer overflow**: Old markers discarded
3. **Firmware issue**: Not injecting markers

**Solutions:**
- Decrease POLLING_INTERVAL
- Increase buffer size in firmware (if possible)
- Check firmware sync marker injection

---

## Data Files

### JSONL Output Format

```json
{"type": "metadata", "test_case": "Test_008_ICG_Resistor_Integration", ...}
{"type": "load_summary", "resistor_ohm": 20, "statistics": {...}, ...}
{"type": "data", "resistor_ohm": 20, "sample": [real, mag, imag, angle, overload]}
{"type": "data", "resistor_ohm": 20, "sample": [...]}
...
{"type": "analysis", "MAE": {...}, "sync_validation_all_pass": true, ...}
```

**Key fields:**
- **metadata**: Test configuration
- **load_summary**: Statistics for each resistor load
  - `sync_validation`: Sync marker validation results
  - `fs_validation`: Sampling frequency validation results
  - `errors`: R and Z errors
- **data**: Individual impedance samples (scaled by 10000)
- **analysis**: Overall MAE and pass/fail status

---

## Integration with CI/CD

### Pytest Markers

```python
@pytest.mark.hardware   # Requires physical hardware
@pytest.mark.max30009   # MAX30009-specific test
@pytest.mark.slow       # Duration > 5 minutes
```

**Run specific tests:**
```bash
# Run all MAX30009 tests
pytest -m max30009

# Run only slow tests
pytest -m slow

# Skip hardware tests
pytest -m "not hardware"
```

### Automation Considerations

**Interactive prompts** make this test unsuitable for fully automated CI/CD.

**For automation:**
1. Use relay board for automatic resistor switching
2. Remove `input()` prompts
3. Add automated resistor selection logic
4. Or use as manual hardware validation step

---

## Related Tests

- **Test 7**: [test_max30009_cole_cole.py](test_max30009_cole_cole.py) - Cole-Cole BCA with RC circuits
- **Test 35**: [test_max30009_build_base_table.py](test_max30009_build_base_table.py) - Base table generation
- **Test 53**: tests/fw-app-integration/test_ads1293_sync_markers.py - Sync marker format validation

---

## Expected Results

### Typical Good Results

```
Resistance MAE:  0.3 - 0.5 Ω
Impedance MAE:   0.3 - 0.5 Ω
Sync markers:    Exactly 60 per 60s recording
Sampling freq:   400 ± 0.2 Hz
```

### Acceptable Results

```
Resistance MAE:  0.5 - 2.0 Ω
Impedance MAE:   0.5 - 3.0 Ω
Sync markers:    58-62 per 60s recording
Sampling freq:   400 ± 1.0 Hz
```

### Marginal/Failing Results

```
Resistance MAE:  > 2.0 Ω      ← Investigate calibration
Impedance MAE:   > 3.0 Ω      ← Check connections
Sync markers:    Non-monotonic ← Firmware bug
Sampling freq:   > 401 Hz      ← Buffer/timing issue
```

---

## References

- **Firmware**: services/spi-service/MAX30009_LIB/
- **Protocol**: JSON_PROTOCOL_REFERENCE.md
- **Sync Markers**: services/spi-service/src/main.cpp (lines 159-209)
- **ICG Theory**: Bioimpedance spectroscopy standards
