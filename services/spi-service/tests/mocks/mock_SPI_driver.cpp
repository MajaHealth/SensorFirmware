/**
 * Mock SPI Driver Implementation
 */

#include "mock_SPI_driver.h"
#include <cstring>

#ifdef USE_MOCK_DRIVERS

MockSPIDriver::MockSPIDriver() : is_open(false) {
}

bool MockSPIDriver::open(const char* device_path) {
    (void)device_path; // Unused in mock
    is_open = true;
    return true;
}

bool MockSPIDriver::send_byte_array(uint8_t* tx_data, uint8_t* rx_data, uint32_t length) {
    if (!is_open) {
        return false;
    }

    // Store transmitted data
    tx_buffer.clear();
    for (uint32_t i = 0; i < length; i++) {
        tx_buffer.push_back(tx_data[i]);
    }

    // Copy mock RX data to output buffer
    for (uint32_t i = 0; i < length && i < rx_buffer.size(); i++) {
        rx_data[i] = rx_buffer[i];
    }

    return true;
}

void MockSPIDriver::close() {
    is_open = false;
}

bool MockSPIDriver::is_opened() {
    return is_open;
}

void MockSPIDriver::set_rx_data(const std::vector<uint8_t>& data) {
    rx_buffer = data;
}

std::vector<uint8_t> MockSPIDriver::get_tx_data() const {
    return tx_buffer;
}

#endif // USE_MOCK_DRIVERS
