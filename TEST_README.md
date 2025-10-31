# Test Suite Documentation

## Overview

This directory contains multiple test scripts for the MajaHealth firmware:

1. **`test_max30009.py`** - MAX30009 (ICG/Bioimpedance) sensor functional tests
2. **`test_icg_ecg_sync.py`** - ICG-ECG synchronization validation tests (NEW)

---

# MAX30009 Test Script - User Guide

## Overview

`test_max30009.py` is a comprehensive automated testing suite for the MAX30009 (ICG/Bioimpedance) sensor service running on Raspberry Pi.

## Features

✅ **Comprehensive Coverage**: 30+ test cases across 5 test suites
✅ **Detailed Logging**: Everything logged to timestamped log files
✅ **CSV Reports**: Machine-readable test results with pass/fail status
✅ **Updated Parameters**: Uses latest firmware parameters (stimulate_table_index with 7 values)
✅ **Raspberry Pi Optimized**: Designed for ARM Linux environment

## Prerequisites

### 1. Python 3 (Already on Raspberry Pi)
```bash
python3 --version  # Should be 3.7+
```

### 2. Running Services
Ensure `SPI_DEV_servise` is running:
```bash
# Check if service is running
netstat -tuln | grep 30009

# Or try connecting
nc localhost 30009
```

### 3. File Permissions
```bash
chmod +x test_max30009.py
```

## Quick Start

### Run All Tests
```bash
python3 test_max30009.py
```

### Run with Python Path (if needed)
```bash
/usr/bin/python3 test_max30009.py
```

## Output Files

After running, you'll get two timestamped files:

1. **CSV Report**: `max30009_test_report_YYYYMMDD_HHMMSS.csv`
   - Columns: timestamp, test_suite, test_name, test_id, status, duration_ms, expected, actual, error_message, details
   - Easy to import into Excel/LibreOffice

2. **Log File**: `max30009_test_log_YYYYMMDD_HHMMSS.log`
   - Detailed execution log with DEBUG level information
   - Shows every command sent and response received

## Test Suites

### Suite 1: Connection Tests (4 tests)
- `CONN-001`: Basic connection establishment
- `CONN-002`: Malformed JSON handling (skipped)
- `CONN-003`: Missing type field error handling
- `CONN-004`: Unknown command type error handling

### Suite 2: Settings Configuration (10 tests)
- `SETT-001`: Power on with minimal settings
- `SETT-002`: Enable measurement with basic config
- `SETT-003`: All 17 stimulation frequencies (25 Hz - 450 kHz)
- `SETT-004`: All 7 stimulation table indices (64µA x10 to 1.28mA x5)
- `SETT-005`: Measure frequency range (1-500 Hz)
- `SETT-006`: Invalid frequency clamping (low)
- `SETT-007`: Invalid frequency clamping (high)
- `SETT-008`: All 5 external MUX states
- `SETT-009`: Partial settings update
- `SETT-010`: Complete configuration test

### Suite 3: Data Retrieval (6 tests)
- `DATA-001`: Get data when measurement disabled
- `DATA-002`: Get data when measurement enabled
- `DATA-003`: Verify data point format (5-element arrays)
- `DATA-004`: Sync marker detection (magic number -99999)
- `DATA-005`: Continuous polling (10 iterations × 1 second)
- `DATA-006`: Buffer overflow test (5 second wait)

### Suite 4: Calibration (5 tests)
- `CALIB-001`: Start calibration command
- `CALIB-002`: Commands blocked during calibration
- `CALIB-003`: Stop calibration command
- `CALIB-004`: Resume normal operation after calibration
- `CALIB-005`: Calibration coverage (7×17=119 combinations)

### Suite 5: Power State (2 tests)
- `PWR-001`: Power off to on transition
- `PWR-002`: Measurement enable/disable cycles (5×)

**Total: 27 active tests** (1 skipped)

## Understanding Results

### Console Output
```
======================================================================
TEST SUMMARY
======================================================================
Total Tests:  27
Passed:       25 (92.6%)
Failed:       2
Errors:       0
Skipped:      0
Duration:     45.23 seconds
Report:       max30009_test_report_20250123_143022.csv
======================================================================
```

### Exit Codes
- `0`: All tests passed
- `1`: One or more tests failed or errored

### Test Status Values
- `PASS`: Test passed successfully
- `FAIL`: Test failed (assertion failed)
- `ERROR`: Test threw an exception
- `SKIP`: Test was skipped (e.g., malformed JSON test)

## Example CSV Output

```csv
timestamp,test_suite,test_name,test_id,status,duration_ms,expected,actual,error_message,details
2025-01-23T14:30:22.123456,ConnectionTests,Connection Establishment,CONN-001,PASS,123.4,Connection successful,Connection successful,,Response type: actual_settings
2025-01-23T14:30:22.456789,SettingsConfigTests,Power On (Minimal),SETT-001,PASS,234.5,power_enable=true,power_enable=True,,{"type":"actual_settings",...}
```

## Viewing Results

### On Raspberry Pi Terminal
```bash
# View summary
tail -20 max30009_test_log_*.log

# View all logs
less max30009_test_log_*.log

# View CSV (if csvkit installed)
csvlook max30009_test_report_*.csv
```

### Transfer to Desktop
```bash
# On your desktop (not Pi)
scp pi@192.168.1.XXX:/path/to/max30009_test_* .
```

Then open in Excel, Google Sheets, or any spreadsheet application.

## Configuration

Edit these constants at the top of `test_max30009.py` if needed:

```python
HOST = "localhost"      # Change if testing remote device
PORT = 30009            # MAX30009 service port
TIMEOUT = 10            # Socket timeout in seconds
```

## Troubleshooting

### Problem: "Connection refused"
```
ERROR: Connection refused to localhost:30009
```

**Solution**: Start the SPI_DEV_servise
```bash
cd SPI_DEV_servise/bin/Debug
./SPI_DEV_servise
```

### Problem: "Socket timeout"
```
ERROR: Socket timeout after 10s
```

**Solution**: Increase timeout or check if service is responding
```bash
# Test manually
echo '{"type":"settings","power_enable":true}' | nc localhost 30009
```

### Problem: "Permission denied"
```
bash: ./test_max30009.py: Permission denied
```

**Solution**: Make executable
```bash
chmod +x test_max30009.py
```

### Problem: Tests hang during data retrieval
**Solution**: Tests include intentional waits for data accumulation (2-5 seconds). This is normal.

## Advanced Usage

### Run Specific Test Suites

Modify `main()` function to comment out suites:

```python
test_suites = [
    ConnectionTests(client, reporter),
    SettingsConfigTests(client, reporter),
    # DataRetrievalTests(client, reporter),  # Skip this
    # CalibrationTests(client, reporter),     # Skip this
    # PowerStateTests(client, reporter)       # Skip this
]
```

### Change Log Level

In `setup_logging()`:
```python
logging.basicConfig(
    level=logging.INFO,  # Change from DEBUG to reduce verbosity
    ...
)
```

### Custom Test Timeout

For slow networks or systems:
```python
TIMEOUT = 30  # Increase from 10 to 30 seconds
```

## Integration with CI/CD

### Example: Run tests and check exit code
```bash
#!/bin/bash
python3 test_max30009.py
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Tests failed!"
    exit 1
fi
```

### Example: Send results via email
```bash
python3 test_max30009.py
mail -s "MAX30009 Test Results" admin@example.com < max30009_test_log_*.log
```

## Parameter Reference

### Stimulation Frequencies (17 values)
| Index | Frequency | Description |
|-------|-----------|-------------|
| 0     | 25 Hz     | Very low    |
| 1     | 100 Hz    | Low         |
| 2     | 200 Hz    |             |
| 3     | 500 Hz    |             |
| 4     | 1 kHz     |             |
| 5     | 5 kHz     |             |
| 6     | 10 kHz    |             |
| 7     | 20 kHz    |             |
| 8     | 50 kHz    | Common ICG  |
| 9     | 100 kHz   |             |
| 10    | 150 kHz   |             |
| 11    | 200 kHz   |             |
| 12    | 250 kHz   |             |
| 13    | 300 kHz   |             |
| 14    | 350 kHz   |             |
| 15    | 400 kHz   |             |
| 16    | 450 kHz   | Very high   |

### Stimulation Table Indices (7 values)
| Index | Current  | Gain | Description        |
|-------|----------|------|--------------------|
| 0     | 64 µA    | x10  | Very low current   |
| 1     | 128 µA   | x10  | Low current        |
| 2     | 256 µA   | x5   | Medium-low         |
| 3     | 640 µA   | x2   | Medium (low gain)  |
| 4     | 640 µA   | x5   | Medium (high gain) |
| 5     | 1.28 mA  | x2   | High (low gain)    |
| 6     | 1.28 mA  | x5   | High (high gain)   |

### External MUX States (5 values)
| Value | State      | Description              |
|-------|------------|--------------------------|
| 0     | ALL_OFF    | All MUX switches off     |
| 1     | 4_WIRE     | 4-wire measurement mode  |
| 2     | 2_WIRE     | 2-wire measurement mode  |
| 3     | CALIBRATE  | Calibration mode         |
| 4     | COLE_COLE  | Cole-Cole model mode     |

## Typical Test Duration

- **Connection Tests**: ~2 seconds
- **Settings Tests**: ~5 seconds
- **Data Retrieval Tests**: ~25 seconds (includes waits)
- **Calibration Tests**: ~5 seconds
- **Power State Tests**: ~8 seconds

**Total**: ~45 seconds for all tests

## Sample Test Run Output

```
2025-01-23 14:30:22,123 [    INFO] ======================================================================
2025-01-23 14:30:22,124 [    INFO] MAX30009 Test Suite Started
2025-01-23 14:30:22,125 [    INFO] ======================================================================
2025-01-23 14:30:22,126 [    INFO] Test Report: max30009_test_report_20250123_143022.csv
2025-01-23 14:30:22,127 [    INFO] Log File: max30009_test_log_20250123_143022.log
2025-01-23 14:30:22,128 [    INFO]
2025-01-23 14:30:22,129 [    INFO] Checking MAX30009 service availability...
2025-01-23 14:30:22,234 [    INFO] MAX30009 service is available
2025-01-23 14:30:22,235 [    INFO]
2025-01-23 14:30:22,236 [    INFO] ======================================================================
2025-01-23 14:30:22,237 [    INFO] Starting ConnectionTests
2025-01-23 14:30:22,238 [    INFO] ======================================================================
2025-01-23 14:30:22,239 [    INFO] Running: CONN-001 - Connection Establishment
2025-01-23 14:30:22,345 [    INFO]   Result: PASS (106.2ms)
...
```

## Support

For issues or questions:
1. Check the log file for detailed error messages
2. Verify SPI_DEV_servise is running: `netstat -tuln | grep 30009`
3. Test manual connection: `nc localhost 30009`
4. Review firmware documentation in CLAUDE.md and API_TEST_PLAN.md

---

# ICG-ECG Synchronization Test - Overview

## Quick Info

**Script:** `test_icg_ecg_sync.py`

**Purpose:** Validates time-locked synchronization between ICG (MAX30009) and ECG (ADS1293) data streams by analyzing sync marks injected every 1 second by the firmware.

**Test Matrix:**
- 10 ICG measure frequencies (100-1000 Hz)
- 4 ECG R2/R3 combinations
- **Total: 40 tests** (~24 minutes)

## Quick Start

```bash
# Terminal 1 - Start service
./SPI_DEV_servise/bin/Debug/SPI_DEV_servise

# Terminal 2 - Run sync test
python3 test_icg_ecg_sync.py
```

## Test Configuration

### ICG Parameters
- **Measure Frequencies:** 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000 Hz
- **Stimulate Table Index:** 5 (fixed)
- **Stimulate Frequency:** 7 (fixed)

### ECG Parameters
- **R2/R3 Combinations:**
  - R2=4, R3=16
  - R2=4, R3=32
  - R2=6, R3=8
  - R2=4, R3=64

### Test Validation
- **Duration:** 30 seconds per test
- **Expected sync marks:** ~30 per test (1 per second)
- **Pass criteria:** Time difference < 200ms between ICG and ECG sync marks

## Output

- **Console:** Real-time progress and results
- **JSON file:** `icg_ecg_sync_test_results_YYYYMMDD_HHMMSS.json`

## Documentation

For complete documentation, see:
- [ICG_ECG_SYNC_TEST.md](ICG_ECG_SYNC_TEST.md) - Full test documentation
- [SYNC_TEST_QUICKSTART.md](SYNC_TEST_QUICKSTART.md) - Quick reference guide

## Understanding Sync Marks

Sync marks are special markers (`-99999`) injected **simultaneously** into both ICG and ECG data streams every 1 second. They allow verification that both data streams are time-locked and synchronized.

See firmware implementation in [main.cpp:109-115](SPI_DEV_servise/main.cpp#L109-L115).

---

## License

Part of MajaHealth Firmware Test Suite
