# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an embedded biomedical sensor firmware system for ARM Linux platforms (Raspberry Pi). It consists of two independent services that communicate via JSON TCP APIs to provide real-time sensor data acquisition and power management for a wearable/portable medical device.

## Build System

### Using CodeBlocks IDE

The project uses CodeBlocks with separate project files for each service:
- `SPI_DEV_servise/SPI_DEV_servise.cbp` - Sensor data acquisition service
- `power_control_servise/power_control_servise.cbp` - Power management service

**Build targets:**
- **Debug**: Includes `-g` debug symbols, outputs to `bin/Debug/`
- **Release**: Optimized with `-O2`, stripped symbols with `-s`, outputs to `bin/Release/`

**Required libraries:**
- `libgpiod` - GPIO control interface
- `libi2c` - I2C/SMBus communication for battery management

**Compiler flags:**
- `-Wall` - All warnings enabled
- `-fexceptions` - C++ exception handling

### Build Outputs
- `SPI_DEV_servise/bin/Debug/SPI_DEV_servise` (or `Release/`)
- `power_control_servise/bin/Release/power_control_servise`

## System Architecture

### Two-Service Architecture

The system runs two independent processes communicating over TCP:

#### 1. SPI_DEV_servise (Sensor Data Service)
**Location:** `SPI_DEV_servise/main.cpp`

Manages three sensor/device types via separate TCP ports:
- **Port 1293**: ADS1293 ECG/EEG sensor (3-channel bioelectric signals)
- **Port 30009**: MAX30009 bioimpedance sensor (EIT measurements)
- **Port 2812**: WS2812 RGB LED strip control

**Main loop timing:** 500 microseconds cycle time (usleep(500))
- Polls JSON requests from all three TCP servers
- Calls process() for each sensor
- Injects sync marks every 1 second for cross-sensor synchronization

**Key operations:**
```cpp
MAX30009_process_obj.init();
ADS1293_process_obj.init();
// Main loop:
//   - Check atomic flags for JSON requests
//   - Process requests via process_JSON_line()
//   - Call sensor process() methods
//   - Add sync marks every 1000ms
```

#### 2. power_control_servise (Power Management)
**Location:** `power_control_servise/main.cpp`

**Port 501**: Power control and battery monitoring

**Main loop timing:** 100 milliseconds cycle time (delay(100))
- Processes button inputs every cycle
- Reads battery status every 3 seconds (30 × 100ms)
- Controls buzzer feedback

**Key operations:**
```cpp
PWRCNTR_process_obj.init();
// Main loop:
//   - Check JSON requests via atomic flags
//   - Process buttons via process_button()
//   - Read battery every 3s via process()
//   - Handle buzzer via process_buzzer()
```

## Core Design Patterns

### Process Class Pattern

Every sensor/subsystem follows this pattern:

**Interface (defined in each *_process.h):**
```cpp
class XXX_process {
    void init();              // Initialize hardware, configure sensor
    void process();           // Periodic processing (read data, state machine)
    std::string process_JSON_line(const char* JSON_line);  // Handle JSON commands
};
```

**Examples:**
- `MAX30009_process` - Bioimpedance sensor management
- `ADS1293_process` - ECG/EEG sensor management
- `WS2812_process` - LED strip control
- `PWRCNTR_process` - Power control and battery

### JSON TCP Server Pattern

**Location:** `SPI_DEV_servise/include/JSON_TCP_sever.h`

Thread-safe request/response communication using atomic flags:

**Architecture:**
1. Main loop polls atomic flag: `request_ready_flag.load()`
2. If true, processes request via process class
3. Sets response string and sets `response_ready_flag` to true
4. TCP server thread (running in background) sends response to client

**Thread synchronization:**
```cpp
std::atomic<bool> request_ready_flag;   // Set by server thread
std::atomic<bool> response_ready_flag;  // Set by main loop
std::string request_json;               // Written by server, read by main
std::string response_json;              // Written by main, read by server
```

**Memory ordering:**
- Uses `memory_order_acquire` for reading flags
- Uses `memory_order_release` for writing flags
- Ensures proper memory visibility across threads

**Server behavior:**
- Non-blocking sockets (O_NONBLOCK)
- poll() used to check socket readiness
- One thread per TCP connection
- Spawned by `JSON_TCP_sever::server_loop()`

### Virtual Toolkit (VTK) Abstraction

**Location:** `SPI_DEV_servise/VTK/` and `power_control_servise/VTK/`

Hardware abstraction layer using pure virtual interfaces:

**Pattern:**
```cpp
class VT_register_process_interface {
    virtual bool load_from_register(uint8_t* data, uint8_t addr) = 0;
    virtual bool write_to_register(uint8_t* data, uint8_t addr) = 0;
};
```

Allows sensor libraries (ADS1293, MAX30009) to be hardware-agnostic. Actual SPI/I2C implementation injected via dependency injection.

### Synchronization Mechanism

**Sync marks** are injected into sensor data streams every 1 second:
- Generated in main loop of SPI_DEV_servise
- `sync_num` increments each second
- Sent to MAX30009 and ADS1293 processes
- Magic number: `-99999` (SYNC_MARK_MAGIC_NUM)
- Allows post-processing to align data from multiple sensors

## Calibration System

**Location:** `SPI_DEV_servise/calib/` (86 JSON files)

The MAX30009 bioimpedance sensor requires calibration coefficients:

**Calibration matrix:**
- 17 frequency points: 25Hz to 450kHz
- 5 current settings: 64µA to 1.28mA
- = 85 calibration files (+ 1 additional file = 86 total)

**File naming pattern:** Based on frequency and current settings

**Data format (JSON):**
```json
{
  "amplitude": <gain coefficient>,
  "phase": <phase correction>,
  "offset": <offset value>,
  "gain": <additional gain>
}
```

**Usage:**
- Loaded during measurement configuration changes
- Applied in `MAX30009_process::calibration_process()`
- Calibration against known 100Ω resistor

## Hardware Drivers

### GPIO Control
**Location:** `hard_driver/GPIO_driver.h`

Uses `libgpiod` for modern GPIO control (replaces deprecated sysfs GPIO).

### SPI Communication
**Location:** `hard_driver/SPI_hard_driver.h`

Manages SPI bus for sensor communication (ADS1293, MAX30009).

### I2C/SMBus
**Location:** `power_control_servise/hard_driver/VT_SMBUS_driver.h`

Battery monitoring chip communication.

### WS2812 LED Driver
**Location:** `SPI_DEV_servise/WS281x/` (C code)

Low-level DMA/PWM driver for RGB LED strip control on Raspberry Pi.

## TCP Port Assignments

| Port  | Service              | Description                    |
|-------|----------------------|--------------------------------|
| 1293  | ADS1293_process      | ECG/EEG sensor data           |
| 30009 | MAX30009_process     | Bioimpedance sensor data      |
| 2812  | WS2812_process       | RGB LED control               |
| 501   | PWRCNTR_process      | Power control & battery info  |

## Timing Constraints

**SPI_DEV_servise:**
- Main loop: 500µs cycle time
- Real-time data acquisition critical
- Sync marks: Exactly 1000ms intervals

**power_control_servise:**
- Main loop: 100ms cycle time
- Battery read: Every 3 seconds (30 iterations)
- Button processing: Every cycle

## Key Sensor Details

### MAX30009 (Bioimpedance)
**Location:** `SPI_DEV_servise/MAX30009_LIB/`

- Configurable stimulation frequency (25Hz - 450kHz)
- Configurable measurement frequency (1-500 Hz)
- Current settings: 64µA, 128µA, 256µA, 640µA, 1.28mA
- I/Q data output (in-phase and quadrature)
- Filter settings: LP, HP, input HP
- External MUX support for multi-channel EIT

### ADS1293 (ECG/EEG)
**Location:** `SPI_DEV_servise/ADS1293_LIB/`

- 3-channel bioelectric ADC
- R2/R3 decimation rate control
- Power management (conversion enable/disable)
- Lead bias enable for electrode impedance reduction

### WS2812 (RGB LED)
**Location:** `SPI_DEV_servise/WS281x/`

- Addressable RGB LED strip
- PWM/DMA-based control
- Direct hardware memory access on Raspberry Pi

## JSON Library

**Location:** `SPI_DEV_servise/include/json.hpp`

Single-header JSON library (nlohmann::json) used throughout for:
- TCP command parsing
- Response formatting
- Calibration file storage
