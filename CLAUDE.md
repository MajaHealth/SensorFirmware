# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MajaHealth firmware for Raspberry Pi that interfaces with biomedical sensors and power management hardware. The system consists of two independent Linux services that communicate via JSON over TCP.

## Build System

Uses Code::Blocks project files (`.cbp`). Build targets are Debug and Release.

**Dependencies (install on Raspberry Pi):**
- libgpiod (GPIO control)
- libfltk (for debug window, optional)
- libi2c (for power_control_servise)

**Building SPI_DEV_servise:**
```bash
cd SPI_DEV_servise
# Using Code::Blocks
codeblocks --build SPI_DEV_servise.cbp --target=Release
# Or manually with g++
g++ -std=c++17 -O2 -Wall -fexceptions main.cpp src/*.cpp WS281x/*.c \
    -Iinclude -Ihard_driver -IVTK -IMAX30009_LIB -IADS1293_LIB -IWS281x \
    -lgpiod -lfltk -o bin/Release/SPI_DEV_servise
```

**Building power_control_servise:**
```bash
cd power_control_servise
codeblocks --build power_control_servise.cbp --target=Release
```

## Architecture

### Services and TCP Ports

| Service | Port | Purpose |
|---------|------|---------|
| MAX30009 | 30009 | Bioimpedance (BIOZ) measurements |
| ADS1293 | 1293 | ECG (3-channel) measurements |
| WS2812 | 2812 | LED strip control (9 LEDs) |
| Power Control | 501 | Battery monitoring, button events |

All services use JSON request/response protocol over TCP. Connect with `nc 127.0.0.1 <port>`.

### Key Components

**SPI_DEV_servise/main.cpp** - Main event loop that:
- Initializes MAX30009, ADS1293, and WS2812 process objects
- Starts TCP servers for each device
- Polls for JSON requests and dispatches to process handlers
- Adds sync marks to sensor data streams every 1 second

**power_control_servise/main.cpp** - Handles:
- Battery status via SMBus (address 0x0B)
- Button press detection with hold time tracking
- Buzzer control

### Hardware Abstraction (VTK interfaces)

- `VT_sync_data_stream_interface` - SPI communication base class
- `VT_register_process_interface` - Register read/write abstraction
- `VT_GPIO_interface` - GPIO pin control
- `VT_SMBUS_interface` - I2C/SMBus communication

Hardware drivers inherit from these interfaces:
- `SPI_hard_driver_cls` implements `VT_sync_data_stream_interface` using `/dev/spidevX.X`
- Uses Linux spidev ioctl for SPI transfers at 5MHz

### Sensor Libraries

**MAX30009_LIB/** - Analog Devices MAX30009 bioimpedance AFE
- Handles calibration, FIFO reading, I/Q channel processing
- Supports configurable stimulation current (16uA-640uA) and frequencies
- Calibration data stored in `base_table.json`

**ADS1293_LIB/** - Texas Instruments ADS1293 ECG analog front-end
- 3-channel ECG acquisition
- Configurable data rates via R1/R2/R3 decimation registers

**WS281x/** - Raspberry Pi WS2812 LED driver (DMA-based)

## JSON Protocol Examples

See `json protocol.txt` for complete examples. Key commands:

**MAX30009 settings:**
```json
{"type":"settings", "stimulate_current":"640uA", "stimulate_frequency":99968, "measure_frequency":500}
```

**ADS1293 settings:**
```json
{"type":"settings", "R1_rate":4, "R2_rate":8, "R3_rate":128, "enable_conversion":true}
```

**Get data (both sensors):**
```json
{"type":"get_data"}
```

**LED control:**
```json
{"leds": [[255,0,0],[0,255,0],[0,0,255],...], "t_time": 1000}
```

**Battery info:**
```json
{"type":"get_batt_info"}
```

## Data Synchronization

Both MAX30009 and ADS1293 insert sync marks into their data streams:
- MAX30009: `SYNC_MAGIC_NUM = -999990000`
- ADS1293: `SYNC_MAGIC_NUM = -99999`

Sync counter increments every second, allowing cross-sensor time alignment.

## Process Classes Pattern

Each sensor has a `*_process` class (e.g., `MAX30009_process`) that:
1. Implements `process_JSON_line(const char*)` - parses JSON commands, returns JSON response
2. Has `init()` for hardware setup
3. Has `process()` called in main loop for background tasks
4. Has `add_sync_mark()` for time synchronization
