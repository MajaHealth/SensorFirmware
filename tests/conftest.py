"""
pytest configuration and shared fixtures
"""
import pytest
import yaml
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from YAML file."""
    config_path = Path(__file__).parent / "config" / "test_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def results_dir(tmp_path_factory):
    """Create results directory for test outputs."""
    results = tmp_path_factory.mktemp("test-results")
    return results

@pytest.fixture
def service_ports(test_config):
    """Get service port configuration."""
    return test_config['services']

@pytest.fixture
def thresholds(test_config):
    """Get pass/fail thresholds."""
    return test_config['thresholds']
