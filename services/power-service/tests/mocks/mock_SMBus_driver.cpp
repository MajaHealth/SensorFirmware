/**
 * Mock SMBus Driver Implementation
 */

#include "mock_SMBus_driver.h"

#ifdef USE_MOCK_DRIVERS

MockSMBusDriver::MockSMBusDriver() : is_open(false), device_address(0) {
}

bool MockSMBusDriver::open(const char* device_path, uint8_t addr) {
    (void)device_path; // Unused in mock
    device_address = addr;
    is_open = true;
    return true;
}

uint8_t MockSMBusDriver::read_byte(uint8_t reg) {
    if (!is_open) {
        return 0;
    }

    auto it = register_map.find(reg);
    if (it != register_map.end()) {
        return it->second;
    }
    return 0;
}

bool MockSMBusDriver::write_byte(uint8_t reg, uint8_t value) {
    if (!is_open) {
        return false;
    }

    register_map[reg] = value;
    return true;
}

void MockSMBusDriver::close() {
    is_open = false;
}

bool MockSMBusDriver::is_opened() {
    return is_open;
}

void MockSMBusDriver::set_register(uint8_t reg, uint8_t value) {
    register_map[reg] = value;
}

uint8_t MockSMBusDriver::get_register(uint8_t reg) const {
    auto it = register_map.find(reg);
    if (it != register_map.end()) {
        return it->second;
    }
    return 0;
}

#endif // USE_MOCK_DRIVERS
