#!/bin/bash
# Medical Device Boot Service Setup Script
# Creates 4 services: main + flutter + SPI_DEV_service + power_service

set -e

echo "✨ Medical Device Boot Service Setup (Main + Flutter + SPI_DEV + Power)"
echo "=============================================================="

# Configuration
SERVICE_DIR="/etc/systemd/system"
LOG_DIR="/home/pi/logs"
FLUTTER_APP_DIR="/home/pi/aarch64-generic"
SPI_EXECUTABLE="/home/pi/spi-service"
POWER_EXECUTABLE="/home/pi/power-service"

# =============================================================================
# INSTALL REQUIRED PACKAGES
# =============================================================================

echo ""
echo "📦 Checking and installing required packages..."

# Check if expect is installed (provides unbuffer command used in start_main.sh)
if ! command -v unbuffer &> /dev/null; then
    echo "   Installing 'expect' package (provides unbuffer command)..."
    sudo apt update
    sudo apt install -y expect
    echo "   ✓ expect package installed successfully"
else
    echo "   ✓ expect package already installed"
fi

# Create log directory
sudo mkdir -p "$LOG_DIR"
sudo chown pi:pi "$LOG_DIR"

# Create archive directory for log rotation
sudo mkdir -p "$LOG_DIR/archive"
sudo chown pi:pi "$LOG_DIR/archive"

# Create medical device monitor log directory
sudo mkdir -p "/home/pi/log/medical_device"
sudo chown pi:pi "/home/pi/log/medical_device"

# Create monitor log archive directory
sudo mkdir -p "/home/pi/log/medical_device/archive"
sudo chown pi:pi "/home/pi/log/medical_device/archive"

echo "🔧 Setting up SPI prerequisites for CM4..."

# Check if SPI_DEV_servise executable exists
if [ -f "$SPI_EXECUTABLE" ]; then
    echo "✓ Found SPI_DEV_servise executable"

    # Set executable permissions
    echo "  Setting executable permissions..."
    chmod a+x "$SPI_EXECUTABLE"
    echo "  Permissions set: $(ls -la $SPI_EXECUTABLE)"
else
    echo "⚠ SPI_DEV_servise executable not found at: $SPI_EXECUTABLE"
    echo "  Please ensure the file exists before continuing"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if power-service executable exists
echo "🔋 Setting up Power Service..."
if [ -f "$POWER_EXECUTABLE" ]; then
    echo "✓ Found power-service executable"

    # Set executable permissions
    echo "  Setting executable permissions..."
    chmod a+x "$POWER_EXECUTABLE"
    echo "  Permissions set: $(ls -la $POWER_EXECUTABLE)"
else
    echo "⚠ power-service executable not found at: $POWER_EXECUTABLE"
    echo "  Please ensure the file exists before continuing"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if SPI is enabled in config
echo "🔍 Checking SPI configuration..."
if grep -q "dtparam=spi=on" /boot/config.txt 2>/dev/null; then
    echo "✓ SPI already enabled in /boot/config.txt"
elif grep -q "^dtparam=spi=off" /boot/config.txt 2>/dev/null; then
    echo "⚠ SPI is disabled in /boot/config.txt"
    echo "  Enabling SPI in /boot/config.txt..."
    sudo sed -i 's/^dtparam=spi=off/dtparam=spi=on/' /boot/config.txt
    echo "✓ SPI enabled - reboot will be required"
    REBOOT_REQUIRED=true
else
    echo "  Adding SPI configuration to /boot/config.txt..."
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "✓ SPI enabled - reboot will be required"
    REBOOT_REQUIRED=true
fi

# Check if SPI kernel modules are loaded
echo "🔍 Checking SPI kernel modules..."
if lsmod | grep -q spi; then
    echo "✓ SPI kernel modules are loaded"
else
    echo "⚠ SPI kernel modules not detected"
    echo "  Loading SPI kernel modules..."
    sudo modprobe spi-bcm2835 2>/dev/null || true
    sudo modprobe spidev 2>/dev/null || true

    if lsmod | grep -q spi; then
        echo "✓ SPI kernel modules loaded successfully"
    else
        echo "⚠ SPI kernel modules may need a reboot to load properly"
        REBOOT_REQUIRED=true
    fi
fi

# Check for SPI devices
echo "🔍 Checking SPI device files..."
if [ -e "/dev/spidev0.0" ] || [ -e "/dev/spidev0.1" ]; then
    echo "✓ SPI devices detected:"
    ls -la /dev/spidev* 2>/dev/null
else
    echo "⚠ No SPI devices found"
    echo "  This is normal if SPI was just enabled - they will appear after reboot"
    REBOOT_REQUIRED=true
fi

echo ""
echo "📝 Creating systemd services..."

# 1. Main Service (keeping your configuration)
cat << 'EOF' | sudo tee "$SERVICE_DIR/main_service.service"
[Unit]
Description=Medical Device Main Application
After=network.target dbus.service NetworkManager.service
# SPI_DEV_servise.service power_service.service
Wants=network.target
Requires=dbus.service NetworkManager.service
# Before=flutter_app.service
StartLimitBurst=3
StartLimitIntervalSec=300

[Service]
Type=simple
ExecStart=/home/pi/start_main.sh
WorkingDirectory=/home/pi
User=root
Group=root
# Restart=always
# RestartSec=5
Restart=on-failure
RestartSec=10
# StartLimitBurst=3
# StartLimitIntervalSec=300

# Critical environment variables for nmcli
Environment="DBUS_SYSTEM_BUS_ADDRESS=unix:path=/var/run/dbus/system_bus_socket"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Ensure proper privileges for network operations
PrivateNetwork=false
NoNewPrivileges=false

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 2. SPI_DEV_servise Service
sudo tee /etc/systemd/system/SPI_DEV_servise.service << 'EOF'
[Unit]
Description=SPI Device Service
After=multi-user.target
# Before=main_service.service flutter_app.service
StartLimitBurst=3
StartLimitIntervalSec=300

[Service]
Type=simple
ExecStart=/home/pi/spi_service_wrapper.sh
WorkingDirectory=/home/pi
User=root
Group=root
# Restart=always
# RestartSec=5
Restart=on-failure
RestartSec=10
# StartLimitBurst=3
# StartLimitIntervalSec=300

# Minimal restrictions
NoNewPrivileges=false
PrivateDevices=false

# Hardware access groups
SupplementaryGroups=video gpio spi dialout

# Basic environment
Environment=HOME=/home/pi

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=spi_dev

[Install]
WantedBy=multi-user.target
EOF

# 3. Power Service (NEW - mirrors SPI service configuration)
sudo tee /etc/systemd/system/power_service.service << 'EOF'
[Unit]
Description=Power Management Service
After=multi-user.target
# Before=main_service.service flutter_app.service
StartLimitBurst=3
StartLimitIntervalSec=300

[Service]
Type=simple
ExecStart=/home/pi/power_service_wrapper.sh
WorkingDirectory=/home/pi
User=root
Group=root
# Restart=always
# RestartSec=5
Restart=on-failure
RestartSec=10
# StartLimitBurst=3
# StartLimitIntervalSec=300

# Minimal restrictions
NoNewPrivileges=false
PrivateDevices=false

# Hardware access groups (I2C for battery, GPIO for buttons/buzzer)
SupplementaryGroups=video gpio i2c dialout

# Basic environment
Environment=HOME=/home/pi

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=power_service

[Install]
WantedBy=multi-user.target
EOF

# 4. Flutter Application Service
cat << 'EOF' | sudo tee "$SERVICE_DIR/flutter_app.service"
[Unit]
Description=Medical Device Flutter UI
# After=main_service.service SPI_DEV_servise.service power_service.service network.target
After=network.target
# Wants=main_service.service SPI_DEV_servise.service power_service.service
# Requires=main_service.service
StartLimitBurst=3
StartLimitIntervalSec=300

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/aarch64-generic

ExecStartPre=/bin/sleep 15
# Start Flutter with your exact command
ExecStart=/home/pi/aarch64-generic/flutter-pi /home/pi/aarch64-generic --enable-dart-profiling=true --enable-checked-mode=true --verify-entry-points=true --vm-service-port=50880

# Restart=always
# RestartSec=10
# StartLimitInterval=300
# StartLimitBurst=3

Restart=on-failure
RestartSec=10
# StartLimitBurst=3
# StartLimitIntervalSec=300

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=flutter_app

# Resource limits
# MemoryLimit=1G
# CPUQuota=90%

# Environment for Flutter
Environment=HOME=/home/pi
Environment=USER=pi
Environment=DISPLAY=:0

# Graphics and hardware access
SupplementaryGroups=video render input gpio

[Install]
WantedBy=multi-user.target
EOF

# CRITICAL: Reload systemd daemon
echo ""
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload
sudo systemctl restart main_service.service SPI_DEV_servise.service power_service.service flutter_app.service

# Enable services for automatic startup
echo "✅ Enabling services for automatic startup..."
sudo systemctl enable SPI_DEV_servise.service
sudo systemctl enable power_service.service
sudo systemctl enable main_service.service
sudo systemctl enable flutter_app.service

# 5. Create control script for all 4 services
cat << 'EOF' | sudo tee "/home/pi/medical_device_control.sh"
#!/bin/bash
# Medical Device Control Script (Main + Flutter + SPI_DEV + Power)

MAIN_SERVICE="main_service.service"
FLUTTER_SERVICE="flutter_app.service"
SPI_SERVICE="SPI_DEV_servise.service"
POWER_SERVICE="power_service.service"
LOG_DIR="/home/pi/logs"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_DIR/control.log"
}

case "$1" in
    start)
        echo "🚀 Starting Medical Device Services..."
        log_message "Starting medical device services (4 services)"

        # Start hardware services first (SPI + Power)
        echo "  Starting SPI_DEV_servise..."
        sudo systemctl start "$SPI_SERVICE"

        echo "  Starting Power service..."
        sudo systemctl start "$POWER_SERVICE"
        sleep 2

        # Start main service
        echo "  Starting Main service..."
        sudo systemctl start "$MAIN_SERVICE"
        echo "  Main service started, waiting 5 seconds..."
        sleep 5

        # Check if main is running before starting Flutter
        if sudo systemctl is-active --quiet "$MAIN_SERVICE"; then
            echo "  Main service confirmed running, starting Flutter..."
            sudo systemctl start "$FLUTTER_SERVICE"
            echo "✓ Flutter service started"
        else
            echo "❌ Main service failed to start, not starting Flutter"
            log_message "Main service failed to start"
            exit 1
        fi

        echo "✅ All services started successfully!"
        log_message "All 4 services started successfully"
        ;;

    stop)
        echo "🛑 Stopping Medical Device Services..."
        log_message "Stopping medical device services"

        # Stop Flutter first
        echo "  Stopping Flutter service..."
        sudo systemctl stop "$FLUTTER_SERVICE"

        # Then stop main
        echo "  Stopping Main service..."
        sudo systemctl stop "$MAIN_SERVICE"

        # Finally stop hardware services
        echo "  Stopping SPI_DEV_servise..."
        sudo systemctl stop "$SPI_SERVICE"

        echo "  Stopping Power service..."
        sudo systemctl stop "$POWER_SERVICE"

        echo "✅ All services stopped"
        log_message "All services stopped successfully"
        ;;

    restart)
        echo "🔄 Restarting Medical Device Services..."
        log_message "Restarting medical device services"

        $0 stop
        sleep 3
        $0 start
        ;;

    status)
        echo "📊 Medical Device Status:"
        echo "========================="

        echo "  SPI_DEV_servise:"
        sudo systemctl status "$SPI_SERVICE" --no-pager -l
        echo ""

        echo "  Power Service:"
        sudo systemctl status "$POWER_SERVICE" --no-pager -l
        echo ""

        echo "  Main Service (start_main.sh):"
        sudo systemctl status "$MAIN_SERVICE" --no-pager -l
        echo ""

        echo "  Flutter Service (aarch64-generic):"
        sudo systemctl status "$FLUTTER_SERVICE" --no-pager -l
        echo ""
        ;;

    enable)
        echo "✅ Enabling Medical Device Services for boot..."
        sudo systemctl enable "$SPI_SERVICE"
        sudo systemctl enable "$POWER_SERVICE"
        sudo systemctl enable "$MAIN_SERVICE"
        sudo systemctl enable "$FLUTTER_SERVICE"
        echo "✓ All 4 services enabled for automatic startup"
        log_message "All services enabled for automatic startup"
        ;;

    disable)
        echo "🚫 Disabling Medical Device Services..."
        sudo systemctl disable "$SPI_SERVICE"
        sudo systemctl disable "$POWER_SERVICE"
        sudo systemctl disable "$MAIN_SERVICE"
        sudo systemctl disable "$FLUTTER_SERVICE"
        echo "✓ All services disabled"
        log_message "All services disabled"
        ;;

    logs)
        case "$2" in
            spi)
                echo "📋 SPI_DEV_servise Logs:"
                sudo journalctl -u SPI_DEV_servise.service -f --no-pager
                ;;
            power)
                echo "📋 Power Service Logs:"
                sudo journalctl -u power_service.service -f --no-pager
                ;;
            main)
                echo "📋 Main Service Logs (start_main.sh):"
                sudo journalctl -u main_service.service -f --no-pager
                ;;
            flutter)
                echo "📋 Flutter Service Logs:"
                sudo journalctl -u flutter_app.service -f --no-pager
                ;;
            *)
                echo "📋 All Service Logs:"
                sudo journalctl -u SPI_DEV_servise.service -u power_service.service -u main_service.service -u flutter_app.service -f --no-pager
                ;;
        esac
        ;;

    test)
        echo "🧪 Testing All Services..."

        # Test SPI_DEV_servise
        if sudo systemctl is-active --quiet "$SPI_SERVICE"; then
            echo "✓ SPI_DEV_servise: RUNNING"
        else
            echo "❌ SPI_DEV_servise: NOT RUNNING"
        fi

        # Test Power service
        if sudo systemctl is-active --quiet "$POWER_SERVICE"; then
            echo "✓ Power service: RUNNING"
        else
            echo "❌ Power service: NOT RUNNING"
        fi

        # Test main service
        if sudo systemctl is-active --quiet "$MAIN_SERVICE"; then
            echo "✓ Main service (start_main.sh): RUNNING"
        else
            echo "❌ Main service (start_main.sh): NOT RUNNING"
        fi

        # Test Flutter service
        if sudo systemctl is-active --quiet "$FLUTTER_SERVICE"; then
            echo "✓ Flutter service: RUNNING"
        else
            echo "❌ Flutter service: NOT RUNNING"
        fi

        echo ""
        echo "📁 File Checks:"

        # Check SPI executable permissions
        if [ -f "/home/pi/spi-service" ]; then
            echo "✓ spi-service executable: EXISTS"
            chmod a+x "/home/pi/spi-service"
            echo "  Permissions: $(ls -la /home/pi/spi-service | awk '{print $1, $3, $4}')"
        else
            echo "❌ spi-service executable: MISSING"
        fi

        # Check Power executable permissions
        if [ -f "/home/pi/power-service" ]; then
            echo "✓ power-service executable: EXISTS"
            chmod a+x "/home/pi/power-service"
            echo "  Permissions: $(ls -la /home/pi/power-service | awk '{print $1, $3, $4}')"
        else
            echo "❌ power-service executable: MISSING"
        fi

        # Check if Flutter app directory exists
        if [ -d "/home/pi/aarch64-generic" ]; then
            echo "✓ Flutter app directory: EXISTS"
            if [ -f "/home/pi/aarch64-generic/flutter-pi" ]; then
                echo "✓ flutter-pi executable: EXISTS"
            else
                echo "❌ flutter-pi executable: MISSING"
            fi
        else
            echo "❌ Flutter app directory: MISSING"
        fi

        # Check if start_main.sh exists
        if [ -f "/home/pi/start_main.sh" ]; then
            echo "✓ start_main.sh script: EXISTS"
        else
            echo "❌ start_main.sh script: MISSING"
        fi

        echo ""
        echo "🔍 Running Processes:"
        echo "SPI processes:"
        ps aux | grep -E "spi-service" | grep -v grep || echo "  No spi-service processes found"
        echo "Power processes:"
        ps aux | grep -E "power-service" | grep -v grep || echo "  No power-service processes found"
        echo "Main processes:"
        ps aux | grep -E "start_main" | grep -v grep || echo "  No start_main processes found"
        echo "Flutter processes:"
        ps aux | grep -E "flutter-pi" | grep -v grep || echo "  No flutter-pi processes found"

        # Check network status (since main service needs network)
        echo ""
        echo "🌐 Network Status:"
        if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
            echo "✓ Network connectivity: OK"
        else
            echo "❌ Network connectivity: FAILED"
        fi

        # Check SPI hardware
        echo ""
        echo "🔌 SPI Hardware:"
        if [ -e "/dev/spidev0.0" ] || [ -e "/dev/spidev0.1" ]; then
            echo "✓ SPI devices detected:"
            ls -la /dev/spidev* 2>/dev/null || echo "  No SPI devices found"
        else
            echo "❌ No SPI devices found - check if SPI is enabled"
        fi

        # Check I2C hardware (for power service)
        echo ""
        echo "🔌 I2C Hardware:"
        if [ -e "/dev/i2c-1" ]; then
            echo "✓ I2C device detected:"
            ls -la /dev/i2c-1 2>/dev/null
        else
            echo "❌ No I2C devices found - check if I2C is enabled"
        fi
        ;;

    check-deps)
        echo "🔍 Checking Dependencies..."

        # Check if NetworkManager is running
        if sudo systemctl is-active --quiet NetworkManager; then
            echo "✓ NetworkManager: RUNNING"
        else
            echo "❌ NetworkManager: NOT RUNNING"
        fi

        # Check if dbus is running
        if sudo systemctl is-active --quiet dbus; then
            echo "✓ D-Bus: RUNNING"
        else
            echo "❌ D-Bus: NOT RUNNING"
        fi

        # Check network target
        if sudo systemctl is-active --quiet network.target; then
            echo "✓ Network Target: ACTIVE"
        else
            echo "❌ Network Target: INACTIVE"
        fi

        # Check SPI kernel module
        if lsmod | grep -q spi; then
            echo "✓ SPI kernel modules: LOADED"
        else
            echo "⚠ SPI kernel modules: NOT DETECTED (may need reboot or manual loading)"
        fi

        # Check if SPI is enabled in config
        if grep -q "dtparam=spi=on" /boot/config.txt 2>/dev/null; then
            echo "✓ SPI enabled in /boot/config.txt"
        elif grep -q "dtparam=spi=off" /boot/config.txt 2>/dev/null; then
            echo "❌ SPI disabled in /boot/config.txt"
            echo "   Run: sudo raspi-config → Interface Options → SPI → Enable"
        else
            echo "⚠ SPI not configured in /boot/config.txt"
            echo "   Run: sudo raspi-config → Interface Options → SPI → Enable"
        fi

        # Check if I2C is enabled in config
        if grep -q "dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null; then
            echo "✓ I2C enabled in /boot/config.txt"
        else
            echo "⚠ I2C not enabled - power service needs I2C for battery monitoring"
            echo "   Run: sudo raspi-config → Interface Options → I2C → Enable"
        fi
        ;;

    setup-direct-boot)
        echo "🖥️ Setting up direct boot (disabling getty@tty1)..."

        # Disable getty@tty1 service
        sudo systemctl disable getty@tty1.service
        sudo systemctl mask getty@tty1.service
        sudo systemctl stop getty@tty1.service

        echo "✓ Direct boot setup completed"
        ;;

    individual)
        case "$2" in
            start)
                case "$3" in
                    spi)
                        echo "🚀 Starting SPI_DEV_servise only..."
                        sudo systemctl start "$SPI_SERVICE"
                        ;;
                    power)
                        echo "🚀 Starting Power service only..."
                        sudo systemctl start "$POWER_SERVICE"
                        ;;
                    main)
                        echo "🚀 Starting Main service only..."
                        sudo systemctl start "$MAIN_SERVICE"
                        ;;
                    flutter)
                        echo "🚀 Starting Flutter service only..."
                        sudo systemctl start "$FLUTTER_SERVICE"
                        ;;
                    *)
                        echo "Usage: $0 individual start {spi|power|main|flutter}"
                        ;;
                esac
                ;;
            stop)
                case "$3" in
                    spi)
                        echo "🛑 Stopping SPI_DEV_servise only..."
                        sudo systemctl stop "$SPI_SERVICE"
                        ;;
                    power)
                        echo "🛑 Stopping Power service only..."
                        sudo systemctl stop "$POWER_SERVICE"
                        ;;
                    main)
                        echo "🛑 Stopping Main service only..."
                        sudo systemctl stop "$MAIN_SERVICE"
                        ;;
                    flutter)
                        echo "🛑 Stopping Flutter service only..."
                        sudo systemctl stop "$FLUTTER_SERVICE"
                        ;;
                    *)
                        echo "Usage: $0 individual stop {spi|power|main|flutter}"
                        ;;
                esac
                ;;
            *)
                echo "Usage: $0 individual {start|stop} {spi|power|main|flutter}"
                ;;
        esac
        ;;

    *)
        echo "Medical Device Control Script (4 Services)"
        echo "Usage: $0 {start|stop|restart|status|enable|disable|logs|test|check-deps|individual|setup-direct-boot}"
        echo ""
        echo "Commands:"
        echo "  start      - Start all services (SPI + Power → Main → Flutter)"
        echo "  stop       - Stop all services (Flutter → Main → Power + SPI)"
        echo "  restart    - Restart all services"
        echo "  status     - Show status of all services"
        echo "  enable     - Enable all services for automatic startup"
        echo "  disable    - Disable automatic startup"
        echo "  logs       - Show live logs (logs spi, logs power, logs main, logs flutter, or logs for all)"
        echo "  test       - Test if services and files are present"
        echo "  check-deps - Check if required dependencies are running"
        echo "  individual - Control individual services"
        echo "  setup-direct-boot - Disable getty@tty1 for direct boot"
        echo ""
        echo "Individual service control:"
        echo "  $0 individual start spi     - Start only SPI_DEV_servise"
        echo "  $0 individual start power   - Start only Power service"
        echo "  $0 individual stop main     - Stop only Main service"
        echo "  $0 individual start flutter - Start only Flutter service"
        echo ""
        echo "Your Configuration (4 Services):"
        echo "  1. SPI_DEV_servise: /home/pi/spi-service (runs as root, hardware access)"
        echo "  2. Power Service: /home/pi/power-service (runs as root, I2C + GPIO)"
        echo "  3. Main: /home/pi/start_main.sh (runs as root with network deps)"
        echo "  4. Flutter: /home/pi/aarch64-generic/flutter-pi /home/pi/aarch64-generic"
        echo ""
        echo "Startup Order: SPI + Power → Main → Flutter"
        exit 1
        ;;
esac
EOF

# Make control script executable
sudo chmod +x "/home/pi/medical_device_control.sh"

# 6. Create enhanced error monitoring script
cat << 'EOF' | sudo tee "/home/pi/medical_device_monitor.sh"
#!/bin/bash
# Medical Device Error Monitor (4 Services)

# =============================================================================
# LOG ROTATION FUNCTION
# =============================================================================
archive_old_monitor_logs() {
    local log_dir="/home/pi/log/medical_device"
    local archive_dir="/home/pi/log/medical_device/archive"
    local today_monitor="monitor-$(date +%Y-%m-%d).log"
    local today_error="errors-$(date +%Y-%m-%d).log"

    # Create archive directory if needed
    mkdir -p "$archive_dir"

    # Move monitor logs that are NOT today's log to archive
    find "$log_dir" -maxdepth 1 -name "monitor-*.log" \
         ! -name "$today_monitor" -exec mv {} "$archive_dir/" \; 2>/dev/null

    # Move error logs that are NOT today's log to archive
    find "$log_dir" -maxdepth 1 -name "errors-*.log" \
         ! -name "$today_error" -exec mv {} "$archive_dir/" \; 2>/dev/null
}

# Archive old logs before starting (runs every 2 minutes, safe due to date check)
archive_old_monitor_logs

# Set up today's dated log files
LOG_FILE="/home/pi/log/medical_device/monitor-$(date +%Y-%m-%d).log"
ERROR_LOG="/home/pi/log/medical_device/errors-$(date +%Y-%m-%d).log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$ERROR_LOG"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
}

check_services() {
    # Check SPI_DEV_servise
    if ! systemctl is-active --quiet SPI_DEV_servise.service; then
        log_error "SPI_DEV_servise is not running"
        echo "⚠ SPI_DEV_servise DOWN - attempting restart..."
        sudo systemctl restart SPI_DEV_servise.service
        sleep 3
        if systemctl is-active --quiet SPI_DEV_servise.service; then
            log_message "SPI_DEV_servise restarted successfully"
        else
            log_error "Failed to restart SPI_DEV_servise"
        fi
    fi

    # Check Power service
    if ! systemctl is-active --quiet power_service.service; then
        log_error "Power service is not running"
        echo "⚠ Power service DOWN - attempting restart..."
        sudo systemctl restart power_service.service
        sleep 3
        if systemctl is-active --quiet power_service.service; then
            log_message "Power service restarted successfully"
        else
            log_error "Failed to restart Power service"
        fi
    fi

    # Check main service
    if ! systemctl is-active --quiet main_service.service; then
        log_error "Main service (start_main.sh) is not running"
        echo "⚠ Main service DOWN - attempting restart..."
        sudo systemctl restart main_service.service
        sleep 5
        if systemctl is-active --quiet main_service.service; then
            log_message "Main service restarted successfully"
        else
            log_error "Failed to restart main service"
        fi
    fi

    # NOTE: Flutter service is monitored by the Supervisor (via heartbeat mechanism)
    # The supervisor checks Flutter heartbeat every 15 seconds and restarts if needed.
    # We only log Flutter status here for informational purposes, no restart action.
    if systemctl is-active --quiet main_service.service; then
        if ! systemctl is-active --quiet flutter_app.service; then
            log_error "Flutter service is not running (Supervisor will handle restart via heartbeat)"
        fi
    else
        log_message "Main service not running, skipping Flutter check"
    fi
}

# Check for critical errors in journals
check_errors() {
    # Check for SPI_DEV_servise errors in last 5 minutes
    if journalctl -u SPI_DEV_servise.service --since "5 minutes ago" | grep -i "error\|failed\|crash" > /dev/null; then
        log_error "SPI_DEV_servise errors detected in recent logs"
    fi

    # Check for Power service errors in last 5 minutes
    if journalctl -u power_service.service --since "5 minutes ago" | grep -i "error\|failed\|crash" > /dev/null; then
        log_error "Power service errors detected in recent logs"
    fi

    # Check for main service errors in last 5 minutes
    if journalctl -u main_service.service --since "5 minutes ago" | grep -i "error\|failed\|crash" > /dev/null; then
        log_error "Main service errors detected in recent logs"
    fi

    # Check for Flutter service errors in last 5 minutes
    if journalctl -u flutter_app.service --since "5 minutes ago" | grep -i "error\|failed\|crash" > /dev/null; then
        log_error "Flutter service errors detected in recent logs"
    fi
}

# Check dependencies
check_dependencies() {
    if ! systemctl is-active --quiet NetworkManager; then
        log_error "NetworkManager is not running - main service may fail"
    fi

    if ! systemctl is-active --quiet dbus; then
        log_error "D-Bus is not running - main service may fail"
    fi

    # Check SPI hardware availability
    if [ ! -e "/dev/spidev0.0" ] && [ ! -e "/dev/spidev0.1" ]; then
        log_error "No SPI devices found - SPI_DEV_servise may fail"
    fi

    # Check I2C hardware availability (for power service)
    if [ ! -e "/dev/i2c-1" ]; then
        log_error "No I2C devices found - Power service may fail"
    fi
}

# Run checks
log_message "Monitor check started (SPI + Power + Main services, Flutter monitored by Supervisor)"
check_dependencies
check_services
check_errors
log_message "Monitor check completed"
EOF

sudo chmod +x "/home/pi/medical_device_monitor.sh"

# 7. Update cron job for monitoring
cat << 'EOF' | sudo tee "/etc/cron.d/medical_device_monitor"
# Medical Device Monitor - check every 2 minutes (4 services)
*/2 * * * * pi /home/pi/medical_device_monitor.sh
EOF

echo "✅ All 4 service files created successfully!"
echo ""

# =============================================================================
# AUTOMATED POST-SETUP CONFIGURATION
# =============================================================================

echo ""
echo "========================================"
echo "⚙️ Running automated post-setup configuration..."
echo "========================================"

# 1. Make control script executable
echo ""
echo "📝 Step 1: Setting control script permissions..."
sudo chmod +x /home/pi/medical_device_control.sh
sudo chmod +x /home/pi/medical_device_monitor.sh
echo "✓ Control scripts are now executable"

# 2. Disable getty@tty1 for direct boot (Flutter takes over display)
echo ""
echo "🖥️ Step 2: Configuring direct boot (disabling getty@tty1)..."
echo "   Current getty@tty1 status:"
sudo systemctl status getty@tty1.service --no-pager -l 2>/dev/null || echo "   getty@tty1 service not found or already disabled"

echo "   Disabling getty@tty1.service..."
sudo systemctl disable getty@tty1.service 2>/dev/null || true
sudo systemctl mask getty@tty1.service 2>/dev/null || true
sudo systemctl stop getty@tty1.service 2>/dev/null || true

echo "   Verifying getty@tty1 is disabled:"
if systemctl is-active --quiet getty@tty1.service; then
    echo "   ⚠ WARNING: getty@tty1 is still active"
else
    echo "   ✓ getty@tty1 is disabled/stopped"
fi

if systemctl is-enabled --quiet getty@tty1.service 2>/dev/null; then
    echo "   ⚠ WARNING: getty@tty1 is still enabled for boot"
else
    echo "   ✓ getty@tty1 will not start on boot"
fi

# 3. Enable medical device services for boot
echo ""
echo "✅ Step 3: Enabling medical device services for automatic startup..."
/home/pi/medical_device_control.sh enable

# 4. Run tests
echo ""
echo "🧪 Step 4: Running service tests..."
/home/pi/medical_device_control.sh test

# 5. Check dependencies
echo ""
echo "🔍 Step 5: Checking dependencies..."
/home/pi/medical_device_control.sh check-deps

echo ""
echo "========================================"
echo "✅ Post-setup configuration complete!"
echo "========================================"

# Final checks and instructions
if [ "$REBOOT_REQUIRED" = true ]; then
    echo "⚠ REBOOT REQUIRED!"
    echo "================================"
    echo "SPI configuration was modified. You must reboot before using SPI services."
    echo ""
    echo "After reboot, run these commands:"
    echo "  1. sudo systemctl daemon-reload"
    echo "  2. /home/pi/medical_device_control.sh enable"
    echo "  3. /home/pi/medical_device_control.sh test"
    echo "  4. /home/pi/medical_device_control.sh start"
    echo ""
    echo "🔄 Reboot now? (y/N):"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⏳ Rebooting in 5 seconds... Press Ctrl+C to cancel"
        sleep 5
        sudo reboot
    else
        echo "⚠ Please remember to reboot before starting the services!"
    fi
else
    echo "✓ No reboot required - SPI is already configured"
fi

echo ""
echo "========================================"
echo "✅ SETUP COMPLETE!"
echo "========================================"
echo ""
echo "📋 Your Configuration (4 Services):"
echo "  1. SPI_DEV_servise: /home/pi/spi-service (runs as root)"
echo "  2. Power Service: /home/pi/power-service (runs as root, I2C + GPIO)"
echo "  3. Main Service: /home/pi/start_main.sh (runs as root)"
echo "  4. Flutter App: /home/pi/aarch64-generic/flutter-pi"
echo ""
echo "📝 What was configured automatically:"
echo "  - Required packages installed (expect)"
echo "  - Systemd services created and enabled (4 services)"
echo "  - Control scripts made executable"
echo "  - getty@tty1 disabled (direct boot to Flutter)"
echo "  - Cron job for monitoring (every 2 minutes)"
echo ""
echo "🎮 Control Commands (after reboot):"
echo "   /home/pi/medical_device_control.sh status   # Check all status"
echo "   /home/pi/medical_device_control.sh stop     # Stop all services"
echo "   /home/pi/medical_device_control.sh start    # Start all services"
echo "   /home/pi/medical_device_control.sh restart  # Restart all services"
echo "   /home/pi/medical_device_control.sh logs     # View all logs (live)"
echo "   /home/pi/medical_device_control.sh logs power  # View power service logs only"
echo ""
echo "🚀 Service Startup Order (automatic on boot):"
echo "   1. SPI_DEV_servise (hardware initialization)"
echo "   2. Power service (battery + power management)"
echo "   3. Main service (network + supervisor)"
echo "   4. Flutter service (UI)"
echo ""

# =============================================================================
# AUTOMATIC REBOOT
# =============================================================================

echo "========================================"
echo "🔄 REBOOT REQUIRED"
echo "========================================"
echo ""
echo "⏳ System will reboot in 10 seconds to apply all changes..."
echo "   Press Ctrl+C to cancel reboot"
echo ""

for i in 10 9 8 7 6 5 4 3 2 1; do
    echo -ne "   Rebooting in $i seconds...\r"
    sleep 1
done

echo ""
echo "🔄 Rebooting now..."
sudo reboot
