#!/bin/bash
# Convenience wrapper for run-tests-remote.sh
# Allows using PI_IP environment variable or default

# Get Pi IP from environment or use default
PI_IP="${PI_IP:-192.168.29.175}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Execute run-tests-remote.sh with Pi IP and all arguments
exec "${SCRIPT_DIR}/run-tests-remote.sh" "$PI_IP" "$@"
