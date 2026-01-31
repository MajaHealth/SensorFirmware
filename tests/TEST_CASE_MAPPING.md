# Test Case Mapping

Mapping between test case numbers and test file locations.

## Hardware-Firmware Integration Tests (TC-007 to TC-012)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-007 | `tests/hardware-integration/test_max30009_cole_cole.py` | MAX30009 Cole/Cole BCA automated integration | ✅ Implemented |
| TC-008 | `tests/hardware-integration/test_max30009_icg_resistor.py` | MAX30009 ICG with resistor loads (20Ω, 100Ω, 200Ω, 300Ω) | ✅ Implemented |
| TC-009 | `tests/hardware-integration/test_max30009_icg_long_duration.py` | MAX30009 ICG long-duration (1 hour, 100Ω) | ✅ Implemented |
| TC-010 | `tests/hardware-integration/test_ads1293_ecg.py` | ADS1293 ECG automated integration (60s) | ✅ Implemented |
| TC-011 | `tests/hardware-integration/test_ads1293_ecg_long.py` | ADS1293 ECG long-duration (1 hour) | ✅ Implemented |
| TC-012 | ❌ Not Implemented | ADS1293 + MAX30009 synchronized (1 hour, AC + Battery) | ⚠️ Pending |

## Hardware Component Tests (TC-013 to TC-020)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-013 | `tests/unit_tests/hw_component/test_013_emmc_integrity.py` | eMMC Integrity Baseline | ✅ Implemented |
| TC-014 | `tests/unit_tests/hw_component/test_014_emmc_endurance.py` | eMMC Endurance | ✅ Implemented |
| TC-015 | `tests/unit_tests/hw_component/test_015_emmc_io_latency.py` | eMMC I/O Latency Under Logging | ✅ Implemented |
| TC-016 | `tests/unit_tests/hw_component/test_016_emmc_integrity_post_stress.py` | eMMC Integrity Post-Stress | ✅ Implemented |
| TC-017 | `tests/unit_tests/hw_component/test_017_sdram_memtester.py` | SDRAM Memtester | ✅ Implemented |
| TC-018 | `tests/unit_tests/hw_component/test_018_sdram_memory_pressure.py` | SDRAM Memory Pressure | ✅ Implemented |
| TC-019 | `tests/unit_tests/hw_component/test_019_cpu_thermal_load.py` | CPU Thermal Load | ✅ Implemented |
| TC-020 | `tests/unit_tests/hw_component/test_020_full_concurrency.py` | Full Concurrency | ✅ Implemented |

## Firmware-Application Integration Tests (TC-021 to TC-051)

### MAX30009 API Tests (TC-021 to TC-029)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-021 | `tests/fw-app-integration/test_max30009_state_machine.py` | MAX30009 measurement settings and state machine | ✅ Implemented |
| TC-022 | `tests/fw-app-integration/test_max30009_invalid_params.py` | Invalid MAX30009 settings parameters | ✅ Implemented |
| TC-023 | `tests/fw-app-integration/test_max30009_get_data.py` | Poll MAX30009 get_data after start_measuring | ✅ Implemented |
| TC-024 | `tests/fw-app-integration/test_max30009_no_measure.py` | get_data when not measuring returns no_measure | ✅ Implemented |
| TC-025 | `tests/hardware-integration/test_max30009_build_base_table.py` | Start base-table build and observe calib_data | ✅ Implemented |
| TC-026 | ❌ Not Implemented | build_base_table during active measurement | ⚠️ TBD |
| TC-027 | `tests/fw-app-integration/test_max30009_poweroff.py` | Power off MAX30009 AFE | ✅ Implemented |
| TC-028 | `tests/fw-app-integration/test_max30009_get_data_after_poweroff.py` | get_data after poweroff returns no_measure | ✅ Implemented |
| TC-029 | `tests/hardware-integration/test_max30009_poweroff_reenable.py` | Repeat poweroff then re-enable measurement | ✅ Implemented |

### ADS1293 API Tests (TC-030 to TC-035)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-030 | `tests/fw-app-integration/test_ads1293_api.py` | Apply ADS1293 sampling settings and enable conversion | ✅ Implemented |
| TC-031 | `tests/fw-app-integration/test_ads1293_invalid_params.py` | Invalid ADS1293 rate parameters | ✅ Implemented |
| TC-032 | `tests/fw-app-integration/test_ads1293_sync_markers.py` | Poll ADS1293 get_data and verify sync marker | ✅ Implemented |
| TC-033 | `tests/fw-app-integration/test_ads1293_get_data_before_config.py` | get_data before configuration/conversion | ✅ Implemented |
| TC-034 | `tests/fw-app-integration/test_ads1293_api.py` | Power off ADS1293 AFE | ✅ Implemented |
| TC-035 | `tests/fw-app-integration/test_ads1293_repeat_poweroff.py` | Repeat poweroff then re-enable conversion | ✅ Implemented |

### Power Service API Tests (TC-036 to TC-040)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-036 | `tests/fw-app-integration/test_power_get_batt_info.py` | Read battery information object | ✅ Implemented |
| TC-037 | `tests/fw-app-integration/test_power_charge_disable.py` | Disable charging via JSON | ✅ Implemented |
| TC-038 | `tests/fw-app-integration/test_power_charge_enable.py` | Enable charging via JSON | ✅ Implemented |
| TC-039 | `tests/fw-app-integration/test_power_invalid_messages.py` | Malformed/unknown power-control message | ✅ Implemented |
| TC-040 | `tests/fw-app-integration/test_power_button_info.py` | Button_info telemetry increments hold_time | ✅ Implemented |

### Dual Sensor Sync Tests (TC-041 to TC-043)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-041 | `tests/fw-app-integration/test_sync_marker_formats.py` | Verify sync marker formats for ECG and ICG | ✅ Implemented |
| TC-042 | `tests/fw-app-integration/test_dual_sensor_sync.py` | Sync counters monotonically increase every 1s | ✅ Implemented |
| TC-043 | `tests/fw-app-integration/test_sync_temporal_alignment.py` | Common sync numbers align within 50ms threshold | ✅ Implemented |

### Long-Duration Integration Tests (TC-044 to TC-047)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-044 | `tests/hardware-integration/test_max30009_long_duration_400hz.py` | MAX30009 long-duration get_data at 0.5s polling (1 hour) | ✅ Implemented |
| TC-045 | `tests/fw-app-integration/test_ads1293_ecg_60s_polling.py` | ADS1293 60-second get_data at 0.5s polling | ✅ Implemented |
| TC-046 | `tests/fw-app-integration/test_ads1293_long_duration_1hr.py` | ADS1293 long-duration get_data at 0.5s polling (1 hour) | ✅ Implemented |
| TC-047 | `tests/fw-app-integration/test_dual_sensor_long_duration_1hr.py` | Simultaneous acquisition + sync integrity + drift (1 hour) | ✅ Implemented |

### Robustness Tests (TC-048 to TC-051)

| Test Case # | Test File | Description | Status |
|-------------|-----------|-------------|--------|
| TC-048 | `tests/fw-app-integration/test_reconnect_behavior.py` | Reconnect behavior during repeated connect/disconnect | ✅ Implemented |
| TC-049 | `tests/fw-app-integration/test_max30009_get_data_no_measurement.py` | get_data polling before measurement is started | ✅ Implemented |
| TC-050 | `tests/fw-app-integration/test_ads1293_get_data_after_poweroff.py` | ADS1293 get_data after poweroff | ✅ Implemented |
| TC-051 | `tests/fw-app-integration/test_corrupted_base_table_recovery.py` | Corrupted base_table.json recovery | ✅ Implemented |

---

## Summary Statistics

- **Total Test Cases:** 45 (TC-007 to TC-051)
- **Implemented:** 41 (91.1%)
- **Pending:** 4 (8.9%)

### By Category:
- **HW-FW Integration (TC-007 to TC-012):** 5/6 implemented (83.3%)
- **Hardware Component (TC-013 to TC-020):** 8/8 implemented (100%)
- **FW-APP Integration (TC-021 to TC-051):** 28/31 implemented (90.3%)

---

## Quick Reference: Run Tests by Category

```bash
# Hardware-Firmware Integration (TC-007 to TC-012)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/ -m hardware

# Hardware Component Tests (TC-013 to TC-020)
./scripts/run-tests-remote.sh $PI_IP tests/unit_tests/hw_component/

# FW-APP Integration - Quick Tests (TC-021 to TC-043)
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/ -m quick

# Long-Duration Tests (TC-044, TC-046, TC-047)
./scripts/run-tests-remote.sh $PI_IP -m long --timeout=0

# All implemented tests
./scripts/run-tests-remote.sh $PI_IP tests/
```

---

**Last Updated:** 2026-01-31
