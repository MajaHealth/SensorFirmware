# Automated Hardware Testing Workflow

**Project:** Sensor Firmware Build
**Date:** 2025-12-26
**Audience:** Stakeholders & Project Managers

---

## 1. Overview

**Goal:** Automatically test firmware and hardware on Raspberry Pi CM4, collect sensor data, and analyze results on development laptop.

**What Gets Tested:**
- ✅ ECG sensor (ADS1293) - heart rate, signal quality
- ✅ Bio-impedance sensor (MAX30009) - impedance measurements
- ✅ Battery & power management
- ✅ Data synchronization between sensors
- ✅ Long-duration stability (1-hour tests)

**Test Count:** 48 automated tests across sensor integration and firmware APIs

---

## 2. Testing Architecture (Simplified)

```
┌─────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT LAPTOP                                              │
│                                                                 │
│  Developer writes tests                                        │
│         ↓                                                       │
│  Run: ./scripts/build-and-deploy.sh --with-tests              │
│         ↓                                                       │
│  Build firmware + Deploy to CM4                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ (SSH/SCP)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ RASPBERRY PI CM4 (Device Under Test)                           │
│                                                                 │
│  ┌──────────────┐         ┌─────────────────┐                 │
│  │   pytest     │ ──────→ │ Firmware        │                 │
│  │   (Tests)    │         │ Services        │                 │
│  │              │         │ • ADS1293:1293  │                 │
│  │ Sends JSON   │         │ • MAX30009:30009│ ──────┐         │
│  │ commands     │         │ • Power:501     │        │         │
│  └──────────────┘         └─────────────────┘        │         │
│         │                                             │         │
│         │                                             ↓         │
│         │                                  ┌──────────────────┐ │
│         │                                  │ Real Hardware    │ │
│         ↓                                  │ • ECG sensor     │ │
│  /tmp/test-results/                       │ • Bio-Z sensor   │ │
│  ├── test_report.html                     │ • Battery        │ │
│  ├── ecg_data.jsonl                       │ • LEDs           │ │
│  ├── impedance_data.jsonl                 └──────────────────┘ │
│  └── plots/                                                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ (Automatic transfer)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT LAPTOP                                              │
│                                                                 │
│  test-results-2025-12-26-143022/                               │
│  ├── test_report.html          ← Open in browser              │
│  ├── ecg_data.jsonl            ← Analyze signal quality       │
│  ├── impedance_data.jsonl      ← Verify measurements          │
│  └── plots/                    ← Review visualizations        │
│      ├── ecg_fft.png                                           │
│      └── cole_cole_plot.png                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Key Principle:**
- pytest **simulates your application** by sending JSON commands to firmware
- Firmware responds with real sensor data from hardware
- No application code needed during testing

---

## 3. How pytest Simulates the Application

### Traditional Testing (Complex):
```
App → Firmware → Hardware
 ↑
 └── How do we test this?
     • Need to modify App
     • Or add proxy between App and Firmware
     • Or modify Firmware to support multiple clients
```

### Our Approach (Simple):
```
pytest → Firmware → Hardware
  ↑
  └── pytest sends the same JSON commands that App would send
      No App needed during testing!
```

### Example Test Sequence:

**What the App does in production:**
```python
# App code (production)
1. Connect to port 1293
2. Send: {"type": "settings", "enable_conversion": true}
3. Send: {"type": "get_data"}
4. Receive ECG data
5. Display to user
```

**What pytest does during testing:**
```python
# pytest code (testing)
1. Connect to port 1293
2. Send: {"type": "settings", "enable_conversion": true}
3. Send: {"type": "get_data"}
4. Receive ECG data
5. Validate quality, save to file, analyze
```

**Result:** Same JSON commands, same firmware behavior, same hardware data!

---

## 4. Step-by-Step Test Execution

### Step 1: Developer Triggers Test

```bash
# On laptop
./scripts/build-and-deploy.sh --with-tests
```

### Step 2: Automated Deployment

The script automatically:
1. ✅ Builds firmware (if code changed)
2. ✅ Connects to CM4 via SSH
3. ✅ Copies firmware binaries to CM4
4. ✅ Copies test suite to CM4
5. ✅ Installs pytest dependencies

### Step 3: Test Execution on CM4

```bash
# Script runs on CM4:
pytest tests/hardware-integration/ \
  --config=tests/config/test_config.yaml \
  --html=/tmp/test-results/report.html \
  -v
```

**What happens:**
- pytest starts
- For each test:
  - Connect to firmware service (port 1293, 30009, or 501)
  - Send JSON commands (from API spec)
  - Collect sensor data
  - Validate measurements
  - Log results
- Generate HTML report with PASS/FAIL status

### Step 4: Automatic Result Transfer

```bash
# Script automatically transfers:
scp -r pi@CM4:/tmp/test-results/* ./test-results-2025-12-26/
```

### Step 5: Review Results

Developer opens `test_report.html` in browser:

```
✅ Test: ADS1293 ECG 60s acquisition - PASSED
   • Sampling rate: 400.2 Hz (within ±1 Hz tolerance)
   • Sync counters: Monotonic, no missing frames
   • BPM detected: 62 bpm (expected: 60 ± 3 bpm)

✅ Test: MAX30009 ICG 1-hour recording - PASSED
   • Impedance error: 1.8 Ω (< 3 Ω threshold)
   • Resistance MAE: 1.5 Ω (< 2 Ω threshold)

❌ Test: Synchronized acquisition drift - FAILED
   • Clock drift: 75 ms (> 50 ms threshold)
   • Action required: Check sync marker implementation
```

---

## 5. Test Categories

### Group 1: Hardware Integration Tests (15 tests)

**Purpose:** Validate sensor data quality with real hardware

| Test ID | Description | Duration | Hardware Needed |
|---------|-------------|----------|-----------------|
| 7 | MAX30009 BCA (Cole-Cole) | 55s | RC circuit model |
| 8 | MAX30009 ICG (resistor loads) | 60s | Resistor loads (20-300Ω) |
| 9 | MAX30009 ICG long-duration | 1 hour | 100Ω resistor |
| 10 | ADS1293 ECG acquisition | 60s | ECG simulator |
| 11 | ADS1293 ECG long-duration | 1 hour | ECG simulator |
| 12 | Synchronized acquisition | 1 hour | ECG + resistor load |

**Validation Metrics:**
- ✅ Sampling rate: 400 Hz ± 1 Hz
- ✅ Sync counters: Monotonic increase, no gaps
- ✅ ECG accuracy: ±25 µV (low) / ±40 µV (high)
- ✅ Impedance accuracy: < 3 Ω error
- ✅ BPM detection: ±3 bpm

**Example Test Flow:**

```python
# Test: ADS1293 60-second ECG acquisition
def test_ads1293_ecg_60s():
    # 1. Connect to ADS1293 service
    client = TCPClient('127.0.0.1', 1293)

    # 2. Configure sensor
    response = client.send({
        "type": "settings",
        "enable_conversion": True,
        "R2_rate": 4,
        "R3_rate": 128
    })
    assert response["type"] == "actual_settings"

    # 3. Collect data for 60 seconds
    all_data = []
    for i in range(120):  # 0.5s intervals
        data = client.send({"type": "get_data"})
        all_data.extend(data["data"])
        time.sleep(0.5)

    # 4. Validate sync counters
    sync_counters = extract_sync_markers(all_data)
    assert is_monotonic(sync_counters)  # No missing frames

    # 5. Validate sampling rate
    actual_rate = calculate_sampling_rate(all_data, duration=60)
    assert abs(actual_rate - 400) <= 1  # Within ±1 Hz

    # 6. Validate BPM
    detected_bpm = detect_bpm(all_data)
    expected_bpm = 60  # ECG simulator setting
    assert abs(detected_bpm - expected_bpm) <= 3

    # 7. Save data for offline analysis
    save_to_file(all_data, "/tmp/test-results/ecg_60s.jsonl")
```

---

### Group 3: Firmware API Tests (33 tests)

**Purpose:** Validate JSON API behavior and protocol correctness

| Category | Test Count | Examples |
|----------|------------|----------|
| MAX30009 API | 15 tests | Settings, get_data, calibration, state machine |
| ADS1293 API | 10 tests | Settings, get_data, power control |
| Power Service | 5 tests | Battery info, charge control, button events |
| Sync Integrity | 3 tests | Sync marker validation, drift computation |

**Example Test:**

```python
# Test: MAX30009 state machine during calibration
def test_max30009_calibration_flow():
    client = TCPClient('127.0.0.1', 30009)

    # Start calibration
    response = client.send({"type": "start_calibrate"})
    assert response["type"] == "calibrate_started"

    # Collect asynchronous calibration messages
    calib_messages = []
    timeout = time.time() + 300  # 5 minutes max
    while time.time() < timeout:
        msg = client.receive_async()
        if msg["type"] == "calib_data":
            calib_messages.append(msg)
        elif msg["type"] == "calibrate_complete":
            break

    # Validate calibration data received for all frequencies
    frequencies = [m["stimulate_frequency"] for m in calib_messages]
    assert len(set(frequencies)) >= 11  # All frequency points
```

---

## 6. Test Configuration

All test parameters stored in YAML config file:

```yaml
# tests/config/test_config.yaml

services:
  ads1293:
    host: "127.0.0.1"
    port: 1293
  max30009:
    host: "127.0.0.1"
    port: 30009

max30009_icg:
  sampling_frequency: 400
  current_ua: 1.28
  stim_frequency_khz: 20
  duration_sec: 60

thresholds:
  max30009:
    impedance_max_ohm: 3
    resistance_mae_ohm: 2
  ads1293:
    voltage_error_low_uv: 25
    bpm_error_absolute: 3
```

**Benefits:**
- ✅ Easy to adjust test parameters without code changes
- ✅ Different configurations for different hardware setups
- ✅ Clear documentation of acceptance criteria

---

## 7. Test Output & Reporting

### Output Files (on CM4):

```
/tmp/test-results/
├── test_report.html              # Main HTML report (PASS/FAIL summary)
├── test_report.json              # Machine-readable results
│
├── data/                         # Raw sensor data
│   ├── test_007_bca_data.jsonl
│   ├── test_010_ecg_60s.jsonl
│   └── test_012_sync_ecg.jsonl
│
├── logs/                         # Test execution logs
│   ├── pytest.log
│   └── firmware_output.log
│
└── plots/                        # Analysis visualizations
    ├── test_007_cole_cole.png
    ├── test_010_ecg_fft.png
    └── test_012_sync_drift.png
```

### HTML Report Example:

```
═══════════════════════════════════════════════════════════
SENSOR FIRMWARE TEST REPORT
Executed: 2025-12-26 14:30:22
Platform: Raspberry Pi CM4
Duration: 2h 15m
═══════════════════════════════════════════════════════════

SUMMARY:
  Total Tests:    48
  Passed:         46  ✅
  Failed:         2   ❌
  Skipped:        0
  Success Rate:   95.8%

═══════════════════════════════════════════════════════════

FAILED TESTS:

❌ test_012_synchronized_acquisition
   Duration: 1h 0m 15s
   Error: Clock drift exceeded threshold
   Details:
     • Expected: < 50 ms
     • Actual: 75 ms
     • Location: tests/hardware-integration/test_synchronized_acquisition.py:142
   Data: test-results/data/test_012_sync_ecg.jsonl

❌ test_056_max30009_long_duration
   Duration: 1h 0m 8s
   Error: Sampling rate error out of tolerance
   Details:
     • Expected: 400 Hz ± 1 Hz
     • Actual: 401.5 Hz
     • Location: tests/hardware-integration/test_max30009_icg.py:89
   Data: test-results/data/test_056_icg_1hr.jsonl

═══════════════════════════════════════════════════════════

PASSED TESTS: (46 tests)
✅ test_007_max30009_bca
✅ test_008_max30009_icg_resistor_loads
✅ test_010_ads1293_ecg_60s
...
```

### Data File Format (JSONL):

Each line is a JSON object:
```json
{"timestamp": "2025-12-26 14:30:45.123", "sample": [12345, -6789, 98765]}
{"timestamp": "2025-12-26 14:30:45.126", "sample": [12350, -6780, 98770]}
{"timestamp": "2025-12-26 14:30:46.123", "sample": [-99999, 379, 0]}
```

**Benefits:**
- ✅ Line-by-line streaming (handles large files)
- ✅ Easy to parse and analyze
- ✅ Compatible with pandas, numpy

---

## 8. Timeline & Execution

### Test Execution Time

| Test Category | Count | Duration | Total Time |
|---------------|-------|----------|------------|
| Quick API tests | 20 | < 1 min | ~15 minutes |
| 60-second tests | 10 | ~1 min | ~10 minutes |
| 1-hour tests | 5 | ~1 hour | ~5 hours |
| **Full Suite** | **48** | **Mixed** | **~8-10 hours** |

**Typical Usage:**

- **During Development:** Run quick API tests (~15 min)
- **Before Release:** Run full suite overnight (~10 hrs)
- **On Demand:** Run specific test categories

### Command Examples:

```bash
# Quick smoke test (API only)
pytest tests/fw-app-integration/ -v

# Hardware tests only
pytest tests/hardware-integration/ -v

# Specific test
pytest tests/hardware-integration/test_ads1293_ecg.py::test_60s_acquisition -v

# Full suite
pytest tests/ -v
```

---

## 9. Success Criteria

### Test Passes When:

✅ **Sampling Rate Accuracy**
- Measured rate within ±1 Hz of configured rate (e.g., 400 Hz)

✅ **Sync Counter Integrity**
- Monotonically increasing every 1 second
- No missing or duplicate sync markers

✅ **Measurement Accuracy**
- ECG voltage: ±25 µV (low signals) or ±40 µV (high signals)
- Impedance: < 3 Ω error
- Resistance: < 2 Ω mean absolute error
- BPM: ±3 bpm or ±1%

✅ **Data Continuity**
- No buffer overflows
- No data loss during long recordings
- Timestamps accurate and monotonic

✅ **Protocol Compliance**
- All JSON commands accepted
- Responses match specification
- Error handling correct

---

## 10. Benefits of This Approach

### For Development Team:

✅ **No Application Dependency**
- Test firmware independently
- pytest simulates application behavior
- No need to modify application code

✅ **Fast Iteration**
- Write test once, run repeatedly
- Automated validation reduces manual testing
- Quick feedback on code changes

✅ **Comprehensive Coverage**
- 48 automated tests
- Both API and hardware validation
- Long-duration stability testing

### For Quality Assurance:

✅ **Repeatable Testing**
- Same tests run identically every time
- No human error in test execution
- Consistent validation criteria

✅ **Traceable Results**
- HTML reports with detailed metrics
- Raw data files for offline analysis
- Plots for visual inspection

✅ **Early Bug Detection**
- Catch issues before production
- Validate hardware integration
- Verify multi-hour stability

### For Project Management:

✅ **Clear Metrics**
- Pass/fail rates
- Test coverage
- Performance benchmarks

✅ **Risk Mitigation**
- Automated regression testing
- Hardware validation before deployment
- Documentation of test procedures

✅ **Time Savings**
- 8-10 hours automated testing vs. weeks of manual testing
- Overnight execution (no human intervention)
- Reproducible results

---

## 11. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hardware not connected | Medium | High | Pre-test hardware validation |
| Network issues during transfer | Low | Low | Retry logic + local backup |
| Test data too large | Medium | Low | Compress data, selective logging |
| CM4 runs out of disk space | Low | Medium | Clean up old results before test |
| Long test interrupted | Low | High | Checkpoint/resume mechanism |

---

## 12. Next Steps

### Phase 1: Infrastructure Setup (Week 1)
- ✅ Create directory structure
- ✅ Write TCP client utility
- ✅ Implement data loggers and validators
- ✅ Create test configuration YAML
- ✅ Modify build-and-deploy.sh

### Phase 2: API Tests (Week 2)
- ✅ Implement 33 firmware API tests
- ✅ Validate JSON protocol
- ✅ Test error handling

### Phase 3: Hardware Tests (Week 3)
- ✅ Implement 15 hardware integration tests
- ✅ ECG acquisition tests
- ✅ Bio-impedance tests
- ✅ Synchronized acquisition

### Phase 4: Validation & Documentation (Week 4)
- ✅ Run full test suite on CM4
- ✅ Validate against real hardware
- ✅ Document test procedures
- ✅ Train team on test execution

---

## 13. Frequently Asked Questions

**Q: Does the application need to be stopped during testing?**
A: Yes, pytest needs exclusive access to firmware ports (1293, 30009, 501). The test script will automatically stop/start services.

**Q: Can we run tests on the development laptop?**
A: No, tests require real CM4 hardware (ADS1293, MAX30009 sensors). Tests are deployed to CM4 and run there.

**Q: How long does a full test run take?**
A: ~8-10 hours for all 48 tests. Quick API tests take ~15 minutes.

**Q: What if a test fails?**
A: The HTML report shows exactly which metric failed (e.g., "Clock drift: 75 ms > 50 ms threshold"). Raw data files allow offline debugging.

**Q: Can we customize test parameters?**
A: Yes, edit `tests/config/test_config.yaml` to change thresholds, durations, sampling rates, etc.

**Q: What hardware is required for testing?**
A: CM4 with sensors, plus external equipment:
- ECG simulator (for ADS1293 tests)
- RC circuit model (for MAX30009 BCA tests)
- Resistor loads 20-300Ω (for MAX30009 ICG tests)

**Q: How are results transferred to laptop?**
A: Automatically via SCP after tests complete. Results copied to `./test-results-<timestamp>/`

---

## 14. Summary

**What:** Automated testing framework for sensor firmware on CM4

**How:** pytest sends JSON commands to firmware, validates sensor data

**Where:** Tests run on CM4, results analyzed on laptop

**When:** On-demand or scheduled (nightly builds)

**Why:** Ensure firmware quality, validate hardware integration, reduce manual testing

**Result:** 48 automated tests providing comprehensive validation in 8-10 hours

---

**Document Version:** 1.0
**Date:** 2025-12-26
**Prepared For:** Stakeholder Review
