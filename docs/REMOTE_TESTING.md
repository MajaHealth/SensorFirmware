# Remote Testing Guide

## Overview

This guide explains how to run firmware integration tests from your laptop that connect to services running on the Raspberry Pi CM4 over the network.

## Why Remote Testing?

### Traditional Approach (Slow)
```
build-and-deploy.sh with RUN_TESTS=1:
1. Build firmware on laptop
2. Transfer binaries to Pi (scp)
3. Transfer test files to Pi (rsync)
4. Create Python venv on Pi
5. Install pytest/dependencies on Pi
6. Run pytest ON Pi
7. Fetch results back to laptop (rsync)
8. Delete venv and tests on Pi
```

**Problems:**
- Every test run recreates venv and installs packages on Pi
- Pi has limited CPU/RAM for pip installs
- Network transfers waste time
- Must redo everything next time

### Remote Testing Approach (Fast)
```
run-tests-remote.sh:
1. One-time venv setup on laptop
2. Run pytest FROM laptop
3. Tests connect to Pi services over TCP
4. Results saved locally
```

**Benefits:**
- ✅ **10x faster** - No venv recreation, no file transfers
- ✅ **Less Pi resource usage** - No pip installs on Pi
- ✅ **Results already on laptop** - No rsync needed
- ✅ **Better developer experience** - Just run pytest
- ✅ **Works for all developers** - Simple script handles everything

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Laptop (WSL Ubuntu / Linux / Mac)                           │
├─────────────────────────────────────────────────────────────┤
│ 1. venv/ (created once)                                     │
│    ├─ pytest                                                │
│    ├─ numpy, scipy, etc.                                    │
│    └─ (reused for all test runs)                            │
│                                                              │
│ 2. pytest runs here                                         │
│    ├─ Test logic executes on laptop                         │
│    ├─ JSON requests sent over TCP                           │
│    └─ Responses validated on laptop                         │
│                                                              │
│ 3. Results saved here                                       │
│    └─ analysis/data/TIMESTAMP/                              │
│        ├─ test_report.html                                  │
│        └─ *.jsonl data files                                │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │ TCP/IP Network
                           │ (WiFi or Ethernet)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Raspberry Pi CM4 (192.168.29.175)                           │
├─────────────────────────────────────────────────────────────┤
│ Firmware services only:                                     │
│ ├─ spi-service (port 1293, 30009, 2812)                    │
│ └─ power-service (port 501)                                 │
│                                                              │
│ Services:                                                    │
│ 1. Listen for TCP connections                               │
│ 2. Receive JSON requests                                    │
│ 3. Control hardware (SPI, GPIO, I2C)                        │
│ 4. Send JSON responses                                      │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### On Your Laptop
- Python 3.8+ installed
- Git repository cloned
- Network access to Pi (same WiFi/LAN)

### On Raspberry Pi
- Firmware binaries deployed to `/opt/sensor-firmware/bin/`
- Services running (`spi-service`, `power-service`)
- Network accessible from laptop
- Ports 1293, 30009, 2812, 501 open

## First-Time Setup

### 1. Clone Repository (if not done)
```bash
git clone <repository-url>
cd sensor-firmware-build
```

### 2. Run Tests (Setup is Automatic!)
```bash
# Script auto-creates venv and installs dependencies on first run
./scripts/run-tests-remote.sh 192.168.29.175
```

The script will:
- ✅ Create `venv/` directory (one-time)
- ✅ Install pytest and all dependencies (one-time)
- ✅ Test connectivity to Pi
- ✅ Run tests
- ✅ Save results
- ✅ Open HTML report

### 3. Subsequent Runs (Instant)
```bash
# Venv already exists, just runs tests
./scripts/run-tests-remote.sh 192.168.29.175
```

## Usage Examples

### Basic Usage

#### Run All Tests
```bash
./scripts/run-tests-remote.sh 192.168.29.175
```

#### Run with Default IP (using wrapper)
```bash
# Uses default IP 192.168.29.175
./scripts/test.sh

# Or override with environment variable
PI_IP=192.168.1.50 ./scripts/test.sh
```

### Selective Testing

#### Run Specific Test File
```bash
./scripts/run-tests-remote.sh 192.168.29.175 tests/fw-app-integration/test_ads1293_api.py
```

#### Run Specific Test Function
```bash
./scripts/run-tests-remote.sh 192.168.29.175 \
    tests/fw-app-integration/test_ads1293_api.py::test_ads1293_settings_configuration
```

#### Run Multiple Files
```bash
./scripts/run-tests-remote.sh 192.168.29.175 \
    tests/fw-app-integration/test_ads1293_api.py \
    tests/fw-app-integration/test_max30009_api.py
```

#### Run Tests by Directory
```bash
./scripts/run-tests-remote.sh 192.168.29.175 tests/fw-app-integration/
```

### Using Test Markers

#### Quick Tests Only
```bash
./scripts/run-tests-remote.sh 192.168.29.175 -m quick
```

#### Hardware Tests
```bash
./scripts/run-tests-remote.sh 192.168.29.175 -m hardware
```

#### Device-Specific Tests
```bash
./scripts/run-tests-remote.sh 192.168.29.175 -m ads1293
./scripts/run-tests-remote.sh 192.168.29.175 -m max30009
./scripts/run-tests-remote.sh 192.168.29.175 -m power
```

### Using Test Patterns

#### Match Test Name
```bash
./scripts/run-tests-remote.sh 192.168.29.175 -k "settings"
./scripts/run-tests-remote.sh 192.168.29.175 -k "ads1293"
```

### Advanced pytest Options

#### Verbose Output
```bash
./scripts/run-tests-remote.sh 192.168.29.175 tests/ -vv
```

#### Stop on First Failure
```bash
./scripts/run-tests-remote.sh 192.168.29.175 tests/ --maxfail=1
```

#### Drop into Debugger on Failure
```bash
./scripts/run-tests-remote.sh 192.168.29.175 tests/ --pdb
```

#### Show Full Traceback
```bash
./scripts/run-tests-remote.sh 192.168.29.175 tests/ --tb=long
```

#### Combine Options
```bash
./scripts/run-tests-remote.sh 192.168.29.175 -m quick -vv --maxfail=3
```

## Workflow Examples

### Daily Development Workflow

```bash
# 1. Make code changes to firmware
vim services/spi-service/src/ADS1293_process.cpp

# 2. Build firmware
docker build --target artifacts -t sensor-firmware-build -f docker/Dockerfile .

# 3. Deploy to Pi (without tests)
scp build-output/bin/spi-service pi@192.168.29.175:/opt/sensor-firmware/bin/

# 4. Restart service on Pi
ssh pi@192.168.29.175 "sudo pkill spi-service; sudo /opt/sensor-firmware/bin/spi-service &"

# 5. Run tests from laptop (fast!)
./scripts/run-tests-remote.sh 192.168.29.175 -m ads1293
```

### Debugging a Specific Test

```bash
# Run just the failing test with verbose output
./scripts/run-tests-remote.sh 192.168.29.175 \
    tests/fw-app-integration/test_ads1293_api.py::test_ads1293_settings_configuration \
    -vv --tb=long
```

### Pre-Commit Testing

```bash
# Run quick tests before committing
./scripts/test.sh -m quick
```

### Full Regression Testing

```bash
# Run all tests
./scripts/run-tests-remote.sh 192.168.29.175
```

## Troubleshooting

### Error: "Cannot reach Pi at <IP>"

**Cause:** Pi is not accessible on network

**Solutions:**
1. Check if Pi is powered on
2. Verify Pi IP address:
   ```bash
   # On Pi:
   hostname -I
   ```
3. Test network connectivity:
   ```bash
   ping 192.168.29.175
   ```
4. Ensure laptop and Pi on same network

### Error: "Service not accessible" on port

**Cause:** Firmware services not running on Pi

**Solution:**
```bash
# SSH to Pi
ssh pi@192.168.29.175

# Check if services running
ps aux | grep -E 'spi-service|power-service'

# Check ports listening
ss -tlnp | grep -E '1293|30009|2812|501'

# Start services if not running
cd /opt/sensor-firmware/bin
sudo ./spi-service &
sudo ./power-service &
```

### Error: "No module named 'pytest'"

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Delete venv and let script recreate it
rm -rf venv
./scripts/run-tests-remote.sh 192.168.29.175
```

### Tests Pass Locally but Fail Remotely

**Cause:** Difference in hardware behavior

**Solution:**
- Check firmware version on Pi matches your build
- Verify hardware is connected properly
- Check service logs on Pi:
  ```bash
  ssh pi@192.168.29.175 "tail -f /tmp/spi-service.log"
  ```

### WSL Cannot Connect to Pi

**Cause:** Windows Firewall blocking WSL

**Solution:**
1. Disable Windows Firewall temporarily to test
2. Or add firewall rule for WSL

### HTML Report Not Opening

**Cause:** No browser opener available

**Solution:**
- Open manually: `analysis/data/<TIMESTAMP>/test_report.html`
- Or install browser opener:
  ```bash
  # WSL:
  sudo apt install wslu  # For wslview command

  # Linux:
  sudo apt install xdg-utils  # For xdg-open command
  ```

## Comparison: build-and-deploy.sh vs run-tests-remote.sh

| Feature | build-and-deploy.sh | run-tests-remote.sh |
|---------|---------------------|---------------------|
| **Test execution location** | On Pi | On laptop |
| **Venv creation** | Every time on Pi | Once on laptop |
| **Package installation** | Every time on Pi | Once on laptop |
| **File transfers** | Tests to Pi, results back | None |
| **Speed** | Slow (~2-3 min) | Fast (~10-30 sec) |
| **Results location** | Fetched to laptop | Already on laptop |
| **Pi resource usage** | High (pip, pytest) | Low (firmware only) |
| **When to use** | Full build+deploy+test | Quick test iterations |

## Advanced Topics

### Using Environment Variables

Instead of passing Pi IP as argument, use environment variable:

```bash
export PI_TARGET_IP=192.168.29.175
pytest tests/ -v
```

This allows running pytest directly without the wrapper script.

### Running from IDE

Configure your IDE (VSCode, PyCharm) to run pytest with:
- Working directory: repository root
- Environment variable: `PI_TARGET_IP=192.168.29.175`
- Python interpreter: `venv/bin/python`

### Multi-Pi Testing

Test against multiple Pi devices:

```bash
# Test Pi 1
./scripts/run-tests-remote.sh 192.168.1.21 -m quick

# Test Pi 2
./scripts/run-tests-remote.sh 192.168.1.22 -m quick
```

### Continuous Integration

For CI/CD pipelines, use the environment variable approach:

```yaml
# .github/workflows/test.yml
- name: Run Integration Tests
  env:
    PI_TARGET_IP: ${{ secrets.PI_IP }}
  run: |
    pytest tests/ -v --html=test_report.html
```

## Tips and Best Practices

1. **Start services before testing**
   - Saves time waiting for error messages
   - Script will warn if services not running

2. **Use test markers for faster iterations**
   - `-m quick` for rapid feedback
   - `-m hardware` for full validation

3. **Run specific tests during debugging**
   - Faster than running entire suite
   - Use `::function_name` syntax

4. **Keep venv updated**
   - If requirements.txt changes:
     ```bash
     source venv/bin/activate
     pip install -r tests/requirements.txt
     ```

5. **Check results directory regularly**
   - Clean old results: `rm -rf analysis/data/202601*`
   - Results include HTML reports and data files

6. **Use verbose mode when debugging**
   - `-vv` shows more details
   - `--tb=long` shows full tracebacks

## Getting Help

If you encounter issues:

1. Check this documentation
2. Check `CLAUDE.md` for quick reference
3. Review error messages carefully
4. Test Pi connectivity manually (`ping`, `nc`)
5. Check Pi service logs

## See Also

- `CLAUDE.md` - Quick reference for all commands
- `tests/README.md` - Test structure and organization
- `docs/COMPLETE_JSON_API_REFERENCE.md` - Firmware API documentation
