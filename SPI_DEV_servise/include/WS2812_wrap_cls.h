#ifndef WS2812_WRAP_CLS_H
#define WS2812_WRAP_CLS_H

#include "ws2811.h"

class WS2812_wrap_cls
{
public:
    WS2812_wrap_cls(int led_count, int gpio_pin = 18, int DMA_channel = 10,
                    int brightness = 255, int strip_type = WS2811_STRIP_GRB)
    {
        _led_count=led_count;
        _initialized=false;


        if (led_count <= 0)            return;
        if (gpio_pin<= 0)            return;
        if (brightness < 0 || brightness > 255) return;

        _ledstring =
        {
            .freq = WS2811_TARGET_FREQ,
            .dmanum = DMA_channel,
            .channel =
            {
                [0] =
                {
                    .gpionum = gpio_pin,
                    .invert = 0,
                    .count = led_count,
                    .strip_type = strip_type,
                    .brightness = brightness,
                },
                [1] =
                {
                    .gpionum = 0,
                    .invert = 0,
                    .count = 0,
                    .brightness = 0,
                },
            },
        };


    }
    virtual ~WS2812_wrap_cls()
    {
        if (_initialized)
        {
            clear();
            ws2811_fini(&_ledstring);
        }
    }

    bool init()
    {
        ws2811_return_t ret = ws2811_init(&_ledstring);
        if (ret != WS2811_SUCCESS)
        {
            _initialized = false;
            return false;
        }
        _initialized = true;
        std::cout << "LEDStrip: Initialized successfully." << std::endl;
        return true;
    }


    void setPixelColor(int index, uint8_t r, uint8_t g, uint8_t b)
    {
        if (index < 0 || index >= _led_count)
        {
            return;
        }
        _ledstring.channel[0].leds[index] = (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | static_cast<uint32_t>(b);

    }


    void fillStrip(uint8_t r, uint8_t g, uint8_t b)
    {
        uint32_t color = (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | static_cast<uint32_t>(b);
        for (int i = 0; i < _led_count; ++i)
        {
            _ledstring.channel[0].leds[i] = color;
        }
    }

    bool show()
    {
        if (!_initialized) return false;

        ws2811_return_t ret = ws2811_render(&_ledstring);
        if (ret != WS2811_SUCCESS) return false;
        return true;
    }


    void clear()
    {
        fillStrip(0, 0, 0);
        show();
    }


    int getLEDCount() const
    {
        return _led_count;
    }



private:
    ws2811_t _ledstring;
    int _led_count;
    bool _initialized;


};

#endif // WS2812_WRAP_CLS_H
