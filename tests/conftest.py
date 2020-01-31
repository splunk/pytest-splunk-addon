import pytest
from pytest_docker_tools import build, container

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

pytest_plugins = "pytester"

REPOSITORY_ROOT = pathlib.Path(__file__).parent

splunk_image = build(
    path='/Users/rfaircloth/PycharmProjects/pytest-splunk-addon/tests'

)
splunk_server_container = container(
    image='{splunk_image.id}',
    ports={
        '8000/tcp': None,
        '8089/tcp': None,
    },
    environment={
        'SPLUNK_PASSWORD': 'Changed@11',
        'SPLUNK_START_ARGS': '--accept-license'
    }

)


@pytest.fixture()
def splunk_server(splunk_server_container):
    return splunk_server_container.get_addr('8089/tcp')
