/**
	\file VT_sync_data_stream_interface.h
	\author VTT TEAM (OK)
	\brief VT sync data stream interface file
 */
#ifndef VT_DATA_STREAM_VT_SYNC_DATA_STREAM_INTERFACE_H_
#define VT_DATA_STREAM_VT_SYNC_DATA_STREAM_INTERFACE_H_

#include "stdint.h"


/**
		\brief interface for VT sync data stream
 */
class VT_sync_data_stream_interface {
public:


	/**
		\brief (Virtual) send byte array for data stream
		\param [in] send_data - pointer to data array for send
		\param [in] receive_data - pointer to data array for receive
		\param [in] data_dize - data size(in byte) for send
		\return true if success
	 */
    virtual bool send_byte_array(uint8_t * send_data,uint8_t * receive_data, uint32_t data_size)=0;

};

#endif /* VT_DATA_STREAM_VT_SYNC_DATA_STREAM_INTERFACE_H_ */
