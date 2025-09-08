#ifndef SPI_HARD_DRIVER_H
#define SPI_HARD_DRIVER_H

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

#include "VT_sync_data_stream_interface.h"




class SPI_hard_driver_cls : public VT_sync_data_stream_interface
{
public:
 SPI_hard_driver_cls(const char * spi_device_path)
    {

        _device_desc = open(spi_device_path, O_RDWR);
        if (_device_desc < 0)
        {
            perror("Error: Failed to open SPI device in constructor");
        }
    }

    ~SPI_hard_driver_cls()
    {
        if (_device_desc >= 0)
        {
            close(_device_desc);
        }
    }

    bool send_byte_array( uint8_t * request_array,uint8_t * response_array,uint32_t data_size)
    {

       if (_device_desc < 0)
        {
            // std::cerr << "Error: SPI device not initialized/opened." << std::endl;
            return false;
        }

        struct spi_ioc_transfer tr =
        {
            .tx_buf = (unsigned long)request_array,
            .rx_buf = (unsigned long)response_array,
            .len = data_size,
            .speed_hz = 5000000,
            .delay_usecs = 5,
            .bits_per_word = 8,
        };

        if (ioctl(_device_desc, SPI_IOC_MESSAGE(1), &tr) < 0)
        {
            perror("Failed send to SPI ");
            return false;
        }

        return true;
    }
protected:

private:
   int _device_desc = -1;

};

#endif // SPI_DRIVER_H
