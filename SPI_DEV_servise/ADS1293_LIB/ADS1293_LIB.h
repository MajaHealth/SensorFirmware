/**
    \file ADS1293_LIB.h
    \author VTK TEAM (OK)
    \brief ADS1293 library file
 */
#ifndef ADS1293_LIB_ADS1293_LIB_H_
#define ADS1293_LIB_ADS1293_LIB_H_

#include "stdint.h"
#include "VT_register_container.h"
#include "ADS1293_register_map.h"
#include "ADS1293_IO.h"
#include "VT_sync_data_stream_interface.h"

namespace ADS1293
{

/**
    \brief ADS1293 library class
 */
class ADS1293_LIB
{
public:
	ADS1293_LIB(VT_sync_data_stream_interface *_SPI_driver_pointer);

	/**
		\brief Set conversion state
		\param [in] enable - conversion state(if true - conversion work)
	 */
	void set_conversion_state(bool enable);

	/**
		\brief Set standby mode
		\param [in] enable - standby state(if true - standby mode active)
	 */
	void set_standby_mode(bool enable);

	/**
		\brief Set power down mode
		\param [in] enable - power down state(if true - power down mode active)
	 */
	void set_powerdown_mode(bool enable);

	/**
		\brief Get conversion state
		\return - conversion state(if true - conversion work)
	 */
	bool get_conversion_state(void);

	/**
		\brief Get standby mode
		\return - standby state(if true - standby mode active)
	 */
	bool get_standby_mode(void);

	/**
		\brief Get power down mode
		\return - power down state(if true - power down mode active)
	 */
	bool get_powerdown_mode(void);

	/**
		\brief set test signal for channel 1
		\param [in] test_signal - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	void set_test_signal_for_ch_1(TEST_SIGNAL_SELECTOR_TDE test_signal);

	/**
		\brief set positive terminal for channel 1
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_positive_terminal_for_ch_1(INPUT_SELECTOR_TDE input);

	/**
		\brief set negative terminal for channel 1
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_negative_terminal_for_ch_1(INPUT_SELECTOR_TDE input);

	/**
		\brief get test signal for channel 1
		\return - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	TEST_SIGNAL_SELECTOR_TDE get_test_signal_for_ch_1(void);

	/**
		\brief get positive terminal for channel 1
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_positive_terminal_for_ch_1(void);

	/**
		\brief get negative terminal for channel 1
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_negative_terminal_for_ch_1(void);

	/**
		\brief set test signal for channel 2
		\param [in] test_signal - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	void set_test_signal_for_ch_2(TEST_SIGNAL_SELECTOR_TDE test_signal);

	/**
		\brief set positive terminal for channel 2
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_positive_terminal_for_ch_2(INPUT_SELECTOR_TDE input);

	/**
		\brief set negative terminal for channel 2
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_negative_terminal_for_ch_2(INPUT_SELECTOR_TDE input);

	/**
		\brief get test signal for channel 2
		\return - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	TEST_SIGNAL_SELECTOR_TDE get_test_signal_for_ch_2(void);

	/**
		\brief get positive terminal for channel 2
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_positive_terminal_for_ch_2(void);

	/**
		\brief get negative terminal for channel 2
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_negative_terminal_for_ch_2(void);

	/**
		\brief set test signal for channel 3
		\param [in] test_signal - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	void set_test_signal_for_ch_3(TEST_SIGNAL_SELECTOR_TDE test_signal);

	/**
		\brief set positive terminal for channel 3
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_positive_terminal_for_ch_3(INPUT_SELECTOR_TDE input);

	/**
		\brief set negative terminal for channel 3
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_negative_terminal_for_ch_3(INPUT_SELECTOR_TDE input);

	/**
		\brief get test signal for channel 3
		\return - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	TEST_SIGNAL_SELECTOR_TDE get_test_signal_for_ch_3(void);

	/**
		\brief get positive terminal for channel 3
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_positive_terminal_for_ch_3(void);

	/**
		\brief get negative terminal for channel 3
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_negative_terminal_for_ch_3(void);

	/**
		\brief set test signal for pace channel
		\param [in] test_signal - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	void set_test_signal_for_pace_channel(TEST_SIGNAL_SELECTOR_TDE test_signal);

	/**
		\brief set positive terminal for pace channel
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_positive_terminal_for_pace_channel(INPUT_SELECTOR_TDE input);

	/**
		\brief set negative terminal for pace channel
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_negative_terminal_for_pace_channel(INPUT_SELECTOR_TDE input);

	/**
		\brief get test signal for pace channel
		\return - test signal type (TEST_SIGNAL_SELECTOR)
	 */
	TEST_SIGNAL_SELECTOR_TDE get_test_signal_for_pace_channel(void);

	/**
		\brief get positive terminal for pace channel
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_positive_terminal_for_pace_channel(void);

	/**
		\brief get negative terminal for pace channel
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_negative_terminal_for_pace_channel(void);

	/**
		\brief Set battery monitor configuration for channel 1
		\param [in] enable - battery monitor state(if true - battery monitor active)
	 */
	void set_battery_monitor_for_ch1(bool enable);

	/**
		\brief Get battery monitor configuration for channel 1
		\return - battery monitor state(if true - battery monitor active)
	 */
	bool get_battery_monitor_for_ch1(void);

	/**
		\brief Set battery monitor configuration for channel 2
		\param [in] enable - battery monitor state(if true - battery monitor active)
	 */
	void set_battery_monitor_for_ch2(bool enable);

	/**
		\brief Get battery monitor configuration for channel 2
		\return - battery monitor state(if true - battery monitor active)
	 */
	bool get_battery_monitor_for_ch2(void);

	/**
		\brief Set battery monitor configuration for channel 3
		\param [in] enable - battery monitor state(if true - battery monitor active)
	 */
	void set_battery_monitor_for_ch3(bool enable);

	/**
		\brief Get battery monitor configuration for channel 3
		\return - battery monitor state(if true - battery monitor active)
	 */
	bool get_battery_monitor_for_ch3(void);


	/**
		\brief Set AC analog/digital lead-off mode select
		\param [in] mode - AC analog or digital lead-off mode (ACAD_LOD_MODE_TDE)
	 */
	void set_AC_leadoff_mode(ACAD_LOD_MODE_TDE mode);

	/**
		\brief Set shutdown lead-off detection
		\param [in] enable - Lead-off detection state(if true - Lead-off detection circuitry is shut down (default))
	 */
	void set_shutdown_leadoff_detection(bool enable);

	/**
		\brief Set Lead-off detect operation mode
		\param [in] mode - Lead-off detect operation mode(SELAC_LOD_MODE_TDE)
	 */
	void set_leadoff_detect_mode(SELAC_LOD_MODE_TDE mode);

	/**
		\brief Set programmable comparator trigger level for AC lead-off detection
		\param [in] level - comparator trigger level for AC lead-off detection(COMPARATOR_TRIGGER_LEVEL_TDE)
	 */
	void set_leadoff_AC_comparator_trigger_level(COMPARATOR_TRIGGER_LEVEL_TDE level);

	/**
		\brief Get AC analog/digital lead-off mode select
		\return - AC analog or digital lead-off mode (ACAD_LOD_MODE_TDE)
	 */
	ACAD_LOD_MODE_TDE get_AC_leadoff_mode(void);

	/**
		\brief Get shutdown lead-off detection
		\return - Lead-off detection state(if true - Lead-off detection circuitry is shut down (default))
	 */
	bool get_shutdown_leadoff_detection(void);

	/**
		\brief Get Lead-off detect operation mode
		\return - Lead-off detect operation mode(SELAC_LOD_MODE_TDE)
	 */
	SELAC_LOD_MODE_TDE get_leadoff_detect_mode(void);

	/**
		\brief Get programmable comparator trigger level for AC lead-off detection
		\return - comparator trigger level for AC lead-off detection(COMPARATOR_TRIGGER_LEVEL_TDE)
	 */
	COMPARATOR_TRIGGER_LEVEL_TDE get_leadoff_AC_comparator_trigger_level(void);


	/**
		\brief set lead-off detection for input 1
		\param [in] enable -  lead-off detection state(if true - Lead-off detection circuitry is active for input))
	 */
	void set_leadoff_detection_for_input_1(bool enable);

	/**
		\brief set lead-off detection for input 2
		\param [in] enable -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	void set_leadoff_detection_for_input_2(bool enable);

	/**
		\brief set lead-off detection for input 3
		\param [in] enable -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	void set_leadoff_detection_for_input_3(bool enable);

	/**
		\brief set lead-off detection for input 4
		\param [in] enable -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	void set_leadoff_detection_for_input_4(bool enable);

	/**
		\brief set lead-off detection for input 5
		\param [in] enable -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	void set_leadoff_detection_for_input_5(bool enable);

	/**
		\brief set lead-off detection for input 6
		\param [in] enable -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	void set_leadoff_detection_for_input_6(bool enable);


	/**
		\brief Get lead-off detection for input 1
		\return -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	bool get_leadoff_detection_for_input_1(void);

	/**
		\brief Get lead-off detection for input 2
		\return -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	bool get_leadoff_detection_for_input_2(void);

	/**
		\brief Get lead-off detection for input 3
		\return -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	bool get_leadoff_detection_for_input_3(void);

	/**
		\brief Get lead-off detection for input 4
		\return -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	bool get_leadoff_detection_for_input_4(void);

	/**
		\brief Get lead-off detection for input 5
		\return -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	bool get_leadoff_detection_for_input_5(void);

	/**
		\brief Get lead-off detection for input 6
		\return -  lead-off detection state for input(if true - Lead-off detection circuitry is active for input))
	 */
	bool get_leadoff_detection_for_input_6(void);

	/**
		\brief set lead-off detection current
		\param [in] current_nA -  lead-off detection current in (nA) nanoampere (min:0nA, max 2040nA)
	 */
	void set_leadoff_detection_current(uint32_t current_nA);

	/**
		\brief get lead-off detection current
		\param [in] current_nA -  lead-off detection current in (nA) nanoampere (min:0nA, max 2040nA)
	 */
	uint32_t get_leadoff_detection_current(void);


	/**
		\brief set lead-off test frequency divider  F=50/(4*K*(divider_ratio+1))kHz
		\param [in] divider_ratio -  Clock divider ratio for AC lead off (max:127)
		\param [in] divider_factor - set additional divider factor(K=1 or K=16) (ACDIV_FACTOR_TDE)
	 */
	void set_leadoff_frequency_divider(uint8_t divider_ratio,ACDIV_FACTOR_TDE divider_factor);
	/**
		\brief get lead-off test frequency
		\return -  Clock frequency for AC lead off (in Hz)
	 */
	uint32_t get_AC_leadoff_frequency(void);

	/**
		\brief set Common-Mode detection for input 1
		\param [in] enable -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	void set_common_mode_detection_for_input_1(bool enable);

	/**
		\brief set Common-Mode detection for input 2
		\param [in] enable -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	void set_common_mode_detection_for_input_2(bool enable);

	/**
		\brief set Common-Mode detection for input 3
		\param [in] enable -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	void set_common_mode_detection_for_input_3(bool enable);

	/**
		\brief set Common-Mode detection for input 4
		\param [in] enable -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	void set_common_mode_detection_for_input_4(bool enable);

	/**
		\brief set Common-Mode detection for input 5
		\param [in] enable -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	void set_common_mode_detection_for_input_5(bool enable);

	/**
		\brief set Common-Mode detection for input 6
		\param [in] enable -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	void set_common_mode_detection_for_input_6(bool enable);

	/**
		\brief set Common-Mode detection for input 1
		\return -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	bool get_common_mode_detection_for_input_1(void);

	/**
		\brief get Common-Mode detection for input 2
		\return -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	bool get_common_mode_detection_for_input_2(void);

	/**
		\brief get Common-Mode detection for input 3
		\return -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	bool get_common_mode_detection_for_input_3(void);

	/**
		\brief get Common-Mode detection for input 4
		\return -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	bool get_common_mode_detection_for_input_4(void);

	/**
		\brief get Common-Mode detection for input 5
		\return -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	bool get_common_mode_detection_for_input_5(void);

	/**
		\brief get Common-Mode detection for input 6
		\return -  Common-Mode detection state(if true - the corresponding input voltage to contribute to the average voltage of the common-mode detect block.)
	 */
	bool get_common_mode_detection_for_input_6(void);


	/**
		\brief Set Common-mode detect bandwidth mode
		\param [in] mode - Common-mode detect bandwidth mode(CMDET_BW_TDE)
	 */
	void set_common_mode_detect_bandwidth_mode(CMDET_BW_TDE mode);

	/**
		\brief Get Common-mode detect bandwidth mode
		\return - Common-mode detect bandwidth mode(CMDET_BW_TDE)
	 */
	CMDET_BW_TDE get_common_mode_detect_bandwidth_mode(void);

	/**
		\brief Set Common-mode detect capacitive load drive capability
		\param [in] mode - detect capacitive load drive capability(CMDET_CAPDRIVE_TDE)
	 */
	void set_common_mode_detect_cap_load_drive_capability(CMDET_CAPDRIVE_TDE mode);

	/**
		\brief Get Common-mode detect capacitive load drive capability
		\return - Common-mode detect capacitive load drive capability(CMDET_CAPDRIVE_TDE)
	 */
	CMDET_CAPDRIVE_TDE get_common_mode_detect_cap_load_drive_capability(void);


	/**
		\brief Set Right-leg drive bandwidth mode
		\param [in] mode - Right-leg drive bandwidth mode(RG_RLD_BW_TDE)
	 */
	void set_right_leg_drive_bandwidth_mode(RG_RLD_BW_TDE mode);

	/**
		\brief Get Right-leg drive bandwidth mode
		\return - Right-leg drive bandwidth mode(RG_RLD_BW_TDE)
	 */
	RG_RLD_BW_TDE get_right_leg_drive_bandwidth_mode(void);

	/**
		\brief Set right_leg detect capacitive load drive capability
		\param [in] mode - right_leg detect capacitive load drive capability(RG_RLD_CAPDRIVE_TDE)
	 */
	void set_right_leg_detect_cap_load_drive_capability(RG_RLD_CAPDRIVE_TDE mode);

	/**
		\brief Get right_leg detect capacitive load drive capability
		\return - right_leg detect capacitive load drive capability(RG_RLD_CAPDRIVE_TDE)
	 */
	RG_RLD_CAPDRIVE_TDE get_right_leg_detect_cap_load_drive_capability(void);

	/**
		\brief set Shut down right-leg drive amplifier
		\param [in] enable -  Shut down right-leg drive amplifier state(if true - right-leg drive amplifier is off)
	 */
	void set_shutdown_right_leg_drive_amplifier(bool enable);

	/**
		\brief get Shut down right-leg drive amplifier
		\return - Shut down right-leg drive amplifier state(if true - right-leg drive amplifier is off)
	 */
	bool get_shutdown_right_leg_drive_amplifier(void);

	/**
		\brief set Right-leg drive output multiplexer
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_right_leg_drive_output(INPUT_SELECTOR_TDE input);

	/**
		\brief get Right-leg drive output multiplexer
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_right_leg_drive_output(INPUT_SELECTOR_TDE input);


	/**
		\brief set Wilson Reference Input 1 selection
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_wilson_reference_input_1(INPUT_SELECTOR_TDE input);

	/**
		\brief set Wilson Reference Input 2 selection
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_wilson_reference_input_2(INPUT_SELECTOR_TDE input);

	/**
		\brief set Wilson Reference Input 1 selection
		\param [in] input - input signal number (INPUT_SELECTOR_TDE)
	 */
	void set_wilson_reference_input_3(INPUT_SELECTOR_TDE input);

	/**
		\brief get Wilson Reference Input 1 selection
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_wilson_reference_input_1(void);

	/**
		\brief get Wilson Reference Input 2 selection
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_wilson_reference_input_2(void);

	/**
		\brief get Wilson Reference Input 3 selection
		\return - input signal number (INPUT_SELECTOR_TDE)
	 */
	INPUT_SELECTOR_TDE get_wilson_reference_input_3(void);


	/**
		\brief set Wilson Reference control
		\param [in] ref_control - reference control (RG_WLS_REFCNTRL_TDE)
								Wilson reference output internally connected to IN6
								Goldberger reference outputs internally connected to IN4, IN5 and IN6
	 */
	void set_wilson_reference_control(RG_WLS_REFCNTRL_TDE ref_control);

	/**
		\brief get Wilson Reference control
		\param [in] ref_control - reference control (RG_WLS_REFCNTRL_TDE)
								Wilson reference output internally connected to IN6
								Goldberger reference outputs internally connected to IN4, IN5 and IN6
	 */
	RG_WLS_REFCNTRL_TDE get_wilson_reference_control(void);


	/**
		\brief set shut down the common-mode and right-leg drive reference voltage circuitry
		\param [in] enable -  Shut down the common-mode reference voltage circuitry  state(if true - common-mode reference voltage is off)
	 */
	void set_shutdown_common_mode_ref_voltage(bool enable);

	/**
		\brief get shut down the common-mode and right-leg drive reference voltage circuitry
		\param [in] enable -  Shut down the common-mode reference voltage circuitry  state(if true - common-mode reference voltage is off)
	 */
	bool get_shutdown_common_mode_ref_voltage(void);

	/**
		\brief set shut down internal 2.4V reference voltage
		\param [in] enable  -  shut down internal 2.4V reference voltage  state(if true - internal 2.4V reference voltage is off)
	 */
	void set_shutdown_internal_ref_voltage(bool enable);

	/**
		\brief get shut down internal 2.4V reference voltage
		\return - shut down internal 2.4V reference voltage  state(if true - internal 2.4V reference voltage is off)
	 */
	bool get_shutdown_internal_ref_voltage(void);



	/**
		\brief set start the clock to digital
		\param [in] enable  -  start the clock to digital state(if true - clock is active)
	 */
	void set_start_clock_to_digital(bool enable);

	/**
		\brief set start the clock to digital
		\return  -  start the clock to digital state(if true - clock is active)
	 */
	bool get_start_clock_to_digital(void);

	/**
		\brief set enable CLK pin output driver
		\param [in] enable  -  enable CLK pin output driver state(if true - CLK pin output is active)
	 */
	void set_enable_CLK_pin_output(bool enable);

	/**
		\brief get enable CLK pin output driver
		\return  -  enable CLK pin output driver state(if true - CLK pin output is active)
	 */
	bool get_enable_CLK_pin_output(void);


	/**
		\brief set clock source
		\param [in] clock source  -  select clock source (CLK_SOURCE_OSC_TDE)
	 */
	void set_clock_source(CLK_SOURCE_OSC_TDE clk_source);

	/**
		\brief get clock source
		\return  -  select clock source (CLK_SOURCE_OSC_TDE)
	 */
	CLK_SOURCE_OSC_TDE get_clock_source(void);

	/**
		\brief set enable High-resolution mode for Channel 1 instrumentation amplifier
		\param [in] enable  - Enable High-resolution mode for Channel INA(if true - INA in High-resolution mode)
	 */
	void set_enable_INA_high_resolition_CH_1(bool enable);

	/**
		\brief set enable High-resolution mode for Channel 2 instrumentation amplifier
		\param [in] enable  - Enable High-resolution mode for Channel INA(if true - INA in High-resolution mode)
	 */
	void set_enable_INA_high_resolition_CH_2(bool enable);

	/**
		\brief set enable High-resolution mode for Channel 3 instrumentation amplifier
		\param [in] enable  - Enable High-resolution mode for Channel INA(if true - INA in High-resolution mode)
	 */
	void set_enable_INA_high_resolition_CH_3(bool enable);

	/**
		\brief get enable High-resolution mode for Channel 1 instrumentation amplifier
		\return  - Enable High-resolution mode for Channel INA(if true - INA in High-resolution mode)
	 */
	bool get_enable_INA_high_resolition_CH_1(void);

	/**
		\brief get enable High-resolution mode for Channel 2 instrumentation amplifier
		\return  - Enable High-resolution mode for Channel INA(if true - INA in High-resolution mode)
	 */
	bool get_enable_INA_high_resolition_CH_2(void);

	/**
		\brief get enable High-resolution mode for Channel 3 instrumentation amplifier
		\return  - Enable High-resolution mode for Channel INA(if true - INA in High-resolution mode)
	 */
	bool get_enable_INA_high_resolition_CH_3(void);


	/**
		\brief set Clock frequency for Channel 1
		\param [in] clk_frequency  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	void set_clock_frequency_for_ch_1(FS_HIGH_CH_TDE clk_frequency);

	/**
		\brief set Clock frequency for Channel 2
		\param [in] clk_frequency  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	void set_clock_frequency_for_ch_2(FS_HIGH_CH_TDE clk_frequency);

	/**
		\brief set Clock frequency for Channel 3
		\param [in] clk_frequency  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	void set_clock_frequency_for_ch_3(FS_HIGH_CH_TDE clk_frequency);

	/**
		\brief get Clock frequency for Channel 1
		\return  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	FS_HIGH_CH_TDE get_clock_frequency_for_ch_1(void);

	/**
		\brief get Clock frequency for Channel 2
		\return  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	FS_HIGH_CH_TDE get_clock_frequency_for_ch_2(void);

	/**
		\brief get Clock frequency for Channel 3
		\return  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	FS_HIGH_CH_TDE get_clock_frequency_for_ch_3(void);

	/**
		\brief get Clock frequency in Hertz
		\param [in] clk_frequency  -  Clock frequency for channel(FS_HIGH_CH_TDE)
	 */
	uint32_t get_clock_frequency_in_hertz(FS_HIGH_CH_TDE clk_frequency);

	/**
		\brief set shut down the instrumentation amplifier for Channel 1
		\param [in] enable  - Shut down the instrumentation amplifier for Channel state(if true - INA is OFF)
	 */
	void set_shutdown_INA_CH_1(bool enable);

	/**
		\brief set shut down the instrumentation amplifier for Channel 2
		\param [in] enable  - Shut down the instrumentation amplifier for Channel state(if true - INA is OFF)
	 */
	void set_shutdown_INA_CH_2(bool enable);

	/**
		\brief set shut down the instrumentation amplifier for Channel 3
		\param [in] enable  - Shut down the instrumentation amplifier for Channel state(if true - INA is OFF)
	 */
	void set_shutdown_INA_CH_3(bool enable);

	/**
		\brief get shut down the instrumentation amplifier for Channel 1
		\return  - Shut down the instrumentation amplifier for Channel state(if true - INA is OFF)
	 */
	bool get_shutdown_INA_CH_1(void);

	/**
		\brief get shut down the instrumentation amplifier for Channel 2
		\return  - Shut down the instrumentation amplifier for Channel state(if true - INA is OFF)
	 */
	bool get_shutdown_INA_CH_2(void);

	/**
		\brief get shut down the instrumentation amplifier for Channel 3
		\return  - Shut down the instrumentation amplifier for Channel state(if true - INA is OFF)
	 */
	bool get_shutdown_INA_CH_3(void);

	/**
		\brief set shut down the sigma-delta modulator for Channel 1
		\param [in] enable  - Shut down the sigma-delta modulator for Channel state(if true - SD modulator is OFF)
	 */
	void set_shutdown_SD_modulator_CH_1(bool enable);

	/**
		\brief set shut down the sigma-delta modulator for Channel 2
		\param [in] enable  - Shut down the sigma-delta modulator for Channel state(if true - SD modulator is OFF)
	 */
	void set_shutdown_SD_modulator_CH_2(bool enable);

	/**
		\brief set shut down the sigma-delta modulator for Channel 3
		\param [in] enable  - Shut down the sigma-delta modulator for Channel state(if true - SD modulator is OFF)
	 */
	void set_shutdown_SD_modulator_CH_3(bool enable);

	/**
		\brief get shut down the sigma-delta modulator for Channel 1
		\return  - Shut down the sigma-delta modulator for Channel state(if true - SD modulator is OFF)
	 */
	bool get_shutdown_SD_modulator_CH_1(void);

	/**
		\brief get shut down the sigma-delta modulator for Channel 2
		\return  - Shut down the sigma-delta modulator for Channel state(if true - SD modulator is OFF)
	 */
	bool get_shutdown_SD_modulator_CH_2(void);

	/**
		\brief get shut down the sigma-delta modulator for Channel 3
		\return  - Shut down the sigma-delta modulator for Channel state(if true - SD modulator is OFF)
	 */
	bool get_shutdown_SD_modulator_CH_3(void);


	/**
		\brief set shut down the instrumentation amplifier fault detection for Channel 1
		\param [in] enable  - Shut down the INA fault detection for Channel state(if true - fault detector is Disable)
	 */
	void set_shutdown_INA_fault_detect_CH_1(bool enable);

	/**
		\brief set shut down the instrumentation amplifier fault detection for Channel 2
		\param [in] enable  - Shut down the INA fault detection for Channel state(if true - fault detector is Disable)
	 */
	void set_shutdown_INA_fault_detect_CH_2(bool enable);

	/**
		\brief set shut down the instrumentation amplifier fault detection for Channel 3
		\param [in] enable  - Shut down the INA fault detection for Channel state(if true - fault detector is Disable)
	 */
	void set_shutdown_INA_fault_detect_CH_3(bool enable);

	/**
		\brief get shut down the instrumentation amplifier fault detection for Channel 1
		\return  - Shut down the INA fault detection for Channel state(if true - fault detector is Disable)
	 */
	bool get_shutdown_INA_fault_detect_CH_1(void);

	/**
		\brief get shut down the instrumentation amplifier fault detection for Channel 2
		\return  - Shut down the INA fault detection for Channel state(if true - fault detector is Disable)
	 */
	bool get_shutdown_INA_fault_detect_CH_2(void);

	/**
		\brief get shut down the instrumentation amplifier fault detection for Channel 3
		\return  - Shut down the INA fault detection for Channel state(if true - fault detector is Disable)
	 */
	bool get_shutdown_INA_fault_detect_CH_3(void);


	/**
		\brief set shut down analog pace channel
		\param [in] enable  - Shut down analog pace channel state(if true - analog pace channel is Disable)
	 */
	void set_shutdown_analog_pace_channel(bool enable);

	/**
		\brief get shut down analog pace channel
		\return  - Shut down analog pace channel state(if true - analog pace channel is Disable)
	 */
	bool get_shutdown_analog_pace_channel(void);

	/**
		\brief set connect the analog pace channel output to WCT pin
		\param [in] enable  - Connect the analog pace channel output to WCT pin state(if true - analog pace channel output is connect WCT pin)
	 */
	void set_connect_pace_ch_output_to_WCT(bool enable);

	/**
		\brief get connect the analog pace channel output to WCT pin
		\return - Connect the analog pace channel output to WCT pin state(if true - analog pace channel output is connect WCT pin)
	 */
	bool get_connect_pace_ch_output_to_WCT(void);

	/**
		\brief set connect the analog pace channel output to RLDIN pin
		\param [in] enable  - Connect the analog pace channel output to RLDIN pin state(if true - analog pace channel output is connect RLDIN pin)
	 */
	void set_connect_pace_ch_output_to_RLDIN(bool enable);

	/**
		\brief get connect the analog pace channel output to RLDIN pin
		\return - Connect the analog pace channel output to RLDIN pin state(if true - analog pace channel output is connect RLDIN pin)
	 */
	bool get_connect_pace_ch_output_to_RLDIN(void);

	/**
		\brief get Lead-Off Detect Error Status
		\return - Lead-Off Detect Error Status (RG_ERROR_LOD_TDS)
	 */
	RG_ERROR_LOD_TDS& get_leadoff_detect_error_status(void);

	/**
		\brief get Analog Other Error Status
		\return - Analog Other Error Status (RG_ERROR_STATUS_TDS)
	 */
	RG_ERROR_STATUS_TDS& get_analog_other_error_status(void);

	/**
		\brief get AFE Out-of-Range Status channel 1
		\return - Channel AFE Out-of-Range Status (RG_ERROR_RANGE_TDS)
	 */
	RG_ERROR_RANGE_TDS& get_AFE_out_of_range_status_CH_1(void);

	/**
		\brief get AFE Out-of-Range Status channel 2
		\return - Channel AFE Out-of-Range Status (RG_ERROR_RANGE_TDS)
	 */
	RG_ERROR_RANGE_TDS& get_AFE_out_of_range_status_CH_2(void);

	/**
		\brief get AFE Out-of-Range Status channel 3
		\return - Channel AFE Out-of-Range Status (RG_ERROR_RANGE_TDS)
	 */
	RG_ERROR_RANGE_TDS& get_AFE_out_of_range_status_CH_3(void);

	/**
		\brief get Synchronization Error Status
		\return - Synchronization Error Status (RG_ERROR_SYNC_TDS)
	 */
	RG_ERROR_SYNC_TDS& get_synchronization_error_status(void);

	/**
		\brief get Miscellaneous Errors  Status
		\return - Miscellaneous Errors  Status (RG_ERROR_MISC_TDS)
	 */
	RG_ERROR_MISC_TDS& get_miscellaneous_error_status(void);


	/**
		\brief set Digital Output Drive Strength
		\param [in] strenght -  Digital Output Drive Strength(DIGO_STRENGTH_TDE)
	 */
	void set_digital_output_drive_strength(DIGO_STRENGTH_TDE strenght);

	/**
		\brief get Digital Output Drive Strength
		\return  -  Digital Output Drive Strength(DIGO_STRENGTH_TDE)
	 */
	DIGO_STRENGTH_TDE get_digital_output_drive_strength(void);


	/**
		\brief set R2 Decimation Rate
		\param [in] rate -  R2 Decimation Rate(R2_RATE_TDE)
	 */
	void set_R2_decimation_rate(R2_RATE_TDE rate);

	/**
		\brief get R2 Decimation Rate
		\return -  R2 Decimation Rate(R2_RATE_TDE)
	 */
	R2_RATE_TDE get_R2_decimation_rate(void);

	/**
		\brief get R2 Decimation Rate in number for channel
		\param [in] rate -  R3 Decimation Rate(R2_RATE_TDE)
	 */
	uint32_t get_R2_decimation_rate_in_number(R2_RATE_TDE rate);

	/**
		\brief set R3 Decimation Rate for channel 1
		\param [in] rate -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	void set_R3_decimation_rate_for_CH_1(R3_RATE_TDE rate);

	/**
		\brief set R3 Decimation Rate for channel 2
		\param [in] rate -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	void set_R3_decimation_rate_for_CH_2(R3_RATE_TDE rate);

	/**
		\brief set R3 Decimation Rate for channel 3
		\param [in] rate -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	void set_R3_decimation_rate_for_CH_3(R3_RATE_TDE rate);

	/**
		\brief get R3 Decimation Rate for channel 1
		\return -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	R3_RATE_TDE get_R3_decimation_rate_for_CH_1(void);

	/**
		\brief get R3 Decimation Rate for channel 2
		\return -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	R3_RATE_TDE get_R3_decimation_rate_for_CH_2(void);

	/**
		\brief get R3 Decimation Rate for channel 3
		\return -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	R3_RATE_TDE get_R3_decimation_rate_for_CH_3(void);

	/**
		\brief get R3 Decimation Rate in number for channel
		\param [in] rate -  R3 Decimation Rate(R3_RATE_TDE)
	 */
	uint32_t get_R3_decimation_rate_in_number(R3_RATE_TDE rate);

	/**
		\brief set R1 Decimation Rate for channel 1
		\param [in] rate -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	void set_R1_decimation_rate_for_CH_1(R1_RATE_TDE rate);

	/**
		\brief set R1 Decimation Rate for channel 2
		\param [in] rate -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	void set_R1_decimation_rate_for_CH_2(R1_RATE_TDE rate);

	/**
		\brief set R1 Decimation Rate for channel 3
		\param [in] rate -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	void set_R1_decimation_rate_for_CH_3(R1_RATE_TDE rate);

	/**
		\brief get R1 Decimation Rate for channel 1
		\return -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	R1_RATE_TDE get_R1_decimation_rate_for_CH_1(void);

	/**
		\brief get R1 Decimation Rate for channel 2
		\return -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	R1_RATE_TDE get_R1_decimation_rate_for_CH_2(void);

	/**
		\brief get R1 Decimation Rate for channel 3
		\return -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	R1_RATE_TDE get_R1_decimation_rate_for_CH_3(void);

	/**
		\brief get R1 Decimation Rate in number for channel
		\param [in] rate -  R1 Decimation Rate(R1_RATE_TDE)
	 */
	uint32_t get_R1_decimation_rate_in_number(R1_RATE_TDE rate);

	/**
		\brief set ECG Filter Disable for channel 1
		\param [in] disable -  ECG Filter Disable for channel state (if true ECG filter is disable)
	 */
	void set_ECG_filter_disable_for_ch_1(bool disable);

	/**
		\brief set ECG Filter Disable for channel 2
		\param [in] disable -  ECG Filter Disable for channel state (if true ECG filter is disable)
	 */
	void set_ECG_filter_disable_for_ch_2(bool disable);

	/**
		\brief set ECG Filter Disable for channel 3
		\param [in] disable -  ECG Filter Disable for channel state (if true ECG filter is disable)
	 */
	void set_ECG_filter_disable_for_ch_3(bool disable);

	/**
		\brief get ECG Filter Disable for channel 1
		\return -  ECG Filter Disable for channel state (if true ECG filter is disable)
	 */
	bool get_ECG_filter_disable_for_ch_1(void);

	/**
		\brief get ECG Filter Disable for channel 2
		\return -  ECG Filter Disable for channel state (if true ECG filter is disable)
	 */
	bool get_ECG_filter_disable_for_ch_2(void);

	/**
		\brief get ECG Filter Disable for channel 3
		\return -  ECG Filter Disable for channel state (if true ECG filter is disable)
	 */
	bool get_ECG_filter_disable_for_ch_3(void);

	/**
		\brief set Data Ready(DRDYB) Pin Source
		\param [in] pin_source -  Data Ready Pin Source(DRDYB_SRC_TDE)
	 */
	void set_DRDYB_pin_source(DRDYB_SRC_TDE source);

	/**
		\brief get Data Ready(DRDYB) Pin Source
		\return -  Data Ready Pin Source(DRDYB_SRC_TDE)
	 */
	DRDYB_SRC_TDE get_DRDYB_pin_source(void);

	/**
		\brief set Disable the SYNCB pin output driver
		\param [in] disable -  Disable the SYNCB pin output driver (if true SYNCB pin output driver is disable)
	 */
	void set_disable_SYNCB_output_driver(bool disable);

	/**
		\brief set Disable the SYNCB pin output driver
		\return -  Disable the SYNCB pin output driver (if true SYNCB pin output driver is disable)
	 */
	bool get_disable_SYNCB_output_driver(void);

	/**
		\brief set sync (SYNCB) Pin Source
		\param [in] pin_source -  sync (SYNCB) Pin Source(SYNCB_SRC_TDE)
	 */
	void set_SYNCB_pin_source(SYNCB_SRC_TDE source);

	/**
		\brief get sync (SYNCB) Pin Source
		\return -  sync (SYNCB) Pin Source(SYNCB_SRC_TDE)
	 */
	SYNCB_SRC_TDE get_SYNCB_pin_source(void);


	/**
		\brief set Mask alarm condition for CMOR=1
		\param [in] enable -  Mask alarm condition for CMOR=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_CMOR(bool enable);

	/**
		\brief get Mask alarm condition for CMOR=1
		\return -  Mask alarm condition for CMOR=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_CMOR(void);

	/**
		\brief set Mask alarm condition for RLDRAIL=1
		\param [in] enable -  Mask alarm condition for RLDRAIL=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_RLDRAIL(bool enable);

	/**
		\brief get Mask alarm condition for RLDRAIL=1
		\return -  Mask alarm condition for RLDRAIL1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_RLDRAIL(void);

	/**
		\brief set Mask alarm condition for BATLOW=1
		\param [in] enable -  Mask alarm condition for BATLOW=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_BATLOW(bool enable);

	/**
		\brief get Mask alarm condition for BATLOW=1
		\return -  Mask alarm condition for BATLOW=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_BATLOW(void);

	/**
		\brief set Mask alarm condition for LEADOFF=1
		\param [in] enable -  Mask alarm condition for LEADOFF=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_LEADOFF(bool enable);

	/**
		\brief get Mask alarm condition for LEADOFF=1
		\return -  Mask alarm condition for LEADOFF=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_LEADOFF(void);

	/**
		\brief set Mask alarm condition for CH1ERR=1
		\param [in] enable -  Mask alarm condition for CH1ERR=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_CH1ERR(bool enable);

	/**
		\brief get Mask alarm condition for CH1ERR=1
		\return -  Mask alarm condition for CH1ERR=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_CH1ERR(void);

	/**
		\brief set Mask alarm condition for CH2ERR=1
		\param [in] enable -  Mask alarm condition for CH2ERR=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_CH2ERR(bool enable);

	/**
		\brief get Mask alarm condition for CH2ERR=1
		\return -  Mask alarm condition for CH2ERR=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_CH2ERR(void);

	/**
		\brief set Mask alarm condition for CH3ERR=1
		\param [in] enable -  Mask alarm condition for CH3ERR=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_CH3ERR(bool enable);

	/**
		\brief get Mask alarm condition for CH3ERR=1
		\return -  Mask alarm condition for CH3ERR=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_CH3ERR(void);

	/**
		\brief set Mask alarm condition for SYNCEDGEER=1
		\param [in] enable -  Mask alarm condition for SYNCEDGEER=1 state(if true alarm is masked)
	 */
	void set_mask_alarm_for_SYNCEDGEER(bool enable);

	/**
		\brief get Mask alarm condition for SYNCEDGEER=1
		\return -  Mask alarm condition for SYNCEDGEER=1 state(if true alarm is masked)
	 */
	bool get_mask_alarm_for_SYNCEDGEER(void);


	/**
		\brief set Digital Filter for  Alarm Signals (Lead-Off Detect)
		\param [in] DF_value -   Number of consecutive lead off alarm signal counts +1 before ALARMB is asserted.(max:15)
	 */
	void set_DF_for_LOD_alarm_signal(uint8_t DF_value);

	/**
		\brief get Digital Filter for  Alarm Signals (Lead-Off Detect)
		\return -   Number of consecutive lead off alarm signal counts +1 before ALARMB is asserted.(max:15)
	 */
	uint8_t get_DF_for_LOD_alarm_signal(void);

	/**
		\brief set Digital Filter for  Alarm Signals (other)
		\param [in] DF_value -   Number of consecutive alarm signal counts +1 before ALARMB is asserted.(max:15)
	 */
	void set_DF_for_other_alarm_signal(uint8_t DF_value);

	/**
		\brief get Digital Filter for  Alarm Signals (other)
		\param [in] DF_value -   Number of consecutive alarm signal counts +1 before ALARMB is asserted.(max:15)
	 */
	uint8_t get_DF_for_other_alarm_signal(void);

	/**
		\brief set Configure DATA_STATUS for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_DATA_STATUS_read_back_mode(bool enable);

	/**
		\brief set Configure DATA_STATUS for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_DATA_STATUS_read_back_mode(void);


	/**
		\brief set Configure CH1_PACE for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_CH1_PACE_read_back_mode(bool enable);

	/**
		\brief set Configure CH1_PACE for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_CH1_PACE_read_back_mode(void);

	/**
		\brief set Configure CH2_PACE for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_CH2_PACE_read_back_mode(bool enable);

	/**
		\brief set Configure CH2_PACE for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_CH2_PACE_read_back_mode(void);


	/**
		\brief set Configure CH3_PACE for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_CH3_PACE_read_back_mode(bool enable);

	/**
		\brief set Configure CH3_PACE for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_CH3_PACE_read_back_mode(void);


	/**
		\brief set Configure CH1_ECG for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_CH1_ECG_read_back_mode(bool enable);

	/**
		\brief set Configure CH1_ECG for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_CH1_ECG_read_back_mode(void);

	/**
		\brief set Configure CH2_ECG for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_CH2_ECG_read_back_mode(bool enable);

	/**
		\brief set Configure CH2_ECG for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_CH2_ECG_read_back_mode(void);

	/**
		\brief set Configure CH3_ECG for Loop Read Back Mode
		\param [in] enable -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	void set_CH3_ECG_read_back_mode(bool enable);

	/**
		\brief set Configure CH3_ECG for Loop Read Back Mode
		\return -  Configure for Loop Read Back Mode(if true read back is enable)
	 */
	bool get_CH3_ECG_read_back_mode(void);

	/**
		\brief get ECG and Pace Data Ready Status
		\return -  ECG and Pace Data Ready Status (RG_DATA_STATUS_TDS)
	 */
	RG_DATA_STATUS_TDS& get_data_ready_status(void);


	/**
		\brief get ECG output data rate for channel 1
		\return -  ECG output data rate for channel (Hz)
	 */
	uint32_t get_ECG_data_rate_CH_1(void);

	/**
		\brief get ECG output data rate for channel 2
		\return -  ECG output data rate for channel (Hz)
	 */
	uint32_t get_ECG_data_rate_CH_2(void);

	/**
		\brief get ECG output data rate for channel 3
		\return -  ECG output data rate for channel (Hz)
	 */
	uint32_t get_ECG_data_rate_CH_3(void);

	/**
		\brief get pace output data rate for channel 1
		\return -  pace output data rate for channel (Hz)
	 */
	uint32_t get_pace_data_rate_CH_1(void);

	/**
		\brief get pace output data rate for channel 2
		\return -  pace output data rate for channel (Hz)
	 */
	uint32_t get_pace_data_rate_CH_2(void);

	/**
		\brief get pace output data rate for channel 3
		\return -  pace output data rate for channel (Hz)
	 */
	uint32_t get_pace_data_rate_CH_3(void);

	/**
		\brief get pace output data  for channel 1
		\return -  pace output data for channel (ADC unit)
	 */
	uint16_t get_pace_data_CH_1(void);

	/**
		\brief get pace output data  for channel 2
		\return -  pace output data for channel (ADC unit)
	 */
	uint16_t get_pace_data_CH_2(void);

	/**
		\brief get pace output data  for channel 3
		\return -  pace output data for channel (ADC unit)
	 */
	uint16_t get_pace_data_CH_3(void);

	/**
		\brief get ECG output data for channel 1
		\return -  ECG output data for channel (ADC unit)
	 */
	uint32_t get_ECG_data_CH_1(void);

	/**
		\brief get ECG output data for channel 2
		\return -  ECG output data for channel (ADC unit)
	 */
	uint32_t get_ECG_data_CH_2(void);

	/**
		\brief get ECG output data for channel 3
		\return -  ECG output data for channel (ADC unit)
	 */
	uint32_t get_ECG_data_CH_3(void);

    /**
		\brief load all register from ADS1293
	 */
	void load_all_registers(void);
private:




	//constants__________________________________________________________________________________________
	const uint32_t LEADOFF_DETECTION_CURRENT_PER_UNIT=8; //in (nA) nanoampere
	const uint32_t MAX_LEADOFF_DETECTION_CURRENT=2040; //in (nA) nanoampere

	//Variables__________________________________________________________________________________________
	ADS1293_IO _IO; //ADS1293 input/output object


	//Operation Mode Registers
	register_container <RG_CONFIG_TDS> R_CONFIG{&_IO,RL_CONFIG}; //0x00 Main Configuration ( R/W ) *default: 0x02
	//Input Channel Selection Registers
	register_container <RG_FLEX_CH_CN_TDS> R_FLEX_CH1_CN{&_IO,RL_FLEX_CH1_CN}; //0x01 Flex Routing Switch Control for Channel 1 ( R/W ) *default: 0x00
	register_container <RG_FLEX_CH_CN_TDS> R_FLEX_CH2_CN{&_IO,RL_FLEX_CH2_CN}; //0x02 Flex Routing Switch Control for Channel 2 ( R/W ) *default: 0x00
	register_container <RG_FLEX_CH_CN_TDS> R_FLEX_CH3_CN{&_IO,RL_FLEX_CH3_CN}; //0x03 Flex Routing Switch Control for Channel 3 ( R/W ) *default: 0x00
	register_container <RG_FLEX_CH_CN_TDS> R_FLEX_PACE_CN{&_IO,RL_FLEX_PACE_CN}; //0x04 Flex Routing Switch Control for Pace Channel ( R/W ) *default: 0x00
	register_container <RG_FLEX_VBAT_CN_TDS> R_FLEX_VBAT_CN{&_IO,RL_FLEX_VBAT_CN}; //0x05 Flex Routing Switch for Battery Monitoring ( R/W ) *default: 0x00
	//Lead-off Detect Control Registers
	register_container <RG_LOD_CN_TDS> R_LOD_CN{&_IO,RL_LOD_CN}; //0x06 Lead-Off Detect Control ( R/W ) *default: 0x08
	register_container <RG_LOD_EN_TDS> R_LOD_EN{&_IO,RL_LOD_EN}; //0x07 Lead-Off Detect Enable ( R/W ) *default: 0x00
	register_container <RG_LOD_CURRENT_TDS> R_LOD_CURRENT{&_IO,RL_LOD_CURRENT}; //0x08 Lead-Off Detect Current ( R/W ) *default: 0x00
	register_container <RG_LOD_AC_CN_TDS> R_LOD_AC_CN{&_IO,RL_LOD_AC_CN}; //0x09 AC Lead-Off Detect Control ( R/W ) *default: 0x00
	//Common-Mode Detection and Right-Leg Drive Feedback Control Registers
	register_container <RG_CMDET_EN_TDS> R_CMDET_EN{&_IO,RL_CMDET_CN}; //0x0A Common-Mode Detect Enable ( R/W ) *default: 0x00
	register_container <RG_CMDET_CN_TDS> R_CMDET_CN{&_IO,RL_CMDET_EN}; //0x0B Common-Mode Detect Control ( R/W ) *default: 0x00
	register_container <RG_RLD_CN_TDS> R_RLD_CN{&_IO,RL_RLD_CN}; //0x0C Right-Leg Drive Control ( R/W ) *default: 0x00
	//Wilson Control Registers
	register_container <RG_WILSON_EN_TDS> R_WILSON_EN1{&_IO,RL_WILSON_EN1}; //0x0D Wilson Reference Input one Selection ( R/W ) *default: 0x00
	register_container <RG_WILSON_EN_TDS> R_WILSON_EN2{&_IO,RL_WILSON_EN2}; //0x0E Wilson Reference Input two Selection ( R/W ) *default: 0x00
	register_container <RG_WILSON_EN_TDS> R_WILSON_EN3{&_IO,RL_WILSON_EN3}; //0x0F Wilson Reference Input three Selection ( R/W ) *default: 0x00
	register_container <RG_WILSON_CN_TDS> R_WILSON_CN{&_IO,RL_WILSON_CN}; //0x10 Wilson Reference Control ( R/W ) *default: 0x00
	//Reference Registers
	register_container <RG_REF_CN_TDS> R_REF_CN{&_IO,RL_REF_CN}; //0x11 Internal Reference Voltage Control ( R/W ) *default: 0x00
	//OSC Control Registers
	register_container <RG_OSC_CN_TDS> R_OSC_CN{&_IO,RL_OSC_CN}; //0x12 Clock Source and Output Clock Control ( R/W ) *default: 0x00
	//AFE Control Registers
	register_container <RG_AFE_RES_TDS> R_AFE_RES{&_IO,RL_AFE_RES}; //0x13 Analog Front End Frequency and Resolution ( R/W ) *default: 0x00
	register_container <RG_AFE_SHDN_CN_TDS> R_AFE_SHDN_CN{&_IO,RL_AFE_SHDN_CN}; //0x14 Analog Front End Shutdown Control ( R/W ) *default: 0x00
	register_container <RG_AFE_FAULT_CN_TDS> R_AFE_FAULT_CN{&_IO,RL_AFE_FAULT_CN}; //0x15 Analog Front End Fault Detection Control ( R/W ) *default: 0x00
	register_container <RG_AFE_PACE_CN_TDS> R_AFE_PACE_CN{&_IO,RL_AFE_PACE_CN}; //0x17 Analog Pace Channel Output Routing Control ( R/W ) *default: 0x01
	//Error Status Registers
	register_container <RG_ERROR_LOD_TDS> R_ERROR_LOD{&_IO,RL_ERROR_LOD}; //0x18 Lead-Off Detect Error Status ( RO ) *default: —
	register_container <RG_ERROR_STATUS_TDS> R_ERROR_STATUS{&_IO,RL_ERROR_STATUS}; //0x19 Other Error Status ( RO ) *default: —
	register_container <RG_ERROR_RANGE_TDS> R_ERROR_RANGE1{&_IO,RL_ERROR_RANGE1}; //0x1A Channel 1 AFE Out-of-Range Status ( RO ) *default: —
	register_container <RG_ERROR_RANGE_TDS> R_ERROR_RANGE2{&_IO,RL_ERROR_RANGE2}; //0x1B Channel 2 AFE Out-of-Range Status ( RO ) *default: —
	register_container <RG_ERROR_RANGE_TDS> R_ERROR_RANGE3{&_IO,RL_ERROR_RANGE3}; //0x1C Channel 3 AFE Out-of-Range Status ( RO ) *default: —
	register_container <RG_ERROR_SYNC_TDS> R_ERROR_SYNC{&_IO,RL_ERROR_STATUS}; //0x1D Synchronization Error ( RO ) *default: —
	register_container <RG_ERROR_MISC_TDS> R_ERROR_MISC{&_IO,RL_ERROR_MISC}; //0x1E Miscellaneous Errors ( RO ) *default: 0x00
	//Digital Registers
	register_container <RG_DIGO_STRENGTH_TDS> R_DIGO_STRENGTH{&_IO,RL_DIGO_STRENGTH}; //0x1F Digital Output Drive Strength ( R/W ) *default: 0x03
	register_container <RG_R2_RATE_TDS> R_R2_RATE{&_IO,RL_R2_RATE}; //0x21 R2 Decimation Rate ( R/W ) *default: 0x08
	register_container <RG_R3_RATE_TDS> R_R3_RATE_CH1{&_IO,RL_R3_RATE_CH1}; //0x22 R3 Decimation Rate for Channel 1 ( R/W ) *default: 0x80
	register_container <RG_R3_RATE_TDS> R_R3_RATE_CH2{&_IO,RL_R3_RATE_CH2}; //0x23 R3 Decimation Rate for Channel 2 ( R/W ) *default: 0x80
	register_container <RG_R3_RATE_TDS> R_R3_RATE_CH3{&_IO,RL_R3_RATE_CH3}; //0x24 R3 Decimation Rate for Channel 3 ( R/W ) *default: 0x80
	register_container <RG_R1_RATE_TDS> R_R1_RATE{&_IO,RL_R1_RATE}; //0x25 R1 Decimation Rate ( R/W ) *default: 0x00
	register_container <RG_DIS_EFILTER_TDS> R_DIS_EFILTER{&_IO,RL_DIS_EFILTER}; //0x26 ECG Filter Disable ( R/W ) *default: 0x00
	register_container <RG_DRDYB_SRC_TDS> R_DRDYB_SRC{&_IO,RL_DRDYB_SRC}; //0x27 Data Ready Pin Source ( R/W ) *default: 0x00
	register_container <RG_DIS_SYNCBOUT_TDS> R_SYNCB_CN{&_IO,RL_SYNCB_CN}; //0x28 SYNCB In/Out Pin Control ( R/W ) *default: 0x40
	register_container <RG_MASK_DRDYB_TDS> R_MASK_DRDYB{&_IO,RL_MASK_DRDYB}; //0x29 Optional Mask Control for DRDYB Output ( R/W ) *default: 0x00
	register_container <RG_MASK_ERR_TDS> R_MASK_ERR{&_IO,RL_MASK_ERR}; //0x2A Mask Error on ALARMB Pin ( R/W ) *default: 0x00
	register_container <RG_ALARM_FILTER_TDS> R_ALARM_FILTER{&_IO,RL_ALARM_FILTER}; //0x2E Digital Filter for Analog Alarm Signals ( R/W ) *default: 0x33
	register_container <RG_CH_CNFG_TDS> R_CH_CNFG{&_IO,RL_CH_CNFG}; //0x2F Configure Channel for Loop Read Back Mode ( R/W ) *default: 0x00
	//Pace and ECG Data Read Back Registers
	register_container <RG_DATA_STATUS_TDS> R_DATA_STATUS{&_IO,RL_DATA_STATUS}; //0x30 ECG and Pace Data Ready Status ( RO ) *default: —
};



inline ADS1293::ADS1293_LIB::ADS1293_LIB(VT_sync_data_stream_interface *_SPI_driver_pointer)
{
	_IO.init(_SPI_driver_pointer);
	load_all_registers();
}

inline void ADS1293::ADS1293_LIB::set_conversion_state(bool enable)
{
	R_CONFIG.load_register();
	R_CONFIG.S.START_CON=enable;
	R_CONFIG.update_register();
}

inline void ADS1293::ADS1293_LIB::set_standby_mode(bool enable)
{
	R_CONFIG.load_register();
	R_CONFIG.S.STANDBY=enable;
	R_CONFIG.update_register();
}

inline void ADS1293::ADS1293_LIB::set_powerdown_mode(bool enable)
{
	R_CONFIG.load_register();
	R_CONFIG.S.PWR_DOWN=enable;
	R_CONFIG.update_register();
}

inline bool ADS1293::ADS1293_LIB::get_conversion_state(void)
{
	R_CONFIG.load_register();
	return R_CONFIG.S.START_CON;
}

inline bool ADS1293::ADS1293_LIB::get_standby_mode(void)
{
	R_CONFIG.load_register();
	return R_CONFIG.S.STANDBY;
}

inline bool ADS1293::ADS1293_LIB::get_powerdown_mode(void)
{
	R_CONFIG.load_register();
	return R_CONFIG.S.PWR_DOWN;
}

inline void ADS1293::ADS1293_LIB::set_test_signal_for_ch_1(TEST_SIGNAL_SELECTOR_TDE test_signal)
{
	R_FLEX_CH1_CN.load_register();
	R_FLEX_CH1_CN.S.TST=test_signal;
	R_FLEX_CH1_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_positive_terminal_for_ch_1(INPUT_SELECTOR_TDE input)
{
	R_FLEX_CH1_CN.load_register();
	R_FLEX_CH1_CN.S.POS=input;
	R_FLEX_CH1_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_negative_terminal_for_ch_1(INPUT_SELECTOR_TDE input)
{
	R_FLEX_CH1_CN.load_register();
	R_FLEX_CH1_CN.S.NEG=input;
	R_FLEX_CH1_CN.update_register();
}

inline TEST_SIGNAL_SELECTOR_TDE ADS1293::ADS1293_LIB::get_test_signal_for_ch_1(void)
{
	R_FLEX_CH1_CN.load_register();
	return R_FLEX_CH1_CN.S.TST;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_positive_terminal_for_ch_1(void)
{
	R_FLEX_CH1_CN.load_register();
	return R_FLEX_CH1_CN.S.POS;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_negative_terminal_for_ch_1(void)
{
	R_FLEX_CH1_CN.load_register();
	return R_FLEX_CH1_CN.S.NEG;
}

inline void ADS1293::ADS1293_LIB::set_test_signal_for_ch_2(TEST_SIGNAL_SELECTOR_TDE test_signal)
{
	R_FLEX_CH2_CN.load_register();
	R_FLEX_CH2_CN.S.TST=test_signal;
	R_FLEX_CH2_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_positive_terminal_for_ch_2(INPUT_SELECTOR_TDE input)
{
	R_FLEX_CH2_CN.load_register();
	R_FLEX_CH2_CN.S.POS=input;
	R_FLEX_CH2_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_negative_terminal_for_ch_2(INPUT_SELECTOR_TDE input)
{
	R_FLEX_CH2_CN.load_register();
	R_FLEX_CH2_CN.S.NEG=input;
	R_FLEX_CH2_CN.update_register();
}

inline TEST_SIGNAL_SELECTOR_TDE ADS1293::ADS1293_LIB::get_test_signal_for_ch_2(void)
{
	R_FLEX_CH2_CN.load_register();
	return R_FLEX_CH2_CN.S.TST;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_positive_terminal_for_ch_2(void)
{
	R_FLEX_CH2_CN.load_register();
	return R_FLEX_CH2_CN.S.POS;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_negative_terminal_for_ch_2(void)
{
	R_FLEX_CH2_CN.load_register();
	return R_FLEX_CH2_CN.S.NEG;
}

inline void ADS1293::ADS1293_LIB::set_test_signal_for_ch_3(TEST_SIGNAL_SELECTOR_TDE test_signal)
{
	R_FLEX_CH3_CN.load_register();
	R_FLEX_CH3_CN.S.TST=test_signal;
	R_FLEX_CH3_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_positive_terminal_for_ch_3(INPUT_SELECTOR_TDE input)
{
	R_FLEX_CH3_CN.load_register();
	R_FLEX_CH3_CN.S.POS=input;
	R_FLEX_CH3_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_negative_terminal_for_ch_3(INPUT_SELECTOR_TDE input)
{
	R_FLEX_CH3_CN.load_register();
	R_FLEX_CH3_CN.S.NEG=input;
	R_FLEX_CH3_CN.update_register();
}

inline TEST_SIGNAL_SELECTOR_TDE ADS1293::ADS1293_LIB::get_test_signal_for_ch_3(void)
{
	R_FLEX_CH3_CN.load_register();
	return R_FLEX_CH3_CN.S.TST;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_positive_terminal_for_ch_3(void)
{
	R_FLEX_CH3_CN.load_register();
	return R_FLEX_CH3_CN.S.POS;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_negative_terminal_for_ch_3(void)
{
	R_FLEX_CH3_CN.load_register();
	return R_FLEX_CH3_CN.S.NEG;
}

inline void ADS1293::ADS1293_LIB::set_test_signal_for_pace_channel(TEST_SIGNAL_SELECTOR_TDE test_signal)
{
	R_FLEX_PACE_CN.load_register();
	R_FLEX_PACE_CN.S.TST=test_signal;
	R_FLEX_PACE_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_positive_terminal_for_pace_channel(INPUT_SELECTOR_TDE input)
{
	R_FLEX_PACE_CN.load_register();
	R_FLEX_PACE_CN.S.POS=input;
	R_FLEX_PACE_CN.update_register();
}

inline void ADS1293::ADS1293_LIB::set_negative_terminal_for_pace_channel(INPUT_SELECTOR_TDE input)
{
	R_FLEX_PACE_CN.load_register();
	R_FLEX_PACE_CN.S.NEG=input;
	R_FLEX_PACE_CN.update_register();
}

inline TEST_SIGNAL_SELECTOR_TDE ADS1293::ADS1293_LIB::get_test_signal_for_pace_channel(void)
{
	R_FLEX_PACE_CN.load_register();
	return R_FLEX_PACE_CN.S.TST;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_positive_terminal_for_pace_channel(void)
{
	R_FLEX_PACE_CN.load_register();
	return R_FLEX_PACE_CN.S.POS;
}

inline INPUT_SELECTOR_TDE ADS1293::ADS1293_LIB::get_negative_terminal_for_pace_channel(void)
{
	R_FLEX_PACE_CN.load_register();
	return R_FLEX_PACE_CN.S.NEG;
}

inline void ADS1293_LIB::set_battery_monitor_for_ch1(bool enable)
{
	R_FLEX_VBAT_CN.load_register();
	R_FLEX_VBAT_CN.S.VBAT_MONI_CH1=enable;
	R_FLEX_VBAT_CN.update_register();
}

inline bool ADS1293_LIB::get_battery_monitor_for_ch1(void)
{
	R_FLEX_VBAT_CN.load_register();
	return R_FLEX_VBAT_CN.S.VBAT_MONI_CH1;
}

inline void ADS1293_LIB::set_battery_monitor_for_ch2(bool enable)
{
	R_FLEX_VBAT_CN.load_register();
	R_FLEX_VBAT_CN.S.VBAT_MONI_CH2=enable;
	R_FLEX_VBAT_CN.update_register();
}

inline bool ADS1293_LIB::get_battery_monitor_for_ch2(void)
{
	R_FLEX_VBAT_CN.load_register();
	return R_FLEX_VBAT_CN.S.VBAT_MONI_CH2;
}

inline void ADS1293_LIB::set_battery_monitor_for_ch3(bool enable)
{
	R_FLEX_VBAT_CN.load_register();
	R_FLEX_VBAT_CN.S.VBAT_MONI_CH3=enable;
	R_FLEX_VBAT_CN.update_register();
}

inline bool ADS1293_LIB::get_battery_monitor_for_ch3(void)
{
	R_FLEX_VBAT_CN.load_register();
	return R_FLEX_VBAT_CN.S.VBAT_MONI_CH3;
}


inline void ADS1293_LIB::set_AC_leadoff_mode(ACAD_LOD_MODE_TDE mode)
{
	R_LOD_CN.load_register();
	R_LOD_CN.S.ACAD_LOD=mode;
	R_LOD_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_leadoff_detection(bool enable)
{
	R_LOD_CN.load_register();
	R_LOD_CN.S.SHDN_LOD=enable;
	R_LOD_CN.update_register();
}

inline void ADS1293_LIB::set_leadoff_detect_mode(SELAC_LOD_MODE_TDE mode)
{
	R_LOD_CN.load_register();
	R_LOD_CN.S.SELAC_LOD=mode;
	R_LOD_CN.update_register();
}

inline void ADS1293_LIB::set_leadoff_AC_comparator_trigger_level(COMPARATOR_TRIGGER_LEVEL_TDE level)
{
	R_LOD_CN.load_register();
	R_LOD_CN.S.ACLVL_LOD=level;
	R_LOD_CN.update_register();
}

inline ACAD_LOD_MODE_TDE ADS1293_LIB::get_AC_leadoff_mode(void)
{
	R_LOD_CN.load_register();
	return R_LOD_CN.S.ACAD_LOD;
}

inline bool ADS1293_LIB::get_shutdown_leadoff_detection(void)
{
	R_LOD_CN.load_register();
	return R_LOD_CN.S.SHDN_LOD;
}

inline SELAC_LOD_MODE_TDE ADS1293_LIB::get_leadoff_detect_mode(void)
{
	R_LOD_CN.load_register();
	return R_LOD_CN.S.SELAC_LOD;
}

inline COMPARATOR_TRIGGER_LEVEL_TDE ADS1293_LIB::get_leadoff_AC_comparator_trigger_level(void)
{
	R_LOD_CN.load_register();
	return R_LOD_CN.S.ACLVL_LOD;
}

inline void ADS1293_LIB::set_leadoff_detection_for_input_1(bool enable)
{
	R_LOD_EN.load_register();
	R_LOD_EN.S.EN_LOD_1=enable;
	R_LOD_EN.update_register();
}

inline void ADS1293_LIB::set_leadoff_detection_for_input_2(bool enable)
{
	R_LOD_EN.load_register();
	R_LOD_EN.S.EN_LOD_2=enable;
	R_LOD_EN.update_register();
}

inline void ADS1293_LIB::set_leadoff_detection_for_input_3(bool enable)
{
	R_LOD_EN.load_register();
	R_LOD_EN.S.EN_LOD_3=enable;
	R_LOD_EN.update_register();
}

inline void ADS1293_LIB::set_leadoff_detection_for_input_4(bool enable)
{
	R_LOD_EN.load_register();
	R_LOD_EN.S.EN_LOD_4=enable;
	R_LOD_EN.update_register();
}

inline void ADS1293_LIB::set_leadoff_detection_for_input_5(bool enable)
{
	R_LOD_EN.load_register();
	R_LOD_EN.S.EN_LOD_5=enable;
	R_LOD_EN.update_register();
}

inline void ADS1293_LIB::set_leadoff_detection_for_input_6(bool enable)
{
	R_LOD_EN.load_register();
	R_LOD_EN.S.EN_LOD_6=enable;
	R_LOD_EN.update_register();
}

inline bool ADS1293_LIB::get_leadoff_detection_for_input_1(void)
{
	R_LOD_EN.load_register();
	return R_LOD_EN.S.EN_LOD_1;
}

inline bool ADS1293_LIB::get_leadoff_detection_for_input_2(void)
{
	R_LOD_EN.load_register();
	return R_LOD_EN.S.EN_LOD_2;
}

inline bool ADS1293_LIB::get_leadoff_detection_for_input_3(void)
{
	R_LOD_EN.load_register();
	return R_LOD_EN.S.EN_LOD_3;
}

inline bool ADS1293_LIB::get_leadoff_detection_for_input_4(void)
{
	R_LOD_EN.load_register();
	return R_LOD_EN.S.EN_LOD_4;
}

inline bool ADS1293_LIB::get_leadoff_detection_for_input_5(void)
{
	R_LOD_EN.load_register();
	return R_LOD_EN.S.EN_LOD_5;
}

inline bool ADS1293_LIB::get_leadoff_detection_for_input_6(void)
{
	R_LOD_EN.load_register();
	return R_LOD_EN.S.EN_LOD_6;
}


inline void ADS1293_LIB::set_leadoff_detection_current(uint32_t current_nA)
{
	if (current_nA>MAX_LEADOFF_DETECTION_CURRENT) {current_nA=MAX_LEADOFF_DETECTION_CURRENT;}
	uint8_t current_unit=current_nA/LEADOFF_DETECTION_CURRENT_PER_UNIT;

	R_LOD_CURRENT.load_register();
	R_LOD_CURRENT.S.CUR_LOD=current_unit;
	R_LOD_CURRENT.update_register();
}

inline uint32_t ADS1293_LIB::get_leadoff_detection_current(void)
{
	R_LOD_CURRENT.load_register();
	uint32_t current_unit=R_LOD_CURRENT.S.CUR_LOD;
	return current_unit*LEADOFF_DETECTION_CURRENT_PER_UNIT;
}

inline void ADS1293_LIB::set_leadoff_frequency_divider(uint8_t divider_ratio,ACDIV_FACTOR_TDE divider_factor)
{
	R_LOD_AC_CN.load_register();
	R_LOD_AC_CN.S.ACDIV_LOD=(divider_ratio & 0x7F);
	R_LOD_AC_CN.S.ACDIV_FACTOR=divider_factor;
	R_LOD_AC_CN.update_register();
}

inline uint32_t ADS1293_LIB::get_AC_leadoff_frequency(void)
{
	//F=50/(4*K*(ACDIV_LOD+1))kHz
	R_LOD_AC_CN.load_register();
	uint32_t div=R_LOD_AC_CN.S.ACDIV_LOD;
	uint32_t K=1;
	if (R_LOD_AC_CN.S.ACDIV_FACTOR==true){K=16;}
	uint32_t frequency=50000/(4*K*(div+1));
	return frequency;
}

inline void ADS1293_LIB::set_common_mode_detection_for_input_1(bool enable)
{
	R_CMDET_EN.load_register();
	R_CMDET_EN.S.CMDET_EN_IN_1=enable;
	R_CMDET_EN.update_register();
}

inline void ADS1293_LIB::set_common_mode_detection_for_input_2(bool enable)
{
	R_CMDET_EN.load_register();
	R_CMDET_EN.S.CMDET_EN_IN_2=enable;
	R_CMDET_EN.update_register();
}

inline void ADS1293_LIB::set_common_mode_detection_for_input_3(bool enable)
{
	R_CMDET_EN.load_register();
	R_CMDET_EN.S.CMDET_EN_IN_3=enable;
	R_CMDET_EN.update_register();
}

inline void ADS1293_LIB::set_common_mode_detection_for_input_4(bool enable)
{
	R_CMDET_EN.load_register();
	R_CMDET_EN.S.CMDET_EN_IN_4=enable;
	R_CMDET_EN.update_register();
}

inline void ADS1293_LIB::set_common_mode_detection_for_input_5(bool enable)
{
	R_CMDET_EN.load_register();
	R_CMDET_EN.S.CMDET_EN_IN_5=enable;
	R_CMDET_EN.update_register();
}

inline void ADS1293_LIB::set_common_mode_detection_for_input_6(bool enable)
{
	R_CMDET_EN.load_register();
	R_CMDET_EN.S.CMDET_EN_IN_6=enable;
	R_CMDET_EN.update_register();
}

inline bool ADS1293_LIB::get_common_mode_detection_for_input_1(void)
{
	R_CMDET_EN.load_register();
	return R_CMDET_EN.S.CMDET_EN_IN_1;
}

inline bool ADS1293_LIB::get_common_mode_detection_for_input_2(void)
{
	R_CMDET_EN.load_register();
	return R_CMDET_EN.S.CMDET_EN_IN_2;
}

inline bool ADS1293_LIB::get_common_mode_detection_for_input_3(void)
{
	R_CMDET_EN.load_register();
	return R_CMDET_EN.S.CMDET_EN_IN_3;
}

inline bool ADS1293_LIB::get_common_mode_detection_for_input_4(void)
{
	R_CMDET_EN.load_register();
	return R_CMDET_EN.S.CMDET_EN_IN_4;
}

inline bool ADS1293_LIB::get_common_mode_detection_for_input_5(void)
{
	R_CMDET_EN.load_register();
	return R_CMDET_EN.S.CMDET_EN_IN_5;
}

inline bool ADS1293_LIB::get_common_mode_detection_for_input_6(void)
{
	R_CMDET_EN.load_register();
	return R_CMDET_EN.S.CMDET_EN_IN_6;
}

inline void ADS1293_LIB::set_common_mode_detect_bandwidth_mode(CMDET_BW_TDE mode)
{
	R_CMDET_CN.load_register();
	R_CMDET_CN.S.CMDET_BW=mode;
	R_CMDET_CN.update_register();
}

inline CMDET_BW_TDE ADS1293_LIB::get_common_mode_detect_bandwidth_mode(void)
{
	R_CMDET_CN.load_register();
	return R_CMDET_CN.S.CMDET_BW;

}

inline void ADS1293_LIB::set_common_mode_detect_cap_load_drive_capability(CMDET_CAPDRIVE_TDE mode)
{
	R_CMDET_CN.load_register();
	R_CMDET_CN.S.CMDET_CAPDRIVE=mode;
	R_CMDET_CN.update_register();
}

inline CMDET_CAPDRIVE_TDE ADS1293_LIB::get_common_mode_detect_cap_load_drive_capability(void)
{
	R_CMDET_CN.load_register();
	return R_CMDET_CN.S.CMDET_CAPDRIVE;
}

inline void ADS1293_LIB::set_right_leg_drive_bandwidth_mode(RG_RLD_BW_TDE mode)
{
	R_RLD_CN.load_register();
	R_RLD_CN.S.RLD_BW=mode;
	R_RLD_CN.update_register();
}

inline RG_RLD_BW_TDE ADS1293_LIB::get_right_leg_drive_bandwidth_mode(void)
{
	R_RLD_CN.load_register();
	return R_RLD_CN.S.RLD_BW;
}

inline void ADS1293_LIB::set_shutdown_right_leg_drive_amplifier(bool enable)
{
	R_RLD_CN.load_register();
	R_RLD_CN.S.SHDN_RLD=enable;
	R_RLD_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_right_leg_drive_amplifier(void)
{
	R_RLD_CN.load_register();
	return R_RLD_CN.S.SHDN_RLD;
}

inline void ADS1293_LIB::set_right_leg_drive_output(INPUT_SELECTOR_TDE input)
{
	R_RLD_CN.load_register();
	R_RLD_CN.S.SELRLD=input;
	R_RLD_CN.update_register();
}

inline INPUT_SELECTOR_TDE ADS1293_LIB::get_right_leg_drive_output(INPUT_SELECTOR_TDE input)
{
	R_RLD_CN.load_register();
	return R_RLD_CN.S.SELRLD;
}

inline void ADS1293_LIB::set_right_leg_detect_cap_load_drive_capability(RG_RLD_CAPDRIVE_TDE mode)
{
	R_RLD_CN.load_register();
	R_RLD_CN.S.RLD_CAPDRIVE=mode;
	R_RLD_CN.update_register();
}

inline RG_RLD_CAPDRIVE_TDE ADS1293_LIB::get_right_leg_detect_cap_load_drive_capability(void)
{
	R_RLD_CN.load_register();
	return R_RLD_CN.S.RLD_CAPDRIVE;
}

inline void ADS1293_LIB::set_wilson_reference_input_1(INPUT_SELECTOR_TDE input)
{
	R_WILSON_EN1.load_register();
	R_WILSON_EN1.S.SELWILSON=input;
	R_WILSON_EN1.update_register();
}

inline void ADS1293_LIB::set_wilson_reference_input_2(INPUT_SELECTOR_TDE input)
{
	R_WILSON_EN2.load_register();
	R_WILSON_EN2.S.SELWILSON=input;
	R_WILSON_EN2.update_register();
}

inline void ADS1293_LIB::set_wilson_reference_input_3(INPUT_SELECTOR_TDE input)
{
	R_WILSON_EN3.load_register();
	R_WILSON_EN3.S.SELWILSON=input;
	R_WILSON_EN3.update_register();
}

inline INPUT_SELECTOR_TDE ADS1293_LIB::get_wilson_reference_input_1(void)
{
	R_WILSON_EN1.load_register();
	return R_WILSON_EN1.S.SELWILSON;
}

inline INPUT_SELECTOR_TDE ADS1293_LIB::get_wilson_reference_input_2(void)
{
	R_WILSON_EN2.load_register();
	return R_WILSON_EN2.S.SELWILSON;
}

inline INPUT_SELECTOR_TDE ADS1293_LIB::get_wilson_reference_input_3(void)
{
	R_WILSON_EN3.load_register();
	return R_WILSON_EN3.S.SELWILSON;
}

inline void ADS1293_LIB::set_wilson_reference_control(RG_WLS_REFCNTRL_TDE ref_control)
{
	R_WILSON_CN.S.WILSONINT=0;
	R_WILSON_CN.S.GOLDINT=0;
	if (ref_control==RG_WLS_REFCNTRL_GOLDINT){R_WILSON_CN.S.GOLDINT=1;}
	if (ref_control==RG_WLS_REFCNTRL_WILSONINT){R_WILSON_CN.S.WILSONINT=1;}
	R_WILSON_CN.update_register();
}

inline RG_WLS_REFCNTRL_TDE ADS1293_LIB::get_wilson_reference_control(void)
{
	R_WILSON_CN.load_register();
	if (R_WILSON_CN.S.WILSONINT==0 && R_WILSON_CN.S.GOLDINT==0) {return RG_WLS_REFCNTRL_NOT_SET;}
	if (R_WILSON_CN.S.WILSONINT==1 && R_WILSON_CN.S.GOLDINT==0) {return RG_WLS_REFCNTRL_WILSONINT;}
	if (R_WILSON_CN.S.WILSONINT==0 && R_WILSON_CN.S.GOLDINT==1) {return RG_WLS_REFCNTRL_GOLDINT;}
	return RG_WLS_REFCNTRL_ERROR;
}

inline void ADS1293_LIB::set_shutdown_common_mode_ref_voltage(bool enable)
{
	R_REF_CN.load_register();
	R_REF_CN.S.SHDN_CMREF=enable;
	R_REF_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_common_mode_ref_voltage(void)
{
	R_REF_CN.load_register();
	return R_REF_CN.S.SHDN_CMREF;
}

inline void ADS1293_LIB::set_shutdown_internal_ref_voltage(bool enable)
{
	R_REF_CN.load_register();
	R_REF_CN.S.SHDN_REF=enable;
	R_REF_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_internal_ref_voltage(void)
{
	R_REF_CN.load_register();
	return R_REF_CN.S.SHDN_REF;
}

inline void ADS1293_LIB::set_start_clock_to_digital(bool enable)
{
	R_OSC_CN.load_register();
	R_OSC_CN.S.STRTCLK=enable;
	R_OSC_CN.update_register();
}

inline bool ADS1293_LIB::get_start_clock_to_digital(void)
{
	R_OSC_CN.load_register();
	return R_OSC_CN.S.STRTCLK;
}

inline void ADS1293_LIB::set_enable_CLK_pin_output(bool enable)
{
	R_OSC_CN.load_register();
	R_OSC_CN.S.EN_CLKOUT=enable;
	R_OSC_CN.update_register();
}

inline bool ADS1293_LIB::get_enable_CLK_pin_output(void)
{
	R_OSC_CN.load_register();
	return R_OSC_CN.S.EN_CLKOUT;
}

inline void ADS1293_LIB::set_clock_source(CLK_SOURCE_OSC_TDE clk_source)
{
	R_OSC_CN.load_register();
	R_OSC_CN.S.SHDN_OSC=clk_source;
	R_OSC_CN.update_register();
}

inline CLK_SOURCE_OSC_TDE ADS1293_LIB::get_clock_source(void)
{
	R_OSC_CN.load_register();
	return R_OSC_CN.S.SHDN_OSC;
}

inline void ADS1293_LIB::set_enable_INA_high_resolition_CH_1(bool enable)
{
	R_AFE_RES.load_register();
	R_AFE_RES.S.EN_HIRES_CH1=enable;
	R_AFE_RES.update_register();
}

inline void ADS1293_LIB::set_enable_INA_high_resolition_CH_2(bool enable)
{
	R_AFE_RES.load_register();
	R_AFE_RES.S.EN_HIRES_CH2=enable;
	R_AFE_RES.update_register();
}

inline void ADS1293_LIB::set_enable_INA_high_resolition_CH_3(bool enable)
{
	R_AFE_RES.load_register();
	R_AFE_RES.S.EN_HIRES_CH3=enable;
	R_AFE_RES.update_register();
}

inline bool ADS1293_LIB::get_enable_INA_high_resolition_CH_1(void)
{
	R_AFE_RES.load_register();
	return R_AFE_RES.S.EN_HIRES_CH1;
}

inline bool ADS1293_LIB::get_enable_INA_high_resolition_CH_2(void)
{
	R_AFE_RES.load_register();
	return R_AFE_RES.S.EN_HIRES_CH2;
}

inline bool ADS1293_LIB::get_enable_INA_high_resolition_CH_3(void)
{
	R_AFE_RES.load_register();
	return R_AFE_RES.S.EN_HIRES_CH3;
}

inline void ADS1293_LIB::set_clock_frequency_for_ch_1(FS_HIGH_CH_TDE clk_frequency)
{
	R_AFE_RES.load_register();
	R_AFE_RES.S.FS_HIGH_CH1=clk_frequency;
	R_AFE_RES.update_register();
}

inline void ADS1293_LIB::set_clock_frequency_for_ch_2(FS_HIGH_CH_TDE clk_frequency)
{
	R_AFE_RES.load_register();
	R_AFE_RES.S.FS_HIGH_CH2=clk_frequency;
	R_AFE_RES.update_register();
}

inline void ADS1293_LIB::set_clock_frequency_for_ch_3(FS_HIGH_CH_TDE clk_frequency)
{
	R_AFE_RES.load_register();
	R_AFE_RES.S.FS_HIGH_CH3=clk_frequency;
	R_AFE_RES.update_register();
}

inline FS_HIGH_CH_TDE ADS1293_LIB::get_clock_frequency_for_ch_1(void)
{
	R_AFE_RES.load_register();
	return R_AFE_RES.S.FS_HIGH_CH1;
}

inline FS_HIGH_CH_TDE ADS1293_LIB::get_clock_frequency_for_ch_2(void)
{
	R_AFE_RES.load_register();
	return R_AFE_RES.S.FS_HIGH_CH2;
}

inline FS_HIGH_CH_TDE ADS1293_LIB::get_clock_frequency_for_ch_3(void)
{
	R_AFE_RES.load_register();
	return R_AFE_RES.S.FS_HIGH_CH3;
}

inline uint32_t ADS1293_LIB::get_clock_frequency_in_hertz(FS_HIGH_CH_TDE clk_frequency)
{
	if(clk_frequency==FS_HIGH_CH_102400HZ) {return 102400;}
	if(clk_frequency==FS_HIGH_CH_204800HZ) {return 204800;}
}

inline void ADS1293_LIB::set_shutdown_INA_CH_1(bool enable)
{
	R_AFE_SHDN_CN.load_register();
	R_AFE_SHDN_CN.S.SHDN_INA_CH1=enable;
	R_AFE_SHDN_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_INA_CH_2(bool enable)
{
	R_AFE_SHDN_CN.load_register();
	R_AFE_SHDN_CN.S.SHDN_INA_CH2=enable;
	R_AFE_SHDN_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_INA_CH_3(bool enable)
{
	R_AFE_SHDN_CN.load_register();
	R_AFE_SHDN_CN.S.SHDN_INA_CH3=enable;
	R_AFE_SHDN_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_INA_CH_1(void)
{
	R_AFE_SHDN_CN.load_register();
	return R_AFE_SHDN_CN.S.SHDN_INA_CH1;
}

inline bool ADS1293_LIB::get_shutdown_INA_CH_2(void)
{
	R_AFE_SHDN_CN.load_register();
	return R_AFE_SHDN_CN.S.SHDN_INA_CH2;
}

inline bool ADS1293_LIB::get_shutdown_INA_CH_3(void)
{
	R_AFE_SHDN_CN.load_register();
	return R_AFE_SHDN_CN.S.SHDN_INA_CH3;
}

inline void ADS1293_LIB::set_shutdown_SD_modulator_CH_1(bool enable)
{
	R_AFE_SHDN_CN.load_register();
	R_AFE_SHDN_CN.S.SHDN_SDM_CH1=enable;
	R_AFE_SHDN_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_SD_modulator_CH_2(bool enable)
{
	R_AFE_SHDN_CN.load_register();
	R_AFE_SHDN_CN.S.SHDN_SDM_CH2=enable;
	R_AFE_SHDN_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_SD_modulator_CH_3(bool enable)
{
	R_AFE_SHDN_CN.load_register();
	R_AFE_SHDN_CN.S.SHDN_SDM_CH3=enable;
	R_AFE_SHDN_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_SD_modulator_CH_1(void)
{
	R_AFE_SHDN_CN.load_register();
	return R_AFE_SHDN_CN.S.SHDN_SDM_CH1;
}

inline bool ADS1293_LIB::get_shutdown_SD_modulator_CH_2(void)
{
	R_AFE_SHDN_CN.load_register();
	return R_AFE_SHDN_CN.S.SHDN_SDM_CH2;
}

inline bool ADS1293_LIB::get_shutdown_SD_modulator_CH_3(void)
{
	R_AFE_SHDN_CN.load_register();
	return R_AFE_SHDN_CN.S.SHDN_SDM_CH3;
}

inline void ADS1293_LIB::set_shutdown_INA_fault_detect_CH_1(bool enable)
{
	R_AFE_FAULT_CN.load_register();
	R_AFE_FAULT_CN.S.SHDN_FAULTDET_CH1=enable;
	R_AFE_FAULT_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_INA_fault_detect_CH_2(bool enable)
{
	R_AFE_FAULT_CN.load_register();
	R_AFE_FAULT_CN.S.SHDN_FAULTDET_CH2=enable;
	R_AFE_FAULT_CN.update_register();
}

inline void ADS1293_LIB::set_shutdown_INA_fault_detect_CH_3(bool enable)
{
	R_AFE_FAULT_CN.load_register();
	R_AFE_FAULT_CN.S.SHDN_FAULTDET_CH3=enable;
	R_AFE_FAULT_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_INA_fault_detect_CH_1(void)
{
	R_AFE_FAULT_CN.load_register();
	return R_AFE_FAULT_CN.S.SHDN_FAULTDET_CH1;
}

inline bool ADS1293_LIB::get_shutdown_INA_fault_detect_CH_2(void)
{
	R_AFE_FAULT_CN.load_register();
	return R_AFE_FAULT_CN.S.SHDN_FAULTDET_CH2;
}

inline bool ADS1293_LIB::get_shutdown_INA_fault_detect_CH_3(void)
{
	R_AFE_FAULT_CN.load_register();
	return R_AFE_FAULT_CN.S.SHDN_FAULTDET_CH3;
}

inline void ADS1293_LIB::set_shutdown_analog_pace_channel(bool enable)
{
	R_AFE_PACE_CN.load_register();
	R_AFE_PACE_CN.S.SHDN_PACE=enable;
	R_AFE_PACE_CN.update_register();
}

inline bool ADS1293_LIB::get_shutdown_analog_pace_channel(void)
{
	R_AFE_PACE_CN.load_register();
	return R_AFE_PACE_CN.S.SHDN_PACE;
}

inline void ADS1293_LIB::set_connect_pace_ch_output_to_WCT(bool enable)
{
	R_AFE_PACE_CN.load_register();
	R_AFE_PACE_CN.S.PACE2WCT=enable;
	R_AFE_PACE_CN.update_register();
}

inline bool ADS1293_LIB::get_connect_pace_ch_output_to_WCT(void)
{
	R_AFE_PACE_CN.load_register();
	return R_AFE_PACE_CN.S.PACE2WCT;
}

inline void ADS1293_LIB::set_connect_pace_ch_output_to_RLDIN(bool enable)
{
	R_AFE_PACE_CN.load_register();
	R_AFE_PACE_CN.S.PACE2RLDIN=enable;
	R_AFE_PACE_CN.update_register();
}

inline bool ADS1293_LIB::get_connect_pace_ch_output_to_RLDIN(void)
{
	R_AFE_PACE_CN.load_register();
	return R_AFE_PACE_CN.S.PACE2RLDIN;
}

inline RG_ERROR_LOD_TDS& ADS1293_LIB::get_leadoff_detect_error_status(void)
{
	R_ERROR_LOD.load_register();
	return R_ERROR_LOD.S;
}

inline RG_ERROR_STATUS_TDS& ADS1293_LIB::get_analog_other_error_status(void)
{
	R_ERROR_STATUS.load_register();
	return R_ERROR_STATUS.S;
}

inline RG_ERROR_RANGE_TDS& ADS1293_LIB::get_AFE_out_of_range_status_CH_1(void)
{
	R_ERROR_RANGE1.load_register();
	return R_ERROR_RANGE1.S;
}

inline RG_ERROR_RANGE_TDS& ADS1293_LIB::get_AFE_out_of_range_status_CH_2(void)
{
	R_ERROR_RANGE2.load_register();
	return R_ERROR_RANGE2.S;
}

inline RG_ERROR_RANGE_TDS& ADS1293_LIB::get_AFE_out_of_range_status_CH_3(void)
{
	R_ERROR_RANGE3.load_register();
	return R_ERROR_RANGE3.S;
}

inline RG_ERROR_SYNC_TDS& ADS1293_LIB::get_synchronization_error_status(void)
{
	R_ERROR_SYNC.load_register();
	return R_ERROR_SYNC.S;
}

inline RG_ERROR_MISC_TDS& ADS1293_LIB::get_miscellaneous_error_status(void)
{
	R_ERROR_MISC.load_register();
	return R_ERROR_MISC.S;
}

inline void ADS1293_LIB::set_digital_output_drive_strength(DIGO_STRENGTH_TDE strenght)
{
	R_DIGO_STRENGTH.load_register();
	R_DIGO_STRENGTH.S.DIGO_STRENGTH=strenght;
	R_DIGO_STRENGTH.update_register();
}

inline DIGO_STRENGTH_TDE ADS1293_LIB::get_digital_output_drive_strength(void)
{
	R_DIGO_STRENGTH.load_register();
	return R_DIGO_STRENGTH.S.DIGO_STRENGTH;
}

inline void ADS1293_LIB::set_R2_decimation_rate(R2_RATE_TDE rate)
{
	R_R2_RATE.load_register();
	R_R2_RATE.S.R2_RATE=rate;
	R_R2_RATE.update_register();
}

inline R2_RATE_TDE ADS1293_LIB::get_R2_decimation_rate(void)
{
	R_R2_RATE.load_register();
	return R_R2_RATE.S.R2_RATE;
}
inline uint32_t ADS1293_LIB::get_R2_decimation_rate_in_number(R2_RATE_TDE rate)
{
	if (rate==R2_RATE_4) {return 4;}
	if (rate==R2_RATE_5) {return 5;}
	if (rate==R2_RATE_6) {return 6;}
	if (rate==R2_RATE_8) {return 8;}
	return 1;
}

inline void ADS1293_LIB::set_R3_decimation_rate_for_CH_1(R3_RATE_TDE rate)
{
	R_R3_RATE_CH1.load_register();
	R_R3_RATE_CH1.S.R3_RATE=rate;
	R_R3_RATE_CH1.update_register();
}

inline void ADS1293_LIB::set_R3_decimation_rate_for_CH_2(R3_RATE_TDE rate)
{
	R_R3_RATE_CH2.load_register();
	R_R3_RATE_CH2.S.R3_RATE=rate;
	R_R3_RATE_CH2.update_register();
}

inline void ADS1293_LIB::set_R3_decimation_rate_for_CH_3(R3_RATE_TDE rate)
{
	R_R3_RATE_CH3.load_register();
	R_R3_RATE_CH3.S.R3_RATE=rate;
	R_R3_RATE_CH3.update_register();
}

inline R3_RATE_TDE ADS1293_LIB::get_R3_decimation_rate_for_CH_1(void)
{
	R_R3_RATE_CH1.load_register();
	return R_R3_RATE_CH1.S.R3_RATE;
}

inline R3_RATE_TDE ADS1293_LIB::get_R3_decimation_rate_for_CH_2(void)
{
	R_R3_RATE_CH2.load_register();
	return R_R3_RATE_CH2.S.R3_RATE;
}

inline R3_RATE_TDE ADS1293_LIB::get_R3_decimation_rate_for_CH_3(void)
{
	R_R3_RATE_CH3.load_register();
	return R_R3_RATE_CH3.S.R3_RATE;
}

inline uint32_t ADS1293_LIB::get_R3_decimation_rate_in_number(R3_RATE_TDE rate)
{
	if (rate==R3_RATE_4) {return 4;}
	if (rate==R3_RATE_6) {return 6;}
	if (rate==R3_RATE_8) {return 8;}
	if (rate==R3_RATE_12) {return 12;}
	if (rate==R3_RATE_16) {return 16;}
	if (rate==R3_RATE_32) {return 32;}
	if (rate==R3_RATE_64) {return 65;}
	if (rate==R3_RATE_128) {return 128;}
	return 1;
}

inline void ADS1293_LIB::set_R1_decimation_rate_for_CH_1(R1_RATE_TDE rate)
{
	R_R1_RATE.load_register();
	R_R1_RATE.S.R1_RATE_CH1=rate;
	R_R1_RATE.update_register();
}

inline void ADS1293_LIB::set_R1_decimation_rate_for_CH_2(R1_RATE_TDE rate)
{
	R_R1_RATE.load_register();
	R_R1_RATE.S.R1_RATE_CH2=rate;
	R_R1_RATE.update_register();
}

inline void ADS1293_LIB::set_R1_decimation_rate_for_CH_3(R1_RATE_TDE rate)
{
	R_R1_RATE.load_register();
	R_R1_RATE.S.R1_RATE_CH3=rate;
	R_R1_RATE.update_register();
}

inline R1_RATE_TDE ADS1293_LIB::get_R1_decimation_rate_for_CH_1(void)
{
	R_R1_RATE.load_register();
	return R_R1_RATE.S.R1_RATE_CH1;
}

inline R1_RATE_TDE ADS1293_LIB::get_R1_decimation_rate_for_CH_2(void)
{
	R_R1_RATE.load_register();
	return R_R1_RATE.S.R1_RATE_CH2;
}

inline R1_RATE_TDE ADS1293_LIB::get_R1_decimation_rate_for_CH_3(void)
{
	R_R1_RATE.load_register();
	return R_R1_RATE.S.R1_RATE_CH3;
}

inline uint32_t ADS1293_LIB::get_R1_decimation_rate_in_number(R1_RATE_TDE rate)
{
	if (rate==R1_RATE_DOUBLE_R1_2) {return 2;}
	if (rate==R1_RATE_STANDART_R1_4) {return 4;}
	return 1;
}

inline void ADS1293_LIB::set_ECG_filter_disable_for_ch_1(bool disable)
{
	R_DIS_EFILTER.load_register();
	R_DIS_EFILTER.S.DIS_E1=disable;
	R_DIS_EFILTER.update_register();
}

inline void ADS1293_LIB::set_ECG_filter_disable_for_ch_2(bool disable)
{
	R_DIS_EFILTER.load_register();
	R_DIS_EFILTER.S.DIS_E2=disable;
	R_DIS_EFILTER.update_register();
}

inline void ADS1293_LIB::set_ECG_filter_disable_for_ch_3(bool disable)
{
	R_DIS_EFILTER.load_register();
	R_DIS_EFILTER.S.DIS_E3=disable;
	R_DIS_EFILTER.update_register();
}

inline bool ADS1293_LIB::get_ECG_filter_disable_for_ch_1(void)
{
	R_DIS_EFILTER.load_register();
	return R_DIS_EFILTER.S.DIS_E1;
}

inline bool ADS1293_LIB::get_ECG_filter_disable_for_ch_2(void)
{
	R_DIS_EFILTER.load_register();
	return R_DIS_EFILTER.S.DIS_E2;
}

inline bool ADS1293_LIB::get_ECG_filter_disable_for_ch_3(void)
{
	R_DIS_EFILTER.load_register();
	return R_DIS_EFILTER.S.DIS_E3;
}

inline void ADS1293_LIB::set_DRDYB_pin_source(DRDYB_SRC_TDE source)
{
	R_DRDYB_SRC.load_register();
	R_DRDYB_SRC.S.DRDYB_SRC=source;
	R_DRDYB_SRC.update_register();
}

inline DRDYB_SRC_TDE ADS1293_LIB::get_DRDYB_pin_source(void)
{
	R_DRDYB_SRC.load_register();
	return R_DRDYB_SRC.S.DRDYB_SRC;
}

inline void ADS1293_LIB::set_disable_SYNCB_output_driver(bool disable)
{
	R_SYNCB_CN.load_register();
	R_SYNCB_CN.S.DIS_SYNCBOUT=disable;
	R_SYNCB_CN.update_register();
}

inline bool ADS1293_LIB::get_disable_SYNCB_output_driver(void)
{
	R_SYNCB_CN.load_register();
	return R_SYNCB_CN.S.DIS_SYNCBOUT;
}

inline void ADS1293_LIB::set_SYNCB_pin_source(SYNCB_SRC_TDE source)
{
	R_SYNCB_CN.load_register();
	R_SYNCB_CN.S.SYNCB_SRC=source;
	R_SYNCB_CN.update_register();
}

inline SYNCB_SRC_TDE ADS1293_LIB::get_SYNCB_pin_source(void)
{
	R_SYNCB_CN.load_register();
	return R_SYNCB_CN.S.SYNCB_SRC;
}

inline void ADS1293_LIB::set_mask_alarm_for_CMOR(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_CMOR=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_CMOR(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_CMOR;
}

inline void ADS1293_LIB::set_mask_alarm_for_RLDRAIL(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_RLDRAIL=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_RLDRAIL(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_RLDRAIL;
}

inline void ADS1293_LIB::set_mask_alarm_for_BATLOW(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_BATLOW=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_BATLOW(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_BATLOW;
}

inline void ADS1293_LIB::set_mask_alarm_for_LEADOFF(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_LEADOFF=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_LEADOFF(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_LEADOFF;
}

inline void ADS1293_LIB::set_mask_alarm_for_CH1ERR(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_CH1ERR=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_CH1ERR(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_CH1ERR;
}

inline void ADS1293_LIB::set_mask_alarm_for_CH2ERR(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_CH2ERR=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_CH2ERR(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_CH2ERR;
}

inline void ADS1293_LIB::set_mask_alarm_for_CH3ERR(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_CH3ERR=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_CH3ERR(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_CH3ERR;
}

inline void ADS1293_LIB::set_mask_alarm_for_SYNCEDGEER(bool enable)
{
	R_MASK_ERR.load_register();
	R_MASK_ERR.S.MASK_SYNCEDGEER=enable;
	R_MASK_ERR.update_register();
}

inline bool ADS1293_LIB::get_mask_alarm_for_SYNCEDGEER(void)
{
	R_MASK_ERR.load_register();
	return R_MASK_ERR.S.MASK_SYNCEDGEER;
}

inline void ADS1293_LIB::set_DF_for_LOD_alarm_signal(uint8_t DF_value)
{
	DF_value=DF_value & 0x0F; // 4 bit for value
	R_ALARM_FILTER.load_register();
	R_ALARM_FILTER.S.AFILTER_LOD=DF_value;
	R_ALARM_FILTER.update_register();
}

inline uint8_t ADS1293_LIB::get_DF_for_LOD_alarm_signal(void)
{
	R_ALARM_FILTER.load_register();
	return R_ALARM_FILTER.S.AFILTER_LOD;
}

inline void ADS1293_LIB::set_DF_for_other_alarm_signal(uint8_t DF_value)
{
	DF_value=DF_value & 0x0F; // 4 bit for value
	R_ALARM_FILTER.load_register();
	R_ALARM_FILTER.S.AFILTER_OTHER=DF_value;
	R_ALARM_FILTER.update_register();
}

inline uint8_t ADS1293_LIB::get_DF_for_other_alarm_signal(void)
{
	R_ALARM_FILTER.load_register();
	return R_ALARM_FILTER.S.AFILTER_OTHER;
}

inline void ADS1293_LIB::set_DATA_STATUS_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.STS_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_DATA_STATUS_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.STS_EN;
}

inline void ADS1293_LIB::set_CH1_PACE_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.P1_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_CH1_PACE_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.P1_EN;
}

inline void ADS1293_LIB::set_CH2_PACE_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.P2_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_CH2_PACE_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.P2_EN;
}

inline void ADS1293_LIB::set_CH3_PACE_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.P3_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_CH3_PACE_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.P3_EN;
}

inline void ADS1293_LIB::set_CH1_ECG_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.E1_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_CH1_ECG_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.E1_EN;
}

inline void ADS1293_LIB::set_CH2_ECG_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.E2_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_CH2_ECG_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.E2_EN;
}

inline void ADS1293_LIB::set_CH3_ECG_read_back_mode(bool enable)
{
	R_CH_CNFG.load_register();
	R_CH_CNFG.S.E3_EN=enable;
	R_CH_CNFG.update_register();
}

inline bool ADS1293_LIB::get_CH3_ECG_read_back_mode(void)
{
	R_CH_CNFG.load_register();
	return R_CH_CNFG.S.E3_EN;
}

inline RG_DATA_STATUS_TDS& ADS1293_LIB::get_data_ready_status(void)
{
	R_DATA_STATUS.load_register();
	return R_DATA_STATUS.S;
}

inline uint32_t ADS1293_LIB::get_ECG_data_rate_CH_1(void)
{
	uint32_t SDM_frequency=get_clock_frequency_in_hertz(get_clock_frequency_for_ch_1());
	uint32_t R1=get_R1_decimation_rate_in_number(get_R1_decimation_rate_for_CH_1());
	uint32_t R2=get_R2_decimation_rate_in_number(get_R2_decimation_rate());
	uint32_t R3=get_R3_decimation_rate_in_number(get_R3_decimation_rate_for_CH_1());

	uint32_t ECG_data_rate=SDM_frequency/(R1*R2*R3);
	return ECG_data_rate;
}

inline uint32_t ADS1293_LIB::get_ECG_data_rate_CH_2(void)
{
	uint32_t SDM_frequency=get_clock_frequency_in_hertz(get_clock_frequency_for_ch_2());
	uint32_t R1=get_R1_decimation_rate_in_number(get_R1_decimation_rate_for_CH_2());
	uint32_t R2=get_R2_decimation_rate_in_number(get_R2_decimation_rate());
	uint32_t R3=get_R3_decimation_rate_in_number(get_R3_decimation_rate_for_CH_2());

	uint32_t ECG_data_rate=SDM_frequency/(R1*R2*R3);
	return ECG_data_rate;
}

inline uint32_t ADS1293_LIB::get_ECG_data_rate_CH_3(void)
{
	uint32_t SDM_frequency=get_clock_frequency_in_hertz(get_clock_frequency_for_ch_3());
	uint32_t R1=get_R1_decimation_rate_in_number(get_R1_decimation_rate_for_CH_3());
	uint32_t R2=get_R2_decimation_rate_in_number(get_R2_decimation_rate());
	uint32_t R3=get_R3_decimation_rate_in_number(get_R3_decimation_rate_for_CH_3());

	uint32_t ECG_data_rate=SDM_frequency/(R1*R2*R3);
	return ECG_data_rate;
}

inline uint32_t ADS1293_LIB::get_pace_data_rate_CH_1(void)
{
	uint32_t SDM_frequency=get_clock_frequency_in_hertz(get_clock_frequency_for_ch_1());
	uint32_t R1=get_R1_decimation_rate_in_number(get_R1_decimation_rate_for_CH_1());
	uint32_t R2=get_R2_decimation_rate_in_number(get_R2_decimation_rate());

	uint32_t pace_data_rate=SDM_frequency/(R1*R2);
	return pace_data_rate;
}

inline uint32_t ADS1293_LIB::get_pace_data_rate_CH_2(void)
{
	uint32_t SDM_frequency=get_clock_frequency_in_hertz(get_clock_frequency_for_ch_2());
	uint32_t R1=get_R1_decimation_rate_in_number(get_R1_decimation_rate_for_CH_2());
	uint32_t R2=get_R2_decimation_rate_in_number(get_R2_decimation_rate());

	uint32_t pace_data_rate=SDM_frequency/(R1*R2);
	return pace_data_rate;
}

inline uint32_t ADS1293_LIB::get_pace_data_rate_CH_3(void)
{
	uint32_t SDM_frequency=get_clock_frequency_in_hertz(get_clock_frequency_for_ch_3());
	uint32_t R1=get_R1_decimation_rate_in_number(get_R1_decimation_rate_for_CH_3());
	uint32_t R2=get_R2_decimation_rate_in_number(get_R2_decimation_rate());

	uint32_t pace_data_rate=SDM_frequency/(R1*R2);
	return pace_data_rate;
}

inline uint16_t ADS1293_LIB::get_pace_data_CH_1(void)
{
	uint16_t register_data=0;
	_IO.load_2_registers(&register_data, RL_DATA_CH1_PACE1);
	return register_data;
}

inline uint16_t ADS1293_LIB::get_pace_data_CH_2(void)
{
	uint16_t register_data=0;
	_IO.load_2_registers(&register_data, RL_DATA_CH2_PACE1);
	return register_data;
}

inline uint16_t ADS1293_LIB::get_pace_data_CH_3(void)
{
	uint16_t register_data=0;
	_IO.load_2_registers(&register_data, RL_DATA_CH3_PACE1);
	return register_data;
}

inline uint32_t ADS1293_LIB::get_ECG_data_CH_1(void)
{
	uint32_t register_data=0;
	_IO.load_3_registers(&register_data, RL_DATA_CH1_ECG1);
	return register_data;
}

inline uint32_t ADS1293_LIB::get_ECG_data_CH_2(void)
{
	uint32_t register_data=0;
	_IO.load_3_registers(&register_data, RL_DATA_CH2_ECG1);
	return register_data;
}

inline uint32_t ADS1293_LIB::get_ECG_data_CH_3(void)
{
	uint32_t register_data=0;
	_IO.load_3_registers(&register_data, RL_DATA_CH3_ECG1);
	return register_data;
}

inline void ADS1293::ADS1293_LIB::load_all_registers(void)
{
	R_CONFIG.load_register();
	//Input Channel Selection Registers
	R_FLEX_CH1_CN.load_register();
	R_FLEX_CH2_CN.load_register();
	R_FLEX_CH3_CN.load_register();
	R_FLEX_PACE_CN.load_register();
	R_FLEX_VBAT_CN.load_register();
	//Lead-off Detect Control Registers
	R_LOD_CN.load_register();
	R_LOD_EN.load_register();
	R_LOD_CURRENT.load_register();
	R_LOD_AC_CN.load_register();
	//Common-Mode Detection and Right-Leg Drive Feedback Control Registers
	R_CMDET_EN.load_register();
	R_CMDET_CN.load_register();
	R_RLD_CN.load_register();
	//Wilson Control Registers
	R_WILSON_EN1.load_register();
	R_WILSON_EN2.load_register();
	R_WILSON_EN3.load_register();
	R_WILSON_CN.load_register();
	//Reference Registers
	R_REF_CN.load_register();
	//OSC Control Registers
	R_OSC_CN.load_register();
	//AFE Control Registers
	R_AFE_RES.load_register();
	R_AFE_SHDN_CN.load_register();
	R_AFE_FAULT_CN.load_register();
	R_AFE_PACE_CN.load_register();
	//Error Status Registers
	R_ERROR_LOD.load_register();
	R_ERROR_STATUS.load_register();
	R_ERROR_RANGE1.load_register();
	R_ERROR_RANGE2.load_register();
	R_ERROR_RANGE3.load_register();
	R_ERROR_SYNC.load_register();
	R_ERROR_MISC.load_register();
	//Digital Registers
	R_DIGO_STRENGTH.load_register();
	R_R2_RATE.load_register();
	R_R3_RATE_CH1.load_register();
	R_R3_RATE_CH2.load_register();
	R_R3_RATE_CH3.load_register();
	R_R1_RATE.load_register();
	R_DIS_EFILTER.load_register();
	R_DRDYB_SRC.load_register();
	R_SYNCB_CN.load_register();
	R_MASK_DRDYB.load_register();
	R_MASK_ERR.load_register();
	R_ALARM_FILTER.load_register();
	R_CH_CNFG.load_register();
	//Pace and ECG Data Read Back Registers
	R_DATA_STATUS.load_register();

}



}
#endif /* ADS1293_LIB_ADS1293_LIB_H_ */
