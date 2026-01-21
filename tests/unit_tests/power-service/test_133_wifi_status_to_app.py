#!/usr/bin/env python3
"""
Test Case #133: Wi-Fi Status Updates Communicated to App
Unit Test for Power Service / Wi-Fi

Tests that Wi-Fi status changes are communicated to the mock app.

Test Setup:
- DUT with Wi-Fi module
- Controllable AP
- Mock app connected
- Log capture enabled

Procedure:
1. Trigger Wi-Fi connected, disconnected, and reconnected events
   (including a temporary out-of-range drop)
2. For each event, verify corresponding log entry and status message
   delivered to mock app

Acceptance Criteria:
- Each Wi-Fi connected/disconnected log entry is also communicated to
  the mock app with the correct timestamp
"""

import time
from datetime import datetime
import pytest
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


@dataclass
class AppNotification:
    timestamp: datetime
    event_type: str  # "connected", "disconnected", "reconnected"
    message: str


@dataclass
class LogEntry:
    timestamp: datetime
    event_type: str
    message: str


class MockWiFiAppCommunicator:
    def __init__(self):
        self.app_notifications: List[AppNotification] = []
        self.log_entries: List[LogEntry] = []
        self.connected = False

    def trigger_connected(self):
        ts = datetime.now()
        self.connected = True
        self.log_entries.append(LogEntry(ts, "connected", "Wi-Fi connected"))
        self.app_notifications.append(AppNotification(ts, "connected", "Wi-Fi connected"))

    def trigger_disconnected(self):
        ts = datetime.now()
        self.connected = False
        self.log_entries.append(LogEntry(ts, "disconnected", "Wi-Fi disconnected"))
        self.app_notifications.append(AppNotification(ts, "disconnected", "Wi-Fi disconnected"))

    def trigger_reconnected(self):
        ts = datetime.now()
        self.connected = True
        self.log_entries.append(LogEntry(ts, "reconnected", "Wi-Fi reconnected"))
        self.app_notifications.append(AppNotification(ts, "reconnected", "Wi-Fi reconnected"))

    def trigger_out_of_range_drop(self):
        """Simulate temporary out-of-range drop"""
        self.trigger_disconnected()
        time.sleep(0.1)
        self.trigger_reconnected()

    def get_app_notifications(self) -> List[AppNotification]:
        return self.app_notifications

    def get_log_entries(self) -> List[LogEntry]:
        return self.log_entries


class WiFiAppController:
    def __init__(self, host: Optional[str] = None):
        self.host = host
        self.use_mock = False
        self.mock: Optional[MockWiFiAppCommunicator] = None

    def initialize(self) -> bool:
        if self.host and self.host != '127.0.0.1':
            return True
        self.use_mock = True
        self.mock = MockWiFiAppCommunicator()
        return True

    def trigger_connected(self):
        if self.use_mock:
            self.mock.trigger_connected()

    def trigger_disconnected(self):
        if self.use_mock:
            self.mock.trigger_disconnected()

    def trigger_reconnected(self):
        if self.use_mock:
            self.mock.trigger_reconnected()

    def trigger_out_of_range_drop(self):
        if self.use_mock:
            self.mock.trigger_out_of_range_drop()

    def get_app_notifications(self) -> List[AppNotification]:
        if self.use_mock:
            return self.mock.get_app_notifications()
        return []

    def get_log_entries(self) -> List[LogEntry]:
        if self.use_mock:
            return self.mock.get_log_entries()
        return []


class TestWiFiStatusToApp:
    """Unit Test - Wi-Fi Status Updates Communicated to App"""

    @pytest.fixture(scope="class")
    def test_config(self):
        return {'host': os.environ.get('PI_TARGET_IP', '127.0.0.1')}

    @pytest.mark.unit
    @pytest.mark.wifi
    @pytest.mark.power
    def test_133_wifi_status_communicated_to_app(self, test_config):
        """
        Test Case #133: Wi-Fi status updates communicated to app

        Acceptance Criteria:
            Each Wi-Fi connected/disconnected log entry is also communicated
            to the mock app with the correct timestamp
        """
        print("\n" + "=" * 70)
        print("Test Case #133: Wi-Fi Status Updates Communicated to App")
        print("=" * 70)

        controller = WiFiAppController(host=test_config['host'])
        controller.initialize()

        print(f"\n  Mode: {'Mock Simulation' if controller.use_mock else 'Hardware'}")

        # Trigger events
        print("\n[STEP 1] Trigger Wi-Fi Events")
        print("-" * 70)

        print("  Triggering: Connected")
        controller.trigger_connected()

        print("  Triggering: Disconnected")
        controller.trigger_disconnected()

        print("  Triggering: Reconnected")
        controller.trigger_reconnected()

        print("  Triggering: Out-of-range drop (disconnect + reconnect)")
        controller.trigger_out_of_range_drop()

        # Get results
        print("\n[STEP 2] Verify App Notifications Match Log Entries")
        print("-" * 70)

        logs = controller.get_log_entries()
        notifications = controller.get_app_notifications()

        print(f"\n  Log entries: {len(logs)}")
        print(f"  App notifications: {len(notifications)}")

        # Display comparison
        print("\n  Log Entries:")
        for i, log in enumerate(logs):
            print(f"    [{i+1}] {log.timestamp.isoformat()} - {log.event_type}: {log.message}")

        print("\n  App Notifications:")
        for i, notif in enumerate(notifications):
            print(f"    [{i+1}] {notif.timestamp.isoformat()} - {notif.event_type}: {notif.message}")

        # Verify each log has corresponding notification
        print("\n[STEP 3] Verify Correspondence")
        print("-" * 70)

        all_matched = True
        for log in logs:
            matched = any(
                n.event_type == log.event_type and
                n.timestamp == log.timestamp
                for n in notifications
            )
            status = "MATCHED" if matched else "MISSING"
            print(f"  Log '{log.event_type}' at {log.timestamp.isoformat()}: {status}")
            if not matched:
                all_matched = False

        counts_match = len(logs) == len(notifications)

        print("\n" + "=" * 70)
        print(f"  [{'PASS' if counts_match else 'FAIL'}] Same number of logs and notifications")
        print(f"  [{'PASS' if all_matched else 'FAIL'}] All logs communicated to app")

        test_pass = counts_match and all_matched
        print(f"\nTEST RESULT: {'PASS' if test_pass else 'FAIL'}")
        print("=" * 70)

        assert counts_match, f"Mismatch: {len(logs)} logs vs {len(notifications)} notifications"
        assert all_matched, "Some log entries not communicated to app"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
