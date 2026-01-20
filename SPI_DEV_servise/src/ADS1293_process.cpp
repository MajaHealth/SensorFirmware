#include "ADS1293_process.h"
#include "json.hpp"

#include "ADS1293_LIB.h"
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
    uint32_t ECG_1=0;
    uint32_t ECG_2=0;
    uint32_t ECG_3=0;
    if (ADS1293_obj.get_data_ready_status().E1_DRDY==true)
    {
        ECG_1=ADS1293_obj.get_ECG_data_CH_1();
        ECG_2=ADS1293_obj.get_ECG_data_CH_2();
        ECG_3=ADS1293_obj.get_ECG_data_CH_3();

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
                if (parsed_json.contains("power_enable"))
                {
                    ADS1293_user_sett.power_enable=parsed_json["power_enable"];
                }

                if (parsed_json.contains("R2_rate"))
                {
                    ADS1293_user_sett.R2_rate=parsed_json["R2_rate"];
                }

                if (parsed_json.contains("R3_rate"))
                {
                    ADS1293_user_sett.R3_rate=parsed_json["R3_rate"];
                }

                // Lead-off detection settings
                if (parsed_json.contains("leadoff_enable"))
                {
                    ADS1293_user_sett.leadoff_enable = parsed_json["leadoff_enable"];
                }
                if (parsed_json.contains("leadoff_mode"))
                {
                    ADS1293_user_sett.leadoff_mode = parsed_json["leadoff_mode"];
                }
                if (parsed_json.contains("leadoff_current_nA"))
                {
                    ADS1293_user_sett.leadoff_current_nA = parsed_json["leadoff_current_nA"];
                }
                if (parsed_json.contains("leadoff_threshold"))
                {
                    ADS1293_user_sett.leadoff_threshold = parsed_json["leadoff_threshold"];
                }

                process_all_settings_for_ADS1293();
                return get_all_settings_as_json();
            }

            if (command_type == "get_data")
            {
                return get_data_as_json();
            }

            if (command_type == "get_leadoff_status")
            {
                return get_leadoff_status_as_json();
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
    response_json["power_enable"] = ADS1293_user_sett.power_enable;
    response_json["R2_rate"] = ADS1293_user_sett.R2_rate;
    response_json["R3_rate"] = ADS1293_user_sett.R3_rate;

    // Lead-off detection settings
    response_json["leadoff_enable"] = ADS1293_user_sett.leadoff_enable;
    response_json["leadoff_mode"] = ADS1293_user_sett.leadoff_mode;
    response_json["leadoff_current_nA"] = ADS1293_user_sett.leadoff_current_nA;
    response_json["leadoff_threshold"] = ADS1293_user_sett.leadoff_threshold;

    return response_json.dump();
}

void ADS1293_process::process_all_settings_for_ADS1293(void)
{

    set_power_state(ADS1293_user_sett.power_enable);

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


    ADS1293::R2_RATE_TDE R2_rate_sel= ADS1293::R2_RATE_8;
    if (ADS1293_user_sett.R2_rate==4) R2_rate_sel= ADS1293::R2_RATE_4;
    else if (ADS1293_user_sett.R2_rate==5) R2_rate_sel= ADS1293::R2_RATE_5;
    else if (ADS1293_user_sett.R2_rate==6) R2_rate_sel= ADS1293::R2_RATE_6;
    else if (ADS1293_user_sett.R2_rate==8) R2_rate_sel= ADS1293::R2_RATE_8;
    else
    {
        R2_rate_sel= ADS1293::R2_RATE_8;
        ADS1293_user_sett.R2_rate=8;
    }


    ADS1293::R3_RATE_TDE R3_rate_sel = ADS1293::R3_RATE_128;

    if (ADS1293_user_sett.R3_rate == 4) R3_rate_sel = ADS1293::R3_RATE_4;
    else if (ADS1293_user_sett.R3_rate == 6) R3_rate_sel = ADS1293::R3_RATE_6;
    else if (ADS1293_user_sett.R3_rate == 8) R3_rate_sel = ADS1293::R3_RATE_8;
    else if (ADS1293_user_sett.R3_rate == 12) R3_rate_sel = ADS1293::R3_RATE_12;
    else if (ADS1293_user_sett.R3_rate == 16) R3_rate_sel = ADS1293::R3_RATE_16;
    else if (ADS1293_user_sett.R3_rate == 32) R3_rate_sel = ADS1293::R3_RATE_32;
    else if (ADS1293_user_sett.R3_rate == 64) R3_rate_sel = ADS1293::R3_RATE_64;
    else if (ADS1293_user_sett.R3_rate == 128) R3_rate_sel = ADS1293::R3_RATE_128;
    else
    {

        R3_rate_sel = ADS1293::R3_RATE_128;
        ADS1293_user_sett.R3_rate = 128;
    }


    ADS1293_obj.set_R2_decimation_rate(R2_rate_sel);

    ADS1293_obj.set_R3_decimation_rate_for_CH_1(R3_rate_sel);
    ADS1293_obj.set_R3_decimation_rate_for_CH_2(R3_rate_sel);
    ADS1293_obj.set_R3_decimation_rate_for_CH_3(R3_rate_sel);

    ADS1293_obj.set_DRDYB_pin_source(ADS1293::DRDYB_SRC_CH_1_ECG);

    ADS1293_obj.set_CH1_ECG_read_back_mode(true);
    ADS1293_obj.set_CH2_ECG_read_back_mode(true);
    ADS1293_obj.set_CH3_ECG_read_back_mode(true);

    ADS1293_obj.set_conversion_state(true);
    ADS1293_obj.set_conversion_state(true);

    // Configure lead-off detection
    configure_leadoff_detection();

    //ADS1293_obj.load_all_registers();

}
std::string ADS1293_process::get_data_as_json(void)
{
    // Read current lead-off status
    if (ADS1293_user_sett.leadoff_enable)
    {
        read_leadoff_status();
    }

    nlohmann::json response_json;
    response_json["type"] = "data";
    int32_t buffer_size = (_IFIFO_write_pos- _IFIFO_read_pos + IFIFO_BUFF_SIZE) % IFIFO_BUFF_SIZE;
    response_json["data_size"] = buffer_size;
    response_json["timestamp"] = get_timestamp_string();

    // Include lead-off status in every data packet
    response_json["lead_off_detected"] = _leadoff_status.lead_off_detected;
    response_json["leadoff_in1"] = _leadoff_status.in1_off;
    response_json["leadoff_in2"] = _leadoff_status.in2_off;
    response_json["leadoff_in3"] = _leadoff_status.in3_off;
    response_json["leadoff_in5"] = _leadoff_status.in5_off;
    response_json["leadoff_in6"] = _leadoff_status.in6_off;

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

void ADS1293_process::configure_leadoff_detection(void)
{
    if (ADS1293_user_sett.leadoff_enable == false)
    {
        // Shut down lead-off detection to save power
        ADS1293_obj.set_shutdown_leadoff_detection(true);
        return;
    }

    // Enable lead-off detection circuit
    ADS1293_obj.set_shutdown_leadoff_detection(false);

    // Set detection mode (DC=0, AC=1)
    if (ADS1293_user_sett.leadoff_mode == 1)
    {
        ADS1293_obj.set_leadoff_detect_mode(ADS1293::SELAC_LOD_AC);
        ADS1293_obj.set_AC_leadoff_mode(ADS1293::ACAD_LOD_ANALOG);
        // Set AC frequency ~625 Hz (divider=19, K=1)
        ADS1293_obj.set_leadoff_frequency_divider(19, ADS1293::ACDIV_FACTOR_K1);
    }
    else
    {
        ADS1293_obj.set_leadoff_detect_mode(ADS1293::SELAC_LOD_DC);
    }

    // Set comparator threshold level
    ADS1293::COMPARATOR_TRIGGER_LEVEL_TDE level = ADS1293::CTL_LEVEL_1;
    if (ADS1293_user_sett.leadoff_threshold == 0) level = ADS1293::CTL_LEVEL_0;
    else if (ADS1293_user_sett.leadoff_threshold == 1) level = ADS1293::CTL_LEVEL_1;
    else if (ADS1293_user_sett.leadoff_threshold == 2) level = ADS1293::CTL_LEVEL_2;
    else if (ADS1293_user_sett.leadoff_threshold == 3) level = ADS1293::CTL_LEVEL_3;
    ADS1293_obj.set_leadoff_AC_comparator_trigger_level(level);

    // Set detection current (default 1400 nA = 1.4 µA)
    uint32_t current = ADS1293_user_sett.leadoff_current_nA;
    if (current == 0) current = 1400;  // Default
    if (current > 2040) current = 2040;
    ADS1293_obj.set_leadoff_detection_current(current);

    // Enable lead-off detection ONLY for used inputs (NOT IN4/RLD)
    // CH1: IN2(+) / IN1(-) → enable IN1, IN2
    // CH2: IN3(+) / IN1(-) → enable IN3 (IN1 already enabled)
    // CH3: IN5(+) / IN6(-) → enable IN5, IN6
    // RLD output: IN4 - DO NOT enable (needs low impedance path)
    ADS1293_obj.set_leadoff_detection_for_input_1(true);   // Used by CH1, CH2
    ADS1293_obj.set_leadoff_detection_for_input_2(true);   // Used by CH1
    ADS1293_obj.set_leadoff_detection_for_input_3(true);   // Used by CH2
    ADS1293_obj.set_leadoff_detection_for_input_4(false);  // RLD - don't monitor
    ADS1293_obj.set_leadoff_detection_for_input_5(true);   // Used by CH3
    ADS1293_obj.set_leadoff_detection_for_input_6(true);   // Used by CH3
}

void ADS1293_process::read_leadoff_status(void)
{
    // Read lead-off error register (0x18)
    ADS1293::RG_ERROR_LOD_TDS lod_status = ADS1293_obj.get_leadoff_detect_error_status();

    _leadoff_status.in1_off = lod_status.OUT_LOD_IN1;
    _leadoff_status.in2_off = lod_status.OUT_LOD_IN2;
    _leadoff_status.in3_off = lod_status.OUT_LOD_IN3;
    _leadoff_status.in4_off = lod_status.OUT_LOD_IN4;
    _leadoff_status.in5_off = lod_status.OUT_LOD_IN5;
    _leadoff_status.in6_off = lod_status.OUT_LOD_IN6;

    // Read general error status for overall LEADOFF flag (0x19)
    ADS1293::RG_ERROR_STATUS_TDS err_status = ADS1293_obj.get_analog_other_error_status();
    _leadoff_status.lead_off_detected = err_status.LEADOFF;
}

std::string ADS1293_process::get_leadoff_status_as_json(void)
{
    read_leadoff_status();

    nlohmann::json response_json;
    response_json["type"] = "leadoff_status";
    response_json["lead_off_detected"] = _leadoff_status.lead_off_detected;

    // Raw input status
    response_json["in1_off"] = _leadoff_status.in1_off;
    response_json["in2_off"] = _leadoff_status.in2_off;
    response_json["in3_off"] = _leadoff_status.in3_off;
    response_json["in4_off"] = _leadoff_status.in4_off;
    response_json["in5_off"] = _leadoff_status.in5_off;
    response_json["in6_off"] = _leadoff_status.in6_off;

    // Map to standard ECG lead names for convenience
    response_json["ra_off"] = _leadoff_status.in1_off;  // IN1 = RA
    response_json["la_off"] = _leadoff_status.in2_off;  // IN2 = LA
    response_json["ll_off"] = _leadoff_status.in3_off;  // IN3 = LL
    response_json["rl_off"] = _leadoff_status.in4_off;  // IN4 = RL (RLD)

    response_json["timestamp"] = get_timestamp_string();

    return response_json.dump();
}

std::string ADS1293_process::check_and_get_periodic_leadoff_status(void)
{
    // Only push if lead-off detection is enabled
    if (!ADS1293_user_sett.leadoff_enable)
    {
        _leadoff_push_counter = 0;
        return "";
    }

    _leadoff_push_counter++;

    // Check if 5 seconds have elapsed (~10000 iterations at 500μs loop)
    if (_leadoff_push_counter < LEADOFF_PUSH_INTERVAL)
    {
        return "";
    }

    // Reset counter and return status JSON
    _leadoff_push_counter = 0;
    return get_leadoff_status_as_json();
}
