/**
    \file VT_GPIO_interface.h
    \author VTT TEAM (OK)
    \brief VT GPIO interface file
 */
#ifndef VT_GPIO_INTERFACE_H
#define VT_GPIO_INTERFACE_H

#include "stdint.h"

typedef enum VT_GPIO_DIRECT_ENUM
{
    VT_GPIO_UNKNOW_DIRECT,
    VT_GPIO_RELEASE,
    VT_GPIO_OUTPUT,
    VT_GPIO_INPUT,
}VT_GPIO_DIRECT_TDE;

typedef enum VT_GPIO_STATE_ENUM
{
    VT_GPIO_UNSET=0,
    VT_GPIO_SET=1,
    VT_GPIO_UNKNOW=3,
}VT_GPIO_STATE_TDE;

/**
        \brief interface for VT GPIO
 */
class VT_GPIO_interface {
public:


    /**
        \brief (Virtual) set GPIO direct
        \param [in] direct - GPIO direct or release state
        \param [in] init_state - GPIO state on init for output
        \return true if success
     */
    virtual bool set_GPIO_direct(VT_GPIO_DIRECT_TDE direct,VT_GPIO_STATE_TDE init_state)=0;

    /**
        \brief (Virtual) set GPIO state
        \param [in] state - GPIO state
        \return true if success
     */
    virtual bool set_GPIO_state(VT_GPIO_STATE_TDE state)=0;

    /**
        \brief (Virtual) get GPIO state
        \return  GPIO state
     */
        virtual VT_GPIO_STATE_TDE get_GPIO_state(void)=0;

    /**
        \brief (Virtual) get GPIO state
        \return  GPIO state
     */
        virtual VT_GPIO_DIRECT_TDE get_GPIO_direct(void)=0;

};


/**
        \brief DUMMY for VT GPIO
 */
class dummy_VT_GPIO:public VT_GPIO_interface
{
public:

    bool set_GPIO_direct(VT_GPIO_DIRECT_TDE direct,VT_GPIO_STATE_TDE init_state){return false;}
    bool set_GPIO_state(VT_GPIO_STATE_TDE state){return false;}
    VT_GPIO_STATE_TDE get_GPIO_state(void){return VT_GPIO_UNKNOW;}
    VT_GPIO_DIRECT_TDE get_GPIO_direct(void){return VT_GPIO_UNKNOW_DIRECT;}
};

inline static dummy_VT_GPIO dummy_VT_GPIO_obj;
#endif // VT_GPIO_INTERFACE_H
