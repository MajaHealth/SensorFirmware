# Multi-stage Dockerfile for Sensor Firmware Build
# Target: Raspberry Pi CM4 (ARM64/aarch64)

FROM debian:bookworm-slim AS builder

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Enable arm64 architecture
RUN dpkg --add-architecture arm64

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    cmake \
    make \
    file \
    libc6-dev-arm64-cross \
    linux-libc-dev-arm64-cross \
    libc6:arm64 \
    libc6-dev:arm64 \
    libi2c-dev:arm64 \
    libgpiod-dev:arm64 \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /work

# Copy toolchain file
COPY docker/arm-toolchain.cmake /work/toolchain.cmake

# Set environment for reproducible builds
ENV SOURCE_DATE_EPOCH=1609459200

# Display toolchain info
RUN echo "=== Toolchain Info ===" && \
    aarch64-linux-gnu-gcc --version && \
    cmake --version

# Build stage
FROM builder AS build

# Copy source code
COPY . /work

# Create build directory and build
RUN mkdir -p build-output && \
    cd build-output && \
    cmake .. \
        -DCMAKE_TOOLCHAIN_FILE=/work/toolchain.cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_VERBOSE_MAKEFILE=ON && \
    cmake --build . -j$(nproc)

# Generate hashes
RUN cd build-output/bin && \
    for binary in *-service; do \
        sha256sum "$binary" > "$binary.sha256"; \
    done

# List artifacts
RUN ls -lh build-output/bin/

# Artifact export stage
FROM scratch AS artifacts
COPY --from=build /work/build-output/bin/ /
