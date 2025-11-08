#include <iostream>
#include "MAX30009_LIB/max30009_lib.h"
#include "GPIO_driver.h"
#include "SPI_hard_driver.h"
#include <chrono>
#include <thread>
#include "max30009_ext_mux.h"

#include "MAX30009_process.h"
#include "ADS1293_process.h"
#include "WS2812_process.h"

MAX30009_process MAX30009_process_obj;
ADS1293_process ADS1293_process_obj;
WS2812_process WS2812_process_obj;

#include <iostream>
#include <vector>
#include <unistd.h>

#include "JSON_TCP_sever.h"

#include <atomic>




std::string ADS1293_request_json;
std::atomic<bool> ADS1293_request_ready_flag(false);
std::string ADS1293_response_json;
std::atomic<bool> ADS1293_response_ready_flag(false);
const int ADS1293_port=1293;
JSON_TCP_sever ADS1293_TCP_server(ADS1293_port,&ADS1293_request_json,&ADS1293_request_ready_flag,&ADS1293_response_json,&ADS1293_response_ready_flag);

std::string MAX30009_request_json;
std::atomic<bool> MAX30009_request_ready_flag(false);
std::string MAX30009_response_json;
std::atomic<bool> MAX30009_response_ready_flag(false);
const int MAX30009_port=30009;
JSON_TCP_sever MAX30009_TCP_server(MAX30009_port,&MAX30009_request_json,&MAX30009_request_ready_flag,&MAX30009_response_json,&MAX30009_response_ready_flag);

std::string WS2812_request_json;
std::atomic<bool> WS2812_request_ready_flag(false);
std::string WS2812_response_json;
std::atomic<bool> WS2812_response_ready_flag(false);
const int WS2812_port=2812;
JSON_TCP_sever WS2812_TCP_server(WS2812_port,&WS2812_request_json,&WS2812_request_ready_flag,&WS2812_response_json,&WS2812_response_ready_flag);


void delay(int ms)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

int main()
{
    MAX30009_process_obj.init();
    ADS1293_process_obj.init();
    ADS1293_TCP_server.Start();
    MAX30009_TCP_server.Start();
    WS2812_TCP_server.Start();



    auto last_call_time = std::chrono::steady_clock::now();
    int32_t sync_num=0;
    while(1)
    {

        if (ADS1293_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=ADS1293_process_obj.process_JSON_line(ADS1293_request_json.c_str());
            ADS1293_request_ready_flag.store(false, std::memory_order_release);
            if (ADS1293_response_ready_flag.load(std::memory_order_release)==false)
            {
                ADS1293_response_json=response_json;
                ADS1293_response_ready_flag.store(true, std::memory_order_release);
            }
        }

        if (MAX30009_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=MAX30009_process_obj.process_JSON_line(MAX30009_request_json.c_str());
            MAX30009_request_ready_flag.store(false, std::memory_order_release);
            if (MAX30009_response_ready_flag.load(std::memory_order_release)==false)
            {
                MAX30009_response_json=response_json;
                MAX30009_response_ready_flag.store(true, std::memory_order_release);
            }
        }

        if (WS2812_request_ready_flag.load(std::memory_order_acquire)==true)
        {
            std::string response_json;
            response_json=WS2812_process_obj.process_JSON_line(WS2812_request_json.c_str());
            WS2812_request_ready_flag.store(false, std::memory_order_release);
            if (WS2812_response_ready_flag.load(std::memory_order_release)==false)
            {
                WS2812_response_json=response_json;
                WS2812_response_ready_flag.store(true, std::memory_order_release);
            }
        }

        auto current_time = std::chrono::steady_clock::now();
        auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - last_call_time);

        if (elapsed_time.count() >= 1000)
        {
            sync_num++;
            MAX30009_process_obj.add_sync_mark(sync_num);
            ADS1293_process_obj.add_sync_mark(sync_num);
            last_call_time = current_time;
        }


        MAX30009_process_obj.process();
        ADS1293_process_obj.process();
        WS2812_process_obj.process();

        std::string response_json=MAX30009_process_obj.calibration_process();
        if (response_json.size()>2)
        {
            if (MAX30009_response_ready_flag.load(std::memory_order_release)==false)
            {
                MAX30009_response_json=response_json;
                MAX30009_response_ready_flag.store(true, std::memory_order_release);
            }


        }

//delay(1);
        usleep(500);

    }


    return 0;
}
