#!/bin/bash
set -e

PI_IP="192.168.1.4"
PI_USER="pi"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================="
echo "  Build & Deploy Pipeline"
echo "=========================================="

# Step 1: Build
echo "[1/3] Building in Docker..."
${PROJECT_ROOT}/scripts/build.sh

# Step 2: Verify
echo "[2/3] Verifying binaries..."
cd ${PROJECT_ROOT}/build-output/bin
for binary in *-service; do
    if [ -f "$binary" ]; then
        file $binary
        sha256sum -c $binary.sha256
    fi
done

# Step 3: Deploy
echo "[3/3] Deploying to Pi..."
${PROJECT_ROOT}/scripts/deploy.sh

echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="