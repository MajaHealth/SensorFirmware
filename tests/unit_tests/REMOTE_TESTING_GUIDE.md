# Remote Unit Testing Guide

How to run unit tests on CM4 remotely from your laptop (WSL2/Linux/Mac).

---

## Quick Start

```bash
# Set CM4 IP address
export PI_IP=192.168.x.x

# Run Test #106 on CM4
./scripts/run-unit-test-remote.sh $PI_IP test_106
```

---

## Why Run Tests Remotely?

| Your Laptop (WSL2) | CM4 Hardware |
|--------------------|--------------|
| ❌ No GPIO hardware | ✅ Real GPIO |
| ❌ Permission errors | ✅ Full access |
| ❌ Can't test hardware | ✅ Tests work |

**Solution:** Run unit tests **ON the CM4** from your laptop!

---

## Method 1: Using Automated Script (Recommended)

### Setup (One-Time)

```bash
# Make script executable (already done)
chmod +x scripts/run-unit-test-remote.sh

# Set CM4 IP
export PI_IP=192.168.x.x  # Add to ~/.bashrc for persistence
```

### Run Tests

```bash
# Run Test #106
./scripts/run-unit-test-remote.sh $PI_IP test_106

# Run specific test file
./scripts/run-unit-test-remote.sh $PI_IP tests/unit_tests/power-service/test_106_soft_shutdown_denied.py

# Run all unit tests
./scripts/run-unit-test-remote.sh $PI_IP

# Pass PI_IP as argument
./scripts/run-unit-test-remote.sh 192.168.1.100 test_106
```

### What the Script Does

1. ✓ Checks CM4 connectivity
2. ✓ Creates remote directories
3. ✓ Copies test files to CM4
4. ✓ Installs pytest on CM4 (if needed)
5. ✓ Runs test on CM4
6. ✓ Shows results on your laptop

---

## Method 2: Manual SSH Method

### One-Time Setup on CM4

```bash
# SSH into CM4
ssh pi@$PI_IP

# Create project directory
mkdir -p ~/sensor_test_project/tests/unit_tests/power-service

# Create virtual environment
cd ~/sensor_test_project
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pytest RPi.GPIO pyyaml

# Exit CM4
exit
```

### Copy Test Files to CM4

```bash
# From your laptop:
export PI_IP=192.168.x.x

# Copy test file
scp tests/unit_tests/power-service/test_106_soft_shutdown_denied.py \
    pi@$PI_IP:~/sensor_test_project/tests/unit_tests/power-service/

# Copy __init__.py files
scp tests/unit_tests/__init__.py \
    pi@$PI_IP:~/sensor_test_project/tests/unit_tests/

scp tests/unit_tests/power-service/__init__.py \
    pi@$PI_IP:~/sensor_test_project/tests/unit_tests/power-service/
```

### Run Test on CM4

```bash
# SSH and run test
ssh pi@$PI_IP << 'EOF'
cd ~/sensor_test_project
source venv/bin/activate
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
EOF
```

---

## Method 3: Interactive SSH Session

```bash
# SSH into CM4
ssh pi@$PI_IP

# Navigate to project
cd ~/sensor_test_project

# Activate virtual environment
source venv/bin/activate

# Run test interactively
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s

# You can manually press the switch when prompted!
```

---

## Expected Output (Successful Test)

```
========================================
Test Case #106: Soft Shutdown Denied/Timeout Behavior
========================================

[SCENARIO A] Testing Denied Shutdown
----------------------------------------------------------------------
Mock app started on 127.0.0.1:8765
✓ GPIO 17 configured                    ← Success on CM4!

📋 MANUAL ACTION:
   Press the OFF switch briefly (0.5s)
   Press ENTER after pressing switch...
[Press switch, then ENTER]

✓ Sent: 'close'
✓ Received: 'ACK:denied'
✓ No shutdown process running
✓ Services remain active

SCENARIO A: ✓ PASS

[SCENARIO B] Testing Timeout Behavior
----------------------------------------------------------------------
... (similar output)

SCENARIO B: ✓ PASS

TEST RESULT: ✓ PASS
==================================================================
```

---

## Troubleshooting

### Issue 1: Cannot Connect to CM4

**Error:**
```
Error: Cannot reach CM4 at 192.168.x.x
```

**Solution:**
```bash
# Check CM4 is powered on
ping 192.168.x.x

# Check SSH is enabled
ssh pi@$PI_IP "echo 'SSH works'"

# Check IP address is correct
echo $PI_IP
```

### Issue 2: Permission Denied (SSH)

**Error:**
```
Permission denied (publickey,password)
```

**Solution:**
```bash
# Setup SSH key (one-time)
ssh-copy-id pi@$PI_IP

# Or use password authentication
ssh pi@$PI_IP
# Enter password when prompted
```

### Issue 3: pytest Not Found on CM4

**Error:**
```
pytest: command not found
```

**Solution:**
```bash
# Run setup on CM4
ssh pi@$PI_IP << 'EOF'
cd ~/sensor_test_project
python3 -m venv venv
source venv/bin/activate
pip install pytest RPi.GPIO pyyaml
EOF
```

### Issue 4: GPIO Still Fails on CM4

**Error:**
```
Permission denied: '/sys/class/gpio/export'
```

**Solution:**
```bash
# Add user to gpio group on CM4
ssh pi@$PI_IP "sudo usermod -a -G gpio pi"

# Or run test with sudo
ssh pi@$PI_IP "cd ~/sensor_test_project && source venv/bin/activate && sudo -E pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s"
```

### Issue 5: Test Files Not Found

**Error:**
```
ERROR: file not found: tests/unit_tests/...
```

**Solution:**
```bash
# Re-copy test files
./scripts/run-unit-test-remote.sh $PI_IP test_106
# Script automatically copies files
```

---

## Comparison: Local vs Remote Testing

### Testing on WSL2 (Your Laptop)

```bash
# This FAILS on WSL2:
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
# ❌ Error: Permission denied: '/sys/class/gpio/export'
```

**Why it fails:**
- No GPIO hardware
- No `/sys/class/gpio/` access
- WSL2 doesn't support GPIO

### Testing on CM4 (Remote)

```bash
# This WORKS on CM4:
./scripts/run-unit-test-remote.sh $PI_IP test_106
# ✓ GPIO configured
# ✓ Test passes
```

**Why it works:**
- Real GPIO hardware
- Full system access
- Actual Raspberry Pi OS

---

## Best Practices

### Development Workflow

1. **Develop tests on laptop** (WSL2)
   - Write test code
   - Check syntax
   - Use version control

2. **Run tests on CM4** (remote)
   ```bash
   ./scripts/run-unit-test-remote.sh $PI_IP test_106
   ```

3. **Debug if needed**
   ```bash
   # SSH for interactive debugging
   ssh pi@$PI_IP
   cd ~/sensor_test_project
   source venv/bin/activate
   pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
   ```

### When to Use Each Method

| Method | Use Case | Interactivity |
|--------|----------|---------------|
| **Automated Script** | Quick validation | ✓ Automatic |
| **SSH Command** | CI/CD pipeline | ✓ Automatic |
| **Interactive SSH** | Debugging, manual testing | ✓ Manual switch press |

---

## Script Reference

### Full Command Options

```bash
# Help
./scripts/run-unit-test-remote.sh --help

# With IP as argument
./scripts/run-unit-test-remote.sh 192.168.1.100 test_106

# With IP as environment variable
PI_IP=192.168.1.100 ./scripts/run-unit-test-remote.sh test_106

# Run all unit tests
./scripts/run-unit-test-remote.sh $PI_IP

# Run specific test file (full path)
./scripts/run-unit-test-remote.sh $PI_IP tests/unit_tests/power-service/test_106_soft_shutdown_denied.py
```

### Script Location

```
scripts/run-unit-test-remote.sh
```

Make executable:
```bash
chmod +x scripts/run-unit-test-remote.sh
```

---

## Advanced: CI/CD Integration

### GitLab CI Example

```yaml
test:unit:cm4:
  stage: test
  script:
    - export PI_IP=192.168.1.100
    - ./scripts/run-unit-test-remote.sh $PI_IP
  only:
    - merge_requests
  tags:
    - raspberry-pi
```

### GitHub Actions Example

```yaml
name: Unit Tests on CM4

on: [push, pull_request]

jobs:
  test:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests on CM4
        env:
          PI_IP: ${{ secrets.CM4_IP }}
        run: ./scripts/run-unit-test-remote.sh $PI_IP
```

---

## Summary

### Quick Commands

```bash
# Setup once
export PI_IP=192.168.x.x

# Run Test #106
./scripts/run-unit-test-remote.sh $PI_IP test_106

# Run all unit tests
./scripts/run-unit-test-remote.sh $PI_IP

# Interactive mode
ssh pi@$PI_IP
cd ~/sensor_test_project && source venv/bin/activate
pytest tests/unit_tests/power-service/test_106_soft_shutdown_denied.py -v -s
```

### Key Points

✅ **Unit tests need GPIO** → Run on CM4, not WSL2
✅ **Automated script** → Easy remote testing
✅ **Manual SSH** → For debugging
✅ **Test results** → Shown on your laptop

---

## Related Documentation

- [Test #106 Guide](power-service/TEST_106_GUIDE.md) - Detailed test documentation
- [Unit Tests README](README.md) - Unit tests overview
- [CLAUDE.md](../../CLAUDE.md) - Development guide

---

**You can now run unit tests on CM4 remotely from your WSL2 laptop! 🎉**
