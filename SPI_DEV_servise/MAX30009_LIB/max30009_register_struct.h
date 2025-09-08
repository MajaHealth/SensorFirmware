#ifndef MAX30009_REGISTER_STRUCT_H
#define MAX30009_REGISTER_STRUCT_H

#include "stdint.h"

#pragma pack(push, 1)


typedef enum MAX30009_REGISTER_ADDRESS_ENUM
{
    MAX30009_ADDRESS_STATUS_1 = 0x00,
    MAX30009_ADDRESS_STATUS_2 = 0x01,

    //FIFO
    MAX30009_ADDRESS_FIFO_WRITE_POINTER = 0x08,
    MAX30009_ADDRESS_FIFO_READ_POINTER = 0x09,
    MAX30009_ADDRESS_FIFO_COUNTER_1 = 0x0A,
    MAX30009_ADDRESS_FIFO_COUNTER_2 = 0x0B,
    MAX30009_ADDRESS_FIFO_DATA_REGISTER = 0x0C,
    MAX30009_ADDRESS_FIFO_CONFIGURATION_1 = 0x0D,
    MAX30009_ADDRESS_FIFO_CONFIGURATION_2 = 0x0E,

    //SYSTEM CONTROL
    MAX30009_ADDRESS_SYSTEM_SYNC = 0x10,
    MAX30009_ADDRESS_SYSTEM_CONFIGURATION = 0x11,
    MAX30009_ADDRESS_PIN_FUNCTIONAL_CONFIGURATION = 0x12,
    MAX30009_ADDRESS_OUTPUT_PIN_CONFIGURATION = 0x13,
    MAX30009_ADDRESS_I2C_BROADCAST = 0x14,

    //PLL
    MAX30009_ADDRESS_PLL_CONFIGURATION_1 = 0x17,
    MAX30009_ADDRESS_PLL_CONFIGURATION_2 = 0x18,
    MAX30009_ADDRESS_PLL_CONFIGURATION_3 = 0x19,
    MAX30009_ADDRESS_PLL_CONFIGURATION_4 = 0x1A,

    //BIOZ SETUP
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_1 = 0x20,
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_2 = 0x21,
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_3 = 0x22,
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_4 = 0x23,
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_5 = 0x24,
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_6 = 0x25,
    MAX30009_ADDRESS_BIOZ_LOW_THRESHOLD = 0x26,
    MAX30009_ADDRESS_BIOZ_HIGH_THRESHOLD = 0x27,
    MAX30009_ADDRESS_BIOZ_CONFIGURATION_7 = 0x28,

    //BIOZ CALIBRATION(MUX)
    MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1 = 0x41,
    MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_2 = 0x42,
    MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3 = 0x43,
    MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_4 = 0x44,

    //DC LEADS SETUP
    MAX30009_ADDRESS_DC_LEADS_CONFIGURATION = 0x50,
    MAX30009_ADDRESS_DC_LEAD_DETECT_THRESHOLD = 0x51,

    //LEAD BIAS
    MAX30009_ADDRESS_LEAD_BIAS_CONFIGURATION = 0x58,

    //INTERRUPT ENABLES
    MAX30009_ADDRESS_INTERRUPT_ENABLE_1 = 0x80,
    MAX30009_ADDRESS_INTERRUPT_ENABLE_2 = 0x81,

    //PART ID
    MAX30009_ADDRESS_PART_ID = 0xFF,
}MAX30009_REGISTER_ADDRESS_ENUM_TYPE;


typedef volatile struct MAX30009_REGISTERS_STATUS_1 // 0x00
{
    uint8_t    PWR_RDY                 :1; //0
    uint8_t    PHASE_LOCK              :1; //1
    uint8_t    PHASE_UNLOCK            :1; //2
    uint8_t    FREQ_LOCK               :1; //3
    uint8_t    FREQ_UNLOCK             :1; //4
    uint8_t    FIFO_DATA_RDY           :1; //5
    uint8_t    X_NOSET                 :1; //6
    uint8_t    A_FULL                  :1; //7
} MAX30009_REGISTERS_STATUS_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_STATUS_2 // 0x01
{
    uint8_t    DC_LOFF_NL              :1; //0
    uint8_t    DC_LOFF_NH              :1; //1
    uint8_t    DC_LOFF_PL              :1; //2
    uint8_t    DC_LOFF_PH              :1; //3
    uint8_t    DRV_OOR                 :1; //4
    uint8_t    BIOZ_UNDR               :1; //5
    uint8_t    BIOZ_OVER               :1; //6
    uint8_t    LON                     :1; //7
} MAX30009_REGISTERS_STATUS_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_FIFO_WRITE_POINTER  //0x08
{
    uint8_t    FIFO_WR_PTR             :8; //0-7
} MAX30009_REGISTERS_FIFO_WRITE_POINTER_TYPE;

typedef volatile struct MAX30009_REGISTERS_FIFO_READ_POINTER  //0x09
{
    uint8_t    FIFO_RD_PTR             :8; //0-7
} MAX30009_REGISTERS_FIFO_READ_POINTER_TYPE;


typedef volatile struct MAX30009_REGISTERS_FIFO_COUNTER_1  //0x0A
{
    uint8_t    OVF_COUNTER             :7; //0-6
    uint8_t    FIFO_DATA_COUNT_HB      :1; //7
} MAX30009_REGISTERS_FIFO_COUNTER_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_FIFO_COUNTER_2  //0x0B
{
    uint8_t    FIFO_DATA_COUNT_LB      :8; //0-7
} MAX30009_REGISTERS_FIFO_COUNTER_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_FIFO_DATA_REGISTER  //0x0C
{
    uint8_t    FIFO_DATA               :8; //0-7
} MAX30009_REGISTERS_FIFO_DATA_REGISTER_TYPE;

typedef volatile struct MAX30009_REGISTERS_FIFO_CONFIGURATION_1  //0x0D
{
    uint8_t    FIFO_A_FULL             :8; //0-7
} MAX30009_REGISTERS_FIFO_CONFIGURATION_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_FIFO_CONFIGURATION_2  //0x0E
{
    uint8_t    X_NOSET3                :1; //0
    uint8_t    FIFO_RO                 :1; //1
    uint8_t    A_FULL_TYPE             :1; //2
    uint8_t    FIFO_STAT_CLR           :1; //3
    uint8_t    FLUSH_FIFO              :1; //4
    uint8_t    FIFO_MARK               :1; //5
    uint8_t    X_NOSET2                :1; //6
    uint8_t    X_NOSET1                :1; //7
} MAX30009_REGISTERS_FIFO_CONFIGURATION_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_SYSTEM_SYNC  //0x10
{
    uint8_t    X_NOSET                 :7; //0-6
    uint8_t    TIMING_SYS_RESET        :1; //7
} MAX30009_REGISTERS_SYSTEM_SYNC_TYPE;

typedef volatile struct MAX30009_REGISTERS_SYSTEM_CONFIGURATION  //0x11
{
    uint8_t    RESET                   :1; //0
    uint8_t    SHDN                    :1; //1
    uint8_t    X_NOSET                 :4; //2-5
    uint8_t    DISABLE_I2C             :1; //6
    uint8_t    MASTER                  :1; //7
} MAX30009_REGISTERS_SYSTEM_CONFIGURATION_TYPE;

typedef volatile struct MAX30009_REGISTERS_PIN_FUNCTIONAL_CONFIGURATION  //0x12
{
    uint8_t    TRIG_ICFG               :1; //0
    uint8_t    X_NOSET                 :1; //1
    uint8_t    INT_FCFG                :2; //2-3
    uint8_t    X_NOSET2                :4; //4-7
} MAX30009_REGISTERS_PIN_FUNCTIONAL_CONFIGURATION_TYPE;

typedef volatile struct MAX30009_REGISTERS_OUTPUT_PIN_CONFIGURATION  //0x13
{
    uint8_t    TRIG_OCFG               :2; //0-1
    uint8_t    INT_OCFG                :2; //2-3
    uint8_t    X_NOSET2                :4; //4-7
} MAX30009_REGISTERS_OUTPUT_PIN_CONFIGURATION_TYPE;

typedef volatile struct MAX30009_REGISTERS_I2C_BROADCAST_ADDRESS  //0x14
{
    uint8_t    I2C_BCAST_EN            :1; //0
    uint8_t    I2C_BCAST_ADDR          :7; //1-7
} MAX30009_REGISTERS_I2C_BROADCAST_ADDRESS_TYPE;

typedef volatile struct MAX30009_REGISTERS_PLL_CONFIGURATION_1  //0x17
{
    uint8_t    PLL_EN                  :1; //0
    uint8_t    KDIV                    :4; //1-4
    uint8_t    NDIV                    :1; //5
    uint8_t    MDIV_H                  :2; //6-7
} MAX30009_REGISTERS_PLL_CONFIGURATION_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_PLL_CONFIGURATION_2  //0x18
{
    uint8_t    MDIV_L                  :8; //0-7
} MAX30009_REGISTERS_PLL_CONFIGURATION_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_PLL_CONFIGURATION_3  //0x19
{
    uint8_t    PLL_LOCK_WNDW           :1; //0
    uint8_t    X_NOSET                 :7; //1-7
} MAX30009_REGISTERS_PLL_CONFIGURATION_3_TYPE;

typedef volatile struct MAX30009_REGISTERS_PLL_CONFIGURATION_4  //0x1A
{
    uint8_t    CLK_FINE_TUNE           :5; //0-4
    uint8_t    CLK_FREQ_SEL            :1; //5
    uint8_t    REF_CLK_SEL             :1; //6
    uint8_t    X_NOSET                 :1; //7
} MAX30009_REGISTERS_PLL_CONFIGURATION_4_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_1  //0x20
{
    uint8_t    BIOZ_I_EN               :1; //0
    uint8_t    BIOZ_Q_EN               :1; //1
    uint8_t    BIOZ_BG_EN              :1; //2
    uint8_t    BIOZ_ADC_OSR            :3; //3-5
    uint8_t    BIOZ_DAC_OSR            :2; //6-7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_2  //0x21
{
    uint8_t    EN_BIOZ_THRESH          :1; //0
    uint8_t    BIOZ_CMP                :2; //1-2
    uint8_t    BIOZ_DLPF               :3; //3-5
    uint8_t    BIOZ_DHPF               :2; //6-7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_3  //0x22
{
    uint8_t    BIOZ_DRV_MODE           :2; //0-1
    uint8_t    BIOZ_IDRV_RGE           :2; //2-3
    uint8_t    BIOZ_VDRV_MAG           :2; //4-5
    uint8_t    LOFF_RAPID              :1; //6
    uint8_t    BIOZ_EXT_RES            :1; //7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_3_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_4  //0x23
{
    uint8_t    BIOZ_FAST_START_EN      :1; //0
    uint8_t    BIOZ_FAST_MANUAL        :1; //1
    uint8_t    X_NOSET                 :6; //2-7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_4_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_5  //0x24
{
    uint8_t    BIOZ_GAIN               :2; //0-1
    uint8_t    BIOZ_DM_DIS             :1; //2
    uint8_t    BIOZ_INA_MODE           :1; //3
    uint8_t    BIOZ_AHPF               :4; //4-7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_5_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_6  //0x25
{
    uint8_t    BIOZ_AMP_BW             :2; //0-1
    uint8_t    BIOZ_AMP_RGE            :2; //2-3
    uint8_t    BIOZ_DAC_RESET          :1; //4
    uint8_t    BIOZ_DRV_RESET          :1; //5
    uint8_t    BIOZ_DC_RESTORE         :1; //6
    uint8_t    BIOZ_EXT_CAP            :1; //7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_6_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_LOW_THRESHOLD  //0x26
{
    uint8_t    BIOZ_LO_THRESH          :8; //0-7
} MAX30009_REGISTERS_BIOZ_LOW_THRESHOLD_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_HIGH_THRESHOLD  //0x27
{
    uint8_t    BIOZ_HI_THRESH          :8; //0-7
} MAX30009_REGISTERS_BIOZ_HIGH_THRESHOLD_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_CONFIGURATION_7  //0x28
{
    uint8_t   BIOZ_CH_FSEL             :1; //0
    uint8_t   BIOZ_INA_CHOP_EN         :1; //1
    uint8_t   BIOZ_I_CLK_PHASE         :1; //2
    uint8_t   BIOZ_Q_CLK_PHASE         :1; //3
    uint8_t   BIOZ_STBYON              :1; //4
    uint8_t   X_NOSET                  :3; //5-7
} MAX30009_REGISTERS_BIOZ_CONFIGURATION_7_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_1  //0x41
{
    uint8_t   CAL_EN                   :1; //0
    uint8_t   MUX_EN                   :1; //1
    uint8_t   CONNECT_CAL_ONLY         :1; //2
    uint8_t   X_NOSET                  :2; //3-4
    uint8_t   BMUX_BIST_EN             :1; //5
    uint8_t   BMUX_RSEL                :2; //6-7
} MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_2  //0x42
{
    uint8_t   EN_INT_INLOAD            :1; //0
    uint8_t   EN_EXT_INLOAD            :1; //1
    uint8_t   X_NOSET                  :3; //2-4
    uint8_t   GSR_LOAD_EN              :1; //5
    uint8_t   BMUX_GSR_RSEL            :2; //6-7
} MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_3  //0x43
{
    uint8_t   DRVN_ASSIGN              :2; //0-1
    uint8_t   DRVP_ASSIGN              :2; //2-3
    uint8_t   BIN_ASSIGN               :2; //4-5
    uint8_t   BIP_ASSIGN               :2; //6-7
} MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_3_TYPE;

typedef volatile struct MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_4  //0x44
{
    uint8_t   BIST_R_ERR               :8; //0-7
} MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_4_TYPE;

typedef volatile struct MAX30009_REGISTERS_DC_LEADS_CONFIGURATION  //0x50
{
    uint8_t     LOFF_IMAG              :3; //0-2
    uint8_t     LOFF_IPOL              :1; //3
    uint8_t     EN_DRV_OOR             :1; //4
    uint8_t     EN_EXT_LOFF            :1; //5
    uint8_t     EN_LOFF_DET            :1; //6
    uint8_t     EN_LON_DET             :1; //7
} MAX30009_REGISTERS_DC_LEADS_CONFIGURATION_TYPE;

typedef volatile struct MAX30009_REGISTERS_DC_LEAD_DETECT_THRESHOLD  //0x51
{
    uint8_t   LOFF_THRESH              :4; //0-4
    uint8_t   X_NOSET                  :4; //5-7
} MAX30009_REGISTERS_DC_LEAD_DETECT_THRESHOLD_TYPE;

typedef volatile struct MAX30009_REGISTERS_LEAD_BIAS_CONFIGURATION  //0x51
{
    uint8_t   EN_RBIAS_BIN             :1; //0
    uint8_t   EN_RBIAS_BIP             :1; //2
    uint8_t   RBIAS_VALUE              :2; //3-4
    uint8_t   X_NOSET                  :4; //5-7
} MAX30009_REGISTERS_LEAD_BIAS_CONFIGURATION_TYPE;

typedef volatile struct MAX30009_REGISTERS_INTERRUPT_ENABLE_1  //0x80
{
    uint8_t   X_NOSET1                 :1; //0
    uint8_t   PHASE_LOCK_EN            :1; //1
    uint8_t   PHASE_UNLOCK_EN          :1; //2
    uint8_t   FREQ_LOCK_EN             :1; //3
    uint8_t   FREQ_UNLOCK_EN           :1; //4
    uint8_t   FIFO_DATA_RDY_EN         :1; //5
    uint8_t   X_NOSET2                 :1; //6
    uint8_t   A_FULL_EN                :1; //7
} MAX30009_REGISTERS_INTERRUPT_ENABLE_1_TYPE;

typedef volatile struct MAX30009_REGISTERS_INTERRUPT_ENABLE_2  //0x81
{
    uint8_t   DC_LOFF_NL_EN            :1; //0
    uint8_t   DC_LOFF_NH_EN            :1; //1
    uint8_t   DC_LOFF_PL_EN            :1; //2
    uint8_t   DC_LOFF_PH_EN            :1; //3
    uint8_t   DRV_OOR_EN               :1; //4
    uint8_t   BIOZ_UNDR_EN             :1; //5
    uint8_t   BIOZ_OVER_EN             :1; //6
    uint8_t   LON_EN                   :1; //7
} MAX30009_REGISTERS_INTERRUPT_ENABLE_2_TYPE;

typedef volatile struct MAX30009_REGISTERS_PART_ID  //0xFF
{
    uint8_t   PART_ID                  :8; //0-7
} MAX30009_REGISTERS_PART_ID_TYPE;

typedef volatile struct MAX30009_REGISTERS
{
    //STATUS
    MAX30009_REGISTERS_STATUS_1_TYPE STATUS_1; //0x00
    MAX30009_REGISTERS_STATUS_2_TYPE STATUS_2; //0x01

    //FIFO
    MAX30009_REGISTERS_FIFO_WRITE_POINTER_TYPE FIFO_WRITE_POINTER;//0x08
    MAX30009_REGISTERS_FIFO_READ_POINTER_TYPE FIFO_READ_POINTER;  //0x09
    MAX30009_REGISTERS_FIFO_COUNTER_1_TYPE FIFO_COUNTER_1; //0x0A
    MAX30009_REGISTERS_FIFO_COUNTER_2_TYPE FIFO_COUNTER_2; //0x0B
    MAX30009_REGISTERS_FIFO_DATA_REGISTER_TYPE FIFO_DATA_REGISTER; //0x0C
    MAX30009_REGISTERS_FIFO_CONFIGURATION_1_TYPE FIFO_CONFIGURATION_1; //0x0D
    MAX30009_REGISTERS_FIFO_CONFIGURATION_2_TYPE FIFO_CONFIGURATION_2; //0x0E

    //SYSTEM CONTROL
    MAX30009_REGISTERS_SYSTEM_SYNC_TYPE    SYSTEM_SYNC; //0x10
    MAX30009_REGISTERS_SYSTEM_CONFIGURATION_TYPE SYSTEM_CONFIGURATION; //0x11
    MAX30009_REGISTERS_PIN_FUNCTIONAL_CONFIGURATION_TYPE PIN_FUNCTIONAL_CONFIGURATION; //0x12
    MAX30009_REGISTERS_OUTPUT_PIN_CONFIGURATION_TYPE OUTPUT_PIN_CONFIGURATION; //0x13
    MAX30009_REGISTERS_I2C_BROADCAST_ADDRESS_TYPE I2C_BROADCAST_ADDRESS; //0x14

    //PLL
    MAX30009_REGISTERS_PLL_CONFIGURATION_1_TYPE PLL_CONFIGURATION_1; //0x17
    MAX30009_REGISTERS_PLL_CONFIGURATION_2_TYPE PLL_CONFIGURATION_2; //0x18
    MAX30009_REGISTERS_PLL_CONFIGURATION_3_TYPE PLL_CONFIGURATION_3; //0x19
    MAX30009_REGISTERS_PLL_CONFIGURATION_4_TYPE PLL_CONFIGURATION_4; //0x1A

    //BIOZ SETUP
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_1_TYPE BIOZ_CONFIGURATION_1;  //0x20
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_2_TYPE BIOZ_CONFIGURATION_2;  //0x21
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_3_TYPE BIOZ_CONFIGURATION_3;  //0x22
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_4_TYPE BIOZ_CONFIGURATION_4;  //0x23
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_5_TYPE BIOZ_CONFIGURATION_5;  //0x24
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_6_TYPE BIOZ_CONFIGURATION_6;  //0x25
    MAX30009_REGISTERS_BIOZ_LOW_THRESHOLD_TYPE BIOZ_LOW_THRESHOLD;      //0x26
    MAX30009_REGISTERS_BIOZ_HIGH_THRESHOLD_TYPE BIOZ_HIGH_THRESHOLD;    //0x27
    MAX30009_REGISTERS_BIOZ_CONFIGURATION_7_TYPE BIOZ_CONFIGURATION_7;  //0x28

    //BIOZ CALIBRATION(MUX)
    MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_1_TYPE BIOZ_MUX_CONFIGURATION_1; //0x41
    MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_2_TYPE BIOZ_MUX_CONFIGURATION_2; //0x42
    MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_3_TYPE BIOZ_MUX_CONFIGURATION_3; //0x43
    MAX30009_REGISTERS_BIOZ_MUX_CONFIGURATION_4_TYPE BIOZ_MUX_CONFIGURATION_4; //0x44

    //DC LEADS SETUP
    MAX30009_REGISTERS_DC_LEADS_CONFIGURATION_TYPE DC_LEADS_CONFIGURATION;      //0x50
    MAX30009_REGISTERS_DC_LEAD_DETECT_THRESHOLD_TYPE DC_LEAD_DETECT_THRESHOLD;  //0x51

    //LEAD BIAS
    MAX30009_REGISTERS_LEAD_BIAS_CONFIGURATION_TYPE LEAD_BIAS_CONFIGURATION; //0x58

    //INTERRUPT ENABLES
    MAX30009_REGISTERS_INTERRUPT_ENABLE_1_TYPE INTERRUPT_ENABLE_1; //0x80
    MAX30009_REGISTERS_INTERRUPT_ENABLE_2_TYPE INTERRUPT_ENABLE_2; //0x81

    //PART ID
    MAX30009_REGISTERS_PART_ID_TYPE PART_ID; // 0xFF

} MAX30009_REGISTERS_TYPE;

#pragma pack(pop)

#endif // MAX30009_REGISTER_STRUCT_H
