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
    // Initialize lead-off detection settings with safe defaults
    ADS1293_user_sett.enable_leadoff_detection = false;  // Disabled by default for safety
    ADS1293_user_sett.leadoff_mode_dc = true;            // DC mode (conservative)
    ADS1293_user_sett.leadoff_current_nA = 40;           // 40 nA (5 × 8nA, biomedical safe)

    // Enable LOD for active electrodes based on channel configuration:
    // CH1: IN2(+) - IN1(-)  → Monitor IN1, IN2
    // CH2: IN3(+) - IN1(-)  → Monitor IN3
    // CH3: IN5(+) - IN6(-)  → Monitor IN5, IN6
    // RLD: IN4              → DO NOT MONITOR (return path)
    ADS1293_user_sett.leadoff_enable_inputs[0] = true;   // IN1 (common ref)
    ADS1293_user_sett.leadoff_enable_inputs[1] = true;   // IN2 (CH1+)
    ADS1293_user_sett.leadoff_enable_inputs[2] = true;   // IN3 (CH2+)
    ADS1293_user_sett.leadoff_enable_inputs[3] = false;  // IN4 (RLD - CRITICAL: must be false!)
    ADS1293_user_sett.leadoff_enable_inputs[4] = true;   // IN5 (CH3+)
    ADS1293_user_sett.leadoff_enable_inputs[5] = true;   // IN6 (CH3-)

    // AC mode settings (used only if leadoff_mode_dc = false)
    ADS1293_user_sett.leadoff_ac_comparator_level = 1;   // Level 1 (~21mV @ 2kHz)
    ADS1293_user_sett.leadoff_ac_divider_ratio = 2;      // 4.17 kHz (50kHz/(4*1*(2+1)))
    ADS1293_user_sett.leadoff_ac_divider_k16 = false;    // K=1

    // Initialize status tracking arrays
    for (int i = 0; i < 6; i++) {
        _leadoff_status[i] = false;
        _leadoff_status_prev[i] = false;
        _leadoff_debounce_counters[i] = 0;
    }
    _leadoff_check_counter = 0;

    std::cout << "ADS1293: Lead-off detection initialized (disabled by default)" << std::endl;
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

    // NEW: Periodic lead-off detection status check
    // Check every LEADOFF_CHECK_INTERVAL cycles (~500ms with 500µs main loop)
    if (ADS1293_user_sett.enable_leadoff_detection) {
        _leadoff_check_counter++;
        if (_leadoff_check_counter >= LEADOFF_CHECK_INTERVAL) {
            _leadoff_check_counter = 0;
            read_leadoff_status();
        }
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

                // NEW: Lead-off detection settings
                if (parsed_json.contains("enable_leadoff"))
                {
                    ADS1293_user_sett.enable_leadoff_detection = parsed_json["enable_leadoff"];
                }
                if (parsed_json.contains("leadoff_mode"))
                {
                    std::string mode = parsed_json["leadoff_mode"];
                    ADS1293_user_sett.leadoff_mode_dc = (mode == "dc" || mode == "DC");
                }
                if (parsed_json.contains("leadoff_current_nA"))
                {
                    ADS1293_user_sett.leadoff_current_nA = parsed_json["leadoff_current_nA"];
                }
                if (parsed_json.contains("leadoff_inputs") && parsed_json["leadoff_inputs"].is_array())
                {
                    auto inputs_array = parsed_json["leadoff_inputs"];
                    for (int i = 0; i < 6 && i < inputs_array.size(); i++) {
                        ADS1293_user_sett.leadoff_enable_inputs[i] = inputs_array[i];
                    }
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
    response_json["power_enable"] =ADS1293_user_sett.power_enable;
    response_json["R2_rate"] =ADS1293_user_sett.R2_rate;
    response_json["R3_rate"] =ADS1293_user_sett.R3_rate;

    // NEW: Add lead-off detection settings
    response_json["enable_leadoff"] = ADS1293_user_sett.enable_leadoff_detection;
    response_json["leadoff_mode"] = ADS1293_user_sett.leadoff_mode_dc ? "dc" : "ac";
    response_json["leadoff_current_nA"] = ADS1293_user_sett.leadoff_current_nA;

    nlohmann::json inputs_array = nlohmann::json::array();
    for (int i = 0; i < 6; i++) {
        inputs_array.push_back(ADS1293_user_sett.leadoff_enable_inputs[i]);
    }
    response_json["leadoff_inputs"] = inputs_array;

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

    // Configure lead-off detection (Phase 1 implementation)
    configure_leadoff_detection();

    ADS1293_obj.set_DRDYB_pin_source(ADS1293::DRDYB_SRC_CH_1_ECG);

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

void ADS1293_process::configure_leadoff_detection()
{
    std::cout << std::endl << "========================================" << std::endl;
    std::cout << "ADS1293: Configuring Lead-Off Detection" << std::endl;
    std::cout << "========================================" << std::endl;

    if (!ADS1293_user_sett.enable_leadoff_detection) {
        // Shut down lead-off detection
        std::cout << "LOD: Shutting down lead-off detection" << std::endl;
        ADS1293_obj.set_shutdown_leadoff_detection(true);  // SHDN_LOD = 1
        std::cout << "LOD: Configuration complete (disabled)" << std::endl;
        return;
    }

    // Enable lead-off detection
    std::cout << "LOD: Enabling lead-off detection" << std::endl;
    ADS1293_obj.set_shutdown_leadoff_detection(false);  // SHDN_LOD = 0

    // Configure DC or AC mode
    if (ADS1293_user_sett.leadoff_mode_dc) {
        std::cout << "LOD: Mode = DC" << std::endl;
        ADS1293_obj.set_leadoff_detect_mode(ADS1293::SELAC_LOD_DC);

        // Set detection current
        uint32_t current_nA = ADS1293_user_sett.leadoff_current_nA;
        // Validate and clamp to 8nA steps
        current_nA = (current_nA / 8) * 8;  // Round down to nearest 8nA
        if (current_nA < 8) current_nA = 8;
        if (current_nA > 2040) current_nA = 2040;
        ADS1293_user_sett.leadoff_current_nA = current_nA;  // Update with clamped value

        ADS1293_obj.set_leadoff_detection_current(current_nA);
        std::cout << "LOD: Current = " << current_nA << " nA" << std::endl;
    }
    else {
        std::cout << "LOD: Mode = AC" << std::endl;
        ADS1293_obj.set_leadoff_detect_mode(ADS1293::SELAC_LOD_AC);
        ADS1293_obj.set_AC_leadoff_mode(ADS1293::ACAD_LOD_DIGITAL);  // Digital mode

        // Set AC comparator trigger level
        ADS1293::COMPARATOR_TRIGGER_LEVEL_TDE level;
        switch (ADS1293_user_sett.leadoff_ac_comparator_level) {
            case 0: level = ADS1293::CTL_LEVEL_0; std::cout << "LOD: Trigger level = 0" << std::endl; break;
            case 1: level = ADS1293::CTL_LEVEL_1; std::cout << "LOD: Trigger level = 1" << std::endl; break;
            case 2: level = ADS1293::CTL_LEVEL_2; std::cout << "LOD: Trigger level = 2" << std::endl; break;
            case 3: level = ADS1293::CTL_LEVEL_3; std::cout << "LOD: Trigger level = 3" << std::endl; break;
            default:
                level = ADS1293::CTL_LEVEL_1;
                ADS1293_user_sett.leadoff_ac_comparator_level = 1;
                std::cout << "LOD: Trigger level = 1 (default)" << std::endl;
        }
        ADS1293_obj.set_leadoff_AC_comparator_trigger_level(level);

        // Set AC frequency divider
        uint8_t ratio = ADS1293_user_sett.leadoff_ac_divider_ratio & 0x7F;  // 7-bit value
        ADS1293::ACDIV_FACTOR_TDE factor = ADS1293_user_sett.leadoff_ac_divider_k16 ?
                                            ADS1293::ACDIV_FACTOR_K16 : ADS1293::ACDIV_FACTOR_K1;
        ADS1293_obj.set_leadoff_frequency_divider(ratio, factor);

        // Calculate and display frequency
        uint32_t K = ADS1293_user_sett.leadoff_ac_divider_k16 ? 16 : 1;
        uint32_t freq_hz = 50000 / (4 * K * (ratio + 1));
        std::cout << "LOD: AC Frequency = " << freq_hz << " Hz (ratio=" << (int)ratio
                  << ", K=" << K << ")" << std::endl;

        // For AC mode, current register should be 0
        ADS1293_obj.set_leadoff_detection_current(0);
    }

    // Enable/disable individual inputs
    std::cout << "LOD: Enabling inputs: ";
    for (int i = 0; i < 6; i++) {
        bool enable = ADS1293_user_sett.leadoff_enable_inputs[i];

        // Safety check: Never enable IN4 (RLD)
        if (i == 3 && enable) {
            std::cout << std::endl << "WARNING: Attempt to enable LOD on IN4 (RLD)! ";
            std::cout << "This will cause false lead-off detection." << std::endl;
            std::cout << "         Forcing IN4 to disabled." << std::endl;
            enable = false;
            ADS1293_user_sett.leadoff_enable_inputs[3] = false;
        }

        switch (i) {
            case 0: ADS1293_obj.set_leadoff_detection_for_input_1(enable); break;
            case 1: ADS1293_obj.set_leadoff_detection_for_input_2(enable); break;
            case 2: ADS1293_obj.set_leadoff_detection_for_input_3(enable); break;
            case 3: ADS1293_obj.set_leadoff_detection_for_input_4(enable); break;
            case 4: ADS1293_obj.set_leadoff_detection_for_input_5(enable); break;
            case 5: ADS1293_obj.set_leadoff_detection_for_input_6(enable); break;
        }

        if (enable) std::cout << "IN" << (i+1) << " ";
    }
    std::cout << std::endl;

    // Add settling time per datasheet recommendation
    std::cout << "LOD: Waiting 100ms for settling..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // Read initial status
    read_leadoff_status();

    std::cout << "LOD: Configuration complete" << std::endl;
    std::cout << "========================================" << std::endl << std::endl;
}

void ADS1293_process::read_leadoff_status()
{
    // Read hardware status register
    ADS1293::RG_ERROR_LOD_TDS& lod_status = ADS1293_obj.get_leadoff_detect_error_status();

    // Extract individual bit status
    bool raw_status[6] = {
        lod_status.OUT_LOD_IN1,
        lod_status.OUT_LOD_IN2,
        lod_status.OUT_LOD_IN3,
        lod_status.OUT_LOD_IN4,
        lod_status.OUT_LOD_IN5,
        lod_status.OUT_LOD_IN6
    };

    // Debug output (only on first read or state change)
    static bool first_read = true;

    // Process each input with debouncing
    for (int i = 0; i < 6; i++) {
        // Skip disabled inputs
        if (!ADS1293_user_sett.leadoff_enable_inputs[i]) {
            continue;
        }

        // Debounce logic: require LEADOFF_DEBOUNCE_COUNT consecutive reads
        if (raw_status[i] == _leadoff_status[i]) {
            // Status unchanged, reset debounce counter
            _leadoff_debounce_counters[i] = 0;
        } else {
            // Status different, increment debounce counter
            _leadoff_debounce_counters[i]++;

            if (_leadoff_debounce_counters[i] >= LEADOFF_DEBOUNCE_COUNT) {
                // Debounce threshold reached, accept new status
                _leadoff_status[i] = raw_status[i];
                _leadoff_debounce_counters[i] = 0;

                // Log state change
                std::cout << "LOD STATUS CHANGE: IN" << (i+1) << " = "
                          << (raw_status[i] ? "DISCONNECTED" : "CONNECTED") << std::endl;
            }
        }
    }

    // First read debug output
    if (first_read) {
        std::cout << "LOD: Initial status: ";
        for (int i = 0; i < 6; i++) {
            if (ADS1293_user_sett.leadoff_enable_inputs[i]) {
                std::cout << "IN" << (i+1) << "="
                          << (_leadoff_status[i] ? "OFF" : "ON") << " ";
            }
        }
        std::cout << std::endl;
        first_read = false;
    }
}

std::string ADS1293_process::get_leadoff_status_as_json()
{
    nlohmann::json response;
    response["type"] = "leadoff_status";
    response["timestamp"] = get_timestamp_string();
    response["enabled"] = ADS1293_user_sett.enable_leadoff_detection;
    response["mode"] = ADS1293_user_sett.leadoff_mode_dc ? "dc" : "ac";
    response["current_nA"] = ADS1293_user_sett.leadoff_current_nA;

    // Individual input status
    nlohmann::json status_obj;
    for (int i = 0; i < 6; i++) {
        std::string key = "IN" + std::to_string(i + 1);
        if (ADS1293_user_sett.leadoff_enable_inputs[i]) {
            status_obj[key] = _leadoff_status[i] ? "disconnected" : "connected";
        } else {
            status_obj[key] = "not_monitored";
        }
    }
    response["status"] = status_obj;

    // Alarm flag (true if ANY monitored input is disconnected)
    bool alarm = false;
    for (int i = 0; i < 6; i++) {
        if (ADS1293_user_sett.leadoff_enable_inputs[i] && _leadoff_status[i]) {
            alarm = true;
            break;
        }
    }
    response["alarm"] = alarm;

    return response.dump();
}
