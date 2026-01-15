# Unit Tests Quick Start Guide

Quick reference for running unit tests separate from integration tests.

## Directory Structure

```
tests/
├── unit_tests/              ← NEW: Unit tests (isolated component testing)
│   ├── power-service/
│   │   ├── test_106_soft_shutdown_denied.py
│   │   └── TEST_106_GUIDE.md
│   ├── spi-service/
│   ├── gpio/
│   ├── shutdown/
│   └── README.md
│
├── fw-app-integration/      ← Integration tests (firmware-app)
├── hardware-integration/    ← Integration tests (hardware)
├── common/                  ← Shared utilities
└── config/                  ← Test configuration
```

## Key Differences

| Aspect | Unit Tests | Integration Tests |
|--------|------------|-------------------|
| **Location** | `tests/unit_tests/` | `tests/fw-app-integration/`, `tests/hardware-integration/` |
| **Purpose** | Test individual components | Test component interactions |
| **Speed** | Fast (< 1s typically) | Slower (seconds to hours) |
| **Dependencies** | Mock objects | Real services/hardware |
| **Markers** | `@pytest.mark.unit` | `@pytest.mark.fw_app`, `@pytest.mark.hardware` |

## Quick Commands

### Run Unit Tests Only
```bash
# All unit tests
pytest tests/unit_tests/ -v

# Power service unit tests
pytest tests/unit_tests/power-service/ -v

# Specific test
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

### Run Integration Tests Only
```bash
# FW-APP integration tests
pytest tests/fw-app-integration/ -v

# Hardware integration tests
pytest tests/hardware-integration/ -v

# Using remote script
./scripts/run-tests-remote.sh $PI_IP -m quick
```

### Run All Tests
```bash
# From tests directory
pytest -v

# From project root
pytest tests/ -v
```

## Test Markers

Use markers to run specific test categories:

```bash
# Unit tests only
pytest -m unit -v

# Integration tests only
pytest -m "fw_app or hardware" -v

# Hardware tests only
pytest -m hardware -v

# GPIO tests (can be unit or integration)
pytest -m gpio -v

# Shutdown handling tests
pytest -m shutdown -v
```

## Current Unit Tests

### Test #106: Soft Shutdown Denied/Timeout
**File:** `tests/unit_tests/power-service/test_106_soft_shutdown_denied.py`
**Guide:** `tests/unit_tests/power-service/TEST_106_GUIDE.md`

**Quick run:**
```bash
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

**Duration:** ~30-40 seconds
**Manual interaction:** Yes (2x switch press)
**Markers:** `unit`, `hardware`, `gpio`, `network`, `shutdown`

## Adding New Unit Tests

### Step 1: Choose Directory
Place test in appropriate subdirectory:
- Power service tests → `tests/unit_tests/power-service/`
- SPI service tests → `tests/unit_tests/spi-service/`
- GPIO tests → `tests/unit_tests/gpio/`
- Shutdown tests → `tests/unit_tests/shutdown/`

### Step 2: Name Your Test
Follow naming convention:
```
test_<number>_<descriptive_name>.py
```
Example: `test_107_hard_shutdown.py`

### Step 3: Use Template
```python
#!/usr/bin/env python3
"""
Test Case #XXX: <Test Name>
Category: Unit Test
Component: <Component Name>
"""

import pytest

class Test<ComponentName>:
    """Unit tests for <component>"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        return {}

    def setup_method(self):
        """Setup before each test"""
        pass

    def teardown_method(self):
        """Cleanup after each test"""
        pass

    @pytest.mark.unit
    @pytest.mark.<component>
    def test_xxx_feature_name(self, test_config):
        """
        Test Case #XXX: Description
        """
        # Test implementation
        assert True
```

### Step 4: Add Markers
Always include at least:
- `@pytest.mark.unit` - Identifies as unit test
- `@pytest.mark.<component>` - Component-specific marker

Optional markers:
- `@pytest.mark.hardware` - Requires physical hardware
- `@pytest.mark.gpio` - GPIO functionality
- `@pytest.mark.network` - Network/TCP functionality
- `@pytest.mark.mock` - Uses mock objects only

### Step 5: Run Your Test
```bash
pytest tests/unit_tests/<subdirectory>/test_xxx_*.py -v -s
```

## Best Practices

### Unit Test Characteristics
✓ **Fast**: Should complete in < 1 second (excluding manual interaction)
✓ **Isolated**: Independent of other tests
✓ **Focused**: Test one component/function
✓ **Repeatable**: Same result every time
✓ **Clear**: Easy to understand purpose

### When to Use Unit Tests vs Integration Tests

**Use Unit Test when:**
- Testing individual function behavior
- Mocking external dependencies
- Fast feedback needed
- No real hardware required (or minimal)

**Use Integration Test when:**
- Testing multiple components together
- Verifying end-to-end workflows
- Real hardware interaction required
- Testing protocol/API compliance

## Configuration

Unit tests share configuration with integration tests:

**Test Config:** `tests/config/test_config.yaml`
**Pytest Config:** `tests/pytest.ini`
**Fixtures:** `tests/conftest.py`

## Running in CI/CD

### Separate Unit and Integration Tests

```yaml
# GitLab CI example
test:unit:
  stage: test
  script:
    - pytest tests/unit_tests/ -v --junitxml=unit-report.xml
  artifacts:
    reports:
      junit: unit-report.xml

test:integration:
  stage: test
  script:
    - pytest tests/fw-app-integration/ -v --junitxml=integration-report.xml
  artifacts:
    reports:
      junit: integration-report.xml
```

## Troubleshooting

### Unit Tests Not Discovered

**Problem:** `pytest` doesn't find unit tests

**Solution:**
```bash
# Ensure __init__.py exists
ls tests/unit_tests/__init__.py

# Run from correct directory
cd tests
pytest unit_tests/ -v

# Or use full path
pytest tests/unit_tests/ -v
```

### Markers Not Recognized

**Problem:** `PytestUnknownMarkWarning: Unknown pytest.mark.unit`

**Solution:**
Check `tests/pytest.ini` includes marker definition:
```ini
markers =
    unit: Unit tests (isolated component tests)
```

### Test Appears in Wrong Category

**Problem:** Unit test shows up in integration test runs

**Solution:**
- Ensure test has `@pytest.mark.unit` decorator
- Don't use integration markers (`fw_app`, `hardware`) on unit tests
- Run with explicit marker: `pytest -m unit`

## Documentation

- **Unit Tests Overview:** [tests/unit_tests/README.md](unit_tests/README.md)
- **Test #106 Guide:** [tests/unit_tests/power-service/TEST_106_GUIDE.md](unit_tests/power-service/TEST_106_GUIDE.md)
- **Integration Tests:** [tests/README.md](README.md)
- **Development Guide:** [CLAUDE.md](../CLAUDE.md)

## Summary

**Unit tests** are now organized in `tests/unit_tests/` separate from integration tests.

**Key benefits:**
- ✅ Clear separation of test types
- ✅ Faster test execution (run unit tests only)
- ✅ Better organization by component
- ✅ Independent test development

**Next steps:**
1. Review existing Test #106
2. Add more unit tests to respective directories
3. Keep integration tests in `fw-app-integration/` and `hardware-integration/`

---

**Quick reference:**
```bash
# Unit tests
pytest tests/unit_tests/ -v

# Integration tests
pytest tests/fw-app-integration/ -v
pytest tests/hardware-integration/ -v

# All tests
pytest tests/ -v
```
