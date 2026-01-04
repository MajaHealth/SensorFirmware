# Power Service Integration - Complete

## ✅ What Was Done

Successfully integrated **power-service** into the medical device setup, mirroring the SPI service architecture.

---

## 📦 Files Created/Modified

### **1. New File: `power_service_wrapper.sh`**

**Location:** `/home/pi/power_service_wrapper.sh` (on CM4)

**Purpose:** Wrapper script that sets up environment and launches power-service binary

**Content:**
```bash
#!/bin/bash
# Wrapper script to run power-service with proper environment

export HOME=/home/pi
export USER=root
export LOGNAME=root
export SHELL=/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export TERM=xterm-256color

cd /home/pi

# Log the attempt
logger "power_service wrapper starting"

# Run the binary
exec /home/pi/power-service "$@"
```

---

### **2. Modified: `medical_device_setup.sh`**

**Changes:**
- ✅ Added power-service executable check (similar to SPI)
- ✅ Created systemd unit: `power_service.service`
- ✅ Updated from 3 services → 4 services
- ✅ Added I2C dependency checks (power service uses I2C for battery)
- ✅ Updated all control and monitoring scripts

**New Systemd Unit:** `/etc/systemd/system/power_service.service`

```ini
[Unit]
Description=Power Management Service
After=multi-user.target
StartLimitBurst=3
StartLimitIntervalSec=300

[Service]
Type=simple
ExecStart=/home/pi/power_service_wrapper.sh
WorkingDirectory=/home/pi
User=root
Group=root
Restart=on-failure
RestartSec=10

# Hardware access groups (I2C for battery, GPIO for buttons/buzzer)
SupplementaryGroups=video gpio i2c dialout

Environment=HOME=/home/pi

StandardOutput=journal
StandardError=journal
SyslogIdentifier=power_service

[Install]
WantedBy=multi-user.target
```

---

### **3. Modified: `medical_device_control.sh`**

**Changes:**
- ✅ Updated from 3 services → 4 services
- ✅ Added `POWER_SERVICE` variable
- ✅ Updated startup order: `SPI + Power → Main → Flutter`
- ✅ Updated stop order: `Flutter → Main → Power + SPI`
- ✅ Added `logs power` command
- ✅ Added power service status/enable/disable commands
- ✅ Added individual control: `individual start power`

**New Commands:**
```bash
/home/pi/medical_device_control.sh logs power    # View power service logs
/home/pi/medical_device_control.sh individual start power
/home/pi/medical_device_control.sh individual stop power
```

---

### **4. Modified: `medical_device_monitor.sh`**

**Changes:**
- ✅ Added power service health checks
- ✅ Added I2C device availability check
- ✅ Auto-restart power service if it fails
- ✅ Log power service errors

**Monitoring:**
- Checks power service status every 2 minutes (via cron)
- Auto-restarts if down
- Logs to `/home/pi/log/medical_device/monitor.log`

---

## 🚀 Service Architecture (4 Services)

| # | Service | Binary | Wrapper | Port | Hardware |
|---|---------|--------|---------|------|----------|
| 1 | **SPI_DEV_servise** | `/home/pi/spi-service` | `spi_service_wrapper.sh` | 1293, 30009, 2812 | SPI, GPIO |
| 2 | **power_service** | `/home/pi/power-service` | `power_service_wrapper.sh` | 501 | I2C, GPIO |
| 3 | **main_service** | Via script | `start_main.sh` | - | Network |
| 4 | **flutter_app** | `flutter-pi` | Direct | - | Display |

---

## 🔄 Startup Order

```
Boot
 ↓
1. SPI_DEV_servise.service (starts immediately)
   └─ Initializes SPI sensors (ADS1293, MAX30009, WS2812)

2. power_service.service (starts immediately)
   └─ Initializes battery monitoring, buttons, buzzer

[2 second delay]

3. main_service.service (starts after SPI + Power)
   └─ Network supervisor, main logic

[5 second delay + health check]

4. flutter_app.service (starts only if main is healthy)
   └─ Medical device UI
```

---

## 🔌 Hardware Dependencies

### **SPI Service:**
- **SPI devices:** `/dev/spidev0.0`, `/dev/spidev0.1`
- **GPIO:** For sensor control
- **Groups:** `gpio`, `spi`, `dialout`

### **Power Service:**
- **I2C device:** `/dev/i2c-1` (battery communication)
- **GPIO:** For button inputs, buzzer output
- **Groups:** `gpio`, `i2c`, `dialout`

---

## 📋 Deployment Checklist

### **Step 1: Build Binaries**

From this repository:
```bash
# Build for ARM target
docker build --target artifacts -t sensor-firmware-build -f docker/Dockerfile .

# Extract binaries
docker create --name temp-container sensor-firmware-build
docker cp temp-container:/. build-output/bin/
docker rm temp-container

# Verify binaries exist
ls -la build-output/bin/spi-service
ls -la build-output/bin/power-service
```

---

### **Step 2: Deploy to CM4**

```bash
# Copy binaries to CM4
scp build-output/bin/spi-service pi@192.168.1.x:/home/pi/
scp build-output/bin/power-service pi@192.168.1.x:/home/pi/

# Copy wrapper scripts
scp deployment/spi_service_wrapper.sh pi@192.168.1.x:/home/pi/
scp deployment/power_service_wrapper.sh pi@192.168.1.x:/home/pi/

# Copy setup script
scp deployment/medical_device_setup.sh pi@192.168.1.x:/home/pi/

# Make wrappers executable
ssh pi@192.168.1.x "chmod +x /home/pi/spi_service_wrapper.sh"
ssh pi@192.168.1.x "chmod +x /home/pi/power_service_wrapper.sh"
ssh pi@192.168.1.x "chmod +x /home/pi/medical_device_setup.sh"
```

---

### **Step 3: Run Setup Script on CM4**

```bash
ssh pi@192.168.1.x
cd /home/pi
sudo ./medical_device_setup.sh
```

**What the setup script does:**
1. ✅ Checks for spi-service and power-service binaries
2. ✅ Enables SPI and I2C interfaces
3. ✅ Creates 4 systemd service units
4. ✅ Creates control and monitoring scripts
5. ✅ Enables services for auto-start
6. ✅ Disables getty@tty1 for direct boot
7. ✅ Sets up cron monitoring
8. ✅ Reboots system

---

### **Step 4: Verify After Reboot**

```bash
ssh pi@192.168.1.x

# Check all services
/home/pi/medical_device_control.sh status

# Test all services
/home/pi/medical_device_control.sh test

# Check dependencies
/home/pi/medical_device_control.sh check-deps

# View logs
/home/pi/medical_device_control.sh logs          # All services
/home/pi/medical_device_control.sh logs spi      # SPI only
/home/pi/medical_device_control.sh logs power    # Power only
```

---

## 🎮 Control Commands

### **Start/Stop All Services:**
```bash
/home/pi/medical_device_control.sh start
/home/pi/medical_device_control.sh stop
/home/pi/medical_device_control.sh restart
```

### **Individual Service Control:**
```bash
# Start individual services
/home/pi/medical_device_control.sh individual start spi
/home/pi/medical_device_control.sh individual start power
/home/pi/medical_device_control.sh individual start main
/home/pi/medical_device_control.sh individual start flutter

# Stop individual services
/home/pi/medical_device_control.sh individual stop spi
/home/pi/medical_device_control.sh individual stop power
/home/pi/medical_device_control.sh individual stop main
/home/pi/medical_device_control.sh individual stop flutter
```

### **View Logs:**
```bash
# Live logs (all services)
/home/pi/medical_device_control.sh logs

# Individual service logs
/home/pi/medical_device_control.sh logs spi
/home/pi/medical_device_control.sh logs power
/home/pi/medical_device_control.sh logs main
/home/pi/medical_device_control.sh logs flutter
```

### **Service Management:**
```bash
/home/pi/medical_device_control.sh enable    # Enable auto-start
/home/pi/medical_device_control.sh disable   # Disable auto-start
/home/pi/medical_device_control.sh status    # Show all status
/home/pi/medical_device_control.sh test      # Test all services
```

---

## 🔍 Troubleshooting

### **Power Service Not Starting:**

```bash
# Check if binary exists
ls -la /home/pi/power-service

# Check if wrapper exists
ls -la /home/pi/power_service_wrapper.sh

# Check systemd service
sudo systemctl status power_service.service

# View recent logs
sudo journalctl -u power_service.service -n 50

# Check I2C hardware
ls -la /dev/i2c-1

# Check if I2C is enabled
grep i2c /boot/config.txt

# Enable I2C if needed
sudo raspi-config
# Interface Options → I2C → Enable
```

### **SPI Service Not Starting:**

```bash
# Check if binary exists
ls -la /home/pi/spi-service

# Check SPI devices
ls -la /dev/spidev*

# Check if SPI is enabled
grep spi /boot/config.txt

# View logs
sudo journalctl -u SPI_DEV_servise.service -n 50
```

### **Check All Hardware:**

```bash
/home/pi/medical_device_control.sh check-deps
```

---

## 📊 System Logs

### **Systemd Journal (Current Session):**
```bash
# All services
sudo journalctl -u SPI_DEV_servise.service -u power_service.service -u main_service.service -u flutter_app.service

# Last 100 lines
sudo journalctl -u power_service.service -n 100

# Follow logs (live)
sudo journalctl -u power_service.service -f

# Filter by time
sudo journalctl -u power_service.service --since "10 minutes ago"
```

### **Monitor Logs:**
```bash
# Monitor script logs
tail -f /home/pi/log/medical_device/monitor.log

# Error logs only
tail -f /home/pi/log/medical_device/errors.log
```

---

## ✅ Verification Tests

After deployment, verify power service integration:

### **1. Check Service Status:**
```bash
systemctl is-active power_service.service
# Expected: active
```

### **2. Check Process:**
```bash
ps aux | grep power-service
# Expected: root ... /home/pi/power-service
```

### **3. Check Port (Port 501):**
```bash
sudo netstat -tulpn | grep 501
# Expected: tcp ... 0.0.0.0:501 ... power-service
```

### **4. Test JSON API:**
```bash
echo '{"type":"get_settings"}' | nc localhost 501
# Expected: JSON response with power settings
```

### **5. Check I2C Communication:**
```bash
sudo i2cdetect -y 1
# Expected: Should show battery chip address
```

---

## 🎯 Summary

**What Changed:**
- ✅ Medical device system now manages **4 services** (was 3)
- ✅ Power service fully integrated with same pattern as SPI service
- ✅ All control scripts updated for 4-service architecture
- ✅ Monitoring includes power service health checks
- ✅ I2C dependency checks added

**File Count:**
- **1 new file:** `power_service_wrapper.sh`
- **3 modified files:** `medical_device_setup.sh`, `medical_device_control.sh`, `medical_device_monitor.sh`
- **1 new systemd unit:** `power_service.service`

**Ready for:** Log rotation implementation (Phase 2)

---

## 📝 Next Steps

Now that power-service is integrated, you can proceed with:

1. **Phase 2:** Implement log rotation (date-based logs + archive)
2. **Phase 3:** Test on actual CM4 hardware
3. **Phase 4:** Deploy to production

---

**Generated:** 2025-01-02
**Status:** ✅ Complete and Ready for Testing
