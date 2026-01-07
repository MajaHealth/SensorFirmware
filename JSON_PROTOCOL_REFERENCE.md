# SPI_DEV_servise JSON Protocol Reference

Complete JSON protocol documentation for all SPI_DEV_servise TCP interfaces.

---

## Connection Information

| Service | Port | Description |
|---------|------|-------------|
| MAX30009 | 30009 | Bioimpedance (BIOZ) measurements |
| ADS1293 | 1293 | 3-channel ECG measurements |
| WS2812 | 2812 | RGB LED strip control (9 LEDs) |

**Connect using:** `nc 127.0.0.1 <port>`

---

# 1. MAX30009 - Bioimpedance Sensor

## 1.1 Commands

### 1.1.1 settings

Configure measurement parameters and start/stop measurement.

**Request:**
```json
{
  "type": "settings",
  "measure_enable": true,
  "stimulate_frequency": 99968,
  "measure_frequency": 500,
  "stimulate_current": "640uA",
  "out_LP_filter": "BYPASS",
  "out_HP_filter": "BYPASS",
  "input_HP_filter": "BYPASS"
}
```

**Request Fields:**

| Field | Type | Required | Valid Values | Description |
|-------|------|----------|--------------|-------------|
| `type` | string | Yes | `"settings"` | Command type |
| `measure_enable` | boolean | Yes | `true`, `false` | Enable/disable measurement |
| `stimulate_frequency` | integer | Yes | Hz value | Stimulation frequency in Hz |
| `measure_frequency` | integer | Yes | Hz value | Data output rate in Hz |
| `stimulate_current` | string | Yes | `"16uA"`, `"32uA"`, `"64uA"`, `"128uA"`, `"256uA"`, `"640uA"` | Stimulation current amplitude |
| `out_LP_filter` | string | No | `"BYPASS"`, filter values | Output low-pass filter |
| `out_HP_filter` | string | No | `"BYPASS"`, filter values | Output high-pass filter |
| `input_HP_filter` | string | No | `"BYPASS"`, filter values | Input high-pass filter |
| `bioz_total_gain` | string | No | `"x1"`, `"x2"`, `"x5"`, `"x10"` | Total gain (auto-selected if omitted) |

**Response Sequence (when `measure_enable: true`):**

1. Pre-measurement phase:
```json
{"type": "meas_state", "state": "pre_measuring"}
```

2. Pre-measurement complete (shows measured impedance):
```json
{"type": "meas_state", "state": "pre_measure_end", "real": 642}
```

3. Calibration starts:
```json
{"type": "meas_state", "state": "calibrating"}
```

4. Calibration data:
```json
{
  "type": "calib_data",
  "ref_value": 643.0,
  "calibrate_frequency": 99968,
  "calibrate_current": "640uA",
  "calibrate_gain": "x1",
  "input_filter": "BYPASS",
  "I_cal_in": 618.51,
  "I_cal_in_ADC": 186832,
  "I_cal_quad": 50.93,
  "I_cal_quad_ADC": 15385.0,
  "I_coef": 0.9651684656109086,
  "I_offset": -546,
  "I_phase_coef": 4.707289352172135,
  "I_phase_cos": 0.996626954273485,
  "I_phase_sin": 0.08206530335992723,
  "Q_cal_in": -621.92,
  "Q_cal_in_ADC": -187862,
  "Q_cal_quad": -54.47,
  "Q_cal_quad_ADC": -16454.0,
  "Q_coef": 0.9709187911604229,
  "Q_offset": -331,
  "Q_phase_coef": 5.005398780568058,
  "Q_phase_cos": 0.9961864812890449,
  "Q_phase_sin": 0.08724961029684569
}
```

5. Calibration complete:
```json
{"type": "meas_state", "state": "calibrate_end"}
```

6. Measurement starts:
```json
{"type": "meas_state", "state": "start_measuring"}
```

7. Current settings confirmation:
```json
{"type": "actual_settings",
  "measure_enable": true,
  "stimulate_frequency": 99968,
  "measure_frequency": 500,
  "stimulate_current": "640uA",
  "gain": "x1",
  "out_LP_filter": "BYPASS",
  "out_HP_filter": "BYPASS",
  "input_HP_filter": "BYPASS"}
```

---

### 1.1.2 get_data

Retrieve collected impedance measurement data.

**Request:**
```json
{"type": "get_data"}
```

**Response (success):**
```json
{
  "type": "data",
  "timestamp": "2025-12-22 21:16:57.968",
  "data_frequency": 5,
  "data_size": 132,
  "data": [
    [-999990000, 510000, 0, 0, 0],
    [6530342, 6530347, 8227, 721, 0],
    [6536827, 6536834, 10104, 885, 0]
  ]
}
```

**Data Array Format:** `[I_ADC, Q_ADC, Load_real, Load_imag, Overload]`

| Index | Field | Description |
|-------|-------|-------------|
| 0 | I_ADC | In-phase ADC value |
| 1 | Q_ADC | Quadrature ADC value |
| 2 | Load_real | Real impedance component (mOhm) |
| 3 | Load_imag | Imaginary impedance component (mOhm) |
| 4 | Overload | Overload flag (0 = OK, 1 = overload) |

**Response (not measuring):**
```json
{"type": "no_measure"}
```

---

### 1.1.3 build_base_table

Build calibration table across frequency range. Uses fixed 370 Ohm reference resistor and 64uA current.

**Request:**
```json
{"type": "build_base_table"}
```

**Response:**
```json
{"type": "build_base_table_started"}
```

Followed by 100 `calib_data` responses (one per frequency point), then saves to `base_table.json`.

---

### 1.1.4 auto_test

Run automated testing across multiple frequency/current combinations. Results written to timestamped CSV file.

**Request:**
```json
{
  "type": "auto_test",
  "freqs_list": [1000, 5000, 10000, 50000, 100000],
  "currs_list": ["64uA", "128uA", "256uA"]
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `"auto_test"` |
| `freqs_list` | array[int] | Yes | List of frequencies to test (Hz) |
| `currs_list` | array[string] | Yes | List of currents to test |

**CSV Output Columns:**
```
Current, Frequency, Pre_meas_ohm, Calib_Ohm, Gain, Load_Real, Load_Imag,
Load_Mag, Load_Angle, Overload, DRV_overload, I_ADC, Q_ADC,
I_IMP_NO_CAL, Q_IMP_NO_CAL, I_CAL_ADC, Q_CAL_ADC
```

---

### 1.1.5 poweroff

Power down the MAX30009 sensor.

**Request:**
```json
{"type": "poweroff"}
```

**Response:**
```json
{"type": "power_is_off"}
```

---

## 1.2 State Machine

```
MMD_STOP ──────────────────────────────────────────────────────┐
    │ (settings with measure_enable=true)                      │
    ▼                                                          │
MMD_BASE_MEASURE_START                                         │
    │                                                          │
    ▼                                                          │
MMD_BASE_MEASURING (collects 20 samples)                       │
    │                                                          │
    ▼                                                          │
MMD_CALIBRATE_START                                            │
    │                                                          │
    ▼                                                          │
MMD_CALIBRATING (waits for calibration)                        │
    │                                                          │
    ▼                                                          │
MMD_MEASURE_START                                              │
    │                                                          │
    ▼                                                          │
MMD_MEASURING ◄────────────────────────────────────────────────┤
    │ (settings with measure_enable=false or poweroff)         │
    └──────────────────────────────────────────────────────────┘
```

---

## 1.3 Special Data Values

| Constant | Value | Description |
|----------|-------|-------------|
| SYNC_MAGIC_NUM | -999990000 | Sync mark in data stream |
| SYNC_COUNTER | Second element | Sync counter (increments every second) |

**Example sync mark in data:**
```json
[-999990000, 510000, 0, 0, 0]
```
Where `510000` = sync counter 51 * 10000

---

## 1.4 Error Responses

```json
{"type": "error JSON"}
```
Returned for: malformed JSON, missing required fields, unknown command type.

```json
{"type": "error settings JSON"}
```
Returned for: invalid settings values.

---

# 2. ADS1293 - ECG Sensor

## 2.1 Commands

### 2.1.1 settings

Configure ADC decimation rates and enable conversion.

**Request:**
```json
{
  "type": "settings",
  "enable_conversion": true,
  "R1_rate": 4,
  "R2_rate": 8,
  "R3_rate": 128
}
```

**Request Fields:**

| Field | Type | Required | Valid Values | Default | Description |
|-------|------|----------|--------------|---------|-------------|
| `type` | string | Yes | `"settings"` | - | Command type |
| `enable_conversion` | boolean | Yes | `true`, `false` | - | Enable ADC conversion |
| `R1_rate` | integer | No | `2`, `4` | 4 | R1 decimation rate |
| `R2_rate` | integer | No | `4`, `5`, `6`, `8` | 8 | R2 decimation rate |
| `R3_rate` | integer | No | `4`, `6`, `8`, `12`, `16`, `32`, `64`, `128` | 128 | R3 decimation rate |

**Response:**
```json
{
  "type": "actual_settings",
  "enable_conversion": true,
  "R1_rate": 4,
  "R2_rate": 8,
  "R3_rate": 128
}
```

**Derived Parameters (calculated from R rates):**

| R1 | R2 | R3 | ODR (Hz) | Bandwidth (Hz) | uV/ADC |
|----|----|----|----------|----------------|--------|
| 4 | 8 | 128 | 50 | 10 | 0.163 |
| 4 | 8 | 64 | 100 | 20 | 0.163 |
| 4 | 8 | 32 | 200 | 40 | 0.163 |
| 2 | 8 | 128 | 100 | 20 | 0.082 |

---

### 2.1.2 get_data

Retrieve buffered ECG data from all 3 channels.

**Request:**
```json
{"type": "get_data"}
```

**Response:**
```json
{
  "type": "data",
  "timestamp": "2025-12-22 21:58:36.937",
  "data_rate": 50,
  "data_size": 142,
  "band_width": 10,
  "uV_per_ADC_unit": 0.1634870320558548,
  "data": [
    [24, -36, 1],
    [27, -36, 2],
    [-99999, 148, 0],
    [20, -37, -3]
  ]
}
```

**Data Array Format:** `[ch1, ch2, ch3]`

| Index | Field | Description |
|-------|-------|-------------|
| 0 | ch1 | Channel 1 ADC value (Input2 - Input1) |
| 1 | ch2 | Channel 2 ADC value (Input3 - Input1) |
| 2 | ch3 | Channel 3 ADC value (Input5 - Input6) |

**Convert to microvolts:** `uV = ADC_value * uV_per_ADC_unit`

---

### 2.1.3 poweroff

Power down the ADS1293 sensor.

**Request:**
```json
{"type": "poweroff"}
```

**Response:**
```json
{"type": "power_is_off"}
```

---

## 2.2 Special Data Values

| Constant | Value | Description |
|----------|-------|-------------|
| SYNC_MAGIC_NUM | -99999 | Sync mark boundary |
| ERROR_MAGIC_NUM | -99998 | Analog error detected |

**Sync mark example:**
```json
[-99999, 148, 0]
```
Where `148` is the sync counter (increments every second).

**Error mark example:**
```json
[-99998, 0, 0]
```
Inserted when CH1ERR, CH2ERR, CH3ERR, RLDRAIL, or CMOR flags are set.

---

## 2.3 Channel Configuration

| Channel | Positive Input | Negative Input |
|---------|----------------|----------------|
| CH1 | Input2 | Input1 |
| CH2 | Input3 | Input1 |
| CH3 | Input5 | Input6 |
| RLD (Right Leg Drive) | Input4 | - |
| Wilson Reference | Inputs 1, 2, 3 | - |

---

## 2.4 Error Responses

```json
{"type": "error JSON"}
```
Returned for: malformed JSON, missing required fields, unknown command type.

---

# 3. WS2812 - LED Controller

## 3.1 Commands

### 3.1.1 Set LED Colors

Set RGB colors for up to 9 LEDs with optional transition animation.

**Request:**
```json
{
  "leds": [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [255, 0, 255],
    [0, 255, 255],
    [255, 255, 255],
    [128, 128, 128],
    [0, 0, 0]
  ],
  "t_time": 1000
}
```

**Request Fields:**

| Field | Type | Required | Valid Values | Default | Description |
|-------|------|----------|--------------|---------|-------------|
| `leds` | array | Yes | Array of [R,G,B] | - | RGB colors for each LED |
| `t_time` | integer | No | 0+ milliseconds | 0 | Transition animation time |

**LED Array Format:** `[R, G, B]` where each value is 0-255.

**Constraints:**
- Maximum 9 LEDs supported
- Colors beyond LED 9 are silently ignored
- `t_time = 0` means instant color change
- `t_time > 0` creates smooth fade transition

**Response:**
```json
{"type": "colors_is_set"}
```

---

## 3.2 Animation System

When `t_time > 0`, the controller interpolates from current colors to target colors:

- **Step rate:** 2 steps per millisecond
- **Formula:** `steps = (t_time * 2) + 1`
- **Interpolation:** Linear per-channel (R, G, B calculated separately)

**Example:** `t_time: 1000` = 2001 animation steps over 1 second

---

## 3.3 Error Responses

```json
{"type": "error JSON"}
```
Returned for: malformed JSON, missing `leds` field, `leds` not an array.

---

# 4. Common Error Handling

All services return the same error format for invalid requests:

```json
{"type": "error JSON"}
```

**Triggers:**
- Malformed JSON syntax
- Missing required `type` field (MAX30009/ADS1293)
- Unknown command type
- Invalid field values
- Missing `leds` array (WS2812)

---

# 5. Data Synchronization

Both MAX30009 and ADS1293 support time synchronization via sync marks inserted every 1 second by the main loop.

| Sensor | Sync Magic Number | Counter Location |
|--------|-------------------|------------------|
| MAX30009 | -999990000 | data[1] / 10000 |
| ADS1293 | -99999 | data[1] |

**Usage:** Match sync counters across sensors to align timestamps.

---

# 6. Quick Reference

## MAX30009 Commands
```
{"type": "settings", "measure_enable": true, ...}
{"type": "get_data"}
{"type": "build_base_table"}
{"type": "auto_test", "freqs_list": [...], "currs_list": [...]}
{"type": "poweroff"}
```

## ADS1293 Commands
```
{"type": "settings", "enable_conversion": true, "R1_rate": 4, "R2_rate": 8, "R3_rate": 128}
{"type": "get_data"}
{"type": "poweroff"}
```

## WS2812 Commands
```
{"leds": [[R,G,B], ...], "t_time": ms}
```
