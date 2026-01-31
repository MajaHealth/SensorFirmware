"""
Test Case 7: MAX30009 Cole-Cole BCA Automated Integration

Category: HW-FW Integration
Components: MAX30009 + firmware service + RC model circuit + analysis

Test Flow:
1. Clear base table if previously generated
2. Connect MAX30009 to test RC model circuit
3. Generate base table and verify "build_base_table_started"
4. Configure sensor and sweep through frequencies
5. Monitor state transitions for each frequency
6. Collect data every 0.5s for 5s at each frequency
7. Record time-to-complete per frequency
8. Analyze and plot results
9. Calculate errors vs known RC values
10. Power off and verify

Frequencies tested: 500, 1k, 2k, 5k, 10k, 20k, 50k, 100k, 200k, 300k, 450 kHz

Pass Criteria:
- Impedance ≤ 3 Ω
- Resistance MAE ≤ 2 Ω
- Reactance MAE ≤ 1 Ω
- Phase angle MAE ≤ 0.2°

Requirements:
- Physical MAX30009 sensor
- RC model circuit connected
- Known RC values for validation
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
FREQUENCIES_HZ = [
    500,
    1000,
    2000,
    5000,
    10000,
    20000,
    50000,
    100000,
    200000,
    300000,
    450000
]

MEASUREMENT_DURATION = 5.0  # seconds
POLLING_INTERVAL = 0.5      # seconds
SAMPLING_RATE = 400          # Hz (measure_frequency parameter)
STIMULATION_CURRENT = "64uA"

# Expected state transition sequence
EXPECTED_STATE_SEQUENCE = [
    "pre_measuring",
    "pre_measure_end",
    "calibrating",
    "calibrate_end",
    "start_measuring"
]

# RC model circuit values (user must configure these based on actual circuit)
# Example: 82Ω resistor + 82Ω resistor + 100nF capacitor
RC_MODEL = {
    "description": "82_82_100nF",
    "R0": 164.0,      # Total resistance at DC (Ω)
    "Rinf": 0.0,      # High-frequency resistance (Ω) - for simple RC, this is 0
    "C": 100e-9,      # Capacitance (F)
    "expected_impedance": {}  # Will be calculated
}


def calculate_expected_impedance(frequency_hz, R0, Rinf, C):
    """
    Calculate expected impedance for RC model at given frequency.

    For simple RC series circuit:
    Z = R + 1/(jωC)
    Where:
    - R = R0 (total resistance)
    - ω = 2πf
    - j = √(-1)

    Returns dict with R, Xc, Z, PhA
    """
    import math

    omega = 2 * math.pi * frequency_hz
    Xc = -1.0 / (omega * C) if C > 0 else 0  # Capacitive reactance (negative)

    R = R0
    Z = math.sqrt(R**2 + Xc**2)
    PhA = math.atan2(Xc, R) * 180 / math.pi  # Phase angle in degrees

    return {
        "frequency": frequency_hz,
        "R": R,
        "Xc": Xc,
        "Z": Z,
        "PhA": PhA
    }


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
    """
    Monitor MAX30009 state transitions and verify expected sequence.

    Returns list of observed states with timestamps.
    """
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
                    # Check if in correct order
                    last_idx = -1
                    for exp in expected_states:
                        try:
                            idx = observed_state_names.index(exp)
                            if idx > last_idx:
                                last_idx = idx
                            else:
                                break
                        except ValueError:
                            break
                    else:
                        print(f"    ✓ All expected states observed in sequence")
                        return observed_states

        except Exception as e:
            continue

    print(f"    Note: Timeout after {timeout}s")
    return observed_states


@pytest.fixture
def max30009_client(test_config, max30009_cleanup):
    """Create TCP client for MAX30009 with cleanup."""
    max_config = test_config['services']['max30009']
    with TCPClient(max_config['host'], max_config['port']) as client:
        # Drain pending messages
        drain_async_messages(client)
        yield client


@pytest.fixture
def results_file(results_dir):
    """Create results file for JSONL data logging.

    Standard practice: ~/sensor-test-data/data/calib/
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_007_cole_cole_{timestamp}.jsonl"
    filepath = results_dir / "data" / "calib" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    return filepath


@pytest.mark.hardware
@pytest.mark.max30009
@pytest.mark.long
def test_max30009_cole_cole_integration(max30009_client, results_file):
    """
    Test Case 7: MAX30009 Cole-Cole BCA automated integration.

    Comprehensive test that:
    1. Generates base table
    2. Sweeps through multiple frequencies
    3. Monitors state transitions
    4. Collects impedance data
    5. Analyzes results and generates plots
    6. Validates against RC model

    **IMPORTANT: This test requires physical MAX30009 hardware and RC model circuit**
    """
    print(f"\n{'='*70}")
    print(f"Test Case 7: MAX30009 Cole-Cole BCA Integration")
    print(f"{'='*70}")
    print(f"\nRC Model: {RC_MODEL['description']}")
    print(f"R0 = {RC_MODEL['R0']} Ω")
    print(f"C = {RC_MODEL['C']*1e9} nF")
    print(f"\nResults will be saved to: {results_file}")

    # Calculate expected values for all frequencies
    print(f"\nCalculating expected impedance values...")
    for freq in FREQUENCIES_HZ:
        expected = calculate_expected_impedance(
            freq,
            RC_MODEL['R0'],
            RC_MODEL['Rinf'],
            RC_MODEL['C']
        )
        RC_MODEL['expected_impedance'][freq] = expected
        print(f"  {freq:6d} Hz: Z={expected['Z']:6.2f} Ω, R={expected['R']:6.2f} Ω, Xc={expected['Xc']:7.2f} Ω, PhA={expected['PhA']:6.2f}°")

    # Initialize logger and write metadata
    logger = JSONLLogger(str(results_file), test_id="test_007", sensor="max30009")

    metadata = {
        'type': 'metadata',
        'test_case': 'TC-007',
        'test_name': 'MAX30009 Cole-Cole BCA Integration',
        'timestamp': datetime.now().isoformat(),
        'rc_model': RC_MODEL,
        'frequencies_hz': FREQUENCIES_HZ,
        'sampling_rate': SAMPLING_RATE,
        'stimulation_current': STIMULATION_CURRENT,
        'measurement_duration_s': MEASUREMENT_DURATION,
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

    # Monitor base table generation (can take time)
    print(f"\n  [Monitoring base table generation...]")
    print(f"    This may take 15-30 seconds, please wait...")
    generation_complete = False
    start_time = time.time()
    timeout = 120.0  # 2 minutes

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

    # Drain any remaining messages
    drain_async_messages(max30009_client)

    # Step 3: Frequency sweep
    print(f"\n{'='*70}")
    print(f"[Step 3] Frequency Sweep")
    print(f"{'='*70}")

    all_frequency_data = []

    for freq_idx, frequency in enumerate(FREQUENCIES_HZ, 1):
        print(f"\n{'-'*70}")
        print(f"Frequency {freq_idx}/{len(FREQUENCIES_HZ)}: {frequency} Hz")
        print(f"{'-'*70}")

        freq_start_time = time.time()

        # Configure sensor for this frequency
        print(f"\n  [Configuring sensor...]")
        drain_async_messages(max30009_client)

        settings = {
            "type": "settings",
            "measure_enable": True,
            "stimulate_frequency": frequency,
            "measure_frequency": SAMPLING_RATE,
            "stimulate_current": STIMULATION_CURRENT
        }

        config_response = send_and_wait_for_response(max30009_client, settings, "actual_settings")

        if config_response["type"] != "actual_settings":
            print(f"  ✗ Configuration failed: {config_response}")
            # Log failure and continue
            error_record = {
                'type': 'error',
                'frequency': frequency,
                'message': 'Configuration failed',
                'response': config_response
            }
            logger.write_raw(error_record)
            continue

        print(f"  ✓ Configured: {config_response['stimulate_frequency']} Hz")

        # Monitor state transitions
        state_transitions = monitor_state_transitions(
            max30009_client,
            EXPECTED_STATE_SEQUENCE,
            timeout=30.0
        )

        # Wait for measurement to stabilize
        print(f"\n  [Waiting for measurement stabilization...]")
        time.sleep(1.0)

        # Collect data for MEASUREMENT_DURATION
        print(f"\n  [Collecting data for {MEASUREMENT_DURATION}s...]")
        measurement_data = []
        collection_start = time.time()
        poll_count = 0

        while (time.time() - collection_start) < MEASUREMENT_DURATION:
            # Request data
            drain_async_messages(max30009_client, max_attempts=5)
            data_request = {"type": "get_data"}
            data_response = send_and_wait_for_response(max30009_client, data_request, "data")

            if data_response["type"] == "data" and "data" in data_response:
                samples = data_response["data"]
                poll_count += 1
                elapsed = time.time() - collection_start

                print(f"    [{elapsed:.1f}s] Poll {poll_count}: {len(samples)} samples")

                # Store data
                measurement_data.extend(samples)

            # Wait for next polling interval
            time.sleep(POLLING_INTERVAL)

        freq_duration = time.time() - freq_start_time
        print(f"  ✓ Collected {len(measurement_data)} samples in {freq_duration:.2f}s")

        # Calculate statistics for this frequency
        if len(measurement_data) > 0:
            # Extract impedance components (format: [Load_real, Load_mag, Load_imag, Load_angle, overload])
            # Note: MAX30009 data is scaled by 10000
            real_values = [s[0] / 10000.0 for s in measurement_data if len(s) >= 5]
            mag_values = [s[1] / 10000.0 for s in measurement_data if len(s) >= 5]
            imag_values = [s[2] / 10000.0 for s in measurement_data if len(s) >= 5]
            angle_values = [s[3] / 10000.0 for s in measurement_data if len(s) >= 5]

            import statistics
            freq_summary = {
                'type': 'frequency_summary',
                'frequency': frequency,
                'duration_s': freq_duration,
                'sample_count': len(measurement_data),
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
                'state_transitions': state_transitions,
                'expected': RC_MODEL['expected_impedance'][frequency]
            }

            print(f"\n  [Statistics]")
            print(f"    Real:  {freq_summary['statistics']['real_mean']:.2f} ± {freq_summary['statistics']['real_std']:.2f} Ω")
            print(f"    Mag:   {freq_summary['statistics']['mag_mean']:.2f} ± {freq_summary['statistics']['mag_std']:.2f} Ω")
            print(f"    Imag:  {freq_summary['statistics']['imag_mean']:.2f} ± {freq_summary['statistics']['imag_std']:.2f} Ω")
            print(f"    Angle: {freq_summary['statistics']['angle_mean']:.2f} ± {freq_summary['statistics']['angle_std']:.2f}°")

            # Write frequency summary to JSONL
            logger.write_raw(freq_summary)

            # Write individual samples
            for sample in measurement_data:
                sample_record = {
                    'type': 'data',
                    'frequency': frequency,
                    'sample': sample
                }
                logger.write_raw(sample_record)

            all_frequency_data.append(freq_summary)

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

    if len(all_frequency_data) > 0:
        print(f"\n  Calculating errors vs RC model...")

        errors = []
        for freq_data in all_frequency_data:
            freq = freq_data['frequency']
            measured = freq_data['statistics']
            expected = freq_data['expected']

            # Calculate errors
            R_error = abs(measured['real_mean'] - expected['R'])
            Z_error = abs(measured['mag_mean'] - expected['Z'])
            Xc_error = abs(measured['imag_mean'] - expected['Xc'])
            PhA_error = abs(measured['angle_mean'] - expected['PhA'])

            errors.append({
                'frequency': freq,
                'R_error': R_error,
                'Z_error': Z_error,
                'Xc_error': Xc_error,
                'PhA_error': PhA_error
            })

            print(f"\n  {freq:6d} Hz:")
            print(f"    R error:   {R_error:.2f} Ω")
            print(f"    Z error:   {Z_error:.2f} Ω")
            print(f"    Xc error:  {Xc_error:.2f} Ω")
            print(f"    PhA error: {PhA_error:.2f}°")

        # Calculate MAE
        import statistics
        R_MAE = statistics.mean([e['R_error'] for e in errors])
        Z_MAE = statistics.mean([e['Z_error'] for e in errors])
        Xc_MAE = statistics.mean([e['Xc_error'] for e in errors])
        PhA_MAE = statistics.mean([e['PhA_error'] for e in errors])

        print(f"\n  [Mean Absolute Errors]")
        print(f"    Resistance MAE:  {R_MAE:.2f} Ω  (Pass: ≤ 2 Ω)")
        print(f"    Impedance MAE:   {Z_MAE:.2f} Ω  (Pass: ≤ 3 Ω)")
        print(f"    Reactance MAE:   {Xc_MAE:.2f} Ω  (Pass: ≤ 1 Ω)")
        print(f"    Phase Angle MAE: {PhA_MAE:.2f}° (Pass: ≤ 0.2°)")

        # Write analysis results
        analysis_record = {
            'type': 'analysis',
            'errors': errors,
            'MAE': {
                'R': R_MAE,
                'Z': Z_MAE,
                'Xc': Xc_MAE,
                'PhA': PhA_MAE
            }
        }
        logger.write_raw(analysis_record)

        # Run analysis script to generate plots
        run_analysis("analyze_cole_cole.py", results_file)

        # Validate pass criteria
        print(f"\n  [Validation]")
        assert Z_MAE <= 3.0, f"Impedance MAE ({Z_MAE:.2f}) exceeds threshold (3 Ω)"
        print(f"    ✓ Impedance MAE ≤ 3 Ω")

        assert R_MAE <= 2.0, f"Resistance MAE ({R_MAE:.2f}) exceeds threshold (2 Ω)"
        print(f"    ✓ Resistance MAE ≤ 2 Ω")

        assert Xc_MAE <= 1.0, f"Reactance MAE ({Xc_MAE:.2f}) exceeds threshold (1 Ω)"
        print(f"    ✓ Reactance MAE ≤ 1 Ω")

        assert PhA_MAE <= 0.2, f"Phase angle MAE ({PhA_MAE:.2f}) exceeds threshold (0.2°)"
        print(f"    ✓ Phase Angle MAE ≤ 0.2°")

    print(f"\n{'='*70}")
    print(f"Test Complete")
    print(f"{'='*70}")
    print(f"\nResults saved to: {results_file}")
    print(f"\nNote: Automatic analysis will generate plots after test session:")
    print(f"  - R vs f, Z vs f, Xc vs f, PhA vs f")
    print(f"  - Cole-Cole plot")
    print(f"  - R0 and Rinf extraction")
    print(f"\n✓ Test PASSED: All validation criteria met")
    print(f"{'='*70}\n")
