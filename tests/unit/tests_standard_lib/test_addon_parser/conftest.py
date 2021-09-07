from unittest.mock import Mock

import pytest


@pytest.fixture
def parser(configuration_file):
    def create_parser(
        parser_class, func_to_be_mocked, parsed_output, headers=None, props_conf=None
    ):
        headers = headers if headers else []
        FakeApp = Mock()
        attrs = {
            "{}.return_value".format(func_to_be_mocked): configuration_file(
                headers=headers, sects=parsed_output, errors=[]
            )
        }
        FakeApp.configure_mock(**attrs)
        if props_conf is not None:
            FakeApp.props_conf.return_value = props_conf
        return parser_class("fake_path", FakeApp)

    return create_parser
