# Sensor Firmware for Raspberry Pi CM4

Medical/biometric sensor firmware providing hardware interface services for Raspberry Pi CM4. The firmware runs as separate services communicating via JSON over TCP sockets.

## Quick Start

### Prerequisites

**Hardware:**
- Raspberry Pi CM4 with network connectivity
- Connected sensors: ADS1293 (ECG), MAX30009 (BIOZ), WS2812 (LED)
- For hardware tests: ECG simulator for BPM validation

**Software (on your laptop):**
- Docker (for building ARM binaries)
- Python 3.7+ with pip
- Network access to CM4

**Ports Required:**
- 1293 (ADS1293 ECG service)
- 30009 (MAX30009 BIOZ service)
- 2812 (WS2812 LED service)
- 501 (Power service)

### First-Time Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd sensor-firmware-build

# 2. Set your CM4's IP address
export PI_IP=192.168.x.x  # Replace with your CM4's IP

# 3. Create Python virtual environment on your laptop
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r tests/requirements.txt

# 4. Build and deploy firmware to CM4 (requires Docker)
./scripts/build-and-deploy.sh

# 5. Verify services are running on CM4
ssh pi@$PI_IP systemctl status spi-service
```

## Running Tests

### Important: Tests Run on Your Laptop, Not on CM4

The test architecture is designed to run pytest **on your laptop** while connecting to firmware services running on the CM4 via TCP/IP. No Python environment is needed on the CM4.

```
┌─────────────────┐                          ┌──────────────────┐
│  Your Laptop    │                          │  CM4 (Pi)        │
│                 │                          │                  │
│  pytest         │  ──── TCP/IP ───────>    │  Firmware        │
│  (tests run     │       (ports 1293,       │  Services        │
│   here)         │        30009, etc.)      │  (run here)      │
│                 │                          │                  │
│  Results saved  │                          │  No Python       │
│  locally        │                          │  needed          │
└─────────────────┘                          └──────────────────┘
```

### Quick Smoke Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run quick validation tests (< 5 min)
./scripts/run-tests-remote.sh $PI_IP -m quick
```

### Hardware Integration Tests

```bash
# ADS1293 ECG 60-second test
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg.py

# ADS1293 1-hour ECG test with BPM validation (requires ECG simulator)
# Run for specific BPM: 30, 60, 120, or 180
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg_long.py -k "bpm-60"

# Run all BPM tests (takes 4 hours)
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/test_ads1293_ecg_long.py
```

### Firmware-Application Integration Tests

```bash
# Test invalid parameter handling
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_invalid_params.py

# Test specific parameter validation
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_invalid_params.py::test_invalid_r2_rate
```

### Running Tests by Markers

```bash
# ADS1293 tests only
./scripts/run-tests-remote.sh $PI_IP -m ads1293

# MAX30009 tests only
./scripts/run-tests-remote.sh $PI_IP -m max30009

# Quick tests only (< 5 min)
./scripts/run-tests-remote.sh $PI_IP -m quick

# Long duration tests (> 1 hour)
./scripts/run-tests-remote.sh $PI_IP -m long

# Invalid parameter tests
./scripts/run-tests-remote.sh $PI_IP -m invalid_params
```

### Advanced Pytest Options

```bash
# Run with verbose output
./scripts/run-tests-remote.sh $PI_IP tests/hardware-integration/ -vv

# Stop on first failure
./scripts/run-tests-remote.sh $PI_IP tests/ --maxfail=1

# Run specific test function
./scripts/run-tests-remote.sh $PI_IP tests/fw-app-integration/test_ads1293_invalid_params.py::test_invalid_r3_rate

# Generate HTML report
./scripts/run-tests-remote.sh $PI_IP tests/ --html=report.html --self-contained-html
```

### Restarting Services Before Tests

If you've deployed new firmware or want to ensure a clean state:

```bash
# Restart services and run tests
./scripts/run-tests-remote.sh $PI_IP --restart-services -m quick
```

## Development Workflow

### Complete Development Cycle

```bash
# 1. Make code changes to firmware

# 2. Build and deploy new firmware to CM4
./scripts/build-and-deploy.sh

# 3. Run tests from your laptop
./scripts/run-tests-remote.sh $PI_IP tests/

# 4. Review results (saved locally on your laptop)
ls /tmp/test-results/
```

### What build-and-deploy.sh Does

1. Builds ARM binaries using Docker cross-compilation
2. Copies binaries to CM4: `/opt/sensor-firmware/bin/`
3. Installs systemd service files
4. Enables and starts services automatically
5. Services run on CM4 startup

### What run-tests-remote.sh Does

1. Copies test files to CM4: `/tmp/tests/` (for reference only)
2. Sets `PI_IP` environment variable
3. **Runs pytest ON YOUR LAPTOP** (not on CM4)
4. Tests connect to CM4 services via TCP/IP
5. Results saved locally on your laptop: `/tmp/test-results/`

**Important:** `run-tests-remote.sh` does **NOT** deploy firmware binaries. For new firmware, run `build-and-deploy.sh` first.

## Test Configuration

### Test Parameters

Edit [tests/config/test_config.yaml](tests/config/test_config.yaml) to configure:

```yaml
# Service connection (update with your CM4's IP)
services:
  ads1293:
    host: "127.0.0.1"  # Change to PI_IP for remote testing
    port: 1293

# ADS1293 ECG test parameters
ads1293_ecg:
  sampling_frequency: 400
  r2_rate: 4           # For 400 Hz: R2=4, R3=16
  r3_rate: 16
  bpm_values: [30, 60, 120, 180]
  duration_sec: 60
  long_duration_sec: 3600
  polling_interval_sec: 1.0

# Pass/fail thresholds
thresholds:
  ads1293:
    voltage_error_low_uv: 25        # for ref ≤ 500 µV
    voltage_error_high_uv: 40       # for ref > 500 µV
    voltage_error_high_pct: 5
    bpm_error_absolute: 3           # ±3 bpm
    bpm_error_pct: 1                # ±1%

  sampling:
    frequency_error_hz: 1
```

### Test Markers Reference

| Marker | Description | Example |
|--------|-------------|---------|
| `@pytest.mark.hardware` | Requires actual hardware | ECG simulator tests |
| `@pytest.mark.ads1293` | ADS1293 ECG tests | ECG data collection |
| `@pytest.mark.max30009` | MAX30009 BIOZ tests | Impedance measurements |
| `@pytest.mark.quick` | Fast tests (< 5 min) | API validation |
| `@pytest.mark.long` | Long tests (> 1 hour) | 1-hour ECG recording |
| `@pytest.mark.invalid_params` | Invalid parameter tests | Edge case validation |
| `@pytest.mark.fw_app` | Firmware-app integration | Protocol tests |

## Test Results

### Output Locations

All test results are saved locally on your laptop:

```
/tmp/test-results/
├── data/                    # Raw data files (.jsonl)
│   ├── test_011_ecg_1hr_bpm60.jsonl
│   └── test_001_ecg_60s.jsonl
├── plots/                   # Visualization (if enabled)
├── logs/                    # Test execution logs
└── report.html             # HTML test report (if --html used)
```

### Viewing Test Data

Test data is saved in JSONL (JSON Lines) format for easy analysis:

```python
import json

# Read test data
with open('/tmp/test-results/data/test_011_ecg_1hr_bpm60.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        if record['type'] == 'data':
            # Process ECG samples
            samples = record['data']
        elif record['type'] == 'metadata':
            # Review test metrics
            metrics = record
```

## Troubleshooting

### Connection Refused on Ports

**Problem:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Solutions:**
```bash
# Check if services are running on CM4
ssh pi@$PI_IP systemctl status spi-service

# Restart services
./scripts/run-tests-remote.sh $PI_IP --restart-services

# Check if ports are accessible
nc -zv $PI_IP 1293  # Should connect successfully
```

### Import Errors in Tests

**Problem:** `ImportError: No module named 'pytest'` or similar

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # You should see (venv) in prompt

# Reinstall dependencies
pip install -r tests/requirements.txt
```

### Sampling Frequency Issues

**Problem:** Sampling frequency is 333 Hz instead of 400 Hz

**Cause:** Incorrect R2/R3 rate configuration or polling interval

**Solution:**
- Check [tests/config/test_config.yaml](tests/config/test_config.yaml)
- For 400 Hz: `r2_rate: 4`, `r3_rate: 16`, `polling_interval_sec: 1.0`
- Formula: `fs = 128000 / (R1 × R2 × R3)` = `128000 / (4 × 4 × 16)` = 500 Hz

### Extra Samples in First Response

**Problem:** First `get_data` response contains ~800 extra samples

**Cause:** Firmware buffer accumulates samples during 2-second stabilization period

**Solution:** Tests automatically flush the buffer before data collection:
```python
time.sleep(2.0)  # Stabilization
flush_response = get_sensor_data(client)  # Discard accumulated samples
# Now start clean collection
```

### Python Not Found on CM4

**This is expected!** Tests run on your laptop, not on the CM4. The CM4 only needs the compiled firmware binaries, not Python.

## Building Firmware

### Docker-Based Cross-Compilation (Recommended)

```bash
# Build for ARM target
docker build --target artifacts -t sensor-firmware-build -f docker/Dockerfile .
docker create --name temp-container sensor-firmware-build
docker cp temp-container:/. build-output/bin/
docker rm temp-container
```

### Native CMake Build

```bash
# For ARM cross-compilation
mkdir -p build-output
cd build-output
cmake .. -DCMAKE_TOOLCHAIN_FILE=../docker/arm-toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build . -j$(nproc)

# For native development (won't run on CM4)
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .
```

## Architecture

### Service-Based Design

The firmware consists of independent services running as separate processes:

1. **spi-service** (ports 1293, 30009, 2812)
   - ADS1293: ECG/biopotential sensor
   - MAX30009: Bio-impedance sensor
   - WS2812: RGB LED strip control

2. **power-service** (port 501)
   - Battery monitoring
   - Power management
   - Button handling

### JSON Protocol

All services use newline-delimited JSON over TCP:

```json
// Configure sensor
{"type": "settings", "enable_conversion": true, "R2_rate": 4, "R3_rate": 16}

// Get data
{"type": "get_data"}

// Response
{"type": "data", "timestamp": "2025-01-10 12:34:56", "data": [[ch1, ch2, ch3], ...]}
```

See [JSON_PROTOCOL_REFERENCE.md](JSON_PROTOCOL_REFERENCE.md) for complete API documentation.

## Documentation

- [CLAUDE.md](CLAUDE.md) - Development guide for Claude Code
- [JSON_PROTOCOL_REFERENCE.md](JSON_PROTOCOL_REFERENCE.md) - Complete JSON API reference
- [tests/README.md](tests/README.md) - Detailed test suite documentation

## Version Management

Version is stored in the [VERSION](VERSION) file at repository root. Update this file to change firmware version.

## License

[Add license information here]

## Contributing

[Add contribution guidelines here]
