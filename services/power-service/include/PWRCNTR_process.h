#ifndef PWRCNTR_PROCESS_H
#define PWRCNTR_PROCESS_H

#include <string>
#include <iostream>
#include <vector>

#include "VT_SMBUS_driver.h"
#include "SES_battery_info.h"

#include <chrono>
#include <thread>




typedef struct BATTINFO
{
    float voltage;
    float temperature;
    float current;
    int relative_state_of_charge;
    float remaining_capacity;
    float full_charge_capacity;
    uint16_t run_time_to_empty;
    uint16_t average_time_to_empty;
    uint16_t average_time_to_full;
    uint16_t cycle_count;
    float design_capacity;
    float design_voltage;

    bool charger_is_connect;
    bool battery_charge_is_disable;

    SES_BATT_STATUS_TDS status;

} BATTINFO_TDS;


#define BATTERY_I2C_ADDRESS     0x0B

class PWRCNTR_process
{
public:
    PWRCNTR_process();

    void init(void);


    void process(void);

void read_all_batt_info(void);

    std::string process_JSON_line(const char * JSON_line);

    std::string process_button(void);

    void process_buzzer(void);
protected:

private:


void delay(int ms)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

    BATTINFO_TDS _BATT;
    int32_t _buzzer_timer=-1;

};

#endif // PWRCNTR_PROCESS_H
