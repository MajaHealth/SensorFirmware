# Test #31 Execution Guide
## eMMC Detection - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #31
pytest tests/unit_tests/hw_component/test_031_emmc_detection.py -v -s
```

---

## Test Overview

### What This Test Does
Verifies that the eMMC storage on CM4 is properly detected and accessible by the operating system.

### Key Difference from Test #30
| Test #30 | Test #31 |
|----------|----------|
| CM4 in USB boot mode | CM4 booted normally |
| Runs on PC | Runs ON CM4 |
| Tests USB enumeration | Tests eMMC detection |
| No OS running on CM4 | OS running on CM4 |

### Test Steps
1. ✓ Verifies system is booted
2. ✓ Detects eMMC via `lsblk`
3. ✓ Detects eMMC via `/dev/mmcblk0`
4. ✓ Detects eMMC via `fdisk`
5. ✓ Detects eMMC via `/sys` filesystem
6. ✓ Verifies eMMC is readable

### Why This Matters
- Validates eMMC hardware is functional
- Ensures storage is accessible
- Confirms drivers are loaded
- Essential for firmware/OS storage

---

## Automation Level

### ✅ **100% Automated!**

Unlike Test #30, Test #31 is **fully automated** when run on CM4:

```
No manual steps required!
✓ Runs automatically on CM4
✓ No hardware connection needed
✓ No jumpers to set
✓ Suitable for CI/CD (if running on CM4)
```

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 with eMMC (not CM4 Lite)
- ✅ CM4 IO Board or carrier board
- ✅ Power supply
- ✅ Network connection (for SSH)

**Note:** CM4 Lite has no eMMC, so this test will fail on CM4 Lite.

### Software Required
- ✅ Operating system installed and booted on CM4
- ✅ pytest installed on CM4
- ✅ SSH access to CM4

---

## Running Test #31

### Method 1: SSH and Run Directly (Recommended)

```bash
# From your laptop
ssh pi@192.168.x.x

# On CM4
cd ~/sensor_test_project
source venv/bin/activate

# Run test
pytest tests/unit_tests/hw_component/test_031_emmc_detection.py -v -s
```

### Method 2: Use Remote Script

```bash
# From your laptop
./scripts/run-unit-test-remote.sh 192.168.x.x test_031
```

### Method 3: One-Liner via SSH

```bash
# From your laptop
ssh pi@192.168.x.x "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_031_emmc_detection.py -v -s"
```

---

## Expected Output

### Successful Test Run (CM4 with eMMC)

```
==================================================================
Test Case #31: eMMC Detection
==================================================================

HW Component Test - eMMC Storage
==================================================================

[STEP 1] Verify System is Booted
----------------------------------------------------------------------
[2026-01-14 20:00:00] Checking if system is booted...
[2026-01-14 20:00:00]   System uptime:  20:00:00 up  2:15,  1 user,  load average: 0.08, 0.12, 0.09
✓ System is booted
  Uptime:  20:00:00 up  2:15,  1 user,  load average: 0.08, 0.12, 0.09

[STEP 2] Detect eMMC via Multiple Methods
----------------------------------------------------------------------
[2026-01-14 20:00:00] Checking eMMC via lsblk...
[2026-01-14 20:00:00]   lsblk: mmcblk0     179:0    0   7.3G  0 disk
✓ Method 1: lsblk - eMMC detected

[2026-01-14 20:00:00] Checking eMMC via /dev/ filesystem...
[2026-01-14 20:00:00]   Device exists: /dev/mmcblk0
[2026-01-14 20:00:00]   Mode: 0o60660
✓ Method 2: /dev/ - /dev/mmcblk0 exists

[2026-01-14 20:00:01] Checking eMMC via fdisk...
[2026-01-14 20:00:01]   fdisk: Disk /dev/mmcblk0: 7.3 GiB, 7818182656 bytes, 15269888 sectors
✓ Method 3: fdisk - eMMC detected

[2026-01-14 20:00:01] Checking eMMC via /sys filesystem...
[2026-01-14 20:00:01]   Found: /sys/block/mmcblk0
[2026-01-14 20:00:01]   Size: 7.28 GB
[2026-01-14 20:00:01]   Model: 8GTF4R
✓ Method 4: /sys - eMMC sysfs entries found

Detection Summary:
  Detected by 4/4 methods
✓ eMMC detected by multiple methods

[STEP 3] Verify eMMC is Readable
----------------------------------------------------------------------
[2026-01-14 20:00:02] Verifying eMMC is readable...
[2026-01-14 20:00:02]   ✓ Successfully read 512 bytes
✓ eMMC is readable

[STEP 4] Gather eMMC Information
----------------------------------------------------------------------
[2026-01-14 20:00:02] Gathering eMMC information...
✓ eMMC partitions detected:
  mmcblk0     179:0    0     7818182656 disk
  ├─mmcblk0p1 179:1    0      268435456 part /boot
  └─mmcblk0p2 179:2    0     7549747200 part /

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ System is booted and operational
  ✓ eMMC detected by 4/4 methods
  ✓ eMMC device file exists: /dev/mmcblk0
  ✓ eMMC is readable
  ✓ eMMC detected by the system (PASS)

📄 Test log: /tmp/test_031_emmc_detection.log
==================================================================

====================== 1 passed in 3.24s ======================
```

### Failed Test (CM4 Lite - No eMMC)

```
[STEP 2] Detect eMMC via Multiple Methods
----------------------------------------------------------------------
✗ Method 1: lsblk - eMMC NOT detected
✗ Method 2: /dev/ - /dev/mmcblk0 NOT found
✗ Method 3: fdisk - eMMC NOT detected
✗ Method 4: /sys - eMMC sysfs entries NOT found

Detection Summary:
  Detected by 0/4 methods

FAILED - eMMC not detected by any method
  lsblk: False
  /dev/: False
  fdisk: False
  /sys:  False

Possible reasons:
  - Running on CM4 Lite (no eMMC)
  - eMMC hardware failure
  - Driver not loaded
  - Running in wrong environment
```

---

## Troubleshooting

### Issue 1: Test Fails on CM4 Lite

**Error:**
```
eMMC not detected by any method
Possible reasons:
  - Running on CM4 Lite (no eMMC)
```

**Explanation:**
- CM4 Lite has **no eMMC** (uses SD card instead)
- This test is designed for CM4 **with eMMC**
- Test failing is **expected behavior** on CM4 Lite

**Solution:**
- This test should only run on CM4 **with eMMC**
- Skip this test on CM4 Lite

### Issue 2: Permission Denied

**Error:**
```
eMMC is detected but not readable
Error: Permission denied
```

**Solution:**
```bash
# Ensure sudo is available
sudo -v

# Or add user to disk group
sudo usermod -a -G disk $USER

# Re-login for group changes to take effect
```

### Issue 3: lsblk Command Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'lsblk'
```

**Solution:**
```bash
# Install util-linux package
sudo apt update
sudo apt install util-linux
```

### Issue 4: Running on Wrong System

**Error:**
```
eMMC not detected by any method
```

**Check:**
```bash
# Verify you're on Raspberry Pi
cat /proc/cpuinfo | grep -i raspberry

# Check if mmcblk exists
ls -l /dev/mmcblk*

# Check dmesg for eMMC detection
dmesg | grep -i mmc
```

**Solution:**
- Ensure test runs **on CM4**, not on your laptop
- Use SSH or run-unit-test-remote.sh script

### Issue 5: eMMC Detected but Not Readable

**Error:**
```
eMMC is detected but not readable
This may indicate:
  - Permission issues
  - Hardware failure
  - Corrupted device
```

**Check:**
```bash
# Check dmesg for errors
dmesg | grep -i mmcblk | grep -i error

# Check eMMC health
sudo smartctl -a /dev/mmcblk0

# Try manual read
sudo dd if=/dev/mmcblk0 of=/dev/null bs=512 count=1
```

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
    'emmc_device': '/dev/mmcblk0',
    'expected_device_name': 'mmcblk0',
    'test_block_size': 512,
    'test_block_count': 1,
    'log_file': '/tmp/test_031_emmc_detection.log',
}
```

### Customizing Configuration

Edit the test file if your eMMC is on a different device:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        'emmc_device': '/dev/mmcblk1',  # Different device
        'expected_device_name': 'mmcblk1',
    }
```

---

## Comparison: Test #30 vs Test #31

| Aspect | Test #30 | Test #31 |
|--------|----------|----------|
| **Test Name** | CM4 Enumeration | eMMC Detection |
| **Runs On** | PC | CM4 |
| **CM4 State** | USB boot mode | Normal boot |
| **OS Running** | No | Yes |
| **Automation** | Semi-automated | **Fully automated** |
| **Manual Steps** | Hardware setup | None! |
| **CI/CD Ready** | ❌ No | ✅ Yes (on CM4) |
| **Purpose** | Test USB boot | Test eMMC detection |
| **Hardware** | CM4 + USB cable | CM4 booted normally |

---

## CI/CD Integration

### ✅ Suitable for CI/CD

Test #31 is **fully automated** and can run in CI/CD **if your CI runner is on CM4**:

```yaml
# GitLab CI example (if runner is on CM4)
test:emmc:
  stage: test
  script:
    - pytest tests/unit_tests/hw_component/test_031_emmc_detection.py -v
  tags:
    - raspberry-pi-cm4
  only:
    - merge_requests
```

### Using Remote CM4 for CI/CD

```yaml
# Run test on remote CM4 from CI
test:emmc:remote:
  stage: test
  script:
    - export PI_IP=192.168.1.100
    - ./scripts/run-unit-test-remote.sh $PI_IP test_031
  tags:
    - linux
```

---

## Test Duration

- **Typical:** 2-4 seconds
- **Fast:** Fully automated, no waiting
- **No manual interaction required**

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ System is booted
2. ✓ eMMC detected by at least 1 method (ideally all 4)
3. ✓ eMMC device file exists
4. ✓ eMMC is readable

### Test FAILS ✗ if:
- System not booted
- eMMC not detected by any method
- eMMC detected but not readable
- Running on CM4 Lite (no eMMC)

---

## Running from WSL2/Laptop

### ❌ Cannot Run Locally on WSL2

This test **must run on CM4** because:
- WSL2 doesn't have CM4's eMMC
- `/dev/mmcblk0` doesn't exist on laptop
- Test validates actual CM4 hardware

### ✅ Run Remotely on CM4

```bash
# From WSL2/laptop, run test on CM4
export PI_IP=192.168.x.x
./scripts/run-unit-test-remote.sh $PI_IP test_031
```

---

## Related Tests

- **Test #30:** CM4 enumeration on PC (runs on PC, CM4 in USB mode)
- **Test #31:** eMMC detection (runs on CM4, normal boot) ← You are here
- **Test #32:** Storage performance (if exists)

---

## Summary

**Test #31** validates eMMC detection on CM4:
- ✅ **Fully automated** (no manual steps!)
- ✅ Runs **ON CM4** (not on PC)
- ✅ Requires CM4 **with eMMC** (not Lite)
- ✅ Suitable for **CI/CD** (on CM4 runners)
- ✅ Fast execution (~2-4 seconds)

**Run command:**
```bash
# On CM4:
pytest tests/unit_tests/hw_component/test_031_emmc_detection.py -v -s

# Remote from laptop:
./scripts/run-unit-test-remote.sh $PI_IP test_031
```

**Prerequisites:**
- CM4 with eMMC (not Lite)
- OS booted on CM4
- SSH access (for remote execution)

---

**Test #31 is ready to use and fully automated! 🎉**
