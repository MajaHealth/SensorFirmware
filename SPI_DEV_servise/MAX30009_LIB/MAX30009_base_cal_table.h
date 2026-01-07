#ifndef MAX30009_BASE_CAL_TABLE_H
#define MAX30009_BASE_CAL_TABLE_H
#include "max30009_data_struct.h"

#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include "json.hpp"

using json = nlohmann::json;

class MAX30009_base_cal_table
{
public:
    MAX30009_base_cal_table() {}

    void init( uint32_t data_count)
    {
        if (data_count>MAX_DATA_COUNT)data_count=MAX_DATA_COUNT;
        _data_count=data_count;

        std::ifstream file(TABLE_FILENAME);
        if (!file.is_open())
        {
            std::cout << TABLE_FILENAME << " - load ERROR or not found." << std::endl;
            return;
        }

        std::string line;
        uint32_t loaded_count = 0;

        while (std::getline(file, line))
        {
            if (line.empty()) continue;
            try
            {
                nlohmann::json j = nlohmann::json::parse(line);
                if (j.contains("index"))
                {
                    uint32_t i = j["index"].get<uint32_t>();
                    if (i < _data_count)
                    {
                        _calib_data[i] = get_calib_koef_from_json(j);
                        loaded_count++;
                    }
                }
            }
            catch (const std::exception& e)
            {
                std::cout << "Error parsing JSON line: " << loaded_count << std::endl;
            }
        }

        std::cout << TABLE_FILENAME << " - load OK. Loaded " << loaded_count << " records." << std::endl;
    }

    void save_calib_data(uint32_t index,const MAX30009_CALIB_DATA & calib_data)
    {
        if (index>=_data_count) return;
        _calib_data[index]=calib_data;
    }

    void save_all_calib_to_file(void)
    {
        std::ofstream outputFile(TABLE_FILENAME, std::ios::out | std::ios::trunc);

        if (outputFile.is_open())
        {
                for (uint32_t i=0; i<_data_count; i++)
                {
                    outputFile << get_calibration_json_data_by_index(i)<< std::endl;
                }
             outputFile.close();
            std::cout << "save file:" << TABLE_FILENAME << " - OK" << std::endl << std::endl;
        }
        else
        {
            std::cout << "save file:" << TABLE_FILENAME << " - ERROR" << std::endl << std::endl;
        }
    }

    MAX30009_CALIB_DATA & get_calib_data(uint32_t index)
    {
        if (index>=_data_count) return calib_zero;
        return _calib_data[index];
    }

    std::string get_calibration_json_data_by_index(uint32_t index)
    {
        if (index>=_data_count) return "";
        return  get_calibration_json_data(_calib_data[index],index);
    }

    static std::string get_calibration_json_data(const MAX30009_CALIB_DATA &calib_koef, uint32_t index=0xFFFF)
    {

        nlohmann::json response_json;
        response_json["type"] = "calib_data";
        if (index<0xFF)
        {
            response_json["index"] = index;
        }

        response_json["I_offset"] =calib_koef.I_offset;
        response_json["I_coef"] =calib_koef.I_coef;
        response_json["I_phase_coef"] =calib_koef.I_phase_coef;
        response_json["I_phase_cos"] =calib_koef.I_phase_cos;
        response_json["I_phase_sin"] =calib_koef.I_phase_sin;
        response_json["Q_offset"] =calib_koef.Q_offset;
        response_json["Q_coef"] =calib_koef.Q_coef;
        response_json["Q_phase_coef"] =calib_koef.Q_phase_coef;
        response_json["Q_phase_cos"] =calib_koef.Q_phase_cos;
        response_json["Q_phase_sin"] =calib_koef.Q_phase_sin;

        response_json["I_cal_in"] =calib_koef.I_cal_in;
        response_json["I_cal_in_ADC"] =calib_koef.I_cal_in_ADC;
        response_json["I_cal_quad"] =calib_koef.I_cal_quad;
        response_json["I_cal_quad_ADC"] =calib_koef.I_cal_quad_ADC;

        response_json["Q_cal_in"] =calib_koef.Q_cal_in;
        response_json["Q_cal_in_ADC"] =calib_koef.Q_cal_in_ADC;
        response_json["Q_cal_quad"] =calib_koef.Q_cal_quad;
        response_json["Q_cal_quad_ADC"] =calib_koef.Q_cal_quad_ADC;

        response_json["calibrate_frequency"] =calib_koef.calibrate_frequency;
        response_json["calibrate_current"] = MAX30009_STATIC::current_to_string(calib_koef.calibrate_current);
        response_json["calibrate_gain"] = MAX30009_STATIC::gain_to_string(calib_koef.calibrate_gain);
        response_json["input_filter"] = MAX30009_STATIC::hp_filter_to_string(calib_koef.input_filter);

        response_json["ref_value"] = calib_koef.ref_value;

        return response_json.dump();
    }

    // 0-19: 1kHz - 20kHz (1kHz step)
    // 20-59: 22kHz - 100kHz (2kHz step)
    //60-99: 110kHz - 500kHz (10kHz step)
    static uint32_t get_frequency_from_index(uint32_t index)
    {
        if (index <= 19)return (index + 1) * 1000;
        else if (index <= 59) return 20000 + (index - 19) * 2000;
        else if (index <= 99) return 100000 + (index - 59) * 10000;
        return 500000;
    }

    static uint32_t get_table_index(uint32_t frequency_hz)
    {
        if (frequency_hz < 1000) return 0; // 1kHz is minimum
        if (frequency_hz > 500000) return 99; // 500kHz is maximum

        if (frequency_hz <= 20000) return ((frequency_hz + 500) / 1000) - 1;
        else if (frequency_hz <= 100000) return 19 + (((frequency_hz - 20000) + 1000) / 2000);
        else return 59 + (((frequency_hz - 100000) + 5000) / 10000);
    }

private:


    MAX30009_CALIB_DATA  get_calib_koef_from_json(nlohmann::json & j)
    {
        MAX30009_CALIB_DATA out{};
        out.calibrate_current=MAX30009_CURRENT_AMP_16nA;
        out.calibrate_gain=MAX30009_BIOZ_TOTAL_GAIN_1;
        out.calibrate_frequency=1000;
        out.input_filter=MAX30009_BIOZ_IN_HPFILTER_BYPASS;
        try
        {
            if (j.contains("I_offset"))  out.I_offset=j["I_offset"];
            if (j.contains("I_coef"))  out.I_coef=j["I_coef"];
            if (j.contains("I_phase_coef"))  out.I_phase_coef=j["I_phase_coef"];
            if (j.contains("I_phase_cos"))  out.I_phase_cos=j["I_phase_cos"];
            if (j.contains("I_phase_sin"))  out.I_phase_sin=j["I_phase_sin"];

            if (j.contains("Q_offset"))  out.Q_offset=j["Q_offset"];
            if (j.contains("Q_coef"))  out.Q_coef=j["Q_coef"];
            if (j.contains("Q_phase_coef"))  out.Q_phase_coef=j["Q_phase_coef"];
            if (j.contains("Q_phase_cos"))  out.Q_phase_cos=j["Q_phase_cos"];
            if (j.contains("Q_phase_sin"))  out.Q_phase_sin=j["Q_phase_sin"];

            if (j.contains("I_cal_in"))  out.I_cal_in=j["I_cal_in"];
            if (j.contains("I_cal_in_ADC"))  out.I_cal_in_ADC=j["I_cal_in_ADC"];
            if (j.contains("I_cal_quad"))  out.I_cal_quad=j["I_cal_quad"];
            if (j.contains("I_cal_quad_ADC"))  out.I_cal_quad_ADC=j["I_cal_quad_ADC"];

            if (j.contains("Q_cal_in"))  out.Q_cal_in=j["Q_cal_in"];
            if (j.contains("Q_cal_in_ADC"))  out.Q_cal_in_ADC=j["Q_cal_in_ADC"];
            if (j.contains("Q_cal_quad"))  out.Q_cal_quad=j["Q_cal_quad"];
            if (j.contains("Q_cal_quad_ADC"))  out.Q_cal_quad_ADC=j["Q_cal_quad_ADC"];

            if (j.contains("ref_value"))  out.ref_value=j["ref_value"];

            if (j.contains("calibrate_current")) out.calibrate_current = MAX30009_STATIC::string_to_сurrent(j["calibrate_current"].get<std::string>());
            if (j.contains("calibrate_gain")) out.calibrate_gain = MAX30009_STATIC::string_to_gain(j["calibrate_gain"].get<std::string>());
            if (j.contains("input_filter"))  out.input_filter = MAX30009_STATIC::string_to_hp_filter(j["input_filter"].get<std::string>());
            if (j.contains("calibrate_frequency"))  out.calibrate_frequency=j["calibrate_frequency"];

        }
        catch (const std::exception& e)
        {

        }

        return out;
    }

    MAX30009_CALIB_DATA calib_zero{};

    uint32_t _data_count=0;
    static const uint32_t MAX_DATA_COUNT=105;
    MAX30009_CALIB_DATA _calib_data[MAX_DATA_COUNT];

    static constexpr char TABLE_FILENAME[]="base_table.json";
};

#endif // MAX30009_BASE_CAL_TABLE_H
