#!/bin/bash
#
# Relaunch this script under stdbuf for line-buffered I/O:
#
if [ -z "$UNBUFFERED" ]; then
  export UNBUFFERED=1
  exec stdbuf -oL -eL "$0" "$@"
fi

# Main service startup script with date-based log rotation
# This script checks for network manager and backlight before starting the main service

# =============================================================================
# LOG ROTATION FUNCTION
# =============================================================================
archive_old_logs() {
    local log_dir="/home/pi/logs"
    local archive_dir="/home/pi/logs/archive"
    local service_name="main_service"
    local today_log="${service_name}-$(date +%Y-%m-%d).log"

    # Create archive directory if needed
    mkdir -p "$archive_dir"

    # Move logs that are NOT today's log to archive
    find "$log_dir" -maxdepth 1 -name "${service_name}-*.log" \
         ! -name "$today_log" -exec mv {} "$archive_dir/" \; 2>/dev/null
}

# =============================================================================
# LOG SETUP
# =============================================================================
# Archive old logs before starting new log
archive_old_logs

# Set up today's dated log file
LOG_FILE="/home/pi/logs/main_service-$(date +%Y-%m-%d).log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "Starting main service checks..."

# Check if NetworkManager is running
check_network_manager() {
    if systemctl is-active --quiet NetworkManager; then
        log_message "NetworkManager is active"
        return 0
    else
        log_message "NetworkManager is not active"
        return 1
    fi
}

# Check if backlight directory exists
check_backlight() {
    if [ -d "/sys/class/backlight" ]; then
        log_message "Backlight directory exists at /sys/class/backlight"
        return 0
    else
        log_message "Backlight directory not found at /sys/class/backlight"
        return 1
    fi
}

# Wait for prerequisites
wait_for_prerequisites() {
    local max_wait=60  # Maximum wait time in seconds
    local wait_time=0

    while [ $wait_time -lt $max_wait ]; do
        if check_network_manager && check_backlight; then
            log_message "All prerequisites met"
            return 0
        fi

        log_message "Waiting for prerequisites... (${wait_time}s/${max_wait}s)"
        sleep 2
        wait_time=$((wait_time + 2))
    done

    log_message "Timeout waiting for prerequisites"
    return 1
}

# Main execution
if wait_for_prerequisites; then
    log_message "Starting main application..."
    log_message "Current working directory: $(pwd)"
    log_message "Changing to /home/pi directory"
    cd /home/pi
    log_message "Executing main with unbuffered logging..."
    # CRITICAL FIX: Remove nested sudo and use absolute path
    exec unbuffer /home/pi/main >> $LOG_FILE 2>&1
else
    log_message "Failed to meet prerequisites. Exiting."
    exit 1
fi
