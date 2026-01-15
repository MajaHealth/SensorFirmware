# Test #38 Execution Guide
## Read/Write Operations on Storage Interfaces - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #38
pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v -s
```

---

## Test Overview

### What This Test Does
Validates that storage interfaces (eMMC and SD card) can perform read/write operations correctly with full data integrity verification.

### Test Steps
1. **Detect Storage Devices**: Finds eMMC and SD card (if present)
2. **Find Writable Locations**: Locates mounted, writable filesystems
3. **Write Test - eMMC**: Writes 1MB test file with checksum
4. **Read Test - eMMC**: Reads file back and verifies checksum
5. **Write Test - SD Card**: Writes 1MB test file (if SD available)
6. **Read Test - SD Card**: Reads file back and verifies checksum
7. **Cleanup**: Removes test files

### Why This Matters
- Validates storage hardware is functional
- Ensures data integrity (no corruption)
- Detects storage failures early
- Measures storage performance
- Essential for firmware storage and logging
- Critical for production reliability

---

## Automation Level

### ✅ **100% Automated!**

Test #38 is **fully automated** when run on CM4:

```
No manual steps required!
✓ Runs automatically on CM4
✓ No hardware setup needed (if storage present)
✓ No user interaction required
✓ Suitable for CI/CD
✓ Fast execution (~5-10 seconds)
✓ Self-cleaning (removes test files)
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
- ✅ Sufficient free space (~10MB minimum)

### Storage Requirements
- ✅ eMMC must be mounted (usually as `/`)
- ✅ SD card must be mounted (if testing SD)
- ✅ At least 10MB free space on each device
- ✅ Write permissions on mount points

---

## Running Test #38

### Method 1: SSH and Run Directly (Recommended)

```bash
# From your laptop
ssh pi@192.168.x.x

# On CM4
cd ~/sensor_test_project
source venv/bin/activate

# Run test
pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v -s
```

### Method 2: Use Remote Script

```bash
# From your laptop
./scripts/run-unit-test-remote.sh 192.168.x.x test_038
```

### Method 3: One-Liner via SSH

```bash
# From your laptop
ssh pi@192.168.x.x "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v -s"
```

---

## Expected Output

### Successful Test Run (eMMC + SD Card)

```
==================================================================
Test Case #38: Read/Write Operations on Storage
==================================================================

HW Component Test - eMMC + SD Card
==================================================================

[STEP 1] Detect Storage Devices
----------------------------------------------------------------------
[2026-01-15 17:00:00] Detecting storage devices...
[2026-01-15 17:00:00]   Available block devices:
[2026-01-15 17:00:00]     NAME        TYPE  SIZE MOUNTPOINT
[2026-01-15 17:00:00]     mmcblk0     disk  7.3G
[2026-01-15 17:00:00]     ├─mmcblk0p1 part  256M /boot
[2026-01-15 17:00:00]     └─mmcblk0p2 part  7.1G /
[2026-01-15 17:00:00]     mmcblk1     disk   32G
[2026-01-15 17:00:00]     └─mmcblk1p1 part   32G /media/sdcard
[2026-01-15 17:00:00]   ✓ eMMC detected: /dev/mmcblk0
[2026-01-15 17:00:00]   ✓ SD card detected: /dev/mmcblk1
✓ eMMC detected: /dev/mmcblk0
✓ SD card detected: /dev/mmcblk1

[STEP 2] Find Writable Locations
----------------------------------------------------------------------
[2026-01-15 17:00:00] Finding writable location for /dev/mmcblk0...
[2026-01-15 17:00:00]   ✓ Mounted at: /
[2026-01-15 17:00:00]   ✓ Using system tmp: /tmp
[2026-01-15 17:00:00]   Filesystem info:
[2026-01-15 17:00:00]     Filesystem      Size  Used Avail Use% Mounted on
[2026-01-15 17:00:00]     /dev/mmcblk0p2  7.1G  2.5G  4.3G  37% /
✓ eMMC writable location: /tmp
[2026-01-15 17:00:01] Finding writable location for /dev/mmcblk1...
[2026-01-15 17:00:01]   ✓ Mounted at: /media/sdcard
[2026-01-15 17:00:01]   ✓ Writable location: /media/sdcard/tmp
[2026-01-15 17:00:01]   Filesystem info:
[2026-01-15 17:00:01]     Filesystem      Size  Used Avail Use% Mounted on
[2026-01-15 17:00:01]     /dev/mmcblk1p1   32G  1.2G   30G   4% /media/sdcard
✓ SD card writable location: /media/sdcard/tmp

[STEP 3] Write Test - eMMC
----------------------------------------------------------------------
[2026-01-15 17:00:01] Writing 1MB test file...
[2026-01-15 17:00:01]   ✓ File written: /tmp/storage_test_1736956801.bin
[2026-01-15 17:00:01]   Size: 1MB
[2026-01-15 17:00:01]   Time: 0.08s
[2026-01-15 17:00:01]   Speed: 12.50 MB/s
[2026-01-15 17:00:01]   Checksum: a7f4d3e9c2b15678...
✓ eMMC write test passed
  Write speed: 12.50 MB/s

[STEP 4] Read Test - eMMC
----------------------------------------------------------------------
[2026-01-15 17:00:02] Reading test file...
[2026-01-15 17:00:02]   ✓ File read: /tmp/storage_test_1736956801.bin
[2026-01-15 17:00:02]   Size: 1.00MB
[2026-01-15 17:00:02]   Time: 0.04s
[2026-01-15 17:00:02]   Speed: 25.00 MB/s
[2026-01-15 17:00:02]   Checksum: a7f4d3e9c2b15678...
[2026-01-15 17:00:02]   ✓ Checksum match: Data integrity verified
✓ eMMC read test passed
  Read speed: 25.00 MB/s
✓ Data integrity verified

[STEP 5] Write Test - SD Card
----------------------------------------------------------------------
[2026-01-15 17:00:02] Writing 1MB test file...
[2026-01-15 17:00:03]   ✓ File written: /media/sdcard/tmp/storage_test_1736956803.bin
[2026-01-15 17:00:03]   Size: 1MB
[2026-01-15 17:00:03]   Time: 0.15s
[2026-01-15 17:00:03]   Speed: 6.67 MB/s
[2026-01-15 17:00:03]   Checksum: b2e8a1f7d4c93456...
✓ SD card write test passed
  Write speed: 6.67 MB/s

[STEP 6] Read Test - SD Card
----------------------------------------------------------------------
[2026-01-15 17:00:03] Reading test file...
[2026-01-15 17:00:03]   ✓ File read: /media/sdcard/tmp/storage_test_1736956803.bin
[2026-01-15 17:00:03]   Size: 1.00MB
[2026-01-15 17:00:03]   Time: 0.08s
[2026-01-15 17:00:03]   Speed: 12.50 MB/s
[2026-01-15 17:00:03]   Checksum: b2e8a1f7d4c93456...
[2026-01-15 17:00:03]   ✓ Checksum match: Data integrity verified
✓ SD card read test passed
  Read speed: 12.50 MB/s
✓ Data integrity verified

[STEP 7] Cleanup
----------------------------------------------------------------------
[2026-01-15 17:00:04]   ✓ Removed: /tmp/storage_test_1736956801.bin
[2026-01-15 17:00:04]   ✓ Removed: /media/sdcard/tmp/storage_test_1736956803.bin
✓ Cleanup complete

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ eMMC detected: True
  ✓ eMMC writable: True
  ✓ eMMC tests passed: 1/1
  ✓ SD card detected: True
  ✓ SD card writable: True
  ✓ SD card tests passed: 1/1
  ✓ Write operations completed without errors
  ✓ Read operations completed without errors
  ✓ Data integrity verified (checksums match)
  ✓ Read/write operations succeed on storage interfaces (PASS)

📄 Test log: /tmp/test_038_storage_readwrite.log
==================================================================

====================== 1 passed in 3.87s ======================
```

### Successful Test Run (eMMC Only, No SD Card)

```
[STEP 1] Detect Storage Devices
----------------------------------------------------------------------
  ✓ eMMC detected: /dev/mmcblk0
  ⚠ SD card not detected
✓ eMMC detected: /dev/mmcblk0

[STEP 2] Find Writable Locations
----------------------------------------------------------------------
✓ eMMC writable location: /tmp
  ⚠ SD card not writable (will skip SD tests)

[STEP 3] Write Test - eMMC
----------------------------------------------------------------------
✓ eMMC write test passed
  Write speed: 12.50 MB/s

[STEP 4] Read Test - eMMC
----------------------------------------------------------------------
✓ eMMC read test passed
  Read speed: 25.00 MB/s
✓ Data integrity verified

[STEP 5 & 6] SD Card Tests - SKIPPED
----------------------------------------------------------------------
  ⚠ SD card not available or not writable

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ eMMC detected: True
  ✓ eMMC writable: True
  ✓ eMMC tests passed: 1/1
  ⚠ SD card not available (optional)
```

### Failed Test (eMMC Not Detected)

```
[STEP 1] Detect Storage Devices
----------------------------------------------------------------------
[2026-01-15 17:00:00]   ✗ eMMC (mmcblk0) not found

FAILED - eMMC device (mmcblk0) not detected

Possible causes:
  - Running on CM4 Lite (no eMMC)
  - eMMC hardware failure
  - Wrong device name in config
  - Available devices:
    NAME    TYPE  SIZE MOUNTPOINT
    sda     disk   32G
    └─sda1  part   32G /
```

### Failed Test (Data Integrity Failure)

```
[STEP 4] Read Test - eMMC
----------------------------------------------------------------------
[2026-01-15 17:00:02]   ✗ Checksum mismatch!
[2026-01-15 17:00:02]     Expected: a7f4d3e9c2b15678...
[2026-01-15 17:00:02]     Got:      f3c8d7a5e1b42901...

FAILED - eMMC data integrity check failed!
  Expected checksum: a7f4d3e9c2b15678...
  Got checksum:      f3c8d7a5e1b42901...
This indicates storage corruption or hardware failure.
```

### Warning (Slow Write Speed)

```
[STEP 3] Write Test - eMMC
----------------------------------------------------------------------
✓ eMMC write test passed
  Write speed: 3.21 MB/s
  ⚠ Warning: Write speed below threshold (5 MB/s)
```

---

## Troubleshooting

### Issue 1: eMMC Not Detected (CM4 Lite)

**Error:**
```
eMMC device (mmcblk0) not detected
Possible causes:
  - Running on CM4 Lite (no eMMC)
```

**Explanation:**
- CM4 Lite models have **no eMMC** (use SD card only)
- This test requires CM4 **with eMMC**

**Solution:**
- Use CM4 with eMMC (not Lite)
- Or modify test to skip eMMC and only test SD card

### Issue 2: Filesystem Read-Only

**Error:**
```
Could not find writable location on eMMC
Possible causes:
  - Filesystem mounted read-only
```

**Check mount status:**
```bash
# Check if filesystem is read-only
mount | grep mmcblk0

# Should show "rw" not "ro"
# Example: /dev/mmcblk0p2 on / type ext4 (rw,relatime)
```

**Solution:**
```bash
# Remount filesystem as read-write
sudo mount -o remount,rw /

# Verify
mount | grep " / "
```

### Issue 3: Disk Full

**Error:**
```
Write failed: [Errno 28] No space left on device
```

**Check free space:**
```bash
# Check disk space
df -h /

# Should have at least 10MB free
```

**Solution:**
```bash
# Free up space
sudo apt clean
sudo rm -rf /tmp/*
sudo journalctl --vacuum-time=1d

# Or increase test file size in config
'test_file_size_mb': 0.1,  # 100KB instead of 1MB
```

### Issue 4: Permission Denied

**Error:**
```
Write failed: [Errno 13] Permission denied
```

**Solution:**
```bash
# Check if /tmp is writable
ls -ld /tmp
# Should show: drwxrwxrwt

# Fix permissions if needed
sudo chmod 1777 /tmp

# Or run test with sudo (not recommended)
sudo pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v
```

### Issue 5: SD Card Not Mounting

**Error:**
```
SD card not writable (will skip SD tests)
```

**Check SD card:**
```bash
# Check if SD card is detected
lsblk | grep mmcblk1

# Check if mounted
mount | grep mmcblk1

# Mount SD card if not mounted
sudo mkdir -p /media/sdcard
sudo mount /dev/mmcblk1p1 /media/sdcard
```

**Auto-mount SD card:**
```bash
# Add to /etc/fstab
echo "/dev/mmcblk1p1  /media/sdcard  vfat  defaults,nofail  0  2" | sudo tee -a /etc/fstab

# Mount all from fstab
sudo mount -a
```

### Issue 6: Data Integrity Failure

**Error:**
```
eMMC data integrity check failed!
Expected checksum: a7f4d3e9c2b15678...
Got checksum:      f3c8d7a5e1b42901...
This indicates storage corruption or hardware failure.
```

**Possible Causes:**
- Storage hardware failure
- Corrupted filesystem
- Bad blocks on storage
- Power instability

**Solutions:**
```bash
# Check filesystem
sudo fsck -n /dev/mmcblk0p2

# Check for bad blocks (DESTRUCTIVE - backup first!)
# sudo badblocks -v /dev/mmcblk0

# Check dmesg for I/O errors
dmesg | grep -i "mmc\|error\|i/o"

# If persistent, storage may be failing - replace hardware
```

### Issue 7: Very Slow Write Speed

**Warning:**
```
Write speed: 1.23 MB/s
⚠ Warning: Write speed below threshold (5 MB/s)
```

**Possible Causes:**
- Old/slow SD card
- Filesystem fragmentation
- High system load
- Failing storage hardware

**Solutions:**
```bash
# Check system load
uptime

# Check I/O wait
iostat -x 1 5

# Test raw device speed
sudo dd if=/dev/zero of=/tmp/test bs=1M count=10 conv=fdatasync
# Should be >> 5 MB/s on healthy storage

# Consider replacing slow SD card with Class 10 or UHS-I
```

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
    # Test data sizes
    'test_file_size_mb': 1,  # Size of test file in MB
    'small_file_size_kb': 100,  # Small file for quick test

    # Device names to check
    'emmc_device': 'mmcblk0',
    'sd_device_names': ['mmcblk1', 'sda'],  # Possible SD names

    # Test file patterns
    'test_file_prefix': 'storage_test_',
    'test_dir_prefix': 'storage_dir_test_',

    # Number of test iterations
    'write_read_cycles': 3,  # Number of write/read cycles

    # Performance thresholds (MB/s)
    'min_write_speed_mb_s': 5,   # Minimum write speed
    'min_read_speed_mb_s': 10,   # Minimum read speed

    # Logging
    'enable_logging': True,
    'log_file': '/tmp/test_038_storage_readwrite.log',
}
```

### Customizing Configuration

Edit the test file to customize:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # Larger test file for stress testing
        'test_file_size_mb': 10,  # 10MB test file

        # Lower thresholds for slow storage
        'min_write_speed_mb_s': 2,
        'min_read_speed_mb_s': 5,

        # Different device names
        'emmc_device': 'mmcblk1',  # If eMMC is on different device
        'sd_device_names': ['sda', 'sdb'],  # USB storage

        # Multiple test cycles
        'write_read_cycles': 5,  # Test 5 times
    }
```

---

## Comparison: Storage-Related Tests

| Aspect | Test #31 | Test #32 | Test #38 |
|--------|----------|----------|----------|
| **Test Name** | eMMC Detection | OS Flashing | Read/Write Operations |
| **Purpose** | Detect eMMC | Flash OS image | Test I/O operations |
| **Destructive** | ❌ No | ✅ **Yes** | ❌ No |
| **Tests SD Card** | ❌ No | ❌ No | ✅ Yes |
| **Data Integrity** | Basic read | Full verify | **Checksum verify** |
| **Performance** | ❌ No | ❌ No | ✅ **Yes (MB/s)** |
| **Automation** | 100% | 60% | **100%** |
| **Duration** | ~2-4 sec | ~10-30 min | ~5-10 sec |
| **CI/CD Ready** | ✅ Yes | ❌ No | ✅ **Yes** |

---

## CI/CD Integration

### ✅ Suitable for CI/CD

Test #38 is **fully automated** and ideal for CI/CD:

```yaml
# GitLab CI example (if runner is on CM4)
test:storage:
  stage: test
  script:
    - pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v
  tags:
    - raspberry-pi-cm4
  only:
    - merge_requests
```

### Using Remote CM4 for CI/CD

```yaml
# Run test on remote CM4 from CI
test:storage:remote:
  stage: test
  script:
    - export PI_IP=192.168.1.100
    - ./scripts/run-unit-test-remote.sh $PI_IP test_038
  tags:
    - linux
  only:
    - merge_requests
```

### Storage Health Monitoring

```bash
# Run test daily to monitor storage health
0 2 * * * cd ~/sensor_test_project && pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v | tee -a /var/log/storage_health.log
```

---

## Test Duration

- **Typical:** 5-10 seconds
- **With SD card:** 8-15 seconds
- **Factors:**
  - Storage speed (eMMC faster than SD)
  - System load
  - File size (configurable)
  - Number of test cycles

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ eMMC device detected
2. ✓ eMMC has writable location
3. ✓ Write operation to eMMC succeeds
4. ✓ Read operation from eMMC succeeds
5. ✓ **Checksums match** (data integrity verified)
6. ✓ No I/O errors during operations

### Test FAILS ✗ if:
- eMMC not detected
- eMMC not writable (read-only, permissions, full)
- Write operation fails
- Read operation fails
- **Checksums don't match** (data corruption)

### Informational Only (Not Failures):
- SD card not detected (optional)
- SD card not writable (optional)
- Write/read speed below threshold (warning only)

---

## Running from WSL2/Laptop

### ❌ Cannot Run Locally on WSL2

This test **must run on CM4** because:
- Test validates CM4's storage hardware
- WSL2 doesn't have CM4's eMMC
- Test checks actual storage I/O

### ✅ Run Remotely on CM4

```bash
# From WSL2/laptop, run test on CM4
export PI_IP=192.168.x.x
./scripts/run-unit-test-remote.sh $PI_IP test_038
```

---

## Related Tests

- **Test #30:** CM4 enumeration on PC (USB boot mode)
- **Test #31:** eMMC detection (normal boot) - Detects eMMC presence
- **Test #32:** OS flashing to eMMC (USB boot mode, **destructive**)
- **Test #33:** Boot verification (normal boot)
- **Test #35:** Internet connectivity (normal boot)
- **Test #36:** SSH accessibility (normal boot)
- **Test #38:** Storage read/write operations ← You are here

---

## Advanced Usage

### Stress Test with Larger Files

```python
# Edit test_config
'test_file_size_mb': 100,  # 100MB test file
'write_read_cycles': 10,   # 10 cycles
```

```bash
# Run stress test
pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v
```

### Monitor Storage Performance Over Time

```bash
# Run test every hour and log performance
while true; do
    pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v \
      | tee -a /var/log/storage_performance.log
    sleep 3600
done
```

### Test Specific Mount Points

```python
# Force specific locations
def get_writable_location(self, device_name, config):
    if 'mmcblk0' in device_name:
        return '/home/pi/test_location'  # Test specific path
    return None
```

### Compare eMMC vs SD Card Performance

```bash
# Run test and extract speeds
pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v -s \
  | grep "speed:" \
  | tee storage_comparison.txt

# Analyze results
grep "eMMC" storage_comparison.txt
grep "SD" storage_comparison.txt
```

---

## Storage Health Best Practices

### Regular Testing
```bash
# Weekly storage health check
0 1 * * 0 cd ~/sensor_test_project && pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v
```

### Performance Baseline
```bash
# Establish baseline performance when storage is new
pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v | tee storage_baseline.txt

# Compare later to detect degradation
```

### Early Warning Signs
Watch for:
- Decreasing write/read speeds over time
- Increasing checksum mismatches
- I/O errors in dmesg
- Filesystem errors

### Data Integrity
- Run this test after any storage-related hardware changes
- Test before deploying to production
- Include in burn-in testing for new devices

---

## Summary

**Test #38** validates storage read/write operations:
- ✅ **Fully automated** (no manual steps)
- ✅ Runs **ON CM4**
- ✅ Tests both eMMC and SD card (if present)
- ✅ **Verifies data integrity** with checksums
- ✅ **Measures performance** (MB/s)
- ✅ Self-cleaning (removes test files)
- ✅ Suitable for **CI/CD**
- ✅ Fast execution (~5-10 seconds)

**Run command:**
```bash
# On CM4:
pytest tests/unit_tests/hw_component/test_038_storage_readwrite.py -v -s

# Remote from laptop:
./scripts/run-unit-test-remote.sh $PI_IP test_038
```

**Prerequisites:**
- CM4 with eMMC (not Lite)
- Booted system
- Filesystems mounted with write permissions
- At least 10MB free space

---

**Test #38 is ready to use and fully automated! 🎉**
