#ifndef ADS1293_PROCESS_H
#define ADS1293_PROCESS_H

#include <string>
#include <iostream>
#include <vector>
#include <cstdint>


typedef struct ADS1293_USER_SETTINGS
{

    bool enable_conversion;
    bool power_enable;
    int32_t R2_rate;
    int32_t R3_rate;

    // Lead-off detection configuration (Phase 1)
    bool enable_leadoff_detection;      // Master enable/disable
    bool leadoff_mode_dc;               // true=DC, false=AC
    uint32_t leadoff_current_nA;        // 8-2040 nA (multiples of 8)
    bool leadoff_enable_inputs[6];      // Per-input enable flags
    uint8_t leadoff_ac_comparator_level; // 0-3 for AC mode threshold
    uint8_t leadoff_ac_divider_ratio;    // 0-127 for AC frequency
    bool leadoff_ac_divider_k16;         // false=K1, true=K16

} ADS1293_USER_SETTINGS_TDE;

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
    std::string get_leadoff_status_as_json(void);

        void set_power_state(bool state);

            std::string get_timestamp_string();
protected:

private:

ADS1293_USER_SETTINGS_TDE ADS1293_user_sett={0};

static const int32_t SYNC_MARK_MAGIC_NUM=-99999;
    static const uint32_t IFIFO_BUFF_SIZE=3000;
    ADS1293_IFIFO_DATA_TDS _IFIFO_BUF[IFIFO_BUFF_SIZE]= {0};
    uint32_t _IFIFO_write_pos=0;
    uint32_t _IFIFO_read_pos=0;


    bool _old_power_state=false;

    // Lead-off detection status tracking
    bool _leadoff_status[6];           // Current lead-off status per input
    bool _leadoff_status_prev[6];      // Previous status for change detection
    uint32_t _leadoff_check_counter;   // Counter for periodic checking
    uint32_t _leadoff_debounce_counters[6]; // Debounce counters per input
    static constexpr uint32_t LEADOFF_CHECK_INTERVAL = 1000; // Check every 1000 cycles (~500ms)
    static constexpr uint32_t LEADOFF_DEBOUNCE_COUNT = 3;    // Require 3 consecutive reads

    // Helper functions
    void configure_leadoff_detection();
    void read_leadoff_status();

};

#endif // ADS1293_PROCESS_H
