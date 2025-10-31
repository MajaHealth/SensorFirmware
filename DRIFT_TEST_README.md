# ICG-ECG 1-Hour Drift Analysis Test

## Overview

This test analyzes long-term synchronization drift between ICG (MAX30009) and ECG (ADS1293) sensors over a 1-hour period with a single fixed configuration.

**Script:** `test_icg_ecg_drift_1hour.py`

## Purpose

- **Drift tracking:** Monitor how time synchronization between ICG and ECG changes over 1 hour
- **Sample rate validation:** Verify that both sensors consistently deliver 400 samples between sync markers
- **Trend detection:** Identify if drift is increasing, decreasing, or stable over time
- **Quality assurance:** Long-duration validation for production systems

## Test Configuration

### ICG (MAX30009) Settings
```json
{
  "type": "settings",
  "power_enable": true,
  "measure_enable": true,
  "measure_frequency": 400,
  "stimulate_table_index": 4,
  "stimulate_frequency": 7,
  "ext_MUX_state": 1,
  "out_HP_filter": 0,
  "out_LP_filter": 0
}
```

### ECG (ADS1293) Settings
```json
{
  "type": "settings",
  "power_enable": true,
  "enable_conversion": true,
  "R2_rate": 4,
  "R3_rate": 16
}
```

### Test Parameters
- **Duration:** 3600 seconds (1 hour)
- **Sampling rate:** 400 Hz (both sensors)
- **Data request interval:** 0.2 seconds
- **Expected samples per interval:** 400 (at 400 Hz for 1 second between sync marks)
- **Expected sync marks:** ~3600 (one per second)

## Prerequisites

### Required Services
- `SPI_DEV_servise` must be running
- ICG service on port 30009
- ECG service on port 1293

### Python Dependencies

**On Embedded Device (test_icg_ecg_drift_1hour.py):**
```bash
# Standard library only - no external dependencies needed!
socket, json, time, sys, csv, datetime, typing, os
```

**On Local Machine (plot_drift_results.py):**
```bash
# For plot generation - install on your local computer only
pip3 install matplotlib numpy pandas
```

**Note:** The test script has NO external dependencies and can run on any embedded system with Python 3.6+. Plots are generated separately on your local machine.

### System Requirements
- Python 3.6 or higher
- ~100 MB free disk space for output files
- Stable network connection to device
- 1+ hour of uninterrupted execution time

## Two-Step Workflow

This test uses a **two-step workflow** optimized for embedded systems:

### Step 1: Run Test on Embedded Device (No Dependencies!)

```bash
# On the embedded device/Raspberry Pi
python3 test_icg_ecg_drift_1hour.py
```

**Output:**
- CSV file with all data points
- JSON file with complete results
- Console summary with statistics
- **NO plotting libraries needed!**

### Step 2: Generate Plots on Local Machine

```bash
# Copy files to your local computer
scp pi@192.168.1.100:~/icg_ecg_drift_1hour_*.csv .
scp pi@192.168.1.100:~/icg_ecg_drift_1hour_results_*.json .
scp pi@192.168.1.100:~/plot_drift_results.py .

# Install plotting libraries (one-time setup)
pip3 install matplotlib numpy pandas

# Generate plots
python3 plot_drift_results.py icg_ecg_drift_1hour_20251028_103000.csv
# OR
python3 plot_drift_results.py icg_ecg_drift_1hour_results_20251028_103000.json
```

**Output:**
- 3 PNG plot files
- Console statistics summary

**Why this approach?**
- ✅ No dependencies on embedded device
- ✅ Lighter resource usage during test
- ✅ Faster test execution
- ✅ More flexible plotting on powerful local machine
- ✅ Can regenerate plots multiple times with different settings

## Usage

### Basic Usage (Local Device)
```bash
python3 test_icg_ecg_drift_1hour.py
```

### Remote Device
```bash
python3 test_icg_ecg_drift_1hour.py 192.168.1.100
```

### Custom Sync Threshold
```bash
python3 test_icg_ecg_drift_1hour.py localhost 10
```

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `host` | String | `localhost` | IP address or hostname of target device |
| `threshold_ms` | Float | `50.0` | Sync threshold in milliseconds |

## Output Files

### From Test Script (test_icg_ecg_drift_1hour.py)

The test script generates 2 files on the embedded device:

### 1. CSV File: `icg_ecg_drift_1hour_YYYYMMDD_HHMMSS.csv`

Detailed per-sync-mark data for analysis.

**Columns:**
- `sync_num` - Sync marker number
- `icg_timestamp` - ICG sync mark timestamp (Unix time, seconds)
- `ecg_timestamp` - ECG sync mark timestamp (Unix time, seconds)
- `time_diff_ms` - Absolute time difference in milliseconds
- `elapsed_time_s` - Elapsed time since test start (seconds)
- `elapsed_time_min` - Elapsed time since test start (minutes)
- `icg_samples_between` - Number of ICG samples between this sync and next
- `ecg_samples_between` - Number of ECG samples between this sync and next
- `icg_sample_deviation` - ICG sample count deviation from expected 400
- `ecg_sample_deviation` - ECG sample count deviation from expected 400

**Example:**
```csv
sync_num,icg_timestamp,ecg_timestamp,time_diff_ms,elapsed_time_s,elapsed_time_min,icg_samples_between,ecg_samples_between,icg_sample_deviation,ecg_sample_deviation
5041,1730013851.234567,1730013851.236789,2.222,1.2,0.02,400,400,0,0
5042,1730013852.235123,1730013852.237234,2.111,2.2,0.04,400,400,0,0
```

### 2. JSON File: `icg_ecg_drift_1hour_results_YYYYMMDD_HHMMSS.json`

Complete test results with configuration, statistics, and all drift data.

**Structure:**
```json
{
  "test_name": "ICG-ECG 1-Hour Drift Analysis",
  "timestamp": "2025-10-28T10:30:00",
  "duration_seconds": 3600,
  "configuration": {
    "icg": {...},
    "ecg": {...},
    "icg_sampling_rate": 400,
    "ecg_sampling_rate": 400,
    "sync_threshold_ms": 50.0
  },
  "results": {
    "success": true,
    "total_sync_marks": 3598,
    "statistics": {
      "mean_drift_ms": 3.456,
      "std_drift_ms": 1.234,
      "min_drift_ms": 0.123,
      "max_drift_ms": 8.765,
      "drift_rate_ms_per_hour": 0.234,
      "icg_avg_samples_between": 400.12,
      "icg_std_samples_between": 2.34,
      "ecg_avg_samples_between": 399.98,
      "ecg_std_samples_between": 1.87,
      "expected_samples": 400
    },
    "drift_data": [...]
  }
}
```

### From Plotting Script (plot_drift_results.py)

The plotting script generates 3 plot files on your local machine:

### 3. Plot 1: `drift_over_time_YYYYMMDD_HHMMSS.png`

**Visualization:** Time difference between ICG and ECG sync marks over the 1-hour test period.

**Features:**
- Blue line: Raw drift measurements
- Red dashed line: Linear trend line with drift rate
- Orange dashed line: Configured threshold
- X-axis: Elapsed time in minutes
- Y-axis: Time difference in milliseconds

**What to look for:**
- ✅ Stable horizontal trend = good synchronization
- ⚠️ Increasing/decreasing trend = drift over time
- ❌ Values above threshold = synchronization issues

### 4. Plot 2: `sample_count_validation_YYYYMMDD_HHMMSS.png`

**Visualization:** Number of samples between consecutive sync marks over time.

**Features:**
- Blue line: ICG sample counts
- Green line: ECG sample counts
- Red dashed line: Expected value (400 samples)
- Orange dotted lines: ±5% tolerance band (380-420 samples)
- X-axis: Elapsed time in minutes
- Y-axis: Sample count

**What to look for:**
- ✅ Both lines at 400 = correct sampling rate
- ⚠️ Slight deviation = minor timing issues
- ❌ Large deviation = sample drops or rate errors

### 5. Plot 3: `drift_histogram_YYYYMMDD_HHMMSS.png`

**Visualization:** Distribution of time differences across all sync marks.

**Features:**
- Blue histogram: Frequency distribution of drift values
- Green vertical line: Mean drift
- Red dashed line: Configured threshold
- X-axis: Time difference in milliseconds
- Y-axis: Frequency (count)

**What to look for:**
- ✅ Narrow bell curve = consistent synchronization
- ✅ Peak well below threshold = good margin
- ⚠️ Wide distribution = inconsistent timing
- ❌ Bimodal distribution = intermittent issues

## Expected Results (Healthy System)

### Sync Marks
- **ICG sync marks:** 3595-3605 (expected ~3600)
- **ECG sync marks:** 3595-3605 (expected ~3600)
- **Common sync marks:** 3595-3605 (should match individual counts)

### Drift Statistics
- **Mean drift:** 1-5 ms
- **Std deviation:** 0.5-3 ms
- **Min drift:** 0-2 ms
- **Max drift:** 2-10 ms
- **Drift rate:** -1 to +1 ms/hour (close to zero)

### Sample Counts
- **ICG average samples:** 398-402 (within ±0.5% of 400)
- **ECG average samples:** 398-402 (within ±0.5% of 400)
- **Std deviation:** < 5 samples

## Progress Monitoring

### Console Output

The test provides real-time progress updates every 60 seconds:

```
Progress: 10.5/60.0 min (ICG: 3142 sets, ECG: 3140 sets, Remaining: 49.5 min)
```

### Real-Time CSV Monitoring

You can monitor the CSV file as it's being written:

```bash
# Terminal 1 - Run test
python3 test_icg_ecg_drift_1hour.py

# Terminal 2 - Monitor CSV
tail -f icg_ecg_drift_1hour_*.csv

# Or with periodic refresh
watch -n 30 'tail -50 icg_ecg_drift_1hour_*.csv'
```

## Interpreting Results

### Success Criteria

✅ **Test PASSES when:**
- All drift values < configured threshold
- Mean drift < 10 ms
- Drift rate close to 0 ms/hour (no significant trend)
- Average sample counts within ±2% of 400 (392-408)
- Sample count std deviation < 5

⚠️ **Warning signs:**
- Drift rate > 1 ms/hour (increasing or decreasing trend)
- Sample count deviations > 5%
- Large drift std deviation (> 5 ms)
- Intermittent spikes in drift

❌ **Test FAILS when:**
- Any drift value exceeds threshold
- Mean drift > 20 ms
- Sample counts consistently != 400
- Missing sync marks (common count << 3600)

### Example: Good Result

```
1-HOUR DRIFT ANALYSIS SUMMARY
================================================================================

Sync Marks:
  ICG sync marks found: 3598
  ECG sync marks found: 3599
  Common sync marks: 3598

Drift Statistics:
  Mean drift: 3.456 ms
  Std deviation: 1.234 ms
  Min drift: 0.123 ms
  Max drift: 8.765 ms
  Drift rate: 0.234 ms/hour

Sample Count Validation:
  Expected samples between markers: 400
  ICG average samples: 400.1 (±1.2)
  ECG average samples: 399.9 (±1.1)

✓ PASS: All drift values within threshold (50.0 ms)
✓ PASS: Sample counts within 5% tolerance
```

### Example: Problem Detected

```
1-HOUR DRIFT ANALYSIS SUMMARY
================================================================================

Sync Marks:
  ICG sync marks found: 3598
  ECG sync marks found: 3599
  Common sync marks: 3598

Drift Statistics:
  Mean drift: 25.678 ms
  Std deviation: 15.234 ms
  Min drift: 2.123 ms
  Max drift: 65.432 ms
  Drift rate: 5.234 ms/hour

Sample Count Validation:
  Expected samples between markers: 400
  ICG average samples: 387.5 (±12.3)
  ECG average samples: 399.8 (±2.1)

⚠ WARNING: Max drift (65.432 ms) exceeds threshold (50.0 ms)
⚠ WARNING: Sample count deviates more than 5% from expected
  ICG deviation: 3.1%
  ECG deviation: 0.1%
```

**Interpretation:** ICG is dropping samples, causing timing drift. Check:
- ICG firmware buffer size
- System load during test
- Hardware/SPI communication issues

## Data Analysis with Python

### Load and Analyze CSV

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv('icg_ecg_drift_1hour_20251028_103000.csv')

# Basic statistics
print(df['time_diff_ms'].describe())
print(f"Mean drift: {df['time_diff_ms'].mean():.3f} ms")
print(f"Max drift: {df['time_diff_ms'].max():.3f} ms")

# Plot drift over time
plt.figure(figsize=(12, 6))
plt.plot(df['elapsed_time_min'], df['time_diff_ms'])
plt.xlabel('Elapsed Time (minutes)')
plt.ylabel('Drift (ms)')
plt.title('ICG-ECG Drift Analysis')
plt.grid(True)
plt.show()

# Find outliers (drift > 3 standard deviations)
mean = df['time_diff_ms'].mean()
std = df['time_diff_ms'].std()
outliers = df[df['time_diff_ms'] > mean + 3*std]
print(f"Outliers found: {len(outliers)}")
print(outliers)

# Check sample count accuracy
icg_sample_error = abs(df['icg_samples_between'] - 400) / 400 * 100
ecg_sample_error = abs(df['ecg_samples_between'] - 400) / 400 * 100
print(f"ICG avg error: {icg_sample_error.mean():.2f}%")
print(f"ECG avg error: {ecg_sample_error.mean():.2f}%")
```

### Load JSON Results

```python
import json

with open('icg_ecg_drift_1hour_results_20251028_103000.json', 'r') as f:
    results = json.load(f)

# Extract statistics
stats = results['results']['statistics']
print(f"Mean drift: {stats['mean_drift_ms']:.3f} ms")
print(f"Drift rate: {stats['drift_rate_ms_per_hour']:.3f} ms/hour")
print(f"ICG avg samples: {stats['icg_avg_samples_between']:.1f}")
print(f"ECG avg samples: {stats['ecg_avg_samples_between']:.1f}")

# Access drift data
drift_data = results['results']['drift_data']
print(f"Total data points: {len(drift_data)}")
```

## Troubleshooting

### Issue: Test Stops Early

**Possible causes:**
- Network connection lost
- Service crashed
- Device powered off
- Ctrl+C pressed

**Solution:**
- Check service is still running: `ps aux | grep SPI_DEV_servise`
- Check network connectivity: `ping <device_ip>`
- Review partial results saved before interruption
- Restart test with fresh services

### Issue: No Sync Marks Found

**Possible causes:**
- Devices not streaming data
- Firmware not injecting sync marks
- Configuration error

**Solution:**
```bash
# Test device connectivity
echo '{"type":"get_data"}' | nc localhost 30009
echo '{"type":"get_data"}' | nc localhost 1293

# Check for data in response
# Should see "data": [...] with sync marks [-99999, ...]
```

### Issue: High Drift Values

**Possible causes:**
- System under heavy load
- Network latency (if remote)
- Firmware timing issues
- Hardware problems

**Solution:**
- Reduce system load
- Test locally (not over network)
- Check for firmware timestamp support
- Monitor CPU usage during test
- Check for thermal throttling

### Issue: Sample Count Errors

**Possible causes:**
- Buffer overflow (samples dropped)
- Incorrect sampling rate configuration
- SPI communication errors

**Solution:**
- Verify configuration was applied correctly
- Check firmware logs for errors
- Reduce data request rate (increase sleep time)
- Monitor system resources

### Issue: Plotting Script Not Working

**Error:**
```
Error: Required plotting libraries not installed.
```

**Solution:**
```bash
# On your LOCAL machine (not embedded device), install:
pip3 install matplotlib numpy pandas

# Or on Debian/Ubuntu
sudo apt-get install python3-matplotlib python3-numpy python3-pandas
```

**Note:** The plotting script is meant to run on your local computer, not the embedded device.

## Stopping the Test

### Graceful Stop (Ctrl+C)

Press `Ctrl+C` to interrupt the test. The script will:
- Save partial results to CSV
- Save partial results to JSON
- Print partial summary
- Close connections cleanly

**Note:** Plots are only generated after full 1-hour completion.

### Forced Stop (Ctrl+\)

Press `Ctrl+\` for immediate termination. Results may not be saved.

## Running Multiple Tests

### Sequential Tests

```bash
# Test 1: Default threshold
python3 test_icg_ecg_drift_1hour.py

# Wait 5 minutes for devices to stabilize
sleep 300

# Test 2: Strict threshold
python3 test_icg_ecg_drift_1hour.py localhost 10
```

### Archiving Results

```bash
# Create dated directory
mkdir -p test_results/$(date +%Y%m%d)

# Move results
mv icg_ecg_drift_1hour_* test_results/$(date +%Y%m%d)/

# Compress
tar -czf test_results_$(date +%Y%m%d).tar.gz test_results/$(date +%Y%m%d)/
```

## Comparison with Short Test

The standard `test_icg_ecg_sync.py` runs 30-second tests across 40 configurations. This 1-hour drift test provides complementary information:

| Aspect | Short Test (30s × 40) | Long Test (1 hour) |
|--------|----------------------|-------------------|
| **Duration** | ~24 minutes total | 1 hour single config |
| **Purpose** | Configuration sweep | Drift analysis |
| **Configurations** | 40 combinations | 1 fixed config |
| **Sync marks** | ~30 per test | ~3600 total |
| **Detects** | Config compatibility | Long-term drift |
| **Best for** | Initial validation | Stability testing |

**Recommendation:** Run short test first to validate configurations, then run long test on selected configuration for production validation.

## Related Documentation

- [CLAUDE.md](CLAUDE.md) - Project overview and build instructions
- [ICG_ECG_SYNC_COMPLETE_GUIDE.md](ICG_ECG_SYNC_COMPLETE_GUIDE.md) - Complete sync testing guide
- [TEST_README.md](TEST_README.md) - General test suite documentation

## Quick Reference: Plotting Script

### Installation (Local Machine Only)
```bash
pip3 install matplotlib numpy pandas
```

### Usage
```bash
# Using CSV file
python3 plot_drift_results.py icg_ecg_drift_1hour_20251028_103000.csv

# Using JSON file (includes more metadata)
python3 plot_drift_results.py icg_ecg_drift_1hour_results_20251028_103000.json
```

### Output
- `drift_over_time_YYYYMMDD_HHMMSS.png` - Drift trend over time
- `sample_count_validation_YYYYMMDD_HHMMSS.png` - Sample rate validation
- `drift_histogram_YYYYMMDD_HHMMSS.png` - Drift distribution
- Console statistics summary

### Features
- ✅ Works with both CSV and JSON input
- ✅ Automatic statistics calculation
- ✅ Trend line with drift rate
- ✅ Threshold and tolerance visualization
- ✅ Can regenerate plots multiple times

## Summary

This 1-hour drift test provides comprehensive long-term validation of ICG-ECG synchronization with:
- ✅ **Zero dependencies on embedded device** - runs anywhere with Python 3.6+
- ✅ Detailed drift tracking over time
- ✅ Sample rate validation
- ✅ Trend detection
- ✅ Statistical analysis
- ✅ Visual plots for easy interpretation (generated separately)
- ✅ Real-time progress monitoring
- ✅ Complete data export for further analysis
- ✅ Flexible two-step workflow

Use this test for production validation, quality assurance, and debugging timing-related issues.
