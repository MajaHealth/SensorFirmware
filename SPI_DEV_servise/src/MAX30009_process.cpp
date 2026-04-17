#include "MAX30009_process.h"
#include <iomanip>
#include <ctime>

using json = nlohmann::json;



MAX30009_uset MAXsett;
MAX30009_data_storage MAXdata;
MAX30009_base_cal_table MAXbase_calib_table;

GPIO_driver_cls GPIO_MUX_R1{17};
GPIO_driver_cls GPIO_MUX_R2{6};
GPIO_driver_cls GPIO_MUX_R3{27};
GPIO_driver_cls GPIO_MUX_R4{13};
GPIO_driver_cls GPIO_MUX_R5{26};
GPIO_driver_cls GPIO_MUX_CAL_OR_WORK{19};
//GPIO_driver_cls GPIO_MUX_2W{5};
GPIO_driver_cls GPIO_MAX30009_POWER{21};

MAX30009_EXT_MUX_GPIOs_TDE MUX_GPIOs= {&GPIO_MUX_CAL_OR_WORK,&GPIO_MUX_R1,&GPIO_MUX_R2,&GPIO_MUX_R3,&GPIO_MUX_R4,&GPIO_MUX_R5};
max30009_ext_MUX max30009_ext_MUX_obj(MUX_GPIOs);
SPI_hard_driver_cls SPI_MAX30009_driver("/dev/spidev0.0");
MAX30009_LIB MAX30009(&SPI_MAX30009_driver);

static const char * max30009_lead_confidence_to_string(MAX30009_LEAD_CONFIDENCE_ENUM_TYPE confidence)
{
    switch (confidence)
    {
    case MAX30009_LEAD_CONNECTED:
        return "connected";
    case MAX30009_LEAD_DEFINITE_OFF:
        return "definite_off";
    case MAX30009_LEAD_PROBABLE_OFF:
        return "probable_off";
    case MAX30009_LEAD_AMBIGUOUS:
        return "ambiguous";
    default:
        return "unknown";
    }
}

MAX30009_process::MAX30009_process()
{

}

void MAX30009_process::init()
{
    GPIO_MAX30009_POWER.set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
    MAXbase_calib_table.init(BASE_DATA_COUNT);
    MAX30009.stop_calibrate();
}




void MAX30009_process::process()
{
    if (_in_calibrate==true) return;
    if(autotest.need_do==true) autotest_process();

    static std::chrono::steady_clock::time_point _last_status_time = std::chrono::steady_clock::now();
    auto now = std::chrono::steady_clock::now();
    if (now - _last_status_time >std::chrono::milliseconds(200))
    {
        _last_status_time=now;
        if (MAX30009.read_status(&status)==true)
        {
            update_passive_lead_monitor(status);
        }
    }



    if(_meas_mode!=MMD_MEASURING) return;

    check_FIFO_buffer();

}

bool MAX30009_process::update_debounced_flag(bool raw_value, uint8_t &counter, bool &debounced_value)
{
    if (raw_value)
    {
        if (counter < LEAD_MONITOR_DEBOUNCE_COUNT)
        {
            counter++;
        }
    }
    else
    {
        counter=0;
    }

    debounced_value=(counter>=LEAD_MONITOR_DEBOUNCE_COUNT);
    return debounced_value;
}

void MAX30009_process::reset_passive_lead_monitor(void)
{
    _lead_status=MAX30009_PASSIVE_LEAD_MONITOR_STATUS_TYPE{};
    _lead_status.active=_lead_monitor_active;
    _lead_status.el1_drvp_confidence=MAX30009_LEAD_CONNECTED;
    _lead_status.el2b_bip_confidence=MAX30009_LEAD_CONNECTED;
    _lead_status.el3b_bin_confidence=MAX30009_LEAD_CONNECTED;
    _lead_status.el4_drvn_confidence=MAX30009_LEAD_CONNECTED;

    _lead_bip_high_counter=0;
    _lead_bip_low_counter=0;
    _lead_bin_high_counter=0;
    _lead_bin_low_counter=0;
    _lead_drv_oor_counter=0;
    _lead_bioz_over_counter=0;
    _lead_bioz_under_counter=0;
}

void MAX30009_process::update_passive_lead_monitor(const MAX30009_STATUS_STRUCT_TYPE &new_status)
{
    if (_lead_monitor_active==false || _meas_mode!=MMD_MEASURING)
    {
        if (_lead_status.active==true)
        {
            _lead_monitor_active=false;
            reset_passive_lead_monitor();
        }
        return;
    }

    _lead_status.active=true;

    update_debounced_flag(new_status.DC_LOFF_BIP_overlimit, _lead_bip_high_counter, _lead_status.raw_bip_high);
    update_debounced_flag(new_status.DC_LOFF_BIP_underlimit, _lead_bip_low_counter, _lead_status.raw_bip_low);
    update_debounced_flag(new_status.DC_LOFF_BIN_overlimit, _lead_bin_high_counter, _lead_status.raw_bin_high);
    update_debounced_flag(new_status.DC_LOFF_BIN_underlimit, _lead_bin_low_counter, _lead_status.raw_bin_low);
    update_debounced_flag(new_status.DRVN_out_of_range, _lead_drv_oor_counter, _lead_status.raw_drv_oor);
    update_debounced_flag(new_status.BIOZ_over_level, _lead_bioz_over_counter, _lead_status.raw_bioz_over);
    update_debounced_flag(new_status.BIOZ_under_level, _lead_bioz_under_counter, _lead_status.raw_bioz_under);

    const bool bip_off=(_lead_status.raw_bip_high || _lead_status.raw_bip_low);
    const bool bin_off=(_lead_status.raw_bin_high || _lead_status.raw_bin_low);
    const bool sense_fault=(bip_off || bin_off);
    const bool ac_lead_off=(_lead_status.raw_bioz_over || _lead_status.raw_bioz_under);
    const bool current_leads_invalid=(ac_lead_off && (!sense_fault || _lead_status.raw_drv_oor));

    _lead_status.el2b_bip_off=bip_off;
    _lead_status.el3b_bin_off=bin_off;
    _lead_status.current_leads_invalid=current_leads_invalid;
    _lead_status.drive_path_fault=current_leads_invalid;
    _lead_status.drive_compliance_warning=(_lead_status.raw_drv_oor && !ac_lead_off);
    _lead_status.probable_el1_drvp_off=false;
    _lead_status.probable_el4_drvn_off=false;
    _lead_status.ambiguous=current_leads_invalid;

    _lead_status.disconnected_mask=0;
    _lead_status.possible_disconnected_mask=0;

    _lead_status.el1_drvp_confidence=MAX30009_LEAD_CONNECTED;
    _lead_status.el2b_bip_confidence=MAX30009_LEAD_CONNECTED;
    _lead_status.el3b_bin_confidence=MAX30009_LEAD_CONNECTED;
    _lead_status.el4_drvn_confidence=MAX30009_LEAD_CONNECTED;

    if (bip_off)
    {
        _lead_status.disconnected_mask|=MAX30009_LEAD_MASK_EL2B_BIP;
        _lead_status.possible_disconnected_mask|=MAX30009_LEAD_MASK_EL2B_BIP;
        _lead_status.el2b_bip_confidence=MAX30009_LEAD_DEFINITE_OFF;
    }
    if (bin_off)
    {
        _lead_status.disconnected_mask|=MAX30009_LEAD_MASK_EL3B_BIN;
        _lead_status.possible_disconnected_mask|=MAX30009_LEAD_MASK_EL3B_BIN;
        _lead_status.el3b_bin_confidence=MAX30009_LEAD_DEFINITE_OFF;
    }

    if (current_leads_invalid)
    {
        _lead_status.possible_disconnected_mask|=(MAX30009_LEAD_MASK_EL1_DRVP | MAX30009_LEAD_MASK_EL4_DRVN);
        _lead_status.el1_drvp_confidence=MAX30009_LEAD_AMBIGUOUS;
        _lead_status.el4_drvn_confidence=MAX30009_LEAD_AMBIGUOUS;
    }
}

void MAX30009_process::check_FIFO_buffer(void)
{
    for (uint32_t i=0; i<128; i++)
    {
        MAX30009_FIFO_DATA I_fd= {0},Q_fd= {0};

        if (MAX30009.read_two_FIFO_item(&I_fd,&Q_fd))
        {
            I_ch_flt.filtered(I_fd.channel_value);
            Q_ch_flt.filtered(Q_fd.channel_value);
            MAXdata.add_new_data_item(I_fd,Q_fd,status.DRVN_out_of_range);
        }
        else
        {
            break;
        }
    }
}


void MAX30009_process::add_sync_mark(int32_t sync_num)
{
    if (_in_calibrate==true)return;
    if(_meas_mode!=MMD_MEASURING) return;
    MAXdata.add_sync_mark(sync_num);
}

std::string MAX30009_process::measure_process(void)
{

    if (_meas_mode==MMD_MEASURING) return "";
    if (_meas_mode==MMD_STOP) return "";

    static std::chrono::steady_clock::time_point _last_calib_time = std::chrono::steady_clock::now();
    auto now = std::chrono::steady_clock::now();
    if (now - _last_calib_time < std::chrono::milliseconds(10)) return "";

    _last_calib_time = now;
    static uint32_t base_table_index=0;
    static uint32_t pre_meas_count=0;
    static int32_t sum_I_ch=0;
    static int32_t sum_Q_ch=0;
    static int32_t skip_sample=0;
    if (_meas_mode==MMD_BASE_MEASURE_START)
    {
        // max30009_ext_MUX_obj.on_calib_mode(318);

        MAXsett.update_stim_current(MAX30009.get_limited_current_by_freq(MAXsett.get_set().stimulate_current,MAXsett.get_set().stimulate_frequency_hz));

        max30009_ext_MUX_obj.off_calib_mode();
        base_table_index=MAXbase_calib_table.get_table_index(MAXsett.get_set().stimulate_frequency_hz);

        MAX30009_START_MEASURE_DATA_TDS start_data{};
        start_data.stimulate_frequency_hz=MAXbase_calib_table.get_frequency_from_index(base_table_index);
        start_data.measure_frequency_hz=1000;

        start_data.out_LP_filter=MAX30009_BIOZ_DLPF_BYPASS;
        start_data.out_HP_filter=MAX30009_BIOZ_DHPF_BYPASS;
        start_data.input_HP_filter=MAX30009_BIOZ_IN_HPFILTER_BYPASS;

        start_data.bioz_total_gain=BASE_TABLE_GAIN;
        start_data.stimulate_current=BASE_TABLE_CURRENT;

        start_measure_MAX30009(start_data);

        _meas_mode=MMD_BASE_MEASURING;
        pre_meas_impendace_value=0;
        pre_meas_count=0;
        sum_I_ch=0;
        sum_Q_ch=0;
        skip_sample=10;

        return "{\"type\":\"meas_state\",\"state\":\"pre_measuring\"}";
    }
    else if (_meas_mode==MMD_BASE_MEASURING)
    {
        MAX30009_FIFO_DATA I_fd{},Q_fd{};
        if (MAX30009.read_two_FIFO_item(&I_fd,&Q_fd))
        {
            if (skip_sample>0)
            {
                skip_sample--;
                MAX30009.Flush_FIFO();
                return "";
            }
            pre_meas_count++;
            sum_I_ch=sum_I_ch+I_fd.channel_value;
            sum_Q_ch=sum_Q_ch+Q_fd.channel_value;
            if (pre_meas_count>=20)
            {
                I_fd.channel_value=sum_I_ch/20;
                Q_fd.channel_value=sum_Q_ch/20;


                MAX30009_LIB::calculate_impendance(&I_fd,MAXbase_calib_table.get_calib_data(base_table_index),MAX30009.get_BIOZ_data());
                MAX30009_LIB::calculate_impendance(&Q_fd,MAXbase_calib_table.get_calib_data(base_table_index),MAX30009.get_BIOZ_data());
                MAX30009_FIFO_DATA_CALIB_TYPE calibrated_data=MAX30009_LIB::calibrate_FIFO_data(I_fd, Q_fd,MAXbase_calib_table.get_calib_data(base_table_index));
                pre_meas_impendace_value=calibrated_data.Load_real;
                _meas_mode=MMD_CALIBRATE_START;
                return "{\"type\":\"meas_state\",\"state\":\"pre_measure_end\",\"real\":" + std::to_string(pre_meas_impendace_value) + " }";
            }
        }
    }
    else if (_meas_mode==MMD_CALIBRATE_START)
    {
        _work_calibrate_resistor_value=pre_meas_impendace_value;
        _need_work_calibrate=true;
        _work_gain=get_auto_gain(pre_meas_impendace_value,MAXsett.get_set().stimulate_current);
        _meas_mode=MMD_CALIBRATING;
        return "{\"type\":\"meas_state\",\"state\":\"calibrating\"}";
    }
    else if (_meas_mode==MMD_CALIBRATING)
    {
        if (_need_work_calibrate==false)
        {
            _meas_mode=MMD_MEASURE_START;
            return "{\"type\":\"meas_state\",\"state\":\"calibrate_end\"}";
        }
    }
    else if (_meas_mode==MMD_MEASURE_START)
    {
        MAX30009_START_MEASURE_DATA_TDS start_data{};
        start_data.stimulate_frequency_hz=MAXsett.get_set().stimulate_frequency_hz;
        start_data.measure_frequency_hz=MAXsett.get_set().measure_frequency_hz;

        start_data.out_LP_filter=MAXsett.get_set().out_LP_filter;
        start_data.out_HP_filter=MAXsett.get_set().out_HP_filter;
        start_data.input_HP_filter=MAXsett.get_set().input_HP_filter;

        start_data.bioz_total_gain=_work_gain;
        // start_data.bioz_total_gain=MAX30009_BIOZ_TOTAL_GAIN_2;
        start_data.stimulate_current=MAXsett.get_set().stimulate_current;
        start_data.passive_lead_monitor_enable=true;

        start_measure_MAX30009(start_data);
        MAXsett.update_real_gain(start_data.bioz_total_gain);
        MAXsett.update_stim_current(start_data.stimulate_current);
        MAXsett.update_real_measure_freq(start_data.measure_frequency_hz);
        MAXsett.update_real_stimulate_freq(start_data.stimulate_frequency_hz);
        _meas_mode=MMD_MEASURING;
        return "{\"type\":\"meas_state\",\"state\":\"start_measuring\"} " + MAXsett.get_all_settings_as_json();
    }
    return "";
}

MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE  MAX30009_process::get_auto_gain(int32_t pre_measure_imp,MAX30009_CURRENT_AMP_ENUM_TYPE current)
{
    pre_measure_imp=labs(pre_measure_imp);
    uint64_t V_peak_nV = (uint64_t)pre_measure_imp *  (uint64_t)MAX30009_STATIC::get_RMS_current_nA(current);
    //AFE limits (in nV) with 40% headroom (600mV on ADC)
    const uint64_t LIMIT_G10_nV = 60000000; // G10: 600mV/10 = 60mV
    const uint64_t LIMIT_G5_nV = 120000000; // G5: 600mV/5 = 120mV
    const uint64_t LIMIT_G2_nV = 300000000; // G2: 600mV/2= 300mV

    if (V_peak_nV > LIMIT_G2_nV) return MAX30009_BIOZ_TOTAL_GAIN_1;
    if (V_peak_nV > LIMIT_G5_nV) return MAX30009_BIOZ_TOTAL_GAIN_2;
    if (V_peak_nV > LIMIT_G10_nV) return MAX30009_BIOZ_TOTAL_GAIN_5;
    return MAX30009_BIOZ_TOTAL_GAIN_10;
}


void MAX30009_process::start_build_calibrate_table(void)
{
    _need_buid_calibrate_table=true;
    _build_base_table_index=0;
}

std::string MAX30009_process::calibration_process(void)
{
    if (MAX30009.get_calibrate_state()==MAX30009_CALIB_STATE_STOPED)
    {
        if(_need_buid_calibrate_table==true)
        {

            if (_build_base_table_index<BASE_DATA_COUNT)
            {
                uint32_t calib_resisor_value=max30009_ext_MUX_obj.on_calib_mode(BASE_TABLE_RESISTOR_VALUE);
                uint32_t calibrate_freq=MAXbase_calib_table.get_frequency_from_index(_build_base_table_index);
                MAX30009.start_calibrate(calib_resisor_value,BASE_TABLE_CURRENT,calibrate_freq,BASE_TABLE_GAIN,MAX30009_BIOZ_IN_HPFILTER_BYPASS);
                _in_calibrate=true;
            }
            else
            {
                _need_buid_calibrate_table=false;
                max30009_ext_MUX_obj.off_calib_mode();
                MAXbase_calib_table.save_all_calib_to_file();
            }
        }
        else if(_need_work_calibrate==true)
        {
            uint32_t calib_resisor_value=max30009_ext_MUX_obj.on_calib_mode(_work_calibrate_resistor_value);
            MAX30009.start_calibrate(calib_resisor_value,
                                     MAX30009.get_limited_current_by_freq(MAXsett.get_set().stimulate_current,MAXsett.get_set().stimulate_frequency_hz),
                                     MAXsett.get_set().stimulate_frequency_hz,
                                     _work_gain,
                                     MAXsett.get_set().input_HP_filter);
            _in_calibrate=true;
        }
    }



    if (_in_calibrate==false) return "";

    set_power_state(true);

    static std::chrono::steady_clock::time_point _last_calib_time = std::chrono::steady_clock::now();
    auto now = std::chrono::steady_clock::now();
    if (now - _last_calib_time > std::chrono::milliseconds(10))
    {
        _last_calib_time = now;

        MAX30009_CALIB_STATE_ENUM_TYPE calibrate_state=MAX30009.calibrate_main_proccess();
        static MAX30009_CALIB_STATE_ENUM_TYPE old_calibrate_state=MAX30009_CALIB_STATE_NODATA;

        if (old_calibrate_state!=calibrate_state)
        {
            old_calibrate_state=calibrate_state;
            std::cout << MAX30009_STATIC::calib_state_to_string(calibrate_state)<< std::endl;
        }

        if (calibrate_state==MAX30009_CALIB_STATE_READY)
        {

            if(_need_buid_calibrate_table==true)
            {
                MAXbase_calib_table.save_calib_data(_build_base_table_index,MAX30009.get_last_calib_data());
                _build_base_table_index++;
            }
            else if(_need_work_calibrate==true)
            {
                _need_work_calibrate=false;
                _work_calib_data=MAX30009.get_last_calib_data();
                max30009_ext_MUX_obj.off_calib_mode();

            }

            _in_calibrate=false;
            MAX30009.stop_calibrate();
            return MAX30009_base_cal_table::get_calibration_json_data(MAX30009.get_last_calib_data());
        }
    }


    return "";

}

std::string MAX30009_process::get_lead_status_as_json(void)
{
    nlohmann::json response_json;
    response_json["type"]="lead_status";
    response_json["active"]=_lead_status.active;
    response_json["timestamp"]=MAX30009_STATIC::get_timestamp_string();
    response_json["debounce_samples"]=LEAD_MONITOR_DEBOUNCE_COUNT;

    nlohmann::json config_json;
    config_json["enabled_after_final_calibration"]=_lead_status.active;
    config_json["loff_imag"]=LEAD_MONITOR_LOFF_IMAG;
    config_json["loff_thresh"]=LEAD_MONITOR_LOFF_THRESH;
    config_json["loff_ipol"]=0;
    config_json["loff_rapid"]=false;
    config_json["bioz_cmp"]=LEAD_MONITOR_BIOZ_CMP;
    config_json["bioz_low_thresh"]=LEAD_MONITOR_BIOZ_LO_THRESH;
    config_json["bioz_high_thresh"]=LEAD_MONITOR_BIOZ_HI_THRESH;
    response_json["config"]=config_json;

    nlohmann::json raw_json;
    raw_json["bip_high"]=_lead_status.raw_bip_high;
    raw_json["bip_low"]=_lead_status.raw_bip_low;
    raw_json["bin_high"]=_lead_status.raw_bin_high;
    raw_json["bin_low"]=_lead_status.raw_bin_low;
    raw_json["drv_oor"]=_lead_status.raw_drv_oor;
    raw_json["bioz_over"]=_lead_status.raw_bioz_over;
    raw_json["bioz_under"]=_lead_status.raw_bioz_under;
    response_json["raw"]=raw_json;

    nlohmann::json derived_json;
    derived_json["el2b_bip_off"]=_lead_status.el2b_bip_off;
    derived_json["el3b_bin_off"]=_lead_status.el3b_bin_off;
    derived_json["current_leads_invalid"]=_lead_status.current_leads_invalid;
    derived_json["drive_path_fault"]=_lead_status.drive_path_fault;
    derived_json["drive_compliance_warning"]=_lead_status.drive_compliance_warning;
    derived_json["probable_el1_drvp_off"]=_lead_status.probable_el1_drvp_off;
    derived_json["probable_el4_drvn_off"]=_lead_status.probable_el4_drvn_off;
    derived_json["ambiguous"]=_lead_status.ambiguous;
    derived_json["disconnected_mask"]=_lead_status.disconnected_mask;
    derived_json["possible_disconnected_mask"]=_lead_status.possible_disconnected_mask;
    response_json["derived"]=derived_json;

    nlohmann::json confidence_json;
    confidence_json["el1_drvp"]=max30009_lead_confidence_to_string(_lead_status.el1_drvp_confidence);
    confidence_json["el2b_bip"]=max30009_lead_confidence_to_string(_lead_status.el2b_bip_confidence);
    confidence_json["el3b_bin"]=max30009_lead_confidence_to_string(_lead_status.el3b_bin_confidence);
    confidence_json["el4_drvn"]=max30009_lead_confidence_to_string(_lead_status.el4_drvn_confidence);
    response_json["confidence"]=confidence_json;

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
                if (MAXsett.process_JSON_settings(JSON_line)==false) return "{\"type\":\"error settings JSON\"}";

                if(MAXsett.get_set().measure_enable==true)
                {
                    _meas_mode=MMD_BASE_MEASURE_START;
                    //_meas_mode=MMD_MEASURE_START;
                    return "";
                }
                else
                {
                    _meas_mode=MMD_STOP;
                    stop_measure_MAX30009();
                    return MAXsett.get_all_settings_as_json();
                }
            }

            if (command_type == "get_data")
            {
                if(_meas_mode!=MMD_MEASURING) return "{\"type\":\"no_measure\"}";
                return MAXdata.get_data_as_json(_work_calib_data,MAX30009.get_BIOZ_data());
            }
            if (command_type == "get_lead_status")
            {
                return get_lead_status_as_json();
            }
            if (command_type == "build_base_table")
            {
                start_build_calibrate_table();
                return "{\"type\":\"build_base_table_started\"}";
            }
            if (command_type == "poweroff")
            {
                _lead_monitor_active=false;
                reset_passive_lead_monitor();
                set_power_state(false);
                max30009_ext_MUX_obj.off_all_out();
                return "{\"type\":\"power_is_off\"}";
            }
            if (command_type == "auto_test")
            {

                if (parsed_json.contains("freqs_list") && parsed_json["freqs_list"].is_array())
                {
                    autotest.freqs_list.clear();
                    for (uint32_t i=0; i < parsed_json["freqs_list"].size(); ++i)
                    {
                        uint32_t freq_value = parsed_json["freqs_list"][i].get<uint32_t>();
                        autotest.freqs_list.push_back(freq_value);
                    }
                }
                if (parsed_json.contains("currs_list") && parsed_json["currs_list"].is_array())
                {
                    autotest.currs_list.clear();
                    for (uint32_t i=0; i < parsed_json["currs_list"].size(); ++i)
                    {
                        autotest.currs_list.push_back(parsed_json["currs_list"][i]);
                    }
                }
                start_autotest();

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


MAX30009_START_MEASURE_DATA_TDS & MAX30009_process::start_measure_MAX30009(MAX30009_START_MEASURE_DATA_TDS & start_data)
{
    set_power_state(true);

    MAX30009.set_PLL_state(false);
    MAX30009.set_BIOZ_I_channel_state(false);
    MAX30009.set_BIOZ_Q_channel_state(false);
    MAX30009.set_MUX_state(false);

    MAX30009.set_reference_clock_source(MAX30009_REFCLK_SRC_INT_32768);
    MAX30009.set_BIOZ_bandgap_state(true);

    MAX30009.set_BIOZ_amplifier_range(MAX30009_BIOZ_AMPLF_MODE_HIGH);
    MAX30009.set_BIOZ_amplifier_bandwidth(MAX30009_BIOZ_AMPLF_MODE_HIGH);


    MAX30009.set_ext_capacitor_state(false);
    MAX30009.set_BIOZ_DC_restore(true);
    MAX30009.set_EN_DRV_OOR(true);
    MAX30009.set_MUX_EN_INT_INLOAD(true);
    MAX30009.set_MUX_EN_EXT_INLOAD(true);

    MAX30009.set_input_HP_filter(start_data.input_HP_filter);
    MAX30009.set_out_DHP_filter(start_data.out_HP_filter);
    MAX30009.set_out_DLP_filter(start_data.out_LP_filter);

    MAX30009.set_MUX_DRVP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_EL1);
    MAX30009.set_MUX_BIP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_EL2B);
    MAX30009.set_MUX_BIN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_EL3B);
    MAX30009.set_MUX_DRVN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_EL4);

    MAX30009.set_LEAD_RBIAS_BIN_state(true);
    MAX30009.set_LEAD_RBIAS_BIP_state(true);
    MAX30009.set_LEAD_RBIAS_VALUE(MAX30009_LEAD_RBIAS_50M);



    MAX30009.set_MUX_state(true);


    MAX30009.set_BIOZ_fast_start_mode(MAX30009_FAST_START_MODE_ON_200ms);

    MAX30009.set_BIOZ_total_gain(start_data.bioz_total_gain);

    MAX30009.set_drive_frequency(start_data.stimulate_frequency_hz*10, start_data.measure_frequency_hz*10*10);

    for(uint32_t i=10; i<100; i++)
    {
        MAX30009.set_drive_frequency(start_data.stimulate_frequency_hz*10, start_data.measure_frequency_hz*10*i);

        if(start_data.measure_frequency_hz*10*10 <= MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE)
        {
            break;
        }
    }

    if (start_data.measure_frequency_hz*10 > MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE)
    {
        start_data.measure_frequency_hz = MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE/10;
    }

    MAX30009.set_BIOZ_constant_current_mode(start_data.stimulate_current);

    start_data.stimulate_frequency_hz = MAX30009.get_all_frequency().BIOZ_DRIVE_FREQ/10;
    start_data.stimulate_current = MAX30009.get_BIOZ_data().current_select;

    _lead_monitor_active=start_data.passive_lead_monitor_enable;
    reset_passive_lead_monitor();

    MAX30009.set_EN_LON_DET(false);
    MAX30009.set_LOFF_RAPID(false);
    MAX30009.set_EN_EXT_LOFF(false);

    if (start_data.passive_lead_monitor_enable==true)
    {
        MAX30009.set_EN_LOFF_DET(false);
        MAX30009.set_EN_BIOZ_THRESH(false);

        MAX30009.set_LOFF_IPOL(false);
        MAX30009.set_LOFF_IMAG(LEAD_MONITOR_LOFF_IMAG);
        MAX30009.set_LOFF_THRESH(LEAD_MONITOR_LOFF_THRESH);

        MAX30009.set_BIOZ_CMP(LEAD_MONITOR_BIOZ_CMP);
        MAX30009.set_BIOZ_LO_THRESH(LEAD_MONITOR_BIOZ_LO_THRESH);
        MAX30009.set_BIOZ_HI_THRESH(LEAD_MONITOR_BIOZ_HI_THRESH);

        MAX30009.set_EN_DRV_OOR(true);
        MAX30009.set_EN_LOFF_DET(true);
        MAX30009.set_EN_BIOZ_THRESH(true);
    }
    else
    {
        MAX30009.set_EN_LOFF_DET(false);
        MAX30009.set_EN_BIOZ_THRESH(false);
    }

    MAX30009.set_PLL_state(true);
    MAX30009.set_BIOZ_I_channel_state(true);
    MAX30009.set_BIOZ_Q_channel_state(true);

    MAX30009.Flush_FIFO();
    MAXdata.reinit_buffer(MAX30009.get_all_frequency().BIOZ_ADC_SAMPLE_RATE, start_data.measure_frequency_hz);

    return start_data;
}



void  MAX30009_process::stop_measure_MAX30009(void)
{
    _lead_monitor_active=false;
    reset_passive_lead_monitor();
    MAX30009.set_EN_LOFF_DET(false);
    MAX30009.set_EN_BIOZ_THRESH(false);
    MAX30009.set_EN_LON_DET(false);
    MAX30009.set_PLL_state(false);
    MAX30009.set_BIOZ_I_channel_state(false);
    MAX30009.set_BIOZ_Q_channel_state(false);
    MAX30009.set_MUX_state(false);
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



MAX30009_DEBUG_DATA_ITEM_TDS MAX30009_process::get_debug_data_item()
{

    MAX30009_DEBUG_DATA_ITEM_TDS out;
    out.user_set=  MAXsett.get_set();

    MAX30009_FIFO_DATA I_ch_data= {0,0,0,MAX30009_I_CHANNEL};
    MAX30009_FIFO_DATA Q_ch_data= {0,0,0,MAX30009_Q_CHANNEL};


    I_ch_data.channel_value=I_ch_flt.get_value();
    Q_ch_data.channel_value=Q_ch_flt.get_value();

    MAX30009.calculate_impendance(&I_ch_data,_work_calib_data,MAX30009.get_BIOZ_data());
    MAX30009.calculate_impendance(&Q_ch_data,_work_calib_data,MAX30009.get_BIOZ_data());

    out.data=MAX30009.calibrate_FIFO_data(I_ch_data, Q_ch_data,_work_calib_data);

    out.I_ch_data=I_ch_data;
    out.Q_ch_data=Q_ch_data;

    out.work_calib_data=_work_calib_data;
    out.status=status;

    return out;
}

void MAX30009_process::start_autotest(void)
{
    autotest.need_do=true;
    autotest.freq_index=0;
    autotest.curr_index=0;
    autotest.wait_stabile_data=0;

    autotest.csv_file.open(MAX30009_STATIC::get_filename_timestamp_string() + ".csv", std::ios::out | std::ios::trunc);
    if (autotest.csv_file.is_open())
    {
        autotest.csv_file << "Current,Freq_Hz,Pre_meas_ohm,Calib_Ohm,Gain,Load_Real,Load_Imag,Load_Mag,Load_Angle,Overload,DRV_overload,I_ADC,Q_ADC,I_IMP_NO_CAL,Q_IMP_NO_CAL,I_CAL_ADC,Q_CAL_ADC\n";
    }
}
void MAX30009_process::autotest_process(void)
{

    if (autotest.currs_list.size()==0 || autotest.freqs_list.size()==0 )
    {
        autotest.need_do=false;
        return;
    }
    if (autotest.wait_stabile_data>0)
    {
        if (_meas_mode==MMD_MEASURING) autotest.wait_stabile_data--;
        if (_meas_mode==MMD_STOP)
        {
            autotest.wait_stabile_data=0;
            return;
        }
        if (autotest.wait_stabile_data==0)
        {
//collect data
            MAX30009_DEBUG_DATA_ITEM_TDS dbg_data= get_debug_data_item();
            std::cout  << std::endl   << std::endl   << std::endl  << "autotest:" << dbg_data.data.Load_real  << std::endl   << std::endl   << std::endl ;

            if (autotest.csv_file.is_open())
            {
                std::stringstream ss;
                ss << MAX30009_STATIC::current_to_string(dbg_data.user_set.stimulate_current) << ",";
                ss << dbg_data.user_set.stimulate_frequency_hz << ",";
                ss << pre_meas_impendace_value << ",";
                ss << (int32_t)dbg_data.work_calib_data.ref_value << ",";
                ss << MAX30009_STATIC::gain_to_string(dbg_data.user_set.bioz_total_gain) << ",";
                ss << dbg_data.data.Load_real << ",";
                ss << dbg_data.data.Load_imag << ",";
                ss << dbg_data.data.Load_mag << ",";
                ss << dbg_data.data.Load_angle << ",";
                ss << (dbg_data.data.overload ? 1 : 0) << ",";
                ss << (dbg_data.status.DRVN_out_of_range ? 1 : 0) << ",";
                ss << dbg_data.I_ch_data.channel_value << ",";
                ss << dbg_data.Q_ch_data.channel_value << ",";
                ss << dbg_data.I_ch_data.impendance_value << ",";
                ss << dbg_data.Q_ch_data.impendance_value  << ",";
                ss << dbg_data.work_calib_data.I_cal_in_ADC  << ",";
                ss << dbg_data.work_calib_data.Q_cal_quad_ADC  << "\n";
                //ss << MAX30009_base_cal_table::get_calibration_json_data(dbg_data.work_calib_data)  << "\n";;
                autotest.csv_file << ss.str();
            }
        }
        return;
    }

    if (autotest.curr_index<autotest.currs_list.size())
    {
        std::string current_str=autotest.currs_list.at(autotest.curr_index);
        uint32_t stimulate_freq=autotest.freqs_list.at(autotest.freq_index);

        if (autotest.freq_index<autotest.freqs_list.size()-1)
        {
            autotest.freq_index++;
        }
        else
        {
            autotest.curr_index++;
            autotest.freq_index=0;
        }

        std::string out_json = "{ \"type\": \"settings\" ,\"stimulate_current\":\"" + current_str + "\", \"measure_frequency\": 2000, \"stimulate_frequency\":" + std::to_string(stimulate_freq) + ",\"measure_enable\": true}";
        process_JSON_line(out_json.c_str());

        autotest.wait_stabile_data=7000;
    }
    else
    {
        autotest.need_do=false;
        if ( autotest.csv_file.is_open())
        {
            autotest.csv_file.close();
            std::cout << "AUTOTEST FINISHED. File saved." << std::endl;
        }
    }

}
