#!/usr/bin/env python3
"""
Platform Check Utilities

Provides functions to detect the current platform and skip tests
that require specific hardware (e.g., Raspberry Pi CM4).
"""

import platform
import pytest


def is_raspberry_pi():
    """
    Check if running on a Raspberry Pi.

    Returns:
        bool: True if running on Raspberry Pi, False otherwise
    """
    # Check /proc/cpuinfo for Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read().lower()
            if 'raspberry pi' in cpuinfo or 'bcm2' in cpuinfo:
                return True
    except:
        pass

    # Check /proc/device-tree/model
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().lower()
            if 'raspberry pi' in model:
                return True
    except:
        pass

    # Check for typical Pi kernel
    try:
        uname = platform.uname()
        if 'raspberry' in uname.release.lower() or 'rpi' in uname.release.lower():
            return True
    except:
        pass

    return False


def is_cm4():
    """
    Check if running on a Raspberry Pi Compute Module 4.

    Returns:
        bool: True if running on CM4, False otherwise
    """
    if not is_raspberry_pi():
        return False

    # Check /proc/device-tree/model for CM4
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().lower()
            if 'compute module 4' in model or 'cm4' in model:
                return True
    except:
        pass

    return is_raspberry_pi()  # Fallback: assume any Pi could be CM4


def get_platform_info():
    """
    Get current platform information.

    Returns:
        dict: Platform information
    """
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'is_raspberry_pi': is_raspberry_pi(),
        'is_cm4': is_cm4(),
    }

    # Try to get Pi model
    try:
        with open('/proc/device-tree/model', 'r') as f:
            info['model'] = f.read().strip().rstrip('\x00')
    except:
        info['model'] = 'Unknown'

    return info


def skip_if_not_raspberry_pi(test_name="This test"):
    """
    Skip test if not running on Raspberry Pi.

    Usage:
        from tests.common.platform_check import skip_if_not_raspberry_pi

        def test_something():
            skip_if_not_raspberry_pi("eMMC detection test")
            # ... rest of test

    Args:
        test_name: Name of the test for the skip message
    """
    if not is_raspberry_pi():
        pytest.skip(
            f"{test_name} must run on Raspberry Pi.\n"
            f"Current platform: {platform.uname().release}\n"
            f"Run this test on the CM4 using:\n"
            f"  ./scripts/run-unit-test-remote.sh <PI_IP> <test_file>"
        )


def skip_if_not_cm4(test_name="This test"):
    """
    Skip test if not running on Raspberry Pi CM4.

    Args:
        test_name: Name of the test for the skip message
    """
    if not is_cm4():
        pytest.skip(
            f"{test_name} must run on Raspberry Pi CM4.\n"
            f"Current platform: {platform.uname().release}\n"
            f"Run this test on the CM4 using:\n"
            f"  ./scripts/run-unit-test-remote.sh <PI_IP> <test_file>"
        )


def require_raspberry_pi(func):
    """
    Decorator to skip test if not running on Raspberry Pi.

    Usage:
        from tests.common.platform_check import require_raspberry_pi

        @require_raspberry_pi
        def test_emmc_detection():
            # ... test code
    """
    def wrapper(*args, **kwargs):
        skip_if_not_raspberry_pi(func.__name__)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def require_cm4(func):
    """
    Decorator to skip test if not running on CM4.

    Usage:
        from tests.common.platform_check import require_cm4

        @require_cm4
        def test_gpio_something():
            # ... test code
    """
    def wrapper(*args, **kwargs):
        skip_if_not_cm4(func.__name__)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Print platform info when module is run directly
if __name__ == '__main__':
    info = get_platform_info()
    print("Platform Information:")
    print("-" * 40)
    for key, value in info.items():
        print(f"  {key}: {value}")
