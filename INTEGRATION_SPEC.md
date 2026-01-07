# SPI Device Service Integration Specification

## Connection Details

| Service | Port | Description |
|---------|------|-------------|
| ECG (ADS1293) | 1293 | ECG data acquisition |
| ICG (MAX30009) | 30009 | Bioimpedance measurements |

**Protocol:** JSON over TCP, newline-delimited messages

**On Connect:** Server sends `Connection accepted\n`

---

## ECG Service API (Port 1293)

### 1. Enable Sensor

**Request:**
```json
{
    "type": "settings",
    "power_enable": true,
    "enable_conversion": true,
    "R2_rate": 4,
    "R3_rate": 16
}
```

**Response:**
```json
{
    "type": "actual_settings",
    "power_enable": true,
    "enable_conversion": true,
    "R2_rate": 4,
    "R3_rate": 16
}
```

**Parameters:**
- `R2_rate`: Valid values: `4`, `5`, `6`, `8`
- `R3_rate`: Valid values: `4`, `6`, `8`, `12`, `16`, `32`, `64`, `128`
- Sample Rate = 204800 / (R2_rate × R3_rate) Hz

---

### 2. Disable Sensor

**Request:**
```json
{
    "type": "settings",
    "power_enable": false,
    "enable_conversion": false,
    "R2_rate": 4,
    "R3_rate": 16
}
```

**Response:**
```json
{
    "type": "actual_settings",
    "power_enable": false,
    "enable_conversion": false,
    "R2_rate": 4,
    "R3_rate": 16
}
```

---

### 3. Get Data

**Request:**
```json
{"type": "get_data"}
```

**Response:**
```json
{
    "type": "data",
    "data_size": 150,
    "timestamp": "2025-01-15 10:30:45.123",
    "data": [
        [4124978, 6327300, 4094084],
        [4124629, 6327633, 4094019],
        [-99999, 329, 0],
        [4123639, 6328260, 4093894]
    ]
}
```

**Data Format:** `[CH1, CH2, CH3]` - 24-bit ECG values per channel

**Sync Mark:** `[-99999, <sync_number>, 0]` - inserted every 1 second

---

### 4. Check Electrodes

**Request:**
```json
{"type": "check_electrodes"}
```

**Response:**
```json
{
    "type": "check_electrodes",
    "status": "connected"
}
```

**Status values:** `"connected"` or `"disconnected"`

---

## ICG Service API (Port 30009)

### 1. Enable Measurement (Settings)

**Request:**
```json
{
    "type": "settings",
    "measure_enable": true,
    "stimulate_frequency": 10000,
    "measure_frequency": 5,
    "stimulate_current": "64uA",
    "input_HP_filter": "BYPASS",
    "out_HP_filter": "BYPASS",
    "out_LP_filter": "BYPASS"
}
```

**Response Sequence (async, ~1 second apart):**

```json
{"type": "meas_state", "state": "pre_measuring"}
```
```json
{"type": "meas_state", "state": "pre_measure_end", "real": 990}
```
```json
{"type": "meas_state", "state": "calibrating"}
```
```json
{"type": "meas_state", "state": "calibrate_end"}
```
```json
{"type": "meas_state", "state": "start_measuring"}
```
```json
{
    "type": "actual_settings",
    "gain": "x5",
    "input_HP_filter": "BYPASS",
    "measure_enable": true,
    "measure_frequency": 5,
    "out_HP_filter": "BYPASS",
    "out_LP_filter": "BYPASS",
    "stimulate_current": "64uA",
    "stimulate_frequency": 10000
}
```

**Valid `stimulate_current` values:**
`"16nA"`, `"32nA"`, `"80nA"`, `"160nA"`, `"320nA"`, `"640nA"`, `"1.6uA"`, `"3.2uA"`, `"6.4uA"`, `"12.8uA"`, `"32uA"`, `"64uA"`, `"128uA"`, `"256uA"`, `"640uA"`, `"1.28mA"`

**Valid `input_HP_filter` values:**
`"100Hz"`, `"200Hz"`, `"500Hz"`, `"1000Hz"`, `"2000Hz"`, `"5000Hz"`, `"10000Hz"`, `"BYPASS"`

**Valid `out_HP_filter` values:**
`"BYPASS"`, `"0_00025xSR"`, `"0_002xSR"`

**Valid `out_LP_filter` values:**
`"BYPASS"`, `"0_005xSR"`, `"0_02xSR"`, `"0_08xSR"`, `"0_25xSR"`

---

### 2. Disable Measurement (Settings)

**Request:**
```json
{
    "type": "settings",
    "measure_enable": false
}
```

**Response:**
```json
{
    "type": "actual_settings",
    "gain": "x5",
    "input_HP_filter": "BYPASS",
    "measure_enable": false,
    "measure_frequency": 5,
    "out_HP_filter": "BYPASS",
    "out_LP_filter": "BYPASS",
    "stimulate_current": "64uA",
    "stimulate_frequency": 10000
}
```

---

### 3. Get Data

**Request:**
```json
{"type": "get_data"}
```

**Response (when measuring):**
```json
{
    "type": "data",
    "data_frequency": 5,
    "data_size": 28,
    "timestamp": "2025-01-15 10:30:45.123",
    "data": [
        [17167805, 17208880, -1188289, -39594, 0],
        [-999990000, 230000, 0, 0, 0],
        [17167484, 17208530, -1187866, -39581, 0]
    ]
}
```

**Response (when not measuring):**
```json
{"type": "no_measure"}
```

**Data Format:** `[Load_real, Load_mag, Load_imag, Load_angle, overload]`
- All values multiplied by 10000 (divide by 10000 for actual value)
- `overload`: 0 or 1

**Sync Mark:** `[-999990000, <sync_number * 10000>, 0, 0, 0]` - inserted every 1 second

---

### 4. Build Base Table

**Request:**
```json
{"type": "build_base_table"}
```

**Response:**
```json
{"type": "build_base_table_started"}
```

*Run once at application startup*

---

### 5. Power Off

**Request:**
```json
{"type": "poweroff"}
```

**Response:**
```json
{"type": "power_is_off"}
```

---

## Error Response

**When JSON parsing fails:**
```json
{"type": "error JSON"}
```

**When calibration is running (ICG only):**
```json
{"type": "calibrate_runing"}
```
