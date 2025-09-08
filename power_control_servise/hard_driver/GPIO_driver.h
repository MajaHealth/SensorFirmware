#ifndef GPIO_DRIVER_H
#define GPIO_DRIVER_H

#include <string>
#include <cstdint>
#include <iostream>

#include <gpiod.h> // Include the main libgpiod header

#include "VT_GPIO_interface.h"
#include <errno.h>
#include <cstring>

class GPIO_driver_cls :public VT_GPIO_interface
{
public:
    GPIO_driver_cls(uint32_t gpio_num, const std::string& chip_name = "gpiochip0")
    {
        _GPIO_num=gpio_num;
        _chip = gpiod_chip_open_by_name(chip_name.c_str());

        if (!_chip)
        {
            std::cerr << "GPIO ERROR: Failed to open chip '" << chip_name << "': " << strerror(errno) << std::endl;
        }
    }

    ~GPIO_driver_cls()
    {
        if (_line)
        {
            gpiod_line_release(_line); // Release the line
            _line = nullptr;
        }
        if (_chip)
        {
            gpiod_chip_close(_chip); // Close the chip
            _chip = nullptr;
        }
    }


    bool set_GPIO_direct(VT_GPIO_DIRECT_TDE direct,VT_GPIO_STATE_TDE init_state=VT_GPIO_UNSET)
    {
        if (!_chip)
        {
            std::cerr << "GPIO ERROR: Chip not initialized." << std::endl;
            return false;
        }

        if (_direct==direct && _line)
        {
            return true;   // not need change direct
        }

        if (_line)
        {
            gpiod_line_release(_line);
        }

        if (direct==VT_GPIO_RELEASE)
        {
            _line = nullptr;
            _direct=VT_GPIO_RELEASE;
            return true;
        }

        _line = gpiod_chip_get_line(_chip, _GPIO_num);

        if (!_line)
        {
            std::cerr << "GPIO ERROR: Failed to get line " << _GPIO_num << ": " << strerror(errno) << std::endl;
            return false;
            return false;
        }

        if (_line)
        {
            int result=-1;
            if (direct==VT_GPIO_OUTPUT)
            {
                int init_state_value=0;
                if (init_state==VT_GPIO_SET)
                {
                    init_state_value=1;
                }
                result = gpiod_line_request_output(_line, "VT_GPIO_driver", init_state_value);
                if (result>=0)
                {
                    _direct=VT_GPIO_OUTPUT;
                    return true;
                }
            }
            else if (direct==VT_GPIO_INPUT)
            {
                result = gpiod_line_request_input(_line, "VT_GPIO_driver");
                if (result>=0)
                {
                    _direct=VT_GPIO_INPUT;
                    return true;
                }
            }
        }

        if (_line)
        {
            gpiod_line_release(_line);
        }



        _line = nullptr;
        _direct=VT_GPIO_UNKNOW_DIRECT;
        return false;
    }

    bool set_GPIO_state(VT_GPIO_STATE_TDE state)
    {
        if (!_line)
        {
            return false;
        }
        if (_direct!=VT_GPIO_OUTPUT)
        {
            return false;
        }

        int result=-1;
        if (state==VT_GPIO_SET)
        {
            result = gpiod_line_set_value(_line, 1);
        }
        else if (state==VT_GPIO_UNSET)
        {
            result = gpiod_line_set_value(_line, 0);
        }

        if (result < 0)
        {
            return false;
        }
        return true;
    }

    VT_GPIO_STATE_TDE get_GPIO_state(void)
    {
        if (!_line)
        {
            return VT_GPIO_UNKNOW;
        }
        if (_direct!=VT_GPIO_INPUT)
        {
            return VT_GPIO_UNKNOW;
        }

        int value = gpiod_line_get_value(_line);
        if (value==0)
        {
            return VT_GPIO_UNSET;
        }
        if (value==1)
        {
            return VT_GPIO_SET;
        }
        return VT_GPIO_UNKNOW;
    }

    VT_GPIO_DIRECT_TDE get_GPIO_direct(void)
    {
        return _direct;
    }

    // Checks if the GPIO_driver_cls object has been successfully initialized.
    bool is_initialized() const
    {
        return _line != nullptr;
    }

private:

    VT_GPIO_DIRECT_TDE _direct=VT_GPIO_UNKNOW_DIRECT;
    gpiod_chip *_chip=nullptr;
    gpiod_line *_line=nullptr; // Pointer to the single line managed by this object
    int _GPIO_num=0;
};

#endif // GPIO_DRIVER_H
