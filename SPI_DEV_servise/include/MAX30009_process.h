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

typedef struct MAX30009_USER_SETTINGS
{
    uint32_t stimulate_frequency;
    uint32_t measure_frequency;

    uint32_t out_LP_filter_select;
    uint32_t out_HP_filter_select;
    uint32_t input_HP_filter_select;

    uint32_t bioz_total_gain;
    uint32_t stimulate_current_select;

    bool measure_enable;
    bool lead_bias_enable;
    bool power_enable;

    uint32_t ext_MUX_state;


} MAX30009_USER_SETTINGS_TDE;


typedef struct MAX30009_IFIFO_DATA
{
    int32_t I_data;
    int32_t Q_data;
} MAX30009_IFIFO_DATA_TDS;

class MAX30009_process
{
public:
    MAX30009_process();

    void init();
    void process(void);
    void add_sync_mark(int32_t sync_num);

    std::string process_JSON_line(const char * JSON_line);
    std::string get_all_settings_as_json(void);
    void process_all_settings_for_MAX30009(void);
    void process_ext_MUX_settings_for_MAX30009(void);
    bool check_enumerate_for_value(uint8_t value,const uint8_t *value_list, uint8_t value_list_size);
    std::vector<MAX30009_FIFO_DATA_CALIB_TYPE> get_decimate_IFIFO_data();
    std::string get_data_as_json(void);

    std::string calibration_process(void);
    std::string get_calibration_json_data(MAX30009_CALIB_DATA calib_koef);
    bool save_string_to_file(const std::string& filename, const std::string& data);

    void set_power_state(bool state);

    MAX30009_CALIB_DATA  get_calib_koef_from_file(const std::string& filename);

    std::string get_timestamp_string();
protected:

private:
    MAX30009_USER_SETTINGS_TDE MAX30009_user_sett= {0};
    static const uint32_t MIN_MEASURE_FREQ	=1;
    static const uint32_t MAX_MEASURE_FREQ=500;
    static const uint32_t CALIB_STEP_PERIOD=60;
    static const uint32_t CALIB_RESISTOR_VALUE=100.0;

    static const int32_t SYNC_MARK_MAGIC_NUM=-99999;

    uint32_t _calibrate_timer=0;

    static const uint32_t FREQ_POINTS_COUNT=17;
    static constexpr  uint32_t FREQ_POINTS[FREQ_POINTS_COUNT]= {25, 100, 200, 500, 1000, 5000, 10000, 20000, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000};

    static const uint32_t CURRENT_POINTS_COUNT=5;
    static constexpr  MAX30009_CURRENT_AMP_ENUM_TYPE CURRENT_POINTS[CURRENT_POINTS_COUNT]=
    {
        MAX30009_CURRENT_AMP_64uA,
        MAX30009_CURRENT_AMP_128uA,
        MAX30009_CURRENT_AMP_256uA,
        MAX30009_CURRENT_AMP_640uA,
        MAX30009_CURRENT_AMP_1_28mA
    };

    MAX30009_CALIB_DATA _calibrate_data[CURRENT_POINTS_COUNT][FREQ_POINTS_COUNT];


    static const uint32_t IFIFO_BUFFER_DURATION=3;
    static const uint32_t IFIFO_BUFF_SIZE=30000;
    uint32_t _max_IFIFO_size = 1;
    MAX30009_IFIFO_DATA_TDS _IFIFO_BUF[IFIFO_BUFF_SIZE]= {0};
    uint32_t _IFIFO_write_pos=0;
    uint32_t _IFIFO_read_pos=0;

    bool _need_calibrate=false;
    uint32_t _calibrate_current_index=0;
    uint32_t _calibrate_freq_index=0;

    bool _old_power_state=false;




};

#endif // MAX30009_PROCESS_H
