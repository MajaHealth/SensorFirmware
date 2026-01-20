# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a medical sensor firmware project for a Raspberry Pi-based device that interfaces with bioimpedance (MAX30009) and ECG (ADS1293) sensors along with power management. The code is written in C++ and uses Code::Blocks as the IDE.

## Repository Structure

The project contains two independent services that run as separate executables:

### power_control_servise
- **Purpose**: Battery monitoring and power management
- **TCP Port**: 501
- **Main Components**:
  - `PWRCNTR_process`: Reads battery info via SMBus/I2C, handles power button events, controls buzzer
  - GPIOs: Power key (24), Charger sensor (22), Charge disable (14), Buzzer (20)
- **Libraries**: libgpiod, libi2c

### SPI_DEV_servise
- **Purpose**: Sensor data acquisition and processing
- **TCP Ports**: 1293 (ADS1293 ECG), 30009 (MAX30009 bioimpedance), 2812 (WS2812 LED)
- **Main Components**:
  - `ADS1293_process`: 3-channel ECG acquisition via SPI (/dev/spidev0.1)
  - `MAX30009_process`: Bioimpedance measurement with calibration via SPI (/dev/spidev0.0)
  - `WS2812_process`: LED strip control
- **Calibration**: Stored in `calib/` directory as JSON files (frequency × current matrix)
- **Libraries**: libgpiod

## Building

Projects use Code::Blocks project files (.cbp). Build commands on target device:
```bash
# Navigate to service directory
cd power_control_servise  # or SPI_DEV_servise

# Debug build
g++ -g -Wall -fexceptions -Iinclude -Ihard_driver -IVTK -o bin/Debug/power_control_servise main.cpp PWRCNTR_process.cpp -lgpiod -li2c

# Release build
g++ -O2 -Wall -fexceptions -Iinclude -Ihard_driver -IVTK -o bin/Release/power_control_servise main.cpp PWRCNTR_process.cpp -lgpiod -li2c
```

For SPI_DEV_servise, include additional directories: `-IADS1293_LIB -IMAX30009_LIB -IWS281x`

## Architecture

### Communication Pattern
All services use a JSON-over-TCP request/response pattern:
1. `JSON_TCP_sever` receives JSON commands on dedicated ports
2. Atomic flags coordinate between TCP thread and main loop
3. Main loop processes commands via `process_JSON_line()` methods
4. Responses sent back as JSON strings

### Hardware Abstraction Layer (VTK)
Located in `VTK/` directories:
- `VT_GPIO_interface`: Abstract GPIO operations
- `VT_sync_data_stream_interface`: Abstract SPI communication
- `VT_SMBUS_interface`: Abstract I2C/SMBus operations
- `VT_register_process_interface`: Register read/write abstraction

### Sensor Libraries
- `ADS1293_LIB/`: ECG AFE driver with register map and configuration
- `MAX30009_LIB/`: Bioimpedance AFE driver with calibration support
- `WS281x/`: Raspberry Pi WS2812 LED driver (DMA-based)

### Data Buffering
Both sensors use internal circular FIFO buffers (`_IFIFO_BUF`) with sync marks for time synchronization between sensors. Sync marks are injected every second with magic number -99999.

## JSON API Commands

### Power Control (port 501)
- `{"type": "get_batt_info"}` - Returns battery status
- `{"type": "charge_disable"}` / `{"type": "charge_enable"}`
- `{"type": "buzzer", "duration": <ms>}`

### ADS1293 ECG (port 1293)
- `{"type": "settings", "power_enable": bool, "enable_conversion": bool, "R2_rate": int, "R3_rate": int, "leadoff_enable": bool, "leadoff_mode": int, "leadoff_current_nA": int, "leadoff_threshold": int}`
- `{"type": "get_data"}` - Returns buffered ECG samples (includes lead-off status)
- `{"type": "get_leadoff_status"}` - Returns current lead-off detection status

**Lead-Off Detection**: When enabled, the service automatically pushes lead-off status every 5 seconds via the TCP connection. Status is also included in every `get_data` response.
- `leadoff_mode`: 0=DC, 1=AC (recommended)
- `leadoff_current_nA`: Detection current 0-2040 (default 1400)
- Monitors inputs: IN1 (RA), IN2 (LA), IN3 (LL), IN5, IN6. IN4 (RLD) is not monitored.

### MAX30009 Bioimpedance (port 30009)
- `{"type": "settings", "power_enable": bool, "measure_enable": bool, "stimulate_frequency": int, "stimulate_current": int, ...}`
- `{"type": "get_data"}` - Returns calibrated impedance data
- `{"type": "start_calibrate"}` / `{"type": "stop_calibrate"}`

## Target Platform

- Raspberry Pi (ARM Linux)
- Uses `/dev/spidev0.0` and `/dev/spidev0.1` for SPI
- Uses `gpiochip0` for GPIO via libgpiod
- SMBus for battery communication at address 0x0B

## Dependencies

System packages required on Raspberry Pi:
- `libgpiod-dev`
- `libi2c-dev`

Header-only library included:
- nlohmann/json (`json.hpp`)
