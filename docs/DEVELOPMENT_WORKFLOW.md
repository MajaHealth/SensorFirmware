# Development Workflow - Writing & Running Tests

**Project:** Sensor Firmware Testing
**Date:** 2025-12-26
**For:** Developers

---

## Quick Start

### Everything Happens on Your Laptop! 💻

```bash
# 1. Write test on laptop
vim tests/hardware-integration/test_ads1293.py

# 2. Run test (automatically deploys to CM4, runs, fetches results)
./scripts/run-test.sh tests/hardware-integration/test_ads1293.py

# 3. Analyze results on laptop
cd analysis/data/20251226-143022/
jupyter notebook
```

**That's it!** No manual CM4 access needed.

---

## Complete Workflow

```
┌────────────────────────────────────────────────────────────────┐
│ YOUR LAPTOP (All development happens here)                     │
│                                                                │
│ 1. WRITE TEST                                                  │
│    ~/sensor-firmware-build/tests/test_ads1293.py              │
│                                                                │
│ 2. RUN COMMAND                                                 │
│    ./scripts/run-test.sh tests/test_ads1293.py                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                             ↓
        ┌────────────────────────────────────────┐
        │ Script does AUTOMATICALLY:             │
        │ 1. Transfer tests to CM4 ──────────┐   │
        │ 2. Run pytest on CM4               │   │
        │ 3. Fetch results to laptop         │   │
        │ 4. Delete tests from CM4 (cleanup) │   │
        └────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│ BACK ON LAPTOP (Results ready for analysis)                    │
│                                                                │
│ analysis/data/20251226-143022/                                │
│ ├── test_report.html          ← Open in browser              │
│ ├── ecg_data.jsonl            ← Analyze in Jupyter/Python    │
│ └── plots/                    ← Review visualizations        │
│                                                                │
│ 4. ANALYZE                                                     │
│    jupyter notebook analysis/notebooks/ecg_analysis.ipynb     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure on Laptop

```
~/sensor-firmware-build/
├── tests/                          ← YOU WRITE TESTS HERE
│   ├── hardware-integration/
│   │   ├── test_ads1293_ecg.py
│   │   ├── test_max30009_icg.py
│   │   └── test_synchronized.py
│   ├── fw-app-integration/
│   │   ├── test_max30009_api.py
│   │   └── test_power_service.py
│   ├── common/
│   │   ├── tcp_client.py
│   │   ├── validators.py
│   │   └── data_logger.py
│   ├── config/
│   │   └── test_config.yaml
│   └── requirements.txt
│
├── scripts/
│   └── run-test.sh                 ← THE MAGIC SCRIPT
│
└── analysis/                       ← RESULTS COME HERE
    ├── data/                       ← Test data
    │   ├── 20251226-143022/
    │   │   ├── test_report.html
    │   │   ├── ecg_60s.jsonl
    │   │   └── impedance.jsonl
    │   └── 20251226-153000/
    │       └── ecg_1hr.jsonl
    │
    ├── notebooks/                  ← YOUR ANALYSIS
    │   ├── ecg_analysis.ipynb
    │   └── impedance_analysis.ipynb
    │
    └── results/                    ← FINAL OUTPUTS
        ├── plots/
        └── reports/
```

**Note:** CM4 keeps NOTHING - all tests and results are temporary!

---

## Usage Examples

### Run Single Test File

```bash
./scripts/run-test.sh tests/hardware-integration/test_ads1293.py
```

### Run Specific Test Function

```bash
./scripts/run-test.sh tests/test_ads1293.py::test_ecg_60s
```

### Run All Tests in Directory

```bash
./scripts/run-test.sh tests/hardware-integration/
```

### Run All Tests

```bash
./scripts/run-test.sh --all
```

### Configure CM4 IP Address

```bash
# If CM4 is not at default IP (192.168.1.100)
export CM4_IP=10.0.0.50
./scripts/run-test.sh tests/test_ads1293.py
```

---

## What the Script Does

### Step 1: Transfer Tests to CM4

```
Laptop                          CM4
tests/ ──────────────────────→  /tmp/sensor-tests-12345/
(your files)                    (temporary copy)
```

### Step 2: Run pytest on CM4

```
CM4: pytest /tmp/sensor-tests-12345/test_ads1293.py
     ├── Connects to firmware services (ports 1293, 30009, etc.)
     ├── Collects sensor data from hardware
     ├── Saves to /tmp/test-results-12345/
     └── Generates HTML report
```

### Step 3: Fetch Results to Laptop

```
CM4                                      Laptop
/tmp/test-results-12345/ ────────────→  analysis/data/20251226-143022/
├── test_report.html                    ├── test_report.html
├── ecg_data.jsonl                      ├── ecg_data.jsonl
└── plots/                              └── plots/
```

### Step 4: Cleanup CM4

```
CM4: rm -rf /tmp/sensor-tests-12345/
     rm -rf /tmp/test-results-12345/

(CM4 is clean - no test files left behind)
```

---

## Example Output

```bash
$ ./scripts/run-test.sh tests/test_ads1293.py

[INFO] Checking CM4 connectivity...
[INFO] ✓ CM4 is reachable
[INFO] Creating temporary directories on CM4...
[INFO] Transferring tests to CM4...
[INFO] ✓ Tests transferred
[INFO] Checking pytest installation on CM4...
[INFO] Running tests on CM4...

════════════════════════════════════════════════════════════════
  Test Execution on CM4
════════════════════════════════════════════════════════════════

tests/test_ads1293.py::test_ecg_connection ✓ PASSED
tests/test_ads1293.py::test_ecg_60s ✓ PASSED
tests/test_ads1293.py::test_ecg_sync_markers ✓ PASSED

3 passed in 65.2s

════════════════════════════════════════════════════════════════

[INFO] Fetching results from CM4 to laptop...
[INFO] ✓ Results saved to: ./analysis/data/20251226-143022
[INFO] Tests and results cleaned up from CM4

════════════════════════════════════════════════════════════════
  Test Complete!
════════════════════════════════════════════════════════════════

Results location: ./analysis/data/20251226-143022

HTML Report:      ./analysis/data/20251226-143022/test_report.html
Data files:
  - ./analysis/data/20251226-143022/ecg_60s.jsonl (2.3M)
  - ./analysis/data/20251226-143022/sync_data.jsonl (45K)

════════════════════════════════════════════════════════════════

[INFO] Opening HTML report in browser...
[INFO] Done! Ready for analysis.
```

---

## Daily Development Cycle

### Typical Day:

```bash
# Morning: Write first test
vim tests/test_new_sensor.py

# Run it
./scripts/run-test.sh tests/test_new_sensor.py

# Check HTML report
# (Opens automatically in browser)

# Analyze data in Jupyter
cd analysis
jupyter notebook

# Found an issue? Fix test and re-run
vim tests/test_new_sensor.py
./scripts/run-test.sh tests/test_new_sensor.py

# Repeat until satisfied
```

### Iteration Time:

- ❌ Manual workflow: ~10-15 minutes per iteration
- ✅ Automated script: ~2-3 minutes per iteration

---

## Analysis Workflow

### After Test Completes:

```bash
# Results are in: analysis/data/20251226-143022/

# Option 1: Jupyter Notebook
cd analysis
jupyter notebook

# In notebook:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
data = pd.read_json('data/20251226-143022/ecg_60s.jsonl', lines=True)

# Analyze...
```

### Example Analysis Script:

```python
# analysis/scripts/quick_ecg_check.py

import sys
import pandas as pd
import numpy as np

# Load latest results
result_dir = sys.argv[1]
data = pd.read_json(f'{result_dir}/ecg_60s.jsonl', lines=True)

# Extract samples
samples = []
for row in data:
    for sample in row:
        if sample[0] != -99999:  # Skip sync markers
            samples.append(sample[0])

# Quick stats
print(f"Total samples: {len(samples)}")
print(f"Mean: {np.mean(samples):.2f}")
print(f"Std: {np.std(samples):.2f}")
print(f"Min: {np.min(samples)}")
print(f"Max: {np.max(samples)}")

# Usage:
# python analysis/scripts/quick_ecg_check.py analysis/data/20251226-143022/
```

---

## First-Time Setup

### One-Time Configuration:

```bash
# 1. Set CM4 IP address (if not default)
echo 'export CM4_IP=192.168.1.100' >> ~/.bashrc
source ~/.bashrc

# 2. Set up SSH key (no password prompt)
ssh-keygen -t rsa -b 4096
ssh-copy-id pi@192.168.1.100

# 3. Test connection
ssh pi@192.168.1.100 echo "Connected!"

# 4. Create analysis directory
mkdir -p analysis/{data,notebooks,scripts,results}

# 5. Install Jupyter on laptop (if needed)
pip3 install jupyter pandas numpy scipy matplotlib

# Done! Ready to write tests.
```

---

## Troubleshooting

### Cannot connect to CM4

```bash
# Check CM4 IP
ping 192.168.1.100

# Check SSH
ssh pi@192.168.1.100

# Set correct IP
export CM4_IP=10.0.0.50
./scripts/run-test.sh tests/test_file.py
```

### pytest not installed on CM4

The script will automatically install it on first run.

Or manually:
```bash
ssh pi@192.168.1.100
pip3 install pytest pytest-html numpy scipy matplotlib pyyaml
```

### Test fails

Check the HTML report:
```bash
# Opens automatically, or:
xdg-open analysis/data/20251226-143022/test_report.html
```

Review logs:
```bash
cat analysis/data/20251226-143022/pytest.log
```

### Results not transferred

Check CM4 disk space:
```bash
ssh pi@192.168.1.100 df -h
```

---

## Advanced Usage

### Run Tests with Custom pytest Options

Edit `run-test.sh` pytest command line, or:

```bash
# Run with verbose output
ssh pi@CM4 "cd /tmp/sensor-tests-XXX && pytest -vv"

# Run with debugging
ssh pi@CM4 "cd /tmp/sensor-tests-XXX && pytest -vv -s --pdb"

# Run with specific markers
ssh pi@CM4 "cd /tmp/sensor-tests-XXX && pytest -m slow"
```

### Keep Tests on CM4 (for debugging)

Comment out cleanup in `run-test.sh`:

```bash
# trap cleanup_cm4 EXIT  # Disabled
```

Then SSH to CM4 and debug:
```bash
ssh pi@192.168.1.100
cd /tmp/sensor-tests-XXXXX
pytest -vv -s
```

### Parallel Test Execution

```bash
# Install pytest-xdist on CM4
ssh pi@CM4 "pip3 install pytest-xdist"

# Modify run-test.sh pytest line:
pytest -n 4 ${PYTEST_TARGET}  # 4 parallel workers
```

---

## Summary

### ✅ What You Do:
1. Write tests on **laptop** (`tests/`)
2. Run script: `./scripts/run-test.sh tests/test_file.py`
3. Analyze results on **laptop** (`analysis/data/`)

### ✅ What Script Does Automatically:
1. Transfer tests to CM4 (temporary)
2. Run pytest on CM4
3. Fetch results to laptop
4. Clean up CM4 (no files left)

### ✅ Result:
- **No manual CM4 access needed**
- **Fast iteration** (2-3 minutes)
- **All files on laptop** (tests + results)
- **CM4 stays clean** (no leftover files)

---

## Next Steps

1. ✅ Read this workflow document
2. ✅ Run first-time setup
3. ✅ Write your first test
4. ✅ Run: `./scripts/run-test.sh tests/your_test.py`
5. ✅ Analyze results in Jupyter

**Happy testing!** 🚀
