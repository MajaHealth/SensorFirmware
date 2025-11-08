#ifndef MAX30009_LIB_H
#define MAX30009_LIB_H


#include "VT_sync_data_stream_interface.h"

#include "max30009_register_struct.h"
#include "stdint.h"
#include "max30009_data_struct.h"

#include "stdlib.h"
#include "math.h"

class MAX30009_LIB
{
public:
    MAX30009_LIB(VT_sync_data_stream_interface *data_stream);

    /**
    	\brief set data stream for input and output data
    	\param [in] _data_stream - pointer to data stream object
     */
    void set_data_stream(VT_sync_data_stream_interface * data_stream);

    //STATUS______________________________________________________________________________________________

    /**
        \brief read current MAX30009 status
        \param [in] status - pointer to struct var for read status
        \return - true if read successful
     */
    bool read_status(MAX30009_STATUS_STRUCT_TYPE * status);


    //PLL_________________________________________________________________________________________________
    /**
        \brief set reference clock source
        \param [in] clock_source - clock_source type (from enum MAX30009_REFCLK_SOURCE_ENUM_TYPE)
        \return - true if set successful
     */
    bool set_reference_clock_source(MAX30009_REFCLK_SOURCE_ENUM_TYPE clock_source);

    /**
        \brief set stimulation drive frequency
        \param [in] drive_freq - stimulation drive frequency in 1/10 hertz (the specified frequency may have an error)
        \param [in] desired_ADC_freq - frequency of operation  of the ADC to which the calculation will aim in 1/10 Hertz.
        \return - true if set successful
     */
    bool set_drive_frequency(uint32_t drive_freq, uint32_t desired_ADC_freq);

    /**
        \brief set PLL state
        \param [in] PLL_enable - PLL enable
        \return - true if set successful
     */
    bool set_PLL_state(bool PLL_enable);

    /**
        \brief calculate all system frequency from MAX30009 registers
     */
    void calculate_all_system_frequency(void);

    /**
        \brief return structure with all frequency
        \return - structure with all frequency
     */
    MAX30009_ALL_CLOCKS_FREQ_TYPE get_all_frequency(void);

    // BIOZ________________________________________________________________________________________________
    /**
        \brief set constant current stimulation  mode (DAC DRIVE MODE)
        \param [in] current_value - output stimulation current value (MAX30009_CURRENT_AMP_ENUM)
        \return - true if set successful
     */
    bool set_BIOZ_constant_current_mode(MAX30009_CURRENT_AMP_ENUM_TYPE current_value);

    /**
        \brief set constant voltage stimulation mode(DAC DRIVE MODE)
        \param [in] voltage_value - output stimulation voltage value (MAX30009_VOLTAGE_AMP_ENUM)
        \return - true if set successful
     */
    bool set_BIOZ_constant_voltage_mode(MAX30009_VOLTAGE_AMP_ENUM_TYPE voltage_value);

    /**
        \brief set H-bridge stimulation mode(DAC DRIVE MODE)
        \return - true if set successful
     */
    bool set_BIOZ_H_brifge_mode(void);

    /**
        \brief set standby stimulation mode(DAC DRIVE MODE)
        \return - true if set successful
     */
    bool set_BIOZ_drive_standby_mode(void);

    /**
        \brief set external capacitor state
        \param [in] ext_cap_enable - ext capacitor enable
        \return - true if set successful
     */
    bool set_ext_capacitor_state(bool ext_cap_enable);

    /**
        \brief set external resistor state
        \param [in] ext_res_enable - ext resistor enable
        \param [in] resistance - ext resistor enable
        \return - true if set successful
     */
    bool set_ext_resistor_state(bool ext_res_enable, uint32_t resistance);

    /**
        \brief set BIOZ DC restore
        \param [in] DCres_enable - DC restore enable
        \return - true if set successful
     */
    bool set_BIOZ_DC_restore(bool DCres_enable);

    /**
        \brief set BIOZ DRV RESET
        \param [in] DRV_RESET_enable - DRV RESET enable
        \return - true if set successful
     */
    bool set_BIOZ_DRV_RESET(bool DRV_RESET_enable);

    /**
        \brief set BIOZ amplifier bandwidth
        \param [in] bandwidth_mode - bandwidth mode (MAX30009_BIOZ_AMPLF_MODE_ENUM)
        \return - true if set successful
     */
    bool set_BIOZ_amplifier_bandwidth(MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE bandwidth_mode);

    /**
        \brief set BIOZ amplifier range
        \param [in] range_mode - range mode (MAX30009_BIOZ_AMPLF_MODE_ENUM)
        \return - true if set successful
     */
    bool set_BIOZ_amplifier_range(MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE range_mode);

    /**
        \brief set BIOZ bandgap state
        \param [in] bandgap_enable - bandgap enable
        \return - true if set successful
     */
    bool set_BIOZ_bandgap_state(bool bandgap_enable);

    /**
        \brief set BIOZ I-channel state
        \param [in] I_channel_enable - I_channel enable
        \return - true if set successful
     */
    bool set_BIOZ_I_channel_state(bool I_channel_enable);

    /**
         \brief set BIOZ_I_CLK_PHASE state (shift I-ch phase to quadrature phase)
         \param [in] BIOZ_I_CLK_PHASE_enable - BIOZ_I_CLK_PHASE enable
         \return - true if set successful
      */
    bool set_BIOZ_I_CLK_PHASE(bool BIOZ_I_CLK_PHASE_enable);

    /**
        \brief set BIOZ_Q_CLK_PHASE state  (shift I-ch phase to direct phase)
        \param [in] BIOZ_Q_CLK_PHASE_enable - BIOZ_Q_CLK_PHASE enable
        \return - true if set successful
     */
    bool set_BIOZ_Q_CLK_PHASE(bool BIOZ_Q_CLK_PHASE_enable);

    /**
        \brief set BIOZ Q-channel state
        \param [in] Q_channel_enable - Q_channel enable
        \return - true if set successful
     */
    bool set_BIOZ_Q_channel_state(bool Q_channel_enable);


    /**
        \brief set input HP filter value
        \param [in] filter_value - HP filter value (from enum MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM)
        \return - true if set successful
     */
    bool set_input_HP_filter(MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM filter_value);

    /**
    \brief set digital output HP filter value
    \param [in] filter_value - HP filter value (from enum MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE)
    \return - true if set successful
    */
    bool set_out_DHP_filter(MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE filter_value);

    /**
    \brief set digital output LP filter value
    \param [in] filter_value - LP filter value (from enum MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE)
    \return - true if set successful
    */
    bool set_out_DLP_filter(MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE filter_value);


    /**
        \brief set input amplifier (INA) low power mode
        \param [in] INA_low_mode_enable - INA low mode enable
        \return - true if set successful
     */
    bool set_INA_low_mode(bool INA_low_mode_enable);

    /**
        \brief set demodulation state
        \param [in] demodulation_enable - demodulation enable
        \return - true if set successful
     */
    bool set_demodulation_state(bool demodulation_enable);

    /**
        \brief set BIOZ total gain
        \param [in] total_gain - total BIOZ system gain (from enum MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE)
        \return - true if set successful
     */
    bool set_BIOZ_total_gain(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE  total_gain);

    /**
        \brief set BIOZ fast start mode
        \param [in] fast_start_mode - BIOZ fast start mode (from enum MAX30009_BIOZ_FAST_START_MODE_ENUM_TYPE)
        \return - true if set successful
     */
    bool set_BIOZ_fast_start_mode(MAX30009_BIOZ_FAST_START_MODE_ENUM_TYPE  fast_start_mode);



    /**
        \brief calculate BIOZ modes from MAX30009 registers
     */
    void calculate_BIOZ_modes(void);

    /**
        \brief return structure with BIOZ data
        \return - structure with BIOZ data
     */
    MAX30009_BIOZ_DATA_TYPE get_BIOZ_data(void);

    // MUX________________________________________________________________________________________________
    /**
        \brief set MUX DRVP assign to out electrode
        \param [in] DRVP_assign - DRVP assign to out electrode (MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM)
        \return - true if set successful
     */
    bool set_MUX_DRVP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM  DRVP_assign);

    /**
        \brief set MUX BIP assign to out electrode
        \param [in] BIP_assign - BIP assign to out electrode (MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM)
        \return - true if set successful
     */
    bool set_MUX_BIP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM  BIP_assign);

    /**
        \brief set MUX BIN assign to out electrode
        \param [in] BIN_assign - BIN assign to out electrode (MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM)
        \return - true if set successful
     */
    bool set_MUX_BIN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM  BIN_assign);

    /**
        \brief set MUX DRVN assign to out electrode
        \param [in] DRVN_assign - DRVN assign to out electrode (MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM)
        \return - true if set successful
     */
    bool set_MUX_DRVN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM  DRVN_assign);

    /**
        \brief set MUX state
        \param [in] MUX_enable - MUX enable
        \return - true if set successful
     */
    bool set_MUX_state(bool MUX_enable);

    /**
        \brief set MUX_CAL state
        \param [in] MUX_CAL_enable - MUX_CAL enable
        \return - true if set successful
     */
    bool set_MUX_CAL_state(bool MUX_CAL_enable);

    /**
        \brief set MUX_CAL_ONLY state
        \param [in] MUX_CAL_ONLY_enable - MUX_CAL_ONLY enable
        \return - true if set successful
    */
    bool set_MUX_CAL_ONLY_state(bool MUX_CAL_ONLY_enable);



    /**
       \brief Sets the BioZ Resistive Load value for non-GSR applications (BMUX_RSEL). This load is applied across DRVP/BIP and DRVN/BIN when BMUX_BIST_EN is enabled.
       \param [in] rsel_value - The desired resistance value (MAX30009_BMUX_RSEL_ENUM_TYPE).
       \return - true if set successful, false otherwise.
    */
    bool set_MUX_Resistor_Load_non_GSR(MAX30009_BMUX_RSEL_ENUM_TYPE rsel_value);

    /**
      \brief Sets the BioZ Resistive Load value for GSR applications (BMUX_GSR_RSEL).  This load is typically applied across DRVP/BIP and DRVN/BIN for GSR measurements.
      \param [in] rsel_value - The desired resistance value (MAX30009_BMUX_GSR_RSEL_ENUM_TYPE).
      \return - true if set successful, false otherwise.
     */
    bool set_MUX_Resistor_Load_GSR(MAX30009_BMUX_GSR_RSEL_ENUM_TYPE rsel_value);

    /**
        \brief Enables or disables the BioZ Built-In Self-Test (BIST)
        \param [in] enable - true to enable BIST, false to disable.
        \return - true if set successful, false otherwise.
     */
    bool set_MUX_BIST_enable(bool enable);

    /**
        \brief Enables or disables the BioZ Built-In Self-Test (BIST) for GSR
        \param [in] enable - true to enable BIST, false to disable.
        \return - true if set successful, false otherwise.
     */
    bool set_MUX_GSR_enable(bool enable);

    /**
        \brief calculate MUX modes from MAX30009 registers
     */
    void calculate_MUX_modes(void);

    /**
        \brief return structure with MUX data
        \return - structure with MUX data
     */
    MAX30009_MUX_DATA_TYPE get_MUX_data(void);

    // FIFO________________________________________________________________________________________________
    /**
        \brief read last ADC value and write to variable
        \param [in] I_channel_value - pointer to output data variable for I channel
        \param [in] Q_channel_value - pointer to output data variable for Q channel
        \return - true if read successful
     */
    bool get_last_ADC_value(MAX30009_FIFO_DATA *I_channel_value,MAX30009_FIFO_DATA *Q_channel_value);

    /**
        \brief readFIFO data to array
        \param [out]  FIFO_data_array -  pointer to varible for read
        \param [in] data_count - data count need read
        \param [out]  real_data_count -  pointer to varible for real read data count
        \return - true if read successful
     */
    bool read_FIFO_data(MAX30009_FIFO_DATA *FIFO_data_array,int32_t data_count,uint8_t * real_data_count);

    /**
        \brief read 10 pcs FIFO data to array
        \param [out]  FIFO_data_array -  pointer to varible for read
        \return - true if read successful
     */
    bool read_10pcs_FIFO_data(MAX30009_FIFO_DATA *FIFO_data_array);

    /**
        \brief read one FIFO item
        \param [out]  FIFO_data -  pointer to varible for read
        \return - true if read successful
     */
    bool read_two_FIFO_item(MAX30009_FIFO_DATA *FIFO_data,MAX30009_FIFO_DATA *FIFO_data2);

    /**
        \brief read buffer average value
        \param [out]  FIFO_I_data -  pointer to variable for read "IN PHASE"
        \param [out]  FIFO_Q_data -  pointer to variable for read "QUAD"
        \return - true if read successful
     */
    bool get_FIFO_average_all_value(MAX30009_FIFO_DATA *FIFO_I_data,MAX30009_FIFO_DATA *FIFO_Q_data);

    /**
        \brief encode FIFO answer bytes to FIFO data
        \param [out]  FIFO_answer_data -  pointer to FIFO answer byte
        \return - FIFO data
     */
    MAX30009_FIFO_DATA encode_FIFO_data(uint8_t * FIFO_answer_data);

    /**
        \brief calculate voltage and impendance from FIFO data
        \param [out]  FIFO_data_item -  pointer to FIFO data item
     */
    void calculate_impendance(MAX30009_FIFO_DATA * FIFO_data_item, MAX30009_CALIB_DATA_TYPE calib_data);

    /**
        \brief Make FIFO mark
    */
    void Make_FIFO_mark(void);

    /**
        \brief Flush FIFO
    */
    void Flush_FIFO(void);

    /**
        \brief set FIFO_STAT_CLR type
        \param [in] stat_clr_type - stat_clr_type (from enum MAX30009_FIFO_STAT_CLR_ENUM)
        \return - true if set successful
     */
    bool set_FIFO_STAT_CLR_type(MAX30009_FIFO_STAT_CLR_ENUM_TYPE  stat_clr_type);

    /**
        \brief set A_FULL type
        \param [in]  a_full_type -  a_full type (from enum MAX30009_FIFO_A_FULL_TYPE_ENUM_TYPE)
        \return - true if set successful
     */
    bool set_A_FULL_type(MAX30009_FIFO_A_FULL_TYPE_ENUM_TYPE  a_full_type);

    /**
        \brief set FIFO_RO type (overwrite type)
        \param [in]  fifo_ro_type -  fifo_ro type (from enum MAX30009_FIFO_RO_ENUM_TYPE)
        \return - true if set successful
     */
    bool set_FIFO_RO_type(MAX30009_FIFO_RO_ENUM_TYPE  fifo_ro_type);

    /**
        \brief set FIFO a full size. When set A_FULL flag and run interupt
        \param [in]  a_full_size -  FIFO buffer size when set A_FULL flag and run interupt
        \return - true if set successful
     */
    bool set_FIFO_A_FULL_size(uint8_t  a_full_size);

    /**
        \brief get FIFO data count
        \param [out]  data_count -  pointer to varible for data count
        \return - true if read successful
     */
    bool get_FIFO_data_count(uint16_t *data_count);

    /**
        \brief get FIFO overflow data count
        \param [out]  overflow_data_count -  pointer to varible for overflow data count
        \return - true if read successful
     */
    bool get_FIFO_overflow_data_count(uint8_t *overflow_data_count);

    /**
        \brief get FIFO write pointer
        \param [out]  write_data_pointer -  pointer to varible for write data pointer
        \return - true if read successful
     */
    bool get_FIFO_write_pointer(uint8_t *write_data_pointer);

    /**
        \brief get FIFO read pointer
        \param [out]  read_data_pointer -  pointer to varible for read data pointer
        \return - true if read successful
     */
    bool get_FIFO_read_pointer(uint8_t *read_data_pointer);



    //LEAD____________________________________________________________________________________

    /**
        \brief set LEAD RBIAS VALUE
        \param [in] RBIAS_VALUE - selects the BioZ input lead bias resistance
        \return - true if set successful
    */
    bool set_LEAD_RBIAS_VALUE(MAX30009_LEAD_RBIAS_VALUE_ENUM_TYPE RBIAS_VALUE);

    /**
        \brief set RBIAS_BIP_state
        \param [in] RBIAS_BIP_enable - enables lead bias on BIP. The resistor connecting BIP to VMID_RX is selected in RBIAS_VALUE
        \return - true if set successful
    */
    bool set_LEAD_RBIAS_BIP_state(bool RBIAS_BIP_enable);

    /**
        \brief set RBIAS_BIN_state
        \param [in] RBIAS_BIN_enable - enables lead bias on BIN. The resistor connecting BIN to VMID_RX is selected in RBIAS_VALUE
        \return - true if set successful
    */
    bool set_LEAD_RBIAS_BIN_state(bool RBIAS_BIN_enable);



    // CALIBRATE________________________________________________________________________________________________
    /**
    	\brief main process for calibrate procedure
    	\return - calibrate state
     */
    MAX30009_CALIB_STATE_ENUM_TYPE calibrate_main_proccess(void);

    /**
    	\brief manual start calibrate procedure
    	\param [in]  calib_source - source for reference data
    	\param [in]  ref_value - value reference data in milliohms
    	\param [in]  calibrate_current - calibrate current
     */
    void start_calibrate(MAX30009_CALIB_SOURCE_ENUM_TYPE calib_source,
                         double ref_value, MAX30009_CURRENT_AMP_ENUM_TYPE calibrate_current,
                         uint32_t calibrate_frequency,MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE calibrate_gain);

    /**
    	\brief manual start calibrate procedure. need call every 100ms
    	\param [in]  I_data - IN PHASE data value
    	\param [in]   I_data - QUAD data value
    	\return - calibrate data
    */
    MAX30009_FIFO_DATA_CALIB_TYPE calibrate_FIFO_data(MAX30009_FIFO_DATA I_data,MAX30009_FIFO_DATA Q_data, MAX30009_CALIB_DATA_TYPE calib_data);


    /**
    \brief return calibrate state
    \return - calibrate state
    */
    MAX30009_CALIB_STATE_ENUM_TYPE get_calibrate_state(void);

    MAX30009_CALIB_DATA_TYPE get_last_calib_data(void);


    /**
    \brief stop calibrate process

    */
    void stop_calibrate();


    /**
        \brief load all registers from MAX30009 to work register array
        \return - true if read successful
     */
    bool start_load_all_registers(void);
private:







    /**
        \brief SPI data transfer with MAX30009
        \param [in] out_data - pointer to output data array
        \param [in] input_data - pointer to input data array
        \param [in] data_size - data size in arrays
        \return - true if data transfer successful
     */
    bool SPI_data_transfer(uint8_t *out_data,uint8_t *input_data,uint8_t data_size);

    /**
        \brief read register from MAX30009 to work register array
        \param [in] register_address - register address in MAX30009
        \return - true if read successful
     */
    bool read_register(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address);

    /**
        \brief read register from MAX30009 to register_value var
        \param [in] register_address - register address in MAX30009
        \param [in] register_value - pointer to variable for register data
        \return - true if read successful
     */
    bool get_register(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address,uint8_t * register_value);

    /**
        \brief read register to MAX30009 from work register array
        \param [in] register_address - register address in MAX30009
        \return - true if write successful
     */
    bool write_register(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address_enum);

    /**
        \brief read register to MAX30009 from work register array without write check
        \param [in] register_address - register address in MAX30009
     */
    void write_register_without_check(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address_enum);


    bool _lib_is_init=false;
    MAX30009_REGISTERS_TYPE _write_reg;
    MAX30009_REGISTERS_TYPE _read_reg;
    uint8_t _X_DUMMY_VALUE=0;// dummy value for pointer array
    uint8_t *_max30009_write_registers_pointer_array[MAX30009_LAST_REGISTER_ADDRESS+1]= {0,}; //array for pointers to MAX30009 write registers
    uint8_t *_max30009_read_registers_pointer_array[MAX30009_LAST_REGISTER_ADDRESS+1]= {0,}; //array for pointers to MAX30009 read registers

    MAX30009_ALL_CLOCKS_FREQ_TYPE _all_clock_requency;
    MAX30009_FIND_CLOCKS_STRUCT_TYPE _best_clk_solution;
    MAX30009_BIOZ_DATA_TYPE _bioz_data;
    MAX30009_MUX_DATA _mux_data;
    MAX30009_FIFO_DATA_TYPE _fifo_data;

    MAX30009_CALIB_DATA_TYPE _calib_data;

    VT_sync_data_stream_interface * _data_stream;

};

inline MAX30009_LIB::MAX30009_LIB(VT_sync_data_stream_interface *data_stream)
{
    _data_stream=data_stream;

    //test bit order
    *((uint8_t*)&_write_reg.STATUS_1)=1;
    if (_write_reg.STATUS_1.A_FULL!=0 || _write_reg.STATUS_1.PWR_RDY!=1)
    {
        return;
    }
    *((uint8_t*)&_write_reg.STATUS_1)=0;

    for (uint32_t i=0; i<=MAX30009_LAST_REGISTER_ADDRESS; i++)
    {
        _max30009_write_registers_pointer_array[i]=&_X_DUMMY_VALUE;
        _max30009_read_registers_pointer_array[i]=&_X_DUMMY_VALUE;
    }

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_STATUS_1]=(uint8_t*)&_write_reg.STATUS_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_STATUS_2]=(uint8_t*)&_write_reg.STATUS_2;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_WRITE_POINTER]=(uint8_t*)&_write_reg.FIFO_WRITE_POINTER;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_READ_POINTER]=(uint8_t*)&_write_reg.FIFO_READ_POINTER;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_COUNTER_1]=(uint8_t*)&_write_reg.FIFO_COUNTER_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_COUNTER_2]=(uint8_t*)&_write_reg.FIFO_COUNTER_2;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_DATA_REGISTER]=(uint8_t*)&_write_reg.FIFO_DATA_REGISTER;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_CONFIGURATION_1]=(uint8_t*)&_write_reg.FIFO_CONFIGURATION_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_FIFO_CONFIGURATION_2]=(uint8_t*)&_write_reg.FIFO_CONFIGURATION_2;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_SYSTEM_SYNC]=(uint8_t*)&_write_reg.SYSTEM_SYNC;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_SYSTEM_CONFIGURATION]=(uint8_t*)&_write_reg.SYSTEM_CONFIGURATION;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_PIN_FUNCTIONAL_CONFIGURATION]=(uint8_t*)&_write_reg.PIN_FUNCTIONAL_CONFIGURATION;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_OUTPUT_PIN_CONFIGURATION]=(uint8_t*)&_write_reg.OUTPUT_PIN_CONFIGURATION;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_I2C_BROADCAST]=(uint8_t*)&_write_reg.I2C_BROADCAST_ADDRESS;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_1]=(uint8_t*)&_write_reg.PLL_CONFIGURATION_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_2]=(uint8_t*)&_write_reg.PLL_CONFIGURATION_2;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_3]=(uint8_t*)&_write_reg.PLL_CONFIGURATION_3;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_4]=(uint8_t*)&_write_reg.PLL_CONFIGURATION_4;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_1]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_2]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_2;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_3]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_3;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_4]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_4;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_5]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_5;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_6]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_6;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_LOW_THRESHOLD]=(uint8_t*)&_write_reg.BIOZ_LOW_THRESHOLD;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_HIGH_THRESHOLD]=(uint8_t*)&_write_reg.BIOZ_HIGH_THRESHOLD;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_7]=(uint8_t*)&_write_reg.BIOZ_CONFIGURATION_7;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1]=(uint8_t*)&_write_reg.BIOZ_MUX_CONFIGURATION_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_2]=(uint8_t*)&_write_reg.BIOZ_MUX_CONFIGURATION_2;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3]=(uint8_t*)&_write_reg.BIOZ_MUX_CONFIGURATION_3;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_4]=(uint8_t*)&_write_reg.BIOZ_MUX_CONFIGURATION_4;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_DC_LEADS_CONFIGURATION]=(uint8_t*)&_write_reg.DC_LEADS_CONFIGURATION;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_DC_LEAD_DETECT_THRESHOLD]=(uint8_t*)&_write_reg.DC_LEAD_DETECT_THRESHOLD;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_LEAD_BIAS_CONFIGURATION]=(uint8_t*)&_write_reg.LEAD_BIAS_CONFIGURATION;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_INTERRUPT_ENABLE_1]=(uint8_t*)&_write_reg.INTERRUPT_ENABLE_1;
    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_INTERRUPT_ENABLE_2]=(uint8_t*)&_write_reg.INTERRUPT_ENABLE_2;

    _max30009_write_registers_pointer_array[MAX30009_ADDRESS_PART_ID]=(uint8_t*)&_write_reg.PART_ID;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_STATUS_1]=(uint8_t*)&_read_reg.STATUS_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_STATUS_2]=(uint8_t*)&_read_reg.STATUS_2;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_WRITE_POINTER]=(uint8_t*)&_read_reg.FIFO_WRITE_POINTER;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_READ_POINTER]=(uint8_t*)&_read_reg.FIFO_READ_POINTER;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_COUNTER_1]=(uint8_t*)&_read_reg.FIFO_COUNTER_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_COUNTER_2]=(uint8_t*)&_read_reg.FIFO_COUNTER_2;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_DATA_REGISTER]=(uint8_t*)&_read_reg.FIFO_DATA_REGISTER;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_CONFIGURATION_1]=(uint8_t*)&_read_reg.FIFO_CONFIGURATION_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_FIFO_CONFIGURATION_2]=(uint8_t*)&_read_reg.FIFO_CONFIGURATION_2;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_SYSTEM_SYNC]=(uint8_t*)&_read_reg.SYSTEM_SYNC;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_SYSTEM_CONFIGURATION]=(uint8_t*)&_read_reg.SYSTEM_CONFIGURATION;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_PIN_FUNCTIONAL_CONFIGURATION]=(uint8_t*)&_read_reg.PIN_FUNCTIONAL_CONFIGURATION;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_OUTPUT_PIN_CONFIGURATION]=(uint8_t*)&_read_reg.OUTPUT_PIN_CONFIGURATION;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_I2C_BROADCAST]=(uint8_t*)&_read_reg.I2C_BROADCAST_ADDRESS;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_1]=(uint8_t*)&_read_reg.PLL_CONFIGURATION_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_2]=(uint8_t*)&_read_reg.PLL_CONFIGURATION_2;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_3]=(uint8_t*)&_read_reg.PLL_CONFIGURATION_3;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_PLL_CONFIGURATION_4]=(uint8_t*)&_read_reg.PLL_CONFIGURATION_4;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_1]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_2]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_2;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_3]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_3;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_4]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_4;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_5]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_5;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_6]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_6;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_LOW_THRESHOLD]=(uint8_t*)&_read_reg.BIOZ_LOW_THRESHOLD;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_HIGH_THRESHOLD]=(uint8_t*)&_read_reg.BIOZ_HIGH_THRESHOLD;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_CONFIGURATION_7]=(uint8_t*)&_read_reg.BIOZ_CONFIGURATION_7;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1]=(uint8_t*)&_read_reg.BIOZ_MUX_CONFIGURATION_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_2]=(uint8_t*)&_read_reg.BIOZ_MUX_CONFIGURATION_2;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3]=(uint8_t*)&_read_reg.BIOZ_MUX_CONFIGURATION_3;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_4]=(uint8_t*)&_read_reg.BIOZ_MUX_CONFIGURATION_4;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_DC_LEADS_CONFIGURATION]=(uint8_t*)&_read_reg.DC_LEADS_CONFIGURATION;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_DC_LEAD_DETECT_THRESHOLD]=(uint8_t*)&_read_reg.DC_LEAD_DETECT_THRESHOLD;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_LEAD_BIAS_CONFIGURATION]=(uint8_t*)&_read_reg.LEAD_BIAS_CONFIGURATION;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_INTERRUPT_ENABLE_1]=(uint8_t*)&_read_reg.INTERRUPT_ENABLE_1;
    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_INTERRUPT_ENABLE_2]=(uint8_t*)&_read_reg.INTERRUPT_ENABLE_2;

    _max30009_read_registers_pointer_array[MAX30009_ADDRESS_PART_ID]=(uint8_t*)&_read_reg.PART_ID;

    calculate_all_system_frequency();

    _calib_data.ref_value=100.0;
    _calib_data.calib_source=MAX30009_CALIB_SOURCE_CALIBPORT;
    _calib_data.calib_state=MAX30009_CALIB_STATE_NEED_CALIB;
    _calib_data.calibrate_current=MAX30009_CURRENT_AMP_64uA;
    _calib_data.calibrate_frequency=100000;

    _calib_data.I_offset=0;
    _calib_data.Q_offset=0;
    _calib_data.I_cal_in=1;
    _calib_data.Q_cal_in=1;
    _calib_data.I_cal_quad=1;
    _calib_data.Q_cal_quad=1;
    _calib_data.I_coef=1;
    _calib_data.Q_coef=1;
    _calib_data.I_phase_coef=1;
    _calib_data.Q_phase_coef=1;

    _lib_is_init=true;



}


inline bool MAX30009_LIB::read_status(MAX30009_STATUS_STRUCT_TYPE *status)
{
    bool read_reg_result=true;
    if (read_register(MAX30009_ADDRESS_STATUS_1)==false)
    {
        read_reg_result=false;
    }
    if (read_register(MAX30009_ADDRESS_STATUS_2)==false)
    {
        read_reg_result=false;
    }

    if (read_reg_result==true)
    {
        status->a_full_flag=(bool)_read_reg.STATUS_1.A_FULL;
        status->FIFO_data_ready=(bool)_read_reg.STATUS_1.FIFO_DATA_RDY;
        status->frequency_unlock=(bool)_read_reg.STATUS_1.FREQ_UNLOCK;
        status->frequency_lock=(bool)_read_reg.STATUS_1.FREQ_LOCK;
        status->phase_unlock=(bool)_read_reg.STATUS_1.PHASE_UNLOCK;
        status->phase_lock=(bool)_read_reg.STATUS_1.PHASE_LOCK;
        status->power_ready=not((bool)_read_reg.STATUS_1.PWR_RDY);

        status->LON_BIOZ_active=(bool)_read_reg.STATUS_2.LON;
        status->BIOZ_over_level=(bool)_read_reg.STATUS_2.BIOZ_OVER;
        status->BIOZ_under_level=(bool)_read_reg.STATUS_2.BIOZ_UNDR;
        status->DRVN_out_of_range=(bool)_read_reg.STATUS_2.DRV_OOR;
        status->DC_LOFF_BIP_overlimit=(bool)_read_reg.STATUS_2.DC_LOFF_PH;
        status->DC_LOFF_BIP_underlimit=(bool)_read_reg.STATUS_2.DC_LOFF_PL;
        status->DC_LOFF_BIN_overlimit=(bool)_read_reg.STATUS_2.DC_LOFF_NH;
        status->DC_LOFF_BIN_underlimit=(bool)_read_reg.STATUS_2.DC_LOFF_NL;
    }

    return read_reg_result;
}

inline bool MAX30009_LIB::set_reference_clock_source(MAX30009_REFCLK_SOURCE_ENUM_TYPE clock_source)
{

    if (clock_source==MAX30009_REFCLK_SRC_INT_32000)
    {
        _write_reg.PLL_CONFIGURATION_4.CLK_FREQ_SEL=0; //set internal source frequency 32.0kHz
        _write_reg.PLL_CONFIGURATION_4.REF_CLK_SEL=0; //set internal source
    }
    else if (clock_source==MAX30009_REFCLK_SRC_INT_32768)
    {
        _write_reg.PLL_CONFIGURATION_4.CLK_FREQ_SEL=1; //set internal source frequency 32.768kHz
        _write_reg.PLL_CONFIGURATION_4.REF_CLK_SEL=0; //set internal source
    }
    else     if (clock_source==MAX30009_REFCLK_SRC_EXT_32000)
    {
        _write_reg.PLL_CONFIGURATION_4.CLK_FREQ_SEL=0; //set external source frequency 32.0kHz
        _write_reg.PLL_CONFIGURATION_4.REF_CLK_SEL=1; //set external source
    }
    else if (clock_source==MAX30009_REFCLK_SRC_EXT_32768)
    {
        _write_reg.PLL_CONFIGURATION_4.CLK_FREQ_SEL=1; //set external source frequency 32.768kHz
        _write_reg.PLL_CONFIGURATION_4.REF_CLK_SEL=1; //set external source
    }
    else
    {
        //error source type
        return false;
    }

    bool write_reg_result=write_register(MAX30009_ADDRESS_PLL_CONFIGURATION_4);

    calculate_all_system_frequency();
    return write_reg_result;
}

inline bool MAX30009_LIB::set_drive_frequency(uint32_t drive_freq, uint32_t desired_ADC_freq)
{
    MAX30009_FIND_CLOCKS_STRUCT_TYPE best_clk_solution;

    //check reference clock
    uint32_t REF_CLK=0;
    if (_write_reg.PLL_CONFIGURATION_4.CLK_FREQ_SEL==0)
    {
        REF_CLK=320000; // in 1/10 Hertz
    }
    else
    {
        REF_CLK=327680; // in 1/10 Hertz
    }

    if (drive_freq<MAX30009_MIN_DRIVE_FREQ)
    {
        return false;
    }
    if (drive_freq>MAX30009_MAX_DRIVE_FREQ)
    {
        return false;
    }


    for (uint32_t tr=0; tr<MAX30009_FIND_CLK_SOLUTION_TRY_COUNT; tr++)
    {
        best_clk_solution.solution_count=0;
        uint32_t min_adc_sample_rate_delta=0xFFFFFF;
        //calculate all possible options for PLL
        for (uint8_t DSR=0; DSR<MAX30009_DAC_OSR_SIZE; DSR++)
        {
            for (uint8_t KDIV=0; KDIV<MAX30009_KDIV_SIZE; KDIV++)
            {
                uint32_t calc_BIOZ_SYNTH_CLK=drive_freq * MAX30009_DAC_OSR_divider[DSR];
                uint32_t calc_PLL_CLK=calc_BIOZ_SYNTH_CLK*MAX30009_KDIV_divider[KDIV];

                uint32_t M=(calc_PLL_CLK+(REF_CLK/2))/REF_CLK;
                uint32_t real_PLL_CLK=M*REF_CLK;
                //check pll range
                if (real_PLL_CLK<MAX30009_MIN_PLL_FREQ)
                {
                    continue;   //PLL_CLK is low
                }
                if (real_PLL_CLK>MAX30009_MAX_PLL_FREQ)
                {
                    continue;   //PLL_CLK is high
                }

                uint32_t real_BIOZ_SYNTH_CLK=real_PLL_CLK/MAX30009_KDIV_divider[KDIV];
                //check BIOZ_SYNTH_CLK range
                if (real_BIOZ_SYNTH_CLK<MAX30009_MIN_BIOZ_SYNTH_FREQ)
                {
                    continue;   //BIOZ_SYNTH_CLK is low
                }
                if (real_BIOZ_SYNTH_CLK>MAX30009_MAX_BIOZ_SYNTH_FREQ)
                {
                    continue;   //BIOZ_SYNTH_CLK is high
                }

                uint32_t real_drive_freq=real_BIOZ_SYNTH_CLK/MAX30009_DAC_OSR_divider[DSR];
                uint32_t drive_freq_error=(labs((int32_t)drive_freq-(int32_t)real_drive_freq));
                //check freq error size
                if (drive_freq_error>real_drive_freq/500)
                {
                    continue;   //drive frequency error more 0.2%
                }

                for (uint8_t NDIV=0; NDIV<MAX30009_NDIV_SIZE; NDIV++)
                {
                    uint32_t real_BIOZ_ADC_CLK=real_PLL_CLK/MAX30009_NDIV_divider[NDIV];
                    //check BIOZ_ADC_CLK range
                    if (real_BIOZ_ADC_CLK<MAX30009_MIN_BIOZ_ADCCLK_FREQ)
                    {
                        continue;   //BIOZ_ADC_CLK is low
                    }
                    if (real_BIOZ_ADC_CLK>MAX30009_MAX_BIOZ_ADCCLK_FREQ)
                    {
                        continue;   //BIOZ_ADC_CLK is high
                    }

                    for (uint32_t ASR=0; ASR<MAX30009_ADC_OSR_SIZE; ASR++)
                    {
                        uint32_t dac_divider=MAX30009_KDIV_divider[KDIV]*MAX30009_DAC_OSR_divider[DSR];
                        uint32_t adc_divider=MAX30009_NDIV_divider[NDIV]*MAX30009_ADC_OSR_divider[ASR];

                        if (dac_divider>adc_divider)
                        {
                            continue;   //ADC work faster than DAC
                        }
                        if (adc_divider%dac_divider!=0)
                        {
                            continue;   //ratio DAC/ADC is not integer
                        }

                        best_clk_solution.solution_count++; //counter good solution for set frequency

                        int32_t real_adc_sample_rate=real_BIOZ_ADC_CLK/MAX30009_ADC_OSR_divider[ASR];

                        //                    qDebug()<< drive_freq << MAX30009_DAC_OSR_divider[DSR] << calc_BIOZ_SYNTH_CLK << MAX30009_KDIV_divider[KDIV] << calc_PLL_CLK << M
                        //                            << real_PLL_CLK << real_BIOZ_SYNTH_CLK  << real_drive_freq << drive_freq_error
                        //                            << MAX30009_NDIV_divider[NDIV] << real_BIOZ_ADC_CLK << MAX30009_ADC_OSR_divider[ASR] <<real_adc_sample_rate
                        //                            << adc_divider << dac_divider;

                        uint32_t delta_t=labs((int32_t)desired_ADC_freq-real_adc_sample_rate);
                        if (delta_t<min_adc_sample_rate_delta)
                        {
                            //new ADC sampling rate is closer to the desired
                            min_adc_sample_rate_delta=delta_t;

                            best_clk_solution.REF_CLK=REF_CLK;
                            best_clk_solution.PLL_CLK=real_PLL_CLK;
                            best_clk_solution.BIOZ_SYNTH_CLK=real_BIOZ_SYNTH_CLK;

                            best_clk_solution.set_drive_freq=drive_freq;
                            best_clk_solution.drive_freq=real_drive_freq;
                            best_clk_solution.drive_freq_error=drive_freq_error;

                            best_clk_solution.BIOZ_ADC_CLK=real_BIOZ_ADC_CLK;
                            best_clk_solution.desire_ADC_sample_rate=desired_ADC_freq;
                            best_clk_solution.ADC_sample_rate=real_adc_sample_rate;


                            best_clk_solution.MDIV=M-1;
                            best_clk_solution.KDIV=KDIV;
                            best_clk_solution.BIOZ_DAC_OSR=DSR;
                            best_clk_solution.NDIV=NDIV;
                            best_clk_solution.BIOZ_ADC_OSR=ASR;

                        }

                    }

                }
            }
        }
        if (best_clk_solution.solution_count==0)
        {
            // no found solution clk
            drive_freq=drive_freq+10; //inc  1Hz to driver frequency and start new try
        }
        else // found solution clk
        {
            //out from find clk solution cycle
            break;
        }
    }

    _best_clk_solution=best_clk_solution;

    if (best_clk_solution.solution_count==0)
    {
        return  false;   //no clk solution found
    }

    //If F_BIOZ = BIOZ_ADC_CLK / 2, set BIOZ_INA_CHOP_EN = 0, otherwise set to 1
    if (best_clk_solution.drive_freq==best_clk_solution.BIOZ_ADC_CLK/2)
    {
        _write_reg.BIOZ_CONFIGURATION_7.BIOZ_INA_CHOP_EN=0;
    }
    else
    {
        _write_reg.BIOZ_CONFIGURATION_7.BIOZ_INA_CHOP_EN=1;
    }

    //If F_BIOZ = BIOZ_ADC_CLK / 8, set BIOZ_CH_FSEL = 1, otherwise set to 0
    if (best_clk_solution.drive_freq==best_clk_solution.BIOZ_ADC_CLK/8)
    {
        _write_reg.BIOZ_CONFIGURATION_7.BIOZ_CH_FSEL=1;
    }
    else
    {
        _write_reg.BIOZ_CONFIGURATION_7.BIOZ_CH_FSEL=1;
    }

    _write_reg.PLL_CONFIGURATION_1.MDIV_H=(best_clk_solution.MDIV>>8) & 0x03;
    _write_reg.PLL_CONFIGURATION_1.NDIV=best_clk_solution.NDIV & 0x01;
    _write_reg.PLL_CONFIGURATION_1.KDIV=best_clk_solution.KDIV & 0x0F;

    _write_reg.PLL_CONFIGURATION_2.MDIV_L=best_clk_solution.MDIV & 0xFF;

    _write_reg.BIOZ_CONFIGURATION_1.BIOZ_DAC_OSR=best_clk_solution.BIOZ_DAC_OSR & 0x03;
    _write_reg.BIOZ_CONFIGURATION_1.BIOZ_ADC_OSR=best_clk_solution.BIOZ_ADC_OSR & 0x07;

    bool write_reg_result=true;
    if (write_register(MAX30009_ADDRESS_PLL_CONFIGURATION_1)==false)
    {
        write_reg_result=false;
    }
    if (write_register(MAX30009_ADDRESS_PLL_CONFIGURATION_2)==false)
    {
        write_reg_result=false;
    }
    if (write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_1)==false)
    {
        write_reg_result=false;
    }
    if (write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_7)==false)
    {
        write_reg_result=false;
    }

    calculate_all_system_frequency();

    return write_reg_result;

}

inline bool MAX30009_LIB::set_PLL_state(bool PLL_enable)
{
    _write_reg.PLL_CONFIGURATION_1.PLL_EN=(uint8_t)PLL_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_PLL_CONFIGURATION_1);

    calculate_all_system_frequency();

    return write_reg_result;
}

inline void MAX30009_LIB::calculate_all_system_frequency()
{
    if (_read_reg.PLL_CONFIGURATION_4.CLK_FREQ_SEL==0)
    {
        _all_clock_requency.REF_CLK=320000; // in 1/10 Hertz
    }
    else
    {
        _all_clock_requency.REF_CLK=327680; // in 1/10 Hertz
    }

    _all_clock_requency.KDIV_VALUE=MAX30009_KDIV_divider[_read_reg.PLL_CONFIGURATION_1.KDIV];
    _all_clock_requency.NDIV_VALUE=MAX30009_NDIV_divider[_read_reg.PLL_CONFIGURATION_1.NDIV];
    _all_clock_requency.BIOZ_DAC_OSR_VALUE=MAX30009_DAC_OSR_divider[_read_reg.BIOZ_CONFIGURATION_1.BIOZ_DAC_OSR];
    _all_clock_requency.BIOZ_ADC_OSR_VALUE=MAX30009_ADC_OSR_divider[_read_reg.BIOZ_CONFIGURATION_1.BIOZ_ADC_OSR];

    _all_clock_requency.MDIV_VALUE=_read_reg.PLL_CONFIGURATION_1.MDIV_H;
    _all_clock_requency.MDIV_VALUE=_all_clock_requency.MDIV_VALUE<<8;
    _all_clock_requency.MDIV_VALUE=_all_clock_requency.MDIV_VALUE+_read_reg.PLL_CONFIGURATION_2.MDIV_L;


    _all_clock_requency.PLL_CLK=_all_clock_requency.REF_CLK*(_all_clock_requency.MDIV_VALUE+1);
    if (_all_clock_requency.KDIV_VALUE!=0) _all_clock_requency.BIOZ_SYNTH_CLK=_all_clock_requency.PLL_CLK/_all_clock_requency.KDIV_VALUE;
    if (_all_clock_requency.BIOZ_DAC_OSR_VALUE!=0) _all_clock_requency.BIOZ_DRIVE_FREQ=_all_clock_requency.BIOZ_SYNTH_CLK/_all_clock_requency.BIOZ_DAC_OSR_VALUE;

    if (_all_clock_requency.NDIV_VALUE!=0) _all_clock_requency.BIOZ_ADC_CLK=_all_clock_requency.PLL_CLK/_all_clock_requency.NDIV_VALUE;
    if(_all_clock_requency.BIOZ_ADC_OSR_VALUE!=0) _all_clock_requency.BIOZ_ADC_SAMPLE_RATE=_all_clock_requency.BIOZ_ADC_CLK/_all_clock_requency.BIOZ_ADC_OSR_VALUE;

    _all_clock_requency.PLL_enable=(bool)_write_reg.PLL_CONFIGURATION_1.PLL_EN;
}

inline MAX30009_ALL_CLOCKS_FREQ_TYPE MAX30009_LIB::get_all_frequency()
{
    return _all_clock_requency;
}

inline bool MAX30009_LIB::set_BIOZ_constant_current_mode(MAX30009_CURRENT_AMP_ENUM_TYPE current_value)
{
    calculate_all_system_frequency();
    //check current limit
    if (current_value==MAX30009_CURRENT_AMP_1_28mA)
    {
        if (_all_clock_requency.BIOZ_DRIVE_FREQ<MAX30009_MIN_FREQ_FOR_1_28mA)
        {
            current_value=MAX30009_CURRENT_AMP_640uA;
        }
    }

    if (current_value==MAX30009_CURRENT_AMP_640uA)
    {
        if (_all_clock_requency.BIOZ_DRIVE_FREQ<MAX30009_MIN_FREQ_FOR_640uA)
        {
            current_value=MAX30009_CURRENT_AMP_256uA;
        }
    }

    if (current_value==MAX30009_CURRENT_AMP_256uA)
    {
        if (_all_clock_requency.BIOZ_DRIVE_FREQ<MAX30009_MIN_FREQ_FOR_256uA)
        {
            current_value=MAX30009_CURRENT_AMP_128uA;
        }
    }

    if (current_value==MAX30009_CURRENT_AMP_128uA)
    {
        if (_all_clock_requency.BIOZ_DRIVE_FREQ<MAX30009_MIN_FREQ_FOR_128uA)
        {
            current_value=MAX30009_CURRENT_AMP_64uA;
        }
    }

    uint8_t BIOZ_IDRV_RGE= (current_value>>4) & 0x03;
    uint8_t BIOZ_VDRV_MAG= current_value & 0x03;

    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_DRV_MODE=MAX30009_BIOZ_DRV_MODE_CURRENT;
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_IDRV_RGE=BIOZ_IDRV_RGE;
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG=BIOZ_VDRV_MAG;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_3);

    calculate_BIOZ_modes();


    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_constant_voltage_mode(MAX30009_VOLTAGE_AMP_ENUM_TYPE voltage_value)
{
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_DRV_MODE=MAX30009_BIOZ_DRV_MODE_VOLTAGE;
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG=(uint8_t)voltage_value & 0x03;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_3);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_H_brifge_mode()
{
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_DRV_MODE=MAX30009_BIOZ_DRV_MODE_H_BRIDGE;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_3);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_drive_standby_mode()
{
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_DRV_MODE=MAX30009_BIOZ_DRV_MODE_STANDBY;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_3);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_ext_capacitor_state(bool ext_cap_enable)
{
    _write_reg.BIOZ_CONFIGURATION_6.BIOZ_EXT_CAP=(uint8_t)ext_cap_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_6);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_ext_resistor_state(bool ext_res_enable, uint32_t resistance)
{
    _write_reg.BIOZ_CONFIGURATION_3.BIOZ_EXT_RES=(uint8_t)ext_res_enable;

    _bioz_data.external_current_resistor_value=resistance;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_3);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_DC_restore(bool DCres_enable)
{
    _write_reg.BIOZ_CONFIGURATION_6.BIOZ_DC_RESTORE=(uint8_t)DCres_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_6);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_DRV_RESET(bool DRV_RESET_enable)
{
    _write_reg.BIOZ_CONFIGURATION_6.BIOZ_DRV_RESET=(uint8_t)DRV_RESET_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_6);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_amplifier_bandwidth(MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE bandwidth_mode)
{
    _write_reg.BIOZ_CONFIGURATION_6.BIOZ_AMP_BW=(uint8_t)bandwidth_mode;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_6);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_amplifier_range(MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE range_mode)
{
    _write_reg.BIOZ_CONFIGURATION_6.BIOZ_AMP_RGE=(uint8_t)range_mode;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_6);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_bandgap_state(bool bandgap_enable)
{
    _write_reg.BIOZ_CONFIGURATION_1.BIOZ_BG_EN=(uint8_t)bandgap_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_I_channel_state(bool I_channel_enable)
{
    _write_reg.BIOZ_CONFIGURATION_1.BIOZ_I_EN=(uint8_t)I_channel_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_I_CLK_PHASE(bool BIOZ_I_CLK_PHASE_enable)
{
    _write_reg.BIOZ_CONFIGURATION_7.BIOZ_I_CLK_PHASE=(uint8_t) BIOZ_I_CLK_PHASE_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_7);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_Q_CLK_PHASE(bool BIOZ_Q_CLK_PHASE_enable)
{
    _write_reg.BIOZ_CONFIGURATION_7.BIOZ_Q_CLK_PHASE=(uint8_t) BIOZ_Q_CLK_PHASE_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_7);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_Q_channel_state(bool Q_channel_enable)
{
    _write_reg.BIOZ_CONFIGURATION_1.BIOZ_Q_EN=(uint8_t)Q_channel_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_input_HP_filter(MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM filter_value)
{
    _write_reg.BIOZ_CONFIGURATION_5.BIOZ_AHPF=(uint8_t)filter_value;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_5);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_out_DHP_filter(MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE filter_value)
{
    _write_reg.BIOZ_CONFIGURATION_2.BIOZ_DHPF=(uint8_t)filter_value;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_2);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_out_DLP_filter(MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE filter_value)
{
    _write_reg.BIOZ_CONFIGURATION_2.BIOZ_DLPF=(uint8_t)filter_value;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_2);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_INA_low_mode(bool INA_low_mode_enable)
{
    _write_reg.BIOZ_CONFIGURATION_5.BIOZ_INA_MODE=(uint8_t)INA_low_mode_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_5);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_demodulation_state(bool demodulation_enable)
{
    demodulation_enable=not(demodulation_enable); // register is disable demodulation

    _write_reg.BIOZ_CONFIGURATION_5.BIOZ_DM_DIS=(uint8_t)demodulation_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_5);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_total_gain(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE total_gain)
{
    _write_reg.BIOZ_CONFIGURATION_5.BIOZ_GAIN=(uint8_t)total_gain;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_5);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_BIOZ_fast_start_mode(MAX30009_BIOZ_FAST_START_MODE_ENUM_TYPE fast_start_mode)
{
    _write_reg.BIOZ_CONFIGURATION_4.BIOZ_FAST_START_EN=(uint8_t)fast_start_mode & 0x01;
    _write_reg.BIOZ_CONFIGURATION_4.BIOZ_FAST_MANUAL=(uint8_t)(fast_start_mode>>1) & 0x01;


    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_CONFIGURATION_4);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline void MAX30009_LIB::calculate_BIOZ_modes()
{
    _bioz_data.drive_mode=(MAX30009_BIOZ_DRV_MODE_ENUM_TYPE)_read_reg.BIOZ_CONFIGURATION_3.BIOZ_DRV_MODE;

    uint8_t current_amp=_read_reg.BIOZ_CONFIGURATION_3.BIOZ_IDRV_RGE;
    current_amp=current_amp<<4;
    current_amp=current_amp+_read_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG;
    _bioz_data.current_select=(MAX30009_CURRENT_AMP_ENUM_TYPE)current_amp;
    _bioz_data.current_RMS=drv_current_RMS_arr[_read_reg.BIOZ_CONFIGURATION_3.BIOZ_IDRV_RGE][_read_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG];
    _bioz_data.current_peak=drv_current_peak_arr[_read_reg.BIOZ_CONFIGURATION_3.BIOZ_IDRV_RGE][_read_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG];


    _bioz_data.voltage_select=(MAX30009_VOLTAGE_AMP_ENUM_TYPE)_read_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG;
    _bioz_data.voltage_RMS=drv_voltage_RMS_arr[_read_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG];
    _bioz_data.voltage_peak=drv_voltage_peak_arr[_read_reg.BIOZ_CONFIGURATION_3.BIOZ_VDRV_MAG];

    _bioz_data.external_capacitor_enable=(bool)_read_reg.BIOZ_CONFIGURATION_6.BIOZ_EXT_CAP;
    _bioz_data.external_current_resistor=(bool)_read_reg.BIOZ_CONFIGURATION_3.BIOZ_EXT_RES;

    _bioz_data.Amplifier_bandwidth=(MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE)_read_reg.BIOZ_CONFIGURATION_6.BIOZ_AMP_BW;
    _bioz_data.Amplifier_range=(MAX30009_BIOZ_AMPLF_MODE_ENUM_TYPE)_read_reg.BIOZ_CONFIGURATION_6.BIOZ_AMP_RGE;

    _bioz_data.bandgap_enable=(bool)_read_reg.BIOZ_CONFIGURATION_1.BIOZ_BG_EN;
    _bioz_data.I_channel_enable=(bool)_read_reg.BIOZ_CONFIGURATION_1.BIOZ_I_EN;
    _bioz_data.Q_channel_enable=(bool)_read_reg.BIOZ_CONFIGURATION_1.BIOZ_Q_EN;

    _bioz_data.input_HP_filter_select=(MAX30009_BIOZ_INPUT_HP_FILTER_VALUE_ENUM_TYPE)_read_reg.BIOZ_CONFIGURATION_5.BIOZ_AHPF;
    _bioz_data.input_HP_filter_frequency=inp_HP_filter_value_arr[_read_reg.BIOZ_CONFIGURATION_5.BIOZ_AHPF];

    _bioz_data.dc_restore_enable=(bool)_read_reg.BIOZ_CONFIGURATION_6.BIOZ_DC_RESTORE;
    _bioz_data.INA_low_mode_enable=(bool)_read_reg.BIOZ_CONFIGURATION_5.BIOZ_INA_MODE;

    _bioz_data.INA_chop_enable=(bool)_read_reg.BIOZ_CONFIGURATION_7.BIOZ_INA_CHOP_EN;
    _bioz_data.channel_freq_sel_enable=(bool)_read_reg.BIOZ_CONFIGURATION_7.BIOZ_CH_FSEL;

    _bioz_data.demodulation_enable=not((bool)_read_reg.BIOZ_CONFIGURATION_5.BIOZ_DM_DIS);

    _bioz_data.total_gain_select=(MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE)_read_reg.BIOZ_CONFIGURATION_5.BIOZ_GAIN;
    _bioz_data.total_gain_value=total_gain_value_arr[_read_reg.BIOZ_CONFIGURATION_5.BIOZ_GAIN];

    uint8_t fast_mode=_write_reg.BIOZ_CONFIGURATION_4.BIOZ_FAST_MANUAL;
    fast_mode=(fast_mode<<1)+_write_reg.BIOZ_CONFIGURATION_4.BIOZ_FAST_START_EN;
    _bioz_data.fast_start_mode=(MAX30009_BIOZ_FAST_START_MODE_ENUM_TYPE)fast_mode;

    _bioz_data.out_DHP_filter=(MAX30009_BIOZ_DIGITAL_OUT_HP_FILTER_ENUM_TYPE) _read_reg.BIOZ_CONFIGURATION_2.BIOZ_DHPF;
    _bioz_data.out_DLP_filter=(MAX30009_BIOZ_DIGITAL_OUT_LP_FILTER_ENUM_TYPE) _read_reg.BIOZ_CONFIGURATION_2.BIOZ_DLPF;
}

inline MAX30009_BIOZ_DATA_TYPE MAX30009_LIB::get_BIOZ_data()
{
    return _bioz_data;
}

inline bool MAX30009_LIB::set_MUX_DRVP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM DRVP_assign)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_3.DRVP_ASSIGN=(uint8_t)DRVP_assign;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3);

    calculate_MUX_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_BIP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM BIP_assign)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_3.BIP_ASSIGN=(uint8_t)BIP_assign;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3);

    calculate_MUX_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_BIN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM BIN_assign)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_3.BIN_ASSIGN=(uint8_t)BIN_assign;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3);

    calculate_MUX_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_DRVN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM DRVN_assign)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_3.DRVN_ASSIGN=(uint8_t)DRVN_assign;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_3);

    calculate_MUX_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_state(bool MUX_enable)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_1.MUX_EN=(uint8_t)MUX_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_CAL_state(bool MUX_CAL_enable)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_1.CAL_EN=(uint8_t)MUX_CAL_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_CAL_ONLY_state(bool MUX_CAL_ONLY_enable)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_1.CONNECT_CAL_ONLY=(uint8_t)MUX_CAL_ONLY_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_Resistor_Load_non_GSR(MAX30009_BMUX_RSEL_ENUM_TYPE rsel_value)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_1.BMUX_RSEL=(uint8_t)rsel_value;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_Resistor_Load_GSR(MAX30009_BMUX_GSR_RSEL_ENUM_TYPE rsel_value)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_2.BMUX_GSR_RSEL=(uint8_t)rsel_value;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_2);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_BIST_enable(bool enable)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_1.BMUX_BIST_EN=(uint8_t)enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_1);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline bool MAX30009_LIB::set_MUX_GSR_enable(bool enable)
{
    _write_reg.BIOZ_MUX_CONFIGURATION_2.GSR_LOAD_EN=(uint8_t)enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_BIOZ_MUX_CONFIGURATION_2);

    calculate_BIOZ_modes();

    return write_reg_result;
}

inline void MAX30009_LIB::calculate_MUX_modes()
{
    _mux_data.DRVP_assign=(MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM)_read_reg.BIOZ_MUX_CONFIGURATION_3.DRVP_ASSIGN;
    _mux_data.BIP_assign=(MAX30009_MUX_BIP_DRVP_ASSIGN_ENUM)_read_reg.BIOZ_MUX_CONFIGURATION_3.BIP_ASSIGN;
    _mux_data.BIN_assign=(MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM)_read_reg.BIOZ_MUX_CONFIGURATION_3.BIN_ASSIGN;
    _mux_data.DRVN_assign=(MAX30009_MUX_BIN_DRVN_ASSIGN_ENUM)_read_reg.BIOZ_MUX_CONFIGURATION_3.DRVN_ASSIGN;

    _mux_data.MUX_enable=(bool)_read_reg.BIOZ_MUX_CONFIGURATION_1.MUX_EN;
    _mux_data.CAL_enable=(bool)_read_reg.BIOZ_MUX_CONFIGURATION_1.CAL_EN;
    _mux_data.CAL_ONLY_enable=(bool)_read_reg.BIOZ_MUX_CONFIGURATION_1.CONNECT_CAL_ONLY;
}

inline MAX30009_MUX_DATA_TYPE MAX30009_LIB::get_MUX_data()
{
    return _mux_data;
}

inline bool MAX30009_LIB::get_last_ADC_value(MAX30009_FIFO_DATA *I_channel_value, MAX30009_FIFO_DATA *Q_channel_value)
{
    return  false;
    //    bool result=true;
    //    MAX30009_FIFO_DATA temp_data_arr[MAX30009_FIND_LAV_REQ_SIZE];
    //    uint16_t FIFO_data_count=0;
    //    if (get_FIFO_data_count(&FIFO_data_count)==true)
    //    {
    //        int32_t data_count=FIFO_data_count;
    //        while(data_count>0)
    //        {
    //            int32_t request_items=MAX30009_FIND_LAV_REQ_SIZE;
    //            if (request_items>data_count) {request_items=data_count;}
    //            uint8_t real_items_read=0;
    //            if (read_FIFO_data(temp_data_arr,request_items,&real_items_read)==true)
    //            {
    //                for (uint32_t i=0;i<real_items_read;i++)
    //                {
    //                    if (temp_data_arr[i].data_source==MAX30009_I_CHANNEL){*I_channel_value=temp_data_arr[i];}
    //                    if (temp_data_arr[i].data_source==MAX30009_Q_CHANNEL){*Q_channel_value=temp_data_arr[i];}
    //                }
    //            }
    //            else
    //            {
    //                result=false;
    //            }
    //            data_count=data_count-request_items;
    //        }
    //    }
    //    else
    //    {
    //        result=false;
    //    }
    //    return result;
}

inline bool MAX30009_LIB::read_FIFO_data(MAX30009_FIFO_DATA *FIFO_data_array, int32_t data_count, uint8_t *real_data_count)
{
    return  false;
    //    bool result=true;
    //    uint8_t request_array[MAX30009_FIFO_REQUEST_SIZE];
    //    request_array[0]=(uint8_t)MAX30009_ADDRESS_FIFO_DATA_REGISTER;
    //    request_array[1]=MAX30009_REGISTER_READ_DIRECT;
    //    for (uint32_t rb=2;rb<MAX30009_FIFO_REQUEST_SIZE;rb++)
    //    {
    //        request_array[rb]=MAX30009_DUMMY_BYTE;
    //    }
    //
    //    *real_data_count=0;
    //    uint8_t answer_array[MAX30009_FIFO_REQUEST_SIZE];
    //    while(data_count>0)
    //    {
    //        int32_t request_items=MAX30009_FIFO_REQUEST_ITEMS;
    //        if (request_items>data_count) {request_items=data_count;}
    //        uint8_t request_size=(request_items*MAX30009_FIFO_DATA_BYTES_SIZE)+2;
    //
    //        if (SPI_data_transfer(request_array,answer_array,request_size)==true)
    //        {
    //            for (uint32_t db=2;db<request_size;db=db+MAX30009_FIFO_DATA_BYTES_SIZE )
    //            {
    //                MAX30009_FIFO_DATA encoded_FIFO_data=encode_FIFO_data(&answer_array[db]);
    //                if (encoded_FIFO_data.data_source==MAX30009_ERROR_DATA_SOURCE)
    //                {
    //                    //last read data is error. FIFO buffer is empty
    //                    return result;
    //                }
    //
    //                FIFO_data_array[*real_data_count]=encoded_FIFO_data;
    //                (*real_data_count)++;
    //            }
    //        }
    //        else
    //        {
    //            result=false;
    //        }
    //        data_count=data_count-request_items;
    //    }

    //all data is read
    // return result;
}

inline bool MAX30009_LIB::read_10pcs_FIFO_data(MAX30009_FIFO_DATA *FIFO_data_array)
{
    return  false;
    //    bool result=true;
    //
    //    uint8_t request_array[32];
    //    request_array[0]=(uint8_t)MAX30009_ADDRESS_FIFO_DATA_REGISTER;
    //    request_array[1]=MAX30009_REGISTER_READ_DIRECT;
    //    for (uint32_t i=2;i<32;i++)
    //    {
    //        request_array[i]=MAX30009_DUMMY_BYTE;
    //    }
    //
    //    uint8_t answer_array[32]={0,};
    //    if (SPI_data_transfer(request_array,answer_array,32)==true)
    //    {
    //        for (uint32_t i=0;i<10;i++)
    //        {
    //           FIFO_data_array[i]=encode_FIFO_data(&answer_array[2+(i*3)]);
    //        }
    //    }
    //    else
    //    {
    //        result=false;
    //    }
    //
    //    return result;
}

inline bool MAX30009_LIB::read_two_FIFO_item(MAX30009_FIFO_DATA *FIFO_data, MAX30009_FIFO_DATA *FIFO_data2)
{
    bool result=true;

    uint8_t request_array[8];
    request_array[0]=(uint8_t)MAX30009_ADDRESS_FIFO_DATA_REGISTER;
    request_array[1]=MAX30009_REGISTER_READ_DIRECT;
    request_array[2]=MAX30009_DUMMY_BYTE;
    request_array[3]=MAX30009_DUMMY_BYTE;
    request_array[4]=MAX30009_DUMMY_BYTE;
    request_array[5]=MAX30009_DUMMY_BYTE;
    request_array[6]=MAX30009_DUMMY_BYTE;
    request_array[7]=MAX30009_DUMMY_BYTE;

    uint8_t answer_array[8];
    if (SPI_data_transfer(request_array,answer_array,8)==true)
    {
        *FIFO_data=encode_FIFO_data(&answer_array[2]);
        *FIFO_data2=encode_FIFO_data(&answer_array[5]);
    }
    else
    {
        result=false;
    }

    return result;
}

inline bool MAX30009_LIB::get_FIFO_average_all_value(MAX30009_FIFO_DATA *FIFO_I_data, MAX30009_FIFO_DATA *FIFO_Q_data)
{
    uint8_t request_array[20];
    request_array[0]=(uint8_t)MAX30009_ADDRESS_FIFO_DATA_REGISTER;
    request_array[1]=MAX30009_REGISTER_READ_DIRECT;
    request_array[2]=MAX30009_DUMMY_BYTE;
    request_array[3]=MAX30009_DUMMY_BYTE;
    request_array[4]=MAX30009_DUMMY_BYTE;
    request_array[5]=MAX30009_DUMMY_BYTE;
    request_array[6]=MAX30009_DUMMY_BYTE;
    request_array[7]=MAX30009_DUMMY_BYTE;
    request_array[8]=MAX30009_DUMMY_BYTE;
    request_array[9]=MAX30009_DUMMY_BYTE;
    request_array[10]=MAX30009_DUMMY_BYTE;
    request_array[11]=MAX30009_DUMMY_BYTE;
    request_array[12]=MAX30009_DUMMY_BYTE;
    request_array[13]=MAX30009_DUMMY_BYTE;
    request_array[14]=MAX30009_DUMMY_BYTE;
    request_array[15]=MAX30009_DUMMY_BYTE;
    request_array[16]=MAX30009_DUMMY_BYTE;
    request_array[17]=MAX30009_DUMMY_BYTE;
    request_array[18]=MAX30009_DUMMY_BYTE;
    request_array[19]=MAX30009_DUMMY_BYTE;
    uint8_t answer_array[20];


    MAX30009_FIFO_DATA FIFO_data;
    int64_t I_sum=0;
    int64_t Q_sum=0;
    int32_t I_sum_items=0;
    int32_t Q_sum_items=0;
    int64_t I_avarage=0;
    int64_t Q_avarage=0;

    for (uint32_t p=0; p<40; p++)
    {
        SPI_data_transfer(request_array,answer_array,20);

        for (uint32_t i=0; i<6; i++)
        {
            FIFO_data=encode_FIFO_data(&answer_array[2+i*3]);

            if (FIFO_data.data_source==MAX30009_I_CHANNEL)
            {
                I_sum=I_sum+FIFO_data.channel_value;
                I_sum_items++;
            }
            else if (FIFO_data.data_source==MAX30009_Q_CHANNEL)
            {
                Q_sum=Q_sum+FIFO_data.channel_value;
                Q_sum_items++;
            }
        }
    }
    if (I_sum_items!=0)
    {
        I_avarage=I_sum/I_sum_items;
    }
    if (Q_sum_items!=0)
    {
        Q_avarage=Q_sum/Q_sum_items;
    }

    FIFO_I_data->channel_value=I_avarage;
    FIFO_I_data->data_source=MAX30009_I_CHANNEL;

    FIFO_Q_data->channel_value=Q_avarage;
    FIFO_Q_data->data_source=MAX30009_Q_CHANNEL;
    return true;
}

inline MAX30009_FIFO_DATA MAX30009_LIB::encode_FIFO_data(uint8_t *FIFO_answer_data)
{
    MAX30009_FIFO_DATA out_data= {0,0,0,MAX30009_ERROR_DATA_SOURCE};
    uint32_t FIFO_answer=FIFO_answer_data[0];
    FIFO_answer=(FIFO_answer<<8)+FIFO_answer_data[1];
    FIFO_answer=(FIFO_answer<<8)+FIFO_answer_data[2];

    if ((FIFO_answer & 0xF00000)==MAX30009_I_CHANNEL_ID)
    {
        out_data.data_source=MAX30009_I_CHANNEL;
    }
    else if ((FIFO_answer & 0xF00000)==MAX30009_Q_CHANNEL_ID)
    {
        out_data.data_source=MAX30009_Q_CHANNEL;
    }
    else if (FIFO_answer==MAX30009_MARKER_ID )
    {
        out_data.data_source=MAX30009_MARKER;
    }
    else
    {
        return out_data;
    }


    int32_t ADC_value=FIFO_answer & 0x0FFFFF;
    if ((ADC_value & 0x80000) >0) //check sign bit
    {
        uint32_t value_module=((~ADC_value) & 0x07FFFF)-1;
        ADC_value=-value_module;
    }

    out_data.channel_value=ADC_value;

    return out_data;
}

inline void MAX30009_LIB::calculate_impendance(MAX30009_FIFO_DATA *FIFO_data_item, MAX30009_CALIB_DATA_TYPE calib_data)
{

    int64_t item_value=FIFO_data_item->channel_value;

    if (FIFO_data_item->data_source==MAX30009_I_CHANNEL)
    {
        item_value=item_value-calib_data.I_offset;
    }
    else if (FIFO_data_item->data_source==MAX30009_Q_CHANNEL)
    {
        item_value=item_value-calib_data.Q_offset;
    }

    int64_t adcv=item_value*(int64_t)100000;
    int64_t divp=333772;
    divp=divp*(int64_t)_bioz_data.total_gain_value;
    divp=divp*(int64_t)_bioz_data.current_peak;
    divp=divp*(int64_t)1000;
    divp=divp/(int64_t)1000000000;

    FIFO_data_item->impendance_value=adcv/divp;

    adcv=item_value*(int64_t)1000000;
    divp=333772;
    divp=divp*(int64_t)_bioz_data.total_gain_value;
    FIFO_data_item->voltage_value=adcv/divp;
}

inline void MAX30009_LIB::Make_FIFO_mark()
{
    _write_reg.FIFO_CONFIGURATION_2.FIFO_MARK=1;
    write_register_without_check(MAX30009_ADDRESS_FIFO_CONFIGURATION_2);
}

inline void MAX30009_LIB::Flush_FIFO()
{
    _write_reg.FIFO_CONFIGURATION_2.FLUSH_FIFO=1;
    write_register_without_check(MAX30009_ADDRESS_FIFO_CONFIGURATION_2);
}

inline bool MAX30009_LIB::set_FIFO_STAT_CLR_type(MAX30009_FIFO_STAT_CLR_ENUM_TYPE stat_clr_type)
{
    _write_reg.FIFO_CONFIGURATION_2.FIFO_STAT_CLR=(uint8_t)stat_clr_type;

    bool write_reg_result=write_register(MAX30009_ADDRESS_FIFO_CONFIGURATION_2);

    return write_reg_result;
}

inline bool MAX30009_LIB::set_A_FULL_type(MAX30009_FIFO_A_FULL_TYPE_ENUM_TYPE a_full_type)
{
    _write_reg.FIFO_CONFIGURATION_2.A_FULL_TYPE=(uint8_t)a_full_type;

    bool write_reg_result=write_register(MAX30009_ADDRESS_FIFO_CONFIGURATION_2);

    return write_reg_result;
}

inline bool MAX30009_LIB::set_FIFO_RO_type(MAX30009_FIFO_RO_ENUM_TYPE fifo_ro_type)
{
    _write_reg.FIFO_CONFIGURATION_2.FIFO_RO=(uint8_t)fifo_ro_type;

    bool write_reg_result=write_register(MAX30009_ADDRESS_FIFO_CONFIGURATION_2);

    return write_reg_result;
}

inline bool MAX30009_LIB::set_FIFO_A_FULL_size(uint8_t a_full_size)
{
    _write_reg.FIFO_CONFIGURATION_1.FIFO_A_FULL=(uint8_t)256-a_full_size;

    bool write_reg_result=write_register(MAX30009_ADDRESS_FIFO_CONFIGURATION_1);

    return write_reg_result;
}

inline bool MAX30009_LIB::get_FIFO_data_count(uint16_t *data_count)
{
    bool read_reg_result=true;
    if (read_register(MAX30009_ADDRESS_FIFO_COUNTER_1)==false)
    {
        read_reg_result=false;
    }
    if (read_register(MAX30009_ADDRESS_FIFO_COUNTER_2)==false)
    {
        read_reg_result=false;
    }

    if (read_reg_result==true)
    {
        //read successful
        uint16_t data_cnt=_read_reg.FIFO_COUNTER_1.FIFO_DATA_COUNT_HB & 0xFF;
        data_cnt=(data_cnt<<8)+_read_reg.FIFO_COUNTER_2.FIFO_DATA_COUNT_LB;
        *data_count=data_cnt;
    }
    return read_reg_result;
}

inline bool MAX30009_LIB::get_FIFO_overflow_data_count(uint8_t *overflow_data_count)
{
    bool read_reg_result=read_register(MAX30009_ADDRESS_FIFO_COUNTER_1);

    if (read_reg_result==true)
    {
        //read successful
        *overflow_data_count=_read_reg.FIFO_COUNTER_1.OVF_COUNTER;
    }
    return read_reg_result;
}

inline bool MAX30009_LIB::get_FIFO_write_pointer(uint8_t *write_data_pointer)
{
    bool read_reg_result=read_register(MAX30009_ADDRESS_FIFO_WRITE_POINTER);

    if (read_reg_result==true)
    {
        //read successful
        *write_data_pointer=_read_reg.FIFO_WRITE_POINTER.FIFO_WR_PTR;
    }
    return read_reg_result;
}

inline bool MAX30009_LIB::get_FIFO_read_pointer(uint8_t *read_data_pointer)
{
    bool read_reg_result=read_register(MAX30009_ADDRESS_FIFO_READ_POINTER);

    if (read_reg_result==true)
    {
        //read successful
        *read_data_pointer=_read_reg.FIFO_READ_POINTER.FIFO_RD_PTR;
    }
    return read_reg_result;
}

inline bool MAX30009_LIB::set_LEAD_RBIAS_VALUE(MAX30009_LEAD_RBIAS_VALUE_ENUM_TYPE RBIAS_VALUE)
{
    _write_reg.LEAD_BIAS_CONFIGURATION.RBIAS_VALUE=(uint8_t)RBIAS_VALUE;

    bool write_reg_result=write_register(MAX30009_ADDRESS_LEAD_BIAS_CONFIGURATION);

    return write_reg_result;
}

inline bool MAX30009_LIB::set_LEAD_RBIAS_BIP_state(bool RBIAS_BIP_enable)
{
    _write_reg.LEAD_BIAS_CONFIGURATION.EN_RBIAS_BIP=(uint8_t)RBIAS_BIP_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_LEAD_BIAS_CONFIGURATION);

    return write_reg_result;
}

inline bool MAX30009_LIB::set_LEAD_RBIAS_BIN_state(bool RBIAS_BIN_enable)
{
    _write_reg.LEAD_BIAS_CONFIGURATION.EN_RBIAS_BIN=(uint8_t)RBIAS_BIN_enable;

    bool write_reg_result=write_register(MAX30009_ADDRESS_LEAD_BIAS_CONFIGURATION);

    return write_reg_result;
}

inline MAX30009_CALIB_STATE_ENUM_TYPE MAX30009_LIB::calibrate_main_proccess()
{
    MAX30009_FIFO_DATA FIFO_I_data;
    MAX30009_FIFO_DATA FIFO_Q_data;
    MAX30009_STATUS_STRUCT_TYPE status;
    if (_calib_data.delay_in_calib>0)
    {
        _calib_data.delay_in_calib--;
        Flush_FIFO(); //clear FIFO after delay
        read_status(&status);

        return MAX30009_CALIB_IN_DELAY;
    }

    if (_calib_data.need_full_FIFO_buffer==true)
    {

        //get_FIFO_data_count(&_calib_data.FIFO_data_count);
        read_status(&status);
        if (status.a_full_flag==false) //buffer is not full
        {
            return MAX30009_CALIB_WAIT_DATA;
        }
        else
        {
            _calib_data.need_full_FIFO_buffer=false;
        }
    }


    if (_calib_data.calib_state==MAX30009_CALIB_STATE_NEED_CALIB)
    {
        set_MUX_Resistor_Load_non_GSR(MAX30009_BMUX_RSEL_280_OHM);
        set_MUX_BIST_enable(true);
        set_MUX_state(true);
        _calib_data.calib_state=MAX30009_CALIB_STATE_PRE_START_CALIB;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_PRE_START_CALIB)
    {
        _calib_data.calib_state=MAX30009_CALIB_STATE_START_MEAS_OFFSET;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_START_MEAS_OFFSET)
    {
        set_reference_clock_source(MAX30009_REFCLK_SRC_INT_32768);
        set_MUX_state(false);

        set_MUX_BIST_enable(false);
        set_MUX_GSR_enable(false);

        set_LEAD_RBIAS_BIN_state(true);
        set_LEAD_RBIAS_BIP_state(true);
        set_LEAD_RBIAS_VALUE(MAX30009_LEAD_RBIAS_50M);

        set_ext_capacitor_state(false);
        set_ext_resistor_state(false,0);
        set_BIOZ_bandgap_state(true);
        set_BIOZ_fast_start_mode(MAX30009_FAST_START_MODE_ON_200ms);
        set_BIOZ_total_gain(_calib_data.calibrate_gain);
        set_BIOZ_amplifier_range(MAX30009_BIOZ_AMPLF_MODE_HIGH);
        set_BIOZ_amplifier_bandwidth(MAX30009_BIOZ_AMPLF_MODE_HIGH);
        set_BIOZ_DC_restore(true);
        set_input_HP_filter(MAX30009_BIOZ_IN_HPFILTER_BYPASS);
        set_out_DHP_filter(MAX30009_BIOZ_DHPF_BYPASS);
        set_out_DLP_filter(MAX30009_BIOZ_DLPF_BYPASS);
        set_drive_frequency(_calib_data.calibrate_frequency*10,3000);


        set_BIOZ_constant_current_mode(MAX30009_CURRENT_AMP_16nA); //set minimum current
        set_BIOZ_DRV_RESET(true);



        set_PLL_state(true);
        set_BIOZ_I_channel_state(true);
        set_BIOZ_Q_channel_state(true);

        set_BIOZ_I_CLK_PHASE(false);
        set_BIOZ_Q_CLK_PHASE(false);

        set_FIFO_A_FULL_size(250);



        _calib_data.delay_in_calib=MAX30009_CALIB_DELAY_PERIOD;
        _calib_data.need_full_FIFO_buffer=true;

        _calib_data.calib_state=MAX30009_CALIB_STATE_MEAS_OFFSET;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_MEAS_OFFSET)
    {
        get_FIFO_average_all_value(&FIFO_I_data, &FIFO_Q_data);
        _calib_data.I_offset=(double)FIFO_I_data.channel_value;
        _calib_data.Q_offset=(double)FIFO_Q_data.channel_value;

        _calib_data.calib_state=MAX30009_CALIB_STATE_START_MEAS_IN_PHASE;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_START_MEAS_IN_PHASE)
    {
        set_MUX_state(true);
        if (_calib_data.calib_source==MAX30009_CALIB_SOURCE_CALIBPORT)
        {
            set_MUX_CAL_state(true);
            set_MUX_CAL_ONLY_state(true);
        }
        else
        {
            set_MUX_CAL_state(false);
            set_MUX_CAL_ONLY_state(false);
            set_MUX_DRVP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_EL1);
            set_MUX_BIP_assign(MAX30009_MUX_BIP_DRVP_ASSIGN_EL2B);
            set_MUX_BIN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_EL3B);
            set_MUX_DRVN_assign(MAX30009_MUX_BIN_DRVN_ASSIGN_EL4);
        }



        set_BIOZ_DRV_RESET(false);
        set_BIOZ_constant_current_mode(_calib_data.calibrate_current);


        set_BIOZ_I_CLK_PHASE(false);
        set_BIOZ_Q_CLK_PHASE(true);


        _calib_data.delay_in_calib=MAX30009_CALIB_DELAY_PERIOD*3;
        _calib_data.need_full_FIFO_buffer=true;

        _calib_data.calib_state=MAX30009_CALIB_STATE_MEAS_IN_PHASE;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_MEAS_IN_PHASE)
    {
        get_FIFO_average_all_value(&FIFO_I_data, &FIFO_Q_data);

        _calib_data.I_cal_in_ADC=FIFO_I_data.channel_value;
        _calib_data.Q_cal_in_ADC=FIFO_Q_data.channel_value;

        calculate_impendance(&FIFO_I_data,_calib_data);
        calculate_impendance(&FIFO_Q_data,_calib_data);
        _calib_data.I_cal_in=(double)FIFO_I_data.impendance_value/100.0;
        _calib_data.Q_cal_in=(double)FIFO_Q_data.impendance_value/100.0;

        _calib_data.calib_state=MAX30009_CALIB_STATE_START_MEAS_QUAD;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_START_MEAS_QUAD)
    {

        set_BIOZ_I_CLK_PHASE(true);
        set_BIOZ_Q_CLK_PHASE(false);

        _calib_data.delay_in_calib=MAX30009_CALIB_DELAY_PERIOD;
        _calib_data.need_full_FIFO_buffer=true;

        _calib_data.calib_state=MAX30009_CALIB_STATE_MEAS_QUAD;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_MEAS_QUAD)
    {
        get_FIFO_average_all_value(&FIFO_I_data, &FIFO_Q_data);
        calculate_impendance(&FIFO_I_data,_calib_data);
        calculate_impendance(&FIFO_Q_data,_calib_data);
        _calib_data.I_cal_quad=(double)FIFO_I_data.impendance_value/100.0;
        _calib_data.Q_cal_quad=(double)FIFO_Q_data.impendance_value/100.0;

        _calib_data.calib_state=MAX30009_CALIB_STATE_CALCULATE_COEF;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_CALCULATE_COEF)
    {

        set_BIOZ_I_CLK_PHASE(false);
        set_BIOZ_Q_CLK_PHASE(false);
        set_PLL_state(false);
        set_MUX_state(false);
        set_BIOZ_I_channel_state(false);
        set_BIOZ_Q_channel_state(false);
        set_MUX_CAL_state(false);
        set_MUX_CAL_ONLY_state(false);
        Flush_FIFO();

        //		1. I_coef = √(I_cal_in^2 + I_cal_quad^2) / RCAL
        //		2. Q_coef = √(Q_cal_in^2 + Q_cal_quad^2) / RCAL
        //		3. I_phase_coef [°] = arctan(I_cal_quad / I_cal_in) x 180° / π
        //		4. Q_phase_coef [°] = arctan(-Q_cal_quad / -Q_cal_in) x 180° / π

        _calib_data.I_coef=sqrt((_calib_data.I_cal_in*_calib_data.I_cal_in)+(_calib_data.I_cal_quad*_calib_data.I_cal_quad))/_calib_data.ref_value;
        _calib_data.Q_coef=sqrt((_calib_data.Q_cal_in*_calib_data.Q_cal_in)+(_calib_data.Q_cal_quad*_calib_data.Q_cal_quad))/_calib_data.ref_value;

        _calib_data.I_phase_coef=atan2(_calib_data.I_cal_quad, _calib_data.I_cal_in)*180.0/M_PI;
        _calib_data.Q_phase_coef=atan2(-_calib_data.Q_cal_quad,-_calib_data.Q_cal_in)*180.0/M_PI;


        _calib_data.I_phase_cos=cos(_calib_data.I_phase_coef*M_PI/180.0);
        _calib_data.I_phase_sin=sin(_calib_data.I_phase_coef*M_PI/180.0);
        _calib_data.Q_phase_cos=cos(_calib_data.Q_phase_coef*M_PI/180.0);
        _calib_data.Q_phase_sin=sin(_calib_data.Q_phase_coef*M_PI/180.0);

        _calib_data.calib_state=MAX30009_CALIB_STATE_PRE_READY;
        return _calib_data.calib_state;
    }

    if (_calib_data.calib_state==MAX30009_CALIB_STATE_PRE_READY)
    {
        _calib_data.calib_state=MAX30009_CALIB_STATE_READY;
        return _calib_data.calib_state;
    }

    return _calib_data.calib_state;
}

inline void MAX30009_LIB::start_calibrate(MAX30009_CALIB_SOURCE_ENUM_TYPE calib_source, double ref_value, MAX30009_CURRENT_AMP_ENUM_TYPE calibrate_current, uint32_t calibrate_frequency, MAX30009_BIOZ_TOTAL_GAIN_ENUM_TYPE calibrate_gain)
{
    _calib_data.calib_state=MAX30009_CALIB_STATE_NEED_CALIB;
    _calib_data.ref_value=ref_value;
    _calib_data.calib_source=calib_source;
    _calib_data.calibrate_current=calibrate_current;
    _calib_data.calibrate_frequency=calibrate_frequency;
    _calib_data.calibrate_gain=calibrate_gain;
    _calib_data.need_full_FIFO_buffer=false;
}

inline MAX30009_FIFO_DATA_CALIB_TYPE MAX30009_LIB::calibrate_FIFO_data(MAX30009_FIFO_DATA I_data, MAX30009_FIFO_DATA Q_data, MAX30009_CALIB_DATA_TYPE calib_data)
{
    //		To apply the calibration coefficients to a measured impedance, follow these steps.
    //		1. Measure I and Q load impedances (I_load [Ω] and Q_load [Ω]).
    //		2. Subtract the offsets from the load impedances:
    //		3. Apply I and Q coefficients to correct magnitude and phase delay of each channel:
    //		1. I_cal_real [Ω] = (I_load_offset / I_coef) x cos(I_phase_coef x π / 180)
    //		2. I_cal_imag [Ω] = (I_load_offset / I_coef) x sin(I_phase_coef x π / 180)
    //		3. Q_cal_real [Ω] = (Q_load_offset / Q_coef) x sin(Q_phase_coef x π / 180)
    //		4. Q_cal_imag [Ω] = (Q_load_offset / Q_coef) x cos(Q_phase_coef x π / 180)
    //		4. Calculate the corrected load impedance:
    //		1. Load_real [Ω] = I_cal_real - Q_cal_real
    //		2. Load_imag [Ω] = I_cal_imag + Q_cal_imag
    //		3. Load_mag [Ω] = √(Load_real^2 + Load_imag^2)
    //		4. Load_angle [°] = arctan(Load_imag / Load_real) x 180 / π

    MAX30009_FIFO_DATA_CALIB_TYPE out_data= {0};
    out_data.I_load=(double)I_data.impendance_value/100.0;
    out_data.Q_load=(double)Q_data.impendance_value/100.0;

    out_data.overload=false;
    if (I_data.channel_value<MAX30009_MIN_ADC_VALUE)
    {
        out_data.overload=true;
    }
    if (I_data.channel_value>MAX30009_MAX_ADC_VALUE)
    {
        out_data.overload=true;
    }
    if (Q_data.channel_value<MAX30009_MIN_ADC_VALUE)
    {
        out_data.overload=true;
    }
    if (Q_data.channel_value>MAX30009_MAX_ADC_VALUE)
    {
        out_data.overload=true;
    }

    if (calib_data.I_coef==0 || calib_data.Q_coef==0)
    {
        return out_data;
    }

    out_data.I_cal_real=(out_data.I_load/calib_data.I_coef) * calib_data.I_phase_cos;
    out_data.I_cal_imag=(out_data.I_load/calib_data.I_coef) * calib_data.I_phase_sin;

    out_data.Q_cal_real=(out_data.Q_load/calib_data.Q_coef) * calib_data.Q_phase_cos;
    out_data.Q_cal_imag=(out_data.Q_load/calib_data.Q_coef) * calib_data.Q_phase_sin;

    out_data.Load_real=out_data.I_cal_real-out_data.Q_cal_real;
    out_data.Load_imag=out_data.I_cal_imag+out_data.Q_cal_imag;

    out_data.Load_mag=sqrt((out_data.Load_real*out_data.Load_real)+(out_data.Load_imag*out_data.Load_imag));
    out_data.Load_angle=atan2(out_data.Load_imag,out_data.Load_real)*180.0/M_PI;

    return out_data;
}

inline MAX30009_CALIB_STATE_ENUM_TYPE MAX30009_LIB::get_calibrate_state()
{
    return _calib_data.calib_state;
}

inline  MAX30009_CALIB_DATA_TYPE MAX30009_LIB::get_last_calib_data(void)
{
    return _calib_data;
}

inline void MAX30009_LIB::stop_calibrate()
{
    _calib_data.calib_state=MAX30009_CALIB_STATE_STOPED;
}

inline bool MAX30009_LIB::start_load_all_registers()
{
    if (_lib_is_init==false)
    {
        return false;
    }
    bool result=true;
    for (uint32_t i=0; i<=MAX30009_LAST_REGISTER_ADDRESS; i++)
    {
        if (_max30009_read_registers_pointer_array[i]!=&_X_DUMMY_VALUE)
        {
            if(read_register((MAX30009_REGISTER_ADDRESS_ENUM_TYPE)i)==false)
            {
                result=false;
            }
        }
    }
    return  result;
}

inline bool MAX30009_LIB::SPI_data_transfer(uint8_t *out_data, uint8_t *input_data, uint8_t data_size)
{

    if (_data_stream!=0)
    {
        return _data_stream->send_byte_array(out_data, input_data, data_size);
    }
    else
    {
        return false;
    }

}

inline bool MAX30009_LIB::read_register(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address)
{
    if (register_address>MAX30009_LAST_REGISTER_ADDRESS)
    {
        return false;
    }
    if (_lib_is_init==false)
    {
        return false;
    }

    uint8_t answer_reg_value;
    if (get_register(register_address,&answer_reg_value)==true)
    {
        *_max30009_write_registers_pointer_array[register_address]=answer_reg_value;
        *_max30009_read_registers_pointer_array[register_address]=answer_reg_value;
        return true;
    }
    return false;
}

inline bool MAX30009_LIB::get_register(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address, uint8_t *register_value)
{
    if (register_address>MAX30009_LAST_REGISTER_ADDRESS)
    {
        return false;
    }
    if (_lib_is_init==false)
    {
        return false;
    }

    uint8_t request_array[MAX30009_REGISTER_PACKET_SIZE];
    request_array[0]=(uint8_t)register_address;
    request_array[1]=MAX30009_REGISTER_READ_DIRECT;
    request_array[2]=MAX30009_DUMMY_BYTE;

    uint8_t answer_array[MAX30009_REGISTER_PACKET_SIZE];
    for (uint32_t i=0; i<MAX30009_TRY_READ_COUNT; i++)
    {
        if (SPI_data_transfer(request_array,answer_array,MAX30009_REGISTER_PACKET_SIZE)==true)
        {
            *register_value=answer_array[2];
            return true;
        }
    }
    return false;
}

inline bool MAX30009_LIB::write_register(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address_enum)
{
    uint8_t register_address=(uint8_t)register_address_enum;
    if (register_address>=MAX30009_LAST_REGISTER_ADDRESS)
    {
        return false;
    }
    if (_lib_is_init==false)
    {
        return false;
    }

    uint8_t request_array[MAX30009_REGISTER_PACKET_SIZE];
    request_array[0]=(uint8_t)register_address;
    request_array[1]=MAX30009_REGISTER_WRITE_DIRECT;
    request_array[2]=*_max30009_write_registers_pointer_array[register_address];

    uint8_t answer_array[MAX30009_REGISTER_PACKET_SIZE];

    for (uint32_t i=0; i<MAX30009_TRY_WRITE_COUNT; i++)
    {
        if (SPI_data_transfer(request_array,answer_array,MAX30009_REGISTER_PACKET_SIZE)==true) //write process
        {
            //check register data
            uint8_t answer_reg_value;
            if (get_register(register_address_enum,&answer_reg_value)==true)
            {
                *_max30009_read_registers_pointer_array[register_address]=answer_reg_value;

                if (answer_reg_value==*_max30009_write_registers_pointer_array[register_address])
                {
                    return true;
                }
            }
        }
    }
    return false;
}

inline void MAX30009_LIB::write_register_without_check(MAX30009_REGISTER_ADDRESS_ENUM_TYPE register_address_enum)
{
    uint8_t register_address=(uint8_t)register_address_enum;
    if (register_address>=MAX30009_LAST_REGISTER_ADDRESS)
    {
        return;
    }
    if (_lib_is_init==false)
    {
        return;
    }

    uint8_t request_array[MAX30009_REGISTER_PACKET_SIZE];
    request_array[0]=(uint8_t)register_address;
    request_array[1]=MAX30009_REGISTER_WRITE_DIRECT;
    request_array[2]=*_max30009_write_registers_pointer_array[register_address];

    uint8_t answer_array[MAX30009_REGISTER_PACKET_SIZE];

    SPI_data_transfer(request_array,answer_array,MAX30009_REGISTER_PACKET_SIZE);
}

#endif // MAX30009_LIB_H
