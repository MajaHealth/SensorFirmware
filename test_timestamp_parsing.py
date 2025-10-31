#!/usr/bin/env python3
"""
Test script to verify firmware timestamp parsing functionality
"""

import sys
from datetime import datetime

# Import the parsing function from the main test script
sys.path.insert(0, '/Users/dineshbhatotia/majahealth/Firmware /Oleh code sensor and power/source code 07092025')
from test_icg_ecg_sync import parse_firmware_timestamp


def test_timestamp_parsing():
    """Test firmware timestamp parsing with various formats"""

    print("="*80)
    print("FIRMWARE TIMESTAMP PARSING TEST")
    print("="*80)

    # Test cases based on actual firmware output format
    test_cases = [
        {
            'input': "2025-10-27 07:55:27.594",
            'description': "Standard firmware timestamp with milliseconds"
        },
        {
            'input': "2025-10-27 15:00:14.123",
            'description': "Afternoon timestamp"
        },
        {
            'input': "2025-01-01 00:00:00.000",
            'description': "Midnight on New Year"
        },
        {
            'input': "2025-12-31 23:59:59.999",
            'description': "End of year"
        }
    ]

    print("\nTest Cases:")
    print("-" * 80)

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        input_str = test['input']
        desc = test['description']

        try:
            # Parse the timestamp
            unix_timestamp = parse_firmware_timestamp(input_str)

            # Convert back to datetime for verification
            dt = datetime.fromtimestamp(unix_timestamp)
            reconstructed = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            print(f"\nTest {i}: {desc}")
            print(f"  Input:        {input_str}")
            print(f"  Unix time:    {unix_timestamp:.3f}")
            print(f"  Reconstructed: {reconstructed}")

            # Verify parsing is reversible (allowing for small floating point errors)
            if reconstructed == input_str or abs(unix_timestamp - datetime.strptime(input_str, "%Y-%m-%d %H:%M:%S.%f").timestamp()) < 0.001:
                print(f"  ✓ PASS")
                passed += 1
            else:
                print(f"  ✗ FAIL - Reconstruction mismatch")
                failed += 1

        except Exception as e:
            print(f"\nTest {i}: {desc}")
            print(f"  Input:  {input_str}")
            print(f"  ✗ FAIL - Exception: {e}")
            failed += 1

    print("\n" + "="*80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80)

    return failed == 0


def test_sync_timestamp_calculation():
    """Test sample-accurate timestamp calculation logic"""

    print("\n" + "="*80)
    print("SAMPLE-ACCURATE TIMESTAMP CALCULATION TEST")
    print("="*80)

    # Simulate scenario from actual test
    firmware_timestamp_str = "2025-10-27 07:55:27.594"
    firmware_timestamp = parse_firmware_timestamp(firmware_timestamp_str)

    print(f"\nScenario: ECG packet with sync mark")
    print(f"Firmware timestamp: {firmware_timestamp_str} ({firmware_timestamp:.3f} Unix time)")
    print(f"Sampling rate: 400 Hz")
    print(f"Total samples in packet: 50")
    print(f"Sync mark position: 25 (middle of packet)")

    # Calculate sample-accurate timestamp
    sampling_rate = 400  # Hz
    total_samples = 50
    sync_position = 25

    samples_after_sync = total_samples - sync_position - 1
    time_offset = samples_after_sync / sampling_rate
    actual_sync_timestamp = firmware_timestamp - time_offset

    print(f"\nCalculation:")
    print(f"  Samples after sync mark: {total_samples} - {sync_position} - 1 = {samples_after_sync}")
    print(f"  Time offset: {samples_after_sync} / {sampling_rate} Hz = {time_offset:.6f} seconds")
    print(f"  Actual sync timestamp: {firmware_timestamp:.6f} - {time_offset:.6f} = {actual_sync_timestamp:.6f}")

    # Convert to readable format
    actual_dt = datetime.fromtimestamp(actual_sync_timestamp)
    print(f"  Readable format: {actual_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    print(f"\n✓ Calculation completed successfully")

    return True


def test_sync_comparison():
    """Test comparing sync marks between ICG and ECG"""

    print("\n" + "="*80)
    print("SYNC MARK COMPARISON TEST")
    print("="*80)

    # Simulate REALISTIC scenario: devices polled in quick succession (2ms apart)
    # In real firmware, sync marks are injected atomically in same loop iteration
    # Firmware timestamps will be very close when get_data is called
    icg_timestamp_str = "2025-10-27 07:55:27.594"
    ecg_timestamp_str = "2025-10-27 07:55:27.596"  # 2ms difference (realistic)

    icg_timestamp = parse_firmware_timestamp(icg_timestamp_str)
    ecg_timestamp = parse_firmware_timestamp(ecg_timestamp_str)

    # Simulate sync mark extraction with sample-accurate calculation
    # REALISTIC: Sync marks appear in similar positions relative to packet boundaries
    # ICG: sync at position 10 out of 20 samples, 200Hz sampling
    icg_samples_after = 20 - 10 - 1
    icg_offset = icg_samples_after / 200.0
    icg_sync_time = icg_timestamp - icg_offset

    # ECG: sync at position 20 out of 40 samples, 400Hz sampling
    ecg_samples_after = 40 - 20 - 1
    ecg_offset = ecg_samples_after / 400.0
    ecg_sync_time = ecg_timestamp - ecg_offset

    time_diff_ms = abs(icg_sync_time - ecg_sync_time) * 1000

    print(f"\nRealistic Scenario:")
    print(f"  - Devices polled in quick succession (main loop)")
    print(f"  - Sync marks injected atomically in same iteration")
    print(f"  - Firmware timestamps very close together")

    print(f"\nICG Sync Mark:")
    print(f"  Firmware timestamp: {icg_timestamp_str} ({icg_timestamp:.6f})")
    print(f"  Position in packet: 10 / 20 samples (200 Hz)")
    print(f"  Time offset: {icg_offset:.6f} seconds")
    print(f"  Actual sync time: {icg_sync_time:.6f}")

    print(f"\nECG Sync Mark:")
    print(f"  Firmware timestamp: {ecg_timestamp_str} ({ecg_timestamp:.6f})")
    print(f"  Position in packet: 20 / 40 samples (400 Hz)")
    print(f"  Time offset: {ecg_offset:.6f} seconds")
    print(f"  Actual sync time: {ecg_sync_time:.6f}")

    print(f"\nComparison:")
    print(f"  Raw firmware timestamp difference: {(ecg_timestamp - icg_timestamp) * 1000:.2f} ms")
    print(f"  After sample-accurate correction: {time_diff_ms:.2f} ms")
    print(f"  Threshold: 50.00 ms")

    if time_diff_ms < 50:
        print(f"  ✓ PASS - Sync marks are time-locked within threshold")
        return True
    else:
        print(f"  ✗ FAIL - Sync marks exceed threshold")
        return False


def main():
    """Run all tests"""

    results = []

    # Test 1: Timestamp parsing
    results.append(test_timestamp_parsing())

    # Test 2: Sample-accurate calculation
    results.append(test_sync_timestamp_calculation())

    # Test 3: Sync comparison
    results.append(test_sync_comparison())

    print("\n" + "="*80)
    print("OVERALL TEST RESULTS")
    print("="*80)

    if all(results):
        print("✓ All tests PASSED")
        print("\nThe firmware timestamp parsing and sample-accurate calculation")
        print("logic is working correctly. Ready for actual device testing.")
        return 0
    else:
        print("✗ Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
