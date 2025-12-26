# Multi-stage Dockerfile for Sensor Firmware Build
# Target: Raspberry Pi CM4 (ARM)

FROM debian:bookworm-slim AS builder

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Enable armhf architecture
RUN dpkg --add-architecture armhf

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    cmake \
    make \
    file \
    libc6-dev-armhf-cross \
    linux-libc-dev-armhf-cross \
    libc6:armhf \
    libc6-dev:armhf \
    libi2c-dev:armhf \
    libgpiod-dev:armhf \
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
    arm-linux-gnueabihf-gcc --version && \
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