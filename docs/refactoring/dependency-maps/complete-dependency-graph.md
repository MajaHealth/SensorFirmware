# Complete File Dependency Graph

**Project:** Sensor Firmware C++ to C Refactoring
**Date:** 2025-11-22

---

## DEPENDENCY HIERARCHY (Bottom-Up, Layer by Layer)

```
LAYER 0: External C Libraries (No changes needed)
├── libgpiod (GPIO access)
├── Linux SPI subsystem (/dev/spidev*)
├── Linux I2C subsystem (/dev/i2c-*)
├── i2c/smbus (SMBus protocol)
├── POSIX sockets (TCP/IP)
├── POSIX threads (pthread)
└── C11 standard library (stdatomic.h, time.h, etc.)

LAYER 1: VTK Interfaces (Pure Virtual - Must Convert First)
├── VT_GPIO_interface.h
│   ├── Defines: VT_GPIO_DIRECT_ENUM, VT_GPIO_STATE_ENUM
│   ├── Pure virtual methods: 4
│   └── Dummy implementation: dummy_VT_GPIO
├── VT_sync_data_stream_interface.h
│   ├── Pure virtual methods: 1 (send_byte_array)
│   └── No dummy implementation
├── VT_register_process_interface.h
│   ├── Pure virtual methods: 2
│   └── Dummy implementation: dummy_register_process
└── VT_SMBUS_interface.h (power-service only)
    ├── Pure virtual methods: 4
    └── No dummy implementation

LAYER 2: Hardware Drivers (Implement Layer 1 Interfaces)
├── GPIO_driver.h (GPIO_driver_cls)
│   ├── Implements: VT_GPIO_interface
│   ├── Uses: libgpiod (gpiod_chip, gpiod_line)
│   ├── Uses: std::string (constructor parameter)
│   ├── Locations: services/spi-service/hard_driver/
│   │             services/power-service/hard_driver/
│   └── Conversion priority: HIGH
├── SPI_hard_driver.h (SPI_hard_driver_cls)
│   ├── Implements: VT_sync_data_stream_interface
│   ├── Uses: Linux SPI (ioctl, spi_ioc_transfer)
│   ├── Locations: services/spi-service/hard_driver/
│   │             services/power-service/hard_driver/
│   └── Conversion priority: HIGH
└── VT_SMBUS_driver.h (VT_SMBUS_driver)
    ├── Implements: VT_SMBUS_interface
    ├── Uses: i2c/smbus (i2c_smbus_read_word_data)
    ├── Uses: std::string, std::cerr
    ├── Location: services/power-service/hard_driver/
    └── Conversion priority: MEDIUM

LAYER 3A: Template Utility Classes (Complex Conversion)
└── VT_register_container.h (register_container<T>)
    ├── Template class with DATA_TYPE parameter
    ├── Uses: VT_register_process_interface
    ├── Member: volatile DATA_TYPE S
    ├── Methods: load_register(), update_register()
    ├── Locations: services/spi-service/VTK/
    │             services/power-service/VTK/
    └── Conversion priority: CRITICAL (template to C)

LAYER 3B: Utility Classes (Use Layer 2 Drivers)
└── SES_battery_info.h (SES_battery_info)
    ├── Uses: VT_SMBUS_interface (constructor parameter)
    ├── 14 getter methods for battery data
    ├── Uses: static_cast<float>
    ├── Enums: BATT_REG (C-compatible)
    ├── Struct: SES_BATT_STATUS_TDS (packed, C-compatible)
    ├── Location: services/power-service/VTK/
    └── Conversion priority: MEDIUM

LAYER 4A: Third-Party C Library (Already Compatible)
└── WS281x Library
    ├── ws2811.h (pure C with extern "C" guards)
    ├── Functions: ws2811_init, ws2811_render, ws2811_fini, ws2811_wait
    ├── Structs: ws2811_t, ws2811_channel_t
    ├── Location: services/spi-service/WS281x/
    └── Action: Remove C++ guards only

LAYER 4B: Third-Party Wrapper (Convert to C)
└── WS2812_wrap_cls.h (WS2812_wrap_cls)
    ├── Wraps: WS281x C library
    ├── Uses: std::cout
    ├── Uses: static_cast<uint32_t>
    ├── Virtual destructor
    ├── Location: services/spi-service/include/
    └── Conversion priority: LOW-MEDIUM

LAYER 5: Device Library Classes (Complex Business Logic)
├── ADS1293_LIB (Namespace: ADS1293)
│   ├── File: services/spi-service/ADS1293_LIB/ADS1293_LIB.h
│   ├── Size: 38,403 tokens (VERY LARGE)
│   ├── Constructor parameter: VT_sync_data_stream_interface*
│   ├── Methods: 100+ (register configuration, data acquisition)
│   ├── Uses: register_container<T> (many instances)
│   ├── Namespace: ADS1293::
│   ├── Related files:
│   │   ├── ADS1293_register_map.h (register definitions)
│   │   └── ADS1293_IO.h (I/O operations)
│   └── Conversion priority: CRITICAL (largest, most complex)
│
└── MAX30009_LIB
    ├── File: services/spi-service/MAX30009_LIB/max30009_lib.h
    ├── Constructor parameter: VT_sync_data_stream_interface*
    ├── Methods: 40+ (PLL, BIOZ, ADC, calibration)
    ├── Uses: math.h (C-compatible)
    ├── Uses: register structs
    ├── Related files:
    │   ├── max30009_register_struct.h (register definitions)
    │   ├── max30009_data_struct.h (measurement data)
    │   └── max30009_ext_mux.h (external multiplexer)
    └── Conversion priority: CRITICAL

LAYER 6: Process Classes (Business Logic + JSON)
├── ADS1293_process
│   ├── Files: services/spi-service/include/ADS1293_process.h
│   │         services/spi-service/src/ADS1293_process.cpp
│   ├── Uses: ADS1293_LIB
│   ├── Uses: nlohmann/json → MUST REPLACE
│   ├── Uses: std::string, std::vector
│   ├── Methods: init(), process(), process_JSON_line(), add_sync_mark()
│   ├── IFIFO buffer: 3000 elements
│   ├── JSON commands: "settings", "get_data"
│   └── Conversion priority: HIGH
│
├── MAX30009_process
│   ├── Files: services/spi-service/include/MAX30009_process.h
│   │         services/spi-service/src/MAX30009_process.cpp
│   ├── Uses: MAX30009_LIB, max30009_ext_mux
│   ├── Uses: nlohmann/json → MUST REPLACE
│   ├── Uses: std::string, std::vector, std::filesystem, std::fstream
│   ├── Uses: std::chrono, std::thread
│   ├── Methods: Many (calibration, settings, data, file I/O)
│   ├── IFIFO buffer: 30,000 elements
│   ├── Calibration: 85-point automatic sequence
│   ├── JSON commands: "settings", "get_data", "start_calibrate", "stop_calibrate"
│   └── Conversion priority: VERY HIGH (most C++ dependencies)
│
├── WS2812_process
│   ├── Files: services/spi-service/include/WS2812_process.h
│   ├── Uses: WS2812_wrap_cls
│   ├── Uses: nlohmann/json → MUST REPLACE
│   ├── Uses: std::string, std::exception
│   ├── Animation engine (color transitions)
│   ├── LED count: 9
│   ├── JSON commands: LED color arrays
│   └── Conversion priority: MEDIUM
│
└── PWRCNTR_process
    ├── Files: services/power-service/include/PWRCNTR_process.h
    │         services/power-service/src/PWRCNTR_process.cpp
    ├── Uses: VT_SMBUS_driver, SES_battery_info
    ├── Uses: GPIO_driver_cls (button, buzzer, charge control)
    ├── Uses: nlohmann/json → MUST REPLACE
    ├── Uses: std::string, std::vector, std::chrono, std::thread
    ├── JSON commands: "get_batt_info", "charge_enable", "charge_disable", "buzzer"
    ├── Async events: Button press detection
    └── Conversion priority: MEDIUM-HIGH

LAYER 7: TCP Server Infrastructure
└── JSON_TCP_sever.h (JSON_TCP_sever class)
    ├── Locations: services/spi-service/include/
    │             services/power-service/include/
    ├── Uses: std::thread (server loop in separate thread)
    ├── Uses: std::atomic<bool> (thread synchronization)
    ├── Uses: std::string* (JSON buffer pointers)
    ├── Uses: std::cout, std::cerr
    ├── Uses: POSIX sockets (C-compatible)
    ├── Uses: poll() (C-compatible)
    ├── Constructor: 5 parameters (port, JSON pointers, flag pointers)
    ├── Methods: Start(), Stop(), server_loop()
    ├── Thread safety: Atomic flags with acquire/release ordering
    └── Conversion priority: VERY HIGH (threading critical)

LAYER 8: Main Entry Points (Orchestration)
├── spi-service/src/main.cpp
│   ├── Global objects:
│   │   ├── ADS1293_process ADS1293_process_obj
│   │   ├── MAX30009_process MAX30009_process_obj
│   │   ├── WS2812_process WS2812_process_obj
│   │   ├── JSON_TCP_sever × 3 (ports 1293, 30009, 2812)
│   │   ├── std::string × 6 (request/response for each service)
│   │   └── std::atomic<bool> × 6 (request/response flags)
│   ├── Uses: std::chrono::steady_clock (sync mark timing)
│   ├── Main loop: 500μs period, usleep(500)
│   ├── Sync marks: Every 1000ms, sent to ADS1293 + MAX30009
│   └── Conversion priority: HIGH
│
└── power-service/src/main.cpp
    ├── Global objects:
    │   ├── PWRCNTR_process PWRCNTR_process_obj
    │   ├── JSON_TCP_sever × 1 (port 501)
    │   ├── std::string × 2 (request/response)
    │   └── std::atomic<bool> × 2 (request/response flags)
    ├── Uses: std::thread::sleep_for
    ├── Main loop: 100ms period, delay(100)
    ├── Battery read throttle: Every ~3 seconds
    └── Conversion priority: MEDIUM

LAYER 9: Build System
├── CMakeLists.txt (root)
│   ├── Sets C++17 standard → Change to C11
│   ├── Finds Threads package
│   ├── Adds subdirectories for services
│   └── Defines install rules
├── services/spi-service/CMakeLists.txt
│   ├── Defines SPI_SERVICE_SOURCES
│   ├── Links: Threads, gpiod
│   ├── Adds WS281x static library
│   └── Must update for .c files
└── services/power-service/CMakeLists.txt
    ├── Defines POWER_SERVICE_SOURCES
    ├── Links: Threads, gpiod, i2c
    └── Must update for .c files
```

---

## CROSS-SERVICE DEPENDENCIES

### Duplicated Files (Must Keep in Sync During Conversion)

| File | Location 1 | Location 2 | Notes |
|------|------------|------------|-------|
| VT_GPIO_interface.h | spi-service/VTK/ | power-service/VTK/ | Identical |
| VT_sync_data_stream_interface.h | spi-service/VTK/ | power-service/VTK/ | Identical |
| VT_register_process_interface.h | spi-service/VTK/ | power-service/VTK/ | Identical |
| VT_register_container.h | spi-service/VTK/ | power-service/VTK/ | Identical |
| GPIO_driver.h | spi-service/hard_driver/ | power-service/hard_driver/ | Identical |
| SPI_hard_driver.h | spi-service/hard_driver/ | power-service/hard_driver/ | Identical |
| JSON_TCP_sever.h | spi-service/include/ | power-service/include/ | Identical |

**CRITICAL:** Convert all 7 duplicated files simultaneously to avoid version mismatches!

---

## EXTERNAL LIBRARY DEPENDENCIES

### C++ Libraries (MUST REPLACE)

| Library | Current Usage | Replacement | Priority |
|---------|---------------|-------------|----------|
| nlohmann/json | JSON parsing (3 process classes) | cJSON or json-c | CRITICAL |
| std::string | Everywhere (20+ files) | char arrays / char* | CRITICAL |
| std::thread | main.cpp, JSON_TCP_sever | pthread | CRITICAL |
| std::atomic | main.cpp, JSON_TCP_sever | stdatomic.h (C11) | CRITICAL |
| std::chrono | main.cpp, process classes | clock_gettime() | HIGH |
| std::vector | process classes | Dynamic arrays / fixed arrays | MEDIUM |
| std::filesystem | MAX30009_process | POSIX file API | LOW |
| std::fstream | MAX30009_process | fopen/fwrite/fclose | LOW |
| std::cout/cerr | Many files | printf/fprintf | LOW |
| std::exception | process classes | Error codes | LOW |

### C Libraries (Already Compatible)

| Library | Usage | Notes |
|---------|-------|-------|
| libgpiod | GPIO operations | Already C |
| Linux SPI | SPI communication | ioctl() calls |
| i2c/smbus | I2C/SMBus | Already C |
| POSIX sockets | TCP communication | Already C |
| pthread | Thread creation | Replacement for std::thread |
| stdatomic.h | Atomic operations | C11 standard |
| time.h | Timestamps | Already C |
| math.h | Impedance calculations | Already C |

---

## COMPILATION ORDER (For Incremental Conversion)

### Phase 1: Foundation
1. VT_GPIO_interface.h
2. VT_sync_data_stream_interface.h
3. VT_register_process_interface.h
4. VT_SMBUS_interface.h

### Phase 2: Drivers
5. GPIO_driver.h/c
6. SPI_hard_driver.h/c
7. VT_SMBUS_driver.h/c

### Phase 3: Utilities
8. VT_register_container.h (template → macro/specific types)
9. SES_battery_info.h/c

### Phase 4: Device Libraries (Can parallelize after dependencies done)
10. WS2812_wrap_cls.h/c (independent path)
11. ADS1293_LIB.h/c (requires 1,2,5,6,8)
12. MAX30009_LIB.h/c (requires 1,2,5,6)

### Phase 5: Process Layer (Can parallelize after Layer 4)
13. WS2812_process.h/c
14. ADS1293_process.h/c
15. MAX30009_process.h/c
16. PWRCNTR_process.h/c

### Phase 6: Infrastructure
17. JSON_TCP_sever.h/c

### Phase 7: Integration
18. spi-service/main.c
19. power-service/main.c

### Phase 8: Build System
20. Update all CMakeLists.txt files
21. Update Dockerfile

---

## INCLUDE DEPENDENCY TREE (Critical for Header Order)

```
<stdio.h>, <stdint.h>, <stdbool.h>, <stdlib.h>
├── VT_GPIO_interface.h
├── VT_sync_data_stream_interface.h
├── VT_register_process_interface.h
└── VT_SMBUS_interface.h
    │
    ├── GPIO_driver.h (needs VT_GPIO_interface.h, gpiod.h)
    ├── SPI_hard_driver.h (needs VT_sync_data_stream_interface.h, linux/spi/spidev.h)
    ├── VT_SMBUS_driver.h (needs VT_SMBUS_interface.h, linux/i2c-dev.h, i2c/smbus.h)
    │
    ├── VT_register_container.h (needs VT_register_process_interface.h)
    ├── SES_battery_info.h (needs VT_SMBUS_interface.h)
    │
    ├── ADS1293_register_map.h
    ├── ADS1293_IO.h
    ├── ADS1293_LIB.h (needs VT_sync_data_stream_interface.h, VT_register_container.h, ADS1293_register_map.h, ADS1293_IO.h)
    │
    ├── max30009_register_struct.h
    ├── max30009_data_struct.h
    ├── max30009_ext_mux.h
    ├── max30009_lib.h (needs VT_sync_data_stream_interface.h, max30009_*.h)
    │
    ├── ws2811.h (standalone C library)
    ├── WS2812_wrap_cls.h (needs ws2811.h)
    │
    ├── ADS1293_process.h (needs ADS1293_LIB.h)
    ├── MAX30009_process.h (needs max30009_lib.h, max30009_ext_mux.h, GPIO_driver.h, SPI_hard_driver.h)
    ├── WS2812_process.h (needs WS2812_wrap_cls.h)
    ├── PWRCNTR_process.h (needs VT_SMBUS_driver.h, SES_battery_info.h, GPIO_driver.h)
    │
    ├── JSON_TCP_sever.h (standalone, needs <sys/socket.h>, <pthread.h>, <stdatomic.h>)
    │
    └── main.c (needs process headers, JSON_TCP_sever.h)
```

---

## TESTING DEPENDENCIES

### Unit Test Requirements

Each layer needs tests before next layer conversion:

**Layer 1 Tests:** Interface function pointer tables work correctly
**Layer 2 Tests:** Drivers pass interface compatibility tests
**Layer 3 Tests:** Template conversion maintains type safety
**Layer 4 Tests:** Device libraries produce same register values
**Layer 5 Tests:** Process classes produce identical JSON output
**Layer 6 Tests:** TCP server maintains thread safety
**Layer 7 Tests:** Main loops maintain timing accuracy

### Integration Test Points

1. **After Layer 2:** GPIO + SPI drivers work with actual hardware
2. **After Layer 4:** Device libraries communicate with sensors
3. **After Layer 5:** JSON commands produce correct sensor responses
4. **After Layer 6:** TCP clients can connect and communicate
5. **After Layer 7:** Full system test on target hardware

---

## CRITICAL PATH ANALYSIS

**Longest dependency chain:**
```
VT_sync_data_stream_interface.h
    → SPI_hard_driver.h
        → VT_register_container.h
            → ADS1293_LIB.h
                → ADS1293_process.h
                    → JSON_TCP_sever.h
                        → main.cpp
```

**Chain length:** 7 levels
**Estimated time:** 3-4 weeks if serial

**Parallelizable paths after Layer 2:**
- Path A: WS281x → WS2812_wrap_cls → WS2812_process
- Path B: VT_SMBUS → SES_battery_info → PWRCNTR_process
- Path C: ADS1293_LIB → ADS1293_process
- Path D: MAX30009_LIB → MAX30009_process

All paths converge at JSON_TCP_sever and main.cpp

---

**Document Status:** COMPLETE
**Total Files Analyzed:** 40+
**Total Dependencies Mapped:** 100+
**Critical Path Length:** 7 levels
