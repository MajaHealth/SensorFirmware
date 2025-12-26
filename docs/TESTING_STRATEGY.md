# Testing Strategy for Sensor Firmware

## Overview

This document defines the testing strategy, directory structure, and implementation plan for the sensor firmware based on the Test_Cases_Master_List_Final.xlsx.

**Test Summary:**
- Total Test Cases: **247**
- Frameworks: **gtest (129 tests)**, **pytest (116 tests)**, **manual (2 tests)**
- Test Categories: **17 categories** (PROTO, DRV, DATA, ADS, MAX, WS, etc.)

---

## Directory Structure (SIMPLIFIED)

```
sensor-firmware-build/
├── CMakeLists.txt                           # Root: BUILD_TESTS option
│
├── services/
│   ├── spi-service/
│   │   ├── CMakeLists.txt                  # Service build + test targets
│   │   ├── src/                            # Production code
│   │   ├── include/                        # Production headers
│   │   │
│   │   └── tests/                          # ⬅️ NEW: All spi-service tests
│   │       ├── CMakeLists.txt              # Test build configuration
│   │       │
│   │       ├── unit/                       # Unit tests (gtest) - All C++ tests here
│   │       │   ├── test_GPIO_driver.cpp            # TC-DRV-GPIO-* (10 tests)
│   │       │   ├── test_SPI_driver.cpp             # TC-DRV-SPI-* (5 tests)
│   │       │   ├── test_I2C_driver.cpp             # TC-DRV-I2C-* (3 tests)
│   │       │   ├── test_FIFO_buffer.cpp            # TC-DATA-* (15 tests)
│   │       │   ├── test_ADS1293_lib.cpp            # TC-ADS-LIB-* (22 tests)
│   │       │   ├── test_ADS1293_process.cpp        # TC-ADS-PROC-* (16 tests)
│   │       │   ├── test_MAX30009_lib.cpp           # TC-MAX-LIB-* (20 tests)
│   │       │   ├── test_MAX30009_process.cpp       # TC-MAX-PROC-* (14 tests)
│   │       │   ├── test_MAX30009_MUX.cpp           # TC-MAX-MUX-* (4 tests)
│   │       │   ├── test_MAX30009_calibration.cpp   # TC-CALIB-* (8 tests)
│   │       │   ├── test_WS2812_driver.cpp          # TC-WS-DRV-* (10 tests)
│   │       │   ├── test_WS2812_process.cpp         # TC-WS-PROC-* (16 tests)
│   │       │   ├── test_error_handling.cpp         # TC-ERR-* (10 tests)
│   │       │   └── test_state_machine.cpp          # TC-STATE-* (12 tests)
│   │       │
│   │       ├── integration/                # Integration tests (pytest) - All Python tests here
│   │       │   ├── test_tcp_protocol.py            # TC-PROTO-* (25 tests)
│   │       │   ├── test_json_commands.py           # JSON command validation
│   │       │   ├── test_sensors_integration.py     # TC-SENSOR-* (16 tests)
│   │       │   └── test_stress.py                  # TC-STRESS-* (6 tests)
│   │       │
│   │       ├── mocks/                      # Mock implementations
│   │       │   ├── mock_GPIO_driver.h
│   │       │   ├── mock_GPIO_driver.cpp
│   │       │   ├── mock_SPI_driver.h
│   │       │   └── mock_SPI_driver.cpp
│   │       │
│   │       └── fixtures/                   # Test data and configs
│   │           ├── sample_calibration.json # Sample calibration files
│   │           ├── test_commands.json      # Sample JSON commands
│   │           └── expected_responses.json
│   │
│   └── power-service/
│       ├── CMakeLists.txt
│       ├── src/
│       ├── include/
│       │
│       └── tests/                          # ⬅️ NEW: Power service tests
│           ├── CMakeLists.txt
│           │
│           ├── unit/                       # Unit tests (gtest)
│           │   ├── test_power_control.cpp          # TC-PWR-* (14 tests)
│           │   ├── test_battery_monitor.cpp        # Battery telemetry tests
│           │   └── test_SMBus_driver.cpp           # TC-SMB-* (5 tests)
│           │
│           ├── integration/                # Integration tests (pytest)
│           │   └── test_power_protocol.py          # TC-POWER-* (6 tests)
│           │
│           └── mocks/                      # Mock drivers
│               ├── mock_SMBus_driver.h
│               └── mock_GPIO_driver.h
│
├── tests/                                   # ⬅️ OPTIONAL: System-level tests only
│   ├── CMakeLists.txt
│   ├── test_multi_service.py               # TC-INT-* (3 tests) - Both services
│   ├── test_main_loop.cpp                  # TC-MAIN-* (3 tests) - Main loop tests
│   └── common/                             # Shared test utilities
│       ├── test_helpers.h
│       ├── test_helpers.cpp
│       └── README.md
│
└── build-output/
    └── tests/                              # Test binary outputs
        ├── spi-service/
        │   ├── test_GPIO_driver            # Individual test executables
        │   ├── test_ADS1293_lib
        │   └── ...
        └── power-service/
            └── ...
```

**Key Simplifications:**
- ✅ Flat `unit/` folder - all C++ test files in one place
- ✅ Flat `integration/` folder - all Python test files in one place
- ✅ Each test file groups related tests (e.g., all GPIO tests in one file)
- ✅ No deeply nested subdirectories
- ✅ Easy to navigate and maintain
- ✅ Optional `tests/` folder only for multi-service integration tests

---

## Test Framework Breakdown

### 1. Unit Tests (gtest) - 129 Tests

**Platform:** Laptop/CM4
**Hardware Required:** No (uses mocks)
**Framework:** Google Test (C++)

| Category | Count | Location |
|----------|-------|----------|
| TC-DRV-GPIO | 10 tests | `services/spi-service/tests/unit/test_GPIO_driver.cpp` |
| TC-DRV-SPI | 5 tests | `services/spi-service/tests/unit/test_SPI_driver.cpp` |
| TC-DRV-I2C | 3 tests | `services/spi-service/tests/unit/test_I2C_driver.cpp` |
| TC-DATA | 15 tests | `services/spi-service/tests/unit/test_FIFO_buffer.cpp` |
| TC-ADS-LIB | 22 tests | `services/spi-service/tests/unit/test_ADS1293_lib.cpp` |
| TC-ADS-PROC | 16 tests | `services/spi-service/tests/unit/test_ADS1293_process.cpp` |
| TC-MAX-LIB | 20 tests | `services/spi-service/tests/unit/test_MAX30009_lib.cpp` |
| TC-MAX-PROC | 14 tests | `services/spi-service/tests/unit/test_MAX30009_process.cpp` |
| TC-MAX-MUX | 4 tests | `services/spi-service/tests/unit/test_MAX30009_MUX.cpp` |
| TC-CALIB | 8 tests | `services/spi-service/tests/unit/test_MAX30009_calibration.cpp` |
| TC-WS-DRV | 10 tests | `services/spi-service/tests/unit/test_WS2812_driver.cpp` |
| TC-WS-PROC | 16 tests | `services/spi-service/tests/unit/test_WS2812_process.cpp` |
| TC-ERR | 10 tests | `services/spi-service/tests/unit/test_error_handling.cpp` |
| TC-STATE | 12 tests | `services/spi-service/tests/unit/test_state_machine.cpp` |
| TC-PWR | 14 tests | `services/power-service/tests/unit/test_power_control.cpp` |
| TC-SMB | 5 tests | `services/power-service/tests/unit/test_SMBus_driver.cpp` |
| TC-MAIN | 3 tests | `tests/test_main_loop.cpp` |

### 2. Integration Tests (pytest) - 116 Tests

**Platform:** CM4 Linux
**Hardware Required:** Varies
**Framework:** pytest (Python)

| Category | Count | Location |
|----------|-------|----------|
| TC-PROTO | 25 tests | `services/spi-service/tests/integration/test_tcp_protocol.py` |
| TC-JSON | ~20 tests | `services/spi-service/tests/integration/test_json_commands.py` |
| TC-SENSOR | 16 tests | `services/spi-service/tests/integration/test_sensors_integration.py` |
| TC-STRESS | 6 tests | `services/spi-service/tests/integration/test_stress.py` |
| TC-POWER | 6 tests | `services/power-service/tests/integration/test_power_protocol.py` |
| TC-INT | 3 tests | `tests/test_multi_service.py` |
| Others | ~40 tests | Various integration scenarios |

### 3. Manual Tests - 2 Tests

Hardware-specific verification tests requiring manual intervention.

---

## CMake Build Configuration

### Root CMakeLists.txt Options

```cmake
# Testing options
option(BUILD_TESTS "Build all tests (unit + integration)" OFF)
option(BUILD_UNIT_TESTS "Build unit tests only (gtest)" OFF)
option(BUILD_INTEGRATION_TESTS "Build integration tests only (pytest)" OFF)
option(ENABLE_MOCKS "Use mock hardware drivers for testing" ON)
```

### Build Commands

```bash
# Build production firmware (no tests)
cmake -B build-output -DCMAKE_BUILD_TYPE=Release
cmake --build build-output

# Build with ALL tests enabled
cmake -B build-output -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build-output

# Build ONLY unit tests (gtest)
cmake -B build-output -DBUILD_UNIT_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build-output

# Build ONLY integration tests (pytest)
cmake -B build-output -DBUILD_INTEGRATION_TESTS=ON
cmake --build build-output

# Run all tests
cd build-output
ctest --output-on-failure

# Run specific test category
ctest -R "GPIO"      # Run all GPIO tests
ctest -R "ADS1293"   # Run all ADS1293 tests
ctest -R "MAX30009"  # Run all MAX30009 tests

# Run unit tests only
ctest -L unit

# Run integration tests only
ctest -L integration
```

---

## Test Priorities

Based on Excel **Priority** column:

### CRITICAL (Must Pass)
- TC-PROTO-001 to TC-PROTO-006: TCP connection and JSON commands
- TC-DRV-GPIO-001: GPIO initialization
- TC-DRV-SPI-001: SPI device open
- All ADS1293 and MAX30009 core functionality tests

### HIGH (Should Pass)
- All driver tests
- FIFO buffer operations
- Calibration tests
- WS2812 LED control

### MEDIUM (Nice to Have)
- Error handling edge cases
- Stress tests
- Performance benchmarks

### LOW (Optional)
- Edge case validation
- Redundant error scenarios

---

## Mock Infrastructure

To enable **laptop development** and CI/CD, mocks are required for:

### Mock GPIO Driver (`mocks/mock_GPIO_driver.h`)
- Implements `VT_GPIO_interface`
- Simulates pin states in memory
- No `/dev/gpiochipN` dependency

### Mock SPI Driver (`mocks/mock_SPI_driver.h`)
- Implements `VT_sync_data_stream_interface`
- Simulates SPI transactions
- No `/dev/spidevX.Y` dependency

### Mock SMBus Driver (`mocks/mock_SMBus_driver.h`)
- Implements `VT_SMBUS_interface`
- Simulates I2C battery data
- No `/dev/i2c-N` dependency

**Activation:**
```cmake
if(ENABLE_MOCKS)
    add_definitions(-DUSE_MOCK_DRIVERS)
    target_sources(test_target PRIVATE mocks/mock_GPIO_driver.cpp)
endif()
```

---

## Implementation Phases

### Phase 1: Infrastructure Setup (Week 1)
1. ✅ Create directory structure
2. ✅ Set up root CMakeLists.txt with BUILD_TESTS option
3. ✅ Integrate Google Test via FetchContent
4. ✅ Create mock driver implementations
5. ✅ Set up pytest environment

### Phase 2: Unit Tests - Drivers (Week 2)
1. Implement TC-DRV-GPIO-* tests (10 tests)
2. Implement TC-DRV-SPI-* tests (5 tests)
3. Implement TC-DRV-I2C-* tests (3 tests)
4. Verify mock drivers work on laptop

### Phase 3: Unit Tests - Data Processing (Week 3)
1. Implement TC-DATA-* tests (15 tests)
2. Test FIFO buffer logic
3. Test sync mark insertion
4. Test decimation logic (fix BUG #1!)

### Phase 4: Unit Tests - ADS1293 (Week 4)
1. Implement TC-ADS-LIB-* tests (22 tests)
2. Implement TC-ADS-PROC-* tests (16 tests)
3. Test register operations
4. Test ECG data flow

### Phase 5: Unit Tests - MAX30009 (Week 5)
1. Implement TC-MAX-LIB-* tests (20 tests)
2. Implement TC-MAX-PROC-* tests (14 tests)
3. Implement TC-MAX-MUX-* tests (4 tests)
4. Implement TC-CALIB-* tests (8 tests)
5. Fix circular buffer race condition (BUG #5)
6. Fix memory ordering (BUG #6)

### Phase 6: Unit Tests - WS2812 & Power (Week 6)
1. Implement TC-WS-* tests (26 tests)
2. Implement TC-PWR-* tests (14 tests)
3. Implement TC-SMB-* tests (5 tests)

### Phase 7: Integration Tests - Protocol (Week 7)
1. Implement TC-PROTO-* tests (25 tests)
2. Test TCP connections
3. Test JSON command parsing
4. Test concurrent client handling

### Phase 8: Integration Tests - Sensors (Week 8)
1. Implement TC-SENSOR-* tests (16 tests)
2. End-to-end ADS1293 workflow
3. End-to-end MAX30009 workflow
4. End-to-end WS2812 workflow

### Phase 9: Stress & System Tests (Week 9)
1. Implement TC-STRESS-* tests (6 tests)
2. Implement TC-INT-* tests (3 tests)
3. Implement TC-MAIN-* tests (3 tests)
4. Full system integration testing

### Phase 10: CI/CD & Documentation (Week 10)
1. Set up GitHub Actions for automated testing
2. Document test execution procedures
3. Create test coverage reports
4. Final validation on CM4 hardware

---

## Next Steps

1. **Review this strategy document** - Confirm approach
2. **Create directory structure** - Execute `mkdir` commands
3. **Modify CMakeLists.txt** - Add BUILD_TESTS option
4. **Implement mock drivers** - Start with GPIO mock
5. **Write first unit test** - TC-DRV-GPIO-001 as proof of concept

---

## Test Execution Workflow

```
Developer writes code
    ↓
Run unit tests locally (laptop with mocks)
    cmake -B build -DBUILD_UNIT_TESTS=ON -DENABLE_MOCKS=ON
    cmake --build build
    cd build && ctest -L unit
    ↓
Fix bugs, iterate
    ↓
Commit to repository
    ↓
CI/CD pipeline runs (GitHub Actions)
    - Unit tests with mocks
    - Integration tests (if CM4 runner available)
    - Code coverage report
    ↓
Deploy to CM4 hardware
    ↓
Run integration tests on hardware
    cmake -B build -DBUILD_INTEGRATION_TESTS=ON -DENABLE_MOCKS=OFF
    pytest tests/integration/
    ↓
Manual validation tests
    ↓
Production release
```

---

**Document Version:** 1.0
**Date:** 2025-11-29
**Author:** Based on Test_Cases_Master_List_Final.xlsx
