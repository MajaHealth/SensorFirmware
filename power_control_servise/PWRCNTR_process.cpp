#include "PWRCNTR_process.h"
#include "json.hpp"


#include "GPIO_driver.h"

#include <chrono>
#include <thread>


VT_SMBUS_driver VT_SMBUS_obj;
SES_battery_info SES_battery(&VT_SMBUS_obj);



using json = nlohmann::json;


GPIO_driver_cls GPIO_POWER_KEY(24);
GPIO_driver_cls GPIO_CHARGER_SENSOR(22);
GPIO_driver_cls GPIO_CHARGE_DISABLE(14);
GPIO_driver_cls GPIO_BUZZER(20);

PWRCNTR_process::PWRCNTR_process()
{

}

void PWRCNTR_process::init(void)
{

    GPIO_POWER_KEY.set_GPIO_direct(VT_GPIO_INPUT,VT_GPIO_UNSET);
    GPIO_CHARGER_SENSOR.set_GPIO_direct(VT_GPIO_INPUT,VT_GPIO_UNSET);

    GPIO_CHARGE_DISABLE.set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
    GPIO_BUZZER.set_GPIO_direct(VT_GPIO_OUTPUT,VT_GPIO_UNSET);
}

void PWRCNTR_process::process(void)
{
    read_all_batt_info();
}

void PWRCNTR_process::read_all_batt_info(void)
{
    VT_SMBUS_obj.open(BATTERY_I2C_ADDRESS);
    delay(1);
    _BATT.voltage = SES_battery.get_voltage();
    delay(1);
    _BATT.temperature = SES_battery.get_temperature();
    delay(1);
    _BATT.current = SES_battery.get_current();
    delay(1);
    _BATT.relative_state_of_charge = SES_battery.get_relative_state_of_charge();
    delay(1);
    _BATT.remaining_capacity = SES_battery.get_remaining_capacity();
    delay(1);
    _BATT.full_charge_capacity = SES_battery.get_full_charge_capacity();
    delay(1);
    _BATT.run_time_to_empty = SES_battery.get_run_time_to_empty();
    delay(1);
    _BATT.average_time_to_empty = SES_battery.get_average_time_to_empty();
    delay(1);
    _BATT.average_time_to_full = SES_battery.get_average_time_to_full();
    delay(1);
    _BATT.cycle_count = SES_battery.get_cycle_count();
    delay(1);
    _BATT.design_capacity = SES_battery.get_design_capacity();
    delay(1);
    _BATT.design_voltage = SES_battery.get_design_voltage();
    delay(1);
    _BATT.status=SES_battery.get_battery_status();
    delay(1);
    VT_SMBUS_obj.close();
}


std::string PWRCNTR_process::process_JSON_line(const char * JSON_line)
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

            if (command_type == "get_batt_info")
            {
                response["type"] = "batt_info";
                response["voltage"] = _BATT.voltage;
                response["temperature"] = _BATT.temperature;
                response["current"] = _BATT.current;
                response["relative_state_of_charge"] = _BATT.relative_state_of_charge;
                response["remaining_capacity"] = _BATT.remaining_capacity;
                response["full_charge_capacity"] = _BATT.full_charge_capacity;
                response["run_time_to_empty"] = _BATT.run_time_to_empty;
                response["average_time_to_empty"] = _BATT.average_time_to_empty;
                response["average_time_to_full"] = _BATT.average_time_to_full;
                response["cycle_count"] = _BATT.cycle_count;
                response["design_capacity"] = _BATT.design_capacity;
                response["design_voltage"] = _BATT.design_voltage;

                bool fully_discharged=_BATT.status.fully_discharged;
                bool fully_charged=_BATT.status.fully_charged;
                bool discharging=_BATT.status.discharging;

                response["fully_discharged"] = fully_discharged;
                response["fully_charged"] = fully_charged;
                response["discharging"] = discharging;
                response["charging"] = !discharging;

                _BATT.charger_is_connect=(bool)GPIO_POWER_KEY.get_GPIO_state();
                response["charger_is_connect"] =  _BATT.charger_is_connect;

                response["battery_charge_is_disable"] = _BATT.battery_charge_is_disable;

                std::string response_string = response.dump();
                return response_string;
            }

            if (command_type == "charge_disable")
            {
                response["type"] = "charge_is_disable";
                _BATT.battery_charge_is_disable=true;
                GPIO_CHARGE_DISABLE.set_GPIO_state(VT_GPIO_SET);
                std::string response_string = response.dump();
                return response_string;
            }
            if (command_type == "charge_enable")
            {
                response["type"] = "charge_is_enable";
                _BATT.battery_charge_is_disable=false;
                GPIO_CHARGE_DISABLE.set_GPIO_state(VT_GPIO_UNSET);
                std::string response_string = response.dump();
                return response_string;
            }
            if (command_type == "buzzer")
            {

                if (parsed_json.contains("duration"))
                {
                    _buzzer_timer= parsed_json["duration"];
                }
                if (_buzzer_timer<0 || _buzzer_timer>100)
                {
                    _buzzer_timer=0;
                }
                process_buzzer();
                return "";
            }
        }
    }
    catch (const std::exception& e)
    {

    }

    response["type"] = "error JSON";
    std::string response_string = response.dump();
    return response_string;

}


std::string PWRCNTR_process::process_button(void)
{
    static  VT_GPIO_STATE_TDE  old_but_state=VT_GPIO_SET;
    VT_GPIO_STATE_TDE  but_state=GPIO_POWER_KEY.get_GPIO_state();

    bool but_bool_state=false;
    static uint32_t hold_time=0;
    if (but_state==VT_GPIO_UNSET)
    {
        but_bool_state=true;
        hold_time++;
        if(hold_time%10!=1)
        {
            return "";
        }
    }
    else
    {
        hold_time=0;
        if (old_but_state!=VT_GPIO_UNSET)
        {
            return "";
        }
    }

    old_but_state=but_state;

    json response;
    response["type"] = "button_info";
    response["state"] = but_bool_state;
    response["hold_time"] = hold_time/10;
    std::string response_string = response.dump();
    return response_string;

}

void PWRCNTR_process::process_buzzer(void)
{
    if (_buzzer_timer<0)
    {
        return;
    }

    _buzzer_timer--;

    if (_buzzer_timer<0)
    {
        GPIO_BUZZER.set_GPIO_state(VT_GPIO_UNSET);
    }
    else
    {
        GPIO_BUZZER.set_GPIO_state(VT_GPIO_SET);
    }
}

