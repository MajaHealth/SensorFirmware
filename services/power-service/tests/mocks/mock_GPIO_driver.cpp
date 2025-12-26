/**
 * Mock GPIO Driver Implementation (Power Service)
 */

#include "mock_GPIO_driver.h"

#ifdef USE_MOCK_DRIVERS

MockGPIODriver::MockGPIODriver(uint32_t pin)
    : pin_number(pin), direction(VT_GPIO_RELEASE), state(false), valid(pin <= 27) {
}

bool MockGPIODriver::set_GPIO(bool new_state) {
    if (!valid || direction != VT_GPIO_OUTPUT) {
        return false;
    }
    state = new_state;
    return true;
}

bool MockGPIODriver::get_GPIO() {
    return state;
}

VT_GPIO_DIR_TYPE MockGPIODriver::get_direction() {
    return direction;
}

void MockGPIODriver::set_direction(VT_GPIO_DIR_TYPE dir) {
    direction = dir;
    if (dir == VT_GPIO_RELEASE) {
        state = false;
    }
}

bool MockGPIODriver::is_valid() {
    return valid;
}

#endif // USE_MOCK_DRIVERS
