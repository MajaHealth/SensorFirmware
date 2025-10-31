 # CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an embedded C++ firmware system for ARM Linux that manages medical sensors and power control for MajaHealth devices. The system consists of two independent services that communicate via JSON over TCP.

## Build System

This project uses **Code::Blocks** with GCC toolchain. Build files are `.cbp` (Code::Blocks Project) format.

### Building SPI_DEV_servise

**In Code::Blocks:**
- Open `SPI_DEV_servise/SPI_DEV_servise.cbp`
- Build targets: Debug or Release

**Manual compilation:**
```bash
cd SPI_DEV_servise
g++ -g -Wall -fexceptions \
  -Iinclude -Ihard_driver -IVTK -IADS1293_LIB -IMAX30009_LIB -IWS281x \
  main.cpp src/*.cpp WS281x/*.c \
  -lgpiod -o bin/Debug/SPI_DEV_servise
```

**For Release:**
```bash
g++ -O2 -s -Wall -fexceptions \
  -Iinclude -Ihard_driver -IVTK -IADS1293_LIB -IMAX30009_LIB -IWS281x \
  main.cpp src/*.cpp WS281x/*.c \
  -lgpiod -o bin/Release/SPI_DEV_servise
```

### Building power_control_servise

**In Code::Blocks:**
- Open `power_control_servise/power_control_servise.cbp`
- Build targets: Debug or Release

**Manual compilation:**
```bash
cd power_control_servise
g++ -g -Wall -fexceptions \
  -Iinclude -Ihard_driver -IVTK \
  main.cpp PWRCNTR_process.cpp \
  -lgpiod -li2c -L/usr/lib/arm-linux-gnueabihf \
  -o bin/Debug/power_control_servise
```

**For Release:**
```bash
g++ -O2 -s -Wall -fexceptions \
  -Iinclude -Ihard_driver -IVTK \
  main.cpp PWRCNTR_process.cpp \
  -lgpiod -li2c -L/usr/lib/arm-linux-gnueabihf \
  -o bin/Release/power_control_servise
```

### Running the Services

```bash
# Run SPI device service
./SPI_DEV_servise/bin/Debug/SPI_DEV_servise

# Run power control service
./power_control_servise/bin/Debug/power_control_servise
```

## Architecture

### Two Independent Services

**1. SPI_DEV_servise** - Sensor data acquisition service
   - **Main loop:** `main.cpp` lines 67-137
   - Manages three sensor/peripheral subsystems in parallel
   - Runs tight polling loop with 500μs sleep (`usleep(500)`)
   - Handles JSON requests/responses via atomic flags and shared strings

**2. power_control_servise** - Power management service
   - **Main loop:** `main.cpp` lines 40-82
   - Manages power, battery monitoring, button input, and buzzer
   - Runs polling loop with 100ms sleep (`delay(100)`)
   - Battery reading throttled to every 3 seconds

### SPI_DEV_servise Components

Three parallel subsystems, each with their own TCP server:

**MAX30009 (Bioimpedance Sensor)**
- **TCP Port:** 30009
- **Process class:** `MAX30009_process` ([include/MAX30009_process.h](SPI_DEV_servise/include/MAX30009_process.h))
- **Implementation:** [src/MAX30009_process.cpp](SPI_DEV_servise/src/MAX30009_process.cpp)
- **Hardware lib:** `MAX30009_LIB/` - register maps, data structures, external MUX control
- **Key features:**
  - Configurable frequency (25Hz-450kHz) and current (64μA-1.28mA)
  - Automated calibration system with 17 frequency points × 5 current levels
  - Calibration data stored in `calib/` directory as JSON files (format: `{current_index}_{freq_index}.json`)
  - I/Q data FIFO buffering (30,000 samples max)
  - Sync marks injected every 1 second

**ADS1293 (ECG Sensor)**
- **TCP Port:** 1293
- **Process class:** `ADS1293_process` ([include/ADS1293_process.h](SPI_DEV_servise/include/ADS1293_process.h))
- **Implementation:** [src/ADS1293_process.cpp](SPI_DEV_servise/src/ADS1293_process.cpp)
- **Hardware lib:** `ADS1293_LIB/` - register maps and I/O
- **Key features:**
  - Multi-channel ECG data acquisition
  - Sync marks injected every 1 second

**WS2812 (LED Control)**
- **TCP Port:** 2812
- **Process class:** `WS2812_process` ([include/WS2812_process.h](SPI_DEV_servise/include/WS2812_process.h))
- **Hardware lib:** `WS281x/` - C library for WS2811/WS2812 LED control (DMA/PWM/PCM based)
- **Purpose:** RGB LED status indicators

### power_control_servise Components

**PWRCNTR_process** - Power control management
- **TCP Port:** 501
- **Process class:** `PWRCNTR_process` ([include/PWRCNTR_process.h](power_control_servise/include/PWRCNTR_process.h))
- **Implementation:** [PWRCNTR_process.cpp](power_control_servise/PWRCNTR_process.cpp)
- **Hardware libs:**
  - `VTK/SES_battery_info.h` - Battery information structures
  - `VTK/VT_SMBUS_interface.h` - SMBus/I2C interface for battery communication
  - `hard_driver/VT_SMBUS_driver.h` - Low-level SMBus driver
- **Key features:**
  - GPIO-based power control
  - I2C battery status monitoring
  - Button input handling via `process_button()`
  - Buzzer control via `process_buzzer()`

### Communication Pattern

Both services use the same JSON-over-TCP architecture:

**JSON_TCP_sever class** ([include/JSON_TCP_sever.h](SPI_DEV_servise/include/JSON_TCP_sever.h))
- Non-blocking TCP server running in separate thread
- Uses atomic flags for thread-safe request/response coordination
- Pattern per device:
  ```cpp
  std::string {DEVICE}_request_json;
  std::atomic<bool> {DEVICE}_request_ready_flag;
  std::string {DEVICE}_response_json;
  std::atomic<bool> {DEVICE}_response_ready_flag;
  JSON_TCP_sever {DEVICE}_TCP_server(port, ...);
  ```
- Main loop polls `request_ready_flag`, processes JSON, sets `response_ready_flag`
- Server thread handles socket I/O asynchronously

### VTK Interface Layer

**VTK/** directory contains abstract interfaces used across both services:

- `VT_register_process_interface.h` - Abstract interface for register read/write operations
- `VT_register_container.h` - Container for register-based device configuration
- `VT_sync_data_stream_interface.h` - Interface for synchronized data streaming
- `VT_GPIO_interface.h` - GPIO abstraction layer
- `VT_SMBUS_interface.h` - SMBus/I2C abstraction layer

**Pattern:** Hardware-specific classes inherit from VTK interfaces, allowing register-based devices (MAX30009, ADS1293) to share common configuration/data patterns.

### Hardware Driver Layer

**hard_driver/** directory contains low-level hardware abstractions:

- `GPIO_driver.h` - Uses libgpiod for GPIO control
- `SPI_hard_driver.h` - SPI bus communication (used by MAX30009, ADS1293)
- `VT_SMBUS_driver.h` - SMBus/I2C driver (used by power control for battery)

### Synchronization System

Both sensor services inject **sync marks** every 1 second:
- Magic number: `-99999` (defined in `MAX30009_process.h:84`)
- Inserted into data streams via `add_sync_mark(sync_num)`
- Allows data alignment between MAX30009 and ADS1293 streams
- Counter increments: `sync_num++`

## Code Style and Conventions

**Naming:**
- Classes: PascalCase with `_cls` suffix (e.g., `GPIO_driver_cls`)
- Structs: UPPERCASE with `_TDE`/`_TDS` suffix (e.g., `MAX30009_USER_SETTINGS_TDE`)
- Member variables: snake_case with leading underscore (e.g., `_GPIO_num`, `_port`)
- Local variables: snake_case or camelCase
- Functions/methods: snake_case

**Headers:**
- Use include guards: `#ifndef HEADER_H` / `#define HEADER_H` / `#endif`
- Group includes: system headers first, then local headers
- Document interfaces with brief comments

**Error Handling:**
- Return codes (bool/int) for success/failure
- perror() for system call errors
- std::cerr for error messages
- No C++ exceptions in embedded code

**JSON:**
- Uses nlohmann/json library (`include/json.hpp`)
- All device commands and responses are JSON formatted
- Device-specific JSON parsing in `process_JSON_line()` methods

**Threading:**
- Use `std::atomic<bool>` with explicit memory ordering for flags
- Pattern: `load(std::memory_order_acquire)` / `store(..., std::memory_order_release)`
- TCP servers run in separate threads spawned by `Start()`
- Main loops are single-threaded polling

**Timing:**
- Microsecond delays: `usleep(microseconds)`
- Millisecond delays: Custom `delay(ms)` function using `std::this_thread::sleep_for`
- Timing measurements: `std::chrono::steady_clock`

## Testing and Debugging

**No formal test framework** - This is production embedded firmware using manual testing.

**Debugging approach:**
- Use `std::cout` for status messages and data inspection
- Check TCP port connectivity: `telnet localhost {port}`
- JSON command/response debugging via TCP server output
- Monitor console output from both services

## Dependencies

**System libraries:**
- `libgpiod` - Modern Linux GPIO interface (required for both services)
- `libi2c` - I2C/SMBus communication (required for power_control_servise)

**Embedded libraries:**
- nlohmann/json (header-only, included in `include/json.hpp`)
- WS281x - Custom C library for WS2812 LED control

**Target platform:** ARM Linux (e.g., Raspberry Pi or similar embedded Linux)

## Key File Locations

**SPI_DEV_servise:**
- Entry point: [main.cpp](SPI_DEV_servise/main.cpp)
- Sensor implementations: `src/*.cpp`
- Calibration data: `calib/*.json`
- Built binaries: `bin/Debug/` or `bin/Release/`

**power_control_servise:**
- Entry point: [main.cpp](power_control_servise/main.cpp)
- Power control implementation: [PWRCNTR_process.cpp](power_control_servise/PWRCNTR_process.cpp)
- Built binaries: `bin/Debug/` or `bin/Release/`

**Shared patterns:**
- All TCP servers: `include/JSON_TCP_sever.h`
- Hardware drivers: `hard_driver/`
- VTK interfaces: `VTK/`
