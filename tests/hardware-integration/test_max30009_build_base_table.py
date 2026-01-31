"""
Test Case 35: MAX30009 Start Base-Table Build and Observe Asynchronous calib_data

Tests the MAX30009 base table calibration build process which performs 100 frequency
calibrations and emits asynchronous calib_data messages for each iteration.

Test Steps:
1. Connect to MAX30009 server
2. Send build_base_table request
3. Confirm immediate response is {"type":"build_base_table_started"}
4. Capture 100 subsequent asynchronous calib_data JSON messages
5. Validate message structure and calibration parameters

Pass Criteria:
- Immediate response is {"type":"build_base_table_started"}
- 100 asynchronous calib_data JSONs are emitted with correct structure
- Frequencies progress from 1kHz to 500kHz
- Fixed calibration settings are correct (64µA, G10, BYPASS, 370Ω)
"""
import pytest
import time
import json
from pathlib import Path
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from data_logger import JSONLLogger


def get_expected_frequency(index: int) -> int:
    """
    Calculate expected calibration frequency for a given index.

    Frequency progression:
    - Index 0-19: 1kHz to 20kHz (1kHz steps)
    - Index 20-59: 22kHz to 100kHz (2kHz steps)
    - Index 60-99: 110kHz to 500kHz (10kHz steps)

    Based on firmware: MAX30009_base_cal_table.h lines 136-155
    """
    if index < 20:
        # 1kHz - 20kHz (1kHz step)
        return 1000 + (index * 1000)
    elif index < 60:
        # 22kHz - 100kHz (2kHz step)
        return 22000 + ((index - 20) * 2000)
    else:
        # 110kHz - 500kHz (10kHz step)
        return 110000 + ((index - 60) * 10000)


def validate_calib_data_structure(msg: dict, index: int) -> None:
    """
    Validate that a calib_data message has all required fields.

    Based on firmware: MAX30009_base_cal_table.h lines 95-134
    """
    # Required fields from JSON format
    required_fields = [
        'type',
        'index',
        'I_offset',
        'I_coef',
        'I_phase_coef',
        'I_phase_cos',
        'I_phase_sin',
        'Q_offset',
        'Q_coef',
        'Q_phase_coef',
        'Q_phase_cos',
        'Q_phase_sin',
        'I_cal_in',
        'I_cal_in_ADC',
        'I_cal_quad',
        'I_cal_quad_ADC',
        'Q_cal_in',
        'Q_cal_in_ADC',
        'Q_cal_quad',
        'Q_cal_quad_ADC',
        'calibrate_frequency',
        'calibrate_current',
        'calibrate_gain',
        'input_filter',
        'ref_value'
    ]

    for field in required_fields:
        assert field in msg, f"Missing required field '{field}' in calib_data message at index {index}"

    # Validate types
    assert isinstance(msg['index'], int), f"index should be int at index {index}"
    assert isinstance(msg['I_offset'], int), f"I_offset should be int at index {index}"
    assert isinstance(msg['Q_offset'], int), f"Q_offset should be int at index {index}"
    assert isinstance(msg['calibrate_frequency'], int), f"calibrate_frequency should be int at index {index}"


def validate_fixed_settings(msg: dict, index: int) -> None:
    """
    Validate that fixed calibration settings are correct.

    Based on firmware: MAX30009_process.h lines 116-119
    - BASE_TABLE_CURRENT = 64µA
    - BASE_TABLE_GAIN = G10 (10x gain)
    - Input filter = BYPASS
    - Reference resistor = 370Ω
    """
    assert msg['calibrate_current'] == '64uA', \
        f"Expected calibrate_current='64uA' at index {index}, got '{msg['calibrate_current']}'"

    assert msg['calibrate_gain'] == 'G10', \
        f"Expected calibrate_gain='G10' at index {index}, got '{msg['calibrate_gain']}'"

    assert msg['input_filter'] == 'BYPASS', \
        f"Expected input_filter='BYPASS' at index {index}, got '{msg['input_filter']}'"

    # ref_value should be close to 370 (may have slight variations)
    ref_value = float(msg['ref_value'])
    assert 300 < ref_value < 450, \
        f"Expected ref_value ~370Ω at index {index}, got {ref_value}Ω"


@pytest.fixture
def max30009_client(test_config, max30009_cleanup):
    """
    Create TCP client for MAX30009 service.

    Note: The max30009_cleanup fixture ensures clean state before/after test.
    """
    max_config = test_config['services']['max30009']

    with TCPClient(max_config['host'], max_config['port']) as client:
        yield client


@pytest.mark.hardware
@pytest.mark.max30009
@pytest.mark.slow
def test_max30009_build_base_table(max30009_client, results_dir):
    """
    Test Case 35: MAX30009 build base table calibration.

    Sends build_base_table command and captures 100 asynchronous calib_data messages.
    Validates message structure, fixed settings, and frequency progression.

    **IMPORTANT: This test requires actual MAX30009 hardware to be connected.**
    The calibration process needs the hardware to generate FIFO data.
    Without hardware, the calibration will hang in CALIB_WAIT_DATA state.

    Duration: ~15-30 seconds (100 calibrations × ~150-300ms each)
    """
    print(f"\n{'='*70}")
    print(f"Test Case 35: MAX30009 Build Base Table Calibration")
    print(f"{'='*70}")

    # Step 1: Send build_base_table request
    print(f"\n[Step 1] Sending build_base_table request...")
    request = {"type": "build_base_table"}

    response = max30009_client.send(request)
    print(f"Response: {response}")

    # Step 2: Validate immediate response
    print(f"\n[Step 2] Validating immediate response...")
    assert response.get('type') == 'build_base_table_started', \
        f"Expected 'build_base_table_started', got '{response.get('type')}'"
    print(f"✓ Received: {{'type': 'build_base_table_started'}}")

    # Debug: Wait a bit and see if data starts flowing
    print(f"\n[Debug] Waiting 2 seconds for calibration to start...")
    time.sleep(2.0)
    print(f"[Debug] Now checking for messages...")

    # Step 3: Capture 100 asynchronous calib_data messages
    print(f"\n[Step 3] Capturing 100 asynchronous calib_data messages...")
    print(f"Expected duration: ~15-30 seconds")
    print(f"This will take some time, please wait...\n")

    calib_messages = []
    expected_count = 100
    timeout_per_message = 10.0  # 10 seconds timeout per message

    start_time = time.time()

    for iteration in range(expected_count):
        try:
            # Receive async calib_data message
            msg = max30009_client.recv(timeout=timeout_per_message)

            if not msg:
                raise TimeoutError(f"Timeout waiting for calib_data message {iteration}")

            # Validate it's a calib_data message
            assert msg.get('type') == 'calib_data', \
                f"Expected 'calib_data' at iteration {iteration}, got '{msg.get('type')}'"

            # Validate index
            msg_index = msg.get('index')
            assert msg_index is not None, f"Missing 'index' field at iteration {iteration}"
            assert 0 <= msg_index < 100, f"Invalid index {msg_index} at iteration {iteration}"

            calib_messages.append(msg)

            # Progress indicator every 10 messages
            if (iteration + 1) % 10 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {iteration + 1}/100 messages received (elapsed: {elapsed:.1f}s)")

        except TimeoutError as e:
            print(f"\n✗ TIMEOUT: {e}")
            print(f"  Received {len(calib_messages)}/100 messages before timeout")
            raise

    elapsed_time = time.time() - start_time
    print(f"\n✓ Received all 100 calib_data messages in {elapsed_time:.1f}s")
    print(f"  Average time per calibration: {elapsed_time/100:.3f}s")

    # Step 4: Validate message structure
    print(f"\n[Step 4] Validating message structure...")

    for i, msg in enumerate(calib_messages):
        validate_calib_data_structure(msg, i)
        validate_fixed_settings(msg, i)

    print(f"✓ All messages have correct structure and fixed settings")

    # Step 5: Validate frequency progression
    print(f"\n[Step 5] Validating frequency progression...")

    # Extract indices and sort messages by index
    sorted_messages = sorted(calib_messages, key=lambda m: m['index'])

    # Check for missing or duplicate indices
    indices = [msg['index'] for msg in sorted_messages]
    assert len(set(indices)) == 100, f"Duplicate indices found: {len(set(indices))} unique out of 100"
    assert indices == list(range(100)), "Indices are not sequential 0-99"
    print(f"✓ All indices 0-99 present, no duplicates")

    # Validate frequencies match expected pattern
    frequency_errors = []
    for msg in sorted_messages:
        index = msg['index']
        expected_freq = get_expected_frequency(index)
        actual_freq = msg['calibrate_frequency']

        if expected_freq != actual_freq:
            frequency_errors.append({
                'index': index,
                'expected': expected_freq,
                'actual': actual_freq
            })

    if frequency_errors:
        print(f"\n✗ Frequency mismatches found:")
        for err in frequency_errors[:10]:  # Show first 10 errors
            print(f"  Index {err['index']}: expected {err['expected']} Hz, got {err['actual']} Hz")
        raise AssertionError(f"Frequency validation failed: {len(frequency_errors)} mismatches")

    print(f"✓ All frequencies match expected progression:")
    print(f"  Index 0-19:  {sorted_messages[0]['calibrate_frequency']} Hz - {sorted_messages[19]['calibrate_frequency']} Hz (1kHz steps)")
    print(f"  Index 20-59: {sorted_messages[20]['calibrate_frequency']} Hz - {sorted_messages[59]['calibrate_frequency']} Hz (2kHz steps)")
    print(f"  Index 60-99: {sorted_messages[60]['calibrate_frequency']} Hz - {sorted_messages[99]['calibrate_frequency']} Hz (10kHz steps)")

    # Step 6: Store calibration data to JSONL file (standard practice: ~/sensor-test-data/data/calib/)
    print(f"\n[Step 6] Storing calibration data...")

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(results_dir) / "data" / "calib" / f"test_025_base_table_calibration_{timestamp}.jsonl"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger = JSONLLogger(str(output_file), test_id="test_025", sensor="max30009")

    # Write metadata
    metadata = {
        'type': 'metadata',
        'test_case': 'TC-025',
        'test_name': 'MAX30009 Base Table Calibration',
        'calibration_count': len(sorted_messages),
        'duration_sec': elapsed_time
    }
    logger.write_raw(metadata)

    # Write calibration data
    for msg in sorted_messages:
        logger.write_raw(msg)

    print(f"✓ Calibration data saved to: {output_file.name}")
    print(f"  File contains {len(sorted_messages)} calibration records")

    # Summary
    print(f"\n{'='*70}")
    print(f"✓ Test Case 35 PASSED")
    print(f"{'='*70}")
    print(f"Summary:")
    print(f"  - Received 100 calib_data messages")
    print(f"  - Total duration: {elapsed_time:.1f}s")
    print(f"  - Avg per calibration: {elapsed_time/100:.3f}s")
    print(f"  - Frequency range: {sorted_messages[0]['calibrate_frequency']} Hz - {sorted_messages[99]['calibrate_frequency']} Hz")
    print(f"  - Fixed settings: 64µA, G10, BYPASS, ~370Ω")
    print(f"  - Output file: {output_file}")
    print(f"{'='*70}")
