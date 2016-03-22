"""py.test configuration file."""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "unit: Run only unit tests"
    )
    config.addinivalue_line(
        "markers",
        "integration: Run only integration tests"
    )
    config.addinivalue_line(
        "markers",
        "functional: Run only functional tests"
    )
