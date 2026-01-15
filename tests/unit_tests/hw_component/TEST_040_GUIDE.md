# Test #40 Execution Guide
## Power Cycling (Retention) - Hardware Component Test

---

## Quick Start

```bash
# SSH into CM4
ssh pi@192.168.x.x

# Navigate to project
cd ~/sensor_test_project
source venv/bin/activate

# Run Test #40 (Phase 1 - will reboot)
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

# After system reboots, SSH back in and run again (Phase 2)
ssh pi@192.168.x.x
cd ~/sensor_test_project
source venv/bin/activate
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

# Repeat until test completes (default: 3 power cycles)
```

---

## Test Overview

### What This Test Does
Validates that storage maintains data integrity across power cycles (system reboots), ensuring data persists reliably through unexpected power loss or intentional reboots.

### Unique Characteristics
**This test is DIFFERENT from all other tests:**
- ✅ **Multi-phase execution**: Runs across multiple test invocations
- ✅ **Requires reboots**: System must reboot between phases
- ✅ **State-based**: Maintains state across reboots via JSON file
- ⏱️ **Longer duration**: Minutes (includes reboot time)
- 🔄 **Multiple cycles**: Tests 3 power cycles by default

### Test Phases

**Phase 1: Write and Reboot**
1. Write test data to eMMC and SD card
2. Calculate and save checksums
3. Save state to persistent file
4. Sync filesystem
5. Reboot system

**Phase 2: Verify After Reboot** (runs after each reboot)
1. Load previous state
2. Verify test files still exist
3. Read data from storage
4. Verify checksums match
5. Either reboot again (more cycles needed) or complete test

### Why This Matters
- Tests **real-world scenarios** (power outages, crashes)
- Validates **data durability** (not just cache writes)
- Detects **fake storage** (claims capacity but doesn't persist)
- Ensures **production reliability** (data survives unexpected power loss)
- Critical for **firmware storage** and **logging systems**

---

## Automation Level

### ⚠️ **Semi-Automated** (Requires Manual Reboots)

Test #40 is semi-automated:

```
Manual steps required:
⚠️ Must SSH back in after each reboot
⚠️ Must re-run test after each reboot
⚠️ Repeat until test completes (3 reboots default)

Automated aspects:
✓ Data writing
✓ Checksum calculation
✓ Verification
✓ State management
✓ Reboot triggering
```

**For full automation**, set up:
- Systemd service to auto-run test after boot
- Or CI/CD runner on CM4 with auto-reboot capability

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 (any variant)
- ✅ CM4 IO Board or carrier board
- ✅ **Reliable power supply** (critical for power cycle testing!)
- ✅ **CM4 with eMMC** (not CM4 Lite)
- ✅ SD card (optional, for SD card tests)

### Software Required
- ✅ Operating system installed and booted on CM4
- ✅ pytest installed on CM4
- ✅ SSH access to CM4
- ✅ **sudo privileges** (for reboot command)
- ✅ Sufficient free space (~50MB)

### Critical Requirements
- ✅ **Stable power supply**: Don't test with unstable power!
- ✅ **SSH access**: Need to reconnect after each reboot
- ✅ **Time availability**: Test takes several minutes (includes reboot time)

---

## Running Test #40

### Method 1: Manual Execution (Recommended First Time)

```bash
# SSH into CM4
ssh pi@192.168.x.x
cd ~/sensor_test_project
source venv/bin/activate

# Run Phase 1 (will write data and reboot)
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

# System will reboot after 10-second warning
# Wait for system to come back online (~30-60 seconds)

# SSH back in
ssh pi@192.168.x.x
cd ~/sensor_test_project
source venv/bin/activate

# Run Phase 2 (will verify and reboot again if more cycles needed)
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

# Repeat until test completes (3 cycles total)
```

### Method 2: Automated Script

```bash
# Create auto-run script
cat > run_power_cycle_test.sh << 'EOF'
#!/bin/bash
PI_IP=$1
MAX_ATTEMPTS=10

for i in $(seq 1 $MAX_ATTEMPTS); do
    echo "Attempt $i/$MAX_ATTEMPTS..."

    ssh pi@$PI_IP "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s"

    # Check if test completed
    if ssh pi@$PI_IP "[ ! -f /var/tmp/test_040_power_cycle_state.json ]"; then
        echo "Test completed!"
        break
    fi

    # Wait for reboot
    echo "Waiting for reboot..."
    sleep 60

    # Wait for system to come back
    while ! ping -c 1 $PI_IP &> /dev/null; do
        sleep 5
    done
    sleep 10  # Extra time for SSH
done
EOF

chmod +x run_power_cycle_test.sh

# Run automated test
./run_power_cycle_test.sh 192.168.x.x
```

### Method 3: Systemd Service (Full Automation)

```bash
# Create systemd service on CM4
sudo tee /etc/systemd/system/power-cycle-test.service << 'EOF'
[Unit]
Description=Power Cycle Test Auto-Runner
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/sensor_test_project
ExecStart=/bin/bash -c 'source venv/bin/activate && pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl enable power-cycle-test.service

# Run initial test (will auto-continue after reboots)
cd ~/sensor_test_project
source venv/bin/activate
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

# Check status after boot
sudo systemctl status power-cycle-test.service

# Disable after test completes
sudo systemctl disable power-cycle-test.service
```

---

## Expected Output

### Phase 1 Output (Before Reboot)

```
==================================================================
Test Case #40: Power Cycling (Retention)
==================================================================

HW Component Test - Storage Data Retention
==================================================================

TEST METHOD:
  Phase 1: Write test data → Reboot system
  Phase 2: Verify data survived reboot → Repeat if needed
==================================================================

[STEP 1] Determine Test Phase
----------------------------------------------------------------------
✓ No previous state found
  → This is PHASE 1: Write data and initiate reboot

==================================================================
PHASE 1: Write Test Data and Reboot
==================================================================

[STEP 2] Detect Storage and Write Test Data
----------------------------------------------------------------------

eMMC Test File:
[2026-01-15 19:00:00] Writing 10MB test file to /tmp/retention_test_emmc.bin...
[2026-01-15 19:00:00]   ✓ File written: 10,485,760 bytes
[2026-01-15 19:00:00]   Checksum: a7f4d3e9c2b15678...

SD Card Test File:
[2026-01-15 19:00:01] Writing 10MB test file to /media/sdcard/retention_test_sd.bin...
[2026-01-15 19:00:01]   ✓ File written: 10,485,760 bytes
[2026-01-15 19:00:01]   Checksum: b2e8a1f7d4c93456...

[STEP 3] Save Test State
----------------------------------------------------------------------
[2026-01-15 19:00:01] ✓ Test state saved to: /var/tmp/test_040_power_cycle_state.json

[STEP 4] Initiate System Reboot
----------------------------------------------------------------------

==================================================================
⚠️  REBOOT REQUIRED
==================================================================

This test requires a system reboot to verify data retention.
System will reboot in 10 seconds.

After reboot, run this test again to complete verification:
  pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

Press Ctrl+C to cancel reboot...
==================================================================

Rebooting in 10 seconds...
Rebooting in 9 seconds...
...
Syncing filesystem...
✓ Filesystem synced

🔄 Initiating system reboot...

[SSH connection lost - system rebooting]
```

### Phase 2 Output (After Reboot - Cycle 1)

```
==================================================================
Test Case #40: Power Cycling (Retention)
==================================================================

HW Component Test - Storage Data Retention
==================================================================

TEST METHOD:
  Phase 1: Write test data → Reboot system
  Phase 2: Verify data survived reboot → Repeat if needed
==================================================================

[STEP 1] Determine Test Phase
----------------------------------------------------------------------
✓ Previous state found
  Test started: Mon Jan 15 19:00:00 2026
  Power cycles completed: 0
  → This is PHASE 2: Verify data retention

==================================================================
PHASE 2: Verify Data Retention After Reboot
==================================================================

Power Cycle: 1/3
Test Duration: 127.3 seconds

[STEP 2] Verify eMMC Data Retention
----------------------------------------------------------------------
[2026-01-15 19:02:07] Verifying test file: /tmp/retention_test_emmc.bin
[2026-01-15 19:02:07]   ✓ File exists
[2026-01-15 19:02:07]   ✓ File read: 10,485,760 bytes
[2026-01-15 19:02:07]   Expected: a7f4d3e9c2b15678...
[2026-01-15 19:02:07]   Actual:   a7f4d3e9c2b15678...
[2026-01-15 19:02:07]   ✓ Checksum match: Data integrity verified
✓ eMMC data retention verified (cycle 1/3)

[STEP 3] Verify SD Card Data Retention
----------------------------------------------------------------------
[2026-01-15 19:02:08] Verifying test file: /media/sdcard/retention_test_sd.bin
[2026-01-15 19:02:08]   ✓ File exists
[2026-01-15 19:02:08]   ✓ File read: 10,485,760 bytes
[2026-01-15 19:02:08]   Expected: b2e8a1f7d4c93456...
[2026-01-15 19:02:08]   Actual:   b2e8a1f7d4c93456...
[2026-01-15 19:02:08]   ✓ Checksum match: Data integrity verified
✓ SD card data retention verified (cycle 1/3)

[STEP 4] Check Power Cycle Progress
----------------------------------------------------------------------
✓ Cycle 1/3 complete
  → Initiating cycle 2/3

==================================================================
⚠️  REBOOT REQUIRED
==================================================================

[Reboot warning and countdown...]

[SSH connection lost - system rebooting again]
```

### Final Phase Output (After Cycle 3)

```
[STEP 4] Check Power Cycle Progress
----------------------------------------------------------------------
✓ All 3 power cycles complete
  → Test successful!

[STEP 5] Cleanup
----------------------------------------------------------------------
[2026-01-15 19:08:45] Cleaning up test files...
[2026-01-15 19:08:45]   ✓ Removed eMMC test file
[2026-01-15 19:08:45]   ✓ Removed SD test file
[2026-01-15 19:08:45]   ✓ Removed state file

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ Test completed 3 power cycle(s)
  ✓ eMMC data retained across all 3 power cycle(s)
  ✓ eMMC data integrity verified (no corruption)
  ✓ SD card data retained across all 3 power cycle(s)
  ✓ SD card data integrity verified (no corruption)
  ✓ Storage retains data correctly across power cycles (PASS)

Test Duration: 385.7 seconds (~6.4 minutes)

📄 Test log: /var/tmp/test_040_power_cycling.log
==================================================================

====================== 1 passed in 6.43 minutes ======================
```

### Failed Test (Data Loss After Reboot)

```
[STEP 2] Verify eMMC Data Retention
----------------------------------------------------------------------
[2026-01-15 19:02:07] Verifying test file: /tmp/retention_test_emmc.bin
[2026-01-15 19:02:07]   ✗ File not found: /tmp/retention_test_emmc.bin

FAILED - eMMC data retention FAILED after power cycle 1!
Error: File not found
This indicates:
  - Storage did not persist data
  - Data corruption occurred
  - Storage device failure
```

### Failed Test (Data Corruption After Reboot)

```
[STEP 2] Verify eMMC Data Retention
----------------------------------------------------------------------
[2026-01-15 19:02:07] Verifying test file: /tmp/retention_test_emmc.bin
[2026-01-15 19:02:07]   ✓ File exists
[2026-01-15 19:02:07]   ✓ File read: 10,485,760 bytes
[2026-01-15 19:02:07]   Expected: a7f4d3e9c2b15678...
[2026-01-15 19:02:07]   Actual:   7f3c9d2e1a584b7f...
[2026-01-15 19:02:07]   ✗ Checksum mismatch: Data corruption detected!

FAILED - eMMC data retention FAILED after power cycle 1!
Error: Checksum mismatch
This indicates:
  - Storage did not persist data
  - Data corruption occurred
  - Storage device failure
```

---

## Troubleshooting

### Issue 1: Cannot Reboot (Permission Denied)

**Error:**
```
[Errno 13] Permission denied: 'reboot'
```

**Cause:**
User doesn't have sudo privileges.

**Solution:**
```bash
# Add user to sudo group
sudo usermod -aG sudo pi

# Or allow reboot without password
echo "pi ALL=(ALL) NOPASSWD: /sbin/reboot" | sudo tee /etc/sudoers.d/reboot-nopasswd

# Test
sudo reboot
```

### Issue 2: State File Not Found After Reboot

**Error:**
```
No previous state found (but there should be)
```

**Possible Causes:**
- State file stored in `/tmp` (cleared on reboot)
- Filesystem not synced before reboot

**Solution:**
```bash
# Ensure state file is in persistent location
# Default: /var/tmp (persists across reboots)
# Check if file exists
ls -la /var/tmp/test_040_power_cycle_state.json

# If using /tmp, change to /var/tmp in test
STATE_FILE = '/var/tmp/test_040_power_cycle_state.json'
```

### Issue 3: Test Files Deleted After Reboot

**Error:**
```
File not found: /tmp/retention_test_emmc.bin
```

**Cause:**
Test file stored in `/tmp` which may be cleared on reboot depending on system configuration.

**Solution:**
```python
# Edit test_config to use persistent location
'emmc_test_dir': '/var/tmp',  # Instead of '/tmp'
```

Or ensure `/tmp` persists:
```bash
# Check if /tmp is tmpfs
mount | grep /tmp

# If tmpfs, test files will be lost on reboot (expected for /tmp)
# Use /var/tmp instead
```

### Issue 4: Reboot Cancelled (Ctrl+C)

**Message:**
```
⚠️  Reboot cancelled by user
To complete test:
  1. Manually reboot the system
  2. Run this test again after reboot
```

**Solution:**
```bash
# Manually reboot
sudo reboot

# After reboot, SSH back in and continue test
ssh pi@192.168.x.x
cd ~/sensor_test_project
source venv/bin/activate
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s
```

### Issue 5: Stuck in Power Cycle Loop

**Problem:**
Test keeps rebooting forever.

**Cause:**
State file not being cleaned up.

**Solution:**
```bash
# Check state file
cat /var/tmp/test_040_power_cycle_state.json

# Manually delete state file to stop test
sudo rm /var/tmp/test_040_power_cycle_state.json

# Or complete the test normally
```

### Issue 6: Intermittent Failures

**Problem:**
Test passes sometimes, fails other times.

**Possible Causes:**
- Power supply instability during reboot
- Filesystem not syncing properly
- Marginal storage hardware

**Solutions:**
```bash
# Check power supply voltage
vcgencmd measure_volts

# Check dmesg for errors after reboot
dmesg | grep -i "error\|fail\|mmc"

# Run extended test
# Edit test_config:
'target_power_cycles': 10,  # More cycles
```

---

## Test Configuration

### Default Configuration

```python
{
    # Test data configuration
    'test_file_size_mb': 10,  # Size of test files

    # Power cycle configuration
    'target_power_cycles': 3,  # Number of power cycles to test
    'auto_reboot': False,      # Set True for automated testing

    # Storage locations
    'emmc_test_dir': '/tmp',
    'emmc_test_file': 'retention_test_emmc.bin',

    # Device names
    'emmc_device': 'mmcblk0',
    'sd_device_names': ['mmcblk1', 'sda'],

    # Reboot delay
    'reboot_warning_seconds': 10,  # Warning before reboot

    # Logging
    'enable_logging': True,
    'log_file': '/var/tmp/test_040_power_cycling.log',
}
```

### Customizing Configuration

**Quick Test (Fewer Cycles)**:
```python
'target_power_cycles': 1,  # Only 1 reboot
'reboot_warning_seconds': 3,  # Shorter warning
```

**Stress Test (Many Cycles)**:
```python
'target_power_cycles': 10,  # 10 reboots
'test_file_size_mb': 50,  # Larger files
```

**Persistent Storage**:
```python
'emmc_test_dir': '/var/tmp',  # Survives /tmp clearing
```

---

## Comparison: Storage Tests

| Aspect | Test #38 | Test #39 | Test #40 |
|--------|----------|----------|----------|
| **Focus** | Basic I/O | Integrity | **Power Cycle Retention** |
| **Reboots** | ❌ No | ❌ No | ✅ **Yes (3x)** |
| **Multi-Phase** | ❌ No | ❌ No | ✅ **Yes** |
| **State-Based** | ❌ No | ❌ No | ✅ **Yes** |
| **Duration** | ~5-10 sec | ~30-60 sec | **~5-10 min** (with reboots) |
| **Automation** | 100% | 100% | **Semi (manual SSH)** |
| **Best For** | Quick test | Thorough test | **Production validation** |

---

## Test Duration

- **Per cycle**: ~60-90 seconds (30s test + 30-60s reboot)
- **Default (3 cycles)**: ~5-10 minutes total
- **Extended (10 cycles)**: ~15-30 minutes total

**Factors:**
- Reboot time (30-60 seconds typically)
- File size (larger = longer write/read)
- Number of cycles
- SSH reconnection time

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ All test files written successfully (Phase 1)
2. ✓ System reboots successfully
3. ✓ **All test files exist after each reboot**
4. ✓ **All checksums match after each reboot**
5. ✓ Completes all target power cycles
6. ✓ No data loss or corruption

### Test FAILS ✗ if:
- Test file missing after any reboot (data loss)
- Checksum mismatch after any reboot (corruption)
- System fails to reboot
- Cannot write initial test data

---

## Use Cases

### 1. Production Qualification
```bash
# Before deploying devices to field
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s
```

### 2. Storage Validation
```bash
# Test new storage batch
# Edit: 'target_power_cycles': 10
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s
```

### 3. Power Supply Testing
```bash
# Test with different power supplies
# Run test with each supply
```

### 4. Firmware Update Validation
```bash
# After firmware updates that affect storage
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s
```

---

## Advanced Usage

### Monitor Test Progress

```bash
# Check state file during test
cat /var/tmp/test_040_power_cycle_state.json | jq

# Check log file
tail -f /var/tmp/test_040_power_cycling.log
```

### Automated Test Loop

```bash
# Run test automatically until completion
while ssh pi@$PI_IP "[ -f /var/tmp/test_040_power_cycle_state.json ]" || [ $FIRST_RUN -eq 1 ]; do
    FIRST_RUN=0
    echo "Running power cycle test..."
    ssh pi@$PI_IP "cd ~/sensor_test_project && source venv/bin/activate && pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v"
    echo "Waiting for system..."
    sleep 90
done
echo "Test complete!"
```

---

## Summary

**Test #40** validates power cycle data retention:
- ✅ **Multi-phase execution** (spans reboots)
- ✅ **State-based approach** (persists across reboots)
- ✅ Tests **real-world power loss** scenarios
- ✅ Validates **data durability**
- ✅ Cryptographic verification (SHA256)
- ⚠️ **Semi-automated** (requires manual SSH between reboots)
- ⏱️ **Longer duration** (~5-10 minutes with 3 cycles)

**When to use:**
- Production qualification
- Storage validation
- Power supply testing
- Before field deployment

**Run command:**
```bash
# On CM4 (Phase 1):
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s

# After reboot (Phase 2 - repeat until test completes):
pytest tests/unit_tests/hw_component/test_040_power_cycling_retention.py -v -s
```

**Prerequisites:**
- CM4 with eMMC
- Reliable power supply
- sudo privileges
- SSH access
- ~5-10 minutes for full test

---

**Test #40 validates production-grade storage reliability! 🎉**
