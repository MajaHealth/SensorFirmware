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

};

#endif // ADS1293_PROCESS_H
