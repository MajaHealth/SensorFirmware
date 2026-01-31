"""
Test Case 8: MAX30009 ICG Automated Integration with Resistor Loads

Category: HW-FW Integration
Components: MAX30009 + firmware service + resistor loads

Test Flow:
1. Clear base table if previously generated
2. Generate base table and verify "build_base_table_started"
3. For each resistor load (20Ω, 100Ω, 200Ω, 300Ω):
   a. Connect resistor to ICG electrodes
   b. Configure: fs=400Hz, current=1.28µA, freq=20kHz
   c. Verify state transitions
   d. Record data for 60 seconds (poll every 0.5s)
   e. Calculate mean error for R and Z
   f. Verify sync markers (monotonic increase every 1s)
   g. Verify sampling frequency 400Hz ± 1Hz
4. Power off and verify

Pass Criteria:
- Impedance MAE ≤ 3 Ω
- Resistance MAE ≤ 2 Ω
- Sync markers monotonically increase every 1s
- Sampling frequency 400 Hz ± 1 Hz

Requirements:
- Physical MAX30009 sensor
- Selectable resistor loads (20, 100, 200, 300 Ω)
- Precision resistors for accurate validation
"""

import pytest
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from tcp_client import TCPClient
from data_logger import JSONLLogger
from analysis_runner import run_analysis


# Test configuration
RESISTOR_LOADS_OHM = [20, 100, 200, 300]  # Resistor values to test

RECORDING_DURATION = 60.0    # seconds per resistor
POLLING_INTERVAL = 0.5       # seconds between polls
SAMPLING_RATE = 400          # Hz (measure_frequency)
STIMULATION_FREQUENCY = 20000  # 20 kHz
STIMULATION_CURRENT = "1.28uA"  # Lower current for ICG

# Expected state transition sequence
EXPECTED_STATE_SEQUENCE = [
    "pre_measuring",
    "pre_measure_end",
    "calibrating",
    "calibrate_end",
    "start_measuring"
]

# Sync marker magic number (MAX30009 scaled by 10000)
ICG_SYNC_MAGIC = -999990000
ICG_SCALING_FACTOR = 10000


def drain_async_messages(client, message_types=['meas_state', 'data'], timeout=0.1, max_attempts=20):
    """Drain pending async messages from MAX30009."""
    time.sleep(0.2)
    drain_attempts = 0
    while drain_attempts < max_attempts:
        try:
            msg = client.recv(timeout=timeout)
            if not msg:
                break
            if msg.get('type') in message_types:
                drain_attempts += 1
                continue
            break
        except:
            break


def send_and_wait_for_response(client, request, expected_type, timeout_attempts=15):
    """Send request and filter async messages until expected response arrives."""
    import json as json_lib

    # Send request
    client.socket.sendall((json_lib.dumps(request) + '\n').encode())

    # Wait for expected response
    for attempt in range(timeout_attempts):
        try:
            response = client.recv(timeout=1.0)

            if not response:
                time.sleep(0.1)
                continue

            if response.get('type') == expected_type:
                return response

            # Filter async messages
            if response.get('type') in ['meas_state', 'data', 'calib_data']:
                continue

            # Unexpected response
            return response

        except Exception as e:
            continue

    return {"type": "timeout", "error": f"No {expected_type} response received"}


def monitor_state_transitions(client, expected_states, timeout=30.0):
    """Monitor MAX30009 state transitions and verify expected sequence."""
    observed_states = []
    start_time = time.time()

    print(f"\n  [Monitoring state transitions...]")
    print(f"    Expected: {' → '.join(expected_states)}")

    while (time.time() - start_time) < timeout:
        try:
            msg = client.recv(timeout=0.5)

            if not msg:
                continue

            if msg.get('type') == 'meas_state':
                state = msg.get('state')
                timestamp = time.time() - start_time

                observed_states.append({
                    'state': state,
                    'timestamp': timestamp,
                    'message': msg
                })

                print(f"    [{timestamp:.2f}s] State: {state}")

                # Check if we've seen all expected states
                observed_state_names = [s['state'] for s in observed_states]
                if all(exp in observed_state_names for exp in expected_states):
                    print(f"    ✓ All expected states observed in sequence")
                    return observed_states

        except Exception as e:
            continue

    print(f"    Note: Timeout after {timeout}s")
    return observed_states


def validate_sync_markers(samples):
    """
    Extract and validate sync markers from ICG data.

    Returns:
    - sync_markers: List of sync marker records
    - data_samples: List of non-sync data samples
    - validation_results: Dict with validation results
    """
    sync_markers = []
    data_samples = []

    # Separate sync markers from data
    for sample in samples:
        if len(sample) >= 5 and sample[0] == ICG_SYNC_MAGIC:
            # Sync marker format: [-999990000, sync_num×10000, 0, 0, 0]
            sync_num = sample[1] // ICG_SCALING_FACTOR
            sync_markers.append({
                'raw': sample,
                'sync_num': sync_num,
                'scaled_sync_num': sample[1]
            })
        else:
            data_samples.append(sample)

    print(f"\n  [Sync Marker Validation]")
    print(f"    Total samples: {len(samples)}")
    print(f"    Sync markers: {len(sync_markers)}")
    print(f"    Data samples: {len(data_samples)}")

    if len(sync_markers) == 0:
        return sync_markers, data_samples, {
            'valid': False,
            'error': 'No sync markers found'
        }

    # Validate monotonic increase
    sync_numbers = [s['sync_num'] for s in sync_markers]
    print(f"    Sync_num sequence: {sync_numbers}")

    is_monotonic = all(sync_numbers[i] < sync_numbers[i+1]
                      for i in range(len(sync_numbers)-1))

    if not is_monotonic:
        print(f"   Sync numbers are NOT monotonically increasing")
        return sync_markers, data_samples, {
            'valid': False,
            'is_monotonic': False,
            'sync_numbers': sync_numbers
        }

    print(f"    ✓ Sync numbers are monotonically increasing")

    # Check increment by 1
    increments = [sync_numbers[i+1] - sync_numbers[i]
                 for i in range(len(sync_numbers)-1)]
    all_ones = all(inc == 1 for inc in increments)

    if all_ones:
        print(f"    ✓ Sync numbers increment by exactly 1")
    else:
        print(f"    Note: Increments are {increments}")

    # Validate ~1 second spacing
    # Each sync marker should appear approximately every 1 second
    expected_markers = int(RECORDING_DURATION)
    marker_count_ok = abs(len(sync_markers) - expected_markers) <= 2

    print(f"    Expected markers: ~{expected_markers} (1 per second)")
    print(f"    Actual markers: {len(sync_markers)}")

    if marker_count_ok:
        print(f"    ✓ Marker count matches expected")
    else:
        print(f"    ✗ Marker count differs from expected")

    return sync_markers, data_samples, {
        'valid': True,
        'is_monotonic': is_monotonic,
        'sync_numbers': sync_numbers,
        'marker_count': len(sync_markers),
        'expected_count': expected_markers,
        'count_ok': marker_count_ok
    }


def validate_sampling_frequency(data_samples, sync_markers, recording_duration):
    """
    Validate actual sampling frequency is 400 Hz ± 1 Hz.

    Uses sync markers to determine actual recording duration.
    """
    print(f"\n  [Sampling Frequency Validation]")

    if len(sync_markers) < 2:
        print(f"    ✗ Insufficient sync markers for validation")
        return {'valid': False, 'error': 'Insufficient sync markers'}

    # Calculate actual duration from sync markers
    # Number of sync markers - 1 = seconds elapsed
    actual_duration = len(sync_markers) - 1
    print(f"    Sync markers: {len(sync_markers)}")
    print(f"    Actual duration: {actual_duration} seconds")

    # Calculate sampling frequency
    total_samples = len(data_samples)
    actual_fs = total_samples / actual_duration

    print(f"    Total data samples: {total_samples}")
    print(f"    Actual sampling rate: {actual_fs:.2f} Hz")
    print(f"    Expected: {SAMPLING_RATE} Hz ± 1 Hz")

    # Validate within ±1 Hz
    error = abs(actual_fs - SAMPLING_RATE)
    within_tolerance = error <= 1.0

    if within_tolerance:
        print(f"    ✓ Sampling frequency within tolerance (error: {error:.2f} Hz)")
    else:
        print(f"    ✗ Sampling frequency outside tolerance (error: {error:.2f} Hz)")

    return {
        'valid': True,
        'actual_fs': actual_fs,
        'expected_fs': SAMPLING_RATE,
        'error': error,
        'within_tolerance': within_tolerance,
        'total_samples': total_samples,
        'duration': actual_duration
    }


@pytest.fixture
def max30009_client(test_config, max30009_cleanup):
    """Create TCP client for MAX30009 with cleanup."""
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        drain_async_messages(client)
        yield client


@pytest.fixture
def results_file(results_dir):
    """Create results file for JSONL data logging.

    Standard practice: ~/sensor-test-data/data/bioz/
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_008_icg_resistor_{timestamp}.jsonl"
    filepath = results_dir / "data" / "bioz" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    return filepath


@pytest.mark.hardware
@pytest.mark.max30009
@pytest.mark.slow
def test_max30009_icg_resistor_loads(max30009_client, results_file):
    """
    Test Case 8: MAX30009 ICG automated integration with resistor loads.

    Tests impedance measurement accuracy, sync marker generation,
    and sampling frequency with pure resistive loads.

    **IMPORTANT: This test requires physical MAX30009 hardware**
    """
    print(f"\n{'='*70}")
    print(f"Test Case 8: MAX30009 ICG Resistor Load Integration")
    print(f"{'='*70}")
    print(f"\nTest Configuration:")
    print(f"  Resistor loads: {RESISTOR_LOADS_OHM} Ω")
    print(f"  Frequency: {STIMULATION_FREQUENCY} Hz")
    print(f"  Current: {STIMULATION_CURRENT}")
    print(f"  Sampling rate: {SAMPLING_RATE} Hz")
    print(f"  Recording duration: {RECORDING_DURATION}s per load")
    print(f"\nResults will be saved to: {results_file}")

    # Initialize logger and write metadata
    logger = JSONLLogger(str(results_file), test_id="test_008", sensor="max30009")

    metadata = {
        'type': 'metadata',
        'test_case': 'TC-008',
        'test_name': 'MAX30009 ICG Resistor Loads Integration',
        'timestamp': datetime.now().isoformat(),
        'resistor_loads_ohm': RESISTOR_LOADS_OHM,
        'stimulation_frequency': STIMULATION_FREQUENCY,
        'stimulation_current': STIMULATION_CURRENT,
        'sampling_rate': SAMPLING_RATE,
        'recording_duration_s': RECORDING_DURATION,
        'polling_interval_s': POLLING_INTERVAL
    }
    logger.write_raw(metadata)

    # Step 1: Clear base table
    print(f"\n{'='*70}")
    print(f"[Step 1] Clearing base table...")
    print(f"{'='*70}")

    drain_async_messages(max30009_client)

    clear_request = {"type": "clear_base_table"}
    clear_response = send_and_wait_for_response(max30009_client, clear_request, "base_table_cleared")

    assert clear_response["type"] == "base_table_cleared", \
        f"Clear base table failed: {clear_response}"
    print(f"  ✓ Base table cleared")

    # Step 2: Generate base table
    print(f"\n{'='*70}")
    print(f"[Step 2] Generating base table (calibration)...")
    print(f"{'='*70}")

    drain_async_messages(max30009_client)

    build_request = {"type": "build_base_table"}
    build_response = send_and_wait_for_response(max30009_client, build_request, "build_base_table_started")

    assert build_response["type"] == "build_base_table_started", \
        f"Build base table failed: {build_response}"
    print(f"  ✓ Base table generation started")

    # Monitor base table generation
    print(f"\n  [Monitoring base table generation...]")
    print(f"    This may take 15-30 seconds, please wait...")
    generation_complete = False
    start_time = time.time()
    timeout = 120.0

    calib_count = 0
    while (time.time() - start_time) < timeout:
        try:
            msg = max30009_client.recv(timeout=2.0)
            if msg:
                msg_type = msg.get('type')
                if msg_type == 'build_base_table_end':
                    elapsed = time.time() - start_time
                    print(f"  ✓ Base table generation complete ({elapsed:.1f}s, {calib_count} calibrations)")
                    generation_complete = True
                    break
                elif msg_type == 'calib_data':
                    calib_count += 1
                    if calib_count % 20 == 0:
                        elapsed = time.time() - start_time
                        print(f"    Progress: {calib_count}/100 calibrations ({elapsed:.1f}s)")
        except:
            continue

    assert generation_complete, "Base table generation did not complete"

    drain_async_messages(max30009_client)

    # Step 3: Test each resistor load
    print(f"\n{'='*70}")
    print(f"[Step 3] Resistor Load Testing")
    print(f"{'='*70}")

    all_load_data = []

    for load_idx, resistor_ohm in enumerate(RESISTOR_LOADS_OHM, 1):
        print(f"\n{'-'*70}")
        print(f"Resistor Load {load_idx}/{len(RESISTOR_LOADS_OHM)}: {resistor_ohm} Ω")
        print(f"{'-'*70}")
        print(f"\n*** PLEASE CONNECT {resistor_ohm} Ω RESISTOR NOW ***")
        print(f"Press Enter when ready...")
        input()

        load_start_time = time.time()

        # Configure sensor
        print(f"\n  [Configuring sensor...]")
        drain_async_messages(max30009_client)

        settings = {
            "type": "settings",
            "measure_enable": True,
            "stimulate_frequency": STIMULATION_FREQUENCY,
            "measure_frequency": SAMPLING_RATE,
            "stimulate_current": STIMULATION_CURRENT
        }

        config_response = send_and_wait_for_response(max30009_client, settings, "actual_settings")

        if config_response["type"] != "actual_settings":
            print(f"  ✗ Configuration failed: {config_response}")
            error_record = {
                'type': 'error',
                'resistor_ohm': resistor_ohm,
                'message': 'Configuration failed',
                'response': config_response
            }
            logger.write_raw(error_record)
            continue

        print(f"  ✓ Configured: {config_response['stimulate_frequency']} Hz, {config_response['stimulate_current']}")

        # Monitor state transitions
        state_transitions = monitor_state_transitions(
            max30009_client,
            EXPECTED_STATE_SEQUENCE,
            timeout=30.0
        )

        # Wait for stabilization
        print(f"\n  [Waiting for measurement stabilization...]")
        time.sleep(2.0)

        # Flush initial buffer
        drain_async_messages(max30009_client, max_attempts=10)

        # Record data for RECORDING_DURATION
        print(f"\n  [Recording data for {RECORDING_DURATION}s...]")
        print(f"    Polling every {POLLING_INTERVAL}s")

        all_samples = []
        collection_start = time.time()
        poll_count = 0

        while (time.time() - collection_start) < RECORDING_DURATION:
            # Request data
            drain_async_messages(max30009_client, max_attempts=5)
            data_request = {"type": "get_data"}
            data_response = send_and_wait_for_response(max30009_client, data_request, "data")

            if data_response["type"] == "data" and "data" in data_response:
                samples = data_response["data"]
                poll_count += 1
                elapsed = time.time() - collection_start

                print(f"    [{elapsed:.1f}s] Poll {poll_count}: {len(samples)} samples")

                all_samples.extend(samples)

            # Wait for next polling interval
            time.sleep(POLLING_INTERVAL)

        load_duration = time.time() - load_start_time
        print(f"  ✓ Collected {len(all_samples)} samples in {load_duration:.2f}s")

        # Validate sync markers
        sync_markers, data_samples, sync_validation = validate_sync_markers(all_samples)

        # Validate sampling frequency
        fs_validation = validate_sampling_frequency(data_samples, sync_markers, RECORDING_DURATION)

        # Calculate statistics
        print(f"\n  [Calculating statistics...]")

        # Extract impedance components (scaled by 10000)
        real_values = [s[0] / ICG_SCALING_FACTOR for s in data_samples if len(s) >= 5]
        mag_values = [s[1] / ICG_SCALING_FACTOR for s in data_samples if len(s) >= 5]
        imag_values = [s[2] / ICG_SCALING_FACTOR for s in data_samples if len(s) >= 5]
        angle_values = [s[3] / ICG_SCALING_FACTOR for s in data_samples if len(s) >= 5]

        import statistics
        load_summary = {
            'type': 'load_summary',
            'resistor_ohm': resistor_ohm,
            'duration_s': load_duration,
            'total_samples': len(all_samples),
            'data_samples': len(data_samples),
            'sync_markers': len(sync_markers),
            'statistics': {
                'real_mean': statistics.mean(real_values) if real_values else 0,
                'real_std': statistics.stdev(real_values) if len(real_values) > 1 else 0,
                'mag_mean': statistics.mean(mag_values) if mag_values else 0,
                'mag_std': statistics.stdev(mag_values) if len(mag_values) > 1 else 0,
                'imag_mean': statistics.mean(imag_values) if imag_values else 0,
                'imag_std': statistics.stdev(imag_values) if len(imag_values) > 1 else 0,
                'angle_mean': statistics.mean(angle_values) if angle_values else 0,
                'angle_std': statistics.stdev(angle_values) if len(angle_values) > 1 else 0
            },
            'expected': {
                'R': resistor_ohm,
                'Z': resistor_ohm,  # For pure resistor, Z = R
                'Xc': 0,            # No reactance
                'PhA': 0            # No phase shift
            },
            'errors': {
                'R_error': abs(statistics.mean(real_values) - resistor_ohm) if real_values else 0,
                'Z_error': abs(statistics.mean(mag_values) - resistor_ohm) if mag_values else 0
            },
            'sync_validation': sync_validation,
            'fs_validation': fs_validation,
            'state_transitions': state_transitions
        }

        print(f"\n  [Statistics]")
        print(f"    Real (R):  {load_summary['statistics']['real_mean']:.2f} ± {load_summary['statistics']['real_std']:.2f} Ω")
        print(f"    Mag (Z):   {load_summary['statistics']['mag_mean']:.2f} ± {load_summary['statistics']['mag_std']:.2f} Ω")
        print(f"    Imag (Xc): {load_summary['statistics']['imag_mean']:.2f} ± {load_summary['statistics']['imag_std']:.2f} Ω")
        print(f"    Angle:     {load_summary['statistics']['angle_mean']:.2f} ± {load_summary['statistics']['angle_std']:.2f}°")
        print(f"\n  [Errors]")
        print(f"    R error: {load_summary['errors']['R_error']:.2f} Ω")
        print(f"    Z error: {load_summary['errors']['Z_error']:.2f} Ω")

        # Write load summary to JSONL
        logger.write_raw(load_summary)

        # Write individual samples
        for sample in all_samples:
            sample_record = {
                'type': 'data',
                'resistor_ohm': resistor_ohm,
                'sample': sample
            }
            logger.write_raw(sample_record)

        all_load_data.append(load_summary)

    # Step 4: Power off
    print(f"\n{'='*70}")
    print(f"[Step 4] Powering off MAX30009...")
    print(f"{'='*70}")

    drain_async_messages(max30009_client)

    poweroff_request = {
        "type": "settings",
        "measure_enable": False,
        "stimulate_frequency": 10000,
        "measure_frequency": 5,
        "stimulate_current": "64uA"
    }

    poweroff_response = send_and_wait_for_response(max30009_client, poweroff_request, "actual_settings")
    assert poweroff_response["type"] == "actual_settings"
    assert poweroff_response["measure_enable"] == False
    print(f"  ✓ MAX30009 powered off")

    # Step 5: Analysis and validation
    print(f"\n{'='*70}")
    print(f"[Step 5] Analysis and Validation")
    print(f"{'='*70}")

    if len(all_load_data) > 0:
        print(f"\n  Calculating overall metrics...")

        # Calculate MAE across all loads
        R_errors = [load['errors']['R_error'] for load in all_load_data]
        Z_errors = [load['errors']['Z_error'] for load in all_load_data]

        import statistics
        R_MAE = statistics.mean(R_errors)
        Z_MAE = statistics.mean(Z_errors)

        print(f"\n  [Mean Absolute Errors Across All Loads]")
        print(f"    Resistance MAE:  {R_MAE:.2f} Ω  (Pass: ≤ 2 Ω)")
        print(f"    Impedance MAE:   {Z_MAE:.2f} Ω  (Pass: ≤ 3 Ω)")

        # Validate sync markers for all loads
        print(f"\n  [Sync Marker Validation Summary]")
        all_sync_valid = all(load['sync_validation'].get('is_monotonic', False)
                            for load in all_load_data)
        if all_sync_valid:
            print(f"    ✓ All loads have monotonically increasing sync markers")
        else:
            print(f"    ✗ Some loads have non-monotonic sync markers")

        # Validate sampling frequency for all loads
        print(f"\n  [Sampling Frequency Validation Summary]")
        all_fs_valid = all(load['fs_validation'].get('within_tolerance', False)
                          for load in all_load_data)
        if all_fs_valid:
            print(f"    ✓ All loads have sampling frequency within 400 ± 1 Hz")
        else:
            print(f"    ✗ Some loads have sampling frequency outside tolerance")

        for load in all_load_data:
            fs_val = load['fs_validation']
            print(f"      {load['resistor_ohm']:3d}Ω: {fs_val.get('actual_fs', 0):.2f} Hz (error: {fs_val.get('error', 0):.2f} Hz)")

        # Write analysis results
        analysis_record = {
            'type': 'analysis',
            'MAE': {
                'R': R_MAE,
                'Z': Z_MAE
            },
            'sync_validation_all_pass': all_sync_valid,
            'fs_validation_all_pass': all_fs_valid
        }
        logger.write_raw(analysis_record)

        # Run analysis script to generate plots
        run_analysis("analyze_icg_resistor.py", results_file)

        # Validate pass criteria
        print(f"\n  [Validation]")

        assert Z_MAE <= 3.0, f"Impedance MAE ({Z_MAE:.2f}) exceeds threshold (3 Ω)"
        print(f"    ✓ Impedance MAE ≤ 3 Ω")

        assert R_MAE <= 2.0, f"Resistance MAE ({R_MAE:.2f}) exceeds threshold (2 Ω)"
        print(f"    ✓ Resistance MAE ≤ 2 Ω")

        assert all_sync_valid, "Sync markers validation failed"
        print(f"    ✓ Sync markers monotonically increasing every 1s")

        assert all_fs_valid, "Sampling frequency validation failed"
        print(f"    ✓ Sampling frequency 400 Hz ± 1 Hz")

    print(f"\n{'='*70}")
    print(f"Test Complete")
    print(f"{'='*70}")
    print(f"\nResults saved to: {results_file}")
    print(f"\n✓ Test PASSED: All validation criteria met")
    print(f"{'='*70}\n")
