# C++ Features Inventory - Complete File Analysis

**Project:** Sensor Firmware C++ to C Refactoring
**Date:** 2025-11-22
**Phase:** 1 - Assessment & Preparation

---

## CATEGORY A: VTK INTERFACE LAYER (Foundation Files)

### 1. VT_GPIO_interface.h
**Location:**
- `services/spi-service/VTK/VT_GPIO_interface.h`
- `services/power-service/VTK/VT_GPIO_interface.h` (duplicate)

**C++ Features Used:**
- ✓ Pure virtual class with `=0` methods (4 virtual methods)
- ✓ C++ enums (VT_GPIO_DIRECT_ENUM, VT_GPIO_STATE_ENUM)
- ✓ Inheritance (dummy_VT_GPIO inherits from VT_GPIO_interface)
- ✓ `inline static` global object (dummy_VT_GPIO_obj)

**Methods to Convert:**
- `virtual bool set_GPIO_direct(VT_GPIO_DIRECT_TDE direct, VT_GPIO_STATE_TDE init_state)=0`
- `virtual bool set_GPIO_state(VT_GPIO_STATE_TDE state)=0`
- `virtual VT_GPIO_STATE_TDE get_GPIO_state(void)=0`
- `virtual VT_GPIO_DIRECT_TDE get_GPIO_direct(void)=0`

**Complexity:** MEDIUM
**Conversion Strategy:** Function pointer table (vtable struct)
**Dependencies:** None (foundation layer)

---

### 2. VT_sync_data_stream_interface.h
**Location:**
- `services/spi-service/VTK/VT_sync_data_stream_interface.h`
- `services/power-service/VTK/VT_sync_data_stream_interface.h` (duplicate)

**C++ Features Used:**
- ✓ Pure virtual class with 1 virtual method
- ✓ `=0` pure virtual specifier

**Methods to Convert:**
- `virtual bool send_byte_array(uint8_t* send_data, uint8_t* receive_data, uint32_t data_size)=0`

**Complexity:** LOW
**Conversion Strategy:** Function pointer table with single function
**Dependencies:** None (foundation layer)

---

### 3. VT_register_process_interface.h
**Location:**
- `services/spi-service/VTK/VT_register_process_interface.h`
- `services/power-service/VTK/VT_register_process_interface.h` (duplicate)

**C++ Features Used:**
- ✓ Pure virtual class (2 virtual methods)
- ✓ Inheritance (dummy_register_process)
- ✓ `inline static` global object

**Methods to Convert:**
- `virtual bool load_from_register(uint8_t* register_data, uint8_t register_address)=0`
- `virtual bool write_to_register(uint8_t* register_data, uint8_t register_address)=0`

**Complexity:** LOW
**Conversion Strategy:** Function pointer table
**Dependencies:** None

---

### 4. VT_SMBUS_interface.h
**Location:** `services/power-service/VTK/VT_SMBUS_interface.h`

**C++ Features Used:**
- ✓ Pure virtual class (4 virtual methods)
- ✓ `=0` pure virtual specifier

**Methods to Convert:**
- `virtual bool open(uint8_t device_address)=0`
- `virtual bool close()=0`
- `virtual uint16_t read_2byte_data(uint8_t register_adr, bool* result)=0`
- `virtual uint8_t read_byte_data(uint8_t register_adr, bool* result)=0`

**Complexity:** MEDIUM
**Conversion Strategy:** Function pointer table
**Dependencies:** None (power-service only)

---

### 5. VT_register_container.h
**Location:**
- `services/spi-service/VTK/VT_register_container.h`
- `services/power-service/VTK/VT_register_container.h` (duplicate)

**C++ Features Used:**
- ✓ **TEMPLATE CLASS** `template <typename DATA_TYPE>`
- ✓ Constructor with parameters
- ✓ Member methods (load_register, update_register)
- ✓ `nullptr` checking
- ✓ Volatile member variable

**Complexity:** HIGH
**Conversion Strategy:** Macro-based generic programming or type-specific implementations
**Dependencies:** VT_register_process_interface

**CRITICAL NOTE:** Templates are the most complex C++ feature to convert!

---

### 6. SES_battery_info.h
**Location:** `services/power-service/VTK/SES_battery_info.h`

**C++ Features Used:**
- ✓ Class with constructor taking interface pointer
- ✓ 14 member methods (get_voltage, get_temperature, etc.)
- ✓ C-style enum (BATT_REG) - compatible with C
- ✓ Packed struct (SES_BATT_STATUS_TDS) - compatible with C
- ✓ `nullptr` checking
- ✓ `static_cast<float>()` type conversions
- ✓ Private member variable pointer

**Methods Count:** 14 getter methods
**Complexity:** MEDIUM-HIGH
**Conversion Strategy:** Struct with context + function prefix
**Dependencies:** VT_SMBUS_interface

---

## CATEGORY B: HARDWARE DRIVER LAYER

### 7. GPIO_driver.h (GPIO_driver_cls)
**Location:**
- `services/spi-service/hard_driver/GPIO_driver.h`
- `services/power-service/hard_driver/GPIO_driver.h` (duplicate)

**C++ Features Used:**
- ✓ Class inheriting from VT_GPIO_interface
- ✓ Constructor with `std::string` parameter (default "gpiochip0")
- ✓ Destructor with resource cleanup
- ✓ Member initialization list
- ✓ Private member variables (4 members)
- ✓ `const` member function (is_initialized)
- ✓ `std::string` type

**External Dependencies:**
- libgpiod (C library) - already compatible

**Complexity:** MEDIUM
**Conversion Strategy:** Struct + init/cleanup functions + string replacement
**Critical:** RAII pattern must be converted to explicit init/cleanup

---

### 8. SPI_hard_driver.h (SPI_hard_driver_cls)
**Location:**
- `services/spi-service/hard_driver/SPI_hard_driver.h`
- `services/power-service/hard_driver/SPI_hard_driver.h` (duplicate)

**C++ Features Used:**
- ✓ Class inheriting from VT_sync_data_stream_interface
- ✓ Constructor with `const char*` (C-compatible)
- ✓ Destructor with resource cleanup
- ✓ RAII pattern (auto close on destroy)
- ✓ Private member variable (_device_desc)

**External Dependencies:**
- Linux SPI subsystem (C-compatible)

**Complexity:** LOW-MEDIUM
**Conversion Strategy:** Struct + init/cleanup functions
**Critical:** File descriptor management

---

### 9. VT_SMBUS_driver.h (VT_SMBUS_driver)
**Location:** `services/power-service/hard_driver/VT_SMBUS_driver.h`

**C++ Features Used:**
- ✓ Class inheriting from VT_SMBUS_interface
- ✓ **`std::string`** for I2C bus path
- ✓ `std::cerr` for error output
- ✓ Static member variable (dummy_result)
- ✓ Default parameter values in method signatures
- ✓ `extern "C"` block for C headers

**External Dependencies:**
- linux/i2c-dev.h (C library)
- i2c/smbus.h (C library)

**Complexity:** MEDIUM
**Conversion Strategy:** Replace std::string, convert error handling
**Critical:** Static variable initialization

---

## CATEGORY C: DEVICE LIBRARY LAYER

### 10. ADS1293_LIB.h (ADS1293_LIB class)
**Location:** `services/spi-service/ADS1293_LIB/ADS1293_LIB.h`

**C++ Features Used:**
- ✓ **Namespace** (`namespace ADS1293`)
- ✓ Large class with 100+ methods
- ✓ Constructor takes VTK interface pointer
- ✓ Complex member variables (register containers)
- ✓ Template usage (register_container<T>)

**File Size:** 38,403 tokens (VERY LARGE)
**Complexity:** VERY HIGH
**Conversion Strategy:** Struct + ads1293_ function prefix
**Dependencies:** VT_sync_data_stream_interface, VT_register_container

**CRITICAL:** This is the most complex file in the project!

---

### 11. MAX30009_LIB.h (MAX30009_LIB class)
**Location:** `services/spi-service/MAX30009_LIB/max30009_lib.h`

**C++ Features Used:**
- ✓ Class with 40+ methods
- ✓ Constructor takes VTK interface pointer
- ✓ Complex register structures
- ✓ Math operations (uses math.h - C-compatible)
- ✓ Private member variables

**Complexity:** HIGH
**Conversion Strategy:** Struct + max30009_ function prefix
**Dependencies:** VT_sync_data_stream_interface, register structures

---

### 12. WS281x Library (ws2811.h)
**Location:** `services/spi-service/WS281x/ws2811.h`

**C++ Features Used:**
- ✓ **NONE - Already pure C library!**
- ✓ `extern "C"` guards for C++ compatibility
- ✓ C structs and enums

**Complexity:** NONE
**Action Required:** Keep as-is, remove C++ guards if needed

---

### 13. WS2812_wrap_cls.h
**Location:** `services/spi-service/include/WS2812_wrap_cls.h`

**C++ Features Used:**
- ✓ Class wrapping C library
- ✓ Constructor with default parameters (5 parameters)
- ✓ Virtual destructor
- ✓ `std::cout` for logging
- ✓ `static_cast<uint32_t>()` conversions
- ✓ C99 designated initializers (struct initialization)
- ✓ Private member variables (3 members)

**Complexity:** MEDIUM
**Conversion Strategy:** Struct wrapper + function prefix
**Dependencies:** ws2811 (already C)

---

## CATEGORY D: PROCESS LAYER

### 14. ADS1293_process.h
**Location:** `services/spi-service/include/ADS1293_process.h`

**C++ Features Used:**
- ✓ Class with 8 methods
- ✓ **`std::string`** return types and parameters
- ✓ **`std::vector`** (imported but not in header)
- ✓ Constructor/destructor
- ✓ Static const members
- ✓ Private member arrays (IFIFO buffer: 3000 elements)
- ✓ Typedef structs (C-compatible)

**Methods:**
- `void init()`
- `void process()`
- `void add_sync_mark(int32_t sync_num)`
- `std::string process_JSON_line(const char* JSON_line)`
- `std::string get_all_settings_as_json()`
- `std::string get_data_as_json()`
- `void set_power_state(bool state)`
- `std::string get_timestamp_string()`

**Complexity:** HIGH
**Conversion Strategy:** Struct + function prefix, char* for strings
**Dependencies:** ADS1293_LIB, JSON parsing

---

### 15. MAX30009_process.h
**Location:** `services/spi-service/include/MAX30009_process.h`

**C++ Features Used:**
- ✓ Class with 15+ methods
- ✓ **`std::string`** extensively
- ✓ **`std::vector`** return type
- ✓ **nlohmann/json** (C++ only library!)
- ✓ **`std::chrono`** for timing
- ✓ **`std::thread`** for delays
- ✓ **`std::filesystem`** for file operations
- ✓ **`std::fstream`** for file I/O
- ✓ Static constexpr arrays
- ✓ 2D array member (_calibrate_data)
- ✓ Large IFIFO buffer (30,000 elements)

**Complexity:** VERY HIGH
**Conversion Strategy:** Multiple replacements needed
**Dependencies:** MAX30009_LIB, JSON, filesystem, threading

**CRITICAL:** Most C++-dependent process file!

---

### 16. WS2812_process.h
**Location:** `services/spi-service/include/WS2812_process.h`

**C++ Features Used:**
- ✓ Class with virtual destructor
- ✓ **nlohmann/json** for parsing
- ✓ **`std::string`**
- ✓ **`std::exception`** handling (try/catch)
- ✓ Static constexpr float
- ✓ Fixed-size arrays (9 LEDs)
- ✓ Constructor initialization list

**Complexity:** MEDIUM-HIGH
**Conversion Strategy:** Struct + JSON replacement
**Dependencies:** WS2812_wrap_cls, JSON library

---

### 17. PWRCNTR_process.h
**Location:** `services/power-service/include/PWRCNTR_process.h`

**C++ Features Used:**
- ✓ Class with 6 methods
- ✓ **`std::string`** parameters/returns
- ✓ **`std::chrono`** for timing
- ✓ **`std::thread::sleep_for`** (embedded in header!)
- ✓ **`std::vector`** (imported)
- ✓ Private inline delay() function using std::chrono
- ✓ Typedef struct (C-compatible)

**Complexity:** MEDIUM
**Conversion Strategy:** Struct + timing replacement
**Dependencies:** VT_SMBUS_driver, SES_battery_info

---

## CATEGORY E: TCP SERVER LAYER

### 18. JSON_TCP_sever.h
**Location:**
- `services/spi-service/include/JSON_TCP_sever.h`
- `services/power-service/include/JSON_TCP_sever.h` (duplicate)

**C++ Features Used:**
- ✓ Class with constructor/destructor
- ✓ **`std::thread`** member variable
- ✓ **`std::atomic<bool>`** for thread synchronization (4 pointers)
- ✓ **`std::string*`** pointers (4 pointers)
- ✓ **`std::this_thread::sleep_for`**
- ✓ **`std::this_thread::yield`**
- ✓ Member initialization list
- ✓ RAII for socket management
- ✓ `std::cout`, `std::cerr` for logging
- ✓ POSIX sockets (C-compatible)
- ✓ `poll()` system call (C-compatible)

**Methods:**
- Constructor with 5 parameters
- Destructor
- `void Start()`
- `void Stop()`
- `bool is_socket_readable(int socket_fd)`
- `bool is_client_connected(int socket_fd)`
- `void server_loop()` (thread function)

**Complexity:** VERY HIGH
**Conversion Strategy:** pthread, C11 atomics, char* strings
**Critical:** Thread safety must be preserved!

---

## CATEGORY F: MAIN ENTRY POINTS

### 19. spi-service/src/main.cpp
**Location:** `services/spi-service/src/main.cpp`

**C++ Features Used:**
- ✓ **`std::string`** for JSON buffers (6 strings)
- ✓ **`std::atomic<bool>`** flags (6 flags)
- ✓ **`std::chrono::steady_clock`** for timing
- ✓ **`std::chrono::duration_cast`**
- ✓ **`std::thread::sleep_for`**
- ✓ Global object instantiation (7 objects)
- ✓ Object method calls
- ✓ `usleep()` C function (already compatible)

**Global Objects:**
- 3 process objects
- 3 TCP server objects
- Atomic flags and strings for each

**Complexity:** HIGH
**Conversion Strategy:** Replace STL types, convert object management
**Critical:** Timing precision (500μs loop, 1-second sync marks)

---

### 20. power-service/src/main.cpp
**Location:** `services/power-service/src/main.cpp`

**C++ Features Used:**
- ✓ **`std::string`** for JSON buffers (2 strings)
- ✓ **`std::atomic<bool>`** flags (2 flags)
- ✓ **`std::thread::sleep_for`**
- ✓ Global object instantiation (2 objects)
- ✓ Static variable in main loop (battery_read_delay_tmr)

**Complexity:** MEDIUM
**Conversion Strategy:** Similar to spi-service
**Critical:** 100ms loop timing

---

## SUMMARY STATISTICS

### C++ Features Usage Count

| Feature | Count | Conversion Priority |
|---------|-------|---------------------|
| Classes with virtual methods | 5 | CRITICAL (foundation) |
| Template classes | 1 | CRITICAL |
| Namespaces | 1 | HIGH |
| std::string | 15+ files | CRITICAL |
| std::thread | 3 files | CRITICAL |
| std::atomic | 3 files | CRITICAL |
| std::chrono | 4 files | HIGH |
| nlohmann/json | 3 files | CRITICAL |
| std::vector | 4 files | MEDIUM |
| std::filesystem | 1 file | LOW |
| std::fstream | 1 file | LOW |
| Inheritance | 10+ classes | CRITICAL |
| Constructors/Destructors | 20+ classes | CRITICAL |
| RAII pattern | 8+ classes | HIGH |

### Conversion Complexity by Layer

1. **VTK Interfaces:** MEDIUM (foundation, must be done first)
2. **Hardware Drivers:** MEDIUM (depends on interfaces)
3. **Device Libraries:** VERY HIGH (largest code volume, templates)
4. **Process Layer:** VERY HIGH (most C++ dependencies)
5. **TCP Server:** VERY HIGH (threading, atomics)
6. **Main Functions:** HIGH (orchestration)

### External C Library Dependencies (Already Compatible)
- libgpiod ✓
- Linux SPI subsystem ✓
- Linux I2C subsystem ✓
- i2c/smbus ✓
- WS281x library ✓
- POSIX sockets ✓
- POSIX threads (pthread) ✓

### External C++ Library Dependencies (Need Replacement)
- nlohmann/json → cJSON or json-c
- C++ Standard Library (string, thread, atomic, chrono, vector, filesystem, fstream)

---

## FILES REQUIRING NO CHANGES

1. `services/spi-service/WS281x/*.h` - Pure C library
2. All `.c` files in WS281x directory

**Total Files:** ~8 files already C-compatible

---

## NEXT STEPS FOR PHASE 1

1. ✓ Complete this inventory
2. Create interface implementation matrix
3. Create dependency graph
4. Document JSON API specifications
5. Create risk assessment
6. Set up parallel build infrastructure

---

**Document Status:** COMPLETE
**Total Files Analyzed:** 20+ header files, 5 implementation files
**Last Updated:** 2025-11-22
