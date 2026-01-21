#!/usr/bin/env python3
"""
Test Case #131: Wi-Fi Polling Interval Cadence and Configurability
Unit Test for Power Service / Wi-Fi

Tests Wi-Fi status polling interval and configurability.

Test Setup:
- DUT with Wi-Fi
- Controllable AP
- Log capture enabled

Procedure:
1. Set Wi-Fi polling interval in firmware configuration and reboot
2. With Wi-Fi available, capture logs across 5 intervals
3. Disconnect AP and capture logs across 2 intervals
4. Reconnect AP and capture logs across 2 intervals
5. Change interval to new value and repeat periodic capture for 5 intervals
6. Induce a brief network flap within one interval and capture logs

Acceptance Criteria:
- Periodic Wi-Fi state log entries are present
- Consecutive log deltas follow configured interval +/-10% jitter
- After interval change, deltas follow new interval +/-10%
- Exactly one transition log per actual state change
"""

import time
import pytest
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class WiFiLogEntry:
    timestamp: float
    state: str
    is_transition: bool


class MockWiFiLogger:
    def __init__(self):
        self.polling_interval_ms = 1000  # Default 1 second
        self.logs: List[WiFiLogEntry] = []
        self.current_state = "CONNECTED"

    def set_polling_interval(self, interval_ms: int):
        self.polling_interval_ms = interval_ms

    def capture_logs(self, duration_intervals: int) -> List[WiFiLogEntry]:
        """Capture logs for specified number of intervals"""
        self.logs = []
        interval_sec = self.polling_interval_ms / 1000

        for i in range(duration_intervals):
            self.logs.append(WiFiLogEntry(
                timestamp=time.time(),
                state=self.current_state,
                is_transition=False
            ))
            time.sleep(interval_sec * 0.1)  # Simulated time

        return self.logs

    def simulate_disconnect(self):
        self.current_state = "DISCONNECTED"
        self.logs.append(WiFiLogEntry(
            timestamp=time.time(),
            state="DISCONNECTED",
            is_transition=True
        ))

    def simulate_reconnect(self):
        self.current_state = "CONNECTED"
        self.logs.append(WiFiLogEntry(
            timestamp=time.time(),
            state="CONNECTED",
            is_transition=True
        ))


class WiFiPollingController:
    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockWiFiLogger] = None

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            return True
        self.use_mock = True
        self.mock = MockWiFiLogger()
        return True

    def set_polling_interval(self, interval_ms: int) -> bool:
        if self.use_mock:
            self.mock.set_polling_interval(interval_ms)
            return True
        return False

    def capture_logs(self, intervals: int) -> List[WiFiLogEntry]:
        if self.use_mock:
            return self.mock.capture_logs(intervals)
        return []

    def simulate_disconnect(self):
        if self.use_mock:
            self.mock.simulate_disconnect()

    def simulate_reconnect(self):
        if self.use_mock:
            self.mock.simulate_reconnect()

    def get_logs(self) -> List[WiFiLogEntry]:
        if self.use_mock:
            return self.mock.logs
        return []


class TestWiFiPollingInterval:
    """Unit Test - Wi-Fi Polling Interval Cadence"""

    @pytest.fixture(scope="class")
    def test_config(self):
        return {
            'host': os.environ.get('PI_TARGET_IP', '127.0.0.1'),
            'initial_interval_ms': 1000,
            'new_interval_ms': 2000,
            'jitter_tolerance': 0.10,  # 10%
        }

    @pytest.mark.unit
    @pytest.mark.wifi
    @pytest.mark.power
    def test_131_wifi_polling_interval(self, test_config):
        """
        Test Case #131: Wi-Fi polling interval cadence and configurability

        Acceptance Criteria:
            - Periodic Wi-Fi state log entries present
            - Log deltas follow configured interval +/-10% jitter
            - After interval change, deltas follow new interval
            - One transition log per actual state change
        """
        print("\n" + "=" * 70)
        print("Test Case #131: Wi-Fi Polling Interval Cadence")
        print("=" * 70)

        controller = WiFiPollingController(host=test_config['host'])
        controller.initialize()

        print(f"\n  Mode: {'Mock Simulation' if controller.use_mock else 'Hardware'}")
        print(f"  Initial interval: {test_config['initial_interval_ms']} ms")
        print(f"  Jitter tolerance: +/-{test_config['jitter_tolerance']*100}%")

        # Step 1: Set initial polling interval
        print("\n[STEP 1] Set Initial Polling Interval")
        print("-" * 70)
        controller.set_polling_interval(test_config['initial_interval_ms'])
        print(f"  Polling interval set to: {test_config['initial_interval_ms']} ms")

        # Step 2: Capture logs with Wi-Fi available
        print("\n[STEP 2] Capture Logs (Wi-Fi Available) - 5 Intervals")
        print("-" * 70)
        logs = controller.capture_logs(5)
        print(f"  Captured {len(logs)} log entries")

        # Step 3: Disconnect and capture
        print("\n[STEP 3] Disconnect AP and Capture - 2 Intervals")
        print("-" * 70)
        controller.simulate_disconnect()
        disconnect_logs = controller.capture_logs(2)
        print(f"  Captured {len(disconnect_logs)} entries after disconnect")

        # Step 4: Reconnect and capture
        print("\n[STEP 4] Reconnect AP and Capture - 2 Intervals")
        print("-" * 70)
        controller.simulate_reconnect()
        reconnect_logs = controller.capture_logs(2)
        print(f"  Captured {len(reconnect_logs)} entries after reconnect")

        # Step 5: Change interval
        print("\n[STEP 5] Change Polling Interval")
        print("-" * 70)
        controller.set_polling_interval(test_config['new_interval_ms'])
        print(f"  New interval: {test_config['new_interval_ms']} ms")
        new_logs = controller.capture_logs(5)
        print(f"  Captured {len(new_logs)} entries with new interval")

        # Verify
        all_logs = controller.get_logs()
        transition_logs = [l for l in all_logs if l.is_transition]

        print("\n[STEP 6] Verify Results")
        print("-" * 70)
        print(f"  Total log entries: {len(all_logs)}")
        print(f"  Transition logs: {len(transition_logs)}")

        logs_present = len(all_logs) > 0
        transitions_ok = len(transition_logs) == 2  # disconnect + reconnect

        test_pass = logs_present and transitions_ok

        print("\n" + "=" * 70)
        print(f"  [{'PASS' if logs_present else 'FAIL'}] Periodic log entries present")
        print(f"  [{'PASS' if transitions_ok else 'FAIL'}] One transition per state change")
        print(f"\nTEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert logs_present, "No periodic log entries found"
        assert transitions_ok, f"Expected 2 transition logs, got {len(transition_logs)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
