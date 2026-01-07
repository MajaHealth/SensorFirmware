#include "ADS1293_process.h"
#include "json.hpp"


#include "GPIO_driver.h"
#include "SPI_hard_driver.h"
#include <chrono>
#include <thread>

using json = nlohmann::json;

SPI_hard_driver_cls SPI_ADS1293_driver("/dev/spidev0.1");
ADS1293::ADS1293_LIB ADS1293_obj(&SPI_ADS1293_driver);
GPIO_driver_cls GPIO_ADS1293_POWER(4);



ADS1293_process::ADS1293_process()
{

}

void ADS1293_process::init(void)
{
    GPIO_ADS1293_POWER.set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
}

void ADS1293_process::process(void)
{

    if (ADS1293_obj.get_data_ready_status().E1_DRDY==true)
    {
        ECG_1=ADS1293_obj.get_ECG_data_CH_1();
        ECG_2=ADS1293_obj.get_ECG_data_CH_2();
        ECG_3=ADS1293_obj.get_ECG_data_CH_3();

        ECG_1=ECG_1-active_mode.base_offset;
        ECG_2=ECG_2-active_mode.base_offset;
        ECG_3=ECG_3-active_mode.base_offset;
        //  std::cout << "ECG1:" << ECG_1;
        //  std::cout << "  ECG2:" << ECG_2;
        //  std::cout << "  ECG3:" << ECG_3 <<std::endl;

        _IFIFO_write_pos=(_IFIFO_write_pos+1)%IFIFO_BUFF_SIZE;
        if (_IFIFO_write_pos==_IFIFO_read_pos)
        {
            _IFIFO_read_pos=(_IFIFO_read_pos+1)%IFIFO_BUFF_SIZE ;
        }

        _IFIFO_BUF[_IFIFO_write_pos].ch1=ECG_1;
        _IFIFO_BUF[_IFIFO_write_pos].ch2=ECG_2;
        _IFIFO_BUF[_IFIFO_write_pos].ch3=ECG_3;

    }
    else
    {
        //  std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" <<std::endl;
    }
}

void ADS1293_process::add_sync_mark(int32_t sync_num)
{
    _IFIFO_write_pos=(_IFIFO_write_pos+1)%IFIFO_BUFF_SIZE;
    if (_IFIFO_write_pos==_IFIFO_read_pos)
    {
        _IFIFO_read_pos=(_IFIFO_read_pos+1)%IFIFO_BUFF_SIZE ;
    }

    _IFIFO_BUF[_IFIFO_write_pos].ch1=SYNC_MARK_MAGIC_NUM;
    _IFIFO_BUF[_IFIFO_write_pos].ch2=sync_num;
    _IFIFO_BUF[_IFIFO_write_pos].ch3=0;

    check_analog_error();
}

void ADS1293_process::check_analog_error(void)
{
    ADS1293::RG_ERROR_STATUS_TDS& status = ADS1293_obj.get_analog_other_error_status();
    if (status.CH1ERR || status.CH2ERR || status.CH3ERR || status.RLDRAIL || status.CMOR)
    {
        _IFIFO_write_pos=(_IFIFO_write_pos+1)%IFIFO_BUFF_SIZE;
        if (_IFIFO_write_pos==_IFIFO_read_pos)
        {
            _IFIFO_read_pos=(_IFIFO_read_pos+1)%IFIFO_BUFF_SIZE ;
        }

        _IFIFO_BUF[_IFIFO_write_pos].ch1=ERROR_MARK_MAGIC_NUM;
        _IFIFO_BUF[_IFIFO_write_pos].ch2=*(uint8_t*)&status;
        _IFIFO_BUF[_IFIFO_write_pos].ch3=0;
    }


}

std::string ADS1293_process::process_JSON_line(const char * JSON_line)
{
    std::cout << "IN:" << JSON_line << std::endl << std::endl;


    json parsed_json;
    json response;

    try
    {
        parsed_json = json::parse(JSON_line);

        if (parsed_json.contains("type"))
        {

            std::string command_type = parsed_json["type"];

            if (command_type == "settings")
            {
                if (parsed_json.contains("enable_conversion"))
                {
                    ADS1293_user_sett.enable_conversion= parsed_json["enable_conversion"];
                }
                if (parsed_json.contains("R1_rate"))
                {
                    ADS1293_user_sett.R1_rate=parsed_json["R1_rate"];
                }

                if (parsed_json.contains("R2_rate"))
                {
                    ADS1293_user_sett.R2_rate=parsed_json["R2_rate"];
                }

                if (parsed_json.contains("R3_rate"))
                {
                    ADS1293_user_sett.R3_rate=parsed_json["R3_rate"];
                }

                process_all_settings_for_ADS1293();
                return get_all_settings_as_json();
            }

            if (command_type == "get_data")
            {

                return get_data_as_json();
            }

            if (command_type == "poweroff")
            {
                set_power_state(false);
                return "{\"type\":\"power_is_off\"}";
            }
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

std::string ADS1293_process::get_all_settings_as_json(void)
{
    nlohmann::json response_json;
    response_json["type"] = "actual_settings";
    response_json["enable_conversion"] = ADS1293_user_sett.enable_conversion;
    response_json["R1_rate"] =ADS1293_user_sett.R1_rate;
    response_json["R2_rate"] =ADS1293_user_sett.R2_rate;
    response_json["R3_rate"] =ADS1293_user_sett.R3_rate;
    return response_json.dump();
}

ADS1293_DEBUG_INFO_TDS ADS1293_process::get_debug_info(void)
{
    ADS1293_DEBUG_INFO_TDS out;
    out.sett=ADS1293_user_sett;
    out.data.ch1=ECG_1;
    out.data.ch2=ECG_2;
    out.data.ch3=ECG_3;
    out.mode_info=active_mode;
    ADS1293::RG_ERROR_STATUS_TDS& status = ADS1293_obj.get_analog_other_error_status();
    out.status = *(uint8_t*)&status;
    return out;
}

void ADS1293_process::process_all_settings_for_ADS1293(void)
{

    set_power_state(true);

    ADS1293_obj.set_conversion_state(false);

    ADS1293_obj.set_standby_mode(false);

    ADS1293_obj.set_positive_terminal_for_ch_1(ADS1293::IS_INPUT_2);
    ADS1293_obj.set_negative_terminal_for_ch_1(ADS1293::IS_INPUT_1);
    ADS1293_obj.set_positive_terminal_for_ch_2(ADS1293::IS_INPUT_3);
    ADS1293_obj.set_negative_terminal_for_ch_2(ADS1293::IS_INPUT_1);
    ADS1293_obj.set_positive_terminal_for_ch_3(ADS1293::IS_INPUT_5);
    ADS1293_obj.set_negative_terminal_for_ch_3(ADS1293::IS_INPUT_6);

    ADS1293_obj.set_common_mode_detection_for_input_1(true);
    ADS1293_obj.set_common_mode_detection_for_input_2(true);
    ADS1293_obj.set_common_mode_detection_for_input_3(true);

    ADS1293_obj.set_right_leg_drive_output(ADS1293::IS_INPUT_4);
    ADS1293_obj.set_right_leg_drive_bandwidth_mode(ADS1293::RLD_BW_HIGH_BANDWIDTH);
    ADS1293_obj.set_right_leg_detect_cap_load_drive_capability(ADS1293::RLD_CAPDRIVE_HIGH);

    ADS1293_obj.set_wilson_reference_input_1(ADS1293::IS_INPUT_1);
    ADS1293_obj.set_wilson_reference_input_2(ADS1293::IS_INPUT_2);
    ADS1293_obj.set_wilson_reference_input_3(ADS1293::IS_INPUT_3);
    ADS1293_obj.set_wilson_reference_control(ADS1293::RG_WLS_REFCNTRL_WILSONINT);

    ADS1293_obj.set_clock_source(ADS1293::SHDN_OSC_INTERNAL);
    ADS1293_obj.set_start_clock_to_digital(true);

    ADS1293_obj.set_clock_frequency_for_ch_1(ADS1293::FS_HIGH_CH_204800HZ);
    ADS1293_obj.set_clock_frequency_for_ch_2(ADS1293::FS_HIGH_CH_204800HZ);
    ADS1293_obj.set_clock_frequency_for_ch_3(ADS1293::FS_HIGH_CH_204800HZ);

    //ADS1293_obj.set_test_signal_for_ch_1(ADS1293::TSS_TO_POSITIVE_TEST_SIGNAL);
    //ADS1293_obj.set_test_signal_for_ch_2(ADS1293::TSS_TO_NEGATIVE_TEST_SIGNAL);
    //ADS1293_obj.set_test_signal_for_ch_3(ADS1293::TSS_TO_ZERO_TEST_SIGNAL);



    ADS1293::R1_RATE_TDE R1_rate_sel= ADS1293::R1_RATE_STANDART_R1_4;
    if (ADS1293_user_sett.R1_rate==4)
    {

        R1_rate_sel= ADS1293::R1_RATE_STANDART_R1_4;
    }
    else if (ADS1293_user_sett.R1_rate==2)
    {
        R1_rate_sel= ADS1293::R1_RATE_DOUBLE_R1_2;
    }
    else
    {
        R1_rate_sel= ADS1293::R1_RATE_STANDART_R1_4;
        ADS1293_user_sett.R1_rate=4;
    }

    ADS1293::R2_RATE_TDE R2_rate_sel;
    switch (ADS1293_user_sett.R2_rate)
    {
    case 4:
        R2_rate_sel = ADS1293::R2_RATE_4;
        break;
    case 5:
        R2_rate_sel = ADS1293::R2_RATE_5;
        break;
    case 6:
        R2_rate_sel = ADS1293::R2_RATE_6;
        break;
    default:
        R2_rate_sel = ADS1293::R2_RATE_8;
        ADS1293_user_sett.R2_rate = 8;
        break;
    }

    ADS1293::R3_RATE_TDE R3_rate_sel;
    switch (ADS1293_user_sett.R3_rate)
    {
    case 4:
        R3_rate_sel = ADS1293::R3_RATE_4;
        break;
    case 6:
        R3_rate_sel = ADS1293::R3_RATE_6;
        break;
    case 8:
        R3_rate_sel = ADS1293::R3_RATE_8;
        break;
    case 12:
        R3_rate_sel = ADS1293::R3_RATE_12;
        break;
    case 16:
        R3_rate_sel = ADS1293::R3_RATE_16;
        break;
    case 32:
        R3_rate_sel = ADS1293::R3_RATE_32;
        break;
    case 64:
        R3_rate_sel = ADS1293::R3_RATE_64;
        break;
    default:
        R3_rate_sel = ADS1293::R3_RATE_128;
        ADS1293_user_sett.R3_rate = 128;
        break;
    }

    const ADS1293::CHANNEL_PARAM_DATA_TDS& channel_params=ADS1293_obj.get_channel_params(ADS1293::FS_HIGH_CH_204800HZ,R1_rate_sel,R2_rate_sel,R3_rate_sel);
    active_mode.ODR =channel_params.ODR;
    active_mode.ADC_max=channel_params.ADC_max;
    active_mode.band_width =channel_params.band_width;
    active_mode.base_offset=channel_params.ADC_max/2;
    active_mode.uV_per_ADC_unit=1371428.57f/(float)active_mode.ADC_max;

    ADS1293_obj.set_R1_decimation_rate_for_CH_1(R1_rate_sel);
    ADS1293_obj.set_R1_decimation_rate_for_CH_2(R1_rate_sel);
    ADS1293_obj.set_R1_decimation_rate_for_CH_3(R1_rate_sel);

    ADS1293_obj.set_R2_decimation_rate(R2_rate_sel);

    ADS1293_obj.set_R3_decimation_rate_for_CH_1(R3_rate_sel);
    ADS1293_obj.set_R3_decimation_rate_for_CH_2(R3_rate_sel);
    ADS1293_obj.set_R3_decimation_rate_for_CH_3(R3_rate_sel);

    ADS1293_obj.set_DRDYB_pin_source(ADS1293::DRDYB_SRC_CH_1_ECG);

    ADS1293_obj.set_enable_INA_high_resolition_CH_1(true);
    ADS1293_obj.set_enable_INA_high_resolition_CH_2(true);
    ADS1293_obj.set_enable_INA_high_resolition_CH_3(true);

    ADS1293_obj.set_CH1_ECG_read_back_mode(true);
    ADS1293_obj.set_CH2_ECG_read_back_mode(true);
    ADS1293_obj.set_CH3_ECG_read_back_mode(true);

    ADS1293_obj.set_conversion_state(true);
    ADS1293_obj.set_conversion_state(true);

    //ADS1293_obj.load_all_registers();

}
std::string ADS1293_process::get_data_as_json(void)
{
    nlohmann::json response_json;
    response_json["type"] = "data";
    int32_t buffer_size = (_IFIFO_write_pos- _IFIFO_read_pos + IFIFO_BUFF_SIZE) % IFIFO_BUFF_SIZE;
    response_json["data_size"] =buffer_size;
    response_json["timestamp"] =get_timestamp_string();
    response_json["data_rate"] =active_mode.ODR;
    response_json["band_width"] =active_mode.band_width;
    response_json["uV_per_ADC_unit"] =active_mode.uV_per_ADC_unit;
    nlohmann::json data_array = nlohmann::json::array();

    for (uint32_t i = 0; i < buffer_size; ++i)
    {
        _IFIFO_read_pos=(_IFIFO_read_pos+1)%IFIFO_BUFF_SIZE;
        nlohmann::json point_array = nlohmann::json::array();
        point_array.push_back(_IFIFO_BUF[_IFIFO_read_pos].ch1);
        point_array.push_back(_IFIFO_BUF[_IFIFO_read_pos].ch2);
        point_array.push_back(_IFIFO_BUF[_IFIFO_read_pos].ch3);
        data_array.push_back(point_array);
    }

    response_json["data"] = data_array;
    return response_json.dump();
}


void ADS1293_process::set_power_state(bool state)
{
    if (_old_power_state==state) return;
    _old_power_state=state;
    if (state==true)
    {
        GPIO_ADS1293_POWER.set_GPIO_state(VT_GPIO_SET);
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    else
    {
        GPIO_ADS1293_POWER.set_GPIO_state(VT_GPIO_UNSET);
    }
}


std::string ADS1293_process::get_timestamp_string()
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
