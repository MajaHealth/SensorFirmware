#ifndef ADS1293_PROCESS_H
#define ADS1293_PROCESS_H

#include <string>
#include <iostream>
#include <vector>


typedef struct ADS1293_USER_SETTINGS
{
    bool enable_conversion;
    bool power_enable;
    int32_t R2_rate;
    int32_t R3_rate;

    // Lead-off detection settings
    bool leadoff_enable;           // Enable lead-off detection
    uint32_t leadoff_mode;         // 0=DC, 1=AC (recommended)
    uint32_t leadoff_current_nA;   // Detection current (default 1400 nA)
    uint32_t leadoff_threshold;    // Comparator trigger level 0-3

} ADS1293_USER_SETTINGS_TDE;

typedef struct ADS1293_LEADOFF_STATUS
{
    bool lead_off_detected;  // Overall lead-off flag from ERROR_STATUS
    bool in1_off;            // IN1 (RA) lead-off status
    bool in2_off;            // IN2 (LA) lead-off status
    bool in3_off;            // IN3 (LL) lead-off status
    bool in4_off;            // IN4 (RL/RLD) lead-off status
    bool in5_off;            // IN5 lead-off status
    bool in6_off;            // IN6 lead-off status
} ADS1293_LEADOFF_STATUS_TDS;

typedef struct ADS1293_IFIFO_DATA
{
    int32_t ch1;
    int32_t ch2;
    int32_t ch3;
} ADS1293_IFIFO_DATA_TDS;

class ADS1293_process
{
public:
    ADS1293_process();
    void process(void);
    void init(void);
    void add_sync_mark(int32_t sync_num);

    std::string process_JSON_line(const char * JSON_line);

    std::string get_all_settings_as_json(void);
    void process_all_settings_for_ADS1293(void);
    std::string get_data_as_json(void);

    void set_power_state(bool state);

    std::string get_timestamp_string();

    // Lead-off detection methods
    void configure_leadoff_detection(void);
    void read_leadoff_status(void);
    std::string get_leadoff_status_as_json(void);
    std::string check_and_get_periodic_leadoff_status(void);
protected:

private:

ADS1293_USER_SETTINGS_TDE ADS1293_user_sett={0};

static const int32_t SYNC_MARK_MAGIC_NUM=-99999;
    static const uint32_t IFIFO_BUFF_SIZE=3000;
    ADS1293_IFIFO_DATA_TDS _IFIFO_BUF[IFIFO_BUFF_SIZE]= {0};
    uint32_t _IFIFO_write_pos=0;
    uint32_t _IFIFO_read_pos=0;

    bool _old_power_state=false;

    // Lead-off detection members
    ADS1293_LEADOFF_STATUS_TDS _leadoff_status = {0};
    uint32_t _leadoff_push_counter = 0;
    static const uint32_t LEADOFF_PUSH_INTERVAL = 10000;  // ~5 seconds at 500μs loop

};

#endif // ADS1293_PROCESS_H
