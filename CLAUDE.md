# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sensor firmware for Raspberry Pi CM4 that provides hardware interface services for medical/biometric sensors. The firmware is built as separate services that communicate via JSON over TCP sockets.

**Target Platform:** Raspberry Pi CM4 (ARM Cortex-A72)
**Build System:** CMake with Docker-based cross-compilation
**Language:** C++17 with some C components

## Quick Workflow Reference

**Complete development cycle:**
```bash
# 1. Set CM4 IP (do this once per session)
export PI_IP=192.168.x.x

# 2. Make firmware changes

# 3. Build and deploy
./scripts/build-and-deploy.sh

# 4. Run tests
./scripts/run-tests-remote.sh $PI_IP -m quick

# 5. Analyze results
ls /tmp/test-results/data/
```

**Common scenarios:**

```bash
# Quick validation after code change
./scripts/build-and-deploy.sh && ./scripts/run-tests-remote.sh $PI_IP -m quick

# Test specific sensor (ADS1293)
./scripts/run-tests-remote.sh $PI_IP -m ads1293

# Run single test with verbose output
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_api.py -vv

# Hardware test with ECG simulator (60 seconds)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg.py

# Restart services and test
./scripts/run-tests-remote.sh $PI_IP --restart-services -m quick
```

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

Tests are organized into three categories:

**1. Unit Tests (Python)** - `tests/unit_tests/`
- `tests/unit_tests/power-service/` - Power service unit tests (e.g., Test #106: Shutdown handling)
- `tests/unit_tests/spi-service/` - SPI service unit tests
- `tests/unit_tests/gpio/` - GPIO-related unit tests
- `tests/unit_tests/shutdown/` - Shutdown handling tests
- Isolated component testing with mock objects
- Fast execution (< 1 second per test typically)

**2. C++ Unit Tests (gtest)**
- `services/spi-service/tests/unit/` - C++ unit tests for SPI service
- `services/power-service/tests/unit/` - C++ unit tests for power service
- Low-level device library testing

**3. Integration Tests (Python)**
- `services/spi-service/tests/integration/` - Python integration tests (pytest)
- `services/power-service/tests/integration/` - Python integration tests (pytest)
- `tests/fw-app-integration/` - Firmware-application integration tests
- `tests/hardware-integration/` - Hardware integration tests (require actual sensors)
- `tests/common/` - Shared test utilities (`tcp_client.py`, `sensor_helpers.py`, `validators.py`, `data_logger.py`)
- `tests/config/test_config.yaml` - Test configuration parameters

### Mock Drivers

Mock implementations in `services/*/tests/mocks/` enable unit testing without hardware:
- `mock_SPI_driver.h/cpp` - Simulates SPI transactions
- `mock_GPIO_driver.h/cpp` - Simulates GPIO state
- `mock_SMBus_driver.h/cpp` - Simulates I2C/SMBus (power-service)

Build with mocks: `cmake -DBUILD_TESTS=ON -DENABLE_MOCKS=ON`

### Test Markers

Available pytest markers for filtering tests:

| Marker | Description | Tests | Duration |
|--------|-------------|-------|----------|
| `quick` | Quick validation tests | 12 | ~4 min |
| `api` | API protocol validation | 3 | ~1 min |
| `invalid_params` | Parameter validation | 5 | ~2 min |
| `fw_app` | FW-APP integration | 12 | ~4 min |
| `hardware` | Hardware integration | 5 | 1-4 hours |
| `slow` | Slow tests (60s ECG) | 1 | ~1 min |
| `long` | Long duration (1hr ECG) | 4 | 4 hours |
| `ads1293` | All ADS1293 tests | 17 | 1-4 hours |
| `max30009` | MAX30009 tests | TBD | - |
| `ws2812` | LED controller tests | TBD | - |

### Test Configuration

Test parameters are configured in `tests/config/test_config.yaml`:
- Service connection settings (host/port)
- Sensor-specific parameters (sampling rates, R-rates, BPM values)
- Pass/fail thresholds
- Output directories

**Environment variable override:**
- Set `PI_TARGET_IP` to override service host for remote testing
- The `run-tests-remote.sh` script automatically sets this

### Run Unit Tests

Unit tests are located in `tests/unit_tests/` and test individual components in isolation:

```bash
# Run all unit tests
pytest tests/unit_tests/ -v

# Run specific service unit tests
pytest tests/unit_tests/power-service/ -v
pytest tests/unit_tests/spi-service/ -v

# Run specific test file
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s

# Run with markers
pytest tests/unit_tests/ -m unit -v           # All unit tests
pytest tests/unit_tests/ -m "unit and gpio" -v  # Unit tests with GPIO
pytest tests/unit_tests/ -m shutdown -v       # Shutdown tests only
```

### Remote Testing (Run from Laptop)

Run integration tests from your laptop connecting to Pi over network (no SSH, no venv on Pi):

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

Responses include `"type"` field indicating response type. See `JSON_PROTOCOL_REFERENCE.md` for full API documentation.

## Data Analysis

### Test Results and Jupyter Notebooks

Test results are saved in JSONL (JSON Lines) format for easy analysis:
- Test data: `/tmp/test-results/data/test_*.jsonl`
- Each line contains a JSON record (data samples, metadata, sync markers, timestamps)

**Analyzing results:**
```python
import json

# Read test data
with open('/tmp/test-results/data/test_011_ecg_1hr_bpm60.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        if record['type'] == 'data':
            # Process ECG samples
            samples = record['data']
        elif record['type'] == 'metadata':
            # Review test metrics
            metrics = record
```

**Jupyter notebooks for analysis:**
- Repository includes example notebooks (`ecg.ipynb`, `test_nov_25.ipynb`) demonstrating ECG and ICG data analysis
- Use these as templates for custom analysis workflows
- Common tasks: plotting signals, calculating metrics, detecting R-peaks, validating BPM

### Common Analysis Patterns

**ECG Analysis:**
```python
import numpy as np
from scipy.signal import find_peaks

# Calculate BPM from ECG data
sampling_freq = 400  # Hz
distance = int(sampling_freq * 0.5)  # Min 0.5s between peaks
peaks, _ = find_peaks(ecg_signal, distance=distance)

# Calculate BPM from peak intervals
if len(peaks) >= 2:
    peak_intervals = np.diff(peaks) / sampling_freq  # seconds
    bpm = 60 / np.mean(peak_intervals)
```

**Sampling Frequency Validation:**
```python
# Extract sync markers and calculate actual sampling frequency
sync_markers = [sample for sample in data if sample == [999, 999, 999]]
duration_sec = len(sync_markers)  # Each sync marker is 1 second
total_samples = len(data) - len(sync_markers)
actual_freq = total_samples / duration_sec
```

## Troubleshooting

### Connection Issues

**Problem:** `ConnectionRefusedError` when running tests

**Solutions:**
```bash
# Check if firmware services are running on CM4
ssh pi@$PI_IP systemctl status spi-service

# Restart services
./scripts/run-tests-remote.sh $PI_IP --restart-services

# Verify port is accessible
nc -zv $PI_IP 1293

# Check firewall (if needed)
ssh pi@$PI_IP sudo iptables -L
```

### Sampling Frequency Issues

**Problem:** Actual sampling frequency differs from expected

**Cause:** Incorrect R-rate configuration or buffer accumulation

**Solution:**
- ADS1293 sampling rate formula: `fs = 128000 / (R1_rate × R2_rate × R3_rate)`
- For 400 Hz: Closest achievable is 500 Hz with R2=4, R3=16
- Always flush buffer after stabilization:
  ```python
  time.sleep(2.0)  # Wait for stabilization
  flush_response = get_sensor_data(client)  # Discard accumulated samples
  # Now start clean data collection
  ```

### First `get_data` Returns Extra Samples

**Problem:** First response contains ~800 samples instead of expected ~400-500

**Cause:** Firmware buffer accumulates samples during 2-second stabilization period

**Solution:** Tests should explicitly flush the buffer before data collection (see pattern above)

### Python Dependencies

**Problem:** `ImportError` or missing modules

**Solutions:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Should see (venv) in prompt

# Reinstall dependencies
pip install -r tests/requirements.txt

# Verify installation
pytest --version
python -c "import numpy, scipy, yaml; print('OK')"
```

### Build Failures

**Problem:** CMake or compilation errors

**Common causes and solutions:**
- **Missing toolchain:** Ensure Docker is installed for cross-compilation
- **Wrong build directory:** Always use `build-output` directory
- **Stale build:** Clean and rebuild:
  ```bash
  rm -rf build-output
  mkdir build-output
  cd build-output
  cmake .. -DCMAKE_TOOLCHAIN_FILE=../docker/arm-toolchain.cmake
  cmake --build . -j$(nproc)
  ```

## Version Management

Version is stored in `VERSION` file at repository root and read by CMake at configure time. Update this file to change firmware version.
