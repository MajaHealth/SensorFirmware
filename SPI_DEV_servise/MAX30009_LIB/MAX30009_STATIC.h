#ifndef MAX30009_STATIC_H
#define MAX30009_STATIC_H
#include "max30009_data_struct.h"

#include <string>
#include <chrono>
#include <iomanip>
#include <ctime>
#include <sstream>

class MAX30009_STATIC
{
public:

    static std::string get_timestamp_string()
    {
        auto now = std::chrono::system_clock::now();
        std::time_t now_c = std::chrono::system_clock::to_time_t(now);

        std::tm ptm;
        gmtime_r(&now_c, &ptm);

        std::stringstream ss;

        ss << std::put_time(&ptm, "%Y-%m-%d %H:%M:%S");


        auto duration = now.time_since_epoch();
        auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(duration) % 1000;

        ss << "." << std::setfill('0') << std::setw(3) << milliseconds.count();

        return ss.str();
    }

     static std::string get_filename_timestamp_string()
    {
        auto now = std::chrono::system_clock::now();
        std::time_t now_c = std::chrono::system_clock::to_time_t(now);

        std::tm ptm;
        gmtime_r(&now_c, &ptm);

        std::stringstream ss;

        ss << std::put_time(&ptm, "%Y-%m-%d %H_%M_%S");

        return ss.str();
    }

    static MAX30009_CURRENT_AMP_ENUM_TYPE string_to_сurrent(const std::string& current_str)
    {
        if (current_str == "16nA") return MAX30009_CURRENT_AMP_16nA;
        if (current_str == "32nA") return MAX30009_CURRENT_AMP_32nA;
        if (current_str == "80nA") return MAX30009_CURRENT_AMP_80nA;
        if (current_str == "160nA") return MAX30009_CURRENT_AMP_160nA;
        if (current_str == "320nA") return MAX30009_CURRENT_AMP_320nA;
        if (current_str == "640nA") return MAX30009_CURRENT_AMP_640nA;
        if (current_str == "1.6uA") return MAX30009_CURRENT_AMP_1_6uA;
        if (current_str == "3.2uA") return MAX30009_CURRENT_AMP_3_2uA;
        if (current_str == "6.4uA") return MAX30009_CURRENT_AMP_6_4uA;
        if (current_str == "12.8uA") return MAX30009_CURRENT_AMP_12_8uA;
        if (current_str == "32uA") return MAX30009_CURRENT_AMP_32uA;
        if (current_str == "64uA") return MAX30009_CURRENT_AMP_64uA;
        if (current_str == "128uA") return MAX30009_CURRENT_AMP_128uA;
        if (current_str == "256uA") return MAX30009_CURRENT_AMP_256uA;
        if (current_str == "640uA") return MAX30009_CURRENT_AMP_640uA;
        if (current_str == "1.28mA") return MAX30009_CURRENT_AMP_1_28mA;

        return MAX30009_CURRENT_ERROR;
    }


    static std::string current_to_string(MAX30009_CURRENT_AMP_ENUM_TYPE current_enum)
    {
        switch (current_enum)
        {
        case MAX30009_CURRENT_AMP_16nA:
            return "16nA";
        case MAX30009_CURRENT_AMP_32nA:
            return "32nA";
        case MAX30009_CURRENT_AMP_80nA:
            return "80nA";
        case MAX30009_CURRENT_AMP_160nA:
            return "160nA";
        case MAX30009_CURRENT_AMP_320nA:
            return "320nA";
        case MAX30009_CURRENT_AMP_640nA:
            return "640nA";
        case MAX30009_CURRENT_AMP_1_6uA:
            return "1.6uA";
        case MAX30009_CURRENT_AMP_3_2uA:
            return "3.2uA";
        case MAX30009_CURRENT_AMP_6_4uA:
            return "6.4uA";
        case MAX30009_CURRENT_AMP_12_8uA:
            return "12.8uA";
        case MAX30009_CURRENT_AMP_32uA:
            return "32uA";
        case MAX30009_CURRENT_AMP_64uA:
            return "64uA";
        case MAX30009_CURRENT_AMP_128uA:
            return "128uA";
        case MAX30009_CURRENT_AMP_256uA:
            return "256uA";
        case MAX30009_CURRENT_AMP_640uA:
            return "640uA";
        case MAX30009_CURRENT_AMP_1_28mA:
            return "1.28mA";
        default:
            return "UNKNOWN_CURRENT";
        }
    }

    static MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE string_to_gain(const std::string& gain_str)
    {
        if (gain_str == "x1") return MAX30009_BIOZ_TOTAL_GAIN_1;
        if (gain_str == "x2") return MAX30009_BIOZ_TOTAL_GAIN_2;
        if (gain_str == "x5") return MAX30009_BIOZ_TOTAL_GAIN_5;
        if (gain_str == "x10") return MAX30009_BIOZ_TOTAL_GAIN_10;

        return MAX30009_BIOZ_TOTAL_GAIN_1;
    }

    static std::string gain_to_string(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE gain_enum)
    {
        switch (gain_enum)
        {
        case MAX30009_BIOZ_TOTAL_GAIN_1:
            return "x1";
        case MAX30009_BIOZ_TOTAL_GAIN_2:
            return "x2";
        case MAX30009_BIOZ_TOTAL_GAIN_5:
            return "x5";
        case MAX30009_BIOZ_TOTAL_GAIN_10:
            return "x10";
        default:
            return "UNKNOWN_GAIN";
        }
    }


    static std::string calib_state_to_string(MAX30009_CALIB_STATE_ENUM_TYPE state)
    {
        switch (state)
        {
        case MAX30009_CALIB_STATE_NODATA:
            return "CALIB_STATE_NODATA";
        case MAX30009_CALIB_STATE_NEED_CALIB:
            return "CALIB_STATE_NEED_CALIB";
        case MAX30009_CALIB_STATE_PRE_START_CALIB:
            return "CALIB_STATE_PRE_START_CALIB";
        case MAX30009_CALIB_STATE_START_MEAS_OFFSET:
            return "CALIB_STATE_START_MEAS_OFFSET";
        case MAX30009_CALIB_STATE_MEAS_OFFSET:
            return "CALIB_STATE_MEAS_OFFSET";
        case MAX30009_CALIB_STATE_START_MEAS_IN_PHASE:
            return "CALIB_STATE_START_MEAS_IN_PHASE";
        case MAX30009_CALIB_STATE_MEAS_IN_PHASE:
            return "CALIB_STATE_MEAS_IN_PHASE";
        case MAX30009_CALIB_STATE_START_MEAS_QUAD:
            return "CALIB_STATE_START_MEAS_QUAD";
        case MAX30009_CALIB_STATE_MEAS_QUAD:
            return "CALIB_STATE_MEAS_QUAD";
        case MAX30009_CALIB_STATE_CALCULATE_COEF:
            return "CALIB_STATE_CALCULATE_COEF";
        case MAX30009_CALIB_STATE_READY:
            return "CALIB_STATE_READY";
        case MAX30009_CALIB_STATE_PRE_READY:
            return "CALIB_STATE_PRE_READY";
        case MAX30009_CALIB_STATE_STOPED:
            return "CALIB_STATE_STOPED";
        case MAX30009_CALIB_WAIT_DATA:
            return "CALIB_WAIT_DATA";
        case MAX30009_CALIB_IN_DELAY:
            return "CALIB_IN_DELAY";
        default:
            return "UNKNOWN_STATE";
        }
    }

    static MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE string_to_hp_filter(const std::string& filter_str)
    {
        if (filter_str == "100Hz")   return MAX30009_BIOZ_IN_HPFILTER_100Hz;
        if (filter_str == "200Hz")   return MAX30009_BIOZ_IN_HPFILTER_200Hz;
        if (filter_str == "500Hz")   return MAX30009_BIOZ_IN_HPFILTER_500Hz;
        if (filter_str == "1000Hz")  return MAX30009_BIOZ_IN_HPFILTER_1000Hz;
        if (filter_str == "2000Hz")  return MAX30009_BIOZ_IN_HPFILTER_2000Hz;
        if (filter_str == "5000Hz")  return MAX30009_BIOZ_IN_HPFILTER_5000Hz;
        if (filter_str == "10000Hz") return MAX30009_BIOZ_IN_HPFILTER_10000Hz;
        if (filter_str == "BYPASS")  return MAX30009_BIOZ_IN_HPFILTER_BYPASS;

        return MAX30009_BIOZ_IN_HPFILTER_BYPASS;
    }

    static std::string hp_filter_to_string(MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE filter_enum)
    {
        switch (filter_enum)
        {
        case MAX30009_BIOZ_IN_HPFILTER_100Hz:
            return "100Hz";
        case MAX30009_BIOZ_IN_HPFILTER_200Hz:
            return "200Hz";
        case MAX30009_BIOZ_IN_HPFILTER_500Hz:
            return "500Hz";
        case MAX30009_BIOZ_IN_HPFILTER_1000Hz:
            return "1000Hz";
        case MAX30009_BIOZ_IN_HPFILTER_2000Hz:
            return "2000Hz";
        case MAX30009_BIOZ_IN_HPFILTER_5000Hz:
            return "5000Hz";
        case MAX30009_BIOZ_IN_HPFILTER_10000Hz:
            return "10000Hz";
        case MAX30009_BIOZ_IN_HPFILTER_BYPASS:
            return "BYPASS";
        default:
            return "UNKNOWN_FILTER";
        }
    }

    static MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE string_to_digital_hp_filter(const std::string& filter_str)
    {
        if (filter_str == "BYPASS")      return MAX30009_BIOZ_DHPF_BYPASS;
        if (filter_str == "0_00025xSR")  return MAX30009_BIOZ_DHPF_0_00025xSR_BIOZ;
        if (filter_str == "0_002xSR")    return MAX30009_BIOZ_DHPF_0_002xSR_BIOZ;
        return MAX30009_BIOZ_DHPF_BYPASS;
    }

    static std::string digital_hp_filter_to_string(MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE filter_enum)
    {
        switch (filter_enum)
        {
        case MAX30009_BIOZ_DHPF_BYPASS:
            return "BYPASS";
        case MAX30009_BIOZ_DHPF_0_00025xSR_BIOZ:
            return "0_00025xSR";
        case MAX30009_BIOZ_DHPF_0_002xSR_BIOZ:
            return "0_002xSR";
        default:
            return "UNKNOWN_DHPF";
        }
    }

    static MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE string_to_digital_lp_filter(const std::string& filter_str)
    {
        if (filter_str == "BYPASS")    return MAX30009_BIOZ_DLPF_BYPASS;
        if (filter_str == "0_005xSR")  return MAX30009_BIOZ_DLPF_0_005xSR_BIOZ;
        if (filter_str == "0_02xSR")   return MAX30009_BIOZ_DLPF_0_02xSR_BIOZ;
        if (filter_str == "0_08xSR")   return MAX30009_BIOZ_DLPF_0_08xSR_BIOZ;
        if (filter_str == "0_25xSR")   return MAX30009_BIOZ_DLPF_0_25xSR_BIOZ;

        return MAX30009_BIOZ_DLPF_BYPASS;
    }

    static std::string digital_lp_filter_to_string(MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE filter_enum)
    {
        switch (filter_enum)
        {
        case MAX30009_BIOZ_DLPF_BYPASS:
            return "BYPASS";
        case MAX30009_BIOZ_DLPF_0_005xSR_BIOZ:
            return "0_005xSR";
        case MAX30009_BIOZ_DLPF_0_02xSR_BIOZ:
            return "0_02xSR";
        case MAX30009_BIOZ_DLPF_0_08xSR_BIOZ:
            return "0_08xSR";
        case MAX30009_BIOZ_DLPF_0_25xSR_BIOZ:
            return "0_25xSR";
        default:
            return "UNKNOWN_DLPF";
        }
    }

    static int32_t get_RMS_current_nA(MAX30009_CURRENT_AMP_ENUM_TYPE current_enum)
    {

        if (current_enum == MAX30009_CURRENT_ERROR) return 1;

        uint8_t row = ((uint8_t)current_enum >> 4) & 0x0F;
        uint8_t col = (uint8_t)current_enum & 0x0F;

        if (row > 3 || col > 3) return 1;
        return drv_current_RMS_arr[row][col];
    }

    static int32_t get_gain_value(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE gain_enum)
    {
        switch (gain_enum)
        {
        case MAX30009_BIOZ_TOTAL_GAIN_1:
            return 1;
        case MAX30009_BIOZ_TOTAL_GAIN_2:
            return 2;
        case MAX30009_BIOZ_TOTAL_GAIN_5:
            return 5;
        case MAX30009_BIOZ_TOTAL_GAIN_10:
            return 10;
        default:
            return 1;
        }
    }
protected:

private:
};

#endif // MAX30009_STATIC_H
