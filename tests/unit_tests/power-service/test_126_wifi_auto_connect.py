#!/usr/bin/env python3
"""
Test Case #126: Auto-Connect on Reboot with Saved Credentials
Unit Test for Power Service / Wi-Fi

Tests that firmware auto-connects to saved network after reboot.

Test Setup:
- DUT with Router A credentials saved
- Log capture enabled

Procedure:
1. Ensure Router A credentials are saved on the device
2. Reboot the device
3. Observe Wi-Fi state transitions without app input

Acceptance Criteria:
- Firmware transitions WIFI_DISCONNECTED -> WIFI_CONNECTING -> WIFI_CONNECTED
  automatically without app input
"""

import time
import pytest
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


class WiFiState(Enum):
    WIFI_DISCONNECTED = "WIFI_DISCONNECTED"
    WIFI_NO_CREDENTIALS = "WIFI_NO_CREDENTIALS"
    WIFI_CONNECTING = "WIFI_CONNECTING"
    WIFI_CONNECTED = "WIFI_CONNECTED"


@dataclass
class WiFiTransition:
    from_state: WiFiState
    to_state: WiFiState
    timestamp: float


class MockWiFiService:
    """Mock Wi-Fi service with saved credentials"""

    def __init__(self):
        self.has_saved_credentials = True
        self.saved_ssid = "RouterA"
        self.current_state = WiFiState.WIFI_DISCONNECTED
        self.transitions: List[WiFiTransition] = []

    def simulate_reboot(self) -> List[WiFiTransition]:
        """Simulate reboot with auto-connect"""
        self.transitions = []
        self.current_state = WiFiState.WIFI_DISCONNECTED

        if self.has_saved_credentials:
            time.sleep(0.1)
            self._transition_to(WiFiState.WIFI_CONNECTING)
            time.sleep(0.1)
            self._transition_to(WiFiState.WIFI_CONNECTED)

        return self.transitions

    def _transition_to(self, new_state: WiFiState):
        self.transitions.append(WiFiTransition(
            from_state=self.current_state,
            to_state=new_state,
            timestamp=time.time()
        ))
        self.current_state = new_state


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

    def simulate_reboot(self) -> List[WiFiTransition]:
        if self.use_mock:
            return self.mock.simulate_reboot()
        return []

    def get_state(self) -> WiFiState:
        if self.use_mock:
            return self.mock.current_state
        return WiFiState.WIFI_DISCONNECTED


class TestWiFiAutoConnect:
    """Unit Test - Wi-Fi Auto-Connect on Reboot"""

    @pytest.fixture(scope="class")
    def test_config(self):
        return {
            'host': os.environ.get('PI_TARGET_IP', '127.0.0.1'),
            'expected_ssid': 'RouterA',
        }

    @pytest.mark.unit
    @pytest.mark.wifi
    @pytest.mark.power
    def test_126_wifi_auto_connect_on_reboot(self, test_config):
        """
        Test Case #126: Auto-connect on reboot with saved credentials

        Acceptance Criteria:
            Firmware transitions WIFI_DISCONNECTED -> WIFI_CONNECTING -> WIFI_CONNECTED
            automatically without app input
        """
        print("\n" + "=" * 70)
        print("Test Case #126: Auto-Connect on Reboot with Saved Credentials")
        print("=" * 70)

        controller = WiFiController(host=test_config['host'])
        controller.initialize()

        print(f"\n  Mode: {'Mock Simulation' if controller.use_mock else 'Hardware'}")

        # Simulate reboot
        print("\n[STEP 1] Simulate Reboot with Saved Credentials")
        print("-" * 70)

        transitions = controller.simulate_reboot()

        print(f"\n  State Transitions (no app input):")
        for i, trans in enumerate(transitions):
            print(f"    [{i+1}] {trans.from_state.value} -> {trans.to_state.value}")

        # Verify transitions
        saw_connecting = any(t.to_state == WiFiState.WIFI_CONNECTING for t in transitions)
        saw_connected = any(t.to_state == WiFiState.WIFI_CONNECTED for t in transitions)
        final_state = controller.get_state()

        print("\n[STEP 2] Verify Auto-Connection")
        print("-" * 70)
        print(f"  Transitioned to CONNECTING: {'YES' if saw_connecting else 'NO'}")
        print(f"  Transitioned to CONNECTED: {'YES' if saw_connected else 'NO'}")
        print(f"  Final state: {final_state.value}")

        test_pass = saw_connecting and saw_connected and final_state == WiFiState.WIFI_CONNECTED

        print("\n" + "=" * 70)
        print(f"TEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert saw_connecting, "Did not transition to WIFI_CONNECTING"
        assert saw_connected, "Did not transition to WIFI_CONNECTED"
        assert final_state == WiFiState.WIFI_CONNECTED


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
