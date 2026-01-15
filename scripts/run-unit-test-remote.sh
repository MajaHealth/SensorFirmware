#!/bin/bash
#
# Run unit tests on CM4 remotely from laptop
#
# Usage:
#   ./scripts/run-unit-test-remote.sh <PI_IP> <test_file>
#
# Examples:
#   ./scripts/run-unit-test-remote.sh 192.168.1.100 tests/unit_tests/power-service/test_106_soft_shutdown_denied.py
#   PI_IP=192.168.1.100 ./scripts/run-unit-test-remote.sh test_106
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PI_IP="${1:-${PI_IP}}"
TEST_FILE="${2}"
REMOTE_DIR="~/sensor_test_project"
REMOTE_TEST_DIR="${REMOTE_DIR}/tests/unit_tests"

# Help message
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    echo "Usage: $0 <PI_IP> [test_file]"
    echo ""
    echo "Run unit tests on CM4 remotely"
    echo ""
    echo "Arguments:"
    echo "  PI_IP       IP address of Raspberry Pi CM4"
    echo "  test_file   Optional: specific test file or test number"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.1.100 tests/unit_tests/power-service/test_106_soft_shutdown_denied.py"
    echo "  $0 192.168.1.100 test_106"
    echo "  $0 192.168.1.100  # Run all unit tests"
    echo ""
    echo "Environment variables:"
    echo "  PI_IP       Can be set instead of passing as argument"
    echo ""
    exit 0
fi

# Check PI_IP is provided
if [[ -z "$PI_IP" ]]; then
    echo -e "${RED}Error: PI_IP not provided${NC}"
    echo "Usage: $0 <PI_IP> [test_file]"
    echo "   or: PI_IP=192.168.x.x $0 [test_file]"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Remote Unit Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Target CM4: ${YELLOW}${PI_IP}${NC}"
echo ""

# Resolve test file path
if [[ -n "$TEST_FILE" ]]; then
    # If just test number provided (e.g., "test_106")
    if [[ "$TEST_FILE" =~ ^test_[0-9]+$ ]]; then
        TEST_FILE="tests/unit_tests/power-service/${TEST_FILE}_soft_shutdown_denied.py"
        echo -e "Resolved test: ${YELLOW}${TEST_FILE}${NC}"
    fi

    # Check if test file exists locally
    if [[ ! -f "$TEST_FILE" ]]; then
        echo -e "${RED}Error: Test file not found: ${TEST_FILE}${NC}"
        exit 1
    fi

    REMOTE_TEST_PATH="${REMOTE_TEST_DIR}/$(basename $(dirname ${TEST_FILE}))/$(basename ${TEST_FILE})"
else
    # Run all unit tests
    TEST_FILE="tests/unit_tests/"
    REMOTE_TEST_PATH="${REMOTE_TEST_DIR}/"
    echo -e "Running: ${YELLOW}All unit tests${NC}"
fi

echo ""

# Step 1: Check connectivity
echo -e "${GREEN}[1/5]${NC} Checking CM4 connectivity..."
if ! ping -c 1 -W 2 $PI_IP > /dev/null 2>&1; then
    echo -e "${RED}Error: Cannot reach CM4 at ${PI_IP}${NC}"
    exit 1
fi
echo -e "  ✓ CM4 is reachable"

# Step 2: Setup remote directory structure
echo -e "${GREEN}[2/5]${NC} Setting up remote directories..."
ssh pi@$PI_IP "mkdir -p ${REMOTE_TEST_DIR}/power-service ${REMOTE_TEST_DIR}/spi-service ${REMOTE_TEST_DIR}/gpio ${REMOTE_TEST_DIR}/shutdown" 2>/dev/null
echo -e "  ✓ Remote directories ready"

# Step 3: Copy test files
echo -e "${GREEN}[3/5]${NC} Copying test files to CM4..."

if [[ -f "$TEST_FILE" ]]; then
    # Copy specific test file
    TEST_DIR=$(dirname ${TEST_FILE})
    scp -q ${TEST_FILE} pi@$PI_IP:${REMOTE_TEST_PATH}

    # Copy __init__.py files
    scp -q tests/unit_tests/__init__.py pi@$PI_IP:${REMOTE_TEST_DIR}/ 2>/dev/null || true
    if [[ -f "${TEST_DIR}/__init__.py" ]]; then
        scp -q ${TEST_DIR}/__init__.py pi@$PI_IP:${REMOTE_TEST_DIR}/$(basename $(dirname ${TEST_FILE}))/ 2>/dev/null || true
    fi

    echo -e "  ✓ Test file copied: $(basename ${TEST_FILE})"
else
    # Copy all unit tests
    scp -r -q tests/unit_tests/* pi@$PI_IP:${REMOTE_TEST_DIR}/
    echo -e "  ✓ All unit test files copied"
fi

# Step 4: Ensure pytest is installed on CM4
echo -e "${GREEN}[4/5]${NC} Checking pytest on CM4..."
ssh pi@$PI_IP << 'REMOTE_SETUP'
cd ~/sensor_test_project

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and check/install pytest
source venv/bin/activate

if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "  Installing pytest and dependencies..."
    pip install -q pytest RPi.GPIO pyyaml
fi

pytest --version
REMOTE_SETUP

echo -e "  ✓ pytest is ready"

# Step 5: Run the test on CM4
echo -e "${GREEN}[5/5]${NC} Running test on CM4..."
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Test Output (from CM4):${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Run test and capture exit code
ssh -t pi@$PI_IP << REMOTE_TEST
cd ~/sensor_test_project
source venv/bin/activate

# Run the test
pytest ${REMOTE_TEST_PATH} -v -s
REMOTE_TEST

EXIT_CODE=$?

echo ""
echo -e "${YELLOW}========================================${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Test completed successfully!${NC}"
else
    echo -e "${RED}✗ Test failed (exit code: ${EXIT_CODE})${NC}"
fi

echo -e "${YELLOW}========================================${NC}"

exit $EXIT_CODE
