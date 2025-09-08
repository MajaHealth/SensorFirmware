/**
    \file ADS1293_IO.h
    \author VTK TEAM (OK)
    \brief ADS1293 input/output process file
 */
#ifndef ADS1293_LIB_ADS1293_IO_H_
#define ADS1293_LIB_ADS1293_IO_H_

#include "stdint.h"
#include "VT_register_process_interface.h"

#include "VT_sync_data_stream_interface.h"


namespace ADS1293
{

#define ADS1293_REGISTER_PACKET_SIZE	2
#define ADS1293_2_BYTE_REGISTER_PACKET_SIZE	3
#define ADS1293_3_BYTE_REGISTER_PACKET_SIZE	4
#define ADS1293_DUMMY_BYTE 				0xFF
#define ADS1293_READ_REQUEST_MARK		0x80
#define ADS1293_WRITE_REQUEST_MARK		0x00




/**
    \brief ADS1293 input/output process class
 */
class ADS1293_IO:public VT_register_process_interface
{
public:
    ADS1293_IO()
    {

    }
    void init(VT_sync_data_stream_interface * spi_driver_pointer)
    {
        _spi_driver_pointer=spi_driver_pointer;
    }

    bool load_from_register(uint8_t * register_data, uint8_t register_address)
    {
        register_address=register_address & 0x7F; //register size 7bit

        uint8_t request_array[ADS1293_REGISTER_PACKET_SIZE];
        request_array[0]=ADS1293_READ_REQUEST_MARK+register_address;
        request_array[1]=ADS1293_DUMMY_BYTE;

        uint8_t response_array[ADS1293_REGISTER_PACKET_SIZE]= {0,};

        if (_spi_driver_pointer->send_byte_array(request_array,response_array,ADS1293_REGISTER_PACKET_SIZE)==true)
        {
            *register_data=response_array[1];
            return true;
        }
        return false;
    }


    bool write_to_register(uint8_t * register_data, uint8_t register_address)
    {
        register_address=register_address & 0x7F; //register size 7bit

        uint8_t request_array[ADS1293_REGISTER_PACKET_SIZE];
        request_array[0]=ADS1293_WRITE_REQUEST_MARK+register_address;
        request_array[1]=*register_data;

        uint8_t response_array[ADS1293_REGISTER_PACKET_SIZE]= {0,};

        if (_spi_driver_pointer->send_byte_array(request_array,response_array,ADS1293_REGISTER_PACKET_SIZE)==true)
        {
            return true;
        }
        return false;
    }

    bool load_2_registers(uint16_t * register_data, uint8_t start_register_address)
    {
        start_register_address=start_register_address & 0x7F; //register size 7bit

        uint8_t request_array[ADS1293_2_BYTE_REGISTER_PACKET_SIZE];
        request_array[0]=ADS1293_READ_REQUEST_MARK+start_register_address;
        request_array[1]=ADS1293_DUMMY_BYTE;
        request_array[2]=ADS1293_DUMMY_BYTE;
        uint8_t response_array[ADS1293_2_BYTE_REGISTER_PACKET_SIZE]= {0,};

        if (_spi_driver_pointer->send_byte_array(request_array,response_array,ADS1293_2_BYTE_REGISTER_PACKET_SIZE)==true)
        {
            *register_data=response_array[1];
            *register_data=(*register_data<<8)+response_array[2];
            return true;
        }
        return false;
    }

    bool load_3_registers(uint32_t * register_data, uint8_t start_register_address)
    {
        start_register_address=start_register_address & 0x7F; //register size 7bit

        uint8_t request_array[ADS1293_3_BYTE_REGISTER_PACKET_SIZE];
        request_array[0]=ADS1293_READ_REQUEST_MARK+start_register_address;
        request_array[1]=ADS1293_DUMMY_BYTE;
        request_array[2]=ADS1293_DUMMY_BYTE;
        request_array[3]=ADS1293_DUMMY_BYTE;
        uint8_t response_array[ADS1293_3_BYTE_REGISTER_PACKET_SIZE]= {0,};

        if (_spi_driver_pointer->send_byte_array(request_array,response_array,ADS1293_3_BYTE_REGISTER_PACKET_SIZE)==true)
        {
            *register_data=response_array[1];
            *register_data=(*register_data<<8)+response_array[2];
            *register_data=(*register_data<<8)+response_array[3];
            return true;
        }
        return false;
    }
private:
    VT_sync_data_stream_interface * _spi_driver_pointer=0;

};



}
#endif /* ADS1293_LIB_ADS1293_IO_H_ */
