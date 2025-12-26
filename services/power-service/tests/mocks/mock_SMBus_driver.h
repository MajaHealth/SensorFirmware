/**
 * Mock SMBus Driver for Testing
 * Implements VT_SMBUS_interface without hardware dependencies
 */

#ifndef MOCK_SMBUS_DRIVER_H
#define MOCK_SMBUS_DRIVER_H

#include "VT_SMBUS_interface.h"
#include <map>
#include <cstdint>

#ifdef USE_MOCK_DRIVERS

class MockSMBusDriver : public VT_SMBUS_interface {
private:
    bool is_open;
    uint8_t device_address;
    std::map<uint8_t, uint8_t> register_map;

public:
    MockSMBusDriver();
    virtual ~MockSMBusDriver() = default;

    // VT_SMBUS_interface implementation
    virtual bool open(const char* device_path, uint8_t addr) override;
    virtual uint8_t read_byte(uint8_t reg) override;
    virtual bool write_byte(uint8_t reg, uint8_t value) override;
    virtual void close() override;
    virtual bool is_opened() override;

    // Test utility methods
    void set_register(uint8_t reg, uint8_t value);
    uint8_t get_register(uint8_t reg) const;
};

#endif // USE_MOCK_DRIVERS

#endif // MOCK_SMBUS_DRIVER_H
