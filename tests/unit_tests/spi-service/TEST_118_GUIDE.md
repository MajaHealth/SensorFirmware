# Test #118 Execution Guide
## Display Rendering Quality - Unit Test (Manual Verification)

---

## Quick Start

```bash
# Set CM4 IP and run
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_118_display_rendering_quality.py -v -s
```

---

## Test Overview

### What This Test Does
Validates display rendering quality:
1. Renders test patterns on display
2. Displays color bars for visual inspection
3. Shows text rendering samples
4. Tests gradient rendering

### Why This Matters
- Ensures display renders correctly
- Validates color accuracy
- Confirms text is readable

---

## Automation Level

### Semi-Automated (Visual Inspection Required)

This test renders patterns but **requires visual inspection**:
- Test will render patterns on display
- User must visually verify quality
- Test prompts for pass/fail confirmation

---

## Prerequisites

### Hardware Required
- Raspberry Pi CM4
- DSI display connected and visible
- Network connection to CM4 (for SSH access)

### Connection Method
This test uses **SSH commands** to render test images (`fbi`) on the CM4.
It does NOT require spi-service to be running.

### Software Required
```bash
pip install pytest pyyaml
```

---

## Running the Test

```bash
export PI_TARGET_IP=192.168.1.4
pytest tests/unit_tests/spi-service/test_118_display_rendering_quality.py -v -s
```

---

## Expected Output

```
======================================================================
Test Case #118: Display Rendering Quality
======================================================================

[STEP 1] Render Color Bars
----------------------------------------------------------------------
  Rendering: Red, Green, Blue, White bars
  → Visually inspect display now

[STEP 2] Render Text Sample
----------------------------------------------------------------------
  Rendering: "Test 118 - Quality Check"
  → Verify text is clear and readable

[STEP 3] Render Gradient
----------------------------------------------------------------------
  Rendering: Black-to-white gradient
  → Verify smooth transitions, no banding

[USER INPUT] Visual Inspection
----------------------------------------------------------------------
  Did the display render correctly? (y/n): _
```

---

## Visual Inspection Checklist

- [ ] Color bars show distinct Red, Green, Blue, White
- [ ] No color bleeding or artifacts
- [ ] Text is sharp and readable
- [ ] Gradient is smooth without banding
- [ ] No dead pixels visible
- [ ] Screen fills completely (no black borders)

---

## Troubleshooting

### Issue: Display is blank
- Verify display is powered on
- Check DSI connection
- Ensure display is initialized (run Test #116 first)

### Issue: Colors look wrong
- Check display color profile
- Verify RGB/BGR order in driver

---

## Related Tests
- **Test #116:** DSI display detection
- **Test #117:** Display power mode
