"""
Test Case 53 (ADS1293 only): Sync Marker Format Verification for ECG

Category: FW-APP Integration
Components: ADS1293 + Firmware sync insertion

Test Steps:
1. Configure ADS1293 for data acquisition
2. Wait for sync markers to be injected
3. Poll with get_data and capture sync markers
4. Verify ECG sync format: [-99999, sync_num, 0]
5. Verify sync_num values are incrementing

Pass Criteria:
- ECG sync uses magic -99999 with sync_num as second element
- Format is exactly: [-99999, sync_num, 0]
- Sync numbers increment properly (1, 2, 3, ...)

Based on firmware:
- services/spi-service/src/main.cpp lines 159-209 (sync injection every 1 second)
- services/spi-service/src/ADS1293_process.cpp lines 61-71 (ECG format)
- services/spi-service/include/ADS1293_process.h (SYNC_MARK_MAGIC_NUM = -99999)
"""

import pytest
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient


# Magic number from firmware
ECG_SYNC_MAGIC = -99999


@pytest.fixture
def ads1293_client(test_config):
    """
    Create TCP client for ADS1293 service with cleanup.

    Ensures sensor is powered off after test.
    """
    import time

    ads_config = test_config['services']['ads1293']
    with TCPClient(ads_config['host'], ads_config['port']) as client:
        yield client

        # Cleanup: Power off sensor
        try:
            poweroff_request = {"type": "poweroff"}
            client.send(poweroff_request)
            time.sleep(0.2)
        except:
            pass


@pytest.mark.fw_app
@pytest.mark.api
@pytest.mark.ads1293
@pytest.mark.quick
def test_ads1293_sync_marker_format(ads1293_client):
    """
    Test Case 53 (ADS1293): Verify sync marker format for ECG stream.

    Validates that:
    1. ECG sync markers use format: [-99999, sync_num, 0]
    2. Sync numbers are incrementing
    3. Sync markers appear every ~1 second
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 53: ADS1293 Sync Marker Format Verification")
    print(f"{'='*70}")

    # Step 1: Configure ADS1293 for ECG acquisition
    print(f"\n[Step 1] Configuring ADS1293 for ECG acquisition...")

    ads_settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": 4,
        "R3_rate": 16
    }

    ads_response = ads1293_client.send(ads_settings)
    assert ads_response["type"] == "actual_settings", \
        f"ADS1293 config failed: {ads_response}"

    print(f"  ✓ ADS1293 configured:")
    print(f"    - R1_rate: {ads_response['R1_rate']}")
    print(f"    - R2_rate: {ads_response['R2_rate']}")
    print(f"    - R3_rate: {ads_response['R3_rate']}")
    print(f"    - Sampling rate: ~{128000 // (ads_response['R1_rate'] * ads_response['R2_rate'] * ads_response['R3_rate'])} Hz")
    print(f"    - Conversion enabled: {ads_response['enable_conversion']}")

    # Step 2: Wait for sensor stabilization and sync marker injection
    print(f"\n[Step 2] Waiting for sensor stabilization and sync marker injection...")
    print(f"  Firmware injects sync markers every 1 second")
    print(f"  Waiting 2.5 seconds for at least 2 sync markers...")
    time.sleep(2.5)

    # Step 3: Flush initial buffer (contains stabilization data)
    print(f"\n[Step 3] Flushing initial buffer...")
    flush_response = ads1293_client.send({"type": "get_data"})
    assert flush_response["type"] == "data", "Flush failed"
    print(f"  ✓ Flushed {len(flush_response['data'])} samples")

    # Step 4: Wait for fresh sync markers
    print(f"\n[Step 4] Waiting for fresh sync markers...")
    time.sleep(2.5)

    # Step 5: Collect data with sync markers
    print(f"\n[Step 5] Collecting ECG data...")

    ecg_request = {"type": "get_data"}
    ecg_response = ads1293_client.send(ecg_request)

    assert ecg_response["type"] == "data", \
        f"Expected 'data', got '{ecg_response.get('type')}'"
    assert "data" in ecg_response, "ECG response missing 'data' field"

    ecg_samples = ecg_response["data"]
    print(f"  ✓ Received {len(ecg_samples)} ECG samples")

    # Step 6: Extract and validate sync markers
    print(f"\n[Step 6] Extracting and validating sync markers...")

    ecg_sync_markers = [s for s in ecg_samples if s[0] == ECG_SYNC_MAGIC]
    data_points = [s for s in ecg_samples if s[0] != ECG_SYNC_MAGIC]

    assert len(ecg_sync_markers) > 0, \
        f"No ECG sync markers found (magic={ECG_SYNC_MAGIC})"

    print(f"  ✓ Found {len(ecg_sync_markers)} sync marker(s)")
    print(f"  ✓ Found {len(data_points)} data point(s)")

    # Validate each sync marker in detail
    print(f"\n[Step 7] Validating sync marker format...")

    for i, marker in enumerate(ecg_sync_markers, 1):
        print(f"\n  [Sync Marker {i}]")
        print(f"    Raw: {marker}")

        # Verify structure
        assert len(marker) == 3, \
            f"ECG marker should have 3 elements, got {len(marker)}"

        # Verify magic number
        assert marker[0] == ECG_SYNC_MAGIC, \
            f"ECG marker[0] should be {ECG_SYNC_MAGIC}, got {marker[0]}"

        # Verify sync_num is valid integer
        sync_num = marker[1]
        assert isinstance(sync_num, int), \
            f"ECG sync_num should be int, got {type(sync_num)}"
        assert sync_num > 0, \
            f"ECG sync_num should be positive, got {sync_num}"

        # Verify third element is 0
        assert marker[2] == 0, \
            f"ECG marker[2] should be 0, got {marker[2]}"

        print(f"    ✓ Magic number: {marker[0]}")
        print(f"    ✓ Sync number:  {marker[1]}")
        print(f"    ✓ Padding:      {marker[2]}")
        print(f"    ✓ Format valid: [-99999, {sync_num}, 0]")

    # Step 8: Verify sync numbers are incrementing
    print(f"\n[Step 8] Verifying sync number sequence...")

    sync_numbers = [marker[1] for marker in ecg_sync_markers]
    print(f"  Sync_num sequence: {sync_numbers}")

    if len(sync_numbers) > 1:
        # Check if incrementing
        is_incrementing = all(sync_numbers[i] < sync_numbers[i+1]
                            for i in range(len(sync_numbers)-1))
        assert is_incrementing, \
            f"Sync numbers should be incrementing, got {sync_numbers}"
        print(f"  ✓ Sync numbers are incrementing")

        # Check increment is by 1
        increments = [sync_numbers[i+1] - sync_numbers[i]
                     for i in range(len(sync_numbers)-1)]
        all_ones = all(inc == 1 for inc in increments)
        if all_ones:
            print(f"  ✓ Sync numbers increment by exactly 1")
        else:
            print(f"  Note: Increments are {increments} (some may be > 1 due to timing)")
    else:
        print(f"  Note: Only one sync marker found, cannot verify incrementing")

    # Step 9: Show example data point format
    if len(data_points) > 0:
        print(f"\n[Step 9] Example data point format...")
        example = data_points[0]
        print(f"  Raw: {example}")
        print(f"  Format: [ch1, ch2, ch3]")
        print(f"  All values are raw ADC counts (no scaling)")

        assert len(example) == 3, "ECG data should have 3 channels"
        print(f"  ✓ Data point structure valid")

    # Print summary
    print(f"\n{'='*70}")
    print(f"ADS1293 Sync Marker Summary:")
    print(f"{'='*70}")
    print(f"  Format:        [-99999, sync_num, 0]")
    print(f"  Magic Number:  {ECG_SYNC_MAGIC}")
    print(f"  Markers Found: {len(ecg_sync_markers)}")
    print(f"  Sync Numbers:  {sync_numbers}")
    print(f"  Data Points:   {len(data_points)}")
    print(f"")
    print(f"  Example Sync Marker: {ecg_sync_markers[0]}")
    if len(data_points) > 0:
        print(f"  Example Data Point:  {data_points[0]}")
    print(f"{'='*70}")

    print(f"\n✓ Test PASSED: ADS1293 sync marker format verified")
    print(f"{'='*70}\n")


@pytest.mark.fw_app
@pytest.mark.api
@pytest.mark.ads1293
@pytest.mark.quick
def test_ads1293_sync_marker_timing(ads1293_client):
    """
    Test Case 53.1 (ADS1293): Verify sync marker injection timing.

    Validates that sync markers appear approximately every 1 second
    as expected from firmware implementation.
    """
    import time

    print(f"\n{'='*70}")
    print(f"Test Case 53.1: ADS1293 Sync Marker Timing")
    print(f"{'='*70}")

    # Configure ADS1293
    print(f"\n[Step 1] Configuring ADS1293...")

    settings = {
        "type": "settings",
        "enable_conversion": True,
        "power_enable": True,
        "R2_rate": 4,
        "R3_rate": 16
    }

    response = ads1293_client.send(settings)
    assert response["type"] == "actual_settings"
    print(f"  ✓ ADS1293 configured")

    # Wait and flush buffer
    print(f"\n[Step 2] Waiting and flushing buffer...")
    time.sleep(2.0)
    flush_response = ads1293_client.send({"type": "get_data"})
    print(f"  ✓ Flushed {len(flush_response['data'])} samples")

    # Collect data over multiple intervals
    print(f"\n[Step 3] Collecting data over 5 seconds...")
    time.sleep(5.0)

    data_response = ads1293_client.send({"type": "get_data"})
    assert data_response["type"] == "data"
    samples = data_response["data"]
    print(f"  ✓ Received {len(samples)} samples")

    # Extract sync markers
    sync_markers = [s for s in samples if s[0] == ECG_SYNC_MAGIC]
    print(f"  ✓ Found {len(sync_markers)} sync markers")

    # Expected: ~5 sync markers over 5 seconds
    assert len(sync_markers) >= 3, \
        f"Expected at least 3 sync markers over 5s, got {len(sync_markers)}"
    assert len(sync_markers) <= 7, \
        f"Expected at most 7 sync markers over 5s, got {len(sync_markers)}"

    print(f"\n[Step 4] Analyzing timing...")
    sync_numbers = [m[1] for m in sync_markers]
    print(f"  Sync_num sequence: {sync_numbers}")

    # Calculate approximate rate
    if len(sync_numbers) > 1:
        total_increments = sync_numbers[-1] - sync_numbers[0]
        expected_rate = total_increments / 5.0  # Over 5 seconds
        print(f"  Total increments: {total_increments}")
        print(f"  Rate: {expected_rate:.2f} markers/second")
        print(f"  Expected: ~1.0 markers/second")

        # Verify approximately 1 per second (allow some tolerance)
        assert 0.7 <= expected_rate <= 1.3, \
            f"Sync marker rate should be ~1/sec, got {expected_rate:.2f}"
        print(f"  ✓ Timing verified: ~1 marker per second")

    print(f"\n{'='*70}")
    print(f"Sync Marker Timing Summary:")
    print(f"{'='*70}")
    print(f"  Duration:      5 seconds")
    print(f"  Markers Found: {len(sync_markers)}")
    print(f"  Expected:      ~5 markers (1 per second)")
    print(f"  Sync Numbers:  {sync_numbers[0]} to {sync_numbers[-1]}")
    print(f"{'='*70}")

    print(f"\n✓ Test PASSED: Sync marker timing verified")
    print(f"{'='*70}\n")
