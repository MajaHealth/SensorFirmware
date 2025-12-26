/**
 * Mock SPI Driver for Testing
 * Implements VT_sync_data_stream_interface without hardware dependencies
 */

#ifndef MOCK_SPI_DRIVER_H
#define MOCK_SPI_DRIVER_H

#include "VT_sync_data_stream_interface.h"
#include <vector>
#include <cstdint>

#ifdef USE_MOCK_DRIVERS

class MockSPIDriver : public VT_sync_data_stream_interface {
private:
    bool is_open;
    std::vector<uint8_t> tx_buffer;
    std::vector<uint8_t> rx_buffer;

public:
    MockSPIDriver();
    virtual ~MockSPIDriver() = default;

    // VT_sync_data_stream_interface implementation
    virtual bool open(const char* device_path) override;
    virtual bool send_byte_array(uint8_t* tx_data, uint8_t* rx_data, uint32_t length) override;
    virtual void close() override;
    virtual bool is_opened() override;

    // Test utility methods
    void set_rx_data(const std::vector<uint8_t>& data);
    std::vector<uint8_t> get_tx_data() const;
};

#endif // USE_MOCK_DRIVERS

#endif // MOCK_SPI_DRIVER_H
