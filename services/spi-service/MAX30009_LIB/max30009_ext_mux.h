#ifndef MAX30009_EXT_MUX_H
#define MAX30009_EXT_MUX_H

#include "VT_GPIO_interface.h"
#include "stdlib.h"

typedef struct MAX30009_EXT_MUX_GPIOs
{
    VT_GPIO_interface * CALIB_MODE;
    VT_GPIO_interface * Calib_RL_1;
    VT_GPIO_interface * Calib_RL_2;
    VT_GPIO_interface * Calib_RL_3;
    VT_GPIO_interface * Calib_RL_4;
    VT_GPIO_interface * Calib_RL_5;

} MAX30009_EXT_MUX_GPIOs_TDE;




class max30009_ext_MUX
{
public:
    max30009_ext_MUX(MAX30009_EXT_MUX_GPIOs_TDE GPIOs)
    {
        _GPIOs=GPIOs;
        if (_GPIOs.Calib_RL_1==0)
        {
            _GPIOs.Calib_RL_1=&dummy_VT_GPIO_obj;
        }
        if (_GPIOs.Calib_RL_2==0)
        {
            _GPIOs.Calib_RL_2=&dummy_VT_GPIO_obj;
        }
        if (_GPIOs.Calib_RL_4==0)
        {
            _GPIOs.Calib_RL_4=&dummy_VT_GPIO_obj;
        }
        if (_GPIOs.Calib_RL_3==0)
        {
            _GPIOs.Calib_RL_3=&dummy_VT_GPIO_obj;
        }
        if (_GPIOs.Calib_RL_5==0)
        {
            _GPIOs.Calib_RL_5=&dummy_VT_GPIO_obj;
        }
        if (_GPIOs.CALIB_MODE==0)
        {
            _GPIOs.CALIB_MODE=&dummy_VT_GPIO_obj;
        }

        _GPIOs.Calib_RL_1->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.Calib_RL_2->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.Calib_RL_4->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.Calib_RL_3->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.Calib_RL_5->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
        _GPIOs.CALIB_MODE->set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
    }
    void off_calib_mode()
    {
        set_GPIOs_out(false,0xFF);
    }

    void off_all_out()
    {
        _GPIOs.Calib_RL_1->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Calib_RL_2->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Calib_RL_4->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Calib_RL_3->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.Calib_RL_5->set_GPIO_state(VT_GPIO_UNSET);
        _GPIOs.CALIB_MODE->set_GPIO_state(VT_GPIO_UNSET);
        _is_calib_mode=true;
    }

    int32_t on_calib_mode(int32_t need_calib_resistor_value)
    {
        int32_t delta=0xFFFFFF;
        int32_t best_resistor=0;
        for (uint32_t i=0; i<RES_VALUE_COUNT; i++)
        {
            if(labs(res_value[i]-need_calib_resistor_value)<delta)
            {
                delta=labs(res_value[i]-need_calib_resistor_value);
                best_resistor=i;
            }
            else
            {
                break;
            }
        }
        set_GPIOs_out(true,res_mask[best_resistor]);
        return res_value[best_resistor];
    }

    void set_GPIOs_out(bool calib_mode, uint8_t resistor_mask)
    {
        _is_calib_mode=calib_mode;
        if (calib_mode==true)
        {
            _GPIOs.CALIB_MODE->set_GPIO_state(VT_GPIO_UNSET);
        }
        else
        {
            _GPIOs.CALIB_MODE->set_GPIO_state(VT_GPIO_SET);
        }

        //if bit is set relay must be off(not short resistor)
        if (resistor_mask & 0b00000001)
        {
            _GPIOs.Calib_RL_1->set_GPIO_state(VT_GPIO_UNSET);
        }
        else
        {
            _GPIOs.Calib_RL_1->set_GPIO_state(VT_GPIO_SET);
        }
        if (resistor_mask & 0b00000010)
        {
            _GPIOs.Calib_RL_2->set_GPIO_state(VT_GPIO_UNSET);
        }
        else
        {
            _GPIOs.Calib_RL_2->set_GPIO_state(VT_GPIO_SET);
        }
        if (resistor_mask & 0b00000100)
        {
            _GPIOs.Calib_RL_3->set_GPIO_state(VT_GPIO_UNSET);
        }
        else
        {
            _GPIOs.Calib_RL_3->set_GPIO_state(VT_GPIO_SET);
        }
        if (resistor_mask & 0b00001000)
        {
            _GPIOs.Calib_RL_4->set_GPIO_state(VT_GPIO_UNSET);
        }
        else
        {
            _GPIOs.Calib_RL_4->set_GPIO_state(VT_GPIO_SET);
        }
        if (resistor_mask & 0b00010000)
        {
            _GPIOs.Calib_RL_5->set_GPIO_state(VT_GPIO_UNSET);
        }
        else
        {
            _GPIOs.Calib_RL_5->set_GPIO_state(VT_GPIO_SET);
        }

    }

    bool get_state()
    {
        return _is_calib_mode;
    }

private:
    //R_base = 100 Ом
    //R1 = 36 Ом
    //R2 = 68 Ом
    //R3 = 150 Ом
    //R4 = 270 Ом
    //R5 = 560 Ом
    static const uint32_t RES_VALUE_COUNT=32;
    static constexpr int32_t res_value[RES_VALUE_COUNT] = {47, 83, 115, 151, 197, 233, 265, 301, 317, 353, 385, 421, 467, 503, 535, 571, 607, 643, 675, 711, 757, 793, 825, 861, 877, 913, 945, 981, 1027, 1063, 1095, 1131};
    static constexpr uint8_t res_mask[RES_VALUE_COUNT] = {0b00000000, 0b00000001, 0b00000010, 0b00000011, 0b00000100, 0b00000101, 0b00000110, 0b00000111, 0b00001000, 0b00001001, 0b00001010, 0b00001011, 0b00001100, 0b00001101, 0b00001110, 0b00001111, 0b00010000, 0b00010001, 0b00010010, 0b00010011, 0b00010100, 0b00010101, 0b00010110, 0b00010111, 0b00011000, 0b00011001, 0b00011010, 0b00011011, 0b00011100, 0b00011101, 0b00011110, 0b00011111};
    MAX30009_EXT_MUX_GPIOs_TDE _GPIOs;
    bool _is_calib_mode=false;
};

#endif // MAX30009_EXT_MUX_H
