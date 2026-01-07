#ifndef MAX30009_DATA_STORAGE_H
#define MAX30009_DATA_STORAGE_H
#include "max30009_data_struct.h"
#include "json.hpp"
#include "MAX30009_STATIC.h"
#include "max30009_lib.h"
using json = nlohmann::json;


typedef struct MAX30009_IFIFO_DATA
{
    int32_t I_data;
    int32_t Q_data;
    bool DRV_overload;
} MAX30009_IFIFO_DATA_TDS;

class MAX30009_data_storage
{
public:

    void reinit_buffer(int32_t adc_sample_rate_1_10hz, int32_t measure_freq_hz)
    {
        _adc_sample_rate=adc_sample_rate_1_10hz;
        _measure_freq=measure_freq_hz*10;
        _max_IFIFO_size =_adc_sample_rate*IFIFO_BUFFER_DURATION;
        if (_max_IFIFO_size>IFIFO_BUFF_SIZE) _max_IFIFO_size=IFIFO_BUFF_SIZE;
        _IFIFO_write_pos=0;
        _IFIFO_read_pos=0;
    }

    void add_new_data_item(const MAX30009_FIFO_DATA  & I_ch, const MAX30009_FIFO_DATA & Q_ch, bool DRV_overload)
    {
        _IFIFO_write_pos=(_IFIFO_write_pos+1)%_max_IFIFO_size ;
        if (_IFIFO_write_pos==_IFIFO_read_pos)
        {
            _IFIFO_read_pos=(_IFIFO_read_pos+1)%_max_IFIFO_size ;
        }

        _IFIFO_BUF[_IFIFO_write_pos].I_data=I_ch.channel_value;
        _IFIFO_BUF[_IFIFO_write_pos].Q_data=Q_ch.channel_value;
        _IFIFO_BUF[_IFIFO_write_pos].DRV_overload=DRV_overload;

        _last_data_receive=_IFIFO_BUF[_IFIFO_write_pos];
    }

    std::string get_data_as_json(MAX30009_CALIB_DATA & calib_data,const MAX30009_BIOZ_DATA_TYPE & bioz_data)
    {
        std::vector<MAX30009_FIFO_DATA_CALIB_TYPE> decimated_data = get_decimate_IFIFO_data(calib_data,bioz_data);

        nlohmann::json response_json;
        response_json["type"] = "data";
        response_json["data_frequency"] = _measure_freq/10; // in Hz
        response_json["data_size"] = decimated_data.size();
        response_json["timestamp"] =MAX30009_STATIC::get_timestamp_string();

        nlohmann::json data_array = nlohmann::json::array();

        for (uint32_t i = 0; i < decimated_data.size(); ++i)
        {
            MAX30009_FIFO_DATA_CALIB_TYPE& item = decimated_data[i];

            nlohmann::json point_array = nlohmann::json::array();

            int32_t load_real=item.Load_real*10000.0;
            int32_t load_mag=item.Load_mag*10000.0;
            int32_t load_imag=item.Load_imag*10000.0;
            int32_t load_angle=item.Load_angle*10000.0;

            point_array.push_back(load_real);
            point_array.push_back(load_mag);
            point_array.push_back(load_imag);
            point_array.push_back(load_angle);
            point_array.push_back((int32_t)item.overload);

            data_array.push_back(point_array);
        }

        response_json["data"] = data_array;
        return response_json.dump();
    }

    void add_sync_mark(int32_t sync_num)
    {
        _IFIFO_write_pos=(_IFIFO_write_pos+1)%_max_IFIFO_size ;
        if (_IFIFO_write_pos==_IFIFO_read_pos)
        {
            _IFIFO_read_pos=(_IFIFO_read_pos+1)%_max_IFIFO_size ;
        }

        _IFIFO_BUF[_IFIFO_write_pos].I_data=SYNC_MARK_MAGIC_NUM;
        _IFIFO_BUF[_IFIFO_write_pos].Q_data=sync_num;
    }

    MAX30009_IFIFO_DATA_TDS  get_last_data_receive()
    {
        return _last_data_receive;
    }



private:



    std::vector<MAX30009_FIFO_DATA_CALIB_TYPE>  get_decimate_IFIFO_data(MAX30009_CALIB_DATA & calib_data,const MAX30009_BIOZ_DATA_TYPE & bioz_data)
    {

        std::vector<MAX30009_FIFO_DATA_CALIB_TYPE> decimated_data;

        if (_IFIFO_read_pos==_IFIFO_write_pos) return decimated_data;
        if (_measure_freq==0) return decimated_data;

        float decimation_ratio = (float)_adc_sample_rate / (float)_measure_freq ;

        if (decimation_ratio<1) return decimated_data;


        uint32_t decimated_data_position=0;
        int64_t sum_I = 0;
        int64_t sum_Q = 0;
        int32_t sum_count = 0;
        int32_t sync_number=0;

        for (uint32_t i=0; i<_max_IFIFO_size ; i++)
        {
            _IFIFO_read_pos=(_IFIFO_read_pos+1)%_max_IFIFO_size ;

            if ((float)i/decimation_ratio>decimated_data_position+1)
            {
                //need start new data decimate
                decimated_data_position++;

                MAX30009_FIFO_DATA I_ch_data;
                MAX30009_FIFO_DATA Q_ch_data;

                I_ch_data.data_source=MAX30009_I_CHANNEL;
                Q_ch_data.data_source=MAX30009_Q_CHANNEL;

                if (sum_count > 0)
                {
                    I_ch_data.channel_value=sum_I/sum_count;
                    Q_ch_data.channel_value=sum_Q/sum_count;
                }
                else
                {
                    I_ch_data.channel_value = 0;
                    Q_ch_data.channel_value = 0;
                }

                MAX30009_LIB::calculate_impendance(&I_ch_data,calib_data,bioz_data);
                MAX30009_LIB::calculate_impendance(&Q_ch_data,calib_data,bioz_data);

                MAX30009_FIFO_DATA_CALIB_TYPE calibrate_data=MAX30009_LIB::calibrate_FIFO_data(I_ch_data, Q_ch_data,calib_data);
                decimated_data.push_back(calibrate_data);

                if (sync_number>0)
                {

                    MAX30009_FIFO_DATA_CALIB_TYPE sync_data= {0,0,0,0,0,0,0,0,0,0,false};
                    sync_data.Load_real=SYNC_MARK_MAGIC_NUM;
                    sync_data.Load_mag=sync_number;
                    decimated_data.push_back(sync_data);
                    sync_number=0;
                }

                sum_I = 0;
                sum_Q = 0;
                sum_count = 0;

                int32_t buffer_size = (_IFIFO_write_pos-_IFIFO_read_pos + _max_IFIFO_size) % _max_IFIFO_size;
                if (buffer_size<decimation_ratio+1)
                {
                    break;
                }
            }

            if (_IFIFO_BUF[_IFIFO_read_pos].I_data==SYNC_MARK_MAGIC_NUM)
            {
                sync_number=_IFIFO_BUF[_IFIFO_read_pos].Q_data;
            }
            else
            {
                sum_I=sum_I+_IFIFO_BUF[_IFIFO_read_pos].I_data;
                sum_Q=sum_Q+_IFIFO_BUF[_IFIFO_read_pos].Q_data;
                sum_count++;
            }

        }

        return decimated_data;
    }

    static const int32_t SYNC_MARK_MAGIC_NUM=-99999;
    static const uint32_t IFIFO_BUFFER_DURATION=3;
    static const uint32_t IFIFO_BUFF_SIZE=30000;
    uint32_t _max_IFIFO_size = 1;
    MAX30009_IFIFO_DATA_TDS _IFIFO_BUF[IFIFO_BUFF_SIZE]= {0};
    uint32_t _IFIFO_write_pos=0;
    uint32_t _IFIFO_read_pos=0;
    MAX30009_IFIFO_DATA_TDS  _last_data_receive;

    int32_t _adc_sample_rate=1;
    int32_t _measure_freq=1;
};

#endif // MAX30009_DATA_STORAGE_H
