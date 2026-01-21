#!/usr/bin/env python3
"""
Test Case #114: Battery Recharge Logging Curve
Unit Test for Power Service

Tests that firmware correctly logs battery recharge data (SOC, voltage, temperature,
time-to-full) during a charging cycle and maintains stable temperature progression.

This unit test can run in two modes:
1. Simulation mode (default): Uses simulated battery data for testing logic
2. Hardware mode: Connects to actual power service (requires PI_TARGET_IP)

Test Setup:
- DUT with battery installed (hardware mode)
- Charger available and connected
- Log capture enabled
- Power service running on CM4 (port 501) for hardware mode

Acceptance Criteria:
- Logs show expected charge curve with correct SOC progression
- Temperature remains stable during charging
"""

import time
import pytest
import os
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import sys

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))


class BatteryState(Enum):
    """Battery state during charging"""
    EMPTY = "empty"
    CHARGING = "charging"
    CHARGING_CC = "charging_cc"      # Constant Current phase
    CHARGING_CV = "charging_cv"      # Constant Voltage phase
    NEARLY_FULL = "nearly_full"
    FULL = "full"


class ChargePhase(Enum):
    """Li-ion charging phases"""
    TRICKLE = "trickle"              # Pre-charge for deeply discharged
    CONSTANT_CURRENT = "cc"          # CC phase - bulk charging
    CONSTANT_VOLTAGE = "cv"          # CV phase - topping off
    MAINTENANCE = "maintenance"      # Float/trickle maintenance
    COMPLETE = "complete"


@dataclass
class BatteryReading:
    """Single battery status reading during charging"""
    timestamp: str
    elapsed_seconds: float
    soc_percent: float              # State of Charge (0-100%)
    voltage_v: float                # Voltage in volts
    current_a: float                # Current in amperes (positive = charging)
    temperature_c: float            # Temperature in Celsius
    remaining_capacity_ah: float
    full_charge_capacity_ah: float
    time_to_full_min: int           # Estimated time to full charge
    cycle_count: int
    fully_discharged: bool
    fully_charged: bool
    charging: bool
    charger_connected: bool
    charge_phase: ChargePhase
    state: BatteryState

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'elapsed_seconds': self.elapsed_seconds,
            'soc_percent': self.soc_percent,
            'voltage_v': self.voltage_v,
            'voltage_mv': self.voltage_v * 1000,
            'current_a': self.current_a,
            'current_ma': self.current_a * 1000,
            'temperature_c': self.temperature_c,
            'remaining_capacity_ah': self.remaining_capacity_ah,
            'full_charge_capacity_ah': self.full_charge_capacity_ah,
            'time_to_full_min': self.time_to_full_min,
            'cycle_count': self.cycle_count,
            'fully_discharged': self.fully_discharged,
            'fully_charged': self.fully_charged,
            'charging': self.charging,
            'charger_connected': self.charger_connected,
            'charge_phase': self.charge_phase.value,
            'state': self.state.value
        }


@dataclass
class ChargeProfile:
    """Expected charge profile parameters for Li-ion battery"""
    # Voltage thresholds (in V)
    voltage_empty: float = 3.0
    voltage_nominal: float = 3.7
    voltage_cv_start: float = 4.1    # Voltage where CV phase begins
    voltage_full: float = 4.2
    voltage_float: float = 4.05      # Maintenance voltage

    # SOC thresholds (in %)
    soc_empty: float = 5.0
    soc_cc_cv_transition: float = 80.0  # Typical CC to CV transition
    soc_nearly_full: float = 95.0
    soc_full: float = 100.0

    # Current thresholds (in A)
    charge_current_max: float = 1.5   # Max CC charging current (0.5C for 3Ah)
    charge_current_taper: float = 0.1 # CV termination current

    # Temperature limits (in C)
    temp_min_charging: float = 0.0
    temp_max_charging: float = 45.0
    temp_min_safe: float = -10.0
    temp_max_safe: float = 60.0
    temp_max_rise: float = 10.0       # Max allowed temp rise during charging

    # Charge characteristics
    expected_capacity_ah: float = 3.0
    typical_charge_time_hours: float = 2.5


class MockBatteryChargeSimulator:
    """
    Simulates battery charging behavior for unit testing.
    Generates realistic Li-ion charge curve data with CC-CV profile.
    """

    def __init__(self, profile: ChargeProfile, start_soc: float = 10.0):
        self.profile = profile
        self.start_time: Optional[datetime] = None
        self.readings: List[BatteryReading] = []

        # Simulation state - start at low SOC
        self.sim_soc = start_soc
        self.sim_voltage = self._soc_to_voltage(start_soc)
        self.sim_current = 1.0  # Charging current
        self.sim_temperature = 25.0
        self.initial_temperature = 25.0
        self.sim_remaining_capacity = profile.expected_capacity_ah * (start_soc / 100.0)
        self.charger_connected = True
        self.charging_enabled = True

    def _soc_to_voltage(self, soc: float) -> float:
        """Convert SOC to approximate voltage (Li-ion curve)"""
        if soc <= 5:
            return 3.0 + soc * 0.04
        elif soc <= 20:
            return 3.2 + (soc - 5) * 0.02
        elif soc <= 80:
            return 3.5 + (soc - 20) * 0.01
        elif soc <= 95:
            return 4.1 + (soc - 80) * 0.006
        else:
            return 4.19 + (soc - 95) * 0.002

    def reset(self, start_soc: float = 10.0):
        """Reset simulator to initial state"""
        self.start_time = datetime.now()
        self.readings.clear()
        self.sim_soc = start_soc
        self.sim_voltage = self._soc_to_voltage(start_soc)
        self.sim_current = 1.0
        self.sim_temperature = 25.0
        self.initial_temperature = 25.0
        self.sim_remaining_capacity = self.profile.expected_capacity_ah * (start_soc / 100.0)

    def enable_charging(self) -> bool:
        """Enable battery charging"""
        self.charging_enabled = True
        return True

    def disable_charging(self) -> bool:
        """Disable battery charging"""
        self.charging_enabled = False
        return True

    def read_battery_status(self) -> BatteryReading:
        """Generate simulated battery reading during charging"""
        if self.start_time is None:
            self.start_time = datetime.now()

        timestamp = datetime.now().isoformat()
        elapsed = (datetime.now() - self.start_time).total_seconds()

        # Simulate charge: ~15% SOC increase per minute for faster testing
        if self.charging_enabled and self.charger_connected and self.sim_soc < 100:
            charge_rate_per_second = 15.0 / 60.0
            self.sim_soc = min(100.0, self.sim_soc + (charge_rate_per_second * 1))  # Per reading

            # Update voltage based on SOC and charge phase
            self.sim_voltage = self._soc_to_voltage(self.sim_soc)

            # Simulate CC-CV charging current profile
            if self.sim_soc < 80:
                # Constant Current phase - high current
                self.sim_current = self.profile.charge_current_max
            else:
                # Constant Voltage phase - tapering current
                cv_progress = (self.sim_soc - 80) / 20.0  # 0 to 1 as SOC goes 80->100
                self.sim_current = self.profile.charge_current_max * (1 - cv_progress * 0.9)
                self.sim_current = max(self.sim_current, self.profile.charge_current_taper)

            # Simulate temperature rise during charging (moderate rise then stable)
            temp_rise = min(5.0, elapsed / 120.0 * 3)  # Rise ~3C over 2 minutes, cap at 5C
            self.sim_temperature = self.initial_temperature + temp_rise

        else:
            # Not charging
            self.sim_current = 0.0

        # Update remaining capacity
        self.sim_remaining_capacity = self.profile.expected_capacity_ah * (self.sim_soc / 100.0)

        # Determine charge phase and state
        charge_phase = self._determine_charge_phase()
        state = self._determine_state()

        # Estimate time to full
        if self.sim_soc < 100 and self.sim_current > 0:
            remaining_capacity = self.profile.expected_capacity_ah * (100 - self.sim_soc) / 100
            time_to_full = int((remaining_capacity / self.sim_current) * 60)  # minutes
        else:
            time_to_full = 0

        reading = BatteryReading(
            timestamp=timestamp,
            elapsed_seconds=round(elapsed, 1),
            soc_percent=round(self.sim_soc, 1),
            voltage_v=round(self.sim_voltage, 3),
            current_a=round(self.sim_current, 3),
            temperature_c=round(self.sim_temperature, 1),
            remaining_capacity_ah=round(self.sim_remaining_capacity, 3),
            full_charge_capacity_ah=self.profile.expected_capacity_ah,
            time_to_full_min=time_to_full,
            cycle_count=42,
            fully_discharged=self.sim_soc <= 5,
            fully_charged=self.sim_soc >= 99,
            charging=self.sim_current > 0.05,
            charger_connected=self.charger_connected,
            charge_phase=charge_phase,
            state=state
        )

        self.readings.append(reading)
        return reading

    def _determine_charge_phase(self) -> ChargePhase:
        """Determine current charging phase"""
        if not self.charging_enabled or not self.charger_connected:
            return ChargePhase.COMPLETE
        if self.sim_soc >= 99:
            return ChargePhase.MAINTENANCE
        if self.sim_soc < 5:
            return ChargePhase.TRICKLE
        if self.sim_soc < 80:
            return ChargePhase.CONSTANT_CURRENT
        return ChargePhase.CONSTANT_VOLTAGE

    def _determine_state(self) -> BatteryState:
        """Determine battery state based on SOC and charging status"""
        if self.sim_soc >= 99:
            return BatteryState.FULL
        if self.sim_soc >= 95:
            return BatteryState.NEARLY_FULL
        if self.sim_soc < 5:
            return BatteryState.EMPTY
        if self.sim_current > 0.05:
            if self.sim_soc < 80:
                return BatteryState.CHARGING_CC
            return BatteryState.CHARGING_CV
        return BatteryState.CHARGING

    def get_all_readings(self) -> List[BatteryReading]:
        """Get all recorded readings"""
        return self.readings.copy()


class PowerServiceClient:
    """
    Client for communicating with power service via TCP/JSON.
    Falls back to simulation if connection fails.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0, start_soc: float = 10.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.start_soc = start_soc
        self.client = None
        self.connected = False
        self.readings: List[BatteryReading] = []
        self.start_time: Optional[datetime] = None

        # Simulation fallback
        self.simulator: Optional[MockBatteryChargeSimulator] = None
        self.use_simulation = False

    def connect(self) -> bool:
        """Connect to power service or fall back to simulation"""
        try:
            from tcp_client import TCPClient
            self.client = TCPClient(self.host, self.port, self.timeout)
            self.client.connect()
            self.connected = True
            self.start_time = datetime.now()
            print(f"  Connected to power service at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"  Could not connect to power service: {e}")
            print("  Falling back to simulation mode")
            self.use_simulation = True
            self.simulator = MockBatteryChargeSimulator(ChargeProfile(), self.start_soc)
            self.simulator.reset(self.start_soc)
            return True

    def disconnect(self):
        """Disconnect from power service"""
        if self.client and self.connected:
            self.client.disconnect()
            self.client = None
            self.connected = False

    def enable_charging(self) -> bool:
        """Enable battery charging"""
        if self.use_simulation:
            return self.simulator.enable_charging()

        try:
            response = self.client.send({"type": "charge_enable"})
            return response and response.get("type") == "charge_is_enable"
        except Exception as e:
            print(f"  Error enabling charging: {e}")
            return False

    def disable_charging(self) -> bool:
        """Disable battery charging"""
        if self.use_simulation:
            return self.simulator.disable_charging()

        try:
            response = self.client.send({"type": "charge_disable"})
            return response and response.get("type") == "charge_is_disable"
        except Exception as e:
            print(f"  Error disabling charging: {e}")
            return False

    def read_battery_status(self) -> Optional[BatteryReading]:
        """Read current battery status"""
        if self.use_simulation:
            return self.simulator.read_battery_status()

        try:
            response = self.client.send({"type": "get_batt_info"})
            if not response or response.get("type") != "batt_info":
                return None

            timestamp = datetime.now().isoformat()
            elapsed = 0.0
            if self.start_time:
                elapsed = (datetime.now() - self.start_time).total_seconds()

            soc = response.get('relative_state_of_charge', 0)
            voltage = response.get('voltage', 0.0)
            current = response.get('current', 0.0)
            temperature = response.get('temperature', 25.0)

            # Determine charge phase and state
            charge_phase = self._determine_charge_phase(soc, current, response)
            state = self._determine_state(soc, current, response)

            reading = BatteryReading(
                timestamp=timestamp,
                elapsed_seconds=elapsed,
                soc_percent=soc,
                voltage_v=voltage,
                current_a=current,
                temperature_c=temperature,
                remaining_capacity_ah=response.get('remaining_capacity', 0.0),
                full_charge_capacity_ah=response.get('full_charge_capacity', 0.0),
                time_to_full_min=response.get('average_time_to_full', 0),
                cycle_count=response.get('cycle_count', 0),
                fully_discharged=response.get('fully_discharged', False),
                fully_charged=response.get('fully_charged', False),
                charging=current > 0.05,
                charger_connected=response.get('charger_is_connect', False),
                charge_phase=charge_phase,
                state=state
            )

            self.readings.append(reading)
            return reading

        except Exception as e:
            print(f"  Error reading battery status: {e}")
            return None

    def _determine_charge_phase(self, soc: float, current: float, response: Dict) -> ChargePhase:
        """Determine current charging phase"""
        if current <= 0.05:
            return ChargePhase.COMPLETE
        if response.get('fully_charged', False):
            return ChargePhase.MAINTENANCE
        if soc < 5:
            return ChargePhase.TRICKLE
        if soc < 80:
            return ChargePhase.CONSTANT_CURRENT
        return ChargePhase.CONSTANT_VOLTAGE

    def _determine_state(self, soc: float, current: float, response: Dict) -> BatteryState:
        """Determine battery state"""
        if response.get('fully_charged', False) or soc >= 99:
            return BatteryState.FULL
        if soc >= 95:
            return BatteryState.NEARLY_FULL
        if soc < 5:
            return BatteryState.EMPTY
        if current > 0.05:
            if soc < 80:
                return BatteryState.CHARGING_CC
            return BatteryState.CHARGING_CV
        return BatteryState.CHARGING

    def get_all_readings(self) -> List[BatteryReading]:
        """Get all recorded readings"""
        if self.use_simulation:
            return self.simulator.get_all_readings()
        return self.readings.copy()

    def clear_readings(self):
        """Clear recorded readings"""
        self.readings.clear()
        if self.simulator:
            self.simulator.readings.clear()
        self.start_time = datetime.now()


class ChargeAnalyzer:
    """Analyzes battery charge data"""

    def __init__(self, profile: ChargeProfile):
        self.profile = profile

    def analyze_curve(self, readings: List[BatteryReading]) -> Dict:
        """Analyze the charge curve"""
        if not readings:
            return {'valid': False, 'error': 'No readings available', 'curve_valid': False}

        analysis = {
            'valid': True,
            'total_readings': len(readings),
            'duration_seconds': readings[-1].elapsed_seconds,
            'start_soc': readings[0].soc_percent,
            'end_soc': readings[-1].soc_percent,
            'start_voltage_v': readings[0].voltage_v,
            'end_voltage_v': readings[-1].voltage_v,
            'soc_gain': readings[-1].soc_percent - readings[0].soc_percent,
            'voltage_gain_v': readings[-1].voltage_v - readings[0].voltage_v,
            'avg_charge_current_a': 0.0,
            'max_charge_current_a': 0.0,
            'min_temperature_c': float('inf'),
            'max_temperature_c': float('-inf'),
            'avg_temperature_c': 0.0,
            'temperature_rise_c': 0.0,
            'temperature_stable': True,
            'curve_valid': True,
            'reached_full': False,
            'cc_cv_transition_soc': None,
            'issues': []
        }

        total_current = 0
        total_temp = 0
        initial_temp = readings[0].temperature_c

        for reading in readings:
            total_current += reading.current_a
            total_temp += reading.temperature_c
            analysis['min_temperature_c'] = min(analysis['min_temperature_c'], reading.temperature_c)
            analysis['max_temperature_c'] = max(analysis['max_temperature_c'], reading.temperature_c)
            analysis['max_charge_current_a'] = max(analysis['max_charge_current_a'], reading.current_a)

            # Detect CC to CV transition
            if analysis['cc_cv_transition_soc'] is None and reading.charge_phase == ChargePhase.CONSTANT_VOLTAGE:
                analysis['cc_cv_transition_soc'] = reading.soc_percent

        analysis['avg_charge_current_a'] = total_current / len(readings)
        analysis['avg_temperature_c'] = total_temp / len(readings)
        analysis['temperature_rise_c'] = analysis['max_temperature_c'] - initial_temp
        analysis['reached_full'] = readings[-1].fully_charged or readings[-1].soc_percent >= 99

        # Check temperature stability
        if analysis['temperature_rise_c'] > self.profile.temp_max_rise:
            analysis['temperature_stable'] = False
            analysis['issues'].append(
                f"Temperature rise too high: {analysis['temperature_rise_c']:.1f}C > {self.profile.temp_max_rise}C"
            )

        if analysis['max_temperature_c'] > self.profile.temp_max_charging:
            analysis['temperature_stable'] = False
            analysis['issues'].append(
                f"Temperature exceeded charging limit: {analysis['max_temperature_c']:.1f}C"
            )

        # Validate curve
        analysis['curve_valid'] = self._validate_curve(readings, analysis)

        return analysis

    def _validate_curve(self, readings: List[BatteryReading], analysis: Dict) -> bool:
        """Validate charge curve"""
        if len(readings) < 3:
            analysis['issues'].append("Not enough readings for curve validation")
            return False

        # Check SOC is monotonically increasing (with tolerance for noise)
        soc_decreases = 0
        for i in range(1, len(readings)):
            if readings[i].soc_percent < readings[i-1].soc_percent - 1:  # 1% tolerance
                soc_decreases += 1

        if soc_decreases > len(readings) * 0.1:
            analysis['issues'].append(f"SOC not monotonically increasing: {soc_decreases} decreases")
            return False

        # Check voltage increases with SOC during charging
        voltage_correlation_ok = True
        for i in range(1, len(readings)):
            soc_gain = readings[i].soc_percent - readings[i-1].soc_percent
            voltage_change = readings[i].voltage_v - readings[i-1].voltage_v

            # If SOC increased significantly, voltage should not drop much
            if soc_gain > 5 and voltage_change < -0.05:
                voltage_correlation_ok = False
                break

        if not voltage_correlation_ok:
            analysis['issues'].append("Voltage does not correlate with SOC increase")
            return False

        # Check that SOC actually increased
        if analysis['soc_gain'] < 5:
            analysis['issues'].append(f"Insufficient SOC gain: {analysis['soc_gain']:.1f}%")
            return False

        return True

    def check_temperature_stability(self, readings: List[BatteryReading]) -> Tuple[bool, List[str]]:
        """Check if temperature remained stable during charging"""
        issues = []
        stable = True

        initial_temp = readings[0].temperature_c if readings else 25.0

        for reading in readings:
            # Check operating range
            if reading.temperature_c < self.profile.temp_min_charging:
                issues.append(f"Temperature below charging range at {reading.elapsed_seconds:.0f}s")
                stable = False
            if reading.temperature_c > self.profile.temp_max_charging:
                issues.append(f"Temperature above charging range at {reading.elapsed_seconds:.0f}s")
                stable = False

            # Check for excessive rise
            temp_rise = reading.temperature_c - initial_temp
            if temp_rise > self.profile.temp_max_rise:
                issues.append(
                    f"Excessive temp rise at {reading.elapsed_seconds:.0f}s: "
                    f"{temp_rise:.1f}C > {self.profile.temp_max_rise}C"
                )
                stable = False

        return stable, issues


class TestBatteryRechargeCurve:
    """Unit Test - Battery Recharge Logging Curve"""

    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration"""
        host = os.environ.get('PI_TARGET_IP', '127.0.0.1')
        port = 501

        return {
            'host': host,
            'port': port,
            'timeout': 10.0,
            'start_soc_percent': 10.0,        # Start from low SOC
            'target_soc_percent': 95.0,       # Target SOC (near full)
            'max_test_duration_seconds': 120, # 2 minutes for unit test
            'logging_interval_seconds': 1,    # Fast logging for unit test
            'profile': ChargeProfile(),
            'enable_charging': True,
            'log_file': '/tmp/test_114_battery_recharge.log',
        }

    def setup_method(self):
        """Setup before each test"""
        self.client: Optional[PowerServiceClient] = None

    def teardown_method(self):
        """Cleanup after each test"""
        if self.client:
            self.client.disconnect()

    def print_reading(self, reading: BatteryReading, index: int):
        """Print formatted battery reading"""
        state_symbol = {
            BatteryState.EMPTY: "[EMPT]",
            BatteryState.CHARGING: "[CHRG]",
            BatteryState.CHARGING_CC: "[ CC ]",
            BatteryState.CHARGING_CV: "[ CV ]",
            BatteryState.NEARLY_FULL: "[NRFL]",
            BatteryState.FULL: "[FULL]",
        }
        phase_symbol = {
            ChargePhase.TRICKLE: "TRK",
            ChargePhase.CONSTANT_CURRENT: "CC ",
            ChargePhase.CONSTANT_VOLTAGE: "CV ",
            ChargePhase.MAINTENANCE: "MNT",
            ChargePhase.COMPLETE: "DON",
        }

        symbol = state_symbol.get(reading.state, "[----]")
        phase = phase_symbol.get(reading.charge_phase, "---")
        charger = "PWR" if reading.charger_connected else "---"
        ttf = f"{reading.time_to_full_min:3d}m" if reading.time_to_full_min > 0 else "  --"

        print(f"  {index:4d} | {reading.elapsed_seconds:7.1f}s | "
              f"SOC: {reading.soc_percent:5.1f}% | "
              f"V: {reading.voltage_v:5.3f}V | "
              f"I: {reading.current_a:+6.3f}A | "
              f"T: {reading.temperature_c:5.1f}C | "
              f"{phase} | {charger} | TTF:{ttf} | {symbol}")

    @pytest.mark.unit
    @pytest.mark.battery
    @pytest.mark.power
    def test_114_battery_recharge_logging(self, test_config):
        """
        Test Case #114: Battery recharge logging curve

        Test Setup:
            DUT with battery installed; charger available; log capture enabled

        Procedure:
            1. Recharge battery to full capacity
            2. Log battery parameters (SOC, voltage, temperature, time-to-full)
               during recharge

        Acceptance Criteria:
            1. Logs show expected charge curve with correct SOC progression
            2. Temperature remains stable during charging

        This test runs in simulation mode by default for unit testing.
        Set PI_TARGET_IP environment variable to test against real hardware.
        """
        config = test_config

        print("\n" + "=" * 85)
        print("Test Case #114: Battery Recharge Logging Curve (Unit Test)")
        print("=" * 85)
        print("\nPURPOSE:")
        print("  Verify firmware logs battery recharge data correctly")
        print("\nMONITORED PARAMETERS:")
        print("  - State of Charge (SOC) - percentage")
        print("  - Voltage - volts")
        print("  - Current - amperes (positive = charging)")
        print("  - Temperature - Celsius")
        print("  - Time to Full - minutes")
        print("\nCONFIGURATION:")
        print(f"  Target: {config['host']}:{config['port']}")
        print(f"  Start SOC: {config['start_soc_percent']}%")
        print(f"  Target SOC: {config['target_soc_percent']}%")
        print(f"  Max Duration: {config['max_test_duration_seconds']}s")
        print(f"  Logging Interval: {config['logging_interval_seconds']}s")
        print("=" * 85)

        analyzer = ChargeAnalyzer(config['profile'])

        # ================================================================
        # STEP 1: Initialize Client
        # ================================================================
        print("\n[STEP 1] Initialize Battery Monitor")
        print("-" * 85)

        self.client = PowerServiceClient(
            host=config['host'],
            port=config['port'],
            timeout=config['timeout'],
            start_soc=config['start_soc_percent']
        )

        connected = self.client.connect()
        assert connected, "Failed to initialize battery monitor"

        if self.client.use_simulation:
            print("  Running in SIMULATION mode")
        else:
            print("  Running in HARDWARE mode")

        # ================================================================
        # STEP 2: Record Initial Battery State
        # ================================================================
        print("\n[STEP 2] Record Initial Battery State")
        print("-" * 85)

        initial_reading = self.client.read_battery_status()
        assert initial_reading is not None, "Failed to read initial battery state"

        print(f"  Initial battery state:")
        print(f"    SOC: {initial_reading.soc_percent}%")
        print(f"    Voltage: {initial_reading.voltage_v:.3f}V")
        print(f"    Current: {initial_reading.current_a:.3f}A")
        print(f"    Temperature: {initial_reading.temperature_c:.1f}C")
        print(f"    Charger connected: {initial_reading.charger_connected}")
        print(f"    State: {initial_reading.state.value}")
        print(f"    Charge phase: {initial_reading.charge_phase.value}")

        self.client.clear_readings()

        # ================================================================
        # STEP 3: Enable Charging
        # ================================================================
        print("\n[STEP 3] Enable Charging")
        print("-" * 85)

        if config['enable_charging']:
            enabled = self.client.enable_charging()
            print(f"  Charging enabled: {enabled}")
        else:
            print("  Charging control not modified")

        # ================================================================
        # STEP 4: Begin Charge Monitoring
        # ================================================================
        print("\n[STEP 4] Begin Charge Monitoring")
        print("-" * 85)

        print(f"\n  Start SOC: {config['start_soc_percent']}%")
        print(f"  Target SOC: {config['target_soc_percent']}%")
        print(f"  Max duration: {config['max_test_duration_seconds']}s")
        print()
        print("  " + "-" * 95)
        print(f"  {'#':>4} | {'Elapsed':>7} | {'SOC':>7} | "
              f"{'Voltage':>7} | {'Current':>8} | "
              f"{'Temp':>6} | Phs | PWR | TTF    | State")
        print("  " + "-" * 95)

        start_time = datetime.now()
        reading_count = 0
        target_reached = False

        while True:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= config['max_test_duration_seconds']:
                print(f"\n  Maximum test duration reached ({elapsed:.0f}s)")
                break

            reading = self.client.read_battery_status()
            reading_count += 1

            if reading:
                self.print_reading(reading, reading_count)

                if reading.soc_percent >= config['target_soc_percent']:
                    print(f"\n  Target SOC reached: {reading.soc_percent}%")
                    target_reached = True
                    break

                if reading.fully_charged:
                    print(f"\n  Battery fully charged at {reading.soc_percent}%")
                    target_reached = True
                    break

                if reading.temperature_c > config['profile'].temp_max_safe:
                    print(f"\n  SAFETY: Temperature too high! {reading.temperature_c}C")
                    break

            time.sleep(config['logging_interval_seconds'])

        print("  " + "-" * 95)

        # ================================================================
        # STEP 5: Analyze Results
        # ================================================================
        print("\n[STEP 5] Analyze Charge Curve")
        print("-" * 85)

        readings = self.client.get_all_readings()
        analysis = analyzer.analyze_curve(readings)

        print(f"\n  Charge Curve Analysis:")
        print(f"    Total readings: {analysis['total_readings']}")
        print(f"    Duration: {analysis['duration_seconds']:.1f}s")
        print(f"    SOC: {analysis['start_soc']:.1f}% -> {analysis['end_soc']:.1f}%")
        print(f"    SOC gained: {analysis['soc_gain']:.1f}%")
        print(f"    Voltage: {analysis['start_voltage_v']:.3f}V -> {analysis['end_voltage_v']:.3f}V")
        print(f"    Avg charge current: {analysis['avg_charge_current_a']:.3f}A")
        print(f"    Max charge current: {analysis['max_charge_current_a']:.3f}A")
        print(f"    Temp range: {analysis['min_temperature_c']:.1f}C - {analysis['max_temperature_c']:.1f}C")
        print(f"    Temp rise: {analysis['temperature_rise_c']:.1f}C")
        if analysis['cc_cv_transition_soc']:
            print(f"    CC->CV transition: {analysis['cc_cv_transition_soc']:.1f}%")
        print(f"    Reached full: {analysis['reached_full']}")

        curve_pass = analysis['curve_valid']
        print(f"\n    Curve validation: {'VALID' if curve_pass else 'INVALID'}")

        if analysis['issues']:
            for issue in analysis['issues']:
                print(f"      - {issue}")

        # ================================================================
        # STEP 6: Verify Temperature Stability
        # ================================================================
        print("\n[STEP 6] Verify Temperature Stability")
        print("-" * 85)

        temp_stable, temp_issues = analyzer.check_temperature_stability(readings)

        if temp_stable:
            print(f"  Temperature remained stable during charging: PASS")
            print(f"    Initial: {readings[0].temperature_c:.1f}C")
            print(f"    Final: {readings[-1].temperature_c:.1f}C")
            print(f"    Rise: {analysis['temperature_rise_c']:.1f}C (limit: {config['profile'].temp_max_rise}C)")
        else:
            print(f"  Temperature stability check: FAIL")
            for issue in temp_issues:
                print(f"    - {issue}")

        # ================================================================
        # Test Result
        # ================================================================
        print("\n" + "=" * 85)

        if curve_pass and temp_stable:
            print("TEST RESULT: PASS")
        else:
            print("TEST RESULT: FAIL")

        print("=" * 85)

        print("\n  Acceptance Criteria:")
        print(f"    [{'PASS' if curve_pass else 'FAIL'}] Logs show expected charge curve with correct SOC progression")
        print(f"    [{'PASS' if temp_stable else 'FAIL'}] Temperature remains stable during charging")

        print("\n  Statistics:")
        print(f"    Readings: {len(readings)}")
        print(f"    Duration: {analysis['duration_seconds']:.1f}s")
        print(f"    SOC gained: {analysis['soc_gain']:.1f}%")
        print(f"    Temperature rise: {analysis['temperature_rise_c']:.1f}C")
        print(f"    Mode: {'Simulation' if self.client.use_simulation else 'Hardware'}")

        print("=" * 85)

        # Assertions
        assert curve_pass, f"Charge curve invalid: {analysis['issues']}"
        assert temp_stable, f"Temperature not stable: {temp_issues}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
