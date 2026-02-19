# MAX30009 Lead-Off Detection (LOD) Bug Documentation

## Bug Summary

The LOD Z value does not match the Z value from `get_data` due to incorrect calibration coefficient lookup.

## Root Cause

`MAX30009_user_sett.stimulate_frequency` stores a **frequency INDEX** (0-16), not an actual frequency value.

### Frequency Index Mapping (FREQ_POINTS array)

| Index | Frequency |
|-------|-----------|
| 0     | 25 Hz     |
| 1     | 100 Hz    |
| 2     | 200 Hz    |
| 3     | 500 Hz    |
| 4     | 1 kHz     |
| 5     | 5 kHz     |
| 6     | 10 kHz    |
| 7     | 20 kHz    |
| 8     | 50 kHz    |
| 9     | 100 kHz   |
| 10    | 150 kHz   |
| 11    | 200 kHz   |
| 12    | 250 kHz   |
| 13    | 300 kHz   |
| 14    | 350 kHz   |
| 15    | 400 kHz   |
| 16    | 450 kHz   |

## The Bug

**Location:** `SPI_DEV_servise/src/MAX30009_process.cpp`, lines 1104-1111 in `read_drive_leadoff_status()`

### Buggy Code:
```cpp
// Get calibration coefficients
uint32_t freq_idx = 0;
for (uint32_t i = 0; i < FREQ_POINTS_COUNT; i++) {
    if (FREQ_POINTS[i] == MAX30009_user_sett.stimulate_frequency) {  // BUG: treating index as value
        freq_idx = i;
        break;
    }
}
MAX30009_CALIB_DATA coef = _calibrate_data[MAX30009_user_sett.stimulate_current_select][freq_idx];
```

### Why It Fails:
- If `stimulate_frequency = 7` (meaning 20kHz index)
- The loop searches for value `7` in `FREQ_POINTS[] = {25, 100, 200, 500, ...}`
- Value `7` is never found in that array
- `freq_idx` stays at `0` (its initial value)
- Result: Uses **25Hz calibration coefficients** instead of **20kHz coefficients**

### Correct Code (from get_data path, line 842):
```cpp
MAX30009_CALIB_DATA_TYPE calibrate_koef = _calibrate_data[MAX30009_user_sett.stimulate_current_select][MAX30009_user_sett.stimulate_frequency];
```
This correctly uses `stimulate_frequency` directly as the array index.

## The Fix

Replace the buggy lookup (lines 1104-1111) with:

```cpp
// Get calibration coefficients - stimulate_frequency IS the index
MAX30009_CALIB_DATA coef = _calibrate_data[MAX30009_user_sett.stimulate_current_select][MAX30009_user_sett.stimulate_frequency];
```

Or if you want to keep bounds checking:
```cpp
uint32_t freq_idx = MAX30009_user_sett.stimulate_frequency;
if (freq_idx >= FREQ_POINTS_COUNT) {
    freq_idx = 0;  // Fallback to lowest frequency
}
MAX30009_CALIB_DATA coef = _calibrate_data[MAX30009_user_sett.stimulate_current_select][freq_idx];
```

## Impact

- LOD impedance calculations are incorrect when using any frequency other than 25Hz
- The mismatch causes incorrect lead-off detection thresholds
- Affects all users of `enable_drive_leadoff` feature

## Verification

After fix, verify by:
1. Set a non-zero frequency index: `{"type": "settings", "stimulate_frequency": 7, ...}`
2. Compare LOD Z output with `get_data` response
3. Values should now match (within measurement noise)

## Files Affected

- `SPI_DEV_servise/src/MAX30009_process.cpp`:
  - `check_drive_leadoff()` function - periodic LOD check
  - `get_drive_leadoff_status_as_json()` function - JSON status query (had same bugs)

---

# Current Implementation: Single Sample for Immediate Detection

## Design Decision

LOD uses **1 single sample** for immediate transient detection:

```cpp
uint32_t latest_pos = (_IFIFO_write_pos - 1) % _max_IFIFO_size;
int32_t I_val = _IFIFO_BUF[latest_pos].I_data;  // 1 sample
int32_t Q_val = _IFIFO_BUF[latest_pos].Q_data;
```

**Rationale:**
- Electrode disconnection causes an immediate Z spike
- Averaging (even 4 samples) can dilute/mask the transient
- Original working implementation used 1 sample
- 3-sample debouncing handles false positives from noise

## Calibration Fix Applied

The calibration lookup was fixed to use `stimulate_frequency` directly as array index:

```cpp
// FIXED: Use stimulate_frequency directly as index (same as get_data path)
MAX30009_CALIB_DATA coef = _calibrate_data[MAX30009_user_sett.stimulate_current_select][MAX30009_user_sett.stimulate_frequency];
```

## Why Not Average More Samples?

Testing showed:
- **32 samples**: Too much averaging, masked electrode disconnect transients
- **4 samples**: Still could mask quick transients
- **1 sample + debounce**: Catches transients immediately, debounce filters noise

## Trade-offs

| Approach | Pro | Con |
|----------|-----|-----|
| 1 sample | Immediate detection | Noisier (but debounced) |
| N samples | Smoother | May mask disconnect transients |

**Current choice:** 1 sample with 3-sample debounce for best transient detection

---

# Current Select Index Mapping

| Index | Current |
|-------|---------|
| 0     | 64 µA   |
| 1     | 128 µA  |
| 2     | 256 µA  |
| 3     | 640 µA  |
| 4     | 1.28 mA |

---

# DRVN Detection Limitation

## Problem: Z Threshold May Not Detect DRVN Disconnection

In tetrapolar bioimpedance measurement:
```
DRVP (I+) ──→ [BODY] ──→ DRVN (I-)
              ↑   ↑
           BIP(V+) BIN(V-)
```

**If DRVN is disconnected:**
- Current source at DRVP still tries to push current
- With AC coupling and body capacitance, current finds **parasitic return paths**
- BIP and BIN still measure a voltage (they're still connected)
- **Z might look plausible** - not obviously "open circuit"

**Contrast with DRVP disconnected:**
- Current source output is floating
- No current flows at all
- Z goes very high → clearly detected

## Detection Difficulty by Electrode (Z Threshold Only)

| Electrode | Disconnection Effect | Z Threshold Detection |
|-----------|---------------------|----------------------|
| DRVP (I+) | Current source broken | ✓ Easy - Z very high |
| DRVN (I-) | Current finds parasitic paths | ✗ **Hard - Z may look normal** |
| BIP (V+)  | Diff sense partially broken | ~ Maybe |
| BIN (V-)  | Diff sense partially broken | ~ Maybe |

---

# Solution: DRV_OOR Hardware Detection

## How It Works

The MAX30009 has built-in **DRV_OOR** (Drive Out Of Range) detection that monitors the DRVN pin voltage internally.

From datasheet:
> "The MAX30009 BioZ channel can perform DRVN lead-off detection by monitoring the voltage of DRVN and triggering the BIOZ_DRV_OOR status bit when either the DRVP or DRVN lead is disconnected."

**Works with external caps** because it monitors the chip's internal DRVN pin voltage, not the electrode voltage directly.

## Already Implemented in Code

The DRV_OOR detection is already implemented and can be enabled via JSON.

### JSON Parameters Required

**TWO flags must be enabled:**
```json
{
  "enable_leadoff": true,     // Master switch - enables periodic status checking
  "enable_drv_oor": true      // Enables DRV_OOR hardware detection specifically
}
```

### Code Flow

1. **JSON Parsing** (`MAX30009_process.cpp:476-478`):
   ```cpp
   if (parsed_json.contains("enable_drv_oor")) {
       MAX30009_user_sett.enable_drv_oor_detection = parsed_json["enable_drv_oor"];
   }
   ```

2. **Hardware Configuration** (`configure_leadoff_detection()`, line 939-941):
   ```cpp
   if (MAX30009_user_sett.enable_drv_oor_detection) {
       MAX30009.set_DRV_OOR_detection_enable(true);  // Writes EN_DRV_OOR bit
   }
   ```

3. **Periodic Status Check** (`process()`, line 107-114):
   - Requires `enable_leadoff_detection` (master) to be true
   - Calls `read_leadoff_status()` every ~1 second

4. **Status Reading** (`read_leadoff_status()`, line 980-981):
   ```cpp
   if (MAX30009_user_sett.enable_drv_oor_detection) {
       bool raw_drv_oor = status.DRVN_out_of_range;  // Reads STATUS_2.DRV_OOR
   }
   ```

5. **Debouncing**: 3 consecutive reads required before status change

---

# Complete Detection Coverage

## Recommended: Use Both Methods Together

| Method | JSON Flags | Detects | How |
|--------|------------|---------|-----|
| **DRV_OOR** (hardware) | `enable_leadoff` + `enable_drv_oor` | DRVP, DRVN | Monitors DRVN pin voltage |
| **Z threshold** (software) | `enable_drive_leadoff` | All 4 electrodes | Compares impedance to threshold |

## Per-Electrode Detection

| Electrode | Z Threshold | DRV_OOR | Combined |
|-----------|-------------|---------|----------|
| DRVP (I+) | ✓ | ✓ | ✓✓ |
| DRVN (I-) | ? (may miss) | ✓ | ✓ |
| BIP (V+)  | ✓ | ✗ | ✓ |
| BIN (V-)  | ✓ | ✗ | ✓ |

---

# Recommended Full Command

Enable all detection methods for comprehensive coverage:

```bash
echo '{"type": "settings", "ext_MUX_state": 1, "power_enable": true, "measure_enable": true, "measure_frequency": 400, "stimulate_frequency": 7, "stimulate_current_select": 4, "enable_leadoff": true, "enable_drv_oor": true, "enable_drive_leadoff": true, "leadoff_threshold_ohms": 500}' | nc localhost 30009
```

### Parameters Explained

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `ext_MUX_state` | 1 | 4-wire mode |
| `power_enable` | true | Power on MAX30009 |
| `measure_enable` | true | Enable measurement |
| `measure_frequency` | 400 | 400 Hz output data rate |
| `stimulate_frequency` | 7 | Index 7 = 20 kHz |
| `stimulate_current_select` | 4 | Index 4 = 1.28 mA |
| `enable_leadoff` | true | Master switch for hardware LOD |
| `enable_drv_oor` | true | Enable DRV_OOR for DRVP/DRVN |
| `enable_drive_leadoff` | true | Enable Z threshold detection |
| `leadoff_threshold_ohms` | 500 | Disconnect if Z > 500Ω |

### Check Status

```bash
# Hardware LOD status (DRV_OOR, BIOZ thresholds)
echo '{"type": "get_leadoff_status"}' | nc localhost 30009

# Software Z threshold status
echo '{"type": "get_drive_leadoff_status"}' | nc localhost 30009
```

---

# Single Electrode Detection Limitations

## Known Limitation

Single electrode disconnection (only I+, only I-, only V+, or only V-) may NOT be reliably detected in all cases. Detection works best when:
- Both electrodes on one side disconnect (I+/V+ or I-/V-)
- All electrodes disconnect

## Why This Is A Hardware Limitation

**Tetrapolar measurement architecture:**
```
DRVP (I+) ──current──→ [BODY] ──current──→ DRVN (I-)
                         ↑   ↑
                      BIP(V+) BIN(V-)
```

| Electrode | Effect When Disconnected | Detection |
|-----------|-------------------------|-----------|
| I+ only | Current source floating | DRV_OOR may detect, Z unpredictable |
| I- only | Return path broken | DRV_OOR should detect |
| V+ only | One diff input floating | Z may look normal (current still flows) |
| V- only | One diff input floating | Z may look normal (current still flows) |

## Why Not Use Signal Variance Detection?

**Considered but rejected:** Variance-based detection was explored to detect single-electrode disconnection by monitoring signal stability.

**Problem:** In bioimpedance monitoring, signal variance is often the SIGNAL OF INTEREST:
- Respiration causes impedance variance (chest expansion)
- Cardiac cycle causes impedance variance (blood volume changes)
- Fluid shifts cause impedance changes (posture, hydration)

Using variance thresholds would cause **false alarms during normal physiological monitoring**.

## Recommendation

Use the datasheet-recommended detection methods:
1. **DRV_OOR** - Hardware detection for drive electrodes
2. **BIOZ_OVER/UNDER** - Hardware ADC thresholds
3. **Z threshold** - Software impedance comparison

Accept that single sense electrode (V+/V-) disconnection may not always be detected reliably with AC-coupled tetrapolar configuration.

---

# Summary of Issues and Fixes

| Issue | Status | Fix |
|-------|--------|-----|
| Wrong calibration lookup | ✅ FIXED | Use `stimulate_frequency` directly as index |
| Single sample | ✅ KEPT | 1 sample + 3-sample debounce for immediate transient detection |
| DRVN not detected | ✅ DOCUMENTED | Enable DRV_OOR hardware detection |
| Single electrode detection | ⚠️ LIMITED | Hardware limitation - use all detection methods together |
| Low Z not detected (0.3Ω) | ✅ FIXED | Added `leadoff_low_threshold_ohms` (default 5Ω) |
| DRV_OOR false positives | ⚠️ AC-COUPLED LIMITATION | See section below |

**Note:** Run calibration first (`{"type":"start_calibrate"}`) before using LOD to ensure accurate Z values.

---

# DRV_OOR False Positives in AC-Coupled Mode

## Problem

DRV_OOR may show "DISCONNECTED" at normal impedance (e.g., 83Ω) when electrodes are connected.

## Root Cause (ADI Register Analysis)

From ADI MAX30009.h register definitions:
- `DC_LEADS_CONFIGURATION_REGISTER (0x50)` bit 4: `EN_DRV_OOR_MASK`
- `STATUS_2_REGISTER (0x01)` bit 4: `DRV_OOR_MASK`

DRV_OOR is a **DC-based detection** that monitors the internal DRVN pin voltage:
- Triggers when DRVN voltage is outside range (0.27V to AVDD-0.35V)
- Designed for DC-coupled electrode configurations

**In AC-coupled configurations** (with external coupling capacitors):
- AC coupling blocks the DC signals DRV_OOR relies on
- Chip monitors internal DRVN voltage, but electrode voltage is different
- Results in unreliable/false positive detection

## Recommendation

For **AC-coupled systems**, use:
1. **Software Z threshold** (`enable_drive_leadoff`) - Most reliable
2. **BIOZ_OVER/BIOZ_UNDER** (`enable_bioz_threshold`) - Monitors ADC output

**Disable DRV_OOR** (`enable_drv_oor: false`) to avoid false positives.

## Updated Command (AC-Coupled Systems)

```bash
echo '{"type": "settings", "ext_MUX_state": 1, "power_enable": true, "measure_enable": true, "measure_frequency": 400, "stimulate_frequency": 7, "stimulate_current": 4, "enable_drive_leadoff": true, "leadoff_threshold_ohms": 500, "leadoff_low_threshold_ohms": 5}' | nc localhost 30009
```

**Parameters:**
- `leadoff_threshold_ohms`: 500 - Above 500Ω = open circuit (disconnected)
- `leadoff_low_threshold_ohms`: 5 - Below 5Ω = short circuit (error)

---

# Dual Threshold Detection (NEW)

## Problem Solved

Previously, only HIGH impedance was detected as disconnection. LOW impedance (0.3Ω) was incorrectly shown as "CONNECTED".

## Implementation

```cpp
if (impedance > leadoff_threshold_ohms) {
    // Open circuit - electrode disconnected
    status = DRIVE_LEAD_OFF;
} else if (impedance < leadoff_low_threshold_ohms) {
    // Short circuit - electrode error
    status = DRIVE_LEAD_OFF;
} else {
    // Normal range - electrodes connected
    status = DRIVE_LEAD_ON;
}
```

## Normal Human Body Impedance

| Measurement | Typical Range |
|-------------|---------------|
| Body (chest-to-chest) | 50-150Ω |
| Body (finger-to-finger) | 100-500Ω |
| Short circuit (error) | < 5Ω |
| Open circuit (disconnected) | > 500Ω |

## JSON Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `leadoff_threshold_ohms` | 500 | HIGH threshold - above = open circuit |
| `leadoff_low_threshold_ohms` | 5 | LOW threshold - below = short circuit |
