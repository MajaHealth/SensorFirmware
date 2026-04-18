# MAX30009 Passive Lead Monitoring Plan

## Summary

This implementation keeps passive lead monitoring active only during final ICG measurement. It preserves the existing measurement/calibration flow, keeps `get_data` unchanged, and keeps `get_lead_status` as a cached-status API that does not read or clear MAX30009 status registers.

Hardware assumptions:

| Function | Electrode | Board path | Passive detection |
|---|---:|---|---|
| DRVP | EL1 | 200 nF series capacitor in electrode lead path | Drive compliance plus AC BioZ threshold |
| BIP | EL2B | 39 kOhm series resistor, no series capacitor | DC lead-off, individually detectable |
| BIN | EL3B | 39 kOhm series resistor, no series capacitor | DC lead-off, individually detectable |
| DRVN | EL4 | 200 nF series capacitor in electrode lead path | Drive compliance plus AC BioZ threshold |

`BIOZ_EXT_CAP` is intentionally kept false by firmware using `set_ext_capacitor_state(false)`.

## Register And Status Handling

The MAX30009 `Status 2 (0x01)` bits, including `DRV_OOR`, clear when `Status 2` is read. The firmware therefore keeps one owner of status reads:

- `MAX30009_process::process()` calls `MAX30009.read_status(&status)` on a fixed polling interval.
- `update_passive_lead_monitor()` debounces and caches the latest status evidence.
- `get_lead_status` only serializes the cached state; it performs no live register reads.
- `get_data` is unchanged and is not the authoritative lead-monitor API.

The poll period is `100 ms`. `LOFF_RAPID` is enabled only when passive lead monitoring is enabled, so the hardware DC lead-off delay is bypassed and the firmware debounce controls the output state.

## Final Measurement Configuration

The final measurement configuration keeps the EL2B/EL3B sensitivity unchanged:

```text
EN_LON_DET      = 0
EN_LOFF_DET     = 1
EN_EXT_LOFF     = 0
EN_DRV_OOR      = 1
LOFF_RAPID      = 1
LOFF_IPOL       = 0
LOFF_IMAG       = 0x04
LOFF_THRESH     = 0x03
EN_BIOZ_THRESH  = 1
BIOZ_CMP        = 0x02
BIOZ_LO_THRESH  = 0x08
BIOZ_HI_THRESH  = 0xF8
BIOZ_EXT_CAP    = 0
BIOZ_DC_RESTORE = 1
RBIAS_VALUE     = 0x00
EN_RBIAS_BIP    = 1
EN_RBIAS_BIN    = 1
```

`DRV_OOR` alone is treated as drive compliance evidence, not proof that EL1 or EL4 is disconnected. This avoids a constant EL1/EL4 alarm on hardware where impedance measurement is still plausible while `DRV_OOR` is asserted.

Drive-path lead-off is promoted only when AC threshold evidence is also present:

```text
drive_path_fault = ac_threshold_fault && (!sense_fault || drv_oor)
drive_compliance_warning = drv_oor && !drive_path_fault
any_lead_off = el2b_bip_off || el3b_bin_off || drive_path_fault
```

## get_lead_status Response

The normal runtime response is intentionally compact:

```json
{
  "type": "lead_status",
  "active": true,
  "timestamp": "2026-04-18 12:00:00.000",
  "any_lead_off": false,
  "measurement_valid": true,
  "reported_fault_mask": 0,
  "disconnected_mask": 0,
  "possible_disconnected_mask": 0,
  "el2b_bip_off": false,
  "el3b_bin_off": false,
  "drive_path_fault": false,
  "drive_compliance_warning": false,
  "drv_oor": false,
  "ac_threshold_fault": false,
  "loff_rapid": true
}
```

Removed from the normal response:

- Full register dumps
- Full config dump
- Nested raw/derived objects
- Confidence/classification strings

Mask bits:

```text
0x01 EL1/DRVP
0x02 EL2B/BIP
0x04 EL3B/BIN
0x08 EL4/DRVN
```

`disconnected_mask` reports definite individual sense-lead failures only. `possible_disconnected_mask` includes `0x09` only when EL1/EL4 drive-path fault evidence is actionable.

## Build And Test

On the RPi:

```bash
cd ~/SensorFirmware/SPI_DEV_servise
gcc -c WS281x/*.c -IWS281x
g++ -std=c++17 -O2 -Wall -fexceptions main.cpp src/*.cpp *.o -Iinclude -Ihard_driver -IVTK -IMAX30009_LIB -IADS1293_LIB -IWS281x -lgpiod -lfltk -o bin/Release/SPI_DEV_servise
sudo ./bin/Release/SPI_DEV_servise
```

Start ICG:

```bash
nc 127.0.0.1 30009
```

Send:

```json
{"type":"settings","input_HP_filter":"BYPASS","measure_enable":true,"measure_frequency":500,"out_HP_filter":"BYPASS","out_LP_filter":"BYPASS","stimulate_current":"1.28mA","stimulate_frequency":20000}
```

After `start_measuring`, query:

```json
{"type":"get_lead_status"}
```

Expected checks:

- Response is compact, with no register/config/classification dump.
- `loff_rapid` is `true` during active passive monitoring.
- `measurement_valid` is only `true` while the monitor is active and no lead/compliance warning is present.
- If only `DRV_OOR` is asserted, expect `drv_oor=true`, `drive_compliance_warning=true`, `drive_path_fault=false`, and `any_lead_off=false`.
- Disconnect EL2B: expect `el2b_bip_off=true` and `disconnected_mask` includes `0x02`.
- Disconnect EL3B: expect `el3b_bin_off=true` and `disconnected_mask` includes `0x04`.
- Disconnect EL1 or EL4: expect `drv_oor=true`; `drive_path_fault` only becomes true if AC threshold evidence also appears.
- Reconnect leads: expect debounced fields to clear after the poll/debounce delay.
