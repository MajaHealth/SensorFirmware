#ifndef MAX30009_USER_SET_H
#define MAX30009_USER_SET_H
#include "max30009_data_struct.h"
#include "json.hpp"
#include "MAX30009_STATIC.h"
#include "max30009_lib.h"
using json = nlohmann::json;

typedef struct MAX30009_USER_SETTINGS
{
    uint32_t stimulate_frequency_hz;
    uint32_t measure_frequency_hz;

    MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE out_LP_filter;
    MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE out_HP_filter;
    MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE input_HP_filter;

    MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE bioz_total_gain;
    MAX30009_CURRENT_AMP_ENUM_TYPE  stimulate_current;

    bool measure_enable;
    bool lead_bias_enable;


} MAX30009_USER_SETTINGS_TDE;

class MAX30009_uset
{
public:

    MAX30009_uset()
    {
        MAX30009_user_sett.stimulate_frequency_hz = 10000;
        MAX30009_user_sett.measure_frequency_hz = 5;

        MAX30009_user_sett.out_LP_filter = MAX30009_BIOZ_DLPF_BYPASS;
        MAX30009_user_sett.out_HP_filter = MAX30009_BIOZ_DHPF_BYPASS;
        MAX30009_user_sett.input_HP_filter = MAX30009_BIOZ_IN_HPFILTER_BYPASS;

        MAX30009_user_sett.bioz_total_gain = MAX30009_BIOZ_TOTAL_GAIN_1;
        MAX30009_user_sett.stimulate_current = MAX30009_CURRENT_AMP_16nA;

        MAX30009_user_sett.measure_enable = false;
        MAX30009_user_sett.lead_bias_enable = false;
    }

    bool process_JSON_settings(const char * JSON_line)
    {

        json parsed_json;

        try
        {
            parsed_json = json::parse(JSON_line);

            if (parsed_json.contains("stimulate_current"))
            {
                MAX30009_CURRENT_AMP_ENUM_TYPE current=MAX30009_STATIC::string_to_сurrent(parsed_json["stimulate_current"]);
                if (current==MAX30009_CURRENT_ERROR)
                {
                    return false;
                }
                MAX30009_user_sett.stimulate_current=current;
            }

            if (parsed_json.contains("input_HP_filter"))
            {
                MAX30009_user_sett.input_HP_filter=MAX30009_STATIC::string_to_hp_filter(parsed_json["input_HP_filter"]);
            }

            if (parsed_json.contains("stimulate_frequency"))
            {
                MAX30009_user_sett.stimulate_frequency_hz=parsed_json["stimulate_frequency"];
            }
            if (parsed_json.contains("measure_frequency"))
            {
                MAX30009_user_sett.measure_frequency_hz=parsed_json["measure_frequency"];
            }
            if (parsed_json.contains("out_LP_filter"))
            {
                MAX30009_user_sett.out_LP_filter = MAX30009_STATIC::string_to_digital_lp_filter(parsed_json["out_LP_filter"]);
            }
            if (parsed_json.contains("out_HP_filter"))
            {
                MAX30009_user_sett.out_HP_filter = MAX30009_STATIC::string_to_digital_hp_filter(parsed_json["out_HP_filter"]);
            }
            if (parsed_json.contains("measure_enable"))
            {
                MAX30009_user_sett.measure_enable = parsed_json["measure_enable"];
            }


            if ( MAX30009_user_sett.measure_frequency_hz<MIN_MEASURE_FREQ)    MAX30009_user_sett.measure_frequency_hz=MIN_MEASURE_FREQ;
            if ( MAX30009_user_sett.measure_frequency_hz>MAX_MEASURE_FREQ)    MAX30009_user_sett.measure_frequency_hz=MAX_MEASURE_FREQ;

            return true;

        }
        catch (const std::exception& e)
        {

        }
        return false;
    }


    std::string get_all_settings_as_json(void)
    {
        nlohmann::json response_json;
        response_json["type"] = "actual_settings";
        response_json["stimulate_frequency"] = MAX30009_user_sett.stimulate_frequency_hz;
        response_json["measure_frequency"] = MAX30009_user_sett.measure_frequency_hz;
        response_json["input_HP_filter"] =  MAX30009_STATIC::hp_filter_to_string(MAX30009_user_sett.input_HP_filter);
        response_json["out_LP_filter"] =MAX30009_STATIC::digital_lp_filter_to_string(MAX30009_user_sett.out_LP_filter);
        response_json["out_HP_filter"] = MAX30009_STATIC::digital_hp_filter_to_string(MAX30009_user_sett.out_HP_filter);
        response_json["stimulate_current"] = MAX30009_STATIC::current_to_string(MAX30009_user_sett.stimulate_current);
        response_json["gain"] = MAX30009_STATIC::gain_to_string(MAX30009_user_sett.bioz_total_gain);
        response_json["measure_enable"] = MAX30009_user_sett.measure_enable;
        return response_json.dump();
    }

    void update_real_stimulate_freq(uint32_t stim_freq_hz)
    {
        MAX30009_user_sett.stimulate_frequency_hz=stim_freq_hz;
    }


    void update_real_measure_freq(uint32_t measure_freq_hz)
    {
        MAX30009_user_sett.measure_frequency_hz=measure_freq_hz;
    }

    void update_real_gain(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE gain)
    {
        MAX30009_user_sett.bioz_total_gain=gain;
    }

    void update_total_gain(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE bioz_total_gain)
    {
        MAX30009_user_sett.bioz_total_gain=bioz_total_gain;
    }

    void update_stim_current( MAX30009_CURRENT_AMP_ENUM_TYPE current)
    {
        MAX30009_user_sett.stimulate_current=current;
    }

    const MAX30009_USER_SETTINGS_TDE  & get_set() const
    {
        return MAX30009_user_sett;
    }

private:
    static const uint32_t MIN_MEASURE_FREQ	=1;
    static const uint32_t MAX_MEASURE_FREQ=500;
    MAX30009_USER_SETTINGS_TDE MAX30009_user_sett= {0};
};

#endif // MAX30009_USER_SET_H
