# Interface Implementation Matrix

**Project:** Sensor Firmware C++ to C Refactoring
**Purpose:** Map which concrete classes implement which VTK interfaces
**Date:** 2025-11-22

---

## INTERFACE → IMPLEMENTATION MAPPING

### 1. VT_GPIO_interface

**Interface Methods:**
- `set_GPIO_direct(direct, init_state)` → bool
- `set_GPIO_state(state)` → bool
- `get_GPIO_state()` → VT_GPIO_STATE_TDE
- `get_GPIO_direct()` → VT_GPIO_DIRECT_TDE

**Implementations:**

| Class | Location | Used By | Notes |
|-------|----------|---------|-------|
| `GPIO_driver_cls` | `services/*/hard_driver/GPIO_driver.h` | ADS1293_LIB, MAX30009_LIB, PWRCNTR | Real implementation using libgpiod |
| `dummy_VT_GPIO` | `services/*/VTK/VT_GPIO_interface.h` | Default/fallback | Returns error values |

**Usage Pattern:**
```cpp
// Device libraries receive pointer to interface
GPIO_driver_cls gpio_driver(pin_number, "gpiochip0");
VT_GPIO_interface* gpio_ptr = &gpio_driver;
// Passed to device library constructor
```

**C Conversion Strategy:**
```c
typedef struct {
    void* context;
    const vt_gpio_vtable_t* vtable;
} vt_gpio_t;

struct vt_gpio_vtable {
    bool (*set_direction)(void* ctx, vt_gpio_direct_t dir, vt_gpio_state_t init);
    bool (*set_state)(void* ctx, vt_gpio_state_t state);
    vt_gpio_state_t (*get_state)(void* ctx);
    vt_gpio_direct_t (*get_direction)(void* ctx);
};
```

---

### 2. VT_sync_data_stream_interface

**Interface Methods:**
- `send_byte_array(send_data, receive_data, data_size)` → bool

**Implementations:**

| Class | Location | Used By | Notes |
|-------|----------|---------|-------|
| `SPI_hard_driver_cls` | `services/*/hard_driver/SPI_hard_driver.h` | ADS1293_LIB, MAX30009_LIB | SPI communication via Linux spidev |

**Usage Pattern:**
```cpp
// Constructor receives pointer
SPI_hard_driver_cls spi_driver("/dev/spidev0.0");
VT_sync_data_stream_interface* spi_ptr = &spi_driver;

// Passed to device library
ADS1293_LIB ads1293(spi_ptr);
MAX30009_LIB max30009(spi_ptr);
```

**C Conversion Strategy:**
```c
typedef struct {
    void* context;
    const vt_stream_vtable_t* vtable;
} vt_stream_t;

struct vt_stream_vtable {
    bool (*send_byte_array)(void* ctx, uint8_t* tx, uint8_t* rx, uint32_t size);
};
```

---

### 3. VT_register_process_interface

**Interface Methods:**
- `load_from_register(register_data, register_address)` → bool
- `write_to_register(register_data, register_address)` → bool

**Implementations:**

| Class | Location | Used By | Notes |
|-------|----------|---------|-------|
| `dummy_register_process` | `services/*/VTK/VT_register_process_interface.h` | register_container<T> | Returns false (not actively used?) |

**Usage Pattern:**
```cpp
// Used by template class register_container
register_container<CONFIG_REG_TYPE> config_reg(register_proc_ptr, address);
```

**Notes:**
- This interface appears to be **not actively used** in current implementation
- Dummy implementation always returns false
- May be legacy or placeholder for future functionality
- **LOW PRIORITY** for conversion

**C Conversion Strategy:**
```c
typedef struct {
    void* context;
    const vt_register_vtable_t* vtable;
} vt_register_t;

struct vt_register_vtable {
    bool (*load_from_register)(void* ctx, uint8_t* data, uint8_t addr);
    bool (*write_to_register)(void* ctx, uint8_t* data, uint8_t addr);
};
```

---

### 4. VT_SMBUS_interface (Power Service Only)

**Interface Methods:**
- `open(device_address)` → bool
- `close()` → bool
- `read_2byte_data(register_adr, result)` → uint16_t
- `read_byte_data(register_adr, result)` → uint8_t

**Implementations:**

| Class | Location | Used By | Notes |
|-------|----------|---------|-------|
| `VT_SMBUS_driver` | `services/power-service/hard_driver/VT_SMBUS_driver.h` | SES_battery_info | I2C/SMBus for battery communication |

**Usage Pattern:**
```cpp
// Driver instantiated globally
VT_SMBUS_driver smbus_driver;
smbus_driver.open(BATTERY_I2C_ADDRESS);

// Passed to battery info class
SES_battery_info battery(&smbus_driver);
```

**C Conversion Strategy:**
```c
typedef struct {
    void* context;
    const vt_smbus_vtable_t* vtable;
} vt_smbus_t;

struct vt_smbus_vtable {
    bool (*open)(void* ctx, uint8_t addr);
    bool (*close)(void* ctx);
    uint16_t (*read_2byte_data)(void* ctx, uint8_t reg, bool* result);
    uint8_t (*read_byte_data)(void* ctx, uint8_t reg, bool* result);
};
```

---

## IMPLEMENTATION → USAGE MAPPING

### GPIO_driver_cls Usage Map

| User | Purpose | GPIO Pins Used |
|------|---------|----------------|
| **ADS1293_LIB** | Chip select, control signals | Multiple (TBD from implementation) |
| **MAX30009_LIB** | Chip select, control signals | Multiple (TBD from implementation) |
| **PWRCNTR** | Button input, buzzer output | 2+ pins |

---

### SPI_hard_driver_cls Usage Map

| User | SPI Device | Purpose |
|------|------------|---------|
| **ADS1293_LIB** | `/dev/spidev0.0` or similar | ECG sensor communication |
| **MAX30009_LIB** | `/dev/spidev0.1` or similar | Bio-impedance sensor communication |

---

### VT_SMBUS_driver Usage Map

| User | I2C Address | Purpose |
|------|-------------|---------|
| **SES_battery_info** | 0x0B | Battery status monitoring |

---

## DEPENDENCY GRAPH (Bottom-Up)

```
Layer 1: VTK Interfaces (Pure Virtual)
├── VT_GPIO_interface
├── VT_sync_data_stream_interface
├── VT_register_process_interface
└── VT_SMBUS_interface

Layer 2: Hardware Drivers (Implement Interfaces)
├── GPIO_driver_cls → implements VT_GPIO_interface
├── SPI_hard_driver_cls → implements VT_sync_data_stream_interface
└── VT_SMBUS_driver → implements VT_SMBUS_interface

Layer 3: Utility Classes (Use Interfaces)
├── register_container<T> → uses VT_register_process_interface
└── SES_battery_info → uses VT_SMBUS_interface

Layer 4: Device Libraries (Use Interfaces)
├── ADS1293_LIB → uses VT_sync_data_stream_interface
├── MAX30009_LIB → uses VT_sync_data_stream_interface
└── WS2812_wrap_cls → wraps pure C library (no interfaces)

Layer 5: Process Classes (Use Device Libraries)
├── ADS1293_process → uses ADS1293_LIB
├── MAX30009_process → uses MAX30009_LIB
├── WS2812_process → uses WS2812_wrap_cls
└── PWRCNTR_process → uses SES_battery_info

Layer 6: TCP Server (Uses Process Classes)
└── JSON_TCP_sever → communicates with any process class

Layer 7: Main Entry Point (Orchestrates Everything)
├── spi-service/main.cpp → instantiates 3 processes + 3 TCP servers
└── power-service/main.cpp → instantiates 1 process + 1 TCP server
```

---

## INTERFACE INSTANTIATION LOCATIONS

### SPI Service Instantiations

**Location:** `services/spi-service/src/main.cpp` and process implementations

```cpp
// Hardware drivers (assumed in process implementations)
GPIO_driver_cls ads1293_cs(CS_PIN_ADS);
GPIO_driver_cls max30009_cs(CS_PIN_MAX);
SPI_hard_driver_cls spi_ads("/dev/spidev0.0");
SPI_hard_driver_cls spi_max("/dev/spidev0.1");

// Device libraries (in process classes)
ADS1293_LIB ads1293_lib(&spi_ads);
MAX30009_LIB max30009_lib(&spi_max);
WS2812_wrap_cls ws2812(9); // 9 LEDs

// Process objects (in main.cpp)
ADS1293_process ADS1293_process_obj;
MAX30009_process MAX30009_process_obj;
WS2812_process WS2812_process_obj;

// TCP servers (in main.cpp)
JSON_TCP_sever ADS1293_TCP_server(1293, ...);
JSON_TCP_sever MAX30009_TCP_server(30009, ...);
JSON_TCP_sever WS2812_TCP_server(2812, ...);
```

### Power Service Instantiations

**Location:** `services/power-service/src/main.cpp` and process implementations

```cpp
// Hardware drivers (in process implementation)
VT_SMBUS_driver smbus;
smbus.open(0x0B);

// Utility classes (in process implementation)
SES_battery_info battery(&smbus);

// GPIO drivers (in process implementation)
GPIO_driver_cls button_gpio(BUTTON_PIN);
GPIO_driver_cls buzzer_gpio(BUZZER_PIN);

// Process object (in main.cpp)
PWRCNTR_process PWRCNTR_process_obj;

// TCP server (in main.cpp)
JSON_TCP_sever PWRCNTR_TCP_server(501, ...);
```

---

## CONVERSION PRIORITY ORDER

Based on dependencies, convert in this order:

1. **VT_GPIO_interface** → Foundation for drivers
2. **VT_sync_data_stream_interface** → Foundation for SPI
3. **VT_SMBUS_interface** → Foundation for battery (power-service)
4. **VT_register_process_interface** → Low priority (not actively used)
5. **GPIO_driver_cls** → Implements #1
6. **SPI_hard_driver_cls** → Implements #2
7. **VT_SMBUS_driver** → Implements #3
8. **register_container<T>** → Template conversion (complex)
9. **SES_battery_info** → Uses #3
10. **ADS1293_LIB** → Uses #2, #5, #8
11. **MAX30009_LIB** → Uses #2, #5
12. **WS2812_wrap_cls** → Independent (C library wrapper)
13. **Process classes** → Use device libraries
14. **JSON_TCP_sever** → Independent infrastructure
15. **Main functions** → Orchestration

---

## RISK ASSESSMENT BY INTERFACE

| Interface | Risk Level | Reason |
|-----------|------------|--------|
| VT_GPIO_interface | LOW | Simple interface, well-defined |
| VT_sync_data_stream_interface | LOW | Single method, clear purpose |
| VT_register_process_interface | VERY LOW | Not actively used |
| VT_SMBUS_interface | LOW | Standard I2C patterns |
| register_container<T> | **HIGH** | Template class, complex |
| Threading/Atomics | **VERY HIGH** | Race conditions possible |
| JSON parsing | **HIGH** | API compatibility critical |

---

## TESTING STRATEGY PER INTERFACE

### VT_GPIO_interface
- Unit test: Mock GPIO operations
- Integration test: Read/write actual GPIO with oscilloscope
- Verify: Direction changes, state changes, pull-up/down

### VT_sync_data_stream_interface
- Unit test: Mock SPI transfers
- Integration test: Loopback SPI test (MOSI → MISO)
- Verify: Full-duplex operation, timing, byte order

### VT_SMBUS_interface
- Unit test: Mock I2C operations
- Integration test: Read battery with known values
- Verify: Word/byte reads, error handling

### register_container<T>
- Unit test: Multiple type instantiations
- Integration test: Actual register operations
- Verify: Template → macro/function conversion correctness

---

**Document Status:** COMPLETE
**Next Document:** Complete Dependency Graph with File-Level Details
