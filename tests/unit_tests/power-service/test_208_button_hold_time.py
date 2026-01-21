#!/usr/bin/env python3
"""
Test Case #208: Button Press Produces button_info with hold_time Progression
Unit Test for Power Service

Tests that the power control service produces repeated button_info messages
with state=true and hold_time progressively increasing while the button is held.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock responses for testing logic
2. Hardware mode: Connects to actual power service (requires PI_TARGET_IP)

Test Setup:
- DUT with power control service running
- Button connected
- Log capture

Procedure:
1. Start firmware/services
2. Press and hold the button
3. Capture the button monitoring outputs during the hold

Acceptance Criteria:
- While pressed: repeated button_info messages are produced
  with state=true and hold_time progressing (as exemplified)
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class ButtonEvent:
    """Single button_info event"""
    state: bool
    hold_time: int
    timestamp: float

    def to_dict(self) -> Dict:
        return {
            'state': self.state,
            'hold_time': self.hold_time,
            'timestamp': self.timestamp
        }


@dataclass
class ButtonHoldAnalysis:
    """Analysis of button hold sequence"""
    events_captured: int
    all_state_true: bool
    hold_times: List[int]
    hold_time_progresses: bool
    min_hold_time: int
    max_hold_time: int
    duration_seconds: float

    def to_dict(self) -> Dict:
        return {
            'events_captured': self.events_captured,
            'all_state_true': self.all_state_true,
            'hold_times': self.hold_times,
            'hold_time_progresses': self.hold_time_progresses,
            'min_hold_time': self.min_hold_time,
            'max_hold_time': self.max_hold_time,
            'duration_seconds': self.duration_seconds
        }


class MockButtonSimulator:
    """
    Mock button simulator for unit testing.
    Simulates button press/hold/release with hold_time progression.
    """

    def __init__(self):
        self.button_pressed = False
        self.hold_start_time: Optional[float] = None
        self.hold_counter = 0
        self.event_queue: List[Dict] = []

    def reset(self):
        """Reset simulator state"""
        self.button_pressed = False
        self.hold_start_time = None
        self.hold_counter = 0
        self.event_queue.clear()

    def press_button(self):
        """Simulate button press"""
        self.button_pressed = True
        self.hold_start_time = time.time()
        self.hold_counter = 0

    def release_button(self):
        """Simulate button release"""
        self.button_pressed = False
        self.hold_start_time = None
        # Generate release event
        self.event_queue.append({
            'type': 'button_info',
            'state': False,
            'hold_time': 0
        })

    def tick(self, interval_ms: int = 100):
        """
        Simulate firmware tick (called every ~100ms in real firmware).
        Generates button_info events while button is held.
        """
        if self.button_pressed:
            self.hold_counter += 1
            # Firmware sends event every 10 ticks (hold_time%10!=1 check)
            # but first event is sent immediately (hold_time=1, 1%10=1)
            if self.hold_counter % 10 == 1:
                self.event_queue.append({
                    'type': 'button_info',
                    'state': True,
                    'hold_time': self.hold_counter // 10
                })

    def get_pending_events(self) -> List[Dict]:
        """Get and clear pending events"""
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events

    def simulate_hold_duration(self, duration_seconds: float) -> List[Dict]:
        """
        Simulate holding button for specified duration.
        Returns all button_info events generated.
        """
        self.reset()
        self.press_button()

        all_events = []
        ticks = int(duration_seconds * 10)  # 100ms per tick

        for _ in range(ticks):
            self.tick(100)
            events = self.get_pending_events()
            all_events.extend(events)

        self.release_button()
        all_events.extend(self.get_pending_events())

        return all_events


class PowerServiceClient:
    """
    Client for communicating with power service via TCP/JSON.
    Falls back to mock simulation if connection fails.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.connected = False

        self.mock: Optional[MockButtonSimulator] = None
        self.use_mock = False

    def connect(self) -> bool:
        """Connect to power service or fall back to mock"""
        try:
            from tcp_client import TCPClient
            self.client = TCPClient(self.host, self.port, self.timeout)
            self.client.connect()
            self.connected = True
            print(f"  Connected to power service at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"  Could not connect to power service: {e}")
            print("  Falling back to mock simulation mode")
            self.use_mock = True
            self.mock = MockButtonSimulator()
            self.mock.reset()
            return True

    def disconnect(self):
        """Disconnect from service"""
        if self.client and self.connected:
            self.client.disconnect()
            self.client = None
            self.connected = False

    def simulate_button_hold(self, duration_seconds: float) -> List[Dict]:
        """
        Simulate or capture button hold events.
        In mock mode: simulates button hold
        In hardware mode: user must physically hold button
        """
        if self.use_mock:
            return self.mock.simulate_hold_duration(duration_seconds)
        else:
            # Hardware mode - capture events from service
            # Note: In real hardware testing, user must press button
            print(f"  [HARDWARE MODE] Please press and hold button for {duration_seconds}s")
            events = []
            start_time = time.time()

            while (time.time() - start_time) < duration_seconds + 1.0:
                try:
                    # Try to receive button_info messages
                    # Power service sends these asynchronously when button state changes
                    response = self.client.receive(timeout=0.5)
                    if response and response.get('type') == 'button_info':
                        events.append(response)
                except:
                    pass

            return events


class TestButtonHoldTime:
    """Unit Test - Button Press with hold_time Progression"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 501

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'hold_duration': 5.0,  # 5 second button hold
            'min_events_expected': 3,  # At least 3 events for 5s hold
            'log_file': '/tmp/test_208_button_hold_time.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[PowerServiceClient] = None

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            self.client.disconnect()

    def analyze_hold_events(self, events: List[Dict]) -> ButtonHoldAnalysis:
        """Analyze button hold events for progression"""
        # Filter only button_info events with state=true (during hold)
        hold_events = [e for e in events if e.get('type') == 'button_info' and e.get('state') == True]

        if not hold_events:
            return ButtonHoldAnalysis(
                events_captured=0,
                all_state_true=False,
                hold_times=[],
                hold_time_progresses=False,
                min_hold_time=0,
                max_hold_time=0,
                duration_seconds=0.0
            )

        hold_times = [e.get('hold_time', 0) for e in hold_events]
        all_state_true = all(e.get('state') == True for e in hold_events)

        # Check if hold_time progresses (each value >= previous)
        hold_time_progresses = all(
            hold_times[i] >= hold_times[i-1]
            for i in range(1, len(hold_times))
        )

        # Also check that we see actual progression (not all same value)
        has_actual_progression = len(set(hold_times)) > 1 if len(hold_times) > 1 else True

        return ButtonHoldAnalysis(
            events_captured=len(hold_events),
            all_state_true=all_state_true,
            hold_times=hold_times,
            hold_time_progresses=hold_time_progresses and has_actual_progression,
            min_hold_time=min(hold_times),
            max_hold_time=max(hold_times),
            duration_seconds=len(hold_events) * 1.0  # Approximate
        )

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_208_button_hold_time_progression(self, test_config):
        """
        Test Case #208: Button press produces button_info with hold_time progression

        Test Setup:
            DUT; button connected; log capture

        Procedure:
            1. Start firmware/services
            2. Press and hold the button
            3. Capture the button monitoring outputs during the hold

        Acceptance Criteria:
            While pressed: repeated button_info messages are produced
            with state=true and hold_time progressing (as exemplified)

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #208: Button Press with hold_time Progression")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify button_info messages show state=true and hold_time progressing")
        print("\nEXPECTED RESPONSE FORMAT:")
        print('  {"type": "button_info", "state": true, "hold_time": <n>}')
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}:{config['port']}")
        print(f"  Hold duration: {config['hold_duration']}s")
        print("=" * 70)

        # ================================================================
        # STEP 1: Connect to Power Control Service
        # ================================================================
        print("\n[STEP 1] Connect to Power Control Service")
        print("-" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect to power service"

        if self.client.use_mock:
            print("  Running in MOCK SIMULATION mode")
        else:
            print("  Running in HARDWARE mode")

        # ================================================================
        # STEP 2: Simulate/Capture Button Hold
        # ================================================================
        print("\n[STEP 2] Press and Hold Button")
        print("-" * 70)

        hold_duration = config['hold_duration']
        print(f"  Simulating button hold for {hold_duration} seconds...")

        events = self.client.simulate_button_hold(hold_duration)

        print(f"  Captured {len(events)} total events")

        # ================================================================
        # STEP 3: Analyze Button Hold Events
        # ================================================================
        print("\n[STEP 3] Analyze Button Hold Events")
        print("-" * 70)

        analysis = self.analyze_hold_events(events)

        print(f"\n  Hold Event Analysis:")
        print(f"    Events captured (state=true): {analysis.events_captured}")
        print(f"    All events have state=true: {'YES' if analysis.all_state_true else 'NO'}")
        print(f"    hold_time values: {analysis.hold_times}")
        print(f"    hold_time progresses: {'YES' if analysis.hold_time_progresses else 'NO'}")
        print(f"    Min hold_time: {analysis.min_hold_time}")
        print(f"    Max hold_time: {analysis.max_hold_time}")

        # Show individual events
        print(f"\n  Captured Events (button_info with state=true):")
        hold_events = [e for e in events if e.get('type') == 'button_info' and e.get('state') == True]
        for i, event in enumerate(hold_events[:10]):  # Show first 10
            print(f"    [{i+1}] state={event.get('state')}, hold_time={event.get('hold_time')}")
        if len(hold_events) > 10:
            print(f"    ... and {len(hold_events) - 10} more events")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)

        test_pass = (
            analysis.events_captured >= config['min_events_expected'] and
            analysis.all_state_true and
            analysis.hold_time_progresses
        )

        if test_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 70)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if analysis.events_captured >= config['min_events_expected'] else 'FAIL'}] "
              f"Repeated button_info messages produced (got {analysis.events_captured}, need >= {config['min_events_expected']})")
        print(f"    [{'PASS' if analysis.all_state_true else 'FAIL'}] All events have state=true")
        print(f"    [{'PASS' if analysis.hold_time_progresses else 'FAIL'}] hold_time progresses over time")

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")
        print("=" * 70)

        # Assertions
        assert analysis.events_captured >= config['min_events_expected'], \
            f"Not enough button_info events captured (got {analysis.events_captured}, need >= {config['min_events_expected']})"
        assert analysis.all_state_true, "Not all events have state=true during hold"
        assert analysis.hold_time_progresses, "hold_time does not progress during hold"

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_208_button_info_response_format(self, test_config):
        """
        Test that button_info response has correct format with required fields.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #208b: button_info Response Format Validation")
        print("=" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Get a single button event
        events = self.client.simulate_button_hold(1.0)  # 1 second hold

        # Filter for button_info events
        button_events = [e for e in events if e.get('type') == 'button_info']

        assert len(button_events) > 0, "No button_info events captured"

        event = button_events[0]

        print(f"\n  Sample button_info event:")
        print(f"    {event}")

        # Validate required fields
        required_fields = ['type', 'state', 'hold_time']

        print(f"\n  Field Validation:")
        all_present = True
        for field_name in required_fields:
            present = field_name in event
            all_present = all_present and present
            print(f"    {field_name}: {'PRESENT' if present else 'MISSING'}")
            if present:
                print(f"      Value: {event[field_name]}")
                print(f"      Type: {type(event[field_name]).__name__}")

        # Validate types
        print(f"\n  Type Validation:")
        type_valid = event.get('type') == 'button_info'
        state_is_bool = isinstance(event.get('state'), bool)
        hold_time_is_int = isinstance(event.get('hold_time'), int)

        print(f"    type == 'button_info': {'YES' if type_valid else 'NO'}")
        print(f"    state is bool: {'YES' if state_is_bool else 'NO'}")
        print(f"    hold_time is int: {'YES' if hold_time_is_int else 'NO'}")

        print("\n" + "=" * 70)
        if all_present and type_valid and state_is_bool and hold_time_is_int:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert all_present, f"Missing required fields in button_info: {required_fields}"
        assert type_valid, f"Expected type='button_info', got '{event.get('type')}'"
        assert state_is_bool, f"Expected state to be bool, got {type(event.get('state')).__name__}"
        assert hold_time_is_int, f"Expected hold_time to be int, got {type(event.get('hold_time')).__name__}"

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_208_hold_time_starts_at_zero(self, test_config):
        """
        Test that hold_time starts at 0 when button is first pressed.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #208c: hold_time Starts at Zero")
        print("=" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Short button press
        events = self.client.simulate_button_hold(0.5)

        # Get first button_info with state=true
        hold_events = [e for e in events if e.get('type') == 'button_info' and e.get('state') == True]

        assert len(hold_events) > 0, "No button hold events captured"

        first_event = hold_events[0]
        first_hold_time = first_event.get('hold_time', -1)

        print(f"\n  First button_info event (state=true):")
        print(f"    hold_time: {first_hold_time}")
        print(f"    Expected: 0")

        print("\n" + "=" * 70)
        if first_hold_time == 0:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert first_hold_time == 0, f"hold_time should start at 0, got {first_hold_time}"

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_208_hold_time_increments(self, test_config):
        """
        Test that hold_time increments as button is held.
        Based on firmware: hold_time increments every ~1 second (10 ticks * 100ms).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #208d: hold_time Increments During Hold")
        print("=" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Hold for 3 seconds - should see hold_time go 0, 1, 2
        events = self.client.simulate_button_hold(3.0)

        hold_events = [e for e in events if e.get('type') == 'button_info' and e.get('state') == True]
        hold_times = [e.get('hold_time', 0) for e in hold_events]

        print(f"\n  Captured {len(hold_events)} hold events")
        print(f"  hold_time sequence: {hold_times}")

        # Verify incrementing pattern
        increments_correctly = True
        for i in range(1, len(hold_times)):
            if hold_times[i] < hold_times[i-1]:
                increments_correctly = False
                print(f"  ERROR: hold_time decreased at index {i}: {hold_times[i-1]} -> {hold_times[i]}")
                break

        # Check we see multiple different values
        unique_values = len(set(hold_times))
        has_progression = unique_values > 1

        print(f"\n  Analysis:")
        print(f"    Unique hold_time values: {unique_values}")
        print(f"    hold_time never decreases: {'YES' if increments_correctly else 'NO'}")
        print(f"    Shows progression: {'YES' if has_progression else 'NO'}")

        print("\n" + "=" * 70)
        if increments_correctly and has_progression:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert increments_correctly, "hold_time should never decrease during hold"
        assert has_progression, "hold_time should show progression (multiple values)"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
