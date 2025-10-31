#!/usr/bin/env python3
"""
Test sync marker detection with actual sample data from the server
"""

import json
from typing import List, Tuple

def extract_sync_marks(data_sets: List, device_type: str = 'ECG') -> List[Tuple[int, float]]:
    """Extract sync marks and their timestamps from data sets

    Args:
        data_sets: List of data sets with timestamps
        device_type: 'ECG' or 'ICG' to handle different formats

    Returns:
        List of tuples (sync_number, timestamp)
    """
    sync_marks = []

    # Different magic numbers for ECG vs ICG
    # ECG: -99999
    # ICG: -999990000 (scaled by 10000)
    ecg_magic = -99999
    icg_magic = -999990000

    for data_set in data_sets:
        timestamp = data_set['timestamp']
        data_array = data_set['data']

        for sample in data_array:
            # Data format is array/list of integers
            # ECG: [ch1, ch2, ch3] - 3 elements
            # ICG: [I, Q, mag, phase, ...] - 5 elements
            # Sync mark in ECG: [-99999, sync_num, 0]
            # Sync mark in ICG: [-999990000, sync_num*10000, 0, 0, 0]

            if isinstance(sample, (list, tuple)) and len(sample) > 0:
                first_val = sample[0]

                # Check for ECG sync mark
                if device_type == 'ECG' and first_val == ecg_magic:
                    if len(sample) >= 2:
                        sync_num = sample[1]
                        sync_marks.append((sync_num, timestamp))
                        print(f"  {device_type} sync found: sample={sample}, sync_num={sync_num}")

                # Check for ICG sync mark (scaled by 10000)
                elif device_type == 'ICG' and first_val == icg_magic:
                    if len(sample) >= 2:
                        # Sync number is also scaled by 10000, so divide it
                        sync_num = sample[1] // 10000
                        sync_marks.append((sync_num, timestamp))
                        print(f"  {device_type} sync found: sample={sample}, sync_num={sync_num}")

    return sync_marks


# Test with actual ECG data from your log
ecg_sample_data = {
    "data": [
        [4140579, 4100438, 2726201],
        [4140557, 4100412, 2729889],
        [4140574, 4100435, 2726294],
        [-99999, 231, 0],  # <-- Sync mark!
        [4140581, 4100413, 2729806],
        [4140575, 4100420, 2726357],
        [4140554, 4100404, 2729695],
        [4140560, 4100427, 2726517]
    ],
    "data_size": 8,
    "timestamp": "2025-10-27 06:12:58.842",
    "type": "data"
}

# Test with actual ICG data from your log
icg_sample_data = {
    "data": [
        [52379102, 66416645, -40836262, -379410, 0],
        [52296790, 65829100, -39981448, -373982, 0],
        [53083761, 67158060, -41137809, -377742, 0],
        [53085537, 67722240, -42050297, -383835, 0],
        [52431257, 66370836, -40694608, -378168, 0],
        [-999990000, 2310000, 0, 0, 0],  # <-- Sync mark!
        [53281094, 67541201, -41508299, -379201, 0],
        [53035382, 67593454, -41906124, -383141, 0]
    ],
    "data_frequency": 200,
    "data_size": 8,
    "timestamp": "2025-10-27 06:12:58.729",
    "type": "data"
}

print("="*80)
print("Testing Sync Marker Detection")
print("="*80)

# Test ECG
print("\n1. Testing ECG sync marker detection:")
print("-" * 40)
ecg_data_sets = [{'timestamp': 1234567890.0, 'data': ecg_sample_data['data']}]
ecg_syncs = extract_sync_marks(ecg_data_sets, device_type='ECG')
print(f"\nECG sync marks found: {len(ecg_syncs)}")
print(f"ECG syncs: {ecg_syncs}")
assert len(ecg_syncs) == 1, f"Expected 1 ECG sync mark, found {len(ecg_syncs)}"
assert ecg_syncs[0][0] == 231, f"Expected sync number 231, got {ecg_syncs[0][0]}"
print("✓ ECG test PASSED")

# Test ICG
print("\n2. Testing ICG sync marker detection:")
print("-" * 40)
icg_data_sets = [{'timestamp': 1234567890.0, 'data': icg_sample_data['data']}]
icg_syncs = extract_sync_marks(icg_data_sets, device_type='ICG')
print(f"\nICG sync marks found: {len(icg_syncs)}")
print(f"ICG syncs: {icg_syncs}")
assert len(icg_syncs) == 1, f"Expected 1 ICG sync mark, found {len(icg_syncs)}"
assert icg_syncs[0][0] == 231, f"Expected sync number 231, got {icg_syncs[0][0]}"
print("✓ ICG test PASSED")

# Test matching
print("\n3. Testing sync number matching:")
print("-" * 40)
if ecg_syncs and icg_syncs:
    ecg_sync_num = ecg_syncs[0][0]
    icg_sync_num = icg_syncs[0][0]
    print(f"ECG sync number: {ecg_sync_num}")
    print(f"ICG sync number: {icg_sync_num}")
    assert ecg_sync_num == icg_sync_num, f"Sync numbers don't match! ECG={ecg_sync_num}, ICG={icg_sync_num}"
    print("✓ Sync numbers MATCH!")

print("\n" + "="*80)
print("All tests PASSED! Sync marker detection is working correctly.")
print("="*80)
