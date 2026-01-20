# ADS1293 Lead-Off Detection Implementation Plan

## Executive Summary

The ADS1293 ECG sensor has built-in lead-off detection (LOD) capability that can detect when electrodes become disconnected from the patient. The good news is that **the ADS1293_LIB library already has all the necessary methods implemented** - they just aren't being used by the `ADS1293_process` class.

## Current State Analysis

### What Already Exists in ADS1293_LIB.h

**Configuration Methods (already implemented):**
- `set_shutdown_leadoff_detection(bool enable)` - Enable/disable LOD circuit
- `set_leadoff_detect_mode(SELAC_LOD_MODE_TDE mode)` - DC or AC mode
- `set_AC_leadoff_mode(ACAD_LOD_MODE_TDE mode)` - Analog or digital AC detection
- `set_leadoff_AC_comparator_trigger_level(COMPARATOR_TRIGGER_LEVEL_TDE level)` - Threshold
- `set_leadoff_detection_for_input_1-6(bool enable)` - Enable per input pin
- `set_leadoff_detection_current(uint32_t current_nA)` - Current 0-2040 nA
- `set_leadoff_frequency_divider(uint8_t ratio, ACDIV_FACTOR_TDE factor)` - AC frequency

**Status Reading Methods (already implemented):**
- `get_leadoff_detect_error_status()` → Returns `RG_ERROR_LOD_TDS` with:
  - `OUT_LOD_IN1` through `OUT_LOD_IN6` - Individual input lead-off status bits
- `get_analog_other_error_status()` → Returns `RG_ERROR_STATUS_TDS` with:
  - `LEADOFF` bit - Overall lead-off detected flag

### What's Missing in ADS1293_process

The `ADS1293_process` class does NOT:
1. Configure lead-off detection during initialization
2. Periodically read lead-off status
3. Report lead-off status via JSON API
4. Include lead-off status in data responses

## Lead-Off Detection Background

### How It Works

The ADS1293 injects a small current (programmable 0-2040 nA) into the input pins. If an electrode is properly connected, this current flows through the body to ground via the RLD (Right Leg Drive) electrode. If an electrode is disconnected, the impedance rises dramatically, causing the voltage at that input to rise toward VDD, which triggers the comparator.

### Two Detection Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **DC** | Uses DC current injection | Simple, fewer components, can affect DC offset |
| **AC** | Uses AC current at configurable frequency | Better for continuous monitoring, minimal ECG impact |

### AC Detection Sub-modes

| Sub-mode | Description |
|----------|-------------|
| **Digital AC** | Uses digital processing to detect lead-off |
| **Analog AC** | Uses analog comparators for faster response |

### Recommended Configuration

Based on the datasheet and TI forums, for ECG monitoring:
- **Mode**: AC lead-off detection (doesn't affect ECG DC offset)
- **Sub-mode**: Analog AC (faster response)
- **Current**: 1-2 µA (1000-2000 nA) - detectable but minimal impact on signal
- **Frequency**: ~600 Hz (outside ECG bandwidth but detectable)
- **Threshold**: Level 1 or 2 (21-54 mV at 2kHz)

## Implementation Plan

### Phase 1: Add Lead-Off Configuration to ADS1293_process

**File: `SPI_DEV_servise/include/ADS1293_process.h`**

Add to `ADS1293_USER_SETTINGS`:
```cpp
typedef struct ADS1293_USER_SETTINGS
{
    bool enable_conversion;
    bool power_enable;
    int32_t R2_rate;
    int32_t R3_rate;

    // NEW: Lead-off detection settings
    bool leadoff_enable;           // Enable/disable lead-off detection
    uint32_t leadoff_mode;         // 0=DC, 1=AC
    uint32_t leadoff_current_nA;   // Current in nA (0-2040)
    uint32_t leadoff_threshold;    // Comparator level (0-3)

} ADS1293_USER_SETTINGS_TDE;
```

Add lead-off status structure:
```cpp
typedef struct ADS1293_LEADOFF_STATUS
{
    bool lead_off_detected;  // Overall flag
    bool in1_off;           // IN1 (typically RA)
    bool in2_off;           // IN2 (typically LA)
    bool in3_off;           // IN3 (typically LL)
    bool in4_off;           // IN4 (typically RL/RLD)
    bool in5_off;           // IN5
    bool in6_off;           // IN6
} ADS1293_LEADOFF_STATUS_TDS;
```

Add member variable:
```cpp
ADS1293_LEADOFF_STATUS_TDS _leadoff_status = {0};
```

Add methods:
```cpp
void configure_leadoff_detection(void);
void read_leadoff_status(void);
std::string get_leadoff_status_as_json(void);
```

### Phase 2: Implement Lead-Off Configuration

**File: `SPI_DEV_servise/src/ADS1293_process.cpp`**

Add in `process_all_settings_for_ADS1293()` after channel setup:
```cpp
void ADS1293_process::configure_leadoff_detection(void)
{
    if (ADS1293_user_sett.leadoff_enable == false)
    {
        // Shut down lead-off detection to save power
        ADS1293_obj.set_shutdown_leadoff_detection(true);
        return;
    }

    // Enable lead-off detection circuit
    ADS1293_obj.set_shutdown_leadoff_detection(false);

    // Set detection mode (DC=0, AC=1)
    if (ADS1293_user_sett.leadoff_mode == 1)
    {
        ADS1293_obj.set_leadoff_detect_mode(ADS1293::SELAC_LOD_AC);
        ADS1293_obj.set_AC_leadoff_mode(ADS1293::ACAD_LOD_ANALOG);
        // Set AC frequency ~625 Hz (divider=19, K=1)
        ADS1293_obj.set_leadoff_frequency_divider(19, ADS1293::ACDIV_FACTOR_K1);
    }
    else
    {
        ADS1293_obj.set_leadoff_detect_mode(ADS1293::SELAC_LOD_DC);
    }

    // Set comparator threshold level
    ADS1293::COMPARATOR_TRIGGER_LEVEL_TDE level = ADS1293::CTL_LEVEL_1;
    if (ADS1293_user_sett.leadoff_threshold == 0) level = ADS1293::CTL_LEVEL_0;
    else if (ADS1293_user_sett.leadoff_threshold == 1) level = ADS1293::CTL_LEVEL_1;
    else if (ADS1293_user_sett.leadoff_threshold == 2) level = ADS1293::CTL_LEVEL_2;
    else if (ADS1293_user_sett.leadoff_threshold == 3) level = ADS1293::CTL_LEVEL_3;
    ADS1293_obj.set_leadoff_AC_comparator_trigger_level(level);

    // Set detection current (default 1400 nA = 1.4 µA)
    uint32_t current = ADS1293_user_sett.leadoff_current_nA;
    if (current == 0) current = 1400;  // Default
    if (current > 2040) current = 2040;
    ADS1293_obj.set_leadoff_detection_current(current);

    // Enable lead-off detection ONLY for used inputs
    // Based on current channel configuration:
    // CH1: IN2(+) / IN1(-) → enable IN1, IN2
    // CH2: IN3(+) / IN1(-) → enable IN3 (IN1 already enabled)
    // CH3: IN5(+) / IN6(-) → enable IN5, IN6
    // RLD output: IN4

    ADS1293_obj.set_leadoff_detection_for_input_1(true);   // Used by CH1, CH2
    ADS1293_obj.set_leadoff_detection_for_input_2(true);   // Used by CH1
    ADS1293_obj.set_leadoff_detection_for_input_3(true);   // Used by CH2
    ADS1293_obj.set_leadoff_detection_for_input_4(false);  // RLD - don't monitor
    ADS1293_obj.set_leadoff_detection_for_input_5(true);   // Used by CH3
    ADS1293_obj.set_leadoff_detection_for_input_6(true);   // Used by CH3
}
```

### Phase 3: Implement Status Reading

```cpp
void ADS1293_process::read_leadoff_status(void)
{
    // Read lead-off error register
    ADS1293::RG_ERROR_LOD_TDS lod_status = ADS1293_obj.get_leadoff_detect_error_status();

    _leadoff_status.in1_off = lod_status.OUT_LOD_IN1;
    _leadoff_status.in2_off = lod_status.OUT_LOD_IN2;
    _leadoff_status.in3_off = lod_status.OUT_LOD_IN3;
    _leadoff_status.in4_off = lod_status.OUT_LOD_IN4;
    _leadoff_status.in5_off = lod_status.OUT_LOD_IN5;
    _leadoff_status.in6_off = lod_status.OUT_LOD_IN6;

    // Read general error status for overall flag
    ADS1293::RG_ERROR_STATUS_TDS err_status = ADS1293_obj.get_analog_other_error_status();
    _leadoff_status.lead_off_detected = err_status.LEADOFF;
}

std::string ADS1293_process::get_leadoff_status_as_json(void)
{
    read_leadoff_status();

    nlohmann::json response_json;
    response_json["type"] = "leadoff_status";
    response_json["lead_off_detected"] = _leadoff_status.lead_off_detected;
    response_json["in1_off"] = _leadoff_status.in1_off;  // RA
    response_json["in2_off"] = _leadoff_status.in2_off;  // LA
    response_json["in3_off"] = _leadoff_status.in3_off;  // LL
    response_json["in4_off"] = _leadoff_status.in4_off;  // RL
    response_json["in5_off"] = _leadoff_status.in5_off;
    response_json["in6_off"] = _leadoff_status.in6_off;

    // Map to standard ECG lead names for convenience
    response_json["ra_off"] = _leadoff_status.in1_off;
    response_json["la_off"] = _leadoff_status.in2_off;
    response_json["ll_off"] = _leadoff_status.in3_off;

    return response_json.dump();
}
```

### Phase 4: Add JSON API Commands

In `process_JSON_line()`, add new command handlers:

```cpp
if (command_type == "get_leadoff_status")
{
    return get_leadoff_status_as_json();
}

if (command_type == "settings")
{
    // ... existing code ...

    // NEW: Lead-off detection settings
    if (parsed_json.contains("leadoff_enable"))
    {
        ADS1293_user_sett.leadoff_enable = parsed_json["leadoff_enable"];
    }
    if (parsed_json.contains("leadoff_mode"))
    {
        ADS1293_user_sett.leadoff_mode = parsed_json["leadoff_mode"];
    }
    if (parsed_json.contains("leadoff_current_nA"))
    {
        ADS1293_user_sett.leadoff_current_nA = parsed_json["leadoff_current_nA"];
    }
    if (parsed_json.contains("leadoff_threshold"))
    {
        ADS1293_user_sett.leadoff_threshold = parsed_json["leadoff_threshold"];
    }

    // ... call configure_leadoff_detection() ...
}
```

### Phase 5: Include Lead-Off Status in Data Response

Modify `get_data_as_json()` to include lead-off status:

```cpp
std::string ADS1293_process::get_data_as_json(void)
{
    read_leadoff_status();  // Read current status

    nlohmann::json response_json;
    response_json["type"] = "data";
    response_json["data_size"] = buffer_size;
    response_json["timestamp"] = get_timestamp_string();

    // NEW: Include lead-off status with every data packet
    response_json["lead_off_detected"] = _leadoff_status.lead_off_detected;
    response_json["leadoff_in1"] = _leadoff_status.in1_off;
    response_json["leadoff_in2"] = _leadoff_status.in2_off;
    response_json["leadoff_in3"] = _leadoff_status.in3_off;
    response_json["leadoff_in5"] = _leadoff_status.in5_off;
    response_json["leadoff_in6"] = _leadoff_status.in6_off;

    // ... existing data array code ...

    return response_json.dump();
}
```

### Phase 6: Update Settings JSON Response

Update `get_all_settings_as_json()`:

```cpp
std::string ADS1293_process::get_all_settings_as_json(void)
{
    nlohmann::json response_json;
    response_json["type"] = "actual_settings";
    response_json["enable_conversion"] = ADS1293_user_sett.enable_conversion;
    response_json["power_enable"] = ADS1293_user_sett.power_enable;
    response_json["R2_rate"] = ADS1293_user_sett.R2_rate;
    response_json["R3_rate"] = ADS1293_user_sett.R3_rate;

    // NEW: Lead-off settings
    response_json["leadoff_enable"] = ADS1293_user_sett.leadoff_enable;
    response_json["leadoff_mode"] = ADS1293_user_sett.leadoff_mode;
    response_json["leadoff_current_nA"] = ADS1293_user_sett.leadoff_current_nA;
    response_json["leadoff_threshold"] = ADS1293_user_sett.leadoff_threshold;

    return response_json.dump();
}
```

## JSON API Reference

### Configure Lead-Off Detection

**Request:**
```json
{
    "type": "settings",
    "leadoff_enable": true,
    "leadoff_mode": 1,
    "leadoff_current_nA": 1400,
    "leadoff_threshold": 1
}
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `leadoff_enable` | bool | Enable/disable lead-off detection |
| `leadoff_mode` | int | 0=DC, 1=AC (recommended) |
| `leadoff_current_nA` | int | Detection current 0-2040 nA (recommended: 1000-1400) |
| `leadoff_threshold` | int | Comparator level 0-3 (recommended: 1) |

### Get Lead-Off Status

**Request:**
```json
{"type": "get_leadoff_status"}
```

**Response:**
```json
{
    "type": "leadoff_status",
    "lead_off_detected": false,
    "in1_off": false,
    "in2_off": false,
    "in3_off": true,
    "in4_off": false,
    "in5_off": false,
    "in6_off": false,
    "ra_off": false,
    "la_off": false,
    "ll_off": true
}
```

### Data Response with Lead-Off

**Response:**
```json
{
    "type": "data",
    "data_size": 100,
    "timestamp": "2024-01-20 12:00:00.123",
    "lead_off_detected": false,
    "leadoff_in1": false,
    "leadoff_in2": false,
    "leadoff_in3": false,
    "leadoff_in5": false,
    "leadoff_in6": false,
    "data": [[...], [...], ...]
}
```

## Default Configuration

Set sensible defaults in the struct initialization:

```cpp
ADS1293_USER_SETTINGS_TDE ADS1293_user_sett = {
    .enable_conversion = false,
    .power_enable = false,
    .R2_rate = 8,
    .R3_rate = 128,
    .leadoff_enable = true,        // Enable by default
    .leadoff_mode = 1,             // AC mode
    .leadoff_current_nA = 1400,    // 1.4 µA
    .leadoff_threshold = 1         // Level 1
};
```

## Testing Procedure

1. **Basic Functionality Test:**
   - Connect all electrodes properly
   - Send: `{"type": "get_leadoff_status"}`
   - Verify all `*_off` fields are `false`

2. **Lead Disconnect Test:**
   - Disconnect one electrode (e.g., LA)
   - Send: `{"type": "get_leadoff_status"}`
   - Verify corresponding field (e.g., `la_off`) is `true`

3. **Continuous Monitoring Test:**
   - Enable data streaming
   - Disconnect/reconnect electrodes
   - Verify `lead_off_detected` updates in data packets

## Important Notes

1. **RLD Electrode**: Don't enable lead-off detection on IN4 if it's used for RLD output - it needs a low impedance path to ground.

2. **AC Mode Recommended**: Use AC mode for continuous monitoring to avoid affecting the ECG DC offset.

3. **Threshold Tuning**: Start with Level 1. If getting false positives, increase to Level 2 or 3.

4. **Current Selection**: 1-2 µA is typical. Higher current = faster detection but more signal impact.

## References

- [ADS1293 Datasheet](https://www.ti.com/lit/ds/symlink/ads1293.pdf)
- [TI Application Note: Understanding Lead-Off Detection in ECG](https://www.ti.com/lit/pdf/sbaa196)
- [TI E2E Forum: ADS1293 AC Lead-Off Detection](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/446633/ads1293-analog-ac-lead-off-detection)
- [Protocentral ADS1293 Arduino Library](https://github.com/Protocentral/protocentral-ads1293-arduino)
- [ADS1293 Python Register Settings](https://github.com/whilemind/ADS1293/blob/master/TI2093RegSetting.py)
