#ifndef VT_SMBUS_STM_H_
#define VT_SMBUS_STM_H_


#include "stdint.h"
#include "VT_SMBUS_interface.h"


#include <iostream>
#include <string>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>


extern "C" {
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
}

/**
        \brief  VT SMBUS driver
 */
class VT_SMBUS_driver: public VT_SMBUS_interface
{
public:

    bool open(uint8_t device_address)
    {

        if (_is_open==true)
        {
            return true;
        }

        _is_open=false;
        _device_address=device_address;


        std::string i2c_bus_path = "/dev/i2c-1";

        file_descriptor = ::open(i2c_bus_path.c_str(), O_RDWR);
        if (file_descriptor < 0)
        {
            std::cerr << "ERROR I2C BUS OPEN." << std::endl;
            return false;
        }

        if (ioctl(file_descriptor, I2C_SLAVE, _device_address) < 0)
        {
            std::cerr << "ERROR I2C ADRRESS" << std::endl;
            ::close(file_descriptor);
            file_descriptor = -1;
            return false;
        }

        _is_open=true;
        return true;
    }


    bool close()
    {
        if (_is_open==false)
        {
            return false;
        }
        ::close(file_descriptor);
        file_descriptor = -1;
        _is_open=false;
        return true;
    }


    uint16_t read_2byte_data(uint8_t register_adr, bool *result=&dummy_result)
    {
        if (_is_open==false)
        {
            *result=false;
            return 0xFFFF;
        }


        int data = i2c_smbus_read_word_data(file_descriptor, register_adr);
        if (data < 0)
        {
            std::cerr << "ERROR I2C READ DATA" << std::endl;
            *result=false;
            return 0xFFFF;
        }

        *result=true;
        return data;
    }

    uint8_t read_byte_data(uint8_t register_adr, bool *result=&dummy_result)
    {
        if (_is_open==true)
        {

        }

        *result=false;
        return 0xFF;
    }

private:
    bool _is_open=false;
    uint8_t _device_address=0;
    static bool dummy_result;
    int file_descriptor=0;
};




#endif
