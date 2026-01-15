# Test Case #41: USB Keyboard and Mouse Functionality - Execution Guide

## Quick Start

```bash
# Run Test #41
pytest tests/unit_tests/hw_component/test_041_usb_keyboard_mouse.py -v -s

# Run with other quick tests
pytest tests/unit_tests/hw_component/ -m quick -v

# Run all hardware component tests
pytest tests/unit_tests/hw_component/ -m hardware -v
```

## Test Overview

**Test ID:** #41
**Category:** HW Component Test
**Component:** USB Ports
**Automation Level:** Fully automated (detection-based)

### What This Test Validates

- ✅ USB subsystem is operational (host controller working)
- ✅ USB devices are enumerated correctly (lsusb works)
- ✅ Linux input subsystem is functional (/dev/input exists)
- ✅ USB keyboard detected (if connected)
- ✅ USB mouse detected (if connected)
- ✅ Input event devices exist and are accessible

### Test Approach

The test uses **multiple detection methods** to validate USB input devices:

**For Keyboard Detection:**
1. Search lsusb output for keywords ('keyboard', 'kbd')
2. Check /dev/input/by-id for keyboard symlinks
3. Search /proc/bus/input/devices for keyboard entries
4. Check /sys/class/input/event*/device/name for keyboard devices

**For Mouse Detection:**
1. Search lsusb output for keywords ('mouse', 'pointing', 'trackball', 'touchpad')
2. Check /dev/input/mice device file
3. Check /dev/input/by-id for mouse symlinks
4. Check /sys/class/input/event*/device/name for mouse devices

### Graceful Degradation for Headless Systems

This test is designed to work on both **desktop** and **headless** CM4 systems:

- **Desktop CM4:** Keyboard and mouse are expected and validated
- **Headless CM4:** USB and input subsystems validated, but keyboard/mouse are optional

**Configuration:**
```python
'require_keyboard': False,  # False = optional (for headless systems)
'require_mouse': False,     # False = optional (for headless systems)
'require_usb': True,        # True = USB subsystem must work
```

## Prerequisites

### System Requirements

1. **Operating System:** Linux (Raspberry Pi OS or similar)
2. **USB Support:** USB host controller functional
3. **Commands Required:**
   - `lsusb` (from usbutils package)
   - Standard Linux utilities (cat, ls)

### Hardware Requirements

**Minimum (Headless):**
- USB host controller operational
- Input subsystem drivers loaded

**Full Testing (Desktop):**
- USB keyboard connected
- USB mouse connected

### Software Dependencies

```bash
# Install usbutils if missing
sudo apt-get update
sudo apt-get install -y usbutils

# Verify installation
lsusb --version
```

## Running the Test

### Method 1: Direct Execution

```bash
# Navigate to test directory
cd tests/unit_tests/hw_component/

# Run Test #41
pytest test_041_usb_keyboard_mouse.py -v -s

# Run with full traceback on failure
pytest test_041_usb_keyboard_mouse.py -v -s --tb=long
```

### Method 2: Run with Markers

```bash
# Run all quick hardware tests (includes Test #41)
pytest tests/unit_tests/hw_component/ -m "quick and hardware" -v

# Run all CM4-specific tests
pytest tests/unit_tests/ -m cm4 -v

# Run only Test #41
pytest tests/unit_tests/hw_component/ -k "test_041" -v -s
```

### Method 3: Run as Part of Test Suite

```bash
# Run all hardware component tests
pytest tests/unit_tests/hw_component/ -v

# Run all unit tests
pytest tests/unit_tests/ -v
```

## Expected Output

### Successful Test (Desktop System with Devices)

```
======================================================================
Test Case #41: USB Keyboard and Mouse Functionality
======================================================================

HW Component Test - USB Input Devices
======================================================================

[STEP 1] Check USB Subsystem
----------------------------------------------------------------------
[2025-01-15 10:30:00] Checking USB devices...
[2025-01-15 10:30:00]   ✓ USB subsystem operational
[2025-01-15 10:30:00]   Devices found: 8
[2025-01-15 10:30:00]     Bus 001 Device 003: ID 046d:c52b Logitech, Inc. Unifying Receiver
[2025-01-15 10:30:00]     Bus 001 Device 004: ID 1a2c:2124 China Resource Semico Co., Ltd USB Keyboard
...
✓ USB subsystem operational (8 devices)

[STEP 2] Check Input Subsystem
----------------------------------------------------------------------
[2025-01-15 10:30:00] Checking input subsystem...
[2025-01-15 10:30:00]   ✓ Input subsystem operational
[2025-01-15 10:30:00]   Event devices: 12
✓ Input subsystem operational (12 event devices)

[STEP 3] Detect USB Keyboard
----------------------------------------------------------------------
[2025-01-15 10:30:00] Detecting USB keyboard...
[2025-01-15 10:30:00]   ✓ Detected via lsusb (keyword: keyboard)
[2025-01-15 10:30:00]   ✓ Detected in /dev/input/by-id: usb-keyboard-event-kbd
[2025-01-15 10:30:00]   ✓ Detected in /proc/bus/input/devices
[2025-01-15 10:30:00]   ✓ Keyboard detected via: lsusb (keyword: keyboard), /dev/input/by-id, /proc/bus/input/devices
✓ USB Keyboard detected
  Detection methods: 3

[STEP 4] Detect USB Mouse
----------------------------------------------------------------------
[2025-01-15 10:30:00] Detecting USB mouse...
[2025-01-15 10:30:00]   ✓ Detected via lsusb (keyword: mouse)
[2025-01-15 10:30:00]   ✓ Detected: /dev/input/mice exists
[2025-01-15 10:30:00]   ✓ Detected in /dev/input/by-id: usb-mouse-event-mouse
[2025-01-15 10:30:00]   ✓ Mouse detected via: lsusb (keyword: mouse), /dev/input/mice, /dev/input/by-id
✓ USB Mouse detected
  Detection methods: 3

======================================================================
TEST RESULT: ✓ PASS
======================================================================

✓ Acceptance Criteria Verification:
  ✓ USB subsystem operational (8 devices)
  ✓ Input subsystem operational (12 event devices)
  ✓ USB Keyboard detected (3 methods)
  ✓ USB Mouse detected (3 methods)

✅ USB input devices operational

📄 Test log: /tmp/test_041_usb_keyboard_mouse.log
======================================================================

PASSED
```

### Successful Test (Headless System without Devices)

```
======================================================================
Test Case #41: USB Keyboard and Mouse Functionality
======================================================================

[STEP 1] Check USB Subsystem
----------------------------------------------------------------------
✓ USB subsystem operational (4 devices)

[STEP 2] Check Input Subsystem
----------------------------------------------------------------------
✓ Input subsystem operational (2 event devices)

[STEP 3] Detect USB Keyboard
----------------------------------------------------------------------
[2025-01-15 10:30:00] Detecting USB keyboard...
[2025-01-15 10:30:00]   ✗ Keyboard not detected
⚠ USB Keyboard not detected
  (This is acceptable for headless systems)

[STEP 4] Detect USB Mouse
----------------------------------------------------------------------
[2025-01-15 10:30:00] Detecting USB mouse...
[2025-01-15 10:30:00]   ✗ Mouse not detected
⚠ USB Mouse not detected
  (This is acceptable for headless systems)

======================================================================
TEST RESULT: ✓ PASS
======================================================================

✓ Acceptance Criteria Verification:
  ✓ USB subsystem operational (4 devices)
  ✓ Input subsystem operational (2 event devices)
  ⚠ USB Keyboard not detected (acceptable for headless)
  ⚠ USB Mouse not detected (acceptable for headless)

⚠️  No USB input devices detected
   Note: This is normal for headless/embedded systems
   Test validates USB and input subsystems are functional

======================================================================

PASSED
```

### Failed Test Examples

**USB Subsystem Failure:**
```
[STEP 1] Check USB Subsystem
----------------------------------------------------------------------
[2025-01-15 10:30:00] Checking USB devices...
[2025-01-15 10:30:00]   ✗ lsusb command not found

FAILED
USB subsystem not functional
Possible causes:
  - USB host controller not working
  - USB drivers not loaded
  - lsusb command not installed (apt install usbutils)
```

**Keyboard Required but Not Found:**
```
[STEP 3] Detect USB Keyboard
----------------------------------------------------------------------
[2025-01-15 10:30:00] Detecting USB keyboard...
[2025-01-15 10:30:00]   ✗ Keyboard not detected

FAILED
USB Keyboard required but not detected
```

## Troubleshooting

### Issue 1: lsusb Command Not Found

**Error:**
```
[2025-01-15 10:30:00]   ✗ lsusb command not found
```

**Cause:** `usbutils` package not installed

**Solution:**
```bash
# Install usbutils package
sudo apt-get update
sudo apt-get install -y usbutils

# Verify installation
lsusb --version
lsusb
```

### Issue 2: USB Subsystem Not Operational

**Error:**
```
[2025-01-15 10:30:00]   ✗ No USB devices found
```

**Possible Causes:**
1. USB host controller not functional
2. USB drivers not loaded
3. Hardware issue

**Solutions:**

```bash
# Check USB controller presence
lspci | grep -i usb
lsusb -t  # Tree view of USB buses

# Check USB drivers loaded
lsmod | grep usb

# Check kernel messages for USB errors
dmesg | grep -i usb

# Check USB devices in sysfs
ls -la /sys/bus/usb/devices/

# For CM4, check device tree overlays
vcgencmd get_config int | grep usb
```

### Issue 3: Input Subsystem Not Operational

**Error:**
```
[2025-01-15 10:30:00]   ✗ No event devices found
```

**Possible Causes:**
1. Input drivers not loaded
2. /dev/input not mounted
3. Minimal system without input support

**Solutions:**

```bash
# Check if /dev/input exists
ls -la /dev/input/

# Check input drivers loaded
lsmod | grep evdev
lsmod | grep usbhid

# Load input drivers if missing
sudo modprobe evdev
sudo modprobe usbhid

# Check input devices in /proc
cat /proc/bus/input/devices
```

### Issue 4: Keyboard Not Detected

**Error:**
```
[2025-01-15 10:30:00]   ✗ Keyboard not detected
```

**Possible Causes:**
1. Keyboard not connected
2. Keyboard not USB (PS/2 keyboard)
3. Keyboard not recognized by kernel
4. Faulty keyboard or cable

**Solutions:**

```bash
# Verify keyboard is USB device
lsusb | grep -i keyboard

# Check USB HID driver loaded
lsmod | grep usbhid

# Disconnect and reconnect keyboard, watch kernel messages
sudo dmesg -w
# (Now disconnect and reconnect keyboard)

# Check input device names
for dev in /dev/input/event*; do
    echo "Device: $dev"
    cat /sys/class/input/$(basename $dev)/device/name 2>/dev/null || echo "  (name not available)"
done

# Try different USB port
# Check cable connection
```

### Issue 5: Mouse Not Detected

**Error:**
```
[2025-01-15 10:30:00]   ✗ Mouse not detected
```

**Similar solutions as Issue 4, but check for mouse-specific keywords:**

```bash
# Verify mouse is USB device
lsusb | grep -i mouse

# Check /dev/input/mice
ls -la /dev/input/mice

# Check mouse event devices
for dev in /dev/input/event*; do
    name=$(cat /sys/class/input/$(basename $dev)/device/name 2>/dev/null)
    echo "$dev: $name" | grep -i mouse
done
```

### Issue 6: Permission Errors

**Error:**
```
[2025-01-15 10:30:00]   ⚠ Could not check by-id: Permission denied
```

**Cause:** Insufficient permissions to read /dev/input or /sys

**Solutions:**

```bash
# Run test with sudo (not recommended)
sudo pytest test_041_usb_keyboard_mouse.py -v -s

# Add user to input group (recommended)
sudo usermod -a -G input $USER
# Log out and log back in for group change to take effect

# Check current groups
groups

# Verify /dev/input permissions
ls -la /dev/input/
```

### Issue 7: Test Passes but Devices Not Actually Working

**Scenario:** Test detects keyboard/mouse but they don't work

**Note:** This test only validates **detection**, not actual functionality. Functional testing requires user interaction and is beyond the scope of this automated test.

**Manual Verification:**

```bash
# Test keyboard input
cat /dev/input/by-id/*-kbd
# (Press keys and see if characters appear)

# Test mouse input
cat /dev/input/mice
# (Move mouse and see if binary data appears)

# Use evtest for detailed testing
sudo apt-get install evtest
sudo evtest
# Select keyboard or mouse device and interact
```

## Test Configuration

### Configuration Parameters

```python
@pytest.fixture(scope="class")
def test_config(self):
    return {
        # Device detection keywords
        'keyboard_keywords': ['keyboard', 'kbd'],
        'mouse_keywords': ['mouse', 'pointing', 'trackball', 'touchpad'],

        # Paths to check
        'input_dir': '/dev/input',
        'by_id_dir': '/dev/input/by-id',
        'by_path_dir': '/dev/input/by-path',
        'proc_devices': '/proc/bus/input/devices',

        # Test mode
        'require_keyboard': False,  # False = optional (for headless systems)
        'require_mouse': False,     # False = optional (for headless systems)
        'require_usb': True,        # True = USB subsystem must work

        # Logging
        'enable_logging': True,
        'log_file': '/tmp/test_041_usb_keyboard_mouse.log',
    }
```

### Customization for Different Scenarios

**Desktop System (Require Devices):**
```python
'require_keyboard': True,
'require_mouse': True,
```

**Headless System (Optional Devices):**
```python
'require_keyboard': False,
'require_mouse': False,
```

**Add Additional Keywords:**
```python
'keyboard_keywords': ['keyboard', 'kbd', 'keybrd', 'chicony'],
'mouse_keywords': ['mouse', 'pointing', 'trackball', 'touchpad', 'logitech'],
```

## Comparison with Related Tests

| Aspect | Test #41 (USB Input Devices) | Test #42 (USB Storage)* | Test #43 (USB Hub)* |
|--------|------------------------------|-------------------------|---------------------|
| **Component** | USB Ports (HID) | USB Ports (Mass Storage) | USB Hub/Ports |
| **Detection** | Keyboard, Mouse | USB drives, SD readers | Hub, port count |
| **Validation** | Device enumeration | Storage operations | Port expansion |
| **Headless OK** | Yes (optional devices) | Yes | Yes |
| **Automation** | Fully automated | Fully automated | Fully automated |
| **Duration** | Quick (~5 seconds) | Medium (~30 seconds) | Quick (~5 seconds) |

*Tests #42 and #43 are hypothetical examples for comparison

### When to Use Test #41

- ✅ Validate USB host controller functionality
- ✅ Detect USB input devices
- ✅ Verify input subsystem is operational
- ✅ Quick smoke test for USB ports
- ✅ Works on both desktop and headless systems

### When Test #41 is NOT Sufficient

- ❌ Testing actual keyboard typing functionality
- ❌ Testing mouse movement and clicks
- ❌ USB storage device testing
- ❌ USB bandwidth/performance testing
- ❌ USB hub port expansion testing

## CI/CD Integration

### GitLab CI Example

```yaml
test:unit:hw-component:usb:
  stage: test
  tags:
    - cm4
    - hardware
  script:
    # Ensure usbutils is installed
    - sudo apt-get update && sudo apt-get install -y usbutils

    # Run Test #41
    - pytest tests/unit_tests/hw_component/test_041_usb_keyboard_mouse.py -v -s

    # Upload test log as artifact
    - mkdir -p artifacts
    - cp /tmp/test_041_usb_keyboard_mouse.log artifacts/ || true
  artifacts:
    when: always
    paths:
      - artifacts/
    expire_in: 7 days
  allow_failure: false  # USB subsystem must work
```

### GitHub Actions Example

```yaml
name: Hardware Tests - USB Input Devices

on: [push, pull_request]

jobs:
  test-usb-input:
    runs-on: [self-hosted, cm4, hardware]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: |
          pip install -r tests/requirements.txt
          sudo apt-get update
          sudo apt-get install -y usbutils

      - name: Run Test #41
        run: |
          pytest tests/unit_tests/hw_component/test_041_usb_keyboard_mouse.py -v -s

      - name: Upload Test Log
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-041-log
          path: /tmp/test_041_usb_keyboard_mouse.log
```

## Use Cases

### Use Case 1: Production Line Testing

**Scenario:** Validate USB ports during CM4 board manufacturing

**Approach:**
- Connect USB keyboard and mouse
- Configure test with `require_keyboard=True`, `require_mouse=True`
- Run test as part of production test suite
- Log results to production database

### Use Case 2: Field Deployment Validation

**Scenario:** Validate USB functionality after shipping to customer site

**Approach:**
- Run test in headless mode (default configuration)
- Validate USB subsystem operational
- Detect any USB devices present
- Pass even if keyboard/mouse not connected

### Use Case 3: Continuous Integration

**Scenario:** Automated testing in CI/CD pipeline

**Approach:**
- Run on self-hosted CM4 runner
- Use headless configuration
- Test USB subsystem without requiring peripherals
- Fail pipeline if USB controller not working

### Use Case 4: Troubleshooting USB Issues

**Scenario:** Customer reports USB devices not working

**Approach:**
- Run test to validate USB subsystem
- Check which detection methods succeed/fail
- Review test log for detailed diagnostic information
- Use troubleshooting section to resolve issues

## Summary

Test #41 validates USB keyboard and mouse functionality on the Raspberry Pi CM4 by:

1. ✅ **USB Subsystem Check** - Verifies USB host controller is operational
2. ✅ **Input Subsystem Check** - Validates Linux input subsystem
3. ✅ **Multiple Detection Methods** - Uses 4 different methods for keyboard and mouse
4. ✅ **Graceful Degradation** - Works on headless systems without devices
5. ✅ **Comprehensive Logging** - Detailed diagnostic information

**Key Features:**
- Fully automated detection-based testing
- No user interaction required
- Suitable for CI/CD pipelines
- Works on both desktop and headless systems
- Provides detailed troubleshooting information

**Test Duration:** ~5 seconds

**Pass Criteria:**
- USB subsystem operational (required)
- Input subsystem operational (desirable)
- Keyboard detected (optional, configurable)
- Mouse detected (optional, configurable)

For questions or issues, refer to the troubleshooting section or check the test log at `/tmp/test_041_usb_keyboard_mouse.log`.
