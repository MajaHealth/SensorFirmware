# Unit Tests

Unit tests for firmware components that test individual functions and modules in isolation.

## Directory Structure

```
unit_tests/
├── power-service/          # Power service unit tests
│   ├── test_106_soft_shutdown_denied.py
│   └── TEST_106_GUIDE.md
├── spi-service/            # SPI service unit tests
├── gpio/                   # GPIO-related unit tests
├── shutdown/               # Shutdown handling tests
├── hw_component/           # Hardware component tests
│   ├── test_030_cm4_enumeration.py
│   ├── test_041_usb_keyboard_mouse.py
│   └── TEST_030_GUIDE.md
├── fw_hw_in_loop/          # Firmware hardware-in-loop tests
│   ├── test_102_switch_state_readback.py
│   └── TEST_102_GUIDE.md
└── common/                 # Shared unit test utilities
```

## Test Categories

### Power Service Tests
- **Test #106:** Soft shutdown denied/timeout behavior
  - Tests firmware's handling of denied shutdown requests
  - Tests firmware's handling of ACK timeouts
  - Verifies graceful cancellation of shutdown

### Hardware Component Tests
- **Test #30:** CM4 enumeration on PC
  - Tests CM4 USB device detection
  - Validates rpiboot enumeration
  - Verifies storage accessibility
  - Semi-automated (requires hardware setup)
- **Test #31:** eMMC detection
  - Tests eMMC storage detection on CM4
  - Validates multiple detection methods
  - Verifies eMMC is readable
  - **Fully automated** when run on CM4
- **Test #32:** OS flashing to eMMC
  - Tests OS image flashing to CM4 eMMC
  - Validates write operation and verification
  - Semi-automated (requires hardware setup)
  - **DESTRUCTIVE** (erases eMMC)
- **Test #33:** Boot verification (kernel/messages)
  - Tests CM4 boot process validation
  - Analyzes kernel messages and system journal
  - Checks for errors and expected boot messages
  - **Fully automated** when run on CM4
- **Test #35:** Internet connectivity check
  - Tests Wi-Fi internet connectivity
  - Validates DNS, ping, and HTTP/HTTPS access
  - Checks network interface and gateway
  - **Fully automated** when run on CM4 with internet
- **Test #36:** SSH accessibility
  - Tests SSH service is running and accessible
  - Validates SSH port listening and banner response
  - Checks SSH configuration and host keys
  - **Fully automated** when run on CM4 with SSH enabled
- **Test #38:** Read/write operations on storage interfaces
  - Tests read/write operations on eMMC and SD card
  - Validates data integrity with checksum verification
  - Measures storage performance (MB/s)
  - **Fully automated** when run on CM4
- **Test #39:** Data integrity verification after read/write
  - Comprehensive integrity testing with multiple cycles
  - Tests multiple file sizes (1MB, 5MB, 10MB)
  - Tests multiple data patterns (random, zeros, ones, alternating)
  - Cryptographic hash verification (SHA256)
  - **Fully automated** when run on CM4
- **Test #40:** Power cycling (retention)
  - Tests data retention across power cycles (reboots)
  - Multi-phase execution (spans multiple test runs)
  - Validates data survives 3 power cycles by default
  - Cryptographic verification after each reboot
  - **Semi-automated** (requires manual re-run after each reboot)
- **Test #41:** USB keyboard and mouse functionality
  - Tests USB keyboard and mouse detection via USB ports
  - Validates USB subsystem and Linux input subsystem
  - Multiple detection methods (lsusb, /dev/input, /proc)
  - Gracefully handles headless systems (devices optional)
  - **Fully automated** (detection-based, no interaction needed)

### Firmware Hardware-in-Loop Tests
- **Test #102:** Switch state readback (OFF/ON)
  - Tests contact-based switch connected to CM4 GPIO
  - Validates GPIO input reading for OFF and ON states
  - Multiple debounced readings to filter noise
  - Tests state transition reliability (OFF → ON → OFF)
  - Supports both RPi.GPIO library and sysfs fallback
  - **Semi-automated** (requires manual switch operation)
- **Test #103:** Press classification (short vs long)
  - Tests button press timing and classification logic
  - Measures actual press duration in milliseconds
  - Classifies short press (50ms-1s) vs long press (1s-10s)
  - Validates debouncing and timing accuracy
  - Event logging with timestamps and durations
  - **Semi-automated** (requires timed button presses)
- **Test #104:** Debounce robustness against bouncing input
  - Tests firmware debounce algorithm against noisy signals
  - Simulates realistic switch bounce (5 bounces over 20ms)
  - Verifies only 1 press detected despite 20+ raw transitions
  - Monitors GPIO with 1ms polling rate
  - Applies 50ms time-based debounce filter
  - **Partially automated** (simulated bouncing) + manual option
- **Test #105:** Soft shutdown handshake (ACK accepted)
  - Tests complete shutdown handshake between firmware and application
  - Validates GPIO switch detection triggers TCP/IP communication
  - Mock application responds with ACK after simulated cleanup (500ms delay)
  - Verifies controlled shutdown initiation (simulated, not actual)
  - Message protocol: "close" → "ACK:shutdown_complete"
  - Includes built-in MockApplication TCP server class
  - **Semi-automated** (requires manual switch press) + TCP/IP network

### GPIO Tests
- GPIO pin configuration and state management
- Switch press detection and debouncing
- Interrupt handling

### Shutdown Tests
- Shutdown state machine verification
- ACK protocol validation
- Timeout handling

## Running Unit Tests

### Run All Unit Tests
```bash
# From project root
pytest tests/unit_tests/ -v

# With verbose output
pytest tests/unit_tests/ -v -s
```

### Run Specific Test Category
```bash
# Power service tests only
pytest tests/unit_tests/power-service/ -v

# Hardware component tests only
pytest tests/unit_tests/hw_component/ -v

# FW hardware-in-loop tests only
pytest tests/unit_tests/fw_hw_in_loop/ -v

# Shutdown tests only
pytest tests/unit_tests/shutdown/ -v

# GPIO tests only
pytest tests/unit_tests/gpio/ -v
```

### Run Specific Test
```bash
# Run Test #106
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s

# Run Test #102
pytest tests/unit_tests/fw_hw_in_loop/test_102_switch_state_readback.py -v -s

# Run Test #103
pytest tests/unit_tests/fw_hw_in_loop/test_103_press_classification.py -v -s

# Run Test #104
pytest tests/unit_tests/fw_hw_in_loop/test_104_debounce_robustness.py -v -s

# Run Test #105
pytest tests/unit_tests/fw_hw_in_loop/test_105_soft_shutdown_handshake.py -v -s

# Run Test #41
pytest tests/unit_tests/hw_component/test_041_usb_keyboard_mouse.py -v -s

# Run specific test function
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py::TestSoftShutdownDenied::test_106_soft_shutdown_denied -v -s
```

### Run with Markers
```bash
# Run only hardware tests
pytest tests/unit_tests/ -m hardware -v

# Run only GPIO tests
pytest tests/unit_tests/ -m gpio -v

# Run only network tests
pytest tests/unit_tests/ -m network -v
```

## Test Markers

Unit tests use pytest markers for categorization:

- `@pytest.mark.hardware` - Requires physical hardware
- `@pytest.mark.gpio` - Tests GPIO functionality
- `@pytest.mark.network` - Tests network/TCP functionality
- `@pytest.mark.shutdown` - Tests shutdown handling
- `@pytest.mark.mock` - Uses mock objects (no hardware needed)

## Writing New Unit Tests

### Test Template

```python
#!/usr/bin/env python3
"""
Test Case #XXX: <Test Name>

Category: Unit Test
Component: <Component Name>
"""

import pytest

class TestComponentName:
    """Unit tests for <component>"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        return {
            'param1': 'value1',
            'param2': 'value2',
        }

    def setup_method(self):
        """Setup before each test method"""
        pass

    def teardown_method(self):
        """Cleanup after each test method"""
        pass

    @pytest.mark.unit
    def test_feature_name(self, test_config):
        """
        Test Case #XXX: Description

        Verifies that <feature> behaves correctly when <condition>
        """
        # Arrange

        # Act

        # Assert
        assert True
```

## Unit Test Best Practices

1. **Isolation**: Each test should be independent
2. **Fast**: Unit tests should run quickly (< 1 second each)
3. **Focused**: Test one thing per test function
4. **Repeatable**: Same result every time
5. **Clear**: Easy to understand what's being tested

## Difference from Integration Tests

| Unit Tests | Integration Tests |
|------------|-------------------|
| Test individual components | Test component interactions |
| Fast execution (< 1s) | Slower execution (seconds to minutes) |
| Mock external dependencies | Use real dependencies |
| No hardware required (usually) | May require hardware |
| Located in `unit_tests/` | Located in `fw-app-integration/`, `hardware-integration/` |

## Dependencies

Unit tests may require additional dependencies:

```bash
pip install pytest pytest-mock pytest-timeout RPi.GPIO
```

See `tests/requirements.txt` for complete list.

## Hardware Requirements

Some unit tests require physical hardware:

- **Test #106**: Requires CM4 with GPIO switch and network connectivity
- **GPIO tests**: Require CM4 with configured GPIO pins
- **Mock tests**: No hardware required

## Configuration

Unit test configuration is shared with integration tests:

- `tests/config/test_config.yaml` - Test parameters
- `tests/conftest.py` - Shared pytest fixtures

## Continuous Integration

Unit tests should be run in CI pipeline:

```yaml
# Example CI configuration
test:
  script:
    - pytest tests/unit_tests/ -v --junitxml=report.xml
```

## Test Results

Results are saved to:
- Console output (stdout)
- Test logs: `/tmp/test-results/logs/`
- JUnit XML reports (if configured)

## Support

For issues or questions:
- See main project README.md
- Check tests/README.md for integration test documentation
- Review CLAUDE.md for development guidelines
