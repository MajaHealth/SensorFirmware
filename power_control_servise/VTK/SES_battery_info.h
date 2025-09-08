#ifndef INC_SES_BATTERY_INFO_H_
#define INC_SES_BATTERY_INFO_H_

#include "VT_SMBUS_interface.h"

enum  BATT_REG {
	TEMPERATURE             = 0x08,  // Temperature (in 0.1K)
	VOLTAGE                 = 0x09,  // Voltage (in mV)
	CURRENT                 = 0x0A,  // Current (in mA, signed value)
	RELATIVE_STATE_OF_CHARGE= 0x0D,  // Relative State of Charge (%)
	CYCLE_COUNT             = 0x17,  // Number of full charge/discharge cycles
	BATTERY_STATUS          = 0x16,  // Battery status (flags)
	FULL_CHARGE_CAPACITY    = 0x10,  // Full charge capacity (in mAh)
	REMAINING_CAPACITY      = 0x0F,  // Remaining capacity (in mAh)
	DESIGN_CAPACITY         = 0x18,  // Designed capacity (in mAh)
	DESIGN_VOLTAGE          = 0x19,  // Designed voltage (in mV)
	MANUFACTURER_NAME       = 0x20,  // Manufacturer name (block data)
	DEVICE_NAME             = 0x21,  // Device name (block data)
	RUN_TIME_TO_EMPTY       = 0x11,  // Estimated run time to empty (in minutes)
	AVERAGE_TIME_TO_EMPTY   = 0x12,  // Average run time to empty (in minutes)
	AVERAGE_TIME_TO_FULL   = 0x13,  // Average run time to full (in minutes)
	AVERAGE_CURRENT         = 0x0B,  // Average current (in mA, signed value)
};

typedef struct __attribute__((packed)) {
    uint16_t error_code : 4;         // Bits 0-3: Reserved for error codes
    uint16_t fully_discharged : 1;   // Bit 4: Fully discharged
    uint16_t fully_charged : 1;      // Bit 5: Fully charged
    uint16_t discharging : 1;        // Bit 6: Discharging
    uint16_t initialized : 1;        // Bit 7: Initialized
    uint16_t remaining_time_alarm : 1; // Bit 8: Remaining time alarm
    uint16_t remaining_capacity_alarm : 1; // Bit 9: Remaining capacity alarm
    uint16_t reserved1 : 1;          // Bit 10: Reserved
    uint16_t terminate_discharge_alarm : 1; // Bit 11: Terminate discharge alarm
    uint16_t over_temp_alarm : 1;    // Bit 12: Over temp alarm
    uint16_t reserved2 : 1;          // Bit 13: Reserved
    uint16_t terminate_charge_alarm : 1; // Bit 14: Terminate charge alarm
    uint16_t over_charged_alarm : 1; // Bit 15: Over charged alarm
} SES_BATT_STATUS_TDS;

class SES_battery_info {
public:
	SES_battery_info(VT_SMBUS_interface * SMBUS_interface)
	{
		_SMBUS_interface=SMBUS_interface;
	}

	bool check_connect()
	{
		bool result=false;
		_SMBUS_interface->read_2byte_data(VOLTAGE,&result);
		return result;
	}

	float get_voltage()
	{
		if (_SMBUS_interface==nullptr) {return 0.0f;}
		bool result=false;
		uint16_t voltage=_SMBUS_interface->read_2byte_data(VOLTAGE,&result);
		if (result==false)  {return 0.0f;}

		float volt_float=voltage;
		volt_float=volt_float/1000.0f;
		return volt_float;
	}

	float get_temperature()
	{
		if (_SMBUS_interface == nullptr) {return 0.0f;}
		bool result = false;
		uint16_t temperature = _SMBUS_interface->read_2byte_data(TEMPERATURE, &result);
		if (result == false) {return 0.0f;}

		// Convert from 0.1K to Celsius
		float temp_celsius = static_cast<float>(temperature) / 10.0f - 273.15f;
		return temp_celsius;
	}

	float get_current()
	{
		if (_SMBUS_interface == nullptr) {return 0.0f;}
		bool result = false;
		uint16_t current_raw = _SMBUS_interface->read_2byte_data(CURRENT, &result);
		if (result == false) {return 0.0f;}
		int16_t current = static_cast<int16_t>(current_raw);

		float current_float=current;
		current_float=current_float/1000.0f;
		return current_float;
	}


	uint16_t get_relative_state_of_charge()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t soc = _SMBUS_interface->read_2byte_data(RELATIVE_STATE_OF_CHARGE, &result);
		if (result == false) {return 0;}
		return soc;
	}

	float get_remaining_capacity()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t capacity = _SMBUS_interface->read_2byte_data(REMAINING_CAPACITY, &result);
		if (result == false) {return 0;}

		float capacity_float=capacity;
		capacity_float=capacity_float/1000.0f;
		return capacity_float;
	}

	float get_full_charge_capacity()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t capacity = _SMBUS_interface->read_2byte_data(FULL_CHARGE_CAPACITY , &result);
		if (result == false) {return 0;}

		float capacity_float=capacity;
		capacity_float=capacity_float/1000.0f;
		return capacity_float;
	}


	uint16_t get_run_time_to_empty()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t time = _SMBUS_interface->read_2byte_data(RUN_TIME_TO_EMPTY, &result);
		if (result == false) {return 0;}
		return time;
	}

	uint16_t get_average_time_to_empty()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t time = _SMBUS_interface->read_2byte_data(AVERAGE_TIME_TO_EMPTY, &result);
		if (result == false) {return 0;}
		return time;
	}

	uint16_t get_average_time_to_full()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t time = _SMBUS_interface->read_2byte_data(AVERAGE_TIME_TO_FULL, &result);
		if (result == false) {return 0;}
		return time;
	}

	uint16_t get_cycle_count()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t count = _SMBUS_interface->read_2byte_data(CYCLE_COUNT, &result);
		if (result == false) {return 0;}
		return count;
	}

	SES_BATT_STATUS_TDS get_battery_status()
	{
		SES_BATT_STATUS_TDS status={0,0,0,0,0,0,0};
		if (_SMBUS_interface == nullptr) {return status;}
		bool result = false;
		uint16_t status_raw = _SMBUS_interface->read_2byte_data(BATTERY_STATUS, &result);
		if (result == false)  {return status;}
		uint16_t *status_ptr=(uint16_t*) &status;
		*status_ptr=status_raw;
		return status;
	}


	float get_design_capacity()
	{
		if (_SMBUS_interface == nullptr) {return 0;}
		bool result = false;
		uint16_t capacity = _SMBUS_interface->read_2byte_data(DESIGN_CAPACITY , &result);
		if (result == false) {return 0;}

		float capacity_float=capacity;
		capacity_float=capacity_float/1000.0f;
		return capacity_float;
	}

	float get_design_voltage()
	{
		if (_SMBUS_interface==nullptr) {return 0.0f;}
		bool result=false;
		uint16_t voltage=_SMBUS_interface->read_2byte_data(DESIGN_VOLTAGE,&result);
		if (result==false)  {return 0.0f;}

		float volt_float=voltage;
		volt_float=volt_float/1000.0f;
		return volt_float;
	}

private:
	VT_SMBUS_interface * _SMBUS_interface=nullptr;
};

#endif /* INC_SES_BATTERY_INFO_H_ */
