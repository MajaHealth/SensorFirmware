/**
 * Mock GPIO Driver for Testing (Power Service)
 * Implements VT_GPIO_interface without hardware dependencies
 */

#ifndef MOCK_GPIO_DRIVER_POWER_H
#define MOCK_GPIO_DRIVER_POWER_H

#include "VT_GPIO_interface.h"

#ifdef USE_MOCK_DRIVERS

// Same implementation as SPI service mock
// Can be shared or copied depending on build system setup

class MockGPIODriver : public VT_GPIO_interface {
private:
    uint32_t pin_number;
    VT_GPIO_DIR_TYPE direction;
    bool state;
    bool valid;

public:
    MockGPIODriver(uint32_t pin);
    virtual ~MockGPIODriver() = default;

    virtual bool set_GPIO(bool state) override;
    virtual bool get_GPIO() override;
    virtual VT_GPIO_DIR_TYPE get_direction() override;
    virtual void set_direction(VT_GPIO_DIR_TYPE dir) override;
    virtual bool is_valid() override;
};

#endif // USE_MOCK_DRIVERS

#endif // MOCK_GPIO_DRIVER_POWER_H
