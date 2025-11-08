#include "MAX30009_process.h"
#include <iomanip>
#include <ctime>

using json = nlohmann::json;



GPIO_driver_cls GPIO_MUX_SP{27};
GPIO_driver_cls GPIO_MUX_MP{13};
GPIO_driver_cls GPIO_MUX_MN{26};
GPIO_driver_cls GPIO_MUX_SN{19};
GPIO_driver_cls GPIO_MUX_2W{5};
GPIO_driver_cls GPIO_MUX_CAL{6};
GPIO_driver_cls GPIO_MUX_CC{17};
GPIO_driver_cls GPIO_MAX30009_POWER{21};

MAX30009_EXT_MUX_GPIOs_TDE MUX_GPIOs= {&GPIO_MUX_SP,&GPIO_MUX_MP,&GPIO_MUX_MN,&GPIO_MUX_SN,&GPIO_MUX_2W,&GPIO_MUX_CAL,&GPIO_MUX_CC};
max30009_ext_MUX max30009_ext_MUX_obj(MUX_GPIOs);
SPI_hard_driver_cls SPI_MAX30009_driver("/dev/spidev0.0");
MAX30009_LIB MAX30009(&SPI_MAX30009_driver);


MAX30009_process::MAX30009_process()
{

}

void MAX30009_process::init()
{
    GPIO_MAX30009_POWER.set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
    for (uint32_t i=0; i<CURRENT_POINTS_COUNT; i++)
    {
        for (uint32_t j=0; j<FREQ_POINTS_COUNT; j++)
        {
            std::string filename = "calib/" +  std::to_string(i) + "_" +  std::to_string(j) + ".json";
            _calibrate_data[i][j]=get_calib_koef_from_file(filename);
        }
    }
}

MAX30009_CALIB_DATA  MAX30009_process::get_calib_koef_from_file(const std::string& filename)
{
    MAX30009_CALIB_DATA out;
    out.I_offset=0;
    out.I_coef=0;
    out.I_phase_coef=0;
    out.I_phase_cos=0;
    out.I_phase_sin=0;
    out.Q_offset=0;
    out.Q_coef=0;
    out.Q_phase_coef=0;
    out.Q_phase_cos=0;
    out.Q_phase_sin=0;

    if (std::filesystem::exists(filename)==false)
    {
        return out;
    }

    std::ifstream file(filename);
    if (file.is_open()==false)
    {
        return out;
    }

    try
    {
        nlohmann::json j;
        file >> j;

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

        std::cout  << filename << " - load OK" << std::endl;
    }
    catch (const std::exception& e)
    {

    }


    return out;
}

void MAX30009_process::process()
{


    if (_need_calibrate==true)
    {
        return;
    }

    if(MAX30009_user_sett.measure_enable==false)
    {
        return;
    }

    for (uint32_t i=0; i<128; i++)
    {
        MAX30009_FIFO_DATA fd1= {0},fd2= {0};
        MAX30009.read_two_FIFO_item(&fd1,&fd2);

        if (fd1.data_source!=MAX30009_ERROR_DATA_SOURCE && fd2.data_source!=MAX30009_ERROR_DATA_SOURCE)
        {
            _IFIFO_write_pos=(_IFIFO_write_pos+1)%_max_IFIFO_size ;
            if (_IFIFO_write_pos==_IFIFO_read_pos)
            {
                _IFIFO_read_pos=(_IFIFO_read_pos+1)%_max_IFIFO_size ;
            }

            if (fd1.data_source==MAX30009_I_CHANNEL)
            {
                _IFIFO_BUF[_IFIFO_write_pos].I_data=fd1.channel_value;
            }
            else if (fd1.data_source==MAX30009_Q_CHANNEL)
            {
                _IFIFO_BUF[_IFIFO_write_pos].Q_data=fd1.channel_value;
            }

            if (fd2.data_source==MAX30009_I_CHANNEL)
            {
                _IFIFO_BUF[_IFIFO_write_pos].I_data=fd2.channel_value;
            }
            else if (fd2.data_source==MAX30009_Q_CHANNEL)
            {
                _IFIFO_BUF[_IFIFO_write_pos].Q_data=fd2.channel_value;
            }
//            MAX30009_CALIB_DATA_TYPE calibrate_koef=_calibrate_data[MAX30009_user_sett.stimulate_current_select][MAX30009_user_sett.stimulate_frequency];
//            MAX30009.calculate_impendance(&fd1,calibrate_koef);
//            MAX30009.calculate_impendance(&fd2,calibrate_koef);
//            MAX30009_FIFO_DATA_CALIB_TYPE calibrate_data=MAX30009.calibrate_FIFO_data(fd1, fd2,calibrate_koef);
//            std::cout << fd1.channel_value << " -  " << fd1.impendance_value << " -  " << calibrate_data.I_cal_real  << " -  " << calibrate_data.Load_real << " -  " <<  calibrate_data.overload << std::endl;
        }
        else
        {
            break;
        }
    }

}

void MAX30009_process::add_sync_mark(int32_t sync_num)
{
    if (_need_calibrate==true)
    {
        return;
    }

    if(MAX30009_user_sett.measure_enable==false)
    {
        return;
    }

    _IFIFO_write_pos=(_IFIFO_write_pos+1)%_max_IFIFO_size ;
    if (_IFIFO_write_pos==_IFIFO_read_pos)
    {
        _IFIFO_read_pos=(_IFIFO_read_pos+1)%_max_IFIFO_size ;
    }

    _IFIFO_BUF[_IFIFO_write_pos].I_data=SYNC_MARK_MAGIC_NUM;
    _IFIFO_BUF[_IFIFO_write_pos].Q_data=sync_num;
}

std::string MAX30009_process::calibration_process(void)
{

    if (_need_calibrate==false)
    {
        MAX30009.stop_calibrate();
        _calibrate_current_index=0;
        _calibrate_freq_index=0;
        return "";
    }
    set_power_state(true);

    _calibrate_timer++;
    if (_calibrate_timer<CALIB_STEP_PERIOD)
    {
        return "";
    }
    _calibrate_timer=0;

//    uint16_t data_count=0;
//    static uint16_t old_data_count=0;
//    MAX30009.get_FIFO_data_count(&data_count);
//
//    if (old_data_count!=data_count)
//    {
//        old_data_count=data_count;
//        std::cout << data_count << std::endl;
//    }

    MAX30009_CALIB_STATE_ENUM_TYPE calibrate_state=MAX30009.calibrate_main_proccess();
    static MAX30009_CALIB_STATE_ENUM_TYPE old_calibrate_state=MAX30009_CALIB_STATE_NODATA;

    if (old_calibrate_state!=calibrate_state)
    {
        old_calibrate_state=calibrate_state;

        switch (calibrate_state)
        {
        case MAX30009_CALIB_STATE_NODATA:
            std::cout << "MAX30009_CALIB_STATE_NODATA";
            break;
        case MAX30009_CALIB_STATE_NEED_CALIB:
            std::cout << "MAX30009_CALIB_STATE_NEED_CALIB";
            break;
        case MAX30009_CALIB_STATE_PRE_START_CALIB:
            std::cout << "MAX30009_CALIB_STATE_PRE_START_CALIB";
            break;
        case MAX30009_CALIB_STATE_START_MEAS_OFFSET:
            std::cout << "MAX30009_CALIB_STATE_START_MEAS_OFFSET";
            break;
        case MAX30009_CALIB_STATE_MEAS_OFFSET:
            std::cout << "MAX30009_CALIB_STATE_MEAS_OFFSET";
            break;
        case MAX30009_CALIB_STATE_START_MEAS_IN_PHASE:
            std::cout << "MAX30009_CALIB_STATE_START_MEAS_IN_PHASE";
            break;
        case MAX30009_CALIB_STATE_MEAS_IN_PHASE:
            std::cout << "MAX30009_CALIB_STATE_MEAS_IN_PHASE";
            break;
        case MAX30009_CALIB_STATE_START_MEAS_QUAD:
            std::cout << "MAX30009_CALIB_STATE_START_MEAS_QUAD";
            break;
        case MAX30009_CALIB_STATE_MEAS_QUAD:
            std::cout << "MAX30009_CALIB_STATE_MEAS_QUAD";
            break;
        case MAX30009_CALIB_STATE_CALCULATE_COEF:
            std::cout << "MAX30009_CALIB_STATE_CALCULATE_COEF";
            break;
        case MAX30009_CALIB_STATE_READY:
            std::cout << "MAX30009_CALIB_STATE_READY";
            break;
        case MAX30009_CALIB_STATE_PRE_READY:
            std::cout << "MAX30009_CALIB_STATE_PRE_READY";
            break;
        case MAX30009_CALIB_STATE_STOPED:
            std::cout << "MAX30009_CALIB_STATE_STOPED";
            break;
        case MAX30009_CALIB_WAIT_DATA:
            std::cout << "MAX30009_CALIB_WAIT_DATA";
            break;
        case MAX30009_CALIB_IN_DELAY:
            std::cout << "MAX30009_CALIB_IN_DELAY";
            break;
        default:
            std::cout << "UNKNOWN_STATE";
            break;
        }
        std::cout << std::endl;
    }



    if (calibrate_state==MAX30009_CALIB_STATE_STOPED)
    {
        max30009_ext_MUX_obj.set_calibrate_mode();
        MAX30009.start_calibrate(MAX30009_CALIB_SOURCE_MAINPORT,
                                 CALIB_RESISTOR_VALUE,
                                 CURRENT_POINTS[_calibrate_current_index],
                                 FREQ_POINTS[_calibrate_freq_index],
                                 MAX30009_BIOZ_TOTAL_GAIN_5);


        std::cout << std::endl  << std::endl <<"START CALIBRATE: freq:" << _calibrate_freq_index << " current:" <<  _calibrate_current_index << std::endl;
    }


    if (calibrate_state==MAX30009_CALIB_STATE_READY)
    {
        //calibrate ready
        _calibrate_data[_calibrate_current_index][_calibrate_freq_index]=MAX30009.get_last_calib_data();
        std::string filename = "calib/" +  std::to_string(_calibrate_current_index) + "_" +  std::to_string(_calibrate_freq_index) + ".json";
        std::filesystem::create_directories("calib/");
        save_string_to_file(filename,get_calibration_json_data(MAX30009.get_last_calib_data()));
        MAX30009.stop_calibrate();

        _calibrate_freq_index++;
        if (_calibrate_freq_index>=FREQ_POINTS_COUNT)
        {
            _calibrate_freq_index=0;
            _calibrate_current_index++;
            if (_calibrate_current_index>=CURRENT_POINTS_COUNT)
            {
                //calibrate is finish
                _need_calibrate=false;
                process_all_settings_for_MAX30009();
                process_ext_MUX_settings_for_MAX30009();

            }
        }
        return get_calibration_json_data(MAX30009.get_last_calib_data());
    }
    return "";

}

bool MAX30009_process::save_string_to_file(const std::string& filename, const std::string& data)
{
    std::cout << "save file:" << filename << std::endl << std::endl;
    std::ofstream outputFile(filename, std::ios::out | std::ios::trunc);

    if (outputFile.is_open())
    {
        outputFile << data;
        outputFile.close();
        return true;
    }
    else
    {
        return false;
    }
}

std::string MAX30009_process::get_calibration_json_data(MAX30009_CALIB_DATA calib_koef)
{
    nlohmann::json response_json;
    response_json["type"] = "calib_data";
    for (uint32_t i=0; i<FREQ_POINTS_COUNT; i++)
    {
        if (FREQ_POINTS[i]==calib_koef.calibrate_frequency)
        {
            response_json["stimulate_frequency"] =i;
        }
    }

    for (uint32_t j=0; j<CURRENT_POINTS_COUNT; j++)
    {
        if (CURRENT_POINTS[j]==calib_koef.calibrate_current)
        {
            response_json["stimulate_current"] =j;
        }
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

    response_json["Q_cal_in"] =calib_koef.Q_cal_in;
    response_json["Q_cal_in_ADC"] =calib_koef.Q_cal_in_ADC;
    response_json["Q_cal_quad"] =calib_koef.I_cal_quad;
    return response_json.dump();
}

std::string MAX30009_process::process_JSON_line(const char * JSON_line)
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
                if (_need_calibrate==true)
                {
                    return "{\"type\":\"calibrate_runing\"}";
                }
                if (parsed_json.contains("stimulate_frequency"))
                {
                    MAX30009_user_sett.stimulate_frequency=parsed_json["stimulate_frequency"];
                }
                if (parsed_json.contains("measure_frequency"))
                {
                    MAX30009_user_sett.measure_frequency=parsed_json["measure_frequency"];
                }
                if (parsed_json.contains("out_LP_filter"))
                {
                    MAX30009_user_sett.out_LP_filter_select = parsed_json["out_LP_filter"];
                }
                if (parsed_json.contains("out_HP_filter"))
                {
                    MAX30009_user_sett.out_HP_filter_select = parsed_json["out_HP_filter"];
                }

                if (parsed_json.contains("stimulate_current"))
                {
                    MAX30009_user_sett.stimulate_current_select = parsed_json["stimulate_current"];
                }
                if (parsed_json.contains("measure_enable"))
                {
                    MAX30009_user_sett.measure_enable = parsed_json["measure_enable"];
                }

                if (parsed_json.contains("power_enable"))
                {
                    MAX30009_user_sett.power_enable = parsed_json["power_enable"];
                }
                if (parsed_json.contains("ext_MUX_state"))
                {
                    MAX30009_user_sett.ext_MUX_state = parsed_json["ext_MUX_state"];
                }
                process_ext_MUX_settings_for_MAX30009();
                process_all_settings_for_MAX30009();
                process_all_settings_for_MAX30009();
                process_all_settings_for_MAX30009();
                process_all_settings_for_MAX30009();
                return get_all_settings_as_json();
            }

            if (command_type == "get_data")
            {
                if (_need_calibrate==true)
                {
                    return "{\"type\":\"calibrate_runing\"}";
                }
                return get_data_as_json();
            }
            if (command_type == "start_calibrate")
            {
                _need_calibrate=true;
                _calibrate_current_index=0;
                _calibrate_freq_index=0;
                return "{\"type\":\"calibrate_started\"}";
            }
            if (command_type == "stop_calibrate")
            {
                _need_calibrate=false;
                _calibrate_current_index=0;
                _calibrate_freq_index=0;
                return "{\"type\":\"calibrate_stoped\"}";
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

std::string MAX30009_process::get_all_settings_as_json(void)
{
    nlohmann::json response_json;
    response_json["type"] = "actual_settings";
    response_json["stimulate_frequency"] = MAX30009_user_sett.stimulate_frequency;
    response_json["measure_frequency"] = MAX30009_user_sett.measure_frequency;
    response_json["out_LP_filter"] = MAX30009_user_sett.out_LP_filter_select;
    response_json["out_HP_filter"] = MAX30009_user_sett.out_HP_filter_select;
    response_json["stimulate_current"] = MAX30009_user_sett.stimulate_current_select;
    response_json["measure_enable"] = MAX30009_user_sett.measure_enable;
    response_json["power_enable"] = MAX30009_user_sett.power_enable;
    response_json["ext_MUX_state"] = MAX30009_user_sett.ext_MUX_state;
    return response_json.dump();
}

std::string MAX30009_process::get_data_as_json(void)
{
    std::vector<MAX30009_FIFO_DATA_CALIB_TYPE> decimated_data = get_decimate_IFIFO_data();

    nlohmann::json response_json;
    response_json["type"] = "data";
    response_json["data_frequency"] = MAX30009_user_sett.measure_frequency;
    response_json["data_size"] = decimated_data.size();
    response_json["timestamp"] =get_timestamp_string();

    nlohmann::json data_array = nlohmann::json::array();

    for (uint32_t i = 0; i < decimated_data.size(); ++i)
    {
        MAX30009_FIFO_DATA_CALIB_TYPE& item = decimated_data[i];

        nlohmann::json point_array = nlohmann::json::array();

        int32_t load_real=item.Load_real*10000.0;
        int32_t load_mag=item.Load_mag*10000.0;
        int32_t load_imag=item.Load_imag*10000.0;
        int32_t load_angle=item.Load_angle*10000.0;

        point_array.push_back(load_real);
        point_array.push_back(load_mag);
        point_array.push_back(load_imag);
        point_array.push_back(load_angle);
        point_array.push_back((int32_t)item.overload);

        data_array.push_back(point_array);
    }

    response_json["data"] = data_array;
    return response_json.dump();
}


void MAX30009_process::process_all_settings_for_MAX30009(void)
{


    set_power_state(MAX30009_user_sett.power_enable);

    MAX30009.set_PLL_state(false);
    MAX30009.set_BIOZ_I_channel_state(false);
    MAX30009.set_BIOZ_Q_channel_state(false);
    MAX30009.set_MUX_state(false);


    MAX30009.set_reference_clock_source(MAX30009_REFCLK_SRC_INT_32768);

    MAX30009.set_ext_capacitor_state(false);
    MAX30009.set_ext_resistor_state(false,0);
    MAX30009.set_BIOZ_bandgap_state(true);
    MAX30009.set_BIOZ_fast_start_mode(MAX30009_FAST_START_MODE_ON_200ms);


    MAX30009.set_BIOZ_amplifier_range(MAX30009_BIOZ_AMPLF_MODE_HIGH);
    MAX30009.set_BIOZ_amplifier_bandwidth(MAX30009_BIOZ_AMPLF_MODE_HIGH);
    MAX30009.set_BIOZ_DC_restore(true);

    MAX30009.set_MUX_DRVP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_EL1);
    MAX30009.set_MUX_BIP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_EL2B);
    MAX30009.set_MUX_BIN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_EL3B);
    MAX30009.set_MUX_DRVN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_EL4);

    MAX30009.set_MUX_CAL_state(false);
    MAX30009.set_MUX_CAL_ONLY_state(false);
    MAX30009.set_LEAD_RBIAS_BIN_state(true);
    MAX30009.set_LEAD_RBIAS_BIP_state(true);
    MAX30009.set_LEAD_RBIAS_VALUE(MAX30009_LEAD_RBIAS_50M);

    MAX30009.set_MUX_BIST_enable(false);
    MAX30009.set_MUX_GSR_enable(false);


    MAX30009.set_input_HP_filter(MAX30009_BIOZ_IN_HPFILTER_BYPASS);

    MAX30009.set_BIOZ_total_gain(MAX30009_BIOZ_TOTAL_GAIN_5);

    if(check_enumerate_for_value(MAX30009_user_sett.out_HP_filter_select,
                                 MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_VALUE_LIST,
                                 sizeof(MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_VALUE_LIST)))
    {
        MAX30009.set_out_DHP_filter((MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM)MAX30009_user_sett.out_HP_filter_select);
    }

    if(check_enumerate_for_value(MAX30009_user_sett.out_LP_filter_select,
                                 MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_VALUE_LIST,
                                 sizeof(MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_VALUE_LIST)))
    {
        MAX30009.set_out_DLP_filter((MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM)MAX30009_user_sett.out_LP_filter_select);
    }


    if (MAX30009_user_sett.stimulate_current_select>=CURRENT_POINTS_COUNT)
    {
        MAX30009_user_sett.stimulate_current_select=0;
    }

    MAX30009.set_BIOZ_constant_current_mode(CURRENT_POINTS[MAX30009_user_sett.stimulate_current_select]);


    if (MAX30009_user_sett.measure_frequency<MIN_MEASURE_FREQ)
    {
        MAX30009_user_sett.measure_frequency=MIN_MEASURE_FREQ;
    }
    if (MAX30009_user_sett.measure_frequency>MAX_MEASURE_FREQ)
    {
        MAX30009_user_sett.measure_frequency=MAX_MEASURE_FREQ;
    }

    if (MAX30009_user_sett.stimulate_frequency>=FREQ_POINTS_COUNT)
    {
        MAX30009_user_sett.stimulate_frequency=0;
    }

    MAX30009.set_drive_frequency(FREQ_POINTS[MAX30009_user_sett.stimulate_frequency]*10,MAX30009_user_sett.measure_frequency*10*10);

    for(uint32_t i=10; i<100; i++)
    {
        if(MAX30009_user_sett.measure_frequency*10>MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE/10)
        {
            MAX30009.set_drive_frequency(FREQ_POINTS[MAX30009_user_sett.stimulate_frequency]*10,MAX30009_user_sett.measure_frequency*10*i);
        }
        else
        {
            break;
        }
    }


    if (MAX30009_user_sett.measure_frequency*10>MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE)
    {
        //adc sample rate not can give measure frequency
        MAX30009_user_sett.measure_frequency=MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE/10;
    }

    if (MAX30009_user_sett.measure_enable==true)
    {
        MAX30009.set_PLL_state(true);
        MAX30009.set_BIOZ_I_channel_state(true);
        MAX30009.set_BIOZ_Q_channel_state(true);
        MAX30009.set_MUX_state(true);
    }
    else
    {
        MAX30009.set_PLL_state(false);
        MAX30009.set_BIOZ_I_channel_state(false);
        MAX30009.set_BIOZ_Q_channel_state(false);
        MAX30009.set_MUX_state(false);
    }

    MAX30009.Flush_FIFO();

    // MAX30009.start_load_all_registers();

    _max_IFIFO_size =(MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE*IFIFO_BUFFER_DURATION)/10;
    if (_max_IFIFO_size>IFIFO_BUFF_SIZE)
    {
        _max_IFIFO_size=IFIFO_BUFF_SIZE;
    }
    _IFIFO_write_pos=0;
    _IFIFO_read_pos=0;

}

void MAX30009_process::process_ext_MUX_settings_for_MAX30009(void)
{
    if ( MAX30009_user_sett.ext_MUX_state==MAX30009_EXT_MUX_ALL_OFF)
    {
        max30009_ext_MUX_obj.set_all_off_mode();
    }
    if ( MAX30009_user_sett.ext_MUX_state==MAX30009_EXT_MUX_4_WIRE)
    {
        max30009_ext_MUX_obj.set_4_wire_mode();
    }
    if ( MAX30009_user_sett.ext_MUX_state==MAX30009_EXT_MUX_2_WIRE)
    {
        max30009_ext_MUX_obj.set_2_wire_mode();
    }
    if ( MAX30009_user_sett.ext_MUX_state==MAX30009_EXT_MUX_CALIBRATE)
    {
        max30009_ext_MUX_obj.set_calibrate_mode();
    }
    if ( MAX30009_user_sett.ext_MUX_state==MAX30009_EXT_MUX_COLE_COLE)
    {
        max30009_ext_MUX_obj.set_Cole_Cole_mode();
    }
}

bool MAX30009_process::check_enumerate_for_value(uint8_t value,const uint8_t *value_list, uint8_t value_list_size)
{
    for (uint8_t i=0; i<value_list_size; i++)
    {
        if (value_list[i]==value)
        {
            return true;
        }
    }
    return false;
}



std::vector<MAX30009_FIFO_DATA_CALIB_TYPE>  MAX30009_process::get_decimate_IFIFO_data()
{

    std::vector<MAX30009_FIFO_DATA_CALIB_TYPE> decimated_data;

    if (_IFIFO_read_pos==_IFIFO_write_pos)
    {
        return decimated_data;
    }

    if (MAX30009_user_sett.measure_frequency==0)
    {
        return decimated_data;
    }

    float decimation_ratio = (float)MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE / ((float)MAX30009_user_sett.measure_frequency*10.0);

    if (decimation_ratio<1)
    {
        return decimated_data;
    }

    uint32_t decimated_data_position=0;
    int64_t sum_I = 0;
    int64_t sum_Q = 0;
    int32_t sum_count = 0;
    int32_t sync_number=0;

    for (uint32_t i=0; i<_max_IFIFO_size ; i++)
    {
        _IFIFO_read_pos=(_IFIFO_read_pos+1)%_max_IFIFO_size ;

        if ((float)i/decimation_ratio>decimated_data_position+1)
        {
            //need start new data decimate
            decimated_data_position++;

            MAX30009_FIFO_DATA I_ch_data;
            MAX30009_FIFO_DATA Q_ch_data;


            I_ch_data.data_source=MAX30009_I_CHANNEL;
            Q_ch_data.data_source=MAX30009_Q_CHANNEL;

            I_ch_data.channel_value=sum_I/sum_count;
            Q_ch_data.channel_value=sum_Q/sum_count;

            MAX30009_CALIB_DATA_TYPE calibrate_koef=_calibrate_data[MAX30009_user_sett.stimulate_current_select][MAX30009_user_sett.stimulate_frequency];
            MAX30009.calculate_impendance(&I_ch_data,calibrate_koef);
            MAX30009.calculate_impendance(&Q_ch_data,calibrate_koef);

            MAX30009_FIFO_DATA_CALIB_TYPE calibrate_data=MAX30009.calibrate_FIFO_data(I_ch_data, Q_ch_data,calibrate_koef);
            decimated_data.push_back(calibrate_data);

            if (sync_number>0)
            {

                MAX30009_FIFO_DATA_CALIB_TYPE sync_data= {0,0,0,0,0,0,0,0,0,0,false};
                sync_data.Load_real=SYNC_MARK_MAGIC_NUM;
                sync_data.Load_mag=sync_number;
                decimated_data.push_back(sync_data);
                sync_number=0;
            }

            sum_I = 0;
            sum_Q = 0;
            sum_count = 0;

            int32_t buffer_size = (_IFIFO_write_pos-_IFIFO_read_pos + _max_IFIFO_size) % _max_IFIFO_size;
            if (buffer_size<decimation_ratio+1)
            {
                break;
            }
        }

        if (_IFIFO_BUF[_IFIFO_read_pos].I_data==SYNC_MARK_MAGIC_NUM)
        {
            sync_number=_IFIFO_BUF[_IFIFO_read_pos].Q_data;
        }
        else
        {
            sum_I=sum_I+_IFIFO_BUF[_IFIFO_read_pos].I_data;
            sum_Q=sum_Q+_IFIFO_BUF[_IFIFO_read_pos].Q_data;
            sum_count++;
        }

    }

    return decimated_data;
}

void MAX30009_process::set_power_state(bool state)
{
    if (_old_power_state==state) return;
    _old_power_state=state;
    if (state==true)
    {
        GPIO_MAX30009_POWER.set_GPIO_state(VT_GPIO_SET);
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    else
    {
        GPIO_MAX30009_POWER.set_GPIO_state(VT_GPIO_UNSET);
    }
}


std::string MAX30009_process::get_timestamp_string()
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
