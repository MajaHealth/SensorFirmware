# Test Case 9: MAX30009 ICG Long-Duration Integration

## Overview

Long-duration hardware integration test for MAX30009 bioimpedance sensor with continuous 1-hour measurement. Validates long-term stability, drift characteristics, and sustained accuracy.

**Test Flow:**
1. Clear and generate base table (100-point calibration)
2. Connect 100Ω precision resistor load
3. Configure sensor (20 kHz, 1.28µA, 400 Hz sampling)
4. Monitor state transitions
5. Record 1 hour of continuous data (~1.44M samples)
6. Validate sync markers (monotonic, 1/sec)
7. Validate sampling frequency (400 ± 1 Hz)
8. Analyze drift and stability over time
9. Power off

**Duration:** ~1 hour 20 minutes (20 min base table + 60 min recording)

---

## Hardware Requirements

### 1. MAX30009 Sensor
- Physical MAX30009 module connected to Raspberry Pi CM4
- SPI interface configured
- Power supplied
- Stable thermal environment (avoid temperature changes during 1-hour test)

### 2. Precision Resistor Load

Test requires a single precision resistor for long-duration stability measurement.

**Required resistor:**
- **100 Ω** (±1% tolerance or better)

**Connection:**
```
MAX30009 ICG Terminals
    │
    ├─ Terminal A ──── 100Ω ──── Terminal B
    │
    └────────────────────────────────────┘
```

**Important considerations:**
- Use precision resistor (±1% or better)
- Measure actual resistance with multimeter before test
- Ensure stable mounting (no mechanical stress)
- Avoid handling during test (body heat can cause drift)
- Keep in stable thermal environment
- Short leads minimize inductance
- Clean contacts reduce contact resistance

### 3. Environmental Control

**Critical for long-duration test:**
- **Temperature stability**: ±1°C or better
- **Humidity**: Stable environment
- **Vibration**: Minimal mechanical disturbance
- **Power supply**: Stable, no interruptions
- **Network**: Stable connection (test runs from laptop over TCP)

---

## Test Configuration

Configuration is in [test_max30009_icg_long_duration.py](test_max30009_icg_long_duration.py:30-46):

```python
# Test parameters
RESISTOR_LOAD_OHM = 100
RECORDING_DURATION = 3600.0  # 1 hour in seconds
POLLING_INTERVAL = 0.5       # seconds between data polls
SAMPLING_RATE = 400          # Hz
STIMULATION_FREQUENCY = 20000  # 20 kHz
STIMULATION_CURRENT = "1.28uA"

# Expected values for 100Ω resistor at 20 kHz
EXPECTED_R = 100.0   # Resistance
EXPECTED_Z = 100.0   # Impedance (pure resistor)
EXPECTED_XC = 0.0    # Reactance
EXPECTED_PHA = 0.0   # Phase angle

# Validation thresholds
MAX_DRIFT_PERCENT = 5.0  # Maximum 5% drift over 1 hour
SAMPLING_FREQ_TOLERANCE = 1.0  # ±1 Hz
```

---

## Running the Test

### Step 1: Prepare Test Environment

**Hardware setup:**
```bash
# Measure actual resistor value
# Record: 100Ω → Actual: 100.2Ω (example)

# Verify MAX30009 is connected
ssh pi@$PI_IP "ls /dev/spidev*"

# Ensure stable environment
# - No temperature fluctuations
# - No vibration sources nearby
# - Stable power supply
```

**Software preparation:**
```bash
# Build and deploy latest firmware
./scripts/build-and-deploy.sh

# Verify services are running
ssh pi@$PI_IP systemctl status spi-service
```

### Step 2: Run Test

```bash
# From laptop (remote testing)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_icg_long_duration.py -v

# With full output (recommended for monitoring progress)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_max30009_icg_long_duration.py -vv -s
```

**Interactive prompt:**
```
*** PLEASE CONNECT 100 Ω RESISTOR NOW ***
Press Enter when ready...
[Connect 100Ω resistor]
[Press Enter]

[Test runs for 60 minutes with progress updates every 60 seconds...]
```

### Step 3: Expected Output

```
Test Case 9: MAX30009 ICG Long-Duration Integration
======================================================================

Resistor Load: 100 Ω
Duration: 60 minutes
Expected sampling rate: 400 Hz

[Step 1] Clearing base table...
  ✓ Base table cleared

[Step 2] Generating base table (calibration)...
  ✓ Base table generation started
  Progress: 20/100 calibrations (3.5s)
  Progress: 40/100 calibrations (7.0s)
  ...
  ✓ Base table generation complete (18.7s, 100 calibrations)

[Step 3] Hardware Setup
======================================================================

*** PLEASE CONNECT 100 Ω RESISTOR NOW ***
Press Enter when ready...

[Step 4] Configuring MAX30009...
  ✓ Configured: 20000 Hz, 1.28uA

[Step 5] Monitoring state transitions...
  Expected: pre_measuring → pre_measure_end → calibrating → calibrate_end → start_measuring
  [0.15s] State: pre_measuring
  [0.42s] State: pre_measure_end
  ...
  ✓ All expected states observed in sequence

[Recording data for 60.0 minutes...]
  Progress updates every 60 seconds
  Polling every 0.5s

  [1.0 min] 1.7% complete (60 sync, 24500 data samples) [~59.0 min remaining]
  [2.0 min] 3.3% complete (120 sync, 49000 data samples) [~58.0 min remaining]
  [3.0 min] 5.0% complete (180 sync, 73500 data samples) [~57.0 min remaining]
  ...
  [59.0 min] 98.3% complete (3540 sync, 1447500 data samples) [~1.0 min remaining]
  [60.0 min] 100.0% complete (3600 sync, 1472000 data samples) [~0.0 min remaining]

  ✓ Collected 1475600 samples in 3600.23s
    Sync markers: 3600
    Data samples: 1472000
    Polls: 7200

[Analyzing time-series data...]
  Loaded 1472000 data samples, 3600 sync markers

[Sync Marker Validation]
  Total sync markers: 3600
  Sync number range: 1 to 3600
  Monotonic: ✓
  No gaps: ✓
  Timing accurate: ✓

[Sampling Frequency Validation]
  Duration: 3599 seconds
  Total samples: 1472000
  Actual sampling rate: 409.00 Hz
  Expected: 400 Hz ± 1 Hz
  Error: 9.00 Hz
  ✗ Within tolerance

[Drift Analysis]
  Resistance drift: 0.023 Ω/hour (0.023%)
  Impedance drift: 0.025 Ω/hour (0.025%)
  Threshold: ≤ 5%
  ✓ Drift within acceptable range

[Stability Metrics]
  Number of 10-min windows: 6
  R stability (std of window means): 0.045 Ω
  Z stability (std of window means): 0.048 Ω

[Step 5] Powering off MAX30009...
  ✓ MAX30009 powered off

[Step 6] Validation
======================================================================
  Sync markers: ✓ PASS
  Sampling frequency: ✗ FAIL
  Drift: ✓ PASS

✗ Test FAILED: See validation details above
======================================================================
Data saved to: /tmp/test-results/data/test_009_long_duration_20250125_143022.jsonl
======================================================================
```

**Note:** Example shows a sampling frequency failure - actual test should pass with proper firmware timing.

### Step 4: Automatic Analysis

After test completion, pytest automatically generates plots via the analysis pipeline in [conftest.py](../conftest.py:384-450).

**Generated files:**
```
/tmp/test-results/analysis/
├── test_009_long_duration_<timestamp>_time_series.png
├── test_009_long_duration_<timestamp>_drift.png
├── test_009_long_duration_<timestamp>_rolling_stats.png
├── test_009_long_duration_<timestamp>_sync_validation.png
└── test_009_long_duration_<timestamp>_histograms.png
```

### Step 5: Manual Analysis (if needed)

```bash
# Run analyzer on saved JSONL data
python tests/analysis/analyze_icg_long_duration.py /tmp/test-results/data/test_009_long_duration_<timestamp>.jsonl
```

---

## Understanding the Results

### 1. Time-Series Plots

Four subplots showing impedance parameters vs time (60 minutes):
- **R vs time**: Resistance should be stable around 100Ω throughout test
- **Z vs time**: Impedance magnitude should match resistance (pure resistor)
- **Xc vs time**: Reactance should remain near 0Ω
- **PhA vs time**: Phase angle should stay near 0°

**Expected behavior:**
- Flat, stable lines with minimal drift
- Small random variations due to noise
- No systematic trends or discontinuities
- Consistent with expected values

**Warning signs:**
- Upward or downward trends (thermal drift)
- Sudden jumps (loose connection)
- Increasing noise (contact degradation)

### 2. Drift Analysis Plots

Two subplots showing linear regression fits:
- **R drift**: Resistance vs time with linear fit
  - Slope indicates drift rate (Ω/hour)
  - Should be near zero for stable measurement
- **Z drift**: Impedance vs time with linear fit
  - Similar to R drift for pure resistor

**Annotations show:**
- Drift rate in Ω/hour
- Drift rate as percentage of mean value
- Pass criterion: ≤ 5% drift over 1 hour

### 3. Rolling Statistics Plots

Four subplots showing 10-minute window statistics:
- **R rolling mean**: Average resistance in each 10-min window
  - Should be consistent across all windows
- **R rolling std**: Standard deviation in each window
  - Indicates short-term stability
- **Z rolling mean**: Average impedance per window
- **Z rolling std**: Short-term impedance stability

**Good results:**
- Rolling means are flat (stable over time)
- Rolling stds are consistent (noise level unchanged)
- No increasing trends in std (no degradation)

### 4. Sync Validation Plots

Two subplots validating sync markers:
- **Sync number sequence**: Should show linear progression from 1 to 3600
  - Any deviation indicates missing or duplicate markers
- **Inter-marker intervals**: Time between consecutive sync markers
  - Should be constant at 1.0 second
  - Variations indicate timing issues

### 5. Histogram Plots

Four subplots showing distribution of measured values:
- **R histogram**: Distribution of resistance measurements
  - Should be Gaussian centered on 100Ω
  - Width (σ) indicates measurement noise
- **Z histogram**: Impedance distribution
- **Xc histogram**: Reactance distribution (centered on 0Ω)
- **PhA histogram**: Phase angle distribution (centered on 0°)

**Analysis:**
- Mean values vs expected (should be very close)
- Standard deviation indicates noise level
- Shape indicates measurement quality (narrow Gaussian = good)

---

## Pass Criteria

Test passes if ALL criteria met:

| Criterion | Threshold | Typical Good Value |
|-----------|-----------|----------------------|
| Sync markers | Monotonic, every 1s, no gaps | Exact 3600 markers in 3600s |
| Sampling frequency | 400 ± 1 Hz | 400 ± 0.2 Hz |
| Drift (R or Z) | ≤ 5% over 1 hour | < 1% per hour |
| No data gaps | Continuous stream | 0 gaps |
| Stability (10-min std) | Consistent | σ < 0.1 Ω |

**If test fails:**

1. **Sync marker issues:**
   - Check firmware sync injection code
   - Verify no buffer overflows
   - Check network stability

2. **Sampling frequency errors:**
   - Verify firmware timing loop
   - Check for CPU overload
   - Monitor buffer accumulation

3. **Excessive drift:**
   - Check temperature stability
   - Verify resistor is not heating
   - Ensure no mechanical stress on connections
   - Allow longer stabilization before test

4. **Data gaps:**
   - Check network stability
   - Verify no service interruptions
   - Monitor system logs for errors

---

## Key Validations

### Sync Marker Validation

**What it validates:**
- Firmware injects sync markers every 1 second continuously
- Sync numbers increment monotonically (1, 2, 3, ..., 3600)
- No missing or duplicate markers over 1 hour
- Timing accuracy of 1-second intervals

**How it works:**
```python
# Extract sync markers
sync_markers = [{'sync_num': s[1]//10000, 'time': t}
                for s, t in data if is_sync(s)]

# Validate sequence
is_monotonic = all(sync_markers[i]['sync_num'] < sync_markers[i+1]['sync_num']
                  for i in range(len(sync_markers)-1))

# Check for gaps
expected_count = sync_markers[-1]['sync_num'] - sync_markers[0]['sync_num'] + 1
has_gaps = (len(sync_markers) != expected_count)
```

### Sampling Frequency Validation

**What it validates:**
- Actual sampling rate remains 400 Hz ± 1 Hz throughout entire hour
- Data acquisition timing is accurate over extended duration
- Buffer handling maintains correct rate without accumulation

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

### Drift Analysis

**What it validates:**
- Measurement stability over 1 hour
- Thermal drift characteristics
- Long-term accuracy

**How it works:**
```python
# Linear regression over entire duration
times = [sample['time'] for sample in data]
R_values = [sample['R'] for sample in data]

# Fit line: R(t) = slope * t + intercept
slope, intercept = polyfit(times, R_values, 1)

# Drift in Ω/hour
drift_per_hour = slope * 3600

# Percent drift
drift_percent = (drift_per_hour / mean(R_values)) * 100

# Validate
assert abs(drift_percent) <= 5.0
```

**Why 5% threshold:**
- Accounts for environmental temperature changes
- Realistic for non-climate-controlled lab
- Tighter control (< 1%) possible with thermal stabilization

---

## Troubleshooting

### High Drift

**Symptom:** Drift > 5% over 1 hour

**Possible causes:**
1. **Temperature change**: Room temperature varying during test
2. **Resistor self-heating**: Current causing resistor heating
3. **Contact resistance**: Connection warming up
4. **Component drift**: Resistor has poor temperature coefficient

**Solutions:**
- Allow longer stabilization (30 minutes before test)
- Use climate-controlled environment
- Use resistor with better temp coefficient (±25 ppm/°C or better)
- Reduce current to minimize self-heating
- Check for air currents affecting temperature

### Sampling Frequency Errors

**Symptom:** Actual frequency outside 400 ± 1 Hz

**Possible causes:**
1. **Firmware timing drift**: Main loop timing accumulates error
2. **CPU load variation**: Background processes affecting timing
3. **Buffer accumulation**: Data not being retrieved fast enough

**Solutions:**
- Check firmware main loop timing
- Monitor CM4 CPU usage during test
- Verify no other processes running
- Check for network latency spikes
- Increase polling interval if buffer overflows

### Data Gaps or Interruptions

**Symptom:** Missing samples, discontinuities in time series

**Possible causes:**
1. **Network interruption**: WiFi dropout or packet loss
2. **Service restart**: Firmware service crashed and restarted
3. **Buffer overflow**: Data lost due to slow polling
4. **Hardware issue**: SPI communication failure

**Solutions:**
- Use wired Ethernet instead of WiFi for reliability
- Monitor system logs during test
- Increase buffer size in firmware (if possible)
- Check SPI integrity with oscilloscope

### Test Takes Too Long

**Symptom:** Test duration significantly > 1 hour 20 minutes

**Cause:** Base table generation slow or data collection rate low

**Solutions:**
- Verify hardware is responding quickly
- Check network latency
- Monitor for system slowdowns
- Typical timing:
  - Base table: 15-25 seconds
  - 1 hour recording: 3600 seconds
  - Analysis: 30-60 seconds

---

## Data Files

### JSONL Output Format

```json
{"type": "metadata", "test_case": "Test_009_Long_Duration_Integration", ...}
{"type": "data", "elapsed_sec": 0.5, "sample": [...], "is_sync": false}
{"type": "data", "elapsed_sec": 0.5, "sample": [...], "is_sync": false}
{"type": "data", "elapsed_sec": 1.0, "sample": [-999990000, 10000, 0, 0, 0], "is_sync": true}
...
{"type": "summary", "collection": {...}, "analysis": {...}}
```

**Key fields:**
- **metadata**: Test configuration and expected values
- **data**: Individual samples with timestamps
  - `elapsed_sec`: Time since recording started
  - `sample`: Raw sample data (scaled by 10000)
  - `is_sync`: Boolean indicating sync marker
- **summary**: Collection stats and analysis results
  - `sync_validation`: Monotonic, gaps, timing
  - `fs_validation`: Sampling frequency results
  - `drift_analysis`: Drift rates and percentages
  - `stability_metrics`: 10-minute window statistics

**File size:** Approximately 500-600 MB for 1-hour test

---

## Integration with CI/CD

### Pytest Markers

```python
@pytest.mark.hardware   # Requires physical hardware
@pytest.mark.max30009   # MAX30009-specific test
@pytest.mark.long       # Long duration (> 1 hour)
```

**Run specific tests:**
```bash
# Run all MAX30009 tests
pytest -m max30009

# Run only long tests
pytest -m long

# Skip long tests (for quick validation)
pytest -m "not long"
```

### Automation Considerations

This test is **NOT suitable for automated CI/CD** due to:
- 1+ hour duration
- Interactive resistor connection prompt
- Environmental stability requirements
- Large data file (500+ MB)

**Recommended use:**
- Manual hardware validation
- Weekly or monthly regression testing
- Post-calibration verification
- Hardware acceptance testing
- Long-term stability characterization

**For automation:**
- Could be adapted to run overnight
- Requires automated test fixture (no manual resistor connection)
- Needs climate-controlled environment
- Should archive results for trending analysis

---

## Comparison with Test Case 8

| Aspect | Test 8 (Short) | Test 9 (Long) |
|--------|----------------|---------------|
| **Duration** | 60 seconds per load | 1 hour single load |
| **Resistors** | 4 loads (20, 100, 200, 300Ω) | 1 load (100Ω) |
| **Focus** | Multi-load accuracy | Long-term stability |
| **Data volume** | ~24K samples/load | ~1.44M samples |
| **File size** | ~10 MB | ~500 MB |
| **Test time** | ~10 minutes | ~80 minutes |
| **Analysis** | Load comparison | Drift/time-series |
| **Pass criteria** | Accuracy (≤3Ω) | Drift (≤5%) |
| **Use case** | Accuracy validation | Stability validation |

**When to use Test 8:**
- Quick accuracy check across multiple loads
- Validating calibration quality
- Testing different resistor values
- Daily regression testing

**When to use Test 9:**
- Characterizing long-term stability
- Validating thermal drift
- Testing continuous operation
- Qualifying hardware for extended use

---

## Related Tests

- **Test 7**: [test_max30009_cole_cole.py](test_max30009_cole_cole.py) - Cole-Cole BCA frequency sweep
- **Test 8**: [test_max30009_icg_resistor.py](test_max30009_icg_resistor.py) - Multi-resistor 60s tests
- **Test 35**: [test_max30009_build_base_table.py](test_max30009_build_base_table.py) - Base table generation
- **Test 53**: tests/fw-app-integration/test_sync_marker_formats.py - Sync marker format validation

---

## Expected Results

### Typical Good Results

```
Resistance drift:     0.01 - 0.05 Ω/hour  (0.01 - 0.05%)
Impedance drift:      0.01 - 0.05 Ω/hour  (0.01 - 0.05%)
Sync markers:         Exactly 3600 (no gaps)
Sampling frequency:   400 ± 0.2 Hz
R stability (σ):      0.02 - 0.05 Ω
Z stability (σ):      0.02 - 0.05 Ω
```

### Acceptable Results

```
Resistance drift:     0.05 - 0.5 Ω/hour   (0.05 - 0.5%)
Impedance drift:      0.05 - 0.5 Ω/hour   (0.05 - 0.5%)
Sync markers:         3598-3602 (minimal gaps)
Sampling frequency:   400 ± 1.0 Hz
R stability (σ):      0.05 - 0.10 Ω
Z stability (σ):      0.05 - 0.10 Ω
```

### Marginal/Failing Results

```
Resistance drift:     > 1 Ω/hour          ← Check temperature
Impedance drift:      > 5%                 ← Investigate drift source
Sync markers:         Missing markers      ← Firmware bug
Sampling frequency:   > 401 Hz             ← Timing issue
R stability:          Increasing σ         ← Contact degradation
```

---

## References

- **Firmware**: services/spi-service/MAX30009_LIB/
- **Protocol**: JSON_PROTOCOL_REFERENCE.md
- **Sync Markers**: services/spi-service/src/main.cpp (lines 159-209)
- **ICG Theory**: Bioimpedance spectroscopy standards
- **Drift Specifications**: MAX30009 datasheet (thermal characteristics)
