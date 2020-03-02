pytest_plugins = "pytester"


def pytest_configure(config):
    config.addinivalue_line("markers", "external: Test search time only")
    config.addinivalue_line("markers", "docker: Test search time only")
