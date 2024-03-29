import pytest
from pytest_splunk_addon.tools import cim_field_report


@pytest.mark.parametrize(
    "data, records, expected",
    [
        (
            [],
            [
                {
                    "punct": '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                    "eventtype": "citrix_netscaler_ipfix_lb",
                },
                {
                    "punct": '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                    "eventtype": [
                        "citrix_netscaler_ipfix_Web",
                        "citrix_netscaler_ipfix_lb",
                        "citrix_netscaler_ipfix_lb_web",
                    ],
                },
                {
                    "punct": '="",="",="/",="",="",="",="",="",="",="",="--",=""',
                    "eventtype": [
                        "citrix_netscaler_nitro_stat_lb",
                        "citrix_netscaler_nitro_stat_service",
                    ],
                },
                {
                    "punct": '="",="",="",="",="",="",="",="",="",="",="",="",="',
                    "eventtype": "citrix_netscaler_nitro_stat_protocolip",
                },
            ],
            [
                (
                    "citrix_netscaler_ipfix_lb",
                    '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                ),
                (
                    "citrix_netscaler_ipfix_Web",
                    '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                ),
                (
                    "citrix_netscaler_ipfix_lb_web",
                    '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                ),
                (
                    "citrix_netscaler_nitro_stat_lb",
                    '="",="",="/",="",="",="",="",="",="",="",="--",=""',
                ),
                (
                    "citrix_netscaler_nitro_stat_service",
                    '="",="",="/",="",="",="",="",="",="",="",="--",=""',
                ),
                (
                    "citrix_netscaler_nitro_stat_protocolip",
                    '="",="",="",="",="",="",="",="",="",="",="",="",="',
                ),
            ],
        )
    ],
)
def test_collect_punct_and_eventtype(data, records, expected):
    cim_field_report.collect_punct_and_eventtype(data, records)
    assert expected == data


@pytest.mark.parametrize(
    "data, records, expected",
    [
        (
            (set(), {}),
            [
                {
                    "sourcetype": "citrix:netscaler:ipfix",
                    "bytes_in": "57016",
                    "dest": "174.145.122.167",
                    "dest_ip": "174.145.122.167",
                    "dest_port": "39888",
                    "destinationIPv4Address": "174.145.122.167",
                    "destinationTransportPort": "39888",
                    "duration": "3346795.701375083",
                    "eventtype": [
                        "citrix_netscaler_ipfix_Web",
                        "citrix_netscaler_ipfix_lb",
                        "citrix_netscaler_ipfix_lb_web",
                    ],
                    "flowEndMicroseconds": "8171933464.406442",
                    "flowStartMicroseconds": "4825137763.031359",
                    "host": "itgdi_citrix_netscaler_ipfix_unknown.samples_11",
                    "http_content_type": "text/html; charset=utf-8",
                    "index": "main",
                    "ipVersion": "4",
                    "linecount": "1",
                    "netscalerHttpContentType": "text/html; charset=utf-8",
                    "netscalerHttpRspLen": "57016",
                    "netscalerHttpRspStatus": "403",
                    "protocol_version": "4",
                    "punct": '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                    "response_code": "403",
                    "source": "itgdi_citrix_netscaler_ipfix_unknown.samples",
                    "sourceIPv4Address": "120.109.26.123",
                    "sourceTransportPort": "504118",
                    "splunk_server": "splunk",
                    "src": "120.109.26.123",
                    "src_ip": "120.109.26.123",
                    "src_port": "504118",
                    "status": "403",
                    "tag": [
                        "inventory",
                        "loadbalancer",
                        "loadbalancer_web",
                        "network",
                        "performance",
                        "web",
                    ],
                    "tag::eventtype": [
                        "inventory",
                        "loadbalancer",
                        "loadbalancer_web",
                        "network",
                        "performance",
                        "web",
                    ],
                    "vendor": "Citrix Systems",
                    "vendor_product": "Citrix ADC",
                },
                {
                    "sourcetype": "citrix:netscaler:ipfix",
                    "bytes_in": "23508",
                    "dest": "163.17.99.238",
                    "dest_ip": "163.17.99.238",
                    "dest_port": "49983",
                    "destinationIPv4Address": "163.17.99.238",
                    "destinationTransportPort": "49983",
                    "duration": "1188715.359898319",
                    "eventtype": [
                        "citrix_netscaler_ipfix_Web",
                        "citrix_netscaler_ipfix_lb",
                        "citrix_netscaler_ipfix_lb_web",
                    ],
                    "flowEndMicroseconds": "8589329539.304007",
                    "flowStartMicroseconds": "7400614179.405687",
                    "host": "itgdi_citrix_netscaler_ipfix_unknown.samples_10",
                    "http_content_type": "image/png",
                    "index": "main",
                    "ipVersion": "4",
                    "linecount": "1",
                    "netscalerHttpContentType": "image/png",
                    "netscalerHttpRspLen": "23508",
                    "netscalerHttpRspStatus": "200",
                    "protocol_version": "4",
                    "punct": '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                    "response_code": "200",
                    "source": "itgdi_citrix_netscaler_ipfix_unknown.samples",
                    "sourceIPv4Address": "115.79.46.87",
                    "sourceTransportPort": "992044",
                    "splunk_server": "splunk",
                    "src": "115.79.46.87",
                    "src_ip": "115.79.46.87",
                    "src_port": "992044",
                    "status": "200",
                    "tag": [
                        "inventory",
                        "loadbalancer",
                        "loadbalancer_web",
                        "network",
                        "performance",
                        "web",
                    ],
                    "tag::eventtype": [
                        "inventory",
                        "loadbalancer",
                        "loadbalancer_web",
                        "network",
                        "performance",
                        "web",
                    ],
                    "vendor": "Citrix Systems",
                    "vendor_product": "Citrix ADC",
                },
                {
                    "sourcetype": "citrix:netscaler:ipfix",
                    "client_type": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36",
                    "dest": "199.33.23.11",
                    "dest_ip": "199.33.23.11",
                    "dest_port": "7234",
                    "destinationIPv4Address": "199.33.23.11",
                    "destinationTransportPort": "7234",
                    "duration": "-5248395.997224312",
                    "eventtype": [
                        "citrix_netscaler_ipfix_Web",
                        "citrix_netscaler_ipfix_lb",
                        "citrix_netscaler_ipfix_lb_web",
                    ],
                    "flowEndMicroseconds": "2443005355.4003525",
                    "flowStartMicroseconds": "7691401352.624664",
                    "host": "itgdi_citrix_netscaler_ipfix_unknown.samples_9",
                    "http_content_type": "text/html; charset=UTF-8",
                    "http_method": "GET",
                    "http_referrer": "https://aaaaa/bbbbb/ccccc",
                    "http_user_agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36",
                    "http_user_agent_length": "109",
                    "index": "main",
                    "ipVersion": "4",
                    "linecount": "1",
                    "netscalerAaaUsername": "anonymous",
                    "netscalerHttpContentType": "text/html; charset=UTF-8",
                    "netscalerHttpReqMethod": "GET",
                    "netscalerHttpReqReferer": "https://aaaaa/bbbbb/ccccc",
                    "netscalerHttpReqUrl": "aaaaa/bbbbb/ccccc",
                    "netscalerHttpReqUserAgent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36",
                    "protocol_version": "4",
                    "punct": '="";_="";_="";_="";_="";_="";_="";_="";_="";_="...',
                    "source": "itgdi_citrix_netscaler_ipfix_unknown.samples",
                    "sourceIPv4Address": "126.200.174.140",
                    "sourceTransportPort": "615762",
                    "splunk_server": "splunk",
                    "src": "126.200.174.140",
                    "src_ip": "126.200.174.140",
                    "src_port": "615762",
                    "tag": [
                        "inventory",
                        "loadbalancer",
                        "loadbalancer_web",
                        "network",
                        "performance",
                        "web",
                    ],
                    "tag::eventtype": [
                        "inventory",
                        "loadbalancer",
                        "loadbalancer_web",
                        "network",
                        "performance",
                        "web",
                    ],
                    "url": "aaaaa/bbbbb/ccccc",
                    "url_length": "17",
                    "user": "anonymous",
                    "vendor": "Citrix Systems",
                    "vendor_product": "Citrix ADC",
                },
            ],
            (
                {"citrix:netscaler:ipfix"},
                {
                    frozenset(
                        {
                            "dest_ip",
                            "linecount",
                            "netscalerHttpRspLen",
                            "src_ip",
                            "flowStartMicroseconds",
                            "dest",
                            "host",
                            "destinationTransportPort",
                            "tag",
                            "sourceIPv4Address",
                            "protocol_version",
                            "status",
                            "duration",
                            "vendor",
                            "flowEndMicroseconds",
                            "ipVersion",
                            "src",
                            "sourceTransportPort",
                            "destinationIPv4Address",
                            "bytes_in",
                            "source",
                            "splunk_server",
                            "tag::eventtype",
                            "vendor_product",
                            "dest_port",
                            "netscalerHttpRspStatus",
                            "index",
                            "response_code",
                            "punct",
                            "http_content_type",
                            "src_port",
                            "eventtype",
                            "netscalerHttpContentType",
                        }
                    ): 2,
                    frozenset(
                        {
                            "dest_ip",
                            "linecount",
                            "src_ip",
                            "netscalerHttpReqUrl",
                            "netscalerHttpReqUserAgent",
                            "netscalerAaaUsername",
                            "url",
                            "http_method",
                            "flowStartMicroseconds",
                            "dest",
                            "host",
                            "url_length",
                            "destinationTransportPort",
                            "tag",
                            "http_referrer",
                            "sourceIPv4Address",
                            "protocol_version",
                            "duration",
                            "vendor",
                            "http_user_agent",
                            "flowEndMicroseconds",
                            "ipVersion",
                            "src",
                            "sourceTransportPort",
                            "destinationIPv4Address",
                            "source",
                            "tag::eventtype",
                            "splunk_server",
                            "vendor_product",
                            "dest_port",
                            "client_type",
                            "index",
                            "http_user_agent_length",
                            "user",
                            "punct",
                            "http_content_type",
                            "netscalerHttpReqMethod",
                            "src_port",
                            "eventtype",
                            "netscalerHttpReqReferer",
                            "netscalerHttpContentType",
                        }
                    ): 1,
                },
            ),
        )
    ],
)
def test_update_summary(data, records, expected):
    cim_field_report.update_summary(data, records)
    real_sourcetypes, real_summary = data
    expected_sourcetypes, expected_summary = expected

    assert real_sourcetypes == expected_sourcetypes
    for k, v in expected_summary.items():
        assert real_summary.get(k)
        assert real_summary[k] == v
