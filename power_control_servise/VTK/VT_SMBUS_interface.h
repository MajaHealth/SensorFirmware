#ifndef VT_SMBUS_INTERFACE_H_
#define VT_SMBUS_INTERFACE_H_

#include "stdint.h"

/**
        \brief interface for VT SMBUS
 */
class VT_SMBUS_interface {
public:
	/**
		\brief (Virtual) Open SMbus device
		\param [in] device_address - device address for opening
		\return - boolean result. true if successful
	 */
	virtual bool open(uint8_t device_address) = 0;

	/**
		\brief (Virtual) close SMbus device
		\return - boolean result. true if successful
	 */
	virtual bool close() = 0;


	/**
		\brief (Virtual) read 2 byte from SMbus device
		\param [in] register_adr - register address for read
		\param [out] result - boolean result. true if successful
		\return - if successful return value. else return 0xFFFF
	 */
	virtual uint16_t read_2byte_data(uint8_t register_adr, bool *result) = 0;

	/**
		\brief (Virtual) read one byte from SMbus device
		\param [in] register_adr - register address for read
		\param [out] result - boolean result. true if successful
		\return - if successful return value. else return 0xFF
	 */
	virtual uint8_t read_byte_data(uint8_t register_adr, bool *result) = 0;

};




#endif
