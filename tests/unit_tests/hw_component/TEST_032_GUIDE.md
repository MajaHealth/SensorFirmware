# Test #32 Execution Guide
## OS Flashing to eMMC - Hardware Component Test

---

## Quick Start

```bash
# Set OS image path
export OS_IMAGE_PATH=/path/to/raspberry-pi-os.img

# Run the test (must use sudo)
sudo -E pytest tests/unit_tests/hw_component/test_032_os_flashing_emmc.py -v -s
```

---

## Test Overview

### What This Test Does
Flashes an OS image to the Raspberry Pi CM4's eMMC storage and verifies the flash was successful.

### Test Steps
1. ✓ Verifies prerequisites (OS image, rpiboot, sudo privileges)
2. ✓ Enumerates CM4 eMMC using rpiboot
3. ✓ Flashes OS image to eMMC using dd
4. ✓ Verifies partition table and boot files
5. ✓ Safely syncs and ejects eMMC

### Why This Matters
- Essential for deploying OS to CM4 devices
- Validates eMMC write functionality
- Confirms proper OS installation
- Required before first boot of new CM4

---

## ⚠️ WARNING

**This test will ERASE all data on CM4's eMMC!**

Make sure you:
- Have backed up any important data
- Are flashing to the correct device
- Have confirmed you want to proceed

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 module (with eMMC)
- ✅ CM4 IO Board (or carrier board with USB slave port)
- ✅ USB cable (USB-A to micro-USB or USB-C)
- ✅ PC/Laptop running Linux (Ubuntu/Debian recommended)
- ✅ Power supply for CM4

### Software Required

```bash
# Install rpiboot tool
sudo apt update
sudo apt install rpiboot

# Verify installation
which rpiboot
# Output: /usr/bin/rpiboot
```

### OS Image Required

Download or prepare a Raspberry Pi OS image:

```bash
# Option 1: Download official Raspberry Pi OS
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz

# Extract
xz -d 2024-03-15-raspios-bookworm-arm64-lite.img.xz

# Set environment variable
export OS_IMAGE_PATH=/path/to/2024-03-15-raspios-bookworm-arm64-lite.img

# Option 2: Use custom image
export OS_IMAGE_PATH=/path/to/your-custom-image.img
```

---

## Hardware Setup

### Step 1: Enable USB Boot Mode

**For CM4 with eMMC:**
```
On CM4 IO Board:
1. Locate the "nRPI_BOOT" jumper (J2)
2. Fit the jumper to disable eMMC boot
3. This forces CM4 into USB boot mode

   ┌─────────────────────┐
   │  nRPI_BOOT (J2)     │
   │  ┌───┐ ┌───┐        │
   │  │ █ │=│ █ │ ← Fit jumper here
   │  └───┘ └───┘        │
   └─────────────────────┘
```

### Step 2: Connect CM4 to PC

```
┌─────────────────────────────┐
│         Your PC             │
│                             │
│  USB Port (Host)            │
└──────────┬──────────────────┘
           │
           │ USB Cable
           │
┌──────────▼──────────────────┐
│    CM4 IO Board             │
│                             │
│  USB Slave/Device Port      │ ← Connect here (J11)
│  (micro-USB labeled         │
│   "USB SLAVE")              │
│                             │
│  nRPI_BOOT Jumper           │ ← Must be fitted
│                             │
│  CM4 Module                 │
└─────────────────────────────┘
```

**Important:**
- ⚠️ Use the **USB slave/device port**, NOT the USB host ports
- ⚠️ The jumper "nRPI_BOOT" MUST be fitted
- ⚠️ Do NOT connect to the USB-A ports (those are USB hosts)

### Step 3: Power CM4

```bash
# CM4 IO Board power options:
# - USB power (if J2 jumper allows)
# - 12V DC barrel jack (recommended)

# Ensure CM4 is powered on
# You should see power LED lit
```

---

## Running Test #32

### Method 1: Command Line

```bash
cd /home/kranti/sensor_test_project
source venv/bin/activate

# Set OS image path
export OS_IMAGE_PATH=/path/to/raspberry-pi-os.img

# Run test with sudo (required for dd and mount operations)
sudo -E pytest tests/unit_tests/hw_component/test_032_os_flashing_emmc.py -v -s
```

**Note:** The `-E` flag preserves environment variables (like OS_IMAGE_PATH) when using sudo.

### Method 2: Interactive Prompts

The test will prompt you for confirmation:

```
⚠️  WARNING: This test will ERASE all data on CM4's eMMC!

📋 MANUAL CONFIRMATION REQUIRED:
   1. Is CM4 connected to PC via USB (slave port)?
   2. Is nRPI_BOOT jumper set (USB boot mode)?
   3. Is CM4 powered on?
   4. Are you sure you want to ERASE eMMC and flash new OS?

   Continue with flashing? (yes/no):
```

**What to do:**
1. Verify all hardware is properly connected
2. Type `yes` and press ENTER to proceed
3. Wait for flashing to complete (5-15 minutes depending on image size)

---

## Expected Output

### Successful Test Run

```
======================================================================
Test Case #32: OS Flashing to eMMC
======================================================================

HW Component Test - eMMC Storage
======================================================================

⚠️  WARNING: This test will ERASE all data on CM4's eMMC!
======================================================================

[STEP 0] Verify Prerequisites
----------------------------------------------------------------------
  ✓ OS image found: /path/to/raspberry-pi-os.img
    Size: 2.50 GB
  ✓ rpiboot is installed
  ✓ dd command available
  ✓ Running with sudo privileges
✓ All prerequisites met
  Image size: 2.50 GB

📋 MANUAL CONFIRMATION REQUIRED:
   1. Is CM4 connected to PC via USB (slave port)?
   2. Is nRPI_BOOT jumper set (USB boot mode)?
   3. Is CM4 powered on?
   4. Are you sure you want to ERASE eMMC and flash new OS?

   Continue with flashing? (yes/no): yes

✓ User confirmed - proceeding with flash

[STEP 1] Enumerate CM4 eMMC using rpiboot
----------------------------------------------------------------------
  Running rpiboot (this may take 30-60 seconds)...
  ✓ rpiboot completed successfully
  Waiting for eMMC device /dev/mmcblk0...
  ✓ eMMC device found: /dev/mmcblk0
  Device info:
NAME        SIZE MODEL
mmcblk0     7.3G
✓ CM4 enumerated
✓ eMMC device ready

[STEP 2] Flash OS Image to eMMC
----------------------------------------------------------------------
Starting OS flash to eMMC...
  OS image size: 2.50 GB
  Unmounting any mounted eMMC partitions...
  Flashing raspberry-pi-os.img to /dev/mmcblk0...
  This may take several minutes (5-10 min for 2GB image)...
  Command: dd if=/path/to/raspberry-pi-os.img of=/dev/mmcblk0 bs=4M conv=fsync status=progress
    Flash in progress... 30s elapsed
    Flash in progress... 60s elapsed
    Flash in progress... 90s elapsed
  Flash output:
    2684354560 bytes (2.7 GB, 2.5 GiB) copied, 180 s, 14.9 MB/s
    640+0 records in
    640+0 records out
  ✓ Flash completed in 180s (3.0 min)
✓ Flash successful (3.0 minutes)

[STEP 3] Verify Flashing Completed Successfully
----------------------------------------------------------------------
Verifying flash...
  Checking partition table...
  ✓ Partition table looks correct
    Disk /dev/mmcblk0: 7.3 GiB
    Device         Boot   Start      End  Sectors  Size Id Type
    /dev/mmcblk0p1         8192   532479   524288  256M  c W95 FAT32 (LBA)
    /dev/mmcblk0p2       532480 15523839 14991360  7.1G 83 Linux
  Checking boot partition filesystem...
    Boot partition: /dev/mmcblk0p1: DOS/MBR boot sector
  ✓ Boot partition filesystem verified
  Attempting read-only mount test...
  ✓ Boot partition mounted successfully
    Boot files found: 42
  ✓ Found expected boot files: start4.elf, config.txt, kernel8.img
✓ Flash verification successful
  Boot files: start4.elf, config.txt, kernel8.img

[STEP 4] Sync and Eject eMMC
----------------------------------------------------------------------
Syncing filesystem...
  ✓ Filesystem synced
  Unmounting eMMC partitions...
  ✓ eMMC safely ejected
✓ eMMC ready to be disconnected

======================================================================
TEST RESULT: ✓ PASS
======================================================================

✓ Acceptance Criteria Verification:
  ✓ CM4 eMMC enumerated successfully
  ✓ OS image flashed to eMMC
  ✓ Flash completed in 3.0 minutes
  ✓ Flash verified successfully
  ✓ Partition table correct
  ✓ Boot partition filesystem verified
  ✓ Boot files present
  ✓ eMMC safely ejected

✓ OS successfully flashed to eMMC

📄 Test log: /tmp/test_032_os_flashing.log

💡 Next Steps:
  1. Remove nRPI_BOOT jumper
  2. Disconnect USB cable
  3. Connect CM4 to network/peripherals
  4. Power on CM4 - it will boot from newly flashed OS
======================================================================

====================== 1 passed in 195.34s ======================
```

---

## Troubleshooting

### Issue 1: OS Image Not Found

**Error:**
```
OS image not found: /path/to/raspberry-pi-os.img
```

**Solution:**
```bash
# Check if image exists
ls -la /path/to/your-image.img

# Set correct path
export OS_IMAGE_PATH=/correct/path/to/image.img

# Verify
echo $OS_IMAGE_PATH
```

### Issue 2: Not Running with Sudo

**Error:**
```
Test must be run with sudo privileges (use: sudo -E pytest ...)
```

**Solution:**
```bash
# Run with sudo and preserve environment
sudo -E pytest tests/unit_tests/hw_component/test_032_os_flashing_emmc.py -v -s

# The -E flag is important to preserve OS_IMAGE_PATH
```

### Issue 3: rpiboot Not Installed

**Error:**
```
rpiboot not installed (required for CM4 enumeration)
```

**Solution:**
```bash
# Install from apt
sudo apt update
sudo apt install rpiboot

# Or build from source
git clone https://github.com/raspberrypi/usbboot
cd usbboot
sudo apt install libusb-1.0-0-dev
make
sudo cp rpiboot /usr/local/bin/
```

### Issue 4: eMMC Device Not Found

**Error:**
```
eMMC device not found after 30s
```

**Solutions:**
1. **Check nRPI_BOOT jumper** - Must be fitted
2. **Check USB connection** - Use slave port, not host
3. **Check power** - CM4 must be powered
4. **Run rpiboot manually:**
   ```bash
   sudo rpiboot
   lsblk | grep mmcblk
   ```

### Issue 5: Flash Timeout

**Error:**
```
Flash timeout after 600s
```

**Solutions:**
1. **Large image** - Increase timeout in test_config
2. **Slow USB** - Use USB 3.0 port if available
3. **Check USB cable** - Use quality data cable

### Issue 6: Verification Failed

**Error:**
```
Flash verification failed: Expected partitions not found
```

**Solutions:**
1. **Check image file** - Ensure it's a valid disk image
2. **Check image integrity** - Verify checksum
3. **Re-flash** - Run test again
4. **Check eMMC health** - May be failing

### Issue 7: Permission Denied During Mount

**Error:**
```
Failed to mount boot partition: Permission denied
```

**Solution:**
```bash
# Ensure running with sudo
sudo -E pytest ...

# Check if device is in use
lsof /dev/mmcblk0*

# Unmount manually if needed
sudo umount /dev/mmcblk0*
```

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
    'os_image_path': os.getenv('OS_IMAGE_PATH', '/path/to/raspberry-pi-os.img'),
    'emmc_device': '/dev/mmcblk0',
    'rpiboot_timeout': 60,         # Seconds for rpiboot
    'flash_timeout': 600,          # 10 minutes for flashing
    'verify_checksum': False,      # Set True for checksum verification
    'enable_logging': True,
    'log_file': '/tmp/test_032_os_flashing.log',
}
```

### Customizing Configuration

Edit the test file to change settings:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        'os_image_path': '/custom/path/to/image.img',
        'emmc_device': '/dev/mmcblk0',
        'rpiboot_timeout': 120,    # More time for rpiboot
        'flash_timeout': 1200,     # 20 minutes for large images
        'verify_checksum': True,   # Enable checksum verification
    }
```

---

## Manual Flashing (Without pytest)

If you want to flash manually:

```bash
# 1. Run rpiboot to enumerate eMMC
sudo rpiboot

# 2. Wait for device to appear
watch -n 1 lsblk

# 3. Flash with dd
sudo dd if=/path/to/image.img of=/dev/mmcblk0 bs=4M conv=fsync status=progress

# 4. Sync and eject
sudo sync
sudo eject /dev/mmcblk0

# 5. Remove jumper and boot
```

---

## Test Duration

- **Typical:** 3-10 minutes (depends on image size)
- **Breakdown:**
  - Prerequisites: ~5 seconds
  - rpiboot: ~30-60 seconds
  - Flashing: 2-10 minutes (14-15 MB/s typical)
  - Verification: ~30 seconds
  - Sync/Eject: ~5 seconds

**Approximate times by image size:**
| Image Size | Flash Time |
|------------|------------|
| 1 GB       | ~1.5 min   |
| 2 GB       | ~3 min     |
| 4 GB       | ~5-6 min   |
| 8 GB       | ~10 min    |

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ OS image file exists and is accessible
2. ✓ rpiboot is installed
3. ✓ Running with sudo privileges
4. ✓ CM4 eMMC enumerated via rpiboot
5. ✓ dd flash completes without errors
6. ✓ Partition table is correct
7. ✓ Boot partition contains expected files
8. ✓ Filesystem safely synced and ejected

### Test FAILS ✗ if:
- OS image not found
- rpiboot not installed
- Not running with sudo
- eMMC not detected
- Flash command fails
- Verification fails

---

## Post-Flash Steps

After successful test:

1. **Remove nRPI_BOOT jumper** - Allow boot from eMMC
2. **Disconnect USB cable** - Remove from PC
3. **Connect peripherals** - HDMI, keyboard, network
4. **Power on CM4** - Will boot from newly flashed OS
5. **First boot setup** - Configure OS as needed

---

## CI/CD Integration

### Not Recommended for CI/CD

This test requires:
- Physical hardware connection
- Manual confirmation (destructive operation)
- Sudo privileges
- Long execution time

**Use case:** Manual hardware provisioning during:
- CM4 manufacturing/QA
- Initial device setup
- OS deployment
- Factory provisioning

---

## Related Tests

- **Test #30:** CM4 enumeration on PC
- **Test #31:** eMMC detection
- **Test #33:** Boot verification
- **Test #38:** Storage read/write

---

## Summary

**Test #32** flashes OS to CM4 eMMC:
- ✅ Essential for CM4 provisioning
- ✅ Validates eMMC write capability
- ✅ Confirms OS installation
- ✅ Includes verification steps
- ✅ Manual test (requires confirmation)
- ⚠️ DESTRUCTIVE - erases eMMC

**Run command:**
```bash
export OS_IMAGE_PATH=/path/to/image.img
sudo -E pytest tests/unit_tests/hw_component/test_032_os_flashing_emmc.py -v -s
```

**Prerequisites:**
- CM4 with eMMC
- rpiboot installed
- OS image file
- USB connection to PC
- CM4 in USB boot mode
- Sudo privileges

---

## References

- [Raspberry Pi CM4 Flashing](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc)
- [rpiboot GitHub](https://github.com/raspberrypi/usbboot)
- [CM4 IO Board Schematic](https://datasheets.raspberrypi.com/cm4io/cm4io-datasheet.pdf)
- [Raspberry Pi OS Downloads](https://www.raspberrypi.com/software/operating-systems/)
