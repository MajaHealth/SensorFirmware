# Risk Assessment - C++ to C Refactoring

**Project:** Sensor Firmware C++ to C Refactoring
**Date:** 2025-11-22
**Purpose:** Identify and mitigate risks for zero-error conversion

---

## EXECUTIVE SUMMARY

**Overall Risk Level:** HIGH
**Total Risk Areas:** 12
**Critical Risks:** 5
**High Risks:** 4
**Medium Risks:** 3

**Primary Concerns:**
1. Thread safety and race conditions
2. Template conversion correctness
3. JSON API compatibility
4. Timing precision maintenance
5. Memory management errors

---

## RISK MATRIX

| Risk ID | Category | Severity | Probability | Overall | Mitigation Status |
|---------|----------|----------|-------------|---------|-------------------|
| R01 | Thread Safety | CRITICAL | HIGH | VERY HIGH | Planned |
| R02 | Template Conversion | CRITICAL | MEDIUM | HIGH | Planned |
| R03 | JSON API Compatibility | CRITICAL | MEDIUM | HIGH | Planned |
| R04 | Memory Leaks | HIGH | MEDIUM | HIGH | Planned |
| R05 | Timing Precision | CRITICAL | MEDIUM | HIGH | Planned |
| R06 | ADS1293 Library Size | HIGH | HIGH | VERY HIGH | Planned |
| R07 | Atomic Operations | CRITICAL | LOW | MEDIUM | Planned |
| R08 | String Buffer Overflows | HIGH | MEDIUM | HIGH | Planned |
| R09 | File I/O Errors | MEDIUM | LOW | LOW | Planned |
| R10 | Hardware Compatibility | HIGH | LOW | MEDIUM | Planned |
| R11 | Build System Migration | MEDIUM | MEDIUM | MEDIUM | Planned |
| R12 | Documentation Drift | MEDIUM | HIGH | MEDIUM | Planned |

---

## R01: THREAD SAFETY AND RACE CONDITIONS

**Severity:** CRITICAL
**Probability:** HIGH
**Impact:** System crashes, data corruption, unpredictable behavior

### Current C++ Implementation
- `std::thread` with RAII cleanup
- `std::atomic<bool>` with acquire/release memory ordering
- Lock-free communication via atomic flags
- Thread-safe string pointers

### C Conversion Challenges

**1. pthread vs std::thread differences:**
- Manual thread creation/join (no RAII)
- Need explicit pthread_attr_t configuration
- Cleanup handlers must be registered manually
- Thread cancellation handling required

**2. stdatomic.h vs std::atomic:**
- C11 atomics have different syntax
- Memory order constants differ: `memory_order_acquire` vs `std::memory_order_acquire`
- Type safety differences: `atomic_bool` vs `std::atomic<bool>`
- No operator overloading in C (must use explicit functions)

**3. Specific Problem Areas:**

| Location | Current C++ | C Challenge | Risk Level |
|----------|-------------|-------------|------------|
| JSON_TCP_sever::server_loop | std::thread member | pthread_t + manual management | HIGH |
| All atomic flags | std::atomic<bool> | atomic_bool + memory_order_* | CRITICAL |
| String pointer access | Implicit barriers | Explicit barriers needed | HIGH |
| Thread destruction | Automatic in destructor | Manual pthread_join() | MEDIUM |

### Example Risk Scenario
```cpp
// C++ (thread-safe)
if (request_ready_flag.load(std::memory_order_acquire)) {
    std::string response = process_JSON_line(request_json.c_str());
    request_ready_flag.store(false, std::memory_order_release);
}

// C (potential race if wrong memory ordering)
if (atomic_load_explicit(&request_ready_flag, memory_order_acquire)) {
    process_json_line(request_json, response_json, MAX_LEN);
    atomic_store_explicit(&request_ready_flag, false, memory_order_release);
}
// RISK: If memory ordering wrong, response might be read before written
```

### Mitigation Strategy

**Testing:**
1. Thread sanitizer (TSan) on all conversions
2. Stress test with rapid concurrent requests
3. Race condition detection tools (Valgrind/Helgrind)
4. Multi-core stress testing

**Code Review:**
1. Peer review of all atomic operations
2. Verify memory ordering semantics
3. Document threading invariants

**Implementation:**
1. Create threading wrapper library
2. Unit test each atomic operation
3. Maintain same synchronization pattern as C++

**Acceptance Criteria:**
- 1000+ rapid requests without crashes
- TSan clean report
- Helgrind clean report

---

## R02: TEMPLATE CONVERSION (register_container<T>)

**Severity:** CRITICAL
**Probability:** MEDIUM
**Impact:** Register access errors, sensor malfunction

### Current Template Usage

```cpp
template <typename DATA_TYPE>
class register_container {
public:
    volatile DATA_TYPE S;  // Register struct
    bool load_register(void);
    bool update_register(void);
};

// Used as:
register_container<CONFIG_REG_TYPE> config_reg(interface_ptr, 0x01);
register_container<STATUS_REG_TYPE> status_reg(interface_ptr, 0x02);
```

### C Conversion Options

**Option A: Macro-Based Generic Programming**
```c
#define DEFINE_REGISTER_CONTAINER(TYPE_NAME, DATA_TYPE) \
typedef struct { \
    volatile DATA_TYPE S; \
    vt_register_t* interface; \
    uint8_t address; \
} TYPE_NAME##_container_t; \
\
bool TYPE_NAME##_load_register(TYPE_NAME##_container_t* container) { \
    return container->interface->vtable->load_from_register( \
        container->interface->context, (uint8_t*)&container->S, container->address); \
}
```

**Risks:**
- Macro expansion errors
- Debugging difficulty
- Type safety reduced

**Option B: Void Pointer Generic**
```c
typedef struct {
    void* data;
    size_t data_size;
    vt_register_t* interface;
    uint8_t address;
} register_container_t;

bool register_container_load(register_container_t* container) {
    return container->interface->vtable->load_from_register(
        container->interface->context, container->data, container->address);
}
```

**Risks:**
- Loss of type safety
- Runtime errors vs compile-time errors
- Pointer casting required

**Option C: Type-Specific Implementations**
```c
// For each register type, create specific struct
typedef struct {
    volatile CONFIG_REG_TYPE S;
    vt_register_t* interface;
    uint8_t address;
} config_register_t;

bool config_register_load(config_register_t* reg);
bool config_register_update(config_register_t* reg);
```

**Risks:**
- Code duplication
- Maintenance burden
- But: Safest option, best debugging

### Mitigation Strategy

**Recommendation:** Option C (type-specific) for safety

**Testing:**
1. Compare register values before/after conversion
2. Verify all register types compile without warnings
3. Test register read/write operations

**Implementation:**
1. Inventory all register types used in ADS1293_LIB and MAX30009_LIB
2. Generate type-specific implementations
3. Create test cases for each register type

---

## R03: JSON API COMPATIBILITY

**Severity:** CRITICAL
**Probability:** MEDIUM
**Impact:** Clients break, protocol incompatibility

### Risk Areas

**1. Field Name Typos**
```c
// C++ (compiler catches)
response["temperature"] = temp;

// C (cJSON - runtime only)
cJSON_AddNumberToObject(response, "temperture", temp);  // TYPO!
// Client expects "temperature", gets nothing
```

**2. Data Type Mismatches**
```c
// C++ (auto-converts)
response["count"] = some_uint16;  // Becomes JSON number

// C (must specify)
cJSON_AddNumberToObject(response, "count", (double)some_uint16);
// If forget cast, might lose precision or truncate
```

**3. Array Structure Changes**
```cpp
// C++ (nlohmann/json)
json data_array = json::array();
data_array.push_back(value1);
data_array.push_back(value2);
response["data"] = data_array;

// C (cJSON)
cJSON *data_array = cJSON_CreateArray();
cJSON_AddItemToArray(data_array, cJSON_CreateNumber(value1));
cJSON_AddItemToArray(data_array, cJSON_CreateNumber(value2));
cJSON_AddItemToObject(response, "data", data_array);
// Easy to forget AddItemToObject at end!
```

### Mitigation Strategy

**Testing:**
1. JSON schema validation for all responses
2. Automated API compatibility tests
3. Compare C++ vs C output byte-by-byte

**Implementation:**
1. Create JSON response templates
2. Use macros for field names (avoid typos)
3. Automated test generation from API spec

**Example Safe Pattern:**
```c
#define JSON_FIELD_TYPE "type"
#define JSON_FIELD_VOLTAGE "voltage"
#define JSON_FIELD_TEMPERATURE "temperature"

cJSON_AddStringToObject(response, JSON_FIELD_TYPE, "batt_info");
cJSON_AddNumberToObject(response, JSON_FIELD_VOLTAGE, voltage);
```

**Acceptance Criteria:**
- All 13 commands produce identical JSON (excluding timestamps)
- JSON schema validator passes 100%
- Existing clients work without modification

---

## R04: MEMORY LEAKS AND MANAGEMENT

**Severity:** HIGH
**Probability:** MEDIUM
**Impact:** Memory exhaustion, system instability

### C++ RAII vs C Manual Management

| Resource | C++ Automatic | C Manual | Risk |
|----------|---------------|----------|------|
| GPIO lines | Destructor releases | Must call cleanup | HIGH |
| SPI file descriptors | Destructor closes | Must call close | HIGH |
| I2C file descriptors | Destructor closes | Must call close | HIGH |
| Sockets | Destructor closes | Must call close | CRITICAL |
| cJSON objects | N/A | Must call cJSON_Delete | HIGH |
| Threads | Destructor joins | Must call pthread_join | HIGH |
| Dynamic arrays | vector destructor | Must call free | MEDIUM |

### Specific Leak Scenarios

**1. Early Return Leaks**
```c
int process_command(const char* json_str) {
    cJSON *root = cJSON_Parse(json_str);
    if (root == NULL) return -1;  // LEAK! Forgot cJSON_Delete

    cJSON *type = cJSON_GetObjectItem(root, "type");
    if (type == NULL) return -1;  // LEAK! Forgot cJSON_Delete

    // ... process ...

    cJSON_Delete(root);
    return 0;
}
```

**Fixed version:**
```c
int process_command(const char* json_str) {
    cJSON *root = cJSON_Parse(json_str);
    if (root == NULL) return -1;

    int result = -1;
    cJSON *type = cJSON_GetObjectItem(root, "type");
    if (type == NULL) goto cleanup;

    // ... process ...
    result = 0;

cleanup:
    cJSON_Delete(root);
    return result;
}
```

**2. Exception Path Leaks**
- C++ try/catch ensures destructors run
- C has no exceptions, must use goto or careful returns

### Mitigation Strategy

**Static Analysis:**
1. Run Clang Static Analyzer
2. Run cppcheck with leak detection
3. Use scan-build on every commit

**Dynamic Analysis:**
1. Valgrind on all test cases
2. AddressSanitizer (ASan) build
3. LeakSanitizer (LSan) for long-running tests

**Code Patterns:**
1. Single-exit functions (use goto cleanup)
2. Resource acquisition wrapper functions
3. Consistent cleanup ordering

**Acceptance Criteria:**
- Valgrind shows 0 leaks after 24-hour run
- ASan clean on all test suites
- Static analyzer reports 0 issues

---

## R05: TIMING PRECISION MAINTENANCE

**Severity:** CRITICAL
**Probability:** MEDIUM
**Impact:** Sensor data corruption, sync errors

### Critical Timing Requirements

| Service | Loop Period | Tolerance | Purpose |
|---------|-------------|-----------|---------|
| spi-service | 500μs | ±10μs | Sensor data polling |
| spi-service | 1000ms | ±1ms | Sync mark insertion |
| power-service | 100ms | ±5ms | Battery monitoring, button |

### C++ vs C Timing Differences

**C++ Implementation:**
```cpp
auto last_call_time = std::chrono::steady_clock::now();
while(1) {
    auto current_time = std::chrono::steady_clock::now();
    auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(
        current_time - last_call_time);

    if (elapsed_time.count() >= 1000) {
        sync_num++;
        last_call_time = current_time;
    }

    usleep(500);  // 500μs
}
```

**C Implementation:**
```c
struct timespec last_call_time, current_time;
clock_gettime(CLOCK_MONOTONIC, &last_call_time);

while(1) {
    clock_gettime(CLOCK_MONOTONIC, &current_time);
    long elapsed_ms = (current_time.tv_sec - last_call_time.tv_sec) * 1000 +
                      (current_time.tv_nsec - last_call_time.tv_nsec) / 1000000;

    if (elapsed_ms >= 1000) {
        sync_num++;
        last_call_time = current_time;
    }

    usleep(500);
}
```

### Potential Issues

**1. Clock Drift:**
- `usleep(500)` is not precise (can drift)
- Accumulated error over time
- Sync marks might not be exactly 1 second apart

**2. System Load Impact:**
- High CPU load delays usleep wake-up
- Scheduler preemption
- Non-real-time Linux kernel

**3. Leap Time Handling:**
- CLOCK_MONOTONIC handles this correctly
- But must ensure using MONOTONIC, not REALTIME

### Mitigation Strategy

**Testing:**
1. Oscilloscope verification of sync mark timing
2. Long-duration drift measurement (24+ hours)
3. High-load stress test (CPU at 100%)

**Implementation:**
1. Use CLOCK_MONOTONIC consistently
2. Compensate for drift (adjust next delay)
3. Log timing statistics for monitoring

**Improved C Implementation:**
```c
struct timespec next_wake;
clock_gettime(CLOCK_MONOTONIC, &next_wake);

while(1) {
    // Calculate next wake time
    next_wake.tv_nsec += 500000;  // 500μs in nanoseconds
    if (next_wake.tv_nsec >= 1000000000) {
        next_wake.tv_sec++;
        next_wake.tv_nsec -= 1000000000;
    }

    // Sleep until absolute time (compensates for drift)
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_wake, NULL);

    // ... process ...
}
```

**Acceptance Criteria:**
- Sync marks at 1000ms ± 1ms over 24 hours
- Loop jitter < 10μs under normal load
- No missed sensor samples

---

## R06: ADS1293 LIBRARY SIZE AND COMPLEXITY

**Severity:** HIGH
**Probability:** HIGH
**Impact:** Conversion errors, long development time

### Statistics
- **File size:** 38,403 tokens
- **Methods:** 100+
- **Register containers:** 30+ instances
- **Namespace:** ADS1293::
- **Dependencies:** VTK interfaces, register_container<T>

### Risk Factors

**1. Sheer Volume:**
- Likely to introduce transcription errors
- Difficult to comprehensively test all paths

**2. Complex Register Interactions:**
- Many registers depend on each other
- Configuration order matters
- Easy to break subtle dependencies

**3. Namespace Removal:**
- All ADS1293:: qualifiers must be changed
- Enum names might conflict
- Type name collisions possible

### Mitigation Strategy

**Divide and Conquer:**
1. Split into modules:
   - Config registers (ads1293_config.c)
   - Channel control (ads1293_channels.c)
   - FIFO operations (ads1293_fifo.c)
   - Power management (ads1293_power.c)

**Automated Conversion:**
1. Use sed/awk for mechanical changes
2. Python script for namespace removal
3. Clang-format for consistent style

**Incremental Testing:**
1. Convert one module at a time
2. Test each module before moving on
3. Register snapshot comparison

**Code Generation:**
1. If register operations are repetitive, generate from spec
2. Reduces human error
3. Easier to verify correctness

**Acceptance Criteria:**
- All 100+ methods produce identical register values
- No namespace collisions
- Compiles without warnings

---

## R07: ATOMIC OPERATIONS AND MEMORY ORDERING

**Severity:** CRITICAL
**Probability:** LOW (with careful review)
**Impact:** Race conditions, undefined behavior

### Memory Ordering Semantics

| C++ | C11 | Equivalent |
|-----|-----|------------|
| std::memory_order_relaxed | memory_order_relaxed | ✓ |
| std::memory_order_acquire | memory_order_acquire | ✓ |
| std::memory_order_release | memory_order_release | ✓ |
| std::memory_order_acq_rel | memory_order_acq_rel | ✓ |
| std::memory_order_seq_cst | memory_order_seq_cst | ✓ |

**Good news:** Memory orderings are 1:1 compatible!

### Current Usage Pattern

```cpp
// Request side (TCP thread)
if (_request_ready_flag->load(std::memory_order_acquire) == false) {
    *_request_json = received_json_command;
    _request_ready_flag->store(true, std::memory_order_release);
}

// Process side (main loop)
if (request_ready_flag.load(std::memory_order_acquire) == true) {
    std::string response = process_JSON_line(request_json.c_str());
    request_ready_flag.store(false, std::memory_order_release);
    if (response_ready_flag.load(std::memory_order_release) == false) {
        response_json = response;
        response_ready_flag.store(true, std::memory_order_release);
    }
}
```

### C Conversion

```c
// Request side (TCP thread)
if (atomic_load_explicit(_request_ready_flag, memory_order_acquire) == false) {
    strncpy(_request_json, received_json_command, MAX_JSON_LEN - 1);
    atomic_store_explicit(_request_ready_flag, true, memory_order_release);
}

// Process side (main loop)
if (atomic_load_explicit(&request_ready_flag, memory_order_acquire) == true) {
    process_json_line(request_json, response, MAX_JSON_LEN);
    atomic_store_explicit(&request_ready_flag, false, memory_order_release);
    if (atomic_load_explicit(&response_ready_flag, memory_order_acquire) == false) {
        strncpy(response_json, response, MAX_JSON_LEN - 1);
        atomic_store_explicit(&response_ready_flag, true, memory_order_release);
    }
}
```

### Potential Pitfalls

**1. Forgot _explicit suffix:**
```c
atomic_load(&flag);  // Uses seq_cst, not acquire!
```

**2. Wrong memory order:**
```c
atomic_store_explicit(&flag, true, memory_order_acquire);  // WRONG! Store needs release
```

**3. Missing volatile on shared data:**
```c
char request_json[MAX_LEN];  // Should be volatile!
```

### Mitigation Strategy

**Code Pattern Template:**
1. Document required memory ordering for each atomic
2. Code review checklist for atomic operations
3. ThreadSanitizer to detect violations

**Acceptance Criteria:**
- TSan clean on all atomic operations
- Documented rationale for each memory ordering choice
- No undefined behavior reported by UBSan

---

## R08: STRING BUFFER OVERFLOWS

**Severity:** HIGH
**Probability:** MEDIUM
**Impact:** Security vulnerability, crashes

### Current C++ Safety

```cpp
std::string request_json;  // Grows automatically
std::string response_json; // No overflow possible
```

### C Risks

```c
char request_json[2048];   // Fixed size!
char response_json[2048];  // Can overflow
```

### Overflow Scenarios

**1. TCP Receive Overflow:**
```c
// UNSAFE:
recv(socket, buffer, sizeof(buffer), 0);
strcat(request_json, buffer);  // No bounds check!
```

**2. JSON Generation Overflow:**
```c
// UNSAFE:
sprintf(response_json, "{\"type\":\"data\",\"data\":[");
for (int i = 0; i < data_count; i++) {
    sprintf(temp, "[%d,%d,%d],", data[i].ch1, data[i].ch2, data[i].ch3);
    strcat(response_json, temp);  // Might overflow if data_count large!
}
```

**3. Timestamp Concatenation:**
```c
// UNSAFE:
strcpy(response, "{\"timestamp\":\"");
strcat(response, get_timestamp());
strcat(response, "\"}");  // No overflow check
```

### Mitigation Strategy

**Always Use Safe Functions:**

| Unsafe | Safe Alternative | Notes |
|--------|------------------|-------|
| strcpy | strncpy | Always specify max length |
| strcat | strncat | Check remaining space |
| sprintf | snprintf | Returns length, checks bounds |
| gets | fgets | Obsolete, never use gets |

**Safe Pattern:**
```c
#define MAX_JSON_LEN 2048

int json_add_string(char* json, size_t max_len, const char* key, const char* value) {
    size_t current_len = strlen(json);
    size_t remaining = max_len - current_len - 1;  // -1 for null terminator

    int written = snprintf(json + current_len, remaining, "\"%s\":\"%s\",", key, value);

    if (written < 0 || (size_t)written >= remaining) {
        // Overflow detected!
        return -1;
    }

    return 0;
}
```

**Compile-time Checks:**
```bash
gcc -D_FORTIFY_SOURCE=2 -Wformat-security -Wformat=2
```

**Runtime Checks:**
```bash
gcc -fsanitize=address  # Detects buffer overflows
```

**Acceptance Criteria:**
- All string operations use safe variants
- ASan clean on fuzz testing
- Static analyzer reports no buffer issues

---

## R09: FILE I/O ERRORS (Calibration Data)

**Severity:** MEDIUM
**Probability:** LOW
**Impact:** Lost calibration data

### Current C++ Implementation

```cpp
bool MAX30009_process::save_string_to_file(const std::string& filename, const std::string& data) {
    std::ofstream outfile(filename);
    if (!outfile.is_open()) return false;
    outfile << data;
    outfile.close();
    return true;
}
```

### C Conversion

```c
bool save_string_to_file(const char* filename, const char* data) {
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        perror("fopen");
        return false;
    }

    size_t len = strlen(data);
    size_t written = fwrite(data, 1, len, file);

    if (written != len) {
        perror("fwrite");
        fclose(file);
        return false;
    }

    if (fclose(file) != 0) {
        perror("fclose");
        return false;
    }

    return true;
}
```

### Risk Areas

1. **Permission errors:** Can't write to `calib/` directory
2. **Disk full:** fwrite fails
3. **Partial writes:** System crash during write
4. **File locking:** Multiple processes access same file

### Mitigation Strategy

**Atomic Writes:**
1. Write to temporary file first
2. fsync() to ensure data on disk
3. Rename to final filename (atomic operation)

**Error Handling:**
1. Check all return values
2. Log errors clearly
3. Fallback to default calibration if read fails

**Testing:**
1. Disk full simulation
2. Permission denied simulation
3. Concurrent access testing

---

## R10: HARDWARE COMPATIBILITY

**Severity:** HIGH
**Probability:** LOW
**Impact:** Firmware doesn't work on target

### Platform-Specific Concerns

**Raspberry Pi CM4:**
- ARM Cortex-A72 architecture
- NEON-FP-ARMV8 extensions
- 64-bit support

**Cross-Compilation:**
- Toolchain compatibility
- Library ABI matching
- Endianness (little-endian assumed)

### Mitigation Strategy

**Testing:**
1. Test on actual CM4 hardware early
2. QEMU emulation for rapid iteration
3. Verify all hardware interfaces (GPIO, SPI, I2C)

**Build Verification:**
1. Confirm ARM toolchain supports C11
2. Link against correct libc version
3. Check gpiod library ARM compatibility

---

## R11: BUILD SYSTEM MIGRATION

**Severity:** MEDIUM
**Probability:** MEDIUM
**Impact:** Build failures, deployment issues

### Changes Required

**CMakeLists.txt:**
- Change C++17 to C11
- Update source file extensions (.cpp → .c)
- Remove C++ standard library linkage
- Add cJSON library
- Update compiler flags

**Dockerfile:**
- Update toolchain if needed
- Add C-specific build tools
- Remove C++ specific dependencies

### Mitigation Strategy

**Parallel Builds:**
1. Maintain both C++ and C builds during transition
2. Use CMake options to switch

**Testing:**
1. Verify Docker build produces identical binaries (eventually)
2. Test cross-compilation early and often
3. Validate SHA256 hash generation

---

## R12: DOCUMENTATION DRIFT

**Severity:** MEDIUM
**Probability:** HIGH
**Impact:** Future maintainers confused, bugs reintroduced

### Risk

- CLAUDE.md becomes outdated
- Code comments don't reflect C patterns
- API documentation doesn't match implementation

### Mitigation Strategy

**Documentation Updates:**
1. Update CLAUDE.md with C-specific patterns
2. Add C coding style guide
3. Document all major architectural changes

**Code Comments:**
1. Update all class → struct comments
2. Document function pointer tables
3. Explain atomic operation memory orderings

**API Documentation:**
1. Regenerate API docs from code
2. Update all examples to C
3. Create migration guide for future developers

---

## RISK MITIGATION TIMELINE

### Week 1-2: Foundation (Low Risk)
- VTK interface conversion
- Hardware driver conversion
- **Mitigation:** Thorough unit testing

### Week 3-4: Critical Components (HIGH RISK)
- Template conversion (R02)
- TCP server threading (R01)
- **Mitigation:** Extensive testing, code review

### Week 5-6: Device Libraries (MEDIUM-HIGH RISK)
- ADS1293 conversion (R06)
- MAX30009 conversion
- **Mitigation:** Module-by-module, snapshot testing

### Week 7-8: Process Layer (HIGH RISK)
- JSON replacement (R03)
- String handling (R08)
- **Mitigation:** API compatibility tests

### Week 9-10: Integration (VERY HIGH RISK)
- Main loops (R05)
- Full system testing
- **Mitigation:** Hardware validation, timing tests

### Week 11-12: Validation
- 24-hour stability testing
- Memory leak detection
- Performance benchmarking

---

## QUALITY GATES

Each phase must pass before proceeding:

**Gate 1: Foundation**
- ✓ All VTK tests pass
- ✓ Driver tests pass on hardware
- ✓ Valgrind clean
- ✓ No compiler warnings

**Gate 2: Libraries**
- ✓ Register value comparison tests pass
- ✓ Template conversion verified
- ✓ JSON output matches C++ version
- ✓ Timing precision verified

**Gate 3: Integration**
- ✓ All 13 API commands work
- ✓ Thread sanitizer clean
- ✓ 1000+ request stress test passes
- ✓ 24-hour stability test passes

**Gate 4: Production**
- ✓ Hardware validation on CM4
- ✓ All sensors functioning
- ✓ Performance equal or better than C++
- ✓ Documentation complete

---

## CONTINGENCY PLANS

**If threading issues persist:**
- Fall back to single-threaded select() loop
- Trade concurrency for stability

**If JSON library has issues:**
- Try alternative (json-c instead of cJSON)
- Write custom minimal JSON parser

**If template conversion fails:**
- Use void* approach
- Accept reduced type safety

**If timing precision insufficient:**
- Use real-time Linux (PREEMPT_RT)
- Increase process priority
- Pin threads to CPU cores

**If ADS1293 conversion too risky:**
- Keep as C++ in separate module
- Use extern "C" bridge
- Defer full conversion

---

## SUCCESS METRICS

**Zero Defect Criteria:**
1. ✓ 0 memory leaks (Valgrind)
2. ✓ 0 race conditions (TSan)
3. ✓ 0 buffer overflows (ASan)
4. ✓ 0 undefined behavior (UBSan)
5. ✓ 100% API compatibility
6. ✓ 100% hardware test pass rate
7. ✓ Timing within spec (±1%)
8. ✓ 24-hour stability test
9. ✓ No regression in functionality
10. ✓ Code coverage > 80%

---

**Document Status:** COMPLETE
**Risk Areas Identified:** 12
**Mitigation Strategies:** 12
**Contingency Plans:** 5
**Success Metrics:** 10
**Last Updated:** 2025-11-22
