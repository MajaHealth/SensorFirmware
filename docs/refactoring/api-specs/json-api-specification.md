# JSON API Specification - All Services

**Project:** Sensor Firmware C++ to C Refactoring
**Purpose:** Complete JSON API documentation for protocol compatibility
**Date:** 2025-11-22
**CRITICAL:** This API must remain 100% compatible after C conversion

---

## OVERVIEW

All services communicate via JSON over TCP sockets. Each service listens on a specific port and accepts JSON requests, returning JSON responses.

### Service Ports

| Service | Port | Process Class | Purpose |
|---------|------|---------------|---------|
| ADS1293 (ECG) | 1293 | ADS1293_process | ECG sensor control/data |
| MAX30009 (Bio-Z) | 30009 | MAX30009_process | Bioimpedance measurement |
| WS2812 (LED) | 2812 | WS2812_process | LED control |
| Power Control | 501 | PWRCNTR_process | Battery & power management |

---

## COMMON PATTERNS

### Request Format
```json
{
    "type": "command_type",
    ... additional fields ...
}
```

### Response Format
```json
{
    "type": "response_type",
    ... response data ...
}
```

### Error Response
```json
{
    "type": "error JSON"
}
```

**Error Conditions:**
- Malformed JSON
- Missing "type" field
- Unknown command type
- Exception during processing

---

## SERVICE 1: ADS1293 (ECG Sensor) - Port 1293

### Command 1.1: Configure Settings

**Request:**
```json
{
    "type": "settings",
    "enable_conversion": true|false,    // Optional
    "power_enable": true|false,          // Optional
    "R2_rate": 4|5|6|8,                 // Optional (decimation rate)
    "R3_rate": 4|6|8|12|16|32|64|128    // Optional (decimation rate)
}
```

**Response:**
```json
{
    "type": "actual_settings",
    "enable_conversion": true|false,
    "power_enable": true|false,
    "R2_rate": 4|5|6|8,
    "R3_rate": 4|6|8|12|16|32|64|128
}
```

**Notes:**
- All fields are optional in request
- Response always contains current settings (after applying changes)
- Invalid R2_rate values default to 8
- Invalid R3_rate values default to 128
- Triggers `process_all_settings_for_ADS1293()` which configures channels, RLD, clock, etc.

---

### Command 1.2: Get ECG Data

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
    "data_frequency": <number>,
    "data_size": <number>,
    "timestamp": "<ISO8601 timestamp>",
    "data": [
        [ch1, ch2, ch3],          // Normal data point
        [-99999, sync_num, 0],    // Sync mark (every 1 second)
        [ch1, ch2, ch3],
        ...
    ]
}
```

**Data Format:**
- Each data point is array of 3 channels (ch1, ch2, ch3)
- Sync marks: `[SYNC_MARK_MAGIC_NUM=-99999, sync_number, 0]`
- Sync marks inserted every 1 second by main loop
- IFIFO buffer size: 3000 elements
- Ring buffer: `_IFIFO_write_pos` and `_IFIFO_read_pos`

---

## SERVICE 2: MAX30009 (Bio-Impedance) - Port 30009

### Command 2.1: Configure Settings

**Request:**
```json
{
    "type": "settings",
    "stimulate_frequency": <number>,     // Optional (1/10 Hz units)
    "measure_frequency": <number>,       // Optional (1-500 Hz)
    "out_LP_filter": <number>,           // Optional
    "out_HP_filter": <number>,           // Optional
    "stimulate_current": <number>,       // Optional
    "measure_enable": true|false,        // Optional
    "power_enable": true|false,          // Optional
    "ext_MUX_state": <number>            // Optional (external MUX)
}
```

**Response (Normal):**
```json
{
    "type": "actual_settings",
    "stimulate_frequency": <number>,
    "measure_frequency": <number>,
    "out_LP_filter": <number>,
    "out_HP_filter": <number>,
    "stimulate_current": <number>,
    "measure_enable": true|false,
    "power_enable": true|false,
    "ext_MUX_state": <number>
}
```

**Response (During Calibration):**
```json
{
    "type": "calibrate_runing"
}
```

**Notes:**
- measure_frequency clamped: MIN=1, MAX=500 Hz
- Settings application calls `process_all_settings_for_MAX30009()` 4 times
- External MUX settings applied via `process_ext_MUX_settings_for_MAX30009()`
- Settings rejected if calibration is running

---

### Command 2.2: Get Bio-Impedance Data

**Request:**
```json
{
    "type": "get_data"
}
```

**Response (Normal):**
```json
{
    "type": "data",
    "data_frequency": <number>,
    "data_size": <number>,
    "timestamp": "<ISO8601 timestamp>",
    "data": [
        [load_real*10000, load_mag*10000, load_imag*10000, load_angle*10000, overload],
        [-99999, sync_num, 0, 0, 0],  // Sync mark
        ...
    ]
}
```

**Response (During Calibration):**
```json
{
    "type": "calibrate_runing"
}
```

**Data Format:**
- 5 elements per point: [real, magnitude, imaginary, angle, overload_flag]
- All impedance values multiplied by 10000 before sending (fixed-point encoding)
- Sync marks: `[-99999, sync_number, 0, 0, 0]`
- IFIFO buffer size: 30,000 elements
- Data is decimated before transmission via `get_decimate_IFIFO_data()`

---

### Command 2.3: Start Calibration

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

**Side Effects:**
- Sets `_need_calibrate = true`
- Resets calibration indices to 0
- Blocks settings changes and data retrieval during calibration
- Calibration runs asynchronously in `calibration_process()`

---

### Command 2.4: Stop Calibration

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

**Side Effects:**
- Sets `_need_calibrate = false`
- Resets calibration indices to 0

---

### Async Event 2.5: Calibration Data (Unsolicited)

**Sent automatically when calibration step completes:**
```json
{
    "type": "calibration_data",
    "timestamp": "<ISO8601 timestamp>",
    "current_index": <0-4>,
    "freq_index": <0-16>,
    "stimulate_frequency": <number>,
    "stimulate_current": <number>,
    "Load_mag": <float>,
    "Load_angle": <float>,
    "Load_real": <float>,
    "Load_imag": <float>
}
```

**Calibration Parameters:**
- FREQ_POINTS: [25, 100, 200, 500, 1000, 5000, 10000, 20000, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000] (17 points, 1/10 Hz units)
- CURRENT_POINTS: [64uA, 128uA, 256uA, 640uA, 1.28mA] (5 points)
- Total calibration points: 5 × 17 = 85
- CALIB_STEP_PERIOD: 60 iterations
- CALIB_RESISTOR_VALUE: 100.0 Ω
- Calibration data saved to files in `calib/` directory

---

## SERVICE 3: WS2812 (LED Control) - Port 2812

### Command 3.1: Set LED Colors

**Request:**
```json
{
    "type": "set_colors",        // Implied (any type works if "leds" present)
    "leds": [
        [R, G, B],               // LED 0
        [R, G, B],               // LED 1
        ...
    ],
    "t_time": <transition_time_ms>  // Optional (transition duration)
}
```

**Response:**
```json
{
    "type": "colors_is_set"
}
```

**Error Response:**
```json
{
    "type": "error JSON"
}
```

**Notes:**
- LED count: 9 (WS_LED_COUNT)
- RGB values: 0-255 per channel
- If LED count in request > 9, extra LEDs ignored
- If `leds` array missing or not array → error
- If individual LED color not 3-element array → breaks processing
- Transition time in milliseconds (default: 0 = instant)
- Transition uses smooth interpolation: 2 steps per ms (STEPS_IN_MS=2.0)
- Animation runs in `process()` loop

**Animation Details:**
- `transition_step` = (transition_time × 2.0) + 1
- Color increment per step = (new - actual) / transition_step
- Runs every 500μs in main loop

---

## SERVICE 4: PWRCNTR (Power Control) - Port 501

### Command 4.1: Get Battery Info

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
    "voltage": <float>,                    // Volts
    "temperature": <float>,                // Celsius
    "current": <float>,                    // Amps
    "relative_state_of_charge": <int>,     // Percent
    "remaining_capacity": <float>,         // Ah
    "full_charge_capacity": <float>,       // Ah
    "run_time_to_empty": <uint16>,         // Minutes
    "average_time_to_empty": <uint16>,     // Minutes
    "average_time_to_full": <uint16>,      // Minutes
    "cycle_count": <uint16>,               // Cycles
    "design_capacity": <float>,            // Ah
    "design_voltage": <float>,             // Volts
    "fully_discharged": true|false,
    "fully_charged": true|false,
    "discharging": true|false,
    "charging": true|false,                // Inverse of discharging
    "charger_is_connect": true|false,      // GPIO state
    "battery_charge_is_disable": true|false
}
```

**Data Source:**
- I2C address: 0x0B (BATTERY_I2C_ADDRESS)
- SMBus protocol via `SES_battery_info` class
- Battery status register (BATTERY_STATUS) parsed as bitfield
- Updates throttled to every ~3 seconds (battery_read_delay_tmr > 30 × 100ms)

---

### Command 4.2: Disable Charging

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

**Side Effects:**
- Sets GPIO_CHARGE_DISABLE to HIGH
- Updates `_BATT.battery_charge_is_disable = true`

---

### Command 4.3: Enable Charging

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

**Side Effects:**
- Sets GPIO_CHARGE_DISABLE to LOW
- Updates `_BATT.battery_charge_is_disable = false`

---

### Command 4.4: Activate Buzzer

**Request:**
```json
{
    "type": "buzzer",
    "duration": <number>  // Optional (100ms units, 0-100)
}
```

**Response:**
```json
Empty string ""
```

**Notes:**
- Duration in 100ms units (loop period)
- Valid range: 0-100 (clamped automatically)
- Values < 0 or > 100 → set to 0
- Buzzer controlled via `process_buzzer()` called every 100ms
- `_buzzer_timer` decrements each loop
- GPIO_BUZZER set HIGH while timer > 0

---

### Async Event 4.5: Button State (Unsolicited)

**Sent automatically when button state changes:**
```json
{
    "type": "button_info",
    "state": true|false,     // true = pressed, false = released
    "hold_time": <number>    // Seconds (hold duration / 10)
}
```

**Button Logic:**
- Polled in `process_button()` every loop (100ms)
- GPIO_POWER_KEY: LOW = pressed, HIGH = released
- Hold time increments while pressed
- Sends update every 1 second while held (hold_time % 10 == 1)
- Sends release event when button released after being pressed
- No event if button remains released

---

## TCP CONNECTION PROTOCOL

### Connection Flow

1. **Client connects** to service port
2. **Server sends:** `"Connection accepted\n"`
3. **Client sends:** JSON request terminated by any data
4. **Server receives:** Request stored in `request_json` string
5. **Server sets:** `request_ready_flag = true` (atomic)
6. **Main loop processes:** Calls `process_JSON_line()`
7. **Main loop stores:** Response in `response_json`
8. **Main loop sets:** `response_ready_flag = true` (atomic)
9. **Server thread sends:** Response + `"\n"`
10. **Server resets:** `response_ready_flag = false`
11. **Loop continues** until client disconnects

### Connection Management

- **Non-blocking sockets:** fcntl(O_NONBLOCK)
- **Socket reuse:** SO_REUSEADDR | SO_REUSEPORT
- **Polling:** `poll()` with POLLIN to check readability
- **Client detection:** Send 0-byte message to check connection
- **Read buffer:** 2048 bytes per request
- **Server thread:** Runs in separate pthread
- **Atomic flags:** std::atomic<bool> for thread safety
- **Memory ordering:** acquire/release semantics

---

## TIMING REQUIREMENTS (CRITICAL FOR C CONVERSION)

### SPI Service Main Loop
- **Loop period:** 500 microseconds (`usleep(500)`)
- **Sync mark interval:** 1 second (checked via std::chrono)
- **Sync counter:** Increments every 1000ms
- **Process calls:** All 3 devices every loop

### Power Service Main Loop
- **Loop period:** 100 milliseconds (`delay(100)`)
- **Battery read throttle:** Every ~3 seconds (counter > 30)
- **Button polling:** Every loop
- **Buzzer update:** Every loop

### Calibration Process (MAX30009)
- **Step period:** 60 loop iterations
- **Per frequency point:** 60 × 500μs = 30ms
- **Total calibration time:** 85 points × 30ms = 2.55 seconds

---

## STRING HANDLING FOR C CONVERSION

### Current C++ String Usage

**Input strings:**
- `std::string` from TCP buffer
- Converted to `const char*` for `process_JSON_line()`

**Output strings:**
- `std::string` return from `process_JSON_line()`
- `json.dump()` returns `std::string`

**C Conversion Strategy:**
- Fixed-size char buffers (2048 bytes matches TCP buffer)
- `process_json_line(const char* request, char* response, size_t max_len)`
- Return int (bytes written or error code)
- Or: Return pointer to response buffer

---

## JSON LIBRARY REPLACEMENT OPTIONS

### Option 1: cJSON
**Pros:**
- Lightweight (single .c/.h file)
- Simple API
- No dependencies

**Cons:**
- Manual memory management
- Less feature-rich

**Example:**
```c
cJSON *root = cJSON_Parse(request);
cJSON *type = cJSON_GetObjectItem(root, "type");
if (cJSON_IsString(type)) {
    if (strcmp(type->valuestring, "settings") == 0) {
        // Process settings
    }
}
cJSON_Delete(root);
```

### Option 2: json-c
**Pros:**
- More mature
- Better error handling
- Reference counting

**Cons:**
- Larger library
- External dependency

**Recommendation:** cJSON for minimal overhead

---

## TESTING REQUIREMENTS

### API Compatibility Tests

For each service, create test scripts that:

1. **Connect to port**
2. **Send all command types** with various parameters
3. **Validate response format** (JSON structure)
4. **Validate response content** (data types, ranges)
5. **Test error conditions** (malformed JSON, missing fields)
6. **Test async events** (calibration, button)
7. **Load testing** (multiple rapid requests)
8. **Timing tests** (sync marks at correct intervals)

### Example Test Cases

**ADS1293:**
- Send settings with all fields
- Send settings with partial fields
- Get data and verify sync marks every 1 second
- Send invalid R2/R3 rates, verify defaults

**MAX30009:**
- Start calibration, wait for 85 async responses
- Try settings during calibration (expect "calibrate_runing")
- Stop calibration mid-way
- Verify data point format (5 elements)

**WS2812:**
- Send 9 LED colors
- Send 20 LED colors (verify only 9 applied)
- Send transition_time, verify smooth animation
- Send malformed LED array

**PWRCNTR:**
- Get battery info 10 times in 1 second (should get same data)
- Enable/disable charging
- Trigger buzzer for various durations
- Monitor button events (press, hold, release)

---

## CRITICAL COMPATIBILITY NOTES

**MUST NOT CHANGE:**
- JSON field names (exact spelling, case)
- Data types (int vs float, etc.)
- Array structures
- Sync mark values (-99999 magic number)
- Port numbers
- Async event formats
- Error response format

**MAY OPTIMIZE:**
- Internal data structures (as long as JSON output matches)
- String buffer sizes (as long as large enough)
- Processing logic (as long as behavior matches)

---

## APPENDIX: Timestamp Format

**Function:** `get_timestamp_string()`
**Format:** ISO 8601 compatible
**Example:** "2025-11-22T15:30:45"

**C Implementation:**
```c
#include <time.h>

void get_timestamp_string(char* buffer, size_t size) {
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    strftime(buffer, size, "%Y-%m-%dT%H:%M:%S", tm_info);
}
```

---

**Document Status:** COMPLETE
**API Version:** 1.0
**Total Commands:** 13
**Total Async Events:** 2
**Last Updated:** 2025-11-22

