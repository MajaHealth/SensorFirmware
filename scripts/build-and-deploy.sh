#!/bin/bash
set -e

PI_IP="${PI_IP:-192.168.1.4}"
PI_USER="${PI_USER:-pi}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_TESTS="${RUN_TESTS:-0}"
TEST_FILTER="${TEST_FILTER:-}"  # Optional: filter tests (e.g., "test_ads1293_api.py" or "test_ads1293_api.py::test_ads1293_settings_configuration")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "=========================================="
echo "  Build & Deploy Pipeline"
echo "=========================================="
echo "Target: ${PI_USER}@${PI_IP}"
echo "Run Tests: ${RUN_TESTS}"
echo "=========================================="

# Step 1: Build
log_step "[1/4] Building firmware..."
cd ${PROJECT_ROOT}

# Build using Docker
log_info "Building with Docker..."
docker build --target artifacts -t sensor-firmware-build -f docker/Dockerfile . || {
    log_error "Docker build failed"
    exit 1
}

# Extract artifacts
log_info "Extracting build artifacts..."
docker create --name temp-container sensor-firmware-build
mkdir -p build-output/bin
docker cp temp-container:/build/bin/. build-output/bin/
docker rm temp-container

log_info "✓ Build complete"

# Step 2: Verify
log_step "[2/4] Verifying binaries..."
cd ${PROJECT_ROOT}/build-output/bin
for binary in *-service; do
    if [ -f "$binary" ]; then
        log_info "Checking $binary..."
        file $binary
    fi
done

# Step 3: Deploy
log_step "[3/4] Deploying to CM4..."
log_info "Deploying binaries to ${PI_USER}@${PI_IP}:/opt/sensor-firmware/bin/..."

# Create directory on CM4
ssh ${PI_USER}@${PI_IP} "mkdir -p /opt/sensor-firmware/bin"

# Copy binaries
scp ${PROJECT_ROOT}/build-output/bin/*-service ${PI_USER}@${PI_IP}:/opt/sensor-firmware/bin/

log_info "✓ Deployment complete"

# Step 4: Run tests (if enabled)
if [ "$RUN_TESTS" = "1" ]; then
    log_step "[4/4] Running Hardware Tests on CM4..."

    # Create results directory with timestamp
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    RESULTS_DIR="${PROJECT_ROOT}/analysis/data/${TIMESTAMP}"
    mkdir -p "${RESULTS_DIR}"

    log_info "Results will be saved to: ${RESULTS_DIR}"

    # Transfer tests to CM4
    log_info "Transferring test suite to CM4..."
    ssh ${PI_USER}@${PI_IP} "mkdir -p /tmp/sensor-tests /tmp/test-results"

    rsync -avz --quiet \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        ${PROJECT_ROOT}/tests/ \
        ${PI_USER}@${PI_IP}:/tmp/sensor-tests/

    log_info "✓ Tests transferred"

    # Check if pytest is installed
    log_info "Checking pytest installation on CM4..."
    if ! ssh ${PI_USER}@${PI_IP} "which pytest 2>/dev/null"; then
        log_warn "pytest not found, installing dependencies..."
        ssh ${PI_USER}@${PI_IP} "pip3 install -r /tmp/sensor-tests/requirements.txt"
        log_info "✓ Dependencies installed"
    fi

    # Run pytest on CM4
    if [ -n "$TEST_FILTER" ]; then
        log_info "Running specific tests: ${TEST_FILTER}"
    else
        log_info "Running all tests..."
    fi
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Test Execution on CM4"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    ssh -t ${PI_USER}@${PI_IP} "
        cd /tmp/sensor-tests && \
        pytest ${TEST_FILTER:-.} \
            --html=/tmp/test-results/test_report.html \
            --self-contained-html \
            -v \
            --tb=short \
            --maxfail=5
    " || {
        log_warn "Some tests failed (will still fetch results)"
    }

    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Fetch results from CM4
    log_info "Fetching test results from CM4..."
    rsync -avz --quiet \
        ${PI_USER}@${PI_IP}:/tmp/test-results/ \
        "${RESULTS_DIR}/"

    log_info "✓ Results saved to: ${RESULTS_DIR}"

    # Cleanup CM4
    log_info "Cleaning up CM4..."
    ssh ${PI_USER}@${PI_IP} "rm -rf /tmp/sensor-tests /tmp/test-results"
    log_info "✓ Cleanup complete"

    # Display results summary
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Test Results Summary"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Results location: ${RESULTS_DIR}"
    echo ""

    if [ -f "${RESULTS_DIR}/test_report.html" ]; then
        echo "HTML Report:  ${RESULTS_DIR}/test_report.html"
    fi

    if ls ${RESULTS_DIR}/*.jsonl >/dev/null 2>&1; then
        echo "Data files:"
        ls -lh ${RESULTS_DIR}/*.jsonl | awk '{print "  - " $9 " (" $5 ")"}'
    fi

    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Open HTML report in browser (optional)
    if [ -f "${RESULTS_DIR}/test_report.html" ]; then
        if command -v xdg-open >/dev/null 2>&1; then
            log_info "Opening HTML report in browser..."
            xdg-open "${RESULTS_DIR}/test_report.html" 2>/dev/null || true
        elif command -v open >/dev/null 2>&1; then
            log_info "Opening HTML report in browser..."
            open "${RESULTS_DIR}/test_report.html" 2>/dev/null || true
        fi
    fi

    log_info "Tests complete! Ready for analysis."
else
    log_info "Skipping tests (set RUN_TESTS=1 to enable)"
fi

echo ""
echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="
