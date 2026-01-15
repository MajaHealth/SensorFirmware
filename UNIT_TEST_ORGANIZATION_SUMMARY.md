# Unit Test Organization - Summary

## What Was Done

Successfully organized Test #106 into a separate **unit tests** directory structure, keeping it isolated from integration tests.

---

## New Directory Structure

```
/home/kranti/sensor_test_project/tests/
│
├── unit_tests/                          ← NEW: Unit tests directory
│   ├── __init__.py
│   ├── README.md                        ← Unit tests documentation
│   │
│   ├── power-service/                   ← Power service unit tests
│   │   ├── __init__.py
│   │   ├── test_106_soft_shutdown_denied.py  ← Test #106
│   │   └── TEST_106_GUIDE.md            ← Detailed test guide
│   │
│   ├── spi-service/                     ← SPI service unit tests (empty, for future)
│   │   └── __init__.py
│   │
│   ├── gpio/                            ← GPIO unit tests (empty, for future)
│   │   └── __init__.py
│   │
│   └── shutdown/                        ← Shutdown unit tests (empty, for future)
│       └── __init__.py
│
├── fw-app-integration/                  ← Integration tests (firmware-app)
├── hardware-integration/                ← Integration tests (hardware)
├── common/                              ← Shared utilities
├── config/                              ← Test configuration
├── conftest.py                          ← Pytest fixtures
├── pytest.ini                           ← Updated with new markers
├── README.md                            ← Integration tests documentation
└── UNIT_TESTS_QUICKSTART.md            ← NEW: Quick start guide
```

---

## Files Created

### 1. Test Implementation
**File:** `tests/unit_tests/power-service/test_106_soft_shutdown_denied.py`
- Complete Test #106 implementation
- Two scenarios: Denied shutdown & Timeout
- Mock application for testing
- GPIO simulation support
- Service status verification
- Comprehensive logging

### 2. Test Documentation
**File:** `tests/unit_tests/power-service/TEST_106_GUIDE.md`
- Complete step-by-step execution guide
- Prerequisites and setup
- Expected output
- Troubleshooting section
- Configuration details

### 3. Unit Tests Overview
**File:** `tests/unit_tests/README.md`
- Unit tests directory explanation
- Test categories and structure
- Running unit tests commands
- Writing new unit tests template
- Best practices

### 4. Quick Start Guide
**File:** `tests/UNIT_TESTS_QUICKSTART.md`
- Quick reference for developers
- Key differences between unit and integration tests
- Common commands
- Adding new tests guide

---

## Files Modified

### 1. pytest.ini
**File:** `tests/pytest.ini`
**Changes:**
- Added `unit` marker for unit tests
- Added `gpio` marker for GPIO tests
- Added `network` marker for network/TCP tests
- Added `shutdown` marker for shutdown handling tests
- Added `mock` marker for tests using mocks

### 2. CLAUDE.md
**File:** `CLAUDE.md`
**Changes:**
- Updated test structure section with three categories
- Added "Run Unit Tests" section with examples
- Documented unit_tests directory organization
- Distinguished between Python unit tests, C++ unit tests, and integration tests

---

## Test Markers

### New Markers Added

| Marker | Description | Example Usage |
|--------|-------------|---------------|
| `unit` | Unit tests (isolated) | `pytest -m unit` |
| `gpio` | GPIO-related tests | `pytest -m gpio` |
| `network` | Network/TCP tests | `pytest -m network` |
| `shutdown` | Shutdown handling tests | `pytest -m shutdown` |
| `mock` | Tests using mock objects | `pytest -m mock` |

### Test #106 Markers
```python
@pytest.mark.unit
@pytest.mark.hardware
@pytest.mark.gpio
@pytest.mark.network
@pytest.mark.shutdown
```

---

## How to Run Tests

### Run Only Unit Tests
```bash
# All unit tests
pytest tests/unit_tests/ -v

# Power service unit tests only
pytest tests/unit_tests/power-service/ -v

# Test #106 specifically
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

### Run Only Integration Tests
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
# From project root
pytest tests/ -v

# Using markers
pytest -m unit                    # Only unit tests
pytest -m "fw_app or hardware"    # Only integration tests
pytest -m "not hardware"          # Exclude hardware tests
```

---

## Test #106 Execution Steps

### Quick Execution
```bash
cd /home/kranti/sensor_test_project
source venv/bin/activate
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

### What Happens
1. **Scenario A: Denied Shutdown**
   - Mock app starts (port 8765)
   - GPIO configured
   - User presses switch (manual)
   - Firmware sends "close"
   - Mock app responds "ACK:denied"
   - Test verifies: No shutdown, services active
   - **Duration:** ~10-15 seconds

2. **Scenario B: Timeout**
   - Mock app starts (port 8766)
   - Mock app configured to NOT respond
   - User presses switch (manual)
   - Firmware sends "close"
   - Wait 3 seconds (timeout)
   - Test verifies: No shutdown, services active
   - **Duration:** ~15-20 seconds

### Manual Interaction Required
Test will prompt **twice** (once per scenario):
```
📋 MANUAL ACTION:
   Press the OFF switch briefly (0.5s)
   Press ENTER after pressing switch...
```

**Action:** Press GPIO switch, then press ENTER

---

## Key Benefits

### 1. Clear Separation
✅ Unit tests in `tests/unit_tests/`
✅ Integration tests in `tests/fw-app-integration/` and `tests/hardware-integration/`
✅ Easy to run each category independently

### 2. Better Organization
✅ Tests grouped by component (power-service, spi-service, gpio, etc.)
✅ Each test has dedicated guide documentation
✅ Clear naming conventions

### 3. Improved Development Workflow
✅ Run fast unit tests during development
✅ Run integration tests before deployment
✅ Run all tests in CI/CD pipeline

### 4. Extensibility
✅ Easy to add new unit tests to appropriate directory
✅ Templates provided for new tests
✅ Consistent structure across all unit tests

---

## Next Steps

### For Adding More Unit Tests

1. **Identify Component**
   - Power service → `tests/unit_tests/power-service/`
   - SPI service → `tests/unit_tests/spi-service/`
   - GPIO → `tests/unit_tests/gpio/`
   - Shutdown → `tests/unit_tests/shutdown/`

2. **Create Test File**
   ```bash
   # Follow naming convention
   tests/unit_tests/<component>/test_<number>_<name>.py
   ```

3. **Use Template**
   - See `tests/unit_tests/README.md` for template
   - Add appropriate markers
   - Follow Test #106 as example

4. **Add Documentation**
   - Create `TEST_<number>_GUIDE.md` if needed
   - Update `tests/unit_tests/README.md`

### For Running Tests

1. **During Development**
   ```bash
   # Quick unit test run
   pytest tests/unit_tests/ -v
   ```

2. **Before Committing**
   ```bash
   # Run affected integration tests
   pytest tests/fw-app-integration/ -v
   ```

3. **Before Deployment**
   ```bash
   # Run all tests
   pytest tests/ -v
   ```

---

## Documentation Reference

| Document | Purpose | Location |
|----------|---------|----------|
| Test #106 Guide | Detailed execution steps | `tests/unit_tests/power-service/TEST_106_GUIDE.md` |
| Unit Tests README | Unit tests overview | `tests/unit_tests/README.md` |
| Quick Start | Quick reference | `tests/UNIT_TESTS_QUICKSTART.md` |
| Integration Tests | Integration tests docs | `tests/README.md` |
| Development Guide | Claude Code guide | `CLAUDE.md` |

---

## Verification Commands

### Check Structure
```bash
# View directory tree
tree tests/unit_tests/

# List test files
find tests/unit_tests/ -name "test_*.py"
```

### Check Test Discovery
```bash
# Collect tests without running
pytest tests/unit_tests/ --collect-only

# Check markers
pytest tests/unit_tests/ --markers
```

### Run Tests
```bash
# Dry run (don't execute)
pytest tests/unit_tests/ --collect-only -v

# Actually run tests
pytest tests/unit_tests/ -v

# Run with verbose output
pytest tests/unit_tests/ -v -s
```

---

## Summary

✅ **Completed:**
- Created separate `tests/unit_tests/` directory structure
- Moved Test #106 to `tests/unit_tests/power-service/`
- Created comprehensive documentation (3 guides)
- Updated pytest.ini with new markers
- Updated CLAUDE.md with unit test information
- Created directory structure for future unit tests

✅ **Test #106 Ready:**
- Fully functional unit test
- Separated from integration tests
- Comprehensive execution guide
- Properly marked and categorized

✅ **Future-Ready:**
- Directory structure for more unit tests
- Templates and best practices documented
- Clear separation between test types
- Easy to extend and maintain

---

## Contact & Support

For questions about:
- **Test #106 execution:** See `tests/unit_tests/power-service/TEST_106_GUIDE.md`
- **Unit tests in general:** See `tests/unit_tests/README.md`
- **Quick reference:** See `tests/UNIT_TESTS_QUICKSTART.md`
- **Development:** See `CLAUDE.md`

---

**Organization complete! Test #106 is now properly separated in the unit_tests directory.**
