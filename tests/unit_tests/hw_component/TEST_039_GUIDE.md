# Test #39 Execution Guide
## Data Integrity Verification After Read/Write - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #39
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v -s
```

---

## Test Overview

### What This Test Does
Performs **comprehensive data integrity verification** using multiple write/read cycles with various data patterns and file sizes, validated through cryptographic hash verification.

### Key Difference from Test #38

| Aspect | Test #38 | Test #39 |
|--------|----------|----------|
| **Focus** | Basic I/O operations | **Data integrity focus** |
| **File Sizes** | Single size (1MB) | **Multiple sizes** (1MB, 5MB, 10MB) |
| **Data Patterns** | Random only | **4 patterns** (random, zeros, ones, alternating) |
| **Test Cycles** | Single pass | **Multiple cycles** (3x per pattern/size) |
| **Purpose** | Validate storage works | **Validate no corruption** |
| **Best For** | Quick functional test | **Thorough integrity validation** |

### Test Parameters
- **File Sizes**: 1MB, 5MB, 10MB (configurable)
- **Data Patterns**:
  - Random (cryptographic random data)
  - Zeros (all 0x00 bytes)
  - Ones (all 0xFF bytes)
  - Alternating (0xAA pattern)
- **Verification Cycles**: 3 cycles per pattern/size combination
- **Hash Algorithm**: SHA256 (cryptographically secure)

### Why This Matters
- Detects intermittent storage failures
- Tests various data patterns (some patterns stress storage differently)
- Multiple cycles catch transient corruption issues
- Essential for production data reliability
- Validates storage under varied workloads

---

## Automation Level

### ✅ **100% Automated!**

Test #39 is **fully automated** but more thorough than Test #38:

```
No manual steps required!
✓ Runs automatically on CM4
✓ No hardware setup needed
✓ No user interaction required
✓ Suitable for burn-in testing
✓ Longer execution (~30-60 seconds)
✓ Comprehensive verification
```

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 (any variant)
- ✅ CM4 IO Board or carrier board
- ✅ Power supply
- ✅ **CM4 with eMMC** (not CM4 Lite)
- ✅ SD card (optional, for SD card tests)

### Software Required
- ✅ Operating system installed and booted on CM4
- ✅ pytest installed on CM4
- ✅ SSH access to CM4
- ✅ Filesystems mounted with write permissions
- ✅ Sufficient free space (~50MB recommended)

### Storage Requirements
- ✅ eMMC must be mounted
- ✅ SD card must be mounted (if testing SD)
- ✅ At least 50MB free space (for multiple test files)
- ✅ Write permissions on mount points

---

## Running Test #39

### Method 1: SSH and Run Directly (Recommended)

```bash
# From your laptop
ssh pi@192.168.x.x

# On CM4
cd ~/sensor_test_project
source venv/bin/activate

# Run test
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v -s
```

### Method 2: Use Remote Script

```bash
# From your laptop
./scripts/run-unit-test-remote.sh 192.168.x.x test_039
```

### Method 3: Quick Test (Fewer Cycles)

```python
# Edit test_config to reduce cycles
'test_file_sizes_mb': [1],  # Only 1MB files
'verification_cycles': 1,    # Only 1 cycle
```

```bash
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v -s
```

---

## Expected Output

### Successful Test Run (Full Test)

```
==================================================================
Test Case #39: Data Integrity Verification
==================================================================

HW Component Test - Storage Data Integrity
==================================================================

TEST METHOD:
  1. Write known data patterns to storage
  2. Read data back from storage
  3. Verify integrity using cryptographic hashes
  4. Test multiple file sizes and patterns
  5. Perform multiple verification cycles
==================================================================

[STEP 1] Detect Storage Devices
----------------------------------------------------------------------
[2026-01-15 18:00:00] Detecting storage devices...
[2026-01-15 18:00:00]   ✓ eMMC detected: /dev/mmcblk0
[2026-01-15 18:00:00]   ✓ SD card detected: /dev/mmcblk1
✓ eMMC detected: /dev/mmcblk0
✓ SD card detected: /dev/mmcblk1

[STEP 2] Find Writable Locations
----------------------------------------------------------------------
[2026-01-15 18:00:00] Finding writable location for /dev/mmcblk0...
[2026-01-15 18:00:00]   ✓ Using: /tmp
✓ eMMC writable location: /tmp
[2026-01-15 18:00:00] Finding writable location for /dev/mmcblk1...
[2026-01-15 18:00:00]   ✓ Mounted at: /media/sdcard
✓ SD card writable location: /media/sdcard

[STEP 3] eMMC Data Integrity Testing
----------------------------------------------------------------------
Testing with 3 file sizes
Testing with 4 data patterns
Verification cycles per test: 3

[2026-01-15 18:00:01] Cycle 1: Testing 1MB with 'random' pattern
[2026-01-15 18:00:01]   Generating 1MB test data (random)...
[2026-01-15 18:00:01]   Expected SHA256: a7f4d3e9c2b15678...
[2026-01-15 18:00:01]   Writing to: /tmp/integrity_test_random_1mb_1.bin
[2026-01-15 18:00:01]   Write time: 0.08s
[2026-01-15 18:00:01]   Reading from: /tmp/integrity_test_random_1mb_1.bin
[2026-01-15 18:00:01]   Read time: 0.04s
[2026-01-15 18:00:01]   Actual SHA256: a7f4d3e9c2b15678...
[2026-01-15 18:00:01]   ✓ Integrity verified: Hashes match

[2026-01-15 18:00:02] Cycle 2: Testing 1MB with 'random' pattern
[2026-01-15 18:00:02]   ✓ Integrity verified: Hashes match

[2026-01-15 18:00:03] Cycle 3: Testing 1MB with 'random' pattern
[2026-01-15 18:00:03]   ✓ Integrity verified: Hashes match

[2026-01-15 18:00:04] Cycle 4: Testing 1MB with 'zeros' pattern
[2026-01-15 18:00:04]   ✓ Integrity verified: Hashes match

[2026-01-15 18:00:05] Cycle 5: Testing 1MB with 'zeros' pattern
[2026-01-15 18:00:05]   ✓ Integrity verified: Hashes match

... (cycles 6-36 omitted for brevity) ...

eMMC Testing Complete:
  Total cycles: 36
  Passed: 36
  Failed: 0
✓ All eMMC integrity checks passed

[STEP 4] SD Card Data Integrity Testing
----------------------------------------------------------------------
... (similar output for SD card) ...

SD Card Testing Complete:
  Total cycles: 36
  Passed: 36
  Failed: 0
✓ All SD card integrity checks passed

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ eMMC integrity cycles passed: 36/36
  ✓ File sizes tested: [1, 5, 10]
  ✓ Data patterns tested: ['random', 'zeros', 'ones', 'alternating']
  ✓ Hash algorithm: SHA256
  ✓ SD card integrity cycles passed: 36/36
  ✓ Data integrity validated after read/write operations (PASS)

📄 Test log: /tmp/test_039_data_integrity.log
==================================================================

====================== 1 passed in 45.23s ======================
```

### Failed Test (Data Corruption Detected)

```
[STEP 3] eMMC Data Integrity Testing
----------------------------------------------------------------------
[2026-01-15 18:00:15] Cycle 15: Testing 5MB with 'alternating' pattern
[2026-01-15 18:00:15]   Generating 5MB test data (alternating)...
[2026-01-15 18:00:15]   Expected SHA256: b2e8a1f7d4c93456...
[2026-01-15 18:00:15]   Writing to: /tmp/integrity_test_alternating_5mb_15.bin
[2026-01-15 18:00:16]   Write time: 0.42s
[2026-01-15 18:00:16]   Reading from: /tmp/integrity_test_alternating_5mb_15.bin
[2026-01-15 18:00:16]   Read time: 0.21s
[2026-01-15 18:00:16]   Actual SHA256: 7f3c9d2e1a584b7f...
[2026-01-15 18:00:16]   ✗ Integrity FAILED: Hashes don't match!
[2026-01-15 18:00:16]     Expected: b2e8a1f7d4c93456...
[2026-01-15 18:00:16]     Actual:   7f3c9d2e1a584b7f...

FAILED - eMMC data integrity check FAILED!
  Cycle: 15
  File size: 5MB
  Pattern: alternating
  Expected hash: b2e8a1f7d4c93456...
  Actual hash: 7f3c9d2e1a584b7f...
This indicates storage corruption or hardware failure.
```

---

## Troubleshooting

All troubleshooting from Test #38 applies, plus:

### Issue 1: Test Takes Too Long

**Problem:**
Test runs for 2-3 minutes with default configuration.

**Cause:**
Testing 3 file sizes × 4 patterns × 3 cycles × 2 storages = 72 total cycles

**Solution:**
Reduce test parameters:

```python
# Edit test_config
'test_file_sizes_mb': [1],           # Only test 1MB files
'test_patterns': ['random'],          # Only test random data
'verification_cycles': 1,             # Only 1 cycle per test
# Total: 1 × 1 × 1 × 2 = 2 cycles (much faster)
```

### Issue 2: Intermittent Failures

**Problem:**
Test passes sometimes, fails other times.

**Possible Causes:**
- Marginal storage hardware (failing)
- Power supply issues (voltage drops)
- Thermal issues (storage overheating)
- Loose connections

**Solutions:**
```bash
# Check dmesg for hardware errors
dmesg | grep -i "mmc\|error\|timeout"

# Check system temperature
vcgencmd measure_temp

# Monitor power supply voltage
vcgencmd measure_volts

# Run extended test
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v --count=10
```

### Issue 3: Specific Pattern Fails

**Problem:**
Test passes with random data but fails with zeros/ones/alternating.

**Explanation:**
- Some failing storage exhibits pattern-dependent failures
- All-zeros or all-ones can reveal cell retention issues
- Alternating patterns (0xAA) stress read amplifiers

**Implication:**
This is a **real hardware problem** - storage is unreliable!

**Solution:**
Replace storage hardware.

### Issue 4: Large File Sizes Fail

**Problem:**
1MB tests pass, but 5MB and 10MB tests fail.

**Possible Causes:**
- Bad blocks in specific regions
- Cache/buffer overflow issues
- Thermal throttling (longer operations heat up storage)

**Solutions:**
```bash
# Check for bad blocks
sudo badblocks -sv /dev/mmcblk0

# Check filesystem errors
sudo fsck -n /dev/mmcblk0p2

# Monitor during test
watch -n1 'vcgencmd measure_temp'
```

---

## Test Configuration

### Default Configuration

```python
{
    # Test file configurations
    'test_file_sizes_mb': [1, 5, 10],  # Multiple file sizes
    'verification_cycles': 3,          # 3 cycles per pattern/size

    # Device names
    'emmc_device': 'mmcblk0',
    'sd_device_names': ['mmcblk1', 'sda'],

    # Hash algorithm
    'hash_algorithm': 'sha256',  # sha256, sha512, or md5

    # Test patterns
    'test_patterns': [
        'random',      # Cryptographic random
        'zeros',       # All 0x00
        'ones',        # All 0xFF
        'alternating', # 0xAA pattern
    ],

    # Logging
    'enable_logging': True,
    'log_file': '/tmp/test_039_data_integrity.log',
}
```

### Customizing Configuration

**Quick Test (Minimal)**:
```python
'test_file_sizes_mb': [1],
'verification_cycles': 1,
'test_patterns': ['random'],
# Total: 1 file size × 1 pattern × 1 cycle = 1 test
```

**Thorough Test (Extended)**:
```python
'test_file_sizes_mb': [1, 5, 10, 20, 50],
'verification_cycles': 10,
'test_patterns': ['random', 'zeros', 'ones', 'alternating'],
# Total: 5 × 4 × 10 = 200 cycles (stress test)
```

**Security-Focused (SHA512)**:
```python
'hash_algorithm': 'sha512',  # Stronger hash (slower)
```

**Custom Pattern**:
```python
def generate_test_data(self, size_bytes, pattern, config):
    if pattern == 'custom':
        # Your custom pattern
        return bytes([0x5A] * size_bytes)  # 0x5A pattern
```

---

## Comparison: Storage Tests

| Aspect | Test #31 | Test #38 | Test #39 |
|--------|----------|----------|----------|
| **Test Name** | eMMC Detection | Read/Write Ops | **Data Integrity** |
| **Focus** | Detection | Basic I/O | **Comprehensive integrity** |
| **File Sizes** | N/A | 1MB | **1MB, 5MB, 10MB** |
| **Patterns** | N/A | Random | **4 patterns** |
| **Cycles** | N/A | 1 | **3 per pattern/size** |
| **Total Tests** | 4 checks | 1 cycle | **36 cycles** |
| **Hash Verify** | ❌ No | ✅ SHA256 | ✅ **SHA256 (multiple)** |
| **Duration** | ~2-4 sec | ~5-10 sec | **~30-60 sec** |
| **Best For** | Quick check | Functional test | **Burn-in/validation** |

---

## CI/CD Integration

### ✅ Suitable for CI/CD

Test #39 is fully automated but longer-running:

```yaml
# GitLab CI - Quick integrity check
test:storage:integrity:quick:
  stage: test
  script:
    - |
      # Reduce cycles for CI
      sed -i "s/'verification_cycles': 3/'verification_cycles': 1/g" \
        tests/unit_tests/hw_component/test_039_data_integrity.py
    - pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v
  tags:
    - raspberry-pi-cm4
  timeout: 5m

# GitLab CI - Full integrity check (nightly)
test:storage:integrity:full:
  stage: test
  script:
    - pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v
  tags:
    - raspberry-pi-cm4
  timeout: 10m
  only:
    - schedules  # Run nightly
```

### Burn-In Testing

Use Test #39 for hardware burn-in:

```bash
# Run extended burn-in test (100 cycles per pattern)
# Edit test_config:
'verification_cycles': 100,

# Run test
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v \
  | tee burn_in_results.txt

# Should take ~30-60 minutes
```

---

## Test Duration

- **Quick (minimal config)**: ~5-10 seconds
- **Default (36 cycles)**: ~30-60 seconds
- **Extended (200 cycles)**: ~5-10 minutes
- **Burn-in (1000+ cycles)**: ~30-60 minutes

**Factors affecting duration:**
- Storage speed (eMMC faster than SD)
- File sizes (larger = longer)
- Number of cycles
- System load

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ All write/read cycles complete without errors
2. ✓ **All hashes match** (100% integrity)
3. ✓ All file sizes tested successfully
4. ✓ All data patterns tested successfully
5. ✓ No I/O errors during operations

### Test FAILS ✗ if:
- **Any hash mismatch** (data corruption)
- Write operation fails
- Read operation fails
- Storage not accessible

### Partial Pass:
- eMMC passes, SD card fails (SD failure is informational)

---

## Use Cases

### 1. Production Qualification
```bash
# Before deploying to production
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v
```

### 2. Hardware Burn-In
```python
# Extended burn-in
'verification_cycles': 100,
'test_file_sizes_mb': [1, 5, 10, 20, 50],
```

### 3. RMA Validation
```bash
# Test returned hardware
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v
```

### 4. Regular Health Checks
```bash
# Weekly integrity check
0 2 * * 0 cd ~/sensor_test_project && \
  pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v
```

---

## Advanced Usage

### Compare Test #38 vs #39

```bash
# Quick functional test (Test #38)
time pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v
# ~5-10 seconds

# Thorough integrity test (Test #39)
time pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v
# ~30-60 seconds
```

### Pattern-Specific Testing

```python
# Only test problematic patterns
'test_patterns': ['alternating', 'ones'],  # Skip random/zeros
```

### Size-Specific Testing

```python
# Only test large files (stress test)
'test_file_sizes_mb': [50, 100, 200],
```

---

## Summary

**Test #39** provides comprehensive data integrity validation:
- ✅ **Multiple test cycles** (catches intermittent issues)
- ✅ **Various data patterns** (stresses different failure modes)
- ✅ **Multiple file sizes** (tests different storage regions)
- ✅ **Cryptographic verification** (mathematically proves integrity)
- ✅ **Fully automated** (no manual steps)
- ✅ Suitable for **burn-in testing**
- ✅ Detects **intermittent failures**
- ⏱️ Longer execution (~30-60 seconds default)

**When to use Test #38 vs Test #39:**
- **Test #38**: Quick functional validation, CI/CD
- **Test #39**: Thorough integrity validation, burn-in, RMA testing

**Run command:**
```bash
# On CM4:
pytest tests/unit_tests/hw_component/test_039_data_integrity.py -v -s

# Remote from laptop:
./scripts/run-unit-test-remote.sh $PI_IP test_039
```

**Prerequisites:**
- CM4 with eMMC (not Lite)
- Booted system
- ~50MB free space
- 30-60 seconds test time

---

**Test #39 is ready for comprehensive integrity validation! 🎉**
