# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sensor firmware for Raspberry Pi CM4 that provides hardware interface services for medical/biometric sensors. The firmware is built as separate services that communicate via JSON over TCP sockets.

**Target Platform:** Raspberry Pi CM4 (ARM Cortex-A72)
**Build System:** CMake with Docker-based cross-compilation
**Language:** C++17 with some C components

## Build Commands

### Standard Build (Docker-based cross-compilation)
```bash
# Build for ARM target using Docker
docker build --target artifacts -t sensor-firmware-build -f docker/Dockerfile .
docker create --name temp-container sensor-firmware-build
docker cp temp-container:/. build-output/bin/
docker rm temp-container
```

### Native CMake Build
```bash
# Configure for ARM cross-compilation
mkdir -p build-output
cd build-output
cmake .. -DCMAKE_TOOLCHAIN_FILE=../docker/arm-toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build . -j$(nproc)

# For debug builds
cmake .. -DCMAKE_TOOLCHAIN_FILE=../docker/arm-toolchain.cmake -DCMAKE_BUILD_TYPE=Debug
cmake --build .

# Native build (development/testing only)
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .
```

### Build Outputs
- Binaries: `build-output/bin/spi-service`, `build-output/bin/power-service`
- SHA256 hashes: Generated automatically as `.sha256` files alongside binaries
- Config files: Installed to `/opt/sensor-firmware/config`
- Calibration data: `spi-service` includes calibration files in `calib/`

### Additional Build Targets
```bash
# Generate SHA256 hashes for verification
cmake --build build-output --target generate-hashes

# Generate SBOM (Software Bill of Materials)
cmake --build build-output --target generate-sbom

# Build and deploy pipeline (requires Pi configuration)
./scripts/build-and-deploy.sh

# Build, deploy, and run tests on CM4
PI_IP=192.168.1.21 RUN_TESTS=1 ./scripts/build-and-deploy.sh

# Run specific test filter
PI_IP=192.168.1.21 RUN_TESTS=1 TEST_FILTER="test_ads1293_api.py" ./scripts/build-and-deploy.sh
```

## Testing Commands

### Build with Tests Enabled

```bash
# Build all tests (unit + integration)
cmake -B build-output -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build-output

# Build only unit tests (gtest)
cmake -B build-output -DBUILD_UNIT_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build-output

# Build only integration tests (pytest)
cmake -B build-output -DBUILD_INTEGRATION_TESTS=ON
cmake --build build-output

# Build with mocks disabled (for hardware testing)
cmake -B build-output -DBUILD_TESTS=ON -DENABLE_MOCKS=OFF
cmake --build build-output
```

### Run Tests

```bash
# Run all tests
cd build-output
ctest --output-on-failure

# Run only unit tests
ctest -L unit

# Run only integration tests
ctest -L integration

# Run specific service tests
ctest -L spi-service
ctest -L power-service

# Run specific test category
ctest -R GPIO        # All GPIO tests
ctest -R MAX30009    # All MAX30009 tests
ctest -R ADS1293     # All ADS1293 tests

# Run a single test by name
ctest -R test_ADS1293_lib --output-on-failure

# Run pytest directly with more options
pytest ../services/spi-service/tests/integration/ -v
pytest ../services/power-service/tests/integration/ -v

# Run a single pytest file
pytest ../tests/fw-app-integration/test_ads1293_api.py -v

# Run a single test function
pytest ../tests/fw-app-integration/test_ads1293_api.py::test_ads1293_settings_configuration -v

# Run pytest with markers
pytest -m tcp        # Only TCP protocol tests
pytest -m slow       # Only slow/stress tests
```

### Install pytest for Integration Tests

```bash
pip3 install -r tests/requirements.txt
```

### Test Structure

Tests are organized per service:
- `services/spi-service/tests/unit/` - C++ unit tests (gtest)
- `services/spi-service/tests/integration/` - Python integration tests (pytest)
- `services/power-service/tests/unit/` - C++ unit tests (gtest)
- `services/power-service/tests/integration/` - Python integration tests (pytest)
- `tests/` - System-level integration tests
- `tests/common/tcp_client.py` - Reusable TCP client for test fixtures

### Mock Drivers

Mock implementations in `services/*/tests/mocks/` enable unit testing without hardware:
- `mock_SPI_driver.h/cpp` - Simulates SPI transactions
- `mock_GPIO_driver.h/cpp` - Simulates GPIO state
- `mock_SMBus_driver.h/cpp` - Simulates I2C/SMBus (power-service)

Build with mocks: `cmake -DBUILD_TESTS=ON -DENABLE_MOCKS=ON`

### Remote Testing (Run from Laptop)

Run tests from your laptop connecting to Pi over network (no SSH, no venv on Pi):

```bash
# First time: Script auto-creates venv and installs dependencies
./scripts/run-tests-remote.sh 192.168.29.175

# Restart services before testing (kills old instances, starts fresh)
./scripts/run-tests-remote.sh 192.168.29.175 --restart-services

# Run specific tests
./scripts/run-tests-remote.sh 192.168.29.175 tests/fw-app-integration/test_ads1293_api.py
./scripts/run-tests-remote.sh 192.168.29.175 tests/fw-app-integration/test_ads1293_api.py::test_ads1293_settings_configuration

# Run by marker
./scripts/run-tests-remote.sh 192.168.29.175 -m quick
./scripts/run-tests-remote.sh 192.168.29.175 -m ads1293

# Run with pytest options
./scripts/run-tests-remote.sh 192.168.29.175 tests/ -vv --maxfail=1

# Restart services and run quick tests
./scripts/run-tests-remote.sh 192.168.29.175 --restart-services -m quick

# Or use convenience wrapper
PI_IP=192.168.29.175 ./scripts/test.sh
./scripts/test.sh tests/fw-app-integration/  # Uses default IP
```

**Requirements:**
- Firmware services must be running on Pi
- Pi must be on same network as laptop
- Ports 1293, 30009, 2812, 501 must be accessible

**How it works:**
- Tests run ON your laptop (not on Pi)
- Tests send TCP commands to Pi over network
- Pi runs firmware services only
- Results saved locally on laptop

**Benefits:**
- ✅ Much faster (no file transfers, no remote venv)
- ✅ Results saved directly on laptop
- ✅ One-time venv setup on laptop
- ✅ Full pytest argument support (files, functions, markers, options)
- ✅ Supports individual test files and specific test functions
- ✅ Optional `--restart-services` flag to ensure testing against fresh deployment

## Architecture

### Service-Based Design

The firmware consists of independent services that run as separate processes:

1. **spi-service** (port 1293, 30009, 2812)
   - Manages SPI-connected sensors and peripherals
   - ADS1293: ECG/biopotential sensor (port 1293)
   - MAX30009: Bio-impedance sensor (port 30009)
   - WS2812: LED control (port 2812)

2. **power-service** (port 501)
   - Power management and battery monitoring
   - I2C-based battery info via SMBus
   - Button handling and buzzer control

### Communication Architecture

Each service follows the same pattern:
- **JSON_TCP_sever**: TCP server accepting JSON requests on specific ports
- **Process objects**: Device-specific logic (`ADS1293_process`, `MAX30009_process`, etc.)
- **Atomic flags**: Lock-free request/response handoff between TCP thread and main loop
- **Main loop**: Polls for requests, processes them, and returns JSON responses

```
Client → TCP Socket → JSON Request → Process Object → Hardware Interface
       ← TCP Socket ← JSON Response ← Process Object ← Hardware Data
```

### VTK (Vendor Toolkit) Layer

Shared abstraction layer used across services:
- `VT_register_process_interface.h`: Register read/write abstraction (virtual methods: `load_from_register`, `write_to_register`)
- `VT_GPIO_interface.h`: GPIO control abstraction (direction, state management)
- `VT_sync_data_stream_interface.h`: Data streaming interface (virtual method: `send_byte_array`)
- `VT_SMBUS_interface.h`: I2C/SMBus communication (power-service only)

**How VTK bridges device libraries and hardware:**
1. Device libraries (e.g., `ADS1293_LIB`) are written against VTK interfaces
2. Hardware drivers (`SPI_hard_driver_cls`, `GPIO_driver_cls`) implement these interfaces
3. At service initialization, hardware driver instances are passed to device library constructors
4. Example: `ADS1293_LIB` constructor takes `VT_sync_data_stream_interface*`, which is satisfied by `SPI_hard_driver_cls`

This design allows device libraries to be hardware-agnostic and reusable across platforms.

### Hardware Driver Layer

Low-level hardware access in `hard_driver/` directories:
- **`GPIO_driver_cls`**: Implements `VT_GPIO_interface` using libgpiod for GPIO manipulation
  - Uses Linux character device interface (`/dev/gpiochipN`)
  - Supports input, output, and release modes
- **`SPI_hard_driver_cls`**: Implements `VT_sync_data_stream_interface` using Linux SPI subsystem
  - Opens `/dev/spidevX.Y` devices
  - Configures transfer parameters (5MHz speed, mode, bits per word)
  - Full-duplex communication via `ioctl` with `SPI_IOC_MESSAGE`

### Third-Party Libraries

- **WS281x**: C library for WS2812 LED control (compiled as static library)
- **nlohmann/json** (`json.hpp`): JSON parsing (header-only)

## Code Conventions

### Service Structure
Each service follows this organization:
```
services/<service-name>/
├── CMakeLists.txt       # Service-specific build config
├── src/                 # Main entry point and process implementations
├── include/             # Process class headers, JSON_TCP_sever
├── hard_driver/         # Hardware abstraction (GPIO, SPI, I2C)
├── VTK/                 # Vendor toolkit interfaces
└── <DEVICE>_LIB/        # Device-specific libraries (e.g., ADS1293_LIB)
```

### Main Loop Pattern

Services use polling-based architecture with atomic flags for lock-free communication:

```cpp
while(1) {
    if (request_ready_flag.load(std::memory_order_acquire)) {
        response = process_obj.process_JSON_line(request_json);
        request_ready_flag.store(false, std::memory_order_release);
        if (!response_ready_flag.load()) {
            response_json = response;
            response_ready_flag.store(true, std::memory_order_release);
        }
    }
    // Service-specific periodic tasks
    delay(100);
}
```

**Key aspects of this pattern:**
- Each device has its own `JSON_TCP_sever` instance running in a separate thread
- TCP server sets `request_ready_flag` when new JSON arrives
- Main loop processes request via `process_JSON_line()` and sets `response_ready_flag`
- TCP server reads response and sends it back to client
- This enables concurrent handling of multiple devices without blocking

**Service-specific timing:**
- **spi-service**: 500μs loop delay, 1-second sync marks for sensor synchronization
- **power-service**: 100ms loop delay, battery reading throttled to every ~3 seconds
- **spi-service** also handles asynchronous calibration responses via `calibration_process()`

### Cross-Compilation Notes

- Always use the ARM toolchain (`docker/arm-toolchain.cmake`) for production builds
- Native builds are for development only and won't run on CM4
- Compiler flags target Cortex-A72 with NEON-FP-ARMV8
- Builds are reproducible via `SOURCE_DATE_EPOCH` in Docker

## File Modifications

### When Modifying VTK Headers
VTK headers are duplicated across services (`services/*/VTK/`). Changes to interfaces may need to be synchronized across:
- `services/spi-service/VTK/`
- `services/power-service/VTK/`

### Adding New Sensors to spi-service
1. Create library in `services/spi-service/<SENSOR>_LIB/`
   - Design library to use VTK interfaces (`VT_sync_data_stream_interface`, `VT_GPIO_interface`, etc.)
   - Follow pattern: library class constructor takes interface pointers as parameters
2. Create process class in `services/spi-service/include/<SENSOR>_process.h`
   - Implement `process_JSON_line()` to handle JSON commands
   - Optionally implement `process()` for periodic tasks
   - Optionally implement `init()` for initialization
3. Implement in `services/spi-service/src/<SENSOR>_process.cpp`
4. Add to `main.cpp`:
   - Instantiate process object globally
   - Create request/response JSON strings and atomic flags
   - Instantiate `JSON_TCP_sever` with unique port
   - Call `TCP_server.Start()` in `main()`
   - Poll request flag and call `process_JSON_line()` in main loop
5. Update `services/spi-service/CMakeLists.txt`:
   - Add source files to `SPI_SERVICE_SOURCES`
   - Add include paths if needed
   - Add port number as compile definition
6. If sensor requires hardware drivers not already present:
   - Add driver class to `hard_driver/` implementing appropriate VTK interface
   - Instantiate and pass to device library constructor

### Port Assignments
Ports are hardcoded per service and device:
- Power service: 501
- ADS1293: 1293
- MAX30009: 30009
- WS2812: 2812

### JSON API Quick Reference

All services use newline-delimited JSON over TCP. Common request patterns:

```json
// Get current settings
{"type": "get_settings"}

// Configure sensor (ADS1293 example)
{"type": "settings", "enable_conversion": true, "power_enable": true}

// Get sensor data
{"type": "get_data"}
```

Responses include `"type"` field indicating response type. See `docs/COMPLETE_JSON_API_REFERENCE.md` for full API documentation.

## Version Management

Version is stored in `VERSION` file at repository root and read by CMake at configure time. Update this file to change firmware version.
