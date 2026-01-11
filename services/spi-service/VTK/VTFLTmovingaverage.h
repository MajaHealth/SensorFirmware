#ifndef SRC_VTFLTMOVINGAVERAGE_H_
#define SRC_VTFLTMOVINGAVERAGE_H_


template < uint16_t _WINDOW_SIZE >
class VTFLT_moving_average
{
public:
    VTFLT_moving_average(int32_t fill_value=0)
    {
        clear(fill_value);
    }

    int32_t filtered(int32_t value)
    {
        _buffer_sum=_buffer_sum-_window_buff[_buffer_pos]; //віднімаємо найстаріше значення буферу
        _window_buff[_buffer_pos]=value; //записуємо в буфер нове значення
        _buffer_sum=_buffer_sum+value; //додаємо нове значення в суму буферу
        _buffer_pos++;// зсуває позицію в буфері
        if(_buffer_pos==_WINDOW_SIZE)
        {
            _buffer_pos=0;
        }
        _last_value=_buffer_sum/_WINDOW_SIZE;
        return _last_value;
    }

    int32_t get_value()
    {
        return _last_value;
    }

    void clear(int32_t fill_value=0)
    {
        _buffer_pos = 0;
        _buffer_sum = (int64_t)fill_value * _WINDOW_SIZE;
        for (int32_t i=0; i < _WINDOW_SIZE; i++)
        {
            _window_buff[i] = fill_value;
        }
    }
private:
    int32_t _window_buff[_WINDOW_SIZE ]; //!< буфер для збереження значень
    int32_t _buffer_pos; //!< позиція в буфері
    int64_t _buffer_sum; //!< сума значень буферу
    int32_t _last_value;//!< Останнє значення фільтру для отримання без розрахунку

};

#endif /* SRC_VTFLTMOVINGAVERAGE_H_ */
