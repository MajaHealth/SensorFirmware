# API Test Plan for MajaHealth Sensor Firmware

This document provides comprehensive test scenarios for all three services via their JSON TCP APIs.

## Test Environment Setup

### Connection Details
- **MAX30009 (ICG/Bioimpedance):** `localhost:30009`
- **ADS1293 (ECG):** `localhost:1293`
- **Power Control:** `localhost:501`

### Test Tools
```bash
# Using netcat for manual testing
nc localhost 30009

# Using telnet
telnet localhost 30009

# Using Python for automated testing
import socket
import json
import time
```

### Python Test Helper
```python
def send_command(host, port, command_dict):
    """Send JSON command and return response"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Wait for connection message
    welcome = sock.recv(1024)
    print(f"Server: {welcome.decode()}")

    # Send command
    cmd = json.dumps(command_dict) + "\n"
    sock.send(cmd.encode())

    # Receive response
    response = sock.recv(65536)
    sock.close()

    return json.loads(response.decode().strip())
```

---

## Test Suite 1: MAX30009 (Bioimpedance/ICG) - Port 30009

### 1.1 Basic Connection Tests

**Test 1.1.1: Connection Establishment**
```bash
# Connect and verify welcome message
nc localhost 30009
# Expected: "Connection accepted"
```

**Test 1.1.2: Malformed JSON**
```json
{"invalid json without closing brace"
```
Expected response:
```json
{"type":"error JSON"}
```

**Test 1.1.3: Missing Type Field**
```json
{"some_field":"some_value"}
```
Expected response:
```json
{"type":"error JSON"}
```

**Test 1.1.4: Unknown Command Type**
```json
{"type":"unknown_command"}
```
Expected response:
```json
{"type":"error JSON"}
```

---

### 1.2 Settings Configuration Tests

**Test 1.2.1: Power On (Minimal Settings)**
```json
{"type":"settings","power_enable":true}
```
Expected response:
```json
{
  "type":"actual_settings",
  "stimulate_frequency":0,
  "measure_frequency":0,
  "out_LP_filter":0,
  "out_HP_filter":0,
  "stimulate_current":0,
  "measure_enable":false,
  "power_enable":true,
  "ext_MUX_state":0
}
```

**Test 1.2.2: Enable Measurement with Basic Config**
```json
{
  "type":"settings",
  "power_enable":true,
  "measure_enable":true,
  "stimulate_frequency":5,
  "measure_frequency":100,
  "stimulate_current":2
}
```
Verify: `measure_enable=true` in response

**Test 1.2.3: All Stimulation Frequencies (17 frequency points)**

Test each frequency index (0-16):
- Index 0: 25 Hz
- Index 1: 100 Hz
- Index 2: 200 Hz
- Index 3: 500 Hz
- Index 4: 1000 Hz (1 kHz)
- Index 5: 5000 Hz (5 kHz)
- Index 6: 10000 Hz (10 kHz)
- Index 7: 20000 Hz (20 kHz)
- Index 8: 50000 Hz (50 kHz)
- Index 9: 100000 Hz (100 kHz)
- Index 10: 150000 Hz (150 kHz)
- Index 11: 200000 Hz (200 kHz)
- Index 12: 250000 Hz (250 kHz)
- Index 13: 300000 Hz (300 kHz)
- Index 14: 350000 Hz (350 kHz)
- Index 15: 400000 Hz (400 kHz)
- Index 16: 450000 Hz (450 kHz)

```python
for freq_idx in range(17):
    cmd = {
        "type": "settings",
        "power_enable": True,
        "measure_enable": True,
        "stimulate_frequency": freq_idx,
        "measure_frequency": 100,
        "stimulate_current": 2
    }
    response = send_command("localhost", 30009, cmd)
    assert response["stimulate_frequency"] == freq_idx
```

**Test 1.2.4: All Stimulation Currents (5 current levels)**

Test each current index (0-4):
- Index 0: 64 µA
- Index 1: 128 µA
- Index 2: 256 µA
- Index 3: 640 µA
- Index 4: 1.28 mA

```python
for current_idx in range(5):
    cmd = {
        "type": "settings",
        "power_enable": True,
        "measure_enable": True,
        "stimulate_frequency": 5,
        "measure_frequency": 100,
        "stimulate_current": current_idx
    }
    response = send_command("localhost", 30009, cmd)
    assert response["stimulate_current"] == current_idx
```

**Test 1.2.5: Measure Frequency Range**

Valid range: 1-500 Hz

```python
# Test boundaries
test_freqs = [1, 10, 50, 100, 250, 500]
for freq in test_freqs:
    cmd = {
        "type": "settings",
        "power_enable": True,
        "measure_enable": True,
        "measure_frequency": freq
    }
    response = send_command("localhost", 30009, cmd)
    # Verify frequency is accepted (might be adjusted by firmware)
```

**Test 1.2.6: Invalid Frequency Clamping**
```json
{"type":"settings","measure_frequency":0}
```
Expected: Firmware clamps to minimum (1 Hz)

```json
{"type":"settings","measure_frequency":10000}
```
Expected: Firmware clamps to maximum (500 Hz)

**Test 1.2.7: External MUX States (5 modes)**
```python
mux_states = [
    (0, "ALL_OFF"),
    (1, "4_WIRE"),
    (2, "2_WIRE"),
    (3, "CALIBRATE"),
    (4, "COLE_COLE")
]

for state_val, state_name in mux_states:
    cmd = {
        "type": "settings",
        "power_enable": True,
        "ext_MUX_state": state_val
    }
    response = send_command("localhost", 30009, cmd)
    assert response["ext_MUX_state"] == state_val
    print(f"MUX state {state_name}: OK")
```

**Test 1.2.8: Partial Settings Update**
```json
{"type":"settings","measure_enable":false}
```
Verify: Only `measure_enable` changes, other settings remain

**Test 1.2.9: Complete Configuration**
```json
{
  "type":"settings",
  "power_enable":true,
  "measure_enable":true,
  "stimulate_frequency":8,
  "measure_frequency":250,
  "stimulate_current":3,
  "out_LP_filter":2,
  "out_HP_filter":1,
  "ext_MUX_state":1
}
```

---

### 1.3 Data Retrieval Tests

**Test 1.3.1: Get Data When Disabled**
```json
{"type":"settings","measure_enable":false}
```
Then:
```json
{"type":"get_data"}
```
Expected: Empty or minimal data array

**Test 1.3.2: Get Data When Enabled**
```json
{"type":"settings","power_enable":true,"measure_enable":true,"measure_frequency":100}
```
Wait 2 seconds, then:
```json
{"type":"get_data"}
```
Expected response structure:
```json
{
  "type":"data",
  "data_frequency":100,
  "data_size":200,
  "timestamp":"2025-01-23 12:34:56.789",
  "data":[
    [12450, 15320, 8940, 4523, 0],
    [13200, 14890, 9100, 4456, 0],
    ...
  ]
}
```

**Test 1.3.3: Verify Data Point Format**

Each data point is: `[Load_real, Load_mag, Load_imag, Load_angle, overload]`
- All values are integers (scaled by 10000 for floats)
- `overload` is 0 or 1 (boolean)

**Test 1.3.4: Sync Marker Detection**

Run for >1 second and verify sync markers appear:
```python
cmd = {"type":"settings","power_enable":True,"measure_enable":True,"measure_frequency":100}
send_command("localhost", 30009, cmd)

time.sleep(3)  # Wait for sync markers

response = send_command("localhost", 30009, {"type":"get_data"})
data_points = response["data"]

# Search for sync markers
sync_markers = [pt for pt in data_points if pt[0] == -99999]
print(f"Found {len(sync_markers)} sync markers")
assert len(sync_markers) >= 2  # Should have at least 2 markers in 3 seconds
```

**Test 1.3.5: Continuous Data Polling**
```python
# Enable measurement
send_command("localhost", 30009, {
    "type":"settings",
    "power_enable":True,
    "measure_enable":True,
    "measure_frequency":100
})

# Poll every 1 second for 10 seconds
for i in range(10):
    time.sleep(1)
    response = send_command("localhost", 30009, {"type":"get_data"})
    print(f"Poll {i}: {response['data_size']} samples")
    # Verify no buffer overflow (data_size should be ~100-200)
```

**Test 1.3.6: Buffer Overflow Test**
```python
# Enable measurement but don't read
send_command("localhost", 30009, {
    "type":"settings",
    "power_enable":True,
    "measure_enable":True,
    "measure_frequency":500
})

# Wait longer than buffer capacity (>3 seconds)
time.sleep(5)

# Read - should get clamped data
response = send_command("localhost", 30009, {"type":"get_data"})
# May have lost some data due to overflow
print(f"Data size after overflow: {response['data_size']}")
```

---

### 1.4 Calibration Tests

**Test 1.4.1: Start Calibration**
```json
{"type":"start_calibrate"}
```
Expected response:
```json
{"type":"calibrate_started"}
```

**Test 1.4.2: Commands During Calibration**

While calibration is running:
```json
{"type":"settings","measure_enable":true}
```
Expected:
```json
{"type":"calibrate_runing"}
```

```json
{"type":"get_data"}
```
Expected:
```json
{"type":"calibrate_runing"}
```

**Test 1.4.3: Calibration Progress Monitoring**
```python
# Start calibration
send_command("localhost", 30009, {"type":"start_calibrate"})

# Monitor calibration responses (automatic responses from main loop)
# Calibration takes ~85 steps * 60 main loops = ~5100 main loops
# At 500µs per loop = ~2.5 seconds per step = ~212 seconds total (~3.5 minutes)

# Wait and check periodically
time.sleep(10)
response = send_command("localhost", 30009, {"type":"get_data"})
# Should still show "calibrate_runing"
```

**Test 1.4.4: Calibration Data Response**

During calibration, server automatically sends calibration results:
```json
{
  "type":"calib_data",
  "stimulate_frequency":5,
  "stimulate_current":2,
  "I_offset":-446,
  "I_coef":0.0624,
  "I_phase_coef":-65.814,
  "I_phase_cos":0.4096,
  "I_phase_sin":-0.9122,
  "Q_offset":-193,
  "Q_coef":0.0582,
  "Q_phase_coef":-40.473,
  "Q_phase_cos":0.7607,
  "Q_phase_sin":-0.6490,
  "I_cal_in":2.56,
  "I_cal_in_ADC":-59,
  "I_cal_quad":-5.7,
  "Q_cal_in":-4.43,
  "Q_cal_in_ADC":-863,
  "Q_cal_quad":-5.7
}
```

**Test 1.4.5: Stop Calibration**
```json
{"type":"stop_calibrate"}
```
Expected:
```json
{"type":"calibrate_stoped"}
```

**Test 1.4.6: Resume Normal Operation After Calibration**

After calibration completes or is stopped:
```json
{"type":"settings","measure_enable":true}
```
Should work normally again.

---

### 1.5 Power State Transitions

**Test 1.5.1: Power Off to On**
```json
{"type":"settings","power_enable":false}
```
Then:
```json
{"type":"settings","power_enable":true}
```
Note: 200ms delay in firmware for power stabilization

**Test 1.5.2: Measurement Enable/Disable Cycles**
```python
for i in range(5):
    send_command("localhost", 30009, {"type":"settings","measure_enable":True})
    time.sleep(1)
    send_command("localhost", 30009, {"type":"settings","measure_enable":False})
    time.sleep(1)
```

---

## Test Suite 2: ADS1293 (ECG) - Port 1293

### 2.1 Connection Tests

**Test 2.1.1: Basic Connection**
```bash
nc localhost 1293
# Expected: "Connection accepted"
```

**Test 2.1.2: Error Handling**
```json
{"invalid":"json"}
```
Expected:
```json
{"type":"error JSON"}
```

---

### 2.2 Settings Configuration Tests

**Test 2.2.1: Power On**
```json
{"type":"settings","power_enable":true}
```
Expected response:
```json
{
  "type":"actual_settings",
  "enable_conversion":false,
  "power_enable":true,
  "R2_rate":8,
  "R3_rate":128
}
```

**Test 2.2.2: Enable Conversion**
```json
{
  "type":"settings",
  "power_enable":true,
  "enable_conversion":true
}
```

**Test 2.2.3: R2 Decimation Rate**

Valid values: 4, 5, 6, 8
```python
for r2_rate in [4, 5, 6, 8]:
    cmd = {
        "type": "settings",
        "power_enable": True,
        "enable_conversion": True,
        "R2_rate": r2_rate
    }
    response = send_command("localhost", 1293, cmd)
    assert response["R2_rate"] == r2_rate
```

**Test 2.2.4: R3 Decimation Rate**

Valid values: 4, 6, 8, 12, 16, 32, 64, 128
```python
for r3_rate in [4, 6, 8, 12, 16, 32, 64, 128]:
    cmd = {
        "type": "settings",
        "power_enable": True,
        "enable_conversion": True,
        "R3_rate": r3_rate
    }
    response = send_command("localhost", 1293, cmd)
    assert response["R3_rate"] == r3_rate
```

**Test 2.2.5: Invalid Decimation Rates**
```json
{"type":"settings","R2_rate":3}
```
Expected: Firmware defaults to R2_rate=8

```json
{"type":"settings","R3_rate":100}
```
Expected: Firmware defaults to R3_rate=128

**Test 2.2.6: Complete Configuration**
```json
{
  "type":"settings",
  "power_enable":true,
  "enable_conversion":true,
  "R2_rate":6,
  "R3_rate":64
}
```

---

### 2.3 Data Retrieval Tests

**Test 2.3.1: Get Data When Disabled**
```json
{"type":"settings","enable_conversion":false}
```
Then:
```json
{"type":"get_data"}
```
Expected: Empty or minimal data

**Test 2.3.2: Get Data When Enabled**
```json
{"type":"settings","power_enable":true,"enable_conversion":true}
```
Wait 2 seconds:
```json
{"type":"get_data"}
```
Expected response:
```json
{
  "type":"data",
  "data_size":250,
  "timestamp":"2025-01-23 12:34:56.789",
  "data":[
    [8934, 7821, 9123],
    [8945, 7834, 9156],
    [-99999, 1, 0],
    [8923, 7845, 9134],
    ...
  ]
}
```

**Test 2.3.3: Verify 3-Channel Data Format**

Each point: `[ch1, ch2, ch3]`
- All values are 24-bit signed integers
- Sync markers: `[-99999, sync_num, 0]`

**Test 2.3.4: Sync Marker Detection**
```python
send_command("localhost", 1293, {
    "type":"settings",
    "power_enable":True,
    "enable_conversion":True
})

time.sleep(3)

response = send_command("localhost", 1293, {"type":"get_data"})
data_points = response["data"]

sync_markers = [pt for pt in data_points if pt[0] == -99999]
print(f"ECG sync markers: {len(sync_markers)}")
assert len(sync_markers) >= 2
```

**Test 2.3.5: Sample Rate Verification**

Calculate expected sample rate based on decimation:
```python
# Base rate: 64 kHz
# Effective rate = 64000 / (R2_rate * R3_rate)

configs = [
    (4, 4, 4000),    # 64k / 16 = 4000 Hz
    (8, 128, 62.5),  # 64k / 1024 = 62.5 Hz
    (6, 64, 166.7),  # 64k / 384 = ~167 Hz
]

for r2, r3, expected_hz in configs:
    send_command("localhost", 1293, {
        "type":"settings",
        "power_enable":True,
        "enable_conversion":True,
        "R2_rate":r2,
        "R3_rate":r3
    })

    time.sleep(2)
    response = send_command("localhost", 1293, {"type":"get_data"})
    samples_per_sec = response["data_size"] / 2.0
    print(f"R2={r2}, R3={r3}: {samples_per_sec:.1f} Hz (expected {expected_hz:.1f})")
```

**Test 2.3.6: Buffer Overflow Test**
```python
# High sample rate
send_command("localhost", 1293, {
    "type":"settings",
    "power_enable":True,
    "enable_conversion":True,
    "R2_rate":4,
    "R3_rate":4  # 4000 Hz
})

# Don't read for longer than buffer capacity
time.sleep(5)  # Buffer is 3000 samples = 0.75 sec at 4kHz

response = send_command("localhost", 1293, {"type":"get_data"})
print(f"Overflow test: {response['data_size']} samples")
# Should be clamped to buffer size
```

---

### 2.4 Synchronization Tests (Cross-Sensor)

**Test 2.4.1: Sync Marker Alignment**
```python
# Enable both sensors
send_command("localhost", 30009, {
    "type":"settings",
    "power_enable":True,
    "measure_enable":True,
    "measure_frequency":100
})

send_command("localhost", 1293, {
    "type":"settings",
    "power_enable":True,
    "enable_conversion":True
})

# Wait for sync markers
time.sleep(3)

# Read both
max_response = send_command("localhost", 30009, {"type":"get_data"})
ads_response = send_command("localhost", 1293, {"type":"get_data"})

# Extract sync markers
max_syncs = [pt[1] for pt in max_response["data"] if pt[0] == -99999]
ads_syncs = [pt[1] for pt in ads_response["data"] if pt[0] == -99999]

print(f"MAX30009 sync markers: {max_syncs}")
print(f"ADS1293 sync markers: {ads_syncs}")

# Should have matching sync numbers
assert len(set(max_syncs) & set(ads_syncs)) > 0
```

**Test 2.4.2: Timestamp Correlation**
```python
max_response = send_command("localhost", 30009, {"type":"get_data"})
ads_response = send_command("localhost", 1293, {"type":"get_data"})

max_time = max_response["timestamp"]
ads_time = ads_response["timestamp"]

print(f"MAX30009 timestamp: {max_time}")
print(f"ADS1293 timestamp: {ads_time}")
# Should be very close (within milliseconds if polled consecutively)
```

---

## Test Suite 3: Power Control - Port 501

### 3.1 Battery Information Tests

**Test 3.1.1: Get Battery Info**
```json
{"type":"get_batt_info"}
```
Expected response:
```json
{
  "type":"batt_info",
  "voltage":4100,
  "temperature":25,
  "current":-250,
  "relative_state_of_charge":85,
  "remaining_capacity":2550,
  "full_charge_capacity":3000,
  "run_time_to_empty":600,
  "average_time_to_empty":580,
  "average_time_to_full":120,
  "cycle_count":15,
  "design_capacity":3000,
  "design_voltage":3700,
  "fully_discharged":false,
  "fully_charged":false,
  "discharging":true,
  "charging":false,
  "charger_is_connect":false,
  "battery_charge_is_disable":false
}
```

**Test 3.1.2: Verify Battery Metrics**
```python
response = send_command("localhost", 501, {"type":"get_batt_info"})

# Validate ranges
assert 2500 <= response["voltage"] <= 4500  # mV
assert -50 <= response["temperature"] <= 80  # °C
assert 0 <= response["relative_state_of_charge"] <= 100  # %
assert response["remaining_capacity"] <= response["full_charge_capacity"]

# Validate flags
assert isinstance(response["fully_discharged"], bool)
assert isinstance(response["charging"], bool)
assert response["charging"] == (not response["discharging"])
```

**Test 3.1.3: Battery Polling**
```python
# Poll every 3 seconds (battery read throttle is 3 sec)
for i in range(5):
    response = send_command("localhost", 501, {"type":"get_batt_info"})
    print(f"Poll {i}: {response['relative_state_of_charge']}% - {response['voltage']}mV")
    time.sleep(3)
```

---

### 3.2 Charge Control Tests

**Test 3.2.1: Disable Charging**
```json
{"type":"charge_disable"}
```
Expected:
```json
{"type":"charge_is_disable"}
```

Then verify:
```json
{"type":"get_batt_info"}
```
Should show: `"battery_charge_is_disable":true`

**Test 3.2.2: Enable Charging**
```json
{"type":"charge_enable"}
```
Expected:
```json
{"type":"charge_is_enable"}
```

Then verify:
```json
{"type":"get_batt_info"}
```
Should show: `"battery_charge_is_disable":false`

**Test 3.2.3: Charge State Transitions**
```python
# Disable
response = send_command("localhost", 501, {"type":"charge_disable"})
assert response["type"] == "charge_is_disable"

# Verify
info = send_command("localhost", 501, {"type":"get_batt_info"})
assert info["battery_charge_is_disable"] == True

# Enable
response = send_command("localhost", 501, {"type":"charge_enable"})
assert response["type"] == "charge_is_enable"

# Verify
info = send_command("localhost", 501, {"type":"get_batt_info"})
assert info["battery_charge_is_disable"] == False
```

---

### 3.3 Buzzer Tests

**Test 3.3.1: Buzzer Short Beep (1 second)**
```json
{"type":"buzzer","duration":10}
```
Note: Duration is in 100ms units, so 10 = 1 second

**Test 3.3.2: Buzzer Medium Beep (3 seconds)**
```json
{"type":"buzzer","duration":30}
```

**Test 3.3.3: Buzzer Long Beep (10 seconds)**
```json
{"type":"buzzer","duration":100}
```

**Test 3.3.4: Invalid Buzzer Duration (negative)**
```json
{"type":"buzzer","duration":-5}
```
Expected: Clamped to 0 (no beep)

**Test 3.3.5: Invalid Buzzer Duration (too long)**
```json
{"type":"buzzer","duration":200}
```
Expected: Clamped to 100 (10 seconds max)

**Test 3.3.6: Buzzer Sequence Test**
```python
# Three short beeps
for i in range(3):
    send_command("localhost", 501, {"type":"buzzer","duration":5})
    time.sleep(1)
```

---

### 3.4 Button Monitoring Tests

**Note:** Button events are automatically sent by the service (not request-based)

**Test 3.4.1: Monitor Button Events**
```python
# Keep connection open and wait for button events
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 501))

welcome = sock.recv(1024)
print(welcome.decode())

# Wait for button press events (automatic from firmware)
while True:
    data = sock.recv(4096)
    if data:
        print(f"Button event: {data.decode()}")
    time.sleep(0.1)
```

Expected event format:
```json
{"type":"button_info","state":true,"hold_time":2}
```

**Test 3.4.2: Button Hold Time**

Press and hold button for various durations:
- Short press: `hold_time` < 1 second
- Medium hold: `hold_time` = 2-5 seconds
- Long hold: `hold_time` > 5 seconds

---

## Test Suite 4: Integration & Stress Tests

### 4.1 Multi-Connection Tests

**Test 4.1.1: Multiple Simultaneous Connections**
```python
# Connect to all three services simultaneously
sockets = []
for port in [30009, 1293, 501]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", port))
    sockets.append(sock)

# All should accept connections
```

**Test 4.1.2: Rapid Connection/Disconnection**
```python
for i in range(20):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 30009))
    sock.close()
```

---

### 4.2 Load Tests

**Test 4.2.1: Rapid Command Sending**
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 30009))
sock.recv(1024)  # Welcome

for i in range(100):
    cmd = json.dumps({"type":"get_data"}) + "\n"
    sock.send(cmd.encode())
    response = sock.recv(65536)

sock.close()
```

**Test 4.2.2: Large Data Retrieval**
```python
# Enable max sample rate
send_command("localhost", 30009, {
    "type":"settings",
    "power_enable":True,
    "measure_enable":True,
    "measure_frequency":500
})

# Wait for buffer to fill
time.sleep(3)

# Retrieve all data
response = send_command("localhost", 30009, {"type":"get_data"})
print(f"Retrieved {response['data_size']} samples")
```

---

### 4.3 Error Recovery Tests

**Test 4.3.1: Incomplete JSON Recovery**
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 30009))
sock.recv(1024)

# Send incomplete JSON
sock.send(b'{"type":"setti')
time.sleep(1)

# Send valid command
cmd = json.dumps({"type":"get_data"}) + "\n"
sock.send(cmd.encode())
response = sock.recv(65536)
# Should still work

sock.close()
```

**Test 4.3.2: Recovery After Settings Error**
```python
# Invalid settings
send_command("localhost", 30009, {"type":"invalid_command"})

# Valid settings should still work
response = send_command("localhost", 30009, {
    "type":"settings",
    "power_enable":True
})
assert response["type"] == "actual_settings"
```

---

## Test Suite 5: Real-World Scenarios

### 5.1 Complete Bioimpedance Measurement Workflow

```python
def run_icg_measurement():
    # 1. Power on
    send_command("localhost", 30009, {"type":"settings","power_enable":True})
    time.sleep(0.5)

    # 2. Configure for thoracic impedance measurement
    send_command("localhost", 30009, {
        "type":"settings",
        "power_enable":True,
        "measure_enable":True,
        "stimulate_frequency":8,  # 50 kHz
        "stimulate_current":3,     # 640 µA
        "measure_frequency":100,   # 100 Hz output
        "ext_MUX_state":1         # 4-wire mode
    })

    # 3. Wait for stabilization
    time.sleep(2)

    # 4. Collect 10 seconds of data
    all_data = []
    for i in range(10):
        time.sleep(1)
        response = send_command("localhost", 30009, {"type":"get_data"})
        all_data.extend(response["data"])
        print(f"Collected {len(all_data)} total samples")

    # 5. Stop measurement
    send_command("localhost", 30009, {"type":"settings","measure_enable":False})

    return all_data
```

### 5.2 Complete ECG Measurement Workflow

```python
def run_ecg_measurement():
    # 1. Power on
    send_command("localhost", 1293, {"type":"settings","power_enable":True})
    time.sleep(0.5)

    # 2. Configure for ECG
    send_command("localhost", 1293, {
        "type":"settings",
        "power_enable":True,
        "enable_conversion":True,
        "R2_rate":6,
        "R3_rate":64  # ~167 Hz
    })

    # 3. Collect data
    all_data = []
    for i in range(10):
        time.sleep(1)
        response = send_command("localhost", 1293, {"type":"get_data"})
        all_data.extend(response["data"])
        print(f"ECG samples: {len(all_data)}")

    return all_data
```

### 5.3 Synchronized ICG + ECG Recording

```python
def run_synchronized_recording():
    # Start both sensors
    send_command("localhost", 30009, {
        "type":"settings",
        "power_enable":True,
        "measure_enable":True,
        "measure_frequency":100
    })

    send_command("localhost", 1293, {
        "type":"settings",
        "power_enable":True,
        "enable_conversion":True
    })

    # Record for 30 seconds
    for i in range(30):
        time.sleep(1)

        # Poll both
        icg_data = send_command("localhost", 30009, {"type":"get_data"})
        ecg_data = send_command("localhost", 1293, {"type":"get_data"})

        # Check sync markers match
        icg_syncs = [pt[1] for pt in icg_data["data"] if pt[0] == -99999]
        ecg_syncs = [pt[1] for pt in ecg_data["data"] if pt[0] == -99999]

        print(f"Second {i}: ICG syncs={icg_syncs}, ECG syncs={ecg_syncs}")
```

---

## Test Automation Script

```python
#!/usr/bin/env python3
"""
Comprehensive API test suite for MajaHealth Firmware
"""

import socket
import json
import time
import sys

class FirmwareTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def send_command(self, port, command_dict):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("localhost", port))
            sock.recv(1024)

            cmd = json.dumps(command_dict) + "\n"
            sock.send(cmd.encode())

            response = sock.recv(65536)
            sock.close()

            return json.loads(response.decode().strip())
        except Exception as e:
            print(f"ERROR: {e}")
            return None

    def test(self, name, condition, details=""):
        if condition:
            print(f"✓ PASS: {name}")
            self.passed += 1
        else:
            print(f"✗ FAIL: {name} - {details}")
            self.failed += 1

    def run_max30009_tests(self):
        print("\n=== MAX30009 Tests ===")

        # Power on
        resp = self.send_command(30009, {"type":"settings","power_enable":True})
        self.test("MAX30009 Power On", resp and resp.get("power_enable") == True)

        # Frequency range
        for freq_idx in range(17):
            resp = self.send_command(30009, {
                "type":"settings",
                "stimulate_frequency":freq_idx
            })
            self.test(f"Frequency Index {freq_idx}",
                     resp and resp.get("stimulate_frequency") == freq_idx)

        # Data retrieval
        self.send_command(30009, {
            "type":"settings",
            "power_enable":True,
            "measure_enable":True
        })
        time.sleep(2)
        resp = self.send_command(30009, {"type":"get_data"})
        self.test("Data Retrieval", resp and resp.get("type") == "data")

    def run_ads1293_tests(self):
        print("\n=== ADS1293 Tests ===")

        # Power on
        resp = self.send_command(1293, {"type":"settings","power_enable":True})
        self.test("ADS1293 Power On", resp and resp.get("power_enable") == True)

        # Decimation rates
        for r2 in [4, 5, 6, 8]:
            resp = self.send_command(1293, {"type":"settings","R2_rate":r2})
            self.test(f"R2 Rate {r2}", resp and resp.get("R2_rate") == r2)

    def run_power_tests(self):
        print("\n=== Power Control Tests ===")

        # Battery info
        resp = self.send_command(501, {"type":"get_batt_info"})
        self.test("Battery Info", resp and resp.get("type") == "batt_info")

        # Charge control
        resp = self.send_command(501, {"type":"charge_disable"})
        self.test("Charge Disable", resp and resp.get("type") == "charge_is_disable")

        resp = self.send_command(501, {"type":"charge_enable"})
        self.test("Charge Enable", resp and resp.get("type") == "charge_is_enable")

    def run_all_tests(self):
        print("Starting Firmware API Tests...")

        self.run_max30009_tests()
        self.run_ads1293_tests()
        self.run_power_tests()

        print(f"\n{'='*50}")
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print(f"{'='*50}")

        return self.failed == 0

if __name__ == "__main__":
    tester = FirmwareTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
```

---

## Test Execution Checklist

- [ ] All services are running
- [ ] Hardware sensors are connected
- [ ] Python test environment is set up
- [ ] Network connectivity verified
- [ ] Run basic connection tests
- [ ] Run MAX30009 configuration tests
- [ ] Run ADS1293 configuration tests
- [ ] Run power control tests
- [ ] Run sync marker verification
- [ ] Run buffer overflow tests
- [ ] Run integration tests
- [ ] Document any failures or issues

---

## Expected Failure Scenarios

These are known limitations to document, not bugs:

1. **Buffer overflow on slow polling** - Expected behavior
2. **Settings during calibration rejected** - Designed behavior
3. **Invalid decimation rates auto-corrected** - Firmware safety
4. **200ms delay on power state changes** - Hardware stabilization
5. **Button events only sent when client connected** - TCP limitation
