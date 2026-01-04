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
        config = yaml.safe_load(f)

    # Allow overriding service host via environment variable
    # This enables remote testing without modifying YAML
    target_host = os.getenv('PI_TARGET_IP')
    if target_host:
        for service in config['services'].values():
            service['host'] = target_host

    return config

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
