import pytest


try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

pytest_plugins = "pytester"

REPOSITORY_ROOT = pathlib.Path(__file__).parent


@pytest.fixture()
def splunk_server(splunk_server_container):
    return splunk_server_container.get_addr('8089/tcp')
