#ifndef WS2812_PROCESS_H
#define WS2812_PROCESS_H

#include "WS2812_wrap_cls.h"
#include "json.hpp"



typedef struct WS_COLOR_STRUCT
{
    float R;
    float G;
    float B;
} WS_COLOR_TDS;

class WS2812_process
{
public:
    WS2812_process()
    {
        WS2812_wrap.init();
        WS2812_wrap.clear();
        for (uint32_t i=0; i<WS_LED_COUNT; i++)
        {
            actual_colors[i].R=0;
            actual_colors[i].G=0;
            actual_colors[i].B=0;
            new_colors[i].R=0;
            new_colors[i].G=0;
            new_colors[i].B=0;
        }

    }
    virtual ~WS2812_process() {}


    void process(void)
    {
        if (transition_step>0)
        {
            transition_step--;
            if (transition_step<=0)
            {
                for (uint32_t i=0; i<WS_LED_COUNT; i++)
                {
                    actual_colors[i]=new_colors[i];
                }
            }
            else
            {
                for (uint32_t i=0; i<WS_LED_COUNT; i++)
                {
                    actual_colors[i].R=actual_colors[i].R+trans_koef[i].R;
                    actual_colors[i].G=actual_colors[i].G+trans_koef[i].G;
                    actual_colors[i].B=actual_colors[i].B+trans_koef[i].B;
                }
            }

            for (uint32_t i=0; i<WS_LED_COUNT; i++)
            {
                  WS2812_wrap.setPixelColor(i,actual_colors[i].R,actual_colors[i].G,actual_colors[i].B);
            }
            WS2812_wrap.show();
        }
}
        std::string process_JSON_line(const char * JSON_line)
        {
            std::cout << "IN:" << JSON_line << std::endl << std::endl;

            nlohmann::json parsed_json;
            nlohmann::json response;

            try
            {
                parsed_json = nlohmann::json::parse(JSON_line);

                if ( parsed_json.contains("leds") &&  parsed_json["leds"].is_array())
                {
                    std::cout << "LEDs array found:" << std::endl;

                    int led_num=0;
                    for (const auto& led_color :  parsed_json["leds"])
                    {
                        if (led_color.is_array() && led_color.size() == 3)
                        {

                            if(led_num<WS_LED_COUNT)
                            {
                                new_colors[led_num].R = led_color[0].get<uint8_t>();
                                new_colors[led_num].G  = led_color[1].get<uint8_t>();
                                new_colors[led_num].B = led_color[2].get<uint8_t>();
                            }
                             led_num++;
                        }
                        else
                        {
                            break;
                        }
                    }
                    uint32_t transition_time=0;
                    if (parsed_json.contains("t_time"))
                    {
                        transition_time=parsed_json["t_time"];
                    }
                    start_animation(transition_time);

                    return "{\"type\": \"colors_is_set\"}";
                }
                else
                {
                    response["type"] = "error JSON";
                }

            }
            catch (const std::exception& e)
            {

            }

            response["type"] = "error JSON";
            std::string response_string = response.dump();
            return response_string;

        }


        void start_animation(float transition_time)
        {
            transition_step= (transition_time*STEPS_IN_MS)+1;
            for (uint32_t i=0; i<WS_LED_COUNT; i++)
            {
                trans_koef[i].R=(new_colors[i].R-actual_colors[i].R)/transition_step;
                trans_koef[i].G=(new_colors[i].G-actual_colors[i].G)/transition_step;
                trans_koef[i].B=(new_colors[i].B-actual_colors[i].B)/transition_step;
            }
        }
protected:

private:

        static constexpr float STEPS_IN_MS=2.0;

        static const uint32_t WS_LED_COUNT=9;
        WS2812_wrap_cls WS2812_wrap{WS_LED_COUNT};

        WS_COLOR_TDS new_colors[WS_LED_COUNT];
        WS_COLOR_TDS trans_koef[WS_LED_COUNT];
        WS_COLOR_TDS actual_colors[WS_LED_COUNT];
        float transition_step=0;


    };
#endif // WS2812_PROCESS_H
