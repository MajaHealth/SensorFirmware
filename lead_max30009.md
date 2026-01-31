# MAX30009 Drive Electrode Lead-On/Lead-Off Detection Implementation Plan

## Overview

Implement I+ (DRVP) and I- (DRVN) drive electrode lead detection for the MAX30009 Bioimpedance AFE in AC-coupled tetrapolar configuration.

---

## Hardware Context

### Electrode Configuration (MayaCardio Check)

| Electrode | Function | MAX30009 Pin | Internal Assignment |
|-----------|----------|--------------|---------------------|
| **I+** | DRVP (Current Source) | EL1 | `DRVP_ASSIGN = EL1` |
| **I-** | DRVN (Current Sink) | EL4 | `DRVN_ASSIGN = EL4` |
| V+ | BIP (Voltage Sense +) | EL2B | `BIP_ASSIGN = EL2B` |
| V- | BIN (Voltage Sense -) | EL3B | `BIN_ASSIGN = EL3B` |

**Critical Constraint**: All electrodes are AC-coupled, so **DC lead-off detection is NOT available**. Only AC-based detection mechanisms can be used.

---

## Available Detection Mechanisms

### 1. DRV_OOR (Drive Out-of-Range) - STATUS_2 Bit 4

**Register**: `DC_LEADS_CONFIGURATION (0x50)`, Bit 4: `EN_DRV_OOR`

**How it works**:
- Monitors DRVN node voltage during drive operation
- Valid range: 0.27V to (AVDD - 0.35V)
- When drive current path is broken, DRVN swings toward rails
- Hardware debounce: ~128ms (built into MAX30009)

**Detection capability**:
| Condition | DRV_OOR Asserts? |
|-----------|------------------|
| I+ (DRVP) disconnected | **YES** - DRVN swings to rails |
| I- (DRVN) disconnected | **Maybe** - Less consistent |
| Both connected | NO - Normal operation |

### 2. BIOZ_OVER (AC Lead-Off Over Threshold) - STATUS_2 Bit 6

**Registers**:
- `BIOZ_CONFIGURATION_2 (0x21)`, Bit 0: `EN_BIOZ_THRESH`
- `BIOZ_HIGH_THRESHOLD (0x27)`: 8-bit threshold (0-255)

**How it works**:
- Monitors demodulated BioZ signal magnitude
- When electrode disconnects, large artifact signals appear
- Signal exceeds high threshold → BIOZ_OVER asserts

**Detection capability**:
| Condition | BIOZ_OVER Asserts? |
|-----------|-------------------|
| I+ (DRVP) disconnected | **YES** - Large artifacts |
| I- (DRVN) disconnected | **YES** - Signal saturates |
| Both connected | NO - Signal within threshold |

### 3. BIOZ_UNDER (AC Lead-Off Under Threshold) - STATUS_2 Bit 5

**Register**: `BIOZ_LOW_THRESHOLD (0x26)`: 8-bit threshold (0-255)

**How it works**:
- Monitors for abnormally low signal (open circuit with no artifacts)
- Less useful for drive electrodes (disconnection causes large signals, not small)

---

## Detection Strategy

### Combined Detection Logic

Since neither mechanism alone reliably detects both I+ and I- disconnection, use **combined detection**:

```
Drive Lead Status = (DRV_OOR == 1) OR (BIOZ_OVER == 1)
```

| I+ Status | I- Status | DRV_OOR | BIOZ_OVER | Detection Result |
|-----------|-----------|---------|-----------|------------------|
| Connected | Connected | 0 | 0 | **LEADS ON** |
| **OFF** | Connected | 1 | 1 | **LEAD OFF** (I+ detected via DRV_OOR) |
| Connected | **OFF** | 0/1 | 1 | **LEAD OFF** (I- detected via BIOZ_OVER) |
| **OFF** | **OFF** | 1 | 1 | **LEADS OFF** |

### Distinguishing I+ vs I- Disconnection

- **DRV_OOR = 1, BIOZ_OVER = 1**: Likely **I+ (DRVP) disconnected**
- **DRV_OOR = 0, BIOZ_OVER = 1**: Likely **I- (DRVN) disconnected**
- **DRV_OOR = 1, BIOZ_OVER = 0**: Unlikely (edge case, treat as I+ off)

---

## Implementation Plan

### Files to Modify

| File | Changes |
|------|---------|
| [MAX30009_process.h](SPI_DEV_servise/include/MAX30009_process.h) | Add lead status tracking, state enum |
| [MAX30009_process.cpp](SPI_DEV_servise/src/MAX30009_process.cpp) | Implement detection logic, messages, JSON |

### Phase 1: Add Data Structures

**File**: `MAX30009_process.h`

```cpp
// Drive electrode lead status
typedef enum {
    DRIVE_LEAD_UNKNOWN = 0,     // Not yet determined
    DRIVE_LEAD_ON,              // Both I+ and I- connected
    DRIVE_LEAD_I_PLUS_OFF,      // I+ (DRVP) disconnected
    DRIVE_LEAD_I_MINUS_OFF,     // I- (DRVN) disconnected
    DRIVE_LEAD_BOTH_OFF         // Both disconnected
} DRIVE_LEAD_STATUS_ENUM;

// Add to MAX30009_USER_SETTINGS:
bool enable_drive_leadoff;              // Enable I+/I- lead detection
uint8_t bioz_high_threshold;            // BIOZ_OVER threshold (default 200)

// Add to class private members:
DRIVE_LEAD_STATUS_ENUM _drive_lead_status = DRIVE_LEAD_UNKNOWN;
DRIVE_LEAD_STATUS_ENUM _drive_lead_status_prev = DRIVE_LEAD_UNKNOWN;
uint8_t _drive_leadoff_debounce_count = 0;
bool _drive_leadoff_active = false;
```

### Phase 2: Configure Detection Hardware

**File**: `MAX30009_process.cpp`

Add function `configure_drive_leadoff_detection()`:

```cpp
void MAX30009_process::configure_drive_leadoff_detection()
{
    if (!MAX30009_user_sett.enable_drive_leadoff) {
        MAX30009.set_DRV_OOR_detection_enable(false);
        MAX30009.set_BIOZ_threshold_detection_enable(false);
        std::cout << "LOD: Drive lead-off detection DISABLED" << std::endl;
        return;
    }

    // Enable DRV_OOR for I+ detection
    MAX30009.set_DRV_OOR_detection_enable(true);
    std::cout << "LOD: DRV_OOR detection ENABLED (monitors I+/DRVP)" << std::endl;

    // Enable BIOZ threshold for I+/I- detection
    MAX30009.set_BIOZ_threshold_detection_enable(true);
    MAX30009.set_BIOZ_high_threshold(MAX30009_user_sett.bioz_high_threshold);
    MAX30009.set_BIOZ_low_threshold(10);  // Low threshold for completeness
    std::cout << "LOD: BIOZ threshold detection ENABLED" << std::endl;
    std::cout << "LOD: BIOZ_HI_THRESH = " << (int)MAX30009_user_sett.bioz_high_threshold << std::endl;

    // Reset status
    _drive_lead_status = DRIVE_LEAD_UNKNOWN;
    _drive_lead_status_prev = DRIVE_LEAD_UNKNOWN;
    _drive_leadoff_debounce_count = 0;
    _drive_leadoff_active = true;
}
```

### Phase 3: Implement Status Reading with Debounce

**File**: `MAX30009_process.cpp`

Add function `read_drive_leadoff_status()`:

```cpp
void MAX30009_process::read_drive_leadoff_status()
{
    MAX30009_STATUS_STRUCT_TYPE status;
    if (!MAX30009.read_status(&status)) {
        return;  // Read failed
    }

    // Get raw flags
    bool drv_oor = status.DRVN_out_of_range;
    bool bioz_over = status.BIOZ_over_level;

    // Determine current lead status based on combined detection
    DRIVE_LEAD_STATUS_ENUM current_status;

    if (!drv_oor && !bioz_over) {
        // Both flags clear = leads connected
        current_status = DRIVE_LEAD_ON;
    } else if (drv_oor && bioz_over) {
        // Both flags set = likely I+ (DRVP) disconnected
        current_status = DRIVE_LEAD_I_PLUS_OFF;
    } else if (!drv_oor && bioz_over) {
        // Only BIOZ_OVER = likely I- (DRVN) disconnected
        current_status = DRIVE_LEAD_I_MINUS_OFF;
    } else {
        // DRV_OOR only (rare) = treat as I+ off
        current_status = DRIVE_LEAD_I_PLUS_OFF;
    }

    // Debounce: require 3 consecutive identical readings
    if (current_status == _drive_lead_status_prev) {
        _drive_leadoff_debounce_count++;
        if (_drive_leadoff_debounce_count >= LEADOFF_DEBOUNCE_COUNT) {
            if (current_status != _drive_lead_status) {
                // Status changed - print message
                print_drive_lead_status_change(_drive_lead_status, current_status);
                _drive_lead_status = current_status;
            }
            _drive_leadoff_debounce_count = 0;
        }
    } else {
        _drive_leadoff_debounce_count = 0;
    }
    _drive_lead_status_prev = current_status;
}
```

### Phase 4: Implement Status Change Messages

**File**: `MAX30009_process.cpp`

```cpp
void MAX30009_process::print_drive_lead_status_change(
    DRIVE_LEAD_STATUS_ENUM old_status,
    DRIVE_LEAD_STATUS_ENUM new_status)
{
    std::cout << std::endl;
    std::cout << "========================================" << std::endl;

    switch (new_status) {
        case DRIVE_LEAD_ON:
            std::cout << "LOD: I+ (DRVP) lead is ON" << std::endl;
            std::cout << "LOD: I- (DRVN) lead is ON" << std::endl;
            std::cout << "LOD: Drive electrode pair: CONNECTED" << std::endl;
            break;

        case DRIVE_LEAD_I_PLUS_OFF:
            std::cout << "LOD: I+ (DRVP) lead is OFF  <-- CHECK THIS ELECTRODE" << std::endl;
            std::cout << "LOD: I- (DRVN) lead status unknown" << std::endl;
            std::cout << "LOD: Drive electrode pair: DISCONNECTED" << std::endl;
            break;

        case DRIVE_LEAD_I_MINUS_OFF:
            std::cout << "LOD: I+ (DRVP) lead status unknown" << std::endl;
            std::cout << "LOD: I- (DRVN) lead is OFF  <-- CHECK THIS ELECTRODE" << std::endl;
            std::cout << "LOD: Drive electrode pair: DISCONNECTED" << std::endl;
            break;

        case DRIVE_LEAD_BOTH_OFF:
            std::cout << "LOD: I+ (DRVP) lead is OFF" << std::endl;
            std::cout << "LOD: I- (DRVN) lead is OFF" << std::endl;
            std::cout << "LOD: Drive electrode pair: BOTH DISCONNECTED" << std::endl;
            break;

        default:
            std::cout << "LOD: Drive lead status: UNKNOWN" << std::endl;
    }

    std::cout << "========================================" << std::endl;
    std::cout << std::endl;
}
```

### Phase 5: Integrate into Main Process Loop

**File**: `MAX30009_process.cpp`

Modify `process()` function:

```cpp
void MAX30009_process::process()
{
    // Drive lead-off detection - AUTO-ENABLED when measurement is active
    // Conditions: power on, 4-wire mode, not calibrating, measurement enabled
    bool should_detect = MAX30009_user_sett.enable_drive_leadoff &&
                         MAX30009_user_sett.power_enable &&
                         MAX30009_user_sett.measure_enable &&  // Auto-detect when measuring
                         MAX30009_user_sett.ext_MUX_state == MAX30009_EXT_MUX_4_WIRE &&
                         !_need_calibrate;

    if (should_detect)
    {
        _leadoff_check_counter++;
        if (_leadoff_check_counter >= LEADOFF_CHECK_INTERVAL) {
            _leadoff_check_counter = 0;
            read_drive_leadoff_status();
        }
        _drive_leadoff_active = true;
    }
    else if (_drive_leadoff_active)
    {
        // Conditions no longer met - reset status
        _drive_lead_status = DRIVE_LEAD_UNKNOWN;
        _drive_leadoff_active = false;
        if (!MAX30009_user_sett.measure_enable) {
            std::cout << "LOD: Drive lead detection paused (measurement stopped)" << std::endl;
        } else if (MAX30009_user_sett.ext_MUX_state != MAX30009_EXT_MUX_4_WIRE) {
            std::cout << "LOD: Drive lead detection paused (MUX not in 4-wire mode)" << std::endl;
        }
    }

    // ... rest of existing process() code ...
}
```

### Phase 6: Add JSON API

**File**: `MAX30009_process.cpp`

Add JSON settings parsing in `process_JSON_line()`:

```cpp
// In settings handler:
if (parsed_json.contains("enable_drive_leadoff")) {
    MAX30009_user_sett.enable_drive_leadoff = parsed_json["enable_drive_leadoff"];
}
if (parsed_json.contains("bioz_high_threshold")) {
    MAX30009_user_sett.bioz_high_threshold = parsed_json["bioz_high_threshold"];
}
```

Add `get_drive_leadoff_status_as_json()`:

```cpp
std::string MAX30009_process::get_drive_leadoff_status_as_json()
{
    nlohmann::json response;
    response["type"] = "drive_leadoff_status";
    response["timestamp"] = get_timestamp_string();
    response["enabled"] = MAX30009_user_sett.enable_drive_leadoff;
    response["mux_state"] = MAX30009_user_sett.ext_MUX_state;

    // Read current raw status
    MAX30009_STATUS_STRUCT_TYPE status;
    MAX30009.read_status(&status);

    response["raw_flags"]["drv_oor"] = status.DRVN_out_of_range;
    response["raw_flags"]["bioz_over"] = status.BIOZ_over_level;
    response["raw_flags"]["bioz_under"] = status.BIOZ_under_level;

    // Interpreted status
    std::string status_str;
    switch (_drive_lead_status) {
        case DRIVE_LEAD_ON:         status_str = "leads_on"; break;
        case DRIVE_LEAD_I_PLUS_OFF: status_str = "i_plus_off"; break;
        case DRIVE_LEAD_I_MINUS_OFF: status_str = "i_minus_off"; break;
        case DRIVE_LEAD_BOTH_OFF:   status_str = "both_off"; break;
        default:                    status_str = "unknown"; break;
    }
    response["drive_status"] = status_str;

    response["electrodes"]["i_plus_drvp"] =
        (_drive_lead_status == DRIVE_LEAD_ON) ? "connected" :
        (_drive_lead_status == DRIVE_LEAD_I_PLUS_OFF || _drive_lead_status == DRIVE_LEAD_BOTH_OFF) ? "disconnected" : "unknown";

    response["electrodes"]["i_minus_drvn"] =
        (_drive_lead_status == DRIVE_LEAD_ON) ? "connected" :
        (_drive_lead_status == DRIVE_LEAD_I_MINUS_OFF || _drive_lead_status == DRIVE_LEAD_BOTH_OFF) ? "disconnected" : "unknown";

    response["alarm"] = (_drive_lead_status != DRIVE_LEAD_ON && _drive_lead_status != DRIVE_LEAD_UNKNOWN);

    return response.dump();
}
```

Add JSON command handler:

```cpp
if (command_type == "get_drive_leadoff_status") {
    return get_drive_leadoff_status_as_json();
}
```

### Phase 7: Set Defaults and Auto-Enable

**File**: `MAX30009_process.cpp`

In `init()`:

```cpp
// Drive lead-off detection defaults
MAX30009_user_sett.enable_drive_leadoff = true;   // Auto-enabled by default
MAX30009_user_sett.bioz_high_threshold = 200;     // Conservative threshold
```

**Auto-enable behavior**: Drive lead-off detection is automatically enabled when `measure_enable` is set to true. This ensures electrode connection is always monitored during active measurements without requiring explicit configuration.

---

## Register Configuration Summary

| Register | Address | Bits | Value | Purpose |
|----------|---------|------|-------|---------|
| DC_LEADS_CONFIGURATION | 0x50 | Bit 4 (EN_DRV_OOR) | 1 | Enable DRV out-of-range |
| BIOZ_CONFIGURATION_2 | 0x21 | Bit 0 (EN_BIOZ_THRESH) | 1 | Enable BIOZ threshold |
| BIOZ_HIGH_THRESHOLD | 0x27 | [7:0] | 200 | Over threshold (adjust as needed) |
| BIOZ_LOW_THRESHOLD | 0x26 | [7:0] | 10 | Under threshold |

---

## Testing Plan

### 1. Enable Detection
```bash
echo '{"type": "settings", "ext_MUX_state": 1, "power_enable": true, "measure_enable": true, "enable_drive_leadoff": true, "bioz_high_threshold": 200}' | nc localhost 30009
```

### 2. Query Status
```bash
echo '{"type": "get_drive_leadoff_status"}' | nc localhost 30009
```

### 3. Test Scenarios

| Test | Action | Expected Output |
|------|--------|-----------------|
| All connected | Connect all 4 electrodes | `"drive_status": "leads_on"` |
| I+ off | Disconnect I+ electrode | `"drive_status": "i_plus_off"`, message printed |
| I- off | Disconnect I- electrode | `"drive_status": "i_minus_off"`, message printed |
| Both off | Disconnect both I+/I- | `"drive_status": "both_off"` or `"i_plus_off"` |
| Reconnect | Reconnect electrodes | `"drive_status": "leads_on"`, message printed |

### 4. Monitor Console Output

When lead status changes, expect messages like:
```
========================================
LOD: I+ (DRVP) lead is OFF  <-- CHECK THIS ELECTRODE
LOD: I- (DRVN) lead status unknown
LOD: Drive electrode pair: DISCONNECTED
========================================
```

---

## Threshold Tuning

The `bioz_high_threshold` may need adjustment based on:
- Stimulation current setting (higher current = larger signals)
- Stimulation frequency
- Expected impedance range

**Recommended starting values**:
| Current Setting | Suggested Threshold |
|-----------------|---------------------|
| 64µA | 180 |
| 128µA | 190 |
| 256µA | 200 |
| 640µA | 210 |
| 1.28mA | 220 |

---

## Summary

This implementation uses **DRV_OOR + BIOZ_OVER** combined detection to reliably detect I+ and I- electrode disconnection in an AC-coupled system where DC lead-off is unavailable.

- **DRV_OOR** primarily detects I+ (DRVP) disconnection
- **BIOZ_OVER** detects both I+ and I- disconnection
- Combined logic distinguishes which electrode is likely disconnected
- Software debounce (3 reads @ 500ms interval) prevents false alarms
- Messages clearly identify the specific electrode that needs attention
