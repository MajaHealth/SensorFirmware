#ifndef MAX30009_PROCESS_H
#define MAX30009_PROCESS_H

#include "max30009_ext_mux.h"
#include <string>
#include <iostream>
#include "max30009_lib.h"
#include <vector>

#include "json.hpp"


#include "GPIO_driver.h"
#include "SPI_hard_driver.h"
#include <chrono>
#include <thread>
#include "max30009_ext_mux.h"
#include <fstream>
#include <filesystem>

#include "MAX30009_user_set.h"
#include "MAX30009_data_storage.h"
#include "MAX30009_base_cal_table.h"
#include "MAX30009_STATIC.h"
#include "VTFLTmovingaverage.h"

typedef struct AUTOTEST_DATA
{
    std::vector<uint32_t> freqs_list;
    std::vector<std::string> currs_list;
    bool need_do;
    uint32_t freq_index;
    uint32_t curr_index;
    uint32_t wait_stabile_data;
    std::ofstream csv_file;
} AUTOTEST_DATA_TDS;
typedef struct MAX30009_START_MEASURE_DATA
{
    uint32_t stimulate_frequency_hz;
    uint32_t measure_frequency_hz;

    MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE out_LP_filter;
    MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE out_HP_filter;
    MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE input_HP_filter;

    MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE bioz_total_gain;
    MAX30009_CURRENT_AMP_ENUM_TYPE  stimulate_current;
    bool passive_lead_monitor_enable=false;

} MAX30009_START_MEASURE_DATA_TDS;

typedef struct MAX30009_DEBUG_DATA_ITEM
{
    MAX30009_USER_SETTINGS_TDE user_set;
    MAX30009_FIFO_DATA_CALIB_TYPE data;

    MAX30009_FIFO_DATA I_ch_data;
    MAX30009_FIFO_DATA Q_ch_data;

    MAX30009_CALIB_DATA_TYPE work_calib_data;

   MAX30009_STATUS_STRUCT_TYPE status;

} MAX30009_DEBUG_DATA_ITEM_TDS;

typedef enum MEASURE_MODE
{
    MMD_STOP,
    MMD_BASE_MEASURE_START,
    MMD_BASE_MEASURING,
    MMD_CALIBRATE_START,
    MMD_CALIBRATING,
    MMD_MEASURE_START,
    MMD_MEASURING,
} MEASURE_MODE_TDE;

class MAX30009_process
{
public:
    MAX30009_process();

    void init();
    void process(void);
    void check_FIFO_buffer(void);
    void add_sync_mark(int32_t sync_num);

    MAX30009_DEBUG_DATA_ITEM_TDS get_debug_data_item();
    MAX30009_FIFO_DATA_CALIB_TYPE get_average_debug_data(uint32_t avrg_cnt);

    std::string process_JSON_line(const char * JSON_line);

    MAX30009_START_MEASURE_DATA_TDS & start_measure_MAX30009(MAX30009_START_MEASURE_DATA_TDS & start_data);
    void  stop_measure_MAX30009(void);

    std::string calibration_process(void);
    std::string measure_process(void);
    std::string get_calibration_json_data(MAX30009_CALIB_DATA calib_koef);

    void set_power_state(bool state);
    std::string get_lead_status_as_json(void);

protected:

private:
    void start_build_calibrate_table(void);
    MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE  get_auto_gain(int32_t pre_measure_imp,MAX30009_CURRENT_AMP_ENUM_TYPE current);
    void autotest_process(void);
    void start_autotest(void);
    void reset_passive_lead_monitor(void);
    void update_passive_lead_monitor(const MAX30009_STATUS_STRUCT_TYPE &new_status);
    bool update_debounced_flag(bool raw_value, uint8_t &counter, bool &debounced_value);

    static constexpr uint8_t LEAD_MONITOR_DEBOUNCE_COUNT=3;
    static constexpr uint8_t LEAD_MONITOR_LOFF_IMAG=0x04;
    static constexpr uint8_t LEAD_MONITOR_LOFF_THRESH=0x03;
    static constexpr uint8_t LEAD_MONITOR_BIOZ_CMP=0x02;
    static constexpr uint8_t LEAD_MONITOR_BIOZ_LO_THRESH=0x08;
    static constexpr uint8_t LEAD_MONITOR_BIOZ_HI_THRESH=0xF8;

    bool _need_buid_calibrate_table=false;
    bool _need_work_calibrate=false;
    uint32_t _work_calibrate_resistor_value=0;
    uint32_t pre_meas_impendace_value=0;
    MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE _work_gain=MAX30009_BIOZ_TOTAL_GAIN_1;
    MAX30009_CALIB_DATA_TYPE _work_calib_data{};
    bool _in_calibrate=false;
    bool _old_power_state=false;

    static const uint32_t BASE_DATA_COUNT=100;
    static const uint32_t BASE_TABLE_RESISTOR_VALUE=370;
    static const MAX30009_CURRENT_AMP_ENUM_TYPE BASE_TABLE_CURRENT=MAX30009_CURRENT_AMP_64uA;
    static const MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE BASE_TABLE_GAIN=MAX30009_BIOZ_TOTAL_GAIN_10;

    uint32_t _build_base_table_index=0;

    MEASURE_MODE_TDE _meas_mode=MMD_STOP;

    VTFLT_moving_average<500> I_ch_flt;
    VTFLT_moving_average<500> Q_ch_flt;
    MAX30009_STATUS_STRUCT_TYPE status;
    MAX30009_PASSIVE_LEAD_MONITOR_STATUS_TYPE _lead_status{};
    bool _lead_monitor_active=false;
    uint8_t _lead_bip_high_counter=0;
    uint8_t _lead_bip_low_counter=0;
    uint8_t _lead_bin_high_counter=0;
    uint8_t _lead_bin_low_counter=0;
    uint8_t _lead_drv_oor_counter=0;
    uint8_t _lead_bioz_over_counter=0;
    uint8_t _lead_bioz_under_counter=0;

AUTOTEST_DATA_TDS autotest{};
};

#endif // MAX30009_PROCESS_H
