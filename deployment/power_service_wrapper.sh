#!/bin/bash
# Wrapper script to run power-service with date-based log rotation

# =============================================================================
# LOG ROTATION FUNCTION
# =============================================================================
archive_old_logs() {
    local log_dir="/home/pi/logs"
    local archive_dir="/home/pi/logs/archive"
    local service_name="power_service"
    local today_log="${service_name}-$(date +%Y-%m-%d).log"

    # Create archive directory if needed
    mkdir -p "$archive_dir"

    # Move logs that are NOT today's log to archive
    find "$log_dir" -maxdepth 1 -name "${service_name}-*.log" \
         ! -name "$today_log" -exec mv {} "$archive_dir/" \; 2>/dev/null
}

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
export HOME=/home/pi
export USER=root
export LOGNAME=root
export SHELL=/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export TERM=xterm-256color

cd /home/pi

# =============================================================================
# LOG ROTATION EXECUTION
# =============================================================================
# Archive old logs at boot (before starting service)
archive_old_logs

# Set up today's dated log file
LOG_DIR="/home/pi/logs"
LOG_FILE="$LOG_DIR/power_service-$(date +%Y-%m-%d).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log startup to syslog
logger "power_service wrapper starting - logging to $LOG_FILE"

# Log startup to dated log file
echo "$(date '+%Y-%m-%d %H:%M:%S') - power_service wrapper starting (PID: $$)" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Log file: $LOG_FILE" >> "$LOG_FILE"

# =============================================================================
# RUN SERVICE WITH LOG REDIRECTION
# =============================================================================
# Run service with output to dated log (append mode)
exec /home/pi/power-service "$@" >> "$LOG_FILE" 2>&1
