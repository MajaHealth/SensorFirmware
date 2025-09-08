#ifndef MAX30009_DATA_STRUCT_H
#define MAX30009_DATA_STRUCT_H

const uint8_t MAX30009_LAST_REGISTER_ADDRESS=0xFF;
const uint8_t MAX30009_REGISTER_READ_DIRECT= 0x80;
const uint8_t MAX30009_REGISTER_WRITE_DIRECT=0x00;
const uint8_t MAX30009_DUMMY_BYTE=0xFF;

const uint32_t MAX30009_REGISTER_PACKET_SIZE=3;
const uint32_t MAX30009_TRY_READ_COUNT=30;
const uint32_t MAX30009_TRY_WRITE_COUNT=30;

const int32_t MAX30009_PART_ONE_DRIVE_FREQ=546680;   // in 1/10 Hertz
const int32_t  MAX30009_MIN_DRIVE_FREQ=160;     // in 1/10 Hertz
const int32_t MAX30009_MAX_DRIVE_FREQ=8000000;  // in 1/10 Hertz

const int32_t MAX30009_MIN_PLL_FREQ=140000000;// in 1/10 Hertz
const int32_t MAX30009_MAX_PLL_FREQ=280000000;// in 1/10 Hertz

const int32_t MAX30009_MIN_BIOZ_SYNTH_FREQ=40960;// in 1/10 Hertz
const int32_t MAX30009_MAX_BIOZ_SYNTH_FREQ=280000000;// 1/10 in Hertz

const int32_t MAX30009_MIN_BIOZ_ADCCLK_FREQ=160000;// in 1/10 Hertz
const int32_t MAX30009_MAX_BIOZ_ADCCLK_FREQ=363750;// in  1/10 Hertz

const int32_t MAX30009_NDIV_SIZE=2;
const int32_t MAX30009_KDIV_SIZE=16;
const int32_t MAX30009_ADC_OSR_SIZE=8;
const int32_t MAX30009_DAC_OSR_SIZE=4;

const int32_t MAX30009_FIND_CLK_SOLUTION_TRY_COUNT=300;

const uint32_t MAX30009_NDIV_divider[MAX30009_NDIV_SIZE]={512,1024};
const uint32_t MAX30009_KDIV_divider[MAX30009_KDIV_SIZE ]={1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,8192,8192};
const uint32_t MAX30009_ADC_OSR_divider[MAX30009_ADC_OSR_SIZE]={8,16,32,64,128,256,512,1024};
const uint32_t MAX30009_DAC_OSR_divider[MAX30009_DAC_OSR_SIZE]={32,64,128,256};


const int32_t MAX30009_MIN_FREQ_FOR_128uA=5120;    // in 1/10 Hertz
const int32_t MAX30009_MIN_FREQ_FOR_256uA=20480;  // in 1/10 Hertz
const int32_t MAX30009_MIN_FREQ_FOR_640uA=81920;  // in 1/10 Hertz
const int32_t MAX30009_MIN_FREQ_FOR_1_28mA=163840;  // in 1/10 Hertz

static const int32_t MAX30009_MIN_ADC_VALUE=-500000;
static const int32_t MAX30009_MAX_ADC_VALUE=500000;
#define MAX30009_FIND_LAV_REQ_SIZE 10

//#define MAX30009_FIFO_REQUEST_ITEMS 10
//#define MAX30009_FIFO_DATA_BYTES_SIZE 3
//#define MAX30009_FIFO_REQUEST_SIZE (MAX30009_FIFO_REQUEST_ITEMS*MAX30009_FIFO_DATA_BYTES_SIZE+2)

const uint32_t MAX30009_I_CHANNEL_ID=0x100000;
const uint32_t MAX30009_Q_CHANNEL_ID=0x200000;
const uint32_t MAX30009_MARKER_ID=0xFFFFFE;

//voltage values arrays in uV
const uint32_t drv_voltage_RMS_arr[4]={35400,70700,177000,354000};
const uint32_t drv_voltage_peak_arr[4]={50000,100000,250000,500000};

//Current values arrays in nA
const uint32_t drv_current_RMS_arr[4][4]={
    {16,32,80,160},
    {320,640,1600,3200},
    {6400,12800,32000,64000,},
    {128000,256000,640000,1280000},
    };
const uint32_t drv_current_peak_arr[4][4]={
    {23,45,113,226},
    {452,905,2262,4525},
    {9050,18100,45250,90500,},
    {181000,362000,905000,1810000},
    };

//input HP filter values arrays in 1/10 Hz
const uint32_t inp_HP_filter_value_arr[16]={1000,2000,5000,10000,20000,50000,100000,10,0,0,0,0,0,0,0,0};

//total BIOZ gain values arrays in 1/10 Hz
const uint32_t total_gain_value_arr[4]={1,2,5,10};


typedef struct MAX30009_STATUS_STRUCT
{
    bool a_full_flag;
    bool FIFO_data_ready;
    bool frequency_unlock;
    bool frequency_lock;
    bool phase_unlock;
    bool phase_lock;
    bool power_ready;

    bool LON_BIOZ_active;
    bool BIOZ_over_level;
    bool BIOZ_under_level;
    bool DRVN_out_of_range;
    bool DC_LOFF_BIP_overlimit;
    bool DC_LOFF_BIP_underlimit;
    bool DC_LOFF_BIN_overlimit;
    bool DC_LOFF_BIN_underlimit;

}MAX30009_STATUS_STRUCT_TYPE;

typedef struct MAX30009_FIND_CLOCKS_STRUCT
{
    uint32_t solution_count;

    uint32_t REF_CLK;
    uint32_t PLL_CLK;

    uint32_t BIOZ_SYNTH_CLK;
    uint32_t set_drive_freq;
    uint32_t drive_freq;
    uint32_t drive_freq_error;

    uint32_t BIOZ_ADC_CLK;
    uint32_t desire_ADC_sample_rate;
    uint32_t ADC_sample_rate;

    uint16_t MDIV;
    uint8_t NDIV;
    uint8_t KDIV;
    uint8_t BIOZ_DAC_OSR;
    uint8_t BIOZ_ADC_OSR;


}MAX30009_FIND_CLOCKS_STRUCT_TYPE;

typedef enum MAX30009_FIFO_DATA_SOURCE
{
    MAX30009_I_CHANNEL,
    MAX30009_Q_CHANNEL,
    MAX30009_MARKER,
    MAX30009_ERROR_DATA_SOURCE,
}MAX30009_FIFI_DATA_SOURCE_TYPE;

typedef struct MAX30009_FIFO_DATA
{
    int32_t channel_value;
    int32_t impendance_value;
    int32_t voltage_value;
    MAX30009_FIFI_DATA_SOURCE_TYPE data_source;

}MAX30009_FIFO_DATA_TYPE;


typedef struct MAX30009_FIFO_DATA_CALIB
{
    double I_load;
    double Q_load;
    double I_cal_real;
    double I_cal_imag;
    double Q_cal_real;
    double Q_cal_imag;

    double Load_real;
    double Load_imag;
    double Load_mag;
    double Load_angle;

    bool overload;

}MAX30009_FIFO_DATA_CALIB_TYPE;


typedef struct MAX30009_ALL_CLOCKS_FREQ
{
    uint32_t REF_CLK;
    uint32_t PLL_CLK;
    uint32_t BIOZ_ADC_CLK;
    uint32_t BIOZ_SYNTH_CLK;
    uint32_t BIOZ_ADC_SAMPLE_RATE;
    uint32_t BIOZ_DRIVE_FREQ;

    uint16_t MDIV_VALUE;
    uint16_t NDIV_VALUE;
    uint16_t KDIV_VALUE;
    uint16_t BIOZ_ADC_OSR_VALUE;
    uint16_t BIOZ_DAC_OSR_VALUE;

    bool PLL_enable;


}MAX30009_ALL_CLOCKS_FREQ_TYPE;

const uint8_t MAX30009_REFCLK_SOURCE_ENUM_VALUE_LIST[]={0,1,2,3};
typedef enum MAX30009_REFCLK_SOURCE_ENUM
{
    MAX30009_REFCLK_SRC_INT_32000=0,
    MAX30009_REFCLK_SRC_INT_32768=1,
    MAX30009_REFCLK_SRC_EXT_32000=2,
    MAX30009_REFCLK_SRC_EXT_32768=3,
}MAX30009_REFCLK_SOURCE_ENUM_TYPE;

const uint8_t MAX30009_CURRENT_AMP_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03,0x10,0x11,0x12,0x13,0x20,0x21,0x22,0x23,0x30,0x31,0x32,0x33};
typedef enum MAX30009_CURRENT_AMP_ENUM
{
    MAX30009_CURRENT_AMP_16nA=  0x00,
    MAX30009_CURRENT_AMP_32nA=  0x01,
    MAX30009_CURRENT_AMP_80nA=  0x02,
    MAX30009_CURRENT_AMP_160nA= 0x03,
    MAX30009_CURRENT_AMP_320nA= 0x10,
    MAX30009_CURRENT_AMP_640nA= 0x11,
    MAX30009_CURRENT_AMP_1_6uA= 0x12,
    MAX30009_CURRENT_AMP_3_2uA= 0x13,
    MAX30009_CURRENT_AMP_6_4uA= 0x20,
    MAX30009_CURRENT_AMP_12_8uA=0x21,
    MAX30009_CURRENT_AMP_32uA=  0x22,
    MAX30009_CURRENT_AMP_64uA=  0x23,
    MAX30009_CURRENT_AMP_128uA= 0x30,
    MAX30009_CURRENT_AMP_256uA= 0x31,
    MAX30009_CURRENT_AMP_640uA= 0x32,
    MAX30009_CURRENT_AMP_1_28mA=0x33,
}MAX30009_CURRENT_AMP_ENUM_TYPE;

const uint8_t MAX30009_VOLTAGE_AMP_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03};
typedef enum MAX30009_VOLTAGE_AMP_ENUM
{
    MAX30009_VOLTAGE_AMP_35_4mV= 0x00,
    MAX30009_VOLTAGE_AMP_70_7mV= 0x01,
    MAX30009_VOLTAGE_AMP_177mV=  0x02,
    MAX30009_VOLTAGE_AMP_354mV=  0x03,
}MAX30009_VOLTAGE_AMP_ENUM_TYPE;

const uint8_t MAX30009_BIOZ_DRV_MODE_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03};
typedef enum MAX30009_BIOZ_DRV_MODE_ENUM
{
    MAX30009_BIOZ_DRV_MODE_CURRENT=     0x00,
    MAX30009_BIOZ_DRV_MODE_VOLTAGE=     0x01,
    MAX30009_BIOZ_DRV_MODE_H_BRIDGE=    0x02,
    MAX30009_BIOZ_DRV_MODE_STANDBY=     0x03,
}MAX30009_BIOZ_DRV_MODE_ENUM_TYPE;

const uint8_t MAX30009_BIOZ_AMPLF_MODE_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03};
typedef enum MAX30009_BIOZ_AMPLF_MODE_ENUM
{
    MAX30009_BIOZ_AMPLF_MODE_LOW=             0x00,
    MAX30009_BIOZ_AMPLF_MODE_MEDIUM_LOW=      0x01,
    MAX30009_BIOZ_AMPLF_MODE_MEDIUM_HIGH=     0x02,
    MAX30009_BIOZ_AMPLF_MODE_HIGH=            0x03,
}MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE;

const uint8_t MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07};
typedef enum MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM
{
    MAX30009_BIOZ_IN_HPFILTER_100Hz=    0x00,
    MAX30009_BIOZ_IN_HPFILTER_200Hz=    0x01,
    MAX30009_BIOZ_IN_HPFILTER_500Hz=    0x02,
    MAX30009_BIOZ_IN_HPFILTER_1000Hz=   0x03,
    MAX30009_BIOZ_IN_HPFILTER_2000Hz=   0x04,
    MAX30009_BIOZ_IN_HPFILTER_5000Hz=   0x05,
    MAX30009_BIOZ_IN_HPFILTER_10000Hz=  0x06,
    MAX30009_BIOZ_IN_HPFILTER_BYPASS=   0x07,
}MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE;

const uint8_t MAX30009_BIOZ_TOTAL_GAIN_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03};
typedef enum MAX30009_BIOZ_TOTAL_GAIN_ENUM
{
    MAX30009_BIOZ_TOTAL_GAIN_1=    0x00,
    MAX30009_BIOZ_TOTAL_GAIN_2=    0x01,
    MAX30009_BIOZ_TOTAL_GAIN_5=    0x02,
    MAX30009_BIOZ_TOTAL_GAIN_10=   0x03,
}MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE;

const uint8_t MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_VALUE_LIST[]={0x00,0x01,0x02};
typedef enum MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM
{
    MAX30009_BIOZ_DHPF_BYPASS=    			0x00,
    MAX30009_BIOZ_DHPF_0_00025xSR_BIOZ=    	0x01,
    MAX30009_BIOZ_DHPF_0_002xSR_BIOZ=    	0x02,
}MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE;

const uint8_t MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03,0x04};
typedef enum MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM
{
    MAX30009_BIOZ_DLPF_BYPASS=    			0x00,
    MAX30009_BIOZ_DLPF_0_005xSR_BIOZ=    	0x01,
    MAX30009_BIOZ_DLPF_0_02xSR_BIOZ=    	0x02,
    MAX30009_BIOZ_DLPF_0_08xSR_BIOZ=    	0x03,
    MAX30009_BIOZ_DLPF_0_25xSR_BIOZ=    	0x04,
}MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE;

typedef enum MAX30009_BIOZ_FAST_START_MODE_ENUM
{
    MAX30009_FAST_START_MODE_OFF=           0x00,
    MAX30009_FAST_START_MODE_ON_200ms=      0x01,
    MAX30009_FAST_START_MODE_ERROR=         0x02,
    MAX30009_FAST_START_MODE_ON_CONSTANT=   0x03,
}MAX30009_BIOZ_FAST_START_MODE_ENUM_TYPE;


typedef struct MAX30009_BIOZ_DATA
{
    MAX30009_BIOZ_DRV_MODE_ENUM drive_mode;
    MAX30009_CURRENT_AMP_ENUM_TYPE current_select;
    uint32_t current_peak;
    uint32_t current_RMS;

    MAX30009_VOLTAGE_AMP_ENUM_TYPE voltage_select;
    uint32_t voltage_peak;
    uint32_t voltage_RMS;

    bool external_capacitor_enable;
    bool external_current_resistor;
    uint32_t  external_current_resistor_value;

    MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE Amplifier_bandwidth;
    MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE Amplifier_range;

    bool bandgap_enable;
    bool I_channel_enable;
    bool Q_channel_enable;

    MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE input_HP_filter_select;
    uint32_t input_HP_filter_frequency;

    bool dc_restore_enable;
    bool INA_low_mode_enable;
    bool INA_chop_enable;
    bool channel_freq_sel_enable;
    bool demodulation_enable;

    MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE total_gain_select;
    uint32_t total_gain_value;

    MAX30009_BIOZ_FAST_START_MODE_ENUM_TYPE fast_start_mode;

    MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE out_DHP_filter;
    MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE out_DLP_filter;

}MAX30009_BIOZ_DATA_TYPE;

const uint8_t MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03};
typedef enum MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM
{
    MAX30009_MUX_BIP_DRVP_ASSIGN_EL1=       0x00,
    MAX30009_MUX_BIP_DRVP_ASSIGN_EL2A=      0x01,
    MAX30009_MUX_BIP_DRVP_ASSIGN_EL2B=      0x02,
    MAX30009_MUX_BIP_DRVP_ASSIGN_NO_USE=    0x03,
}MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM_TYPE;

const uint8_t MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM_VALUE_LIST[]={0x00,0x01,0x02,0x03};
typedef enum MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM
{
    MAX30009_MUX_BIN_DRVN_ASSIGN_EL4=       0x00,
    MAX30009_MUX_BIN_DRVN_ASSIGN_EL3A=      0x01,
    MAX30009_MUX_BIN_DRVN_ASSIGN_EL3B=      0x02,
    MAX30009_MUX_BIN_DRVN_ASSIGN_NO_USE=    0x03,
}MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM_TYPE;


const uint8_t MAX30009_BMUX_RSEL_ENUM_VALUE_LIST[] = {0x00, 0x01, 0x02, 0x03};
typedef enum MAX30009_BMUX_RSEL_ENUM
{
    MAX30009_BMUX_RSEL_5100_OHM = 0x00, // 5100 Ω
    MAX30009_BMUX_RSEL_900_OHM = 0x01,  // 900 Ω
    MAX30009_BMUX_RSEL_600_OHM = 0x02,  // 600 Ω
    MAX30009_BMUX_RSEL_280_OHM = 0x03,  // 280 Ω
} MAX30009_BMUX_RSEL_ENUM_TYPE;

const uint8_t MAX30009_BMUX_GSR_RSEL_ENUM_VALUE_LIST[] = {0x00, 0x01, 0x02, 0x03};
typedef enum MAX30009_BMUX_GSR_RSEL_ENUM
{
    MAX30009_BMUX_GSR_RSEL_25_7_KOHM = 0x00, // 25.7 kΩ
    MAX30009_BMUX_GSR_RSEL_101_KOHM = 0x01,  // 101 kΩ
    MAX30009_BMUX_GSR_RSEL_505_KOHM = 0x02,  // 505 kΩ
    MAX30009_BMUX_GSR_RSEL_1000_KOHM = 0x03, // 1000 kΩ (1 MΩ)
} MAX30009_BMUX_GSR_RSEL_ENUM_TYPE;

typedef struct MAX30009_MUX_DATA
{
    MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM_TYPE DRVP_assign;
    MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM_TYPE BIP_assign;
    MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM_TYPE BIN_assign;
    MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM_TYPE DRVN_assign;

    bool MUX_enable;
    bool CAL_enable;
    bool CAL_ONLY_enable;
}MAX30009_MUX_DATA_TYPE;


//FIFO_______________________________________________________________________________________
typedef enum MAX30009_FIFO_STAT_CLR_ENUM
{
    MAX30009_FIFO_STAT_CLR_ONLY_STATUS1=                0x00,
    MAX30009_FIFO_STAT_CLR_VIA_FIFODATA_AND_STATUS1=    0x01,
}MAX30009_FIFO_STAT_CLR_ENUM_TYPE;

typedef enum MAX30009_FIFO_A_FULL_TYPE_ENUM
{
    MAX30009_FIFO_A_FULL_TYPE_ALWAYS_CHECK=                0x00,
    MAX30009_FIFO_A_FULL_TYPE_CHECK_ONLY_NEW_FULL_CYCLE=   0x01,
}MAX30009_FIFO_A_FULL_TYPE_ENUM_TYPE;

typedef enum MAX30009_FIFO_RO_ENUM
{
    MAX30009_FIFO_RO_STOP_WHEN_FULL=    0x00,
    MAX30009_FIFO_RO_REWRITE_OLD=       0x01,
}MAX30009_FIFO_RO_ENUM_TYPE;

//typedef struct MAX30009_FIFO_DATA
//{
//    uint8_t write_pointer;
//    uint8_t read_pointer;
//    uint16_t data_cont;
//    uint32_t I_CH_value;
//    uint32_t Q_CH_value;
//}MAX30009_FIFO_DATA_TYPE;


//LEAD____________________________________________________________________________________

typedef enum MAX30009_LEAD_RBIAS_VALUE_ENUM
{
    MAX30009_LEAD_RBIAS_50M=    	0x00,
    MAX30009_LEAD_RBIAS_100M=    	0x01,
    MAX30009_LEAD_RBIAS_200M=    	0x02,
    MAX30009_LEAD_RBIAS_NOT_USE=    0x03,
}MAX30009_LEAD_RBIAS_VALUE_ENUM_TYPE;

//CALIBRATE_______________________________________________________________________________________
#define MAX30009_CALIB_DELAY_PERIOD	5

typedef enum MAX30009_CALIB_STATE_ENUM
{
    MAX30009_CALIB_STATE_NODATA,
    MAX30009_CALIB_STATE_NEED_CALIB,

    MAX30009_CALIB_STATE_PRE_START_CALIB,

    MAX30009_CALIB_STATE_START_MEAS_OFFSET,
    MAX30009_CALIB_STATE_MEAS_OFFSET,

    MAX30009_CALIB_STATE_START_MEAS_IN_PHASE,
    MAX30009_CALIB_STATE_MEAS_IN_PHASE,

    MAX30009_CALIB_STATE_START_MEAS_QUAD,
    MAX30009_CALIB_STATE_MEAS_QUAD,


    MAX30009_CALIB_STATE_CALCULATE_COEF,

    MAX30009_CALIB_STATE_READY,
    MAX30009_CALIB_STATE_PRE_READY,
    MAX30009_CALIB_STATE_STOPED,

    MAX30009_CALIB_WAIT_DATA,
    MAX30009_CALIB_IN_DELAY,
}MAX30009_CALIB_STATE_ENUM_TYPE;

typedef enum MAX30009_CALIB_SOURCE_ENUM
{
    MAX30009_CALIB_SOURCE_CALIBPORT,
    MAX30009_CALIB_SOURCE_MAINPORT,

}MAX30009_CALIB_SOURCE_ENUM_TYPE;

typedef struct MAX30009_CALIB_DATA
{
    MAX30009_CALIB_STATE_ENUM_TYPE calib_state;
    MAX30009_CALIB_SOURCE_ENUM_TYPE calib_source;
    uint32_t delay_in_calib;
    bool need_full_FIFO_buffer;

    double ref_value; //in milliohms
    MAX30009_CURRENT_AMP_ENUM_TYPE calibrate_current;
    MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE calibrate_gain;
    uint32_t calibrate_frequency;

    int32_t I_offset;
    int32_t Q_offset;
    int32_t I_cal_in_ADC;
    int32_t Q_cal_in_ADC;
    double I_cal_in;
    double Q_cal_in;
    double I_cal_quad;
    double Q_cal_quad;
    double I_coef;
    double Q_coef;
    double I_phase_coef;
    double Q_phase_coef;

    double I_phase_cos;
    double I_phase_sin;
    double Q_phase_cos;
    double Q_phase_sin;

    uint16_t FIFO_data_count;

}MAX30009_CALIB_DATA_TYPE;



#endif // MAX30009_DATA_STRUCT_H
