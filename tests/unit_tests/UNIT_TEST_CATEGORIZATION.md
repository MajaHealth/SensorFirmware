# Unit Test Categorization Guide

This document categorizes all unit tests based on their connection method, service requirements, and execution location.

---

## Quick Reference Table

| Test # | Name | Service | Connection | Run Location | Mock Support |
|--------|------|---------|------------|--------------|--------------|
| 030 | CM4 Enumeration | None | USB/Local | PC (with CM4 connected) | No |
| 031 | eMMC Detection | None | USB/Local | PC (with CM4 connected) | No |
| 032 | OS Flashing eMMC | None | USB/Local | PC (with CM4 connected) | No |
| 033 | Boot Verification | None | Local (dmesg) | **CM4 only** | No |
| 035 | Internet Connectivity | None | SSH/Local | CM4 or SSH | Yes |
| 036 | SSH Accessibility | None | SSH/Local | **CM4 only** | No |
| 038 | Storage Read/Write | None | Local (eMMC) | **CM4 only** | No |
| 039 | Data Integrity | None | Local (eMMC) | **CM4 only** | No |
| 040 | Power Cycling Retention | None | Local (eMMC) | **CM4 only** | No |
| 041 | USB Keyboard/Mouse | None | Local (USB) | **CM4 only** | No |
| 102 | Switch State Readback | None | GPIO | **CM4 only** | No |
| 103 | Press Classification | None | GPIO | **CM4 only** | No |
| 104 | Debounce Robustness | None | GPIO | **CM4 only** | No |
| 105 | Soft Shutdown Handshake | power-service | TCP:501 | Laptop | Yes |
| 106 | Soft Shutdown Denied | power-service | TCP:501 | Laptop | Yes |
| 107 | Hard Shutdown Bypass | None | GPIO | **CM4 only** | No |
| 108 | Shutdown Initiated Status | power-service | TCP:501 | Laptop | Yes |
| 113 | Battery Discharge | power-service | TCP:501 | Laptop | Yes |
| 114 | Battery Recharge | power-service | TCP:501 | Laptop | Yes |
| 115 | Charge Control | power-service | TCP:501 | Laptop | Yes |
| 116 | DSI Display Detect | None | SSH (dmesg) | Laptop (SSH) | Yes |
| 117 | Display Power Mode | None | SSH (xrandr) | Laptop (SSH) | Yes |
| 118 | Display Rendering | None | SSH (fbi) | Laptop (SSH) | Yes |
| 119 | DSI Display Absent | None | SSH (dmesg) | Laptop (SSH) | Yes |
| 120 | Backlight Range | None | SSH (sysfs) | Laptop (SSH) | Yes |
| 121 | Backlight Toggle | None | SSH (sysfs) | Laptop (SSH) | Yes |
| 122 | Brightness Valid | None | SSH (sysfs) | Laptop (SSH) | Yes |
| 123 | Brightness Invalid | None | SSH (sysfs) | Laptop (SSH) | Yes |
| 124 | WiFi No Credentials | power-service | TCP:501 | Laptop | Yes |
| 125 | WiFi Provision | power-service | TCP:501 | Laptop | Yes |
| 126 | WiFi Auto Connect | power-service | TCP:501 | Laptop | Yes |
| 127 | WiFi Out of Range | power-service | TCP:501 | Laptop | Yes |
| 128 | WiFi Switch Network | power-service | TCP:501 | Laptop | Yes |
| 129 | WiFi Fallback | power-service | TCP:501 | Laptop | Yes |
| 130 | WiFi False Credentials | power-service | TCP:501 | Laptop | Yes |
| 131 | WiFi Polling Interval | power-service | TCP:501 | Laptop | Yes |
| 132 | WiFi Status Logging | power-service | TCP:501 | Laptop | Yes |
| 133 | WiFi Status to App | power-service | TCP:501 | Laptop | Yes |
| 134 | RTC I2C Presence | None | SSH (i2cdetect) | Laptop (SSH) | Yes |
| 135 | RTC Read/Write | None | SSH (hwclock) | Laptop (SSH) | Yes |
| 136 | RTC Advances Realtime | None | SSH (hwclock) | Laptop (SSH) | Yes |
| 196 | MAX30009 Data Envelope | spi-service | TCP:30009 | Laptop | Yes |
| 197 | MAX30009 Sync Mark | spi-service | TCP:30009 | Laptop | Yes |
| 198 | MAX30009 Sync Scaling | spi-service | TCP:30009 | Laptop | Yes |
| 206 | Battery Info Schema | power-service | TCP:501 | Laptop | Yes |
| 207 | Charge Disable State | power-service | TCP:501 | Laptop | Yes |
| 208 | Button Hold Time | power-service | TCP:501 | Laptop | Yes |
| 209 | Button Release State | power-service | TCP:501 | Laptop | Yes |

---

## Category Details

### Category 1: Tests Requiring spi-service (TCP Port 30009)

These tests communicate with spi-service via TCP/JSON protocol.

| Test # | Test Name | Description |
|--------|-----------|-------------|
| 196 | MAX30009 Data Envelope | Validates get_data response envelope fields |
| 197 | MAX30009 Sync Mark | Verifies sync mark presence in data stream |
| 198 | MAX30009 Sync Counter Scaling | Validates sync counter scaling factor |

**How to Run:**
```bash
# Hardware Mode (against real spi-service)
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_196_max30009_data_envelope.py -v -s

# Mock Simulation Mode (no hardware needed)
pytest tests/unit_tests/spi-service/test_196_max30009_data_envelope.py -v -s
```

**Requirements:**
- Hardware Mode: spi-service running on CM4, `PI_TARGET_IP` set
- Mock Mode: No requirements (runs locally with simulated responses)

---

### Category 2: Tests Requiring power-service (TCP Port 501)

These tests communicate with power-service via TCP/JSON protocol.

| Test # | Test Name | Description |
|--------|-----------|-------------|
| 105 | Soft Shutdown Handshake | Tests shutdown coordination |
| 106 | Soft Shutdown Denied | Tests button press without shutdown |
| 108 | Shutdown Initiated Status | Tests shutdown status reporting |
| 113 | Battery Discharge | Tests battery discharge monitoring |
| 114 | Battery Recharge | Tests battery recharge monitoring |
| 115 | Charge Control | Tests charge enable/disable commands |
| 124-133 | WiFi Tests | Various WiFi state and control tests |
| 206 | Battery Info Schema | Validates batt_info response format |
| 207 | Charge Disable State | Tests charge disable status |
| 208 | Button Hold Time | Tests button hold_time reporting |
| 209 | Button Release State | Tests button release detection |

**How to Run:**
```bash
# Hardware Mode (against real power-service)
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/power-service/test_115_charge_control.py -v -s

# Mock Simulation Mode (no hardware needed)
pytest tests/unit_tests/power-service/test_115_charge_control.py -v -s
```

**Requirements:**
- Hardware Mode: power-service running on CM4, `PI_TARGET_IP` set
- Mock Mode: No requirements (runs locally with simulated responses)

---

### Category 3: Tests Using SSH Commands (Run from Laptop)

These tests use SSH to execute commands on CM4. They do NOT require any firmware service.

| Test # | Test Name | SSH Commands Used |
|--------|-----------|-------------------|
| 116 | DSI Display Detect | `dmesg`, `/sys/class/drm/` |
| 117 | Display Power Mode | `xrandr`, `fbset`, `/sys/` |
| 118 | Display Rendering | `fbi` (framebuffer image) |
| 119 | DSI Display Absent | `dmesg` |
| 120 | Backlight Range | `/sys/class/backlight/` |
| 121 | Backlight Toggle | `/sys/class/backlight/` |
| 122 | Brightness Valid | `/sys/class/backlight/` |
| 123 | Brightness Invalid | `/sys/class/backlight/` |
| 134 | RTC I2C Presence | `i2cdetect` |
| 135 | RTC Read/Write | `hwclock` |
| 136 | RTC Advances Realtime | `hwclock`, `date` |

**How to Run:**
```bash
# Hardware Mode (SSH to CM4)
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_116_dsi_display_detect_init.py -v -s

# Mock Simulation Mode (no hardware needed)
pytest tests/unit_tests/spi-service/test_116_dsi_display_detect_init.py -v -s
```

**Requirements:**
- Hardware Mode: SSH access to CM4 (passwordless SSH recommended), `PI_TARGET_IP` set
- Mock Mode: No requirements (runs locally with simulated responses)

---

### Category 4: Tests That MUST Run on CM4

These tests access local hardware (GPIO, eMMC, USB) and cannot be run remotely.

| Test # | Test Name | Local Resource |
|--------|-----------|----------------|
| 033 | Boot Verification | `dmesg`, `journalctl` |
| 036 | SSH Accessibility | Local SSH service |
| 038 | Storage Read/Write | Local eMMC `/dev/mmcblk0` |
| 039 | Data Integrity | Local eMMC |
| 040 | Power Cycling Retention | Local eMMC `/var/tmp/` |
| 041 | USB Keyboard/Mouse | Local USB HID |
| 102 | Switch State Readback | GPIO (RPi.GPIO) |
| 103 | Press Classification | GPIO (RPi.GPIO) |
| 104 | Debounce Robustness | GPIO (RPi.GPIO) |
| 107 | Hard Shutdown Bypass | GPIO (RPi.GPIO) |

**How to Run:**
```bash
# Copy test file to CM4
scp tests/unit_tests/hw_component/test_033_boot_verification.py pi@192.168.1.4:/home/pi/unit_tests/

# SSH to CM4 and run
ssh pi@192.168.1.4
cd /home/pi/unit_tests
python3 -m pytest test_033_boot_verification.py -v -s
```

**Requirements:**
- Physical access to CM4 or SSH session
- Test file must be on CM4 filesystem
- Required hardware connected (GPIO, USB devices, etc.)

---

### Category 5: Tests That Run on PC (CM4 Connected via USB)

These tests run on a PC while CM4 is connected in USB boot mode.

| Test # | Test Name | Description |
|--------|-----------|-------------|
| 030 | CM4 Enumeration | Detect CM4 via `lsusb` |
| 031 | eMMC Detection | Detect eMMC after `rpiboot` |
| 032 | OS Flashing eMMC | Flash OS image to eMMC |

**How to Run:**
```bash
# On PC with CM4 connected via USB (boot mode)
pytest tests/unit_tests/hw_component/test_030_cm4_enumeration.py -v -s
```

**Requirements:**
- CM4 connected to PC via USB
- CM4 in USB boot mode (no bootable eMMC or SD)
- `rpiboot` utility installed on PC
- Run as root or with USB permissions

---

## Mock Simulation Mode Explained

Many tests support **Mock Simulation Mode** which allows running tests without hardware:

### When Mock Mode is Used:
- `PI_TARGET_IP` environment variable is NOT set
- Test cannot connect to the target service (connection refused)

### What Mock Mode Does:
- Simulates expected firmware responses
- Tests the test logic and validation code
- Returns predefined "correct" data

### When to Use Mock Mode:
- Developing/debugging test logic
- CI/CD pipeline testing
- When hardware is unavailable

### When to Use Hardware Mode:
- Validating actual firmware behavior
- Integration testing
- Final acceptance testing

---

## Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `PI_TARGET_IP` | CM4 IP address for TCP/SSH tests | `192.168.1.4` |

**Setting for Current Session:**
```bash
export PI_TARGET_IP=192.168.1.4
```

**Setting for Single Command:**
```bash
PI_TARGET_IP=192.168.1.4 pytest tests/unit_tests/power-service/test_115_charge_control.py -v -s
```

**Making Permanent:**
```bash
echo 'export PI_TARGET_IP=192.168.1.4' >> ~/.bashrc
source ~/.bashrc
```

---

## Service Port Reference

| Service | Port | Protocol | Tests |
|---------|------|----------|-------|
| power-service | 501 | TCP/JSON | 105, 106, 108, 113-115, 124-133, 206-209 |
| spi-service (MAX30009) | 30009 | TCP/JSON | 196, 197, 198 |
| spi-service (ADS1293) | 1293 | TCP/JSON | (integration tests) |
| spi-service (WS2812) | 2812 | TCP/JSON | (integration tests) |

---

## Troubleshooting

### Test shows "Mock Simulation Mode" when hardware is connected

**Cause:** `PI_TARGET_IP` is not set or is set incorrectly.

**Solution:**
```bash
# Verify the variable
echo $PI_TARGET_IP

# Set it correctly
export PI_TARGET_IP=192.168.1.4

# Verify connectivity
nc -zv $PI_TARGET_IP 501   # For power-service
nc -zv $PI_TARGET_IP 30009 # For spi-service MAX30009
```

### Connection Refused Error

**Cause:** Service is not running on CM4.

**Solution:**
```bash
# Check service status on CM4
ssh pi@192.168.1.4 "ps aux | grep -E 'power-service|spi-service'"

# Start services if needed
ssh pi@192.168.1.4 "/opt/sensor-firmware/bin/power-service &"
ssh pi@192.168.1.4 "/opt/sensor-firmware/bin/spi-service &"
```

### Test Fails on Laptop but Should Run on CM4

**Cause:** Test requires local hardware access (GPIO, eMMC).

**Solution:**
1. Copy test file to CM4
2. Run test directly on CM4
3. See "Category 4" tests above

---

## Summary by Execution Location

### Run from Laptop (with PI_TARGET_IP set):
- All power-service tests (105, 106, 108, 113-115, 124-133, 206-209)
- All spi-service MAX30009 tests (196-198)
- All display/backlight SSH tests (116-123)
- All RTC SSH tests (134-136)

### Run on CM4 Only:
- Boot/storage tests (033, 036, 038-041)
- GPIO hardware-in-loop tests (102-104, 107)

### Run on PC (CM4 via USB):
- USB boot mode tests (030-032)

---

*Document generated: 2026-01-26*
*Based on unit test analysis of sensor_test_project*
