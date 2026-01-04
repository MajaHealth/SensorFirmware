"""
Helper functions for common sensor operations
"""
from typing import Dict, Any
from tcp_client import TCPClient


def configure_ads1293(client: TCPClient, sampling_freq: int = 400,
                     r2_rate: int = 4, r3_rate: int = 128,
                     enable_conversion: bool = True) -> Dict[str, Any]:
    """
    Configure ADS1293 sensor.

    Args:
        client: TCP client connected to ADS1293 service
        sampling_freq: Desired sampling frequency (Hz)
        r2_rate: R2 decimation rate (4, 5, 6, or 8)
        r3_rate: R3 decimation rate (4, 6, 8, 12, 16, 32, 64, or 128)
        enable_conversion: Enable ADC conversion

    Returns:
        Response with actual settings
    """
    request = {
        "type": "settings",
        "enable_conversion": enable_conversion,
        "power_enable": True,
        "R2_rate": r2_rate,
        "R3_rate": r3_rate
    }
    return client.send(request)


def configure_max30009(client: TCPClient, sampling_freq: int = 400,
                      stim_current: int = 4, stim_freq: int = 7,
                      mux_state: int = 1) -> Dict[str, Any]:
    """
    Configure MAX30009 sensor.

    Args:
        client: TCP client connected to MAX30009 service
        sampling_freq: Sampling frequency (Hz)
        stim_current: Stimulation current index (0-4)
        stim_freq: Stimulation frequency index (0-16)
        mux_state: External MUX state (0-4)

    Returns:
        Response with actual settings
    """
    request = {
        "type": "settings",
        "measure_enable": True,
        "power_enable": True,
        "stimulate_frequency": stim_freq,
        "measure_frequency": sampling_freq,
        "stimulate_current": stim_current,
        "ext_MUX_state": mux_state,
        "out_LP_filter": 0,
        "out_HP_filter": 0
    }
    return client.send(request)


def get_sensor_data(client: TCPClient) -> Dict[str, Any]:
    """
    Request sensor data.

    Args:
        client: TCP client connected to sensor service

    Returns:
        Response with sensor data
    """
    request = {"type": "get_data"}
    return client.send(request)


def power_off_sensor(client: TCPClient) -> Dict[str, Any]:
    """
    Power off sensor.

    Args:
        client: TCP client connected to sensor service

    Returns:
        Power off confirmation
    """
    request = {"type": "poweroff"}
    return client.send(request)
