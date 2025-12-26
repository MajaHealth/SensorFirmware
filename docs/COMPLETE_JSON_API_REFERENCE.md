# Complete JSON API Reference - Sensor Firmware Services

**Project:** Sensor Firmware Build
**Date:** 2025-12-26
**Purpose:** Complete command/response specification for all firmware services

---

## Quick Reference - Service Ports

| Service | Port | Purpose | File Location |
|---------|------|---------|---------------|
| ADS1293 | 1293 | ECG/Biopotential sensor | `services/spi-service/src/ADS1293_process.cpp` |
| MAX30009 | 30009 | Bio-impedance sensor | `services/spi-service/src/MAX30009_process.cpp` |
| WS2812 | 2812 | RGB LED control | `services/spi-service/src/WS2812_process.cpp` |
| Power Control | 501 | Battery & power management | `services/power-service/src/PWRCNTR_process.cpp` |

**Connection:** All services listen on `127.0.0.1:<port>` (localhost)

---

## SERVICE 1: ADS1293 (ECG Sensor)

**Port:** 1293
**Protocol:** JSON over TCP
**Purpose:** ECG/biopotential data acquisition

### Commands

#### 1.1. Configure Settings

**Request:**
```json
{
  "type": "settings",
  "enable_conversion": true,
  "power_enable": true,
  "R2_rate": 4,
  "R3_rate": 128
}
```

**Fields:**
- `type` (required): Must be `"settings"`
- `enable_conversion` (optional, boolean): Start/stop ADC conversion
  - `true`: Enable data acquisition
  - `false`: Stop data acquisition
- `power_enable` (optional, boolean): Power control
  - `true`: Power on ADS1293
  - `false`: Power off ADS1293
- `R2_rate` (optional, integer): Stage 2 decimation rate
  - Valid values: `4`, `5`, `6`, `8`
  - Default: `8`
- `R3_rate` (optional, integer): Stage 3 decimation rate
  - Valid values: `4`, `6`, `8`, `12`, `16`, `32`, `64`, `128`
  - Default: `128`

**Response:**
```json
{
  "type": "actual_settings",
  "enable_conversion": true,
  "power_enable": true,
  "R2_rate": 4,
  "R3_rate": 128
}
```

**Notes:**
- All fields are optional; only provided fields will be updated
- Response always returns current settings (after applying changes)
- Invalid R2/R3 rates are clamped to valid values
- Triggers full sensor reconfiguration when settings change

---

#### 1.2. Get ECG Data

**Request:**
```json
{
  "type": "get_data"
}
```

**Response:**
```json
{
  "type": "data",
  "data_size": 1205,
  "timestamp": "2025-12-26 14:30:45.123",
  "data": [
    [12345, -6789, 98765],
    [12350, -6780, 98770],
    [-99999, 379, 0],
    [12355, -6775, 98775]
  ]
}
```

**Fields:**
- `type`: Always `"data"`
- `data_size`: Number of samples in data array
- `timestamp`: GMT timestamp in format `YYYY-MM-DD HH:MM:SS.mmm`
- `data`: Array of 3-channel ECG samples
  - Each sample: `[CH1, CH2, CH3]` as 32-bit signed integers
  - **Sync marker format:** `[-99999, sync_counter, 0]`
    - Magic number: `-99999` identifies sync marker
    - `sync_counter`: Monotonically increasing counter (increments every 1 second)
    - Third value always `0`

**Notes:**
- Returns last ~3 seconds of buffered data
- Sync markers inserted every 1 second for time synchronization
- Data units are raw ADC values (24-bit signed, extended to 32-bit)

---

#### 1.3. Error Response

**Response:**
```json
{
  "type": "error JSON"
}
```

**Triggered by:**
- Malformed JSON
- Missing `"type"` field
- Exception during command processing

---

## SERVICE 2: MAX30009 (Bio-Impedance Sensor)

**Port:** 30009
**Protocol:** JSON over TCP
**Purpose:** Bio-impedance spectroscopy and ICG measurements

### Commands

#### 2.1. Configure Settings

**Request:**
```json
{
  "type": "settings",
  "stimulate_frequency": 7,
  "measure_frequency": 400,
  "out_LP_filter": 0,
  "out_HP_filter": 0,
  "stimulate_current": 4,
  "measure_enable": true,
  "power_enable": true,
  "ext_MUX_state": 1
}
```

**Fields:**
- `type` (required): Must be `"settings"`
- `stimulate_frequency` (optional, integer): Stimulation frequency index (0-16)
  - `0`: 25 Hz
  - `1`: 100 Hz
  - `2`: 200 Hz
  - `3`: 500 Hz
  - `4`: 1 kHz
  - `5`: 5 kHz
  - `6`: 10 kHz
  - `7`: 20 kHz
  - `8`: 50 kHz
  - `9`: 100 kHz
  - `10`: 150 kHz
  - `11`: 200 kHz
  - `12`: 250 kHz
  - `13`: 300 kHz
  - `14`: 350 kHz
  - `15`: 400 kHz
  - `16`: 450 kHz
- `measure_frequency` (optional, integer): Sampling rate in Hz (1-500)
  - Typically: `400` Hz for physiological measurements
- `out_LP_filter` (optional, integer): Digital low-pass filter (0-4)
  - `0`: Bypass (no filtering)
  - `1`: 0.005 × SR_BIOZ
  - `2`: 0.02 × SR_BIOZ
  - `3`: 0.08 × SR_BIOZ
  - `4`: 0.25 × SR_BIOZ
- `out_HP_filter` (optional, integer): Digital high-pass filter (0-2)
  - `0`: Bypass (no filtering)
  - `1`: 0.00025 × SR_BIOZ
  - `2`: 0.002 × SR_BIOZ
- `stimulate_current` (optional, integer): Stimulation current index (0-4)
  - `0`: 64 µA
  - `1`: 128 µA
  - `2`: 256 µA
  - `3`: 640 µA
  - `4`: 1.28 mA
- `measure_enable` (optional, boolean): Enable/disable measurements
  - `true`: Start measuring
  - `false`: Stop measuring
- `power_enable` (optional, boolean): Power control
  - `true`: Power on MAX30009
  - `false`: Power off MAX30009
- `ext_MUX_state` (optional, integer): External multiplexer state (0-4)
  - `0`: ALL_OFF - All switches off
  - `1`: 4_WIRE - 4-wire configuration
  - `2`: 2_WIRE - 2-wire configuration
  - `3`: CALIBRATE - Calibration mode
  - `4`: COLE_COLE - Cole-Cole spectroscopy mode

**Response (Success):**
```json
{
  "type": "actual_settings",
  "stimulate_frequency": 7,
  "measure_frequency": 400,
  "out_LP_filter": 0,
  "out_HP_filter": 0,
  "stimulate_current": 4,
  "measure_enable": true,
  "power_enable": true,
  "ext_MUX_state": 1
}
```

**Response (Calibration Running):**
```json
{
  "type": "calibrate_runing"
}
```
- Returned if calibration is in progress (settings cannot be changed during calibration)

---

#### 2.2. Get Bio-Impedance Data

**Request:**
```json
{
  "type": "get_data"
}
```

**Response (Success):**
```json
{
  "type": "data",
  "data_frequency": 400,
  "data_size": 1205,
  "timestamp": "2025-12-26 14:30:45.123",
  "data": [
    [1234500, 5678900, -9876500, 4321000, 0],
    [1235000, 5679000, -9877000, 4320000, 0],
    [-999990000, 3790000, 0, 0, 0],
    [1235500, 5679500, -9877500, 4319500, 0]
  ]
}
```

**Fields:**
- `type`: Always `"data"`
- `data_frequency`: Actual sampling frequency (Hz)
- `data_size`: Number of samples in data array
- `timestamp`: GMT timestamp in format `YYYY-MM-DD HH:MM:SS.mmm`
- `data`: Array of 5-element impedance measurements
  - Each sample: `[Real, Magnitude, Imaginary, Phase_Angle, Overload_Flag]`
  - **All values are scaled by 10000** (divide by 10000 to get actual values)
  - `Real`: Real component of impedance (Ohms × 10000)
  - `Magnitude`: Magnitude of impedance (Ohms × 10000)
  - `Imaginary`: Imaginary component (Ohms × 10000)
  - `Phase_Angle`: Phase angle (degrees × 10000)
  - `Overload_Flag`: Overload detection flag (0 = normal, non-zero = overload)
  - **Sync marker format:** `[-999990000, sync_counter × 10000, 0, 0, 0]`
    - Magic number: `-999990000` identifies sync marker
    - `sync_counter`: Monotonically increasing (divide by 10000 to get actual counter)
    - Inserted every 1 second

**Response (Calibration Running):**
```json
{
  "type": "calibrate_runing"
}
```

**Notes:**
- Returns last ~3 seconds of buffered data
- Sync markers ensure time alignment with ADS1293
- Scaling by 10000 allows integer storage of float values

---

#### 2.3. Start Calibration

**Request:**
```json
{
  "type": "start_calibrate"
}
```

**Response:**
```json
{
  "type": "calibrate_started"
}
```

**Asynchronous Push Messages During Calibration:**

The service will send periodic calibration data messages:

```json
{
  "type": "calib_data",
  "stimulate_frequency": 7,
  "stimulate_current": 4,
  "I_offset": 123.456,
  "I_coef": 0.9876,
  "I_phase_coef": 1.234,
  "I_phase_cos": 0.999,
  "I_phase_sin": 0.001,
  "Q_offset": 234.567,
  "Q_coef": 0.9865,
  "Q_phase_coef": 1.345,
  "Q_phase_cos": 0.998,
  "Q_phase_sin": 0.002,
  "I_cal_in": 1000.0,
  "I_cal_in_ADC": 65535.0,
  "I_cal_quad": 500.0,
  "Q_cal_in": 1001.0,
  "Q_cal_in_ADC": 65536.0,
  "Q_cal_quad": 501.0
}
```

**Fields:**
- Calibration coefficients for I (in-phase) and Q (quadrature) channels
- `stimulate_frequency`: Frequency index being calibrated
- `stimulate_current`: Current index being calibrated
- Sent for each frequency/current combination during calibration sweep

---

#### 2.4. Stop Calibration

**Request:**
```json
{
  "type": "stop_calibrate"
}
```

**Response:**
```json
{
  "type": "calibrate_stoped"
}
```

---

#### 2.5. Error Response

**Response:**
```json
{
  "type": "error JSON"
}
```

**Triggered by:**
- Malformed JSON
- Missing `"type"` field
- Exception during command processing

---

## SERVICE 3: WS2812 (RGB LED Control)

**Port:** 2812
**Protocol:** JSON over TCP
**Purpose:** Control 9 RGB LEDs with smooth transitions

### Commands

#### 3.1. Set LED Colors

**Request:**
```json
{
  "leds": [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [0, 255, 255],
    [255, 0, 255],
    [255, 255, 255],
    [128, 128, 128],
    [0, 0, 0]
  ],
  "t_time": 1000
}
```

**Fields:**
- `leds` (required): Array of exactly **9 RGB color arrays**
  - Each color: `[R, G, B]` where R, G, B are 0-255
  - LED order: `[LED0, LED1, LED2, LED3, LED4, LED5, LED6, LED7, LED8]`
- `t_time` (optional, float): Transition time in **milliseconds**
  - Default: `0` (immediate color change)
  - Animation rate: 2 steps per millisecond
  - Example: `1000` ms = smooth 1-second transition

**Response:**
```json
{
  "type": "colors_is_set"
}
```

**Examples:**

Immediate color change:
```json
{
  "leds": [
    [255, 0, 0], [255, 0, 0], [255, 0, 0],
    [255, 0, 0], [255, 0, 0], [255, 0, 0],
    [255, 0, 0], [255, 0, 0], [255, 0, 0]
  ]
}
```

Smooth 2-second fade to blue:
```json
{
  "leds": [
    [0, 0, 255], [0, 0, 255], [0, 0, 255],
    [0, 0, 255], [0, 0, 255], [0, 0, 255],
    [0, 0, 255], [0, 0, 255], [0, 0, 255]
  ],
  "t_time": 2000
}
```

Rainbow pattern:
```json
{
  "leds": [
    [255, 0, 0],     // Red
    [255, 127, 0],   // Orange
    [255, 255, 0],   // Yellow
    [0, 255, 0],     // Green
    [0, 255, 255],   // Cyan
    [0, 0, 255],     // Blue
    [127, 0, 255],   // Purple
    [255, 0, 127],   // Magenta
    [0, 0, 0]        // Off
  ],
  "t_time": 500
}
```

---

#### 3.2. Error Response

**Response:**
```json
{
  "type": "error JSON"
}
```

**Triggered by:**
- Malformed JSON
- Missing `"leds"` array
- `leds` array not exactly 9 elements
- Exception during processing

---

## SERVICE 4: Power Control (PWRCNTR)

**Port:** 501
**Protocol:** JSON over TCP
**Purpose:** Battery monitoring, charging control, buzzer, button events

### Commands

#### 4.1. Get Battery Information

**Request:**
```json
{
  "type": "get_batt_info"
}
```

**Response:**
```json
{
  "type": "batt_info",
  "voltage": 12.6,
  "temperature": 25.3,
  "current": -1.5,
  "relative_state_of_charge": 85,
  "remaining_capacity": 8500.0,
  "full_charge_capacity": 10000.0,
  "run_time_to_empty": 340,
  "average_time_to_empty": 360,
  "average_time_to_full": 120,
  "cycle_count": 42,
  "design_capacity": 10000.0,
  "design_voltage": 12.0,
  "fully_discharged": false,
  "fully_charged": false,
  "discharging": true,
  "charging": false,
  "charger_is_connect": false,
  "battery_charge_is_disable": false
}
```

**Fields:**
- `voltage` (float): Battery voltage in Volts
- `temperature` (float): Battery temperature in °C
- `current` (float): Battery current in Amperes (negative = discharging)
- `relative_state_of_charge` (int): State of charge percentage (0-100%)
- `remaining_capacity` (float): Remaining capacity in mAh
- `full_charge_capacity` (float): Full charge capacity in mAh
- `run_time_to_empty` (uint16): Runtime to empty in minutes
- `average_time_to_empty` (uint16): Average time to empty in minutes
- `average_time_to_full` (uint16): Average time to full in minutes
- `cycle_count` (uint16): Number of charge/discharge cycles
- `design_capacity` (float): Design capacity in mAh
- `design_voltage` (float): Design voltage in Volts
- `fully_discharged` (boolean): Battery fully discharged flag
- `fully_charged` (boolean): Battery fully charged flag
- `discharging` (boolean): Battery is discharging
- `charging` (boolean): Battery is charging (inverse of discharging)
- `charger_is_connect` (boolean): External charger connected (GPIO 24 detection)
- `battery_charge_is_disable` (boolean): Charging is disabled via software

**Notes:**
- Data sourced from I2C SMBus battery management IC
- Battery reading throttled to ~3 seconds to reduce I2C traffic
- `charging` field added for convenience (computed from `discharging`)

---

#### 4.2. Disable Battery Charging

**Request:**
```json
{
  "type": "charge_disable"
}
```

**Response:**
```json
{
  "type": "charge_is_disable"
}
```

**Notes:**
- Disables charging via GPIO control
- Useful for thermal management or battery protection

---

#### 4.3. Enable Battery Charging

**Request:**
```json
{
  "type": "charge_enable"
}
```

**Response:**
```json
{
  "type": "charge_is_enable"
}
```

**Notes:**
- Re-enables charging after `charge_disable`
- Normal charging behavior resumes

---

#### 4.4. Activate Buzzer

**Request:**
```json
{
  "type": "buzzer",
  "duration": 50
}
```

**Fields:**
- `type` (required): Must be `"buzzer"`
- `duration` (required, integer): Duration in **deciseconds** (1/10 second)
  - Valid range: 0-100 (0 to 10 seconds)
  - Values outside range are clamped
  - Example: `50` = 5 seconds

**Response:**
```
(empty string - no JSON response)
```

**Examples:**

Short beep (0.5 seconds):
```json
{
  "type": "buzzer",
  "duration": 5
}
```

Long beep (5 seconds):
```json
{
  "type": "buzzer",
  "duration": 50
}
```

Maximum duration (10 seconds):
```json
{
  "type": "buzzer",
  "duration": 100
}
```

---

#### 4.5. Asynchronous Button Events

**Push Message (Button Pressed/Held):**
```json
{
  "type": "button_info",
  "state": true,
  "hold_time": 15
}
```

**Push Message (Button Released):**
```json
{
  "type": "button_info",
  "state": false,
  "hold_time": 0
}
```

**Fields:**
- `type`: Always `"button_info"`
- `state` (boolean): Button state
  - `true`: Button is currently pressed
  - `false`: Button released
- `hold_time` (integer): Hold duration in **deciseconds** (1/10 second)
  - Increments while button is held
  - Resets to 0 on release

**Notes:**
- Sent automatically when button state changes
- Periodic updates while button is held
- No request required - asynchronous push

---

#### 4.6. Error Response

**Response:**
```json
{
  "type": "error JSON"
}
```

**Triggered by:**
- Malformed JSON
- Missing `"type"` field
- Exception during command processing

---

## Protocol Notes

### General Communication Pattern

1. **Client connects** to service port via TCP
2. **Client sends** JSON command (single line, newline-terminated)
3. **Service responds** with JSON response (single line)
4. **Connection persists** for multiple request/response cycles
5. **Asynchronous messages** may be pushed (calibration, button events)

### JSON Format Requirements

- All JSON must be **single-line** (no newlines within JSON)
- Messages terminated with `\n` (newline)
- UTF-8 encoding
- Whitespace between fields is allowed but not required

### Error Handling

All services return `{"type":"error JSON"}` for:
- Malformed JSON syntax
- Missing required `"type"` field
- Exceptions during command processing
- Unknown command types

### Timing Characteristics

| Service | Loop Delay | Data Rate | Notes |
|---------|------------|-----------|-------|
| ADS1293 | 500 µs | ~400 Hz | 1-second sync marks |
| MAX30009 | 500 µs | 1-500 Hz | 1-second sync marks |
| WS2812 | 500 µs | N/A | Animation at 2 steps/ms |
| Power | 100 ms | ~0.3 Hz | Battery read throttled to 3s |

### Sync Markers

Both ADS1293 and MAX30009 insert synchronization markers every 1 second:

**ADS1293 Sync Marker:**
```json
[-99999, sync_counter, 0]
```

**MAX30009 Sync Marker:**
```json
[-999990000, sync_counter_x10000, 0, 0, 0]
```

**Purpose:**
- Time alignment between multiple sensors
- Detect missing/duplicate data
- Verify sampling rate accuracy

**Validation:**
- `sync_counter` should increment by 1 each second
- No missing sync marks over long recordings
- Common sync numbers should align within 50 ms threshold

---

## Testing Recommendations

### Basic Connectivity Test

```python
import socket
import json

# Connect to ADS1293
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 1293))

# Send settings command
request = {"type": "settings", "enable_conversion": True}
sock.send((json.dumps(request) + '\n').encode())

# Receive response
response = sock.recv(4096).decode()
print(json.loads(response))
```

### Data Collection Test

```python
import socket
import json
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 30009))

# Configure MAX30009
settings = {
    "type": "settings",
    "measure_enable": True,
    "stimulate_frequency": 7,
    "measure_frequency": 400,
    "stimulate_current": 4,
    "ext_MUX_state": 1
}
sock.send((json.dumps(settings) + '\n').encode())
response = sock.recv(4096).decode()
print("Settings:", json.loads(response))

# Collect data for 10 seconds
for i in range(20):  # Poll every 0.5s
    request = {"type": "get_data"}
    sock.send((json.dumps(request) + '\n').encode())
    response = sock.recv(65536).decode()  # Large buffer for data
    data = json.loads(response)
    print(f"Sample {i}: {data['data_size']} samples")
    time.sleep(0.5)

sock.close()
```

### Multi-Service Synchronization Test

```python
import socket
import json
import time

# Connect to both sensors
ads_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ads_sock.connect(('127.0.0.1', 1293))

max_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
max_sock.connect(('127.0.0.1', 30009))

# Configure both sensors...

# Collect synchronized data
for i in range(120):  # 1 minute @ 0.5s intervals
    # Get ADS1293 data
    ads_sock.send(b'{"type":"get_data"}\n')
    ads_data = json.loads(ads_sock.recv(65536).decode())

    # Get MAX30009 data
    max_sock.send(b'{"type":"get_data"}\n')
    max_data = json.loads(max_sock.recv(65536).decode())

    # Extract sync counters
    ads_sync = [s[1] for s in ads_data['data'] if s[0] == -99999]
    max_sync = [s[1]//10000 for s in max_data['data'] if s[0] == -999990000]

    print(f"t={i*0.5}s | ADS sync: {ads_sync} | MAX sync: {max_sync}")

    time.sleep(0.5)
```

---

## Appendix: Source Code References

All command handling is implemented in `process_JSON_line()` methods:

- **ADS1293:** `services/spi-service/src/ADS1293_process.cpp:process_JSON_line()`
- **MAX30009:** `services/spi-service/src/MAX30009_process.cpp:process_JSON_line()`
- **WS2812:** `services/spi-service/src/WS2812_process.cpp:process_JSON_line()`
- **Power:** `services/power-service/src/PWRCNTR_process.cpp:process_JSON_line()`

TCP server implementation: `JSON_TCP_sever` class in:
- `services/spi-service/include/JSON_TCP_sever.h`
- `services/power-service/include/JSON_TCP_sever.h`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-26
**Extracted From:** Firmware source code analysis
