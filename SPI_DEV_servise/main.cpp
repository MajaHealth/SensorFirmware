#include <iostream>
#include "MAX30009_LIB/max30009_lib.h"
#include "GPIO_driver.h"
#include "SPI_hard_driver.h"
#include <chrono>
#include <thread>
#include "max30009_ext_mux.h"

#include "MAX30009_process.h"
#include "ADS1293_process.h"
#include "WS2812_process.h"
#include "MAX30009_STATIC.h"
MAX30009_process MAX30009_process_obj;
ADS1293_process ADS1293_process_obj;
WS2812_process WS2812_process_obj;

#include <iostream>
#include <vector>
#include <unistd.h>

#include "JSON_TCP_sever.h"

#include <atomic>




std::string ADS1293_request_json;
std::atomic<bool> ADS1293_request_ready_flag(false);
std::string ADS1293_response_json;
std::atomic<bool> ADS1293_response_ready_flag(false);
const int ADS1293_port=1293;
JSON_TCP_sever ADS1293_TCP_server(ADS1293_port,&ADS1293_request_json,&ADS1293_request_ready_flag,&ADS1293_response_json,&ADS1293_response_ready_flag);

std::string MAX30009_request_json;
std::atomic<bool> MAX30009_request_ready_flag(false);
std::string MAX30009_response_json;
std::atomic<bool> MAX30009_response_ready_flag(false);
const int MAX30009_port=30009;
JSON_TCP_sever MAX30009_TCP_server(MAX30009_port,&MAX30009_request_json,&MAX30009_request_ready_flag,&MAX30009_response_json,&MAX30009_response_ready_flag);

std::string WS2812_request_json;
std::atomic<bool> WS2812_request_ready_flag(false);
std::string WS2812_response_json;
std::atomic<bool> WS2812_response_ready_flag(false);
const int WS2812_port=2812;
JSON_TCP_sever WS2812_TCP_server(WS2812_port,&WS2812_request_json,&WS2812_request_ready_flag,&WS2812_response_json,&WS2812_response_ready_flag);

//#include "debug_window.h"
//DebugWindow max30009_dbg_out(800,800,"MAX30009 & ADS1293");


void delay(int ms)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}



//void update_debug_info(void)
//{
//    std::stringstream ss;
//
//    MAX30009_DEBUG_DATA_ITEM_TDS max30009_debug_info=MAX30009_process_obj.get_debug_data_item();
//    const auto& settings = max30009_debug_info.user_set;
//    const auto& data = max30009_debug_info.data;
//    const auto& Ich= max30009_debug_info.I_ch_data;
//    const auto& Qch= max30009_debug_info.Q_ch_data;
//    const auto& calib= max30009_debug_info.work_calib_data;
//    const auto& status= max30009_debug_info.status;
//    ss << std::fixed << std::setprecision(3);
//
//    // --- (USER_SETTINGS) ---
//    ss << "--- SETTINGS ---\n";
//    ss << "Stim Freq: " << settings.stimulate_frequency_hz << " Hz\n";
//    ss << "Measure Freq: " << settings.measure_frequency_hz << " Hz\n";
//    ss << "Stim Current: " << MAX30009_STATIC::current_to_string(settings.stimulate_current) << "\n";
//    ss << "Total Gain: " << MAX30009_STATIC::gain_to_string(settings.bioz_total_gain) << "\n";
//    ss << "Filters (LP/HP_Out/HP_In): " << MAX30009_STATIC::digital_lp_filter_to_string(settings.out_LP_filter)
//       << "/" << MAX30009_STATIC::digital_hp_filter_to_string(settings.out_HP_filter)
//       << "/" << MAX30009_STATIC::hp_filter_to_string(settings.input_HP_filter) << "\n";
//
//    ss << "--- DATA ---\n";
//    ss << "Load real: " << data.Load_real << " Ohm\n";
//    ss << "Load Mag: " << data.Load_mag << " Ohm\n";
//    ss << "Load Angle: " << data.Load_angle << " deg\n";
//    ss << "Load Imag: " << data.Load_imag << "\n";
//    ss << "Overload: " << (data.overload ? "YES!" : "no") << "\n";
//    ss << "I-channel: ADC" <<Ich.channel_value << "   IMP: " << Ich.impendance_value << "   VLT: " << Ich.voltage_value << "\n";
//    ss << "Q-channel: ADC" <<Qch.channel_value << "   IMP: " << Qch.impendance_value << "   VLT: " << Qch.voltage_value << "\n";
//
//    ss << "--- CALIB---\n";
//    ss << "ref_value: " << (int32_t)calib.ref_value << " Ohm\n";
//    ss << "I_cal_in: " << (int32_t)calib.I_cal_in  << " Ohm\n";
//    ss << "I_cal_in_ADC: " << calib.I_cal_in_ADC << "\n";
//    ss << "I_coef: " << calib.I_coef << "\n";
//    ss << "\n";
//
//    ss << "--- STATUS---\n";
//    ss << "DRV_OVERLOAD: " << status.DRVN_out_of_range << "\n";
//
//    ss << "\n";
//    max30009_dbg_out.update_data_1(ss.str());
//}
//
//void update_debug_info_ADS(void)
//{
//    std::stringstream ss;
//
//    ADS1293_DEBUG_INFO_TDS ADS1293_debug_info=ADS1293_process_obj.get_debug_info();
//    const ADS1293_USER_SETTINGS_TDE& sett = ADS1293_debug_info.sett;
//    const auto& data = ADS1293_debug_info.data;
//    const ADS1293_MODE_DATA_TDS & mode= ADS1293_debug_info.mode_info;
//    ADS1293::RG_ERROR_STATUS_TDS status;
//    *(uint8_t*)&status=ADS1293_debug_info.status;
//
//    ss << std::fixed << std::setprecision(3);
//
//    ss << "--- SETTINGS ---\n";
//    ss << "R2_rate: " << sett.R2_rate << "\n";
//    ss << "R3_rate: " << sett.R3_rate << "\n";
//
//    ss << "\n";
//    ss << "--- DATA ---\n";
//    ss << "Ch1: " << data.ch1 << "(" << (float)data.ch1 * mode.uV_per_ADC_unit << "uV)\n";
//    ss << "Ch2: " << data.ch2 << "(" << (float)data.ch2 * mode.uV_per_ADC_unit << "uV)\n";
//    ss << "Ch3: " << data.ch3 << "(" << (float)data.ch3 * mode.uV_per_ADC_unit << "uV)\n";
//    ss << "\n";
//
//    ss << "\n";
//    ss << "--- MODE ---\n";
//    ss << "ADC max: " << mode.ADC_max << "\n";
//    ss << "ODR: " << mode.ODR << " Hz\n";
//    ss << "Band width: " << mode.band_width << " Hz\n";
//    ss << "uV per ADc unit: " << mode.uV_per_ADC_unit << "uV\n";
//    ss << "\n";
//
//    ss << "\n";
//    ss << "--- STATUS ---\n";
//    ss << "Ch1-3 ERROR: " << status.CH1ERR << status.CH2ERR << status.CH3ERR << "\n";
//    ss << "CMOR: " << status.CMOR << "\n";
//    ss << "RLDRAIL: " << status.RLDRAIL << "\n";
//    ss << "SYNCEDGEERR: " << status.SYNCEDGEERR<< "\n";
//    ss << "LEADOFF: " << status.LEADOFF << "\n";
//    ss << "\n";
//    max30009_dbg_out.update_data_2(ss.str());
//}

int main()
{
    MAX30009_process_obj.init();
    ADS1293_process_obj.init();
    ADS1293_TCP_server.Start();
    MAX30009_TCP_server.Start();
    WS2812_TCP_server.Start();



    auto last_sync_time = std::chrono::steady_clock::now();
    auto last_debug_time = std::chrono::steady_clock::now();
    int32_t sync_num=0;
    while(1)
    {

        if (ADS1293_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=ADS1293_process_obj.process_JSON_line(ADS1293_request_json.c_str());
            ADS1293_request_ready_flag.store(false, std::memory_order_release);
            if (ADS1293_response_ready_flag.load(std::memory_order_release)==false)
            {
                ADS1293_response_json=response_json;
                ADS1293_response_ready_flag.store(true, std::memory_order_release);
            }
        }

        if (MAX30009_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=MAX30009_process_obj.process_JSON_line(MAX30009_request_json.c_str());
            MAX30009_request_ready_flag.store(false, std::memory_order_release);
            if (MAX30009_response_ready_flag.load(std::memory_order_release)==false)
            {
                MAX30009_response_json=response_json;
                MAX30009_response_ready_flag.store(true, std::memory_order_release);
            }
        }

        if (WS2812_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=WS2812_process_obj.process_JSON_line(WS2812_request_json.c_str());
            WS2812_request_ready_flag.store(false, std::memory_order_release);
            if (WS2812_response_ready_flag.load(std::memory_order_release)==false)
            {
                WS2812_response_json=response_json;
                WS2812_response_ready_flag.store(true, std::memory_order_release);
            }
        }

        auto current_time = std::chrono::steady_clock::now();
        auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - last_sync_time);
        if (elapsed_time.count() >= 1000)
        {
            sync_num++;
            MAX30009_process_obj.add_sync_mark(sync_num);
            ADS1293_process_obj.add_sync_mark(sync_num);
            last_sync_time = current_time;
        }

//        auto elapsed_time2 = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - last_debug_time);
//        if (elapsed_time2.count() >= 100)
//        {
//            last_debug_time = current_time;
//            update_debug_info();
//            update_debug_info_ADS();
//
//        }





        MAX30009_process_obj.process();
        ADS1293_process_obj.process();
        WS2812_process_obj.process();


        if (MAX30009_response_ready_flag.load(std::memory_order_release)==false)
        {
            std::string response_json_meas=MAX30009_process_obj.measure_process();
            std::string response_json=MAX30009_process_obj.calibration_process();
            if (response_json_meas.size()>2)
            {

                MAX30009_response_json=response_json_meas;
                MAX30009_response_ready_flag.store(true, std::memory_order_release);

            }
            else if (response_json.size()>2)
            {

                MAX30009_response_json=response_json;
                MAX30009_response_ready_flag.store(true, std::memory_order_release);
            }
        }



//delay(1);
        usleep(500);

    }


    return 0;
}
