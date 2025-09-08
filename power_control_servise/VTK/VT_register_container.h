/**
    \file VT_register_container.h
    \author VTK TEAM (OK)
    \brief register container class file
 */

#ifndef VD_REGISTER_CONTAINER_H_
#define VD_REGISTER_CONTAINER_H_

#include "stdint.h"
#include "VT_register_process_interface.h"

/**
    \brief register container class
 */
template <typename DATA_TYPE>
class register_container
{
public:

    register_container(VT_register_process_interface * register_process_obj,uint8_t register_address)
    {
        if (register_process_obj==nullptr)
        {

             _register_process_obj=&dummy_register_process_obj;
        }
        else
        {
            _register_process_obj=register_process_obj;
        }
        _register_address=register_address;
    }


    /**
        \brief load data to register
        \param [in] item - item value
        \return  true - if item append  succesfull
     */
    bool load_register(void)
    {
        return _register_process_obj->load_from_register((uint8_t*)&S,_register_address);
    }

    /**
        \brief append item to list container.
        \param [in] item - item value
        \return  true - if item append  succesfull
     */
    bool update_register(void)
    {
        return _register_process_obj->write_to_register((uint8_t*)&S,_register_address);
    }

    volatile DATA_TYPE S;
private:

    VT_register_process_interface * _register_process_obj=&dummy_register_process_obj;
    uint8_t _register_address=0;

};

#endif
