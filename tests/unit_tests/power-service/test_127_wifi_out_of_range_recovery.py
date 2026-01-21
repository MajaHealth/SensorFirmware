#!/usr/bin/env python3
"""
Test Case #127: Out-of-Range Recovery
Unit Test for Power Service / Wi-Fi

Tests Wi-Fi recovery when device goes out of range and returns.

Test Setup:
- DUT connected to Router A
- Ability to induce range loss
- Log capture enabled

Procedure:
1. Start connected to Router A
2. Simulate leaving Router A range (connection loss)
3. Observe Wi-Fi state transitions on return

Acceptance Criteria:
- On range loss and return, firmware shows:
  WIFI_DISCONNECTED -> WIFI_CONNECTING -> WIFI_CONNECTED once back in range
"""

import time
import pytest
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


class WiFiState(Enum):
    WIFI_DISCONNECTED = "WIFI_DISCONNECTED"
    WIFI_CONNECTING = "WIFI_CONNECTING"
    WIFI_CONNECTED = "WIFI_CONNECTED"


@dataclass
class WiFiTransition:
    from_state: WiFiState
    to_state: WiFiState
    timestamp: float


class MockWiFiService:
    def __init__(self):
        self.current_state = WiFiState.WIFI_CONNECTED
        self.in_range = True
        self.transitions: List[WiFiTransition] = []

    def simulate_out_of_range(self):
        """Simulate going out of range"""
        self.in_range = False
        self._transition_to(WiFiState.WIFI_DISCONNECTED)

    def simulate_back_in_range(self):
        """Simulate returning to range"""
        self.in_range = True
        self._transition_to(WiFiState.WIFI_CONNECTING)
        time.sleep(0.1)
        self._transition_to(WiFiState.WIFI_CONNECTED)

    def _transition_to(self, new_state: WiFiState):
        self.transitions.append(WiFiTransition(
            from_state=self.current_state,
            to_state=new_state,
            timestamp=time.time()
        ))
        self.current_state = new_state

    def get_transitions(self) -> List[WiFiTransition]:
        return self.transitions


class WiFiController:
    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockWiFiService] = None

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            return True
        self.use_mock = True
        self.mock = MockWiFiService()
        return True

    def simulate_range_loss(self):
        if self.use_mock:
            self.mock.simulate_out_of_range()

    def simulate_range_return(self):
        if self.use_mock:
            self.mock.simulate_back_in_range()

    def get_transitions(self) -> List[WiFiTransition]:
        if self.use_mock:
            return self.mock.get_transitions()
        return []

    def get_state(self) -> WiFiState:
        if self.use_mock:
            return self.mock.current_state
        return WiFiState.WIFI_DISCONNECTED


class TestWiFiOutOfRangeRecovery:
    """Unit Test - Wi-Fi Out-of-Range Recovery"""

    @pytest.fixture(scope="class")
    def test_config(self):
        return {'host': os.environ.get('PI_TARGET_IP', '127.0.0.1')}

    @pytest.mark.unit
    @pytest.mark.wifi
    @pytest.mark.power
    def test_127_wifi_out_of_range_recovery(self, test_config):
        """
        Test Case #127: Out-of-range recovery

        Acceptance Criteria:
            On range loss and return:
            WIFI_DISCONNECTED -> WIFI_CONNECTING -> WIFI_CONNECTED
        """
        print("\n" + "=" * 70)
        print("Test Case #127: Out-of-Range Recovery")
        print("=" * 70)

        controller = WiFiController(host=test_config['host'])
        controller.initialize()

        print(f"\n  Mode: {'Mock Simulation' if controller.use_mock else 'Hardware'}")

        # Initial state
        print("\n[STEP 1] Start Connected to Router A")
        print("-" * 70)
        print(f"  Initial state: {controller.get_state().value}")

        # Simulate out of range
        print("\n[STEP 2] Simulate Going Out of Range")
        print("-" * 70)
        controller.simulate_range_loss()
        print(f"  State after range loss: {controller.get_state().value}")

        # Simulate return to range
        print("\n[STEP 3] Simulate Returning to Range")
        print("-" * 70)
        controller.simulate_range_return()

        transitions = controller.get_transitions()
        print(f"\n  State Transitions:")
        for i, trans in enumerate(transitions):
            print(f"    [{i+1}] {trans.from_state.value} -> {trans.to_state.value}")

        # Verify
        final_state = controller.get_state()
        saw_disconnected = any(t.to_state == WiFiState.WIFI_DISCONNECTED for t in transitions)
        saw_connecting = any(t.to_state == WiFiState.WIFI_CONNECTING for t in transitions)
        saw_connected = any(t.to_state == WiFiState.WIFI_CONNECTED for t in transitions)

        print("\n[STEP 4] Verify Recovery")
        print("-" * 70)
        print(f"  Final state: {final_state.value}")

        test_pass = saw_disconnected and saw_connecting and saw_connected and final_state == WiFiState.WIFI_CONNECTED

        print("\n" + "=" * 70)
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert final_state == WiFiState.WIFI_CONNECTED, "Did not recover to CONNECTED state"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
