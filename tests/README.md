# Test Suite Documentation

Complete testing guide for sensor firmware. Tests run on your laptop and connect to CM4 firmware services via TCP/IP.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Architecture](#test-architecture)
- [Test Categories](#test-categories)
- [Available Test Cases](#available-test-cases)
- [Running Tests](#running-tests)
- [Test Configuration](#test-configuration)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## Quick Start

### First-Time Setup

```bash
# 1. Set CM4 IP address (replace with your CM4's IP)
export PI_IP=192.168.x.x

# 2. Create virtual environment on your laptop
cd sensor-firmware-build
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install test dependencies
pip install -r tests/requirements.txt

# 4. Deploy firmware to CM4 (only needed once or after firmware changes)
./scripts/build-and-deploy.sh

# 5. Run smoke tests to verify setup
./scripts/run-tests-remote.sh $PI_IP -m quick
```

### Running Your First Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run a simple 60-second ECG test
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg.py
```

## Test Architecture

### How Tests Work

```
┌──────────────────────────────────────────────────────────────────┐
│                         YOUR LAPTOP                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ pytest (running locally)                               │    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────┐     │    │
│  │  │ Test: test_ads1293_ecg.py                    │     │    │
│  │  │                                               │     │    │
│  │  │ 1. TCPClient.connect("192.168.x.x:1293") ────┼─────┼────┼───┐
│  │  │ 2. send_json({"type": "settings", ...})      │     │    │   │
│  │  │ 3. recv_json() <- response                   │     │    │   │
│  │  │ 4. Assert validations                        │     │    │   │
│  │  │ 5. Save results locally                      │     │    │   │
│  │  └──────────────────────────────────────────────┘     │    │   │
│  │                                                         │    │   │
│  │  Results saved: /tmp/test-results/                    │    │   │
│  └────────────────────────────────────────────────────────┘    │   │
└──────────────────────────────────────────────────────────────────┘   │
                                                                       │
                                    TCP/IP Network                     │
                                    (ports 1293, 30009, etc.)          │
                                                                       │
┌──────────────────────────────────────────────────────────────────┐   │
│                    RASPBERRY PI CM4                              │   │
│                                                                  │   │
│  ┌────────────────────────────────────────────────────────┐    │   │
│  │ Firmware Services (systemd)                            │    │   │
│  │                                                         │    │   │
│  │  ┌──────────────────────────────────────────────┐     │    │   │
│  │  │ spi-service (port 1293, 30009, 2812)        │ ◄───┼────┼───┘
│  │  │                                               │     │    │
│  │  │ - ADS1293 ECG (port 1293)                   │     │    │
│  │  │ - MAX30009 BIOZ (port 30009)                │     │    │
│  │  │ - WS2812 LED (port 2812)                    │     │    │
│  │  └──────────────────────────────────────────────┘     │    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────┐     │    │
│  │  │ power-service (port 501)                     │     │    │
│  │  └──────────────────────────────────────────────┘     │    │
│  │                                                         │    │
│  │  No Python needed on CM4!                             │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Key Points:**
- ✅ Tests run **ON YOUR LAPTOP**, not on CM4
- ✅ Tests communicate with CM4 via **TCP/IP network**
- ✅ Results saved **locally on your laptop**
- ✅ **No Python environment needed on CM4**
- ✅ CM4 only runs compiled firmware binaries

## Test Categories

### 1. Hardware Integration Tests (`tests/hardware-integration/`)

Tests that require actual hardware sensors connected to CM4.

| Test File | Description | Markers | Duration | Hardware Required |
|-----------|-------------|---------|----------|-------------------|
| `test_ads1293_ecg.py` | 60-second ECG data collection | `hardware`, `ads1293`, `slow` | ~1 min | ADS1293 + ECG simulator |
| `test_ads1293_ecg_long.py` | 1-hour ECG with BPM validation | `hardware`, `ads1293`, `long` | 1-4 hours | ADS1293 + ECG simulator |
| `test_max30009_bioz.py` | Bioimpedance measurements | `hardware`, `max30009` | ~5 min | MAX30009 + load resistors |

### 2. Firmware-Application Integration Tests (`tests/fw-app-integration/`)

Tests for protocol validation, error handling, and parameter validation.

| Test File | Description | Markers | Duration | Hardware Required |
|-----------|-------------|---------|----------|-------------------|
| `test_ads1293_api.py` | JSON protocol validation (3 tests) | `api`, `ads1293`, `quick` | ~1 min | ADS1293 only |
| `test_ads1293_invalid_params.py` | Invalid parameter handling (5 tests) | `fw_app`, `ads1293`, `invalid_params`, `quick` | ~2 min | ADS1293 only |
| `test_max30009_api.py` | MAX30009 protocol tests | `api`, `max30009` | ~1 min | MAX30009 only |

### 3. System Integration Tests (`tests/system-integration/`)

End-to-end tests involving multiple services.

## Available Test Cases

### Test Case 01: ADS1293 ECG 60-Second Test

**File:** `tests/hardware-integration/test_ads1293_ecg.py`

**Purpose:** Validate ECG data collection, sampling frequency, and sync markers

**Test Steps:**
1. Connect to ADS1293 service
2. Configure for 400 Hz sampling (R2=4, R3=16)
3. Wait 2 seconds for stabilization
4. Flush accumulated buffer
5. Collect data for 60 seconds (poll every 1.0s)
6. Validate sync counters (monotonic, no missing frames)
7. Calculate and verify sampling frequency (400 Hz ± 1 Hz)
8. Power off sensor

**Pass Criteria:**
- Sync counters increase monotonically every 1s
- Mean sampling frequency: 400 Hz ± 1 Hz
- ~24,000 total samples collected

**Run:**
```bash
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg.py
```

---

### Test Case 11: ADS1293 ECG 1-Hour Long-Duration Test

**File:** `tests/hardware-integration/test_ads1293_ecg_long.py`

**Purpose:** Validate long-duration ECG recording with BPM detection

**Parametrized BPM:** 30, 60, 120, 180 (runs 4 tests, 1 hour each)

**Test Steps:**
1. Connect to ADS1293 service
2. Configure for 400 Hz sampling (R2=4, R3=16)
3. Flush accumulated buffer
4. Collect data for 1 hour (3600 polls at 1.0s interval)
5. Progress updates every 5 minutes
6. Validate sync counters (~3600 markers)
7. Calculate sampling frequency (400 Hz ± 1 Hz)
8. Detect R-peaks using scipy.signal.find_peaks
9. Calculate BPM from peak intervals
10. Validate BPM matches simulator (±3 bpm or ±1%)
11. Log all metrics to JSONL file
12. Power off sensor

**Pass Criteria:**
- 1 hour recording completes successfully
- Sync counters monotonically increase
- No missing sync frames
- Mean sampling frequency: 400 Hz ± 1 Hz
- BPM error: ±3 bpm or ±1%, whichever is greater
- ~1,440,000 total samples

**Run:**
```bash
# Run for single BPM (1 hour)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg_long.py -k "bpm-60"

# Run all BPM values (4 hours total)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg_long.py
```

**Output:**
- Data file: `/tmp/test-results/data/test_011_ecg_1hr_bpm{bpm}.jsonl`
- Contains: raw ECG samples, sync markers, timestamps, metadata

---

### Test Case 41: Invalid ADS1293 Rate Parameters

**File:** `tests/fw-app-integration/test_ads1293_invalid_params.py`

**Purpose:** Document firmware behavior when receiving invalid parameters

**Sub-Tests:**
1. **test_invalid_r1_rate**: Test invalid R1_rate values
   - Valid: 2, 4
   - Test: 0, 1, 3, 5, 8, 16, -1, 100

2. **test_invalid_r2_rate**: Test invalid R2_rate values
   - Valid: 4, 5, 6, 8
   - Test: 0, 1, 2, 3, 7, 9, 16, 32, -1, 100

3. **test_invalid_r3_rate**: Test invalid R3_rate values
   - Valid: 4, 6, 8, 12, 16, 32, 64, 128
   - Test: 0, 1, 2, 3, 5, 7, 9, 10, 11, 13-15, 17-31, 33-63, 65-127, 129+

4. **test_multiple_invalid_rates**: Test combinations
   - All invalid, all negative, all zero, all very large

5. **test_missing_rate_parameters**: Test default behavior
   - All omitted, R1 omitted, R2 omitted, R3 omitted

**Pass Criteria:**
- Record all firmware responses
- Document behavior for specification clarification
- No crashes or hangs

**Run:**
```bash
# Run all invalid parameter tests
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_invalid_params.py

# Run specific sub-test
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_invalid_params.py::test_invalid_r2_rate
```

## Running Tests

### By Test File

```bash
# Single test file
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg.py

# All files in directory
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/

# All tests
./scripts/run-tests-remote.sh $PI_IP tests/
```

### By Test Function

```bash
# Run specific test function
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_invalid_params.py::test_invalid_r3_rate

# Run parametrized test with specific parameter
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg_long.py -k "bpm-120"
```

### By Markers

```bash
# Quick tests only (< 5 min) - Runs 8 FW-APP tests
./scripts/run-tests-remote.sh $PI_IP -m quick
# Runs: test_ads1293_api.py (3 tests) + test_ads1293_invalid_params.py (5 tests)

# Long duration tests (> 1 hour) - Runs 4 hardware tests
./scripts/run-tests-remote.sh $PI_IP -m long
# Runs: test_ads1293_ecg_long.py (4 parametrized tests, 1 hour each)

# ADS1293 tests only - Runs ALL ADS1293 tests
./scripts/run-tests-remote.sh $PI_IP -m ads1293
# Runs: All 13 ADS1293 tests (FW-APP + hardware)

# MAX30009 tests only
./scripts/run-tests-remote.sh $PI_IP -m max30009

# Hardware-required tests - Runs 5 hardware integration tests
./scripts/run-tests-remote.sh $PI_IP -m hardware
# Runs: test_ads1293_ecg.py (1 test) + test_ads1293_ecg_long.py (4 tests)

# Invalid parameter tests - Runs 5 parameter validation tests
./scripts/run-tests-remote.sh $PI_IP -m invalid_params
# Runs: test_ads1293_invalid_params.py only

# Firmware-app integration tests - Runs 8 FW-APP tests
./scripts/run-tests-remote.sh $PI_IP -m fw_app
# Runs: test_ads1293_invalid_params.py (5 tests) + others

# API validation tests - Runs 3 API protocol tests
./scripts/run-tests-remote.sh $PI_IP -m api
# Runs: test_ads1293_api.py (3 tests)

# Combine markers (AND) - Only tests with BOTH markers
./scripts/run-tests-remote.sh $PI_IP -m "ads1293 and quick"
# Runs: 8 tests (only ADS1293 tests that are also quick)

# Combine markers (OR) - Tests with EITHER marker
./scripts/run-tests-remote.sh $PI_IP -m "ads1293 or max30009"
# Runs: All sensor tests
```

**Quick Reference:**

| Command | Tests Run | Total Tests | Duration |
|---------|-----------|-------------|----------|
| `-m quick` | FW-APP integration only | 8 tests | ~3 min |
| `-m fw_app` | FW-APP integration only | 8 tests | ~3 min |
| `-m api` | API protocol validation | 3 tests | ~1 min |
| `-m invalid_params` | Parameter validation | 5 tests | ~2 min |
| `-m hardware` | Hardware integration | 5 tests | 1-4 hours |
| `-m slow` | 60-second ECG test | 1 test | ~1 min |
| `-m long` | 1-hour ECG tests | 4 tests | 4 hours |
| `-m ads1293` | All ADS1293 tests | 13 tests | 1-4 hours |
| `tests/fw-app-integration/` | All FW-APP tests | 8 tests | ~3 min |
| `tests/hardware-integration/` | All hardware tests | 5 tests | 1-4 hours |

### Advanced Options

```bash
# Verbose output
./scripts/run-tests-remote.sh $PI_IP tests/ -v
./scripts/run-tests-remote.sh $PI_IP tests/ -vv  # Extra verbose

# Stop on first failure
./scripts/run-tests-remote.sh $PI_IP tests/ --maxfail=1

# Show local variables on failure
./scripts/run-tests-remote.sh $PI_IP tests/ -l

# Generate HTML report
./scripts/run-tests-remote.sh $PI_IP tests/ --html=report.html --self-contained-html

# Set timeout
./scripts/run-tests-remote.sh $PI_IP tests/ --timeout=300  # 5 min per test

# Restart services before testing
./scripts/run-tests-remote.sh $PI_IP --restart-services tests/
```

### Continuous Integration Mode

```bash
# Run all tests with detailed output and HTML report
./scripts/run-tests-remote.sh $PI_IP tests/ \
  -vv \
  --html=test-report.html \
  --self-contained-html \
  --maxfail=1
```

## Test Configuration

### Main Configuration File

Edit `tests/config/test_config.yaml`:

```yaml
# Service connections
services:
  ads1293:
    host: "127.0.0.1"  # Will be overridden by PI_IP env var
    port: 1293
  max30009:
    host: "127.0.0.1"
    port: 30009

# ADS1293 ECG parameters
ads1293_ecg:
  sampling_frequency: 400      # Target sampling frequency
  r2_rate: 4                   # For 400 Hz: use R2=4, R3=16
  r3_rate: 16
  bpm_values: [30, 60, 120, 180]  # BPM values to test
  duration_sec: 60             # Short test duration
  long_duration_sec: 3600      # Long test duration (1 hour)
  polling_interval_sec: 1.0    # How often to poll for data

# Pass/fail thresholds
thresholds:
  ads1293:
    voltage_error_low_uv: 25        # ±25 µV for ref ≤ 500 µV
    voltage_error_high_uv: 40       # ±40 µV for ref > 500 µV
    voltage_error_high_pct: 5       # ±5% for ref > 500 µV
    bpm_error_absolute: 3           # ±3 bpm
    bpm_error_pct: 1                # ±1%

  sampling:
    frequency_error_hz: 1           # ±1 Hz tolerance
    sync_counter_tolerance_ms: 50   # ±50 ms for sync timing
```

### Understanding R-Rate Configuration

**Sampling Rate Formula:**
```
fs = 128000 / (R1_rate × R2_rate × R3_rate)
```

**Common Configurations:**

| R1 | R2 | R3 | Sampling Rate | Bandwidth | µV/ADC |
|----|----|----|---------------|-----------|--------|
| 4  | 4  | 16 | 500 Hz        | 100 Hz    | 0.163  |
| 4  | 8  | 32 | 200 Hz        | 40 Hz     | 0.163  |
| 4  | 8  | 64 | 100 Hz        | 20 Hz     | 0.163  |
| 4  | 8  | 128| 50 Hz         | 10 Hz     | 0.163  |

**For 400 Hz target:**
- Closest achievable: 500 Hz with R2=4, R3=16
- Polling interval: 1.0 second (allows ~500 samples per poll)

### Pytest Fixtures

Available fixtures in `conftest.py`:

```python
@pytest.fixture
def test_config():
    """Load test configuration from YAML"""
    # Returns dict with all config values

@pytest.fixture
def results_dir():
    """Create and return results directory path"""
    # Returns Path object: /tmp/test-results/data/

@pytest.fixture
def ads1293_client(test_config):
    """Create TCP client connected to ADS1293"""
    # Yields TCPClient instance, auto-closes after test
```

## Writing New Tests

### Test Template

```python
"""
Test Case XX: <Test Name>

Category: <HW-FW Integration | FW-APP Integration | System>
Components: <Hardware components involved>
Test Name: <Descriptive name>

Prerequisites:
- List prerequisites here

Pass Criteria:
- List pass criteria here
"""

import pytest
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from sensor_helpers import configure_ads1293, get_sensor_data, power_off_sensor

@pytest.mark.hardware  # Mark with appropriate markers
@pytest.mark.ads1293
def test_my_new_test(test_config, results_dir):
    """
    Test Case XX: <Brief description>

    Test Steps:
    1. Step 1
    2. Step 2
    ...
    """
    # Get configuration
    ads_config = test_config['services']['ads1293']

    print(f"\n{'='*70}")
    print(f"Test Case XX: <Test Name>")
    print(f"{'='*70}\n")

    # Connect to service
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        # Test implementation
        response = client.send_json({"type": "get_data"})
        assert response["type"] == "data"

        # More test logic...

    print(f"\n✓ TEST PASSED\n")
```

### Common Helper Functions

Located in `tests/common/`:

**tcp_client.py:**
```python
client = TCPClient(host, port)
response = client.send_json({"type": "settings", ...})
client.close()

# Or use context manager (auto-closes)
with TCPClient(host, port) as client:
    response = client.send_json({...})
```

**sensor_helpers.py:**
```python
# Configure ADS1293
response = configure_ads1293(
    client,
    sampling_freq=400,
    r2_rate=4,
    r3_rate=16,
    enable_conversion=True
)

# Get sensor data
response = get_sensor_data(client)

# Power off sensor
response = power_off_sensor(client)
```

**validators.py:**
```python
# Extract sync markers
sync_markers = extract_sync_markers_ads1293(data)

# Validate monotonic increase
valid, msg = validate_sync_monotonic(sync_markers)

# Calculate sampling frequency
freq = calculate_sampling_frequency(data, duration_sec)

# Validate sampling frequency
valid, msg = validate_sampling_frequency(actual, expected, tolerance)
```

**data_logger.py:**
```python
# Create JSONL logger
logger = JSONLLogger(
    str(output_file),
    test_id="test_001",
    sensor="ads1293",
    metadata={"extra": "info"}
)

# Write data
logger.write_data(
    data=samples,
    metadata={"timestamp": "..."}
)

# Write metadata
logger.write_metadata({"metric": value})
```

## Troubleshooting

### Connection Issues

**Problem:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Solutions:**
```bash
# 1. Check if services are running on CM4
ssh pi@$PI_IP "systemctl status spi-service"

# 2. Check if port is accessible
nc -zv $PI_IP 1293

# 3. Restart services
./scripts/run-tests-remote.sh $PI_IP --restart-services

# 4. Verify PI_IP is set correctly
echo $PI_IP

# 5. Verify CM4 is on network
ping $PI_IP
```

### Import Errors

**Problem:** `ImportError: No module named 'pytest'`

**Solutions:**
```bash
# 1. Ensure venv is activated (should see "(venv)" in prompt)
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r tests/requirements.txt

# 3. Verify pytest is installed
pytest --version
```

### Sampling Frequency Issues

**Problem:** Calculated frequency is 333.77 Hz instead of 400 Hz

**Cause:** Incorrect R2/R3 configuration or polling interval

**Solution:**
1. Check `test_config.yaml`:
   - For 400 Hz target: `r2_rate: 4`, `r3_rate: 16`
   - Polling interval: `polling_interval_sec: 1.0`

2. Verify formula: `128000 / (4 × 4 × 16) = 500 Hz` (closest to 400 Hz)

3. Check test is flushing buffer:
   ```python
   time.sleep(2.0)  # Stabilization
   flush_response = get_sensor_data(client)  # Flush accumulated
   # Now start collection
   ```

### Extra Samples in First Response

**Problem:** First `get_data` returns ~800-900 samples instead of ~400

**Cause:** Buffer accumulation during 2-second stabilization period

**Solution:** Explicitly flush buffer before data collection:
```python
time.sleep(2.0)  # Allow sensor to stabilize
flush_response = get_sensor_data(client)  # Discard accumulated samples
print(f"Flushed {len(flush_response['data'])} samples")
# Now start clean collection
```

### BPM Detection Issues

**Problem:** `IndexError` or incorrect BPM calculation

**Causes & Solutions:**

1. **Insufficient data for peak detection:**
   ```python
   if len(peaks) < 2:
       pytest.skip("Insufficient peaks for BPM calculation")
   ```

2. **Peak detection parameters:**
   ```python
   # Increase distance for low BPM, decrease for high BPM
   distance = int(sampling_freq * 0.5)  # Min 0.5s between peaks
   peaks, _ = find_peaks(ecg_signal, distance=distance)
   ```

3. **Signal quality:**
   - Check ECG simulator connections
   - Verify signal amplitude (should be > 100 µV)
   - Check for electrical noise

### Test Timeout

**Problem:** Test runs longer than expected and times out

**Solutions:**
```bash
# Increase timeout for long tests
./scripts/run-tests-remote.sh $PI_IP tests/ --timeout=7200  # 2 hours

# Or disable timeout
./scripts/run-tests-remote.sh $PI_IP tests/ --timeout=0
```

### Results Not Saved

**Problem:** Cannot find test results in `/tmp/test-results/`

**Solutions:**
```bash
# 1. Check results_dir in conftest.py
cat tests/conftest.py | grep results_dir

# 2. Verify directory exists
ls -la /tmp/test-results/

# 3. Check permissions
mkdir -p /tmp/test-results/data
chmod 777 /tmp/test-results/

# 4. Check logger is being used in test
# Should see: logger.write_data(...) calls
```

## Dependencies

From `requirements.txt`:

```
# Testing framework
pytest>=7.4.0              # Test runner
pytest-html>=4.1.0         # HTML reporting
pytest-timeout>=2.2.0      # Test timeouts

# Data processing
numpy>=1.24.0              # Numerical arrays
scipy>=1.11.0              # Signal processing (find_peaks)

# Visualization
matplotlib>=3.7.0          # Plotting (optional)

# Configuration
pyyaml>=6.0                # YAML config parsing
```

## Further Reading

- [Parent README](../README.md) - Main project documentation
- [JSON Protocol Reference](../JSON_PROTOCOL_REFERENCE.md) - Complete API docs
- [CLAUDE.md](../CLAUDE.md) - Development guide
