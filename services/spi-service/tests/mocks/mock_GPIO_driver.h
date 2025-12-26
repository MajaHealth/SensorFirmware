/**
 * Mock GPIO Driver for Testing
 * Implements VT_GPIO_interface without hardware dependencies
 */

#ifndef MOCK_GPIO_DRIVER_H
#define MOCK_GPIO_DRIVER_H

#include "VT_GPIO_interface.h"

#ifdef USE_MOCK_DRIVERS

class MockGPIODriver : public VT_GPIO_interface {
private:
    uint32_t pin_number;
    VT_GPIO_DIR_TYPE direction;
    bool state;
    bool valid;

public:
    MockGPIODriver(uint32_t pin);
    virtual ~MockGPIODriver() = default;

    // VT_GPIO_interface implementation
    virtual bool set_GPIO(bool state) override;
    virtual bool get_GPIO() override;
    virtual VT_GPIO_DIR_TYPE get_direction() override;
    virtual void set_direction(VT_GPIO_DIR_TYPE dir) override;
    virtual bool is_valid() override;
};

#endif // USE_MOCK_DRIVERS

#endif // MOCK_GPIO_DRIVER_H
