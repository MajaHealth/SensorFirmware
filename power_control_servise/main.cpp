#include <iostream>
#include "GPIO_driver.h"
#include "SPI_hard_driver.h"
#include <chrono>
#include <thread>

#include "PWRCNTR_process.h"


PWRCNTR_process PWRCNTR_process_obj;


#include <iostream>
#include <vector>
#include <unistd.h>

#include "JSON_TCP_sever.h"

#include <atomic>


std::string PWRCNTR_request_json;
std::atomic<bool> PWRCNTR_request_ready_flag(false);
std::string PWRCNTR_response_json;
std::atomic<bool> PWRCNTR_response_ready_flag(false);
const int PWRCNTR_port=501;
JSON_TCP_sever PWRCNTR_TCP_server(PWRCNTR_port,&PWRCNTR_request_json,&PWRCNTR_request_ready_flag,&PWRCNTR_response_json,&PWRCNTR_response_ready_flag);

void delay(int ms)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

int main()
{

    PWRCNTR_TCP_server.Start();
    PWRCNTR_process_obj.init();

    while(1)
    {

        if (PWRCNTR_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=PWRCNTR_process_obj.process_JSON_line(PWRCNTR_request_json.c_str());
            PWRCNTR_request_ready_flag.store(false, std::memory_order_release);
            if (PWRCNTR_response_ready_flag.load(std::memory_order_release)==false)
            {
                PWRCNTR_response_json=response_json;
                PWRCNTR_response_ready_flag.store(true, std::memory_order_release);
            }
        }


        std::string response_json=PWRCNTR_process_obj.process_button();
        if (response_json.size()>2)
        {
            if (PWRCNTR_response_ready_flag.load(std::memory_order_release)==false)
            {
                PWRCNTR_response_json=response_json;
                PWRCNTR_response_ready_flag.store(true, std::memory_order_release);
            }


        }


        static uint32_t battery_read_delay_tmr=0;
        battery_read_delay_tmr++;
        if (battery_read_delay_tmr>30)
        {
            battery_read_delay_tmr=0;
            PWRCNTR_process_obj.process();
        }

        PWRCNTR_process_obj.process_buzzer();

        delay(100);


    }


    return 0;
}
