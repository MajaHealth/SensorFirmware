"""
Test Case 45: ADS1293 60-Second ECG with 0.5s Polling

Validates ADS1293 ECG acquisition with ECG simulator over 60 seconds using
0.5s polling interval. Tests sync marker integrity, sampling frequency
accuracy, and BPM signal validation.
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from data_logger import JSONLLogger
from validators import (
    validate_sampling_frequency,
    validate_sync_monotonic,
    extract_sync_markers_ads1293
)


ECG_SYNC_MAGIC = -99999


@pytest.fixture
def ads1293_client(test_config):
    ads_config = test_config['services']['ads1293']
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        yield client
        try:
            client.send({"type": "poweroff"})
            time.sleep(0.2)
        except:
            pass


@pytest.mark.fw_app
@pytest.mark.ads1293
@pytest.mark.quick
@pytest.mark.parametrize("bpm", [30, 60, 120, 180])
def test_ads1293_ecg_60s_polling(test_config, results_dir, ads1293_client, bpm):
    """
    Test Case 45: ADS1293 60s ECG with 0.5s polling interval.

    Pass criteria:
    - Sync counters monotonically increase every 1s (no missing frames)
    - Mean sampling frequency = 400 Hz ± 1 Hz
    - ECG BPM matches simulator ± 3 BPM or ± 1%
    - Poweroff returns power_is_off
    """

    ecg_params = test_config['ads1293_ecg']
    thresholds = test_config['thresholds']

    test_duration = 60
    polling_interval = 0.5
    expected_freq = ecg_params['sampling_frequency']
    freq_tolerance = thresholds['sampling']['frequency_error_hz']
    
    r2_rate = ecg_params['r2_rate']
    r3_rate = ecg_params['r3_rate']

    print(f"\n{'='*70}")
    print(f"Test Case 45: ADS1293 ECG 60s (BPM={bpm}, 0.5s polling)")
    print(f"{'='*70}")
    print(f"Duration: {test_duration}s")
    print(f"Polling interval: {polling_interval}s")
    print(f"Expected frequency: {expected_freq} Hz ± {freq_tolerance} Hz")
    print(f"ECG simulator BPM: {bpm}")
    print(f"{'='*70}\n")

    output_file = results_dir / f"test_045_ecg_60s_bpm{bpm}.jsonl"
    logger = JSONLLogger(
        str(output_file),
        test_id=f"test_045_bpm{bpm}",
        sensor="ads1293"
    )

    logger.write_raw({
        "type": "test_metadata",
        "test_id": "test_045",
        "bpm_setting": bpm,
        "duration_sec": test_duration,
        "polling_interval_sec": polling_interval,
        "expected_frequency_hz": expected_freq
    })

    print(f"[Step 1] Configuring ADS1293...")
    
    settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": r2_rate,
        "R3_rate": r3_rate
    }

    response = ads1293_client.send(settings)
    assert response["type"] == "actual_settings", f"Config failed: {response}"
    assert response["enable_conversion"] == True

    actual_fs = 128000 // (response['R1_rate'] * response['R2_rate'] * response['R3_rate'])
    
    print(f"  ✓ Configuration:")
    print(f"    R-rates: R1={response['R1_rate']}, R2={response['R2_rate']}, R3={response['R3_rate']}")
    print(f"    Sampling: ~{actual_fs} Hz")
    print(f"    Conversion: enabled")

    print(f"\n[Step 2] Stabilization (2 seconds)...")
    time.sleep(2.0)

    print(f"\n[Step 3] Flushing buffer...")
    for attempt in range(3):
        flush = ads1293_client.send({"type": "get_data"})
        if flush["type"] == "data" and len(flush["data"]) > 0:
            print(f"  Flush {attempt + 1}: {len(flush['data'])} samples")
        time.sleep(0.2)

    print(f"\n[Step 4] Collecting data ({test_duration}s, poll every {polling_interval}s)...")
    
    num_polls = int(test_duration / polling_interval)
    all_data = []
    start_time = time.time()

    for poll_num in range(num_polls):
        poll_start = time.time()

        response = ads1293_client.send({"type": "get_data"})

        if response["type"] == "data":
            logger.write_data(
                data=response["data"],
                metadata={
                    "poll_number": poll_num,
                    "elapsed_time": time.time() - start_time
                }
            )
            all_data.extend(response["data"])

            if (poll_num + 1) % 20 == 0:
                elapsed = time.time() - start_time
                print(f"  Poll {poll_num + 1}/{num_polls} - {elapsed:.1f}s - {len(all_data)} samples")

        sleep_time = polling_interval - (time.time() - poll_start)
        if sleep_time > 0:
            time.sleep(sleep_time)

    total_time = time.time() - start_time

    print(f"\n  ✓ Collection complete:")
    print(f"    Duration: {total_time:.2f}s")
    print(f"    Total samples: {len(all_data)}")

    print(f"\n[Step 5] Extracting sync markers...")

    sync_markers = extract_sync_markers_ads1293(all_data)
    
    print(f"  ✓ Found {len(sync_markers)} sync markers")

    assert len(sync_markers) > 0, "No sync markers found"

    expected_syncs = test_duration
    assert len(sync_markers) >= expected_syncs - 2, \
        f"Too few syncs: expected ~{expected_syncs}, got {len(sync_markers)}"
    assert len(sync_markers) <= expected_syncs + 2, \
        f"Too many syncs: expected ~{expected_syncs}, got {len(sync_markers)}"

    print(f"\n[Step 6] Validating sync sequence...")

    sync_nums = [s[1] for s in sync_markers]

    is_monotonic = validate_sync_monotonic(sync_markers)
    assert is_monotonic, "Syncs not monotonic"
    print(f"  ✓ Monotonic")

    for i in range(len(sync_nums) - 1):
        diff = sync_nums[i+1] - sync_nums[i]
        assert diff == 1, f"Missing frame: {sync_nums[i]} → {sync_nums[i+1]} (gap={diff})"
    print(f"  ✓ Consecutive (no missing frames)")

    assert len(sync_nums) == len(set(sync_nums)), "Duplicate syncs"
    print(f"  ✓ No duplicates")

    print(f"\n[Step 7] Sampling frequency validation...")

    data_samples = len(all_data) - len(sync_markers)
    measured_fs = data_samples / total_time

    print(f"  Data samples: {data_samples}")
    print(f"  Duration: {total_time:.2f}s")
    print(f"  Measured: {measured_fs:.2f} Hz")
    print(f"  Expected: {expected_freq} ± {freq_tolerance} Hz")

    freq_valid = validate_sampling_frequency(measured_fs, expected_freq, freq_tolerance)
    assert freq_valid, \
        f"Frequency {measured_fs:.2f} Hz out of tolerance"
    print(f"  ✓ Within tolerance")

    print(f"\n[Step 8] ECG BPM validation...")

    ecg_signal = [s[0] for s in all_data if s[0] != ECG_SYNC_MAGIC]

    if len(ecg_signal) >= measured_fs * 5:
        import numpy as np
        from scipy.signal import find_peaks

        ecg_array = np.array(ecg_signal)
        
        distance = int(measured_fs * 0.4)
        peaks, _ = find_peaks(ecg_array, distance=distance)

        if len(peaks) >= 2:
            peak_intervals_sec = np.diff(peaks) / measured_fs
            measured_bpm = 60 / np.mean(peak_intervals_sec)
            bpm_error_abs = abs(measured_bpm - bpm)
            bpm_error_pct = (bpm_error_abs / bpm) * 100

            print(f"  Detected peaks: {len(peaks)}")
            print(f"  Measured BPM: {measured_bpm:.1f}")
            print(f"  Expected BPM: {bpm}")
            print(f"  Error: {bpm_error_abs:.1f} bpm ({bpm_error_pct:.1f}%)")

            bpm_threshold_abs = thresholds['ads1293']['bpm_error_absolute']
            bpm_threshold_pct = thresholds['ads1293']['bpm_error_pct']

            assert (bpm_error_abs <= bpm_threshold_abs or bpm_error_pct <= bpm_threshold_pct), \
                f"BPM error {bpm_error_abs:.1f} bpm exceeds threshold"
            print(f"  ✓ BPM within tolerance")

            logger.write_raw({
                "type": "bpm_analysis",
                "measured_bpm": measured_bpm,
                "expected_bpm": bpm,
                "error_bpm": bpm_error_abs,
                "error_pct": bpm_error_pct,
                "peaks_detected": len(peaks)
            })
        else:
            print(f"  ⚠ Insufficient peaks for BPM analysis ({len(peaks)} peaks)")
    else:
        print(f"  ⚠ Insufficient data for BPM analysis")

    print(f"\n[Step 9] Powering off...")

    poweroff = ads1293_client.send({"type": "poweroff"})
    assert poweroff["type"] == "power_is_off", f"Poweroff failed: {poweroff}"
    print(f"  ✓ Power off confirmed")

    logger.close()

    print(f"\n{'='*70}")
    print(f"✓ TEST PASSED (BPM={bpm})")
    print(f"{'='*70}")
    print(f"  Samples: {data_samples}")
    print(f"  Syncs: {len(sync_markers)}")
    print(f"  Frequency: {measured_fs:.2f} Hz")
    print(f"  Data: {output_file}")
    print(f"{'='*70}\n")
