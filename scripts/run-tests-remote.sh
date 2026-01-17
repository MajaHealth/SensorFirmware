#!/bin/bash
# Remote Test Runner - Run tests from laptop connecting to Pi over TCP
# No SSH required, no venv setup on Pi needed

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_IP="${1}"
PI_USER="${PI_USER:-pi}"
RESTART_SERVICES=false

# Check for --restart-services flag
if [[ "$@" == *"--restart-services"* ]]; then
    RESTART_SERVICES=true
    # Remove the flag from arguments
    set -- "${@/--restart-services/}"
fi

shift || true  # Remove first argument (PI_IP)
TEST_ARGS="$@"  # Remaining arguments for pytest

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}$1${NC}"
}

# Check if Pi IP provided

if [ -z "$PI_IP" ]; then
    log_error "Usage: $0 <PI_IP> [--restart-services] [pytest arguments]"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.29.175                                    # Run all tests"
    echo "  $0 192.168.29.175 --restart-services                 # Restart services before testing"
    echo "  $0 192.168.29.175 tests/fw-app-integration/          # Run specific directory"
    echo "  $0 192.168.29.175 tests/.../test_ads1293_api.py      # Run specific file"
    echo "  $0 192.168.29.175 tests/.../test_ads1293_api.py::test_settings  # Run specific function"
    echo "  $0 192.168.29.175 -m quick                           # Run tests with marker"
    echo "  $0 192.168.29.175 -k ads1293                         # Run tests matching pattern"
    echo "  $0 192.168.29.175 --restart-services -m quick        # Restart services and run quick tests"
    echo ""
    echo "Environment variables:"
    echo "  PI_USER=pi    # SSH username (default: pi)"
    exit 1
fi

echo "=========================================="
echo "  Remote Test Runner"
echo "=========================================="
echo "Target Pi: ${PI_IP}"
echo "Test Args: ${TEST_ARGS:-tests/ (all tests)}"
echo "=========================================="
echo ""

cd "${PROJECT_ROOT}"

# Default to all tests if no args provided
if [ -z "$TEST_ARGS" ]; then
    TEST_ARGS="tests/"
    log_info "No test filter specified, running all tests"
fi

# Step 1: Setup Python virtual environment (one-time)
log_step "[1/5] Setting up Python environment..."

if [ ! -d "${PROJECT_ROOT}/venv" ]; then
    log_info "Creating virtual environment (one-time setup)..."
    python3 -m venv "${PROJECT_ROOT}/venv"
    log_info "✓ Virtual environment created"
fi

log_info "Activating virtual environment..."
source "${PROJECT_ROOT}/venv/bin/activate"

# Check if dependencies need installing
if ! python -c "import pytest" 2>/dev/null; then
    log_info "Installing test dependencies (one-time setup)..."
    pip install --quiet --upgrade pip
    pip install --quiet -r "${PROJECT_ROOT}/tests/requirements.txt"
    log_info "✓ Dependencies installed"
else
    log_info "✓ Dependencies already installed"
fi

# Step 2: Test Pi connectivity
log_step "[2/5] Testing connectivity to Pi..."

log_info "Checking if Pi is reachable..."
if ! ping -c 1 -W 2 ${PI_IP} >/dev/null 2>&1; then
    log_error "Cannot reach Pi at ${PI_IP}"
    log_error "Please check:"
    log_error "  1. Pi is powered on"
    log_error "  2. Pi is on same network"
    log_error "  3. IP address is correct"
    exit 1
fi
log_info "✓ Pi is reachable at ${PI_IP}"

# Handle service restart if requested
if [ "$RESTART_SERVICES" = true ]; then
    log_info "Restarting firmware services on Pi..."

    # Stop any running services (from any location)
    log_info "Stopping any running services..."
    ssh -t ${PI_USER}@${PI_IP} "sudo pkill -f 'spi-service|power-service' 2>/dev/null; exit 0" || true
    sleep 1

    # Start services from deployment location
    log_info "Starting services from /opt/sensor-firmware/bin..."
    ssh ${PI_USER}@${PI_IP} "bash -c '
        cd /opt/sensor-firmware/bin
        sudo nohup ./spi-service > /tmp/spi-service.log 2>&1 < /dev/null &
        sudo nohup ./power-service > /tmp/power-service.log 2>&1 < /dev/null &
        sleep 1
    '"
    sleep 3  # Wait for services to initialize

    # Verify services are running
    log_info "Verifying services started..."
    ssh ${PI_USER}@${PI_IP} "pgrep -f spi-service && echo 'spi-service running' || echo 'spi-service NOT running'"
    ssh ${PI_USER}@${PI_IP} "pgrep -f power-service && echo 'power-service running' || echo 'power-service NOT running'"
    log_info "✓ Services restarted"
fi

# Check if services are running (test port connectivity)
log_info "Checking if firmware services are accessible..."
SERVICES_OK=true

declare -A services=(
    [1293]="ADS1293"
    [30009]="MAX30009"
    [2812]="WS2812"
    [501]="Power"
)

for port in "${!services[@]}"; do
    if nc -z -w 2 ${PI_IP} ${port} 2>/dev/null; then
        log_info "  ✓ ${services[$port]} service (port ${port})"
    else
        log_warn "  ✗ ${services[$port]} service (port ${port}) not accessible"
        SERVICES_OK=false
    fi
done

if [ "$SERVICES_OK" = false ]; then
    echo ""
    log_error "Some firmware services are not running on Pi!"
    echo ""
    echo "Options to fix:"
    echo "  1. Run this script with --restart-services flag:"
    echo "     $0 ${PI_IP} --restart-services"
    echo ""
    echo "  2. Or manually start services on Pi (${PI_USER}@${PI_IP}):"
    echo "     ssh ${PI_USER}@${PI_IP}"
    echo "     cd /opt/sensor-firmware/bin"
    echo "     sudo ./spi-service > /tmp/spi-service.log 2>&1 &"
    echo "     sudo ./power-service > /tmp/power-service.log 2>&1 &"
    echo ""
    exit 1
fi

log_info "✓ All required services are accessible"

# Step 3: Create results directory
log_step "[3/5] Preparing results directory..."

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULTS_DIR="${PROJECT_ROOT}/analysis/data/${TIMESTAMP}"
mkdir -p "${RESULTS_DIR}"

log_info "Results will be saved to: ${RESULTS_DIR}"

# Step 4: Run pytest from laptop
log_step "[4/5] Running tests from laptop..."

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Test Execution"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Set environment variable for remote Pi IP
export PI_TARGET_IP="${PI_IP}"

# Run pytest with all provided arguments
cd "${PROJECT_ROOT}"
pytest ${TEST_ARGS} \
    -v \
    --html="${RESULTS_DIR}/test_report.html" \
    --self-contained-html \
    --tb=short \
    --maxfail=5 \
    || TEST_EXIT_CODE=$?

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Step 5: Display results
log_step "[5/5] Test Results"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Results Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Results location: ${RESULTS_DIR}"
echo ""

if [ -f "${RESULTS_DIR}/test_report.html" ]; then
    echo "HTML Report:  ${RESULTS_DIR}/test_report.html"
fi

if ls ${RESULTS_DIR}/*.jsonl >/dev/null 2>&1; then
    echo "Data files:"
    ls -lh ${RESULTS_DIR}/*.jsonl 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Open HTML report in browser
if [ -f "${RESULTS_DIR}/test_report.html" ]; then
    log_info "Opening HTML report in browser..."
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "${RESULTS_DIR}/test_report.html" 2>/dev/null || true
    elif command -v wslview >/dev/null 2>&1; then
        # WSL support for opening in Windows browser
        wslview "${RESULTS_DIR}/test_report.html" 2>/dev/null || true
    fi
fi

# Exit with pytest's exit code
if [ -n "$TEST_EXIT_CODE" ]; then
    log_warn "Some tests failed (exit code: ${TEST_EXIT_CODE})"
    exit ${TEST_EXIT_CODE}
else
    log_info "All tests passed!"
    exit 0
fi
