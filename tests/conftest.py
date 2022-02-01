import os
import pytest

pytest_plugins = "pytester"


def pytest_configure(config):
    config.addinivalue_line("markers", "external: Test search time only")
    config.addinivalue_line("markers", "kubernetes: Test search time only")
    config.addinivalue_line("markers", "doc: Test Sphinx docs")

