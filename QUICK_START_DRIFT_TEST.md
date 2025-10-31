# Quick Start: 1-Hour Drift Test

## Overview
Test ICG-ECG synchronization for 1 hour and analyze drift with NO external dependencies on the embedded device!

## Step 1: Run Test on Device (No Dependencies!)

```bash
# Make sure SPI_DEV_servise is running
./SPI_DEV_servise/bin/Debug/SPI_DEV_servise

# In another terminal, run the test
python3 test_icg_ecg_drift_1hour.py
```

**Wait:** ~1 hour for test completion

**Output files generated:**
- `icg_ecg_drift_1hour_YYYYMMDD_HHMMSS.csv`
- `icg_ecg_drift_1hour_results_YYYYMMDD_HHMMSS.json`

## Step 2: Generate Plots on Local Machine

### Copy Files
```bash
# Copy results to your local computer
scp user@device_ip:~/icg_ecg_drift_1hour_*.csv .
scp user@device_ip:~/icg_ecg_drift_1hour_results_*.json .
scp user@device_ip:~/plot_drift_results.py .
```

### Install Dependencies (One-time)
```bash
# On your local machine only
pip3 install matplotlib numpy pandas
```

### Generate Plots
```bash
# Use CSV file
python3 plot_drift_results.py icg_ecg_drift_1hour_20251028_103000.csv

# OR use JSON file (includes more metadata)
python3 plot_drift_results.py icg_ecg_drift_1hour_results_20251028_103000.json
```

**Output:**
- `drift_over_time_*.png` - Drift trend with linear regression
- `sample_count_validation_*.png` - Sample rate accuracy
- `drift_histogram_*.png` - Drift distribution
- Console statistics summary

## What Gets Tested

### Configuration
- **ICG:** 400 Hz, stimulate_table_index=4, stimulate_frequency=7
- **ECG:** R2=4, R3=16 (400 Hz)
- **Duration:** 3600 seconds (1 hour)
- **Data interval:** 0.2 seconds

### Measurements
Every second (3600 times):
1. Time difference between ICG/ECG sync marks
2. Sample count between sync markers (should be 400)

### Statistics Calculated
- Mean, median, std deviation of drift
- Min/max drift values
- Drift rate (ms/hour) - shows if drift is increasing
- Sample count accuracy
- Outlier detection

## Expected Results (Healthy System)

✅ **Good:**
- Mean drift: 1-5 ms
- Max drift: < 10 ms
- Drift rate: ~0 ms/hour (stable)
- Sample counts: 400 ± 2% (392-408)
- ~3600 sync marks in each sensor

⚠️ **Warning Signs:**
- Mean drift > 10 ms
- Drift rate > 1 ms/hour (increasing trend)
- Sample count deviation > 5%

❌ **Problems:**
- Any drift > 50 ms
- Missing sync marks
- Sample counts consistently != 400

## Customization

### Different Threshold
```bash
# Strict 10ms threshold
python3 test_icg_ecg_drift_1hour.py localhost 10

# Lenient 100ms threshold
python3 test_icg_ecg_drift_1hour.py localhost 100
```

### Remote Device
```bash
python3 test_icg_ecg_drift_1hour.py 192.168.1.100
```

## Progress Monitoring

### Real-time Console
Updates every 60 seconds:
```
Progress: 10.5/60.0 min (ICG: 3142 sets, ECG: 3140 sets, Remaining: 49.5 min)
```

### Monitor CSV
```bash
# In another terminal
tail -f icg_ecg_drift_1hour_*.csv

# Or periodic view
watch -n 30 'tail -50 icg_ecg_drift_1hour_*.csv'
```

## Key Advantages

✅ **Zero Dependencies on Device**
- No matplotlib, numpy, or pandas needed
- Runs on any Python 3.6+ system
- Perfect for embedded systems

✅ **Flexible Workflow**
- Test and plot separately
- Regenerate plots anytime
- Analyze data with your own tools

✅ **Complete Data Export**
- CSV for spreadsheet analysis
- JSON for programmatic access
- All raw data preserved

✅ **Comprehensive Analysis**
- Drift tracking over time
- Sample rate validation
- Trend detection
- Statistical validation

## Troubleshooting

### Test won't start
```bash
# Check services running
netstat -tuln | grep -E '30009|1293'

# Test connectivity
echo '{"type":"get_data"}' | nc localhost 30009
```

### Plotting script fails
```bash
# Make sure you're on LOCAL machine, not device
pip3 install matplotlib numpy pandas

# Check file exists
ls -lh icg_ecg_drift_1hour_*.csv
```

### High drift values
- Check system load during test
- Test locally (not over network)
- Verify firmware timestamps enabled
- Check for thermal throttling

## Files

- `test_icg_ecg_drift_1hour.py` - Main test script (runs on device)
- `plot_drift_results.py` - Plotting script (runs on local machine)
- `DRIFT_TEST_README.md` - Complete documentation

## Next Steps

After reviewing results:
1. If drift is stable and low → System is healthy
2. If drift is increasing → Investigate timing/clock issues
3. If sample counts are off → Check buffer sizes and rates
4. Compare with other configurations using `test_icg_ecg_sync.py`

---

**Need more details?** See [DRIFT_TEST_README.md](DRIFT_TEST_README.md) for complete documentation.
