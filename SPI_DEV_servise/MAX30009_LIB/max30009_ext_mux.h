#ifndef MAX30009_EXT_MUX_H
#define MAX30009_EXT_MUX_H

#include "VT_GPIO_interface.h"

typedef struct MAX30009_EXT_MUX_GPIOs
{
    VT_GPIO_interface * SP_channel;
    VT_GPIO_interface * MP_channel;
    VT_GPIO_interface * MN_channel;
    VT_GPIO_interface * SN_channel;
    VT_GPIO_interface * two_wire;
    VT_GPIO_interface * calib_resistor;
    VT_GPIO_interface * Cole_Cole;

}MAX30009_EXT_MUX_GPIOs_TDE;

typedef enum MAX30009_EXT_MUX_STATE
{
    MAX30009_EXT_MUX_ALL_OFF=0,
     MAX30009_EXT_MUX_4_WIRE=1,
    MAX30009_EXT_MUX_2_WIRE=2,
    MAX30009_EXT_MUX_CALIBRATE=3,
    MAX30009_EXT_MUX_COLE_COLE=4,
}MAX30009_EXT_MUX_STATE_TDE;

class max30009_ext_MUX
{
public:
    max30009_ext_MUX(MAX30009_EXT_MUX_GPIOs_TDE GPIOs)
    {
        _GPIOs=GPIOs;
        if (_GPIOs.SP_channel==0) {_GPIOs.SP_channel=&dummy_VT_GPIO_obj;}
        if (_GPIOs.MP_channel==0) {_GPIOs.MP_channel=&dummy_VT_GPIO_obj;}
        if (_GPIOs.SN_channel==0) {_GPIOs.SN_channel=&dummy_VT_GPIO_obj;}
        if (_GPIOs.MN_channel==0) {_GPIOs.MN_channel=&dummy_VT_GPIO_obj;}
        if (_GPIOs.two_wire==0) {_GPIOs.two_wire=&dummy_VT_GPIO_obj;}
        if (_GPIOs.calib_resistor==0) {_GPIOs.calib_resistor=&dummy_VT_GPIO_obj;}
        if (_GPIOs.Cole_Cole==0) {_GPIOs.Cole_Cole=&dummy_VT_GPIO_obj;}

        _GPIOs.SP_channel->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.MP_channel->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.SN_channel->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.MN_channel->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.two_wire->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.calib_resistor->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.Cole_Cole->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
    }
    void set_all_off_mode()
    {
        _GPIOs.SP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.MP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.SN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.MN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.two_wire->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.calib_resistor->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Cole_Cole->set_GPIO_state(VT_GPIO_UNSET);
        _MUX_state = MAX30009_EXT_MUX_ALL_OFF;
    }


    void set_4_wire_mode()
    {
        _GPIOs.SP_channel->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.MP_channel->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.SN_channel->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.MN_channel->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.two_wire->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.calib_resistor->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Cole_Cole->set_GPIO_state(VT_GPIO_UNSET);
        _MUX_state = MAX30009_EXT_MUX_4_WIRE;
    }


    void set_2_wire_mode()
    {
        _GPIOs.SP_channel->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.MP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.SN_channel->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.MN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.two_wire->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.calib_resistor->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Cole_Cole->set_GPIO_state(VT_GPIO_UNSET);
        _MUX_state = MAX30009_EXT_MUX_2_WIRE;
    }

    void set_calibrate_mode()
    {
        _GPIOs.SP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.MP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.SN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.MN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.two_wire->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.calib_resistor->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.Cole_Cole->set_GPIO_state(VT_GPIO_UNSET);
        _MUX_state = MAX30009_EXT_MUX_CALIBRATE;
    }

    void set_Cole_Cole_mode()
    {
        _GPIOs.SP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.MP_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.SN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.MN_channel->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.two_wire->set_GPIO_state(VT_GPIO_SET);
        _GPIOs.calib_resistor->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Cole_Cole->set_GPIO_state(VT_GPIO_SET);
        _MUX_state = MAX30009_EXT_MUX_COLE_COLE;
    }

    MAX30009_EXT_MUX_STATE_TDE get_state()
    {
       return _MUX_state;
    }
private:
    MAX30009_EXT_MUX_GPIOs_TDE _GPIOs;
    MAX30009_EXT_MUX_STATE_TDE _MUX_state;
};

#endif // MAX30009_EXT_MUX_H
