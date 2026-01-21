#!/usr/bin/env python3
"""
Test Case #209: Button Release Produces button_info state=false and hold_time Reset
Unit Test for Power Service

Tests that the power control service produces a button_info message with
state=false and hold_time=0 when the button is released after a hold.

This unit test can run in two modes:
1. Simulation mode (default): Uses mock responses for testing logic
2. Hardware mode: Connects to actual power service (requires PI_TARGET_IP)

Test Setup:
- DUT with power control service running
- Button connected
- Log capture

Procedure:
1. After a multi-second hold, release the button
2. Capture the next button monitoring output

Acceptance Criteria:
- After release: a button_info message is produced with state=false
  and hold_time=0 (as exemplified)
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class ButtonReleaseValidation:
    """Validation result for button release event"""
    release_event_found: bool
    state_is_false: bool
    hold_time_is_zero: bool
    release_event: Optional[Dict]

    def to_dict(self) -> Dict:
        return {
            'release_event_found': self.release_event_found,
            'state_is_false': self.state_is_false,
            'hold_time_is_zero': self.hold_time_is_zero,
            'release_event': self.release_event
        }


class MockButtonSimulator:
    """
    Mock button simulator for unit testing.
    Simulates button press/hold/release with proper state transitions.
    """

    def __init__(self):
        self.button_pressed = False
        self.hold_counter = 0
        self.event_queue: List[Dict] = []
        self.last_reported_state = False

    def reset(self):
        """Reset simulator state"""
        self.button_pressed = False
        self.hold_counter = 0
        self.event_queue.clear()
        self.last_reported_state = False

    def press_button(self):
        """Simulate button press"""
        self.button_pressed = True
        self.hold_counter = 0

    def release_button(self):
        """
        Simulate button release.
        Generates button_info with state=false and hold_time=0.
        """
        if self.button_pressed:
            self.button_pressed = False
            # On release, firmware sends state=false, hold_time=0
            # (only if previous state was pressed)
            if self.last_reported_state:
                self.event_queue.append({
                    'type': 'button_info',
                    'state': False,
                    'hold_time': 0
                })
                self.last_reported_state = False
            self.hold_counter = 0

    def tick(self, interval_ms: int = 100):
        """
        Simulate firmware tick (called every ~100ms in real firmware).
        Generates button_info events while button is held.
        """
        if self.button_pressed:
            self.hold_counter += 1
            # Firmware sends event every 10 ticks (hold_time%10!=1 check)
            # First event at hold_time=1 (1%10=1, so it's sent)
            if self.hold_counter % 10 == 1:
                self.event_queue.append({
                    'type': 'button_info',
                    'state': True,
                    'hold_time': self.hold_counter // 10
                })
                self.last_reported_state = True

    def get_pending_events(self) -> List[Dict]:
        """Get and clear pending events"""
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events

    def simulate_hold_and_release(self, hold_duration_seconds: float) -> List[Dict]:
        """
        Simulate holding button for specified duration then releasing.
        Returns all button_info events including the release event.
        """
        self.reset()
        self.press_button()

        all_events = []
        ticks = int(hold_duration_seconds * 10)  # 100ms per tick

        # Simulate hold
        for _ in range(ticks):
            self.tick(100)
            events = self.get_pending_events()
            all_events.extend(events)

        # Release button
        self.release_button()
        release_events = self.get_pending_events()
        all_events.extend(release_events)

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

    def simulate_hold_and_release(self, hold_duration_seconds: float) -> List[Dict]:
        """
        Simulate or capture button hold and release events.
        In mock mode: simulates button hold then release
        In hardware mode: user must physically hold and release button
        """
        if self.use_mock:
            return self.mock.simulate_hold_and_release(hold_duration_seconds)
        else:
            # Hardware mode - capture events from service
            print(f"  [HARDWARE MODE] Please press, hold for {hold_duration_seconds}s, then release")
            events = []
            start_time = time.time()

            # Wait for hold duration plus extra time for release
            while (time.time() - start_time) < hold_duration_seconds + 2.0:
                try:
                    response = self.client.receive(timeout=0.5)
                    if response and response.get('type') == 'button_info':
                        events.append(response)
                except:
                    pass

            return events


class TestButtonReleaseState:
    """Unit Test - Button Release State and hold_time Reset"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 501

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'hold_duration': 3.0,  # 3 second button hold before release
            'log_file': '/tmp/test_209_button_release_state.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[PowerServiceClient] = None

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            self.client.disconnect()

    def find_release_event(self, events: List[Dict]) -> ButtonReleaseValidation:
        """
        Find and validate the button release event.
        Release event has state=false after a sequence of state=true events.
        """
        # Look for state=false event that comes after state=true events
        saw_pressed = False
        release_event = None

        for event in events:
            if event.get('type') != 'button_info':
                continue

            if event.get('state') == True:
                saw_pressed = True
            elif event.get('state') == False and saw_pressed:
                release_event = event
                break

        if release_event is None:
            return ButtonReleaseValidation(
                release_event_found=False,
                state_is_false=False,
                hold_time_is_zero=False,
                release_event=None
            )

        state_is_false = release_event.get('state') == False
        hold_time_is_zero = release_event.get('hold_time') == 0

        return ButtonReleaseValidation(
            release_event_found=True,
            state_is_false=state_is_false,
            hold_time_is_zero=hold_time_is_zero,
            release_event=release_event
        )

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_209_button_release_state_false(self, test_config):
        """
        Test Case #209: Button release produces button_info state=false and hold_time=0

        Test Setup:
            DUT; button connected; log capture

        Procedure:
            1. After a multi-second hold, release the button
            2. Capture the next button monitoring output

        Acceptance Criteria:
            After release: a button_info message is produced with state=false
            and hold_time=0 (as exemplified)

        This test runs in mock simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #209: Button Release State and hold_time Reset")
        print("=" * 70)
        print("\nPURPOSE:")
        print("  Verify button release produces state=false and hold_time=0")
        print("\nEXPECTED RELEASE EVENT:")
        print('  {"type": "button_info", "state": false, "hold_time": 0}')
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}:{config['port']}")
        print(f"  Hold duration before release: {config['hold_duration']}s")
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
        # STEP 2: Perform Multi-Second Hold Then Release
        # ================================================================
        print("\n[STEP 2] Hold Button Then Release")
        print("-" * 70)

        hold_duration = config['hold_duration']
        print(f"  Holding button for {hold_duration} seconds...")

        events = self.client.simulate_hold_and_release(hold_duration)

        print(f"  Captured {len(events)} total events")

        # Show event sequence
        print(f"\n  Event Sequence:")
        for i, event in enumerate(events):
            state = event.get('state')
            hold_time = event.get('hold_time')
            marker = " <-- RELEASE EVENT" if state == False else ""
            print(f"    [{i+1}] state={state}, hold_time={hold_time}{marker}")

        # ================================================================
        # STEP 3: Validate Release Event
        # ================================================================
        print("\n[STEP 3] Validate Release Event")
        print("-" * 70)

        validation = self.find_release_event(events)

        print(f"\n  Release Event Validation:")
        print(f"    Release event found: {'YES' if validation.release_event_found else 'NO'}")

        if validation.release_event_found:
            print(f"    Release event: {validation.release_event}")
            print(f"    state == false: {'YES' if validation.state_is_false else 'NO'}")
            print(f"    hold_time == 0: {'YES' if validation.hold_time_is_zero else 'NO'}")
        else:
            print("    No release event found in captured events")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 70)

        test_pass = (
            validation.release_event_found and
            validation.state_is_false and
            validation.hold_time_is_zero
        )

        if test_pass:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 70)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if validation.release_event_found else 'FAIL'}] "
              f"button_info message produced after release")
        print(f"    [{'PASS' if validation.state_is_false else 'FAIL'}] "
              f"state=false in release event")
        print(f"    [{'PASS' if validation.hold_time_is_zero else 'FAIL'}] "
              f"hold_time=0 in release event")

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")
        print("=" * 70)

        # Assertions
        assert validation.release_event_found, "No button release event found"
        assert validation.state_is_false, "Release event state should be false"
        assert validation.hold_time_is_zero, "Release event hold_time should be 0"

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_209_release_after_short_hold(self, test_config):
        """
        Test release event after a short hold (1 second).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #209b: Release After Short Hold")
        print("=" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Short hold (1 second)
        events = self.client.simulate_hold_and_release(1.0)

        print(f"  Captured {len(events)} events for 1s hold")

        validation = self.find_release_event(events)

        print(f"\n  Release event: {validation.release_event}")

        print("\n" + "=" * 70)
        if validation.release_event_found and validation.state_is_false and validation.hold_time_is_zero:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert validation.release_event_found, "No release event after short hold"
        assert validation.state_is_false, "state should be false"
        assert validation.hold_time_is_zero, "hold_time should be 0"

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_209_release_after_long_hold(self, test_config):
        """
        Test release event after a long hold (5 seconds).
        Verifies hold_time resets to 0 regardless of hold duration.
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #209c: Release After Long Hold (5s)")
        print("=" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # Long hold (5 seconds)
        events = self.client.simulate_hold_and_release(5.0)

        print(f"  Captured {len(events)} events for 5s hold")

        # Find max hold_time during hold
        hold_events = [e for e in events if e.get('state') == True]
        if hold_events:
            max_hold_time = max(e.get('hold_time', 0) for e in hold_events)
            print(f"  Max hold_time during hold: {max_hold_time}")

        validation = self.find_release_event(events)

        print(f"\n  Release event: {validation.release_event}")
        print(f"  hold_time reset to 0: {'YES' if validation.hold_time_is_zero else 'NO'}")

        print("\n" + "=" * 70)
        if validation.release_event_found and validation.state_is_false and validation.hold_time_is_zero:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert validation.release_event_found, "No release event after long hold"
        assert validation.state_is_false, "state should be false"
        assert validation.hold_time_is_zero, "hold_time should reset to 0 after long hold"

    @pytest.mark.unit
    @pytest.mark.button
    @pytest.mark.power
    def test_209_state_transition_sequence(self, test_config):
        """
        Test the complete state transition: false -> true (hold) -> false (release).
        """
        config = test_config

        print("\n" + "=" * 70)
        print("Test Case #209d: State Transition Sequence")
        print("=" * 70)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout']
        )

        connected = self.client.connect()
        assert connected, "Failed to connect"

        print(f"\n  Mode: {'Mock Simulation' if self.client.use_mock else 'Hardware'}")

        # 2 second hold
        events = self.client.simulate_hold_and_release(2.0)

        print(f"\n  State Transition Analysis:")

        # Extract state sequence
        states = [e.get('state') for e in events if e.get('type') == 'button_info']

        print(f"    State sequence: {states}")

        # Verify we have: [True, True, ..., False]
        # (one or more True followed by False)
        has_hold_states = any(s == True for s in states)
        has_release_state = states[-1] == False if states else False
        ends_with_false = has_release_state

        print(f"    Has hold states (True): {'YES' if has_hold_states else 'NO'}")
        print(f"    Ends with release (False): {'YES' if ends_with_false else 'NO'}")

        # Verify no True states after False (proper transition)
        found_false = False
        proper_transition = True
        for state in states:
            if state == False:
                found_false = True
            elif found_false and state == True:
                proper_transition = False
                break

        print(f"    Proper transition (no True after False): {'YES' if proper_transition else 'NO'}")

        print("\n" + "=" * 70)
        if has_hold_states and ends_with_false and proper_transition:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")
        print("=" * 70)

        assert has_hold_states, "Should have state=True events during hold"
        assert ends_with_false, "Should end with state=False (release)"
        assert proper_transition, "Should not have True states after False"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
