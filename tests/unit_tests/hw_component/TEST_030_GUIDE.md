# Test #30 Execution Guide
## CM4 Enumeration on PC - Hardware Component Test

---

## Quick Start

```bash
# Install rpiboot (one-time)
sudo apt install rpiboot

# Run the test
pytest tests/unit_tests/hw_component/test_030_cm4_enumeration.py -v -s
```

---

## Test Overview

### What This Test Does
Verifies that the Raspberry Pi CM4 can be successfully enumerated when connected to a PC via USB.

### Test Steps
1. ✓ Checks if `rpiboot` is installed
2. ✓ Detects CM4 as USB device
3. ✓ Runs `rpiboot` to enumerate CM4
4. ✓ Verifies CM4 storage appears as block device

### Why This Matters
- Validates CM4 hardware functionality
- Tests USB boot capability
- Confirms storage accessibility
- Essential for flashing firmware or OS images

---

## Prerequisites

### Hardware Required
- ✅ Raspberry Pi CM4 module
- ✅ CM4 IO Board (or carrier board with USB slave port)
- ✅ USB cable (USB-A to micro-USB or USB-C, depending on board)
- ✅ PC/Laptop running Linux (Ubuntu/Debian recommended)

### Software Required

```bash
# Install rpiboot tool
sudo apt update
sudo apt install rpiboot

# Verify installation
which rpiboot
# Output: /usr/bin/rpiboot

rpiboot --version
# Or just run: rpiboot --help
```

### Alternative Installation (if not in apt)

```bash
# Clone rpiboot from GitHub
git clone --depth=1 https://github.com/raspberrypi/usbboot
cd usbboot
sudo apt install libusb-1.0-0-dev
make
sudo cp rpiboot /usr/local/bin/
```

---

## Hardware Setup

### Step 1: Prepare CM4

**Option A: CM4 with eMMC**
```
1. Disable eMMC boot:
   - On CM4 IO Board: Set "nRPI_BOOT" jumper
   - This forces USB boot mode

2. Or use rpiboot to disable eMMC boot:
   sudo rpiboot -d boot_cm4
```

**Option B: CM4 Lite (without eMMC)**
```
1. No special setup needed
2. CM4 Lite boots to USB by default (no eMMC present)
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
│  USB Slave/Device Port      │ ← Connect here
│  (Usually micro-USB)        │
│                             │
│  CM4 Module                 │
└─────────────────────────────┘
```

**Important:**
- ⚠️ Use the **USB slave/device port**, NOT the USB host ports
- ⚠️ On CM4 IO Board, this is usually the micro-USB port labeled "J11" or "USB SLAVE"
- ⚠️ Do NOT connect to the USB-A ports (those are USB hosts)

### Step 3: Power CM4

```bash
# CM4 IO Board usually has:
# - Power from USB (if J2 jumper set)
# - Or 12V DC barrel jack

# Ensure CM4 is powered on
# You should see power LED lit
```

---

## Running Test #30

### Method 1: Local Execution (if you have CM4 connected to your PC)

```bash
cd /home/kranti/sensor_test_project
source venv/bin/activate

# Run the test
pytest tests/unit_tests/hw_component/test_030_cm4_enumeration.py -v -s
```

### Method 2: Interactive Steps

The test will prompt you:

```
📋 MANUAL ACTIONS REQUIRED:
   1. Connect CM4 to PC via USB (slave/device port)
   2. Ensure CM4 is in USB boot mode
   3. Power on CM4

   The test will wait up to 30 seconds for USB detection...

   Have you completed the setup? (yes/no):
```

**What to do:**
1. Complete the hardware setup (connect CM4)
2. Type `yes` and press ENTER
3. Test will automatically detect and enumerate CM4

---

## Expected Output

### Successful Test Run

```
==================================================================
Test Case #30: CM4 Enumeration on PC
==================================================================

HW Component Test - CM4
==================================================================

[STEP 1] Verify Prerequisites
----------------------------------------------------------------------
✓ rpiboot is installed

[STEP 2] Manual Setup Required
----------------------------------------------------------------------

📋 MANUAL ACTIONS REQUIRED:
   1. Connect CM4 to PC via USB (slave/device port)
   2. Ensure CM4 is in USB boot mode
   3. Power on CM4

   The test will wait up to 30 seconds for USB detection...

   Have you completed the setup? (yes/no): yes

✓ Manual setup confirmed

[STEP 3] Detect CM4 USB Device
----------------------------------------------------------------------
[2026-01-14 18:30:00] Waiting for CM4 USB device...
✓ CM4 USB device detected: 0a5c:2711

[STEP 4] Run rpiboot
----------------------------------------------------------------------
[2026-01-14 18:30:05] Running rpiboot...
✓ rpiboot completed successfully

rpiboot output:
Waiting for BCM2835/6/7/2711...
Loading embedded: bootcode4.bin
Sending bootcode.bin
Successful read 4 bytes
Waiting for BCM2835/6/7/2711...
Loading embedded: bootcode4.bin
Second stage boot server
... (more output)

[STEP 5] Verify Storage Enumeration
----------------------------------------------------------------------
[2026-01-14 18:30:08] Checking for enumerated storage...
✓ CM4 storage enumerated: mmcblk (eMMC)

Detected block devices:
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda      8:0    0 238.5G  0 disk
└─sda1   8:1    0 238.5G  0 part /
mmcblk0 179:0   0   7.3G  0 disk  ← CM4 eMMC!

==================================================================
TEST RESULT: ✓ PASS
==================================================================

✓ Acceptance Criteria Verification:
  ✓ CM4 detected as USB device
  ✓ rpiboot enumeration successful
  ✓ CM4 storage enumerated as block device
  ✓ CM4 enumerated successfully on PC as expected

📄 Test log: /tmp/test_030_cm4_enumeration.log
==================================================================

====================== 1 passed in 15.34s ======================
```

---

## Troubleshooting

### Issue 1: rpiboot Not Installed

**Error:**
```
rpiboot not installed. Install with: sudo apt install rpiboot
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

### Issue 2: CM4 USB Device Not Detected

**Error:**
```
CM4 USB device not detected after 30s
Ensure CM4 is:
  - Connected via USB
  - In USB boot mode
  - Powered on
```

**Check:**
```bash
# Monitor USB devices
watch -n 1 lsusb

# When CM4 connects, you should see:
# Bus 001 Device 005: ID 0a5c:2711 Broadcom Corp. BCM2711 Boot
```

**Solutions:**
1. **Check USB cable** - Try a different cable
2. **Check USB port** - Try different USB port on PC
3. **Check nRPI_BOOT jumper** - Must be fitted to disable eMMC boot
4. **Check power** - Ensure CM4 is powered on (LED lit)
5. **Check USB port on CM4** - Use slave/device port, not host port

### Issue 3: Permission Denied

**Error:**
```
rpiboot failed: Permission denied
```

**Solution:**
```bash
# Run rpiboot with sudo
sudo rpiboot

# Or add udev rules (permanent solution)
sudo nano /etc/udev/rules.d/99-rpiboot.rules

# Add this line:
SUBSYSTEM=="usb", ATTR{idVendor}=="0a5c", ATTR{idProduct}=="2711", MODE="0666"

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Issue 4: rpiboot Timeout

**Error:**
```
rpiboot timed out
```

**Solutions:**
1. **Reset CM4** - Power cycle the CM4
2. **Check boot mode** - Ensure nRPI_BOOT jumper is set
3. **Update rpiboot** - Get latest version from GitHub
4. **Check USB cable quality** - Data lines must work (not charge-only cable)

### Issue 5: Storage Not Enumerated

**Error:**
```
CM4 storage not enumerated
Expected to find mmcblk* or sd* device
```

**Check:**
```bash
# List all block devices
lsblk -a

# Check kernel messages
dmesg | tail -50

# Check for USB mass storage
lsusb -t
```

**Solutions:**
1. **Wait longer** - Some systems take 5-10 seconds
2. **Check dmesg** - Look for error messages
3. **CM4 Lite** - Has no eMMC, so no storage expected
4. **Run rpiboot again** - Sometimes needs second attempt

### Issue 6: Test on WSL2

**Problem:** WSL2 doesn't have direct USB access

**Solution:** Run test on native Linux, or use WSL2 with USB passthrough:

```bash
# Install usbipd on Windows
winget install usbipd

# In PowerShell (as Administrator):
usbipd list
usbipd bind --busid <busid>
usbipd attach --wsl --busid <busid>

# Now run test in WSL2
```

---

## Test Configuration

### Default Configuration

Located in `test_config` fixture:

```python
{
    'usb_detection_timeout': 30,      # Seconds to wait for USB
    'rpiboot_timeout': 60,            # Seconds for rpiboot
    'storage_wait_time': 3,           # Seconds to wait for storage
    'expected_vendor_ids': ['0a5c:2711', 'Broadcom'],
    'log_file': '/tmp/test_030_cm4_enumeration.log',
}
```

### Customizing Configuration

Edit the test file to change timeouts:

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        'usb_detection_timeout': 60,  # Longer timeout
        'rpiboot_timeout': 120,       # More time for rpiboot
        'storage_wait_time': 5,       # Wait longer for storage
    }
```

---

## Manual Testing (Without pytest)

If you want to test CM4 enumeration manually:

```bash
# 1. Check if CM4 is detected
lsusb | grep -i broadcom

# 2. Run rpiboot
sudo rpiboot

# 3. Check for storage
lsblk | grep -E "mmcblk|sd"

# 4. If successful, you should see CM4 storage device
```

---

## CI/CD Integration

### Not Recommended for CI/CD

This test requires **physical hardware connection** and **manual setup**, so it's not suitable for automated CI/CD pipelines.

**Use case:** Manual hardware validation during:
- CM4 manufacturing/QA
- Hardware bring-up
- Board testing
- Pre-deployment validation

---

## Related Tests

- **Test #105:** Soft shutdown ACK accepted
- **Test #106:** Soft shutdown denied/timeout
- **Test #107:** Hard shutdown (if exists)

These tests validate CM4 **firmware behavior**, while Test #30 validates CM4 **hardware functionality**.

---

## Test Duration

- **Typical:** 10-20 seconds
- **With delays:** 30-60 seconds
- **Includes:** USB detection, rpiboot execution, storage enumeration

---

## Success Criteria

### Test PASSES ✓ if:
1. ✓ rpiboot is installed
2. ✓ CM4 detected as USB device (0a5c:2711)
3. ✓ rpiboot completes without errors
4. ✓ CM4 storage appears as block device (mmcblk* or sd*)

### Test FAILS ✗ if:
- rpiboot not installed
- CM4 USB device not detected
- rpiboot fails or times out
- No storage device enumerated

---

## Summary

**Test #30** validates CM4 hardware enumeration on PC:
- ✅ Essential for firmware flashing workflows
- ✅ Confirms CM4 USB boot capability
- ✅ Verifies storage accessibility
- ✅ Requires physical hardware setup
- ✅ Manual test (not for CI/CD)

**Run command:**
```bash
pytest tests/unit_tests/hw_component/test_030_cm4_enumeration.py -v -s
```

**Prerequisites:**
- CM4 hardware
- rpiboot installed
- USB connection to PC
- CM4 in USB boot mode

---

## References

- [Raspberry Pi USB Boot](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc)
- [rpiboot GitHub](https://github.com/raspberrypi/usbboot)
- [CM4 IO Board Schematic](https://datasheets.raspberrypi.com/cm4io/cm4io-datasheet.pdf)
