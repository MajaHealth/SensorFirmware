/**
    \file ADS1293_register_map.h
    \author VTK TEAM (OK)
    \brief ADS1293 register map file
 */
#ifndef ADS1293_REGISTER_MAP_H
#define ADS1293_REGISTER_MAP_H

namespace ADS1293
{

#pragma pack(push, 1)

/**
    \brief ADS1293 all register list in enum
 */
typedef enum REGISTERS_LIST
{
	//Operation Mode Registers
	RL_CONFIG = 0x00, //Main Configuration ( R/W ) *default: 0x02
	//Input Channel Selection Registers
	RL_FLEX_CH1_CN = 0x01, //Flex Routing Switch Control for Channel 1 ( R/W ) *default: 0x00
	RL_FLEX_CH2_CN = 0x02, //Flex Routing Switch Control for Channel 2 ( R/W ) *default: 0x00
	RL_FLEX_CH3_CN = 0x03, //Flex Routing Switch Control for Channel 3 ( R/W ) *default: 0x00
	RL_FLEX_PACE_CN = 0x04, //Flex Routing Switch Control for Pace Channel ( R/W ) *default: 0x00
	RL_FLEX_VBAT_CN = 0x05, //Flex Routing Switch for Battery Monitoring ( R/W ) *default: 0x00
	//Lead-off Detect Control Registers
	RL_LOD_CN = 0x06, //Lead-Off Detect Control ( R/W ) *default: 0x08
	RL_LOD_EN = 0x07, //Lead-Off Detect Enable ( R/W ) *default: 0x00
	RL_LOD_CURRENT = 0x08, //Lead-Off Detect Current ( R/W ) *default: 0x00
	RL_LOD_AC_CN = 0x09, //AC Lead-Off Detect Control ( R/W ) *default: 0x00
	//Common-Mode Detection and Right-Leg Drive Feedback Control Registers
	RL_CMDET_EN = 0x0A, //Common-Mode Detect Enable ( R/W ) *default: 0x00
	RL_CMDET_CN = 0x0B, //Common-Mode Detect Control ( R/W ) *default: 0x00
	RL_RLD_CN = 0x0C, //Right-Leg Drive Control ( R/W ) *default: 0x00
	//Wilson Control Registers
	RL_WILSON_EN1 = 0x0D, //Wilson Reference Input one Selection ( R/W ) *default: 0x00
	RL_WILSON_EN2 = 0x0E, //Wilson Reference Input two Selection ( R/W ) *default: 0x00
	RL_WILSON_EN3 = 0x0F, //Wilson Reference Input three Selection ( R/W ) *default: 0x00
	RL_WILSON_CN = 0x10, //Wilson Reference Control ( R/W ) *default: 0x00
	//Reference Registers
	RL_REF_CN = 0x11, //Internal Reference Voltage Control ( R/W ) *default: 0x00
	//OSC Control Registers
	RL_OSC_CN = 0x12, //Clock Source and Output Clock Control ( R/W ) *default: 0x00
	//AFE Control Registers
	RL_AFE_RES = 0x13, //Analog Front End Frequency and Resolution ( R/W ) *default: 0x00
	RL_AFE_SHDN_CN = 0x14, //Analog Front End Shutdown Control ( R/W ) *default: 0x00
	RL_AFE_FAULT_CN = 0x15, //Analog Front End Fault Detection Control ( R/W ) *default: 0x00
	RL_RESERVED = 0x16, //— ( R/W ) *default: 0x00
	RL_AFE_PACE_CN = 0x17, //Analog Pace Channel Output Routing Control ( R/W ) *default: 0x01
	//Error Status Registers
	RL_ERROR_LOD = 0x18, //Lead-Off Detect Error Status ( RO ) *default: —
	RL_ERROR_STATUS = 0x19, //Other Error Status ( RO ) *default: —
	RL_ERROR_RANGE1 = 0x1A, //Channel 1 AFE Out-of-Range Status ( RO ) *default: —
	RL_ERROR_RANGE2 = 0x1B, //Channel 2 AFE Out-of-Range Status ( RO ) *default: —
	RL_ERROR_RANGE3 = 0x1C, //Channel 3 AFE Out-of-Range Status ( RO ) *default: —
	RL_ERROR_SYNC = 0x1D, //Synchronization Error ( RO ) *default: —
	RL_ERROR_MISC = 0x1E, //Miscellaneous Errors ( RO ) *default: 0x00
	//Digital Registers
	RL_DIGO_STRENGTH = 0x1F, //Digital Output Drive Strength ( R/W ) *default: 0x03
	RL_R2_RATE = 0x21, //R2 Decimation Rate ( R/W ) *default: 0x08
	RL_R3_RATE_CH1 = 0x22, //R3 Decimation Rate for Channel 1 ( R/W ) *default: 0x80
	RL_R3_RATE_CH2 = 0x23, //R3 Decimation Rate for Channel 2 ( R/W ) *default: 0x80
	RL_R3_RATE_CH3 = 0x24, //R3 Decimation Rate for Channel 3 ( R/W ) *default: 0x80
	RL_R1_RATE = 0x25, //R1 Decimation Rate ( R/W ) *default: 0x00
	RL_DIS_EFILTER = 0x26, //ECG Filter Disable ( R/W ) *default: 0x00
	RL_DRDYB_SRC = 0x27, //Data Ready Pin Source ( R/W ) *default: 0x00
	RL_SYNCB_CN = 0x28, //SYNCB In/Out Pin Control ( R/W ) *default: 0x40
	RL_MASK_DRDYB = 0x29, //Optional Mask Control for DRDYB Output ( R/W ) *default: 0x00
	RL_MASK_ERR = 0x2A, //Mask Error on ALARMB Pin ( R/W ) *default: 0x00
	RL_Reserved = 0x2B, //— ( — ) *default: 0x00
	RL_Reserved1 = 0x2C, //— ( — ) *default: 0x00
	RL_Reserved2 = 0x2D, //— ( — ) *default: 0x09
	RL_ALARM_FILTER = 0x2E, //Digital Filter for Analog Alarm Signals ( R/W ) *default: 0x33
	RL_CH_CNFG = 0x2F, //Configure Channel for Loop Read Back Mode ( R/W ) *default: 0x00
	//Pace and ECG Data Read Back Registers
	RL_DATA_STATUS = 0x30, //ECG and Pace Data Ready Status ( RO ) *default: —
	RL_DATA_CH1_PACE1 = 0x31, //Channel 1 Pace Data ( RO ) *default: —
	RL_DATA_CH1_PACE2 = 0x32, //Channel 1 Pace Data ( RO ) *default: —
	RL_DATA_CH2_PACE1 = 0x33, //Channel 2 Pace Data ( RO ) *default: —
	RL_DATA_CH2_PACE2 = 0x34, //Channel 2 Pace Data ( RO ) *default: —
	RL_DATA_CH3_PACE1 = 0x35, //Channel 3 Pace Data ( RO ) *default: —
	RL_DATA_CH3_PACE2 = 0x36, //Channel 3 Pace Data ( RO ) *default: —
	RL_DATA_CH1_ECG1 = 0x37, //Channel 1 ECG Data ( RO ) *default: —
	RL_DATA_CH1_ECG2 = 0x38, //Channel 1 ECG Data ( RO ) *default: —
	RL_DATA_CH1_ECG3 = 0x39, //Channel 1 ECG Data ( RO ) *default: —
	RL_DATA_CH2_ECG1 = 0x3A, //Channel 2 ECG Data ( RO ) *default: —
	RL_DATA_CH2_ECG2 = 0x3B, //Channel 2 ECG Data ( RO ) *default: —
	RL_DATA_CH2_ECG3 = 0x3C, //Channel 2 ECG Data ( RO ) *default: —
	RL_DATA_CH3_ECG1 = 0x3D, //Channel 3 ECG Data ( RO ) *default: —
	RL_DATA_CH3_ECG2 = 0x3E, //Channel 3 ECG Data ( RO ) *default: —
	RL_DATA_CH3_ECG3 = 0x3F, //Channel 3 ECG Data ( RO ) *default: —
	RL_REVID = 0x40, //Revision ID ( RO ) *default: 0x01
	RL_DATA_LOOP = 0x50, //Loop Read-Back Address ( RO ) *default: —

}REGISTERS_LIST_TDE;


//Operation Mode Registers________________________________________________________

/**
    \brief Main Configuration ( R/W ) *default: 0x02
 */
typedef volatile struct RG_CONFIG // 0x00
{
    bool START_CON					:1; //0		Start conversion
    bool STANDBY					:1; //1		Standby mode
    bool PWR_DOWN					:1; //2		Power-down mode
    uint8_t	NOSET					:5; //3-7 no set
} RG_CONFIG_TDS;


//Input Channel Selection Registers_______________________________________________

typedef enum TEST_SIGNAL_SELECTOR
{
	TSS_DISCONECT=0b00, //Test signal disconnected and CH1 inputs determined by POS1 and NEG1 (default)
	TSS_TO_POSITIVE_TEST_SIGNAL=0b01, //Connect channel to positive test signal
	TSS_TO_NEGATIVE_TEST_SIGNAL=0b10, //Connect channel to negative test signal
	TSS_TO_ZERO_TEST_SIGNAL=0b11, //Connect channel to zero test signal
}TEST_SIGNAL_SELECTOR_TDE;

typedef enum INPUT_SELECTOR
{
	IS_DISCONECT=0b000, //Terminal is disconnected
	IS_INPUT_1=0b001, //Terminal connected to input IN1
	IS_INPUT_2=0b010, //Terminal connected to input IN2
	IS_INPUT_3=0b011, //Terminal connected to input IN3
	IS_INPUT_4=0b100, //Terminal connected to input IN4
	IS_INPUT_5=0b101, //Terminal connected to input IN5
	IS_INPUT_6=0b110, //Terminal connected to input IN6

}INPUT_SELECTOR_TDE;

/**
    \brief  Flex Routing Switch Control for Channel ( R/W ) *default: 0x00
 */
typedef volatile struct RG_FLEX_CH_CN // 0x01-0x04
{
	INPUT_SELECTOR_TDE NEG			:3; //0-2	Negative terminal of channel
	INPUT_SELECTOR_TDE POS			:3; //3-5	Positive terminal of channel
	TEST_SIGNAL_SELECTOR_TDE TST	:2; //6-7	Positive terminal of channel
} RG_FLEX_CH_CN_TDS;

/**
    \brief  Flex Routing Switch for Battery Monitoring ( R/W ) *default: 0x00
 */
typedef volatile struct RG_FLEX_VBAT_CN // 0x05
{
    bool VBAT_MONI_CH1					:1; //0		 Battery monitor configuration for channel 1
    bool VBAT_MONI_CH2					:1; //1		 Battery monitor configuration for channel 2
    bool VBAT_MONI_CH3					:1; //2		 Battery monitor configuration for channel 3
    uint8_t	NOSET						:5; //3-7 no set
} RG_FLEX_VBAT_CN_TDS;


//Lead-off Detect Control Registers_____________________________________________________

typedef enum COMPARATOR_TRIGGER_LEVEL
{
	CTL_LEVEL_0 = 0b00,
	CTL_LEVEL_1 = 0b01,
	CTL_LEVEL_2 = 0b10,
	CTL_LEVEL_3 = 0b11,
}COMPARATOR_TRIGGER_LEVEL_TDE;

/**
    \brief AC analog/digital lead-off mode select
 */
typedef enum ACAD_LOD_MODE
{
	ACAD_LOD_DIGITAL = 0b00, //Digital AC lead-off detect (default)
	ACAD_LOD_ANALOG = 0b01, //Analog AC lead-off detect
}ACAD_LOD_MODE_TDE;

/**
    \brief Lead-off detect operation mode
 */
typedef enum SELAC_LOD_MODE
{
	SELAC_LOD_DC = 0b00, //DC lead-off mode (default)
	SELAC_LOD_AC = 0b01, //AC lead-off mode
}SELAC_LOD_MODE_TDE;

/**
    \brief  Lead-Off Detect Control ( R/W ) *default: 0x08
 */
typedef volatile struct RG_LOD_CN // 0x06
{

	COMPARATOR_TRIGGER_LEVEL_TDE ACLVL_LOD 	:2; //0-1 Programmable comparator trigger level for AC lead-off detection
	SELAC_LOD_MODE_TDE SELAC_LOD			:1; //2 Lead-off detect operation mode
	bool SHDN_LOD							:1; //3 Shut down lead-off detection
	ACAD_LOD_MODE_TDE	ACAD_LOD			:1; //4 AC analog/digital lead-off mode select
    uint8_t	NOSET							:3; //5-7 no set
} RG_LOD_CN_TDS;

/**
    \brief Lead-Off Detect Enable ( R/W ) *default: 0x00
 */
typedef volatile struct RG_LOD_EN // 0x07
{

	bool EN_LOD_1 							:1; //0 Lead-off-Detection for input IN1
	bool EN_LOD_2 							:1; //1 Lead-off-Detection for input IN2
	bool EN_LOD_3 							:1; //2 Lead-off-Detection for input IN3
	bool EN_LOD_4 							:1; //3 Lead-off-Detection for input IN4
	bool EN_LOD_5 							:1; //4 Lead-off-Detection for input IN5
	bool EN_LOD_6 							:1; //5 Lead-off-Detection for input IN6
    uint8_t	NOSET							:2; //6-7 no set
} RG_LOD_EN_TDS;

/**
    \brief Lead-Off Detect Current ( R/W ) *default: 0x00
 */
typedef volatile struct RG_LOD_CURRENT // 0x08
{
	uint8_t	CUR_LOD;	 //The lead-off detect current is programmable in a range of 2.04μA with steps of 8nA. current=CUR_LOD*0.008 μA
} RG_LOD_CURRENT_TDS;


/**
    \brief AC lead off test frequency division factor enum
 */
typedef enum ACDIV_FACTOR_ENUM
{
	ACDIV_FACTOR_K1 = 0, //Clock divider factor K = 1 (default)
	ACDIV_FACTOR_K16 = 1, //Clock divider factor K = 16
}ACDIV_FACTOR_TDE;

/**
    \brief AC Lead-Off Detect Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_LOD_AC_CN // 0x09
{
	uint8_t ACDIV_LOD					:7;	//0-6 Clock divider ratio for AC lead off.	There are 7 bits available to program the clock divider that generates the AC lead off test frequency
	ACDIV_FACTOR_TDE ACDIV_FACTOR		:1; //7 AC lead off test frequency division factor
} RG_LOD_AC_CN_TDS;


//Common-Mode Detection and Right-Leg Drive Feedback Control Registers ___________________________________________

/**
    \brief //Common-Mode Detect Enable ( R/W ) *default: 0x00
 */
typedef volatile struct RG_CMDET_EN // 0x0A
{

	bool CMDET_EN_IN_1 						:1; //0 Common-mode detect input enable IN1
	bool CMDET_EN_IN_2 						:1; //1 Common-mode detect input enable IN2
	bool CMDET_EN_IN_3 						:1; //2 Common-mode detect input enable IN3
	bool CMDET_EN_IN_4 						:1; //3 Common-mode detect input enable IN4
	bool CMDET_EN_IN_5 						:1; //4 Common-mode detect input enable IN5
	bool CMDET_EN_IN_6 						:1; //5 Common-mode detect input enable IN6
    uint8_t	NOSET							:2; //6-7 no set
} RG_CMDET_EN_TDS;


/**
    \brief Common-mode detect bandwidth mode enum
 */
typedef enum CMDET_BW_ENUM
{
	CMDET_BW_LOW_BANDWIDTH = 0, // Low-bandwidth mode (default)
	CMDET_BW_HIGH_BANDWIDTH  = 1, //High-bandwidth mode
}CMDET_BW_TDE;

/**
    \brief Common-mode detect capacitive load drive capability enum
 */
typedef enum CMDET_CAPDRIVE_ENUM
{
	CMDET_CAPDRIVE_LOW=0b00,
	CMDET_CAPDRIVE_MEDIUM_LOW=0b01,
	CMDET_CAPDRIVE_MEDIUM_HIGH=0b10,
	CMDET_CAPDRIVE_HIGH=0b11,
}CMDET_CAPDRIVE_TDE;


/**
    \brief Common-Mode Detect Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_CMDET_CN// 0x0B
{
	CMDET_CAPDRIVE_TDE	CMDET_CAPDRIVE	:2; //0 Common-mode detect capacitive load drive capability
	CMDET_BW_TDE CMDET_BW				:1;	//1 Clock divider ratio for AC lead off.	There are 7 bits available to program the clock divider that generates the AC lead off test frequency
    uint8_t	NOSET						:5; //2-7 no set
} RG_CMDET_CN_TDS;


/**
    \brief Right-leg drive bandwidth mode
 */
typedef enum RG_RLD_BW_ENUM
{
	RLD_BW_LOW_BANDWIDTH = 0, // Low-bandwidth mode (default)
	RLD_BW_HIGH_BANDWIDTH  = 1, //High-bandwidth mode
}RG_RLD_BW_TDE;

/**
    \brief Right-leg drive capacitive load drive capability enum
 */
typedef enum RG_RLD_CAPDRIVE_ENUM
{
	RLD_CAPDRIVE_LOW=0b00,
	RLD_CAPDRIVE_MEDIUM_LOW=0b01,
	RLD_CAPDRIVE_MEDIUM_HIGH=0b10,
	RLD_CAPDRIVE_HIGH=0b11,
}RG_RLD_CAPDRIVE_TDE;

/**
    \brief Right-Leg Drive Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_RLD_CN// 0x0C
{
	INPUT_SELECTOR_TDE SELRLD			:3; //0-2  Right-leg drive multiplexer
	bool SHDN_RLD						:1; //3 Shut down right-leg drive amplifier
	RG_RLD_CAPDRIVE_TDE RLD_CAPDRIVE	:2; //4-5 Right-leg drive capacitive load drive capabilit
	RG_RLD_BW_TDE RLD_BW				:1;	//1 Right-leg drive bandwidth mode
    uint8_t	NOSET						:1; //7 no set
} RG_RLD_CN_TDS;


//Wilson Control Registers _________________________________________________________________________________

/**
    \brief Wilson Reference Input Selection ( R/W ) *default: 0x00
 */
typedef volatile struct RG_WILSON_EN// 0x0D-0x0F
{
	INPUT_SELECTOR_TDE SELWILSON			:3; //0-2  Wilson reference routing for the buffer amplifier
    uint8_t	NOSET							:5; //3-7 no set
} RG_WILSON_EN_TDS;

/**
    \brief Wilson Reference Control enum
 */
typedef enum RG_WLS_REFCNTRL_ENUM
{
	RG_WLS_REFCNTRL_NOT_SET=0b00,
	RG_WLS_REFCNTRL_WILSONINT=0b01,
	RG_WLS_REFCNTRL_GOLDINT=0b10,
	RG_WLS_REFCNTRL_ERROR=0b11,
}RG_WLS_REFCNTRL_TDE;

/**
    \brief Wilson Reference Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_WILSON_CN// 0x10
{
	bool WILSONINT 			:1; //0  Wilson reference routing
	bool GOLDINT			:1; //1  Goldberger reference routing
    uint8_t	NOSET			:6; //2-7 no set
} RG_WILSON_CN_TDS;


//Reference Registers ____________________________________________________________________

/**
    \brief //Internal Reference Voltage Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_REF_CN// 0x11
{
	bool SHDN_REF 			:1; //0  Shut down internal 2.4-V reference voltage
	bool SHDN_CMREF			:1; //1  Shut down the common-mode and right-leg drive reference voltage circuitry
    uint8_t	NOSET			:6; //2-7 no set
} RG_REF_CN_TDS;


//OSC Control Registers ___________________________________________________________________

/**
    \brief  clock source enum
 */
typedef enum CLK_SOURCE_OSC_ENUM
{
	SHDN_OSC_INTERNAL=0, //Use internal clock with external crystal on XTAL1 and XTAL2 pins (default)
	SHDN_OSC_EXTERNAL=1, // Shut down internal oscillator and use external clock from CLK pin
}CLK_SOURCE_OSC_TDE;

/**
    \brief Clock Source and Output Clock Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_OSC_CN// 0x12
{
	bool EN_CLKOUT				:1; //0  Enable CLK pin output driver
	CLK_SOURCE_OSC_TDE SHDN_OSC	:1; //1  Select clock source
	bool STRTCLK				:1; //2  Start the clock to digital
    uint8_t	NOSET				:5; //3-7 no set
} RG_OSC_CN_TDS;


//AFE Control Registers________________________________________________________________

/**
    \brief  Clock frequency for channel
 */
typedef enum FS_HIGH_CH_ENUM
{
	FS_HIGH_CH_102400HZ=0,
	FS_HIGH_CH_204800HZ=1,
}FS_HIGH_CH_TDE;

/**
    \brief Analog Front End Frequency and Resolution ( R/W ) *default: 0x00
 */
typedef volatile struct RG_AFE_RES// 0x13
{
	bool EN_HIRES_CH1			:1; //0 Enable High-resolution mode for Channel 1 instrumentation amplifier
	bool EN_HIRES_CH2			:1; //1 Enable High-resolution mode for Channel 2 instrumentation amplifier
	bool EN_HIRES_CH3			:1; //2 Enable High-resolution mode for Channel 3 instrumentation amplifier
	FS_HIGH_CH_TDE FS_HIGH_CH1 	:1; //3 Clock frequency for Channel 1
	FS_HIGH_CH_TDE FS_HIGH_CH2 	:1; //4 Clock frequency for Channel 2
	FS_HIGH_CH_TDE FS_HIGH_CH3 	:1; //5 Clock frequency for Channel 3
    uint8_t	NOSET				:2; //6-7 no set
} RG_AFE_RES_TDS;

/**
    \brief Analog Front End Shutdown Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_AFE_SHDN_CN// 0x14
{
	bool SHDN_INA_CH1 			:1; //0 Shut down the instrumentation amplifier for Channel 1
	bool SHDN_INA_CH2 			:1; //1 Shut down the instrumentation amplifier for Channel 2
	bool SHDN_INA_CH3 			:1; //2 Shut down the instrumentation amplifier for Channel 3
	bool SHDN_SDM_CH1			:1; //3 Shut down the sigma-delta modulator for Channel 1
	bool SHDN_SDM_CH2			:1; //4 Shut down the sigma-delta modulator for Channel 2
	bool SHDN_SDM_CH3			:1; //5 Shut down the sigma-delta modulator for Channel 3
    uint8_t	NOSET				:2; //6-7 no set
} RG_AFE_SHDN_CN_TDS;

/**
    \brief Analog Front End Fault Detection Control ( R/W ) *default: 0x00
 */
typedef volatile struct RG_AFE_FAULT_CN // 0x15
{
	bool SHDN_FAULTDET_CH1 			:1; //0 Disable the instrumentation amplifier fault detection for Channel 1
	bool SHDN_FAULTDET_CH2 			:1; //1 Disable the instrumentation amplifier fault detection for Channel 2
	bool SHDN_FAULTDET_CH3 			:1; //2 Disable the instrumentation amplifier fault detection for Channel 3
	uint8_t	NOSET					:5; //3-7 no set
} RG_AFE_FAULT_CN_TDS;


/**
    \brief Analog Pace Channel Output Routing Control ( R/W ) *default: 0x01
 */
typedef volatile struct RG_AFE_PACE_CN // 0x17
{
	bool SHDN_PACE 			:1; //0 Shut down analog pace channel
	bool PACE2WCT			:1; //1 Connect the analog pace channel output to WCT pin
	bool PACE2RLDIN 		:1; //2 Connect the analog pace channel output to RLDIN pin
	uint8_t	NOSET			:5; //3-7 no set
} RG_AFE_PACE_CN_TDS;


//Error Status Registers ____________________________________________________________________________

/**
    \brief Lead-Off Detect Error Status ( RO ) *default: —
 */
typedef volatile struct RG_ERROR_LOD// 0x18
{
	//Lead-Off Detect Status.There is one bit available per input pin, where the MSB corresponds to input pin IN6 and the LSB	corresponds to input pin IN1.
	bool OUT_LOD_IN1 		:1; //0 Lead-Off Detect Status IN1
	bool OUT_LOD_IN2 		:1; //1 Lead-Off Detect Status IN2
	bool OUT_LOD_IN3 		:1; //2 Lead-Off Detect Status IN3
	bool OUT_LOD_IN4 		:1; //3 Lead-Off Detect Status IN4
	bool OUT_LOD_IN5 		:1; //4 Lead-Off Detect Status IN5
	bool OUT_LOD_IN6 		:1; //5 Lead-Off Detect Status IN6
	uint8_t	NOSET			:2; //6-7 no set
} RG_ERROR_LOD_TDS;

/**
    \brief Analog Other Error Status ( RO ) *default: —
 */
typedef volatile struct RG_ERROR_STATUS// 0x19
{
	bool CMOR 			:1; //0 Common-mode level out-of-range
	bool RLDRAIL		:1; //1 Right leg drive near rail
	bool BATLOW 		:1; //2 Low battery
	bool LEADOFF		:1; //3 Lead off detected
	bool CH1ERR			:1; //4 Channel 1 out-of-range error
	bool CH2ERR			:1; //5 Channel 2 out-of-range error
	bool CH3ERR			:1; //6 Channel 3 out-of-range error
	bool SYNCEDGEERR	:1; //7 Digital synchronization error
} RG_ERROR_STATUS_TDS;

/**
    \brief Channel  AFE Out-of-Range Status ( RO ) *default: —
 */
typedef volatile struct RG_ERROR_RANGE// 0x1A-0x1C
{
	bool DIF_HIGH_CH		:1; //0 Channel instrumentation amplifier output out-of-range
	bool OUTP_HIGH_CH		:1; //1 Channel instrumentation amplifier positive output near positive rail
	bool OUTP_LOW_CH  		:1; //2 Channel instrumentation amplifier positive output near negative rail
	bool OUTN_HIGH_CH		:1; //3 Channel instrumentation amplifier negative output near positive rail
	bool OUTN_LOW_CH		:1; //4 Channel instrumentation amplifier negative output near negative rail
	bool SIGN_CH			:1; //5 Channel instrumentation amplifier output sign
	bool SDM_OR_CH			:1; //6 Sigma-delta modulator over range
	uint8_t	NOSET			:1; //7 no set
} RG_ERROR_RANGE_TDS;

/**
    \brief Synchronization Error ( RO ) *default: —
 */
typedef volatile struct RG_ERROR_SYNC// 0x1D
{
	bool SYNC_CH1ERR			:1; //0 Channel 1 synchronization error
	bool SYNC_CH2ERR			:1; //1 Channel 2 synchronization error
	bool SYNC_CH3ERR			:1; //2 Channel 3 synchronization error
	bool SYNC_PHASEERR			:1; //3 Clock timing generator phase error
    uint8_t	NOSET				:4; //4-7 no set
} RG_ERROR_SYNC_TDS;

/**
    \brief Miscellaneous Errors ( RO ) *default: 0x00
 */
typedef volatile struct RG_ERROR_MISC// 0x1E
{
	bool CMOR_STATUS			:1; //0 Common-mode level out-of-range error status
	bool RLDRAIL_STATUS			:1; //1 Right-leg drive near rail error status
	bool BATLOW_STATUS			:1; //2 Low-battery error status
    uint8_t	NOSET				:5; //3-7 no set
} RG_ERROR_MISC_TDS;

//Digital Registers_______________________________________________________________________________________________

/**
    \brief Right-leg drive capacitive load drive capability enum
 */
typedef enum DIGO_STRENGTH_ENUM
{
	DIGO_STRENGTH_LOW=0b00, 		//Low drive mode
	DIGO_STRENGTH_MEDIUM_LOW=0b01,	//Mid-low drive mode
	DIGO_STRENGTH_MEDIUM_HIGH=0b10,	//Mid-high drive mode
	DIGO_STRENGTH_HIGH=0b11,		//High drive mode (Default)
}DIGO_STRENGTH_TDE;

/**
	\brief Digital Output Drive Strength ( R/W ) *default: 0x03
 */
typedef volatile struct RG_DIGO_STRENGTH// 0x1F
{
	DIGO_STRENGTH_TDE DIGO_STRENGTH	:2; //0-1 Digital Output Drive Strength
	uint8_t	NOSET					:6; //2-7 no set
} RG_DIGO_STRENGTH_TDS;

typedef enum R2_RATE_ENUM
{
	R2_RATE_4=0b0001,
	R2_RATE_5=0b0010,
	R2_RATE_6=0b0100,
	R2_RATE_8=0b1000, //(default)
}R2_RATE_TDE;

/**
	\brief R2 Decimation Rate ( R/W ) *default: 0x08
 */
typedef volatile struct RG_R2_RATE// 0x21
{
	R2_RATE_TDE R2_RATE		:4; //0-3 R2 decimation rate
								//The register sets to its default value if none or more than one bit are enabled.
	uint8_t	NOSET			:4; //4-7 no set
} RG_R2_RATE_TDS;

typedef enum R3_RATE_ENUM
{
	R3_RATE_4= 0b00000001,
	R3_RATE_6= 0b00000010,
	R3_RATE_8= 0b00000100,
	R3_RATE_12=0b00001000,
	R3_RATE_16=0b00010000,
	R3_RATE_32=0b00100000,
	R3_RATE_64=0b01000000,
	R3_RATE_128=0b10000000, //(default)

}R3_RATE_TDE;

/**
	\brief R3 Decimation Rate for Channel 1 ( R/W ) *default: 0x80
 */
typedef volatile struct RG_R3_RATE// 0x22-0x24
{
	R3_RATE_TDE R3_RATE		:8; //0-7 R3 decimation rate
								//The register sets to its default value if none or more than one bit are enabled.
} RG_R3_RATE_TDS;


typedef enum R1_RATE_ENUM
{
	R1_RATE_STANDART_R1_4=0, //R1 = 4: Standard PACE Data Rate (default)
	R1_RATE_DOUBLE_R1_2=1,	//R1 = 2: Double PACE Data Rate
} R1_RATE_TDE;

/**
	\brief R1 Decimation Rate ( R/W ) *default: 0x00
 */
typedef volatile struct RG_R1_RATE// 0x25
{
	R1_RATE_TDE R1_RATE_CH1		:1; //0 Pace data rate for channel 1
	R1_RATE_TDE R1_RATE_CH2		:1; //1 Pace data rate for channel 2
	R1_RATE_TDE R1_RATE_CH3		:1; //2 Pace data rate for channel 3
	uint8_t	NOSET						:5; //3-7 no set
} RG_R1_RATE_TDS;


/**
    \brief ECG Filter Disable ( R/W ) *default: 0x00
 */
typedef volatile struct RG_DIS_EFILTER// 0x26
{
	bool DIS_E1			:1; //0 Disable the ECG filter for channel 1
	bool DIS_E2			:1; //1 Disable the ECG filter for channel 2
	bool DIS_E3			:1; //2 Disable the ECG filter for channel 3
    uint8_t	NOSET		:5; //3-7 no set
} RG_DIS_EFILTER_TDS;

typedef enum DRDYB_SRC_ENUM
{
	DRDYB_SRC_NO_SET=    0b000000, //DRDYB pin not asserted (default)
	DRDYB_SRC_CH_1_PACE= 0b000001, //Driven by Channel 1 pace
	DRDYB_SRC_CH_2_PACE= 0b000010, //Driven by Channel 2 pace
	DRDYB_SRC_CH_3_PACE= 0b000100, //Driven by Channel 3 pace
	DRDYB_SRC_CH_1_ECG=  0b001000, //Driven by Channel 1 ECG
	DRDYB_SRC_CH_2_ECG=  0b010000, //Driven by Channel 2 ECG
	DRDYB_SRC_CH_3_ECG=  0b100000, //Driven by Channel 3 ECG
}DRDYB_SRC_TDE;

/**
	\brief Data Ready Pin Source ( R/W ) *default: 0x00
 */
typedef volatile struct RG_DRDYB_SRC// 0x27
{
	DRDYB_SRC_TDE DRDYB_SRC		:6; //0-5 Select channel to drive the DRDYB pin
	uint8_t	NOSET				:2; //6-7 no set
} RG_DRDYB_SRC_TDS;

typedef enum SYNCB_SRC_ENUM
{
	SYNCB_SRC_NO_SET=    0b000000, //No source selected (default)
	SYNCB_SRC_CH_1_PACE= 0b000001, //Driven by Channel 1 pace
	SYNCB_SRC_CH_2_PACE= 0b000010, //Driven by Channel 2 pace
	SYNCB_SRC_CH_3_PACE= 0b000100, //Driven by Channel 3 pace
	SYNCB_SRC_CH_1_ECG=  0b001000, //Driven by Channel 1 ECG
	SYNCB_SRC_CH_2_ECG=  0b010000, //Driven by Channel 2 ECG
	SYNCB_SRC_CH_3_ECG=  0b100000, //Driven by Channel 3 ECG
}SYNCB_SRC_TDE;

/**
	\brief SYNCB In/Out Pin Control ( R/W ) *default: 0x40
 */
typedef volatile struct RG_DIS_SYNCBOUT// 0x28
{
	SYNCB_SRC_TDE SYNCB_SRC		:6; //0-5 Select channel to drive the SYNCB pin. Note: Choose the slowest pace or ECG channel as source. Bits[5:0] must be cleared to 0 for slave devices.
	bool DIS_SYNCBOUT			:1; //6 Disable the SYNCB pin output driver. Note: Bit should be set to 1 for slave devices.
	uint8_t	NOSET				:1; //7 no set
} RG_DIS_SYNCBOUT_TDS;


/**
    \brief Optional Mask Control for DRDYB Output ( R/W ) *default: 0x00
 */
typedef volatile struct RG_MASK_DRDYB// 0x29
{
	bool DRDYBMASK_CTL0		:1; //0 Optional mask control for DRDYB output
	bool DRDYBMASK_CTL1		:1; //1 START_CON mask control for DRDYB output
    uint8_t	NOSET			:6; //2-7 no set
} RG_MASK_DRDYB_TDS;


/**
    \brief Mask Error on ALARMB Pin ( R/W ) *default: 0x00
 */
typedef volatile struct RG_MASK_ERR// 0x2A
{
	bool MASK_CMOR			:1; //0 Mask alarm condition for CMOR=1
	bool MASK_RLDRAIL 		:1; //1 Mask alarm condition for RLDRAIL=1
	bool MASK_BATLOW 		:1; //2 Mask alarm condition for BATLOW=1
	bool MASK_LEADOFF 		:1; //3 Mask alarm condition for LEADOFF=1
	bool MASK_CH1ERR 		:1; //4 Mask alarm condition for CH1ERR=1
	bool MASK_CH2ERR 		:1; //5 Mask alarm condition for CH2ERR=1
	bool MASK_CH3ERR 		:1; //6 Mask alarm condition for CH3ERR=1
	bool MASK_SYNCEDGEER	:1; //7 Mask alarm condition when SYNCEDGEERR=1
} RG_MASK_ERR_TDS;

/**
    \brief //Digital Filter for Analog Alarm Signals ( R/W ) *default: 0x33
 */
typedef volatile struct RG_ALARM_FILTER// 0x2E
{
	uint8_t AFILTER_LOD		:4; //0-3 Filter for OUT_LOD[5:0] alarm count. Number of consecutive lead off alarm signal counts +1 before ALARMB is asserted.
    uint8_t	AFILTER_OTHER	:4; //4-7 Filter for all other alarms count. Number of consecutive analog alarm signal counts +1 before ALARMB is asserted.
} RG_ALARM_FILTER_TDS;

/**
    \brief Configure Channel for Loop Read Back Mode ( R/W ) *default: 0x00
 */
typedef volatile struct RG_CH_CNFG// 0x2F
{
	bool STS_EN :1; //0 Enable DATA_STATUS read back
	bool P1_EN 	:1; //1 Enable DATA_CH1_PACE read back
	bool P2_EN 	:1; //2 Enable DATA_CH2_PACE read back
	bool P3_EN 	:1; //3 Enable DATA_CH3_PACE read back
	bool E1_EN 	:1; //4 Enable DATA_CH1_ECG read back
	bool E2_EN 	:1; //5 Enable DATA_CH2_ECG read back
	bool E3_EN 	:1; //6 Enable DATA_CH3_ECG read back
	uint8_t	NOSET		:1; //7 no set
} RG_CH_CNFG_TDS;


//Pace and ECG Data Read Back Registers ________________________________________________________________________________

/**
    \brief ECG and Pace Data Ready Status ( RO ) *default: —
 */
typedef volatile struct RG_DATA_STATUS// 0x30
{
	bool NOSET :1; //0 no set
	bool ALARMB 	:1; //1 ALARMB status
	bool P1_DRDY 	:1; //Channel 1 pace data ready
	bool P2_DRDY 	:1; //Channel 2 pace data ready
	bool P3_DRDY 	:1; //Channel 3 pace data ready
	bool E1_DRDY 	:1; //5 Channel 1 ECG data ready
	bool E2_DRDY 	:1; //6 Channel 2 ECG data ready
	bool E3_DRDY 	:1; //7 Channel 3 ECG data ready
} RG_DATA_STATUS_TDS;

#pragma pack(pop)

}

#endif
