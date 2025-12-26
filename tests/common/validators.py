"""
Validators for test criteria (sync counters, sampling frequency, etc.)
"""
from typing import List, Tuple
import numpy as np


def extract_sync_markers_ads1293(data: List[List[int]]) -> List[Tuple[int, int]]:
    """
    Extract sync markers from ADS1293 data.

    Args:
        data: Raw data array from get_data responses

    Returns:
        List of (index, sync_counter) tuples
    """
    sync_markers = []
    for idx, sample in enumerate(data):
        if len(sample) >= 3 and sample[0] == -99999:
            sync_counter = sample[1]
            sync_markers.append((idx, sync_counter))
    return sync_markers


def extract_sync_markers_max30009(data: List[List[int]]) -> List[Tuple[int, int]]:
    """
    Extract sync markers from MAX30009 data.

    Args:
        data: Raw data array from get_data responses

    Returns:
        List of (index, sync_counter) tuples (sync_counter already divided by 10000)
    """
    sync_markers = []
    for idx, sample in enumerate(data):
        if len(sample) >= 5 and sample[0] == -999990000:
            sync_counter = sample[1] // 10000  # Divide by 10000
            sync_markers.append((idx, sync_counter))
    return sync_markers


def validate_sync_monotonic(sync_markers: List[Tuple[int, int]]) -> bool:
    """
    Validate that sync counters are monotonically increasing.

    Args:
        sync_markers: List of (index, sync_counter) tuples

    Returns:
        True if monotonic, False otherwise
    """
    if len(sync_markers) < 2:
        return True

    for i in range(1, len(sync_markers)):
        if sync_markers[i][1] <= sync_markers[i-1][1]:
            return False
    return True


def calculate_sampling_frequency(data: List[List[int]], duration_sec: float,
                                 sensor: str = "ads1293") -> float:
    """
    Calculate actual sampling frequency from data.

    Args:
        data: Raw data array
        duration_sec: Test duration in seconds
        sensor: Sensor type ("ads1293" or "max30009")

    Returns:
        Calculated sampling frequency in Hz
    """
    # Extract sync markers to get actual samples (exclude sync markers)
    if sensor == "ads1293":
        actual_samples = [s for s in data if s[0] != -99999]
    else:  # max30009
        actual_samples = [s for s in data if s[0] != -999990000]

    total_samples = len(actual_samples)
    return total_samples / duration_sec


def validate_sampling_frequency(actual_freq: float, expected_freq: float,
                                tolerance_hz: float = 1.0) -> bool:
    """
    Validate sampling frequency within tolerance.

    Args:
        actual_freq: Measured frequency
        expected_freq: Expected frequency
        tolerance_hz: Tolerance in Hz

    Returns:
        True if within tolerance, False otherwise
    """
    return abs(actual_freq - expected_freq) <= tolerance_hz


def calculate_mean_absolute_error(measured: np.ndarray, reference: np.ndarray) -> float:
    """
    Calculate mean absolute error.

    Args:
        measured: Measured values
        reference: Reference values

    Returns:
        Mean absolute error
    """
    return np.mean(np.abs(measured - reference))
