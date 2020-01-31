# -*- coding: utf-8 -*-

import logging
import re

import pytest
from splunk_appinspect import App

from .helmut.manager.jobs import Jobs
from .helmut.splunk.cloud import CloudSplunk
from .helmut_lib.SearchUtil import SearchUtil
from pytest_docker_tools import build, container

logger = logging.getLogger()


def pytest_addoption(parser):
    group = parser.getgroup('splunk-addon')

    group.addoption(
        '--splunk_app',
        action='store',
        dest='splunk_app',
        default='package',
        help='Path to Splunk app'
    )
    group.addoption(
        '--splunk_host',
        action='store',
        dest='splunk_host',
        default='127.0.0.1',
        help='Address of the Splunk Server'
    )
    group.addoption(
        '--splunk_port',
        action='store',
        dest='splunk_port',
        default='8089',
        help='Splunk rest port'
    )
    group.addoption(
        '--splunk_user',
        action='store',
        dest='splunk_user',
        default='admin',
        help='Splunk login user'
    )
    group.addoption(
        '--splunk_password',
        action='store',
        dest='splunk_password',
        default='changeme',
        help='Splunk password'
    )

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


#@pytest.fixture(scope="session")
@pytest.fixture
def splunk_search_util(request, splunk_server_container):


    ip, port = splunk_server_container.get_addr('8089/tcp')

    splunk = CloudSplunk(splunkd_host=ip,
                      splunkd_port=port,
                      username=request.config.getoption('splunk_user'),
                      password=request.config.getoption('splunk_password')
                      )

    # splunk = CloudSplunk(splunkd_host=request.config.getoption('splunk_host'),
    #                      splunkd_port=request.config.getoption('splunk_port'),
    #                      username=request.config.getoption('splunk_user'),
    #                      password=request.config.getoption('splunk_password')
    #                      )

    conn = splunk.create_logged_in_connector()
    jobs = Jobs(conn)

    return SearchUtil(jobs, logger)


def pytest_generate_tests(metafunc):
    if "sourcetypes" in metafunc.fixturenames or "eventtypes" in metafunc.fixturenames or "prop_elements" in metafunc.fixturenames:

        app = App(location=metafunc.config.getoption('splunk_app'), python_analyzer_enable=False)
        props = app.props_conf()
        eventtypes = app.eventtypes_conf().sects
        transforms = app.transforms_conf().sects

        if "sourcetypes" in metafunc.fixturenames:

            params = []
            # Add source types which are not RENAME host:: or used to set source:: used to set SOURCETYPE
            for section in props.sects:
                if section.startswith('source::'):
                    if props.sects[section].options['sourcetype']:
                        continue
                    else:
                        params.append(
                            pytest.param({'sourcetype': section, 'sourcetype': section},
                                         marks=pytest.mark.dependency(
                                             name='splunk::addon::sourcetype[{}]'.format(section)
                                             ),
                                         id=section
                                         )
                        )
                elif section.startswith('host::'):
                    continue
                else:
                    params.append(
                        pytest.param({'sourcetype': section, 'sourcetype': section},
                                     marks=pytest.mark.dependency(
                                         name='splunk::addon::sourcetype[{}]'.format(section)
                                     ),
                                     id=section
                                     )
                    )



            metafunc.parametrize("sourcetypes", params)

        elif "eventtypes" in metafunc.fixturenames:
            metafunc.parametrize("eventtypes", eventtypes)

        elif "prop_elements" in metafunc.fixturenames:
            extract_regex = r'\(\?\<(?P<FIELD>[^\>]+)\>'
            field_alias_regex = r'(?P<FIELD>\"[^\"]+\"|[^ ]+) * AS'

            params = []
            for section in props.sects:
                stanza = props.sects[section]
                for name, option in stanza.options.items():

                    # Identify any fields created via an EXTRACT regex
                    if name.startswith("EXTRACT-"):
                        matches = re.findall(extract_regex, option.value)
                        if matches:
                            terms = []
                            for m in matches:
                                terms.append('({}=* AND NOT {}="-" AND NOT {}="")'.format(m, m, m))

                            condition = '( {} )'.format(' AND '.join(terms))
                            params.append(
                                pytest.param({'sourcetype': section, 'field': condition},
                                             marks=pytest.mark.dependency(
                                                 depends=['splunk::addon::sourcetype[{}]'.format(section)]
                                             ),
                                             id="{}::{}".format(section, name)
                                             )
                            )
                    elif name.startswith("REPORT-"):
                        used_transforms = option.value.split(",")
                        for transform in used_transforms:
                            if transform in transforms:
                                current_transform = transforms[transform]
                                matches = re.findall(extract_regex, current_transform.options['REGEX'].value)

                                if matches:
                                    terms = []
                                    for m in matches:
                                        terms.append('({}=* AND NOT {}="-" AND NOT {}="")'.format(m, m, m))

                                    condition = '( {} )'.format(' AND '.join(terms))

                                    params.append(
                                        pytest.param(
                                            {'sourcetype': section, 'field': condition},
                                            marks=pytest.mark.dependency(
                                                depends=['splunk::addon::sourcetype[{}]'.format(section)]
                                            ),
                                            id="{}::{}".format(section, name)
                                            )
                                    )
                    elif name.startswith("FIELDALIAS-"):
                        # Identify any fields created via an EXTRACT regex

                        matches = re.findall(field_alias_regex, option.value, re.IGNORECASE)
                        if matches:
                            term = '({}=* AND NOT {}="-" AND NOT {}="")'.format(matches[0], matches[0], matches[0])

                            params.append(
                                pytest.param({'sourcetype': section, 'field': term },
                                             marks=pytest.mark.dependency(
                                                 depends=['splunk::addon::sourcetype[{}]'.format(section)]
                                             ),
                                             id="{}::{}".format(section, name)
                                             )
                            )
                    elif name.startswith("EVAL-"):
                        # Eval tests are hard we simple check to see if the field will ever populate for the source type
                        # When if or coalesce is used we should demand a manual test creation to test the paths

                        matches = re.findall(r'EVAL-(?P<FIELD>.*)', option.name, re.IGNORECASE)
                        if matches:
                            terms = []
                            for m in matches:
                                terms.append('({}=* AND NOT {}="-" AND NOT {}="")'.format(m, m, m))

                            condition = '( {} )'.format(' AND '.join(terms))

                        params.append(
                            pytest.param({'sourcetype': section, 'field': condition},
                                         marks=pytest.mark.dependency(
                                             depends=['splunk::addon::sourcetype[{}]'.format(section)]
                                         ),
                                         id="{}::{}".format(section, name)
                                         )
                        )
                    elif name.startswith("LOOKUP-"):
                        lookup_key_group = re.match(r'[^ ]+ +(?P<KEYS>.+) +OUTPUT', option.value, re.IGNORECASE).group('KEYS')

                        lookup_keys = r'(?:[^ ]* +AS +)?(?P<FIELD>[^ ]+)'

                        matches = re.findall(lookup_keys, lookup_key_group, re.IGNORECASE)

                        if matches:
                            terms = []
                            for m in matches:
                                terms.append('({}=* AND NOT {}="-" AND NOT {}="")'.format(m, m, m))

                            condition = '( {} )'.format(' AND '.join(terms))

                            params.append(
                                pytest.param({'sourcetype': section, 'field': condition},
                                             marks=pytest.mark.dependency(
                                                 depends=['splunk::addon::sourcetype[{}]'.format(section)]
                                             ),
                                             id="{}::{}".format(section, name)
                                             )
                            )

            metafunc.parametrize("prop_elements", params)
