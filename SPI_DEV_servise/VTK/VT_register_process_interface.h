
#ifndef ADS1293_LIB_VT_REGISTER_PROCESS_INTERFACE_H_
#define ADS1293_LIB_VT_REGISTER_PROCESS_INTERFACE_H_

/**
    \brief register process interface
 */
class  VT_register_process_interface
{
public:

	virtual bool load_from_register(uint8_t * register_data, uint8_t register_address)=0;
	virtual bool write_to_register(uint8_t * register_data, uint8_t register_address)=0;
};

class dummy_register_process :public VT_register_process_interface
{
	bool load_from_register(uint8_t * register_data, uint8_t register_address){return false;}
	bool write_to_register(uint8_t * register_data, uint8_t register_address){return false;}
};

inline static dummy_register_process dummy_register_process_obj;

#endif /* ADS1293_LIB_VT_REGISTER_PROCESS_INTERFACE_H_ */
