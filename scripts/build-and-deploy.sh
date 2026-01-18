#!/bin/bash
set -e

PI_IP="${PI_IP:-192.168.29.197}"
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
# Build the 'build' stage to extract binaries (scratch images can't be extracted directly)
docker build --target build -t sensor-firmware-build-stage -f docker/Dockerfile . > /dev/null 2>&1

# Clean and recreate output directory to avoid tar conflicts
# Use sudo because Docker may have created files with root ownership
sudo rm -rf build-output/bin
mkdir -p build-output/bin

# Extract with overwrite flag
docker run --rm sensor-firmware-build-stage tar -C /work/build-output/bin -cf - . | tar -C build-output/bin -xf -

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

# Stop any running services before deployment
log_info "Stopping any running services..."
ssh -t ${PI_USER}@${PI_IP} "sudo pkill -f 'spi-service|power-service' 2>/dev/null; exit 0" || true
sleep 1

# Create directory on CM4
ssh -t ${PI_USER}@${PI_IP} "sudo mkdir -p /opt/sensor-firmware/bin && sudo chown -R ${PI_USER}:${PI_USER} /opt/sensor-firmware" || true

# Copy binaries
scp ${PROJECT_ROOT}/build-output/bin/*-service ${PI_USER}@${PI_IP}:/opt/sensor-firmware/bin/

log_info "Deployment complete"

# Step 4: Run tests (if enabled)
if [ "$RUN_TESTS" = "1" ]; then
    log_step "[4/4] Running Hardware Tests on CM4..."

    echo ""
    log_warn "IMPORTANT: Make sure the firmware services are running on CM4!"
    echo ""
    echo "On CM4, run:"
    echo "  cd /opt/sensor-firmware/bin"
    echo "Current directory: $(pwd)"
    echo "  ./spi-service &"
    echo "  ./power-service &"
    echo ""
    read -p "Press ENTER when services are running and ready for testing..."
    echo ""

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

    # Setup Python virtual environment and install dependencies
    log_info "Setting up Python environment on CM4..."
    ssh ${PI_USER}@${PI_IP} "
        if [ ! -d /tmp/sensor-venv ]; then
            python3 -m venv /tmp/sensor-venv
        fi
        source /tmp/sensor-venv/bin/activate
        pip install --quiet -r /tmp/sensor-tests/requirements.txt
    "
    log_info "✓ Python environment ready"

    # Start services before running tests
    log_info "Starting services on CM4..."
    ssh ${PI_USER}@${PI_IP} "bash -c '
        cd /opt/sensor-firmware/bin
        sudo nohup ./spi-service > /tmp/spi-service.log 2>&1 < /dev/null &
        sudo nohup ./power-service > /tmp/power-service.log 2>&1 < /dev/null &
        sleep 1
    '"
    sleep 3  # Wait for services to initialize

    # Verify services are running
    log_info "Verifying services..."
    ssh ${PI_USER}@${PI_IP} "pgrep -f spi-service && echo 'spi-service running' || echo 'spi-service NOT running'"
    ssh ${PI_USER}@${PI_IP} "pgrep -f power-service && echo 'power-service running' || echo 'power-service NOT running'"
    log_info "✓ Services started"

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
        source /tmp/sensor-venv/bin/activate && \
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

    # Fetch service logs for debugging
    log_info "Fetching service logs..."
    rsync -avz --quiet \
        ${PI_USER}@${PI_IP}:/tmp/spi-service.log \
        "${RESULTS_DIR}/" 2>/dev/null || true
    rsync -avz --quiet \
        ${PI_USER}@${PI_IP}:/tmp/power-service.log \
        "${RESULTS_DIR}/" 2>/dev/null || true

    # Stop services and cleanup CM4
    log_info "Stopping services and cleaning up CM4..."
    ssh -t ${PI_USER}@${PI_IP} "
        sudo pkill -f 'spi-service|power-service' 2>/dev/null || true
        rm -rf /tmp/sensor-tests /tmp/test-results /tmp/sensor-venv /tmp/spi-service.log /tmp/power-service.log
        exit 0
    " || true
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
