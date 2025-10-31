# AGENTS.md - MajaHealth Sensor Firmware

## Build Commands
- **Debug build**: Open `.cbp` files in Code::Blocks IDE, or use GCC directly with `-g -Wall -fexceptions`
- **Release build**: Use `-O2 -s` optimization flags  
- **Manual compile**: `g++ -g -Wall -fexceptions -Iinclude -Ihard_driver -IVTK -IADS1293_LIB -IMAX30009_LIB -IWS281x main.cpp src/*.cpp -lgpiod -o bin/Debug/[project_name]`
- **Run**: Execute binaries from `bin/Debug/` or `bin/Release/` directories
- **No formal testing**: This firmware uses manual debugging with std::cout, no unit test framework

## Architecture
Two main C++ services for ARM Linux embedded system:
- **SPI_DEV_servise**: Handles sensor data from MAX30009 (bioimpedance) and ADS1293 (ECG) via SPI, serves TCP on multiple ports
- **power_control_servise**: Manages power control functionality via GPIO/I2C, serves TCP on port 501
- **JSON TCP servers**: Both services use JSON over TCP for external communication
- **Hardware libraries**: Custom drivers for GPIO (libgpiod), SPI, and sensor-specific libraries

## Code Style
- **Headers**: Use include guards (`#ifndef HEADER_H`)
- **Classes**: PascalCase with `_cls` suffix (e.g., `GPIO_driver_cls`)
- **Structs**: UPPERCASE with underscores (e.g., `MAX30009_USER_SETTINGS`)
- **Variables**: snake_case for members (`_GPIO_num`), camelCase for some locals
- **Includes**: System headers first, then local headers, group by functionality
- **Error handling**: Basic return codes, no exceptions in embedded code
- **JSON**: Uses nlohmann/json library for data serialization
